import itertools
import re
from typing import Any

from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .example import extract_example_section
from .inflection import extract_inflection_section
from .linkage import LINKAGE_TYPES, extract_linkage_section
from .models import Form, Sense, WordEntry
from .note import extract_note_section
from .pos import extract_pos_section
from .sound import extract_sound_section
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    # title templates
    # https://pl.wiktionary.org/wiki/Kategoria:Szablony_szablonów_haseł
    title_text = clean_node(wxr, None, level_node.largs)
    wxr.wtp.start_subsection(title_text)
    if title_text == "wymowa" and wxr.config.capture_pronunciation:
        extract_sound_section(wxr, base_data, level_node)
    elif title_text == "znaczenia":
        extract_pos_section(wxr, page_data, base_data, level_node)
    elif title_text == "przykłady":
        extract_example_section(wxr, page_data, base_data, level_node)
    elif title_text == "etymologia" and wxr.config.capture_etymologies:
        extract_etymology_section(wxr, page_data, base_data, level_node)
    elif title_text == "tłumaczenia" and wxr.config.capture_translations:
        extract_translation_section(
            wxr, page_data, level_node, base_data.lang_code
        )
    elif title_text in LINKAGE_TYPES and wxr.config.capture_inflections:
        extract_linkage_section(
            wxr,
            page_data,
            level_node,
            LINKAGE_TYPES[title_text],
            base_data.lang_code,
        )
    elif title_text == "uwagi":
        extract_note_section(wxr, page_data, base_data, level_node)
    elif title_text == "odmiana" and wxr.config.capture_inflections:
        extract_inflection_section(
            wxr, page_data, base_data.lang_code, level_node
        )
    elif title_text == "zapis":
        extract_zapis_section(wxr, base_data, level_node)
    elif title_text == "transliteracja":
        extract_transliteracja_section(wxr, base_data, level_node)


def extract_zapis_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    # get around "preformatted" node
    for node in level_node.find_child_recursively(NodeKind.TEMPLATE):
        if node.template_name == "ptrad":
            form_text = clean_node(
                wxr, None, node.template_parameters.get(1, "")
            )
            if form_text != "":
                base_data.forms.append(
                    Form(form=form_text, tags=["Traditional Chinese"])
                )


def extract_transliteracja_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        for node in list_item.children:
            if isinstance(node, str):
                m = re.search(r"\([\d\s,-.]+\)", node)
                if m is not None:
                    sense_index = m.group(0).strip("()")
                    roman = node[m.end() :].strip()
                    if roman != "":
                        base_data.forms.append(
                            Form(
                                form=roman,
                                sense_index=sense_index,
                                tags=["romanization"],
                            )
                        )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://pl.wiktionary.org/wiki/Wikisłownik:Zasady_tworzenia_haseł
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        after_parenthesis = False
        lang_code = "unknown"
        lang_name = "unknown"
        lang_title_cats = {}
        for title_content_node in itertools.chain.from_iterable(
            level2_node.largs
        ):
            if isinstance(
                title_content_node, str
            ) and title_content_node.strip().endswith("("):
                after_parenthesis = True
            elif (
                isinstance(title_content_node, TemplateNode)
                and after_parenthesis
            ):
                expanded_template = wxr.wtp.parse(
                    wxr.wtp.node_to_wikitext(title_content_node),
                    expand_all=True,
                )
                for span_tag in expanded_template.find_html("span"):
                    lang_code = span_tag.attrs.get("id", "")
                    break
                lang_name = clean_node(wxr, lang_title_cats, expanded_template)
                break
        if (
            wxr.config.capture_language_codes is not None
            and lang_code not in wxr.config.capture_language_codes
        ):
            continue
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
            categories=lang_title_cats.get("categories", []),
        )
        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            parse_section(wxr, page_data, base_data, level3_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]


def match_sense_index(sense_index: str, word_entry: WordEntry) -> bool:
    # return `True` if `WordEntry` has a `Sense` with same POS section
    # index number, usually the first number before "."
    if hasattr(word_entry, "senses") and len(word_entry.senses) == 0:
        return False
    if hasattr(word_entry, "senses"):
        sense = word_entry.senses[0]
    elif isinstance(word_entry, Sense):
        sense = word_entry
        # find exact match for index like "1.1"
        exact_match = not (
            "," in sense_index or "-" in sense_index or "." not in sense_index
        )
        if exact_match:
            return sense_index == sense.sense_index

    pos_index_str = sense.sense_index[: sense_index.find(".")]
    pos_section_index = 0
    if pos_index_str.isdigit():
        pos_section_index = int(pos_index_str)
    else:
        return False

    for part_of_index in sense_index.split(","):
        part_of_index = part_of_index.strip()
        if (
            "." in part_of_index
            and pos_index_str == part_of_index[: part_of_index.find(".")]
        ):
            return True
        elif re.fullmatch(r"\d+-\d+", part_of_index):
            start_str, end_str = part_of_index.split("-")
            if int(start_str) <= pos_section_index and pos_section_index <= int(
                end_str
            ):
                return True

    return False

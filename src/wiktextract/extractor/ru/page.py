import logging
from typing import Any, Optional

from wikitextprocessor import NodeKind, WikiNode
from wiktextract.config import POSSubtitleData
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .gloss import extract_gloss
from .inflection import extract_inflection
from .linkage import extract_linkages
from .models import WordEntry
from .pronunciation import extract_pronunciation
from .translation import extract_translations

# Templates that are used to form panels on pages and that
# should be ignored in various positions
PANEL_TEMPLATES = set()

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES = set()

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES = set()


def process_semantic_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    semantic_level_node: WikiNode,
):
    for level4_node in semantic_level_node.find_child(NodeKind.LEVEL4):
        section_title = clean_node(wxr, {}, level4_node.largs).lower()
        if section_title == "значение":
            for list_item in level4_node.find_child_recursively(
                NodeKind.LIST_ITEM
            ):
                extract_gloss(wxr, page_data[-1], list_item)

        elif section_title in wxr.config.LINKAGE_SUBTITLES:
            linkage_type = wxr.config.LINKAGE_SUBTITLES.get(section_title)
            extract_linkages(wxr, page_data[-1], linkage_type, level4_node)
        else:
            wxr.wtp.debug(
                f"Unprocessed section {section_title} in semantic section",
                sortid="extractor/ru/page/process_semantic_section/35",
            )

    # XXX: Process non level4 nodes such as illustration templates "{илл|...}",
    # cf. https://ru.wiktionary.org/wiki/овощ


POS_TEMPLATE_NAME_MAP = {
    "abbrev": {"pos": "abbrev", "tags": ["abbreviation"]},
    "adv": {"pos": "adv"},
    "affix": {"pos": "affix"},
    "conj": {"pos": "conj"},
    "interj": {"pos": "intj"},
    "noun": {"pos": "noun"},
    "onomatop": {"pos": "onomatopeia", "tags": ["onomatopoeic"]},
    "part": {"pos": "particle"},
    "phrase": {"pos": "phrase"},
    "predic": {"pos": "adj"},
    "prep": {"pos": "prep"},
    "suffix": {"pos": "suffix"},
    "буква": {"pos": "character"},
    "гидроним": {"pos": "name"},
    "гл": {"pos": "verb"},
    "дее": {"pos": "verb", "tags": ["participle", "gerund"]},
    "деепр": {"pos": "verb", "tags": ["participle", "gerund"]},
    "мест": {"pos": "pron"},
    "нар": {"pos": "adv"},
    "падежи": {"pos": "noun"},
    "послелог": {"pos": "postp"},
    "прил": {"pos": "adj"},
    "прич": {"pos": "verb", "tags": ["participle"]},
    "союз": {"pos": "conj"},
    "сущ": {"pos": "noun"},
    "существительное": {"pos": "noun"},
    "топоним": {"pos": "name"},
    "фам": {"pos": "name"},
    "част": {"pos": "particle"},
    "числ": {"pos": "num"},
}


def get_pos(
    wxr: WiktextractContext, level_node: WikiNode
) -> Optional[POSSubtitleData]:
    # Search for POS in template names
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        template_name = template_node.template_name.lower()
        for part in template_name.split()[:2]:
            for subpart in part.split("-")[:2]:
                if subpart in POS_TEMPLATE_NAME_MAP:
                    return POS_TEMPLATE_NAME_MAP[subpart]

    # Search for POS in clean_text
    text = clean_node(wxr, {}, level_node.children)

    for pos_string in wxr.config.POS_SUBTITLES.keys():
        if pos_string in text.lower():
            return wxr.config.POS_SUBTITLES[pos_string]

    if "форма" in text.lower():
        # XXX: Decide what to do with form entries
        return

    if len(text) > 0:
        wxr.wtp.debug(
            f"No part of speech found in children: {level_node.children} "
            f"with clean text {text}",
            sortid="extractor/ru/page/get_pos/98",
        )


def parse_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level3_node: WikiNode
) -> None:
    section_title = clean_node(wxr, None, level3_node.largs).lower()
    wxr.wtp.start_subsection(section_title)
    if section_title in [
        # Morphological and syntactic properties
        "морфологические и синтаксические свойства",
        # Type and syntactic properties of the word combination
        "тип и синтаксические свойства сочетания",
    ]:
        pos_data = get_pos(wxr, level3_node)
        if pos_data is not None:
            page_data[-1].pos = pos_data["pos"]
            page_data[-1].tags.extend(pos_data.get("tags", []))
        extract_inflection(wxr, page_data[-1], level3_node)
        # XXX: Extract grammatical tags (gender, etc.) from Russian Wiktionary
    elif section_title in wxr.config.POS_SUBTITLES:
        pos_data = wxr.config.POS_SUBTITLES[section_title]
        page_data[-1].pos = pos_data["pos"]
        page_data[-1].tags.extend(pos_data.get("tags", []))
        for list_item in level3_node.find_child_recursively(NodeKind.LIST_ITEM):
            extract_gloss(wxr, page_data[-1], list_item)
    elif section_title == "произношение" and wxr.config.capture_pronunciation:
        extract_pronunciation(wxr, page_data[-1], level3_node)
    elif section_title == "семантические свойства":  # Semantic properties
        process_semantic_section(wxr, page_data, level3_node)
    elif section_title == "значение":
        pass
    elif section_title == "родственные слова" and wxr.config.capture_linkages:
        # Word family
        pass
    elif section_title == "этимология" and wxr.config.capture_etymologies:
        # XXX: Extract etymology
        pass
    elif (
        section_title == "фразеологизмы и устойчивые сочетания"
        and wxr.config.capture_linkages
    ):
        pass
    elif section_title == "перевод" and wxr.config.capture_translations:
        extract_translations(wxr, page_data[-1], level3_node)
    elif section_title in ['анаграммы', 'метаграммы', 'синонимы', 'антонимы']:
        pass
    elif section_title == "библиография":
        pass
    elif section_title in ['латиница (latinça)', 'латиница (latinca)']:
        pass
    elif section_title == "иноязычные аналоги":
        pass
    elif section_title == "прочее":
        pass
    else:
        wxr.wtp.debug(
            f"Unprocessed section {section_title}",
            sortid="wixtextract/extractor/ru/page/parse_section/66",
        )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # Help site describing page structure:
    # https://ru.wiktionary.org/wiki/Викисловарь:Правила_оформления_статей

    if wxr.config.verbose:
        logging.info(f"Parsing page: {page_title}")

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    tree = wxr.wtp.parse(
        page_text,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
    )

    page_data: list[WordEntry] = []
    for level1_node in tree.find_child(NodeKind.LEVEL1):
        for subtitle_template in level1_node.find_content(NodeKind.TEMPLATE):
            lang_code = subtitle_template.template_name.strip(" -")
            if (
                wxr.config.capture_language_codes is not None
                and lang_code not in wxr.config.capture_language_codes
            ):
                continue

            categories = {"categories": []}

            lang = clean_node(wxr, categories, subtitle_template)
            wxr.wtp.start_section(lang)

            base_data = WordEntry(
                lang=lang, lang_code=lang_code, word=wxr.wtp.title
            )
            base_data.categories.extend(categories["categories"])

            unprocessed_nodes = []
            for non_level23_node in level1_node.invert_find_child(
                NodeKind.LEVEL2 | NodeKind.LEVEL3
            ):
                IGNORED_TEMPLATES = [
                    "wikipedia",
                    "Омонимы",
                    "improve",
                    "Лексема в Викиданных",
                ]
                if not (
                    isinstance(non_level23_node, WikiNode)
                    and non_level23_node.kind == NodeKind.TEMPLATE
                    and non_level23_node.template_name in IGNORED_TEMPLATES
                ):
                    unprocessed_nodes.append(non_level23_node)

                # XXX: Extract form pages that never reach a level 2 or 3 node
                # https://ru.wiktionary.org/wiki/Διὸς

            if (
                len(unprocessed_nodes) > 0
                and len(clean_node(wxr, None, unprocessed_nodes)) > 0
            ):
                wxr.wtp.debug(
                    f"Unprocessed nodes in level node {level1_node.largs}: "
                    + str(unprocessed_nodes),
                    sortid="extractor/es/page/parse_page/80",
                )

            for level2_node in level1_node.find_child(NodeKind.LEVEL2):
                page_data.append(base_data.model_copy(deep=True))
                for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                    parse_section(wxr, page_data, level3_node)

            is_first_level2_node = True
            for level3_node in level1_node.find_child(NodeKind.LEVEL3):
                if is_first_level2_node:
                    page_data.append(base_data.model_copy(deep=True))
                    is_first_level2_node = False
                parse_section(wxr, page_data, level3_node)

    return [d.model_dump(exclude_defaults=True) for d in page_data]

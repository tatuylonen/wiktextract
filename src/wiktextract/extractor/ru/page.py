import copy
import logging
from typing import Optional

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.extractor.ru.gloss import extract_gloss
from wiktextract.extractor.ru.linkage import extract_linkages
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.pronunciation import extract_pronunciation
from wiktextract.extractor.ru.translation import extract_translations
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

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

    # XXX: Process non level4 nodes such as illustration templates "{илл|...}", cf. https://ru.wiktionary.org/wiki/овощ


def get_pos(
    wxr: WiktextractContext,
    level_node: WikiNode,
) -> Optional[str]:
    # Search for POS in template names
    for template_node in level_node.find_child(NodeKind.TEMPLATE):
        POS_MAP = {
            "abbrev": "abbrev",
            "adv": "adv",
            "affix": "affix",
            "conj": "conj",
            "interj": "interj",
            "noun": "noun",
            "onomatop": "onomatopeia",
            "part": "particle",
            "phrase": "phrase",
            "predic": "adj",
            "prep": "prep",
            "suffix": "suffix",
            "буква": "character",
            "гидроним": "name",
            "гл": "verb",
            "дее": "gerund",
            "деепр": "gerund",
            "мест": "pronoun",
            "нар": "adv",
            "падежи": "noun",
            "послелог": "postp",
            "прил": "adj",
            "прич": "participle",
            "союз": "conj",
            "сущ": "noun",
            "существительное": "noun",
            "топоним": "name",
            "фам": "name",
            "част": "particle",
            "числ": "number",
        }
        template_name = template_node.template_name.lower()
        for part in template_name.split()[:2]:
            for subpart in part.split("-")[:2]:
                if subpart in POS_MAP:
                    return POS_MAP[subpart]

    # Search for POS in clean_text
    text = clean_node(wxr, {}, level_node.children)

    for POS_string in wxr.config.POS_SUBTITLES.keys():
        if POS_string in text.lower():
            return wxr.config.POS_SUBTITLES[POS_string]["pos"]

    if "форма" in text.lower():
        # XXX: Decide what to do with form entries
        return

    if text.strip():
        wxr.wtp.debug(
            f"No part of speech found in children: {level_node.children} with clean text {text}",
            sortid="extractor/ru/page/get_pos/98",
        )


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level3_node: WikiNode,
):
    section_title = clean_node(wxr, {}, level3_node.largs).strip()
    wxr.wtp.start_subsection(section_title)
    if section_title in [
        "Морфологические и синтаксические свойства",  # Morphological and syntactic properties
        "Тип и синтаксические свойства сочетания",  # Type and syntactic properties of the word combination
    ]:
        pos = get_pos(wxr, level3_node)
        if pos:
            page_data[-1].pos = pos
        # XXX: Extract forms from Russian Wiktionary
        # XXX: Extract grammatical tags (gender, etc.) from Russian Wiktionary

    elif section_title == "Произношение":
        if wxr.config.capture_pronunciation:
            extract_pronunciation(wxr, page_data[-1], level3_node)
    elif section_title == "Семантические свойства":  # Semantic properties
        process_semantic_section(wxr, page_data, level3_node)
    elif section_title == "Значение":
        pass
    elif section_title == "Родственные слова":  # Word family
        if wxr.config.capture_linkages:
            pass
    elif section_title == "Этимология":
        if wxr.config.capture_etymologies:
            # XXX: Extract etymology
            pass
    elif section_title == "Фразеологизмы и устойчивые сочетания":
        if wxr.config.capture_linkages:
            pass
    elif section_title == "Перевод":
        if wxr.config.capture_translations:
            extract_translations(wxr, page_data[-1], level3_node)
    elif section_title in ["Анаграммы", "Метаграммы", "Синонимы", "Антонимы"]:
        pass
    elif section_title == "Библиография":
        pass
    elif section_title in ["Латиница (Latinça)", "Латиница (Latinca)"]:
        pass
    elif section_title == "Иноязычные аналоги":
        pass
    elif section_title == "Прочее":
        pass
    else:
        wxr.wtp.debug(
            f"Unprocessed section {section_title}",
            sortid="wixtextract/extractor/ru/page/parse_section/66",
        )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, str]]:
    # Help site describing page structure: https://ru.wiktionary.org/wiki/Викисловарь:Правила_оформления_статей

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
            lang_code = (
                subtitle_template.template_name.strip()
                .removeprefix("-")
                .removesuffix("-")
            )

            if (
                wxr.config.capture_language_codes is not None
                and lang_code not in wxr.config.capture_language_codes
            ):
                continue

            categories = {"categories": []}

            lang_name = clean_node(wxr, categories, subtitle_template)
            wxr.wtp.start_section(lang_name)

            base_data = WordEntry(
                lang_name=lang_name, lang_code=lang_code, word=wxr.wtp.title
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

            if (
                unprocessed_nodes
                and clean_node(wxr, {}, unprocessed_nodes).strip()
            ):
                wxr.wtp.debug(
                    f"Unprocessed nodes in level node {level1_node.largs}: {non_level23_node}",
                    sortid="extractor/es/page/parse_page/80",
                )

            for level2_node in level1_node.find_child(NodeKind.LEVEL2):
                page_data.append(copy.deepcopy(base_data))
                for level3_node in level2_node.find_child(NodeKind.LEVEL3):
                    parse_section(wxr, page_data, level3_node)

            is_first_level2_node = True
            for level3_node in level1_node.find_child(NodeKind.LEVEL3):
                if is_first_level2_node:
                    page_data.append(copy.deepcopy(base_data))
                    is_first_level2_node = False
                parse_section(wxr, page_data, level3_node)

    return [d.model_dump(exclude_defaults=True) for d in page_data]

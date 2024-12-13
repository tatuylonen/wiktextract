from typing import Any

from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_citation_section, extract_etymology_section
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .section_titles import POS_DATA
from .sound import extract_hyphenation_section
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_text = clean_node(wxr, None, level_node.largs)
    if title_text in POS_DATA:
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)
    elif title_text == "Traduzione":
        extract_translation_section(wxr, page_data, level_node)
    elif title_text == "Etimologia / Derivazione":
        extract_etymology_section(wxr, page_data, level_node)
    elif title_text == "Citazione":
        extract_citation_section(wxr, page_data, level_node)
    elif title_text == "Sillabazione":
        extract_hyphenation_section(wxr, page_data, level_node)

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://it.wiktionary.org/wiki/Wikizionario:Manuale_di_stile
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        lang_cats = {}
        lang_name = clean_node(wxr, lang_cats, level2_node.largs)
        if lang_name in ["Altri progetti", "Note / Riferimenti"]:
            continue
        lang_code = "unknown"
        for lang_template in level2_node.find_content(NodeKind.TEMPLATE):
            lang_code = lang_template.template_name.strip("-")
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
            categories=lang_cats.get("categories", []),
        )
        for next_level_node in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]

from typing import Any

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .linkage import extract_expression_section, extract_linkage_section
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .section_titles import LINKAGE_SECTIONS, POS_DATA
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    cats = {}
    title_text = clean_node(wxr, cats, level_node.largs)
    if title_text in POS_DATA:
        extract_pos_section(
            wxr,
            page_data,
            base_data,
            level_node,
            title_text,
            cats.get("categories", []),
        )
    elif title_text in ["Tradução", "Cognatos"]:
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text == "Expressões":
        extract_expression_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text in LINKAGE_SECTIONS:
        extract_linkage_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
            LINKAGE_SECTIONS[title_text],
        )
    elif title_text == "Etimologia":
        extract_etymology_section(wxr, page_data, level_node)

    cats = {}
    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(wxr, cats, link_node)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.categories.extend(cats.get("categories", []))

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://pt.wiktionary.org/wiki/Wikcionário:Livro_de_estilo
    if "/traduções" in page_title:  # skip translation page
        return []
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []
    for level1_node in tree.find_child(NodeKind.LEVEL1):
        lang_cats = {}
        lang_name = clean_node(wxr, lang_cats, level1_node.largs)
        lang_code = "unknown"
        for lang_template in level1_node.find_content(NodeKind.TEMPLATE):
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
        for next_level_node in level1_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]

import string
from typing import Any

from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .section_titles import POS_DATA


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_text = clean_node(wxr, None, level_node.largs)
    title_text = title_text.rstrip(string.digits + string.whitespace)
    wxr.wtp.start_subsection(title_text)
    if title_text in POS_DATA:
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)
    elif title_text == "Etîmolojî":
        extract_etymology_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://ku.wiktionary.org/wiki/Wîkîferheng:Normalkirina_gotaran
    # https://ku.wiktionary.org/wiki/Alîkarî:Formata_nivîsînê
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        cats = {}
        lang_name = clean_node(wxr, cats, level2_node.largs)
        lang_code = "unknown"
        for t_node in level2_node.find_content(NodeKind.TEMPLATE):
            new_lang_code = clean_node(
                wxr, None, t_node.template_parameters.get(1, "")
            )
            if new_lang_code != "":
                lang_code = new_lang_code
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
            categories=cats.get("categories", []),
        )
        for next_level_node in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]

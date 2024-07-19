import re
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import (
    NodeKind,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .pos import parse_pos_section
from .section_titles import POS_DATA

PANEL_TEMPLATES = set()
PANEL_PREFIXES = set()
ADDITIONAL_EXPAND_TEMPLATES = set()


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    title_texts = clean_node(wxr, None, level_node.largs)
    for title_text in re.split(r"：|・", title_texts):
        if title_text in POS_DATA:
            parse_pos_section(wxr, page_data, base_data, level_node, title_text)
            break


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://ja.wiktionary.org/wiki/Wiktionary:スタイルマニュアル
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs)
        lang_code = name_to_code(lang_name, "ja")
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
        )
        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            parse_section(wxr, page_data, base_data, level3_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]

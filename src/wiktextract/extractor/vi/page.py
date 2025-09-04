from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .section_titles import POS_DATA, TRANSLATION_SECTIONS
from .sound import extract_sound_section
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    subtitle = clean_node(wxr, None, level_node.largs)
    if subtitle in POS_DATA:
        extract_pos_section(wxr, page_data, base_data, level_node, subtitle)
    elif subtitle in TRANSLATION_SECTIONS:
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) else base_data, level_node
        )
    elif subtitle == "Cách phát âm":
        extract_sound_section(wxr, base_data, level_node)
    elif subtitle not in ["Tham khảo", "Cách ra dấu", "Đọc thêm"]:
        wxr.wtp.debug(f"Unknown title: {subtitle}", sortid="vi/page/22")

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://vi.wiktionary.org/wiki/Wiktionary:Sơ_đồ_mục_từ

    # ignore thesaurus, rhyme, quote, reconstruct pages
    if page_title.startswith(
        ("Kho từ vựng:", "Vần:", "Kho ngữ liệu:", "Từ tái tạo:")
    ):
        return []

    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        categories = {}
        lang_name = clean_node(wxr, categories, level2_node.largs)
        lang_code = name_to_code(lang_name, "vi") or "unknown"
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
        )
        base_data.categories = categories.get("categories", [])
        for next_level in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))

    return [d.model_dump(exclude_defaults=True) for d in page_data]

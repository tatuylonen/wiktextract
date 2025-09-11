from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .linkage import extract_alt_form_section, extract_linkage_section
from .models import Sense, WordEntry
from .pos import extract_note_section, extract_pos_section
from .section_titles import LINKAGE_SECTIONS, POS_DATA, TRANSLATION_SECTIONS
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
        if len(page_data[-1].senses) == 0 and subtitle in LINKAGE_SECTIONS:
            page_data.pop()
            extract_linkage_section(
                wxr,
                page_data if len(page_data) > 0 else [base_data],
                level_node,
                LINKAGE_SECTIONS[subtitle],
            )
    elif subtitle in TRANSLATION_SECTIONS:
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) else base_data, level_node
        )
    elif subtitle == "Cách phát âm":
        extract_sound_section(wxr, base_data, level_node)
    elif subtitle == "Từ nguyên":
        extract_etymology_section(wxr, base_data, level_node)
    elif subtitle == "Cách viết khác":
        extract_alt_form_section(wxr, base_data, page_data, level_node)
    elif subtitle == "Ghi chú sử dụng":
        extract_note_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif subtitle in LINKAGE_SECTIONS:
        extract_linkage_section(
            wxr,
            page_data if len(page_data) > 0 else [base_data],
            level_node,
            LINKAGE_SECTIONS[subtitle],
        )
    elif subtitle not in ["Tham khảo", "Cách ra dấu", "Đọc thêm", "Xem thêm"]:
        wxr.wtp.debug(f"Unknown title: {subtitle}", sortid="vi/page/22")

    extract_section_cats(wxr, base_data, page_data, level_node)
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
        lang_name = clean_node(wxr, categories, level2_node.largs) or "unknown"
        lang_code = name_to_code(lang_name, "vi") or "unknown"
        for t_node in level2_node.find_content(NodeKind.TEMPLATE):
            if t_node.template_name == "langname":
                lang_code = clean_node(
                    wxr, None, t_node.template_parameters.get(1, "")
                )
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
        extract_section_cats(wxr, base_data, page_data, level2_node)
        for next_level in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))

    return [d.model_dump(exclude_defaults=True) for d in page_data]


def extract_section_cats(
    wxr: WiktextractContext,
    base_data: WordEntry,
    page_data: list[WordEntry],
    level_node: LevelNode,
):
    cats = {}
    for node in level_node.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
        if node.kind == NodeKind.LINK:
            clean_node(wxr, cats, node)
        elif node.template_name in [
            "topics",
            "C",
            "topic",
            "catlangname",
            "cln",
        ]:
            clean_node(wxr, cats, node)

    if len(page_data) == 0 or page_data[-1].lang_code != base_data.lang_code:
        base_data.categories.extend(cats.get("categories", []))
    else:
        for data in page_data:
            if data.lang_code == page_data[-1].lang_code:
                data.categories.extend(cats.get("categories", []))

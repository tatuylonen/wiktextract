import re
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .linkage import extract_linkage_section
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .section_titles import LINKAGE_SECTIONS, POS_DATA
from .sound import (
    SOUND_TEMPLATES,
    extract_sound_section,
    extract_sound_template,
)
from .translation import extract_translation_section


def extract_section_categories(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, link_node
        )


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_text = clean_node(wxr, None, level_node.largs)
    title_text = re.sub(r"\s*\d+$", "", title_text)
    if title_text.removeprefix("보조 ").strip() in POS_DATA:
        orig_page_data_len = len(page_data)
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)
        if (
            len(page_data) == orig_page_data_len
            and title_text in LINKAGE_SECTIONS
            and len(page_data) > 0
        ):  # try extract as linkage section
            extract_linkage_section(
                wxr, page_data[-1], level_node, LINKAGE_SECTIONS[title_text]
            )
    elif title_text in LINKAGE_SECTIONS and len(page_data) > 0:
        extract_linkage_section(
            wxr, page_data[-1], level_node, LINKAGE_SECTIONS[title_text]
        )
    elif title_text == "번역" and len(page_data) > 0:
        extract_translation_section(wxr, page_data[-1], level_node)
    elif title_text == "발음":
        extract_sound_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    extract_section_categories(wxr, page_data, base_data, level_node)


def parse_language_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level2_node: LevelNode
) -> None:
    pre_data_len = len(page_data)
    lang_name = clean_node(wxr, None, level2_node.largs)
    if lang_name == "":
        lang_name = "unknown"
    lang_code = name_to_code(lang_name, "ko")
    if lang_code == "":
        lang_code = "unknown"
    if (
        wxr.config.capture_language_codes is not None
        and lang_code not in wxr.config.capture_language_codes
    ):
        return
    wxr.wtp.start_section(lang_name)
    base_data = WordEntry(
        word=wxr.wtp.title,
        lang_code=lang_code,
        lang=lang_name,
        pos="unknown",
    )
    extract_section_categories(wxr, page_data, base_data, level2_node)
    for t_node in level2_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in SOUND_TEMPLATES:
            extract_sound_template(wxr, base_data, t_node)

    for next_level in level2_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    # no POS section
    if len(page_data) == pre_data_len:
        extract_pos_section(wxr, page_data, base_data, level2_node, "")


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://ko.wiktionary.org/wiki/위키낱말사전:문서_양식
    # https://ko.wiktionary.org/wiki/위키낱말사전:한국어_편집부
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        parse_language_section(wxr, page_data, level2_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]

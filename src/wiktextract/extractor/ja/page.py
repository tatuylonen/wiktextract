import re
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .linkage import extract_linkage_section
from .models import Sense, WordEntry
from .pos import parse_pos_section
from .section_titles import LINKAGES, POS_DATA
from .sound import extract_sound_section
from .translation import extract_translation_section

PANEL_TEMPLATES = set()
PANEL_PREFIXES = set()
ADDITIONAL_EXPAND_TEMPLATES = set()


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_texts = clean_node(wxr, None, level_node.largs)
    for title_text in re.split(r"：|・", title_texts):
        if title_text in POS_DATA:
            pre_len = len(page_data)
            parse_pos_section(wxr, page_data, base_data, level_node, title_text)
            if (
                len(page_data) == pre_len
                and title_text in LINKAGES
                and pre_len > 0
            ):
                extract_linkage_section(
                    wxr, page_data[-1], level_node, LINKAGES[title_text]
                )
            break
        elif title_text in ["語源", "由来"] and wxr.config.capture_etymologies:
            extract_etymology_section(wxr, page_data, base_data, level_node)
            break
        elif title_text == "発音" and wxr.config.capture_pronunciation:
            extract_sound_section(wxr, page_data, base_data, level_node)
            break
        elif title_text == "翻訳" and wxr.config.capture_translations:
            if len(page_data) == 0:
                page_data.append(base_data.model_copy(deep=True))
            extract_translation_section(wxr, page_data[-1], level_node)
            break
        elif title_text in LINKAGES and wxr.config.capture_linkages:
            if len(page_data) == 0:
                page_data.append(base_data.model_copy(deep=True))
            extract_linkage_section(
                wxr, page_data[-1], level_node, LINKAGES[title_text]
            )
            break

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)


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
        if lang_code == "":
            for template in level2_node.find_content(NodeKind.TEMPLATE):
                if template.template_name == "L":
                    lang_code = template.template_parameters.get(1, "")
        if lang_code == "":
            lang_code = "unknown"
        wxr.wtp.start_section(lang_name)
        base_data = WordEntry(
            word=wxr.wtp.title,
            lang_code=lang_code,
            lang=lang_name,
            pos="unknown",
        )
        for link_node in level2_node.find_child(NodeKind.LINK):
            clean_node(wxr, base_data, link_node)
        for level3_node in level2_node.find_child(NodeKind.LEVEL3):
            parse_section(wxr, page_data, base_data, level3_node)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))
    return [m.model_dump(exclude_defaults=True) for m in page_data]

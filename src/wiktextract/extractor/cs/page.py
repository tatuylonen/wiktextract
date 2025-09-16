import re
from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .declension import extract_declension_section
from .linkage import extract_alt_form_section, extract_linkage_section
from .models import Sense, WordEntry
from .pos import extract_pos_section, extract_sense_section
from .section_titles import LINKAGE_SECTIONS, POS_DATA
from .sound import extract_hyphenation_section, extract_sound_section
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
):
    subtitle = clean_node(wxr, None, level_node.largs)
    subtitle = re.sub(r"\(\d+\)", "", subtitle).strip()
    if subtitle in POS_DATA and level_node.contain_node(LEVEL_KIND_FLAGS):
        extract_pos_section(wxr, page_data, base_data, level_node, subtitle)
    elif subtitle == "význam" and len(page_data) > 0:
        extract_sense_section(wxr, page_data[-1], level_node)
    elif subtitle == "výslovnost":
        extract_sound_section(wxr, base_data, level_node)
    elif subtitle == "dělení":
        extract_hyphenation_section(wxr, base_data, level_node)
    elif subtitle == "etymologie":
        base_data.etymology_text = clean_node(
            wxr, base_data, list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
        )
    elif subtitle == "varianty":
        extract_alt_form_section(wxr, base_data, level_node)
    elif subtitle == "překlady":
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif subtitle in LINKAGE_SECTIONS:
        extract_linkage_section(
            wxr,
            page_data[-1] if len(page_data) > 0 else base_data,
            level_node,
            LINKAGE_SECTIONS[subtitle],
        )
    elif subtitle in ["skloňování", "stupňování"]:
        extract_declension_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif subtitle not in ["externí odkazy"]:
        wxr.wtp.debug(f"Unknown title: {subtitle}", sortid="cs/page/27")

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, link_node
        )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://cs.wiktionary.org/wiki/Wikislovník:Formát_hesla
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text)
    page_data = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        lang_name = clean_node(wxr, None, level2_node.largs) or "unknown"
        if lang_name in ["poznámky", "externí odkazy"]:
            continue
        lang_code = name_to_code(lang_name, "cs") or "unknown"
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
        for next_level in level2_node.find_child(LEVEL_KIND_FLAGS):
            parse_section(wxr, page_data, base_data, next_level)

    for data in page_data:
        if len(data.senses) == 0:
            data.senses.append(Sense(tags=["no-gloss"]))

    return [d.model_dump(exclude_defaults=True) for d in page_data]

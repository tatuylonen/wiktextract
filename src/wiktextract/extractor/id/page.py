from typing import Any

from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .etymology import extract_etymology_section
from .models import Sense, WordEntry
from .pos import extract_pos_section
from .section_titles import POS_DATA
from .sound import extract_sound_section
from .translation import extract_translation_section


def parse_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    title_text = clean_node(wxr, None, level_node.largs)
    wxr.wtp.start_subsection(title_text)
    if title_text in POS_DATA:
        extract_pos_section(wxr, page_data, base_data, level_node, title_text)
    elif title_text == "Etimologi":
        extract_etymology_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text == "Terjemahan":
        extract_translation_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )
    elif title_text in ["Pelafalan", "Ejaan"]:
        extract_sound_section(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, level_node
        )

    for next_level in level_node.find_child(LEVEL_KIND_FLAGS):
        parse_section(wxr, page_data, base_data, next_level)

    for link_node in level_node.find_child(NodeKind.LINK):
        clean_node(
            wxr, page_data[-1] if len(page_data) > 0 else base_data, link_node
        )
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name.endswith("-cat"):
            clean_node(
                wxr, page_data[-1] if len(page_data) > 0 else base_data, t_node
            )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> list[dict[str, Any]]:
    # page layout
    # https://id.wiktionary.org/wiki/Wikikamus:Penjelasan_tataletak_entri
    # https://id.wiktionary.org/wiki/Wikikamus:Format_Kamus
    wxr.wtp.start_page(page_title)
    tree = wxr.wtp.parse(page_text, pre_expand=True)
    page_data: list[WordEntry] = []
    for level2_node in tree.find_child(NodeKind.LEVEL2):
        cats = {}
        lang_name = clean_node(wxr, cats, level2_node.largs)
        lang_code = (
            name_to_code(lang_name.removeprefix("bahasa "), "id") or "unknown"
        )
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

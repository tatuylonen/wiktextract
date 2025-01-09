from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    base_data.etymology_text = ""
    base_data.etymology_categories.clear()
    index = len(level_node.children)
    for node_index, _ in level_node.find_child(LEVEL_KIND_FLAGS, True):
        index = node_index
        break
    cats = {}
    e_str = clean_node(wxr, cats, level_node.children[:index])
    if e_str != "":
        base_data.etymology_text = e_str
        base_data.etymology_categories = cats.get("categories", [])

from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            e_str = clean_node(wxr, base_data, list_item.children)
            if e_str != "":
                base_data.etymology_texts.append(e_str)
    if len(base_data.etymology_texts) == 0:
        e_str = clean_node(
            wxr, base_data, list(level_node.invert_find_child(LEVEL_KIND_FLAGS))
        )
        if e_str != "":
            base_data.etymology_texts.append(e_str)

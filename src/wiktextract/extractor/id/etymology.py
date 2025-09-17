from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    has_list = False
    for list_node in level_node.find_child(NodeKind.LIST):
        has_list = True
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            e_str = clean_node(wxr, word_entry, list_item.children)
            if e_str != "":
                word_entry.etymology_texts.append(e_str)
    if not has_list:
        e_str = clean_node(
            wxr,
            word_entry,
            list(
                level_node.invert_find_child(
                    LEVEL_KIND_FLAGS, include_empty_str=True
                )
            ),
        )
        if e_str != "":
            word_entry.etymology_texts.append(e_str)

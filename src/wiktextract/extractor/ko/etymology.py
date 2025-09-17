from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    if len(word_entry.etymology_texts) > 0:
        word_entry.etymology_texts.clear()
        word_entry.categories.clear()

    has_list = False
    for list_node in level_node.find_child(NodeKind.LIST):
        has_list = True
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            text = clean_node(wxr, word_entry, list_item.children)
            if len(text) > 0:
                word_entry.etymology_texts.append(text)

    if not has_list:
        text = clean_node(
            wxr,
            word_entry,
            list(
                level_node.invert_find_child(
                    LEVEL_KIND_FLAGS, include_empty_str=True
                )
            ),
        )
        if len(text) > 0:
            word_entry.etymology_texts.append(text)

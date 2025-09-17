from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        text = clean_node(
            wxr,
            word_entry,
            list(
                list_item.invert_find_child(
                    NodeKind.LIST, include_empty_str=True
                )
            ),
        )
        if text != "":
            word_entry.etymology_texts.append(text)

from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    # Nested etymology bullets belong here; lists in child sections do not.
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child_recursively(NodeKind.LIST_ITEM):
            links: list[tuple[str, str]] = []
            text = clean_node(
                wxr,
                word_entry,
                list(
                    list_item.invert_find_child(
                        NodeKind.LIST, include_empty_str=True
                    )
                ),
                link_collector=links,
            )
            if text != "":
                word_entry.etymology_texts.append(text)
                word_entry.etymology_links.extend(links)

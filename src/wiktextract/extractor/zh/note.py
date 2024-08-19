from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import WordEntry


def extract_note(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        page_data[-1].notes.append(
            clean_node(wxr, page_data[-1], list_item.children)
        )

    if not level_node.contain_node(NodeKind.LIST):
        page_data[-1].notes.append(
            clean_node(wxr, page_data[-1], level_node.children)
        )

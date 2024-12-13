from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_hyphenation_section(
    wxr: WiktextractContext, page_data: list[WordEntry], level_node: LevelNode
) -> None:
    hyphenation = ""
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            hyphenation = clean_node(wxr, None, list_item.children)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.hyphenation = hyphenation

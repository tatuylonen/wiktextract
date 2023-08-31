from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = [
            child
            for child in list_item_node.children
            if not isinstance(child, WikiNode) or child.kind != NodeKind.LIST
        ]
        gloss_data = defaultdict(list)
        raw_gloss_text = clean_node(wxr, gloss_data, gloss_nodes)
        gloss_data["glosses"] = [raw_gloss_text]
        page_data[-1]["senses"].append(gloss_data)

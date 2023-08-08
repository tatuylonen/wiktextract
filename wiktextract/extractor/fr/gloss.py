from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import filter_child_wikinodes


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
) -> None:
    lang_code = page_data[-1].get("lang_code")
    for list_item_node in filter_child_wikinodes(list_node, NodeKind.LIST_ITEM):
        gloss_nodes = [
            child
            for child in list_item_node.children
            if not isinstance(child, WikiNode) or child.kind != NodeKind.LIST
        ]
        gloss_data = defaultdict(list)
        raw_gloss_text = clean_node(wxr, gloss_data, gloss_nodes)
        gloss_data["glosses"] = [raw_gloss_text]
        page_data[-1]["senses"].append(gloss_data)

from wikitextprocessor.parser import (
    LEVEL_KIND_FLAGS,
    LevelNode,
    NodeKind,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
) -> None:
    cats = {}
    e_nodes = []
    e_texts = []
    for node in level_node.children:
        if isinstance(node, WikiNode) and node.kind in LEVEL_KIND_FLAGS:
            break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            e_text = clean_node(wxr, cats, e_nodes).lstrip(": ")
            if e_text != "":
                e_texts.append(e_text)
            e_nodes.clear()
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                e_text = clean_node(wxr, cats, list_item.children)
                if e_text != "":
                    e_texts.append(e_text)
        else:
            e_nodes.append(node)

    if len(e_nodes) > 0:
        e_text = clean_node(wxr, cats, e_nodes).lstrip(": ")
        if e_text != "":
            e_texts.append(e_text)
    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            data.etymology_texts.extend(e_texts)
            data.categories.extend(cats.get("categories", []))

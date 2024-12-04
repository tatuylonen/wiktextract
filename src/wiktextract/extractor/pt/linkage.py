from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry


def extract_expression_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_expression_list_item(wxr, word_entry, list_item)


def extract_expression_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
) -> None:
    from .pos import extract_gloss_list_item

    expression_data = Linkage(word="")
    sense_nodes = []
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.BOLD:
            expression_data.word = clean_node(wxr, None, node)
        elif isinstance(node, str) and ":" in node:
            node = node.lstrip(": ")
            if node != "":
                sense_nodes.append(node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            sense_nodes.append(node)

    sense_str = clean_node(wxr, None, sense_nodes)
    if sense_str != "":
        gloss_list_item = WikiNode(NodeKind.LIST_ITEM, 0)
        gloss_list_item.children = sense_nodes
        for child_list in list_item.find_child(NodeKind.LIST):
            gloss_list_item.children.append(child_list)
        extract_gloss_list_item(wxr, expression_data, gloss_list_item)
    else:
        for child_list in list_item.find_child(NodeKind.LIST):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, expression_data, child_list_item)

    if expression_data.word != "":
        word_entry.expressions.append(expression_data)

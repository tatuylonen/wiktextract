from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    e_nodes = []
    for node in level_node.children:
        if isinstance(node, LevelNode):
            break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                e_text = clean_node(wxr, word_entry, list_item.children)
                if e_text != "":
                    word_entry.etymology_texts.append(e_text)
        elif not (
            isinstance(node, TemplateNode) and node.template_name == "improve"
        ):
            e_nodes.append(node)
    if len(e_nodes) > 0:
        e_str = clean_node(wxr, word_entry, e_nodes)
        if e_str != "":
            word_entry.etymology_texts.append(e_str)

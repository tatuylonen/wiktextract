from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    # https://ku.wiktionary.org/wiki/Wîkîferheng:Etîmolojî
    e_nodes = []
    for node in level_node.children:
        if isinstance(node, LevelNode):
            break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_item in node.find_child(NodeKind.LIST_ITEM):
                e_text = clean_node(wxr, word_entry, list_item.children)
                if e_text != "":
                    word_entry.etymology_texts.append(e_text)
    if len(e_nodes) > 0:
        e_text = clean_node(wxr, word_entry, e_nodes)
        if e_text != "":
            word_entry.etymology_texts.append(e_text)

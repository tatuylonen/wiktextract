from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from .models import WordEntry


def extract_note_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: WikiNode
) -> None:
    has_list = False
    for index, list_node in level_node.find_child(NodeKind.LIST, True):
        if not has_list:
            has_list = True
            note = clean_node(wxr, word_entry, level_node.children[:index])
            if note != "":
                word_entry.notes.append(note)
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            note = extract_node_list_item(wxr, list_item)
            if note != "":
                word_entry.notes.append(note)

    if not has_list:
        word_entry.notes.append(
            clean_node(wxr, word_entry, level_node.children)
        )


def extract_node_list_item(wxr: WiktextractContext, list_item: WikiNode) -> str:
    nodes = []
    child_str_list = []
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                child_str_list.append(
                    extract_node_list_item(wxr, child_list_item)
                )
        else:
            nodes.append(node)
    return clean_node(wxr, None, nodes) + " ".join(child_str_list)

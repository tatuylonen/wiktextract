from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_spelling_form_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        form_nodes = []
        note_str = ""
        for node in list_item.children:
            if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
                new_note_str = clean_node(wxr, None, node)
                if new_note_str.startswith("(") and new_note_str.endswith(")"):
                    note_str = new_note_str.strip("() ")
                else:
                    form_nodes.append(new_note_str)
            elif isinstance(node, str) or (
                isinstance(node, WikiNode) and node.kind == NodeKind.LINK
            ):
                form_nodes.append(node)
        form_str = clean_node(wxr, None, form_nodes)
        if len(form_str) > 0:
            word_entry.forms.append(Form(form=form_str, note=note_str))

from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, WordEntry


def extract_alt_form_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
):
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for node in list_item.children:
                if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
                    word = clean_node(wxr, None, node)
                    if word != "":
                        base_data.forms.append(
                            Form(form=word, tags=["alternative"])
                        )

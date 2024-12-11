from wikitextprocessor import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode
) -> None:
    example = Example()
    for node in list_item.children:
        if isinstance(node, WikiNode):
            match node.kind:
                case NodeKind.ITALIC:
                    example.text = clean_node(wxr, sense, node)
                case NodeKind.LIST:
                    for tr_list_item in node.find_child(NodeKind.LIST_ITEM):
                        example.translation = clean_node(
                            wxr, sense, tr_list_item.children
                        )

    if example.text != "":
        sense.examples.append(example)

from wikitextprocessor import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense, WordEntry


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item: WikiNode,
) -> None:
    italic_str = ""
    for node in list_item.children:
        if isinstance(node, WikiNode):
            if node.kind == NodeKind.ITALIC:
                italic_str = clean_node(wxr, sense, node)
            elif node.kind == NodeKind.LIST:
                for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                    e_data = Example(
                        text=italic_str,
                        translation=clean_node(
                            wxr, sense, child_list_item.children
                        ),
                    )
                    if e_data.text != "":
                        sense.examples.append(e_data)
                        italic_str = ""

    if italic_str != "":
        sense.examples.append(Example(text=italic_str))

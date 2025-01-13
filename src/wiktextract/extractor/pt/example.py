import re

from wikitextprocessor import (
    HTMLNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense


def extract_example_list_item(
    wxr: WiktextractContext,
    sense: Sense,
    list_item: WikiNode,
) -> None:
    example = Example()
    ref_nodes = []

    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
            and example.text == ""
        ):
            example.text = clean_node(wxr, None, node)
        elif isinstance(node, HTMLNode) and node.tag == "small":
            example.translation = clean_node(wxr, None, node)
            if example.translation.startswith(
                "("
            ) and example.translation.endswith(")"):
                example.translation = example.translation.strip("()")
        elif isinstance(node, TemplateNode):
            match node.template_name:
                case "OESP":
                    example.ref = clean_node(wxr, sense, node).strip("()")
                case "tradex":
                    example.text = clean_node(
                        wxr, None, node.template_parameters.get(2, "")
                    )
                    example.translation = clean_node(
                        wxr, None, node.template_parameters.get(3, "")
                    )
                    clean_node(wxr, sense, node)
                case "Ex.":
                    example.text = clean_node(
                        wxr, sense, node.template_parameters.get(1, "")
                    )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.BOLD:
            bold_str = clean_node(wxr, None, node)
            if re.fullmatch(r"\d+", bold_str) is not None:
                list_item_str = clean_node(
                    wxr, None, list(list_item.invert_find_child(NodeKind.LIST))
                )
                if list_item_str.endswith(":"):
                    ref_nodes.clear()
                    example.ref = list_item_str
                    for child_list in list_item.find_child(NodeKind.LIST):
                        for child_list_item in child_list.find_child(
                            NodeKind.LIST_ITEM
                        ):
                            example.text = clean_node(
                                wxr, None, child_list_item.children
                            )
                    break
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            ref_nodes.clear()
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                ref_nodes.append(child_list_item.children)
        else:
            ref_nodes.append(node)

    if example.text != "":
        if example.ref == "":
            example.ref = clean_node(wxr, sense, ref_nodes).strip(":() \n")
        sense.examples.append(example)
    else:
        extract_example_text_list(wxr, sense, list_item)


def extract_example_text_list(
    wxr: WiktextractContext,
    sense: Sense,
    list_item: WikiNode,
) -> None:
    list_item_text = clean_node(
        wxr, sense, list(list_item.invert_find_child(NodeKind.LIST))
    )
    example = Example(text=list_item_text)
    if "-" in example.text:
        tr_start = example.text.index("-")
        example.translation = example.text[tr_start + 1 :].strip()
        example.text = example.text[:tr_start].strip()
        sense.examples.append(example)

from wikitextprocessor.parser import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Example, Sense


def extract_example_list_item(
    wxr: WiktextractContext,
    sense: Sense,
    list_item: WikiNode,
    parent_list_text: str = "",
) -> None:
    # https://ja.wiktionary.org/wiki/Wiktionary:用例#用例を示す形式
    if any(
        child.contain_node(NodeKind.BOLD) or child.kind == NodeKind.BOLD
        for child in list_item.children
        if isinstance(child, WikiNode) and child.kind != NodeKind.LIST
    ) or not list_item.contain_node(NodeKind.LIST):
        # has bold node or doesn't have list child node
        expanded_nodes = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                list(list_item.invert_find_child(NodeKind.LIST))
            ),
            expand_all=True,
        )
        ruby, no_ruby = extract_ruby(wxr, expanded_nodes.children)
        example = Example(text=clean_node(wxr, None, no_ruby), ruby=ruby)
        for tr_list_item in list_item.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            example.translation = clean_node(wxr, None, tr_list_item.children)
        if len(parent_list_text) > 0:
            example.ref = parent_list_text
        elif "（" in example.text:
            ref_start = example.text.rindex("（")
            example.ref = example.text[ref_start:]
            example.text = example.text[:ref_start].strip()
            for ref_tag in expanded_nodes.find_html_recursively("ref"):
                example.ref += " " + clean_node(wxr, None, ref_tag.children)
        sense.examples.append(example)
    else:
        list_item_text = clean_node(
            wxr, None, list(list_item.invert_find_child(NodeKind.LIST))
        )
        for ref_tag in list_item.find_html("ref"):
            list_item_text += " " + clean_node(wxr, None, ref_tag.children)
        for next_list_item in list_item.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            extract_example_list_item(
                wxr, sense, next_list_item, list_item_text
            )

from collections import defaultdict
from typing import Dict

from wikitextprocessor import NodeKind, WikiNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby

DESCENDANT_TEMPLATES = frozenset(["desc", "descendant"])


def extract_descendants(
    wxr: WiktextractContext,
    level_node: WikiNode,
    parent_data: Dict,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
            extract_descendant_list_item(wxr, list_item_node, parent_data)


def extract_descendant_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    parent_data: Dict,
) -> None:
    lang_code = ""
    lang_name = ""
    descendant_data = defaultdict(list)
    for template_node in list_item_node.find_child(NodeKind.TEMPLATE):
        expanded_template = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(template_node), expand_all=True
        )
        if template_node.template_name.lower() in DESCENDANT_TEMPLATES:
            lang_code = template_node.template_parameters.get(1)
            descendant_data["lang_code"] = lang_code
        ruby_data, nodes_without_ruby = extract_ruby(
            wxr, expanded_template.children
        )
        if len(ruby_data) > 0:
            descendant_data["ruby"] = ruby_data
        for child_index, child_node in enumerate(nodes_without_ruby):
            if isinstance(child_node, str) and child_node.endswith("："):
                lang_name = child_node.strip(" ：")
                descendant_data["lang_name"] = lang_name
            elif (
                isinstance(child_node, WikiNode)
                and child_node.kind == NodeKind.HTML
            ):
                if child_node.tag == "span":
                    class_names = child_node.attrs.get("class", "")
                    if (
                        "Latn" in class_names or "tr" in class_names
                    ) and "word" in descendant_data:
                        # template:ja-r
                        descendant_data["roman"] = clean_node(
                            wxr, None, child_node
                        )
                    elif "lang" in child_node.attrs:
                        if "word" in descendant_data:
                            parent_data["descendants"].append(descendant_data)
                            descendant_data = defaultdict(
                                list,
                                {
                                    "lang_code": lang_code,
                                    "lang_name": lang_name,
                                },
                            )
                            if len(ruby_data) > 0:
                                descendant_data["ruby"] = ruby_data
                        descendant_data["word"] = clean_node(
                            wxr, None, child_node
                        )
                    if "qualifier-content" in class_names:
                        descendant_data["tags"].append(
                            clean_node(wxr, None, child_node)
                        )
                elif child_node.tag == "i":
                    # template:zh-l
                    for span_tag in child_node.find_html(
                        "span", attr_name="class", attr_value="Latn"
                    ):
                        descendant_data["roman"] = clean_node(
                            wxr, None, span_tag
                        )

        if "word" in descendant_data:
            parent_data["descendants"].append(descendant_data)

    if list_item_node.contain_node(NodeKind.LIST):
        extract_descendants(
            wxr,
            list_item_node,
            descendant_data if "word" in descendant_data else parent_data,
        )

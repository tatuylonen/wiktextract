import re
from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from ..share import contains_list, filter_child_wikinodes
from .example import extract_examples


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
    gloss_data: Dict[str, List[str]],
) -> None:
    lang_code = page_data[-1].get("lang_code")
    for list_item_node in filter_child_wikinodes(list_node, NodeKind.LIST_ITEM):
        gloss_nodes = [
            child
            for child in list_item_node.children
            if not isinstance(child, WikiNode) or child.kind != NodeKind.LIST
        ]
        if lang_code == "ja":
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_nodes), expand_all=True
            )
            ruby_data, nodes_without_ruby = extract_ruby(
                wxr, expanded_node.children
            )
            raw_gloss_text = clean_node(wxr, None, nodes_without_ruby)
        else:
            ruby_data = []
            raw_gloss_text = clean_node(wxr, None, gloss_nodes)
        new_gloss_data = merge_gloss_data(
            gloss_data, extract_gloss_and_tags(raw_gloss_text)
        )
        if len(ruby_data) > 0:
            new_gloss_data["ruby"] = ruby_data

        has_nested_gloss = False
        if contains_list(list_item_node.children):
            for child_node in filter_child_wikinodes(
                list_item_node, NodeKind.LIST
            ):
                if child_node.args.endswith("#"):  # nested gloss
                    has_nested_gloss = True
                    extract_gloss(wxr, page_data, child_node, new_gloss_data)
                else:  # example list
                    extract_examples(wxr, new_gloss_data, child_node)

        if not has_nested_gloss:
            page_data[-1]["senses"].append(new_gloss_data)


def merge_gloss_data(
    data_a: Dict[str, List[str]], data_b: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    new_data = defaultdict(list)
    for data in data_a, data_b:
        for key, value in data.items():
            new_data[key].extend(value)
    return new_data


def extract_gloss_and_tags(raw_gloss: str) -> Dict[str, List[str]]:
    left_brackets = ("(", "（")
    right_brackets = (")", "）")
    if raw_gloss.startswith(left_brackets) or raw_gloss.endswith(
        right_brackets
    ):
        tags = []
        split_tag_regex = r", ?|，|或"
        front_tag_end = -1
        rear_tag_start = len(raw_gloss)
        for index, left_bracket in enumerate(left_brackets):
            if raw_gloss.startswith(left_bracket):
                front_tag_end = raw_gloss.find(right_brackets[index])
                front_label = raw_gloss[1:front_tag_end]
                tags += re.split(split_tag_regex, front_label)
        for index, right_bracket in enumerate(right_brackets):
            if raw_gloss.endswith(right_bracket):
                rear_tag_start = raw_gloss.rfind(left_brackets[index])
                rear_label = raw_gloss.rstrip("".join(right_brackets))[
                    rear_tag_start + 1 :
                ]
                tags += re.split(split_tag_regex, rear_label)

        gloss = raw_gloss[front_tag_end + 1 : rear_tag_start].strip()
        return defaultdict(
            list, {"glosses": [gloss], "raw_glosses": [raw_gloss], "tags": tags}
        )
    else:
        return defaultdict(list, {"glosses": [raw_gloss]})

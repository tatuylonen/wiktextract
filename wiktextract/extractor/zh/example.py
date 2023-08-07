from collections import defaultdict
from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby
from ..share import contains_list, strip_nodes


def extract_examples(
    wxr: WiktextractContext,
    sense_data: Dict,
    node: Union[WikiNode, List[WikiNode]],
) -> None:
    if isinstance(node, list):
        for n in node:
            extract_examples(wxr, sense_data, n)
    elif isinstance(node, WikiNode):
        if node.kind == NodeKind.LIST_ITEM:
            example_data = defaultdict(list, {"type": "example"})
            # example text in the nested list
            # https://zh.wiktionary.org/wiki/%, the second example
            if contains_list(node.children):
                extract_example_list(wxr, node, example_data)
            else:
                # parse example templates
                for child in strip_nodes(node.children):
                    if (
                        isinstance(child, WikiNode)
                        and child.kind == NodeKind.TEMPLATE
                    ):
                        template_name = child.args[0][0].strip()
                        if template_name.startswith(("quote-", "RQ:")):
                            extract_quote_templates(wxr, child, example_data)
                        elif template_name in {"ja-x", "ja-usex"}:
                            extract_template_ja_usex(wxr, child, example_data)
                        elif template_name in {"zh-x", "zh-usex"}:
                            extract_template_zh_usex(wxr, child, example_data)
                        elif template_name in {"ux", "eg", "usex"}:
                            extract_template_ux(wxr, child, example_data)
                        elif template_name == "uxi":
                            extract_template_uxi(wxr, child, example_data)
                        else:
                            example_data["text"] = clean_node(wxr, None, child)

            if "text" in example_data or "texts" in example_data:
                sense_data["examples"].append(example_data)
        else:
            extract_examples(wxr, sense_data, node.children)


def extract_example_list(
    wxr: WiktextractContext, node: WikiNode, example_data: Dict
) -> None:
    for index, child_node in enumerate(node.children):
        if (
            isinstance(child_node, WikiNode)
            and child_node.kind == NodeKind.LIST
        ):
            example_data["type"] = "quote"
            example_data["ref"] = clean_node(wxr, None, node.children[:index])
            example_data["text"] = clean_node(
                wxr, None, child_node.children[0].children
            )


def extract_quote_templates(
    wxr: WiktextractContext, node: WikiNode, example_data: Dict
) -> None:
    """
    Process template `quote-book` and "RQ:*".
    """
    example_data["type"] = "quote"
    expanded_text = clean_node(wxr, None, node)
    for line_num, expanded_line in enumerate(expanded_text.splitlines()):
        if line_num == 0:
            key = "ref"
        elif line_num == 1:
            key = "text"
        elif line_num == 2 and any(
            template_arg[0].startswith("transliteration=")
            for template_arg in node.args
            if len(template_arg) > 0 and isinstance(template_arg[0], str)
        ):
            key = "roman"
        else:
            key = "translation"

        if expanded_line != "（請為本引文添加中文翻譯）":
            example_data[key] = expanded_line


def extract_template_ja_usex(
    wxr: WiktextractContext, node: WikiNode, example_data: Dict
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    ruby_data, node_without_ruby = extract_ruby(wxr, expanded_node.children)
    expanded_text = clean_node(wxr, None, node_without_ruby)
    for line_num, expanded_line in enumerate(expanded_text.splitlines()):
        if line_num == 0:
            key = "text"
        elif line_num == 1:
            key = "roman"
        else:
            key = "translation"
        example_data[key] = expanded_line
    if len(ruby_data) > 0:
        example_data["ruby"] = ruby_data


def extract_template_zh_usex(
    wxr: WiktextractContext, node: WikiNode, example_data: Dict
) -> None:
    expanded_text = clean_node(wxr, None, node)
    if "―" in expanded_text:
        for index, split_text in enumerate(expanded_text.split("―")):
            if index == 0:
                for example_text in split_text.split(" / "):
                    example_data["texts"].append(example_text.strip())
            elif index == 1:
                example_data["roman"] = split_text.strip()
        return

    for expanded_line in expanded_text.splitlines():
        if expanded_line.endswith("體]"):
            # expanded simplified or traditional Chinese
            # example sentence usually ends with
            # "繁體]" or "簡體]"
            example_data["texts"].append(expanded_line)
        elif expanded_line.endswith("]"):
            example_data["roman"] = expanded_line
        elif expanded_line.startswith("來自："):
            example_data["ref"] = expanded_line[3:]
            example_data["type"] = "quote"
        else:
            example_data["translation"] = expanded_line


def extract_template_ux(
    wxr: WiktextractContext, node: WikiNode, example_data: Dict
) -> None:
    expanded_text = clean_node(wxr, None, node)
    if " ― " in expanded_text:
        extract_template_uxi_text(expanded_text, example_data)
        return

    lines = expanded_text.splitlines()
    for line_num, expanded_line in enumerate(lines):
        if line_num == 0:
            key = "text"
        elif line_num == 1:
            if line_num == len(lines) - 1:
                key = "translation"
            else:
                key = "roman"
        else:
            key = "translation"
        example_data[key] = expanded_line


def extract_template_uxi(
    wxr: WiktextractContext, node: WikiNode, example_data: Dict
) -> None:
    expanded_text = clean_node(wxr, None, node)
    extract_template_uxi_text(expanded_text, example_data)


def extract_template_uxi_text(expanded_text: str, example_data: Dict) -> None:
    parts = expanded_text.split(" ― ")
    for index, part in enumerate(parts):
        if index == 0:
            key = "text"
        elif index == 1:
            if index == len(parts) - 1:
                key = "translation"
            else:
                key = "roman"
        else:
            key = "translation"
        example_data[key] = part

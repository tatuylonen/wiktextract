from collections import defaultdict
from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_linkage(
    wxr: WiktextractContext,
    page_data: List[Dict],
    level_node: WikiNode,
    linkage_type: str,
) -> None:
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        linkage_data = defaultdict(list)
        for index, child_node in enumerate(
            list_item_node.filter_empty_str_child()
        ):
            if index == 0:
                if (
                    isinstance(child_node, WikiNode)
                    and child_node.kind == NodeKind.TEMPLATE
                ):
                    process_linkage_template(wxr, child_node, linkage_data)
                else:
                    linkage_data["word"] = clean_node(wxr, None, child_node)
            else:
                tag = clean_node(wxr, page_data[-1], child_node).strip("()")
                if tag.startswith("— "):
                    linkage_data["translation"] = tag.removeprefix("— ")
                else:
                    linkage_data["tags"].append(tag)

        page_data[-1][linkage_type].append(linkage_data)


def process_linkage_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Dict[str, Union[str, List[str]]],
) -> None:
    if node.template_name == "lien":
        process_lien_template(wxr, node, linkage_data)
    elif node.template_name.startswith("zh-lien"):
        process_zh_lien_template(wxr, node, linkage_data)


def process_lien_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Dict[str, Union[str, List[str]]],
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:lien
    word = node.template_parameters.get(1)
    if "dif" in node.template_parameters:
        word = node.template_parameters.get("dif")
    linkage_data["word"] = word
    if "tr" in node.template_parameters:
        linkage_data["roman"] = node.template_parameters.get("tr")
    if "sens" in node.template_parameters:
        linkage_data["translation"] = node.template_parameters.get("sens")


def process_zh_lien_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Dict[str, Union[str, List[str]]],
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:zh-lien
    linkage_data["word"] = node.template_parameters.get(1)
    linkage_data["roman"] = node.template_parameters.get(2)  # pinyin
    traditional_form = node.template_parameters.get(3, "")
    if len(traditional_form) > 0:
        linkage_data["alt"] = traditional_form

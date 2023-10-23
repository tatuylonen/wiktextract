from collections import defaultdict
from typing import Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import split_tag_text


def extract_linkage(
    wxr: WiktextractContext,
    page_data: List[Dict],
    level_node: WikiNode,
    linkage_type: str,
) -> None:
    sense_text = ""
    sense_index = 0
    for template_or_list_node in level_node.find_child_recursively(
        NodeKind.LIST_ITEM | NodeKind.TEMPLATE
    ):
        # list table start template: https://fr.wiktionary.org/wiki/Modèle:(
        if (
            isinstance(template_or_list_node, TemplateNode)
            and template_or_list_node.template_name == "("
        ):
            sense_text = clean_node(
                wxr, None, template_or_list_node.template_parameters.get(1, "")
            )
            sense_index_text = template_or_list_node.template_parameters.get(
                2, "0"
            )
            if sense_index_text.isdigit():
                sense_index = int(sense_index_text)
            continue

        linkage_data = defaultdict(list)
        if len(sense_text) > 0:
            linkage_data["sense"] = sense_text
        if sense_index != 0:
            linkage_data["sense_index"] = sense_index
        pending_tag = ""
        for index, child_node in enumerate(  # remove nested lists
            template_or_list_node.invert_find_child(NodeKind.LIST)
        ):
            if index == 0 or "word" not in linkage_data:
                if isinstance(child_node, TemplateNode):
                    process_linkage_template(wxr, child_node, linkage_data)
                else:
                    linkage_data["word"] = clean_node(wxr, None, child_node)
            else:
                tag_text = (
                    child_node
                    if isinstance(child_node, str)
                    else clean_node(wxr, page_data[-1], child_node)
                )
                if tag_text.strip().startswith(
                    "("
                ) and not tag_text.strip().endswith(")"):
                    pending_tag = tag_text
                    continue
                elif not tag_text.strip().startswith(
                    "("
                ) and tag_text.strip().endswith(")"):
                    tag_text = pending_tag + tag_text
                    pending_tag = ""
                elif tag_text.strip() == ",":
                    # list item has more than one word
                    page_data[-1][linkage_type].append(linkage_data)
                    linkage_data = defaultdict(list)
                    continue
                elif len(pending_tag) > 0:
                    pending_tag += tag_text
                    continue

                for tag in split_tag_text(tag_text):
                    if tag.startswith("— "):
                        linkage_data["translation"] = tag.removeprefix("— ")
                    elif len(tag) > 0:
                        linkage_data["tags"].append(tag)

        if "word" in linkage_data:
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
    # link word template: https://fr.wiktionary.org/wiki/Modèle:lien
    word = clean_node(
        wxr,
        None,
        node.template_parameters.get("dif", node.template_parameters.get(1)),
    )
    linkage_data["word"] = word
    if "tr" in node.template_parameters:
        linkage_data["roman"] = clean_node(
            wxr, None, node.template_parameters.get("tr")
        )
    if "sens" in node.template_parameters:
        linkage_data["translation"] = clean_node(
            wxr, None, node.template_parameters.get("sens")
        )


def process_zh_lien_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Dict[str, Union[str, List[str]]],
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:zh-lien
    linkage_data["word"] = clean_node(
        wxr, None, node.template_parameters.get(1)
    )
    linkage_data["roman"] = clean_node(
        wxr, None, node.template_parameters.get(2)
    )  # pinyin
    traditional_form = clean_node(
        wxr, None, node.template_parameters.get(3, "")
    )
    if len(traditional_form) > 0:
        linkage_data["alt"] = traditional_form

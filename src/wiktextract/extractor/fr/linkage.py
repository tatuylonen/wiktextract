import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import capture_text_in_parentheses
from .models import Linkage, WordEntry
from .section_types import LINKAGE_SECTIONS


def extract_linkage(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    section_type: str,
) -> None:
    if section_type == "dérivés autres langues":
        process_derives_autres_list(wxr, page_data, level_node)
    else:
        process_linkage_list(
            wxr,
            page_data,
            level_node,
            LINKAGE_SECTIONS[section_type],
        )


def process_derives_autres_list(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
):
    # drrive to other languages list
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        lang_code = ""
        lang_name = ""
        for node in list_item.find_child(NodeKind.TEMPLATE | NodeKind.LINK):
            if isinstance(node, TemplateNode) and node.template_name == "L":
                lang_code = node.template_parameters.get(1)
                lang_name = clean_node(wxr, None, node)
            elif node.kind == NodeKind.LINK or (
                isinstance(node, TemplateNode) and node.template_name == "lien"
            ):
                word = clean_node(wxr, None, node)
                page_data[-1].derived.append(
                    Linkage(lang_code=lang_code, lang=lang_name, word=word)
                )


def process_linkage_list(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
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
            if (
                isinstance(sense_index_text, str)
                and sense_index_text.isdecimal()
            ):
                sense_index = int(sense_index_text)
            continue
        # sense could also be in ";" description list
        if (
            template_or_list_node.kind == NodeKind.LIST_ITEM
            and template_or_list_node.sarg in {";", ":"}
        ):
            sense_text = clean_node(wxr, None, template_or_list_node.children)
            index_pattern = r"\s*\((?:sens\s*)?(\d+)\)$"
            m = re.search(index_pattern, sense_text)
            if m is not None:
                sense_text = re.sub(index_pattern, "", sense_text)
                sense_index = int(m.group(1))
            continue

        linkage_data = Linkage(word="")
        if len(sense_text) > 0:
            linkage_data.sense = sense_text
        if sense_index != 0:
            linkage_data.sense_index = sense_index
        pending_tag = ""
        for index, child_node in enumerate(  # remove nested lists
            template_or_list_node.invert_find_child(NodeKind.LIST)
        ):
            if index == 0 and isinstance(child_node, TemplateNode):
                process_linkage_template(wxr, child_node, linkage_data)
            elif (
                isinstance(child_node, WikiNode)
                and child_node.kind == NodeKind.LINK
            ):
                linkage_data.word = clean_node(wxr, None, child_node)
            elif (
                isinstance(child_node, WikiNode)
                and child_node.kind == NodeKind.ITALIC
            ):
                current_sense = clean_node(wxr, None, child_node).strip("()")
                if current_sense.isdecimal():
                    linkage_data.sense_index = int(current_sense)
                else:
                    linkage_data.sense = current_sense
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
                elif tag_text.strip() in {",", "/"}:
                    # list item has more than one word
                    pre_data = getattr(page_data[-1], linkage_type)
                    pre_data.append(linkage_data)
                    linkage_data = Linkage(word="")
                    continue
                elif len(pending_tag) > 0:
                    pending_tag += tag_text
                    continue

                if tag_text.strip().startswith("— "):
                    linkage_data.translation = tag_text.strip().removeprefix(
                        "— "
                    )
                else:
                    tags, _ = capture_text_in_parentheses(tag_text)
                    for tag in tags:
                        if tag.isdecimal():
                            linkage_data.sense_index = int(tag)
                        else:
                            linkage_data.raw_tags.append(tag)

        if len(linkage_data.word) > 0:
            pre_data = getattr(page_data[-1], linkage_type)
            pre_data.append(linkage_data)


def process_linkage_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Linkage,
) -> None:
    if node.template_name in {"lien", "l"}:
        process_lien_template(wxr, node, linkage_data)
    elif node.template_name.startswith("zh-lien"):
        process_zh_lien_template(wxr, node, linkage_data)


def process_lien_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Linkage,
) -> None:
    # link word template: https://fr.wiktionary.org/wiki/Modèle:lien
    word = clean_node(
        wxr,
        None,
        node.template_parameters.get("dif", node.template_parameters.get(1)),
    )
    linkage_data.word = word
    if "tr" in node.template_parameters:
        linkage_data.roman = clean_node(
            wxr, None, node.template_parameters.get("tr")
        )
    if "sens" in node.template_parameters:
        linkage_data.translation = clean_node(
            wxr, None, node.template_parameters.get("sens")
        )


def process_zh_lien_template(
    wxr: WiktextractContext,
    node: TemplateNode,
    linkage_data: Linkage,
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:zh-lien
    linkage_data.word = clean_node(wxr, None, node.template_parameters.get(1))
    linkage_data.roman = clean_node(
        wxr, None, node.template_parameters.get(2)
    )  # pinyin
    traditional_form = clean_node(
        wxr, None, node.template_parameters.get(3, "")
    )
    if len(traditional_form) > 0:
        linkage_data.alt = traditional_form

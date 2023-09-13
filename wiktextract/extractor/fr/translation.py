from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_translation(
    wxr: WiktextractContext, page_data: List[Dict], level_node: WikiNode
) -> None:
    base_translation_data = defaultdict(list)
    for level_node_child in level_node.filter_empty_str_child():
        if isinstance(level_node_child, WikiNode):
            if level_node_child.kind == NodeKind.TEMPLATE:
                # get sense from "trad-début" template
                process_translation_templates(
                    wxr, level_node_child, page_data, base_translation_data
                )
            elif level_node_child.kind == NodeKind.LIST:
                for list_item_node in level_node_child.find_child(
                    NodeKind.LIST_ITEM
                ):
                    previous_node = None
                    for child_node in list_item_node.filter_empty_str_child():
                        if isinstance(child_node, WikiNode):
                            if child_node.kind == NodeKind.TEMPLATE:
                                process_translation_templates(
                                    wxr,
                                    child_node,
                                    page_data,
                                    base_translation_data,
                                )
                            elif child_node.kind == NodeKind.ITALIC:
                                process_italic_node(
                                    wxr, child_node, previous_node, page_data
                                )
                            previous_node = child_node


def process_italic_node(
    wxr: WiktextractContext,
    italic_node: WikiNode,
    previous_node: WikiNode,
    page_data: List[Dict],
) -> None:
    # add italic text after a "trad" template as a tag
    tag = clean_node(wxr, None, italic_node)
    if (
        tag.startswith("(")
        and tag.endswith(")")
        and previous_node.kind == NodeKind.TEMPLATE
        and previous_node.template_name.startswith("trad")
        and len(page_data[-1].get("translations", [])) > 0
    ):
        page_data[-1]["translations"][-1]["tags"].append(tag.strip("()"))


def process_translation_templates(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    page_data: List[Dict],
    base_translation_data: Dict[str, str],
) -> None:
    if template_node.template_name == "trad-début":
        # translation box start: https://fr.wiktionary.org/wiki/Modèle:trad-début
        translation_sense_wikitext = template_node.template_parameters.get(
            1, ""
        )
        if len(translation_sense_wikitext) > 0:
            base_translation_data["sense"] = clean_node(
                wxr, None, translation_sense_wikitext
            )
    elif template_node.template_name == "T":
        # Translation language: https://fr.wiktionary.org/wiki/Modèle:T
        base_translation_data["code"] = template_node.template_parameters.get(1)
        base_translation_data["lang"] = clean_node(
            wxr, page_data[-1], template_node
        )
    elif template_node.template_name.startswith("trad"):
        # Translation term: https://fr.wiktionary.org/wiki/Modèle:trad
        translation_term = clean_node(
            wxr, None, template_node.template_parameters.get(2)
        )
        translation_roman = clean_node(
            wxr,
            None,
            (
                template_node.template_parameters.get(
                    "tr", template_node.template_parameters.get("R", "")
                )
            ),
        )
        # traditional writing of Chinese and Korean word
        translation_traditional_writing = clean_node(
            wxr, None, template_node.template_parameters.get("tradi", "")
        )
        translation_data = base_translation_data.copy()
        translation_data["word"] = translation_term
        if len(translation_roman) > 0:
            translation_data["roman"] = translation_roman
        if len(translation_traditional_writing) > 0:
            translation_data[
                "traditional_writing"
            ] = translation_traditional_writing
        page_data[-1]["translations"].append(translation_data)
    elif len(page_data[-1].get("translations", [])) > 0:
        tag = clean_node(wxr, None, template_node).strip("()")
        page_data[-1]["translations"][-1]["tags"].append(tag)

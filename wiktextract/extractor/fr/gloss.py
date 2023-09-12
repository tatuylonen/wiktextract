from collections import defaultdict
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import TemplateNode

from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[Dict],
    list_node: WikiNode,
) -> None:
    for list_item_node in list_node.find_child(NodeKind.LIST_ITEM):
        gloss_nodes = list(list_item_node.invert_find_child(NodeKind.LIST))
        gloss_data = defaultdict(list)
        gloss_start = 0
        # process modifier, theme tempaltes before gloss text
        # https://fr.wiktionary.org/wiki/Wiktionnaire:Liste de tous les modèles/Précisions de sens
        if (
            len(gloss_nodes) > 0
            and isinstance(gloss_nodes[0], WikiNode)
            and gloss_nodes[0].kind == NodeKind.TEMPLATE
        ):
            gloss_start = 1
            for index, gloss_node in enumerate(gloss_nodes[1:], 1):
                if (
                    not isinstance(gloss_node, WikiNode)
                    or gloss_node.kind != NodeKind.TEMPLATE
                    # template "variante de" is not a modifier
                    # https://fr.wiktionary.org/wiki/Modèle:variante_de
                    or gloss_node.template_name == "variante de"
                ):
                    gloss_start = index
                    break
                else:
                    gloss_start = index + 1
            for mod_template in gloss_nodes[:gloss_start]:
                gloss_data["tags"].append(
                    clean_node(wxr, gloss_data, mod_template).strip("()")
                )

        gloss_text = clean_node(wxr, gloss_data, gloss_nodes[gloss_start:])
        gloss_data["glosses"] = [gloss_text]
        extract_examples(wxr, gloss_data, list_item_node)
        page_data[-1]["senses"].append(gloss_data)


def extract_examples(
    wxr: WiktextractContext,
    gloss_data: Dict,
    gloss_list_node: WikiNode,
) -> None:
    for example_node in gloss_list_node.find_child_recursively(
        NodeKind.LIST_ITEM
    ):
        example_node_children = list(example_node.filter_empty_str_child())
        if len(example_node_children) == 0:
            continue
        first_child = example_node_children[0]
        if (
            isinstance(first_child, WikiNode)
            and first_child.kind == NodeKind.TEMPLATE
            and first_child.template_name == "exemple"
        ):
            process_exemple_template(wxr, first_child, gloss_data)
        else:
            example_nodes = []
            source_template = None
            for example_template in example_node.find_child(NodeKind.TEMPLATE):
                if example_template.template_name == "source":
                    source_template = example_template
            example_nodes = [
                node
                for node in example_node_children
                if node != source_template
            ]
            example_data = {"type": "example"}
            example_data["text"] = clean_node(wxr, None, example_nodes)
            if source_template is not None:
                example_data["source"] = clean_node(
                    wxr, None, source_template
                ).strip("— ()")
                example_data["type"] = "quotation"
            gloss_data["examples"].append(example_data)


def process_exemple_template(
    wxr: WiktextractContext, node: TemplateNode, gloss_data: Dict
) -> None:
    # https://fr.wiktionary.org/wiki/Modèle:exemple
    # https://fr.wiktionary.org/wiki/Modèle:ja-exemple
    # https://fr.wiktionary.org/wiki/Modèle:zh-exemple
    text = clean_node(wxr, None, node.template_parameters.get(1, ""))
    translation = clean_node(
        wxr,
        None,
        node.template_parameters.get(
            2, node.template_parameters.get("sens", "")
        ),
    )
    transcription = clean_node(
        wxr,
        None,
        node.template_parameters.get(3, node.template_parameters.get("tr", "")),
    )
    source = clean_node(wxr, None, node.template_parameters.get("source", ""))
    example_data = {"type": "example"}
    if len(text) > 0:
        example_data["text"] = clean_node(wxr, None, text)
    if len(translation) > 0:
        example_data["translation"] = clean_node(wxr, None, translation)
    if len(transcription) > 0:
        example_data["roman"] = clean_node(wxr, None, transcription)
    if len(source) > 0:
        example_data["source"] = clean_node(wxr, None, source)
        example_data["type"] = "quotation"
    if len(example_data) > 0:
        gloss_data["examples"].append(example_data)

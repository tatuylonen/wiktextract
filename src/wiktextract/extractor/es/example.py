import re
from typing import Optional, Union

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import WikiNodeChildrenList
from wiktextract.extractor.es.models import Example, Sense
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

EXAMPLE_TEMPLATE_KEY_MAPPING = {
    "título": "title",
    "nombre": "first_name",
    "apellidos": "last_name",
    "páginas": "pages",
    "URL": "url",
    "año": "year",
    "capítulo": "chapter",
    "fecha": "date",
    "editorial": "journal",
    "editor": "editor",
    "ubicación": "place",
}


def clean_text_and_url_from_text_nodes(
    wxr: WiktextractContext, nodes: WikiNodeChildrenList
) -> tuple[str, Optional[str]]:
    if not nodes:
        return "", None

    url_node = None
    text_nodes_without_url = []
    for n in nodes:
        if isinstance(n, WikiNode) and n.kind == NodeKind.URL:
            url_node = n
        else:
            text_nodes_without_url.append(n)

    url = None
    if url_node:
        url = clean_node(wxr, {}, url_node)

    text = clean_node(wxr, {}, text_nodes_without_url)

    return text, url


def add_template_params_to_example(
    wxr: WiktextractContext,
    params: Optional[
        dict[
            Union[str, int],
            Union[str, WikiNode, list[Union[str, WikiNode]]],
        ]
    ],
    example: Example,
):
    for key in params.keys():
        if isinstance(key, int):
            continue

        ref_key = EXAMPLE_TEMPLATE_KEY_MAPPING.get(key, key)
        if ref_key in example.model_fields:
            setattr(example, ref_key, clean_node(wxr, {}, params.get(key)))
        else:
            wxr.wtp.debug(
                f"Unknown key {key} in example template {params}",
                sortid="extractor/es/example/add_template_params_to_reference/73",
            )


def process_example_template(
    wxr: WiktextractContext,
    sense_data: Sense,
    template_node: WikiNode,
):
    params = template_node.template_parameters
    text_nodes = params.get(1)

    # Remove url node before cleaning text nodes
    text, url = clean_text_and_url_from_text_nodes(wxr, text_nodes)

    if not text:
        return

    example = Example(text=text)

    if url is not None:
        example.url = url

    if template_node.template_name == "ejemplo_y_trad":
        example.translation = clean_node(wxr, {}, params.get(2))

    add_template_params_to_example(wxr, params, example)

    sense_data.examples.append(example)


def extract_example(
    wxr: WiktextractContext,
    sense_data: Sense,
    nodes: WikiNodeChildrenList,
):
    rest: WikiNodeChildrenList = []

    for node in nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.TEMPLATE:
            if node.template_name in ["ejemplo", "ejemplo_y_trad"]:
                process_example_template(wxr, sense_data, node)
            else:
                rest.append(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.URL:
            if len(sense_data.examples) > 0:
                sense_data.examples[-1].url = clean_node(wxr, {}, node)
        else:
            rest.append(node)

    if not sense_data.examples and rest:
        example = Example(text=clean_node(wxr, {}, rest))
        sense_data.examples.append(example)
    elif rest:
        wxr.wtp.debug(
            f"Unprocessed nodes from example group: {rest}",
            sortid="extractor/es/example/extract_example/87",
        )


def process_example_list(
    wxr: WiktextractContext,
    sense_data: Sense,
    list_item: WikiNode,
):
    for sub_list_item in list_item.find_child_recursively(NodeKind.LIST_ITEM):
        text_nodes: WikiNodeChildrenList = []
        template_nodes: list[WikiNode] = []
        for child in sub_list_item.children:
            if isinstance(child, WikiNode) and child.kind == NodeKind.TEMPLATE:
                template_nodes.append(child)
            else:
                text_nodes.append(child)

        text, url = clean_text_and_url_from_text_nodes(wxr, text_nodes)

        if len(text) == 0:
            continue

        example = Example(text=text)
        if url is not None:
            example.url = url

        for template_node in template_nodes:
            if template_node.template_name == "cita libro":
                add_template_params_to_example(
                    wxr, template_node.template_parameters, example
                )

        sense_data.examples.append(example)

    # If no example was found in sublists, assume example is in list_item.children directly.
    if not sense_data.examples:
        text, url = clean_text_and_url_from_text_nodes(wxr, list_item.children)
        text = re.sub(r"^(Ejemplos?:?)", "", text).strip()
        if len(text) == 0:
            return
        example = Example(text=text)
        if url is not None:
            example.url = url
        sense_data.examples.append(example)

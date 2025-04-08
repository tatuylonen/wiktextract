from wikitextprocessor.parser import (
    NodeKind,
    TemplateNode,
    WikiNode,
    WikiNodeChildrenList,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .models import Example, Sense, TemplateData


def process_ejemplo_template(
    wxr: WiktextractContext,
    sense_data: Sense,
    template_node: TemplateNode,
):
    # https://es.wiktionary.org/wiki/Plantilla:ejemplo
    # https://es.wiktionary.org/wiki/Módulo:ejemplo
    example_data = Example(text="")
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    for span_tag in expanded_template.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class")
        if "cita" == span_class:
            if (
                len(span_tag.children) > 1
                and isinstance(span_tag.children[-1], WikiNode)
                and span_tag.children[-1].kind == NodeKind.URL
            ):
                example_data.text = clean_node(
                    wxr, None, span_tag.children[:-1]
                )
                calculate_bold_offsets(
                    wxr,
                    wxr.wtp.parse(
                        wxr.wtp.node_to_wikitext(span_tag.children[:-1])
                    ),
                    example_data.text,
                    example_data,
                    "bold_text_offsets",
                    extra_node_kind=NodeKind.ITALIC,
                )
                example_data.ref = clean_node(wxr, None, span_tag.children[-1])
            else:
                example_data.text = clean_node(wxr, None, span_tag)
                calculate_bold_offsets(
                    wxr,
                    span_tag,
                    example_data.text,
                    example_data,
                    "bold_text_offsets",
                    extra_node_kind=NodeKind.ITALIC,
                )
        elif "trad" == span_class:
            example_data.translation = clean_node(
                wxr, None, span_tag
            ).removeprefix("Traducción: ")
        elif "ref" == span_class:
            example_data.ref = clean_node(wxr, None, span_tag)

    if len(example_data.text) == 0:
        first_arg = template_node.template_parameters.get(1, "")
        example_data.text = clean_node(wxr, None, first_arg)
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(first_arg)),
            example_data.text,
            example_data,
            "bold_text_offsets",
            extra_node_kind=NodeKind.ITALIC,
        )

    if len(example_data.text) > 0:
        template_data = TemplateData(
            expansion=clean_node(wxr, None, expanded_template)
        )
        template_data.name = template_node.template_name
        for arg, value in template_node.template_parameters.items():
            template_data.args[str(arg)] = clean_node(wxr, None, value)
        example_data.example_templates.append(template_data)
        sense_data.examples.append(example_data)


def extract_example(
    wxr: WiktextractContext,
    sense_data: Sense,
    nodes: WikiNodeChildrenList,
):
    text_nodes: WikiNodeChildrenList = []
    for node in nodes:
        if isinstance(node, WikiNode) and node.kind == NodeKind.TEMPLATE:
            if node.template_name == "ejemplo":
                process_ejemplo_template(wxr, sense_data, node)
            else:
                text_nodes.append(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.URL:
            if len(sense_data.examples) > 0:
                sense_data.examples[-1].ref = clean_node(wxr, None, node)
        else:
            text_nodes.append(node)

    if len(sense_data.examples) == 0 and len(text_nodes) > 0:
        example = Example(text=clean_node(wxr, None, text_nodes))
        sense_data.examples.append(example)
    elif len(text_nodes) > 0:
        wxr.wtp.debug(
            f"Unprocessed nodes from example group: {text_nodes}",
            sortid="extractor/es/example/extract_example/87",
        )


def process_example_list(
    wxr: WiktextractContext,
    sense_data: Sense,
    list_item: WikiNode,
):
    for sub_list_item in list_item.find_child_recursively(NodeKind.LIST_ITEM):
        example_data = Example(text="")
        text_nodes: WikiNodeChildrenList = []
        for child in sub_list_item.children:
            # "cita *" templates are obsolete
            if isinstance(
                child, TemplateNode
            ) and child.template_name.startswith("cita "):
                example_data.ref = clean_node(wxr, None, child)
            elif (
                isinstance(child, TemplateNode)
                and child.template_name == "referencia incompleta"
            ):
                # ignore empty ref template
                continue
            else:
                text_nodes.append(child)
        example_data.text = clean_node(wxr, None, text_nodes)
        if len(example_data.text) > 0:
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(text_nodes)),
                example_data.text,
                example_data,
                "bold_text_offsets",
                extra_node_kind=NodeKind.ITALIC,
            )
            sense_data.examples.append(example_data)

    # If no example was found in sublists,
    # assume example is in list_item.children directly.
    if len(sense_data.examples) == 0:
        text = clean_node(wxr, None, list_item.children).removeprefix(
            "Ejemplo: "
        )
        if len(text) > 0:
            example_data = Example(text=text)
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(list_item.children)),
                text,
                example_data,
                "bold_text_offsets",
                extra_node_kind=NodeKind.ITALIC,
            )
            sense_data.examples.append(example_data)

from wikitextprocessor.parser import (
    NodeKind,
    TemplateNode,
    WikiNode,
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
            example_data.translation = (
                clean_node(wxr, None, span_tag).removeprefix("→").strip()
            )
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

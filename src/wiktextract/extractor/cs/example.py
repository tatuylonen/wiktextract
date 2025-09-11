from wikitextprocessor import TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .models import Example, Sense


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode
):
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "Příklad":
            extract_příklad_template(wxr, sense, node)


def extract_příklad_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
):
    # https://cs.wiktionary.org/wiki/Šablona:Příklad
    second_arg = wxr.wtp.parse(t_node.template_parameters.get(2, ""))
    third_arg = wxr.wtp.parse(t_node.template_parameters.get(3, ""))
    e_data = Example(
        text=clean_node(wxr, None, second_arg),
        translation=clean_node(wxr, None, third_arg),
    )
    if e_data.text != "":
        calculate_bold_offsets(
            wxr, second_arg, e_data.text, e_data, "bold_text_offsets"
        )
        sense.examples.append(e_data)

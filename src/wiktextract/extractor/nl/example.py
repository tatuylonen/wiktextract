from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .models import Example, Sense

EXAMPLE_TEMPLATES = frozenset({"bijv-1", "bijv-2", "bijv-e", "citeer"})


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode
) -> None:
    has_template = False
    for t_node in list_item.find_child(NodeKind.TEMPLATE):
        extract_example_template(wxr, sense, t_node)
        has_template = True
    if not has_template:
        example_text = clean_node(wxr, None, list_item.children)
        if example_text != "":
            sense.examples.append(Example(text=example_text))


def extract_example_template(
    wxr: WiktextractContext, sense: Sense, node: TemplateNode
) -> None:
    if node.template_name == "bijv-1":
        # https://nl.wiktionary.org/wiki/Sjabloon:bijv-1
        first_arg = node.template_parameters.get(1, "")
        e_text = clean_node(wxr, None, first_arg)
        if len(e_text) > 0:
            e_data = Example(text=e_text)
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(first_arg)),
                e_text,
                e_data,
                "bold_text_offsets",
            )
            sense.examples.append(e_data)
    elif node.template_name in ["bijv-2", "bijv-e"]:
        first_arg = node.template_parameters.get(1, "")
        e_text = clean_node(wxr, None, first_arg)
        if len(e_text) > 0:
            e_data = Example(text=e_text)
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(first_arg)),
                e_text,
                e_data,
                "bold_text_offsets",
            )
            second_arg = node.template_parameters.get(2, "")
            e_data.translation = clean_node(wxr, None, second_arg)
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(second_arg)),
                e_data.translation,
                e_data,
                "bold_translation_offsets",
            )
            sense.examples.append(e_data)
    elif node.template_name == "citeer":
        extract_citeer_template(wxr, sense, node)


def extract_citeer_template(
    wxr: WiktextractContext, sense: Sense, node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:citeer
    e_data = Example()
    for text_arg_name in ["citaat", "passage"]:
        text_arg = node.template_parameters.get(text_arg_name, "")
        e_data.text = clean_node(wxr, None, text_arg)
        if e_data.text != "":
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(text_arg)),
                e_data.text,
                e_data,
                "bold_text_offsets",
            )
            break
    tr_arg = node.template_parameters.get("vertaling", "")
    e_data.translation = clean_node(wxr, None, tr_arg)
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(tr_arg)),
        e_data.translation,
        e_data,
        "bold_translation_offsets",
    )
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for ref_tag in expanded_node.find_html_recursively("ref"):
        e_data.ref = clean_node(wxr, sense, ref_tag.children)
        break
    if e_data.text != "":
        sense.examples.append(e_data)

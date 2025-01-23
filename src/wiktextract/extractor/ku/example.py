from wikitextprocessor import TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense, WordEntry


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item: WikiNode,
) -> None:
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name == "jêder" or node.template_name.startswith(
                "jêder-"
            ):
                extract_jêder_template(wxr, sense, node)


def extract_jêder_template(
    wxr: WiktextractContext,
    sense: Sense,
    t_node: TemplateNode,
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:jêder
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    e_data = Example(
        text=clean_node(
            wxr, None, t_node.template_parameters.get("jêgirtin", "")
        ),
        roman=clean_node(wxr, None, t_node.template_parameters.get("tr", "")),
        translation=clean_node(
            wxr, None, t_node.template_parameters.get("werger", "")
        ),
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="jeder"
    ):
        e_data.ref = clean_node(wxr, None, span_tag).strip("— ()")
    if e_data.text != "":
        sense.examples.append(e_data)
    clean_node(wxr, sense, expanded_node)

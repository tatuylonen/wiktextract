from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
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
        e_text = clean_node(wxr, None, node.template_parameters.get(1, ""))
        if len(e_text) > 0:
            sense.examples.append(Example(text=e_text))
    elif node.template_name in ["bijv-2", "bijv-e"]:
        e_text = clean_node(wxr, None, node.template_parameters.get(1, ""))
        if len(e_text) > 0:
            e_trans = clean_node(wxr, None, node.template_parameters.get(2, ""))
            sense.examples.append(Example(text=e_text, translation=e_trans))
    elif node.template_name == "citeer":
        extract_citeer_template(wxr, sense, node)


def extract_citeer_template(
    wxr: WiktextractContext, sense: Sense, node: TemplateNode
) -> None:
    # https://nl.wiktionary.org/wiki/Sjabloon:citeer
    e_text = clean_node(wxr, None, node.template_parameters.get("citaat", ""))
    if len(e_text) == 0:
        e_text = clean_node(
            wxr, None, node.template_parameters.get("passage", "")
        )
    if len(e_text) == 0:
        return
    e_trans = clean_node(
        wxr, None, node.template_parameters.get("vertaling", "")
    )
    example = Example(text=e_text, translation=e_trans)
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for ref_tag in expanded_node.find_html_recursively("ref"):
        example.ref = clean_node(wxr, sense, ref_tag.children)
        break
    sense.examples.append(example)

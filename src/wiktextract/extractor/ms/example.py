import re

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense, WordEntry


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item: WikiNode,
    parent_e_data: Example | None = None,
) -> None:
    e_data = Example(text="") if parent_e_data is None else parent_e_data
    is_first_node = True
    is_ref = False
    for node in list_item.children:
        if isinstance(node, TemplateNode) and (
            node.template_name
            in ["cp", "usex", "ux", "ko-usex", "uxi", "quote"]
            or node.template_name.startswith("quote-")
        ):
            extract_cp_template(wxr, sense, node, e_data)
        elif isinstance(node, WikiNode):
            if node.kind == NodeKind.ITALIC and not is_ref:
                if parent_e_data is None:
                    e_data.text = clean_node(wxr, sense, node)
                else:
                    e_data.translation = clean_node(wxr, sense, node)
            elif node.kind == NodeKind.LIST:
                for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                    extract_example_list_item(
                        wxr, word_entry, sense, child_list_item, e_data
                    )
            elif is_first_node and node.kind == NodeKind.BOLD:
                bold_text = clean_node(wxr, None, node)
                if re.fullmatch(r"\d{4}", bold_text):
                    e_data.ref = clean_node(
                        wxr,
                        sense,
                        list(list_item.invert_find_child(NodeKind.LIST)),
                    )
                    is_ref = True
            is_first_node = False

    if e_data.text != "" and parent_e_data is None:
        sense.examples.append(e_data)


def extract_cp_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode, e_data: Example
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    for html_tag in expanded_template.find_child_recursively(NodeKind.HTML):
        html_class = html_tag.attrs.get("class", "")
        if "e-example" in html_class or "e-quotation" in html_class:
            e_data.text = clean_node(wxr, None, html_tag)
        elif "e-transliteration" in html_class:
            e_data.roman = clean_node(wxr, None, html_tag)
        elif "e-translation" in html_class:
            e_data.translation = clean_node(wxr, None, html_tag)
        elif "e-literally" in html_class:
            e_data.literal_meaning = clean_node(wxr, None, html_tag)
        elif "cited-source" in html_class:
            e_data.ref = clean_node(wxr, None, html_tag)

    clean_node(wxr, sense, expanded_template)

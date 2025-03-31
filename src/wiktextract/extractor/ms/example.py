from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense, WordEntry


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item: WikiNode,
) -> None:
    italic_str = ""
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["cp", "usex", "ux", "ko-usex", "uxi"]:
                extract_cp_template(wxr, sense, node)
        elif isinstance(node, WikiNode):
            if node.kind == NodeKind.ITALIC:
                italic_str = clean_node(wxr, sense, node)
            elif node.kind == NodeKind.LIST:
                for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                    e_data = Example(
                        text=italic_str,
                        translation=clean_node(
                            wxr, sense, child_list_item.children
                        ),
                    )
                    if e_data.text != "":
                        sense.examples.append(e_data)
                        italic_str = ""

    if italic_str != "":
        sense.examples.append(Example(text=italic_str))


def extract_cp_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    e_data = Example(text="")
    for html_tag in expanded_template.find_child_recursively(NodeKind.HTML):
        html_class = html_tag.attrs.get("class", "")
        if html_tag.tag == "i":
            if "e-example" in html_class:
                e_data.text = clean_node(wxr, None, html_tag)
            elif "e-transliteration" in html_class:
                e_data.roman = clean_node(wxr, None, html_tag)
        elif html_tag.tag == "span" and "e-translation" in html_class:
            e_data.translation = clean_node(wxr, None, html_tag)
        elif html_tag.tag == "span" and "e-literally" in html_class:
            e_data.literal_meaning = clean_node(wxr, None, html_tag)

    if e_data.text != "":
        sense.examples.append(e_data)
    for link_node in expanded_template.find_child(NodeKind.LINK):
        clean_node(wxr, sense, link_node)

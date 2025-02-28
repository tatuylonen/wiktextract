from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .linkage import extract_syn_template
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
            if node.template_name == "ux":
                extract_ux_template(wxr, sense, node)
            elif node.template_name in [
                "sinonim",
                "syn",
                "synonyms",
                "synonym of",
                "sinonim dari",
            ]:
                extract_syn_template(wxr, word_entry, node, "synonyms")
            elif node.template_name == "antonim":
                extract_syn_template(wxr, word_entry, node, "antonyms")
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


def extract_ux_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    e_data = Example(text="")
    for i_tag in expanded_node.find_html_recursively("i"):
        i_class = i_tag.attrs.get("class", "")
        if "e-example" in i_class:
            e_data.text = clean_node(wxr, None, i_tag)
        elif "e-transliteration" in i_class:
            e_data.roman = clean_node(wxr, None, i_tag)
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "e-translation" in span_class:
            e_data.translation = clean_node(wxr, None, span_tag)
        elif "e-literally" in span_class:
            e_data.literal_meaning = clean_node(wxr, None, span_tag)
        elif "qualifier-content" in span_class:
            raw_tag = clean_node(wxr, None, span_tag)
            if raw_tag != "":
                e_data.raw_tags.append(raw_tag)

    e_data.ref = clean_node(
        wxr, None, t_node.template_parameters.get("ref", "")
    )
    if e_data.text != "":
        sense.examples.append(e_data)
        for link_node in expanded_node.find_child(NodeKind.LINK):
            clean_node(wxr, sense, link_node)

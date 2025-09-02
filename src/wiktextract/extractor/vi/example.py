from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .linkage import (
    GLOSS_LIST_LINKAGE_TEMPLATES,
    extract_gloss_list_linkage_template,
)
from .models import Example, Sense, WordEntry
from .tags import translate_raw_tags


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item: WikiNode,
    ref: str = "",
):
    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
            and node.contain_node(NodeKind.BOLD)
        ):
            e_text = clean_node(wxr, None, node)
            if e_text != "":
                e_data = Example(text=e_text)
                calculate_bold_offsets(
                    wxr, node, e_text, e_data, "bold_text_offsets"
                )
                e_data.translation = clean_node(
                    wxr, None, list_item.children[index + 1 :]
                ).strip("— \n")
                sense.examples.append(e_data)
                break
        elif isinstance(node, TemplateNode) and node.template_name in [
            "ux",
            "usex",
            "ux2",
        ]:
            extract_ux_template(wxr, sense, node)
        elif (
            isinstance(node, TemplateNode)
            and node.template_name in GLOSS_LIST_LINKAGE_TEMPLATES
        ):
            extract_gloss_list_linkage_template(
                wxr,
                word_entry,
                node,
                GLOSS_LIST_LINKAGE_TEMPLATES[node.template_name],
                " ".join(word_entry.senses[-1].glosses),
            )


def extract_ux_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    e_data = Example(text="")
    for i_tag in expanded_node.find_html_recursively("i"):
        i_class = i_tag.attrs.get("class", "")
        if "e-example" in i_class:
            e_data.text = clean_node(wxr, None, i_tag)
            calculate_bold_offsets(
                wxr, i_tag, e_data.text, e_data, "bold_text_offsets"
            )
        elif "e-transliteration" in i_class:
            e_data.roman = clean_node(wxr, None, i_tag)
            calculate_bold_offsets(
                wxr, i_tag, e_data.roman, e_data, "bold_roman_offsets"
            )
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "e-translation" in span_class:
            e_data.translation = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                e_data.translation,
                e_data,
                "bold_translation_offsets",
            )
        elif "e-literally" in span_class:
            e_data.literal_meaning = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                e_data.literal_meaning,
                e_data,
                "bold_literal_offsets",
            )
        elif "qualifier-content" in span_class:
            raw_tag = clean_node(wxr, None, span_tag)
            if raw_tag != "":
                e_data.raw_tags.append(raw_tag)

    e_data.ref = clean_node(
        wxr, None, t_node.template_parameters.get("ref", "")
    )
    if e_data.text != "":
        translate_raw_tags(e_data)
        sense.examples.append(e_data)
        for link_node in expanded_node.find_child(NodeKind.LINK):
            clean_node(wxr, sense, link_node)

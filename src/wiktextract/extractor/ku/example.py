from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
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
            elif node.template_name in ["mk", "mînak"]:
                extract_mînak_template(wxr, sense, node)


def extract_jêder_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:jêder
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    text_arg = t_node.template_parameters.get("jêgirtin", "")
    roman_arg = t_node.template_parameters.get("tr", "")
    trans_arg = t_node.template_parameters.get("werger", "")
    e_data = Example(
        text=clean_node(wxr, None, text_arg),
        roman=clean_node(wxr, None, roman_arg),
        translation=clean_node(wxr, None, trans_arg),
    )
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(text_arg)),
        e_data.text,
        e_data,
        "bold_text_offsets",
    )
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(roman_arg)),
        e_data.roman,
        e_data,
        "bold_roman_offsets",
    )
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(trans_arg)),
        e_data.translation,
        e_data,
        "bold_translation_offsets",
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="jeder"
    ):
        e_data.ref = clean_node(wxr, None, span_tag).strip("— ()")
    if e_data.text != "":
        sense.examples.append(e_data)
    clean_node(wxr, sense, expanded_node)


def extract_mînak_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    # https://ku.wiktionary.org/wiki/Şablon:mînak
    text_arg = t_node.template_parameters.get(2, "")
    roman_arg = t_node.template_parameters.get("tr", "")
    trans_arg = t_node.template_parameters.get("w", "")
    e_data = Example(
        text=clean_node(wxr, None, text_arg),
        roman=clean_node(wxr, None, roman_arg),
        translation=clean_node(wxr, None, trans_arg),
    )
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(text_arg)),
        e_data.text,
        e_data,
        "bold_text_offsets",
    )
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(roman_arg)),
        e_data.roman,
        e_data,
        "bold_roman_offsets",
    )
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(trans_arg)),
        e_data.translation,
        e_data,
        "bold_translation_offsets",
    )
    if e_data.text != "":
        sense.examples.append(e_data)
    clean_node(wxr, sense, t_node)


def extract_example_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    if len(word_entry.senses) > 0:
        for list_node in level_node.find_child(NodeKind.LIST):
            for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(
                    wxr, word_entry, word_entry.senses[0], list_item
                )

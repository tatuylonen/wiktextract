from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import calculate_bold_offsets
from .linkage import (
    GLOSS_LIST_LINKAGE_TEMPLATES,
    extract_gloss_list_linkage_template,
)
from .models import Example, WordEntry


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    example: Example,
) -> None:
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["ux", "uxi"]:
                extract_ux_template(wxr, word_entry.lang_code, node, example)
            elif node.template_name == "örnek":
                extract_örnek_template(wxr, word_entry.lang_code, node, example)
            elif node.template_name in GLOSS_LIST_LINKAGE_TEMPLATES:
                extract_gloss_list_linkage_template(wxr, word_entry, node)
            elif node.template_name.startswith("AT:"):
                extract_at_template(wxr, example, node)
        elif isinstance(node, WikiNode):
            match node.kind:
                case NodeKind.LIST:
                    for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                        extract_example_list_item(
                            wxr, word_entry, child_list_item, example
                        )
                case NodeKind.ITALIC:
                    italic_str = clean_node(wxr, None, node)
                    if italic_str != "":
                        if example.text == "":
                            example.text = italic_str
                            calculate_bold_offsets(
                                wxr,
                                node,
                                italic_str,
                                example,
                                "bold_text_offsets",
                            )
                        else:
                            example.translation = italic_str
                            calculate_bold_offsets(
                                wxr,
                                node,
                                italic_str,
                                example,
                                "bold_translation_offsets",
                            )


def extract_ux_template(
    wxr: WiktextractContext,
    lang_code: str,
    t_node: TemplateNode,
    example: Example,
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:ux
    e_lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    second_arg = t_node.template_parameters.get(2, "")
    second_arg_text = clean_node(wxr, None, second_arg)
    if e_lang_code == lang_code:
        example.text = second_arg_text
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(second_arg)),
            second_arg_text,
            example,
            "bold_text_offsets",
        )
    elif e_lang_code == "tr":
        example.translation = second_arg_text
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(second_arg)),
            second_arg_text,
            example,
            "bold_translation_offsets",
        )
    for index in [4, 5]:
        ref = clean_node(wxr, None, t_node.template_parameters.get(index, ""))
        if ref != "":
            example.ref = ref
    third_arg = t_node.template_parameters.get(3, "")
    tr_value = clean_node(wxr, None, third_arg)
    if tr_value != "":
        example.translation = tr_value
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(third_arg)),
            tr_value,
            example,
            "bold_translation_offsets",
        )


def extract_örnek_template(
    wxr: WiktextractContext,
    lang_code: str,
    t_node: TemplateNode,
    example: Example,
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:örnek
    e_lang_code = clean_node(
        wxr, None, t_node.template_parameters.get("dil", "")
    )
    first_arg = t_node.template_parameters.get(1, "")
    first_arg_text = clean_node(wxr, None, first_arg)
    if e_lang_code == lang_code:
        example.text = first_arg_text
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(first_arg)),
            first_arg_text,
            example,
            "bold_text_offsets",
        )
    elif e_lang_code == "tr":
        example.translation = first_arg_text
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(first_arg)),
            first_arg_text,
            example,
            "bold_translation_offsets",
        )
    for index in [2, 3]:
        ref = clean_node(wxr, None, t_node.template_parameters.get(index, ""))
        if ref != "":
            example.ref = ref
    t_arg = t_node.template_parameters.get("t", "")
    t_value = clean_node(wxr, None, t_arg)
    if t_value != "":
        example.translation = t_value
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(t_arg)),
            t_value,
            example,
            "bold_translation_offsets",
        )


def extract_at_template(
    wxr: WiktextractContext, example: Example, t_node: TemplateNode
) -> None:
    # Şablon:AT:Kur'an
    if any(
        arg in t_node.template_parameters for arg in ["pasaj", "text", "metin"]
    ):
        for arg in ["pasaj", "text", "metin"]:
            if arg in t_node.template_parameters:
                arg_value = t_node.template_parameters[arg]
                example.text = clean_node(wxr, None, arg_value)
                calculate_bold_offsets(
                    wxr,
                    wxr.wtp.parse(wxr.wtp.node_to_wikitext(arg_value)),
                    example.text,
                    example,
                    "bold_text_offsets",
                )
                break
        for arg in ["anlam", "mana", "mânâ", "t", "tercüme"]:
            if arg in t_node.template_parameters:
                arg_value = t_node.template_parameters[arg]
                example.translation = clean_node(wxr, None, arg_value)
                calculate_bold_offsets(
                    wxr,
                    wxr.wtp.parse(wxr.wtp.node_to_wikitext(arg_value)),
                    example.translation,
                    example,
                    "bold_translation_offsets",
                )
                break
    else:
        for arg in ["anlam", "mana", "mânâ", "t", "tercüme"]:
            if arg in t_node.template_parameters:
                arg_value = t_node.template_parameters[arg]
                example.text = clean_node(wxr, None, arg_value)
                calculate_bold_offsets(
                    wxr,
                    wxr.wtp.parse(wxr.wtp.node_to_wikitext(arg_value)),
                    example.text,
                    example,
                    "bold_text_offsets",
                )
                break

    example.ref = clean_node(wxr, None, t_node).splitlines()[0]

from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, WordEntry


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    example: Example,
) -> None:
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            match node.template_name:
                case "ux" | "uxi":
                    extract_ux_template(
                        wxr, word_entry.lang_code, node, example
                    )
                case "örnek":
                    extract_örnek_template(
                        wxr, word_entry.lang_code, node, example
                    )
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
                        else:
                            example.translation = italic_str


def extract_ux_template(
    wxr: WiktextractContext,
    lang_code: str,
    t_node: TemplateNode,
    example: Example,
) -> None:
    # https://tr.wiktionary.org/wiki/Şablon:ux
    e_lang_code = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    second_arg = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    if e_lang_code == lang_code:
        example.text = second_arg
    elif e_lang_code == "tr":
        example.translation = second_arg
    for index in [4, 5]:
        ref = clean_node(wxr, None, t_node.template_parameters.get(index, ""))
        if ref != "":
            example.ref = ref
    tr_value = clean_node(wxr, None, t_node.template_parameters.get(3, ""))
    if tr_value != "":
        example.translation = tr_value


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
    first_arg = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    if e_lang_code == lang_code:
        example.text = first_arg
    elif e_lang_code == "tr":
        example.translation = first_arg
    for index in [2, 3]:
        ref = clean_node(wxr, None, t_node.template_parameters.get(index, ""))
        if ref != "":
            example.ref = ref
    t_value = clean_node(wxr, None, t_node.template_parameters.get("t", ""))
    if t_value != "":
        example.translation = t_value

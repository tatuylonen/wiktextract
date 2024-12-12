from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Example, Sense


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode, lang_code: str
) -> None:
    examples = []
    before_italic = True
    text_nodes = []
    roman = ""
    translation = ""
    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, TemplateNode)
            and node.template_name == "zh-tradsem"
        ):
            examples.extend(extract_zh_tradsem(wxr, node))
        elif isinstance(node, WikiNode):
            match node.kind:
                case NodeKind.ITALIC:
                    if lang_code in ["zh", "ja"]:
                        if before_italic:
                            roman = clean_node(wxr, sense, node)
                            before_italic = False
                    else:
                        examples.append(
                            Example(text=clean_node(wxr, sense, node))
                        )
                case NodeKind.LIST:
                    for tr_list_item in node.find_child(NodeKind.LIST_ITEM):
                        translation = clean_node(
                            wxr, sense, tr_list_item.children
                        )
                case _ if lang_code in ["zh", "ja"]:
                    if before_italic:
                        text_nodes.append(node)
        elif (
            isinstance(node, str) and lang_code in ["zh", "ja"] and "-" in node
        ):
            translation = clean_node(
                wxr,
                sense,
                wxr.wtp.node_to_wikitext(
                    [node[node.index("-") + 1 :]]
                    + list_item.children[index + 1 :]
                ),
            )
            break
        elif lang_code in ["zh", "ja"] and len(examples) == 0 and before_italic:
            text_nodes.append(node)

    if lang_code in ["zh", "ja"] and len(examples) == 0 and len(text_nodes) > 0:
        expanded_nodes = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(text_nodes), expand_all=True
        )
        example = Example()
        example.ruby, node_without_ruby = extract_ruby(
            wxr, expanded_nodes.children
        )
        example.text = (
            clean_node(wxr, sense, node_without_ruby)
            .replace(" ", "")
            .strip("(")
        )
        examples.append(example)

    for example in examples:
        if roman != "":
            example.roman = roman
        if translation != "":
            example.translation = translation
        if example.text != "":
            sense.examples.append(example)


def extract_zh_tradsem(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Example]:
    # https://it.wiktionary.org/wiki/Template:zh-tradsem
    examples = []
    for arg_index in [1, 2]:
        arg_value = clean_node(
            wxr, None, t_node.template_parameters.get(arg_index, "")
        ).replace(" ", "")
        if arg_value != "":
            example = Example(text=arg_value)
            if arg_index == 1:
                example.tags.append("Traditional Chinese")
            elif arg_index == 2:
                example.tags.append("Simplified Chinese")
            examples.append(example)

    return examples

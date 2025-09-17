from wikitextprocessor import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import calculate_bold_offsets
from .models import Example, Sense


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode, lang_code: str
) -> None:
    examples = []
    before_italic = True
    text_nodes = []
    shared_example = Example()
    has_zh_tradsem = False
    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, TemplateNode)
            and node.template_name == "zh-tradsem"
        ):
            examples.extend(extract_zh_tradsem(wxr, node))
            has_zh_tradsem = True
        elif isinstance(node, WikiNode):
            match node.kind:
                case NodeKind.ITALIC:
                    if lang_code in ["zh", "ja"]:
                        if before_italic:
                            shared_example.roman = clean_node(wxr, sense, node)
                            calculate_bold_offsets(
                                wxr,
                                node,
                                shared_example.roman,
                                shared_example,
                                "bold_roman_offsets",
                            )
                            before_italic = False
                    else:
                        e_data = Example(text=clean_node(wxr, sense, node))
                        calculate_bold_offsets(
                            wxr, node, e_data.text, e_data, "bold_text_offsets"
                        )
                        examples.append(e_data)
                case NodeKind.LIST:
                    for tr_list_item in node.find_child(NodeKind.LIST_ITEM):
                        shared_example.translation = clean_node(
                            wxr, sense, tr_list_item.children
                        )
                        calculate_bold_offsets(
                            wxr,
                            tr_list_item,
                            shared_example.translation,
                            shared_example,
                            "bold_translation_offsets",
                        )
                case _ if lang_code in ["zh", "ja"]:
                    if before_italic:
                        text_nodes.append(node)
        elif isinstance(node, str) and "-" in node:
            for t_node in list_item.find_child(NodeKind.TEMPLATE):
                if t_node.template_name == "Term":
                    shared_example.ref = clean_node(wxr, None, t_node).strip(
                        "()"
                    )
                    break
            tr_nodes = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(
                    [node[node.index("-") + 1 :]]
                    + [
                        n
                        for n in list_item.children[index + 1 :]
                        if not (
                            isinstance(n, TemplateNode)
                            and n.template_name == "Term"
                        )
                    ]
                )
            )
            shared_example.translation = clean_node(wxr, sense, tr_nodes)
            calculate_bold_offsets(
                wxr,
                tr_nodes,
                shared_example.translation,
                shared_example,
                "bold_translation_offsets",
            )
            if not has_zh_tradsem and len(examples) > 1:
                examples.clear()
                text_node = wxr.wtp.parse(
                    wxr.wtp.node_to_wikitext(
                        list_item.children[:index] + [node[: node.index("-")]]
                    )
                )
                e_data = Example(text=clean_node(wxr, None, text_node))
                calculate_bold_offsets(
                    wxr, text_node, e_data.text, e_data, "bold_text_offsets"
                )
                examples.append(e_data)
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
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(node_without_ruby)),
            example.text,
            example,
            "bold_text_offsets",
        )
        examples.append(example)

    if not has_zh_tradsem and len(examples) > 1:
        examples.clear()
        text_node = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                list(
                    list_item.invert_find_child(
                        NodeKind.LIST, include_empty_str=True
                    )
                )
            )
        )
        e_data = Example(text=clean_node(wxr, None, text_node))
        calculate_bold_offsets(
            wxr, text_node, e_data.text, e_data, "bold_text_offsets"
        )
        examples.append(e_data)

    for example in examples:
        for attr in [
            "roman",
            "bold_roman_offsets",
            "translation",
            "bold_translation_offsets",
            "ref",
            "text",
            "bold_text_offsets",
        ]:
            value = getattr(shared_example, attr)
            if len(value) > 0:
                setattr(example, attr, value)
        if len(example.text) > 0:
            sense.examples.append(example)


def extract_zh_tradsem(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Example]:
    # https://it.wiktionary.org/wiki/Template:zh-tradsem
    examples = []
    for arg_index in [1, 2]:
        arg_value = t_node.template_parameters.get(arg_index, "")
        arg_value_str = clean_node(wxr, None, arg_value).replace(" ", "")
        if arg_value_str != "":
            example = Example(text=arg_value_str)
            calculate_bold_offsets(
                wxr,
                wxr.wtp.parse(wxr.wtp.node_to_wikitext(arg_value)),
                example.text,
                example,
                "bold_text_offsets",
            )
            if arg_index == 1:
                example.tags.append("Traditional-Chinese")
            elif arg_index == 2:
                example.tags.append("Simplified-Chinese")
            examples.append(example)

    return examples

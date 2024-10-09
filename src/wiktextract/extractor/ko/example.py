from wikitextprocessor import TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Example, Sense


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode, lang_code: str
) -> None:
    example = Example()
    after_lang_template = False
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "lang":
            after_lang_template = True
            extract_example_lang_template(wxr, example, node, lang_code)
        elif isinstance(node, TemplateNode) and node.template_name.startswith(
            "따옴"
        ):
            example.ref = clean_node(wxr, None, node).strip("() ")
        elif after_lang_template:
            example.translation += clean_node(wxr, None, node)
        else:
            example.text += clean_node(wxr, None, node)

    if len(example.text) > 0:
        if lang_code == "zh" and "/" in example.text:
            for index, text in enumerate(example.text.split("/", 1)):
                new_example = example.model_copy(deep=True)
                new_example.text = text
                new_example.tags.append(
                    "Traditional Chinese"
                    if index == 0
                    else "Simplified Chinese"
                )
                sense.examples.append(new_example)
        else:
            sense.examples.append(example)


def extract_example_lang_template(
    wxr: WiktextractContext,
    example: Example,
    node: TemplateNode,
    lang_code: str,
) -> None:
    # https://ko.wiktionary.org/wiki/틀:lang
    if lang_code == "ja":
        example.ruby, text_nodes = extract_ruby(
            wxr,
            wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(node.template_parameters.get(2, "")),
                expand_all=True,
            ).children,
        )
        example.text = clean_node(wxr, None, text_nodes)
    else:
        example.text = clean_node(
            wxr, None, node.template_parameters.get(2, "")
        )
    example.translation = clean_node(
        wxr, None, node.template_parameters.get(4, "")
    )
    if lang_code == "zh" and "(" in example.text and example.text.endswith(")"):
        roman_start_index = example.text.index("(")
        example.roman = example.text[roman_start_index:].strip("() ")
        example.text = example.text[:roman_start_index].strip()

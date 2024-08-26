from typing import Optional, Union

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .linkage import process_linkage_templates_in_gloss
from .models import Example, Sense, WordEntry
from .tags import translate_raw_tags

LINKAGE_TEMPLATES = {
    "syn": "synonyms",
    "synonyms": "synonyms",
    "ant": "antonyms",
    "antonyms": "antonyms",
    "hyper": "hypernyms",
    "hypernyms": "hypernyms",
    "hypo": "hyponyms",
    "hyponyms": "hyponyms",
}


def extract_examples(
    wxr: WiktextractContext,
    sense_data: Sense,
    node: Union[WikiNode, list[WikiNode]],
    page_data: list[WordEntry],
    parent_example: Optional[Example] = None,
) -> None:
    if isinstance(node, list):
        for n in node:
            extract_examples(wxr, sense_data, n, page_data)
    elif isinstance(node, WikiNode):
        if node.kind == NodeKind.LIST_ITEM:
            example_data = parent_example or Example()
            # example text in the nested list
            # https://zh.wiktionary.org/wiki/%, the second example
            if node.contain_node(NodeKind.LIST) and not all(
                isinstance(n, TemplateNode)
                for n in node.invert_find_child(NodeKind.LIST)
            ):
                extract_example_list(wxr, node, example_data)
            else:
                # parse example templates
                for child in node.find_child(NodeKind.TEMPLATE):
                    template_name = child.template_name
                    if template_name.startswith(("quote-", "RQ:")):
                        extract_quote_templates(wxr, child, example_data)
                    elif template_name in {"ja-x", "ja-usex"}:
                        extract_template_ja_usex(wxr, child, example_data)
                        clean_node(wxr, sense_data, child)  # add cat link
                    elif template_name in {"zh-x", "zh-usex", "zh-q"}:
                        sense_data.examples.extend(
                            extract_template_zh_x(wxr, child, example_data)
                        )
                        clean_node(wxr, sense_data, child)  # add cat link
                    elif template_name in {"ux", "eg", "usex"}:
                        extract_template_ux(wxr, child, example_data)
                    elif template_name == "uxi":
                        extract_template_uxi(wxr, child, example_data)
                    elif template_name in LINKAGE_TEMPLATES:
                        process_linkage_templates_in_gloss(
                            wxr,
                            page_data,
                            child,
                            LINKAGE_TEMPLATES[template_name],
                            sense_data.glosses[0]
                            if len(sense_data.glosses) > 0
                            else "",
                        )
                    else:
                        example_data.text = clean_node(wxr, None, child)

                for list_item in node.find_child_recursively(
                    NodeKind.LIST_ITEM
                ):
                    extract_examples(
                        wxr, sense_data, list_item, page_data, example_data
                    )

            if len(example_data.text) > 0 and parent_example is None:
                sense_data.examples.append(example_data)
        else:
            extract_examples(wxr, sense_data, node.children, page_data)


def extract_example_list(
    wxr: WiktextractContext, node: WikiNode, example_data: Example
) -> None:
    for index, child_node in enumerate(node.children):
        if (
            isinstance(child_node, WikiNode)
            and child_node.kind == NodeKind.LIST
        ):
            example_data.ref = clean_node(wxr, None, node.children[:index])
            example_data.text = clean_node(
                wxr, None, child_node.children[0].children
            )


def extract_quote_templates(
    wxr: WiktextractContext, node: TemplateNode, example_data: Example
) -> None:
    """
    Process template `quote-book` and "RQ:*".
    """
    expanded_text = clean_node(wxr, None, node)
    for line_num, expanded_line in enumerate(expanded_text.splitlines()):
        if line_num == 0:
            key = "ref"
        elif line_num == 1:
            key = "text"
        elif line_num == 2 and "transliteration" in node.template_parameters:
            key = "roman"
        else:
            key = "translation"

        if expanded_line != "（請為本引文添加中文翻譯）":
            if key == "text":
                example_data.text = expanded_line
            else:
                setattr(example_data, key, expanded_line)


def extract_template_ja_usex(
    wxr: WiktextractContext, node: TemplateNode, example_data: Example
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="Jpan"
    ):
        ruby_data, node_without_ruby = extract_ruby(wxr, span_tag)
        example_data.text = clean_node(wxr, None, node_without_ruby)
        example_data.ruby = ruby_data
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="tr"
    ):
        example_data.roman = clean_node(wxr, None, span_tag)
    example_data.translation = clean_node(
        wxr, None, node.template_parameters.get(3, "")
    )
    example_data.literal_meaning = clean_node(
        wxr, None, node.template_parameters.get("lit", "")
    )


def extract_template_zh_x(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    parent_example: Example,
) -> list[Example]:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    has_dl_tag = False
    results = []
    for dl_tag in expanded_node.find_html_recursively("dl"):
        has_dl_tag = True
        ref = ""
        roman = ""
        translation = ""
        roman_raw_tags = []
        for dd_tag in dl_tag.find_html("dd"):
            dd_text = clean_node(wxr, None, dd_tag)
            if dd_text.startswith("出自："):
                ref = dd_text.removeprefix("出自：")
            else:
                is_roman = False
                for span_tag in dd_tag.find_html_recursively(
                    "span", attr_name="lang", attr_value="Latn"
                ):
                    roman = clean_node(wxr, None, span_tag)
                    is_roman = True
                    for span_tag in dd_tag.find_html_recursively("span"):
                        span_text = clean_node(wxr, None, span_tag)
                        if span_text.startswith("[") and span_text.endswith(
                            "]"
                        ):
                            roman_raw_tags.append(span_text.strip("[]"))
                if not is_roman:
                    translation = dd_text

        example_text = ""
        last_span_is_exmaple = False
        for span_tag in dl_tag.find_html_recursively("span"):
            if span_tag.attrs.get("class", "") in ["Hant", "Hans"]:
                example_text = clean_node(wxr, None, span_tag)
                last_span_is_exmaple = True
            elif last_span_is_exmaple:
                last_span_is_exmaple = False
                if len(example_text) > 0:
                    raw_tag = clean_node(wxr, None, span_tag)
                    example = parent_example.model_copy(deep=True)
                    example.text = example_text
                    example.roman = roman
                    example.translation = translation
                    example.raw_tags.extend(raw_tag.strip("[]").split("，"))
                    example.raw_tags.extend(roman_raw_tags)
                    if len(ref) > 0:  # don't override parent quote-* template
                        example.ref = ref
                    translate_raw_tags(example)
                    results.append(example)

    # no source, single line example
    if not has_dl_tag:
        roman = ""
        raw_tags = []
        for span_tag in expanded_node.find_html(
            "span", attr_name="lang", attr_value="Latn"
        ):
            roman = clean_node(wxr, None, span_tag)
        for span_tag in expanded_node.find_html("span"):
            span_text = clean_node(wxr, None, span_tag)
            if span_text.startswith("[") and span_text.endswith("]"):
                raw_tags.append(span_text.strip("[]"))
        translation = clean_node(
            wxr, None, template_node.template_parameters.get(2, "")
        )
        literal_meaning = clean_node(
            wxr, None, template_node.template_parameters.get("lit", "")
        )
        for span_tag in expanded_node.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            if span_lang in ["zh-Hant", "zh-Hans"]:
                example_text = clean_node(wxr, None, span_tag)
                if len(example_text) > 0:
                    example_data = parent_example.model_copy(deep=True)
                    example_data.text = example_text
                    example_data.roman = roman
                    example_data.tags.append(
                        "Traditional Chinese"
                        if span_lang == "zh-Hant"
                        else "Simplified Chinese"
                    )
                    example_data.translation = translation
                    example_data.literal_meaning = literal_meaning
                    example_data.raw_tags.extend(raw_tags)
                    translate_raw_tags(example_data)
                    results.append(example_data)
    return results


def extract_template_ux(
    wxr: WiktextractContext, node: WikiNode, example_data: Example
) -> None:
    expanded_text = clean_node(wxr, None, node)
    if " ― " in expanded_text:
        extract_template_uxi_text(expanded_text, example_data)
        return

    lines = expanded_text.splitlines()
    for line_num, expanded_line in enumerate(lines):
        if line_num == 0:
            key = "text"
        elif line_num == 1:
            if line_num == len(lines) - 1:
                key = "translation"
            else:
                key = "roman"
        else:
            key = "translation"
        if key == "text":
            example_data.text = expanded_line
        else:
            setattr(example_data, key, expanded_line)


def extract_template_uxi(
    wxr: WiktextractContext, node: WikiNode, example_data: Example
) -> None:
    expanded_text = clean_node(wxr, None, node)
    extract_template_uxi_text(expanded_text, example_data)


def extract_template_uxi_text(
    expanded_text: str, example_data: Example
) -> None:
    parts = expanded_text.split(" ― ")
    for index, part in enumerate(parts):
        if index == 0:
            key = "text"
        elif index == 1:
            if index == len(parts) - 1:
                key = "translation"
            else:
                key = "roman"
        else:
            key = "translation"
        if key == "text":
            example_data.text = part
        else:
            setattr(example_data, key, part)

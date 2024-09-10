from copy import deepcopy
from typing import Optional

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...tags import valid_tags
from ...type_utils import ExampleData, SenseData
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby


def extract_example_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    sense_data: SenseData,
    parent_data: Optional[ExampleData],
) -> list[ExampleData]:
    examples = []
    for template_node in list_item.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in ["zh-x", "zh-q"]:
            examples.extend(
                extract_template_zh_x(
                    wxr,
                    template_node,
                    sense_data,
                    parent_data
                    if parent_data is not None
                    else ExampleData(raw_tags=[], tags=[]),
                )
            )
        elif template_node.template_name in ["ja-usex", "ja-x"]:
            examples.append(
                extract_template_ja_usex(
                    wxr,
                    template_node,
                    sense_data,
                    parent_data
                    if parent_data is not None
                    else ExampleData(raw_tags=[], tags=[]),
                )
            )
        elif (
            template_node.template_name.startswith(("quote-", "RQ:"))
            or template_node.template_name == "quote"
        ):
            q_example = extract_quote_templates(wxr, template_node, sense_data)
            if list_item.contain_node(NodeKind.LIST):
                for next_list_item in list_item.find_child_recursively(
                    NodeKind.LIST_ITEM
                ):
                    for key in ["tags", "raw_tags"]:
                        q_example[key] = []
                    examples.extend(
                        extract_example_list_item(
                            wxr, next_list_item, sense_data, q_example
                        )
                    )
            else:
                examples.append(q_example)

    return examples


def extract_quote_templates(
    wxr: WiktextractContext, node: TemplateNode, sense_data: SenseData
) -> ExampleData:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    clean_node(wxr, sense_data, expanded_node)
    ref = ""
    text = ""
    translation = ""
    roman = ""
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "cited-source" == span_class:
            ref = clean_node(wxr, None, span_tag)
        elif "cited-passage" in span_class:
            text = clean_node(wxr, None, span_tag)
        elif "e-translation" in span_class:
            translation = clean_node(wxr, None, span_tag)
    for i_tag in expanded_node.find_html_recursively(
        "i", attr_name="class", attr_value="e-transliteration"
    ):
        roman = clean_node(wxr, None, i_tag)
        break
    return ExampleData(
        text=text, ref=ref, english=translation, roman=roman, type="quote"
    )


def extract_template_ja_usex(
    wxr: WiktextractContext,
    node: TemplateNode,
    sense_data: SenseData,
    example_data: ExampleData,
) -> ExampleData:
    # https://en.wiktionary.org/wiki/Template:ja-usex
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    clean_node(wxr, sense_data, expanded_node)
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="Jpan"
    ):
        ruby_data, node_without_ruby = extract_ruby(wxr, span_tag)
        example_data["text"] = clean_node(wxr, None, node_without_ruby)
        example_data["ruby"] = ruby_data
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="tr"
    ):
        example_data["roman"] = clean_node(wxr, None, span_tag)
    example_data["english"] = clean_node(
        wxr, None, node.template_parameters.get(3, "")
    )
    example_data["literal_meaning"] = clean_node(
        wxr, None, node.template_parameters.get("lit", "")
    )


def extract_template_zh_x(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense_data: SenseData,
    parent_example: ExampleData,
) -> list[ExampleData]:
    # https://en.wiktionary.org/wiki/Template:zh-x
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    clean_node(wxr, sense_data, expanded_node)
    has_dl_tag = False
    results = []
    for dl_tag in expanded_node.find_html_recursively("dl"):
        has_dl_tag = True
        ref = ""
        roman = ""
        translation = clean_node(
            wxr, None, template_node.template_parameters.get(2, "")
        )
        roman_raw_tags = []
        for dd_tag in dl_tag.find_html("dd"):
            dd_text = clean_node(wxr, None, dd_tag)
            if dd_text.startswith("From:"):
                ref = dd_text.removeprefix("From:")
            else:
                for span_tag in dd_tag.find_html_recursively(
                    "span", attr_name="lang", attr_value="Latn"
                ):
                    roman = clean_node(wxr, None, span_tag)
                    for span_tag in dd_tag.find_html_recursively("span"):
                        span_text = clean_node(wxr, None, span_tag)
                        if span_text.startswith("[") and span_text.endswith(
                            "]"
                        ):
                            roman_raw_tags.append(span_text.strip("[]"))
                    break

        example_text = ""
        last_span_is_example = False
        for span_tag in dl_tag.find_html_recursively("span"):
            if span_tag.attrs.get("class", "") in ["Hant", "Hans"]:
                example_text = clean_node(wxr, None, span_tag)
                last_span_is_example = True
            elif last_span_is_example:
                last_span_is_example = False
                if len(example_text) > 0:
                    example = deepcopy(parent_example)
                    # dialect and character variant tag
                    for link_node in span_tag.find_child_recursively(
                        NodeKind.LINK
                    ):
                        example["raw_tags"].append(
                            clean_node(wxr, None, link_node)
                        )
                    example["text"] = example_text
                    example["roman"] = roman
                    example["english"] = translation
                    example["raw_tags"].extend(roman_raw_tags)
                    if len(ref) > 0:  # don't override parent quote-* template
                        example["ref"] = ref
                    clean_example_empty_data(example)
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
                    example_data = deepcopy(parent_example)
                    example_data["text"] = example_text
                    example_data["roman"] = roman
                    example_data["tags"].append(
                        "Traditional Chinese"
                        if span_lang == "zh-Hant"
                        else "Simplified Chinese"
                    )
                    example_data["english"] = translation
                    example_data["literal_meaning"] = literal_meaning
                    example_data["raw_tags"].extend(raw_tags)
                    clean_example_empty_data(example_data)
                    results.append(example_data)
    return results


ZH_X_TAGS = {
    "trad.": "Traditional Chinese",
    "simp.": "Simplified Chinese",
}


def clean_example_empty_data(data: ExampleData) -> ExampleData:
    raw_tags = data.get("raw_tags", [])
    new_raw_tags = []
    for raw_tag in raw_tags:
        if raw_tag in ZH_X_TAGS:
            data["tags"].append(ZH_X_TAGS[raw_tag])
        elif raw_tag in valid_tags:
            data["tags"].append(raw_tag)
        else:
            new_raw_tags.append(raw_tag)
    data["raw_tags"] = new_raw_tags
    if len(data.get("ref", "")) > 0:
        data["type"] = "quote"
    else:
        data["type"] = "example"
    for key, value in data.copy().items():
        if len(value) == 0:
            del data[key]

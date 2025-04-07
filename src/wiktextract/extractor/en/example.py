from copy import deepcopy

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...tags import valid_tags
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import calculate_bold_offsets
from .type_utils import ExampleData, SenseData


def extract_example_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    sense_data: SenseData,
    parent_data: ExampleData,
) -> list[ExampleData]:
    examples = []
    for template_node in list_item.find_child(NodeKind.TEMPLATE):
        if template_node.template_name in ["zh-x", "zh-usex", "zh-q"]:
            examples.extend(
                extract_template_zh_x(
                    wxr,
                    template_node,
                    sense_data,
                    parent_data,
                )
            )
        elif template_node.template_name in ["ja-usex", "ja-x", "ja-ux"]:
            examples.append(
                extract_template_ja_usex(
                    wxr,
                    template_node,
                    sense_data,
                    parent_data,
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
                        if key not in q_example:
                            q_example[key] = []
                    examples.extend(
                        extract_example_list_item(
                            wxr, next_list_item, sense_data, q_example
                        )
                    )
            else:
                examples.append(q_example)
        elif template_node.template_name in [
            "ux",
            "usex",
            "uxi",
            "ko-usex",
            "koex",
            "ko-x",
            "th-usex",
            "th-x",
            "th-xi",
        ]:
            examples.append(
                extract_ux_template(
                    wxr,
                    template_node,
                    sense_data,
                    parent_data,
                )
            )

    return examples


def extract_quote_templates(
    wxr: WiktextractContext, node: TemplateNode, sense_data: SenseData
) -> ExampleData:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    clean_node(wxr, sense_data, expanded_node)
    example_data = ExampleData(
        text="", ref="", english="", roman="", type="quote"
    )
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "cited-source" == span_class:
            example_data["ref"] = clean_node(wxr, None, span_tag)
        elif "e-quotation" in span_class:
            example_data["text"] = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                example_data["text"],
                example_data,
                "bold_text_offsets",
            )
        elif "e-translation" in span_class:
            example_data["english"] = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                example_data["english"],
                example_data,
                "bold_english_offsets",
            )
    for i_tag in expanded_node.find_html_recursively(
        "i", attr_name="class", attr_value="e-transliteration"
    ):
        example_data["roman"] = clean_node(wxr, None, i_tag)
        calculate_bold_offsets(
            wxr,
            span_tag,
            example_data["roman"],
            example_data,
            "bold_roman_offsets",
        )
        break
    clean_example_empty_data(example_data)
    return example_data


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
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(node_without_ruby)),
            example_data["text"],
            example_data,
            "bold_text_offsets",
        )
        example_data["ruby"] = ruby_data
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="tr"
    ):
        example_data["roman"] = clean_node(wxr, None, span_tag)
        calculate_bold_offsets(
            wxr,
            span_tag,
            example_data["roman"],
            example_data,
            "bold_roman_offsets",
        )
    tr_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node.template_parameters.get(3, ""))
    )
    example_data["english"] = clean_node(wxr, None, tr_arg)
    calculate_bold_offsets(
        wxr,
        tr_arg,
        example_data["english"],
        example_data,
        "bold_english_offsets",
    )
    lit_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node.template_parameters.get("lit", ""))
    )
    example_data["literal_meaning"] = clean_node(wxr, None, lit_arg)
    calculate_bold_offsets(
        wxr,
        lit_arg,
        example_data["literal_meaning"],
        example_data,
        "bold_literal_offsets",
    )
    clean_example_empty_data(example_data)
    return example_data


def extract_template_zh_x(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    sense_data: SenseData | None,
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
        example_data = deepcopy(parent_example)
        tr_arg = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                template_node.template_parameters.get(2, "")
            )
        )
        example_data["english"] = clean_node(wxr, None, tr_arg)
        calculate_bold_offsets(
            wxr,
            tr_arg,
            example_data["english"],
            example_data,
            "bold_english_offsets",
        )
        for dd_tag in dl_tag.find_html("dd"):
            dd_text = clean_node(wxr, None, dd_tag)
            if dd_text.startswith("From:"):
                example_data["ref"] = dd_text.removeprefix("From:")
            else:
                for span_tag in dd_tag.find_html_recursively(
                    "span", attr_name="lang", attr_value="Latn"
                ):
                    example_data["roman"] = clean_node(wxr, None, span_tag)
                    calculate_bold_offsets(
                        wxr,
                        span_tag,
                        example_data["roman"],
                        example_data,
                        "bold_roman_offsets",
                    )
                    for span_tag in dd_tag.find_html_recursively("span"):
                        span_text = clean_node(wxr, None, span_tag)
                        if span_text.startswith("[") and span_text.endswith(
                            "]"
                        ):
                            example_data["raw_tags"].append(
                                span_text.strip("[]")
                            )
                    break
        results.extend(extract_zh_x_dl_span_tag(wxr, dl_tag, example_data))

    # no source, single line example
    if not has_dl_tag:
        example_data = deepcopy(parent_example)
        for span_tag in expanded_node.find_html(
            "span", attr_name="lang", attr_value="Latn"
        ):
            example_data["roman"] = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                example_data["roman"],
                example_data,
                "bold_roman_offsets",
            )
            break
        for span_tag in expanded_node.find_html("span"):
            span_text = clean_node(wxr, None, span_tag)
            if span_text.startswith("[") and span_text.endswith("]"):
                example_data["raw_tags"].append(span_text.strip("[]"))
        tr_arg = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                template_node.template_parameters.get(2, "")
            )
        )
        example_data["english"] = clean_node(wxr, None, tr_arg)
        calculate_bold_offsets(
            wxr,
            tr_arg,
            example_data["english"],
            example_data,
            "bold_english_offsets",
        )
        lit_arg = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(
                template_node.template_parameters.get("lit", "")
            )
        )
        example_data["literal_meaning"] = clean_node(wxr, None, lit_arg)
        calculate_bold_offsets(
            wxr,
            tr_arg,
            example_data["literal_meaning"],
            example_data,
            "bold_literal_offsets",
        )
        for span_tag in expanded_node.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            if span_lang in ["zh-Hant", "zh-Hans"]:
                example_text = clean_node(wxr, None, span_tag)
                if len(example_text) > 0:
                    new_example = deepcopy(example_data)
                    new_example["text"] = example_text
                    calculate_bold_offsets(
                        wxr,
                        span_tag,
                        example_text,
                        example_data,
                        "bold_text_offsets",
                    )
                    new_example["tags"].append(
                        "Traditional Chinese"
                        if span_lang == "zh-Hant"
                        else "Simplified Chinese"
                    )
                    clean_example_empty_data(new_example)
                    results.append(new_example)
    return results


def extract_zh_x_dl_span_tag(
    wxr: WiktextractContext, dl_tag: HTMLNode, example: ExampleData
) -> list[ExampleData]:
    # process example text span tag and dialect span tag
    results = []
    is_first_hide = True
    for span_tag in dl_tag.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        if span_lang in ["zh-Hant", "zh-Hans"]:
            new_example = deepcopy(example)
            new_example["text"] = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                new_example["text"],
                new_example,
                "bold_text_offsets",
            )
            results.append(new_example)
        elif "vsHide" in span_tag.attrs.get("class", ""):
            # template has arg "collapsed=y"
            results.extend(
                extract_zh_x_dl_span_tag(
                    wxr,
                    span_tag,
                    results[-1]
                    if is_first_hide and len(results) > 0
                    else example,
                )
            )
            is_first_hide = False
        elif "font-size:x-small" in span_tag.attrs.get("style", ""):
            for link_node in span_tag.find_child_recursively(NodeKind.LINK):
                raw_tag = clean_node(wxr, None, link_node)
                if len(raw_tag) > 0:
                    if len(results) > 0:
                        results[-1]["raw_tags"].append(raw_tag)
                    else:
                        example["raw_tags"].append(raw_tag)

    if dl_tag.tag == "dl":
        for data in results:
            clean_example_empty_data(data)
    return results


ZH_X_TAGS = {
    "trad.": "Traditional Chinese",
    "simp.": "Simplified Chinese",
}


def clean_example_empty_data(data: ExampleData) -> None:
    # remove empty data and convert raw tags
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


def extract_ux_template(
    wxr: WiktextractContext,
    t_node: TemplateNode,
    sense_data: SenseData,
    example_data: ExampleData,
) -> ExampleData:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    clean_node(wxr, sense_data, expanded_node)
    for html_node in expanded_node.find_child_recursively(NodeKind.HTML):
        class_names = html_node.attrs.get("class", "")
        if "e-example" in class_names:
            example_data["text"] = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data["text"],
                example_data,
                "bold_text_offsets",
            )
        elif "e-transliteration" in class_names:
            example_data["roman"] = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data["roman"],
                example_data,
                "bold_roman_offsets",
            )
        elif "e-translation" in class_names:
            example_data["english"] = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data["english"],
                example_data,
                "bold_english_offsets",
            )
        elif "e-literally" in class_names:
            example_data["literal_meaning"] = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data["literal_meaning"],
                example_data,
                "bold_literal_offsets",
            )
        elif "qualifier-content" in class_names:
            raw_tag = clean_node(wxr, None, html_node)
            if raw_tag != "":
                example_data["raw_tags"].append(raw_tag)

    clean_example_empty_data(example_data)
    return example_data

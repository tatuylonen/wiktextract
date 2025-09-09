from wikitextprocessor.parser import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import calculate_bold_offsets
from .linkage import process_linkage_templates_in_gloss
from .models import Example, Form, Sense, WordEntry
from .tags import translate_raw_tags

LINKAGE_TEMPLATES = {
    "syn": "synonyms",
    "synonyms": "synonyms",
    "ant": "antonyms",
    "antonyms": "antonyms",
    "antonym": "antonyms",
    "hyper": "hypernyms",
    "hypernyms": "hypernyms",
    "hypo": "hyponyms",
    "hyponyms": "hyponyms",
    "cot": "coordinate_terms",
    "coo": "coordinate_terms",
    "coord": "coordinate_terms",
    "coordinate terms": "coordinate_terms",
}


def extract_example_list_item(
    wxr: WiktextractContext,
    sense_data: Sense,
    list_item: WikiNode,
    word_entry: WordEntry,
    parent_example: Example | None = None,
) -> None:
    example_data = parent_example or Example()
    if list_item.contain_node(NodeKind.LIST) and not all(
        isinstance(n, TemplateNode)
        for n in list_item.invert_find_child(NodeKind.LIST)
    ):
        # plain text in the nested list, not using any template
        # https://zh.wiktionary.org/wiki/%, the second example
        extract_plain_text_example_list(wxr, list_item, example_data)
    else:
        # parse example templates
        for child in list_item.find_child(NodeKind.TEMPLATE):
            template_name = child.template_name
            if (
                template_name.startswith(("quote-", "RQ:"))
                or template_name == "quote"
            ):
                extract_quote_templates(wxr, child, example_data)
                clean_node(wxr, sense_data, child)  # add cat link
            elif template_name in ["ja-x", "ja-usex"]:
                extract_template_ja_usex(wxr, child, example_data)
                clean_node(wxr, sense_data, child)  # add cat link
            elif template_name in ["zh-x", "zh-usex", "zh-q", "zh-co"]:
                sense_data.examples.extend(
                    extract_template_zh_x(wxr, child, example_data)
                )
                clean_node(wxr, sense_data, child)  # add cat link
            elif template_name in [
                "ux",
                "eg",
                "usex",
                "uxi",
                "collocation",
                "co",
                "coi",
                "ko-usex",
                "ko-x",
                "koex",
                "th-usex",
                "th-x",
                "th-xi",
            ]:
                extract_template_ux(wxr, child, example_data)
                clean_node(wxr, sense_data, child)  # add cat link
            elif template_name == "Q":
                extract_template_Q(wxr, child, example_data)
                clean_node(wxr, sense_data, child)  # add cat link
            elif template_name.lower() in LINKAGE_TEMPLATES:
                process_linkage_templates_in_gloss(
                    wxr,
                    word_entry,
                    child,
                    LINKAGE_TEMPLATES[template_name.lower()],
                    " ".join(sense_data.glosses),
                )
            elif template_name.lower() in ["inline alt forms", "alti"]:
                extract_inline_alt_forms_template(wxr, word_entry, child)

        for next_list_item in list_item.find_child_recursively(
            NodeKind.LIST_ITEM
        ):
            extract_example_list_item(
                wxr, sense_data, next_list_item, word_entry, example_data
            )

    if len(example_data.text) > 0 and parent_example is None:
        sense_data.examples.append(example_data)


def extract_plain_text_example_list(
    wxr: WiktextractContext, list_item: WikiNode, example_data: Example
) -> None:
    for index, nested_list in list_item.find_child(
        NodeKind.LIST, with_index=True
    ):
        example_data.ref = clean_node(wxr, None, list_item.children[:index])
        example_data.text = clean_node(
            wxr, None, nested_list.children[0].children
        )


def extract_quote_templates(
    wxr: WiktextractContext, node: TemplateNode, example_data: Example
) -> None:
    """
    Process `quote-*` and "RQ:*" templates.
    """
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "cited-source" == span_class:
            example_data.ref = clean_node(wxr, None, span_tag)
        elif "e-quotation" in span_class:
            example_data.ruby, node_without_ruby = extract_ruby(wxr, span_tag)
            example_data.text = clean_node(wxr, None, node_without_ruby)
            calculate_bold_offsets(
                wxr,
                span_tag,
                example_data.text,
                example_data,
                "bold_text_offsets",
            )
        elif "e-translation" in span_class:
            example_data.translation = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                example_data.translation,
                example_data,
                "bold_translation_offsets",
            )
    for i_tag in expanded_node.find_html_recursively(
        "i", attr_name="class", attr_value="e-transliteration"
    ):
        example_data.roman = clean_node(wxr, None, i_tag)
        calculate_bold_offsets(
            wxr,
            i_tag,
            example_data.roman,
            example_data,
            "bold_roman_offsets",
        )
        break


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
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(node_without_ruby)),
            example_data.text,
            example_data,
            "bold_text_offsets",
        )
        example_data.ruby = ruby_data
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="tr"
    ):
        example_data.roman = clean_node(wxr, None, span_tag)
        calculate_bold_offsets(
            wxr,
            span_tag,
            example_data.roman,
            example_data,
            "bold_roman_offsets",
        )
    tr_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node.template_parameters.get(3, "")),
        expand_all=True,
    )
    example_data.translation = clean_node(wxr, None, tr_arg)
    calculate_bold_offsets(
        wxr,
        tr_arg,
        example_data.translation,
        example_data,
        "bold_translation_offsets",
    )
    lit_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node.template_parameters.get("lit", "")),
        expand_all=True,
    )
    example_data.literal_meaning = clean_node(wxr, None, lit_arg)
    calculate_bold_offsets(
        wxr,
        lit_arg,
        example_data.literal_meaning,
        example_data,
        "bold_literal_offsets",
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
    example_data = parent_example.model_copy(deep=True)
    tr_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node.template_parameters.get(2, "")),
        expand_all=True,
    )
    example_data.translation = clean_node(wxr, None, tr_arg)
    calculate_bold_offsets(
        wxr,
        tr_arg,
        example_data.translation,
        example_data,
        "bold_translation_offsets",
    )
    lit_arg = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(
            template_node.template_parameters.get("lit", "")
        ),
        expand_all=True,
    )
    example_data.literal_meaning = clean_node(wxr, None, lit_arg)
    calculate_bold_offsets(
        wxr,
        lit_arg,
        example_data.literal_meaning,
        example_data,
        "bold_literal_offsets",
    )
    for dl_tag in expanded_node.find_html_recursively("dl"):
        has_dl_tag = True
        for dd_tag in dl_tag.find_html("dd"):
            dd_text = clean_node(wxr, None, dd_tag)
            if dd_text.startswith("出自："):
                example_data.ref = dd_text.removeprefix("出自：")
            elif not dd_text.startswith("（字面義為"):
                for span_tag in dd_tag.find_html_recursively(
                    "span", attr_name="lang", attr_value="Latn"
                ):
                    example_data.roman = clean_node(wxr, None, span_tag)
                    calculate_bold_offsets(
                        wxr,
                        span_tag,
                        example_data.roman,
                        example_data,
                        "bold_roman_offsets",
                    )
                    for span_tag in dd_tag.find_html_recursively("span"):
                        span_text = clean_node(wxr, None, span_tag)
                        if span_text.startswith("[") and span_text.endswith(
                            "]"
                        ):
                            example_data.raw_tags.append(span_text.strip("[]"))
                    break
        results.extend(extract_zh_x_dl_span_tag(wxr, dl_tag, example_data))

    # no source, single line example
    if not has_dl_tag:
        for span_tag in expanded_node.find_html(
            "span", attr_name="lang", attr_value="Latn"
        ):
            example_data.roman = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                example_data.roman,
                example_data,
                "bold_roman_offsets",
            )
            break
        for span_tag in expanded_node.find_html("span"):
            span_text = clean_node(wxr, None, span_tag)
            if span_text.startswith("[") and span_text.endswith("]"):
                example_data.raw_tags.append(span_text.strip("[]"))
        for span_tag in expanded_node.find_html("span"):
            span_lang = span_tag.attrs.get("lang", "")
            if span_lang in ["zh-Hant", "zh-Hans"]:
                example_text = clean_node(wxr, None, span_tag)
                if len(example_text) > 0:
                    new_example = example_data.model_copy(deep=True)
                    new_example.text = example_text
                    calculate_bold_offsets(
                        wxr,
                        span_tag,
                        example_text,
                        new_example,
                        "bold_text_offsets",
                    )
                    new_example.tags.append(
                        "Traditional-Chinese"
                        if span_lang == "zh-Hant"
                        else "Simplified-Chinese"
                    )
                    translate_raw_tags(new_example)
                    results.append(new_example)
    return results


def extract_zh_x_dl_span_tag(
    wxr: WiktextractContext, dl_tag: HTMLNode, example: Example
) -> list[Example]:
    # process example text span tag and dialect span tag
    results = []
    is_first_hide = True
    for span_tag in dl_tag.find_html("span"):
        span_lang = span_tag.attrs.get("lang", "")
        if span_lang in ["zh-Hant", "zh-Hans"]:
            new_example = example.model_copy(deep=True)
            new_example.text = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                new_example.text,
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
            for link_node in span_tag.find_child(NodeKind.LINK):
                raw_tag = clean_node(wxr, None, link_node)
                if len(raw_tag) > 0:
                    if len(results) > 0:
                        results[-1].raw_tags.append(raw_tag)
                    else:
                        example.raw_tags.append(raw_tag)

    if dl_tag.tag == "dl":
        for data in results:
            translate_raw_tags(data)
    return results


def extract_template_ux(
    wxr: WiktextractContext, node: TemplateNode, example_data: Example
) -> None:
    # https://zh.wiktionary.org/wiki/Template:ux
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for html_node in expanded_node.find_child_recursively(NodeKind.HTML):
        class_names = html_node.attrs.get("class", "")
        if "e-example" in class_names:
            example_data.text = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data.text,
                example_data,
                "bold_text_offsets",
            )
        elif "e-transliteration" in class_names:
            example_data.roman = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data.roman,
                example_data,
                "bold_roman_offsets",
            )
        elif "e-translation" in class_names:
            example_data.translation = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data.translation,
                example_data,
                "bold_translation_offsets",
            )
        elif "e-literally" in class_names:
            example_data.literal_meaning = clean_node(wxr, None, html_node)
            calculate_bold_offsets(
                wxr,
                html_node,
                example_data.literal_meaning,
                example_data,
                "bold_literal_offsets",
            )
        elif "qualifier-content" in class_names:
            example_data.raw_tags.extend(
                clean_node(wxr, None, html_node).split("、")
            )
    translate_raw_tags(example_data)


def extract_template_Q(
    wxr: WiktextractContext, node: TemplateNode, example_data: Example
) -> None:
    # https://zh.wiktionary.org/wiki/Template:Q
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(node), expand_all=True
    )
    for div_tag in expanded_node.find_html(
        "div", attr_name="class", attr_value="wiktQuote"
    ):
        ref_nodes = []
        for child in div_tag.children:
            if isinstance(child, HTMLNode) and child.tag == "dl":
                for i_tag in child.find_html_recursively(
                    "i", attr_name="class", attr_value="e-transliteration"
                ):
                    example_data.roman = clean_node(wxr, None, i_tag)
                    calculate_bold_offsets(
                        wxr,
                        i_tag,
                        example_data.roman,
                        example_data,
                        "bold_roman_offsets",
                    )
                break
            ref_nodes.append(child)
        ref_text = clean_node(wxr, None, ref_nodes)
        if len(ref_text) > 0:
            example_data.ref = ref_text
        for t_arg, field in (
            ("quote", "text"),
            ("t", "translation"),
            ("trans", "translation"),
            ("lit", "literal_meaning"),
        ):
            t_arg_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(
                    node.template_parameters.get(t_arg, "")
                ),
                expand_all=True,
            )
            value = clean_node(wxr, None, t_arg_node)
            if len(value) > 0:
                setattr(example_data, field, value)
                calculate_bold_offsets(
                    wxr,
                    t_arg_node,
                    value,
                    example_data,
                    "bold_" + field.split("_")[0] + "_offsets",
                )


def extract_inline_alt_forms_template(
    wxr: WiktextractContext, word_entry: WordEntry, t_node: TemplateNode
):
    sense = " ".join(word_entry.senses[-1].glosses)
    forms = []
    raw_tag = ""
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    lang = clean_node(wxr, None, t_node.template_parameters.get(1, ""))
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        span_lang = span_tag.attrs.get("lang", "")
        if "qualifier-content" in span_class:
            raw_tag = clean_node(wxr, None, span_tag)
        elif span_lang == lang:
            word = clean_node(wxr, None, span_tag)
            if word != "":
                form = Form(form=word, sense=sense, tags=["alternative"])
                if raw_tag != "":
                    form.raw_tags.append(raw_tag)
                    raw_tag = ""
                    translate_raw_tags(form)
                forms.append(form)
        elif span_class == "tr Latn" and len(forms) > 0:
            forms[-1].roman = clean_node(wxr, None, span_tag)
    word_entry.forms.extend(forms)

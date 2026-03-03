from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import calculate_bold_offsets
from .linkage import (
    GLOSS_LIST_LINKAGE_TEMPLATES,
    extract_gloss_list_linkage_template,
)
from .models import Example, Sense, WordEntry
from .tags import translate_raw_tags


def extract_example_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    sense: Sense,
    list_item: WikiNode,
    ref: str = "",
):
    for index, node in enumerate(list_item.children):
        if (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.ITALIC
            and node.contain_node(NodeKind.BOLD)
        ):
            e_text = clean_node(wxr, None, node)
            if e_text != "":
                e_data = Example(text=e_text)
                calculate_bold_offsets(
                    wxr, node, e_text, e_data, "bold_text_offsets"
                )
                e_data.translation = clean_node(
                    wxr, None, list_item.children[index + 1 :]
                ).strip("—- \n")
                sense.examples.append(e_data)
                break
        elif isinstance(node, TemplateNode):
            if node.template_name in [
                "ux",
                "usex",
                "ux2",
                "uxi",
                "collocation",
                "th-usex",
                "th-x",
                "tha-x",
                "tha-usex",
                "uxa",
            ]:
                extract_ux_template(wxr, sense, node)
            elif node.template_name.startswith(("quote-", "RQ:")):
                ref = extract_quote_template(wxr, sense, node)
            elif node.template_name in GLOSS_LIST_LINKAGE_TEMPLATES:
                extract_gloss_list_linkage_template(
                    wxr,
                    word_entry,
                    node,
                    GLOSS_LIST_LINKAGE_TEMPLATES[node.template_name],
                    " ".join(word_entry.senses[-1].glosses)
                    if len(word_entry.senses) > 0
                    else "",
                )
            elif node.template_name in ["ja-usex", "ja-x", "jpn-usex"]:
                extract_ja_x_template(wxr, node, sense, ref)
            elif node.template_name in [
                "zho-x",
                "zh-x",
                "zh-usex",
                "zho-usex",
                "zhex",
            ]:
                extract_zh_x_template(wxr, node, sense, ref)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for child_list_item in node.find_child(NodeKind.LIST_ITEM):
                extract_example_list_item(
                    wxr, word_entry, sense, child_list_item, ref
                )


def extract_ux_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    e_data = Example(text="")
    for i_tag in expanded_node.find_html_recursively("i"):
        i_class = i_tag.attrs.get("class", "")
        if "e-example" in i_class:
            e_data.text = clean_node(wxr, None, i_tag)
            calculate_bold_offsets(
                wxr, i_tag, e_data.text, e_data, "bold_text_offsets"
            )
        elif "e-transliteration" in i_class:
            e_data.roman = clean_node(wxr, None, i_tag)
            calculate_bold_offsets(
                wxr, i_tag, e_data.roman, e_data, "bold_roman_offsets"
            )
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "e-translation" in span_class:
            e_data.translation = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                e_data.translation,
                e_data,
                "bold_translation_offsets",
            )
        elif "e-literally" in span_class:
            e_data.literal_meaning = clean_node(wxr, None, span_tag)
            calculate_bold_offsets(
                wxr,
                span_tag,
                e_data.literal_meaning,
                e_data,
                "bold_literal_offsets",
            )
        elif "qualifier-content" in span_class:
            raw_tag = clean_node(wxr, None, span_tag)
            if raw_tag != "":
                e_data.raw_tags.append(raw_tag)

    e_data.ref = clean_node(
        wxr, None, t_node.template_parameters.get("ref", "")
    )
    if e_data.text != "":
        translate_raw_tags(e_data)
        sense.examples.append(e_data)
        for link_node in expanded_node.find_child(NodeKind.LINK):
            clean_node(wxr, sense, link_node)


def extract_quote_template(
    wxr: WiktextractContext,
    sense: Sense,
    t_node: TemplateNode,
) -> str:
    ref = ""
    if all(
        arg not in t_node.template_parameters for arg in ["text", "passage", 7]
    ):
        ref = clean_node(wxr, sense, t_node)
    else:
        expanded_node = wxr.wtp.parse(
            wxr.wtp.node_to_wikitext(t_node), expand_all=True
        )
        example = Example(text="")
        for span_tag in expanded_node.find_html_recursively("span"):
            span_class = span_tag.attrs.get("class", "")
            if "cited-source" == span_class:
                example.ref = clean_node(wxr, None, span_tag)
            elif "e-quotation" in span_class:
                example.ruby, node_without_ruby = extract_ruby(wxr, span_tag)
                example.text = clean_node(wxr, None, node_without_ruby)
                calculate_bold_offsets(
                    wxr, span_tag, example.text, example, "bold_text_offsets"
                )
            elif "e-translation" in span_class:
                example.translation = clean_node(wxr, None, span_tag)
                calculate_bold_offsets(
                    wxr,
                    span_tag,
                    example.translation,
                    example,
                    "bold_translation_text",
                )
        for i_tag in expanded_node.find_html_recursively(
            "i", attr_name="class", attr_value="e-transliteration"
        ):
            example.roman = clean_node(wxr, None, i_tag)
            calculate_bold_offsets(
                wxr, i_tag, example.roman, example, "bold_roman_offsets"
            )
            break
        if example.text != "":
            sense.examples.append(example)
        clean_node(wxr, sense, expanded_node)

    return ref


def extract_ja_x_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: Sense, ref: str
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    example = Example(text="", ref=ref)
    for span_tag in expanded_node.find_html(
        "span", attr_name="class", attr_value="Jpan"
    ):
        ruby_data, node_without_ruby = extract_ruby(wxr, span_tag)
        example.text = clean_node(wxr, None, node_without_ruby)
        example.ruby = ruby_data
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(node_without_ruby)),
            example.text,
            example,
            "bold_text_offsets",
        )
    for span_tag in expanded_node.find_html_recursively(
        "span", attr_name="class", attr_value="tr"
    ):
        example.roman = clean_node(wxr, None, span_tag)
        calculate_bold_offsets(
            wxr, span_tag, example.roman, example, "bold_roman_offsets"
        )
    third_arg = t_node.template_parameters.get(3, "")
    example.translation = clean_node(wxr, None, third_arg)
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(third_arg)),
        example.translation,
        example,
        "bold_translation_offsets",
    )
    lit_arg = t_node.template_parameters.get("lit", "")
    example.literal_meaning = clean_node(wxr, None, lit_arg)
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(lit_arg)),
        example.literal_meaning,
        example,
        "bold_literal_offsets",
    )
    if example.text != "":
        sense.examples.append(example)
        for link_node in expanded_node.find_child(NodeKind.LINK):
            clean_node(wxr, sense, link_node)


def extract_zh_x_template(
    wxr: WiktextractContext, t_node: TemplateNode, sense: Sense, ref: str
):
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    examples = []
    for dl_tag in expanded_node.find_html("dl"):
        examples.extend(extract_zh_x_dl_tag(wxr, dl_tag))
    if len(examples) == 0:
        examples.extend(extract_zh_x_no_dl_tag(wxr, expanded_node))

    second_arg = t_node.template_parameters.get(2, "")
    translation = clean_node(wxr, None, second_arg)
    for e_data in examples:
        e_data.translation = translation
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(second_arg)),
            translation,
            e_data,
            "bold_translation_offsets",
        )
        translate_raw_tags(e_data)

    for link_node in expanded_node.find_child(NodeKind.LINK):
        clean_node(wxr, sense, link_node)
    sense.examples.extend(examples)


def extract_zh_x_dl_tag(
    wxr: WiktextractContext, dl_tag: HTMLNode
) -> list[Example]:
    examples = []
    for span_tag in dl_tag.find_html("span"):
        if "lang" in span_tag.attrs:
            e_text = clean_node(wxr, None, span_tag)
            if e_text != "":
                e_data = Example(text=e_text)
                calculate_bold_offsets(
                    wxr, span_tag, e_text, e_data, "bold_text_offsets"
                )
                examples.append(e_data)
        else:
            raw_tags = clean_node(wxr, None, span_tag).strip("[] ")
            for raw_tag in raw_tags.split(","):
                raw_tag = raw_tag.strip()
                if raw_tag != "" and len(examples) > 0:
                    examples[-1].raw_tags.append(raw_tag)
    ref = ""
    for dd_tag in dl_tag.find_html("dd"):
        for span_tag in dd_tag.find_html("span"):
            if "Latn" in span_tag.attrs.get("lang", ""):
                roman = clean_node(wxr, None, span_tag)
                for e_data in examples:
                    e_data.roman = roman
                    calculate_bold_offsets(
                        wxr, span_tag, roman, e_data, "bold_roman_offsets"
                    )
            else:
                raw_tag = clean_node(wxr, None, span_tag).strip("[] ")
                if raw_tag != "":
                    for e_data in examples:
                        e_data.raw_tags.append(raw_tag)
        for small_tag in dd_tag.find_html("small"):
            ref = clean_node(wxr, None, small_tag).removeprefix("Từ:").strip()
    for e_data in examples:
        e_data.ref = ref

    return examples


def extract_zh_x_no_dl_tag(
    wxr: WiktextractContext, expanded_node: WikiNode
) -> list[Example]:
    examples = []
    for span_tag in expanded_node.find_html("span"):
        lang = span_tag.attrs.get("lang", "")
        match lang:
            case "zh-Latn":
                roman = clean_node(wxr, None, span_tag)
                for e_data in examples:
                    e_data.roman = roman
                    calculate_bold_offsets(
                        wxr, span_tag, roman, e_data, "bold_roman_offsets"
                    )
            case "zh-Hant" | "zh-Hans":
                e_text = clean_node(wxr, None, span_tag)
                example = Example(text=e_text)
                example.tags.append(
                    "Traditional-Chinese"
                    if lang == "zh-Hant"
                    else "Simplified-Chinese"
                )
                if example.text != "":
                    calculate_bold_offsets(
                        wxr, span_tag, e_text, example, "bold_text_offsets"
                    )
                    examples.append(example)

    return examples

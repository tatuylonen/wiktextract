import re

from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Example, Sense
from .tags import translate_raw_tags


def extract_example_list_item(
    wxr: WiktextractContext, sense: Sense, list_item: WikiNode
) -> None:
    for node in list_item.children:
        if isinstance(node, TemplateNode):
            if node.template_name in ["ux", "usex", "ko-usex"]:
                extract_ux_template(wxr, sense, node)
            elif node.template_name in ["zh-x", "zh-usex"]:
                extract_template_zh_x(wxr, sense, node)


def extract_ux_template(
    wxr: WiktextractContext, sense: Sense, t_node: TemplateNode
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    e_data = Example(text="")
    for i_tag in expanded_node.find_html_recursively("i"):
        i_class = i_tag.attrs.get("class", "")
        if "e-example" in i_class:
            e_data.text = clean_node(wxr, None, i_tag)
        elif "e-transliteration" in i_class:
            e_data.roman = clean_node(wxr, None, i_tag)
    for span_tag in expanded_node.find_html_recursively("span"):
        span_class = span_tag.attrs.get("class", "")
        if "e-translation" in span_class:
            e_data.translation = clean_node(wxr, None, span_tag)
        elif "e-literally" in span_class:
            e_data.literal_meaning = clean_node(wxr, None, span_tag)
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


def extract_template_zh_x(
    wxr: WiktextractContext,
    sense: Sense,
    t_node: TemplateNode,
) -> None:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    examples = []
    for dl_tag in expanded_node.find_html("dl"):
        examples.extend(extract_zh_x_dl_tag(wxr, dl_tag))
    if len(examples) == 0:
        examples.extend(extract_zh_x_no_dl_tag(wxr, expanded_node))

    translation = clean_node(wxr, None, t_node.template_parameters.get(2, ""))
    for e_data in examples:
        e_data.translation = translation
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
                examples.append(Example(text=e_text))
        else:
            raw_tags = clean_node(wxr, None, span_tag).strip("[] ")
            for raw_tag in re.split(r", | and ", raw_tags):
                raw_tag = raw_tag.strip()
                if raw_tag != "" and len(examples) > 0:
                    examples[-1].raw_tags.append(raw_tag)
    for dd_tag in dl_tag.find_html("dd"):
        for span_tag in dd_tag.find_html("span"):
            if "Latn" in span_tag.attrs.get("lang", ""):
                roman = clean_node(wxr, None, span_tag)
                for e_data in examples:
                    e_data.roman = roman
            else:
                raw_tag = clean_node(wxr, None, span_tag).strip("[] ")
                if raw_tag != "":
                    for e_data in examples:
                        e_data.raw_tags.append(raw_tag)
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
            case "zh-Hant" | "zh-Hans":
                e_text = clean_node(wxr, None, span_tag)
                example = Example(text=e_text)
                example.tags.append(
                    "Traditional Chinese"
                    if lang == "zh-Hant"
                    else "Simplified Chinese"
                )
                if example.text != "":
                    examples.append(example)

    return examples

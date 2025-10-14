from wikitextprocessor import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from ..share import calculate_bold_offsets, set_sound_file_url_fields
from .models import Example, Sense, Sound
from .tags import translate_raw_tags


def extract_example_list_item(
    wxr: WiktextractContext,
    sense: Sense,
    list_item: WikiNode,
    lang_code: str,
    parent_example: Example | None = None,
) -> None:
    example = Example() if parent_example is None else parent_example
    e_text_nodes = []
    e_tr_nodes = []
    after_lang_template = False
    for node in list_item.children:
        if isinstance(node, TemplateNode) and node.template_name == "lang":
            after_lang_template = True
            extract_example_lang_template(wxr, example, node, lang_code)
        elif isinstance(node, TemplateNode) and node.template_name.startswith(
            ("따옴", "지봉유설")
        ):
            example.ref = (
                clean_node(wxr, None, node).strip("() ").removeprefix("따옴◄")
            )
        elif isinstance(node, TemplateNode) and node.template_name in [
            "예문",
            "ux",
            "uxi",
        ]:
            extract_ux_template(wxr, sense, example, node)
            break
        elif isinstance(node, TemplateNode) and node.template_name in [
            "zh-x",
            "zh-usex",
        ]:
            extract_template_zh_x(wxr, sense, node)
            break
        elif after_lang_template:
            e_tr_nodes.append(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            break
        elif (
            isinstance(node, WikiNode)
            and node.kind == NodeKind.LINK
            and len(node.largs) > 0
            and len(node.largs[0]) > 0
            and isinstance(node.largs[0][0], str)
            and node.largs[0][0].startswith("File:")
        ):
            sound = Sound()
            sound_file = node.largs[0][0].removeprefix("File:").strip()
            set_sound_file_url_fields(wxr, sound_file, sound)
            if sound.audio != "":
                example.sounds.append(sound)
        else:
            e_text_nodes.append(node)

    e_text = clean_node(wxr, sense, e_text_nodes)
    if e_text != "":
        example.text = e_text
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(e_text_nodes)),
            e_text,
            example,
            "bold_text_offsets",
        )
    e_tr = clean_node(wxr, sense, e_tr_nodes)
    if e_tr != "":
        example.translation = e_tr

    if len(example.text) > 0:
        if lang_code == "zh" and "/" in example.text:
            example.bold_text_offsets = example.bold_text_offsets[
                : len(example.bold_text_offsets) // 2
            ]
            for index, text in enumerate(example.text.split("/", 1)):
                new_example = example.model_copy(deep=True)
                new_example.text = text
                new_example.tags.append(
                    "Traditional-Chinese"
                    if index == 0
                    else "Simplified-Chinese"
                )
                sense.examples.append(new_example)
        else:
            sense.examples.append(example)

    for nested_list in list_item.find_child(NodeKind.LIST):
        for nested_list_item in nested_list.find_child(NodeKind.LIST_ITEM):
            extract_example_list_item(
                wxr,
                sense,
                nested_list_item,
                lang_code,
                example if example.text == "" else Example(),
            )


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
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(text_nodes)),
            example.text,
            example,
            "bold_text_offsets",
        )
    else:
        second_arg = node.template_parameters.get(2, "")
        example.text = clean_node(wxr, None, second_arg)
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(second_arg)),
            example.text,
            example,
            "bold_text_offsets",
        )
    tr_arg = node.template_parameters.get(4, "")
    example.translation = clean_node(wxr, None, tr_arg)
    calculate_bold_offsets(
        wxr,
        wxr.wtp.parse(wxr.wtp.node_to_wikitext(tr_arg)),
        example.translation,
        example,
        "bold_translation_offsets",
    )
    if lang_code == "zh" and "(" in example.text and example.text.endswith(")"):
        roman_start_index = example.text.index("(")
        example.roman = example.text[roman_start_index:].strip("() ")
        example.text = example.text[:roman_start_index].strip()


def extract_ux_template(
    wxr: WiktextractContext,
    sense: Sense,
    example: Example,
    t_node: TemplateNode,
) -> None:
    # https://ko.wiktionary.org/wiki/틀:ux
    # https://ko.wiktionary.org/wiki/모듈:usex/templates
    lang_code = t_node.template_parameters.get(1, "")
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    if lang_code == "ja":
        for span_tag in expanded_node.find_html_recursively("span"):
            span_class = span_tag.attrs.get("class", "")
            if span_class == "Jpan":
                example.ruby, no_ruby = extract_ruby(wxr, span_tag)
                example.text = clean_node(wxr, None, no_ruby)
                calculate_bold_offsets(
                    wxr,
                    wxr.wtp.parse(wxr.wtp.node_to_wikitext(no_ruby)),
                    example.text,
                    example,
                    "bold_text_offsets",
                )
            elif span_class == "tr":
                example.roman = clean_node(wxr, None, span_tag)
                calculate_bold_offsets(
                    wxr,
                    wxr.wtp.parse(wxr.wtp.node_to_wikitext(span_tag)),
                    example.roman,
                    example,
                    "bold_roman_offsets",
                )
        tr_arg = t_node.template_parameters.get(4, "")
        example.translation = clean_node(wxr, None, tr_arg)
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(tr_arg)),
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
        if example.ref == "":
            example.ref = clean_node(
                wxr, None, t_node.template_parameters.get("ref", "")
            )
    else:
        second_arg = t_node.template_parameters.get(2, "")
        example.text = clean_node(wxr, None, second_arg)
        calculate_bold_offsets(
            wxr,
            wxr.wtp.parse(wxr.wtp.node_to_wikitext(second_arg)),
            example.text,
            example,
            "bold_text_offsets",
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
        example.note = clean_node(
            wxr, None, t_node.template_parameters.get("footer", "")
        )
        if example.ref == "":
            example.ref = clean_node(
                wxr, None, t_node.template_parameters.get("출처", "")
            )
        if example.ref == "":
            example.ref = clean_node(
                wxr, None, t_node.template_parameters.get("source", "")
            )

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

import re

from mediawiki_langcodes import name_to_code
from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Descendant, WordEntry
from .tags import TEMPLATE_TAG_ARGS, translate_raw_tags


def extract_descendant_section(
    wxr: WiktextractContext, level_node: LevelNode, page_data: list[WordEntry]
) -> None:
    desc_list = []
    for node in level_node.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            for list_node in level_node.find_child(NodeKind.LIST):
                for list_item in list_node.find_child(NodeKind.LIST_ITEM):
                    desc_list.extend(
                        process_desc_list_item(wxr, list_item, [], [])[0]
                    )
        elif (
            isinstance(node, TemplateNode)
            and node.template_name.lower() == "cjkv"
        ):
            desc_list.extend(process_cjkv_template(wxr, node))

    page_data[-1].descendants.extend(desc_list)
    for data in page_data[:-1]:
        if (
            data.lang_code == page_data[-1].lang_code
            and data.sounds == page_data[-1].sounds
            and data.etymology_text == page_data[-1].etymology_text
            and data.pos_level == page_data[-1].pos_level == level_node.kind
        ):
            data.descendants.extend(desc_list)


def process_cjkv_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[Descendant]:
    expanded_node = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    desc_list = []
    for list_item in expanded_node.find_child_recursively(NodeKind.LIST_ITEM):
        desc_list.extend(process_desc_list_item(wxr, list_item, [], [])[0])
    return desc_list


def process_desc_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    parent_data: list[Descendant],
    raw_tags: list[str],
    lang_code: str = "unknown",
    lang_name: str = "unknown",
) -> tuple[list[Descendant], str, str]:
    # process list item node and <li> tag
    data_list = []
    before_word_raw_tags = []
    after_word = False
    for child in list_item.children:
        if isinstance(child, str) and child.strip().endswith(":"):
            lang_name = child.strip(": ") or "unknown"
            lang_code = name_to_code(lang_name, "zh") or "unknown"
        elif isinstance(child, str) and child.strip() == ",":
            after_word = False
        elif isinstance(child, HTMLNode) and child.tag == "span":
            extract_desc_span_tag(
                wxr,
                child,
                data_list,
                lang_code,
                lang_name,
                raw_tags,
                before_word_raw_tags,
                after_word,
            )
        elif (
            isinstance(child, HTMLNode)
            and child.tag == "i"
            and len(data_list) > 0
        ):
            for span_tag in child.find_html(
                "span", attr_name="class", attr_value="Latn"
            ):
                roman = clean_node(wxr, None, span_tag)
                data_list[-1].roman = roman
                if (
                    len(data_list) > 1
                    and "Traditional-Chinese" in data_list[-2].tags
                ):
                    data_list[-2].roman = roman
        elif isinstance(child, TemplateNode) and child.template_name in [
            "desctree",
            "descendants tree",
            "desc",
            "descendant",
            "ja-r",
            "zh-l",
            "zh-m",
        ]:
            if child.template_name.startswith("desc"):
                lang_code = child.template_parameters.get(1, "") or "unknown"
            expanded_template = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(child), expand_all=True
            )
            new_data, new_l_code, new_l_name = process_desc_list_item(
                wxr,
                expanded_template,
                [],  # avoid add twice
                raw_tags,
                lang_code,
                lang_name,
            )
            data_list.extend(new_data)
            # save lang data from desc template
            lang_code = new_l_code
            lang_name = new_l_name

    for ul_tag in list_item.find_html("ul"):
        for li_tag in ul_tag.find_html("li"):
            process_desc_list_item(wxr, li_tag, data_list, [])
    for next_list in list_item.find_child(NodeKind.LIST):
        for next_list_item in next_list.find_child(NodeKind.LIST_ITEM):
            process_desc_list_item(wxr, next_list_item, data_list, [])

    for p_data in parent_data:
        p_data.descendants.extend(data_list)
    return data_list, lang_code, lang_name


def extract_desc_span_tag(
    wxr: WiktextractContext,
    span_tag: HTMLNode,
    desc_lists: list[Descendant],
    lang_code: str,
    lang_name: str,
    raw_tags: list[str],
    before_word_raw_tags: list[str],
    after_word: bool,
) -> bool:
    class_names = span_tag.attrs.get("class", "").split()
    span_lang = span_tag.attrs.get("lang", "")
    span_title = span_tag.attrs.get("title", "")
    if ("tr" in class_names or span_lang.endswith("-Latn")) and len(
        desc_lists
    ) > 0:
        roman = clean_node(wxr, None, span_tag)
        desc_lists[-1].roman = roman
        if len(desc_lists) > 1 and "Traditional-Chinese" in desc_lists[-2].tags:
            desc_lists[-2].roman = roman
    elif (
        "qualifier-content" in class_names
        or "gender" in class_names
        or "label-content" in class_names
    ) and len(desc_lists) > 0:
        for raw_tag in re.split(r"，|,", clean_node(wxr, None, span_tag)):
            raw_tag = raw_tag.strip()
            if raw_tag == "":
                continue
            if after_word:
                if raw_tag in TEMPLATE_TAG_ARGS:
                    desc_lists[-1].tags.append(TEMPLATE_TAG_ARGS[raw_tag])
                else:
                    desc_lists[-1].raw_tags.append(raw_tag)
                    translate_raw_tags(desc_lists[-1])
            else:
                before_word_raw_tags.append(raw_tag)
    elif span_lang != "":
        ruby_data, nodes_without_ruby = extract_ruby(wxr, span_tag)
        desc_data = Descendant(
            lang=lang_name,
            lang_code=lang_code,
            word=clean_node(wxr, None, nodes_without_ruby),
            ruby=ruby_data,
            raw_tags=before_word_raw_tags + raw_tags,
        )
        before_word_raw_tags.clear()
        if desc_data.lang_code == "unknown":
            desc_data.lang_code = span_lang
        if "Hant" in class_names:
            desc_data.tags.append("Traditional-Chinese")
        elif "Hans" in class_names:
            desc_data.tags.append("Simplified-Chinese")
        if desc_data.word not in ["", "／"]:
            translate_raw_tags(desc_data)
            desc_lists.append(desc_data)
        after_word = True
    elif span_title != "" and clean_node(wxr, None, span_tag) in [
        "→",
        "⇒",
        ">",
        "?",
    ]:
        raw_tags.append(span_title)
    elif "mention-gloss" in class_names and len(desc_lists) > 0:
        desc_lists[-1].sense = clean_node(wxr, None, span_tag)

    return after_word

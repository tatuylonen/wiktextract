from copy import deepcopy

from mediawiki_langcodes import name_to_code
from wikitextprocessor import (
    HTMLNode,
    LevelNode,
    NodeKind,
    TemplateNode,
    WikiNode,
)

from ...datautils import data_append, data_extend
from ...page import clean_node
from ...tags import valid_tags
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .type_utils import DescendantData, WordData


def extract_descendant_section(
    wxr: WiktextractContext,
    word_entry: WordData,
    level_node: LevelNode,
    is_derived: bool,
):
    desc_list = []
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if (
            isinstance(t_node, TemplateNode)
            and t_node.template_name.lower() == "cjkv"
        ):
            desc_list.extend(extract_cjkv_template(wxr, t_node))

    seen_lists = set()
    # get around unnecessarily pre-expanded "top" template
    for list_node in level_node.find_child_recursively(NodeKind.LIST):
        if list_node in seen_lists:
            continue
        seen_lists.add(list_node)
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            desc_list.extend(
                extract_desc_list_item(wxr, list_item, [], seen_lists, [])[0]
            )

    if is_derived:
        for data in desc_list:
            if "derived" not in data.get("tags", []):
                data_append(data, "tags", "derived")
    if len(desc_list) > 0:
        data_extend(word_entry, "descendants", desc_list)


def extract_cjkv_template(
    wxr: WiktextractContext, t_node: TemplateNode
) -> list[DescendantData]:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(t_node), expand_all=True
    )
    seen_lists = set()
    desc_list = []
    for list_node in expanded_template.find_child_recursively(NodeKind.LIST):
        if list_node in seen_lists:
            continue
        seen_lists.add(list_node)
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            desc_list.extend(
                extract_desc_list_item(wxr, list_item, [], seen_lists, [])[0]
            )
    return desc_list


def extract_desc_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    parent_data: list[DescendantData],
    seen_lists: set[WikiNode],
    raw_tags: list[str],
    lang_code: str = "unknown",
    lang_name: str = "unknown",
) -> tuple[list[DescendantData], str, str]:
    # process list item node and <li> tag
    data_list = []
    before_word_raw_tags = []
    after_word = False
    for child in list_item.children:
        if isinstance(child, str) and child.strip().endswith(":"):
            lang_name = child.strip(": \n") or "unknown"
            lang_code = name_to_code(lang_name, "en") or "unknown"
        elif isinstance(child, str) and child.strip() == ",":
            after_word = False
        elif isinstance(child, HTMLNode) and child.tag == "span":
            after_word = extract_desc_span_tag(
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
                if roman != "":
                    data_list[-1]["roman"] = roman
                    if len(
                        data_list
                    ) > 1 and "Traditional-Chinese" in data_list[-2].get(
                        "tags", []
                    ):
                        data_list[-2]["roman"] = roman
        elif isinstance(child, TemplateNode) and child.template_name in [
            "desctree",
            "descendants tree",
            "desc",
            "descendant",
            "ja-r",
            "zh-l",
            "zh-m",
            "link",  # used in Reconstruction pages
            "l",
        ]:
            if child.template_name.startswith("desc"):
                lang_code = child.template_parameters.get(1, "") or "unknown"
            expanded_template = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(child), expand_all=True
            )
            new_data, new_l_code, new_l_name = extract_desc_list_item(
                wxr,
                expanded_template,
                [],  # avoid add twice
                seen_lists,
                raw_tags,
                lang_code,
                lang_name,
            )
            data_list.extend(new_data)
            # save lang data from desc template
            lang_code = new_l_code
            lang_name = new_l_name

    if (
        wxr.wtp.title.startswith("Reconstruction:")
        and len(data_list) == 0
        and (lang_code != "unknown" or lang_name != "unknown")
    ):
        data = DescendantData(lang_code=lang_code, lang=lang_name)
        if len(raw_tags) > 0:
            data["raw_tags"] = raw_tags
        data_list.append(data)

    for ul_tag in list_item.find_html("ul"):
        for li_tag in ul_tag.find_html("li"):
            extract_desc_list_item(wxr, li_tag, data_list, seen_lists, [])
    for next_list in list_item.find_child(NodeKind.LIST):
        if next_list in seen_lists:
            continue
        seen_lists.add(next_list)
        for next_list_item in next_list.find_child(NodeKind.LIST_ITEM):
            extract_desc_list_item(
                wxr, next_list_item, data_list, seen_lists, []
            )

    for p_data in parent_data:
        data_extend(p_data, "descendants", data_list)
    return data_list, lang_code, lang_name


def extract_desc_span_tag(
    wxr: WiktextractContext,
    span_tag: HTMLNode,
    desc_lists: list[DescendantData],
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
        if roman != "":
            desc_lists[-1]["roman"] = clean_node(wxr, None, span_tag)
            if len(desc_lists) > 1 and "Traditional-Chinese" in desc_lists[
                -2
            ].get("tags", []):
                desc_lists[-2]["roman"] = roman
    elif (
        "qualifier-content" in class_names
        or "gender" in class_names
        or "label-content" in class_names
    ) and len(desc_lists) > 0:
        for raw_tag in clean_node(wxr, None, span_tag).split(","):
            raw_tag = raw_tag.strip()
            if raw_tag != "":
                if after_word:
                    data_append(
                        desc_lists[-1],
                        "tags" if raw_tag in valid_tags else "raw_tags",
                        raw_tag,
                    )
                else:
                    before_word_raw_tags.append(raw_tag)
    elif span_lang != "":
        ruby_data, nodes_without_ruby = extract_ruby(wxr, span_tag)
        desc_data = DescendantData(
            lang=lang_name,
            lang_code=lang_code,
            word=clean_node(wxr, None, nodes_without_ruby),
        )
        for raw_tag_list in [before_word_raw_tags, raw_tags]:
            for raw_tag in raw_tag_list:
                data_append(
                    desc_data,
                    "tags" if raw_tag in valid_tags else "raw_tags",
                    raw_tag,
                )
        before_word_raw_tags.clear()
        if len(ruby_data) > 0:
            desc_data["ruby"] = ruby_data
        if desc_data["lang_code"] == "unknown":
            desc_data["lang_code"] = span_lang
        if "Hant" in class_names:
            data_append(desc_data, "tags", "Traditional-Chinese")
        elif "Hans" in class_names:
            data_append(desc_data, "tags", "Simplified-Chinese")
        if desc_data["word"] not in ["", "／"]:
            desc_lists.append(deepcopy(desc_data))
        after_word = True
    elif span_title != "" and clean_node(wxr, None, span_tag) in [
        "→",
        "⇒",
        ">",
        "?",
    ]:
        raw_tags.append(span_title)
    elif "mention-gloss" in class_names and len(desc_lists) > 0:
        sense = clean_node(wxr, None, span_tag)
        if sense != "":
            desc_lists[-1]["sense"] = sense

    return after_word

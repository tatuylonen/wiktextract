from mediawiki_langcodes import name_to_code
from wikitextprocessor.parser import HTMLNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..ruby import extract_ruby
from .models import Descendant, WordEntry
from .tags import translate_raw_tags


def extract_descendant_section(
    wxr: WiktextractContext, level_node: WikiNode, word_entry: WordEntry
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for data in process_desc_list_item(wxr, list_item, []):
                if data.word != "":
                    word_entry.descendants.append(data)
    for node in level_node.find_child(NodeKind.TEMPLATE):
        if node.template_name.lower() == "cjkv":
            process_cjkv_template(wxr, node, word_entry)


def process_cjkv_template(
    wxr: WiktextractContext, template_node: TemplateNode, word_entry: WordEntry
) -> None:
    expanded_template = wxr.wtp.parse(
        wxr.wtp.node_to_wikitext(template_node), expand_all=True
    )
    seen_lists = set()
    for list_node in expanded_template.find_child_recursively(NodeKind.LIST):
        if list_node in seen_lists:
            continue
        seen_lists.add(list_node)
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            for data in process_desc_list_item(wxr, list_item, []):
                if data.word != "":
                    word_entry.descendants.append(data)


def process_desc_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    parent_data: list[Descendant],
    lang_code: str = "",
    lang_name: str = "",
) -> list[Descendant]:
    # process list item node and <li> tag
    data_list = []
    data = Descendant(lang=lang_name, lang_code=lang_code)
    for child in list_item.children:
        if isinstance(child, str) and child.strip().endswith(":"):
            data.lang = child.strip(": ")
            data.lang_code = name_to_code(data.lang, "zh")
        elif isinstance(child, HTMLNode) and child.tag == "span":
            class_names = child.attrs.get("class", "")
            if "Latn" in class_names or "tr" in class_names:
                data.roman = clean_node(wxr, None, child)
            elif "qualifier-content" in class_names:
                raw_tag = clean_node(wxr, None, clean_node(wxr, None, child))
                if raw_tag != "":
                    data.raw_tags.append(raw_tag)
        elif isinstance(child, HTMLNode) and child.tag == "i":
            for span_tag in child.find_html(
                "span", attr_name="class", attr_value="Latn"
            ):
                data.roman = clean_node(wxr, None, span_tag)
        elif isinstance(child, TemplateNode) and child.template_name in [
            "desctree",
            "descendants tree",
            "desc",
            "descendant",
            "ja-r",
            "zh-l",
        ]:
            if child.template_name.startswith("desc"):
                data.lang_code = child.template_parameters.get(1)
            expanded_template = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(child), expand_all=True
            )
            for new_data in process_desc_list_item(
                wxr,
                expanded_template,
                [],  # avoid add twice
                data.lang_code,
                data.lang,
            ):
                if new_data.word != "":
                    data_list.append(new_data)
                else:  # save lang data from desc template
                    data = new_data

    for span_tag in list_item.find_html("span", attr_name="lang"):
        ruby_data, nodes_without_ruby = extract_ruby(wxr, span_tag)
        old_word = data.word
        data.word = clean_node(wxr, None, nodes_without_ruby)
        data.ruby = ruby_data
        if data.lang_code == "":
            data.lang_code = span_tag.attrs["lang"]
        span_lang = span_tag.attrs["lang"]
        if span_lang == "zh-Hant":
            data.tags.append("Traditional Chinese")
        elif span_lang == "zh-Hans":
            if "Traditional Chinese" in data.tags:
                data.tags.remove("Traditional Chinese")
            data.tags.append("Simplified Chinese")
        if data.roman == data.word:
            if old_word == "":
                data.roman = ""
            else:  # roman tag also could have "lang"
                continue
        if data.word not in ["", "／"]:
            data_list.append(data.model_copy(deep=True))

    for ul_tag in list_item.find_html("ul"):
        for li_tag in ul_tag.find_html("li"):
            process_desc_list_item(wxr, li_tag, data_list)
    for next_list in list_item.find_child(NodeKind.LIST):
        for next_list_item in next_list.find_child(NodeKind.LIST_ITEM):
            process_desc_list_item(wxr, next_list_item, data_list)

    translate_raw_tags(data)
    for p_data in parent_data:
        p_data.descendants.extend(data_list)
    if len(data_list) == 0 and data.lang != "":
        # save lang name from desc template
        data_list.append(data)
    return data_list

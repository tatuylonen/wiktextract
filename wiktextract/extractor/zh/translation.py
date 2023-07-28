import re
from collections import defaultdict
from typing import Dict, List, Optional, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.datautils import find_similar_gloss
from wiktextract.page import LEVEL_KINDS, clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import (
    capture_text_in_parentheses,
    contains_list,
    filter_child_wikinodes,
)


def extract_translation(
    wxr: WiktextractContext, page_data: List[Dict], node: WikiNode
) -> None:
    sense_text = ""
    append_to = page_data[-1]
    for child in node.children:
        if isinstance(child, WikiNode):
            if child.kind == NodeKind.TEMPLATE:
                template_name = child.args[0][0].lower()
                if (
                    template_name in {"trans-top", "翻譯-頂", "trans-top-also"}
                    and len(child.args) > 1
                ):
                    sense_text = clean_node(wxr, None, child.args[1][0])
                    append_to = find_similar_gloss(page_data, sense_text)
                elif template_name == "checktrans-top":
                    return
                elif template_name == "see translation subpage":
                    translation_subpage(wxr, page_data, child.args[1:])
            elif child.kind == NodeKind.LIST:
                for list_item_node in filter_child_wikinodes(
                    child, NodeKind.LIST_ITEM
                ):
                    if not contains_list(list_item_node):
                        process_translation_list_item(
                            wxr,
                            page_data,
                            clean_node(wxr, None, list_item_node.children),
                            sense_text,
                            append_to,
                        )
                    else:
                        nested_list_index = 0
                        for index, item_child in enumerate(
                            list_item_node.children
                        ):
                            if (
                                isinstance(item_child, WikiNode)
                                and item_child.kind == NodeKind.LIST
                            ):
                                nested_list_index = index
                                break

                        process_translation_list_item(
                            wxr,
                            page_data,
                            clean_node(
                                wxr,
                                None,
                                list_item_node.children[:nested_list_index],
                            ),
                            sense_text,
                            append_to,
                        )
                        for nested_list_node in filter_child_wikinodes(
                            list_item_node, NodeKind.LIST
                        ):
                            for nested_list_item in filter_child_wikinodes(
                                nested_list_node, NodeKind.LIST_ITEM
                            ):
                                process_translation_list_item(
                                    wxr,
                                    page_data,
                                    clean_node(
                                        wxr, None, nested_list_item.children
                                    ),
                                    sense_text,
                                    append_to,
                                )


def process_translation_list_item(
    wxr: WiktextractContext,
    page_data: List[Dict],
    expanded_text: str,
    sense: str,
    append_to: Dict,
) -> None:
    from .headword_line import GENDERS

    split_results = re.split(r":|：", expanded_text, maxsplit=1)
    if len(split_results) != 2:
        return
    lang_text, words_text = split_results
    lang_text = lang_text.strip()
    words_text = words_text.strip()
    if len(words_text) == 0:
        return
    lang_code = wxr.config.LANGUAGES_BY_NAME.get(lang_text)

    # split words by `,` or `;` that are not inside `()`
    for word_and_tags in re.split(r"[,;、](?![^(]*\))\s*", words_text):
        tags, word = capture_text_in_parentheses(word_and_tags)
        tags = [tag for tag in tags if tag != lang_code]  # rm Wiktionary link
        translation_data = defaultdict(
            list,
            {
                "code": lang_code,
                "lang": lang_text,
                "word": word,
            },
        )
        tags_without_roman = []
        for tag in tags:
            if re.search(r"[a-z]", tag):
                translation_data["roman"] = tag
            else:
                tags_without_roman.append(tag)

        if len(tags_without_roman) > 0:
            translation_data["tags"] = tags_without_roman

        gender = word.split(" ")[-1]
        if gender in GENDERS:
            translation_data["word"] = word.removesuffix(f" {gender}")
            translation_data["tags"].append(GENDERS.get(gender))

        if len(sense) > 0:
            translation_data["sense"] = sense
        append_to["translations"].append(translation_data)


def translation_subpage(
    wxr: WiktextractContext,
    page_data: List[Dict],
    template_args: List[List[str]],
) -> None:
    from .page import ADDITIONAL_EXPAND_TEMPLATES

    page_title = wxr.wtp.title
    target_section = None
    if len(template_args) > 0:
        target_section = template_args[0][0]
    if len(template_args) > 1:
        page_title = template_args[1][0]

    translation_subpage_title = f"{page_title}/翻譯"
    subpage = wxr.wtp.get_page(translation_subpage_title)
    if subpage is None:
        return

    root = wxr.wtp.parse(
        subpage.body,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
    )
    target_section_node = (
        root
        if target_section is None
        else find_subpage_section(wxr, root, target_section)
    )
    translation_node = find_subpage_section(
        wxr, target_section_node, wxr.config.OTHER_SUBTITLES["translations"]
    )
    if translation_node is not None:
        extract_translation(wxr, page_data, translation_node)


def find_subpage_section(
    wxr: WiktextractContext, node: Union[WikiNode, str], target_section: str
) -> Optional[WikiNode]:
    if isinstance(node, WikiNode):
        if node.kind in LEVEL_KINDS:
            section_title = clean_node(wxr, None, node.args)
            if section_title == target_section:
                return node

        for child in node.children:
            returned_node = find_subpage_section(wxr, child, target_section)
            if returned_node is not None:
                return returned_node

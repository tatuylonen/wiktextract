import re
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.datautils import data_append
from wiktextract.page import clean_node
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
    for child in node.children:
        if isinstance(child, WikiNode):
            if child.kind == NodeKind.TEMPLATE:
                template_name = child.args[0][0].lower()
                if (
                    template_name in {"trans-top", "翻譯-頂", "trans-top-also"}
                    and len(child.args) > 1
                ):
                    sense_text = clean_node(wxr, None, child.args[1][0])
                elif template_name == "checktrans-top":
                    sense_text = ""  # TODO page: 自然神論
                # TODO: handle translation subpage, page: 工作
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
                                )


def process_translation_list_item(
    wxr: WiktextractContext,
    page_data: List[Dict],
    expanded_text: str,
    sense: str,
) -> None:
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
        translation_data = {
            "code": lang_code,
            "lang": lang_text,
            "word": word,
        }
        if len(tags) > 0:
            translation_data["tags"] = tags
        # TODO: handle gender text
        if len(sense) > 0:
            translation_data["sense"] = sense
        data_append(wxr, page_data[-1], "translations", translation_data)

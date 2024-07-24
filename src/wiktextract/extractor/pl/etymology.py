from wikitextprocessor.parser import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
) -> None:
    etymology_texts = []
    has_list = False
    for list_item_node in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        text = clean_node(wxr, None, list_item_node.children)
        if len(text) > 0:
            etymology_texts.append(text)
            has_list = True
    if not has_list:
        text = clean_node(wxr, None, level_node.children)
        if len(text) > 0:
            etymology_texts.append(text)

    for data in page_data:
        if data.lang_code == base_data.lang_code:
            data.etymology_texts = etymology_texts
    base_data.etymology_texts = etymology_texts

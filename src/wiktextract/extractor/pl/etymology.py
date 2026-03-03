import re
from collections import defaultdict

from wikitextprocessor.parser import NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: WikiNode,
):
    from .page import match_sense_index

    etymology_texts = defaultdict(list)
    has_list = False
    sense_index = ""
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        e_nodes = []
        for node in list_item.children:
            if isinstance(node, str):
                m = re.search(r"\(([\d\s,-.]+)\)", node)
                if m is not None:
                    sense_index = m.group(1)
                    remain_str = node[m.end() :]
                    if remain_str != "":
                        e_nodes.append(remain_str)
                else:
                    e_nodes.append(node)
            else:
                e_nodes.append(node)
        text = clean_node(wxr, None, e_nodes)
        if len(text) > 0:
            etymology_texts[sense_index].append(text)
            has_list = True
    if not has_list:
        text = clean_node(wxr, None, level_node.children)
        if len(text) > 0:
            etymology_texts[sense_index].append(text)

    for data in page_data:
        if data.lang_code == base_data.lang_code:
            for sense_index, texts in etymology_texts.items():
                if sense_index == "" or match_sense_index(sense_index, data):
                    data.etymology_texts = texts

    base_data.etymology_texts = etymology_texts.get("", [])

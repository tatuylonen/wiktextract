import re

from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry


def extract_expression_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_expression_list_item(wxr, word_entry, list_item)


def extract_expression_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
) -> None:
    from .pos import extract_gloss_list_item

    expression_data = Linkage(word="")
    sense_nodes = []
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.BOLD:
            expression_data.word = clean_node(wxr, None, node)
        elif isinstance(node, str) and ":" in node:
            node = node.lstrip(": ")
            if node != "":
                sense_nodes.append(node)
        elif not (isinstance(node, WikiNode) and node.kind == NodeKind.LIST):
            sense_nodes.append(node)

    sense_str = clean_node(
        wxr,
        None,
        [
            n
            for n in sense_nodes
            if not (
                isinstance(n, TemplateNode) and n.template_name == "escopo2"
            )
        ],
    )
    if sense_str != "":
        gloss_list_item = WikiNode(NodeKind.LIST_ITEM, 0)
        gloss_list_item.children = sense_nodes
        for child_list in list_item.find_child(NodeKind.LIST):
            gloss_list_item.children.append(child_list)
        extract_gloss_list_item(wxr, expression_data, gloss_list_item)
    else:
        for child_list in list_item.find_child(NodeKind.LIST):
            for child_list_item in child_list.find_child(NodeKind.LIST_ITEM):
                extract_gloss_list_item(wxr, expression_data, child_list_item)

    if expression_data.word != "":
        word_entry.expressions.append(expression_data)


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_linkage_list_item(wxr, word_entry, list_item, linkage_type)


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    linkage_type: str,
) -> None:
    linkage_words = []
    sense = ""
    sense_index = 0
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                linkage_words.append(word)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.BOLD:
            bold_str = clean_node(wxr, None, node)
            if re.fullmatch(r"\d+", bold_str):
                sense_index = int(bold_str)
        elif isinstance(node, str):
            m = re.search(r"\((.+)\)", node)
            if m is not None:
                sense = m.group(1)

    for word in linkage_words:
        getattr(word_entry, linkage_type).append(
            Linkage(word=word, sense=sense, sense_index=sense_index)
        )

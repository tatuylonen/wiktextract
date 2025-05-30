from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .tags import translate_raw_tags


def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    linkages = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            linkages.extend(
                extract_proverb_list_item(wxr, list_item)
                if linkage_type == "proverbs"
                else extract_linkage_list_item(wxr, list_item)
            )

    for l_data in linkages:
        translate_raw_tags(l_data)

    for data in page_data:
        if data.lang_code == page_data[-1].lang_code:
            getattr(data, linkage_type).extend(linkages)


def extract_linkage_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Linkage]:
    raw_tags = []
    linkages = []
    for node in list_item.children:
        if isinstance(node, WikiNode):
            match node.kind:
                case NodeKind.LINK:
                    node_str = clean_node(wxr, None, node)
                    if node_str != "":
                        linkages.append(
                            Linkage(word=node_str, raw_tags=raw_tags)
                        )
                        raw_tags.clear()
                case NodeKind.TEMPLATE | NodeKind.ITALIC:
                    node_str = clean_node(wxr, None, node)
                    if node_str.startswith("(") and node_str.endswith(")"):
                        raw_tags.append(node_str.strip("()"))
        elif isinstance(node, str):
            for word_str in node.split(","):
                word_str = word_str.strip()
                if word_str.startswith("(") and word_str.endswith(")"):
                    raw_tags.append(word_str.strip("()"))
                elif word_str != "":
                    linkages.append(Linkage(word=word_str, raw_tags=raw_tags))
                    raw_tags.clear()
    return linkages


def extract_proverb_list_item(
    wxr: WiktextractContext, list_item: WikiNode
) -> list[Linkage]:
    proverb = Linkage(word="")
    for index, node in enumerate(list_item.children):
        if isinstance(node, WikiNode) and node.kind == NodeKind.ITALIC:
            proverb.word = clean_node(wxr, None, node)
        elif isinstance(node, str) and ":" in node:
            proverb.sense = clean_node(
                wxr,
                None,
                [node[node.index(":") + 1 :]] + list_item.children[index + 1 :],
            )
            break
    return [proverb] if proverb.word != "" else []

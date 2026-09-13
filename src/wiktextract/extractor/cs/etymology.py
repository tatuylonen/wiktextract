from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext, base_data: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            links: list[tuple[str, str]] = []
            e_str = clean_node(
                wxr, None, list_item.children, link_collector=links
            )
            if e_str != "":
                base_data.etymology_texts.append(e_str)
                base_data.etymology_links.extend(links)
    if len(base_data.etymology_texts) == 0:
        links = []
        e_str = clean_node(
            wxr,
            base_data,
            list(
                level_node.invert_find_child(
                    LEVEL_KIND_FLAGS, include_empty_str=True
                )
            ),
            link_collector=links,
        )
        if e_str != "":
            base_data.etymology_texts.append(e_str)
            base_data.etymology_links.extend(links)

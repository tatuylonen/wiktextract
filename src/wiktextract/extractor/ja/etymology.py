from wikitextprocessor.parser import LEVEL_KIND_FLAGS, LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import WordEntry


def extract_etymology_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    base_data: WordEntry,
    level_node: LevelNode,
) -> None:
    etymology_texts = []
    etymology_links: list[tuple[str, str]] = []
    cats = {}
    for list_node in level_node.find_child(NodeKind.LIST):
        # don't use `find_child_recursively` to avoid lists in subsection
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            e_links: list[tuple[str, str]] = []
            text = clean_node(
                wxr,
                cats,
                list(
                    list_item.invert_find_child(
                        NodeKind.LIST, include_empty_str=True
                    )
                ),
                link_collector=e_links,
            )
            if len(text) > 0:
                etymology_texts.append(text)
                etymology_links.extend(e_links)
    if len(etymology_texts) == 0:
        e_links: list[tuple[str, str]] = []
        text = clean_node(
            wxr,
            cats,
            list(
                level_node.invert_find_child(
                    LEVEL_KIND_FLAGS, include_empty_str=True
                )
            ),
            link_collector=e_links,
        )
        if len(text) > 0:
            etymology_texts.append(text)
            etymology_links.extend(e_links)
    for link in level_node.find_child(NodeKind.LINK):
        clean_node(wxr, cats, link)
    base_data.etymology_texts = etymology_texts
    base_data.etymology_links = etymology_links
    base_data.categories.extend(cats.get("categories", []))
    if level_node.kind != NodeKind.LEVEL3:  # under POS section
        for data in page_data:
            if (
                data.lang_code == base_data.lang_code
                and len(data.etymology_texts) == 0
            ):
                data.etymology_texts = etymology_texts
                data.etymology_links = etymology_links.copy()
                data.categories.extend(cats.get("categories", []))

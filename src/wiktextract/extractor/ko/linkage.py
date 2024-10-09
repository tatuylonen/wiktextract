from wikitextprocessor import LevelNode, NodeKind

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    if linkage_type == "proverbs":
        extract_proverb_section(wxr, word_entry, level_node)
    elif level_node.contain_node(NodeKind.LIST):
        for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
            for link_node in list_item.find_child(NodeKind.LINK):
                word = clean_node(wxr, None, link_node)
                if word != "":
                    getattr(word_entry, linkage_type).append(Linkage(word=word))


def extract_proverb_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
) -> None:
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        linkage = Linkage(word="")
        for index, child in enumerate(list_item.children):
            if isinstance(child, str) and ":" in child:
                linkage.word = clean_node(wxr, None, list_item.children[:index])
                linkage.word += child[: child.index(":")].strip()
                linkage.sense = child[child.index(":") + 1 :].strip()
                linkage.sense += clean_node(
                    wxr, None, list_item.children[index + 1 :]
                )
                break
        if linkage.word != "":
            word_entry.proverbs.append(linkage)

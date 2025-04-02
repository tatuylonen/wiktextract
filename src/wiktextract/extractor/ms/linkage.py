from wikitextprocessor import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Form, Linkage, WordEntry
from .section_titles import LINKAGE_SECTIONS


def extract_form_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    tags: list[str],
) -> None:
    for t_node in level_node.find_child(NodeKind.TEMPLATE):
        if t_node.template_name in ["ARchar", "Arab", "PSchar", "SDchar"]:
            word = clean_node(wxr, None, t_node)
            if word != "":
                word_entry.forms.append(Form(form=word, tags=tags))


def extract_linkage_section(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_linkage_list_item(wxr, word_entry, list_item)


def extract_linkage_list_item(
    wxr: WiktextractContext, word_entry: WordEntry, list_item: WikiNode
) -> None:
    linkage_name = clean_node(wxr, None, list_item.children)
    if linkage_name not in LINKAGE_SECTIONS:
        return
    for node in list_item.definition:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            word = clean_node(wxr, None, node)
            if word != "":
                getattr(word_entry, LINKAGE_SECTIONS[linkage_name]).append(
                    Linkage(word=word)
                )
        elif isinstance(node, str):
            for word in node.split(","):
                word = word.strip(" .\n")
                if word != "":
                    getattr(word_entry, LINKAGE_SECTIONS[linkage_name]).append(
                        Linkage(word=word)
                    )

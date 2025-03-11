from wikitextprocessor import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .tags import translate_raw_tags


def extract_linkage_section(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    l_type: str,
    tags: list[str],
) -> None:
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            extract_linkage_list_item(wxr, word_entry, list_item, l_type, tags)
    for link_node in level_node.find_child(NodeKind.LINK):
        word = clean_node(wxr, None, link_node)
        if word != "":
            getattr(word_entry, l_type).append(Linkage(word=word, tags=tags))


def extract_linkage_list_item(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    list_item: WikiNode,
    l_type: str,
    tags: list[str],
) -> None:
    sense = ""
    l_list = []
    for node in list_item.children:
        if isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            l_data = Linkage(
                word=clean_node(wxr, None, node), sense=sense, tags=tags
            )
            if l_data.word != "":
                l_list.append(l_data)
        elif isinstance(node, TemplateNode):
            if node.template_name in ["anlam", "mânâ", "mana"]:
                sense = clean_node(wxr, None, node).strip("(): ")
            elif node.template_name == "şerh" and len(l_list) > 0:
                raw_tag = clean_node(wxr, None, node).strip("() ")
                if raw_tag != "":
                    l_list[-1].raw_tags.append(raw_tag)
                    translate_raw_tags(l_list[-1])
    getattr(word_entry, l_type).extend(l_list)

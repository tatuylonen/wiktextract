import re

from wikitextprocessor.parser import LevelNode, NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .tags import translate_raw_tags
from .utils import extract_sense_index


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    linkage_list = []
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_linkage_list_item(wxr, list_item, linkage_list, linkage_type)
    getattr(word_entry, linkage_type).extend(linkage_list)


def process_linkage_list_item(
    wxr: WiktextractContext,
    list_item_node: WikiNode,
    linkage_list: list[Linkage],
    linkage_type: str,
) -> None:
    sense_idx = ""
    raw_tags = []
    after_dash = False
    note_nodes = []
    for child in list_item_node.children:
        if after_dash:
            note_nodes.append(child)
        elif isinstance(child, str):
            if child.startswith("["):
                sense_idx, _ = extract_sense_index(child)
            elif "," in child or ";" in child:
                raw_tags.clear()
            if linkage_type == "expressions" and contains_dash(child):
                after_dash = True
                note_nodes.append(child)
        elif isinstance(child, WikiNode) and child.kind == NodeKind.ITALIC:
            raw_tag = clean_node(wxr, None, child)
            if raw_tag.endswith(":"):
                raw_tags.append(raw_tag.strip(": "))
            else:
                for link_node in child.find_child(NodeKind.LINK):
                    link_text = clean_node(wxr, None, link_node)
                    if link_text != "":
                        linkage = Linkage(
                            word=link_text,
                            sense_index=sense_idx,
                            raw_tags=raw_tags,
                        )
                        translate_raw_tags(linkage)
                        linkage_list.append(linkage)
        elif isinstance(child, TemplateNode) and child.template_name.endswith(
            "."
        ):
            raw_tag = clean_node(wxr, None, child)
            raw_tag = raw_tag.strip(",: ")
            if raw_tag != "":
                raw_tags.append(raw_tag)
        elif isinstance(child, WikiNode) and child.kind == NodeKind.LINK:
            word = clean_node(wxr, None, child)
            if not word.startswith("Verzeichnis:") and len(word) > 0:
                # https://de.wiktionary.org/wiki/Wiktionary:Verzeichnis
                # ignore index namespace links
                linkage = Linkage(
                    word=word, sense_index=sense_idx, raw_tags=raw_tags
                )
                translate_raw_tags(linkage)
                linkage_list.append(linkage)

    if len(note_nodes) > 0 and len(linkage_list) > 0:
        linkage_list[-1].note = clean_node(wxr, None, note_nodes).strip(
            "–—―‒- "
        )


def contains_dash(text: str) -> bool:
    return re.search(r"[–—―‒-]", text) is not None

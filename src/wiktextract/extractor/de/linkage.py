import re
from typing import Optional

from wikitextprocessor.parser import LevelNode, NodeKind, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .utils import extract_sense_index


def extract_linkages(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    level_node: LevelNode,
    linkage_type: str,
) -> None:
    linkage_list = []
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            sense_idx = ""
            for child in list_item.children:
                if isinstance(child, str) and child.startswith("["):
                    sense_idx, _ = extract_sense_index(child)
            # Extract links
            if linkage_type == "expressions":
                after_dash = False
                note_nodes = []
                for child in list_item.children:
                    if after_dash:
                        note_nodes.append(child)
                    elif isinstance(child, str) and contains_dash(child):
                        after_dash = True
                        note_nodes.append(child)
                    elif (
                        isinstance(child, WikiNode)
                        and child.kind == NodeKind.LINK
                    ):
                        new_data = process_link(wxr, sense_idx, child)
                        if new_data is not None:
                            linkage_list.append(new_data)
                note_text = clean_node(wxr, None, note_nodes).strip("–—―‒- ")
                if len(linkage_list) > 0:
                    linkage_list[-1].note = note_text
            else:
                for link_node in list_item.find_child(NodeKind.LINK):
                    new_data = process_link(wxr, sense_idx, link_node)
                    if new_data is not None:
                        linkage_list.append(new_data)

            # Check for potentially missed data
            for non_link in list_item.invert_find_child(NodeKind.LINK):
                if (
                    linkage_type == "expressions"
                    and isinstance(non_link, str)
                    and contains_dash(non_link)
                ):
                    break
                elif isinstance(non_link, str) and (
                    non_link.startswith("[") or len(non_link.strip()) <= 3
                ):
                    continue
                wxr.wtp.debug(
                    f"Unexpected non-link node '{non_link}' in: {list_item}",
                    sortid="extractor/de/linkages/extract_linkages/84",
                )

    pre_list = getattr(word_entry, linkage_type)
    pre_list.extend(linkage_list)


def process_link(
    wxr: WiktextractContext,
    sense_idx: str,
    link_node: WikiNode,
) -> Optional[Linkage]:
    word = clean_node(wxr, None, link_node)
    if word.startswith("Verzeichnis:") or len(word) == 0:
        # https://de.wiktionary.org/wiki/Wiktionary:Verzeichnis
        # Links to this namesapce pages are ignored,
        # should find what it contains later
        return None
    return Linkage(word=word, sense_index=sense_idx)


def contains_dash(text: str) -> bool:
    return re.search(r"[–—―‒-]", text) is not None

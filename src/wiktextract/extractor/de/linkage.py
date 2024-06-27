import re

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import split_senseids
from .models import Linkage, WordEntry
from .section_titles import LINKAGE_TITLES


def extract_linkages(
    wxr: WiktextractContext, word_entry: WordEntry, level_node: LevelNode
):
    linkage_type = LINKAGE_TITLES.get(level_node.largs[0][0])
    for list_node in level_node.find_child(NodeKind.LIST):
        for list_item in list_node.find_child(NodeKind.LIST_ITEM):
            # Get the senseids
            senseids = (
                split_senseids(list_item.children[0])
                if (
                    len(list_item.children) > 0
                    and isinstance(list_item.children[0], str)
                )
                else []
            )

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
                        process_link(
                            wxr, word_entry, linkage_type, senseids, child
                        )
                note_text = clean_node(wxr, None, note_nodes).strip("–—―‒- ")
                if len(word_entry.expressions) > 0:
                    word_entry.expressions[-1].note = note_text

            else:
                for link in list_item.find_child(NodeKind.LINK):
                    process_link(wxr, word_entry, linkage_type, senseids, link)

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
                    f"Found unexpected non-link node '{non_link}' in: {list_item}",
                    sortid="extractor/de/linkages/extract_linkages/84",
                )


def process_link(
    wxr: WiktextractContext,
    word_entry: WordEntry,
    linkage_type: str,
    sense_ids: list[str],
    link_node: WikiNode,
):
    word = clean_node(wxr, None, link_node)
    if word.startswith("Verzeichnis:") or len(word) == 0:
        # https://de.wiktionary.org/wiki/Wiktionary:Verzeichnis
        # Links to this namesapce pages are ignored,
        # should find what it contains later
        return
    if linkage_type in word_entry.model_fields:
        linkage = Linkage(word=word)
        if len(sense_ids) > 0:
            linkage.sense_id = sense_ids[0]
        getattr(word_entry, linkage_type).append(linkage)
    else:
        wxr.wtp.debug(
            f"Linkage type {linkage_type} not in entry model fields",
            sortid="extractor/de/linkages/108}",
        )


def contains_dash(text: str) -> bool:
    return re.search(r"[–—―‒-]", text) is not None

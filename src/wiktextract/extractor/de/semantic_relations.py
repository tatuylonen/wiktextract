import re
from typing import Dict, List

from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.parser import LevelNode

from wiktextract.extractor.de.utils import split_senseids
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext

SEMANTIC_RELATIONS = {
    "Gegenwörter": "antonyms",
    "Holonyme": "holonyms",
    "Oberbegriffe": "hypernyms",
    "Redewendungen": "expressions",
    "Sinnverwandte Wörter": "coordinate_terms",
    "Sprichwörter": "proverbs",
    "Synonyme": "synonyms",
    "Unterbegriffe": "hyponyms",
    "Wortbildungen": "derived",
}


def extract_semantic_relations(
    wxr: WiktextractContext, page_data: List[Dict], level_node: LevelNode
):
    relation_key = SEMANTIC_RELATIONS.get(level_node.largs[0][0])
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
            semantic_links = []
            if relation_key == "expressions":
                for child in list_item.children:
                    if isinstance(child, str) and contains_dash(child):
                        # XXX Capture the part after the dash as an explanatory note to the expression, e.g.:
                        # https://de.wiktionary.org/wiki/Beispiel
                        # ":[[ein gutes Beispiel geben]] – als [[Vorbild]] zur [[Nachahmung]] [[dienen]]/[[herausfordern]]"
                        break
                    elif (
                        isinstance(child, WikiNode)
                        and child.kind == NodeKind.LINK
                    ):
                        process_link(wxr, semantic_links, child)
            else:
                for link in list_item.find_child(NodeKind.LINK):
                    process_link(wxr, semantic_links, link)

            # Add links to the page data
            if len(page_data[-1]["senses"]) == 1:
                page_data[-1]["senses"][0][relation_key].extend(semantic_links)
            elif len(senseids) > 0:
                for senseid in senseids:
                    for sense in page_data[-1]["senses"]:
                        if sense["senseid"] == senseid:
                            sense[relation_key].extend(semantic_links)
            else:
                page_data[-1][relation_key].extend(semantic_links)

            # Check for potentially missed data
            for non_link in list_item.invert_find_child(NodeKind.LINK):
                if (
                    relation_key == "expressions"
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
                    sortid="extractor/de/semantic_relations/extract_semantic_relations/84",
                )


def process_link(
    wxr: WiktextractContext, semantic_links: List[str], link: WikiNode
):
    clean_link = clean_node(wxr, {}, link)
    if clean_link.startswith("Verzeichnis:"):
        return
    semantic_links.append(clean_link)


def contains_dash(text: str):
    return re.search(r"[–—―‒-]", text)

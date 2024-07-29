import re
from collections import defaultdict

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .tags import translate_raw_tags

LINKAGE_TYPES = {
    "antonimy": "antonyms",
    "hiperonimy": "hypernyms",
    "hiponimy": "hyponyms",
    "holonimy": "holonyms",
    "meronimy": "meronyms",
    "synonimy": "synonyms",
    "wyrazy pokrewne": "related",
    "związki frazeologiczne": "proverbs",
}


def extract_linkage_section(
    wxr: WiktextractContext,
    page_data: list[WordEntry],
    level_node: WikiNode,
    linkage_type: str,
    lang_code: str,
) -> None:
    linkages = defaultdict(list)
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_linakge_list_item(wxr, list_item, linkages)

    for data in page_data:
        if data.lang_code == lang_code:
            for sense in data.senses:
                if sense.sense_index in linkages:
                    getattr(data, linkage_type).extend(
                        linkages[sense.sense_index]
                    )
                    del linkages[sense.sense_index]
            getattr(data, linkage_type).extend(linkages.get("", []))

    if "" in linkages:
        del linkages[""]
    for data in page_data:
        if data.lang_code == lang_code:
            for linkage_list in linkages.values():
                getattr(data, linkage_type).extend(linkage_list)
            break


def process_linakge_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    linkages: dict[str, list[Linkage]],
) -> None:
    raw_tags = []
    sense_index = ""
    last_linkage = None
    for node in list_item.children:
        if isinstance(node, str):
            m = re.search(r"\(\d+\.\d+\)", node)
            if m is not None:
                sense_index = m.group(0).strip("()")
            if ";" in node or "•" in node:
                raw_tags.clear()
                last_linkage = None
        elif isinstance(node, TemplateNode):
            raw_tag = clean_node(wxr, None, node)
            if raw_tag.endswith("."):
                if last_linkage is None:
                    raw_tags.append(raw_tag)
                else:
                    last_linkage.raw_tags.append(raw_tag)
                    translate_raw_tags(last_linkage)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            linkage = Linkage(
                word=clean_node(wxr, None, node),
                sense_index=sense_index,
                raw_tags=raw_tags,
            )
            translate_raw_tags(linkage)
            linkages[sense_index].append(linkage)
            last_linkage = linkage

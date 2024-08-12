import re
from collections import defaultdict
from typing import Optional

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
    "kolokacje": "related",
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
    from .page import match_sense_index

    linkages = defaultdict(list)
    for list_item in level_node.find_child_recursively(NodeKind.LIST_ITEM):
        process_linkage_list_item(wxr, list_item, linkages)

    matched_indexes = set()
    for data in page_data:
        if data.lang_code == lang_code:
            for sense_index in linkages.keys():
                if match_sense_index(sense_index, data):
                    getattr(data, linkage_type).extend(linkages[sense_index])
                    matched_indexes.add(sense_index)
            getattr(data, linkage_type).extend(linkages.get("", []))

    # add not matched data
    if "" in linkages:
        del linkages[""]
    for data in page_data:
        if data.lang_code == lang_code:
            for sense_index, linkage_list in linkages.items():
                if sense_index not in matched_indexes:
                    getattr(data, linkage_type).extend(linkage_list)
            break


def process_linkage_list_item(
    wxr: WiktextractContext,
    list_item: WikiNode,
    linkages: dict[str, list[Linkage]],
) -> None:
    raw_tags = []
    sense_index = ""
    last_linkage = None
    for node in list_item.children:
        if isinstance(node, str):
            m = re.search(r"\([\d\s,-.]+\)", node)
            if m is not None:
                sense_index = m.group(0).strip("()")
            for sep in [";", "•", ","]:
                if sep in node:
                    part_of_word = node[: node.index(sep)].strip()
                    if len(part_of_word) > 0 and last_linkage is not None:
                        last_linkage.word += " " + part_of_word
                    raw_tags.clear()
                    last_linkage = None
                    break
        elif isinstance(node, TemplateNode):
            process_linkage_template(
                wxr, node, linkages, sense_index, last_linkage, raw_tags
            )
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LINK:
            linkage = Linkage(
                word=clean_node(wxr, None, node),
                sense_index=sense_index,
                raw_tags=raw_tags,
            )
            translate_raw_tags(linkage)
            linkages[sense_index].append(linkage)
            last_linkage = linkage


def process_linkage_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    linkages: dict[str, list[Linkage]],
    sense_index: str,
    last_linkage: Optional[Linkage],
    raw_tags: list[str],
) -> None:
    if template_node.template_name == "furi":
        expanded_text = clean_node(wxr, None, template_node)
        if "(" in expanded_text:
            furigana_start = expanded_text.rindex("(")
            linkage = Linkage(
                word=expanded_text[:furigana_start],
                furigana=expanded_text[furigana_start:].strip("() "),
                sense_index=sense_index,
            )
            linkages[sense_index].append(linkage)
            last_linkage = linkage
    else:
        raw_tag = clean_node(wxr, None, template_node)
        if raw_tag.endswith("."):
            if last_linkage is None:
                raw_tags.append(raw_tag)
            else:
                last_linkage.raw_tags.append(raw_tag)
                translate_raw_tags(last_linkage)

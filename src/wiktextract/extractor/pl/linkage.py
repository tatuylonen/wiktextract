import re
from collections import defaultdict

from wikitextprocessor.parser import NodeKind, TemplateNode, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from .models import Linkage, WordEntry
from .tags import TAGS, translate_raw_tags

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
    word_nodes = []
    translation_nodes = []
    is_translation = False
    for node in list_item.children:
        if isinstance(node, str):
            m = re.search(r"\([\d\s,-.]+\)", node)
            if m is not None:
                sense_index = m.group(0).strip("()")
                node = node[m.end() :]

            if "→" in node:
                is_translation = True
                tr_start = node.index("→")
                word_nodes.append(node[:tr_start])
                translation_nodes.append(node[tr_start + 1 :])
            else:
                has_sep = False
                for sep in [";", "•", ","]:
                    if sep in node:
                        has_sep = True
                        sep_index = node.index(sep)
                        if is_translation:
                            translation_nodes.append(node[:sep_index])
                        else:
                            word_nodes.append(node[:sep_index])
                        linkage = Linkage(
                            word=clean_node(wxr, None, word_nodes),
                            translation=clean_node(
                                wxr, None, translation_nodes
                            ),
                            raw_tags=raw_tags,
                            sense_index=sense_index,
                        )
                        translate_raw_tags(linkage)
                        if len(linkage.word) > 0:
                            linkages[sense_index].append(linkage)

                        word_nodes.clear()
                        translation_nodes.clear()
                        is_translation = False
                        raw_tags.clear()
                        word_nodes.append(node[sep_index + 1 :])
                        break
                if not has_sep:
                    if is_translation:
                        translation_nodes.append(node)
                    else:
                        word_nodes.append(node)
        elif isinstance(node, TemplateNode):
            process_linkage_template(
                wxr,
                node,
                linkages,
                sense_index,
                is_translation,
                word_nodes,
                translation_nodes,
                raw_tags,
            )
        elif is_translation:
            translation_nodes.append(node)
        elif isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
            continue
        else:
            word_nodes.append(node)

    if len(word_nodes) > 0:
        word = clean_node(wxr, None, word_nodes)
        if len(word) > 0:
            linkage = Linkage(
                word=word,
                translation=clean_node(wxr, None, translation_nodes),
                raw_tags=raw_tags,
                sense_index=sense_index,
            )
            translate_raw_tags(linkage)
            linkages[sense_index].append(linkage)


def process_linkage_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    linkages: dict[str, list[Linkage]],
    sense_index: str,
    is_translation: bool,
    word_nodes: list[WikiNode],
    tr_nodes: list[WikiNode],
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
    else:
        raw_tag = clean_node(wxr, None, template_node)
        if raw_tag.endswith(".") or raw_tag in TAGS:
            raw_tags.append(raw_tag)
        elif is_translation:
            tr_nodes.append(raw_tag)
        else:
            word_nodes.append(raw_tag)

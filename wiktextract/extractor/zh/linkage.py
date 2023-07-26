from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.datautils import find_similar_gloss
from wiktextract.page import LEVEL_KINDS, clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import (
    capture_text_in_parentheses,
    split_chinese_variants,
    strip_nodes,
)


def extract_linkages(
    wxr: WiktextractContext,
    page_data: List[Dict],
    nodes: List[Union[WikiNode, str]],
    linkage_type: str,
    sense: str,
    append_to: Dict,
) -> Tuple[str, Dict]:
    """
    Return linkage sense text for `sense` template inside a list item node.
    """
    strip_sense_chars = "()（）:："
    sense_template_names = {"s", "sense"}
    for node in strip_nodes(nodes):
        if isinstance(node, str) and len(sense) == 0:
            sense = node.strip(strip_sense_chars)
            append_to = find_similar_gloss(page_data, sense)
        elif isinstance(node, WikiNode):
            if node.kind == NodeKind.LIST_ITEM:
                not_term_indexes = set()
                filtered_children = list(strip_nodes(node.children))
                linkage_data = defaultdict(list)
                for index, item_child in enumerate(filtered_children):
                    if (
                        isinstance(item_child, WikiNode)
                        and item_child.kind == NodeKind.TEMPLATE
                    ):
                        template_name = item_child.args[0][0].lower()
                        if template_name in sense_template_names:
                            not_term_indexes.add(index)
                            sense = clean_node(wxr, None, item_child).strip(
                                strip_sense_chars
                            )
                            append_to = find_similar_gloss(page_data, sense)
                            if index == len(filtered_children) - 1:
                                # sense template before entry list
                                return sense, append_to
                        elif template_name in {"qualifier", "qual"}:
                            not_term_indexes.add(index)
                            linkage_data["tags"].append(
                                clean_node(wxr, None, item_child).strip("()")
                            )
                # sense template before entry and they are inside the same
                # list item
                terms = clean_node(
                    wxr,
                    None,
                    [
                        n
                        for n_index, n in enumerate(filtered_children)
                        if n_index not in not_term_indexes
                    ],
                )
                roman, terms = capture_text_in_parentheses(terms)
                roman = roman[0] if len(roman) > 0 else None
                if roman is not None:
                    linkage_data["roman"] = roman
                if sense is not None:
                    linkage_data["sense"] = sense
                for term in terms.split("、"):
                    for variant_type, variant_term in split_chinese_variants(
                        term
                    ):
                        final_linkage_data = deepcopy(linkage_data)
                        final_linkage_data["word"] = variant_term
                        if variant_type is not None:
                            final_linkage_data[
                                "language_variant"
                            ] = variant_type
                        append_to["linkage_type"].append(final_linkage_data)
            elif node.kind == NodeKind.TEMPLATE:
                template_name = node.args[0][0].lower()
                if template_name in sense_template_names:
                    sense = clean_node(wxr, None, node).strip(strip_sense_chars)
                elif template_name.endswith("-saurus"):
                    extract_saurus_template(
                        wxr, node, page_data, linkage_type, sense, append_to
                    )
                elif template_name == "zh-dial":
                    extract_zh_dial_template(
                        wxr, node, linkage_type, sense, append_to
                    )
                else:
                    expanded_node = wxr.wtp.parse(
                        wxr.wtp.node_to_wikitext(node), expand_all=True
                    )
                    extract_linkages(
                        wxr,
                        page_data,
                        [expanded_node],
                        linkage_type,
                        sense,
                        append_to,
                    )
            elif node.kind in LEVEL_KINDS:
                from .page import parse_section

                base_data = defaultdict(
                    list,
                    {
                        "lang": page_data[-1].get("lang"),
                        "lang_code": page_data[-1].get("lang_code"),
                        "word": wxr.wtp.title,
                    },
                )
                parse_section(wxr, page_data, base_data, node)
            elif len(node.children) > 0:
                returned_sense, returned_append_target = extract_linkages(
                    wxr,
                    page_data,
                    node.children,
                    linkage_type,
                    sense,
                    append_to,
                )
                if len(returned_sense) > 0:
                    sense = returned_sense
                    append_to = returned_append_target


def extract_saurus_template(
    wxr: WiktextractContext,
    node: WikiNode,
    page_data: Dict,
    linkage_type: str,
    sense: Optional[str],
    append_to: Dict,
) -> None:
    """
    Extract data from template names end with "-saurus", like "zh-syn-saurus"
    and "zh-ant-saurus". These templates get data from thesaurus pages, search
    the thesaurus database to avoid parse these pages again.
    """
    from wiktextract.thesaurus import search_thesaurus

    thesaurus_page_title = node.args[-1][0]
    for thesaurus in search_thesaurus(
        wxr.thesaurus_db_conn,
        thesaurus_page_title,
        page_data[-1].get("lang_code"),
        page_data[-1].get("pos"),
        linkage_type,
    ):
        if thesaurus.term == wxr.wtp.title:
            continue
        linkage_data = {"word": thesaurus.term}
        if thesaurus.roman is not None:
            linkage_data["roman"] = thesaurus.roman
        if thesaurus.tags is not None:
            linkage_data["tags"] = thesaurus.tags.split("|")
        if thesaurus.language_variant is not None:
            linkage_data["language_variant"] = thesaurus.language_variant
        if sense is not None:
            linkage_data["sense"] = sense
        elif thesaurus.sense is not None:
            linkage_data["sense"] = thesaurus.sense
        append_to[linkage_type].append(linkage_data)


def extract_zh_dial_template(
    wxr: WiktextractContext,
    node: Union[WikiNode, str],
    linkage_type: str,
    sense: Optional[str],
    append_to: Dict,
) -> None:
    dial_data = {}
    node = wxr.wtp.parse(wxr.wtp.node_to_wikitext(node), expand_all=True)
    extract_zh_dial_recursively(wxr, node, dial_data, None)
    for term, tags in dial_data.items():
        linkage_data = {"word": term}
        if sense is not None:
            linkage_data["sense"] = sense
        if len(tags) > 0:
            linkage_data["tags"] = tags
        append_to[linkage_type].append(linkage_data)


def extract_zh_dial_recursively(
    wxr: WiktextractContext,
    node: Union[WikiNode, str],
    dial_data: Dict[str, List[str]],
    header_lang: Optional[str],
) -> str:
    if isinstance(node, WikiNode) and node.kind == NodeKind.TABLE_ROW:
        tags = []
        for child in node.children:
            if isinstance(child, WikiNode):
                if child.kind == NodeKind.TABLE_HEADER_CELL:
                    header_lang = clean_node(wxr, None, child)
                elif child.kind == NodeKind.TABLE_CELL:
                    tags.append(clean_node(wxr, None, child))
        if len(tags) < 1:  # table header
            return
        terms = tags[-1].removesuffix(" dated")
        tags = tags[:-1]
        if header_lang is not None:
            tags = [header_lang] + tags
        for term in terms.split("、"):
            if term == wxr.wtp.title:
                continue
            old_tags = dial_data.get(term, [])
            old_tag_set = set(old_tags)
            new_tags = old_tags
            for tag in tags:
                if tag not in old_tag_set:
                    new_tags.append(tag)
            dial_data[term] = new_tags
    elif isinstance(node, WikiNode):
        for child in node.children:
            returned_lang = extract_zh_dial_recursively(
                wxr, child, dial_data, header_lang
            )
            if returned_lang is not None:
                header_lang = returned_lang
    return header_lang

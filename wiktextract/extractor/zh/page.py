import copy
import logging
import re
import string

from collections import defaultdict
from typing import Dict, List, Union, Any

from wikitextprocessor import WikiNode, NodeKind
from wiktextract.page import clean_node, LEVEL_KINDS
from wiktextract.wxr_context import WiktextractContext

from .example import extract_examples
from .headword_line import extract_headword_line
from .linkage import extract_linkages
from .pronunciation import extract_pronunciation_recursively
from ..share import strip_nodes, contains_list, filter_child_wikinodes
from ..ruby import extract_ruby


# Templates that are used to form panels on pages and that
# should be ignored in various positions
PANEL_TEMPLATES = {
    "CJKV",
    "French personal pronouns",
    "French possessive adjectives",
    "French possessive pronouns",
    "Han etym",
    "Japanese demonstratives",
    "Latn-script",
    "Webster 1913",
    "attention",
    "attn",
    "character info",
    "character info/new",
    "character info/var",
    "delete",
    "dial syn",
    "dialect synonyms",
    "examples",
    "hu-corr",
    "hu-suff-pron",
    "interwiktionary",
    "ja-kanjitab",
    "ko-hanja-search",
    "maintenance box",
    "maintenance line",
    "merge",
    "morse links",
    "move",
    "multiple images",
    "picdic",
    "picdicimg",
    "picdiclabel",
    "punctuation",
    "reconstructed",
    "request box",
    "rfap",
    "rfc",
    "rfc-header",
    "rfc-level",
    "rfc-sense",
    "rfd",
    "rfdate",
    "rfdatek",
    "rfdef",
    "rfe",
    "rfe/dowork",
    "rfgender",
    "rfi",
    "rfinfl",
    "rfp",
    "rfquotek",
    "rfscript",
    "rftranslit",
    "selfref",
    "stroke order",
    "t-needed",
    "unblock",
    "unsupportedpage",
    "wrongtitle",
    "zh-forms",
    "zh-hanzi-box",
}

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES = {
    "list:compass points/",
    "list:Gregorian calendar months/",
}

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES = {
    "multitrans",
    "multitrans-nowiki",
    "trans-top",
    "trans-top-also",
    "trans-bottom",
    "checktrans-top",
    "checktrans-bottom",
    "col1",
    "col2",
    "col3",
    "col4",
    "col5",
    "col1-u",
    "col2-u",
    "col3-u",
    "col4-u",
    "col5-u",
    "check deprecated lang param usage",
    "deprecated code",
    "ru-verb-alt-ё",
    "ru-noun-alt-ё",
    "ru-adj-alt-ё",
    "ru-proper noun-alt-ё",
    "ru-pos-alt-ё",
    "ru-alt-ё",
    # langhd is needed for pre-expanding language heading templates in the
    # Chinese Wiktionary dump file: https://zh.wiktionary.org/wiki/Template:-en-
    "langhd",
    "zh-der",  # col3 for Chinese
    "der3",  # redirects to col3
}


def append_page_data(
    page_data: List[Dict], field: str, value: Any, base_data: Dict
) -> bool:
    if page_data[-1].get(field) is not None:
        if len(page_data[-1]["senses"]) > 0:
            # append new dictionary if the last dictionary has sense data and
            # also has the same key
            page_data.append(copy.deepcopy(base_data))
        elif isinstance(page_data[-1].get(field), list):
            page_data[-1][field] += value
    else:
        page_data[-1][field] = value


def recursive_parse(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    node: Union[WikiNode, List[Union[WikiNode, str]]],
) -> None:
    if isinstance(node, list):
        for x in node:
            recursive_parse(wxr, page_data, base_data, x)
        return
    if not isinstance(node, WikiNode):
        return
    if node.kind in LEVEL_KINDS:
        subtitle = clean_node(wxr, None, node.args)
        subtitle = subtitle.rstrip(string.digits)
        wxr.wtp.start_subsection(subtitle)
        if subtitle in wxr.config.OTHER_SUBTITLES["ignored_sections"]:
            pass
        elif subtitle in wxr.config.POS_SUBTITLES:
            pos_type = wxr.config.POS_SUBTITLES[subtitle]["pos"]
            base_data["pos"] = pos_type
            append_page_data(page_data, "pos", pos_type, base_data)
            for index, node in enumerate(strip_nodes(node.children)):
                if isinstance(node, WikiNode):
                    if index == 0 and node.kind == NodeKind.TEMPLATE:
                        lang_code = base_data.get("lang_code")
                        extract_headword_line(wxr, page_data, node, lang_code)
                    elif node.kind == NodeKind.LIST:
                        extract_gloss(wxr, page_data, node.children, {})
                else:
                    recursive_parse(wxr, page_data, base_data, node)
        elif (
            wxr.config.capture_etymologies
            and subtitle in wxr.config.OTHER_SUBTITLES["etymology"]
        ):
            extract_etymology(wxr, page_data, base_data, node.children)
        elif (
            wxr.config.capture_pronunciation
            and subtitle in wxr.config.OTHER_SUBTITLES["pronunciation"]
        ):
            extract_pronunciation(wxr, page_data, base_data, node.children)
        elif (
            wxr.config.capture_linkages
            and subtitle in wxr.config.LINKAGE_SUBTITLES
        ):
            extract_linkages(
                wxr,
                page_data,
                node.children,
                wxr.config.LINKAGE_SUBTITLES[subtitle],
                None,
            )


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[Dict],
    nodes: List[Union[WikiNode, str]],
    gloss_data: Dict[str, List[str]],
) -> None:
    lang_code = page_data[-1].get("lang_code")
    for node in filter(
        lambda n: isinstance(n, WikiNode) and n.kind == NodeKind.LIST_ITEM,
        nodes,
    ):
        gloss_nodes = [
            child
            for child in node.children
            if not isinstance(child, WikiNode) or child.kind != NodeKind.LIST
        ]
        if lang_code == "ja":
            expanded_node = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(gloss_nodes), expand_all=True
            )
            ruby_data, nodes_without_ruby = extract_ruby(
                wxr, expanded_node.children
            )
            raw_gloss_text = clean_node(wxr, None, nodes_without_ruby)
        else:
            ruby_data = []
            raw_gloss_text = clean_node(wxr, None, gloss_nodes)
        new_gloss_data = merge_gloss_data(
            gloss_data, extract_gloss_and_tags(raw_gloss_text)
        )
        if len(ruby_data) > 0:
            new_gloss_data["ruby"] = ruby_data
        if contains_list(node.children):
            for child_node in filter_child_wikinodes(node, NodeKind.LIST):
                if child_node.args.endswith("#"):
                    # nested gloss
                    extract_gloss(
                        wxr,
                        page_data,
                        child_node.children,
                        new_gloss_data,
                    )
                else:
                    # example list
                    page_data[-1]["senses"].append(new_gloss_data)
                    extract_examples(
                        wxr,
                        page_data,
                        child_node,
                    )
        else:
            page_data[-1]["senses"].append(new_gloss_data)


def merge_gloss_data(
    data_a: Dict[str, List[str]], data_b: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    new_data = defaultdict(list)
    for data in data_a, data_b:
        for key, value in data.items():
            new_data[key].extend(value)
    return new_data


def extract_gloss_and_tags(raw_gloss: str) -> Dict[str, List[str]]:
    left_brackets = ("(", "（")
    right_brackets = (")", "）")
    if raw_gloss.startswith(left_brackets) or raw_gloss.endswith(
        right_brackets
    ):
        tags = []
        split_tag_regex = r", ?|，|或"
        front_tag_end = -1
        rear_tag_start = len(raw_gloss)
        for index, left_bracket in enumerate(left_brackets):
            if raw_gloss.startswith(left_bracket):
                front_tag_end = raw_gloss.find(right_brackets[index])
                front_label = raw_gloss[1:front_tag_end]
                tags += re.split(split_tag_regex, front_label)
        for index, right_bracket in enumerate(right_brackets):
            if raw_gloss.endswith(right_bracket):
                rear_tag_start = raw_gloss.rfind(left_brackets[index])
                rear_label = raw_gloss.rstrip("".join(right_brackets))[
                    rear_tag_start + 1 :
                ]
                tags += re.split(split_tag_regex, rear_label)

        gloss = raw_gloss[front_tag_end + 1 : rear_tag_start].strip()
        return {"glosses": [gloss], "raw_glosses": [raw_gloss], "tags": tags}
    else:
        return {"glosses": [raw_gloss]}


def extract_etymology(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    nodes: List[Union[WikiNode, str]],
) -> None:
    level_node_index = -1
    for index, node in enumerate(nodes):
        if isinstance(node, WikiNode) and node.kind in LEVEL_KINDS:
            level_node_index = index
            break
    if level_node_index != -1:
        etymology = clean_node(wxr, None, nodes[:index])
    else:
        etymology = clean_node(wxr, None, nodes)
    base_data["etymology_text"] = etymology
    append_page_data(page_data, "etymology_text", etymology, base_data)
    if level_node_index != -1:
        recursive_parse(wxr, page_data, base_data, nodes[level_node_index:])


def extract_pronunciation(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    nodes: List[Union[WikiNode, str]],
) -> None:
    lang_code = base_data.get("lang_code")
    for index, node in enumerate(nodes):
        if isinstance(node, WikiNode):
            if node.kind in LEVEL_KINDS:
                recursive_parse(wxr, page_data, base_data, nodes[index:])
                return
            elif node.kind == NodeKind.TEMPLATE:
                node = wxr.wtp.parse(
                    wxr.wtp.node_to_wikitext(node), expand_all=True
                )
        extract_pronunciation_recursively(
            wxr, page_data, base_data, lang_code, node, []
        )


def parse_page(
    wxr: WiktextractContext, page_title: str, page_text: str
) -> List[Dict[str, str]]:
    if wxr.config.verbose:
        logging.info(f"Parsing page: {page_title}")

    wxr.config.word = page_title
    wxr.wtp.start_page(page_title)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    tree = wxr.wtp.parse(
        page_text,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
    )

    page_data = []
    for node in filter(lambda n: isinstance(n, WikiNode), tree.children):
        # ignore link created by `also` template at the page top
        # also ignore "character info" templates
        if node.kind == NodeKind.TEMPLATE and node.args[0][0].lower() in {
            "also",
            "see also",
            "亦",
            "character info",
            "character info/new",
            "character info/var",
        }:
            continue
        if node.kind != NodeKind.LEVEL2:
            wxr.wtp.warning(
                f"Unexpected top-level node: {node}",
                sortid="extractor/zh/page/parse_page/503",
            )
            continue
        lang_name = clean_node(wxr, None, node.args)
        if lang_name not in wxr.config.LANGUAGES_BY_NAME:
            wxr.wtp.warning(
                f"Unrecognized language name at top-level {lang_name}",
                sortid="extractor/zh/page/parse_page/509",
            )
        lang_code = wxr.config.LANGUAGES_BY_NAME.get(lang_name)
        if (
            wxr.config.capture_language_codes
            and lang_code not in wxr.config.capture_language_codes
        ):
            continue
        wxr.wtp.start_section(lang_name)

        base_data = {
            "lang": lang_name,
            "lang_code": lang_code,
            "word": wxr.wtp.title,
            "senses": [],
        }
        page_data.append(copy.deepcopy(base_data))
        recursive_parse(wxr, page_data, base_data, node.children)

    return page_data

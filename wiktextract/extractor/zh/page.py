import copy
import logging
import re
from collections import defaultdict
from typing import Any, Dict, List, Union

from wikitextprocessor import NodeKind, WikiNode

from wiktextract.page import LEVEL_KINDS, clean_node
from wiktextract.wxr_context import WiktextractContext

from ..share import strip_nodes
from .gloss import extract_gloss
from .headword_line import extract_headword_line
from .inflection import extract_inflections
from .linkage import extract_linkages
from .pronunciation import extract_pronunciation_recursively
from .translation import extract_translation

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
) -> None:
    if page_data[-1].get(field) is not None:
        if len(page_data[-1]["senses"]) > 0:
            # append new dictionary if the last dictionary has sense data and
            # also has the same key
            page_data.append(copy.deepcopy(base_data))
        elif isinstance(page_data[-1].get(field), list):
            page_data[-1][field] += value
    else:
        page_data[-1][field] = value


def parse_section(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    node: Union[WikiNode, List[Union[WikiNode, str]]],
) -> None:
    if isinstance(node, list):
        for x in node:
            parse_section(wxr, page_data, base_data, x)
        return
    if not isinstance(node, WikiNode):
        return
    if node.kind in LEVEL_KINDS:
        subtitle = clean_node(wxr, None, node.args)
        # remove number suffix from subtitle
        subtitle = re.sub(r"\s*(?:（.+）|\d+)$", "", subtitle)
        wxr.wtp.start_subsection(subtitle)
        if subtitle in wxr.config.OTHER_SUBTITLES["ignored_sections"]:
            pass
        elif subtitle in wxr.config.POS_SUBTITLES:
            process_pos_block(wxr, page_data, base_data, node, subtitle)
        elif wxr.config.capture_etymologies and subtitle.startswith(
            tuple(wxr.config.OTHER_SUBTITLES["etymology"])
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
                "",
                page_data[-1],
            )
        elif (
            wxr.config.capture_translations
            and subtitle in wxr.config.OTHER_SUBTITLES["translations"]
        ):
            extract_translation(wxr, page_data, node)
        elif (
            wxr.config.capture_inflections
            and subtitle in wxr.config.OTHER_SUBTITLES["inflection_sections"]
        ):
            extract_inflections(wxr, page_data, node)
        else:
            wxr.wtp.debug(
                f"Unhandled subtitle: {subtitle}",
                sortid="extractor/zh/page/parse_section/192",
            )


def process_pos_block(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    node: WikiNode,
    pos_text: str,
):
    pos_type = wxr.config.POS_SUBTITLES[pos_text]["pos"]
    base_data["pos"] = pos_type
    append_page_data(page_data, "pos", pos_type, base_data)
    for index, child in enumerate(strip_nodes(node.children)):
        if isinstance(child, WikiNode):
            if index == 0 and child.kind == NodeKind.TEMPLATE:
                lang_code = base_data.get("lang_code")
                extract_headword_line(wxr, page_data, child, lang_code)
            elif child.kind == NodeKind.LIST:
                extract_gloss(wxr, page_data, child, defaultdict(list))
            elif child.kind in LEVEL_KINDS:
                parse_section(wxr, page_data, base_data, child)
        else:
            parse_section(wxr, page_data, base_data, child)


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
        parse_section(wxr, page_data, base_data, nodes[level_node_index:])


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
                parse_section(wxr, page_data, base_data, nodes[index:])
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

        base_data = defaultdict(
            list,
            {"lang": lang_name, "lang_code": lang_code, "word": wxr.wtp.title},
        )
        page_data.append(copy.deepcopy(base_data))
        parse_section(wxr, page_data, base_data, node.children)

    return page_data

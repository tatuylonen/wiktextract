import copy
import logging
import re
import string

from typing import Dict, List, Union, Any

from wikitextprocessor import WikiNode, NodeKind
from wiktextract.wxr_context import WiktextractContext
from wiktextract.page import clean_node, LEVEL_KINDS
from wiktextract.extractor.share import contains_list, WIKIMEDIA_COMMONS_URL


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
    "RQ:",
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
        if subtitle in wxr.config.OTHER_SUBTITLES["ignored_sections"]:
            pass
        elif subtitle in wxr.config.POS_SUBTITLES:
            pos_type = wxr.config.POS_SUBTITLES[subtitle]["pos"]
            base_data["pos"] = pos_type
            append_page_data(page_data, "pos", pos_type, base_data)
            for node in node.children:
                if isinstance(node, WikiNode) and node.kind == NodeKind.LIST:
                    extract_gloss(wxr, page_data, node.children)
                else:
                    recursive_parse(wxr, page_data, base_data, node)
        elif subtitle in wxr.config.OTHER_SUBTITLES["etymology"]:
            extract_etymology(wxr, page_data, base_data, node.children)
        elif subtitle in wxr.config.OTHER_SUBTITLES["pronunciation"]:
            extract_pronunciation(wxr, page_data, base_data, node.children)


def extract_gloss(
    wxr: WiktextractContext,
    page_data: List[Dict],
    nodes: List[Union[WikiNode, str]],
) -> None:
    for node in filter(
        lambda n: isinstance(n, WikiNode) and n.kind == NodeKind.LIST_ITEM,
        nodes,
    ):
        gloss = clean_node(
            wxr,
            None,
            [
                child
                for child in node.children
                if not isinstance(child, WikiNode)
                or child.kind != NodeKind.LIST
            ],
        )
        extract_sense_tags(wxr, page_data, gloss)


def extract_sense_tags(
    wxr: WiktextractContext, page_data: List[Dict], raw_gloss: str
) -> None:
    if raw_gloss.startswith("("):
        label_end = raw_gloss.find(")")
        label = raw_gloss[1:label_end]
        gloss = raw_gloss[label_end + 2 :]  # also remove space after ")"
        # labels: https://zh.wiktionary.org/wiki/Module:Labels/data
        tags = re.split(r",|或", label)
        page_data[-1]["senses"].append(
            {"glosses": [gloss], "raw_glosses": [raw_gloss], "tags": tags}
        )
    else:
        page_data[-1]["senses"].append({"glosses": [raw_gloss]})


def extract_etymology(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    nodes: List[Union[WikiNode, str]],
) -> None:
    for index, node in enumerate(nodes):
        if isinstance(node, WikiNode) and node.kind == NodeKind.TEMPLATE:
            etymology = clean_node(
                wxr,
                None,
                [
                    child
                    for child in node.children
                    if not isinstance(child, WikiNode)
                    or (
                        child.kind != NodeKind.LIST
                        and child.kind not in LEVEL_KINDS
                    )
                ],
            )
            base_data["etymology_text"] = etymology
            append_page_data(page_data, "etymology_text", etymology, base_data)
            recursive_parse(wxr, page_data, base_data, nodes[index + 1 :])
            return


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
                    wxr.wtp.expand(wxr.wtp.node_to_wikitext(node))
                )
        extract_pronunciation_recursively(
            wxr, page_data, base_data, lang_code, node, []
        )


def extract_pronunciation_recursively(
    wxr: WiktextractContext,
    page_data: List[Dict],
    base_data: Dict,
    lang_code: str,
    node: Union[WikiNode, List[Union[WikiNode, str]]],
    tags: List[str],
) -> None:
    if isinstance(node, list):
        for x in node:
            extract_pronunciation_recursively(
                wxr, page_data, base_data, lang_code, x, tags
            )
        return
    if not isinstance(node, WikiNode):
        return
    if node.kind == NodeKind.LIST_ITEM:
        if not contains_list(node):
            data = extract_pronunciation_item(wxr, lang_code, node, tags)
            if isinstance(data, str):
                for index in range(len(page_data[-1].get("sounds", []))):
                    page_data[-1]["sounds"][index].update(
                        {
                            "audio": data.removeprefix("File:"),
                            "ogg_file": WIKIMEDIA_COMMONS_URL + data,
                        }
                    )
            else:
                append_page_data(
                    page_data,
                    "sounds",
                    [data],
                    base_data,
                )
        else:
            new_tags = clean_node(
                wxr,
                None,
                [
                    child
                    for child in node.children
                    if not isinstance(child, WikiNode)
                    or child.kind != NodeKind.LIST
                ],
            )
            new_tags = split_pronunciation_tags(new_tags)
            extract_pronunciation_recursively(
                wxr,
                page_data,
                base_data,
                lang_code,
                node.children,
                list(set(tags + new_tags)),
            )
    else:
        extract_pronunciation_recursively(
            wxr, page_data, base_data, lang_code, node.children, tags
        )


def split_pronunciation_tags(text: str) -> List[str]:
    return list(
        filter(
            None,
            re.split(
                r"，|, | \(|和|包括|: ",
                text.removesuffix(" ^((幫助))")  # remove help link
                # remove link to page "Wiktionary:漢語發音表記"
                .removesuffix(" (維基詞典)")
                # remove Dungan language pronunciation warning from "Module:Zh-pron"
                .removesuffix("(注意：東干語發音目前仍處於實驗階段，可能會不準確。)")
                .strip("()⁺\n "),
            ),
        )
    )


def extract_pronunciation_item(
    wxr: WiktextractContext, lang_code: str, node: WikiNode, tags: List[str]
) -> Union[Dict, str]:
    expanded_text = clean_node(wxr, None, node.children)
    # breakpoint()
    if expanded_text.startswith("File:"):
        return expanded_text
    else:
        sound_tags, ipa = re.split("：|:", expanded_text, 1)
        data = {"tags": list(set(tags + split_pronunciation_tags(sound_tags)))}
        ipa_key = "zh-pron" if lang_code == "zh" else "ipa"
        data[ipa_key] = ipa.strip()
        return data


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
    for node in filter(
        # ignore link created by `also` template at the page top
        lambda n: isinstance(n, WikiNode) and n.kind != NodeKind.LINK,
        tree.children,
    ):
        if node.kind != NodeKind.LEVEL2:
            logging.warning(f"Unexpected top-level node: {node}")
            continue
        lang_name = clean_node(wxr, None, node.args)
        if lang_name not in wxr.config.LANGUAGES_BY_NAME:
            logging.warning(
                f"Unrecognized language name at top-level {lang_name}"
            )
            continue
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

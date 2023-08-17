import logging
import re
import time
from typing import List, Optional, Union

from wikitextprocessor import NodeKind, Page, WikiNode

from ...page import clean_node
from ...wxr_context import WiktextractContext
from ..share import capture_text_in_parentheses, split_chinese_variants

SENSE_SUBTITLE_PREFIX = "詞義："
IGNORED_LEVEL3_SUBTITLES = {
    "參見",  # see also
    "参见",
    "延伸閱讀",  # further reading
    "延伸阅读",
}


def parse_ja_thesaurus_term(
    wxr: WiktextractContext,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    term_str: str,
) -> List["ThesaurusTerm"]:
    from wiktextract.thesaurus import ThesaurusTerm

    tags = None
    roman = None
    if term_str.startswith("("):  # has qualifier
        qual_bracket_idx = term_str.find(")")
        tags = "|".join(term_str[1:qual_bracket_idx].split(", "))
        term_str = term_str[qual_bracket_idx + 2 :]

    thesaurus = []
    for term_str in term_str.split("、"):
        # Example term_str from https://zh.wiktionary.org/wiki/Thesaurus:死ぬ
        # Fromat: (qualifer) term (roman, gloss)
        # 'この世(よ)を去(さ)る (kono yo o saru, 字面意思為“to leave this world”)'
        # '若死(わかじ)にする (wakajini suru, “还年轻时死去”)'
        term_end = term_str.find(" (")
        term = term_str[:term_end]
        roman_and_gloss = term_str[term_end + 2 :].removesuffix(")").split(", ")
        if roman_and_gloss:
            roman = roman_and_gloss[0]
        thesaurus.append(
            ThesaurusTerm(
                entry=entry,
                language_code=lang_code,
                pos=pos,
                linkage=linkage,
                term=term,
                tags=tags,
                roman=roman,
                sense=sense,
            )
        )
    return thesaurus


def parse_zh_thesaurus_term(
    wxr: WiktextractContext,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    term_str: str,
) -> List["ThesaurusTerm"]:
    from wiktextract.thesaurus import ThesaurusTerm

    # Example term_str from https://zh.wiktionary.org/wiki/Thesaurus:安置
    # Fromat: traditional／simplified (pinyin) (tags)
    # 施設／施设 (shīshè) (書面)
    # 擺佈／摆布 (bǎibù, bǎibu)
    # 著落／着落 (書面)
    # 措置
    tags = []
    roman = None
    raw_tags, term = capture_text_in_parentheses(term_str)
    for tag in raw_tags:
        if re.search(r"[a-z]", tag):
            roman = tag  # pinyin
        else:
            tags.append(tag)

    return [
        ThesaurusTerm(
            entry=entry,
            language_code=lang_code,
            pos=pos,
            linkage=linkage,
            term=variant_term,
            tags="|".join(tags) if len(tags) > 0 else None,
            roman=roman,
            sense=sense,
            language_variant=variant_type,
        )
        for variant_type, variant_term in split_chinese_variants(term)
    ]


def parse_thesaurus_term(
    wxr: WiktextractContext,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    node: WikiNode,
) -> List["ThesaurusTerm"]:
    from wiktextract.thesaurus import ThesaurusTerm

    node_str = clean_node(wxr, None, node)
    node_str = node_str.removeprefix("* ")  # remove list wikitext

    if lang_code == "ja":
        return parse_ja_thesaurus_term(
            wxr, entry, lang_code, pos, sense, linkage, node_str
        )
    elif lang_code == "zh":
        return parse_zh_thesaurus_term(
            wxr, entry, lang_code, pos, sense, linkage, node_str
        )
    else:
        return [
            ThesaurusTerm(
                entry=entry,
                language_code=lang_code,
                pos=pos,
                linkage=linkage,
                term=node_str,
                sense=sense,
            )
        ]


def recursive_parse(
    wxr: WiktextractContext,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    node: Union[WikiNode, List[Union[WikiNode, str]]],
) -> Optional[List["ThesaurusTerm"]]:
    if isinstance(node, list):
        thesaurus = []
        for x in node:
            x_result = recursive_parse(
                wxr, entry, lang_code, pos, sense, linkage, x
            )
            if x_result is not None:
                thesaurus.extend(x_result)
        return thesaurus
    if not isinstance(node, WikiNode):
        return

    if node.kind == NodeKind.LEVEL2:
        lang_name = clean_node(wxr, None, node.largs)
        lang_code = wxr.config.LANGUAGES_BY_NAME.get(lang_name)
        if lang_code is None:
            logging.warning(
                f"Unrecognized language: {lang_name} in page Thesaurus:{entry}"
            )
        return recursive_parse(
            wxr, entry, lang_code, None, None, None, node.children
        )
    elif node.kind == NodeKind.LEVEL3:
        local_pos_name = clean_node(wxr, None, node.largs)
        if local_pos_name in IGNORED_LEVEL3_SUBTITLES:
            return None
        english_pos = wxr.config.POS_SUBTITLES.get(local_pos_name, {}).get(
            "pos"
        )
        if english_pos is None:
            logging.warning(
                f"Unrecognized POS subtitle: {local_pos_name} in page "
                f"Thesaurus:{entry}"
            )
            english_pos = local_pos_name
        return recursive_parse(
            wxr, entry, lang_code, english_pos, None, None, node.children
        )
    elif node.kind == NodeKind.LEVEL4:
        sense = clean_node(wxr, None, node.largs)
        sense = sense.removeprefix(SENSE_SUBTITLE_PREFIX)
        return recursive_parse(
            wxr, entry, lang_code, pos, sense, None, node.children
        )
    elif node.kind == NodeKind.LEVEL5:
        local_linkage_name = clean_node(wxr, None, node.largs)
        english_linkage = wxr.config.LINKAGE_SUBTITLES.get(local_linkage_name)
        if english_linkage is None:
            logging.warning(
                f"Unrecognized linkage subtitle: {local_linkage_name} in page "
                f"Thesaurus:{entry}"
            )
            english_linkage = local_linkage_name
        return recursive_parse(
            wxr, entry, lang_code, pos, sense, english_linkage, node.children
        )
    elif node.kind == NodeKind.LIST:
        thesaurus = []
        for list_item_node in filter(
            lambda x: isinstance(x, WikiNode) and x.kind == NodeKind.LIST_ITEM,
            node.children,
        ):
            thesaurus.extend(
                parse_thesaurus_term(
                    wxr, entry, lang_code, pos, sense, linkage, list_item_node
                )
            )
        return thesaurus
    elif node.children:
        return recursive_parse(
            wxr, entry, lang_code, pos, sense, linkage, node.children
        )
    return None


def extract_thesaurus_data(wxr: WiktextractContext) -> None:
    from wiktextract.thesaurus import (
        ThesaurusTerm,
        insert_thesaurus_terms,
        thesaurus_linkage_number,
    )

    start_t = time.time()
    logging.info("Extracting thesaurus data")
    thesaurus_ns_data = wxr.wtp.NAMESPACE_DATA.get("Thesaurus", {})
    thesaurus_ns_id = thesaurus_ns_data.get("id")

    def page_handler(page: Page) -> Optional[List[ThesaurusTerm]]:
        entry = page.title[page.title.find(":") + 1 :]
        wxr.wtp.start_page(page.title)
        root = wxr.wtp.parse(page.body, additional_expand={"ws", "zh-syn-list"})
        return recursive_parse(
            wxr, entry, None, None, None, None, root.children
        )

    for thesaurus_terms in wxr.wtp.reprocess(
        page_handler, include_redirects=False, namespace_ids=[thesaurus_ns_id]
    ):
        insert_thesaurus_terms(wxr.thesaurus_db_conn, thesaurus_terms)

    wxr.thesaurus_db_conn.commit()
    num_pages = wxr.wtp.saved_page_nums([thesaurus_ns_id], False)
    total = thesaurus_linkage_number(wxr.thesaurus_db_conn)
    logging.info(
        "Extracted {} linkages from {} thesaurus pages (took {:.1f}s)".format(
            total, num_pages, time.time() - start_t
        )
    )

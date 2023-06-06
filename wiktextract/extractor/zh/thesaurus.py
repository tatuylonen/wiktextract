import logging
import re
import time

from typing import Union, List, Optional

from wiktextract.wxr_context import WiktextractContext
from wiktextract.page import clean_node
from wikitextprocessor import NodeKind, WikiNode, Page


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
) -> None:
    from wiktextract.thesaurus import insert_thesaurus_entry_and_term

    tags = None
    roman = None
    if term_str.startswith("("):  # has qualifier
        qual_bracket_idx = term_str.find(")")
        tags = "|".join(term_str[1:qual_bracket_idx].split(", "))
        term_str = term_str[qual_bracket_idx + 2 :]

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
        insert_thesaurus_entry_and_term(
            wxr.thesaurus_db_conn,
            entry,
            lang_code,
            pos,
            sense,
            linkage,
            term,
            tags,
            None,
            roman,
            None,
        )


def parse_zh_thesaurus_term(
    wxr: WiktextractContext,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    term_str: str,
) -> None:
    from wiktextract.thesaurus import insert_thesaurus_entry_and_term

    # Example term_str from https://zh.wiktionary.org/wiki/Thesaurus:安置
    # Fromat: traditional／simplified (pinyin) (tags)
    # 施設／施设 (shīshè) (書面)
    # 擺佈／摆布 (bǎibù, bǎibu)
    # 著落／着落 (書面)
    # 措置
    tags = None
    roman = None
    term = term_str
    if " (" in term_str:
        roman_or_tags_start = term_str.find(" (")
        term = term_str[:roman_or_tags_start]
        roman_and_tags = term_str[roman_or_tags_start + 2 :].removesuffix(")")
        if ") (" in roman_and_tags:
            roman, tag_str = roman_and_tags.split(") (", 1)
            tags = tag_str
        else:
            if re.search(r"[a-z]", roman_and_tags):
                roman = roman_and_tags  # pinyin
            else:
                tags = roman_and_tags
        if roman is not None:
            roman = "|".join(roman.split(", "))

    for index, split_term in enumerate(term.split("／")):
        language_variant = "zh-Hant" if index == 0 else "zh-Hans"
        insert_thesaurus_entry_and_term(
            wxr.thesaurus_db_conn,
            entry,
            lang_code,
            pos,
            sense,
            linkage,
            split_term,
            tags,
            None,
            roman,
            language_variant,
        )


def parse_thesaurus_term(
    wxr: WiktextractContext,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    node: WikiNode,
) -> None:
    from wiktextract.thesaurus import insert_thesaurus_entry_and_term

    node_str = clean_node(wxr, None, node)
    node_str = node_str.removeprefix("* ")  # remove list wikitext

    if lang_code == "ja":
        parse_ja_thesaurus_term(
            wxr, entry, lang_code, pos, sense, linkage, node_str
        )
    elif lang_code == "zh":
        parse_zh_thesaurus_term(
            wxr, entry, lang_code, pos, sense, linkage, node_str
        )
    else:
        insert_thesaurus_entry_and_term(
            wxr.thesaurus_db_conn,
            entry,
            lang_code,
            pos,
            sense,
            linkage,
            node_str,
            None,
            None,
            None,
            None,
        )


def recursive_parse(
    wxr: WiktextractContext,
    entry: str,
    lang_code: Optional[str],
    pos: Optional[str],
    sense: Optional[str],
    linkage: Optional[str],
    node: Union[WikiNode, List[Union[WikiNode, str]]],
) -> None:
    if isinstance(node, list):
        for x in node:
            recursive_parse(wxr, entry, lang_code, pos, sense, linkage, x)
        return
    if not isinstance(node, WikiNode):
        return

    if node.kind == NodeKind.LEVEL2:
        lang_name = clean_node(wxr, None, node.args)
        lang_code = wxr.config.LANGUAGES_BY_NAME.get(lang_name)
        recursive_parse(wxr, entry, lang_code, None, None, None, node.children)
    elif node.kind == NodeKind.LEVEL3:
        local_pos_name = clean_node(wxr, None, node.args)
        if local_pos_name in IGNORED_LEVEL3_SUBTITLES:
            return
        english_pos = wxr.config.POS_SUBTITLES.get(local_pos_name, {}).get(
            "pos"
        )
        if english_pos is None:
            logging.warning(
                f"Unrecognized POS subtitle: {local_pos_name} in page "
                f"Thesaurus:{entry}"
            )
            english_pos = local_pos_name
        recursive_parse(
            wxr, entry, lang_code, english_pos, None, None, node.children
        )
    elif node.kind == NodeKind.LEVEL4:
        sense = clean_node(wxr, None, node.args)
        sense = sense.removeprefix(SENSE_SUBTITLE_PREFIX)
        recursive_parse(wxr, entry, lang_code, pos, sense, None, node.children)
    elif node.kind == NodeKind.LEVEL5:
        local_linkage_name = clean_node(wxr, None, node.args)
        english_linkage = wxr.config.LINKAGE_SUBTITLES.get(local_linkage_name)
        if english_linkage is None:
            logging.warning(
                f"Unrecognized linkage subtitle: {local_linkage_name} in page "
                f"Thesaurus:{entry}"
            )
            english_linkage = local_linkage_name
        recursive_parse(
            wxr, entry, lang_code, pos, sense, english_linkage, node.children
        )
    elif node.kind == NodeKind.LIST:
        for list_item_node in filter(
            lambda x: isinstance(x, WikiNode) and x.kind == NodeKind.LIST_ITEM,
            node.children,
        ):
            parse_thesaurus_term(
                wxr, entry, lang_code, pos, sense, linkage, list_item_node
            )
    elif node.children:
        recursive_parse(
            wxr, entry, lang_code, pos, sense, linkage, node.children
        )


def extract_thesaurus_data(wxr: WiktextractContext) -> None:
    from wiktextract.thesaurus import thesaurus_linkage_number

    start_t = time.time()
    logging.info("Extracting thesaurus data")
    thesaurus_ns_data = wxr.wtp.NAMESPACE_DATA.get("Thesaurus", {})
    thesaurus_ns_id = thesaurus_ns_data.get("id")

    def page_handler(page: Page) -> None:
        entry = page.title[page.title.find(":") + 1 :]
        wxr.wtp.start_page(page.title)
        root = wxr.wtp.parse(page.body, additional_expand={"ws", "zh-syn-list"})
        recursive_parse(wxr, entry, None, None, None, None, root.children)

    for _ in wxr.wtp.reprocess(
        page_handler, include_redirects=False, namespace_ids=[thesaurus_ns_id]
    ):
        pass

    num_pages = wxr.wtp.saved_page_nums([thesaurus_ns_id], False)
    total = thesaurus_linkage_number(wxr.thesaurus_db_conn)
    logging.info(
        "Extracted {} linkages from {} thesaurus pages (took {:.1f}s)".format(
            total, num_pages, time.time() - start_t
        )
    )

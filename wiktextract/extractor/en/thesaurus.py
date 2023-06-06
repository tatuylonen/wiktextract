# Extracting information from thesaurus pages in Wiktionary.  The data will be
# merged into word linkages in later stages.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import time
import logging

from wiktextract.wxr_context import WiktextractContext
from wiktextract.datautils import ns_title_prefix_tuple
from wiktextract.page import clean_node, LEVEL_KINDS
from wiktextract.form_descriptions import parse_sense_qualifier
from wikitextprocessor import NodeKind, WikiNode, Page


IGNORED_SUBTITLE_TAGS_MAP = {
    "by reason": [],
    "by period of time": [],
    "by degree": [],
    "by type": [],
    "other": [],
    "opaque slang terms": ["slang"],
    "slang": ["slang"],
    "colloquial, archaic, slang": ["colloquial", "archaic", "slang"],
    "euphemisms": ["euphemism"],
    "colloquialisms": ["colloquial"],
    "colloquialisms or slang": ["colloquial"],
    "technical terms misused": ["colloquial"],
    "people": [],
    "proper names": ["proper-noun"],
    "race-based (warning- offensive)": ["offensive"],
    "substance addicts": [],
    "non-substance addicts": [],
    "echoing sounds": [],
    "movement sounds": [],
    "impacting sounds": [],
    "destructive sounds": [],
    "noisy sounds": [],
    "vocal sounds": [],
    "miscellaneous sounds": [],
    "age and gender": [],
    "breeds and types": [],
    "by function": [],
    "wild horses": [],
    "body parts": [],
    "colors, patterns and markings": [],
    "diseases": [],
    "equipment and gear": [],
    "groups": [],
    "horse-drawn vehicles": [],
    "places": [],
    "sports": [],
    "sounds and behavior": [],
    "obscure derivations": [],
    "plants": [],
    "animals": [],
    "common": [],
    "rare": ["rare"],
}


def contains_list(contents):
    """Returns True if there is a list somewhere nested in contents."""
    if isinstance(contents, (list, tuple)):
        return any(contains_list(x) for x in contents)
    if not isinstance(contents, WikiNode):
        return False
    kind = contents.kind
    if kind == NodeKind.LIST:
        return True
    return contains_list(contents.children) or contains_list(contents.args)


def extract_thesaurus_data(wxr: WiktextractContext) -> None:
    """Extracts linkages from the thesaurus pages in Wiktionary."""
    from wiktextract.thesaurus import (
        insert_thesaurus_entry_and_term,
        thesaurus_linkage_number
    )

    start_t = time.time()
    logging.info("Extracting thesaurus data")
    thesaurus_ns_data = wxr.wtp.NAMESPACE_DATA.get("Thesaurus", {})
    thesaurus_ns_id = thesaurus_ns_data.get("id")
    thesaurus_ns_local_name = thesaurus_ns_data.get("name")

    def page_handler(page: Page):
        title = page.title
        text = page.body
        if title.startswith("Thesaurus:Requested entries "):
            return None
        if "/" in title:
            #print("STRANGE TITLE:", title)
            return None
        word = title[len(thesaurus_ns_local_name) + 1:]
        idx = word.find(":")
        if idx > 0 and idx < 5:
            word = word[idx + 1:]  # Remove language prefix
        expanded = wxr.wtp.expand(text, templates_to_expand=None)  # Expand all
        expanded = re.sub(r'(?s)<span class="tr Latn"[^>]*>(<b>)?(.*?)(</b>)?'
                          r'</span>',
                          r"XLITS\2XLITE", expanded)
        tree = wxr.wtp.parse(expanded, pre_expand=False)
        assert tree.kind == NodeKind.ROOT
        lang = None
        pos = None
        sense = None
        linkage = None
        subtitle_tags = ()
        entry_id = -1
        # Some pages don't have a language subtitle, but use
        # {{ws header|lang=xx}}
        m = re.search(r'(?s)\{\{ws header\|[^}]*lang=([^}|]*)', text)
        if m:
            lang = wxr.config.LANGUAGES_BY_CODE.get(m.group(1), [None])[0]

        def recurse(contents):
            nonlocal lang
            nonlocal pos
            nonlocal sense
            nonlocal linkage
            nonlocal subtitle_tags
            nonlocal entry_id
            item_sense = None
            tags = None
            topics = None

            if isinstance(contents, (list, tuple)):
                for x in contents:
                    recurse(x)
                return
            if not isinstance(contents, WikiNode):
                return
            kind = contents.kind
            if kind == NodeKind.LIST and not contains_list(contents.children):
                if lang is None:
                    logging.debug(
                        f"{title=} {lang=} UNEXPECTED LIST WITHOUT LANG: " +
                        str(contents)
                    )
                    return
                for node in contents.children:
                    if node.kind != NodeKind.LIST_ITEM:
                        continue
                    w = clean_node(wxr, None, node.children)
                    if "*" in w:
                        logging.debug(
                            f"{title=} {lang=} {pos=} STAR IN WORD: {w}"
                        )
                    # Check for parenthesized sense at the beginning
                    m = re.match(r"(?s)^\(([^)]*)\):\s*(.*)$", w)
                    if m:
                        item_sense, w = m.groups()
                        # XXX check for item_sense being part-of-speech
                    else:
                        item_sense = sense

                    # Remove thesaurus links, if any
                    w = re.sub(r"\s*\[W[Ss]\]", "", w)

                    # Check for English translation in quotes.  This can be
                    # literal translation, not necessarily the real meaning.
                    english = None

                    def engl_fn(m):
                        nonlocal english
                        english = m.group(1)
                        return ""

                    w = re.sub(r'(\bliterally\s*)?(, )?“([^"]*)"\s*',
                               engl_fn, w)

                    # Check for qualifiers in parentheses
                    tags = []
                    topics = []

                    def qual_fn(m):
                        q = m.group(1)
                        if q == item_sense:
                            return ""
                        if "XLITS" in q:
                            return q
                        dt = {}
                        parse_sense_qualifier(wxr, q, dt)
                        tags.extend(dt.get("tags", ()))
                        topics.extend(dt.get("topics", ()))
                        return ""

                    w = re.sub(r"\(([^)]*)\)$", qual_fn, w).strip()

                    # XXX there could be a transliteration, e.g.
                    # Thesaurus:老百姓

                    # XXX Apparently there can also be alternative spellings,
                    # such as 眾人／众人 on Thesaurus:老百姓

                    # If the word is now empty or separator, skip
                    if not w or w.startswith("---") or w == "\u2014":
                        return
                    rel = linkage or "synonyms"
                    for w1 in w.split(","):
                        m = re.match(r"(?s)(.*?)\s*XLITS(.*?)XLITE\s*", w1)
                        if m:
                            w1, xlit = m.groups()
                        else:
                            xlit = None
                        w1 = w1.strip()
                        if w1.startswith(
                                ns_title_prefix_tuple(wxr, "Thesaurus")
                        ):
                            w1 = w1[10:]
                        if w1:
                            lang_code = wxr.config.LANGUAGES_BY_NAME.get(lang)
                            if lang_code is None:
                                logging.debug(
                                    f"Linkage language {lang} not recognized"
                                )
                            insert_thesaurus_entry_and_term(
                                wxr.thesaurus_db_conn,
                                word,
                                lang_code,
                                pos,
                                item_sense,
                                rel,
                                w1,
                                "|".join(tags) if tags else None,
                                "|".join(topics) if topics else None,
                                xlit,
                                None
                            )
                return
            if kind not in LEVEL_KINDS:
                recurse(contents.args)
                recurse(contents.children)
                return
            subtitle = wxr.wtp.node_to_text(contents.args)
            if subtitle in wxr.config.LANGUAGES_BY_NAME:
                lang = subtitle
                pos = None
                sense = None
                linkage = None
                recurse(contents.children)
                return
            if subtitle.lower().startswith(
                    wxr.config.OTHER_SUBTITLES["sense"].lower()
            ):
                sense = subtitle[len(wxr.config.OTHER_SUBTITLES["sense"]):]
                linkage = None
                recurse(contents.children)
                return
            subtitle = subtitle.lower()
            if subtitle in ("further reading", "external links",
                            "references", "translations", "notes", "usage",
                            "work to be done", "quantification",
                            "abbreviation", "symbol"):
                return
            if subtitle in wxr.config.LINKAGE_SUBTITLES:
                linkage = wxr.config.LINKAGE_SUBTITLES[subtitle]
                recurse(contents.children)
                return
            if subtitle in wxr.config.POS_SUBTITLES:
                pos = wxr.config.POS_SUBTITLES[subtitle]["pos"]
                sense = None
                linkage = None
                recurse(contents.children)
                return
            if subtitle in IGNORED_SUBTITLE_TAGS_MAP:
                # These subtitles are ignored but children are processed and
                # possibly given additional tags
                subtitle_tags = IGNORED_SUBTITLE_TAGS_MAP[subtitle]
                recurse(contents.children)
                subtitle_tags = ()
                return
            logging.debug(
                f"{title=} {lang=} {pos=} {sense=} UNHANDLED SUBTITLE: " +
                "subtitle " + str(contents.args)
            )
            recurse(contents.children)
            return None

        recurse(tree)

    for _ in wxr.wtp.reprocess(
            page_handler,
            include_redirects=False,
            namespace_ids=[thesaurus_ns_id]
    ):
        pass

    num_pages = wxr.wtp.saved_page_nums([thesaurus_ns_id], False)
    total = thesaurus_linkage_number(wxr.thesaurus_db_conn)
    logging.info("Extracted {} linkages from {} thesaurus pages (took {:.1f}s)"
                 .format(total, num_pages, time.time() - start_t))

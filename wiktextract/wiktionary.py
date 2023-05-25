# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import io
import logging
import re
import time
import tarfile
import collections

from pathlib import Path
from typing import Optional, List, Set, Tuple

from wikitextprocessor import Page
from .page import (parse_page, additional_expand_templates)
from .config import WiktionaryConfig
from .wxr_context import WiktextractContext
from .thesaurus import extract_thesaurus_data
from .datautils import data_append


def page_handler(wxr, page: Page, config_kwargs, thesaurus_data, dont_parse):
    # Make sure there are no newlines or other strange characters in the
    # title.  They could cause security problems at several post-processing
    # steps.
    title = re.sub(r"[\s\000-\037]+", " ", page.title)
    title = title.strip()
    if dont_parse:
        return None
    if page.redirect_to is not None:
        wxr1 = WiktextractContext(wxr.wtp, WiktionaryConfig())
        ret = [{"title": title, "redirect": page.redirect_to}]
    else:
        if page.model != "wikitext":
            return None
        if title.endswith("/translations"):
            return None

        # XXX Sign gloss pages?
        wxr1 = WiktextractContext(wxr.wtp, WiktionaryConfig(**config_kwargs))
        wxr1.config.thesaurus_data = thesaurus_data
        start_t = time.time()
        ret = parse_page(wxr1, title, page.body)
        dur = time.time() - start_t
        if dur > 100:
            logging.warning("====== WARNING: PARSING PAGE TOOK {:.1f}s: {}"
                            .format(dur, title))
    stats = wxr1.config.to_return()
    for k, v in wxr.wtp.to_return().items():
        stats[k] = v
    return ret, stats


def parse_wiktionary(
        wxr: WiktextractContext, path: str, word_cb,
        phase1_only: bool, dont_parse: bool, namespace_ids: Set[int],
        override_folders: Optional[List[str]] = None,
        skip_extract_dump: bool = False,
        save_pages_path: Optional[str] = None):
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls `word_cb(data)` for all words defined for languages in `languages`."""
    assert callable(word_cb)
    capture_language_codes = wxr.config.capture_language_codes
    if capture_language_codes is not None:
        assert isinstance(capture_language_codes, (list, tuple, set))
        for x in capture_language_codes:
            assert isinstance(x, str)

    # langhd is needed for pre-expanding language heading templates in the
    # Chinese Wiktionary dump file: https://zh.wiktionary.org/wiki/Template:-en-
    # Move this to lang_specific
    if wxr.wtp.lang_code == "zh":
        additional_expand_templates.add("langhd")

    logging.info("First phase - extracting templates, macros, and pages")
    if override_folders is not None:
        override_folders = [Path(folder) for folder in override_folders]
    if save_pages_path is not None:
        save_pages_path = Path(save_pages_path)
    list(wxr.wtp.process(path, None, namespace_ids, True, override_folders,
                     skip_extract_dump, save_pages_path))
    if phase1_only:
        wxr.wtp.close_db_conn()
        return []

    # Phase 2 - process the pages using the user-supplied callback
    logging.info("Second phase - processing pages")
    return reprocess_wiktionary(wxr, word_cb, dont_parse)


def reprocess_wiktionary(wxr: WiktextractContext, word_cb, dont_parse):
    """Reprocesses the Wiktionary from the cache file."""
    assert callable(word_cb)
    assert dont_parse in (True, False)

    config_kwargs = wxr.config.to_kwargs()

    # Extract thesaurus data. This iterates over thesaurus pages,
    # but is very fast.
    thesaurus_data = extract_thesaurus_data(wxr)

    # Then perform the main parsing pass.
    def page_cb(page: Page):
        return page_handler(
            wxr, page, config_kwargs, thesaurus_data, dont_parse)

    emitted = set()
    process_ns_ids = list({
        wxr.wtp.NAMESPACE_DATA.get(ns, {}).get("id", 0)
        for ns in ["Main", "Reconstruction"]
    })
    for ret, stats in wxr.wtp.reprocess(page_cb, namespace_ids=process_ns_ids):
        wxr.config.merge_return(stats)
        for dt in ret:
            word_cb(dt)
            word = dt.get("word")
            lang = dt.get("lang")
            pos = dt.get("pos")
            if word and lang and pos:
                emitted.add((word, lang, pos))

    # Emit words that occur in thesaurus as main words but for which
    # Wiktionary has no word in the main namespace. This seems to happen
    # sometimes.
    logging.info("Emitting words that only occur in thesaurus")
    for (word, lang), linkages in thesaurus_data.items():
        pos_ht = collections.defaultdict(list)
        for x in linkages:
            if x[0] is not None:
                pos_ht[x[0]].append(x)
        for pos, linkages in pos_ht.items():
            if (word, lang, pos) in emitted:
                continue
            if lang not in wxr.config.LANGUAGES_BY_NAME:
                print("Linkage language {} not recognized".format(lang))
                continue
            lang_code = wxr.config.LANGUAGES_BY_NAME[lang]
            logging.info(
                "Emitting thesaurus main entry for {}/{}/{} (not in main)"
                .format(word, lang, pos))
            sense_ht = collections.defaultdict(list)
            for tpos, rel, w, sense, xlit, tags, topics, source in linkages:
                if not sense:
                    continue
                sense_ht[sense].append((rel, w, xlit, tags, topics, source))
            senses = []
            for sense, linkages in sense_ht.items():
                sense_dt = {
                    "glosses": [sense],
                }
                for rel, w, xlit, tags, topics, source in linkages:
                    dt = {"word": w, "source": source}
                    if tags:
                        dt["tags"] = tags
                    if topics:
                        dt["topics"] = topics
                    data_append(wxr, sense_dt, rel, dt)
                senses.append(sense_dt)
            if not senses:
                senses.append({"tags": ["no-gloss"]})
            data = {
                "word": word,
                "lang": lang,
                "lang_code": lang_code,
                "pos": pos,
                "senses": senses,
                "source": "thesaurus",
            }
            word_cb(data)

    logging.info("Reprocessing wiktionary complete")


def process_ns_page_title(page: Page, ns_name: str) -> Tuple[str, str]:
    text = page.body if page.body is not None else page.redirect_to
    title = page.title[page.title.find(":") + 1:]
    title = re.sub(r"(^|/)\.($|/)", r"\1__dotdot__\2", title)
    title = re.sub(r"(^|/)\.\.($|/)", r"\1__dotdot__\2", title)
    title = title.replace("//", "__slashslash__")
    title = re.sub(r"^/", r"__slash__", title)
    title = re.sub(r"/$", r"__slash__", title)
    title = ns_name + "/" + title
    return (title, text)


def extract_namespace(wxr: WiktextractContext,
                      namespace: str,
                      path: str
                    ) -> None:
    """Extracts all pages in the given namespace and writes them to a .tar
    file with the given path."""
    logging.info(
        f"Extracting pages from namespace {namespace} to tar file {path}")
    ns_id = wxr.wtp.NAMESPACE_DATA.get(namespace, {}).get("id")
    t = time.time()
    with tarfile.open(path, "w") as tarf:
        for page in wxr.wtp.get_all_pages([ns_id]):
            title, text = process_ns_page_title(page, namespace)
            text = text.encode("utf-8")
            f = io.BytesIO(text)
            title += ".txt"
            ti = tarfile.TarInfo(name=title)
            ti.size = len(text)
            ti.mtime = t
            ti.uid = 0
            ti.gid = 0
            ti.type = tarfile.REGTYPE
            tarf.addfile(ti, f)

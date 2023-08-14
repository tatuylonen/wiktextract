# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import io
import logging
import re
import sqlite3
import tarfile
import time
from pathlib import Path
from typing import List, Optional, Set, Tuple

from wikitextprocessor import Page

from .page import parse_page
from .thesaurus import (
    emit_words_in_thesaurus,
    extract_thesaurus_data,
    thesaurus_linkage_number,
)
from .wxr_context import WiktextractContext


def page_handler(
    wxr: WiktextractContext,
    page: Page,
    dont_parse: bool,
) -> Optional[Tuple[List[dict], dict]]:
    # Make sure there are no newlines or other strange characters in the
    # title.  They could cause security problems at several post-processing
    # steps.

    title = re.sub(r"[\s\000-\037]+", " ", page.title)
    title = title.strip()
    if dont_parse:
        return None
    if page.redirect_to is not None:
        ret = [{"title": title, "redirect": page.redirect_to}]
    else:
        if page.model != "wikitext":
            return None
        # the value of OTHER_SUBTITLES["translations"] is a string
        # use it to skip translation pages
        if title.endswith(f"/{wxr.config.OTHER_SUBTITLES.get('translations')}"):
            return None

        # XXX Sign gloss pages?

        # This function runs inside worker process, the sqlite connection needs
        # to be recreated to avoid `SQLite objects created in a thread can only
        # be used in that same thread` error
        wxr.thesaurus_db_conn.close()
        wxr.thesaurus_db_conn = sqlite3.connect(wxr.thesaurus_db_path)
        start_t = time.time()
        ret = parse_page(wxr, title, page.body)
        dur = time.time() - start_t
        if dur > 100:
            logging.warning(
                "====== WARNING: PARSING PAGE TOOK {:.1f}s: {}".format(
                    dur, title
                )
            )
        wxr.thesaurus_db_conn.close()

    return ret, wxr.wtp.to_return()


def parse_wiktionary(
    wxr: WiktextractContext,
    path: str,
    word_cb,
    phase1_only: bool,
    dont_parse: bool,
    namespace_ids: Set[int],
    override_folders: Optional[List[str]] = None,
    skip_extract_dump: bool = False,
    save_pages_path: Optional[str] = None,
):
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls `word_cb(data)` for all words defined for languages in `languages`."""
    assert callable(word_cb)
    capture_language_codes = wxr.config.capture_language_codes
    if capture_language_codes is not None:
        assert isinstance(capture_language_codes, (list, tuple, set))
        for x in capture_language_codes:
            assert isinstance(x, str)

    logging.info("First phase - extracting templates, macros, and pages")
    if override_folders is not None:
        override_folders = [Path(folder) for folder in override_folders]
    if save_pages_path is not None:
        save_pages_path = Path(save_pages_path)
    for _ in wxr.wtp.process(
        path,
        None,
        namespace_ids,
        True,
        override_folders,
        skip_extract_dump,
        save_pages_path,
    ):
        pass
    if phase1_only:
        return []

    # Phase 2 - process the pages using the user-supplied callback
    logging.info("Second phase - processing pages")
    return reprocess_wiktionary(wxr, word_cb, dont_parse)


def reprocess_wiktionary(
    wxr: WiktextractContext, word_cb, dont_parse, search_pattern: str = None
):
    """Reprocesses the Wiktionary from the cache file."""
    assert callable(word_cb)
    assert dont_parse in (True, False)

    # Extract thesaurus data. This iterates over thesaurus pages,
    # but is very fast.
    if thesaurus_linkage_number(wxr.thesaurus_db_conn) == 0:
        extract_thesaurus_data(wxr)

    # Then perform the main parsing pass.
    def page_cb(page: Page):
        return page_handler(wxr, page, dont_parse)

    emitted = set()
    process_ns_ids = list(
        {
            wxr.wtp.NAMESPACE_DATA.get(ns, {}).get("id", 0)
            for ns in ["Main", "Reconstruction"]
        }
    )
    for ret, stats in wxr.wtp.reprocess(
        page_cb,
        namespace_ids=process_ns_ids,
        search_pattern=search_pattern,
    ):
        wxr.config.merge_return(stats)
        for dt in ret:
            word_cb(dt)
            word = dt.get("word")
            lang_code = dt.get("lang_code")
            pos = dt.get("pos")
            if word and lang_code and pos:
                emitted.add((word, lang_code, pos))

    emit_words_in_thesaurus(wxr, emitted, word_cb)
    logging.info("Reprocessing wiktionary complete")


def process_ns_page_title(page: Page, ns_name: str) -> Tuple[str, str]:
    text = page.body if page.body is not None else page.redirect_to
    title = page.title[page.title.find(":") + 1 :]
    title = re.sub(r"(^|/)\.($|/)", r"\1__dotdot__\2", title)
    title = re.sub(r"(^|/)\.\.($|/)", r"\1__dotdot__\2", title)
    title = title.replace("//", "__slashslash__")
    title = re.sub(r"^/", r"__slash__", title)
    title = re.sub(r"/$", r"__slash__", title)
    title = ns_name + "/" + title
    return (title, text)


def extract_namespace(
    wxr: WiktextractContext, namespace: str, path: str
) -> None:
    """Extracts all pages in the given namespace and writes them to a .tar
    file with the given path."""
    logging.info(
        f"Extracting pages from namespace {namespace} to tar file {path}"
    )
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

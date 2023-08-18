# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import io
import json
import logging
import os
import re
import tarfile
import tempfile
import time
import traceback
from multiprocessing import Pool, current_process
from pathlib import Path
from typing import Dict, List, Optional, Set, TextIO, Tuple

from wikitextprocessor import Page
from wikitextprocessor.dumpparser import process_dump

from .page import parse_page
from .thesaurus import (
    emit_words_in_thesaurus,
    extract_thesaurus_data,
    thesaurus_linkage_number,
)
from .wxr_context import WiktextractContext


def page_handler(page: Page) -> Tuple[bool, Tuple[List[dict], dict], str]:
    # Make sure there are no newlines or other strange characters in the
    # title.  They could cause security problems at several post-processing
    # steps.
    wxr: WiktextractContext = page_handler.wxr
    # Helps debug extraction hangs. This writes the path of each file being
    # processed into /tmp/wiktextract*/wiktextract-*.  Once a hang
    # has been observed, these files contain page(s) that hang.  They should
    # be checked before aborting the process, as an interrupt might delete them.
    with tempfile.TemporaryDirectory(prefix="wiktextract") as tmpdirname:
        debug_path = "{}/wiktextract-{}".format(tmpdirname, os.getpid())
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(page.title + "\n")

        wxr.wtp.start_page(page.title)
        try:
            title = re.sub(r"[\s\000-\037]+", " ", page.title)
            title = title.strip()
            if page.redirect_to is not None:
                ret = [{"title": title, "redirect": page.redirect_to}]
            else:
                # the value of OTHER_SUBTITLES["translations"] is a string
                # use it to skip translation pages
                if title.endswith(
                    f"/{wxr.config.OTHER_SUBTITLES.get('translations')}"
                ):
                    return True, ([], {}), None

                # XXX Sign gloss pages?

                start_t = time.time()
                ret = parse_page(wxr, title, page.body)
                dur = time.time() - start_t
                if dur > 100:
                    logging.warning(
                        "====== WARNING: PARSING PAGE TOOK {:.1f}s: {}".format(
                            dur, title
                        )
                    )

            return True, (ret, wxr.wtp.to_return()), None
        except Exception as e:
            lst = traceback.format_exception(
                type(e), value=e, tb=e.__traceback__
            )
            msg = (
                '=== EXCEPTION while parsing page "{}":\n '
                "in process {}".format(
                    page.title,
                    current_process().name,
                )
                + "".join(lst)
            )
            return False, ([], {}), msg


def parse_wiktionary(
    wxr: WiktextractContext,
    dump_path: str,
    num_processes: Optional[int],
    phase1_only: bool,
    namespace_ids: Set[int],
    out_f: TextIO,
    human_readable: bool,
    override_folders: Optional[List[str]] = None,
    skip_extract_dump: bool = False,
    save_pages_path: Optional[str] = None,
) -> None:
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls `word_cb(data)` for all words defined for languages in `languages`."""
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

    process_dump(
        wxr.wtp,
        dump_path,
        namespace_ids,
        override_folders,
        skip_extract_dump,
        save_pages_path,
    )

    if not phase1_only:
        reprocess_wiktionary(wxr, num_processes, out_f, human_readable)


def write_json_data(data: Dict, out_f: TextIO, human_readable: bool) -> None:
    if out_f is not None:
        if human_readable:
            out_f.write(
                json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
            )
        else:
            out_f.write(json.dumps(data, ensure_ascii=False))
        out_f.write("\n")


def estimate_progress(
    processed_pages: int, all_pages: int, start_time: float, last_time: float
) -> float:
    current_time = time.time()
    processed_pages += 1
    if current_time - last_time > 1:
        remaining_pages = all_pages - processed_pages
        estimate_seconds = (
            (current_time - start_time) / processed_pages * remaining_pages
        )
        logging.info(
            "  ... {}/{} pages ({:.1%}) processed, "
            "{:02d}:{:02d}:{:02d} remaining".format(
                processed_pages,
                all_pages,
                processed_pages / all_pages,
                int(estimate_seconds / 3600),
                int(estimate_seconds / 60 % 60),
                int(estimate_seconds % 60),
            )
        )
        last_time = current_time
    return last_time


def init_worker_process(worker_func, wxr: WiktextractContext) -> None:
    wxr.reconnect_databases()
    worker_func.wxr = wxr


def reprocess_wiktionary(
    wxr: WiktextractContext,
    num_processes: Optional[int],
    out_f: TextIO,
    human_readable: bool,
    search_pattern: Optional[str] = None,
) -> None:
    """Reprocesses the Wiktionary from the sqlite db."""
    logging.info("Second phase - processing pages")

    # Extract thesaurus data. This iterates over thesaurus pages,
    # but is very fast.
    if thesaurus_linkage_number(wxr.thesaurus_db_conn) == 0:
        extract_thesaurus_data(wxr, num_processes)

    emitted = set()
    process_ns_ids = list(
        {
            wxr.wtp.NAMESPACE_DATA.get(ns, {}).get("id", 0)
            for ns in ["Main", "Reconstruction"]
        }
    )
    start_time = time.time()
    last_time = start_time
    all_page_nums = wxr.wtp.saved_page_nums(
        process_ns_ids, True, search_pattern
    )
    wxr.remove_unpicklable_objects()
    with Pool(num_processes, init_worker_process, (page_handler, wxr)) as pool:
        wxr.reconnect_databases(False)
        for processed_pages, (success, ret, err) in enumerate(
            pool.imap_unordered(
                page_handler,
                wxr.wtp.get_all_pages(
                    process_ns_ids, True, search_pattern=search_pattern
                ),
            )
        ):
            if not success:
                # Print error in parent process - do not remove
                logging.error(err)
                continue

            page_data, stats = ret
            wxr.config.merge_return(stats)
            for dt in page_data:
                write_json_data(dt, out_f, human_readable)
                word = dt.get("word")
                lang_code = dt.get("lang_code")
                pos = dt.get("pos")
                if word and lang_code and pos:
                    emitted.add((word, lang_code, pos))
            last_time = estimate_progress(
                processed_pages, all_page_nums, start_time, last_time
            )

    emit_words_in_thesaurus(wxr, emitted, out_f, human_readable)
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
    return title, text


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

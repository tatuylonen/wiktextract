# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2022, 2024 Tatu Ylonen.  See file LICENSE and https://ylonen.org

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
from typing import Optional, TextIO

from wikitextprocessor import Page
from wikitextprocessor.dumpparser import process_dump

from .page import parse_page
from .thesaurus import (
    emit_words_in_thesaurus,
    extract_thesaurus_data,
    thesaurus_linkage_number,
)
from .wxr_context import WiktextractContext


def page_handler(page: Page) -> tuple[list[dict], dict]:
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
                page_data = [
                    {
                        "title": title,
                        "redirect": page.redirect_to,
                        "pos": "hard-redirect",
                    }
                ]
            else:
                # XXX Sign gloss pages?
                start_t = time.time()
                page_data = parse_page(wxr, title, page.body)
                dur = time.time() - start_t
                if dur > 100:
                    logging.warning(
                        "====== WARNING: PARSING PAGE TOOK {:.1f}s: {}".format(
                            dur, title
                        )
                    )

            return page_data, wxr.wtp.to_return()
        except Exception:
            wxr.wtp.error(
                f'=== EXCEPTION while parsing page "{page.title}" '
                f"in process {current_process().name}",
                traceback.format_exc(),
                "page_handler_exception",
            )
            return [], wxr.wtp.to_return()


def parse_wiktionary(
    wxr: WiktextractContext,
    dump_path: str,
    num_processes: Optional[int],
    phase1_only: bool,
    namespace_ids: set[int],
    out_f: TextIO,
    human_readable: bool = False,
    override_folders: Optional[list[str]] = None,
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
        not wxr.config.analyze_templates,
    )

    if not phase1_only:
        reprocess_wiktionary(wxr, num_processes, out_f, human_readable)


def write_json_data(data: dict, out_f: TextIO, human_readable: bool) -> None:
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


def check_error(
        wxr: WiktextractContext,
        dt: dict,
        word: str,
        lang: str,
        pos: str,
        msg: str
) -> None:
    """Formats and outputs an error message about data format checks."""
    msg += ": " + json.dumps(dt, sort_keys=True)
    prefix = word or ""
    if lang:
        prefix += "/" + lang
    if pos:
        prefix += "/" + pos
    if prefix:
        msg = prefix + ": " + msg
    print(msg)
    config = wxr.config
    if len(config.debugs) > 100000:  # Avoid excessive size
        return
    dt = { "msg": msg,
           "trace": "",
           "title": word,
           "section": lang,
           "subsection": pos,
           "called_from": "XYZunsorted",
           "path": [] }
    config.debugs.append(dt)


def check_tags(
        wxr: WiktextractContext,
        dt: dict,
        word: str,
        lang: str,
        pos: str,
        item: dict
) -> None:
    assert isinstance(item, dict)
    tags = item.get("tags")
    if tags is None:
        return
    if not isinstance(tags, (list, tuple)):
        check_error(wxr, dt, word, lang, pos,
                    "\"tags\" field value must be a list of strings: {}"
                    .format(repr(tags)))
        return
    for tag in tags:
        if not isinstance(tag, str):
            check_error(wxr, dt, word, lang, pos,
                        "\"tags\" field should only contain strings: {}"
                        .format(repr(tag)))
            continue
        # XXX enable the following later (currently too many bogus tags in
        # non-English editions).  Tag values should be standardized across
        # editions, except for uppercase tags (e.g., regional variants).
        if wxr.wtp.lang_code in ("en",):  # Check edition
            from .tags import valid_tags

            if tag not in valid_tags:
                check_error(wxr, dt, word, lang, pos,
                            "invalid tag {} not in valid_tags (or "
                            "uppercase_tags)"
                            .format(repr(tag)))


def check_str_fields(
        wxr: WiktextractContext,
        dt: dict,
        word: str,
        lang: str,
        pos: str,
        item: dict,
        fields: list[str],
        mandatory: bool = False,
        empty_ok: bool = False
) -> None:
    """Checks that each of the listed fields contains a non-empty string.
    Non-existent fields are ok unless ``mandatory`` is True."""
    assert isinstance(item, dict)
    for field in fields:
        v = item.get(field)
        if v is None:
            if mandatory:
                check_error(wxr, dt, word, lang, pos,
                            "{!r} should be a non-empty string (it is a "
                            "mandatory field): {}"
                            .format(field,
                                    json.dumps(item, sort_keys=True)))
            continue
        if not isinstance(v, str):
            check_error(wxr, dt, word, lang, pos,
                        "{!r} should be a non-empty string: {}"
                        .format(field,
                                json.dumps(item, sort_keys=True)))
        if not v and not empty_ok:
            check_error(wxr, dt, word, lang, pos,
                        "{!r} should contain a non-empty string: {}"
                        .format(field, json.dumps(item, sort_keys=True)))



def check_dict_list_fields(
        wxr: WiktextractContext,
        dt: dict,
        word: str,
        lang: str,
        pos: str,
        item: dict,
        fields: list[str]
) -> bool:
    """Checks that each listed field, if present, is a list of dicts."""
    assert isinstance(item, dict)
    for field in fields:
        lst = item.get(field)
        if lst is None:
            continue
        if not isinstance(lst, (list, tuple)):
            check_error(wxr, dt, word, lang, pos,
                        "{!r} should be a list of dicts: {}"
                        .format(field,
                                json.dumps(lst, sort_keys=True)))
            return False
        for x in lst:
            if not isinstance(x, dict):
                check_error(wxr, dt, word, lang, pos,
                            "{!r} should be a list of dicts: {}"
                            .format(field,
                                    json.dumps(lst, sort_keys=True)))
                return False
    return True


def check_str_list_fields(
        wxr: WiktextractContext,
        dt: dict,
        word: str,
        lang: str,
        pos: str,
        item: dict,
        fields: list[str]
) -> None:
    """Checks that each of the listed fields contains a list of non-empty
    strings or is not present."""
    assert isinstance(item, dict)
    for field in fields:
        lst = item.get(field)
        if lst is None:
            continue
        if not isinstance(lst, (list, tuple)):
            check_error(wxr, dt, word, lang, pos,
                        "{!r} should be a list of dicts: {}"
                        .format(field, json.dumps(item, sort_keys=True)))
            continue
        for x in lst:
            if not isinstance(x, str) or not x:
                check_error(wxr, dt, word, lang, pos,
                            "{!r} should be a list of non-empty strings: {}"
                            .format(field,
                                    json.dumps(item, sort_keys=True)))
                break


def check_json_data(
        wxr: WiktextractContext,
        dt: dict
) -> None:
    """Performs some basic checks on the generated data."""
    word = dt.get("word", dt.get("title"))
    if word is None:
        check_error(
            wxr,
            dt,
            None,
            None,
            None,
            'missing "word" or "title" field in data',
        )
        return
    if "title" in dt:
        return  # redirect pages don't have following fields
    lang = dt.get("lang")
    if not lang:
        check_error(wxr, dt, word, None, None,
                    "missing \"lang\" field in data")
        return
    pos = dt.get("pos")
    if not pos:
        check_error(wxr, dt, word, lang, pos,
                    "missing \"pos\" field in data")
        return
    if not dt.get("lang_code"):
        check_error(wxr, dt, word, lang, pos,
                    "missing \"lang_code\" field in data")
    check_tags(wxr, dt, word, lang, pos, dt)
    check_str_fields(wxr, dt, word, lang, pos, dt,
                     ["etymology_text"])
    num = dt.get("etymology_number")
    if num is not None and not isinstance(num, int):
        check_error(wxr, dt, word, lang, pos,
                    "\"etymology_number\" must be an int")
    # Check that certain fields, if present, contain lists of dicts
    if not check_dict_list_fields(wxr, dt, word, lang, pos, dt,
                                  ["forms", "senses",
                                   "synonyms", "antonyms", "hypernyms",
                                   "holonyms", "meronyms",
                                   "coordinate_terms", "derived",
                                   "related",
                                   "sounds", "translations",
                                   "descendants", "etymology_templates",
                                   "head_templates",
                                   "inflection_templates"]):
        return  # Avoid further processing because it would cause type errors
    # Check the "forms" field
    forms = dt.get("forms") or []
    for form in forms:
        check_tags(wxr, dt, word, lang, pos, form)
        tags = dt.get("tags")
        if not isinstance(tags, (list, tuple)) or "table-tags" not in tags:
            check_str_fields(wxr, dt, word, lang, pos, form, ["form"],
                             mandatory=True)
    check_str_list_fields(wxr, dt, word, lang, pos, dt,
                          ["categories", "topics", "wikidata",
                           "wikipedia"])
    # Check the "senses" field
    senses = dt.get("senses") or []
    if not senses:
        check_error(wxr, dt, word, lang, pos,
                    "missing \"senses\" in data (must have at least one "
                    "sense, add empty sense with \"no-gloss\" tag if none "
                    "otherwise available)")
        return
    for sense in senses:
        check_str_list_fields(wxr, dt, word, lang, pos, sense,
                              ["glosses", "raw_glosses"])
        # Extra check: should have no-gloss tag if no glosses
        for field in ("glosses", "raw_glosses"):
            glosses = sense.get(field) or []
            if (not glosses and
                isinstance(sense.get("tags"), str) and
                "no-gloss" not in sense.get("tags", "").split()):
                check_error(wxr, dt, word, lang, pos,
                            "{!r} should have at least one gloss or "
                            "\"no-gloss\" in \"tags\""
                            .format(field))
                continue
        check_tags(wxr, dt, word, lang, pos, sense)
        check_str_list_fields(wxr, dt, word, lang, pos, sense,
                              ["categories", "topics", "wikidata",
                               "wikipedia"])
        check_str_fields(wxr, dt, word, lang, pos, sense,
                         ["english"])
        if not check_dict_list_fields(wxr, dt, word, lang, pos, sense,
                                      ["alt_of", "form_of",
                                       "synonyms", "antonyms", "hypernyms",
                                       "holonyms", "meronyms",
                                       "coordinate_terms", "derived",
                                       "related"]):
            continue
        for field in ("alt_of", "form_of"):
            lst = sense.get(field)
            if lst is None:
                continue
            for item in lst:
                check_str_fields(wxr, dt, word, lang, pos, item,
                                 ["word"], mandatory=True)
                check_str_fields(wxr, dt, word, lang, pos, item,
                                 ["extra"], mandatory=False)

        for field in ("synonyms", "antonyms", "hypernyms", "holonyms",
                      "meronyms", "coordinate_terms", "derived", "related"):
            lst = sense.get(field)
            if lst is None:
                continue
            for item in lst:
                check_str_fields(wxr, dt, word, lang, pos, item,
                                 ["word"], mandatory=True)
                check_tags(wxr, dt, word, lang, pos, item)
                check_str_fields(wxr, dt, word, lang, pos, item,
                                 ["english", "roman", "sense", "taxonomic"],
                                 mandatory=False, empty_ok=True)
                check_str_list_fields(wxr, dt, word, lang, pos, item,
                                      ["topics"])
    # Check the "sounds" field
    # We will permit having any number of different types (ipa, enpr, etc)
    # in the same sound entry or in different sound entries.
    sounds = dt.get("sounds") or []
    for item in sounds:
        check_str_fields(wxr, dt, word, lang, pos, item,
                         ["ipa", "enpr", "audio", "ogg_url", "mp3_url",
                          "audio-ipa", "text"])
        check_tags(wxr, dt, word, lang, pos, item)
        check_str_list_fields(wxr, dt, word, lang, pos, item,
                              ["homophones", "hyphenation"])
    # Check the "translations" field
    translations = dt.get("translations") or []
    for item in translations:
        check_str_fields(wxr, dt, word, lang, pos, item, ["word"],
                         mandatory=True)
        check_tags(wxr, dt, word, lang, pos, item)
        check_str_fields(wxr, dt, word, lang, pos, item,
                         ["alt", "code", "english", "lang", "note", "roman",
                          "sense", "taxonomic"])
        if not item.get("code") and not item.get("lang"):
            check_error(wxr, dt, word, lang, pos,
                        "\"translations\" items must contain at least one "
                        "of \"code\" and \"lang\" (normally both): {}"
                        .format(json.dumps(item, sort_keys=True)))
    # Check the "etymology_templates", "head_templates", and
    # "inflection_templates" fields
    for field in ["etymology_templates", "head_templates",
                  "inflection_templates"]:
        lst = dt.get(field)
        if lst is None:
            continue
        for item in lst:
            check_str_fields(wxr, dt, word, lang, pos, item, ["name"],
                             mandatory=True)
            check_str_fields(wxr, dt, word, lang, pos, item, ["expansion"],
                             mandatory=False)
            args = item.get("args")
            if args is None:
                continue
            if not isinstance(args, dict):
                check_error(wxr, dt, word, lang, pos,
                            "{!r} item \"args\" value must be a dict: {}"
                            .format(field, json.dumps(args, sort_keys=True)))
                continue
            for k, v in args.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    check_error(wxr, dt, word, lang, pos,
                                "{!r} item \"args\" must be a dict with "
                                "string keys and values: {}"
                                .format(field,
                                        json.dumps(args, sort_keys=True)))
                continue
    # Check the "descendants" field
    descendants = dt.get("descendants") or []
    for item in descendants:
        check_str_fields(wxr, dt, word, lang, pos, item, ["text"])
        depth = item.get("depth")
        if depth is not None and not isinstance(depth, int):
            check_error(wxr, dt, word, lang, pos,
                        "\"descentants\" field \"depth\" must be an int")
        check_dict_list_fields(wxr, dt, word, lang, pos, item, ["templates"])
        # XXX should check that they are valid templates, perhaps turn
        # template checking code above into a function


def reprocess_wiktionary(
    wxr: WiktextractContext,
    num_processes: Optional[int],
    out_f: TextIO,
    human_readable: bool = False,
    search_pattern: Optional[str] = None,
) -> None:
    """Reprocesses the Wiktionary from the sqlite db."""
    logging.info("Second phase - processing pages")

    # Extract thesaurus data. This iterates over thesaurus pages,
    # but is very fast.
    if (
        wxr.config.extract_thesaurus_pages
        and thesaurus_linkage_number(wxr.thesaurus_db_conn) == 0
    ):
        extract_thesaurus_data(wxr, num_processes)

    emitted = set()
    process_ns_ids = list(
        {
            wxr.wtp.NAMESPACE_DATA.get(ns, {}).get("id", 0)
            for ns in wxr.config.extract_ns_names
        }
    )
    start_time = time.time()
    last_time = start_time
    all_page_nums = wxr.wtp.saved_page_nums(
        process_ns_ids, True, "wikitext", search_pattern
    )
    wxr.remove_unpicklable_objects()
    with Pool(num_processes, init_worker_process, (page_handler, wxr)) as pool:
        wxr.reconnect_databases(False)
        for processed_pages, (page_data, wtp_stats) in enumerate(
            pool.imap_unordered(
                page_handler,
                wxr.wtp.get_all_pages(
                    process_ns_ids, True, "wikitext", search_pattern
                ),
            )
        ):
            wxr.config.merge_return(wtp_stats)
            for dt in page_data:
                check_json_data(wxr, dt)
                write_json_data(dt, out_f, human_readable)
                word = dt.get("word")
                lang_code = dt.get("lang_code")
                pos = dt.get("pos")
                if word and lang_code and pos:
                    emitted.add((word, lang_code, pos))
            last_time = estimate_progress(
                processed_pages, all_page_nums, start_time, last_time
            )
    if wxr.config.dump_file_lang_code == "en":
        emit_words_in_thesaurus(wxr, emitted, out_f, human_readable)
    logging.info("Reprocessing wiktionary complete")


def process_ns_page_title(page: Page, ns_name: str) -> tuple[str, str]:
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

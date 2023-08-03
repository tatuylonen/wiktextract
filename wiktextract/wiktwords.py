#!/usr/bin/env python3
#
# Main program for extracting a dictionary from wiktionary.  This has
# mostly been used with enwiktionary, but should be usable with other
# wiktionaries as well.
#
# Copyright (c) 2018-2023 Tatu Ylonen.  See LICENSE and https://ylonen.org
#
# For pre-extracted data files, see https://kaikki.org/dictionary/

import os
import re
import sys
import json
import logging
import pstats
import argparse
import collections

from pathlib import Path
from typing import Any, Callable

from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor import Wtp
from wikitextprocessor.dumpparser import analyze_and_overwrite_pages
from wiktextract.inflection import set_debug_cell_text
from wiktextract.template_override import template_override_fns

from wiktextract import (WiktionaryConfig, parse_wiktionary,
                         reprocess_wiktionary, parse_page,
                         extract_namespace)
from wiktextract.thesaurus import (
    extract_thesaurus_data, thesaurus_linkage_number, close_thesaurus_db
)
from wiktextract import extract_categories

# Pages within these namespaces are captured.
RECOGNIZED_NAMESPACE_NAMES = [
    "Main",
    "Category",
    "Appendix",
    "Project",
    "Thesaurus",
    "Module",
    "Template",
    "Reconstruction"
]


def process_single_page(
    path_or_title: str,
    args: argparse.Namespace,
    wxr: WiktextractContext,
    word_cb: Callable[[Any], None],
) -> None:
    if Path(path_or_title).exists():
        # Load the page wikitext from the given file
        with open(path_or_title, encoding="utf-8") as f:
            first_line = f.readline()
            if first_line.startswith("TITLE: "):
                title = first_line[7:].strip()
            else:
                title = "Test page"
                f.seek(0)
            text = f.read()
    else:
        # Get page content from database
        title = path_or_title
        text = wxr.wtp.read_by_title(title)
        if text is None:
            logging.error(f"Can't find page '{title}' in the database.")
            return

    # Extract Thesaurus data (this is a bit slow for a single page, but
    # needed for debugging linkages with thesaurus extraction).  This
    # is disabled by default to speed up single page testing.
    if (
        args.use_thesaurus
        and thesaurus_linkage_number(wxr.thesaurus_db_conn) == 0
    ):
        extract_thesaurus_data(wxr)
    # Parse the page
    ret = parse_page(wxr, title, text)
    for x in ret:
        word_cb(x)


def main():
    parser = argparse.ArgumentParser(
        description="Multilingual Wiktionary data extractor")
    parser.add_argument("path", type=str, nargs="?", default=None,
                        help="Input file (.../enwiktionary-<date>-"
                        "pages-articles.xml.bz2)")
    parser.add_argument("--out", type=str, default=None,
                        help="Path where to write output (- for stdout)")
    parser.add_argument("--errors", type=str,
                        help="File in which to save error information")
    parser.add_argument("--dump-file-language-code", type=str, default="en",
                        help="Language code of the dump file.")
    parser.add_argument("--language", type=str, action="append", default=[],
                        help="Language code to capture (can specify multiple "
                        "times, defaults to English [en] and "
                        "Translingual [mul])")
    parser.add_argument("--all-languages", action="store_true", default=False,
                        help="Extract words for all languages")
    parser.add_argument("--list-languages", action="store_true", default=False,
                        help="Print list of supported languages")
    parser.add_argument("--pages-dir", type=str, default=None,
                        help="Directory under which to save all pages")
    parser.add_argument("--all", action="store_true", default=False,
                        help="Capture everything for the selected languages")
    parser.add_argument("--translations", action="store_true", default=False,
                        help="Capture translations")
    parser.add_argument("--pronunciations", action="store_true", default=False,
                        help="Capture pronunciation information")
    parser.add_argument("--linkages", action="store_true", default=False,
                        help="Capture linkages (hypernyms, synonyms, etc)")
    parser.add_argument("--compounds", action="store_true", default=False,
                        help="Capture compound words using each word")
    parser.add_argument("--redirects", action="store_true", default=False,
                        help="Capture redirects")
    parser.add_argument("--examples", action="store_true", default=False,
                        help="Capture usage examples")
    parser.add_argument("--etymologies", action="store_true", default=False,
                        help="Capture etymologies")
    parser.add_argument("--inflections", action="store_true", default=False,
                        help="Capture inflection tables")
    parser.add_argument("--descendants", action="store_true", default=False,
                        help="Capture descendants")
    parser.add_argument("--statistics", action="store_true", default=False,
                        help="Print statistics")
    parser.add_argument("--page", type=str, action="append",
                        help="Pass a Wiktionary page title or file path for "
                        "debugging. Can be specified multiple times.")
    parser.add_argument("--db-path", type=str,
                        help="File path of saved database; "
                        "speeds up processing a single page tremendously")
    parser.add_argument("--num-threads", type=int, default=None,
                        help="Number of parallel processes (default: #cpus)")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Print verbose status messages (for debugging)")
    parser.add_argument("--human-readable", action="store_true", default=False,
                        help="Write output in human-readable JSON")
    parser.add_argument("--override", type=str, action="append",
                        help="Override module(s) by one in file or files in "
                             "directory (for debugging)")
    parser.add_argument("--use-thesaurus", action="store_true", default=False,
                        help="Include thesaurus in single page mode")
    parser.add_argument("--profile", action="store_true", default=False,
                        help="Enable CPU time profiling")
    parser.add_argument("--categories-file", type=str,
                        help="Extract category tree as JSON in this file")
    parser.add_argument("--modules-file", type=str,
                        help="Extract all modules and save in this .tar file")
    parser.add_argument("--templates-file", type=str,
                        help="Extract all templates and save in this .tar file")
    parser.add_argument("--redirects-file", type=str,
                        help="Optional file containing sound file redirect "
                        "names from Wikimedia Commons and what "
                        "they point to")
    parser.add_argument("--inflection-tables-file", type=str, default=None,
                    help="Extract expanded tables in this file (for test data)")
    parser.add_argument("--debug-cell-text", type=str, default=None,
                    help="Print out debug messages when encountering this text")
    parser.add_argument("--quiet", default=False, action="store_true")
    parser.add_argument("--search-pattern", type=str, default=None,
                    help="Filter out pages that do not contain this pattern "
                        "of text; %% is zero, one or more wildcard characters, "
                        "_ is exactly one wildcard character. Example: "
                        "'%%==English==%%', '%%==Anglo_Saxon==%%'; functions "
                        "only with ready database file")
    args = parser.parse_args()

    if not args.quiet:
        logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
                            level=logging.DEBUG)

    if args.debug_cell_text:
        # importing debug_cell_text from wiktextract.inflection
        # does not work because the debug_cell_text here would be
        # only a reference, and assigning to it just changes the
        # thing it is pointing at. Instead of just importing the
        # whole inflection module and doing wiktextract.inflection
        # .debug_cell_text =, a simple setter function does
        # the same thing.
        set_debug_cell_text(args.debug_cell_text)

    # The --all option turns on capturing all data types
    if args.all and (not args.pages_dir or args.out):
        args.translations = True
        args.pronunciations = True
        args.linkages = True
        args.compounds = True
        args.redirects = True
        args.examples = True
        args.etymologies = True
        args.inflections = True
        args.descendants = True

    # Default to English and Translingual if language not specified.
    if not args.language:
        args.language = ["en", "mul"]

    if args.all_languages:
        args.language = None
        print("Capturing words for all available languages")
    else:
        print("Capturing words for:", ", ".join(args.language))

    if args.num_threads and args.num_threads > 1:
        import multiprocessing

        if multiprocessing.get_start_method() == "spawn":
            logging.error("--num-threads not supported on this OS (no stable "
                          "implementation of fork() available)")
            sys.exit(1)

    # Open output file.
    out_path = args.out
    if not out_path and args.pages_dir:
        out_f = None
    elif out_path and out_path != "-":
        if out_path.startswith("/dev/"):
            out_tmp_path = out_path
        else:
            out_tmp_path = out_path + ".tmp"
        out_f = open(out_tmp_path, "w", buffering=1024*1024, encoding="utf-8")
    else:
        out_tmp_path = out_path
        out_f = sys.stdout

    word_count = 0

    # Create expansion context

    conf1 = WiktionaryConfig(dump_file_lang_code=args.dump_file_language_code,
                              capture_language_codes=args.language,
                              capture_translations=args.translations,
                              capture_pronunciation=args.pronunciations,
                              capture_linkages=args.linkages,
                              capture_compounds=args.compounds,
                              capture_redirects=args.redirects,
                              capture_examples=args.examples,
                              capture_etymologies=args.etymologies,
                              capture_inflections=args.inflections,
                              capture_descendants=args.descendants,
                              verbose=args.verbose,
                              expand_tables=args.inflection_tables_file,)


    if args.language:
        new_lang_codes = []
        for x in args.language:
            if x not in conf1.LANGUAGES_BY_CODE:
                if x in conf1.LANGUAGES_BY_NAME:
                    new_lang_codes.append(conf1.LANGUAGES_BY_NAME[x])
                else:
                    logging.error(f"Invalid language: {x}")
                    sys.exit(1)
            else:
                new_lang_codes.append(x)
        conf1.capture_language_codes = new_lang_codes

    if args.language:
        lang_names = []
        for x in args.language:
            if x in conf1.LANGUAGES_BY_CODE:
                lang_names.extend(conf1.LANGUAGES_BY_CODE[x])
            else:
                lang_names.extend(conf1.LANGUAGES_BY_CODE[
                                            conf1.LANGUAGES_BY_NAME[x] ])

        lang_names = [re.escape(x) for x in lang_names]
        lang_names_re = r"==\s*("
        lang_names_re += "|".join(lang_names)
        lang_names_re += r")"
        lang_names_re = re.compile(lang_names_re)

    # If --list-languages has been specified, just print the list of supported
    # languages
    if args.list_languages:
        print("Supported languages:")
        for lang_name, lang_code in conf1.LANGUAGES_BY_NAME.items():
            print(f"    {lang_name}: {lang_code}")
        sys.exit(0)

    if not args.path and not args.db_path:
        print("The PATH argument for wiktionary dump file is normally "
              "mandatory.")
        print("Alternatively, --db-path with --page can be used.")
        sys.exit(1)

    context1 = Wtp(db_path=args.db_path, num_threads=args.num_threads,
                   lang_code=args.dump_file_language_code,
                   languages_by_code=conf1.LANGUAGES_BY_CODE,
                   template_override_funcs=template_override_fns)

    wxr = WiktextractContext(context1, conf1)

    def word_cb(data):
        nonlocal word_count
        word_count += 1
        if out_f is not None:
            if args.human_readable:
                out_f.write(json.dumps(data, indent=2, sort_keys=True,
                                       ensure_ascii=False))
            else:
                out_f.write(json.dumps(data, ensure_ascii=False))
            out_f.write("\n")
            if not out_path or out_path == "-" or word_count % 1000 == 0:
                out_f.flush()

    # load redirects if given
    if args.redirects_file:
        with open(args.redirects_file) as f:
            wxr.config.redirects = json.load(f)

    if args.profile:
        import cProfile

        pr = cProfile.Profile()
        pr.enable()

    try:
        if args.path:
            namespace_ids = {
                wxr.wtp.NAMESPACE_DATA.get(name, {}).get("id")
                for name in RECOGNIZED_NAMESPACE_NAMES
            }
            # Parse the normal full Wiktionary data dump
            parse_wiktionary(wxr, args.path, word_cb,
                             (args.page is not None),  # phase1_only
                             (args.pages_dir is not None and
                              not args.out), # dont_parse
                             namespace_ids,
                             args.override,
                             wxr.wtp.saved_page_nums() > 0,
                             args.pages_dir)

        if args.page:
            # Parse a single Wiktionary page (extracted using --pages-dir)
            if not args.db_path:
                logging.warning(
                    "NOTE: you probably want to use --db-path with --page or "
                    "otherwise processing will be very slow."
                )
            if args.override is not None and args.path is None:
                analyze_and_overwrite_pages(
                    wxr.wtp, [Path(p) for p in args.override]
                )

            for title_or_path in args.page:
                process_single_page(title_or_path, args, wxr, word_cb)

            # Merge errors from wtp to config, so that we can also use
            # --errors with single page extraction
            wxr.config.merge_return(wxr.wtp.to_return())

        if not args.path and not args.page:
            # Parse again from the cache file
            reprocess_wiktionary(wxr, word_cb,
                                 dont_parse=(bool(args.pages_dir) and
                                                 not bool(args.out)),
                                 search_pattern=args.search_pattern)

    finally:
        if out_path and out_path != "-" and out_f is not None:
            out_f.close()

    if args.modules_file:
        extract_namespace(wxr, "Module", args.modules_file)
    if args.templates_file:
        extract_namespace(wxr, "Template", args.templates_file)
    if args.categories_file:
        logging.info("Extracting category tree")
        tree = extract_categories(wxr)
        with open(args.categories_file, "w") as f:
            json.dump(tree, f, indent=2, sort_keys=True)

    wxr.wtp.close_db_conn()
    close_thesaurus_db(wxr.thesaurus_db_path, wxr.thesaurus_db_conn)

    if args.profile:
        pr.disable()
        ps = pstats.Stats(pr).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats()

    if out_f is not None and out_path != out_tmp_path:
        try:
            os.remove(out_path)
        except FileNotFoundError:
            pass
        os.rename(out_tmp_path, out_path)

    if args.statistics:
        print("")
        print("LANGUAGE COUNTS")
        for k, cnt in sorted(wxr.config.language_counts.items(),
                             key=lambda x: -x[1]):
            print("  {:>7d} {}".format(cnt, k))
            if cnt < 1000:
                break
        print("  ...")
        print("")

        print("")
        print("POS HEADER USAGE")
        for k, cnt in sorted(wxr.config.pos_counts.items(),
                             key=lambda x: -x[1]):
            print("  {:>7d} {}".format(cnt, k))

        print("")
        print("POS SUBSECTION HEADER USAGE")
        for k, cnt in sorted(wxr.config.section_counts.items(),
                             key=lambda x: -x[1]):
            print("  {:>7d} {}".format(cnt, k))

        print("")
        print("{} WORDS CAPTURED".format(word_count))

    if args.errors:
        with open(args.errors, "w", encoding="utf-8") as f:
            json.dump({
                "errors": wxr.config.errors,
                "warnings": wxr.config.warnings,
                "debugs": wxr.config.debugs,
                }, f, sort_keys=True)

    def dump_un(title, limit, counts, samples):
        counts_ht = {}
        for k, v in counts.items():
            counts_ht[k] = v
        lst = list(sorted(counts_ht.items(), reverse=True,
                          key=lambda x: x[1]))
        if lst:
            print(title)
            for k, cnt in lst[:limit]:
                print("{:5d} {}".format(cnt, k))
                for kk, vv in samples[k].items():
                    for sample in vv:
                        print("        {}".format(sample))

    def dump_val(title, limit, counts):
        counts_ht = collections.defaultdict(int)
        for la, la_val in counts.items():
            for name, name_val in la_val.items():
                for value, cnt in name_val.items():
                    counts_ht[name, value] += cnt
        for la, la_val in counts.items():
            for name, name_val in la_val.items():
                for value, v in name_val.items():
                    counts_ht[name, value] = v
        lst = list(sorted(counts_ht.items(), reverse=True,
                          key=lambda x: x[1]))
        if lst:
            print("")
            print(title)
            for (k, kk), v in lst[:limit]:
                print("  {:5d} {}: {}".format(v, k, kk))


if __name__ == "__main__":
    main()

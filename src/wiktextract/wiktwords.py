#!/usr/bin/env python3
#
# Main program for extracting a dictionary from wiktionary.  This has
# mostly been used with enwiktionary, but should be usable with other
# wiktionaries as well.
#
# Copyright (c) 2018-2023 Tatu Ylonen.  See LICENSE and https://ylonen.org
#
# For pre-extracted data files, see https://kaikki.org/dictionary/

import argparse
import collections
import json
import logging
import os
import pstats
import sys
from importlib.resources import files
from pathlib import Path
from typing import TextIO

from mediawiki_langcodes import code_to_name, name_to_code
from wikitextprocessor import Wtp
from wikitextprocessor.dumpparser import analyze_and_overwrite_pages

from .categories import extract_categories
from .config import WiktionaryConfig
from .template_override import template_override_fns
from .thesaurus import (
    close_thesaurus_db,
    extract_thesaurus_data,
    thesaurus_linkage_number,
)
from .wiktionary import (
    check_json_data,
    extract_namespace,
    parse_page,
    parse_wiktionary,
    reprocess_wiktionary,
    write_json_data,
)
from .wxr_context import WiktextractContext
from .wxr_logging import logger


def process_single_page(
    path_or_title: str,
    args: argparse.Namespace,
    wxr: WiktextractContext,
    out_f: TextIO,
    human_readable: bool,
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
        text = wxr.wtp.get_page_body(title, None)  # type: ignore[assignment]
        if text is None:
            logger.error(f"Can't find page '{title}' in the database.")
            return

    # Extract Thesaurus data (this is a bit slow for a single page, but
    # needed for debugging linkages with thesaurus extraction).  This
    # is disabled by default to speed up single page testing.
    if (
        args.use_thesaurus
        and wxr.config.extract_thesaurus_pages
        and thesaurus_linkage_number(wxr.thesaurus_db_conn) == 0  # type: ignore[arg-type]
    ):
        extract_thesaurus_data(wxr)
    # Parse the page
    ret = parse_page(wxr, title, text)
    for data in ret:
        check_json_data(wxr, data)
        write_json_data(data, out_f, human_readable)


def main():
    parser = argparse.ArgumentParser(
        description="Multilingual Wiktionary data extractor"
    )
    parser.add_argument(
        "path",
        type=str,
        nargs="?",
        default=None,
        help="Input file (.../enwiktionary-<date>-pages-articles.xml.bz2)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Path where to write output (- for stdout)",
    )
    parser.add_argument(
        "--errors", type=str, help="File in which to save error information"
    )
    parser.add_argument(
        "--dump-file-language-code",
        "--edition",
        type=str,
        required=True,
        choices=sorted(
            [
                p.stem
                for p in (files("wiktextract") / "extractor").iterdir()
                if p.is_dir()
                and p.stem != "template"
                and (p / "page.py").is_file()
            ]
        ),
        help="Language code of the dump file.",
    )
    parser.add_argument(
        "--language-code",
        type=str,
        action="append",
        default=[],
        help="Language code to capture (can specify multiple times, defaults "
        "to dump file language code and `mul`(Translingual))",
    )
    parser.add_argument(
        "--language-name",
        type=str,
        action="append",
        default=[],
        help="Language names to capture (can specify multiple times, defaults "
        "to dump file language and Translingual)",
    )
    parser.add_argument(
        "--all-languages",
        action="store_true",
        default=False,
        help="Extract words for all languages",
    )
    parser.add_argument(
        "--pages-dir",
        type=str,
        default=None,
        help="Directory under which to save all pages",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Capture everything for the selected languages",
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        default=False,
        help="Skip the (usually lengthy) json data extraction "
        "procedure to do other things, like creating a database "
        "file or other files.",
    )
    parser.add_argument(
        "--translations",
        action="store_true",
        default=False,
        help="Capture translations",
    )
    parser.add_argument(
        "--pronunciations",
        action="store_true",
        default=False,
        help="Capture pronunciation information",
    )
    parser.add_argument(
        "--linkages",
        action="store_true",
        default=False,
        help="Capture linkages (hypernyms, synonyms, etc)",
    )
    parser.add_argument(
        "--compounds",
        action="store_true",
        default=False,
        help="Capture compound words using each word",
    )
    parser.add_argument(
        "--redirects",
        action="store_true",
        default=False,
        help="Capture redirects",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        default=False,
        help="Capture usage examples",
    )
    parser.add_argument(
        "--etymologies",
        action="store_true",
        default=False,
        help="Capture etymologies",
    )
    parser.add_argument(
        "--inflections",
        action="store_true",
        default=False,
        help="Capture inflection tables",
    )
    parser.add_argument(
        "--descendants",
        action="store_true",
        default=False,
        help="Capture descendants",
    )
    parser.add_argument(
        "--page",
        type=str,
        action="append",
        help="Pass a Wiktionary page title or file path for debugging. Can be "
        "specified multiple times.",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="File path of saved database; speeds up processing a single page "
        "tremendously",
    )
    parser.add_argument(
        "--num-processes",
        type=int,
        default=None,
        help="Number of parallel processes (default: #cpus)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print verbose status messages (for debugging)",
    )
    parser.add_argument(
        "--human-readable",
        action="store_true",
        default=False,
        help="Write output in human-readable JSON",
    )
    parser.add_argument(
        "--override",
        type=str,
        action="append",
        help="Path of JSON file contains override page data",
    )
    parser.add_argument(
        "--use-thesaurus",
        action="store_true",
        default=False,
        help="Include thesaurus in single page mode",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="Enable CPU time profiling",
    )
    parser.add_argument(
        "--categories-file",
        type=str,
        help="Extract category tree as JSON in this file",
    )
    parser.add_argument(
        "--modules-file",
        type=str,
        help="Extract all modules and save in this .tar file",
    )
    parser.add_argument(
        "--templates-file",
        type=str,
        help="Extract all templates and save in this .tar file",
    )
    parser.add_argument(
        "--redirects-file",
        type=str,
        help="Optional file containing sound file redirect names from "
        "Wikimedia Commons and what they point to",
    )
    parser.add_argument(
        "--inflection-tables-file",
        type=str,
        default=None,
        help="Extract expanded tables in this file (for test data)",
    )
    parser.add_argument(
        "--debug-cell-text",
        type=str,
        default=None,
        help="Print out debug messages when encountering this text",
    )
    parser.add_argument("--quiet", default=False, action="store_true")
    parser.add_argument(
        "--search-pattern",
        type=str,
        default=None,
        help="Filter out pages that do not contain this pattern of text; %% is "
        "zero, one or more wildcard characters, _ is exactly one wildcard "
        "character. Example: '%%==English==%%', '%%==Anglo_Saxon==%%'; "
        "functions only with ready database file",
    )
    args = parser.parse_args()

    if not args.quiet:
        logger.setLevel(logging.DEBUG)

    if args.debug_cell_text:
        # importing debug_cell_text from wiktextract.inflection
        # does not work because the debug_cell_text here would be
        # only a reference, and assigning to it just changes the
        # thing it is pointing at. Instead of just importing the
        # whole inflection module and doing wiktextract.inflection
        # .debug_cell_text =, a simple setter function does
        # the same thing.
        from .extractor.en.inflection import set_debug_cell_text

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

    # Default to dump file language and Translingual if not specified.
    capture_lang_codes = set()
    if len(args.language_code) > 0:
        for lang_code in args.language_code:
            lang_name = code_to_name(lang_code, args.dump_file_language_code)
            if lang_name == "":
                logger.warning(f"Unknown language code: {lang_code}")
            else:
                capture_lang_codes.add(lang_code)
    if len(args.language_name) > 0:
        for lang_name in args.language_name:
            lang_code = name_to_code(lang_name, args.dump_file_language_code)
            if lang_code == "":
                logger.warning(f"Unknown language name: {lang_name}")
            else:
                capture_lang_codes.add(lang_code)
    if len(capture_lang_codes) == 0:
        capture_lang_codes = {args.dump_file_language_code, "mul"}

    if args.all_languages:
        capture_lang_codes = None
        logger.info("Capturing words for all available languages")
    else:
        logger.info(f"Capturing words for: {', '.join(capture_lang_codes)}")

    # Open output file.
    out_path = args.out
    if not out_path and args.pages_dir:
        out_f = None
    elif out_path and out_path != "-":
        if out_path.startswith("/dev/"):
            out_tmp_path = out_path
        else:
            out_tmp_path = out_path + ".tmp"
        out_f = open(out_tmp_path, "w", buffering=1024 * 1024, encoding="utf-8")
    else:
        out_tmp_path = out_path
        out_f = sys.stdout

    # Create expansion context

    conf = WiktionaryConfig(
        dump_file_lang_code=args.dump_file_language_code,
        capture_language_codes=capture_lang_codes,
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
        expand_tables=args.inflection_tables_file,
    )

    if not args.path and not args.db_path:
        print(
            "The PATH argument for wiktionary dump file is normally mandatory."
        )
        print("Alternatively, --db-path with --page can be used.")
        sys.exit(1)

    wtp = Wtp(
        db_path=args.db_path,
        lang_code=args.dump_file_language_code,
        template_override_funcs=template_override_fns
        if args.dump_file_language_code == "en"
        else {},
        extension_tags=conf.allowed_html_tags,
        parser_function_aliases=conf.parser_function_aliases,
        quiet=args.quiet,
    )
    wxr = WiktextractContext(wtp, conf)

    # load redirects if given
    if args.redirects_file:
        with open(args.redirects_file) as f:
            wxr.config.redirects = json.load(f)

    if args.profile:
        import cProfile

        pr = cProfile.Profile()
        pr.enable()

    skip_extract_dump = wxr.wtp.saved_page_nums() > 0
    default_override_json_path = (
        files("wiktextract")
        / "data"
        / "overrides"
        / f"{args.dump_file_language_code}.json"
    )
    if default_override_json_path.exists() and not skip_extract_dump:
        if args.override is None:
            args.override = [default_override_json_path]
        elif default_override_json_path not in args.override:
            args.override.append(default_override_json_path)

    try:
        if args.path is not None:
            namespace_ids = {
                wxr.wtp.NAMESPACE_DATA.get(name, {}).get("id", 0)
                for name in wxr.config.save_ns_names
            }
            # Parse the normal full Wiktionary data dump
            parse_wiktionary(
                wxr,
                args.path,
                args.num_processes,
                args.page is not None
                or (args.pages_dir is not None and not args.out)
                or args.skip_extraction,  # phase1_only
                namespace_ids,
                out_f,
                args.human_readable,
                args.override,
                skip_extract_dump,
                args.pages_dir,
            )

        if args.override is not None and args.path is None:
            analyze_and_overwrite_pages(
                wxr.wtp,
                [Path(p) for p in args.override],
                skip_extract_dump,
                None,
            )

        if args.page and not args.skip_extraction:
            # Parse a single Wiktionary page (extracted using --pages-dir)
            if not args.db_path:
                logger.warning(
                    "NOTE: you probably want to use --db-path with --page or "
                    "otherwise processing will be very slow."
                )

            for title_or_path in args.page:
                process_single_page(
                    title_or_path, args, wxr, out_f, args.human_readable
                )

            # Merge errors from wtp to config, so that we can also use
            # --errors with single page extraction
            wxr.config.merge_return(wxr.wtp.to_return())

        if not args.path and not args.page and not args.skip_extraction:
            # Parse again from the db file
            reprocess_wiktionary(
                wxr,
                args.num_processes,
                out_f,
                args.human_readable,
                search_pattern=args.search_pattern,
            )

    finally:
        if out_path and out_path != "-" and out_f is not None:
            out_f.close()

    if args.modules_file:
        extract_namespace(wxr, "Module", args.modules_file)
    if args.templates_file:
        extract_namespace(wxr, "Template", args.templates_file)
    if args.categories_file and args.dump_file_language_code == "en":
        logger.info("Extracting category tree")
        tree = extract_categories(wxr)
        with open(args.categories_file, "w") as f:
            json.dump(tree, f, indent=2, sort_keys=True)

    wxr.wtp.close_db_conn()
    if wxr.config.extract_thesaurus_pages:
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

    if args.errors:
        with open(args.errors, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "errors": wxr.config.errors,
                    "warnings": wxr.config.warnings,
                    "debugs": wxr.config.debugs,
                    "notes": wxr.config.notes,
                    "wiki_notices": wxr.config.wiki_notices,
                },
                f,
                sort_keys=True,
            )

    def dump_un(title, limit, counts, samples):
        counts_ht = {}
        for k, v in counts.items():
            counts_ht[k] = v
        lst = list(sorted(counts_ht.items(), reverse=True, key=lambda x: x[1]))
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
        lst = list(sorted(counts_ht.items(), reverse=True, key=lambda x: x[1]))
        if lst:
            print("")
            print(title)
            for (k, kk), v in lst[:limit]:
                print("  {:5d} {}: {}".format(v, k, kk))


if __name__ == "__main__":
    main()

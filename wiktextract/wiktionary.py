# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import io
import re
import sys
import time
import tarfile
import collections
from wikitextprocessor import Wtp
from wiktextract.wxr_context import WiktextractContext
from .page import (parse_page, additional_expand_templates)
from .config import WiktionaryConfig
from .thesaurus import extract_thesaurus_data
from .datautils import data_append

# Title prefixes that indicate that the page is not a normal page and
# should not be used when searching for word forms
SPECIAL_PREFIXES = None

# Title suffixes that indicate that the page should be ignored
ignore_suffixes = [
    "/documentation",
]

# Title suffixes that indicate the page is a translation page
translation_suffixes = [
    "/translations",
]


def init_special_prefixes(wxr: WiktextractContext) -> None:
    global SPECIAL_PREFIXES
    if SPECIAL_PREFIXES is None:
        SPECIAL_PREFIXES = {
            wxr.wtp.NAMESPACE_DATA.get("Category", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Module", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Template", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Citations", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Appendix", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Rhymes", {}).get("name"),  # XXX check these out
            wxr.wtp.NAMESPACE_DATA.get("Project", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Thread", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Index", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Thesaurus", {}).get("name"),  # These are handled as a separate pass
            wxr.wtp.NAMESPACE_DATA.get("MediaWiki", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Concordance", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("Sign gloss", {}).get("name"),  # XXX would I like to capture these too?
            wxr.wtp.NAMESPACE_DATA.get("Help", {}).get("name"),
            wxr.wtp.NAMESPACE_DATA.get("File", {}).get("name"),
        }


def page_handler(wxr, model, title, text, capture_cb, config_kwargs,
                 thesaurus_data, dont_parse):
    # Make sure there are no newlines or other strange characters in the
    # title.  They could cause security problems at several post-processing
    # steps.
    init_special_prefixes(wxr)
    title = re.sub(r"[\s\000-\037]+", " ", title)
    title = title.strip()
    if capture_cb and not capture_cb(model, title, text):
        return None
    if dont_parse:
        return None
    if model == "redirect":
        config1 = WiktionaryConfig()
        wxr1 = WiktextractContext(config1, wxr.wtp)
        ret = [{"title": title, "redirect": text}]
    else:
        if model != "wikitext":
            return None
        idx = title.find(":")
        if idx >= 0:
            prefix = title[:idx]
            if prefix in SPECIAL_PREFIXES:
                return None
        for suffix in ignore_suffixes:
            if title.endswith(suffix):
                return None
        for suffix in translation_suffixes:
            if title.endswith(suffix):
                return None # XXX

        # XXX Sign gloss pages?
        config1 = WiktionaryConfig(**config_kwargs)
        wxr1 = WiktextractContext(config1, wxr.wtp)
        wxr1.config.thesaurus_data = thesaurus_data
        start_t = time.time()
        ret = parse_page(wxr, title, text)
        dur = time.time() - start_t
        if dur > 100:
            print("====== WARNING: PARSING PAGE TOOK {:.1f}s: {}"
                  .format(dur, title))
    stats = wxr1.config.to_return()
    for k, v in wxr1.wtp.to_return().items():
        stats[k] = v
    return (ret, stats)


def parse_wiktionary(wxr, path, word_cb, capture_cb,
                     phase1_only, dont_parse):
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls ``capture_cb(title)`` for each raw page (if provided), and
    if it returns True, and calls ``word_cb(data)`` for all words
    defined for languages in ``languages``."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(path, str)
    assert callable(word_cb)
    assert capture_cb is None or callable(capture_cb)
    assert phase1_only in (True, False)
    capture_language_codes = wxr.config.capture_language_codes
    if capture_language_codes is not None:
        assert isinstance(capture_language_codes, (list, tuple, set))
        for x in capture_language_codes:
            assert isinstance(x, str)

    # config_kwargs = wxr.config.to_kwargs()

    if not wxr.wtp.quiet:
        print("First phase - extracting templates, macros, and pages")
        sys.stdout.flush()

    # def page_cb(model, title, text):
    #     return page_handler(wxr, model, title, text, capture_cb, config_kwargs)

    # langhd is needed for pre-expanding language heading templates in the
    # Chinese Wiktionary dump file: https://zh.wiktionary.org/wiki/Template:-en-
    # Move this to lang_specific
    if wxr.wtp.lang_code == "zh":
        additional_expand_templates.add("langhd")
    
    list(wxr.wtp.process(path, None, phase1_only=True))
    if phase1_only:
        return []

    # Phase 2 - process the pages using the user-supplied callback
    if not wxr.wtp.quiet:
        print("Second phase - processing pages")
        sys.stdout.flush()

    return reprocess_wiktionary(wxr, word_cb, capture_cb, dont_parse)


def reprocess_wiktionary(wxr, word_cb, capture_cb, dont_parse):
    """Reprocesses the Wiktionary from the cache file."""
    assert isinstance(wxr, WiktextractContext)
    assert callable(word_cb)
    assert capture_cb is None or callable(capture_cb)
    assert dont_parse in (True, False)

    config_kwargs = wxr.config.to_kwargs()

    # Extract thesaurus data. This iterates over all pages in the cache file,
    # but is very fast.
    thesaurus_data = extract_thesaurus_data(wxr)

    # Then perform the main parsing pass.
    def page_cb(model, title, text):
        return page_handler(wxr, model, title, text, capture_cb, config_kwargs,
                            thesaurus_data, dont_parse)

    emitted = set()
    for ret, stats in wxr.wtp.reprocess(page_cb):
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
    print("Emitting words that only occur in thesaurus")
    sys.stdout.flush()
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
            print("Emitting thesaurus main entry for {}/{}/{} (not in main)"
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
    print("Reprocessing wiktionary complete")
    sys.stdout.flush()


def extract_namespace(wxr, namespace, path):
    """Extracts all pages in the given namespace and writes them to a .tar
    file with the given path."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(namespace, str)
    assert isinstance(path, str)

    print("Extracting pages from namespace {} to tar file {}"
          .format(namespace, path))

    prefix = namespace + ":"
    t = time.time()

    def page_cb(model, title, text):
        if not title.startswith(prefix):
            return None
        text = wxr.wtp.read_by_title(title)
        title = title[len(prefix):]
        title = re.sub(r"(^|/)\.($|/)", r"\1__dotdot__\2", title)
        title = re.sub(r"(^|/)\.\.($|/)", r"\1__dotdot__\2", title)
        title = re.sub(r"//", r"__slashslash__", title)
        title = re.sub(r"^/", r"__slash__", title)
        title = re.sub(r"/$", r"__slash__", title)
        title = namespace + "/" + title
        return (title, text)

    with tarfile.open(path, mode="w", bufsize=16 * 1024 * 1024) as tarf:
        for title, text in wxr.wtp.reprocess(page_cb, autoload=False):
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

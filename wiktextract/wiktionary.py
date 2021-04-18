# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import collections
from wikitextprocessor import Wtp
from .page import parse_page, languages_by_name
from .config import WiktionaryConfig
from .thesaurus import extract_thesaurus_data
from .datautils import data_append

# Title prefixes that indicate that the page is not a normal page and
# should not be used when searching for word forms
special_prefixes = set([
    "Category",
    "Module",
    "Template",
    "Citations",
    "Reconstruction",  # XXX how about this one?
    "Appendix",
    "Rhymes",  # XXX check these out
    "Wiktionary",
    "Thread",
    "Index",
    "Thesaurus",  # XXX some of these might be useful?
    "MediaWiki",
    "Concordance",
    "Sign gloss",  # XXX would I like to capture these too?
    "Help",
    "File",
])

# Title suffixes that indicate that the page should be ignored
ignore_suffixes = [
    "/documentation",
]

# Title suffixes that indicate the page is a translation page
translation_suffixes = [
    "/translations",
]

def capture_specials_fn(dt):
    """Captures certain special pages that are needed for processing other
    pages."""
    # XXX remove this?  Move some of the code to other places?
    assert isinstance(dt, dict)
    title = dt["title"]
    if "redirect" in dt:
        idx = title.find(":")
        if idx > 3:
            cat = title[:idx]
            rest = title[idx + 1:]
            return [["#redirect", title, dt["redirect"]]]
        return []
    text = dt["text"]
    model = dt["model"]
    #print(title)

    if model in ("css", "javascript", "sanitized-css", "json"):
        return []

    if title.endswith("/documentation"):
        return []

    idx = title.find(":")
    if idx > 3:
        cat = title[:idx]
        rest = title[idx + 1:]
        if "redirect" in dt:
            return [[cat, rest, dt["redirect"]]]
        if cat == "Category":
            return [[cat, rest, text]]
        elif cat == "Module":
            if model == "Scribunto":
                return [["Scribunto", rest, text]]
            return [[cat, rest, text]]
        elif cat == "Template":
            return [[cat, rest, text]]
        elif cat == "Citations":
            return []
        elif cat == "Reconstruction":
            # print("Reconstruction", rest)
            return []
        elif cat == "Appendix":
            # print("Appendix", rest)
            return []
        elif cat == "Rhymes":
            return []
        elif cat == "Wiktionary":
            return []
        elif cat == "Thread":
            return []
        elif cat == "Index":
            return []
        elif cat == "Thesaurus":
            if rest.endswith("/translations"):
                return [["Translations", title[:-len("/translations")], text]]
            return [[cat, title, text]]
        elif cat == "MediaWiki":
            return []
        elif cat == "Concordance":
            return []
        elif cat == "Sign gloss":
            return []
        elif cat == "Help":
            return []
        elif cat == "File":
            return []

    if model == "Scribunto":
        print("Unexpected Scribunto:", title)
        return []

    if title.endswith("/translations"):
        return [["Translations", title[:-len("/translations")], text]]

    return []


def page_handler(ctx, model, title, text, capture_cb, config_kwargs,
                 thesaurus_data):
    title = title.strip()
    if capture_cb is not None:
        capture_cb(model, title, text)
    if model == "redirect":
        config1 = WiktionaryConfig()
        ret = [{"title": title, "redirect": text}]
    else:
        if model != "wikitext":
            return None
        idx = title.find(":")
        if idx >= 0:
            prefix = title[:idx]
            if prefix in special_prefixes:
                return None
        for suffix in ignore_suffixes:
            if title.endswith(suffix):
                return None
        for suffix in translation_suffixes:
            if title.endswith(suffix):
                return None # XXX
        # XXX Thesaurus pages?
        # XXX Sign gloss pages?
        # XXX Reconstruction pages?
        config1 = WiktionaryConfig(**config_kwargs)
        config1.thesaurus_data = thesaurus_data
        ret = parse_page(ctx, title, text, config1)
    stats = config1.to_return()
    for k, v in ctx.to_return().items():
        stats[k] = v
    return (ret, stats)


def parse_wiktionary(ctx, path, config, word_cb, capture_cb=None,
                     phase1_only=False):
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls ``capture_cb(title)`` for each raw page (if provided), and
    if it returns True, and calls ``word_cb(data)`` for all words
    defined for languages in ``languages``."""
    assert isinstance(ctx, Wtp)
    assert isinstance(path, str)
    assert isinstance(config, WiktionaryConfig)
    assert callable(word_cb)
    assert capture_cb is None or callable(capture_cb)
    assert phase1_only in (True, False)
    languages = config.capture_languages
    if languages is not None:
        assert isinstance(languages, (list, tuple, set))
        for x in languages:
            assert isinstance(x, str)

    config_kwargs = config.to_kwargs()

    if not ctx.quiet:
        print("First phase - extracting templates, macros, and pages")
        sys.stdout.flush()

    def page_cb(model, title, text):
        return page_handler(ctx, model, title, text, capture_cb, config_kwargs)

    list(ctx.process(path, page_cb, phase1_only=True))
    if phase1_only:
        return []

    # Phase 2 - process the pages using the user-supplied callback
    if not ctx.quiet:
        print("Second phase - processing pages")
        sys.stdout.flush()

    return reprocess_wiktionary(ctx, config, word_cb, capture_cb)


def reprocess_wiktionary(ctx, config, word_cb, capture_cb):
    """Reprocesses the Wiktionary from the cache file."""
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert callable(word_cb)
    assert capture_cb is None or callable(capture_cb)

    config_kwargs = config.to_kwargs()

    # Extract thesaurus data. This iterates over all pages in the cache file,
    # but is very fast.
    thesaurus_data = extract_thesaurus_data(ctx, config)

    # Then perform the main parsing pass.
    def page_cb(model, title, text):
        return page_handler(ctx, model, title, text, capture_cb, config_kwargs,
                            thesaurus_data)

    emitted = set()
    for ret, stats in ctx.reprocess(page_cb):
        config.merge_return(stats)
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
    for (word, lang), linkages in thesaurus_data.items():
        pos_ht = collections.defaultdict(list)
        for x in linkages:
            if x[0] is not None:
                pos_ht[x[0]].append(x)
        for pos, linkages in pos_ht.items():
            if (word, lang, pos) in emitted:
                continue
            if lang not in languages_by_name:
                print("Linkage language {} not recognized".format(lang))
                continue
            lang_code = languages_by_name[lang]["code"]
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
                    data_append(ctx, sense_dt, rel, dt)
                senses.append(sense_dt)
            data = {
                "word": word,
                "lang": lang,
                "lang_code": lang_code,
                "pos": pos,
                "senses": senses,
            }
            word_cb(data)

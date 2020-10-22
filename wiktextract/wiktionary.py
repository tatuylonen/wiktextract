# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
from wikitextprocessor import Wtp
from .wiktlangs import wiktionary_languages
from .page import parse_page
from .config import WiktionaryConfig

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


def parse_wiktionary(path, config, word_cb, capture_cb=None):
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls ``capture_cb(title)`` for each raw page (if provided), and
    if it returns True, and calls ``word_cb(data)`` for all words
    defined for languages in ``languages``."""
    assert isinstance(path, str)
    assert isinstance(config, WiktionaryConfig)
    assert callable(word_cb)
    assert capture_cb is None or callable(capture_cb)
    languages = config.capture_languages
    if languages is not None:
        assert isinstance(languages, (list, tuple, set))
        for x in languages:
            assert isinstance(x, str)
            assert x in wiktionary_languages

    ctx = Wtp()
    config_kwargs = config.to_kwargs()

    def page_handler(model, title, text):
        if capture_cb is not None:
            capture_cb(model, title, text)
        if model == "redirect":
            config1 = WiktionaryConfig()
            return ([{"title": title, "redirect": text}],
                    config1.to_return())
        if model != "wikitext":
            return
        idx = title.find(":")
        if idx >= 0:
            prefix = title[:idx]
            if prefix in special_prefixes:
                return
        for suffix in ignore_suffixes:
            if title.endswith(suffix):
                return
        for suffix in translation_suffixes:
            if title.endswith(suffix):
                return  # XXX
        # XXX translation suffixes?
        # XXX Thesaurus pages?
        # XXX Sign gloss pages?
        # XXX Reconstruction pages?
        config1 = WiktionaryConfig(**config_kwargs)
        ret = parse_page(title, text, config1)
        stats = config1.to_return()
        return (ret, stats)

    results = ctx.process(path, page_handler)
    words = []
    for ret, stats in results:
        config.merge_return(stats)
        words.extend(ret)

    # XXX Merge information from separate translations and thesaurus pages

    for w in words:
        word_cb(w)

    # Return the parsing context.
    return ctx

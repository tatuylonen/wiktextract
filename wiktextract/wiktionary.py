# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.  This file contains code to uncompress the Wiktionary
# dump file and to separate it into individual pages.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import io
import re
import sys
import time
import tarfile
import collections
from wikitextprocessor import Wtp
from .page import parse_page
from .config import WiktionaryConfig
from .thesaurus import extract_thesaurus_data
from .datautils import data_append, languages_by_name

# Title prefixes that indicate that the page is not a normal page and
# should not be used when searching for word forms
special_prefixes = set([
    "Category",
    "Module",
    "Template",
    "Citations",
    "Appendix",
    "Rhymes",  # XXX check these out
    "Wiktionary",
    "Thread",
    "Index",
    "Thesaurus",  # These are handled as a separate pass
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


def page_handler(ctx, model, title, text, capture_cb, config_kwargs,
                 thesaurus_data):
    # Make sure there are no newlines or other strange characters in the
    # title
    title = re.sub(r"[\s\000-\037]+", " ", title)
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

        # XXX Sign gloss pages?
        config1 = WiktionaryConfig(**config_kwargs)
        config1.thesaurus_data = thesaurus_data
        start_t = time.time()
        ret = parse_page(ctx, title, text, config1)
        dur = time.time() - start_t
        if dur > 100:
            print("====== WARNING: PARSING PAGE TOOK {:.1f}s: {}"
                  .format(dur, title))
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
                "source": "thesaurus",
            }
            word_cb(data)
    print("Reprocessing wiktionary complete")
    sys.stdout.flush()


def extract_namespace(ctx, namespace, path):
    """Extracts all pages in the given namespace and writes them to a .tar
    file with the given path."""
    assert isinstance(ctx, Wtp)
    assert isinstance(namespace, str)
    assert isinstance(path, str)

    print("Extracting pages from namespace {} to tar file {}"
          .format(namespace, path))

    prefix = namespace + ":"
    t = time.time()

    def page_cb(model, title, text):
        if not title.startswith(prefix):
            return None
        text = ctx.read_by_title(title)
        title = title[len(prefix):]
        title = re.sub(r"(^|/)\.($|/)", r"\1__dotdot__\2", title)
        title = re.sub(r"(^|/)\.\.($|/)", r"\1__dotdot__\2", title)
        title = re.sub(r"//", r"__slashslash__", title)
        title = re.sub(r"^/", r"__slash__", title)
        title = re.sub(r"/$", r"__slash__", title)
        title = namespace + "/" + title
        return (title, text)

    with tarfile.open(path, mode="w", bufsize=16 * 1024 * 1024) as tarf:
        for title, text in ctx.reprocess(page_cb, autoload=False):
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

# Extracting information from thesaurus pages in Wiktionary.  The data will be
# merged into word linkages in later stages.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import time
import collections
from wikitextprocessor import Wtp, NodeKind, WikiNode
from .parts_of_speech import part_of_speech_map
from .page import (linkage_map, linkage_inverses, clean_node,
                   LEVEL_KINDS)
from .form_descriptions import parse_sense_qualifier
from .config import WiktionaryConfig
from .datautils import languages_by_name, languages_by_code

ignored_subtitle_tags_map = {
    "by reason": [],
    "by period of time": [],
    "by degree": [],
    "by type": [],
    "other": [],
    "opaque slang terms": ["slang"],
    "slang": ["slang"],
    "colloquial, archaic, slang": ["colloquial", "archaic", "slang"],
    "euphemisms": ["euphemism"],
    "colloquialisms": ["colloquial"],
    "colloquialisms or slang": ["colloquial"],
    "technical terms misused": ["colloquial"],
    "people": [],
    "proper names": ["proper-noun"],
    "race-based (warning- offensive)": ["offensive"],
    "substance addicts": [],
    "non-substance addicts": [],
    "echoing sounds": [],
    "movement sounds": [],
    "impacting sounds": [],
    "destructive sounds": [],
    "noisy sounds": [],
    "vocal sounds": [],
    "miscellaneous sounds": [],
    "age and gender": [],
    "breeds and types": [],
    "by function": [],
    "wild horses": [],
    "body parts": [],
    "colors, patterns and markings": [],
    "diseases": [],
    "equipment and gear": [],
    "groups": [],
    "horse-drawn vehicles": [],
    "places": [],
    "sports": [],
    "sounds and behavior": [],
    "obscure derivations": [],
    "plants": [],
    "animals": [],
    "common": [],
    "rare": ["rare"],
}

def contains_list(contents):
    """Returns True if there is a list somewhere nested in contents."""
    if isinstance(contents, (list, tuple)):
        return any(contains_list(x) for x in contents)
    if not isinstance(contents, WikiNode):
        return False
    kind = contents.kind
    if kind == NodeKind.LIST:
        return True
    return contains_list(contents.children) or contains_list(contents.args)

def extract_thesaurus_data(ctx, config):
    """Extracts linkages from the thesaurus pages in Wiktionary."""
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    start_t = time.time()
    if not ctx.quiet:
        print("Extracting thesaurus data")

    def page_handler(model, title, text):
        if not title.startswith("Thesaurus:"):
            return None
        if title.startswith("Thesaurus:Requested entries "):
            return None
        if title.find("/") >= 0:
            #print("STRANGE TITLE:", title)
            return None
        text = ctx.read_by_title(title)
        word = title[10:]
        idx = word.find(":")
        if idx > 0 and idx < 5:
            word = word[idx + 1:]  # Remove language prefix
        expanded = ctx.expand(text, templates_to_expand=None)  # Expand all
        expanded = re.sub(r'(?s)<span class="tr Latn"[^>]*>(<b>)?(.*?)(</b>)?'
                          r'</span>',
                          r"XLITS\2XLITE", expanded)
        tree = ctx.parse(expanded, pre_expand=False)
        assert tree.kind == NodeKind.ROOT
        lang = None
        pos = None
        sense = None
        linkage = None
        subtitle_tags = ()
        ret = []
        # Some pages don't have a language subtitle, but use
        # {{ws header|lang=xx}}
        m = re.search(r'(?s)\{\{ws header\|[^}]*lang=([^}|]*)', text)
        if m:
            lang = languages_by_code.get(m.group(1), {}).get("name")

        def recurse(contents):
            nonlocal lang
            nonlocal pos
            nonlocal sense
            nonlocal linkage
            nonlocal subtitle_tags
            item_sense = None
            tags = None
            topics = None

            if isinstance(contents, (list, tuple)):
                for x in contents:
                    recurse(x)
                return
            if not isinstance(contents, WikiNode):
                return
            kind = contents.kind
            if kind == NodeKind.LIST and not contains_list(contents.children):
                if lang is None:
                    print(title, lang, "UNEXPECTED LIST WITHOUT LANG:",
                          contents)
                    return
                for node in contents.children:
                    if node.kind != NodeKind.LIST_ITEM:
                        continue
                    w = clean_node(config, ctx, None, node.children)
                    if w.find("*") >= 0:
                        print(title, lang, pos, "STAR IN WORD:", w)
                    # Check for parenthesized sense at the beginning
                    m = re.match(r"(?s)^\(([^)]*)\):\s*(.*)$", w)
                    if m:
                        item_sense, w = m.groups()
                        # XXX check for item_sense being part-of-speech
                    else:
                        item_sense = sense

                    # Remove thesaurus links, if any
                    w = re.sub(r"\s*\[W[Ss]\]", "", w)

                    # Check for English translation in quotes.  This can be
                    # literal translation, not necessarily the real meaning.
                    english = None

                    def engl_fn(m):
                        nonlocal english
                        english = m.group(1)
                        return ""

                    w = re.sub(r'(\bliterally\s*)?(, )?“([^"]*)"\s*',
                               engl_fn, w)

                    # Check for qualifiers in parentheses
                    tags = []
                    topics = []

                    def qual_fn(m):
                        q = m.group(1)
                        if q == item_sense:
                            return ""
                        if q.find("XLITS") >= 0:
                            return q
                        dt = {}
                        parse_sense_qualifier(ctx, q, dt)
                        tags.extend(dt.get("tags", ()))
                        topics.extend(dt.get("topics", ()))
                        return ""

                    w = re.sub(r"\(([^)]*)\)$", qual_fn, w).strip()

                    # XXX there could be a transliteration, e.g.
                    # Thesaurus:老百姓

                    # XXX Apparently there can also be alternative spellings,
                    # such as 眾人／众人 on Thesaurus:老百姓

                    # If the word is now empty or separator, skip
                    if not w or w.startswith("---") or w == "\u2014":
                        return
                    rel = linkage or "synonyms"
                    for w1 in w.split(","):
                        m = re.match(r"(?s)(.*?)\s*XLITS(.*?)XLITE\s*", w1)
                        if m:
                            w1, xlit = m.groups()
                        else:
                            xlit = None
                        w1 = w1.strip()
                        if w1.startswith("Thesaurus:"):
                            w1 = w1[10:]
                        if w1:
                            ret.append((lang, pos, rel, w1, item_sense,
                                        xlit, tags, topics, title))
                return
            if kind not in LEVEL_KINDS:
                recurse(contents.args)
                recurse(contents.children)
                return
            subtitle = ctx.node_to_text(contents.args)
            if subtitle in languages_by_name:
                lang = subtitle
                pos = None
                sense = None
                linkage = None
                recurse(contents.children)
                return
            if subtitle.startswith("Sense: ") or subtitle.startswith("sense: "):
                sense = subtitle[7:]
                linkage = None
                recurse(contents.children)
                return
            subtitle = subtitle.lower()
            if subtitle in ("further reading", "external links",
                            "references", "translations", "notes", "usage",
                            "work to be done", "quantification",
                            "abbreviation", "symbol"):
                return
            if subtitle in linkage_map:
                linkage = linkage_map[subtitle]
                recurse(contents.children)
                return
            if subtitle in part_of_speech_map:
                pos = part_of_speech_map[subtitle]["pos"]
                sense = None
                linkage = None
                recurse(contents.children)
                return
            if subtitle in ignored_subtitle_tags_map:
                # These subtitles are ignored but children are processed and
                # possibly given additional tags
                subtitle_tags = ignored_subtitle_tags_map[subtitle]
                recurse(contents.children)
                subtitle_tags = ()
                return
            print(title, lang, pos, sense, "UNHANDLED SUBTITLE:", subtitle)
            print(contents.args)
            recurse(contents.children)
            return None

        recurse(tree)
        return [word, ret]

    ret = collections.defaultdict(list)
    num_pages = 0
    for word, linkages in ctx.reprocess(page_handler, autoload=False):
        assert isinstance(linkages, (list, tuple))
        num_pages += 1
        for lang, pos, rel, w, sense, xlit, tags, topics, title in linkages:
            # Add the forward direction
            v = (pos, rel, w, sense, xlit, tuple(tags), tuple(topics), title)
            key = (word, lang)
            ret[key].append(v)
            if False:  # XXX don't add reverse releations here, disambig first
                # Add inverse linkages where applicable
                inv_rel = linkage_inverses.get(rel)
                if inv_rel is not None:
                    if rel in ("derived", "related"):
                        inv_pos = None
                    else:
                        inv_pos = pos
                    inv_v = (inv_pos, inv_rel, word, sense, None, (), (), title)
                    key = (w, lang)
                    ret[key].append(inv_v)

    total = sum(len(x) for x in ret.values())
    if not ctx.quiet:
        print("Extracted {} linkages from {} thesaurus pages "
              "(took {:.1f}s)"
              .format(total, num_pages, time.time() - start_t))
    return ret

# Tests/experiments related to WikiText parsing and Lua extension invocation
#
# Third iteration
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import os
import re
import sys
import json
import collections
from wikitextprocessor import Wtp, NodeKind, ALL_LANGUAGES

LANGUAGE_NAMES = set(x.get("name") for x in ALL_LANGUAGES)

path = "data/enwiktionary-20200920-pages-articles.xml.bz2"

ignore_prefixes = set([
    "Appendix",
    "Category",
    "Citations",
    "Concordance",
    "File",
    "Help",
    "Image",
    "Index",
    "Media",
    "MediaWiki",
    "Module",
    "Project",
    "Reconstruction",
    "Rhymes",
    "Sign gloss",
    "Summary",
    "Talk",
    "Template",
    "Thesaurus",
    "Thread",
    "User",
    "Wiktionary",
])

def page_handler(model, title, text):
    if model != "wikitext":
        return None

    # Skip pages with certain prefixes
    ofs = title.find(":")
    if ofs >= 0:
        prefix = title[:ofs]
        if prefix in ignore_prefixes:
            return None

    # XXX testing bugs
    # if title != "soil":
    #     return None
    # expanded = ctx.expand(text, pre_only=True)
    # print(expanded)
    # sys.stdout.flush()
    # return None

    print("Processing {}".format(title))
    sys.stdout.flush()

    # Test fully expanding the page (all templates)
    expanded = ctx.expand(text)
    m = re.search(r"\{\{+[^}]*\}\}+", expanded)
    if m:
        print("{}: BRACES REMAIN: {}".format(title, m.group(0)))

    # Parse the template
    tree = ctx.parse(text, pre_expand=True)
    #if ctx.errors:
    #    for e in ctx.errors:
    #        print("{}: {}".format(title, e))
    #    for e in ctx.warnings:
    #        print("{}: WARNING: {}".format(title, e))
    titles = []
    for node in tree.children:
        if isinstance(node, str):
            continue
        if node.kind not in (NodeKind.LEVEL2, NodeKind.LEVEL3,
                             NodeKind.LEVEL4, NodeKind.LEVEL5,
                             NodeKind.LEVEL6):
            continue
        if (len(node.args) != 1 or len(node.args[0]) != 1 or
            not isinstance(node.args[0][0], str)):
            print("  {} - {}: {}".format(title, node.kind, node.children))
            continue
        t = node.args[0][0]
        assert isinstance(t, str)
        print("  {} - {}".format(title, t))
        titles.append(t)
    sys.stdout.flush()
    return title, titles, ctx.errors

ctx = Wtp()
ret = ctx.process(path, page_handler)
counts = collections.defaultdict(int)
titles_ht = collections.defaultdict(list)
for page_title, titles, errors in ret:
    for title in titles:
        titles_ht[title].append(page_title)
    for err in errors:
        msg = err["msg"]
        counts[msg] += 1

print("=== MOST COMMON ERRORS")
errors = list(sorted(counts.items(), key=lambda x: x[1], reverse=True))
for err, cnt in errors[:40]:
    print(cnt, err)

print("=== Saving non-language titles in temp-nonlangs.json")
non_lang_titles = list(x for x in titles_ht if x[0] not in LANGUAGE_NAMES)
with open("temp-nonlangs.json", "w") as f:
    json.dump(non_lang_titles, f)

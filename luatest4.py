# Tests/experiments related to WikiText parsing and Lua extension invocation
#
# Third iteration
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import os
import re
import sys
import collections
from wikitextprocessor import Wtp

path = "data/enwiktionary-20200920-pages-articles.xml.bz2"

def page_handler(model, title, text):
    if model != "wikitext":
        return None
    print("Processing {}".format(title))
    expanded = ctx.expand(text)
    m = re.search(r"\{\{+[^}]*\}\}+", expanded)
    if m:
        print("{}: BRACES REMAIN: {}".format(title, m.group(0)))

    tree = ctx.parse(text, pre_expand=True)
    #if ctx.errors:
    #    for e in ctx.errors:
    #        print("{}: {}".format(title, e))
    #    for e in ctx.warnings:
    #        print("{}: WARNING: {}".format(title, e))
    sys.stdout.flush()
    return ctx.errors

ctx = Wtp()
ret = ctx.process(path, page_handler)
counts = collections.defaultdict(int)
for lst in ret:
    for err in lst:
        msg = err["msg"]
        counts[msg] += 1

print("=== MOST COMMON ERRORS")
errors = list(sorted(counts.items(), key=lambda x: x[1], reverse=True))
for err, cnt in errors[:20]:
    print(cnt, err)

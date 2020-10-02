# Tests/experiments related to WikiText parsing and Lua extension invocation
#
# Third iteration
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import os
import re
import sys
import json
import os.path
from wiktextract import wikitext
from wiktextract import ExpandCtx, phase1_to_ctx, start_page, expand_wikitext

print("Loading specials (templates & modules)")
with open("tempXXXspecials.json") as f:
    specials = json.load(f)

print("Analyzing templates", len(specials))
expand_ctx = phase1_to_ctx(specials)
print("Processing test page")

# page = open("tests/animal.txt").read()
# page_title = "animal"
# page = wikitext.preprocess_text(page)

# # Sanity check that expanding all works
# ret = expand_wikitext(expand_ctx, page_title, page)
# if ret.find("{{") >= 0:
#     print("{}: HAVE {{{{".format(page_title))


def process_file(path):
    if not path.endswith(".txt"):
        return
    print("Processing {}".format(path))
    page = open(path).read()
    m = re.match(r"(?s)^TITLE: ([^\n]*)\n", page)
    if m:
        title = m.group(1)
        page = page[m.end():]
    else:
        title = os.path.basename(path)[:-4]

    start_page(expand_ctx, title, page)
    text = wikitext.preprocess_text(page)
    ret = expand_wikitext(expand_ctx, text)
    if ret.find("{{") >= 0:
        print("{}: HAVE {{{{".format(title))

    text = expand_wikitext(expand_ctx, text,
                           templates_to_expand=expand_ctx.need_pre_expand)
    tree, parse_ctx = wikitext.parse_with_ctx(title, text, no_preprocess=True)
    if parse_ctx.errors:
        print("{}: HAD PARSE ERRORS".format(path))
        for e in parse_ctx.errors:
            print(e)

def recurse(path):
    if os.path.isfile(path):
        process_file(path)
        return
    for fn in os.listdir(path):
        if fn in (".", ".."):
            continue
        recurse(path + "/" + fn)

recurse("pages/Words")

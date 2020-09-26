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
from wiktextract import ExpandCtx, phase1_to_ctx, expand_wikitext

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
    title = os.path.basename(path)[:-4]
    text = wikitext.preprocess_text(page)
    ret = expand_wikitext(expand_ctx, title, text)
    if ret.find("{{") >= 0:
        print("{}: HAVE {{{{".format(title))

    text = expand_wikitext(expand_ctx, title, text,
                           templates_to_expand=expand_ctx.need_pre_expand,
                           fullpage=page)
    tree, parse_ctx = wikitext.parse_with_ctx(title, text, no_preprocess=True)
    if parse_ctx.errors:
        print("{}: HAD PARSE ERRORS".format(path))

def recurse(path):
    if os.path.isfile(path):
        process_file(path)
        return
    for fn in os.listdir(path):
        if fn in (".", ".."):
            continue
        recurse(path + "/" + fn)

recurse("pages/Words")

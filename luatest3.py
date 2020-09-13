# Tests/experiments related to WikiText parsing and Lua extension invocation
#
# Third iteration
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import json
from wiktextract import wikitext
from wiktextract import ExpandCtx, phase1_to_ctx, expand_wikitext

print("Loading specials (templates & modules)")
with open("tempXXXspecials.json") as f:
    specials = json.load(f)

print("Analyzing templates", len(specials))
ctx = phase1_to_ctx(specials)
print("Processing test page")

page = open("tests/animal.txt").read()
page_title = "animal"
page = wikitext.preprocess_text(page)

ret = expand_wikitext(ctx, page_title, page)

print("Expanded:", ret)

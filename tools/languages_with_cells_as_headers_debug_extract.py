#!/usr/bin/env python3
#
# This script extracts debug messages related to
# LANGUAGES_WITH_CELLS_AS_HEADERS, which is a dictionary of
# languages with lists of table cell text that should not be
# ignored by certain heuristics in inflection.py.
# Download error message data from https://kaikki.org/dictionary/rawdata.html
# and put the wiktextract-error-data.json in the same directory as this
# script. The output is printed into stdout as a python syntax dict,
# which can be copy-pasted and pruned to get a good LWCAH whitelist.
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import json
from collections import defaultdict

messages = defaultdict(dict)

ISNOTIN = " is not in LANGUAGES_WITH_CELLS_AS_HEADERS; cleaned text: "
STYLE = ", style: "

with open("wiktextract-error-data.json") as f:
    # ~ print("Loading file into json...")
    dt = json.load(f)
    # ~ print(".get(\"debugs\")")
    dt = dt.get("debugs")
    # ~ print("iterating...")
    for entry in dt:
        msg = entry.get("msg")
        # ~ if (msg.startswith("suspicious heuristic header") or
           # ~ msg.startswith("expected heuristic header")):
        if msg.startswith("table cell identified as header"):
            isnotinindex = msg.find(ISNOTIN)
            styleindex = msg.find(STYLE)

            language = entry.get("section")
            if styleindex > -1:
                cleaned = msg[isnotinindex + len(ISNOTIN): styleindex]
            else:
                cleaned = msg[isnotinindex + len(ISNOTIN):]
            nmsg = "{}: {}".format(language, cleaned)
            ok = messages[language].get(cleaned)
            if ok and ok["count"] < 10 and ok["count"] % 3 == 0:
                messages[language][cleaned]["count"] += 1
                messages[language][cleaned]["title"] += "; " + entry.get("title")
            elif ok:
                messages[language][cleaned]["count"] += 1
            else:
                messages[language][cleaned] = { "count": 1, "title": entry.get("title")}
                

print("LANGUAGES_WITH_CELLS_AS_HEADERS = {")

for lang, dd in messages.items():
    print('    "{}": ['.format(lang))
    for cleaned, vals in sorted(dd.items(), key=lambda dd: dd[1]["count"], reverse=True):
        clquotes = cleaned.replace('"', '\\"')
        print('        "{}",  # {}, in "{}"'.format(clquotes, int(vals["count"] / 3), vals["title"]))
    print('    ],')

print("}")

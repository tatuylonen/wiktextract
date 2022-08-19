#!/usr/bin/env python3
#
# This script extracts debug messages related to
# LANGUAGES_WITH_CELLS_AS_HEADERS, which is a dictionary of
# languages with lists of table cell texts that should not be
# ignored by certain heuristics in inflection.py.
# Download error message data from https://kaikki.org/dictionary/rawdata.html
# and put the wiktextract-error-data.json in the same directory as this
# script. The output is printed into stdout as the content of
# table_headers_heuristics_data.py,  which can be copy-pasted and pruned to get
# a good LWCAH whitelist.
# The script automatically comments out lines that are received from rejected
# debug messages, and also comments out the whole language block if all of the
# cell texts have previously been rejected. Because of this, you can trust
# uncommented lines to contain no new data (except on Wiktionary's side), and
# you have to scan commented lines to see, if anything has appeared and then
# been rejected by default.
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import json
from collections import defaultdict

messages = defaultdict(dict)

ISNOTIN = "; cleaned text: "
STYLE = ", style: "

with open("wiktextract-error-data.json") as f:
    # ~ print("Loading file into json...")
    dt = json.load(f)
    # ~ print(".get(\"debugs\")")
    dt = dt.get("debugs")
    # ~ print("iterating...")
    for entry in dt:
        msg = entry.get("msg")
        rejected = msg.startswith("rejected heuristic header")
        accepted = msg.startswith("accepted heuristic header")
        if (accepted or rejected):
            isnotinindex = msg.find(ISNOTIN)
            styleindex = msg.find(STYLE)

            language = entry.get("section")
            if styleindex > -1:
                cleaned = msg[isnotinindex + len(ISNOTIN): styleindex]
            else:
                cleaned = msg[isnotinindex + len(ISNOTIN):]
            ok = messages[language].get(cleaned)
            if ok and ok["count"] < 10:
                messages[language][cleaned]["count"] += 1
                messages[language][cleaned]["title"] += "; " + entry.get("title")
            elif ok:
                messages[language][cleaned]["count"] += 1
            else:
                messages[language][cleaned] = { "count": 1,
                                                "title": entry.get("title"),
                                                "accepted": accepted,
                                                }
                

print(
"""# Data for heuristically determinining whether a table cell should actually
# be parsed as a table header instead.
#
# The base for this dict is first generated from debug message data with
# tools/languages_with_cells_as_headers_debug_extract.py, which is then pruned.
# Pruning basically involves looking at each line and determining whether
# it is actually a systematic header (in a table cell), or just a fluke.
# For example Romanian "superlative" is a fluke, because it is only
# found in Romanian in the article "superlativ"; the heuristic made the cells in
# the table with it a candidate header (candidate_hdr = True in inflection.py)
# because expand_hdr() did not return any error tags: it *looked* like a
# header, because "superlative" is used in headers.
#
# When pruning, delete obvious cases that do not need thinking about
# (for example all Egyptian entries); if there are any that *could* be,
# and need repetitive checking each time this file is regenerated and repruned,
# put the line in a comment for future pruners.
#
# Commented entry => rejected
# Deleted => rejected
# Uncommented => accepted
# If all entries in a language are commented, comment the whole language to
# prevent possible future false positives.
#
# When languages_with_cells_as_headers_debug_extract.py is used to regenerate
# this script, everything that is new or rejected will be commented (and
# rejected) unless explicitly uncommented.
#
# Copyright (c) 2021, 2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

""")
print("LANGUAGES_WITH_CELLS_AS_HEADERS = {")

for lang, dd in sorted(messages.items()):
    some_accepted = any([acc == True for acc in [dd[cl]["accepted"] for cl in dd]])
    if some_accepted:
        print('    "{}": ['.format(lang))
    else:
        print('    # "{}": ['.format(lang))
    for cleaned, vals in sorted(dd.items(),
                                # short by count first (padded), then by
                                # cleaned (= x[0] < x-tuple from dd.items())
                                key=lambda x:
                                "{:010d}{}".format(
                                        x[1]["count"],
                                        x[0],
                                        ),
                                reverse=True):
        clquotes = cleaned.replace('"', '\\"')
        print('        {}"{}",  # {} in "{}"'
                .format(("# ", "")[vals["accepted"]],
                        clquotes,
                        vals["count"],
                        vals["title"]))
    if some_accepted:
        print('    ],')
    else:
        print('    # ],')

print("}")

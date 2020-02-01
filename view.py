# XXX temporary tool for viewing contents of database dumps

import sys
import json

#with open("temp.tmp") as f:
for line in sys.stdin:
    data = json.loads(line)
    word = data["word"]
    if "lang" not in data:
        continue
    senses = data.get("senses", [])
    if not senses:
        print("{:<15s} {}".format(word, "NO SENSES"))
        continue
    for sense in senses:
        for gloss in (sense.get("glosses", [""]) or [""]):
            print("{:<15s} {}".format(word, gloss))

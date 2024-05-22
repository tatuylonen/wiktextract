# Compare two wiktextract output files to each other to find differences
# SLOW AND USES TONS OF MEMORY

import json
from jsondiff import diff
from collections import defaultdict
from sys import argv

if len(argv) != 3:
    print("Need two arguments: file1 and file2")

file1, file2 = argv[1], argv[2]

words1: dict[str, list] = defaultdict(list)
counter1: dict[str, int] = defaultdict(int)
words2: dict[str, list] = defaultdict(list)

for file, words in ((file1, words1), (file2, words2)):
    with open(file, "r") as f:
        for line in f.readlines():
            data = json.loads(line)
            if "title" in data:
                continue
            if "word" not in data:
                # print("'word' not in {data=}")
                word = "MISSINGWORD"
            else:
                word = data["word"]
            if "pos" not in data:
                # print("'pos missing from {data=}")
                pos = "MISSINGPOS"
            else:
                pos = data["pos"]
            if "lang" not in data and "lang_code" not in data:
                # print("neither 'lang' nor 'lang_code' in {data=}")
                lang = "MISSINGLANG"
            else:
                lang = data.get("lang", None) or data.get("lang_code", None)
            # words1[lang].append(pos+word)
            # counter1[f"{lang}:{word}:{pos}"] += 1
            words[f"{lang}:{word}:{pos}"].append(data)
            # if counter1[f"{lang}:{word}:{pos}"] > 1:
            #     print(f"More than one: {lang}:{word}:{pos}")
            #     print(data)
            #     print("------")

i = 0
for k, datas1 in words1.items():
    if i > 100_000:
        break
    i += 1
    if k not in words2:
        print(f"====== {k=} not found in words2!")
        continue
    datas2 = words2[k]
    if len(datas1) != len(datas2):
        print(f"======= Len mismatch with {k=}")
        continue
    for x, y in zip(datas1, datas2):
        d = diff(x, y, syntax="symmetric")
        if "senses" in d.keys() and len(d) == 1:
        # kludge to handle a 'bug' with a quotation template: if a day is not
        # specified, we apparently add a day number after the month based on
        # the current date.
            cur = next(iter(d["senses"].values()))
            if cur and "examples" in cur.keys():
                ref = next(iter(cur["examples"].values()))
                if "ref" in ref:
                    continue
        # print(f"jsondiff: {d=}")
        if d:
            print("==================")
            print(d, " ->")
            print("-----")
            print(x)
            print("------")
            print(y)

# for i, (k, v) in enumerate(words1.items()):
#     if i > 1000:
#         break
#     print(f"{k}:  {v}")
print("Finished")

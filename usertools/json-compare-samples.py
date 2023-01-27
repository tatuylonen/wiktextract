#!/usr/bin/env python3
#
# Compare random samples between two Wiktextract JSON files.
# The script first loads into memory one of the files, and then
# goes through the other file, randomly picking a line every
# now and then based on the --one-in-a=[int] parameter.
# The line is decoded, then the equivalent object is
# searched for in the first file; the two lines are compared,
# and if they differ we read in the json for both, express
# them as human-readable json and compare those using difflib.
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import json
import difflib
import random
import argparse
from collections import defaultdict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare random samples in two json files")
    parser.add_argument("filea", type=str, nargs="?", default=None,
                        help="First input file")
    parser.add_argument("fileb", type=str, nargs="?", default=None,
                        help="Second input file")
    parser.add_argument("--one-in-a", type=int, default=10000,
                        help="Ratio 1/N of words to sample, "
                              "defaults to 1/10000")
    args = parser.parse_args()

file_a = args.filea
file_b = args.fileb
one_in_a = args.one_in_a
first_index = dict()


with open(file_a, "rb", buffering=16*1024*1024) as f:
    jsonf = f.read()
    fpos = 0
    line = "!!!!init!!!!"
    count = 0
    while line != "":
        if count % 10000 == 0:
            print(count, "...")
        count += 1
        i = jsonf.find(b"\n", fpos)
        if i != -1:
            line = jsonf[fpos:i+1]
        else:
            line = jsonf[fpos:]
            i = len(jsonf)
        if line == b'':
            break
        
        word = json.loads(line)
        if (not word.get("word", "") or
            word.get("pos", "") == "character"):
            fpos = i + 1
            continue

        sort_key = "{}/{}/{}/{}".format(
                            word.get("lang_code", ""),  # language
                            word.get("word", ""),  # word
                            word.get("pos", ""),  # PoS
                            word.get("etymology_number", ""), 
                            )
        num = ""
        if sort_key in first_index:
            # print(f"sort_key collision: {sort_key}")
            num = 1
            while sort_key + str(num) in first_index:
                # print(f"sort_key + num collision: {sort_key}, {num}")
                num += 1
            # first_index is an index of each entry, pointing
            # to the position of that entry in the json data
        first_index[sort_key + str(num)] = (fpos, i + 1)
        fpos = i + 1
        
        
    with open(file_b, "rb") as cf:
        compf = cf.read()
        fpos = 0
        line = "!!!!!!!init!!!!!!"
        while line != "":
            i = compf.find(b"}\n", fpos)
            r = random.randrange(one_in_a)
            # print(r)
            if r != 0:
                if i == -1:
                    break
                fpos = i + 1
                
                continue
            if i != -1:
                line = compf[fpos:i+1]
            else:
                line = compf[fpos:]
                i = len(compf)
            if line == b'':
                break

            word = json.loads(line)
            if (not word.get("word", "") or
                word.get("pos", "") == "character"):
                fpos = i + 1
                continue
            sort_key = "{}/{}/{}/{}".format(
                            word.get("lang_code", ""),  # language
                            word.get("word", ""),  # word
                            word.get("pos", ""),  # PoS
                            word.get("etymology_number", ""), 
                            )
            # print(f"Sample: {sort_key}")
            if sort_key in first_index:
                a, b = first_index[sort_key]
                old_line = jsonf[a : b]
                if old_line == line:
                    fpos = i + 1
                    continue
                compstr = json.dumps(word,
                                       sort_keys=True,
                                       indent=1,
                                       ensure_ascii=False)
                compjson = [l for l in compstr.splitlines()]
                baseword = json.loads(old_line)
                basestr = json.dumps(baseword,
                                       sort_keys=True,
                                       indent=1,
                                       ensure_ascii=False)
                basejson = [l for l in basestr.splitlines()]

                diffs = "\n".join(x for x in difflib.context_diff(basejson, compjson,
                                            fromfile=sort_key) if x)
                if diffs:
                    print("==========================")
                    print(diffs)
            else:
                print("Not in first_index")

            fpos = i + 1

            

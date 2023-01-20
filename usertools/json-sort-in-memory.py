#!/usr/bin/env python3
#
# Sort a file with Wiktextract JSON objects on each line into a
# new output file.
# Because Wiktextract processes data with multiprocessing, the output
# of that data is in unreliable order, and the contents of two runs of
# Wiktextract will probably not be identical because the lines are shuffled.
# This script takes a file and then sorts it, outputting it into a new
# file.
# This version of the script loads the json data wholly into memory.
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import os
import json
import sys
from collections import defaultdict

if len(sys.argv) > 1:
    json_data = sys.argv[1]
else:
    print("python json-sort.py json_data_file [sorted_output_file]")
    quit()
if len(sys.argv) > 2:
    output_file = sys.argv[2]
else:
    output_file = json_data + ".sort"

to_be_sorted = dict()

with open(json_data, "rb", buffering=16*1024*1024) as f:
    count = 0
    jsonf = f.read()
    fpos = 0
    line = "init"
    while line != "":
        i = jsonf.find(b"\n", fpos)
        if i != -1:
            line = jsonf[fpos:i+1]
        else:
            line = jsonf[fpos:]
            i = len(jsonf)
        if line == b'':
            break
        
        word = json.loads(line)

        sort_key = "{}{}{}".format(
                            word.get("lang_code", ""),  # language
                            word.get("word", ""),  # word
                            word.get("pos", ""),  # PoS
                            )
        num = 1
        while sort_key + str(num) in to_be_sorted:
            num += 1
        # to_be_sorted is an index of each entry, pointing
        # to the position of that entry in the json data
        to_be_sorted[sort_key + str(num)] = (fpos, i + 1)
        fpos = i + 1
        
        count += 1
        if count % 10000 == 0: # if you only need a sample
            print(f"... {count}")

    # make a sorted list of (sort_key, file_position) tuples
    has_been_sorted = [x[1] for x in sorted(to_be_sorted.items())]
    
    with open(output_file, "w") as output:
        # iterate through the sorted list of tuples and
        # then slice the word data from the full data,
        # writing it into the output file
        for fpos, end in has_been_sorted:
            word = json.loads(jsonf[fpos:end])
            output.write(json.dumps(word, sort_keys=True,
                             ensure_ascii=False))
            output.write("\n")


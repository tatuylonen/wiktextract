#!/usr/bin/env python3
#
# Search for a word or a word that fulfils a regex in
# Wiktexctract json objects.
# Copyright (c) 20

import re
import json
import argparse
from collections import defaultdict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get word data from Wiktextract json")
    parser.add_argument("path", type=str, nargs="?", default=None,
                        help="Input file")
    parser.add_argument("word", type=str, nargs="?", default=None,
                        help="Word (or regex) to be searched")
    parser.add_argument("--regex", action="store_true", default=False,
                        help="Use regex in the word filter. "
                            "We use re.match() which will match if "
                            "the start of the string matches; "
                            "use $ to indicate end of string explicitly")
    parser.add_argument("--language", type=str, action="append", default=[],
                        help="Accepted language(s)")
    parser.add_argument("--max", type=int, default=None,
                        help="Stop when reaching this number of found entries")
    args = parser.parse_args()

if args.regex:
    word_re = re.compile(args.word)
else:
    word_re = None

with open(args.path, buffering=16*1024*1024) as jsonf:
    count = 0
    # some good old-fashioned premature optimization,
    # might be completely unnecessary. But it seems
    # like such a waste to check the configuration
    # variables each time inside the loop, and just
    # premaking some variations of the loop is simple
    # enough for a small job like this.
    if not word_re and args.language and args.max:
        for line in jsonf:
            word = json.loads(line)
            if (word.get("word", "") == args.word and
                word.get("lang", "") in args.language):
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))
                count += 1
            if args.max and count >= args.max:
                break
    elif not word_re and not args.language and args.max:
        for line in jsonf:
            word = json.loads(line)
            if word.get("word", "") == args.word:
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))
                count += 1
            if args.max and count >= args.max:
                break
    elif not word_re and args.language and not args.max:
        for line in jsonf:
            word = json.loads(line)
            if (word.get("word", "") == args.word and
                word.get("lang", "") in args.language):
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))
    elif not word_re and not args.language and not args.max:
        for line in jsonf:
            word = json.loads(line)
            if word.get("word", "") == args.word:
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))
    elif word_re and args.language and args.max:
        for line in jsonf:
            word = json.loads(line)
            if (re.match(word_re, word.get("word", "")) and
                word.get("lang", "") in args.language):
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))
                count += 1
            if args.max and count >= args.max:
                break
    elif word_re and not args.language and args.max:
        for line in jsonf:
            word = json.loads(line)
            if re.match(word_re, word.get("word", "")):
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))
                count += 1
            if args.max and count >= args.max:
                break
    elif word_re and args.language and not args.max:
        for line in jsonf:
            word = json.loads(line)
            if (re.match(word_re, word.get("word", "")) and
                word.get("lang", "") in args.language):
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))
    elif word_re and not args.language and not args.max:
        for line in jsonf:
            word = json.loads(line)
            if re.match(word_re, word.get("word", "")):
                print(json.dumps(word, sort_keys=True,
                                 ensure_ascii=False))

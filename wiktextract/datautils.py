# Utilities for manipulating word data structures
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import functools
import collections
from wikitextprocessor import Wtp

# Keys in ``data`` that can only have string values (a list of them)
str_keys = ("tags", "glosses")
# Keys in ``data`` that can only have dict values (a list of them)
dict_keys = set(["pronunciations", "senses", "synonyms", "related",
                 "antonyms", "hypernyms", "holonyms", "forms"])


def data_append(ctx, data, key, value):
    """Appends ``value`` under ``key`` in the dictionary ``data``.  The key
    is created if it does not exist."""
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(key, str)

    if key in str_keys:
        assert isinstance(value, str)
    elif key in dict_keys:
        assert isinstance(value, dict)
    if key == "tags":
        if value == "":
            return
    lst = data.get(key)
    if lst is None:
        lst = []
        data[key] = lst
    lst.append(value)


def data_extend(ctx, data, key, values):
    """Appends all values in a list under ``key`` in the dictionary ``data``."""
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(key, str)
    assert isinstance(values, (list, tuple))

    # Note: we copy values, just in case it would actually be the same as
    # data[key].  This has happened, and leads to iterating for ever, running
    # out of memory.  Other ways of avoiding the sharing may be more
    # complex.
    for x in tuple(values):
        data_append(ctx, data, key, x)


@functools.lru_cache(maxsize=20)
def make_split_re(seps):
    """Cached helper function for split_at_comma_semi."""


def split_at_comma_semi(text, separators=(",", ";", "，", "،"), extra=()):
    """Splits the text at commas and semicolons, unless they are inside
    parenthesis.  ``separators`` is default separators (setting it eliminates
    default separators).  ``extra`` is extra separators to be used in addition
    to ``separators``.  The separators in ``separators`` and ``extra`` must
    be valid regexp pieces (already escaped if needed)."""
    assert isinstance(text, str)
    assert isinstance(separators, (list, tuple))
    assert isinstance(extra, (list, tuple))
    lst = []
    paren_cnt = 0
    bracket_cnt = 0
    ofs = 0
    parts = []
    if extra:
        separators = tuple(separators) + tuple(extra)
    split_re = r"[][()]|" + "|".join(sorted(separators, key=lambda x: -len(x)))
    for m in re.finditer(split_re, text):
        if ofs < m.start():
            parts.append(text[ofs:m.start()])
        if m.start() == 0 and m.end() == len(text):
            return [text]  # Don't split if it is the only content
        ofs = m.end()
        token = m.group(0)
        if token in "([":
            bracket_cnt += 1
            parts.append(token)
        elif token in ")]":
            bracket_cnt -= 1
            parts.append(token)
        elif paren_cnt > 0 or bracket_cnt > 0:
            parts.append(token)
        else:
            if parts:
                lst.append("".join(parts).strip())
                parts = []
    if ofs < len(text):
        parts.append(text[ofs:])
    if parts:
        lst.append("".join(parts).strip())
    return lst

def split_slashes(ctx, text):
    """Splits the text at slashes.  This tries to use heuristics on how the
    split is to be interpreted, trying to prefer longer forms that can be
    found in the dictionary."""
    text = text.strip()
    if ctx.page_exists(text):
        return [text]

    text = re.sub(r"[／]", "/", text)
    alts = text.split(" / ")  # Always full split at " / "
    ret = []
    for alt in alts:
        alt = alt.strip()
        if alt.find("/") < 0 or alt[0] == "/" or alt[-1] == "/":
            # No slashes, no splitting; or starts/ends with a slash
            ret.append(alt)
            continue

        # Split text into words.  If only one word, assume single-word splits
        words = alt.split()
        if len(words) == 1:
            # Only one word
            ret.extend(x.strip() for x in alt.split("/"))
            continue

        # More than one word
        cands = [((), ())]
        for word in alt.split():
            new_cands = []
            parts = word.split("/")
            if len(parts) == 1:
                for ws, divs in cands:
                    ws = ws + tuple(parts)
                    new_cands.append([ws, divs])
            else:
                # Otherwise we might either just add alternatives for this word
                # or add alternatives for the whole phrase
                for p in parts:
                    for ws, divs in cands:
                        ws = ws + (p,)
                        new_cands.append(((), divs + (ws,)))
                        new_cands.append((ws, divs))
            cands = new_cands

        # Finalize candidates
        final_cands = set()
        for ws, divs in cands:
            if not ws:
                final_cands.add(divs)
                continue
            final_cands.add(divs + (ws,))
        print("final_cands", final_cands)

        # XXX this does not work yet
        ht = collections.defaultdict(list)
        for divs in final_cands:
            assert isinstance(divs, tuple) and isinstance(divs[0], tuple)
            score = 0
            words = []
            for ws in divs:
                assert isinstance(ws, tuple)
                exists = ctx.page_exists(" ".join(ws))
                words.extend(ws)
                score += 100
                score += 1 / len(ws)
                #if not exists:
                #    score += 1000 * len(ws)
            key = tuple(words)
            ht[key].append((score, divs))
        for key, items in sorted(ht.items()):
            print("key={} items={}".format(key, items))
            score, divs = min(items)
            for ws in divs:
                ret.append(" ".join(ws))

    return ret


def freeze(x):
    """Produces a read-only key for sets/dictionaries from the data.  This
    ignores "source" field from dictionaries."""
    if isinstance(x, dict):
        # XXX pending removal - we now add all entries from inflection tables
        # if "source" in x:
        #     x = x.copy()
        #     del x["source"]
        return frozenset((k, freeze(v)) for k, v in x.items())
    if isinstance(x, set):
        return frozenset(x)
    if isinstance(x, (list, tuple)):
        return tuple(freeze(v) for v in x)
    # XXX objects not current handled
    return x

# Utilities for manipulating word data structures
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import copy
import re
from collections import defaultdict
from functools import lru_cache, partial
from typing import Any, Dict, Iterable, List, Tuple

from wiktextract.wxr_context import WiktextractContext

# Keys in ``data`` that can only have string values (a list of them)
str_keys = ("tags", "glosses")
# Keys in ``data`` that can only have dict values (a list of them)
dict_keys = {
    "pronunciations",
    "senses",
    "synonyms",
    "related",
    "antonyms",
    "hypernyms",
    "holonyms",
    "forms",
}


def data_append(
    wxr: WiktextractContext, data: Dict, key: str, value: Any
) -> None:
    """Appends ``value`` under ``key`` in the dictionary ``data``.  The key
    is created if it does not exist."""
    assert isinstance(wxr, WiktextractContext)
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


def data_extend(
    wxr: WiktextractContext, data: Dict, key: str, values: Iterable
) -> None:
    """Appends all values in a list under ``key`` in the dictionary ``data``."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(data, dict)
    assert isinstance(key, str)
    assert isinstance(values, (list, tuple))

    # Note: we copy values, just in case it would actually be the same as
    # data[key].  This has happened, and leads to iterating for ever, running
    # out of memory.  Other ways of avoiding the sharing may be more
    # complex.
    for x in tuple(values):
        data_append(wxr, data, key, x)


@lru_cache(maxsize=20)
def make_split_re(seps):
    """Cached helper function for split_at_comma_semi."""


def split_at_comma_semi(text: str, separators=(",", ";", "，", "،"), extra=()
) -> List[str]:
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
            parts.append(text[ofs : m.start()])
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


def split_slashes(wxr, text):
    """Splits the text at slashes.  This tries to use heuristics on how the
    split is to be interpreted, trying to prefer longer forms that can be
    found in the dictionary."""
    text = text.strip()
    if wxr.wtp.page_exists(text):
        return [text]

    text = text.replace("／", "/")
    alts = text.split(" / ")  # Always full split at " / "
    ret = []
    for alt in alts:
        alt = alt.strip()
        if "/" not in alt or alt[0] == "/" or alt[-1] == "/":
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
        ht = defaultdict(list)
        for divs in final_cands:
            assert isinstance(divs, tuple) and isinstance(divs[0], tuple)
            score = 0
            words = []
            for ws in divs:
                assert isinstance(ws, tuple)
                # exists = wxr.wtp.page_exists(" ".join(ws))
                words.extend(ws)
                score += 100
                score += 1 / len(ws)
                # if not exists:
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


def ns_title_prefix_tuple(
    wxr, namespace: str, lower: bool = False
) -> Tuple[str, ...]:
    """Based on given namespace name, create a tuple of aliases"""
    if namespace in wxr.wtp.NAMESPACE_DATA:
        return tuple(
            map(
                lambda x: x.lower() + ":" if lower else x + ":",
                [wxr.wtp.NAMESPACE_DATA[namespace]["name"]]
                + wxr.wtp.NAMESPACE_DATA[namespace]["aliases"],
            )
        )
    else:
        return ()


def find_similar_gloss(page_data: List[Dict], gloss: str) -> Dict:
    """
    Return a sense dictionary if it has similar gloss, return the last
    word dictionary if can't found such gloss.
    """
    from rapidfuzz.fuzz import partial_token_set_ratio
    from rapidfuzz.process import extractOne
    from rapidfuzz.utils import default_process

    if len(gloss) == 0:
        return page_data[-1]

    choices = [
        sense_dict.get("raw_glosses", sense_dict.get("glosses", [""]))[0]
        for sense_dict in page_data[-1]["senses"]
    ]
    if match_result := extractOne(
        gloss,
        choices,
        score_cutoff=85,
        scorer=partial(partial_token_set_ratio, processor=default_process),
    ):
        return page_data[-1]["senses"][match_result[2]]

    return page_data[-1]


def append_base_data(
    page_data: List[Dict], field: str, value: Any, base_data: Dict
) -> None:
    if page_data[-1].get(field) is not None:
        if len(page_data[-1]["senses"]) > 0:
            # append new dictionary if the last dictionary has sense data and
            # also has the same key
            page_data.append(copy.deepcopy(base_data))
            page_data[-1][field] = value
        elif isinstance(page_data[-1].get(field), list):
            page_data[-1][field] += value
    else:
        page_data[-1][field] = value

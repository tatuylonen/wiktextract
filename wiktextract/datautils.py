# Utilities for manipulating word data structures
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
from .config import WiktionaryConfig
from wikitextprocessor import ALL_LANGUAGES, Wtp

# Keys in ``data`` that can only have string values (a list of them)
str_keys = ("tags", "glosses")
# Keys in ``data`` that can only have dict values (a list of them)
dict_keys = ("pronunciations", "senses", "synonyms", "related",
             "antonyms", "hypernyms", "holonyms", "forms")

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
    lst = data.get(key, [])
    lst.append(value)
    data[key] = lst


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


def split_at_comma_semi(text, extra=()):
    """Splits the text at commas and semicolons, unless they are inside
    parenthesis."""
    assert isinstance(text, str)
    assert isinstance(extra, (list, tuple))
    lst = []
    paren_cnt = 0
    bracket_cnt = 0
    ofs = 0
    parts = []
    split_re = r"[][(),;]"
    if extra:
        split_re = "({})|{}".format(split_re,
                                    "|".join(re.escape(x) for x in extra))
    for m in re.finditer(split_re, text):
        if ofs < m.start():
            parts.append(text[ofs:m.start()])
        ofs = m.end()
        token = m.group(0)
        if token == "[":
            bracket_cnt += 1
            parts.append(token)
        elif token == "]":
            bracket_cnt -= 1
            parts.append(token)
        elif token == "(":
            paren_cnt += 1
            parts.append(token)
        elif token == ")":
            paren_cnt -= 1
            parts.append(token)
        elif paren_cnt > 0 or bracket_cnt > 0:
            parts.append(token)
        else:
            assert token in ",;" or token in extra
            if parts:
                lst.append("".join(parts).strip())
                parts = []
    if ofs < len(text):
        parts.append(text[ofs:])
    if parts:
        lst.append("".join(parts).strip())
    return lst

# Utilities for manipulating word data structures
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
from .config import WiktionaryConfig
from wikitextprocessor import ALL_LANGUAGES

# Mapping from language code to language info
languages_by_code = {x["code"]: x for x in ALL_LANGUAGES}

# Keys in ``data`` that can only have string values (a list of them)
str_keys = ("tags", "glosses")
# Keys in ``data`` that can only have dict values (a list of them)
dict_keys = ("pronunciations", "senses", "synonyms", "related",
             "antonyms", "hypernyms", "holonyms", "forms")


def data_append(config, data, key, value):
    """Appends ``value`` under ``key`` in the dictionary ``data``.  The key
    is created if it does not exist."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(key, str)

    if key in str_keys:
        assert isinstance(value, str)
    elif key in dict_keys:
        assert isinstance(value, dict)
    if key == "tags":
        if value == "":
            return
        if value in languages_by_code:
            if value not in ("law", "toy", "and", "etc", "the", "god", "adj",
                             "man", "an", "tax", "or", "war", "job", "box",
                             "pop", "cay", "lay", "nut", "bay", "sea", "now"):
                config.debug("language code {} in tags: {}".format(value, data))
    lst = data.get(key, [])
    lst.append(value)
    data[key] = lst


def data_extend(config, data, key, values):
    """Appends all values in a list under ``key`` in the dictionary ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(key, str)
    assert isinstance(values, (list, tuple))

    for x in values:
        data_append(config, data, key, x)


def data_inflection_of(config, data, t, tags):
    """Adds an "inflection_of" value to ``data`` for the last argument of
    template ``t``.  Adds ``tags`` to the "tags" value in ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(tags, (list, tuple))

    vec = t_vec(config, t)
    if len(vec) == 0:
        config.debug("data_inflection_of empty vec: {} {} {}"
                     "".format(str(t), data, tags))
        return
    data_append(config, data, "inflection_of", vec[-1])
    data_extend(config, data, "tags", tags)


def data_alt_of(config, data, t, tags):
    """Adds an "alt_of" value to ``data`` for the last argument of
    template ``t``.  Adds ``tags`` to the "tags" value in ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(tags, (list, tuple))

    vec = t_vec(config, t)
    if len(vec) == 0:
        config.debug("data_alt_of empty vec: {} {} {}"
                     "".format(str(t), data, tags))
        return
    data_append(config, data, "alt_of", vec[-1])
    data_extend(config, data, "tags", tags)


def split_at_comma_semi(text):
    """Splits the text at commas and semicolons, unless they are inside
    parenthesis."""
    lst = []
    paren_cnt = 0
    bracket_cnt = 0
    ofs = 0
    parts = []
    for m in re.finditer(r"[][(),;]", text):
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
            assert token in ",;"
            if parts:
                lst.append("".join(parts).strip())
                parts = []
    if ofs < len(text):
        parts.append(text[ofs:])
    if parts:
        lst.append("".join(parts).strip())
    return lst

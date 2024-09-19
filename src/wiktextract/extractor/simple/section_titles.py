# https://simple.wiktionary.org/wiki/Category:Part_of_speech_templates
from typing import Optional, TypedDict

POSMap = TypedDict(
    "POSMap",
    {
        "pos": str,
        # "debug" is legacy from [en], might be implemented
        "debug": str,
        "tags": list[str],
        # SimplEn seems to very consistently use standardized templates
        # for each of its 'official' PoSes, so we can use that as a way
        # to further specify tags to be added
        "templates": dict[str, Optional[list[str]]],
    },
    total=False,
)

# Main entries for different kinds of POS headings; no aliases
POS_DATA: dict[str, POSMap] = {
    # "": {"pos": "", "tags": [""], "templates": {"": [""]}},
    "noun": {
        "pos": "noun",
        "templates": {
            "noun": None,
            "irrnoun": ["irregular"],
            "noun2": ["plural-only"],
            "noun3": None,  # Two singular forms
            "noun4": ["singular-only"],
            "letter": ["letter"],
        },
    },
    "abbreviation": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
        "templates": {"abbreviation": None},
    },
    "acronym": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
        "templates": {"acronym": None, "initialism": None},
    },
    "adjective": {"pos": "adj", "templates": {"adjective": None, "adj": None}},
    "adverb": {"pos": "adv", "templates": {"adverb": None}},
    "determiner": {
        "pos": "det",
        "templates": {
            "comparative determiner": ["comparative"],
            "determiner-comp": ["comparative"],
            "determiner": None,
        },
    },
    "conjunction": {"pos": "conj", "templates": {"conjunction": None}},
    "contraction": {
        "pos": "contraction",
        "tags": ["abbreviation"],
        "templates": {"contraction": None},
    },
    "coordinator": {
        "pos": "conj",
        "tags": ["coordinating"],
        "templates": {"coordinator": None},
    },
    "expression": {"pos": "phrase", "templates": {"expression": None}},
    "initialism": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
        "templates": {"initialism": None, "acronym": None},
    },
    "interjection": {"pos": "intj", "templates": {"interjection": None}},
    "preposition": {"pos": "prep", "templates": {"preposition": None}},
    "prefix": {
        "pos": "prefix",
        "tags": ["morpheme"],
        "templates": {"prefix": None},
    },
    "pronoun": {"pos": "pron", "templates": {"pron": None}},
    "proper noun": {"pos": "name", "templates": {"proper noun": None}},
    "subordinator": {
        "pos": "conj",
        "tags": ["subordinate-clause"],
        "templates": {"subordinator": None},
    },
    "suffix": {
        "pos": "suffix",
        "tags": ["morpheme"],
        "templates": {"suffix": None},
    },
    "symbol": {"pos": "symbol", "templates": {"symbol": None}},
    "verb": {
        "pos": "verb",
        "templates": {
            "verb": None,
            "verb2": None,  # alternative paradigms, "spelled" vs. "spelt"
            "verb3": None,  # Only used by "be", "is", etc.
            "verb4": ["auxiliary", "modal"],  # modal aux. 'will', 'can'.
            "verb5": ["auxiliary"],  # non-modal auxiliares like 'do' and 'have'
            "verb6": ["auxiliary"],  # same as verb5?
        },
    },
}


POS_HEADINGS_MAP = {
    "acronym & initialism": "acronym",
}

# POS aliases; use this to figure out if a heading is a POS heading
POS_HEADINGS = { k: v for k, v in POS_DATA.items() }

for k, v in POS_HEADINGS_MAP.items():
    if k in POS_HEADINGS or v not in POS_DATA:
        continue
    POS_HEADINGS[k] = POS_DATA[v]

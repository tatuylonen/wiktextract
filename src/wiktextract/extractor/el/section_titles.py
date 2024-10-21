# https://simple.wiktionary.org/wiki/Category:Part_of_speech_templates
from typing import TypedDict

POSMap = TypedDict(
    "POSMap",
    {
        "pos": str,
        # "debug" is legacy from [en], might be implemented
        "debug": str,
        "tags": list[str],
    },
    total=False,
)

# Main entries for different kinds of POS headings; no aliases
# XXX translate these
_POS_HEADINGS_BASE: dict[str, POSMap] = {
    # "": {"pos": "", "tags": [""],
    "noun": {
        "pos": "noun",
    },
    "abbreviation": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "acronym": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "adjective": {"pos": "adj"},
    "adverb": {"pos": "adv"},
    "determiner": {
        "pos": "det",
    },
    "conjunction": {
        "pos": "conj",
    },
    "contraction": {
        "pos": "contraction",
        "tags": ["abbreviation"],
    },
    "coordinator": {
        "pos": "conj",
        "tags": ["coordinating"],
    },
    "expression": {
        "pos": "phrase",
    },
    "initialism": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "interjection": {
        "pos": "intj",
    },
    "preposition": {
        "pos": "prep",
    },
    "prefix": {
        "pos": "prefix",
        "tags": ["morpheme"],
    },
    "pronoun": {
        "pos": "pron",
    },
    "proper noun": {
        "pos": "name",
    },
    "subordinator": {
        "pos": "conj",
        "tags": ["subordinate-clause"],
    },
    "suffix": {
        "pos": "suffix",
        "tags": ["morpheme"],
    },
    "symbol": {
        "pos": "symbol",
    },
    "verb": {
        "pos": "verb",
    },
}


_POS_HEADINGS_MAP = {
    "acronym & initialism": "acronym",
}


for k, v in _POS_HEADINGS_MAP.items():
    _POS_HEADINGS_BASE[k] = _POS_HEADINGS_BASE[v]

POS_HEADINGS = _POS_HEADINGS_BASE

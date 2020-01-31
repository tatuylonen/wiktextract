# This file defines corrections for common (and less common) misspellings in
# section titles in Wiktionary.  This also configures special handling for
# certain section titles.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org


# Corrections for misspelled section titles.  This basically maps the actual
# subsection title to the title that will be used when we parse it.  We should
# really review and fix all Wiktionary entries that use these, especially the
# misspellings.  In some cases we should improve the code to handle the
# additional information provided by the section title (e.g., gender).
# XXX do that later.
sectitle_corrections = {
    "adjectif": {
        "correct": "adjective",
        "error": True,
    },
    "alernative forms": {
        "correct": "alternative forms",
        "error": True,
    },
    "antonyid": {
        "correct": "antonyms",
        "error": True,
    },
    "antoynms": {
        "correct": "antonyms",
        "error": True,
    },
    "conjugaton 1": {
        "correct": "declension",  # XXX
        "error": True,
    },
    "conjugaton 2": {
        "correct": "declension",  # XXX
        "error": True,
    },
    "coordinate terid": {
        "correct": "coordinate terms",
        "error": True,
    },
    "decelsnion": {
        "correct": "declension",
        "error": True,
    },
    "decentants": {
        "correct": "descendants",
        "error": True,
    },
    "declension (fem.)": {
        "correct": "declension",  # XXX should utilize this
    },
    "declension (masc.)": {
        "correct": "declension",  # XXX should utilize this
    },
    "declension (neut.)": {
        "correct": "declension",  # XXX should utilize this
    },
    "declension (person)": {
        "correct": "declension",  # XXX
    },
    "declension for adjectives": {
        "correct": "declension",
    },
    "declension for feminine": {
        "correct": "declension",  # XXX
    },
    "declension for nouns": {
        "correct": "declension",
    },
    "declension for sense 1 only": {
        "correct": "declension",  # XXX
    },
    "declension for sense 2 only": {
        "correct": "declension",  # XXX
    },
    "declension for words with singular and plural": {
        "correct": "declension",  # XXX
    },
    "declension for words with singular only": {
        "correct": "declension",  # XXX
    },
    "declination": {
        "correct": "declension",
    },
    "deived terms": {
        "correct": "derived terms",
        "error": True,
    },
    "derived teerms": {
        "correct": "derived terms",
        "error": True,
    },
    "derived temrs": {
        "correct": "derived terms",
        "error": True,
    },
    "derived terrms": {
        "correct": "derived terms",
        "error": True,
    },
    "derived words": {
        "correct": "derived terms",
    },
    "derivedt terms": {
        "correct": "derived terms",
        "error": True,
    },
    "deriveed terms": {
        "correct": "derived terms",
        "error": True,
    },
    "derivered terms": {
        "correct": "derived terms",
        "error": True,
    },
    "etimology": {
        "correct": "etymology",
        "error": True,
    },
    "etymlogy": {
        "correct": "etymology",
        "error": True,
    },
    "etymology2": {
        "correct": "etymology",
    },
    "expresion": {
        "correct": "expression",
        "error": True,
    },
    "feminine declension": {
        "correct": "declension",  # XXX
    },
    "holonyid": {
        "correct": "holonyms",
        "error": True,
    },
    "hypernym": {
        "correct": "hypernyms",
    },
    "hyponyid": {
        "correct": "hyponyms",
        "error": True,
    },
    "inflection 1 (fem.)": {
        "correct": "declension",  # XXX
    },
    "inflection 1 (way)": {
        "correct": "declension",  # XXX
    },
    "inflection 2 (neut.)": {
        "correct": "declension",  # XXX
    },
    "inflection 2 (time)": {
        "correct": "declension",  # XXX
    },
    "inflection": {
        "correct": "declension",
    },
    "masculine declension": {
        "correct": "declension",  # XXX
    },
    "nouns and adjective": {
        "correct": "noun",  # XXX not really correct
        "error": True,
    },
    "nouns and adjectives": {
        "correct": "noun",   # XXX this isn't really correct
        "error": True,
    },
    "nouns and other parts of speech": {
        "correct": "noun",   # XXX not really correct
        "error": True,
    },
    "opposite": {
        "correct": "antonyms",
        "error": True,
    },
    "participles": {
        "correct": "verb",
    },
    "pronounciation": {
        "correct": "pronunciation",
        "error": True,
    },
    "pronuncation": {
        "correct": "pronunciation",
        "error": True,
    },
    "pronunciaion": {
        "correct": "pronunciation",
        "error": True,
    },
    "pronunciation and usage notes": {
        "correct": "pronunciation",
    },
    "pronunciationi": {
        "correct": "pronunciation",
        "error": True,
    },
    "pronunciations": {
        "correct": "pronunciation",
    },
    "pronunciaton": {
        "correct": "pronunciation",
        "error": True,
    },
    "pronunciayion": {
        "correct": "pronunciation",
        "error": True,
    },
    "pronuniation": {
        "correct": "pronunciation",
        "error": True,
    },
    "pronunciation 1": {
        "correct": "pronunciation",
    },
    "pronunciation 2": {
        "correct": "pronunciation",
    },
    "pronunciation 3": {
        "correct": "pronunciation",
    },
    "pronunciation 4": {
        "correct": "pronunciation",
    },
    "quptations": {
        "correct": "quotations",
        "error": True,
    },
    "realted terms": {
        "correct": "related terms",
        "error": True,
    },
    "refereces": {
        "correct": "references",
        "error": True,
    },
    "referenes": {
        "correct": "references",
        "error": True,
    },
    "refererences": {
        "correct": "references",
        "error": True,
    },
    "referneces": {
        "correct": "references",
        "error": True,
    },
    "refernecs": {
        "correct": "references",
        "error": True,
    },
    "related names": {
        "correct": "related terms",
    },
    "related terid": {
        "correct": "related terms",
        "error": True,
    },
    "synomyms": {
        "correct": "synonyms",
        "error": True,
    },
    "synonmys": {
        "correct": "synonyms",
        "error": True,
    },
    "synonym": {
        "correct": "synonyms",
    },
    "synonymes": {
        "correct": "synonyms",
        "error": True,
    },
    "syonyms": {
        "correct": "synonyms",
        "error": True,
    },
    "syonynms": {
        "correct": "synonyms",
        "error": True,
    },
    "usagw note": {
        "correct": "usage note",
        "error": True,
    },
}

# Definitions of extracted parts of speech codes and a mapping from
# Wiktionary section titles to parts of speech.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

# This dictionary maps section titles in articles to parts-of-speech.  There
# is a lot of variety and misspellings, and this tries to deal with those.
part_of_speech_map = {
    "abbreviation": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "acronym": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "adjectival": {
        "pos": "adj_noun",
    },
    "adjectival noun": {
        "pos": "adj_noun",
    },
    "adjectival verb": {
        "pos": "adj_verb",
    },
    "adjective": {
        "pos": "adj",
    },
    "adjectuve": {
        "pos": "adj",
        "error": "Misspelled subtitle",
    },
    "adjectives": {
        "pos": "adj",
        "warning": "Usually used in singular",
    },
    "adverb": {
        "pos": "adv",
    },
    "adverbs": {
        "pos": "adv",
        "warning": "Usually used in singular",
    },
    "adverbial phrase": {
        "pos": "adv_phrase",
    },
    "affix": {
        "pos": "affix",
    },
    "adjective suffix": {
        "pos": "affix",
    },
    "article": {
        "pos": "article",
    },
    "character": {
        "pos": "character",
    },
    "circumfix": {
        "pos": "circumfix",
    },
    "circumposition": {
        "pos": "circumpos",
    },
    "classifier": {
        "pos": "classifier",
    },
    "clipping": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "clitic": {
        "pos": "suffix",
        "tags": ["clitic"],
    },
    "combining form": {
        "pos": "combining_form",
        # XXX should change to affix/suffix/prefix?
    },
    "comparative": {
        "pos": "adj",
        "tags": ["comparative"],
    },
    "conjunction": {
        "pos": "conj",
    },
    "conjuntion": {
        "pos": "conj",
        "error": "Misspelled subtitle",
    },
    "contraction": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "converb": {
        "pos": "converb",
    },
    "counter": {
        "pos": "counter",
    },
    "determiner": {
        "pos": "det",
    },
    "diacritical mark": {
        "pos": "character",
    },
    "enclitic": {
        "pos": "suffix",
        "tags": ["clitic"],
    },
    "enclitic particle": {
        "pos": "suffix",
        "tags": ["clitic"],
    },
    "gerund": {
        "pos": "verb",
        "tags": ["participle", "gerund"],
    },
    "han character": {
        "pos": "character",
    },
    "han characters": {
        "pos": "character",
        "warning": "Usually used in singular",
    },
    "ideophone": {
        "pos": "noun",
        "tags": ["ideophone"],
    },
    "infix": {
        "pos": "infix",
    },
    "infinitive": {
        "pos": "verb",
        "tags": ["infinitive"],
    },
    "initialism": {
        "pos": "abbrev",
        "tags": ["abbreviation"],
    },
    "interfix": {
        "pos": "interfix",
    },
    "interjection": {
        "pos": "intj",
    },
    "interrogative pronoun": {
        "pos": "pron",
        "tags": ["interrogative"],
    },
    "intransitive verb": {
        "pos": "verb",
        "tags": ["intransitive"],
    },
    "instransitive verb": {
        "pos": "verb",
        "tags": ["intransitive"],
        "error": "Misspelled subtitle",
    },
    "kanji": {
        "pos": "character",
    },
    "letter": {
        "pos": "letter",
    },
    "ligature": {
        "pos": "character",
        "tags": ["ligature"],
    },
    "label": {
        "pos": "character",
    },
    "nom character": {
        "pos": "character",
    },
    "nominal nuclear clause": {
        "pos": "clause",
    },
    "νoun": {
        "pos": "noun",
        "error": "Misspelled subtitle",
    },
    "nouɲ": {
        "pos": "noun",
        "error": "Misspelled subtitle",
    },
    "noun": {
        "pos": "noun",
    },
    "nouns": {
        "pos": "noun",
        "warning": "Usually in singular",
    },
    "noum": {
        "pos": "noun",
        "error": "Misspelled subtitle",
    },
    "number": {
        "pos": "num",
    },
    "numeral": {
        "pos": "num",
    },
    "ordinal number": {
        "pos": "num",
        "tags": ["ordinal"],
    },
    "participle": {
        "pos": "verb",
        "tags": ["participle"],
    },
    "particle": {
        "pos": "particle",
        # XXX Many of these seem to be prefixes or suffixes
    },
    "past participle": {
        "pos": "verb",
        "tags": ["participle", "past"],
    },
    "perfect expression": {
        "pos": "verb",
    },
    "perfection expression": {
        "pos": "verb",
    },
    "perfect participle": {
        "pos": "verb",
        "tags": ["participle", "perfect"],
    },
    "personal pronoun": {
        "pos": "pron",
        "tags": ["person"],
    },
    "phrase": {
        "pos": "phrase",
    },
    "phrases": {
        "pos": "phrase",
        "warning": "Usually used in singular",
    },
    "possessive determiner": {
        "pos": "det",
        "tags": ["possessive"],
    },
    "possessive pronoun": {
        "pos": "det",
        "tags": ["possessive"],
    },
    "postposition": {
        "pos": "postp",
    },
    "predicative": {
        "pos": "adj",
        "tags": ["predicative"],
    },
    "prefix": {
        "pos": "prefix",
    },
    "preposition": {
        "pos": "prep",
    },
    "prepositions": {
        "pos": "prep",
        "warning": "Usually used in singular",
    },
    "prepositional expressions": {
        "pos": "prep",
    },
    "prepositional phrase": {
        "pos": "prep_phrase",
    },
    "prepositional pronoun": {
        "pos": "pron",
        "tags": ["prepositional"],
    },
    "present participle": {
        "pos": "verb",
        "tags": ["participle", "present"],
    },
    "preverb": {
        "pos": "preverb",
    },
    "pronoun": {
        "pos": "pron",
    },
    "proper noun": {
        "pos": "name",
    },
    "proper oun": {
        "pos": "name",
        "error": "Misspelled subtitle",
    },
    "proposition": {
        "pos": "prep",  # Appears to be a misspelling of preposition
        "error": "Misspelled subtitle",
    },
    "proverb": {
        "pos": "proverb",
    },
    "punctuation mark": {
        "pos": "punct",
    },
    "punctuation": {
        "pos": "punct",
    },
    "relative": {
        "pos": "conj",
        "tags": ["relative"],
    },
    "syllable": {
        "pos": "syllable",
    },
    "suffix": {
        "pos": "suffix",
    },
    "suffix form": {
        "pos": "suffix",
    },
    "symbol": {
        "pos": "symbol",
    },
    "transitive verb": {
        "pos": "verb",
        "tags": ["transitive"],
    },
    "unknown": {
        "pos": "unknown",
        # for languages like Chinese where we don't have the part-of-speech of a word
    },
    "verb": {
        "pos": "verb",
    },
    "verbal noun": {
        "pos": "noun",
        "tags": ["verbal"],
    },
    "verbs": {
        "pos": "verb",
        "warning": "Usually in singular",
    },
}

# Set of all possible parts-of-speech returned by wiktionary reading.
PARTS_OF_SPEECH = set(x["pos"] for x in part_of_speech_map.values())

# Definitions of extracted parts of speech codes and a mapping from
# Wiktionary section titles to parts of speech.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

# This dictionary maps section titles in articles to parts-of-speech.  There
# is a lot of variety and misspellings, and this tries to deal with those.
part_of_speech_map = {
    "abbreviation": {
        "pos": "abbrev",
        "debug": "part-of-speech Abbreviation is proscribed",
        "tags": ["abbreviation"],
    },
    "acronym": {
        "pos": "abbrev",
        "debug": "part-of-speech Acronym is proscribed",
        "tags": ["abbreviation"],
    },
    "adjectival": {
        "pos": "adj_noun",
        "debug": "part-of-speech Adjectival is not valid",
    },
    "adjectival noun": {
        # Not listed as allowed, but common
        "pos": "adj_noun",
    },
    "adjectival verb": {
        # Not listed as allowed, but common
        "pos": "adj_verb",
    },
    "adjective": {
        "pos": "adj",
    },
    "adjectuve": {
        "pos": "adj",
        "debug": "misspelled subtitle",
    },
    "adjectives": {
        "pos": "adj",
        "debug": "usually used in singular",
    },
    "adverb": {
        "pos": "adv",
    },
    "adverbs": {
        "pos": "adv",
        "debug": "usually used in singular",
    },
    "adverbial phrase": {
        "pos": "adv_phrase",
        "debug": "part-of-speech Adverbial phrase is proscribed",
    },
    "affix": {
        "pos": "affix",
    },
    "adjective suffix": {
        "pos": "suffix",
        "debug": "part-of-speech Adjective suffix is proscribed",
    },
    "ambiposition": {
        "pos": "ambiposition",
    },
    "article": {
        "pos": "article",
    },
    "character": {
        "pos": "character",
    },
    "circumfix": {
        "pos": "circumfix",
        "tags": ["morpheme"],
    },
    "circumposition": {
        "pos": "circumpos",
    },
    "classifier": {
        "pos": "classifier",
    },
    "clipping": {
        "pos": "abbrev",
        "debug": "part-of-speech Clipping is proscribed",
        "tags": ["abbreviation"],
    },
    "clitic": {
        "pos": "suffix",
        "debug": "part-of-speech Clitic is proscribed",
        "tags": ["clitic"],
    },
    "combining form": {
        "pos": "combining_form",
        "tags": ["morpheme"],
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
        "debug": "misspelled subtitle",
    },
    "contraction": {
        "pos": "contraction",
        "tags": ["abbreviation"],
    },
    "converb": {
        "pos": "converb",
    },
    "counter": {
        "pos": "counter",
    },
    "definitions": {
        # This is used under chinese characters
        "pos": "character",
    },
    "determiner": {
        "pos": "det",
    },
    "diacritical mark": {
        "pos": "character",
        "tags": ["diacritic"],
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
        "debug": "part-of-speech Gerund is proscribed",
        "tags": ["participle", "gerund"],
    },
    "han character": {
        "pos": "character",
        "tags": ["han"],
    },
    "han characters": {
        "pos": "character",
        "tags": ["han"],
        "debug": "psually used in singular",
    },
    "hanja": {
        "pos": "character",
        "tags": ["Hanja"],
    },
    "hanzi": {
        "pos": "character",
        "tags": ["hanzi"],
    },
    "ideophone": {
        "pos": "noun",
        "tags": ["ideophone"],
    },
    "idiom": {
        "pos": "phrase",
        "tags": ["idiomatic"],
        # This is too common for now to complain about
        # "debug": "part-of-speech Idiom is proscribed",
    },
    "infix": {
        "pos": "infix",
        "tags": ["morpheme"],
    },
    "infinitive": {
        "pos": "verb",
        "debug": "part-of-speech Infinitive is proscribed",
        "tags": ["infinitive"],
    },
    "initialism": {
        "pos": "abbrev",
        "debug": "part-of-speech Initialism is proscribed",
        "tags": ["abbreviation"],
    },
    "interfix": {
        "pos": "interfix",
        "tags": ["morpheme"],
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
        "debug": "part-of-speech Intransitive verb is proscribed",
        "tags": ["intransitive"],
    },
    "instransitive verb": {
        "pos": "verb",
        "tags": ["intransitive"],
        "debug": "pisspelled subtitle",
    },
    "kanji": {
        "pos": "character",
        "tags": ["kanji"],
    },
    "letter": {
        "pos": "character",
        "tags": ["letter"],
    },
    "ligature": {
        "pos": "character",
        "tags": ["ligature"],
    },
    "nominal nuclear clause": {
        "pos": "clause",
        "debug": "part-of-speech Nominal nuclear clause is proscribed",
    },
    "νoun": {
        "pos": "noun",
        "debug": "misspelled subtitle",
    },
    "nouɲ": {
        "pos": "noun",
        "debug": "misspelled subtitle",
    },
    "noun": {
        "pos": "noun",
    },
    "noun form": {
        "pos": "noun",
        "debug": "part-of-speech Noun form is proscribed",
    },
    "nouns": {
        "pos": "noun",
        "debug": "usually in singular",
    },
    "noum": {
        "pos": "noun",
        "debug": "misspelled subtitle",
    },
    "number": {
        "pos": "num",
        "tags": ["number"],
    },
    "numeral": {
        "pos": "num",
    },
    "ordinal number": {
        "pos": "adj",
        "debug": "ordinal numbers should be adjectives",
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
        "debug": "usually used in singular",
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
        "tags": ["morpheme"],
    },
    "preposition": {
        "pos": "prep",
    },
    "prepositions": {
        "pos": "prep",
        "debug": "usually used in singular",
    },
    "prepositional expressions": {
        "pos": "prep",
        "debug": "part-of-speech Prepositional expressions is proscribed",
    },
    "prepositional phrase": {
        "pos": "prep_phrase",
    },
    "prepositional pronoun": {
        "pos": "pron",
        "debug": "part-of-speech Prepositional pronoun is proscribed",
        "tags": ["prepositional"],
    },
    "present participle": {
        "pos": "verb",
        "debug": "part-of-speech Present participle is proscribed",
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
        "debug": "misspelled subtitle",
    },
    "proposition": {
        "pos": "prep",  # Appears to be a misspelling of preposition
        "debug": "misspelled subtitle",
    },
    "proverb": {
        "pos": "proverb",
    },
    "punctuation mark": {
        "pos": "punct",
        "tags": ["punctuation"],
    },
    "punctuation": {
        "pos": "punct",
        "debug": "part-of-speech Punctuation should be Punctuation mark",
        "tags": ["punctuation"],
    },
    "relative": {
        "pos": "conj",
        "tags": ["relative"],
    },
    "romanization": {
        "pos": "romanization",
    },
    "root": {
        "pos": "root",
        "tags": ["morpheme"],
    },
    "suffix": {
        "pos": "suffix",
        "tags": ["morpheme"],
    },
    "suffix form": {
        "pos": "suffix",
        "debug": "part-of-speech Suffix form is proscribed",
        "tags": ["morpheme"],
    },
    "syllable": {
        "pos": "syllable",
    },
    "symbol": {
        "pos": "symbol",
    },
    "transitive verb": {
        "pos": "verb",
        "tags": ["transitive"],
    },
    "verb": {
        "pos": "verb",
    },
    "verb form": {
        "pos": "verb",
        "debug": "part-of-speech Verb form is proscribed",
    },
    "verbal noun": {
        "pos": "noun",
        "tags": ["verbal"],
    },
    "verbs": {
        "pos": "verb",
        "debug": "usually in singular",
    },
}
for k, v in part_of_speech_map.items():
    if "tags" in v:
        assert isinstance(v["tags"], (list, tuple))

# Set of all possible parts-of-speech returned by wiktionary reading.
PARTS_OF_SPEECH = set(x["pos"] for x in part_of_speech_map.values())

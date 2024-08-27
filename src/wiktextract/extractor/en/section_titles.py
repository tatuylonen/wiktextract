from wiktextract.config import POSSubtitleData

# Lower case POS titles
POS_TITLES: dict[str, POSSubtitleData] = {
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
    "adjectival noun": {"pos": "adj_noun"},
    "adjectival verb": {"pos": "adj_verb"},
    "adjective": {"pos": "adj"},
    "adjectuve": {"pos": "adj", "debug": "misspelled subtitle"},
    "adjectives": {"pos": "adj", "debug": "usually used in singular"},
    "adverb": {"pos": "adv"},
    "adverbs": {"pos": "adv", "debug": "usually used in singular"},
    "adverbial phrase": {
        "pos": "adv_phrase",
        "debug": "part-of-speech Adverbial phrase is proscribed",
    },
    "affix": {"pos": "affix"},
    "adjective suffix": {
        "pos": "suffix",
        "debug": "part-of-speech Adjective suffix is proscribed",
    },
    "ambiposition": {"pos": "ambiposition"},
    "article": {"pos": "article"},
    "character": {"pos": "character"},
    "circumfix": {"pos": "circumfix", "tags": ["morpheme"]},
    "circumposition": {"pos": "circumpos"},
    "classifier": {"pos": "classifier"},
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
    "combining form": {"pos": "combining_form", "tags": ["morpheme"]},
    "comparative": {"pos": "adj", "tags": ["comparative"]},
    "conjunction": {"pos": "conj"},
    "conjuntion": {"pos": "conj", "debug": "misspelled subtitle"},
    "contraction": {"pos": "contraction", "tags": ["contraction"]},
    "converb": {"pos": "converb"},
    "counter": {"pos": "counter"},
    "definitions": {"pos": "character"},
    "dependent noun": {
        "pos": "noun",
        "tags": [
            "dependent",
        ],
    },
    "determiner": {"pos": "det"},
    "diacritical mark": {"pos": "character", "tags": ["diacritic"]},
    "enclitic": {"pos": "suffix", "tags": ["clitic"]},
    "enclitic particle": {"pos": "suffix", "tags": ["clitic"]},
    "gerund": {
        "pos": "verb",
        "debug": "part-of-speech Gerund is proscribed",
        "tags": ["participle", "gerund"],
    },
    "han character": {"pos": "character", "tags": ["han"]},
    "han characters": {
        "pos": "character",
        "tags": ["han"],
        "debug": "psually used in singular",
    },
    "hanja": {"pos": "character", "tags": ["Hanja"]},
    "hanzi": {"pos": "character", "tags": ["hanzi"]},
    "ideophone": {"pos": "noun", "tags": ["ideophone"]},
    "idiom": {"pos": "phrase", "tags": ["idiomatic"]},
    "infix": {"pos": "infix", "tags": ["morpheme"]},
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
    "interfix": {"pos": "interfix", "tags": ["morpheme"]},
    "interjection": {"pos": "intj"},
    "interrogative pronoun": {"pos": "pron", "tags": ["interrogative"]},
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
    "kanji": {"pos": "character", "tags": ["kanji"]},
    "letter": {"pos": "character", "tags": ["letter"]},
    "ligature": {"pos": "character", "tags": ["ligature"]},
    "nominal nuclear clause": {
        "pos": "clause",
        "debug": "part-of-speech Nominal nuclear clause is proscribed",
    },
    "νoun": {"pos": "noun", "debug": "misspelled subtitle"},
    "nouɲ": {"pos": "noun", "debug": "misspelled subtitle"},
    "noun": {"pos": "noun"},
    "noun form": {
        "pos": "noun",
        "debug": "part-of-speech Noun form is proscribed",
    },
    "nouns": {"pos": "noun", "debug": "usually in singular"},
    "noum": {"pos": "noun", "debug": "misspelled subtitle"},
    "number": {"pos": "num", "tags": ["number"]},
    "numeral": {"pos": "num"},
    "ordinal number": {
        "pos": "adj",
        "debug": "ordinal numbers should be adjectives",
        "tags": ["ordinal"],
    },
    "participle": {"pos": "verb", "tags": ["participle"]},
    "particle": {"pos": "particle"},
    "past participle": {"pos": "verb", "tags": ["participle", "past"]},
    "perfect expression": {"pos": "verb"},
    "perfection expression": {"pos": "verb"},
    "perfect participle": {"pos": "verb", "tags": ["participle", "perfect"]},
    "personal pronoun": {"pos": "pron", "tags": ["person"]},
    "phrase": {"pos": "phrase"},
    "phrases": {"pos": "phrase", "debug": "usually used in singular"},
    "possessive determiner": {"pos": "det", "tags": ["possessive"]},
    "possessive pronoun": {"pos": "det", "tags": ["possessive"]},
    "postposition": {"pos": "postp"},
    "predicative": {"pos": "adj", "tags": ["predicative"]},
    "prefix": {"pos": "prefix", "tags": ["morpheme"]},
    "preposition": {"pos": "prep"},
    "prepositions": {"pos": "prep", "debug": "usually used in singular"},
    "prepositional expressions": {
        "pos": "prep",
        "debug": "part-of-speech Prepositional expressions is proscribed",
    },
    "prepositional phrase": {"pos": "prep_phrase"},
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
    "preverb": {"pos": "preverb"},
    "pronoun": {"pos": "pron"},
    "proper noun": {"pos": "name"},
    "proper oun": {"pos": "name", "debug": "misspelled subtitle"},
    "proposition": {"pos": "prep", "debug": "misspelled subtitle"},
    "proverb": {"pos": "proverb"},
    "punctuation mark": {"pos": "punct", "tags": ["punctuation"]},
    "punctuation": {
        "pos": "punct",
        "debug": "part-of-speech Punctuation should be Punctuation mark",
        "tags": ["punctuation"],
    },
    "relative": {"pos": "conj", "tags": ["relative"]},
    "romanization": {"pos": "romanization"},
    "root": {"pos": "root", "tags": ["morpheme"]},
    "suffix": {"pos": "suffix", "tags": ["morpheme"]},
    "suffix form": {
        "pos": "suffix",
        "debug": "part-of-speech Suffix form is proscribed",
        "tags": ["morpheme"],
    },
    "syllable": {"pos": "syllable"},
    "symbol": {"pos": "symbol"},
    "transitive verb": {"pos": "verb", "tags": ["transitive"]},
    "verb": {"pos": "verb"},
    "verb form": {
        "pos": "verb",
        "debug": "part-of-speech Verb form is proscribed",
    },
    "verbal noun": {"pos": "noun", "tags": ["verbal"]},
    "verbs": {"pos": "verb", "debug": "usually in singular"},
}

LINKAGE_TITLES: dict[str, str] = {
    "synonyms": "synonyms",
    "ambiguous synonyms": "synonyms",
    "near synonyms": "synonyms",
    "pseudo-synonyms": "synonyms",
    "idiomatic synonyms": "synonyms",
    "hypernyms": "hypernyms",
    "hypernym": "hypernyms",
    "hyperonyms": "hypernyms",
    "classes": "hypernyms",
    "class": "hypernyms",
    "hyponyms": "hyponyms",
    "holonyms": "holonyms",
    "meronyms": "meronyms",
    "derived": "derived",
    "related": "related",
    "related terms": "related",
    "related words": "related",
    "related characters": "related",
    "idioms": "related",
    "idioms/phrases": "related",
    "similes": "related",
    "variance": "related",
    "coordinate terms": "coordinate_terms",
    "coordinate term": "coordinate_terms",
    "troponyms": "troponyms",
    "antonyms": "antonyms",
    "near antonyms": "antonyms",
    "instances": "instances",
    "intances": "instances",
    "archetypes": "instances",
    "see also": "related",
    "seealso": "related",
    "specific multiples": "related",
    "various": "related",
    "metonyms": "related",
    "demonyms": "related",
    "comeronyms": "related",
    "cohyponyms": "related",
    "proverbs": "proverbs",
    "abbreviations": "abbreviations",
    "derived terms": "derived",
    "alternative forms": "synonyms",
}

COMPOUNDS_TITLE = "compounds"

ETYMOLOGY_TITLES: frozenset[str] = frozenset(["etymology", "glyph origin"])

IGNORED_TITLES: frozenset[str] = frozenset(
    ["anagrams", "further reading", "references", "quotations", "statistics"]
)

INFLECTION_TITLES: frozenset[str] = frozenset(
    ["declension", "conjugation", "inflection", "mutation"]
)

DESCENDANTS_TITLE = "descendants"

PROTO_ROOT_DERIVED_TITLES: frozenset[str] = frozenset(
    ["derived terms", "extensions"]
)

PRONUNCIATION_TITLE = "pronunciation"

TRANSLATIONS_TITLE = "translations"

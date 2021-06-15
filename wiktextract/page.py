# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import copy
import html
import collections
import unicodedata
from wikitextprocessor import Wtp, WikiNode, NodeKind, ALL_LANGUAGES
from .parts_of_speech import part_of_speech_map, PARTS_OF_SPEECH
from .config import WiktionaryConfig
from .clean import clean_value
from .places import place_prefixes  # XXX move processing to places.py
from .unsupported_titles import unsupported_title_map
from .datautils import (data_append, data_extend, split_at_comma_semi)
from .disambiguate import disambiguate_clear_cases
from wiktextract.form_descriptions import (
    decode_tags, parse_word_head, parse_sense_qualifier,
    parse_pronunciation_tags,
    parse_alt_or_inflection_of, parse_head_final_tags,
    parse_translation_desc, xlat_tags_map, valid_tags,
    classify_desc, nested_translations_re, tr_note_re)
from .tags import linkage_beginning_tags

# NodeKind values for subtitles
LEVEL_KINDS = (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
               NodeKind.LEVEL5, NodeKind.LEVEL6)

# Mapping from language name to language info
languages_by_name = {x["name"]: x for x in ALL_LANGUAGES}

# Mapping from language code to language info
languages_by_code = {x["code"]: x for x in ALL_LANGUAGES}

# Matches head tag
head_tag_re = re.compile(r"^(head|Han char|arabic-noun|arabic-noun-form|"
                         r"hangul-symbol|syllable-hangul)$|" +
                         r"^(latin|" +
                         "|".join(languages_by_code.keys()) + r")-(" +
                         "|".join([
                             "abbr",
                             "adj",
                             "adjective",
                             "adjective form",
                             "adjective-form",
                             "adv",
                             "adverb",
                             "affix",
                             "animal command",
                             "art",
                             "article",
                             "aux",
                             "bound pronoun",
                             "bound-pronoun",
                             "Buyla",
                             "card num",
                             "card-num",
                             "cardinal",
                             "chunom",
                             "classifier",
                             "clitic",
                             "cls",
                             "cmene",
                             "cmavo",
                             "colloq-verb",
                             "colverbform",
                             "combining form",
                             "combining-form",
                             "comparative",
                             "con",
                             "concord",
                             "conj",
                             "conjunction",
                             "conjug",
                             "cont",
                             "contr",
                             "converb",
                             "daybox",
                             "decl",
                             "decl noun",
                             "def",
                             "dem",
                             "det",
                             "determ",
                             "Deva",
                             "ending",
                             "entry",
                             "form",
                             "fuhivla",
                             "gerund",
                             "gismu",
                             "hanja",
                             "hantu",
                             "hanzi",
                             "head",
                             "ideophone",
                             "idiom",
                             "inf",
                             "indef",
                             "infixed pronoun",
                             "infixed-pronoun",
                             "inflection",
                             "initialism",
                             "int",
                             "interfix",
                             "interj",
                             "interjection",
                             "jyut",
                             "latin",
                             "letter",
                             "locative",
                             "lujvo",
                             "monthbox",
                             "mutverb",
                             "name",
                             "nisba",
                             "nom",
                             "noun",
                             "noun form",
                             "noun-form",
                             "noun plural",
                             "noun-plural",
                             "nounprefix",
                             "num",
                             "number",
                             "numeral",
                             "ord",
                             "ordinal",
                             "par",
                             "part",
                             "part form",
                             "part-form",
                             "participle",
                             "particle",
                             "past",
                             "past neg",
                             "past-neg",
                             "past participle",
                             "past-participle",
                             "perfect participle",
                             "perfect-participle",
                             "personal pronoun",
                             "personal-pronoun",
                             "pref",
                             "prefix",
                             "phrase",
                             "pinyin",
                             "plural noun",
                             "plural-noun",
                             "pos",
                             "poss-noun",
                             "post",
                             "postp",
                             "postposition",
                             "PP",
                             "pp",
                             "ppron",
                             "pred",
                             "predicative",
                             "prep",
                             "prep phrase",
                             "prep-phrase",
                             "preposition",
                             "present participle",
                             "present-participle",
                             "pron",
                             "prondem",
                             "pronindef",
                             "pronoun",
                             "prop",
                             "proper noun",
                             "proper-noun",
                             "proper noun form",
                             "proper-noun form",
                             "proper noun-form",
                             "proper-noun-form",
                             "prov",
                             "proverb",
                             "prpn",
                             "prpr",
                             "punctuation mark",
                             "punctuation-mark",
                             "regnoun",
                             "rel",
                             "rom",
                             "romanji",
                             "root",
                             "sign",
                             "suff",
                             "suffix",
                             "syllable",
                             "symbol",
                             "verb",
                             "verb form",
                             "verb-form",
                             "verbal noun",
                             "verbal-noun",
                             "verbnec",
                             "vform",
                             ]) +
                         r")(-|/|$)")

# Matches an unicode character including any combining diacritics (even if
# separate characters)
unicode_dc_re = re.compile(r"\w[{}]|.".format(
    "".join(chr(x) for x in range(0, 0x110000)
            if unicodedata.category(chr(x)) == "Mn")))

# Additional templates to be expanded in the pre-expand phase
additional_expand_templates = set([
    "multitrans",
    "col1",
    "col2",
    "col3",
    "col4",
    "col5",
    "col1-u",
    "col2-u",
    "col3-u",
    "col4-u",
    "col5-u",
    "check deprecated lang param usage",
    "deprecated code",
])

# Mapping from subtitle to linkage field
linkage_map = {
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
}

# Inverse linkage for those that have them
linkage_inverses = {
    "synonyms": "synonyms",
    "hypernyms": "hyponyms",
    "hyponyms": "hypernyms",
    "holonyms": "meronyms",
    "meronyms": "holonyms",
    "derived": "derived_from",
    "coordinate_terms": "coordinate_terms",
    "troponyms": "hypernyms",
    "antonyms": "antonyms",
    "instances": "instance_of",
    "related": "related",
}

# List of all field names used for linkages
linkage_fields = list(sorted(set(linkage_map.values())))

# Templates that are used to form panels on pages and that
# should be ignored in various positions
panel_templates = set([
    "Character info",
    "CJKV",
    "French personal pronouns",
    "French possessive adjectives",
    "French possessive pronouns",
    "Han etym",
    "Japanese demonstratives",
    "Latn-script",
    "LDL",
    "MW1913Abbr",
    "Number-encoding",
    "Nuttall",
    "Spanish possessive adjectives",
    "Spanish possessive pronouns",
    "USRegionDisputed",
    "Webster 1913",
    "W",
    "Wikipedia",
    "ase-rfr",
    "attention",
    "attn",
    "beer",
    "broken ref",
    "ca-compass",
    "character info",
    "character info/var",
    "checksense",
    "compass-fi",
    "copyvio suspected",
    "delete",
    "etystub",
    "examples",
    "hu-corr",
    "hu-suff-pron",
    "interwiktionary",
    "ja-kanjitab",
    "ko-hanja-search",
    "look",
    "maintenance box",
    "maintenance line",
    "mediagenic terms",
    "merge",
    "missing template",
    "morse links",
    "move",
    "no inline",
    "picdic",
    "picdicimg",
    "picdiclabel",
    "polyominoes",
    "predidential nomics",
    "punctuation",  # This actually gets pre-expanded
    "request box",
    "rf-sound example",
    "rfaccents",
    "rfap",
    "rfaspect",
    "rfc",
    "rfc-auto",
    "rfc-header",
    "rfc-level",
    "rfc-pron-n",
    "rfc-sense",
    "rfclarify",
    "rfd",
    "rfd-redundant",
    "rfd-sense",
    "rfdate",
    "rfdatek",
    "rfdef",
    "rfe",
    "rfe/dowork",
    "rfex",
    "rfexp",
    "rfform",
    "rfgender",
    "rfi",
    "rfinfl",
    "rfm",
    "rfm-sense",
    "rfp",
    "rfp-old",
    "rfquote",
    "rfquote-sense",
    "rfquotek",
    "rfref",
    "rfscript",
    "rft2",
    "rftaxon",
    "rftone",
    "rftranslit",
    "rfv",
    "rfv-etym",
    "rfv-pron",
    "rfv-quote",
    "rfv-sense",
    "selfref",
    "split",
    "stroke order",  # XXX consider capturing this?
    "stub entry",
    "t-needed",
    "tbot entry",
    "tea room",
    "tea room sense",
    # "ttbc", - XXX needed in at least on/Preposition/Translation page
    "unblock",
    "unsupportedpage",
    "video frames",
    "wikipedia",
    "was wotd",
    "wrongtitle",
    "zh-forms",
    "zh-hanzi-box",
])

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
panel_prefixes = [
    "list:compass points/",
    "list:Latin script letters/",
    "list:Gregorian calendar months/",
    "RQ:",
]

wikipedia_templates = [
    "wikipedia",
    "slim-wikipedia",
    "w",
    "W",
    "swp",
    "Wikipedia",
    "wtorw",
]

# Some category tags are so common that they would clutter the extracted data
# and are not linguistically very interesting (e.g., the same information can
# easily be seen from part-of-speech, tags, or other information).  Ignore such
# categories.
ignored_category_patterns = [
    ".* term requests",
    ".* redlinks",
    ".* red links",
    ".* lemmas$",
    ".* nouns$",
    ".* verbs$",
    ".* adverbs$",
    ".* adjectives$",
    ".* conjunctions$",
    ".* abbreviations$",
    ".* initialisms$",
    ".* clippings$",
    ".* acronyms$",
    ".* interjections$",
    ".* misspellings$",
    ".* suffixes$",
    ".* prefixes$",
    ".* letters$",
    ".* palindromes$",
    ".* possessive suffixes$",
    ".* infinitives$",
    ".* participles$",
    ".* Han characters$",
    ".* syllables$",
    ".* forms$",
    ".* language$",
    ".* phrases",
    ".* missing plurals$",
    ".* eponyms$",
    ".*-syllable words$",
    ".* terms with .*IPA pronunciation",
    ".* terms without .*IPA",
    ".* terms with audio pronunciation",
    ".* terms with .* senses$",
    ".* slang$",
    ".* terms with homophones",
    ".* terms$",
    ".* vulgarities$",
    ".* terms with usage examples$",
    ".* colloquialisms$",
    ".* words without vowels$",
    ".* contractions$",
    ".* terms with audio links$",
    ".* terms with quotations$",
    ".* templates to be cleaned",
    ".* terms inherited from ",
    ".* terms borrowed from ",
    ".* terms derived from ",
    ".* terms coined by ",
    ".* terms calqued from ",
    ".* terms partially calqued from ",
    ".* calques$",
    ".* coinages$",
    ".* orthographic borrowings from ",
    ".* unadapted borrowings from ",
    ".* learned borrowings from ",
    ".* semi-learned borrowings from ",
    ".* semantic loans from ",
    ".* phono-semantic matchings from ",
    ".* terms spelled with ",
    ".* words suffixed with ",
    ".* words prefixed with ",
    ".* etymologies$",
    ".* etymologies with ",
    ".* doublets$",
    ".* (female|male) given names from ",
    ".* surnames from ",
    ".* terms needing to be assigned to a sense",
    ".* nouns with unknown or uncertain plurals",
    ".* foreign words of the day",
    ".* non-lemma forms$",
    ".* pinyin$",
    ".* nocat$",
    ".* with appendix$",
    ".* without a main entry",
    ".* with qual$",
    ".* with nopl$",
    ".* needing pronunciation attention",
    ".* link with missing target page",
    ".* nouns in .* script$",
    ".* verbs in .* script$",
    ".* gerunds$",
    "Japanese terms written with .* Han script characters",
    "Japanese terms written with one Han script character",
    "Vietnamese Han characters with unconfirmed readings",
    "Vietnamese terms written with one Han script character",
    "Vietnamese terms written with .* Han script characters",
    "Spanish forms of verbs ending in ",
    "Advanced Mandarin",
    "Japanese kanji with ",
    "Japanese katagana",
    "Japanese hiragana",
    "Han script characters",
    "Han char without ",
    "Japanese terms historically spelled with ",
    "Vietnamese Han character with unconfirmed readings",
    "Translingual symbols",
    "Check ",
    "Kenny's testing category 2",
    "Sort key tracking/redundant",
    "head tracking/",
    "Template with ",
    "Entries with deprecated labels",
    "Requests for ",
    "Terms with manual ",
    "Terms with redundant ",
    "Reference templates lacking",
    "Entries using missing taxonomic name",
    "Entries missing ",
    "etyl cleanup",
    "attention lacking explanation",
    "Translation table header lacks gloss",
    "Entries needing topical attention",
    "English words following the I before E except after C rule",
    "English words containing Q not followed by U",
    "IPA for English using",
    " IPA pronunciation",
    "IPA pronunciations with invalid IPA characters",
    "^[a-z]{2,3}-",
    "Foreign word of the day",
    "Foreign words of the day",
    ".* two-letter words$",
    ".* three-letter words$",
    ".* four-letter words$",
]
ignored_cat_re = re.compile(r"([a-z]{2,4})?" +
                            "|".join(ignored_category_patterns))

# Mapping from a template name (without language prefix) for the main word
# (e.g., fi-noun, fi-adj, en-verb) to permitted parts-of-speech in which
# it could validly occur.  This is used as just a sanity check to give
# warnings about probably incorrect coding in Wiktionary.
template_allowed_pos_map = {
    "abbr": ["abbrev"],
    "abbr": ["abbrev"],
    "noun": ["noun", "abbrev", "pron", "name", "num", "adj_noun"],
    "plural noun": ["noun", "name"],
    "plural-noun": ["noun", "name"],
    "proper noun": ["noun", "name"],
    "proper-noun": ["name", "noun"],
    "prop": ["name", "noun"],
    "verb": ["verb", "phrase"],
    "gerund": ["verb"],
    "adv": ["adv"],
    "particle": ["adv", "particle"],
    "part-form": ["adv", "particle"],
    "adj": ["adj", "adj_noun"],
    "pron": ["pron", "noun"],
    "name": ["name", "noun"],
    "adv": ["adv", "intj", "conj", "particle"],
    "phrase": ["phrase", "prep_phrase"],
    "noun phrase": ["phrase"],
    "ordinal": ["num"],
    "number": ["num"],
    "pos": ["affix", "name", "num"],
    "suffix": ["suffix", "affix"],
    "character": ["character"],
    "letter": ["character"],
    "kanji": ["character"],
    "cont": ["abbrev"],
    "interj": ["intj"],
    "con": ["conj"],
    "part": ["particle"],
    "part-form": ["participle"],
    "prep": ["prep", "postp"],
    "postp": ["postp"],
    "misspelling": ["noun", "adj", "verb", "adv"],
    "part-form": ["verb"],
}
for k, v in template_allowed_pos_map.items():
    for x in v:
        if x not in PARTS_OF_SPEECH:
            print("BAD PART OF SPEECH {!r} IN template_allowed_pos_map: {}={}"
                  "".format(x, k, v))
            assert False


# Ignore translations that start with one of these
tr_ignore_prefixes = [
    "+",
    "Different structure used",
    "Literally",
    "No equivalent",
    "Not used",
    "Please add this translation if you can",
    "See: ",
    "Use ",
    "[Book Pahlavi needed]",
    "[book pahlavi needed]",
    "different structure used",
    "e.g.",
    "lit.",
    "literally",
    "no equivalent",
    "normally ",
    "not used",
    "noun compound ",
    "please add this translation if you can",
    "prefix ",
    "see: ",
    "suffix ",
    "use ",
    "usually ",
]

# Ignore translations that contain one of these anywhere (case-sensitive).
# Or actually, put such translations in the "note" field rather than in "word".
tr_ignore_contains = [
    "usually expressed with ",
    " can be used ",
    " construction used",
    " used with ",
    " + ",
    "genitive case",
    "dative case",
    "nominative case",
    "accusative case",
    "absolute state",
    "infinitive of ",
    "participle of ",
    "for this sense",
    "depending on the circumstances",
    "expressed with ",
    " expression ",
    " means ",
    " is used",
    " — ",  # Used to give example sentences
    " translation",
    "not attested",
    "grammatical structure",
    "construction is used",
    "tense used",
    " lit.",
    " literally",
    "dative",
    "accusative",
    "genitive",
    "essive",
    "partitive",
    "translative",
    "elative",
    "inessive",
    "illative",
    "adessive",
    "ablative",
    "allative",
    "abessive",
    "comitative",
    "instructive",
    "particle",
    "predicative",
    "attributive",
    "preposition",
    "postposition",
    "prepositional",
    "postpositional",
    "prefix",
    "suffix",
]

# Ignore translations that match one of these regular expressions
tr_ignore_regexps = [
    r"^\[[\d,]+\]$",
    r"\?\?$",
    r"^\s*$",
]

# If a translation matches this regexp (with re.search), we print a debug
# message
tr_suspicious_re = re.compile(
    "|".join(re.escape(x) for x in
             [", ", "; ", "* ", ": ", "[", "]",
              "{", "}", "／", "^", "literally", "lit.",
              "also expressed with", "e.g.", "cf.",
              "used ", "script needed",
              "please add this translation",
              "usage "]))

# Regular expression to be searched from translation (with re.search) to check
# if it should be ignored.
tr_ignore_re = re.compile(
    "^(" + "|".join(re.escape(x) for x in tr_ignore_prefixes) + ")|" +
    "|".join(re.escape(x) for x in tr_ignore_contains) + "|" +
    "|".join(tr_ignore_regexps))  # These are not to be escaped


def parse_sense_XXXold_going_away(config, data, text, use_text):
    """Parses a word sense from the text.  The text is usually a list item
    from the beginning of the dictionary entry (i.e., before the first
    subtitle).  There is a lot of information and linkings in the sense
    description, which we try to gather here.  We also try to convert the
    various encodings used in Wiktionary into a fairly uniform form.
    The goal here is to obtain any information that might be helpful in
    automatically determining the meaning of the word sense."""

    # XXX this function is going away!  Still need to review what this captures
    # and reimplement some of them

    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(text, str)
    assert use_text in (True, False)

    if use_text:
        # The gloss is just the value cleaned into a string.  However, much of
        # the useful information is in the tagging within the text.  Note that
        # some entries don't really have a gloss text; for them, we may only
        # obtain some machine-readable linkages.
        gloss = clean_value(config, text)
        gloss = re.sub(r"\s*\[\d\d\d\d\]", "", gloss)  # Remove first years
        # Remove parenthesized start (usually tags/topics) from the gloss
        gloss = re.sub(r"^\([^()]*\)\s*", "", gloss)
        if gloss:
            # Got a gloss for this sense.
            data_append(config, data, "glosses", gloss)

    # Parse the Wikimedia coding from the text.
    p = wikitextparser.parse(text)

    # Iterate over all templates in the text.
    for t in p.templates:
        name = t.name.strip()

        # Usage examples are collected under "examples"
        if name in ("ux", "uxi", "usex", "afex", "zh-x", "prefixusex",
                      "ko-usex", "ko-x", "hi-x", "ja-usex-inline", "ja-x",
                      "quotei"):
            data_append(config, data, "examples", t_dict(config, t))
        # Various words have non-gloss definitions; we collect them under
        # "nonglosses".  For many purposes they might be treated similar to
        # glosses, though.
        elif name in ("non-gloss definition", "n-g", "ngd", "non-gloss",
                      "non gloss definition"):
            gloss = t_arg(config, t, 1)
            data_append(config, data, "nonglosses", gloss)
        # The "sense" templates are treated as additional glosses.
        elif name in ("sense", "Sense"):
            data_append(config, data, "tags", t_arg(config, t, 1))
        # These weird templates seem to be used to indicate a literal sense.
        elif name in ("&lit", "&oth"):
            data_append(config, data, "tags", "literal")
        # Many given names (first names) are tagged as such.  We tag them as
        # such, and tag with gender when available.  We also tag the term
        # as meaning an organism (though this might not be the case in rare
        # cases) and "person" (if it has a gender).
        elif name in ("given name",
                      "forename",
                      "historical given name"):
            data_extend(config, data, "tags", ["person", "given_name"])
            for k, v in t_dict(config, t).items():
                if k in ("template_name", "usage", "f", "var", "var2",
                         "from", "from2", "from3", "from4", "from5", "fron",
                         "fromt", "meaning", "m", "mt", "f",
                         "diminutive", "diminutive2",
                         "dim", "dim2", "dim3", "dim4", "dim5",
                         "dim6", "dim7", "dim8", "eq", "eq2", "eq3", "eq4",
                         "eq5", "A", "3"):
                    continue
                if k == "sort":
                    data_append(config, data, "sort", v)
                    continue
                if v == "en" or (k == "1" and len(v) <= 3):
                    continue
                if v in ("male_or_female", "unisex"):
                    pass
                elif v == "male":
                    data_append(config, data, "tags", "masculine")
                elif v == "female":
                    data_append(config, data, "tags", "feminine")
                else:
                    config.unknown_value(t, v)
        # Surnames are also often tagged as such, and we tag the sense
        # with "surname" and "person".
        elif name == "surname":
            data_extend(config, data, "tags", ["surname", "person"])
            from_ = t_arg(config, t, "from")
            if from_:
                data_append(config, data, "origin", from_)
        # Many nouns that are species and other organism types have taxon
        # links using various templates.  Store those links under
        # "taxon" (try to extract the species name).
        elif name in ("taxlink", "taxlinkwiki"):
            x = t_arg(config, t, 1)
            m = re.search(r"(.*) (subsp\.|f.)", x)
            if m:
                x = m.group(1)
            data_append(config, data, "taxon", t_vec(config, t))
            data_append(config, data, "tags", "organism")
        elif name == "taxon":
            data_append(config, data, "taxon", t_arg(config, t, 3))
            data_append(config, data, "tags", "organism")
        # Many organisms have vernacular names.
        elif name == "vern":
            data_append(config, data, "taxon", t_arg(config, t, 1))
            data_append(config, data, "tags", "organism")
        # Many colors have a color panel that defines the RGB value of the
        # color.  This provides a physical reference for what the color means
        # and identifies the word as a color value.  Record the corresponding
        # RGB value under "color".  Sometimes it may be a CSS color
        # name, sometimes an RGB value in hex.
        elif name in ("color panel", "colour panel"):
            vec = t_vec(config, t)
            for v in vec:
                if re.match(r"^[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]"
                            r"[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]$", v):
                    v = "#" + v
                elif re.match(r"^[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]$", v):
                    v = "#" + v[0] + v[0] + v[1] + v[1] + v[2] + v[2]
                data_append(config, data, "color", v)
        elif name in ("colorbox", "colourbox"):
            data_append(config, data, "tags", "color_value")
            data_append(config, data, "color", t_arg(config, t, 1))
        # Numbers often have a number box, which will indicate the numeric
        # value meant by the word.  We record the numeric value under "value".
        # (There is also other information that we don't currently capture.)
        elif name == "number box":
            data_append(config, data, "tags", "number_value")
            data_append(config, data, "value", t_arg(config, t, 2))
        # SI units of measurement appear to have tags that identify them
        # as such.  Add the information under "unit" and tag them as "unit".
        elif name in ("SI-unit", "SI-unit-2",
                      "SI-unit-np", "SI-unit-abb", "SI-unit-abbnp",
                      "SI-unit-abb2"):
            data_append(config, data, "unit", t_dict(config, t))
            data_append(config, data, "tags", "unit-of-measurement")
        # There are various templates that links to other Wikimedia projects,
        # typically Wikipedia.  Record such links under "wikipedia".
        elif name in ("slim-wikipedia", "wikipedia", "wikispecies", "w", "W",
                      "swp", "pedlink", "specieslink", "comcatlite",
                      "Wikipedia", "taxlinknew", "wtorw", "wj"):
            v = t_arg(config, t, 1)
            if not v:
                v = config.word
            if use_text:  # Skip wikipedia links in examples
                data_append(config, data, "wikipedia", v)
        elif name in ("w2",):
            if use_text:  # Skip wikipedia links in examples
                data_append(config, data, "wikipedia", t_arg(config, t, 2))
        # There are even morse code sequences (and semaphore (flag)) positions
        # defined in the Translingual portion of Wiktionary.  Collect
        # morse code information under "morse_code".
        elif name in ("morse code for", "morse code of",
                      "morse code abbreviation",
                      "morse code prosign"):
            data_append(config, data, "morse_code", t_arg(config, t, 1))
        elif name in ("translation hub", "translation only"):
            data_append(config, data, "tags", "translation_hub")
        elif name == "+preo":
            data_append(config, data, "object_preposition", t_arg(config, t, 2))
        elif name in ("+obj", "construed with"):
            if t_arg(config, t, "lang"):
                v = t_arg(config, t, 1)
            else:
                v = t_arg(config, t, 2)
            if v in ("dat", "dative"):
                data_append(config, data, "tags", "object_dative")
            elif v in ("acc", "accusative"):
                data_append(config, data, "tags", "object_accusative")
            elif v in ("ela", "elative"):
                data_append(config, data, "tags", "object_elative")
            elif v in ("abl", "ablative"):
                data_append(config, data, "tags", "object_ablative")
            elif v in ("gen", "genitive"):
                data_append(config, data, "tags", "object_genitive")
            elif v in ("nom", "nominative"):
                data_append(config, data, "tags", "object_nominative")
            elif v in ("ins", "instructive"):
                data_append(config, data, "tags", "object_instructive")
            elif v in ("obl", "oblique"):
                data_append(config, data, "tags", "object_oblique")
            elif v in ("loc", "locative"):
                data_append(config, data, "tags", "object_locative")
            elif v in ("participial",):
                data_append(config, data, "tags", "object_participial")
            elif v in ("subj", "subjunctive"):
                # (??? not really sure if subjunctive)
                data_append(config, data, "tags", "object_subjunctive")
            elif v == "with":
                data_append(config, data, "object_preposition", "with")
            elif v == "avec":
                data_append(config, data, "object_preposition", "avec")
            elif not v:
                ctx.warning("empty/missing object construction argument "
                            "in {}".format(t))
            else:
                config.unknown_value(t, v)
        elif name == "es-demonstrative-accent-usage":
            data_append(config, data, "tags", "demonstrative-accent")
        # Handle some Japanese-specific tags
        elif name in ("ja-kyujitai spelling of", "ja-kyu sp"):
            data_append(config, data, "kyujitai_spelling", t_arg(config, t, 1))
        # Handle some Chinese-specific tags
        elif name in ("zh-old-name", "18th c."):
            data_append(config, data, "tags", "archaic")
        elif name in ("zh-alt-form", "zh-altname", "zh-alt-name",
                      "zh-alt-term", "zh-altterm"):
            data_append(config, data, "alt_of", t_arg(config, t, 1))
        elif name in ("zh-short", "zh-abbrev", "zh-short-comp", "mfe-short of"):
            data_append(config, data, "tags", "abbreviation")
            for x in t_vec(config, t):
                data_append(config, data, "alt_of", x)
        elif name == "zh-misspelling":
            data_append(config, data, "alt_of", t_arg(config, t, 1))
            data_append(config, data, "tags", "misspelling")
        elif name in ("zh-synonym", "zh-synonym of", "zh-syn-saurus"):
            data_append(config, data, "tags", "synonym")
            base = t_arg(config, t, 1)
            if base != config:
                data_append(config, data, "alt_of", base)
        elif name in ("zh-dial", "zh-erhua form of"):
            base = t_arg(config, t, 1)
            if base != config:
                data_append(config, data, "alt_of", base)
                data_append(config, data, "tags", "dialectical")
        elif name == "zh-mw":
            data_extend(config, data, "classifier", t_vec(config, t))
        elif name == "zh-classifier":
            data_append(config, data, "tags", "classifier")
        elif name == "zh-div":
            # Seems to indicate type of a place (town, etc) in some entries
            # but the value is in Chinese
            # XXX check this
            data_append(config, data, "hypernyms",
                        {"word": t_arg(config, t, 1)})
        elif name in ("†", "zh-obsolete"):
            data_extend(config, data, "tags", ["archaic", "obsolete"])
        # Various words are marked as place names.  Tag such words as a
        # "place", by the place type, and add a link under "holonyms" if what
        # the place is part of has been specified.
        elif name == "place":
            data_append(config, data, "tags", "place")
            transl = t_arg(config, t, "t")
            if transl:
                data_append(config, data, "alt_of", transl)
            vec = t_vec(config, t)
            if len(vec) < 2:
                config.unknown_value(t, "TOO FEW ARGS")
                continue
            for x in vec[1].split("/"):
                data_append(config, data, "tags", x)
                data_append(config, data, "hypernyms", {"word": x})
            # XXX many templates have non-first arguments not containing /
            # that are a definition/gloss, and some have def=
            for x in vec[2:]:
                if not x:
                    continue
                idx = x.find("/")
                if idx >= 0:
                    prefix = x[:idx]
                    m = re.match(r"(?i)^(.+):(pref|suf|Suf)$", prefix)
                    if m:
                        prefix = m.group(1)
                    if prefix in place_prefixes:
                        kind = place_prefixes[prefix]
                        v = x[idx + 1:]
                        m = re.match(langtag_colon_re, v)
                        if m:
                            v = v[m.end():]
                        if v.find(":") >= 0:
                            config.unknown_value(t, x)
                        data_append(config, data, "holonyms",
                                    {"word": v,
                                     "type": kind})
                    else:
                        config.unknown_value(t, x)
                else:
                    data_append(config, data, "holonyms", {"word": x})
        # US state names seem to have a special tagging as such.  We tag them
        # as places, indicate that they are a part of the Unites States, and
        # are places of type "state".
        elif name == "USstate":
            data_append(config, data, "tags", "place")
            data_append(config, data, "holonyms", "United States")
            data_append(config, data, "place", {"type": "state",
                                        "english": [word]})
        # Brazilian states and state capitals seem to use their own tagging.
        # Collect this information in tags and links.
        elif name == "place:Brazil/state":
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "province")
            capital = t_arg(config, t, "capital")
            if capital:
                data_append(config, data, "meronyms", {"word": capital,
                                               "type": "city"})
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})
        elif name in ("place:Brazil/capital",):
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "city")
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})
        elif name in ("place:Brazil/state capital",
                      "place:state capital of Brazil"):
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "city")
            state = t_arg(config, t, "state")
            if state:
                data_append(config, data, "holonyms", {"word": state,
                                               "type": "province"})
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})
        elif name in ("place:Brazil/municipality",
                      "place:municipality of Brazil"):
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "municipality")
            if state:
                data_append(config, data, "holonyms", {"word": state,
                                               "type": "province"})
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})


def parse_pronunciation_XXX_old_going_away(config, data, text, p):
    """Extracts pronunciation information for the word."""

    # XXX this function being removed, but still has some things that should
    # be captured by the new version

    # XXX stuff removed
    # XXX "PIE root" has been replaced by "root" in Nov 2020
    if name == "PIE root":
        data_append(config, variant, "pie_root", t_arg(config, t, 2))


######################################################################
# XXX Above this is old junk
######################################################################

# Template name component to linkage section listing.  Integer section means
# default section, starting at that argument.
template_linkage_mappings = [
    ["syn", "synonyms"],
    ["synonyms", "synonyms"],
    ["ant", "antonyms"],
    ["hyp", "hyponyms"],
    ["der", "derived"],
    ["derived terms", "derived"],
    ["rel", "related"],
    ["col", 2],
]

# Maps template name used in a word sense to a linkage field that it adds.
sense_linkage_templates = {
    "syn": "synonyms",
    "synonyms": "synonyms",
    "hyponyms": "hyponyms",
}


def decode_html_entities(v):
    """Decodes HTML entities from a value, converting them to the respective
    Unicode characters/strings."""
    if isinstance(v, int):
        v = str(v)
    return html.unescape(v)


def is_panel_template(name):
    """Checks if ``name`` is a known panel template name (i.e., one that
    produces an infobox in Wiktionary, but this also recognizes certain other
    templates that we do not wish to expand)."""
    assert isinstance(name, str)
    if name in panel_templates:
        return True
    for prefix in panel_prefixes:
        if name.startswith(prefix):
            return True
    return False


def parse_sense_linkage(config, ctx, data, name, ht):
    """Parses a linkage (synonym, etc) specified in a word sense."""
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(name, str)
    assert isinstance(ht, dict)
    field = sense_linkage_templates[name]
    for i in range(2, 20):
        w = ht.get(i) or ""
        w = clean_node(config, ctx, data, w)
        if w.startswith("Thesaurus:"):
            w = w[10:]
        if not w:
            break
        data_append(ctx, data, field, {"word": w})


def recursively_extract(contents, fn):
    """Recursively extracts elements from contents for which ``fn`` returns
    True.  This returns two lists, the extracted elements and the remaining
    content (with the extracted elements removed at each level).  Only
    WikiNode objects can be extracted."""
    # If contents is a list, process each element separately
    extracted = []
    new_contents = []
    if isinstance(contents, (list, tuple)):
        for x in contents:
            e1, c1 = recursively_extract(x, fn)
            extracted.extend(e1)
            new_contents.extend(c1)
        return extracted, new_contents
    # If content is not WikiNode, just return it as new contents.
    if not isinstance(contents, WikiNode):
        return [], [contents]
    # Check if this content should be extracted
    if fn(contents):
        return [contents], []
    # Otherwise content is WikiNode, and we must recurse into it.
    kind = contents.kind
    new_node = WikiNode(kind, contents.loc)
    new_contents.append(new_node)
    if kind in (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
                NodeKind.LEVEL5, NodeKind.LEVEL6, NodeKind.LINK):
        # Process args and children
        assert isinstance(contents.args, (list, tuple))
        new_args = []
        for arg in contents.args:
            e1, c1 = recursively_extract(arg, fn)
            new_args.append(c1)
            extracted.extend(e1)
        new_node.args = new_args
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    elif kind in (NodeKind.ITALIC, NodeKind.BOLD, NodeKind.TABLE,
                  NodeKind.TABLE_CAPTION, NodeKind.TABLE_ROW,
                  NodeKind.TABLE_HEADER_CELL, NodeKind.TABLE_CELL,
                  NodeKind.PRE, NodeKind.PREFORMATTED):
        # Process only children
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    elif kind in (NodeKind.HLINE,):
        # No arguments or children
        pass
    elif kind in (NodeKind.LIST, NodeKind.LIST_ITEM):
        # Keep args as-is, process children
        new_node.args = contents.args
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    elif kind in (NodeKind.TEMPLATE, NodeKind.TEMPLATE_ARG, NodeKind.PARSER_FN,
                  NodeKind.URL):
        # Process only args
        new_args = []
        for arg in contents.args:
            e1, c1 = recursively_extract(arg, fn)
            new_args.append(c1)
            extracted.extend(e1)
        new_node.args = new_args
    elif kind == NodeKind.HTML:
        # Keep attrs and args as-is, process children
        new_node.attrs = contents.attrs
        new_node.args = contents.args
        e1, c1 = recursively_extract(contents.children, fn)
        extracted.extend(e1)
        new_node.children = c1
    else:
        raise RuntimeError("recursively_extract: unhandled kind {}"
                           .format(kind))
    return extracted, new_contents

def parse_language(ctx, config, langnode, language, lang_code):
    """Iterates over the text of the page, returning words (parts-of-speech)
    defined on the page one at a time.  (Individual word senses for the
    same part-of-speech are typically encoded in the same entry.)"""
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(langnode, WikiNode)
    assert isinstance(language, str)
    assert isinstance(lang_code, str)
    # print("parse_language", language)

    word = ctx.title
    unsupported_prefix = "Unsupported titles/"
    if word.startswith(unsupported_prefix):
        w = word[len(unsupported_prefix):]
        if w in unsupported_title_map:
            word = unsupported_title_map[w]
        else:
            ctx.error("Unimplemented unsupported title: {}".format(word))
            word = w

    base = {"word": word, "lang": language, "lang_code": lang_code}
    sense_data = {}
    pos_data = {}  # For a current part-of-speech
    etym_data = {}  # For one etymology
    pos_datas = []
    etym_datas = []
    page_datas = []
    stack = []

    def merge_base(data, base):
        for k, v in base.items():
            if k not in data:
                if isinstance(v, (list, tuple)):
                    # Copy the list to ensure that we don't share lists between
                    # structures.
                    data[k] = list(v)
                else:
                    data[k] = v
            elif isinstance(data[k], list):
                data[k].extend(v)
            elif data[k] != v:
                ctx.warning("conflicting values for {}: {} vs {}"
                            .format(k, data[k], v))

    def push_sense():
        """Starts collecting data for a new word sense.  This returns True
        if a sense was added."""
        nonlocal sense_data
        if not sense_data:
            return False
        pos_datas.append(sense_data)
        sense_data = {}
        return True

    def push_pos():
        """Starts collecting data for a new part-of-speech."""
        nonlocal pos_data
        nonlocal pos_datas
        push_sense()
        if ctx.subsection:
            if not pos_datas:
                pos_datas = [{"tags": ["no-senses"]}]
            data = {"senses": pos_datas}
            merge_base(data, pos_data)
            etym_datas.append(data)
        pos_data = {}
        pos_datas = []
        ctx.start_subsection(None)

    def push_etym():
        """Starts collecting data for a new etymology."""
        nonlocal etym_data
        nonlocal etym_datas
        push_pos()
        for data in etym_datas:
            merge_base(data, etym_data)
            page_datas.append(data)
        etym_data = {}
        etym_datas = []

    def parse_sense(pos, contents, sense_base):
        """Parses a word sense (basically, a list item describing a word sense).
        Sometimes there may be a second-level sublist that actually contains
        word senses (in which case the higher-level entry is just a grouping).
        This parses such sublists as separate senses (thus this can generate
        multiple new senses), unless the sublist has only one element, in which
        case it is assumed to be a wiktionary error and is interpreted as
        a top-level item.  This returns True if this added one or more
        senses."""
        assert isinstance(pos, str)
        assert isinstance(contents, (list, tuple))
        assert isinstance(sense_base, dict)  # Added to every sense
        # print("PARSE_SENSE ({}): {}".format(sense_base, contents))
        lst = []
        for i in range(len(contents)):
            x = contents[i]
            if isinstance(x, WikiNode) and x.kind == NodeKind.LIST:
                break
            lst.append(x)

        def sense_template_fn(name, ht):
            if is_panel_template(name):
                return ""
            if name in ("defdate",):
                return ""
            if name == "senseid":
                langid = clean_node(config, ctx, None, ht.get(1, ()))
                arg = clean_node(config, ctx, sense_base, ht.get(2, ()))
                if re.match(r"Q\d+$", arg):
                    data_append(ctx, sense_base, "wikidata", arg)
                data_append(ctx, sense_base, "senseid",
                            langid + ":" + arg)
            if name in sense_linkage_templates:
                parse_sense_linkage(config, ctx, sense_base, name, ht)
                return ""
            if name == "†" or name == "zh-obsolete":
                data_append(ctx, sense_base, "tags", "obsolete")
                return ""
            if name in ("ux", "uxi", "usex", "afex", "zh-x", "prefixusex",
                        "ko-usex", "ko-x", "hi-x", "ja-usex-inline", "ja-x",
                        "quotei", "zh-x", "he-x", "hi-x", "km-x", "ne-x",
                        "shn-x", "th-x", "ur-x"):
                # XXX capture usage example (check quotei!)
                return ""
            if name == "w":
                if ht.get(2) == "Wp":
                    return ""
            return None

        rawgloss = clean_node(config, ctx, sense_base, lst,
                              template_fn=sense_template_fn)

        # The gloss could contain templates that produce more list items.
        # This happens commonly with, e.g., {{inflection of|...}}.  Split
        # to parts.
        subglosses = re.split(r"[#*]+\s*", rawgloss)

        # Some entries, e.g., "iacebam", have weird sentences in quotes
        # after the gloss, but these sentences don't seem to be intended
        # as glosses.  Skip them.
        subglosses = list(gl for gl in subglosses
                          if not re.match(r'\s*(\([^)]*\)\s*)?(:|"[^"]*"\s*$)',
                                          gl))

        if len(subglosses) > 1 and "form_of" not in sense_base:
            gl = subglosses[0].strip()
            if gl.endswith(":"):
                gl = gl[:-1].strip()
            parsed = parse_alt_or_inflection_of(ctx, gl)
            if parsed is not None:
                infl_tags, infl_dt = parsed
                if infl_dt is not None and "form-of" in infl_tags:
                    # Interpret others as a particular form under
                    # "inflection of"
                    data_extend(ctx, sense_base, "tags", infl_tags)
                    data_append(ctx, sense_base, "form_of", infl_dt)
                    subglosses = subglosses[1:]
                elif infl_dt is not None:
                    data_extend(ctx, sense_base, "tags", infl_tags)
                    subglosses = subglosses[1:]

        # Create senses for remaining subglosses
        added = False
        for gloss_i, gloss in enumerate(subglosses):
            gloss = gloss.strip()
            if not gloss and len(subglosses) > 1:
                continue
            # Push a new sense (if the last one is not empty)
            if push_sense():
                added = True
            # If the gloss starts with †, mark as obsolete
            if gloss.startswith("^†"):
                data_append(ctx, sense_data, "tags", "obsolete")
                gloss = gloss[2:].strip()
            # Copy data for all senses to this sense
            for k, v in sense_base.items():
                if isinstance(v, (list, tuple)):
                    if k != "tags":
                        # Tags handled below (countable/uncountable special)
                        data_extend(ctx, sense_data, k, v)
                else:
                    assert k not in ("tags", "categories", "topics")
                    sense_data[k] = v
            # Parse the gloss for this particular sense
            m = re.match(r"^\((([^()]|\([^()]*\))*)\):?\s*", gloss)
            if m:
                parse_sense_qualifier(ctx, m.group(1), sense_data)
                gloss = gloss[m.end():].strip()

            def sense_repl(m):
                par = m.group(1)
                cls = classify_desc(par)
                # print("sense_repl: {} -> {}".format(par, cls))
                if cls == "tags":
                    parse_sense_qualifier(ctx, par, sense_data)
                    return ""
                # Otherwise no substitution
                return m.group(0)

            # Replace parenthesized expressions commonly used for sense tags
            gloss = re.sub(r"^\(([^()]*)\)", sense_repl, gloss)
            gloss = re.sub(r"\s*\(([^()]*)\)$", sense_repl, gloss)

            # Remove common suffix "[from 14th c.]" and similar
            gloss = re.sub(r"\s\[[^]]*\]\s*$", "", gloss)

            # Check to make sure we don't have unhandled list items in gloss
            ofs = max(gloss.find("#"), gloss.find("*"))
            if ofs > 10:
                ctx.debug("gloss may contain unhandled list items: {}"
                          .format(gloss))

            # Kludge, some glosses have a comma after initial qualifiers in
            # parentheses
            if gloss.startswith(",") or gloss.startswith(":"):
                gloss = gloss[1:]
            gloss = gloss.strip()
            if gloss.endswith(":"):
                gloss = gloss[:-1].strip()
            if gloss.startswith("N. of "):
                gloss = "Name of " +  gloss[6:]
            if gloss.startswith("†"):
                data_append(ctx, sense_data, "tags", "obsolete")
                gloss = gloss[1:]
            elif gloss.startswith("^†"):
                data_append(ctx, sense_data, "tags", "obsolete")
                gloss = gloss[2:]

            # Copy tags from sense_base if any.  This will not copy
            # countable/uncountable if either was specified in the sense,
            # as sometimes both are specified in word head but only one
            # in individual senses.
            countability_tags = []
            base_tags = sense_base.get("tags", ())
            sense_tags = sense_data.get("tags", ())
            for tag in base_tags:
                if tag in ("countable", "uncountable"):
                    if tag not in countability_tags:
                        countability_tags.append(tag)
                    continue
                if tag not in sense_tags:
                    data_append(ctx, sense_data, "tags", tag)
            if countability_tags:
                if ("countable" not in sense_tags and
                    "uncountable" not in sense_tags):
                    data_extend(ctx, sense_data, "tags", countability_tags)

            # If outer gloss specifies a form-of ("inflection of", see
            # aquamarine/German), try to parse the inner glosses as
            # tags for an inflected form.
            if "form-of" in sense_base.get("tags", ()):
                parsed = parse_alt_or_inflection_of(ctx, gloss)
                if parsed is not None:
                    infl_tags, infl_dt = parsed
                    if infl_dt is None and infl_tags:
                        # Interpret as a particular form under "inflection of"
                        data_extend(ctx, sense_data, "tags", infl_tags)

            if not gloss:
                #ctx.debug("{}: empty gloss at {}"
                #             .format(pos, "/".join(stack)))
                data_append(ctx, sense_data, "tags", "empty-gloss")
            elif gloss != "-":
                # Add the gloss for the sense.
                data_append(ctx, sense_data, "glosses", gloss)

            # Check if this gloss describes an alt-of or inflection-of
            parsed = parse_alt_or_inflection_of(ctx, gloss)
            if parsed is not None:
                tags, dt = parsed
                if dt is not None:
                    ftags = list(tag for tag in tags if tag != "form-of")
                    if "alt-of" in tags:
                        data_extend(ctx, sense_data, "tags", ftags)
                        data_append(ctx, sense_data, "alt_of", dt)
                    elif "compound-of" in tags:
                        data_extend(ctx, sense_data, "tags", ftags)
                        data_append(ctx, sense_data, "compound_of", dt)
                    elif "synonym-of" in tags:
                        data_extend(ctx, dt, "tags", ftags)
                        data_append(ctx, sense_data, "synonyms", dt)
                    elif tags and dt.get("word", "").startswith("of "):
                        dt["word"] = dt["word"][3:]
                        data_append(ctx, sense_data, "tags", "form-of")
                        data_extend(ctx, sense_data, "tags", ftags)
                        data_append(ctx, sense_data, "form_of", dt)
                    elif "form-of" in tags:
                        data_extend(ctx, sense_data, "tags", tags)
                        data_append(ctx, sense_data, "form_of", dt)

        if push_sense():
            added = True
        return added

    def head_template_fn(name, ht):
        """Handles special templates in the head section of a word.  Head
        section is the text after part-of-speech subtitle and before word
        sense list. Typically it generates the bold line for the word, but
        may also contain other useful information that often ends in
        side boxes.  We want to capture some of that additional information."""
        # print("HEAD_TEMPLATE_FN", name, ht)
        if name == "wtorw":
            parse_wikipedia_template(config, ctx, pos_data, ht)
            return None
        if name in wikipedia_templates:
            parse_wikipedia_template(config, ctx, pos_data, ht)
            return ""
        if is_panel_template(name):
            return ""
        if name == "number box":
            # XXX extract numeric value?
            return ""
        if name == "enum":
            # XXX extract?
            return ""
        if name == "cardinalbox":
            # XXX extract similar to enum?
            # XXX this can also occur in top-level under language
            return ""
        if name == "Han simplified forms":
            # XXX extract?
            return ""
        if name == "ja-kanji forms":
            # XXX extract?
            return ""
        if name == "vi-readings":
            # XXX extract?
            return ""
        if name == "ja-kanji":
            # XXX extract?
            return ""
        if name == "picdic" or name == "picdicimg" or name == "picdiclabel":
            # XXX extract?
            return ""
        # if name in ("tlb", "term-context", "term-label", "tcx"):
        #     i = 2
        #     while True:
        #         v = ht.get(i)
        #         if v is None:
        #             break
        #         v = clean_value(config, v)
        #         data_append(ctx, pos_data, "tags", v)
        #         i += 1
        #     return ""
        if name == "head":
            t = ht.get(2, "")
            if t == "pinyin":
                data_append(ctx, pos_data, "tags", "Pinyin")
            elif t == "romanization":
                data_append(ctx, pos_data, "tags", "romanization")
        m = re.search(head_tag_re, name)
        if m:
            new_ht = {}
            for k, v in ht.items():
                new_ht[decode_html_entities(k)] = decode_html_entities(v)
            new_ht["template_name"] = name
            data_append(ctx, pos_data, "heads", new_ht)
        return None

    def parse_part_of_speech(posnode, pos):
        """Parses the subsection for a part-of-speech under a language on
        a page."""
        assert isinstance(posnode, WikiNode)
        assert isinstance(pos, str)
        # print("parse_part_of_speech", pos)
        pos_data["pos"] = pos
        pre = []
        have_subtitle = False
        lists = []
        first_para = True
        for node in posnode.children:
            if isinstance(node, str):
                for m in re.finditer(r"\n+|[^\n]+", node):
                    p = m.group(0)
                    if p.startswith("\n\n") and pre:
                        first_para = False
                        break
                    if p:
                        pre.append(p)
                continue
            assert isinstance(node, WikiNode)
            kind = node.kind
            if kind == NodeKind.LIST:
                lists.append(node)
                break
            elif kind in LEVEL_KINDS:
                break
            elif kind == NodeKind.LINK:
                # We might collect relevant links as they are often pictures
                # relating to the word
                if (len(node.args[0]) >= 1 and
                    isinstance(node.args[0][0], str) and
                    (node.args[0][0].startswith("File:") or
                     node.args[0][0].startswith("Image:"))):
                    continue
                pre.extend(node.args[-1])
            elif kind == NodeKind.HTML:
                if node.args not in ("gallery", "ref", "cite", "caption"):
                    pre.append(node)
            elif first_para:
                pre.append(node)
        # XXX use template_fn in clean_node to check that the head macro
        # is compatible with the current part-of-speech and generate warning
        # if not.  Use template_allowed_pos_map.
        # print("parse_part_of_speech: {}: {}: pre={}"
        #       .format(ctx.section, ctx.subsection, pre))
        text = clean_node(config, ctx, pos_data, pre,
                          template_fn=head_template_fn)
        parse_word_head(ctx, pos, text, pos_data)
        if "tags" in pos_data:
            common_tags = pos_data["tags"]
            del pos_data["tags"]
        else:
            common_tags = []
        for node in lists:
            for node in node.children:
                if node.kind != NodeKind.LIST_ITEM:
                    ctx.warning("{}: non-list-item inside list".format(pos))
                    continue
                if node.args[-1] == ":":
                    # Sometimes there may be lists with indented examples
                    # in otherwise the same level as real sense entries.
                    # I assume those will get parsed as separate lists, but
                    # we don't want to include such examples as word senses.
                    continue
                contents = node.children
                sublists = [x for x in contents
                            if isinstance(x, WikiNode) and
                            x.kind == NodeKind.LIST and
                            x.args == "##"]
                others = [x for x in contents
                          if isinstance(x, WikiNode) and
                          x.kind == NodeKind.LIST and
                          x.args != "##"]

                # This entry has sublists of entries.  We should contain
                # gloss information from both.  Sometimes the outer gloss
                # is more non-gloss or tags, sometimes it is a coarse sense
                # and the inner glosses are more specific.  The outer one does
                # not seem to have qualifiers.
                outer = [x for x in contents
                         if not isinstance(x, WikiNode) or
                         x.kind != NodeKind.LIST]
                common_data = {}
                common_data["tags"] = list(common_tags)

                # If we have one sublist with one element, treat it specially as
                # it may be a Wiktionary error; raise that nested element
                # to the same level.
                if len(sublists) == 1:
                    slc = sublists[0].children
                    if len(slc) == 1:
                        parse_sense(pos, outer, common_data)
                        parse_sense(pos, slc[0].children, {})
                        continue

                def outer_template_fn(name, ht):
                    if is_panel_template(name):
                        return ""
                    if name in ("defdate",):
                        return ""
                    if name in sense_linkage_templates:
                        parse_sense_linkage(config, ctx, common_data, name, ht)
                        return ""
                    return None

                # Process others, so that we capture any sense linkages from
                # there
                clean_node(config, ctx, common_data, others,
                           template_fn=outer_template_fn)

                # If there are no sublists of senses, parse it as just one
                if not sublists:
                    parse_sense(pos, contents, common_data)
                    continue

                # Clean the outer gloss
                outer_text = clean_node(config, ctx, common_data, outer,
                                        template_fn=outer_template_fn)
                strip_ends = [", particularly:"]
                for x in strip_ends:
                    if outer_text.endswith(x):
                        outer_text = outer_text[:-len(x)]
                        break
                # Check if the outer gloss starts with parenthesized tags/topics
                m = re.match(r"\(([^()]+)\):?\s*", outer_text)
                if m:
                    q = m.group(1)
                    outer_text = outer_text[m.end():].strip()
                    parse_sense_qualifier(ctx, q, common_data)

                if outer_text == "A pejorative:":
                    data_append(ctx, common_data, "tags", "perjorative")
                    outer_text = None
                elif outer_text == "Short forms.":
                    data_append(ctx, common_data, "tags", "abbreviation")
                    outer_text = None
                elif outer_text == "Technical or specialized senses.":
                    outer_text = None
                # XXX is it always a gloss?  Maybe non-gloss?
                if outer_text:
                    data_append(ctx, common_data, "glosses", outer_text)

                # Process any inner glosses
                added = False
                for sublist in sublists:
                    assert sublist.kind == NodeKind.LIST
                    for item in sublist.children:
                        if not isinstance(item, WikiNode):
                            continue
                        if item.kind != NodeKind.LIST_ITEM:
                            continue
                        sense_base = copy.deepcopy(common_data)
                        if parse_sense(pos, item.children, sense_base):
                            added = True
                # If the sublists resulted in no senses added, add
                # common_data as a sense if it has a gloss
                if not added and common_data.get("glosses"):
                    gls = common_data.get("glosses") or [""]
                    assert len(gls) == 1
                    common_data["glosses"] = []
                    parse_sense(pos, gls, common_data)

    def parse_pronunciation(node):
        """Parses the pronunciation section from a language section on a
        page."""
        assert isinstance(node, WikiNode)
        if node.kind in LEVEL_KINDS:
            contents = node.children
        else:
            contents = [node]
        # Remove subsections, such as Usage notes.  They may contain IPAchar
        # templates in running text, and we do not want to extract IPAs from
        # those.
        contents = [x for x in contents
                    if not isinstance(x, WikiNode) or x.kind not in LEVEL_KINDS]

        data = etym_data if etym_data else base
        enprs = []
        audios = []
        rhymes = []
        have_panel_templates = False

        def parse_pronunciation_template_fn(name, ht):
            nonlocal have_panel_templates
            if is_panel_template(name):
                have_panel_templates = True
                return ""
            if name == "enPR":
                enpr = ht.get(1)
                if enpr:
                    enprs.append(enpr)
                return ""
            if name == "audio":
                filename = ht.get(2) or ""
                desc = ht.get(3) or ""
                desc = clean_node(config, ctx, None, [desc])
                audio = {"audio": filename}
                if desc:
                    audio["text"] = desc
                m = re.search(r"\((([^()]|\([^()]*\))*)\)", desc)
                skip = False
                if m:
                    par = m.group(1)
                    cls = classify_desc(par)
                    if cls == "tags":
                        parse_pronunciation_tags(ctx, par, audio)
                    else:
                        skip = True
                if skip:
                    return ""
                audios.append(audio)
                return "__AUDIO_IGNORE_THIS__" + str(len(audios) - 1) + "__"
            if name == "audio-IPA":
                filename = ht.get(2) or ""
                ipa = ht.get(3) or ""
                dial = ht.get("dial")
                audio = {"audio": filename}
                if dial:
                    dial = clean_node(config, ctx, None, [dial])
                    audio["text"] = dial
                if ipa:
                    audio["audio-ipa"] = ipa
                audios.append(audio)
                # The problem with these IPAs is that they often just describe
                # what's in the sound file, rather than giving the pronunciation
                # of the word alone.  It is common for audio files to contain
                # multiple pronunciations or articles in the same file, and then
                # this IPA often describes what is in the file.
                return "__AUDIO_IGNORE_THIS__" + str(len(audios) - 1) + "__"
            if name == "audio-pron":
                filename = ht.get(2) or ""
                ipa = ht.get("ipa")
                dial = ht.get("dial")
                country = ht.get("country")
                audio = {"audio": filename}
                if dial:
                    dial = clean_node(config, ctx, None, [dial])
                    audio["text"] = dial
                    parse_pronunciation_tags(ctx, dial, audio)
                if country:
                    parse_pronunciation_tags(ctx, country, audio)
                if ipa:
                    audio["audio-ipa"] = ipa
                audios.append(audio)
                # XXX do we really want to extract pronunciations from these?
                # Or are they spurious / just describing what is in the
                # audio file?
                # if ipa:
                #     pron = {"ipa": ipa}
                #     if dial:
                #         parse_pronunciation_tags(ctx, dial, pron)
                #     if country:
                #         parse_pronunciation_tags(ctx, country, pron)
                #     data_append(ctx, data, "sounds", pron)
                return "__AUDIO_IGNORE_THIS__" + str(len(audios) - 1) + "__"
            return None

        def parse_pron_post_template_fn(name, ht, text):
            if name in ("q", "qualifier", "sense", "a", "accent",
                        "l", "link", "lb", "lbl", "label"):
                # Kludge: when these templates expand to /.../ or [...],
                # replace the expansion by the empty string.  This is used
                # to filter spurious IPA-looking expansions that aren't really
                # IPAs.  We probably don't care about these tempates in the
                # contexts where they expand to something containing these.
                v = re.sub(r'href="[^"]*"', "", text)  # Ignore URLs
                v = re.sub(r'src="[^"]*"', "", v)
                if re.search(r"/[^/,]+?/|\[[^]0-9,/][^],/]*?\]", v):
                    return ""
            return text

        # XXX change this code to iterate over node as a LIST, warning about
        # anything else.  Don't try to split by "*".
        # XXX fix enpr tags
        text = clean_node(config, ctx, data, contents,
                          template_fn=parse_pronunciation_template_fn)
        ipa_text = clean_node(config, ctx, data, contents,
                              post_template_fn=parse_pron_post_template_fn)
        have_pronunciations = False
        text_splits = re.split(r"[*#]+", text)
        ipa_splits = re.split(r"[*#]+", ipa_text)
        if len(text_splits) != len(ipa_splits):
            ctx.warning("text_splits length differs from ipa_splits: "
                        "{!r} vs. {!r}"
                        .format(text, ipa_text))
            ipa_splits = text_splits
        for origtext, ipa_text in zip(text_splits, ipa_splits):
            text = origtext
            m = re.match(r"^[*#\s]*\((([^()]|\([^()]*\))*?)\)", text)
            if m:
                tagstext = m.group(1)
                text = text[m.end():]
            else:
                tagstext = ""
            if origtext.find("IPA") >= 0:
                field = "ipa"
            else:
                # This is used for Rhymes, Homophones, etc
                field = "other"
            # Check if it contains Japanese "Tokyo" pronunciation with
            # special syntax
            m = re.search(r"\(Tokyo\) +([^ ]+) +\[", origtext)
            if m:
                pron = {field: m.group(1)}
                parse_pronunciation_tags(ctx, tagstext, pron)
                data_append(ctx, data, "sounds", pron)
                have_pronunciations = True
            # Check if it contains Rhymes
            m = re.search(r"\bRhymes: ([^\s,]+(,\s*[^\s,]+)*)", text)
            if m:
                for ending in m.group(1).split(","):
                    ending = ending.strip()
                    if ending:
                        pron = {"rhymes": ending}
                        parse_pronunciation_tags(ctx, tagstext, pron)
                        data_append(ctx, data, "sounds", pron)
                        have_pronunciations = True
            # Check if it contains homophones
            m = re.search(r"\bHomophones?: ([^\s,]+(,\s*[^\s,]+)*)", text)
            if m:
                for w in m.group(1).split(","):
                    w = w.strip()
                    if w:
                        pron = {"homophone": w}
                        parse_pronunciation_tags(ctx, tagstext, pron)
                        data_append(ctx, data, "sounds", pron)
                        have_pronunciations = True

            for m in re.finditer(r"/[^/,]+?/|\[[^]0-9,/][^],/]*?\]", ipa_text):
                v = m.group(0)
                # The regexp above can match file links.  Skip them.
                if v.startswith("[[File:"):
                    continue
                if v == "/wiki.local/":
                    continue
                if field == "ipa" and text.find("__AUDIO_IGNORE_THIS__") >= 0:
                    m = re.search(r"__AUDIO_IGNORE_THIS__(\d+)__", text)
                    assert m
                    idx = int(m.group(1))
                    if not audios[idx].get("audio-ipa"):
                        audios[idx]["audio-ipa"] = v
                else:
                    pron = {field: v}
                    parse_pronunciation_tags(ctx, tagstext, pron)
                    data_append(ctx, data, "sounds", pron)
                have_pronunciations = True

            # XXX what about {{hyphenation|...}}, {{hyph|...}}
            # and those used to be stored under "hyphenation"
            m = re.search(r"\b(Syllabification|Hyphenation): ([^\s,]*)", text)
            if m:
                data_append(ctx, data, "hyphenation", m.group(2))
                have_pronunciations = True

        # Add data that was collected in template_fn
        if audios:
            data_extend(ctx, data, "sounds", audios)
            have_pronunciations = True
        for enpr in enprs:
            pron = {"enpr": enpr}
            # XXX need to parse enpr separately for each list item to get
            # tags correct!
            # parse_pronunciation_tags(ctx, tagstext, pron)
            data_append(ctx, data, "sounds", pron)
            have_pronunciations = True

        if not have_pronunciations and not have_panel_templates:
            ctx.debug("no pronunciations found from pronunciation section")

    def parse_inflection(node):
        """Parses inflection data (declension, conjugation) from the given
        page.  This retrieves the actual inflection template
        parameters, which are very useful for applications that need
        to learn the inflection classes and generate inflected
        forms."""
        # print("parse_inflection:", node)
        assert isinstance(node, WikiNode)
        captured = False

        def inflection_template_fn(name, ht):
            # print("decl_conj_template_fn", name, ht)
            if is_panel_template(name):
                return ""
            if name in ("is-u-mutation",):
                # These are not to be captured as an exception to the
                # generic code below
                return None
            m = re.search(r"-(conj|decl|ndecl|adecl|infl|conjugation|"
                          r"declension|inflection|mut|mutation)($|-)", name)
            if m:
                new_ht = {}
                # Convert html entities that may be used in the arguments
                for k, v in ht.items():
                    v = clean_value(config, v, no_strip=True)
                    v = decode_html_entities(v)
                    new_ht[decode_html_entities(k)] = v
                new_ht["template_name"] = name
                data_append(ctx, pos_data, "inflection", new_ht)
                nonlocal captured
                captured = True
                return ""

            return None

        # Clean the node.  This captures category links and calls the template
        # function.
        clean_node(config, ctx, etym_data, node,
                   template_fn=inflection_template_fn)
        # XXX try to parse either a WikiText table or a HTML table that
        # contains the inflectional paradigm
        # XXX should we try to capture it even if we got the template?

    def get_subpage_section(language, title, subtitle, pos, section):
        """Loads a subpage of the given page, and finds the section
        for the given language, part-of-speech, and section title.  This
        is used for finding translations and other sections on subpages."""
        assert isinstance(language, str)
        assert isinstance(title, str)
        assert isinstance(subtitle, str)
        assert isinstance(pos, str)
        assert isinstance(section, str)
        subpage_title = word + "/" + subtitle
        subpage_content = ctx.read_by_title(subpage_title)
        if subpage_content is None:
            ctx.error("/translations not found despite "
                      "{{see translation subpage|...}}")

        def recurse(node, seq):
            if not seq:
                return node
            if not isinstance(node, WikiNode):
                return None
            if node.kind in LEVEL_KINDS:
                t = clean_node(config, ctx, None, node.args[0])
                if t == seq[0]:
                    seq = seq[1:]
                    if not seq:
                        return node
            for n in node.children:
                ret = recurse(n, seq)
                if ret is not None:
                    return ret
            return None

        tree = ctx.parse(subpage_content, pre_expand=True,
                         additional_expand=additional_expand_templates)
        assert tree.kind == NodeKind.ROOT
        seq = [language, pos, section]
        ret = recurse(tree, seq)
        if ret is None:
            ctx.warning("Failed to find subpage section {} {}/{} {} {}"
                        .format(language, title, subtitle, pos, section))
        return ret

    def parse_linkage(data, field, linkagenode):
        assert isinstance(data, dict)
        assert isinstance(field, str)
        assert isinstance(linkagenode, WikiNode)
        # print("PARSE_LINKAGE:", linkagenode)
        if not config.capture_linkages:
            return
        have_linkages = False
        have_panel_template = False
        toplevel_text = []

        def parse_linkage_item(contents, field, sense):
            assert isinstance(contents, (list, tuple))
            assert isinstance(field, str)
            assert sense is None or isinstance(sense, str)
            nonlocal have_linkages

            # print("PARSE_LINKAGE_ITEM: {} ({}): {}"
            #       .format(field, sense, contents))

            parts = []
            ruby = ""
            base_roman = None
            base_alt = None
            base_qualifier = None

            # If ``sense`` can be parsed as tags, treat it as tags instead
            if sense:
                cls = classify_desc(sense)
                if cls == "tags":
                    base_qualifier = sense
                    sense = None

            def item_recurse(contents, italic=False):
                assert isinstance(contents, (list, tuple))
                nonlocal have_linkages
                nonlocal sense
                nonlocal ruby
                nonlocal parts
                # print("ITEM_RECURSE:", contents)
                for node in contents:
                    if isinstance(node, str):
                        # XXX remove:
                        # if italic:
                        #     if qualifier:
                        #         qualifier += node
                        #     else:
                        #         qualifier = node
                        parts.append(node)
                        continue
                    kind = node.kind
                    # print("ITEM_RECURSE KIND:", kind, node.args)
                    if kind == NodeKind.LIST:
                        if parts:
                            sense1 = clean_node(config, ctx, None, parts)
                            if sense1.endswith(":"):
                                sense1 = sense1[:-1].strip()
                            if sense1.startswith("(") and sense1.endswith(")"):
                                sense1 = sense1[1:-2].strip()
                            if sense1 == "Translations":
                                sense1 = None
                            # print("linkage item_recurse LIST sense1:", sense1)
                            parse_linkage_recurse(node.children, field,
                                                  sense=sense1 or sense)
                            parts = []
                        else:
                            parse_linkage_recurse(node.children, field, sense)
                    elif kind in (NodeKind.TABLE, NodeKind.TABLE_ROW,
                                  NodeKind.TABLE_CELL):
                        parse_linkage_recurse(node.children, field, sense)
                    elif kind in (NodeKind.TABLE_HEADER_CELL,
                                  NodeKind.TABLE_CAPTION):
                        continue
                    elif kind == NodeKind.HTML:
                        classes = (node.attrs.get("class") or "").split()
                        if node.args in ("gallery", "ref", "cite", "caption"):
                            continue
                        elif node.args == "rp":
                            continue  # Parentheses inside <ruby>
                        elif node.args == "rt":
                            ruby += clean_node(config, ctx, None, node)
                            continue
                        elif "interProject" in classes:
                            continue  # These do not seem to be displayed
                        if "NavFrame" in classes:
                            parse_linkage_recurse(node.children, field, sense)
                        else:
                            item_recurse(node.children, italic=italic)
                    elif kind == NodeKind.ITALIC:
                        item_recurse(node.children, italic=True)
                    elif kind == NodeKind.LINK:
                        ignore = False
                        if isinstance(node.args[0][0], str):
                            v = node.args[0][0].strip().lower()
                            if (v.startswith("category:") or
                                v.startswith("image:") or
                                v.startswith("file:")):
                                ignore = True
                            if not ignore:
                                item_recurse(node.args[-1], italic=italic)
                    elif kind == NodeKind.URL:
                        item_recurse(node.args[-1], italic=italic)
                    elif kind in (NodeKind.PREFORMATTED, NodeKind.BOLD):
                        item_recurse(node.children, italic=italic)
                    else:
                        ctx.debug("linkage item_recurse unhandled: {}"
                                  .format(node))

            item_recurse(contents)
            item = clean_node(config, ctx, None, parts)
            # print("CLEANED ITEM: {!r}".format(item))
            item = re.sub(r", \)", ")", item)
            item = re.sub(r"\(\)", "", item)
            item = re.sub(r"\s\s+", " ", item)
            item = item.strip()

            # If the item is a reference to the thesaurus, skip it.  We should
            # be injecting data from the thesaurus in each word referenced
            # from it.
            lst = item.split(" ")
            if item.startswith("See also Thesaurus:"):
                item = ""
                have_linkages = True
            elif item.startswith("See also Appendix:"):
                item = ""
                have_linkages = True
            elif item.startswith("See also "):
                item = item[9:]
            elif item.startswith("See "):
                item = item[4:]
            elif item.startswith("Appendix:"):
                item = ""
                have_linkages = True
            elif item.startswith("Category:") or item.startswith(":Category:"):
                item = ""
                have_linkages = True
            elif item.startswith("Entries in the "):
                item = ""
                have_linkages = True
            elif item.startswith("Wikipedia article "):
                item = ""
                have_linkages = True
            elif item.endswith(" Wikipedia"):
                item = ""
                have_linkages = True
            elif item.endswith(" Wikipedia."):
                item = ""
                have_linkages = True
            elif (len(lst) > 2 and
                  lst[0] in (word, word.capitalize()) and
                  lst[1] in ("in", "on")):
                # E.g., harness in the Encyclopaedia Britannica...
                item = ""
                have_linkages = True

            if item.startswith(":"):
                item = item[1:]
            item = item.strip()

            # print("    LINKAGE ITEM: {}: {} (sense {})"
            #       .format(field, item, sense))

            # Replace occurrences of ~ in the item by the page title
            safetitle = ctx.title.replace("\\", "\\\\")
            item = re.sub(r" ~ ", " " + safetitle + " ", item)
            item = re.sub(r"^~ ", safetitle + " ", item)
            item = re.sub(r" ~$", " " + safetitle, item)

            # Some Korean words use "word (romanized): english" pattern
            m = re.match(r"(.+?) \(([^()]+)\): ([-a-zA-Z0-9,. ]+)$", item)
            if m:
                base_roman = m.group(2)
                english = m.group(3)
                item = m.group(1)
                lst = base_roman.split(", ")
                if len(lst) == 2 and classify_desc(lst[0]) == "other":
                    base_alt = lst[0]
                    base_roman = lst[1]
                if sense:
                    sense += "; " + english
                else:
                    sense = english

            # Many words have tags or similar descriptions in the beginning
            # followed by a colon and one or more linkages (e.g.,
            # panetella/Finnish)
            m = re.match(r"^\(?([a-zA-Z ]+)\)?: (.*)$", item)
            if m:
                desc, rest = m.groups()
                # print("linkage colon prefix desc={!r} rest={!r}"
                #      .format(desc, rest))
                cls = classify_desc(desc)
                if cls == "tags":
                    if base_qualifier:
                        base_qualifier += " " + desc
                    else:
                        base_qualifier = desc
                    item = rest
                elif cls == "english":
                    if sense:
                        sense += ";" + desc
                    else:
                        sense = desc
                    item = rest
                else:
                    ctx.debug("unrecognized linkage prefix: {}"
                              .format(item))

            # Various words have a sense or tags in parenthesis (sometimes
            # followed by a colon) at the start of the item
            m = re.match(r"\((([^()]|\([^()]*\))*)\):?\s*", item)
            if m:
                par = m.group(1)

                # Check for certain comma-separated tags combined
                # with English text at the beginning or end of a
                # comma-separated parenthesized list
                lst = par.split(", ")
                while len(lst) > 1:
                    cls = classify_desc(lst[0])
                    if cls == "tags":
                        if base_qualifier:
                            base_qualifier += " " + lst[0]
                        else:
                            base_qualifier = lst[0]
                        lst = lst[1:]
                        continue
                    cls = classify_desc(lst[-1])
                    if cls == "tags":
                        if base_qualifier:
                            base_qualifier += " " + lst[-1]
                        else:
                            base_qualifier = lst[-1]
                        lst = lst[:-1]
                        continue
                    break
                par = ", ".join(lst)

                # Classify the item and handle it
                cls = classify_desc(par)
                # print("parenthesized prefix: {} -> {}".format(par, cls))
                if cls == "tags":
                    base_qualifier = par
                    item = item[m.end():]
                elif cls in ("english", "taxonomic"):
                    if sense:
                        sense += "; " + par
                    else:
                        sense = par
                    item = item[m.end():]
                else:
                    # Otherwise we won't handle it here
                    ctx.debug("unhandled parenthesized prefix: {}"
                              .format(item))

            base_sense = sense

            # Certain linkage items have space-separated valus.  These are
            # generated by, e.g., certain templates
            if base_sense:
                if base_sense in ("A paper sizes",
                                  "Arabic digits"):
                    base_qualifier = None
                    item = ", ".join(item.split())
                elif (base_sense in (
                        "Arabic digits",
                        "Latin script",
                        "Latin script letters",
                        "Latin-script letters",
                        "Latvian letters") or
                      base_sense.startswith("Variations of letter ")):
                    base_qualifier = None
                    idx = item.find("; ")
                    if idx >= 0:
                        prefix = item[:idx]
                        item = item[idx + 2:]
                    else:
                        prefix = None
                    lst = item.split(", ")
                    if len(lst) > 5:
                        if lst[0].count(" ") == 1:
                            item = ", ".join(x for x in re.split(r",| ", item)
                                             if x not in (" ", ","))
                        else:
                            item = ", ".join(x for x in
                                             list(m.group(0) for m in
                                                  re.finditer(unicode_dc_re,
                                                              item))
                                             if x not in (" ", ","))
                    if prefix:
                        item = prefix + "; " + item

            # XXX temporarily disabled.  These should be analyzed.
            #if item.find("(") >= 0 and item.find(", though ") < 0:
            #    ctx.debug("linkage item has remaining parentheses: {}"
            #              .format(item))

            item = re.sub(r"\s*\^?\s*\(\s*\)", "", item)
            item = item.strip()
            if not item:
                return
            # The item may contain multiple comma-separated linkages
            if base_roman:
                subitems = [item]
            elif ctx.title.find(" or ") < 0:
                subitems = split_at_comma_semi(item, extra=[" or "])
            else:
                subitems = split_at_comma_semi(item)
            if len(subitems) > 1:  # Would be merged from multiple subitems
                ruby = ""
            for item1 in subitems:
                if len(subitems) > 1 and item1 in ("...", "…"):
                    # Some lists have ellipsis in the middle - don't generate
                    # linkages for the ellipsis
                    continue
                item1 = item1.strip()
                qualifier = base_qualifier
                sense = base_sense
                parts = []
                roman = base_roman  # Usually None
                alt = base_alt  # Usually None
                taxonomic = None
                english = None

                words = item1.split(" ")
                if len(words) > 1 and words[0] in linkage_beginning_tags:
                    t = linkage_beginning_tags[words[0]]
                    item1 = " ".join(words[1:])
                    if qualifier:
                        qualifier += " " + t
                    else:
                        qualifier = t

                # Extract quoted English translations (there are also other
                # kinds of English translations)
                def english_repl(m):
                    nonlocal sense
                    nonlocal qualifier
                    v = m.group(1).strip()
                    # If v is "tags: sense", handle the tags
                    m = re.match(r"^([a-zA-Z ]+): (.*)$", v)
                    if m:
                        desc, rest = m.groups()
                        if classify_desc(desc) == "tags":
                            if qualifier:
                                qualifier += " " + desc
                            else:
                                qualifier = desc
                            v = rest
                    if sense:
                        sense += "; " + v
                    else:
                        sense = v
                    return ""

                item1 = re.sub(r'[“"]([^"]+)[“"],?\s*', english_repl, item1)
                item1 = re.sub(r", \)", ")", item1)

                # There could be multiple parenthesized parts, and
                # sometimes both at the beginning and at the end
                while True:
                    par = None
                    if par is None:
                        m = re.match(r"\((([^()]|\([^()]*\))*)\):?\s*", item1)
                        if m:
                            par = m.group(1)
                            item1 = item1[m.end():]
                        else:
                            m = re.search(" \((([^()]|\([^()]*\))*)\)\.?$",
                                          item1)
                            if m:
                                par = m.group(1)
                                item1 = item1[:m.start()]
                    if not par:
                        break
                    # Handle tags from beginning of par.  We also handle "other"
                    # here as Korean entries often have Hanja form in the
                    # beginning of parenthesis, before romanization.  Similar
                    # for many Japanese entries.
                    while par:
                        idx = par.find(",")
                        if idx < 0:
                            break
                        cls = classify_desc(par[:idx])
                        if cls == "other" and not alt:
                            alt = par[:idx]
                        elif cls == "taxonomic":
                            taxonomic = par[:idx]
                        elif cls == "tags":
                            if qualifier:
                                qualifier += " " + par[:idx]
                            else:
                                qualifier = par[:idx]
                        else:
                            break
                        par = par[idx + 1:].strip()

                    # Check for certain comma-separated tags combined
                    # with English text at the beginning or end of a
                    # comma-separated parenthesized list
                    lst = par.split(", ")
                    while len(lst) > 1:
                        cls = classify_desc(lst[0])
                        if cls == "tags":
                            if qualifier:
                                qualifier += " " + lst[0]
                            else:
                                qualifier = lst[0]
                            lst = lst[1:]
                            continue
                        cls = classify_desc(lst[-1])
                        if cls == "tags":
                            if qualifier:
                                qualifier += " " + lst[-1]
                            else:
                                qualifier = lst[-1]
                            lst = lst[:-1]
                            continue
                        break
                    par = ", ".join(lst)

                    # Handle remaining types
                    if not par:
                        continue
                    cls = classify_desc(par)
                    # print("classify_desc: {} -> {}".format(par, cls))
                    if cls == "tags":
                        if qualifier:
                            qualifier += " " + par
                        else:
                            qualifier = par
                    elif cls == "english":
                        if sense:
                            sense += "; " + par
                        else:
                            sense = par
                    elif cls == "romanization":
                        roman = par
                    elif cls == "taxonomic":
                        taxonomic = par
                    else:
                        if alt:
                            alt += "; " + par
                        else:
                            alt = par

                # Parse linkages with "value = english" syntax (e.g.,
                # väittää/Finnish)
                idx = item1.find(" = ")
                if idx >= 0:
                    eng = item1[idx + 3:]
                    if classify_desc(eng) == "english":
                        english = eng
                        item1 = item1[:idx]
                    else:
                        # Some places seem to use it reversed "english = value"
                        eng = item1[:idx]
                        if classify_desc(eng) == "english":
                            english = eng
                            item1 = item1[idx + 3:]

                # Parse linkages with "value - english" syntax (e.g.,
                # man/Faroese)
                idx = item1.find(" - ")
                if idx >= 0:
                    eng = item1[idx + 3:]
                    if classify_desc(eng) == "english":
                        english = eng
                        item1 = item1[:idx]

                if item1.startswith("see Thesaurus:"):
                    item1 = item1[14:]
                elif item1.startswith("see also Thesaurus:"):
                    item1 = item1[19:]
                elif item1.startswith("Thesaurus:"):
                    item1 = item1[10:]
                elif item1.startswith("see more at Thesaurus:"):
                    item1 = item1[22:]

                # Parse certain tags at the end of the linked term
                lang = ctx.section
                item1, q = parse_head_final_tags(ctx, lang, item1)
                if q:
                    if qualifier:
                        qualifier += " " + " ".join(q)
                    else:
                        qualifier = " ".join(q)

                if not item1:
                    continue  # Ignore empty link targets
                if item1 == word:
                    continue  # Ignore self-links

                def add(w, r):
                    nonlocal alt
                    nonlocal taxonomic
                    nonlocal have_linkages
                    # Filter out certain words that are used in linkages but
                    # are generally not intended as a linked word.
                    if w in ("etc.", "other derived terms:"):
                        return

                    # Check if the word contains the Fullwith Solidus, and if
                    # so, split by it and treat the the results as alternative
                    # linkages.  (This is very commonly used for alternative
                    # written forms in Chinese compounds and other linkages.)
                    # However, if the word contains a comma, then we wont't
                    # split as this is used when we have a different number
                    # of romanizations than written forms, and don't know
                    # which is which.
                    if ((not w or w.find(",") < 0) and
                        (not r or r.find(",") < 0)):
                        lst = w.split("／")
                        if len(lst) > 1:
                            # Treat each alternative as separate linkage
                            for w in lst:
                                add(w, r)
                            return
                    # If we have roman but not alt and the word is ASCII,
                    # move roman to alt.
                    if r and not alt and w.isascii():
                        alt = r
                        r = None
                    # Add the linkage
                    dt = {}
                    if qualifier:
                        parse_sense_qualifier(ctx, qualifier, dt)
                    if sense:
                        dt["sense"] = sense
                    if r:
                        dt["roman"] = r
                    if ruby:
                        dt["ruby"] = ruby
                    if alt:
                        dt["alt"] = alt
                    if english:
                        dt["english"] = english
                    if taxonomic:
                        if re.match(r"×[A-Z]", taxonomic):
                            data_append(ctx, dt, "tags", "extinct")
                            taxonomic = taxonomic[1:]
                        dt["taxonomic"] = taxonomic
                    if re.match(r"×[A-Z]", w):
                        data_append(ctx, dt, "tags", "extinct")
                        w = w[1:]  # Remove × before dead species names
                    if alt and re.match(r"×[A-Z]", alt):
                        data_append(ctx, dt, "tags", "extinct")
                        alt = alt[1:]  # Remove × before dead species names
                    dt["word"] = w
                    for old in data.get(field, ()):
                        if dt == old:
                            break
                    else:
                        data_append(ctx, data, field, dt)
                        have_linkages = True

                if sense in ("Cyrillic-script letters",):
                    ws = item1.split(" ")
                    if roman:
                        rs = roman.split(" ")
                    elif len(ws) == 2 and ws[0].isupper() and ws[1].islower():
                        rs = [None] * len(ws)
                    else:
                        rs = None
                    if rs and len(ws) > 1 and len(ws) == len(rs):
                        for w, r in zip(ws, rs):
                            add(w, r)
                        continue
                add(item1, roman)

        def parse_linkage_template(node):
            nonlocal have_panel_template
            # XXX remove this function but check how to handle the
            # template_linkage_mappings
            # print("LINKAGE TEMPLATE:", node)

            def linkage_template_fn(name, ht):
                # print("LINKAGE_TEMPLATE_FN:", name, ht)
                nonlocal field
                nonlocal have_panel_template
                if is_panel_template(name):
                    have_panel_template = True
                    return ""
                for prefix, t in template_linkage_mappings:
                    if re.search(r"(^|[-/\s]){}($|\b|[0-9])".format(prefix),
                                 name):
                        f = t if isinstance(t, str) else field
                        if (name.endswith("-top") or name.endswith("-bottom") or
                            name.endswith("-mid")):
                            field = f
                            return ""
                        i = t if isinstance(t, int) else 2
                        while True:
                            v = ht.get(i, None)
                            if v is None:
                                break
                            v = clean_node(config, ctx, None, v)
                            parse_linkage_item(v, f)
                            i += 1
                        return ""
                # print("UNHANDLED LINKAGE TEMPLATE:", name, ht)
                return None

            # Main body of parse_linkage_template()
            text = ctx.node_to_wikitext(node)
            parsed = ctx.parse(text, expand_all=True,
                               template_fn=linkage_template_fn)
            parse_linkage_recurse(parsed.children, field, Node)

        def parse_linkage_recurse(contents, field, sense):
            assert isinstance(contents, (list, tuple))
            assert sense is None or isinstance(sense, str)
            # print("PARSE_LINKAGE_RECURSE: {}: {}".format(sense, contents))
            for node in contents:
                if isinstance(node, str):
                    # Ignore top-level text, generally comments before the
                    # linkages list.  However, if no linkages are found, then
                    # use this for linkages (not all words use bullet points
                    # for linkages).
                    toplevel_text.append(node)
                    continue
                assert isinstance(node, WikiNode)
                kind = node.kind
                # print("PARSE_LINKAGE_RECURSE CHILD", kind)
                if kind == NodeKind.LIST:
                    parse_linkage_recurse(node.children, field, sense)
                elif kind == NodeKind.LIST_ITEM:
                    parse_linkage_item(node.children, field, sense)
                elif kind in (NodeKind.TABLE, NodeKind.TABLE_ROW):
                    parse_linkage_recurse(node.children, field, sense)
                elif kind == NodeKind.TABLE_CELL:
                    parse_linkage_item(node.children, field, sense)
                elif kind in (NodeKind.TABLE_CAPTION,
                              NodeKind.TABLE_HEADER_CELL,
                              NodeKind.PREFORMATTED, NodeKind.BOLD):
                    continue
                elif kind == NodeKind.HTML:
                    # Recurse to process inside the HTML for most tags
                    if node.args in ("gallery", "ref", "cite", "caption"):
                        continue
                    classes = (node.attrs.get("class") or "").split()
                    if "qualifier-content" in classes:
                        sense1 = clean_node(config, ctx, None, node.children)
                        if sense1.endswith(":"):
                            sense1 = sense1[:-1].strip()
                        if sense and sense1:
                            ctx.debug("linkage qualifier-content on multiple "
                                      "levels: {!r} and {!r}"
                                      .format(sense, sense1))
                        parse_linkage_recurse(node.children, field, sense1)
                    else:
                        parse_linkage_recurse(node.children, field, sense)
                elif kind in LEVEL_KINDS:
                    # Just recurse to any possible subsections
                    parse_linkage_recurse(node.children, field, sense)
                elif kind in (NodeKind.BOLD, NodeKind.ITALIC):
                    # Skip these on top level; at least sometimes bold is
                    # used for indicating a subtitle
                    continue
                elif kind == NodeKind.LINK:
                    # Recurse into the last argument
                    parse_linkage_recurse(node.args[-1], field, sense)
                else:
                    ctx.debug("parse_linkage_recurse unhandled {}"
                              .format(kind))

        def linkage_template_fn1(name, ht):
            nonlocal have_panel_template
            if is_panel_template(name):
                have_panel_template = True
                return ""
            return None

        # Main body of parse_linkage()
        text = ctx.node_to_wikitext(linkagenode.children)
        parsed = ctx.parse(text, expand_all=True,
                           template_fn=linkage_template_fn1)
        parse_linkage_recurse(parsed.children, field, None)
        if not have_linkages and not have_panel_template:
            text = "".join(toplevel_text).strip()
            if (text.find("\n") < 0 and text.find(",") > 0 and
                text.count(",") > 3):
                if text.startswith("See "):
                    have_linkages = True
                else:
                    parse_linkage_item([text], field, None)
            elif text.startswith("See "):
                have_linkages = True
            if not have_linkages and not have_panel_template:
                ctx.debug("no linkages found")

    def parse_translations(data, xlatnode):
        """Parses translations for a word.  This may also pull in translations
        from separate translation subpages."""
        assert isinstance(data, dict)
        assert isinstance(xlatnode, WikiNode)
        # print("===== PARSE_TRANSLATIONS {} {}".format(ctx.title, ctx.section))
        if not config.capture_translations:
            return
        sense_parts = []
        sense = None
        sense_locked = False

        def parse_translation_item(contents, lang=None):
            nonlocal sense
            assert isinstance(contents, list)
            assert lang is None or isinstance(lang, str)
            # print("PARSE_TRANSLATION_ITEM:", contents)

            langcode = None
            if sense is None:
                sense = clean_node(config, ctx, data, sense_parts).strip()
                idx = sense.find("See also translations at")
                if idx > 0:
                    ctx.debug("Skipping translation see also: {}".format(sense))
                    sense = sense[:idx].strip()
                if sense.endswith(":"):
                    sense = sense[:-1].strip()
            sense_detail = None

            def translation_item_template_fn(name, ht):
                nonlocal langcode
                # print("TRANSLATION_ITEM_TEMPLATE_FN:", name, ht)
                if is_panel_template(name):
                    return ""
                if name in ("t+check", "t-check", "t-needed"):
                    # We ignore these templates.  They seem to have outright
                    # garbage in some entries, and very varying formatting in
                    # others.  These should be transitory and unreliable
                    # anyway.
                    return "__IGNORE__"
                if name in ("t", "t+", "t-simple", "t"):
                    code = ht.get(1)
                    if code:
                        if langcode and code != langcode:
                            ctx.warning("differing language codes {} vs "
                                        "{} in translation item: {!r} {}"
                                        .format(langcode, code, name, ht))
                        langcode = code
                    return None
                if name == "t-egy":
                    langcode = "egy"
                    return None
                if name == "ttbc":
                    code = ht.get(1)
                    if code:
                        langcode = code
                    return None
                if name == "trans-see":
                    ctx.error("UNIMPLEMENTED trans-see template")
                    return ""
                if name.endswith("-top"):
                    return ""
                if name.endswith("-bottom"):
                    return ""
                if name.endswith("-mid"):
                    return ""
                #ctx.debug("UNHANDLED TRANSLATION ITEM TEMPLATE: {!r}"
                #             .format(name))
                return None

            sublists = list(x for x in contents
                            if isinstance(x, WikiNode) and
                            x.kind == NodeKind.LIST)
            contents = list(x for x in contents
                            if not isinstance(x, WikiNode) or
                            x.kind != NodeKind.LIST)

            item = clean_node(config, ctx, data, contents,
                              template_fn=translation_item_template_fn)
            # print("    TRANSLATION ITEM: {!r}  [{}]".format(item, sense))

            # Find and remove nested translations from the item
            nested = list(m.group(1)
                          for m in re.finditer(nested_translations_re, item))
            if nested:
                item = re.sub(nested_translations_re, "", item)

            if re.search(r"\(\d+\)|\[\d+\]", item):
                if not item.find("numeral:"):
                    ctx.warning("POSSIBLE SENSE NUMBER IN ITEM: {}"
                                .format(item))

            # Translation items should start with a language name (except
            # some nested translation items don't and rely on the language
            # name from the higher level, and some append a language variant
            # name to a broader language name)
            m = re.match(r"\*?\s*([-' \w][-' \w()]*):\s*", item)
            tags = []
            if m:
                sublang = m.group(1)
                if lang is None:
                    lang = sublang
                elif lang and lang + " " + sublang in languages_by_name:
                    lang = lang + " " + sublang
                elif lang and sublang + " " + lang in languages_by_name:
                    lang = sublang + " " + lang  # E.g., Ancient Egyptian
                elif sublang in languages_by_name:
                    lang = sublang
                elif sublang[0].isupper():
                    # Interpret it as a tag
                    tags.append(sublang)
                else:
                    # We don't recognize this prefix
                    ctx.error("unrecognized prefix (language name?) in "
                              "translation item: {}".format(item))
                    return
                # Strip the language name/tag from the item
                item = item[m.end():]
            elif lang is None:
                # No mathing language prefix
                ctx.error("no language name in translation item: {}"
                          .format(item))
                return
            # If we didn't get language code from the template, look it up
            # based on language name
            if langcode is None:
                if lang in languages_by_name:
                    langcode = languages_by_name[lang]["code"]

            # Remove (<langcode>) parts from the item.  They seem to be
            # generated by {{t+|...}}.
            if langcode:
                item = re.sub(r"\s*\^?\({}\)".format(langcode), "", item)
                if langcode.find("-") >= 0:
                    item = re.sub(r"\s*\^?\({}\)"
                                  .format(langcode.split("-")[0]),
                                  "", item)
                if langcode in ("cmn",):
                    item = re.sub(r"\s*\^?\(zh\)", "", item)
                elif langcode in ("nn", "nb"):
                    item = re.sub(r"\s*\^?\(no\)", "", item)

            # There may be multiple translations, separated by comma
            nested.append(item)
            for item in nested:
                tagsets = []
                topics = []

                for part in split_at_comma_semi(item, extra=[" / ", " ／ "]):
                    if part.endswith(":"):  # E.g. "salt of the earth"/Korean
                        part = part[:-1].strip()
                    if not part:
                        continue

                    # Strip language links
                    tr = {"lang": lang, "code": langcode}
                    if tags:
                        tr["tags"] = list(tags)
                        for t in tagsets:
                            tr["tags"].extend(t)
                    if topics:
                        tr["topics"] = list(topics)
                    if sense:
                        if sense == "Translations to be checked":
                            continue  # Skip such translations
                        elif sense.startswith(":The translations below need "
                                              "to be checked"):
                            continue  # Skip such translations
                        else:
                            tr["sense"] = sense

                    # Check if this part starts with "<tags/english>: <rest>"
                    m = re.match(r"([\w ]+): (.*)$", part)
                    if m:
                        par = m.group(1).strip()
                        rest = m.group(2).strip()
                        if par == "see":
                            # Sometimes we have, e.g., "Different structure
                            # used, see: <word>" (e.g., have/English sense
                            # "To depict as being" Finnish tr)
                            continue
                        cls = classify_desc(par)
                        # print("tr colon prefix: {!r} -> {}".format(par, cls))
                        if cls == "tags":
                            tagsets2, topics2 = decode_tags([par])
                            for t in tagsets2:
                                data_extend(ctx, tr, "tags", t)
                            data_extend(ctx, tr, "topics", topics2)
                            part = rest
                        elif cls == "english":
                            if re.search(tr_note_re, par):
                                if "note" in tr:
                                    tr["note"] += "; " + par
                                else:
                                    tr["note"] = par
                            else:
                                if "english" in tr:
                                    tr["english"] += "; " + par
                                else:
                                    tr["english"] = par
                            part = rest

                    # Skip translations that our template_fn says to ignore
                    # and those that contain Lua execution errors.
                    if part.find("__IGNORE__") >= 0:
                        continue  # Contains something we want to ignore
                    if part.startswith("Lua execution error"):
                        continue

                    # Handle certain suffixes in translations that
                    # we might put in "note" but that we can actually
                    # parse into tags.
                    for suffix, t in (
                            (" with dative", "with-dative"),
                            (" with genitive", "with-genitive"),
                            (" with accusative", "with-accusative"),
                    ):
                        if part.endswith(suffix):
                            part = part[:-len(suffix)]
                            data_append(ctx, tr, "tags", t)
                            break

                    # Certain values indicate it is not actually a translation.
                    # See definition of tr_ignore_re to adjust.
                    m = re.search(tr_ignore_re, part)
                    if (m and (m.start() != 0 or m.end() != len(part) or
                               len(part.split()) > 1)):
                        # This translation will be skipped because it
                        # seems to be some kind of explanatory text.
                        # However, let's put it in the "note" field
                        # instead.
                        tr["note"] = part
                    else:
                        # Interpret it as an actual translation
                        parse_translation_desc(ctx, lang, part, tr)
                        w = tr.get("word")
                        if not w:
                            continue  # Not set or empty
                        if w.startswith("*") or w.startswith(":"):
                            w = w[1:].strip()
                        if w in ("[Term?]", ":", "/", "?"):
                            continue  # These are not valid linkage targets
                        if len(w) > 3 * len(word) + 20:
                            # Likely descriptive text or example
                            del tr["word"]
                            tr["note"] = w

                    # Sanity check: try to detect certain suspicious
                    # patterns in translations
                    if "word" in tr and re.search(tr_suspicious_re, tr["word"]):
                        ctx.debug("suspicious translation: {}"
                                  .format(tr))

                    if "tags" in tr:
                        tr["tags"] = list(sorted(set(tr["tags"])))

                    # If we have only notes, add as-is
                    if "word" not in tr:
                        data_append(ctx, data, "translations", tr)
                        continue

                    # Split if it contains no spaces
                    alts = [w]
                    if w.find(" ") < 0:
                        # If no spaces, split by separator
                        alts = re.split(r"/|／", w)
                    # Note: there could be remaining slashes, but they are
                    # sometimes used in ways we cannot resolve programmatically.
                    # Create translations for each alternative.
                    for alt in alts:
                        alt = alt.strip()
                        tr1 = copy.deepcopy(tr)
                        if alt.startswith("*") or alt.startswith(":"):
                            alt = alt[1:].strip()
                        if not alt:
                            continue
                        tr1["word"] = alt
                        data_append(ctx, data, "translations", tr1)

            # Handle sublists.  They are frequently used for different scripts
            # for the language and different variants of the language.  We will
            # include the lower-level header as a tag in those cases.
            for listnode in sublists:
                assert listnode.kind == NodeKind.LIST
                for node in listnode.children:
                    if not isinstance(node, WikiNode):
                        continue
                    if node.kind == NodeKind.LIST_ITEM:
                        parse_translation_item(node.children, lang=lang)

        def parse_translation_template(node):
            assert isinstance(node, WikiNode)

            def template_fn(name, ht):
                nonlocal sense_parts
                nonlocal sense
                if is_panel_template(name):
                    return ""
                if name == "see also":
                    # XXX capture
                    # XXX for example, "/" has top-level list containing
                    # see also items.  So also should parse those.
                    return ""
                if name == "trans-see":
                    # XXX capture
                    return ""
                if name == "see translation subpage":
                    sense_parts = []
                    sense = None
                    pos = ht.get(1)
                    if not isinstance(pos, str):
                        ctx.error("no part-of-speech in "
                                  "{{see translation subpage|...}}")
                        return
                    subnode = get_subpage_section(language, ctx.title,
                                                  "translations", pos,
                                                  "Translations")
                    if subnode is not None:
                        parse_translations(data, subnode)
                    return ""
                if name in ("c", "C", "categorize", "cat", "catlangname",
                            "topics", "top", "qualifier", "cln"):
                    # These are expanded in the default way
                    return None
                if name in ("trans-top",):
                    # XXX capture id from trans-top?  Capture sense here
                    # instead of trying to parse it from expanded content?
                    sense_parts = []
                    sense = None
                    return None
                if name in ("trans-bottom", "trans-mid"):
                    return None
                if name == "checktrans-top":
                    sense_parts = []
                    sense = None
                    return ""
                if name == "trans-top-also":
                    # XXX capture?
                    sense_parts = []
                    sense = None
                    return ""
                ctx.error("UNIMPLEMENTED: parse_translation_template: {} {}"
                          .format(name, ht))
                return ""
            ctx.expand(ctx.node_to_wikitext(node), template_fn=template_fn)

        def parse_translation_recurse(xlatnode):
            nonlocal sense
            nonlocal sense_parts
            for node in xlatnode.children:
                if isinstance(node, str):
                    if sense:
                        if not node.isspace():
                            ctx.debug("skipping string in the middle of "
                                      "translations: {}".format(node))
                        continue
                    # Add a part to the sense
                    sense_parts.append(node)
                    sense = None
                    continue
                assert isinstance(node, WikiNode)
                kind = node.kind
                if kind == NodeKind.LIST:
                    for item in node.children:
                        if not isinstance(item, WikiNode):
                            continue
                        if item.kind != NodeKind.LIST_ITEM:
                            continue
                        if item.args == ":":
                            continue
                        parse_translation_item(item.children)
                elif kind == NodeKind.LIST_ITEM and node.args == ":":
                    # Silently skip list items that are just indented; these
                    # are used for text between translations, such as indicating
                    # translations that need to be checked.
                    pass
                elif kind == NodeKind.TEMPLATE:
                    parse_translation_template(node)
                elif kind in (NodeKind.TABLE, NodeKind.TABLE_ROW,
                              NodeKind.TABLE_CELL):
                    parse_translation_recurse(node)
                elif kind == NodeKind.HTML:
                    if node.attrs.get("class") == "NavFrame":
                        # Reset ``sense_parts`` (and force recomputing
                        # by clearing ``sense``) as each NavFrame specifies
                        # its own sense.  This helps eliminate garbage coming
                        # from text at the beginning at the translations
                        # section.
                        sense_parts = []
                        sense = None
                    # for item in node.children:
                    #     if not isinstance(item, WikiNode):
                    #         continue
                    #     parse_translation_recurse(item)
                    parse_translation_recurse(node)
                elif kind in LEVEL_KINDS:
                    # Sub-levels will be recursed elsewhere
                    pass
                elif kind in (NodeKind.ITALIC, NodeKind.BOLD):
                    parse_translation_recurse(node)
                elif kind == NodeKind.LINK:
                    arg0 = node.args[0]
                    if (len(arg0) >= 1 and
                        isinstance(arg0[0], str) and
                        not arg0[0].lower().startswith("category:")):
                        for x in node.args[-1]:
                            if isinstance(x, str):
                                sense_parts.append(x)
                            else:
                                parse_translation_recurse(x)
                elif not sense:
                    sense_parts.append(node)
                else:
                    ctx.debug("skipping text between translation items/senses: "
                              "{}".format(node))

        # Main code of parse_translation().  We want ``sense`` to be assigned
        # regardless of recursion levels, and thus the code is structured
        # to define at this level and recurse in parse_translation_recurse().
        parse_translation_recurse(xlatnode)

    def process_children(treenode):
        """This recurses into a subtree in the parse tree for a page."""
        nonlocal etym_data
        nonlocal pos_data

        def skip_template_fn(name, ht):
            """This is called for otherwise unprocessed parts of the page.
            We still expand them so that e.g. Category links get captured."""
            if name in wikipedia_templates:
                data = base if len(stack) <= 1 else etym_data
                parse_wikipedia_template(config, ctx, data, ht)
                return ""
            if is_panel_template(name):
                return ""
            return None

        def select_data():
            """Selects where to store data (pos or etym) based on whether we
            are inside a pos (part-of-speech)."""
            if any(x.lower() in part_of_speech_map for x in stack):
                return pos_data
            return etym_data

        for node in treenode.children:
            if not isinstance(node, WikiNode):
                # print("  X{}".format(repr(node)[:40]))
                continue
            if node.kind not in LEVEL_KINDS:
                # XXX handle e.g. wikipedia links at the top of a language
                # XXX should at least capture "also" at top of page
                if node.kind in (NodeKind.HLINE, NodeKind.LIST,
                                 NodeKind.LIST_ITEM):
                    continue
                # print("      UNEXPECTED: {}".format(node))
                # Clean the node to collect category links
                clean_node(config, ctx, etym_data, node,
                           template_fn=skip_template_fn)
                continue
            t = clean_node(config, ctx, etym_data, node.args)
            config.section_counts[t] += 1
            pos = t.lower()
            # print("PROCESS_CHILDREN: T:", repr(t))
            if t.startswith("Pronunciation"):
                if config.capture_pronunciation:
                    parse_pronunciation(node)
                if t.startswith("Pronunciation "):
                    # Pronunciation 1, etc, are used in Chinese Glyphs,
                    # and each of them may have senses under Definition
                    push_etym()
                    ctx.start_subsection(None)
            elif t.startswith("Etymology"):
                push_etym()
                ctx.start_subsection(None)
                # XXX parse etymology section, up to the next subtitle
            elif pos in part_of_speech_map:
                push_pos()
                dt = part_of_speech_map[pos]
                pos = dt["pos"]
                ctx.start_subsection(t)
                if "warning" in dt:
                    ctx.warning("{}: {}".format(t, dt["warning"]))
                if "error" in dt:
                    ctx.error("{}: {}".format(t, dt["error"]))
                # Parse word senses for the part-of-speech
                parse_part_of_speech(node, pos)
                if "tags" in dt:
                    for pdata in pos_datas:
                        data_extend(ctx, pdata, "tags", dt["tags"])
            elif t == "Translations":
                data = select_data()
                parse_translations(data, node)
            elif t in ("Declension", "Conjugation", "Inflection", "Mutation"):
                parse_inflection(node)
            elif pos in linkage_map:
                rel = linkage_map[pos]
                data = select_data()
                parse_linkage(data, rel, node)
            elif pos == "compounds":
                data = select_data()
                if config.capture_compounds:
                    parse_linkage(data, "derived", node)
            elif t in ("Anagrams", "Further reading", "References",
                       "Quotations", "Descendants"):
                # XXX does the Descendants section have something we'd like
                # to capture?
                pass

            # XXX parse interesting templates also from other sections.  E.g.,
            # {{Letter|...}} in ===See also===
            # Also <gallery>

            # Recurse to children of this node, processing subtitles therein
            stack.append(t)
            process_children(node)
            stack.pop()

    # Main code of parse_language()
    # Process the section
    stack.append(language)
    process_children(langnode)
    stack.pop()

    # Finalize word entires
    push_etym()
    ret = []
    for data in page_datas:
        merge_base(data, base)
        # XXX merge any other data that should be merged from other parts of
        # the page or from related pages
        ret.append(data)

    # Copy all tags to word senses
    for data in ret:
        if "senses" not in data:
            continue
        tags = data.get("tags", ())
        if "tags" in data:
            del data["tags"]
        for sense in data["senses"]:
            data_extend(ctx, sense, "tags", tags)

    return ret


def parse_wikipedia_template(config, ctx, data, ht):
    """Helper function for parsing {{wikipedia|...}} and related templates."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(ht, dict)
    langid = clean_node(config, ctx, data, ht.get("lang", ()))
    pagename = clean_node(config, ctx, data, ht.get(1, ())) or ctx.title
    if langid:
        data_append(ctx, data, "wikipedia", langid + ":" + pagename)
    else:
        data_append(ctx, data, "wikipedia", pagename)


def parse_top_template(config, ctx, node, data):
    """Parses a template that occurs on the top-level in a page, before any
    language subtitles."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(node, WikiNode)
    assert isinstance(data, dict)

    def top_template_fn(name, ht):
        if name in wikipedia_templates:
            parse_wikipedia_template(config, ctx, data, ht)
            return ""
        if is_panel_template(name):
            return ""
        if name == "also":
            # XXX shows related words that might really have been the intended
            # word, capture them
            return ""
        if name == "see also":
            # XXX capture
            return ""
        if name == "cardinalbox":
            # XXX capture
            return ""
        if name == "character info":
            # XXX capture
            return ""
        if name == "commonscat":
            # XXX capture link to Wikimedia commons
            return ""
        if name == "wikidata":
            arg = clean_node(config, ctx, data, ht.get(1, ()))
            if arg.startswith("Q") or arg.startswith("Lexeme:L"):
                data_append(ctx, data, "wikidata", arg)
            return ""
        ctx.warning("UNIMPLEMENTED top-level template: {} {}"
                    .format(name, ht))
        return ""

    clean_node(config, ctx, None, [node], template_fn=top_template_fn)


def parse_page(ctx, word, text, config):
    """Parses the text of a Wiktionary page and returns a list of
    dictionaries, one for each word/part-of-speech defined on the page
    for the languages specified by ``capture_languages`` (None means
    all available languages).  ``word`` is page title, and ``text`` is
    page text in Wikimedia format.  Other arguments indicate what is
    captured."""
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(text, str)
    assert isinstance(config, WiktionaryConfig)

    # Skip words that have been moved to the Attic
    if word.startswith("/(Attic) "):
        return []

    if config.verbose:
        print("Parsing page:", word)

    config.word = word

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    ctx.start_page(word)
    tree = ctx.parse(text, pre_expand=True,
                     additional_expand=additional_expand_templates)
    # print("PAGE PARSE:", tree)

    top_data = {}

    # Iterate over top-level titles, which should be languages for normal
    # pages
    by_lang = collections.defaultdict(list)
    for langnode in tree.children:
        if not isinstance(langnode, WikiNode):
            continue
        if langnode.kind == NodeKind.TEMPLATE:
            parse_top_template(config, ctx, langnode, top_data)
            continue
        if langnode.kind == NodeKind.LINK:
            # Some pages have links at top level, e.g., "trees" in Wiktionary
            continue
        if langnode.kind != NodeKind.LEVEL2:
            ctx.error("unexpected top-level node: {}".format(langnode))
            continue
        lang = clean_node(config, ctx, None, langnode.args)
        if lang not in languages_by_name:
            ctx.error("unrecognized language name at top-level {!r}"
                         .format(lang))
            continue
        if config.capture_languages and lang not in config.capture_languages:
            continue
        langdata = languages_by_name[lang]
        lang_code = langdata["code"]
        ctx.start_section(lang)

        # Collect all words from the page.
        datas = parse_language(ctx, config, langnode, lang, lang_code)

        # Propagate fields resulting from top-level templates to this
        # part-of-speech.
        for data in datas:
            if "lang" not in data:
                ctx.debug("no lang in data: {}".format(data))
                continue
            for k, v in top_data.items():
                assert isinstance(v, (list, tuple))
                data_extend(ctx, data, k, v)
            by_lang[data["lang"]].append(data)

    # Do some post-processing on the words.  For example, we may distribute
    # conjugation information to all the words.
    ret = []
    for lang, lang_datas in by_lang.items():
        # If one of the words coming from this article does not have
        # conjugation information, but another one for the same
        # language and a compatible part-of-speech has, use the
        # information from the other one also for the one without.
        for data in lang_datas:
            if "pos" not in data:
                continue
            if "conjugation" not in data:
                pos = data.get("pos")
                assert pos
                for dt in datas:
                    if data.get("lang") != dt.get("lang"):
                        continue
                    conjs = dt.get("conjugation", ())
                    if not conjs:
                        continue
                    cpos = dt.get("pos")
                    if (pos == cpos or
                        (pos, cpos) in (("noun", "adj"),
                                        ("noun", "name"),
                                        ("name", "noun"),
                                        ("name", "adj"),
                                        ("adj", "noun"),
                                        ("adj", "name")) or
                        (pos == "adj" and cpos == "verb" and
                         any("participle" in s.get("tags", ())
                             for s in dt.get("senses", ())))):
                        data["conjugation"] = list(conjs)  # Copy list!
                        break
        # Add topics from the last sense of a language to its other senses,
        # marking them inaccurate as they may apply to all or some sense
        if len(lang_datas) > 1:
            topics = lang_datas[-1].get("topics", [])
            for t in topics:
                t["inaccurate"] = True
            for data in lang_datas[:-1]:
                new_topics = data.get("topics", []) + topics
                if new_topics:
                    data["topics"] = list(new_topics)  # Copy list!
        ret.extend(lang_datas)

    # Inject linkages from thesaurus entries
    for data in ret:
        if "pos" not in data:
            continue
        word = data["word"]
        lang = data["lang"]
        pos = data["pos"]
        for tpos, rel, w, sense, xlit, tags, topics, title in \
            config.thesaurus_data.get((word, lang), ()):
            if tpos is not None and pos != tpos:
                continue
            if w == word:
                continue
            for dt in data.get(rel, ()):
                if dt.get("word") == w:
                    if not sense or dt.get("sense") == sense:
                        break
            else:
                dt = {"word": w, "source": title}
                if sense:
                    dt["sense"] = sense
                if tags:
                    dt["tags"] = tags
                if topics:
                    dt["topics"] = topics
                if xlit:
                    dt["xlit"] = xlit
                data_append(ctx, data, rel, dt)

    # Disambiguate those items from word level that can be disambiguated
    for data in ret:
        disambiguate_clear_cases(ctx, data, "translations")
        for field in linkage_fields:
            disambiguate_clear_cases(ctx, data, field)

    # Categories are not otherwise disambiguated, but if there is only
    # one sense and only one data in ret for the same language, move
    # categories to the only sense.  Note that categories are commonly
    # specified for the page, and thus if we have multiple data in
    # ret, we don't know which one they belong to (not even which
    # language necessarily?).
    # XXX can Category links be specified globally (i.e., in a different
    # language?)
    by_lang = collections.defaultdict(list)
    for data in ret:
        by_lang[data["lang"]].append(data)
    for la, lst in by_lang.items():
        if len(lst) > 1:
            # Propagate categories from the last entry for the language to
            # its other entries.  It is common for them to only be specified
            # in the last part-of-speech.
            last = lst[-1]
            for field in ("categories",):
                if field not in last:
                    continue
                vals = last[field]
                for data in lst[:-1]:
                    assert data is not last
                    assert data.get(field) is not vals
                    if data.get("alt_of") or data.get("form_of"):
                        continue  # Don't add to alt-of/form-of entries
                    data_extend(ctx, data, field, vals)
            continue
        if len(lst) != 1:
            continue
        data = lst[0]
        senses = data.get("senses") or []
        if len(senses) != 1:
            continue
        # Only one sense for this language.  Move categories and certain other
        # data to sense.
        for field in ("categories", "topics", "wikidata", "wikipedia"):
            if field in data:
                v = data[field]
                del data[field]
                data_extend(ctx, senses[0], field, v)

    # If the last part-of-speech of the last language (i.e., last item in "ret")
    # has categories or topics not bound to a sense, propagate those
    # categories and topics to all datas on "ret".  It is common for categories
    # to be specified at the end of an article.  Apparently these can also
    # apply to different languages.
    if len(ret) > 1:
        last = ret[-1]
        for field in ("categories",):
            if field not in last:
                continue
            lst = last[field]
            for data in ret[:-1]:
                if data.get("form_of") or data.get("alt_of"):
                    continue  # Don't add to form_of or alt_of entries
                data_extend(ctx, data, field, lst)

    # Remove category links that start with a language name from entries for
    # different languages
    for data in ret:
        lang = data.get("lang")
        assert lang
        cats = data.get("categories", ())
        new_cats = []
        for cat in cats:
            parts = cat.split(" ")
            if parts[0] in languages_by_name and parts[0] != lang:
                continue  # Ignore categories for a different language
            new_cats.append(cat)
        if not new_cats:
            if "categories" in data:
                del data["categories"]
        else:
            data["categories"] = new_cats

    # Remove duplicates from tags, topics, and categories, etc.
    for data in ret:
        for field in ("topics", "categories", "tags", "wikidata", "wikipedia"):
            if field in data:
                data[field] = list(sorted(set(data[field])))
            for sense in data.get("senses", ()):
                if field in sense:
                    sense[field] = list(sorted(set(sense[field])))

    # Return the resulting words
    return ret


def clean_node(config, ctx, category_data, value, template_fn=None,
               post_template_fn=None):
    """Expands the node to text, cleaning up any HTML and duplicate spaces.
    This is intended for expanding things like glosses for a single sense."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert category_data is None or isinstance(category_data, dict)
    assert template_fn is None or callable(template_fn)
    assert post_template_fn is None or callable(post_template_fn)
    # print("CLEAN_NODE:", repr(value))

    def clean_template_fn(name, ht):
        if template_fn is not None:
            return template_fn(name, ht)
        if name in panel_templates:
            return ""
        return None

    def recurse(value):
        if isinstance(value, str):
            ret = value
        elif isinstance(value, (list, tuple)):
            ret = "".join(map(recurse, value))
        elif isinstance(value, WikiNode):
            ret = ctx.node_to_html(value, template_fn=clean_template_fn,
                                   post_template_fn=post_template_fn)
        else:
            ret = str(value)
        return ret

    v = recurse(value)
    # print("clean_node:", repr(v))

    # Capture categories if category_data has been given.  We also track
    # Lua execution errors here.
    if category_data is not None:
        # Check for Lua execution error
        if v.find('<strong class="error">Lua execution error') >= 0:
            data_append(ctx, category_data, "tags", "error-lua-exec")
        if v.find('<strong class="error">Lua timeout error') >= 0:
            data_append(ctx, category_data, "tags", "error-lua-timeout")
        # Capture Category tags
        for m in re.finditer(r"(?is)\[\[:?\s*Category\s*:([^]|]+)", v):
            cat = clean_value(config, m.group(1))
            m = re.match(r"[a-z]{2,4}:", cat)
            if m:
                # XXX these provide important information for disambiguating
                # cat link at the end of the page (to at least the proper
                # language).  However, the information is not always accurate -
                # for example, "A8" has "en:Paper sizes" category even though
                # the paper sizes are under Translingual.
                cat = cat[m.end():]
            cat = re.sub(r"\s+", " ", cat)
            cat = cat.strip()
            if not cat:
                continue
            if re.match(ignored_cat_re, cat):
                continue
            if cat.find(" female given names") >= 0:
                data_append(ctx, category_data, "tags", "feminine")
            elif cat.find(" male given names") >= 0:
                data_append(ctx, category_data, "tags", "masculine")
            elif cat.startswith("Places "):
                data_append(ctx, category_data, "tags", "place")
            if cat not in category_data.get("categories", ()):
                data_append(ctx, category_data, "categories", cat)

    v = clean_value(config, v)
    # print("After clean:", repr(v))

    # Strip any unhandled templates and other stuff.  This is mostly intended
    # to clean up erroneous codings in the original text.
    v = re.sub(r"(?s)\{\{.*", "", v)
    # Some templates create <sup>(Category: ...)</sup>; remove
    v = re.sub(r"(?si)\s*(^\s*)?\(Category:[^)]*\)", "", v)
    # Some templates create question mark in <sup>, e.g., some Korean Hanja form
    v = re.sub(r"\^\?", "", v)
    return v

# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import html
import collections
from wikitextprocessor import Wtp, WikiNode, NodeKind, ALL_LANGUAGES
from .parts_of_speech import part_of_speech_map, PARTS_OF_SPEECH
from .config import WiktionaryConfig
from .clean import clean_value
from .places import place_prefixes  # XXX move processing to places.py
from .unsupported_titles import unsupported_title_map
from .datautils import (data_append, data_extend, split_at_comma_semi)
from .disambiguate import disambiguate_clear_cases
from wiktextract.form_descriptions import (
    decode_tags, parse_word_head, parse_sense_tags, parse_pronunciation_tags,
    parse_alt_or_inflection_of,
    parse_translation_desc, xlat_tags_map, valid_tags,
    classify_desc)

# NodeKind values for subtitles
LEVEL_KINDS = (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
               NodeKind.LEVEL5, NodeKind.LEVEL6)

# Mapping from language name to language info
languages_by_name = {x["name"]: x for x in ALL_LANGUAGES}

# Mapping from language code to language info
languages_by_code = {x["code"]: x for x in ALL_LANGUAGES}

# Matches head tag
head_tag_re = re.compile(r"^(head|Han char)$|" +
                         r"^(" + "|".join(languages_by_code.keys()) + r")"
                         r"-(plural-noun|plural noun|noun|verb|adj|adv|"
                         r"name|proper-noun|proper noun|prop|pron|phrase|"
                         r"decl noun|decl-noun|prefix|clitic|number|ordinal|"
                         r"syllable|suffix|affix|pos|gerund|combining form|"
                         r"combining-form|converb|cont|con|interj|det|part|"
                         r"part-form|postp|prep)(-|$)")

# Regular expression for removing links to specific languages from
# translation items
langlink_re = re.compile(r"\s*\((" + "|".join(languages_by_code.keys()) +
                         r")\)|"
                         r"\(\s*\[\[:[-a-zA-Z0-9]+:[^]]+\]\]\s*\)")

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
    "ttbc",
    "unblock",
    "unsupportedpage",
    "video frames",
    "wikipedia",
    "w",
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
        gloss = re.sub(r"^\([^)]*\)\s*", "", gloss)
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


def parse_sense_linkage(ctx, data, name, ht):
    """Parses a linkage (synonym, etc) specified in a word sense."""
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(name, str)
    assert isinstance(ht, dict)
    field = sense_linkage_templates[name]
    for i in range(2, 20):
        w = ht.get(i) or ""
        w = w.strip()
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
                data[k] = v
            elif isinstance(data[k], list):
                data[k].extend(v)
            elif data[k] != v:
                ctx.warning("conflicting values for {}: {} vs {}"
                            .format(k, data[k], v))

    def push_sense():
        """Starts collecting data for a new word sense."""
        nonlocal sense_data
        if not sense_data:
            return
        pos_datas.append(sense_data)
        sense_data = {}

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
        a top-level item."""
        assert isinstance(pos, str)
        assert isinstance(contents, (list, tuple))
        assert isinstance(sense_base, dict)  # Added to every sense
        # print("PARSE_SENSE ({}): {}".format(sense_base, contents))
        lst = [x for x in contents
               if not isinstance(x, WikiNode) or
               x.kind not in (NodeKind.LIST,)]

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
                parse_sense_linkage(ctx, sense_base, name, ht)
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
            return None

        rawgloss = clean_node(config, ctx, sense_base, lst,
                              template_fn=sense_template_fn)
        # The gloss could contain templates that produce more list items.
        # This happens commonly with, e.g., {{inflection of|...}}.  Split
        # to parts.
        subglosses = re.split(r"[#*]+\s*", rawgloss)
        if len(subglosses) > 1 and "form_of" not in sense_base:
            infl_tags, infl_base = parse_alt_or_inflection_of(ctx,
                                                              subglosses[0])
            if infl_base and "form-of" in infl_tags:
                # Interpret others as a particular form under "inflection of"
                data_extend(ctx, sense_base, "tags", infl_tags)
                data_append(ctx, sense_base, "form_of", infl_base)
                subglosses = subglosses[1:]
        # Create senses for remaining subglosses
        for gloss in subglosses:
            gloss = gloss.strip()
            if not gloss and len(subglosses) > 1:
                continue
            # Push a new sense (if the last one is not empty)
            push_sense()
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
                    sense_data[k] = v
            # Parse the gloss for this particular sense
            m = re.match(r"^\((([^()]|\([^)]*\))*)\):?\s*", gloss)
            if m:
                parse_sense_tags(ctx, m.group(1), sense_data)
                gloss = gloss[m.end():].strip()

            def sense_repl(m):
                par = m.group(1)
                cls = classify_desc(par)
                if cls == "tags":
                    parse_sense_tags(ctx, par, sense_data)
                else:
                    return m.group(0)
                return ""

            # Replace parenthesized expressions commonly used for sense tags
            gloss = re.sub(r"\s*\(([^)]*)\)", sense_repl, gloss)

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
                infl_tags, infl_base = parse_alt_or_inflection_of(ctx, gloss)
                if not infl_base and infl_tags:
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
            tags, base = parse_alt_or_inflection_of(ctx, gloss)
            ftags = list(tag for tag in tags if tag != "form-of") # Spurious
            if "alt-of" in tags:
                data_extend(ctx, sense_data, "tags", ftags)
                data_append(ctx, sense_data, "alt_of", base)
            elif "compound-of" in tags:
                data_extend(ctx, sense_data, "tags", ftags)
                data_append(ctx, sense_data, "compound_of", base)
            elif "synonym-of" in tags:
                dt = { "word": base }
                data_extend(ctx, dt, "tags", ftags)
                data_append(ctx, sense_data, "synonyms", dt)
            elif tags and base.startswith("of "):
                base = base[3:]
                data_append(ctx, sense_data, "tags", "form-of")
                data_extend(ctx, sense_data, "tags", ftags)
                data_append(ctx, sense_data, "form_of", base)
            elif "form-of" in tags:
                data_extend(ctx, sense_data, "tags", tags)
                data_append(ctx, sense_data, "form_of", base)

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
        if name in ("tlb", "term-context", "term-label", "tcx"):
            i = 2
            while True:
                v = ht.get(i)
                if v is None:
                    break
                v = clean_value(config, v)
                data_append(ctx, pos_data, "tags", v)
                i += 1
            return ""
        if name == "head":
            t = ht.get(2, "")
            if t == "pinyin":
                data_append(ctx, pos_data, "tags", "pinyin")
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
                continue
            elif kind == NodeKind.HTML:
                if node.args not in ("gallery", "ref", "cite", "caption"):
                    pre.append(node)
            elif first_para:
                pre.append(node)
        # XXX use template_fn in clean_node to check that the head macro
        # is compatible with the current part-of-speech and generate warning
        # if not.  Use template_allowed_pos_map.
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
                        parse_sense_linkage(ctx, common_data, name, ht)
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
                # Process any inner glosses
                for sublist in sublists:
                    assert sublist.kind == NodeKind.LIST
                    for item in sublist.children:
                        if not isinstance(item, WikiNode):
                            continue
                        if item.kind != NodeKind.LIST_ITEM:
                            continue
                        sense_base = {}
                        for k, v in common_data.items():
                            if isinstance(v, (list, tuple)):
                                data_extend(ctx, sense_base, k, v)
                            else:
                                sense_base[k] = v
                        # XXX is it always a gloss?  Maybe non-gloss?
                        tags = ()
                        if outer_text == "A pejorative:":
                            tags = ["pejorative"]
                            outer_text = None
                        elif outer_text == "Short forms.":
                            tags = ["abbreviation"]
                            outer_text = None
                        elif outer_text == "Technical or specialized senses.":
                            outer_text = None
                        data_extend(ctx, sense_base, "tags", tags)
                        if outer_text:
                            data_append(ctx, sense_base, "glosses",
                                        outer_text)
                        parse_sense(pos, item.children, sense_base)

    def parse_pronunciation(node):
        """Parses the pronunciation section from a language section on a
        page."""
        assert isinstance(node, WikiNode)
        if node.kind in LEVEL_KINDS:
            node = node.children
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
                audio = {"audio": filename}
                m = re.search(r"\((([^()]|\([^)]*\))*)\)", desc)
                if m:
                    parse_pronunciation_tags(ctx, m.group(1), audio)
                if desc:
                    audio["text"] = desc
                audios.append(audio)
                return ""
            if name == "audio-pron":
                filename = ht.get(2) or ""
                ipa = ht.get("ipa")
                dial = ht.get("dial")
                country = ht.get("country")
                audio = {"audio": filename}
                if dial:
                    audio["text"] = dial
                    data_append(ctx, audio, "tags", dial)
                if country:
                    data_append(ctx, audio, "tags", country.upper())
                audios.append(audio)
                if ipa:
                    pron = {"ipa": ipa}
                    if dial:
                        data_append(ctx, pron, "tags", dial)
                    if country:
                        data_append(ctx, pron, "tags", country.upper())
                    data_append(ctx, data, "sounds", pron)
            return None

        # XXX change this code to iterate over node as a LIST, warning about
        # anything else.  Don't try to split by "*".
        # XXX fix enpr tags
        text = clean_node(config, ctx, data, node,
                          template_fn=parse_pronunciation_template_fn)
        have_pronunciations = False
        for origtext in re.split(r"[*#]+", text):  # Items generated by macros
            text = origtext
            m = re.match("^[*#\s]*\((([^()]|\([^)]*\))*?)\)", text)
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
                    w = word.strip()
                    if w:
                        pron = {"homophone": w}
                        parse_pronunciation_tags(ctx, tagstext, pron)
                        data_append(ctx, data, "sounds", pron)
                        have_pronunciations = True

            # First remove some patterns that may introduce incorrect
            # spurious IPAs.
            text1 = re.sub(r"\bsee /æ/ raising\b", "", text)
            for m in re.finditer("/[^/,]+?/|\[[^]0-9,/][^],/]*?\]", text1):
                v = m.group(0)
                # The regexp above can match file links.  Skip them.
                if v.startswith("[[File:"):
                    continue
                if v == "/wiki.local/":
                    continue
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
        content = ctx.read_by_title(subpage_title)
        if content is None:
            ctx.error("/translations not found despite "
                      "{{see translation subpage|...}}")
        tree = ctx.parse(content, pre_expand=True,
                         additional_expand=additional_expand_templates)
        assert tree.kind == NodeKind.ROOT
        # Find the language subtitle
        for node1 in tree.children:
            if not isinstance(node1, WikiNode):
                continue
            if node1.kind != NodeKind.LEVEL2:
                continue
            subtitle = clean_node(config, ctx, None, node1.args[0])
            if subtitle != language:
                continue
            # Find the part-of-speech subtitle
            for node2 in node1.children:
                if not isinstance(node2, WikiNode):
                    continue
                if node2.kind != NodeKind.LEVEL3:
                    continue
                subtitle = clean_node(config, ctx, None, node2.args[0])
                if subtitle != pos:
                    continue
                # Find the specified section under the part-of-speech
                for node3 in node2.children:
                    if not isinstance(node3, WikiNode):
                        continue
                    if node3.kind != NodeKind.LEVEL4:
                        continue
                    subtitle = clean_node(config, ctx, None, node3.args[0])
                    if subtitle != section:
                        continue
                    return node3
        ctx.warning("Failed to find subpage section {} {}/{} {} {}"
                    .format(language, title, subtitle, pos, section))
        return None

    def parse_linkage(data, field, linkagenode):
        assert isinstance(data, dict)
        assert isinstance(field, str)
        assert isinstance(linkagenode, WikiNode)
        # print("PARSE_LINKAGE:", linkagenode)
        if not config.capture_linkages:
            return
        have_linkages = False
        have_panel_template = False

        def parse_linkage_item(contents, field, sense):
            assert isinstance(contents, (list, tuple))
            assert isinstance(field, str)
            assert sense is None or isinstance(sense, str)
            nonlocal have_linkages

            #print("PARSE_LINKAGE_ITEM: {} ({}): {}"
            #      .format(field, sense, contents))

            qualifier = None
            parts = []
            roman = None
            ruby = ""
            alt = None
            taxonomic = None

            def item_recurse(contents, italic=False):
                assert isinstance(contents, (list, tuple))
                nonlocal have_linkages
                nonlocal sense
                nonlocal qualifier
                nonlocal roman
                nonlocal ruby
                nonlocal parts
                nonlocal alt
                nonlocal taxonomic
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
                            if sense1.startswith("(") and sense1.endswith("):"):
                                sense1 = sense1[1:-2]
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
                        if node.args in ("gallery", "ref", "cite", "caption"):
                            continue
                        elif node.args == "rp":
                            continue  # Parentheses inside <ruby>
                        elif node.args == "rt":
                            ruby += clean_node(config, ctx, None, node)
                            continue
                        classes = (node.attrs.get("class") or "").split()
                        if "NavFrame" in classes:
                            parse_linkage_recurse(node.children, field, sense)
                        else:
                            item_recurse(node.children, italic=italic)
                    elif kind == NodeKind.ITALIC:
                        item_recurse(node.children, italic=True)
                    elif kind == NodeKind.LINK:
                        if (not isinstance(node.args[0][0], str) or
                            node.args[0][0].find("Category:")):
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
            if item.startswith("See also Thesaurus:"):
                item = ""
                have_linkages = True

            if item.startswith(":"):
                item = item[1:]
            item = item.strip()

            #print("    LINKAGE ITEM: {}: {} (sense {})"
            #      .format(field, item, sense))

            base_qualifier = None
            m = re.match(r"\((([^()]|\([^)]*\))*)\):?\s*", item)
            if m:
                par = m.group(1)
                cls = classify_desc(par)
                if cls == "tags":
                    base_qualifier = par
                    item = item[m.end():]
                elif cls in ("english", "taxonomic"):
                    if sense:
                        sense = sense + "; " + par
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
            if base_sense in ("A paper sizes",
                              "Arabic digits"):
                base_qualifier = None
                item = ", ".join(item.split())

            # XXX temporarily disabled.  These should be analyzed.
            #if item.find("(") >= 0 and item.find(", though ") < 0:
            #    ctx.debug("linkage item has remaining parentheses: {}"
            #              .format(item))

            item = re.sub(r"\s*\^?\s*\(\s*\)", "", item)
            item = item.strip()
            # XXX check for: stripped item text starts with "See also [[...]]"
            if not item:
                return
            # The item may contain multiple comma-separated linkages
            subitems = split_at_comma_semi(item)
            if len(subitems) > 1:  # Would be merged from multiple subitems
                ruby = ""
            for item1 in subitems:
                item1 = item1.strip()
                qualifier = base_qualifier
                sense = base_sense
                parts = []
                roman = None
                alt = None
                taxonomic = None

                # Extract quoted English translations (there are also other
                # kinds of English translations)
                def english_repl(m):
                    nonlocal sense
                    v = m.group(1).strip()
                    if sense:
                        sense += "; " + v
                    else:
                        sense = v
                    return ""

                item = re.sub(r'[“"]([^"]+)[“"],?\s*', english_repl, item)
                item = re.sub(r", \)", ")", item)

                # There could be multiple parenthesized parts, and
                # sometimes both at the beginning and at the end
                while True:
                    par = None
                    if par is None:
                        m = re.match(r"\((([^()]|\([^)]*\))*)\):?\s*", item1)
                        if m:
                            par = m.group(1)
                            item1 = item1[m.end():]
                        else:
                            m = re.search(" \((([^()]|\([^)]*\))*)\)$", item1)
                            if m:
                                par = m.group(1)
                                item1 = item1[:m.start()]
                    if not par:
                        break
                    # Handle tags from beginning of par.  We also handle "other"
                    # here as Korean entries often have Hanja form in the
                    # beginning of paranthesis, before romanization.
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

                if item1.startswith("see Thesaurus:"):
                    item1 = item1[14:]
                elif item1.startswith("see also Thesaurus:"):
                    item1 = item1[19:]
                elif item1.startswith("Thesaurus:"):
                    item1 = item1[10:]
                if not item1:
                    continue
                if item1 == word:
                    continue
                dt = {"word": item1}
                if qualifier:
                    parse_sense_tags(ctx, qualifier, dt)
                if sense:
                    dt["sense"] = sense
                if roman:
                    dt["roman"] = roman
                if ruby:
                    dt["ruby"] = ruby
                if alt:
                    dt["alt"] = alt
                if taxonomic:
                    dt["taxonomic"] = taxonomic
                for old in data.get(field, ()):
                    if dt == old:
                        break
                else:
                    data_append(ctx, data, field, dt)
                    have_linkages = True

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
                    # linkages list
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
            ctx.debug("no linkages found")

    def parse_translations(data, xlatnode):
        """Parses translations for a word.  This may also pull in translations
        from separate translation subpages."""
        assert isinstance(data, dict)
        assert isinstance(xlatnode, WikiNode)
        # print("PARSE_TRANSLATIONS:", xlatnode)
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
                idx = sense.find("See also translations at ")
                if idx > 0:
                    sense = sense[:idx].strip()
            sense_detail = None

            def translation_item_template_fn(name, ht):
                nonlocal langcode
                nonlocal sense_parts
                nonlocal sense
                # print("TRANSLATION_ITEM_TEMPLATE_FN:", name, ht)
                if name in ("t", "t+", "t-simple", "t", "t+check", "t-check"):
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
                if name in ("t-needed", "checktrans-top"):
                    return ""
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
            # print("    TRANSLATION ITEM: {}  [{}]".format(item, sense))

            item = re.sub(r"\^\(please verify\)\s*", "", item)

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
            else:
                # We have no prefix that looks like a language name but
                # we already know the language.  Check if it might have
                # a word sense prefix.
                m = re.match(r"\*?\s*\(([^)]*)\):\s*", item)
                if m:
                    sense_detail = m.group(1)
                    item = item[m.end():]
                elif item.find(": ") >= 0:
                    ctx.warning("suspicious prefix in translation should be "
                                "checked: {}".format(item))

            # Certain values indicate it is not actually a translation
            for prefix in ("Use ", "use ", "suffix ", "prefix "):
                if item.startswith(prefix):
                    return
            if item in ("please add this translation if you can",):
                return

            # There may be multiple translations, separated by comma
            for part in split_at_comma_semi(item):
                part = part.strip()
                if not part:
                    continue
                # Strip language links
                part = re.sub(langlink_re, "", part)
                if langcode is None:
                    if lang in languages_by_name:
                        langcode = languages_by_name[lang]["code"]
                tr = {"lang": lang, "code": langcode}
                if tags:
                    tr["tags"] = list(tags)  # Copy so we don't modify others
                if sense:
                    if sense == "Translations to be checked":
                        pass
                    elif sense.startswith(":The translations below need to be "
                                          "checked"):
                        pass
                    else:
                        if sense_detail:
                            tr["sense"] = "{} ({})".format(sense, sense_detail)
                        else:
                            tr["sense"] = sense
                elif sense_detail:
                    tr["sense"] = sense_detail
                parse_translation_desc(ctx, part, tr)
                if not tr.get("word"):
                    continue  # Not set or empty
                if tr.get("word").startswith("Lua execution error"):
                    continue
                data_append(ctx, data, "translations", tr)

            m = re.match(r"\((([^()]|\([^)]*\))*)\) ", item)
            qualifier = None
            if m:
                qualifier = m.group(1)
                item = item[m.end():]
            else:
                m = re.search(" \((([^()]|\([^)]*\))*)\)$", item)
                if m:
                    qualifier = m.group(1)
                    item = item[:m.start()]

            # Handle sublists.  They are frequently used for different scripts
            # for the language and different variants of the langauge.  We will
            # include the lower-level header as a tag in those cases.
            for listnode in sublists:
                assert listnode.kind == NodeKind.LIST
                for node in listnode.children:
                    if not isinstance(node, WikiNode):
                        continue
                    if node.kind == NodeKind.LIST_ITEM:
                        parse_translation_item(node.children, lang=sublang)

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
                            "topics", "top", "qualifier",):
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
                    for item in node.children:
                        if not isinstance(item, WikiNode):
                            continue
                        parse_translation_recurse(item)
                elif kind in LEVEL_KINDS:
                    # Sub-levels will be recursed elsewhere
                    pass
                elif kind == NodeKind.ITALIC:
                    # Silently skip italicized text between translation items.
                    # It is commonly used, e.g., for indicating translations
                    # that need to be checked.
                    pass
                elif kind == NodeKind.LINK:
                    # At least category links can occur there
                    pass
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
                if stack[-1].lower() in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                parse_translations(data, node)
            elif t in ("Declension", "Conjugation", "Inflection", "Mutation"):
                parse_inflection(node)
            elif pos in linkage_map:
                rel = linkage_map[pos]
                if stack[-1].lower() in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                ctx.start_subsection(t)
                parse_linkage(data, rel, node)
            elif pos == "compounds":
                if stack[-1].lower() in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                if config.capture_compounds:
                    ctx.start_subsection(t)
                    parse_linkage(data, "compounds", node)
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

        # Do some post-processing on the words.  For example, we may distribute
        # conjugation information to all the words.
        for data in datas:
            if "lang" not in data:
                ctx.debug("no lang in data: {}".format(data))
                continue
            for k, v in top_data.items():
                assert isinstance(v, (list, tuple))
                data_extend(ctx, data, k, v)
            by_lang[data["lang"]].append(data)

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
                        data["conjugation"] = conjs
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
                    data["topics"] = new_topics
        ret.extend(lang_datas)

    # If the last part-of-speech of the last language (i.e., last item in "ret")
    # has categories or topics not bound to a sense, propagate those
    # categories and topics to all datas on "ret".  It is common for categories
    # to be specified at the end of an article.
    if len(ret) > 1:
        last = ret[-1]
        for field in ("topics", "categories"):
            if field not in last:
                continue
            lst = last[field]
            for data in ret[:-1]:
                assert data is not last
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
        # one sense and only one data in ret, move categories to the only sense.
        # Note that categories are commonly specified for the page, and thus
        # if we have multiple data in ret, we don't know which one they
        # belong to.
        for field in ("categories", "topics", "wikidata", "wikipedia"):
            if (field in data and len(data.get("senses", ())) == 1 and
                len(ret) == 1):
                v = data[field]
                del data[field]
                for sense in data["senses"]:
                    data_extend(ctx, sense, field, v)

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


def clean_node(config, ctx, category_data, value, template_fn=None):
    """Expands the node to text, cleaning up any HTML and duplicate spaces.
    This is intended for expanding things like glosses for a single sense."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert category_data is None or isinstance(category_data, dict)
    assert template_fn is None or callable(template_fn)
    # print("CLEAN_NODE:", repr(value))

    def recurse(value):
        if isinstance(value, str):
            ret = value
        elif isinstance(value, (list, tuple)):
            ret = "".join(map(recurse, value))
        elif isinstance(value, WikiNode):
            ret = ctx.node_to_html(value, template_fn=template_fn)
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

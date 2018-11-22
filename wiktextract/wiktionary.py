# Wiktionary parser for extracting a lexicon and various other information
# from wiktionary.
#
# Copyright (c) 2018 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import bz2
import html
import collections
from lxml import etree
import wikitextparser
from wiktextract import wiktlangs


# These XML tags are ignored when parsing.
ignore_tags = set(["sha1", "comment", "username", "timestamp",
                   "sitename", "dbname", "base", "generator", "case",
                   "ns", "restrictions", "contributor", "username",
                   "minor", "parentid", "namespaces", "revision",
                   "siteinfo", "mediawiki",
])

# Other tags are ignored inside these tags.
stack_ignore = ["contributor"]

# These Wiktionary templates are silently ignored (though some of them may be
# used when cleaning up titles and values).
ignored_templates = set([
    "-",
    "=",
    "*",
    "!",
    ",",
    "...",
    "AD",
    "BCE",
    "B.C.E.",
    "Book-B",
    "C.",
    "CE",
    "C.E.",
    "BC",
    "B.C.",
    "A.D.",
    "Clade",  # XXX Might want to dig information from this for hypernyms
    "CURRENTYEAR",
    "EtymOnLine",
    "EtymOnline",
    "IPAchar",
    "LR",
    "PAGENAME",
    "Q",
    "Webster 1913",
    "\\",
    "abbreviation-old",
    "af",
    "affix",
    "altcaps",
    "anchor",
    "ante",
    "attention",
    "attn",
    "bor",
    "borrowed",
    "bottom",
    "bottom2",
    "bottom3",
    "bottom4",
    "bullet",
    "checksense",
    "circa",
    "circa2",
    "cite",
    "cite book",
    "Cite news",
    "cite news",
    "cite-book",
    "cite-journal",
    "cite-magazine",
    "cite-news",
    "cite-newgroup",
    "cite-song",
    "cite-text",
    "cite-video",
    "cite-web",
    "cite web",
    "cog",
    "col-top",
    "col-bottom",
    "datedef",
    "def-date",
    "defdate",
    "defdt",
    "defn",
    "der",
    "der-bottom",
    "der-bottom2",
    "der-bottom3",
    "der-bottom4",
    "der-mid2",
    "der-mid3",
    "der-mid4",
    "der-mid",
    "derived",
    "dot",
    "doublet",
    "eggcorn of",
    "ellipsis",
    "em dash",
    "en dash",
    "etyl",
    "example needed",
    "examples",
    "examples-right",
    "frac",
    "g",  # gender - too rare to be useful
    "gloss-stub",
    "glossary",
    "hyp2",
    "hyp-top",
    "hyp-mid",
    "hyp-mid3",
    "hyp-bottom3",
    "hyp-bottom",
    "inh",
    "inherited",
    "interwiktionary",
    "ISO 639",
    "jump",
    "katharevousa",
    "ko-inline",
    "lang",
    "list",
    "ll",
    "lookfrom",
    "m",
    "mention",
    "mid2",
    "mid3",
    "mid4",
    "mid4",
    "middot",
    "multiple images",
    "nb...",
    "nbsp",
    "ndash",
    "no entry",
    "noncog",
    "noncognate",
    "nowrap",
    "nuclide",
    "overline",
    "phrasebook",
    "pedia",
    "pedialite",
    "picdic",
    "picdiclabel",
    "picdiclabel/new",
    "pos_v",
    "post",
    "quote-book",
    "quote-journal",
    "quote-magazine",
    "quote-news",
    "quote-newsgroup",
    "quote-song",
    "quote-text",
    "quote-video",
    "quote-web",
    "redirect",
    "rel-bottom",
    "rel-mid",
    "rel-mid2",
    "rel-mid3",
    "rel-mid4",
    "rfap",
    "rfc",
    "rfc-auto",
    "rfc-def",
    "rfc-header",
    "rfc-level",
    "rfc-subst",
    "rfc-tsort",
    "rfc-sense",
    "rfcite-sense",
    "rfd-redundant",
    "rfd-sense",
    "rfdate",
    "rfdatek",
    "rfdef",
    "rfe",
    "rfex",
    "rfexample",
    "rfm-sense",
    "rfgloss",
    "rfquote",
    "rfquote-sense",
    "rfquotek",
    "rft-sense",
    "rfv-sense",
    "rhymes",
    "rhymes",
    "see",
    "see also",
    "seeCites",
    "seemoreCites",
    "seemorecites",
    "seeMoreCites",
    "seeSynonyms",
    "sic",
    "smallcaps",
    "soplink",
    "spndash",
    "stroke order",
    "stub-gloss",
    "sub",
    "suffixsee",
    "sup",
    "syndiff",
    "t-check",
    "t+check",
    "table:colors/fi",
    "top2",
    "top3",
    "top4",
    "translation only",
    "trans-mid",
    "trans-bottom",
    "uncertain",
    "unk",
    "unsupported",
    "used in phrasal verbs",
    "was wotd",
    "wikisource1911Enc",
    "wikivoyage",
    "ws",
    "ws link",
    "zh-hg",
])

# This dictionary maps section titles in articles to parts-of-speech.  There
# is a lot of variety and misspellings, and this tries to deal with those.
pos_map = {
    "abbreviation": "abbrev",
    "acronym": "abbrev",
    "adjectival": "adj_noun",
    "adjectival noun": "adj_noun",
    "adjectival verb": "adj_verb",
    "adjective": "adj",
    "adjectuve": "adj",
    "adjectives": "adj",
    "adverb": "adv",
    "adverbs": "adv",
    "adverbial phrase": "adv_phrase",
    "affix": "affix",
    "adjective suffix": "affix",
    "article": "article",
    "character": "character",
    "circumfix": "circumfix",
    "circumposition": "circumpos",
    "classifier": "classifier",
    "clipping": "abbrev",
    "clitic": "clitic",
    "command form": "cmd",
    "command conjugation": "cmd_conj",
    "combining form": "combining_form",
    "comparative": "adj_comp",
    "conjunction": "conj",
    "conjuntion": "conj",
    "contraction": "abbrev",
    "converb": "converb",
    "counter": "counter",
    "determiner": "det",
    "diacritical mark": "character",
    "enclitic": "clitic",
    "enclitic particle": "clitic",
    "gerund": "gerund",
    "glyph": "character",
    "han character": "character",
    "han characters": "character",
    "ideophone": "noun",  # XXX
    "infix": "infix",
    "infinitive": "participle",
    "initialism": "abbrev",
    "interfix": "interfix",
    "interjection": "intj",
    "interrogative pronoun": "pron",
    "intransitive verb": "verb",
    "instransitive verb": "verb",
    "letter": "letter",
    "ligature": "character",
    "label": "character",
    "nom character": "character",
    "nominal nuclear clause": "clause",
    "νoun": "noun",
    "nouɲ": "noun",
    "noun": "noun",
    "nouns": "noun",
    "noum": "noun",
    "number": "num",
    "numeral": "num",
    "ordinal number": "ordinal",
    "participle": "participle",  # XXX
    "particle": "particle",
    "past participle": "participle",  # XXX
    "perfect expression": "participle",  # XXX
    "perfection expression": "participle",  # XXX
    "perfect participle": "participle",  # XXX
    "personal pronoun": "pron",
    "phrasal verb": "phrasal_verb",
    "phrase": "phrase",
    "phrases": "phrase",
    "possessive determiner": "det",
    "possessive pronoun": "det",
    "postposition": "postp",
    "predicative": "predicative",
    "prefix": "prefix",
    "preposition": "prep",
    "prepositions": "prep",
    "prepositional expressions": "prep",
    "prepositional phrase": "prep_phrase",
    "prepositional pronoun": "pron",
    "present participle": "participle",
    "preverb": "verb",
    "pronoun": "pron",
    "proper noun": "name",
    "proper oun": "name",
    "proposition": "prep",  # Appears to be a misspelling of preposition
    "proverb": "proverb",
    "punctuation mark": "punct",
    "punctuation": "punct",
    "relative": "conj",
    "root": "root",
    "syllable": "character",
    "suffix": "suffix",
    "suffix form": "suffix",
    "symbol": "symbol",
    "transitive verb": "verb",
    "verb": "verb",
    "verbal noun": "noun",
    "verbs": "verb",
}

# Set of all possible parts-of-speech returned by wiktionary reading.
PARTS_OF_SPEECH = set(pos_map.values())

# Templates ({{name|...}}) that will be replaced by the value of their
# first argument when cleaning up titles/values.
clean_arg1_tags = [
    "...",
    "Br. English form of",
    "W",
    "Wikipedia",
    "abb",
    "abbreviation of",
    "abbreviation",
    "acronym of",
    "agent noun of",
    "alt form of",
    "alt form",
    "alt form",
    "alt-form",
    "alt-sp",
    "altcaps",
    "alternate form of",
    "alternate spelling of",
    "alternative capitalisation of",
    "alternative capitalization of",
    "alternative case form of",
    "alternative form of",
    "alternative name of",
    "alternative name of",
    "alternative plural of",
    "alternative spelling of",
    "alternative term for",
    "alternative typography of",
    "altform",
    "altspell",
    "altspelling",
    "apocopic form of",
    "archaic form of",
    "archaic spelling of",
    "aspirate mutation of",
    "attributive form of",
    "attributive of",
    "caret notation of",
    "clip",
    "clipping of",
    "clipping",
    "common misspelling of",
    "comparative of",
    "contraction of",
    "dated form of",
    "dated spelling of",
    "deliberate misspelling of",
    "diminutive of",
    "ellipsis of",
    "ellipse of",
    "elongated form of",
    "en-archaic second-person singular of",
    "en-archaic third-person singular of",
    "en-comparative of",
    "en-irregular plural of",
    "en-past of",
    "en-second person singular past of",
    "en-second-person singular past of",
    "en-simple past of",
    "en-superlative of",
    "en-third person singular of",
    "en-third-person singular of",
    "euphemistic form of",
    "euphemistic spelling of",
    "eye dialect of",
    "eye dialect",
    "eye-dialect of",
    "femine of",
    "feminine noun of",
    "feminine plural of",
    "feminine singular of",
    "form of",
    "former name of",
    "gerund of",
    "hard mutation of",
    "honoraltcaps",
    "imperative of",
    "informal form of"
    "informal spelling of",
    "initialism of",
    "ja-l",
    "ja-r",
    "lenition of",
    "masculine plural of",
    "masculine singular of",
    "misconstruction of",
    "misspelling of",
    "mixed mutation of",
    "n-g",
    "native or resident of",
    "nb...",
    "neuter plural of",
    "neuter singular of",
    "ngd",
    "nobr",
    "nominative plural of",
    "non-gloss definition",
    "non-gloss",
    "nonstandard form of",
    "nonstandard spelling of",
    "nowrap",
    "obsolete form of",
    "obsolete spelling of",
    "obsolete typography of",
    "overwrite",
    "past of",
    "past sense of",
    "past tense of",
    "pedlink",
    "pedlink",
    "plural form of",
    "plural of",
    "present of",
    "present particle of",
    "present tense of",
    "pronunciation spelling of",
    "pronunciation spelling",
    "pronunciation respelling of",
    "rare form of",
    "rare spelling of",
    "rareform",
    "second person singular past of",
    "second-person singular of",
    "second-person singular past of",
    "short for",
    "short form of",
    "short of",
    "singular form of",
    "singular of",
    "slim-wikipedia",
    "soft mutation of",
    "standard form of",
    "standard spelling of",
    "standspell",
    "sub",
    "sup",
    "superlative of",
    "superseded spelling of",
    "swp",
    "taxlink",
    "taxlinknew",
    "uncommon spelling of",
    "unsupported",
    "verb",
    "vern",
    "w",
    "wikipedia",
    "wikisaurus",
    "wikispecies",
    "zh-m",
]

# Templates that will be replaced by their second argument when cleaning up
# titles/values.
clean_arg2_tags = [
    "zh-l",
    "ja-l",
    "l",
    "defn",
    "w",
    "m",
    "mention",
]

# Templates that will be replaced by their third argument when cleaning up
# titles/values.
clean_arg3_tags = [
    "w2",
]

# Templates that will be replaced by a value when cleaning up titles/values.
# The replacements may refer to the first argument of the template using \1.
#
# Note that there is a non-zero runtime cost for each replacement in this
# dictionary; keep its size reasonable.
clean_replace_map = {
    "en dash": " - ",
    "em dash": " - ",
    "ndash": " - ",
    "\\": " / ",
    "...": "...",
    "BCE": "BCE",
    "B.C.E.": "B.C.E.",
    "CE": "CE",
    "C.E.": "C.E.",
    "BC": "BC",
    "B.C.": "B.C.",
    "A.D.": "A.D.",
    "AD": "AD",
    "Latn-def": "latin character",
    "sumti": r"x\1",
    "inflection of": r"inflection of \1",
    "given name": r"\1 given name",
    "forename": r"\1 given name",
    "historical given name": r"\1 given name",
    "surname": r"\1 surname",
    "taxon": r"a taxonomic \1",
    "SI-unit": "a unit of measurement",
    "SI-unit-abb2": "a unit of measurement",
    "SI-unit-2": "a unit of measurement",
    "SI-unit-np": "a unit of measurement",
    "gloss": r"(\1)",
}

# Note: arg_re contains two sets of parenthesis
arg_re = (r"(\|[-_a-zA-Z0-9]+=[^}|]+)*"
          r"\|(([^|{}]|\{\{[^}]*\}\}|\[\[[^]]+\]\]|\[[^]]+\])*)")

# Matches more arguments and end of template
args_end_re = r"(" + arg_re + r")*\}\}"

# Regular expression for replacing templates by their arg1.  arg1 is \3
clean_arg1_re = re.compile(r"(?s)\{\{(" +
                           "|".join(re.escape(x) for x in clean_arg1_tags) +
                           r")" +
                           arg_re + args_end_re)

# Regular expression for replacing templates by their arg2.  arg2 is \4
clean_arg2_re = re.compile(r"(?s)\{\{(" +
                           "|".join(re.escape(x) for x in clean_arg2_tags) +
                           r")" + arg_re + arg_re + args_end_re)

# Regular expression for replacing templates by their arg3.  arg3 is \6
clean_arg3_re = re.compile(r"(?s)\{\{(" +
                           "|".join(re.escape(x) for x in clean_arg3_tags) +
                           r")" + arg_re + arg_re + arg_re + args_end_re)

# Mapping from German verb form arguments to "canonical" values in
# word sense tags."""
de_verb_form_map = {
    # Keys under which to look for values
    "_keys": [2, 3, 4, 5, 6, 7, 8, 9],
    # Mapping of values in arguments to canonical values
    "1": ["1"],
    "2": ["2"],
    "3": ["3"],
    "pr": ["present participle"],
    "pp": ["past participle"],
    "i": ["imperative"],
    "s": ["singular"],
    "p": ["plural"],
    "g": ["present"],
    "v": ["past"],
    "k1": ["subjunctive 1"],
    "k2": ["subjunctive 2"],
}

# Mapping from Spanish verb form values to "canonical" values."""
es_verb_form_map = {
    # Argument names under which we search for values.
    "_keys": ["mood", "tense", "num", "number", "pers", "person", "formal",
              "sense", "sera", "gen", "gender"],
    # Mapping of values in arguments to canonical values
    "ind": ["indicative"],
    "indicative": ["indicative"],
    "subj": ["subjunctive"],
    "subjunctive": ["subjunctive"],
    "imp": ["imperative"],
    "imperative": ["imperative"],
    "cond": ["conditional"],
    "par": ["past participle"],
    "part": ["past participle"],
    "participle": ["past participle"],
    "past-participle": ["past participle"],
    "past participle": ["past participle"],
    "adv": ["present participle"],
    "adverbial": ["present participle"],
    "ger": ["present participle"],
    "gerund": ["present participle"],
    "gerundive": ["present participle"],
    "gerundio": ["present participle"],
    "present-participle": ["present participle"],
    "present participle": ["present participle"],
    "pres": ["present"],
    "present": ["present"],
    "pret": ["preterite"],
    "preterit": ["preterite"],
    "preterite": ["preterite"],
    "imp": ["past"],
    "imperfect": ["past"],
    "fut": ["future"],
    "future": ["future"],
    "cond": ["conditional"],
    "conditional": ["conditional"],
    "s": ["singular"],
    "sing": ["singular"],
    "singular": ["singular"],
    "p": ["plural"],
    "pl": ["plural"],
    "plural": ["plural"],
    "1": ["1"],
    "first": ["1"],
    "first-person": ["1"],
    "2": ["2"],
    "second": ["2"],
    "second person": ["2"],
    "second-person": ["2"],
    "3": ["3"],
    "third": ["3"],
    "third person": ["3"],
    "third-person": ["3"],
    "y": ["formal"],
    "yes": ["formal"],
    "no": ["not formal"],
    "+": ["affirmative"],
    "aff": ["affirmative"],
    "affirmative": ["affirmative"],
    "-": ["negative"],
    "neg": ["negative"],
    "negative": ["negative"],
    "se": ["se"],
    "ra": ["ra"],
    "m": ["masculine"],
    "masc": ["masculine"],
    "masculine": ["masculine"],
    "f": ["feminine"],
    "fem": ["feminine"],
    "feminine": ["feminine"],
}


# Mapping from a template name (without language prefix) for the main word
# (e.g., fi-noun, fi-adj, en-verb) to permitted parts-of-speech in which
# it could validly occur.  This is used as just a sanity check to give
# warnings about probably incorrect coding in Wiktionary.
template_allowed_pos_map = {
    "abbr": ["abbrev"],
    "abbr": ["abbrev"],
    "noun": ["noun", "abbrev", "pron", "name", "num"],
    "plural noun": ["noun", "name"],
    "proper noun": ["noun", "name", "proper-noun"],
    "proper-noun": ["name", "noun", "proper-noun"],
    "verb": ["verb", "phrase"],
    "plural noun": ["noun"],
    "adv": ["adv"],
    "particle": ["adv", "particle"],
    "adj": ["adj"],
    "pron": ["pron", "noun"],
    "name": ["name", "noun", "proper-noun"],
    "adv": ["adv", "intj", "conj", "particle"],
    "phrase": ["phrase"],
}


# Corrections for misspelled section titles.  This basically maps the actual
# subsection title to the title that will be used when we parse it.  We should
# really review and fix all Wiktionary entries that use these, especially the
# misspellings.  In some cases we should improve the code to handle the
# additional information provided by the section title (e.g., gender).
# XXX do that later.
sectitle_corrections = {
    "adjectif": "adjective",
    "alernative forms": "alternative forms",
    "antonyid": "antonyms",
    "antoynms": "antonyms",
    "conjugaton 1": "declension",  # XXX
    "conjugaton 2": "declension",  # XXX
    "coordinate terid": "coordinate terms",
    "decelsnion": "declension",
    "decentants": "descendants",
    "declension (fem.)": "declension",  # XXX should utilize this
    "declension (masc.)": "declension",  # XXX should utilize this
    "declension (neut.)": "declension",  # XXX should utilize this
    "declension (person)": "declension",  # XXX
    "declension for adjectives": "declension",
    "declension for feminine": "declension",  # XXX
    "declension for nouns": "declension",
    "declension for sense 1 only": "declension",  # XXX
    "declension for sense 2 only": "declension",  # XXX
    "declension for words with singular and plural": "declension",  # XXX
    "declension for words with singular only": "declension",  # XXX
    "declination": "declension",
    "deived terms": "derived terms",
    "derived teerms": "derived terms",
    "derived temrs": "derived terms",
    "derived terrms": "derived terms",
    "derived words": "derived terms",
    "derivedt terms": "derived terms",
    "deriveed terms": "derived terms",
    "derivered terms": "derived terms",
    "etimology": "etymology",
    "etymlogy": "etymology",
    "etymology2": "etymology",
    "expresion": "expression",
    "feminine declension": "declension",  # XXX
    "holonyid": "holonyms",
    "hypernym": "hypernyms",
    "hyponyid": "hyponyms",
    "inflection 1 (fem.)": "declension",  # XXX
    "inflection 1 (way)": "declension",  # XXX
    "inflection 2 (neut.)": "declension",  # XXX
    "inflection 2 (time)": "declension",  # XXX
    "inflection": "declension",
    "masculine declension": "declension",  # XXX
    "nouns and adjective": "noun",  # XXX not really correct
    "nouns and adjectives": "noun",   # XXX this isn't really correct
    "nouns and other parts of speech": "noun",   # XXX not really correct
    "opposite": "antonyms",
    "participles": "verb",
    "pronounciation": "pronunciation",
    "pronuncation": "pronunciation",
    "pronunciaion": "pronunciation",
    "pronunciation and usage notes": "pronunciation",
    "pronunciationi": "pronunciation",
    "pronunciations": "pronunciation",
    "pronunciaton": "pronunciation",
    "pronunciayion": "pronunciation",
    "pronuniation": "pronunciation",
    "pronunciation 1": "pronunciation",
    "pronunciation 2": "pronunciation",
    "pronunciation 3": "pronunciation",
    "pronunciation 4": "pronunciation",
    "quptations": "quotations",
    "realted terms": "related terms",
    "refereces": "references",
    "referenes": "references",
    "refererences": "references",
    "referneces": "references",
    "refernecs": "references",
    "related names": "related terms",
    "related terid": "related terms",
    "synomyms": "synonyms",
    "synonmys": "synonyms",
    "synonym": "synonyms",
    "synonymes": "synonyms",
    "syonyms": "synonyms",
    "syonynms": "synonyms",
    "usagw note": "usage note",
}


def remove_html_comments(text):
    """Removes HTML comments from the value."""
    assert isinstance(text, str)
    text = text.strip()
    text = re.sub(r"(?s)<!--.*?-->", "", text)
    return text


def clean_value(title):
    """Cleans a title or value into a normal string.  This should basically
    remove any Wikimedia formatting from it: HTML tags, templates, links,
    emphasis, etc.  This will also merge multiple whitespaces into one
    normal space and will remove any surrounding whitespace."""
    # Remove HTML comments
    title = re.sub(r"(?s)<!--.*?-->", "", title)
    # Replace tags for which we have replacements.
    for k, v in clean_replace_map.items():
        if v.find("\\") < 0:
            title = re.sub(r"\{\{" + re.escape(k) + r"\}\}", v, title)
        else:
            v = re.sub(r"\\2", r"\\7", v)
            v = re.sub(r"\\1", r"\\4", v)
            title = re.sub(r"\{\{" + re.escape(k) +
                           r"((" + arg_re + r")"
                           r"(" + arg_re + r")?)?"
                           r"\}\}",
                           v, title)
    # Replace tags by their arguments.  Note that they may be nested, so we
    # keep repeating this until there is no change.  The regexps can only
    # handle one level of nesting (i.e., one template inside another).
    while True:
        orig = title
        title = re.sub(clean_arg3_re, r"\9", title)
        title = re.sub(clean_arg2_re, r"\6", title)
        title = re.sub(clean_arg1_re, r"\3", title)
        if title == orig:
            break
    # Remove any remaining templates.
    title = re.sub(r"\{\{[^}]+\}\}", "", title)
    # Remove references (<ref>...</ref>).
    title = re.sub(r"(?s)<ref>.*?</ref>", "", title)
    # Remove any remaining HTML tags.
    title = re.sub(r"(?s)<[^>]+>", "", title)
    # Replace links with [[...|...]] by their only or second argument
    title = re.sub(r"\[\[(([^]|]+\|)?)([^]|]+?)\]\]", r"\3", title)
    # Replace HTML links [url display] (with space) by the display value.
    title = re.sub(r"\[[^ ]+?\s+([^]]+?)\]", r"\1", title)
    # Replace remaining HTML links by the URL.
    title = re.sub(r"\[([^]]+)\]", r"\1", title)
    # Replace various empases (quoted text) by its value.
    title = re.sub(r"''+(([^']|'[^'])+?)''+", r"\1", title)
    # Replace HTML entities
    title = html.unescape(title)
    title = re.sub("\xa0", " ", title)  # nbsp
    # This unicode quote seems to be used instead of apostrophe quite randomly
    # (about 4% of apostrophes in English entries, some in Finnish entries).
    title = re.sub("\u2019", "'", title)  # Note: no r"..." here!
    # Replace whitespace sequences by a single space.
    title = re.sub(r"\s+", " ", title)
    # Remove whitespace before periods and commas etc
    title = re.sub(r" ([.,;:!?)])", r"\1", title)
    # Strip surrounding whitespace.
    title = title.strip()
    return title


def split_subsections(text):
    """Split the text into a linear sequence of sections.  Note that we
    ignore the nesting structure of subtitles, since that seems to be
    poorly enforced in Wiktionary.  This returns a list of (subtitle,
    text).  The subtitle has been fully cleaned, and HTML comments
    have been removed from the text."""
    # Remove HTML comments from the whole page.  We want to do this before
    # analyzing subsections, as they could be commented out.
    text = remove_html_comments(text)
    # Find start and end offsets and titles for all subsections
    regexp = r"(?s)(^|\n)==+([^=\n]+?)==+"
    offsets = list((m.start(), m.end(), clean_value(m.group(2)))
                   for m in re.finditer(regexp, text))
    # Add a dummy section at end of text.
    offsets.append((len(text), len(text), ""))
    # Create first subsection from text before the first subtitle
    subsections = []
    first = text[:offsets[0][0]]
    if first:
        subsections.append(("", first))
    # Add all other subsections (except the dummy one)
    for i in range(len(offsets) - 1):
        titlestart, start, subtitle = offsets[i]
        # Get end offset from the entry for the next subsection
        end = offsets[i + 1][0]
        # Clean the section title
        subtitle = clean_value(subtitle)
        # Add an entry for the subsection.
        subsection = text[start: end]
        subsections.append((subtitle, subsection))
    return subsections


def data_append(data, key, value):
    """Appends ``value`` under ``key`` in the dictionary ``data``.  The key
    is created if it does not exist."""
    assert isinstance(data, dict)
    assert isinstance(key, str)
    lst = data.get(key, [])
    lst.append(value)
    if lst:
        data[key] = lst


def data_extend(data, key, values):
    """Appends all values in a list under ``key`` in the dictionary ``data``."""
    assert isinstance(data, dict)
    assert isinstance(key, str)
    assert isinstance(values, (list, tuple))
    lst = data.get(key, [])
    lst.extend(values)
    if lst:
        data[key] = lst


def template_args_to_dict(t):
    """Returns a dictionary containing the template arguments.  This is
    typically used when the argument dictionary will be returned from the
    parsing.  Positional arguments will be keyed by numeric strings.
    The name of the template will be added under the key "template_name"."""
    ht = {}
    for x in t.arguments:
        name = x.name.strip()
        value = x.value
        ht[name] = value
    ht["template_name"] = t.name.strip()
    return ht


def clean_quals(vec):
    """Extracts and cleans qualifier values from the vector of arguments.
    Qualifiers are generally usage or other notes such as "archaic",
    "colloquial", "chemistry", "british", etc.  There is no standard set
    of values for them and the set probably varies from language to
    language."""
    assert isinstance(vec, (list, tuple))
    for x in vec:
        assert isinstance(x, str)

    tags = []
    for i in range(len(vec)):
        x = vec[i]
        i += 1
        if x in ("en", "fi"):
            # If the qualifiers are from a template that has language tags,
            # those hould be removed from the vector before passing it to
            # this function.  This warning indicates the caller probably
            # forgot to remove the language tag.
            print("clean_quals: WARNING: {} in vec: {}".format(x, vec))
            continue
        # Certain modifiers are often written as separate arguments but
        # actually modify the following value.  We combine them with the
        # following value using a space.
        while (i < len(vec) - 1 and
               vec[-1] in ("usually", "often", "rarely", "strongly",
                           "extremely", "including",
                           "chiefly", "sometimes", "mostly", "with", "now")):
            x += " " + vec[i]
            i += 1
        # Values may be combined using "and" and "or" or "_".  We replace
        # all these by a space and combine.
        while (i < len(vec) - 2 and
               vec[i] in ("_", "and", "or")):
            x += " " + vec[i + 1]
            i += 2
        tags.append(x)
    return tags


def t_vec(t):
    """Returns a list containing positional template arguments.  Empty strings
    will be added for any omitted arguments.  The vector will include the last
    non-empty supplied argument, but not values beyond it."""
    vec = []
    for i in range(1, 20):
        v = t_arg(t, i)
        vec.append(v)
    while vec and not vec[-1]:
        vec.pop()
    return vec


def t_arg(t, arg):
    """Retrieves argument ``arg`` from the template.  The argument may be
    identified either by its number or a string name.  Positional argument
    numbers start at 1.  This returns the empty string for arguments that
    don't exist.  The argument value is cleaned before returning."""
    # If the argument specifier is an integer, convert it to a string.
    if isinstance(arg, int):
        arg = str(arg)
    assert isinstance(arg, str)
    # Get the argument value from the template.
    v = t.get_arg(arg)
    # If it does not exist, return empty string.
    if v is None:
        return ""
    # Otherwise clean the value.
    return clean_value(v.value)


def verb_form_map_fn(word, data, name, t, form_map):
    """Maps values in a language-specific verb form map into values for "tags"
    that are reasonably uniform across languages.  This also deals with a
    lot of misspellings and inconsistencies in how the values are entered in
    Wiktionary.  ``data`` here is the word sense."""
    # Add an indication that the word sense is a form of an other word.
    data_append(data, "form_of", t_arg(t, 1))
    # Iterate over the specified keys in the template.
    for k in form_map["_keys"]:
        v = t_arg(t, k)
        if not v:
            continue
        # Got a value for key.  Now map the value.  Each entry in the
        # dictionary should be a list of tags to add.
        if v in form_map:
            lst = form_map[v]
            assert isinstance(lst, (list, tuple))
            for x in lst:
                assert isinstance(x, str)
                data_append(data, "tags", x)
        else:
            print(word, "UNKNOWN VERB FORM KEY", k, "IN", name, "of:",
                  v, "in:", str(t))


def parse_sense(word, text):
    """Parses a word sense from the text.  The text is usually a list item
    from the beginning of the dictionary entry (i.e., before the first
    subtitle).  There is a lot of information and linkings in the sense
    description, which we try to gather here.  We also try to convert the
    various encodings used in Wiktionary into a fairly uniform form.
    The goal here is to obtain any information that might be helpful in
    automatically determining the meaning of the word sense."""

    # The gloss is just the value cleaned into a string.  However, much of
    # the useful information is in the tagging within the text.  Note that
    # some entries don't really have a gloss text; for them, we may only
    # obtain some machine-readable linkages.
    gloss = clean_value(text)
    data = {}
    if gloss:
        # Got a gloss for this sense.
        data_append(data, "glosses", gloss)

    # Parse the Wikimedia coding from the text.
    p = wikitextparser.parse(text)

    # Iterate over all templates in the text.
    for t in p.templates:
        name = t.name.strip()

        # Check for silently ignored templates, and skip them.
        if name in ignored_templates:
            continue
        # Labels and various other links are used for qualifiers. However,
        # they also seem to be sometimes used for other purposes, so this
        # may result in extra tags that perhaps should be elsewhere.
        elif name in ("lb", "label", "context", "term-context", "term-label",
                      "lbl", "tlb", "tcx"):
            data_extend(data, "tags", clean_quals(t_vec(t)[1:]))
        # Qualifiers are pretty clear; they provide useful information about
        # the word sense, such as field of study, dialect, or usage notes.
        elif name in ("qual", "qualifier", "q", "qf", "i"):
            data_extend(data, "tags", clean_quals(t_vec(t)))
        # Usage examples are collected under "examples"
        elif name == "ux":
            data_append(data, "examples", (t_arg(t, 2), t_arg(t, 3)))
        # Additional "gloss" templates are added under "glosses"
        #elif name == "gloss":
        #    gloss = t_arg(t, 1)
        #    data_append(data, "glosses", gloss)
        # Various words have non-gloss definitions; we collect them under
        # "nonglosses".  For many purposes they might be treated similar to
        # glosses, though.
        elif name in ("non-gloss definition", "n-g", "ngd", "non-gloss"):
            gloss = t_arg(t, 1)
            data_append(data, "nonglosses", gloss)
        # The senseid template seems to have varied uses. Sometimes it contains
        # a Wikidata id Q<numbers>; at other times it seems to be something
        # else.  We collect them under "senseid".  XXX this needs more study
        elif name == "senseid":
            data_append(data, "senseid", t_arg(t, 2))
        # The "sense" templates are treated as additional glosses.
        elif name == "sense":
            gloss = t_arg(t, 1)
            data_append(data, "glosses", gloss)
        # US state names seem to have a special tagging as such.  We tag them
        # as places, indicate that they are a part of the Unites States, and
        # are places of type "state".
        elif name == "USstate":
            data_append(data, "tags", "place")
            data_append(data, "holonyms", "United States")
            data_append(data, "place", {"type": "state",
                                        "english": [word]})
        # These weird templates seem to be used to indicate a literal sense.
        elif name in ("&lit", "&oth"):
            data_append(data, "tags", "literal")
        # Many given names (first names) are tagged as such.  We tag them as
        # such, and tag with gender when available.  We also tag the term
        # as meaning an organism (though this might not be the case in rare
        # cases) and "person" (if it has a gender).
        elif name in ("given name",
                      "forename",
                      "historical given name"):
            gender = t_arg(t, 1)
            data_extend(data, "tags", ["given name", "organism"])
            if gender in ("male", "female", "unisex"):
                data_append(data, "tags", gender)
                data_append(data, "tags", "person")
            elif gender == "male or female":
                pass
            elif gender:
                print(word, "PARSE_SENSE: unrecognized gender", repr(gender))
        # Surnames are also often tagged as such, and we tag the sense
        # with "surname" and "person".
        elif name == "surname":
            data_extend(data, "tags", ["surname", "person"])
            from_ = t_arg(t, "from")
            if from_:
                data_append(data, "origin", from_)
        # Various tags seem to indicate topical categories that the
        # word belongs to.  These are added under "topics".
        # XXX similar things are also express by qualifiers (fields of study);
        # should investigate if these should be combined.
        elif name in ("topics", "categorize", "catlangname", "c", "C", "cln",
                      "top", "categorise"):
            data_extend(data, "topics", t_vec(t)[1:])
            data_extend(data, "tags", t_vec(t)[1:])
        # Many nouns that are species and other organism types have taxon
        # links using various templates.  Store those links under
        # "taxon" without trying to interpret them here.
        elif name in ("taxlink", "taxon", "taxlinkwiki"):
            data_append(data, "taxon", t_vec(t))
            data_append(data, "tags", "organism")
        # Many organisms have vernacular names.  If such is specified,
        # mark the word sense as an alternative term for the same and tag it
        # as an "organism".
        elif name == "vern":
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "organism")
        # Many colors have a color panel that defines the RGB value of the
        # color.  This provides a physical reference for what the color means
        # and identifies the word as a color value.  Record the corresponding
        # RGB value under "color".  Sometimes it may be a CSS color
        # name, sometimes an RGB value in hex.
        elif name in ("color panel", "colour panel"):
            v = t_vec(t)
            if len(v) == 1:
                data_append(data, "color", v[0])
            else:
                data_append(data, "color", v[1])
        elif name in ("colorbox", "colourbox"):
            data_append(data, "color", t_arg(t, 1))
        # Numbers often have a number box, which will indicate the numeric
        # value meant by the word.  We record the numeric value under "value".
        # (There is also other information that we don't currently capture.)
        elif name == "number box":
            data_append(data, "value", t_arg(t, 2))
        # SI units of measurement appear to have tags that identify them
        # as such.  Add the information under "unit" and tag them as "unit".
        elif name in ("SI-unit", "SI-unit-2",
                      "SI-unit-np"):
            print(word, name, template_args_to_dict(t))
            data_append(data, "unit", template_args_to_dict(t))
            data_append(data, "tags", "unit")
        elif name in ("SI-unit-abb", "SI-unit-abbnp"):
            data_append(data, "unit", template_args_to_dict(t))
            data_append(data, "tags", "unit")
            mul = t_arg(t, 1)
            base = t_arg(t, 2)
            metric = t_arg(t, 3)
            gloss = ("{}{}, a unit of measurement for {}"
                     "".format(mul, base, metric))
            data_append(data, "glosses", gloss)
        elif name == "SI-unit-abb2":
            data_append(data, "unit", template_args_to_dict(t))
            data_append(data, "tags", "unit")
            mul = t_arg(t, 1)
            base = t_arg(t, 2)
            base2 = t_arg(t, 3)
            metric = t_arg(t, 4)
            gloss = ("{}{}, a unit of measurement for {}"
                     "".format(mul, base, metric))
            data_append(data, "glosses", gloss)
        # There are various templates that links to other Wikimedia projects,
        # typically Wikipedia.  Record such links under "wikipedia".
        elif name in ("slim-wikipedia", "wikipedia", "wikispecies", "w", "W",
                      "swp", "pedlink", "specieslink", "comcatlite",
                      "Wikipedia", "taxlinknew"):
            v = t_arg(t, 1)
            if not v:
                v = word
            data_append(data, "wikipedia", v)
        # Various words are marked as place names.  Tag such words as a
        # "place", by the place type, and add a link under "holonyms" if what
        # the place is part of has been specified.
        elif name == "place":
            data_append(data, "tags", "place")
            data_append(data, "tags", t_arg(t, 2))
            for i in range(3, 10):
                v = t_arg(t, i)
                if v:
                    data_append(data, "holonyms", v)
        # There are even morse code sequences (and semaphore (flag)) positions
        # defined in the Translingual portion of Wiktionary.  Collect
        # morse code information under "morse_code".
        elif name in ("morse code for", "morse code of",
                      "morse code abbreviation",
                      "morse code prosign"):
            data_append(data, "morse_code", t_arg(t, 1))
        elif name in ("mul-semaphore-for", "mul-semaphore for"):
            data_append(data, "semaphore", t_arg(t, 1))
        # Some glosses identify the word as a character.  If so, tag it as
        # "character".
        elif (name == "Latn-def" or re.search("-letter$", name)):
              if not gloss:
                  data_append(data, "tags", "character")
        # There are various ways to specify that a word is a synonym or
        # alternative spelling/form of another word.  We record these all
        # under "alt_of".
        elif name in ("synonym of", "altname", "synonym",
                      "alternative form of", "alt form", "alt form of",
                      "alternative spelling of", "aspirate mutation of",
                      "alternate spelling of", "altspelling", "standspell",
                      "standard spelling of", "soft mutation of",
                      "hard mutation of", "mixed mutation of", "lenition of",
                      "alt form", "altform", "alt-form",
                      "apocopic form of", "altcaps",
                      "alternative name of", "honoraltcaps",
                      "alternative capitalisation of",
                      "alternative capitalization of", "alternate form of",
                      "alternative case form of", "alt-sp",
                      "standard form of", "alternative typography of",
                      "elongated form of", "alternative name of",
                      "uncommon spelling of",
                      "combining form of",
                      "caret notation of",
                      "alternative term for", "altspell"):
            data_append(data, "alt_of", t_arg(t, 1))
        elif name in ("Br. English form of",):
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "british")
        # Some words are marked as being pronunciation spellings, or
        # "eye dialect" words.  Record the canonical word under "alt_of" and
        # add a "spoken" tag.
        elif name in ("eye dialect of", "eye dialect", "eye-dialect of",
                      "pronunciation spelling",
                      "pronunciation respelling of",
                      "pronunciation spelling of"):
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "spoken")
        # If the gloss is marked as an obsolete/archaic spelling,
        # include "alt_of" and tag the gloss as "archaic".
        elif name in ("obsolete spelling of", "obsolete form of",
                      "obsolete typography of", "rareform",
                      "superseded spelling of", "former name of",
                      "archaic spelling of", "dated spelling of",
                      "archaic form of", "dated form of"):
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "archaic")
        # If the gloss is marked as an informal spqlling, include "alt_of" and
        # tag it as "colloquial".
        elif name in ("informal spelling of", "informal form of"):
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "colloquial")
        # If the gloss is marked as an euphemistic spelling, include "alt_of"
        # and tag it as "euphemism".
        elif name in ("euphemistic form of", "euphemistic spelling of"):
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "euphemism")
        # If the gloss is indicated as a misspelling or non-standard spelling
        # of another word, include "alt_of" and tag it as a "misspelling".
        elif name in ("deliberate misspelling of", "misconstruction of",
                      "misspelling of", "common misspelling of",
                      "nonstandard form of", "nonstandard spelling of"):
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "misspelling")
        # If the gloss is indicated as a rare form of anothe word, include
        # "alt_of" and tag it as "rare".
        elif name in ("rare form of", "rare spelling of"):
            data_append(data, "alt_of", t_arg(t, 1))
            data_append(data, "tags", "rare")
        # If the gloss is marked as an abbreviation of another term
        # (there are many ways to do this!), include "alt_of" and tag it
        # as an "abbreviation".  Also, if it includes wikipedia links,
        # include those under "wikipedia".
        elif name in ("abbreviation of", "short for", "initialism of",
                      "acronym of", "contraction of", "clipping of",
                      "clip", "clipping", "short form of", "ellipsis of",
                      "ellipse of", "short of", "abbreviation", "abb"):
            for x in t_vec(t):
                if x.startswith("w:"):
                    x = x[2:]
                    data_append(data, "wikipedia", x)
                data_append(data, "alt_of", x)
                data_append(data, "tags", "abbreviation")
        elif name in ("only used in", "only in"):
            # This appears to be used in "man" for "man enough"
            data_append(data, "only_in", t_arg(t, 1))
        # This tag indicates the word is an inflection of another word, but
        # in a complicated way that we won't try to parse here.  We include
        # the information under "complex_inflection_of".
        elif name == "inflection of":
            data_append(data, "complex_inflection_of", template_args_to_dict(t))
        # There are many templates that indicate a word is an inflected form
        # of another word.  Such tags are handled here.  For all of them,
        # we include the base form under "inflection_of" and add tags to
        # indicate the type of inflection/derivation.
        elif name == "inflected form of":
            data_append(data, "inflection_of", t_arg(t, 1))
        elif name == "agent noun of":
            data_append(data, "agent_of", t_arg(t, 1))
            # XXX does this imply a person or organism?
            data_append(data, "tags", "agent")
        elif name == "feminine plural of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "feminine")
            data_append(data, "tags", "plural")
        elif name == "feminine singular of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "feminine")
            data_append(data, "tags", "singular")
        elif name == "masculine plural of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "masculine")
            data_append(data, "tags", "plural")
        elif name == "neuter plural of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "neuter")
            data_append(data, "tags", "plural")
        elif name == "feminine noun of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "feminine")
        elif name == "masculine singular of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "masculine")
            data_append(data, "tags", "singular")
        elif name == "neuter singular of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "neuter")
            data_append(data, "tags", "singular")
        elif name == "feminine of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "feminine")
        elif name in ("present participle of", "gerund of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "participle")
            data_append(data, "tags", "present")
        elif name in ("present tense of", "present of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "present")
        elif name in ("past of", "past sense of",
                      "past tense of",
                      "en-simple past of", "en-past of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "past")
        elif name == "past participle of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "participle")
            data_append(data, "tags", "past")
        elif name in ("en-third-person singular of",
                      "en-third person singular of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_extend(data, "tags", ["present", "singular", "3"])
        elif name == "imperative of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "imperative")
        elif name == "nominative plural of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "plural")
            data_append(data, "tags", "nominative")
        elif name in ("plural of",
                      "alternative plural of",
                      "plural form of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "plural")
        elif name in ("singular of", "singular form of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "singular")
        elif name == "diminutive of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "diminutive")
        elif name == "form of":
            data_append(data, "inflection_of", t_arg(t, 2))
            data_append(data, "tags", t_arg(t, 1))
        elif name in ("comparative of", "en-comparative of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "comparative")
        elif name in ("superlative of", "en-superlative of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "superlative")
        elif name in ("attributive of", "attributive form of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "attributive")
        # Handle some English-specific word form taggings.
        elif name == "en-irregular plural of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "plural")
            data_append(data, "tags", "irregular")
        elif name == "en-archaic second-person singular of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_extend(data, "tags", ["singular", "archaic", "present", "2"])
        elif name == "second-person singular of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_extend(data, "tags", ["singular", "present", "2"])
        elif name in ("en-second-person singular past of",
                      "en-second person singular past of",
                      "second-person singular past of",
                      "second person singular past of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            data_extend(data, "tags", ["singular", "past", "2"])
        elif name == "en-archaic third-person singular of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_extend(data, "tags", ["singular", "archaic", "3"])
        # Handle some Spanish-specific word form taggings.
        elif name == "es-verb form of":
            verb_form_map_fn(word, data, name, t, es_verb_form_map)
        # Handle some German-specific word form taggings.
        elif name == "de-verb form of":
            verb_form_map_fn(word, data, name, t, de_verb_form_map)
        # Handle some Finnish-specific
        elif name == "fi-infinitive of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "infinitive")
            if t_arg(t, "t"):
                data_append(data, "tags", "inf-" + t_arg(t, "t"))
        elif name == "fi-participle of":
            data_append(data, "inflection_of", t_arg(t, 1))
            data_append(data, "tags", "participle")
            if t_arg(t, "t"):
                data_append(data, "tags", "pcp-" + t_arg(t, "t"))
        elif name == "fi-verb form of":
            data_append(data, "inflection_of", t_arg(t, 1))
            mapping = {"1s": ["1", "singular"],
                       "2s": ["2", "singular"],
                       "3s": ["3", "singular"],
                       "1p": ["1", "plural"],
                       "2p": ["2", "plural"],
                       "3p": ["3", "plural"],
                       "p": ["plural"],
                       "plural": ["plural"],
                       "s": ["singular"],
                       "pass": ["passive"],
                       "cond": ["conditional"],
                       "potn": ["potential"],
                       "impr": ["imperative"],
                       "pres": ["present"],
                       "past": ["past"]}
            for k in t.arguments:
                k = k.name.strip()
                if k in ("1", "c", "nodot", "suffix"):
                    continue
                v = t_arg(t, k)
                if v in mapping:
                    v = mapping[v]
                else:
                    print(word, "FI-VERB FORM OF", v, str(t))
                    v = [v]
                data_extend(data, "tags", v)
        elif name in ("fi-form of", "conjugation of"):
            data_append(data, "inflection_of", t_arg(t, 1))
            for k in ("suffix", "suffix2", "suffix3"):
                suffix = t_arg(t, k)
                if suffix:
                    data_append(data, "suffix", suffix)
            for k in t.arguments:
                k = k.name.strip()
                if k in ("1", "2", "3", "suffix", "suffix2", "suffix3",
                         "c", "n", "type", "lang"):
                    continue
                v = t_arg(t, k)
                if not v or v == "-":
                    continue
                if v in ("first-person", "first person", "1p"):
                    v = "1"
                elif v in ("second-person", "second person", "2p"):
                    v = "2"
                elif v in ("third-person", "third person", "3p"):
                    v = "3"
                elif v == "connegative present":
                    v = "present connegative"
                elif v in ("singural", "s"):
                    v = "singular"
                elif v in ("p,"):
                    v = "plural"
                elif v == "pres":
                    v = "present"
                elif v == "imperfect":
                    v = "past"
                if k != "case":
                    if v not in ("1", "2", "3", "impersonal",
                                 "first-person singular",
                                 "first-person plural",
                                 "second-person singular",
                                 "second-person plural",
                                 "third-person singular",
                                 "third-person plural",
                                 "first, second, and third person",
                                 "singular or plural",
                                 "plural", "singular", "present", "past",
                                 "imperative", "present connegative",
                                 "indicative connegative",
                                 "indicative present",
                                 "indicative past",
                                 "potential present",
                                 "conditional present",
                                 "potential present connegative",
                                 "connegative", "partitive", "optative",
                                 "eventive",
                                 "singular and plural", "passive",
                                 "indicative", "conditional", "potential"):
                        print(word, "FI-FORM UNRECOGNIZED", v, str(t))
                if v in ("singular and plural", "singular or plural"):
                    data_append(data, "tags", "singular")
                    data_append(data, "tags", "plural")
                elif v == "first-person singular":
                    data_append(data, "tags", "singular")
                    data_append(data, "tags", "1")
                elif v == "first-person plural":
                    data_append(data, "tags", "plural")
                    data_append(data, "tags", "1")
                elif v == "second-person singular":
                    data_append(data, "tags", "singular")
                    data_append(data, "tags", "2")
                elif v == "second-person plural":
                    data_append(data, "tags", "plural")
                    data_append(data, "tags", "2")
                elif v == "third-person singular":
                    data_append(data, "tags", "singular")
                    data_append(data, "tags", "3")
                elif v == "third-person plural":
                    data_append(data, "tags", "plural")
                    data_append(data, "tags", "3")
                elif v == "first, second, and third person":
                    pass
                elif v == "present connegative":
                    data_append(data, "tags", "present")
                    data_append(data, "tags", "connegative")
                elif v == "indicative connegative":
                    data_append(data, "tags", "indicative")
                    data_append(data, "tags", "connegative")
                elif v == "potential present connegative":
                    data_append(data, "tags", "potential")
                    data_append(data, "tags", "connegative")
                elif v == "potential present":
                    data_append(data, "tags", "potential")
                elif v == "conditional present":
                    data_append(data, "tags", "conditional")
                elif v == "indicative present":
                    data_append(data, "tags", "present")
                elif v == "indicative past":
                    data_append(data, "tags", "past")
                else:
                    data_append(data, "tags", v)
        # Brazilian states and state capitals seem to use their own tagging.
        # Collect this information in tags and links.
        elif name == "place:Brazil/state":
            data_append(data, "tags", "place")
            data_append(data, "tags", "state")
            data_append(data, "meronyms", t_arg(t, "capital"))
            data_append(data, "holonyms", "Brazil")
        elif name in ("place:Brazil/capital",):
            data_append(data, "tags", "place")
            data_append(data, "tags", "city")
            data_append(data, "tags", "capital")
            data_append(data, "holonyms", "Brazil")
        elif name in ("place:Brazil/state capital",
                      "place:state capital of Brazil"):
            data_append(data, "tags", "place")
            data_append(data, "tags", "city")
            data_append(data, "holonyms", t_arg(t, "state"))
            data_append(data, "holonyms", "Brazil")
        elif name in ("place:Brazil/municipality",
                      "place:municipality of Brazil"):
            data_append(data, "tags", "place")
            data_append(data, "tags", "region")
            data_append(data, "holonyms", t_arg(t, "state"))
            data_append(data, "holonyms", "Brazil")
        # Skip various templates in this processing.  We silence warnings
        # about unhandled tags for these.  (Many of them are handled
        # elsewhere.)
        elif name in ("audio", "audio-pron",
                      "IPA", "ipa", "a", "accent", "l", "link", "m",
                      "zh-m", "zh-l", "ja-l", "sumti",
                      "alter", "ISBN", "syn",
                      "hyph", "hyphenation", "ja-r", "ja-l", "homophones",
                      "pinyin reading of", "enPR",
                      "mul-kangxi radical-def", "speciesabbrev",
                      "mul-kanadef",
                      "mul-domino def",
                      "mul-cjk stroke-def",
                      "Han char", "zh-only",
                      "gloss",
                      "non-gloss definition", "n-g", "ngd", "non-gloss"):
            continue
        # There are whole patterns of templates that we don't want warnings for.
        elif re.search(r"IPA|^RQ:|^R:|"
                       r"-romanization$|-romanji$|romanization of$",
                       name):
            continue
        # Otherwise warn about an unhandled template.  It is normal to get
        # a few of these warnings whenever this is run; such templates may
        # later be added to the silencing list above or proper handling may
        # be added for them.  For a few templates, they have intentionally
        # not yet been silenced because they could be useful but their use is
        # still too rare to bother collecting them.
        else:
            print(word, "INSIDE GLOSS:", repr(name), str(t))
    # Various fields should only contain strings.  Check that they do
    # (helps find bugs fast).  Also remove any duplicates from the lists and
    # sort them into ascending order for easier reading.
    for k in ("tags", "glosses", "holonyms" "meronyms", "hypernyms", "hyponyms",
              "antonyms", "synonyms", "derived", "form_of", "alt_of",
              "inflection_of", "color", "wikidata"):
        if k not in data:
            continue
        for x in data[k]:
            if not isinstance(x, str):
                print(word, "INTERNAL ERROR GLOSS PARSING", k, data.get(k, ()))
                assert False
        data[k] = list(set(sorted(data[k])))

    return data


def parse_preamble(word, data, pos, text, p):
    """Parse the head template for the word (part-of-speech) and other
    stuff that affects all senses.  Then parse the word sense defintions."""
    heads = []
    plural = False
    for t in p.templates:
        name = t.name.strip()
        if re.search("plural", name):
            plural = True
        # Note: want code below in addition to code above.
        # Record the head template fo the word entry. This often contains
        # important inflection information (e.g., comparatives and verb
        # forms).
        #
        # Also Warn about potentially incorrect templates for the
        # part-of-speech (common error in Wiktionary that should be corrected
        # there).
        m = re.search("^head$|^[a-z][a-z][a-z]?-(plural noun|noun|verb|adj|adv|name|proper-noun|pron|phrase)(-|$)", name)
        if m:
            tagpos = m.group(1) or pos
            if ((tagpos not in template_allowed_pos_map or
                 pos not in template_allowed_pos_map[tagpos]) and
                m.group(0) != "head"):
                print(word, "SUSPECT POS", pos, tagpos, str(t))
            # Record the head template under "heads".
            data_append(data, "heads", template_args_to_dict(t))
        # If hyphenation information has been provided, record it.
        elif name in ("hyphenation", "hyph"):
            data_append(data, "hyphenation", t_vec(t))
        # If pinyin reading has been provided, record it (this is reading
        # of a Chinese word in romanized forms, i.e., western characters).
        elif name == "pinyin reading of":
            data_extend(data, "pinyin", t_vec(t))
        # XXX what other potentially useful information might be available?

    # Parse word senses for the part-of-speech.
    for node in p.lists():
        for item in node.items:
            sense = parse_sense(word, str(item))
            if plural and "plural" not in sense.get("tags", ()):
                sense["tags"] = list(sorted(set(sense.get("tags", []) +
                                                ["plural"])))
            data_append(data, "senses", sense)
    # XXX there might be word senses encoded in other ways, without using
    # a list for them.  Do some tests to find out how common this is.


def parse_pronunciation(word, data, text, p):
    """Extracts pronunciation information for the word."""

    def parse_variant(text):
        variant = {}
        sense = None

        p = wikitextparser.parse(text)
        for t in p.templates:
            name = t.name.strip()
            # Silently ignore templates that we don't care about.
            if name in ignored_templates:
                continue
            elif name == "sense":
                # Some words, like "house" (English) have a two-level structure
                # with different pronunciations for verbs and nouns, with
                # {{sense|...}} used to distinguish them
                sense = t_arg(t, 1)
            # Pronunciation may be qualified by
            # accent/dialect/variant.  These are recorded under
            # "tags".  See
            # https://en.wiktionary.org/wiki/Module:accent_qualifier/data
            elif name in ("a", "accent"):
                data_extend(variant, "accent", clean_quals(t_vec(t)))
            # These other qualifiers and context markers may be used for
            # similar things, but their values are less well defined.
            elif name in ("qual", "qualifier", "q", "qf"):
                data_extend(variant, "tags", t_vec(t))
            elif name in ("lb", "context",
                          "term-context", "tcx", "term-label", "tlb", "i"):
                print(word, "Pronunciation qualifier:", str(t))
                data_extend(variant, "tags", clean_quals(t_vec(t)[1:]))
            # Extact IPA pronunciation specification under "ipa".
            elif name in ("IPA", "ipa"):
                data_append(variant, "ipa",
                            (t_arg(t, "lang"), t_arg(t, 1)))
            # Extract special variants of the IPA template.  Store these as
            # dictionaries under "special_ipa".
            elif re.search("IPA", name):
                data_append(variant, "special_ipa", template_args_to_dict(t))
            # If English pronunciation (enPR) has been specified, record them
            # under "enpr".
            elif name == "enPR":
                data_append(variant, "enpr", t_arg(t, 1))
            # There are also some other forms of pronunciation information that
            # we collect; it is not yet clear what all these mean.
            elif name in ("it-stress",):
                data_append(variant, "stress", t_arg(t, 1))
            elif name == "PIE root":
                data_append(variant, "pie_root", t_arg(t, 2))
            # If an audio file has been specified for the word,
            # collect those under "audios".
            elif name in ("audio", "audio-pron"):
                data_append(variant, "audios",
                            (t_arg(t, "lang"),
                             t_arg(t, 1),
                             t_arg(t, 2)))
            # If homophones have been specified, collect those under
            # "homophones".
            elif name in ("homophones", "homophone"):
                data_extend(variant, "homophones", t_vec(t))
            elif name == "hyphenation":
                # This is often in pronunciation, but we'll store it at top
                # level in the entry
                data_append(data, "hyphenation", t_vec(t))
            # These templates are silently ignored for pronunciation information
            # collection purposes.
            elif name in ("inflection of", "l", "link", "m", "w", "W", "label",
                          "gloss", "zh-m", "zh-l", "ja-l",
                          "ux", "ant", "syn", "synonyms", "antonyms",
                          "wikipedia", "Wikipedia",
                          "alternative form of", "alt form",
                          "altform", "alt-form", "abb", "rareform",
                          "alter", "hyph", "honoraltcaps",
                          "non-gloss definition", "n-g", "non-gloss",
                          "ngd", "topics", "top", "c", "C", "categorize",
                          "catlangname", "categorise",
                          "senseid", "defn", "ja-r", "ja-l",
                          "place:Brazil/state",
                          "place:Brazil/municipality",
                          "place", "taxlink",
                          "color panel", "pedlink", "vern", "prefix", "affix",
                          "suffix", "wikispecies", "ISBN", "slim-wikipedia",
                          "swp", "comcatlite", "forename",
                          "given name", "surname", "head"):
                continue
            # Any templates matching these are silently ignored for
            # pronunciation information collection purposes.
            elif re.search(r"^R:|^RQ:|^&|"
                           r"-form|-def|-verb|-adj|-noun|-adv|"
                           r"-prep| of$|"
                           r"-romanization|-romanji|-letter|"
                           r"^en-|^fi-|",
                           name):
                continue
            else:
                # Warn about unhandled templates.
                print(word, "UNRECOGNIZED PRONUNCIATION", str(t))

        if sense:
            variant["sense"] = sense

        # If we got some useful pronunciation information, save it
        # under "sounds" in the word entry.
        if len(set(variant.keys()) - set(["tags", "sense", "accent"])):
            data_append(data, "pronunciations", variant)

    # If the pronunciation section does not contain a list, parse it all
    # as a single pronunciation variant.  Otherwise parse each list item
    # separately.
    spans = []
    for node in p.lists():
        spans.append(node.span)
        for item in node.items:
            parse_variant(str(item))
    for s, e in reversed(spans):
        text = text[:s] + text[e:]
    text = text.strip()
    if text:
        parse_variant(text)


def parse_linkage(word, data, kind, text, p, sense_text=None):
    """Parses links to other words, such as synonyms, hypernyms, etc.
    ```kind``` identifies the default type for such links (based on section
    header); however, it is not entirely reliable.  The particular template
    types used may also indicate what type of link it is; we trust that
    information more."""

    added = set()

    def parse_item(text, kind, is_item):

        sense_text = None
        qualifiers = ()

        def add_linkage(kind, v):
            nonlocal qualifiers
            v = v.strip()
            if v.startswith("See also"):  # Used to refer to thesauri
                return
            if v.find(" Thesaurus:") >= 0:  # Thesaurus links handled separately
                return
            if v.lower() == "see also":
                return
            if v.startswith("Category:"):
                # These are probably from category links at the end of page,
                # which could end up in any section.
                return
            if v.startswith(":Category:"):
                v = v[1:]
            elif v.startswith("See "):
                v = v[4:]
            if v.endswith("."):
                v = v[:-1]
            v = v.strip()
            if not v:
                return
            key = (kind, v, sense_text, tuple(sorted(qualifiers)))
            if key in added:
                return
            added.add(key)
            v = {"word": v}
            if sense_text:
                v["sense"] = sense_text
            if qualifiers:
                v["tags"] = qualifiers
            data_append(data, kind, v)
            qualifiers = ()

        # Parse the item text.
        p = wikitextparser.parse(text)
        if len(text) < 200 and text and text[0] not in "*:":
            item = clean_value(text)
            if item:
                if item.startswith("For more, see "):
                    item = item[14:]

                for t in p.templates:
                    name = t.name.strip()
                    if name == "sense":
                        sense_text = t_arg(t, 1)
                    elif name == "l":
                        add_linkage(kind, t_arg(t, 2))

                found = False
                for m in re.finditer(r"''+([^']+)''+", text):
                    v = m.group(1)
                    v = clean_value(v)
                    if v.startswith("(") and v.endswith(")"):
                        # These seem to often be qualifiers
                        sense_text = v[1:-1]
                        continue
                    add_linkage(kind, v)
                    found = True
                if found:
                    return

                m = re.match(r"^\((([^)]|\([^)]+\))*)\):? ?(.*)$", item)
                if m:
                    q = m.group(1)
                    sense_text = q
                    item = m.group(3)
                # Parenthesized parts at the end often contain extra stuff
                # that we don't want
                item = re.sub(r"\([^)]+\)\s*", "", item)
                # Semicolons and dashes commonly occur here in phylum hypernyms
                for v in item.split("; "):
                    for vv in v.split(", "):
                        vv = vv.split(" - ")[0]
                        add_linkage(kind, vv)

                # Add thesaurus links
                if kind == "synonyms":
                    for t in p.wikilinks:
                        target = t.target.strip()
                        if target.startswith("Thesaurus:"):
                            add_linkage("synonyms", target)
                return

        # Iterate over all templates
        for t in p.templates:
            name = t.name.strip()
            # Skip silently ignored tags
            if name in ignored_templates:
                continue
            # Link tags just use the default kind
            elif name in ("l", "link"):
                add_linkage(kind, t_arg(t, 2))
            # Wikipedia links also suggest a linkage of the default kind
            elif name in ("wikipedia", "Wikipedia", "w"):
                add_linkage(kind, t_arg(t, 1))
            # Japanese links seem to commonly use "ja-r" template.
            # Use the default linkage for them, and collect the
            # "hiragana" mapping for the catagana term when available
            # (actually using them would require later
            # postprocessing).
            elif name == "ja-r":
                kata = t_arg(t, 1)
                hira = t_arg(t, 2)
                add_linkage(kind, kata)
                if hira:
                    data_append(data, "hiragana", (kata, hira))
            # Handle various types of common Japanese/Chinese links.
            elif name in ("ja-l", "lang", "zh-l"):
                add_linkage(kind, t_arg(t, 1))
            # Vernacular names seem to be specified fairly often, but not
            # always intended as the actual link.  For now, we'll skip them.
            # XXX should look into these more thoroughly.
            elif name == "vern":
                pass  # Skip here
            # Taxonomical links often seem to be to superclasses of what the
            # linkage should be.  Skip them for now.
            # XXX should look into these more thoroughly.
            elif name == "taxlink":
                pass  # Skip here, these often seem to be superclasses etc
            # Qualifiers modify the next link.  We make the (questionable)
            # assumption that they only refer to the next link.
            elif name in ("q", "qual", "qualifier", "qf", "i", "topics"):
                qualifiers = clean_quals(t_vec(t)[1:])
            # Label tags are frequently used to specify qualifiers.
            elif name in ("lb", "lbl", "label", "cln", "C", "categorize",
                          "categorise",
                          "catlangname", "c", "a", "accent"):
                qualifiers = clean_quals(t_vec(t)[1:])
            # Gloss templates are sometimes used to qualify the sense
            # in which the link is intended.
            elif name in ("sense", "gloss", "s"):
                sense_text = t_arg(t, 1)
            # Synonym templates expressly indicate the link as a synonym.
            elif name in ("syn", "synonyms"):
                for x in t_vec(t)[1:]:
                    add_linkage("synonyms", x)
            elif name in ("syn2", "syn3", "syn4", "syn5", "syn1",
                          "syn2-u", "syn3-u", "syn4-u", "syn5-u"):
                qualifiers = []
                sense_text = t_arg(t, "title")
                for x in t_vec(t):
                    add_linkage("synonyms", x)
                sense_text = None
            # Antonym templates expressly indicate the link as an antonym.
            elif name in ("ant", "antonyms"):
                add_linkage("antonyms", t_arg(t, 2))
            elif name in ("ant5", "ant4", "ant3", "ant2", "ant1",
                          "ant5-u", "ant4-u", "ant3-u", "ant2-u"):
                qualifiers = []
                sense_text = t_arg(t, "title")
                for x in t_vec(t):
                    add_linkage("antonyms", x)
                sense_text = None
            # Hyponym templates expressly indicate the link as a hyponym.
            elif name in ("hyp5", "hyp4", "hyp3", "hyp2", "hyp1",
                          "hyp5-u", "hyp4-u", "hyp3-u", "hyp2-u"):
                qualifiers = []
                sense_text = t_arg(t, "title")
                for x in t_vec(t):
                    add_linkage("hyponyms", x)
                sense_text = None
            # Derived term links expressly indicate the link as a derived term.
            # XXX is this semantic meaning always clear, or are these also used
            # in other linkage subsections for just formatting purposes?
            elif name in ("der5", "der4", "der3", "der2", "der1", "zh-der",
                          "der5-u", "der4-u", "der3-u", "der2-u"):
                qualifiers = []
                sense_text = t_arg(t, "title")
                for x in t_vec(t):
                    add_linkage("derived", x)
                sense_text = None
            # Related term links expressly indicate the link is a related term.
            # XXX are these also used for other purposes?
            elif name in ("rel5", "rel4", "rel3", "rel2", "rel1",
                          "rel5-u", "rel4-u", "rel3-u", "rel2-u"):
                qualifiers = []
                sense_text = t_arg(t, "title")
                for x in t_vec(t):
                    add_linkage("related", x)
                sense_text = None
            # These templates start a range with links of the specific kind.
            elif name in ("rel-top3", "rel-top4", "rel-top5",
                          "rel-top2", "rel-top"):
                qualifiers = []
                sense_text = t_arg(t, 1)
                kind = "related"
            elif name in ("hyp-top3", "hyp-top4", "hyp-top5", "hyp-top2"):
                qualifiers = []
                sense_text = t_arg(t, 1)
                kind = "hyponym"
            elif name in ("der-top", "der-top2", "der-top3", "der-top4",
                          "der-top5"):
                qualifiers = []
                sense_text = t_arg(t, 1)
                kind = "derived"
            # These templates end a range with links of the specific kind.
            elif name in ("rel-bottom", "rel-bottom1", "rel-bottom2",
                          "rel-bottom3", "rel-bottom4", "rel-bottom5"):
                qualifiers = []
                sense_text = None
            # These templates seem to be frequently used for things that
            # aren't particularly useful for linking.
            elif name in ("t", "t+", "ux", "trans-top", "w", "pedlink",
                          "affixes", "ISBN", "specieslite", "projectlink",
                          "wikispecies", "comcatlite", "wikidata"):
                continue
            # Silently skip any templates matching these.
            elif re.search("^list:|^R:", name):
                continue
            # It is common to use special templates to indicate genus or higher
            # classes for species.  We just convert those templates to hypernym
            # links.
            elif re.match("^[A-Za-z].*? Hypernyms$", name):
                m = re.match("^([A-Za-z].*?) Hypernyms$", name)
                v = m.group(1)
                add_linkage("hypernyms", v)

            else:
                # Warn about unhandled templates.
                print(word, "LINKAGE", str(t))

        # Add thesaurus links
        for t in p.wikilinks:
            target = t.target.strip()
            if target.startswith("Thesaurus:"):
                add_linkage("synonyms", target)


    # If the linkage section does not contain a list, parse it all
    # as a single pronunciation variant.  Otherwise parse each list item
    # separately.
    spans = []
    for node in p.lists():
        spans.append(node.span)
        for item in node.items:
            parse_item(str(item), kind, True)
    for s, e in reversed(spans):
        text = text[:s] + text[e:]
    text = text.strip()
    if text:
        parse_item(text, kind, False)


def parse_any(word, base, data, text, pos, sectitle, p, capture_translations):
    """This function is called for all subsections of a word entry to parse
    information that might be in any section and that can be interpreted
    without knowing the specific section."""
    translation_sense = None
    for t in p.templates:
        name = t.name.strip()
        # Alternative forms seem to provide alternative forms with dialectal
        # descriptions.  XXX see how to handle these, and if they should be
        # merged with "alt_of" in word senses.
        if name == "alter":
            data_extend(data, "alternate", t_vec(t))
        # If a reference to a book by ISBN has been provided, save its ISBN.
        elif name == "ISBN":
            data_append(data, "isbn", t_arg(t, 1))
        # This template marks the beginning of a group of translations, and
        # may provide a word sense for the translations.
        elif name == "trans-top":
            translation_sense = t_arg(t, 1)
        elif name == "trans-bottom":
            translation_sense = None
        # These templates indicate translations for the word.  We capture
        # translations optionally, as they substantially increase the size
        # of the collected data (particularly for Engligh that typically
        # has a lot of translations to other languages).  Translations are
        # stored under "translations"; it contains a dictionary for each
        # translation, and the dictionary may include keys like:
        #   lang  - code for the language that the tranlation is for
        #   sense - word sense the translation is for (free text)
        #   markers - markers for the translation, e.g., gender
        #   roman   - romanization of the translation, if available
        elif name in ("t", "t+"):  # translations
            if capture_translations:
                vec = t_vec(t)
                if len(vec) < 2:
                    continue
                lang = vec[0]
                transl = vec[1]
                markers = vec[2:]  # gender/class markers
                alt = t_arg(t, "alt")
                roman = t_arg(t, "tr")
                script = t_arg(t, "sc")
                t = {"lang": lang, "word": transl}
                if translation_sense:
                    t["sense"] = translation_sense
                if markers:
                    t["tags"] = markers
                if alt:
                    t["alt"] = alt
                if roman:
                    t["roman"] = roman
                if script:
                    t["script"] = script
                data_append(data, "translations", t)
        # Collect any conjugation/declension information for the word.
        # These are highly language-specific, and this may require tweaking
        # as support for more languages is added.
        elif re.match("^[a-z][a-z][a-z]?-(conj|decl|infl|conjugation|declension|inflection)($|-)", name):
            args = template_args_to_dict(t)
            data_append(data, "conjugation", args)
        # The "enum" template links words that are in a sequence to the next
        # and previous words in the sequence, as well as may provide a topic
        # for the sequence.  Collect this information when available, but
        # we don't try to interpret it here (there seems to be some variation).
        elif name == "enum":
            data_append(data, "enum", t_vec(t))
        elif name == "IPA" and sectitle != "pronunciation":
            print(word, "IPA OUTSIDE PRONUNCIATION ", sectitle)

    # Parse category links.  These may provide semantic and other information
    # about the word.  Note that category links are global for the word; we
    # cannot associate them with any particular word sense or part-of-speech.
    # The links are collected under "categories".
    for t in p.wikilinks:
        target = t.target.strip()
        if target.startswith("Category:"):
            target = target[9:]
            m = re.match(r"^[a-z][a-z][a-z]?:(.*)", target)
            if m:
                target = m.group(1)
            data_append(data, "categories", target)


def parse_etymology(word, data, text, p):
    """From the etymology section we parse "compound", "affix", and
    "suffix" templates.  These may suggest that the word is a compound
    word.  They are stored under "compound"."""
    for t in p.templates:
        name = t.name.strip()
        if name in ("compound", "affix", "prefix"):
            data_append(data, "compound", template_args_to_dict(t))


def page_iter(word, text, ctx):
    """Iterates over the text of the page, returning words (parts-of-speech)
    defined on the page one at a time.  (Individual word senses for the
    same part-of-speech are typically encoded in the same entry.)"""
    assert isinstance(word, str)
    assert isinstance(text, str)
    assert isinstance(ctx, WiktionaryTarget)

    # Divide the text into subsections.  We ignore the tree structure of
    # sections because it has so many inconsistencies.
    sections = split_subsections(text)

    def iter_fn():
        language = None
        pos = None
        base = {}
        datas = []
        data = {}

        def flush():
            # Flushes information about the current part-of-speech entry.
            nonlocal data
            if language in ctx.capture_languages and pos is not None:
                data["pos"] = pos
                datas.append(data)
                data = {}

        def flush_datas():
            # Returns datas for parts-of-speech for the current language,
            # merging information from the base (for all entries) with
            # information for each specific entry.
            ret = []
            for x in datas:
                # XXX this merging needs more work
                dt = base.copy()
                for k, v in x.items():
                    if k in dt and k not in ("sounds",):
                        dt[k] = dt[k] + v
                    else:
                        dt[k] = v
                ret.append(dt)
            return ret

        # Iterate over all sections on the page, looking for sections whose
        # name matches the name of a known language.
        for sectitle, text in sections:
            if sectitle in wiktlangs.languages:
                # Found section for a langauge.  First flush any information
                # for the previous language.
                flush()
                flush_datas()
                for x in flush_datas():
                    yield x

                # Initialize for parsing words in the new language.
                language = sectitle
                ctx.language_counts[language] += 1
                pos = None
                base = {"word": clean_value(word), "lang": language}
                data = {}
                datas = []
                sectitle = ""
            else:
                # This title continues the previous language or could be
                # a new language or a misspelling or a previously unsupported
                # subtitle.
                sectitle = sectitle.lower()
                if sectitle in pos_map:
                    # New part-of-speech.  Flush the old part-of-speech.
                    flush()
                    # Initialize for parsing the new part-of-speech.
                    pos = pos_map[sectitle]
                    ctx.pos_counts[pos] += 1
                    data = {}
                    sectitle = ""
                else:
                    # We don't recognize this subtitle.  Include it in the
                    # counts; the counts should be periodically investigates
                    # to find out if new languages have been added.
                    ctx.section_counts[sectitle] += 1

            # Check if this is a language we are capturing.  If not, just
            # skip the section.
            if language not in ctx.capture_languages:
                continue

            if pos is None:
                # Have not yet seen a part-of-speech.  However, this initial
                # part frequently contains pronunciation information that
                # is shared by all parts of speech.  We don't care here
                # whether it is under a ``pronunciation`` subsection, because
                # the structure may vary.
                if ctx.capture_pronunciation:
                    p = wikitextparser.parse(text)
                    parse_pronunciation(word, base, text, p)
                continue

            # Remove any numbers at the end of the section title.
            sectitle = re.sub(r"\s+\d+(\.\d+)$", "", sectitle)

            # Apply corrections to common misspellings in sectitle
            if sectitle in sectitle_corrections:
                sectitle = sectitle_corrections[sectitle]

            # Mostly ignore etymology sections, as they often seem to contain
            # links that could be misinterpreted as something else.
            # We don't want to completely ignore Usage notes or References
            # or Anagrams, as they are often the last section of an entry
            # and thus completely ignoring them might miss classifications
            # etc.
            #
            # However, we do want to collect information about the parts of
            # compound words from the etymology sections (this is particularly
            # useful for Finnish).
            if sectitle.startswith("etymology"):
                parse_etymology(word, data, text, p)
                continue

            # Parse the section contents.
            p = wikitextparser.parse(text)

            # If the section title is empty, it is the preamble (text before
            # the first subsection for the language).
            if sectitle == "":  # Preamble
                parse_preamble(word, data, pos, text, p)
            # If the section title title indicates pronunciation, parse it here.
            elif sectitle == "pronunciation":
                if ctx.capture_pronunciation:
                    parse_pronunciation(word, data, text, p)
            # Parse various linkage sections, defaulting to the linkage type
            # indicated by the section header.
            elif sectitle == "synonyms":
                if ctx.capture_linkages:
                    parse_linkage(word, data, "synonyms", text, p)
            elif sectitle == "hypernyms":
                if ctx.capture_linkages:
                    parse_linkage(word, data, "hypernyms", text, p)
            elif sectitle == "hyponyms":
                if ctx.capture_linkages:
                    parse_linkage(word, data, "hyponyms", text, p)
            elif sectitle == "antonyms":
                if ctx.capture_linkages:
                    parse_linkage(word, data, "antonyms", text, p)
            elif sectitle == "derived terms":
                if ctx.capture_linkages:
                    parse_linkage(word, data, "derived", text, p)
            elif sectitle == "related terms":
                if ctx.capture_linkages:
                    parse_linkage(word, data, "related", text, p)
            # Parse abbreviations.
            elif sectitle == "abbreviations":
                parse_linkage(word, data, "abbreviations", text, p)
            # Parse proverbs.
            elif sectitle == "proverbs":
                parse_linkage(word, data, "abbreviations", text, p)
            # Parse compounds using the word.
            elif sectitle == "compounds":
                if ctx.capture_compounds:
                    parse_linkage(word, data, "compounds", text, p)
            # We skip declension information here, as it is parsed from all
            # sections in parse_any().
            elif sectitle in ("declension", "conjugation"):
                pass
            # XXX warn on other sections

            # Some information is parsed from any section.
            parse_any(word, base, data, text, pos, sectitle,
                      p, ctx.capture_translations)

        # Finally flush the last language.
        flush()
        for x in flush_datas():
            yield x

    return iter_fn()


def parse_text(word, text, ctx):
    """Parses the text of a Wiktionary page and returns a list of dictionaries,
    one for each word/part-of-speech defined on the page for the languages
    specified by ``capture_languages``.  ``word`` is page title, and ``text``
    is page text in Wikimedia format.  Other arguments indicate what is
    captured."""
    assert isinstance(word, str)
    assert isinstance(text, str)
    assert isinstance(ctx, WiktionaryTarget)

    # Collect all words from the page.
    datas = list(x for x in page_iter(word, text, ctx))

    # Do some post-processing on the words.  For example, we may distribute
    # conjugation information to all the words.
    for data in datas:
        # If one of the words coming from this article does not have
        # conjugation information, but another one has, use the information
        # from the other one also for the one without.
        if "conjugation" not in data:
            pos = data.get("pos")
            assert pos
            for dt in datas:
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

    # XXX some other information is global to page, e.g., the Category links.
    # such information should be distributed to all words on the page
    # (or perhaps all nouns, or perhaps only Enligh nouns?).

    # Return the resulting words
    return datas


class WiktionaryTarget(object):
    """This class is used for XML parsing the Wiktionary dump file."""

    def __init__(self, word_cb, capture_cb,
                 capture_languages, capture_translations,
                 capture_pronunciation, capture_linkages,
                 capture_compounds, capture_redirects):
        assert callable(word_cb)
        assert capture_cb is None or callable(capture_cb)
        assert isinstance(capture_languages, (list, tuple, set))
        for x in capture_languages:
            assert isinstance(x, str)
        assert capture_translations in (True, False)
        assert capture_linkages in (True, False)
        assert capture_translations in (True, False)
        self.word_cb = word_cb
        self.capture_cb = capture_cb
        self.capture_languages = capture_languages
        self.capture_translations = capture_translations
        self.capture_pronunciation = capture_pronunciation
        self.capture_linkages = capture_linkages
        self.capture_compounds = capture_compounds
        self.capture_redirects = capture_redirects
        self.tag = None
        self.namespaces = {}
        self.stack = []
        self.text = None
        self.title = None
        self.pageid = None
        self.redirect = None
        self.model = None
        self.format = None
        self.language_counts = collections.defaultdict(int)
        self.pos_counts = collections.defaultdict(int)
        self.section_counts = collections.defaultdict(int)


    def start(self, tag, attrs):
        """This is called whenever an XML start tag is encountered."""
        idx = tag.find("}")
        if idx >= 0:
            tag = tag[idx + 1:]
        attrs = {re.sub(r".*}", "", k): v for k, v in attrs.items()}
        tag = tag.lower()
        #while tag in self.stack:
        #    self.end(self.stack[-1])
        self.tag = tag
        self.stack.append(tag)
        self.attrs = attrs
        self.data = []
        if tag == "page":
            self.text = None
            self.title = None
            self.pageid = None
            self.redirect = None
            self.model = None
            self.format = None

    def end(self, tag):
        """This function is called whenever an XML end tag is encountered."""
        idx = tag.find("}")
        if idx >= 0:
            tag = tag[idx + 1:]
        tag = tag.lower()
        ptag = self.stack.pop()
        assert tag == ptag
        attrs = self.attrs
        data = "".join(self.data).strip()
        self.data = []
        if tag in ignore_tags:
            return
        for t in stack_ignore:
            if t in self.stack:
                return
        if tag == "id":
            if "revision" in self.stack:
                return
            self.pageid = data
        elif tag == "title":
            self.title = data
        elif tag == "text":
            self.text = data
        elif tag == "redirect":
            self.redirect = attrs.get("title")
        elif tag == "namespace":
            key = attrs.get("key")
            self.namespaces[key] = data
        elif tag == "model":
            self.model = data
            if data not in ("wikitext", "Scribunto", "css", "javascript",
                            "sanitized-css"):
                print("UNRECOGNIZED MODEL", data)
        elif tag == "format":
            self.format = data
            if data not in ("text/x-wiki", "text/plain",
                            "text/css", "text/javascript"):
                print("UNRECOGNIZED FORMAT", data)
        elif tag == "page":
            pageid = self.pageid
            title = self.title
            redirect = self.redirect
            if self.model in ("css", "sanitized-css", "javascript",
                              "Scribunto"):
                return
            if redirect:
                if self.capture_redirects:
                    data = {"redirect": redirect, "word": title}
                    self.word_cb(data)
            else:
                # If a capture callback has been provided, skip this page.
                if self.capture_cb and not self.capture_cb(title, self.text):
                    return
                # Parse the page, and call ``word_cb`` for each captured
                # word.
                ret = parse_text(title, self.text, self)
                for data in ret:
                    self.word_cb(data)
        else:
            print("UNSUPPORTED", tag, len(data), attrs)

    def data(self, data):
        """This function is called for data within an XML tag."""
        self.data.append(data)

    def close(self):
        """This function is called when parsing is complete."""
        return None


def parse_wiktionary(path, word_cb, capture_cb=None,
                     languages=["English", "Translingual"],
                     translations=False,
                     pronunciations=False,
                     linkages=False,
                     compounds=False,
                     redirects=False):
    """Parses Wiktionary from the dump file ``path`` (which should point
    to a "enwiktionary-<date>-pages-articles.xml.bz2" file.  This
    calls ``capture_cb(title)`` for each raw page (if provided), and
    if it returns True, and calls ``word_cb(data)`` for all words
    defined for languages in ``languages``.  The other keyword
    arguments control what data is to be extracted."""
    assert isinstance(path, str)
    assert callable(word_cb)
    assert capture_cb is None or callable(capture_cb)
    assert isinstance(languages, (list, tuple, set))
    for x in languages:
        assert isinstance(x, str)
        assert x in wiktlangs.languages
    assert translations in (True, False)
    assert pronunciations in (True, False)
    assert linkages in (True, False)
    assert compounds in (True, False)
    assert redirects in (True, False)

    # Open the input file.
    if path.endswith(".bz2"):
        wikt_f = bz2.BZ2File(path, "r", buffering=(4 * 1024 * 1024))
    else:
        wikt_f = open(path, "rb", buffering=(4 * 1024 * 1024))

    try:
        # Create parsing context.
        ctx = WiktionaryTarget(word_cb, capture_cb,
                               languages, translations,
                               pronunciations, linkages, compounds,
                               redirects)
        # Parse the XML file.
        parser = etree.XMLParser(target=ctx)
        etree.parse(wikt_f, parser)
    finally:
        wikt_f.close()

    # Return the parsing context.  At least the statistics fields are
    # accessible:
    #   ctx.language_counts
    #   ctx.pos_counts
    #   ctx.section_counts
    return ctx


# XXX pages linked under "Category:English glossaries" may be interesting
# to check out

# XXX pages linked under "Category:English appendices" may be interesting
# to check out

# XXX pages like "Appendix:Glossary of ..." seem interesting, might want to
# extract data from them?

# XXX "Appendix:Animals" seems to contain helpful information that we might
# want to extract.

# XXX Thesaurus:* pages seem potentially useful

# XXX Check out: Appendix:Roget's thesaurus classification.  Could this be
# helpful in hypernyms etc?

# Category:<langcode>:All topics and its subcategories seems very interesting.
# The English category tree looks very promising.  XXX where are the
# category relationships defined?  Wikimedia Commons?

# XXX check Unsupported titles/* and how to get their real title

# XXX test "sama" (Finnish) to check that linkages for list items are correct

# XXX test "juttu" (Finnish) to check that sense is correctly included in
# linkages

# XXX check pronunciations for "house" to see that "noun" and "verb" senses
# are correctly parsed

# XXX test "cat" (english) linkage - stuff at end in parenthesis

# XXX test "Friday" - it has embedded template in Related terms (currently
# handled wrong)

# XXX Finnish ällös seems to leave [[w:Optative mood|optative]] in gloss ???

# XXX Finnish binääri leaves binäärinen#Compounds in gloss

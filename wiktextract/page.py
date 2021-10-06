# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import copy
import html
import urllib
import hashlib
import collections
from wikitextprocessor import (Wtp, WikiNode, NodeKind, ALL_LANGUAGES,
                               MAGIC_FIRST, MAGIC_LAST)
from .parts_of_speech import part_of_speech_map, PARTS_OF_SPEECH
from .config import WiktionaryConfig
from .linkages import parse_linkage_item_text
from .translations import parse_translation_item_text
from .clean import clean_value, clean_template_args
from .places import place_prefixes  # XXX move processing to places.py
from .unsupported_titles import unsupported_title_map
from .datautils import (data_append, data_extend, split_at_comma_semi,
                        languages_by_name, languages_by_code)
from wiktextract.form_descriptions import (
    decode_tags, parse_word_head, parse_sense_qualifier,
    parse_pronunciation_tags,
    parse_alt_or_inflection_of, classify_desc)

# NodeKind values for subtitles
LEVEL_KINDS = (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
               NodeKind.LEVEL5, NodeKind.LEVEL6)


# Subsections with these titles are ignored.
ignored_section_titles = (
    "Anagrams", "Further reading", "References",
    "Quotations", "Descendants")

# Subsections with these titles contain inflection (conjugation, declension)
# information
inflection_section_titles = (
    "Declension", "Conjugation", "Inflection", "Mutation")

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
                             "infl",
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
    "alternative forms": "synonyms",
}

# Inverse linkage for those that have them
linkage_inverses = {
    # XXX this is not currently used, move to post-processing
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
    "dial syn",  # Currently ignore these, but could be useful in Chinese/Korean
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
    "multiple images",
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
    "list:Gregorian calendar months/",
    "RQ:",
]

# Templates used for wikipedia links.
wikipedia_templates = set([
    "wikipedia",
    "slim-wikipedia",
    "w",
    "W",
    "swp",
    "wiki",
    "Wikipedia",
    "wtorw",
])
for x in panel_templates & wikipedia_templates:
    print("WARNING: {!r} in both panel_templates and wikipedia_templates"
          .format(x))

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


# Prefixes, tags, and regexp for finding romanizations from the pronuncation
# section
pron_romanizations = {
    " Revised Romanization ": "romanization revised",
    " Revised Romanization (translit.) ":
    "romanization revised transliteration",
    " McCune-Reischauer ": "McCune-Reischauer romanization",
    " McCune–Reischauer ": "McCune-Reischauer romanization",
    " Yale Romanization ": "Yale romanization",
}
pron_romanization_re = re.compile(
    "(?m)^(" +
    "|".join(re.escape(x) for x in
             sorted(pron_romanizations.keys(), key=lambda x: len(x),
                    reverse=True)) +
    ")([^\n]+)")

# Templates ignored during etymology extraction, i.e., these will not be listed
# in the extracted etymology templates.
ignored_etymology_templates = [
    "...",
    "IPAchar",
    "ISBN",
    "isValidPageName",
    "redlink category",
    "deprecated code",
    "check deprecated lang param usage",
    "para",
]
# Regexp for matching ignored etymology template names.  This adds certain
# prefixes to the names listed above.
ignored_etymology_templates_re = re.compile(
    r"^((cite-|R:).*|" +
    r"|".join(re.escape(x) for x in ignored_etymology_templates) +
    r")$")


# Regexp for matching category tags that start with a language name.
# Group 2 will be the language name.  The category tag should be without
# the namespace prefix.
starts_lang_re = re.compile(
    r"^(Rhymes:)?(" +
    "|".join(re.escape(x["name"]) for x in ALL_LANGUAGES) +
    ")[ /]")


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

        # Various words have non-gloss definitions; we collect them under
        # "nonglosses".  For many purposes they might be treated similar to
        # glosses, though.
        if name in ("non-gloss definition", "n-g", "ngd", "non-gloss",
                      "non gloss definition"):
            gloss = t_arg(config, t, 1)
            data_append(config, data, "nonglosses", gloss)
        # The "sense" templates are treated as additional glosses.
        elif name in ("sense", "Sense"):
            data_append(config, data, "tags", t_arg(config, t, 1))
        # These weird templates seem to be used to indicate a literal sense.
        elif name in ("&lit", "&oth"):
            data_append(config, data, "tags", "literal")
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
    ["antonyms", "antonyms"],
    ["hyp", "hyponyms"],
    ["hyponyms", "hyponyms"],
    ["der", "derived"],
    ["derived terms", "derived"],
    ["rel", "related"],
    ["col", 2],
]

# Maps template name used in a word sense to a linkage field that it adds.
sense_linkage_templates = {
    "syn": "synonyms",
    "synonyms": "synonyms",
    "hyp": "hyponyms",
    "hyponyms": "hyponyms",
    "ant": "antonyms",
    "antonyms": "antonyms",
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
        tags = []
        topics = []
        english = None
        # Try to find qualifiers for this synonym
        q = ht.get("q{}".format(i - 1))
        if q:
            cls = classify_desc(q)
            if cls == "tags":
                tagsets1, topics1 = decode_tags(q)
                for ts in tagsets1:
                    tags.extend(ts)
                topics.extend(topics1)
            elif cls == "english":
                if english:
                    english += "; " + q
                else:
                    english = q
        # Try to find English translation for this synonym
        t = ht.get("t{}".format(i - 1))
        if t:
            if english:
                english += "; " + t
            else:
                english = t

        # See if the linkage contains a parenthesized alt
        alt = None
        m = re.search(r"\(([^)]+)\)$", w)
        if m:
            w = w[:m.start()].strip()
            alt = m.group(1)

        dt = {"word": w}
        if tags:
            data_extend(ctx, dt, "tags", tags)
        if topics:
            data_extend(ctx, dt, "topics", topics)
        if english:
            dt["english"] = english
        if alt:
            dt["alt"] = alt
        data_append(ctx, data, field, dt)


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

    base_data = {"word": word, "lang": language, "lang_code": lang_code}
    sense_data = {}
    pos_data = {}  # For a current part-of-speech
    etym_data = {}  # For one etymology
    pos_datas = []
    etym_datas = []
    page_datas = []
    have_etym = False
    stack = []

    def merge_base(data, base):
        for k, v in base.items():
            # Copy the value to ensure that we don't share lists or
            # dicts between structures (even nested ones).
            v = copy.deepcopy(v)
            if k not in data:
                # The list was copied above, so this will not create shared ref
                data[k] = v
                continue
            if data[k] == v:
                continue
            if (isinstance(data[k], (list, tuple)) or
                  isinstance(v, (list, tuple))):
                data[k] = list(data[k]) + list(v)
            elif data[k] != v:
                ctx.warning("conflicting values for {} in merge_base: "
                            "{!r} vs {!r}"
                            .format(k, data[k], v))
        # If the result has sounds, eliminate sounds that have a prefix that
        # does not match "word" or one of "forms"
        if "sounds" in data and "word" in data:
            accepted = [data["word"]]
            accepted.extend(f["form"] for f in data.get("forms", ()))
            data["sounds"] = list(s for s in data["sounds"]
                                  if "form" not in s or s["form"] in accepted)

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
        nonlocal have_etym
        have_etym = True
        push_pos()
        for data in etym_datas:
            merge_base(data, etym_data)
            page_datas.append(data)
        etym_data = {}
        etym_datas = []

    def select_data():
        """Selects where to store data (pos or etym) based on whether we
        are inside a pos (part-of-speech)."""
        if ctx.subsection is not None:
            return pos_data
        if stack[-1] == language:
            return base_data
        return etym_data

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
        for x in contents:
            if isinstance(x, WikiNode) and x.kind == NodeKind.LIST:
                break
            lst.append(x)
        sublists = list(x for x in contents
                        if isinstance(x, WikiNode) and x.kind == NodeKind.LIST)

        def sense_template_fn(name, ht):
            if name in wikipedia_templates:
                parse_wikipedia_template(config, ctx, pos_data, ht)
                return None
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
                # Usage examples are captured separately below.  We don't
                # want to expand them into glosses even when unusual coding
                # is used in the entry.
                return ""
            if name == "w":
                if ht.get(2) == "Wp":
                    return ""
            return None

        rawgloss = clean_node(config, ctx, sense_base, lst,
                              template_fn=sense_template_fn)
        # print("parse_sense rawgloss:", repr(rawgloss))

        # Extract examples that are in sublists
        examples = []
        if config.capture_examples:
            for sub in sublists:
                if not sub.args.endswith(":") and not sub.args.endswith("*"):
                    continue
                for item in sub.children:
                    if not isinstance(item, WikiNode):
                        continue
                    if item.kind != NodeKind.LIST_ITEM:
                        continue
                    subtext = clean_node(config, ctx, None, item.children)
                    ref = None
                    lines = subtext.split("\n")
                    lines = list(x for x in lines
                                 if not re.match(
                                         r"(Synonyms: |Antonyms: |Hyponyms: |"
                                         r"Synonym: |Antonym: |Hyponym: |"
                                         r"Hypernyms: |Derived terms: |"
                                         r"Related terms: |"
                                         r"Hypernym: |Derived term: |"
                                         r"Related term: |"
                                         r"For more quotations using )",
                                         x))
                    tr = None
                    if len(lines) > 1:
                        if re.search(r"[]\d:)]\s*$", lines[0]):
                            ref = lines[0]
                            lines = lines[1:]
                            if (language != "English" and len(lines) == 2 and
                                classify_desc(lines[1]) == "english"):
                                tr = lines[1]
                                lines = [lines[0]]
                        elif (language == "English" and
                              re.match(r"^[#*]*:", lines[1])):
                            ref = lines[0]
                            lines = lines[1:]
                        elif language != "English" and len(lines) == 2:
                            cls1 = classify_desc(lines[0])
                            cls2 = classify_desc(lines[1])
                            if cls2 == "english" and cls1 != "english":
                                tr = lines[1]
                                lines = [lines[0]]
                            elif cls1 == "english" and cls2 != "english":
                                tr = lines[0]
                                lines = [lines[1]]
                            elif re.match(r"^[#*]*:", lines[1]):
                                line = re.sub(r"^[#*:]+\s*", "", lines[1])
                                if classify_desc(line) == "english":
                                    tr = line
                                    lines = [lines[0]]
                    lines = list(re.sub(r"^[#*:]+\s*", "", x) for x in lines)
                    subtext = " ".join(lines)
                    subtext = re.sub(r'^[“"`]([^“"`”\']*)[”"\']$', r"\1",
                                     subtext)
                    subtext = re.sub(r"\s+", " ", subtext).strip()
                    if ref:
                        ref = re.sub(r"\s*\(→ISBN\)", "", ref)
                        if ref.endswith(":") or ref.endswith(","):
                            ref = ref[:-1].strip()
                    if ref and not subtext:
                        subtext = ref
                        ref = None
                    if subtext:
                        dt = {"text": subtext}
                        if ref:
                            dt["ref"] = ref
                        if tr:
                            dt["english"] = tr
                        examples.append(dt)

        # Generate no gloss for translation hub pages, but add the
        # "translation-hub" tag for them
        if rawgloss == "(This entry is a translation hub.)":
            data_append(ctx, sense_data, "tags", "translation-hub")
            return push_sense()

        # The gloss could contain templates that produce more list items.
        # This happens commonly with, e.g., {{inflection of|...}}.  Split
        # to parts.  However, e.g. Interlingua generates multiple glosses
        # in HTML directly without Wikitext markup, so we must also split
        # by just newlines.
        subglosses = re.split(r"(?m)^[#*]*\s*", rawgloss)

        # Some entries, e.g., "iacebam", have weird sentences in quotes
        # after the gloss, but these sentences don't seem to be intended
        # as glosses.  Skip them.
        subglosses = list(gl for gl in subglosses
                          if gl.strip() and
                          not re.match(r'\s*(\([^)]*\)\s*)?(:|"[^"]*"\s*$)',
                                       gl))

        if len(subglosses) > 1 and "form_of" not in sense_base:
            gl = subglosses[0].strip()
            if gl.endswith(":"):
                gl = gl[:-1].strip()
            parsed = parse_alt_or_inflection_of(ctx, gl)
            if parsed is not None:
                infl_tags, infl_dts = parsed
                if (infl_dts and "form-of" in infl_tags and
                    len(infl_tags) == 1):
                    # Interpret others as a particular form under
                    # "inflection of"
                    data_extend(ctx, sense_base, "tags", infl_tags)
                    data_extend(ctx, sense_base, "form_of", infl_dts)
                    subglosses = subglosses[1:]
                elif not infl_dts:
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
            if gloss_i == 0 and examples:
                data_extend(ctx, sense_data, "examples", examples)
            # If the gloss starts with †, mark as obsolete
            if gloss.startswith("^†"):
                data_append(ctx, sense_data, "tags", "obsolete")
                gloss = gloss[2:].strip()
            elif gloss.startswith("^‡"):
                data_extend(ctx, sense_data, "tags", ["obsolete", "historical"])
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
            # XXX disabled parsing parentheses from the end for now.
            # How common are these and what do they really contain?
            # gloss = re.sub(r"^\(([^()]*)\)", sense_repl, gloss)
            # gloss = re.sub(r"\s*\(([^()]*)\)$", sense_repl, gloss)

            # Remove common suffix "[from 14th c.]" and similar
            gloss = re.sub(r"\s\[[^]]*\]\s*$", "", gloss)

            # Check to make sure we don't have unhandled list items in gloss
            ofs = max(gloss.find("#"), gloss.find("*"))
            if ofs > 10 and gloss.find("(#)") < 0:
                ctx.debug("gloss may contain unhandled list items: {}"
                          .format(gloss))
            elif gloss.find("\n") >= 0:
                ctx.debug("gloss contains newline: {}".format(gloss))

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
                    infl_tags, infl_dts = parsed
                    if not infl_dts and infl_tags:
                        # Interpret as a particular form under "inflection of"
                        data_extend(ctx, sense_data, "tags", infl_tags)

            if not gloss:
                #ctx.debug("{}: empty gloss at {}"
                #             .format(pos, "/".join(stack)))
                data_append(ctx, sense_data, "tags", "empty-gloss")
            elif gloss != "-":
                # Add the gloss for the sense.
                data_append(ctx, sense_data, "glosses", gloss)

            # Kludge: there are cases (e.g., etc./Swedish) where there are
            # two abbreviations in the same sense, both generated by the
            # {{abbreviation of|...}} template.  Handle these with some magic.
            pos = 0
            split_glosses = []
            for m in re.finditer(r"Abbreviation of ", gloss):
                if m.start() != pos:
                    split_glosses.append(gloss[pos: m.start()])
                    pos = m.start()
            split_glosses.append(gloss[pos:])
            for gloss in split_glosses:
                # Check if this gloss describes an alt-of or inflection-of
                parsed = parse_alt_or_inflection_of(ctx, gloss)
                if parsed is not None:
                    tags, dts = parsed
                    if not dts and tags:
                        data_extend(ctx, sense_data, "tags", tags)
                    else:
                        for dt in dts:
                            ftags = list(tag for tag in tags
                                         if tag != "form-of")
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

    def head_post_template_fn(name, ht, expansion):
        """Handles special templates in the head section of a word.  Head
        section is the text after part-of-speech subtitle and before word
        sense list. Typically it generates the bold line for the word, but
        may also contain other useful information that often ends in
        side boxes.  We want to capture some of that additional information."""
        # print("HEAD_POST_TEMPLATE_FN", name, ht)
        if is_panel_template(name):
            # Completely ignore these templates (not even recorded in
            # head_templates)
            return ""
        if name == "head":
            # XXX are these also captured in forms?  Should this special case
            # be removed?
            t = ht.get(2, "")
            if t == "pinyin":
                data_append(ctx, pos_data, "tags", "Pinyin")
            elif t == "romanization":
                data_append(ctx, pos_data, "tags", "romanization")
        m = re.search(head_tag_re, name)
        if m:
            args_ht = clean_template_args(config, ht)
            cleaned_expansion = clean_node(config, ctx, None, expansion)
            dt = {"name": name, "args": args_ht, "expansion": cleaned_expansion}
            data_append(ctx, pos_data, "head_templates", dt)

        # The following are both captured in head_templates and parsed
        # separately

        if name in wikipedia_templates:
            # Note: various places expect to have content from wikipedia
            # templates, so cannot convert this to empty
            parse_wikipedia_template(config, ctx, pos_data, ht)
            return None

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
        # if name == "ja-kanji forms":
        #     # XXX extract?
        #     return ""
        # if name == "vi-readings":
        #     # XXX extract?
        #     return ""
        # if name == "ja-kanji":
        #     # XXX extract?
        #     return ""
        if name == "picdic" or name == "picdicimg" or name == "picdiclabel":
            # XXX extract?
            return ""

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
                          post_template_fn=head_post_template_fn)
        text = re.sub(r"\s+", " ", text)  # Any newlines etc to spaces
        parse_word_head(ctx, pos, text, pos_data)
        if "tags" in pos_data:
            common_tags = pos_data["tags"]
            del pos_data["tags"]
        else:
            common_tags = []
        for node in lists:
            for node in node.children:
                if node.kind != NodeKind.LIST_ITEM:
                    ctx.debug("{}: non-list-item inside list".format(pos))
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
                common_data = {"tags": list(common_tags)}

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
                    if outer_text in ("A person:",):
                        data_append(ctx, common_data, "tags", "g-person")

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

        # If there are no senses extracted, add a dummy sense.  We want to
        # keep tags extracted from the head for the dummy sense.
        push_sense()  # Make sure unfinished data pushed, and start clean sense
        if not pos_datas:
            data_extend(ctx, sense_data, "tags", common_tags)
            data_append(ctx, sense_data, "tags", "no-senses")
            push_sense()

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

        data = select_data()
        if have_etym and data is base_data:
            data = etym_data
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
                audio = {"audio": filename.strip()}
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
                audio = {"audio": filename.strip()}
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
                audio = {"audio": filename.strip()}
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
                # replace the expansion by something safe.  This is used
                # to filter spurious IPA-looking expansions that aren't really
                # IPAs.  We probably don't care about these templates in the
                # contexts where they expand to something containing these.
                v = re.sub(r'href="[^"]*"', "", text)  # Ignore URLs
                v = re.sub(r'src="[^"]*"', "", v)
                if re.search(r"/[^/,]+?/|\[[^]0-9,/][^],/]*?\]", v):
                    # Note: replacing by empty results in Lua errors that we
                    # would rather not have.  For example, voi/Middle Vietnamese
                    # uses {{a|{{l{{vi|...}}}}, and the {{a|...}} will fail
                    # if {{l|...}} returns empty.
                    return "stripped-by-parse_pron_post_template_fn"
            return text

        # XXX change this code to iterate over node as a LIST, warning about
        # anything else.  Don't try to split by "*".
        # XXX fix enpr tags
        text = clean_node(config, ctx, data, contents,
                          template_fn=parse_pronunciation_template_fn)
        ipa_text = clean_node(config, ctx, data, contents,
                              post_template_fn=parse_pron_post_template_fn)
        have_pronunciations = False
        text_splits = re.split(r":*[*#\n]+:*", text)
        ipa_splits = re.split(r":*[*#\n]+:*", ipa_text)
        if len(text_splits) != len(ipa_splits):
            #ctx.warning("text_splits length differs from ipa_splits: "
            #            "{!r} vs. {!r}"
            #            .format(text, ipa_text))
            ipa_splits = text_splits
        prefix = None
        for text, ipa_text in zip(text_splits, ipa_splits):
            if text.find("IPA") >= 0:
                field = "ipa"
            else:
                # This is used for Rhymes, Homophones, etc
                field = "other"

            # Check if it contains Japanese "Tokyo" pronunciation with
            # special syntax
            m = re.search(r"(?m)\(Tokyo\) +([^ ]+) +\[", text)
            if m:
                pron = {field: m.group(1)}
                data_append(ctx, data, "sounds", pron)
                have_pronunciations = True
                continue

            # Check if it contains Rhymes
            m = re.match(r"\s*Rhymes: (.*)", text)
            if m:
                for ending in split_at_comma_semi(m.group(1)):
                    ending = ending.strip()
                    if ending:
                        pron = {"rhymes": ending}
                        data_append(ctx, data, "sounds", pron)
                        have_pronunciations = True
                continue

            # Check if it contains homophones
            m = re.search(r"(?m)\bHomophones?: (.*)", text)
            if m:
                for w in split_at_comma_semi(m.group(1)):
                    w = w.strip()
                    if w:
                        pron = {"homophone": w}
                        data_append(ctx, data, "sounds", pron)
                        have_pronunciations = True
                continue

            # Check if it contains Phonetic hangeul
            m = re.search(r"(?m)\bPhonetic hangeul: \[([^]]+)\]", text)
            if m:
                seen = set()
                for w in m.group(1).split("/"):
                    w = w.strip()
                    if w and w not in seen:
                        seen.add(w)
                        pron = {"hangeul": w}
                        data_append(ctx, data, "sounds", pron)
                        have_pronunciations = True

            # See if it contains a word prefix restricting which forms the
            # pronunciation applies to (see amica/Latin) and/or parenthesized
            # tags.
            m = re.match(r"^[*#\s]*(([-\w]+):\s+)?\((([^()]|\([^()]*\))*?)\)",
                         text)
            if m:
                prefix = m.group(2) or ""
                tagstext = m.group(3)
                text = text[m.end():]
            else:
                m = re.match(r"^[*#\s]*([-\w]+):\s+", text)
                if m:
                    prefix = m.group(1)
                    tagstext = ""
                    text = text[m.end():]
                else:
                    # No prefix.  In this case, we inherit prefix from previous
                    # entry.  This particularly applies for nested Audio files.
                    tagstext = ""

            # Find romanizations from the pronunciation section (routinely
            # produced for Korean by {{ko-IPA}})
            for m in re.finditer(pron_romanization_re, text):
                prefix = m.group(1)
                w = m.group(2).strip()
                tag = pron_romanizations[prefix]
                form = {"form": w,
                        "tags": tag.split()}
                data_append(ctx, data, "forms", form)

            for m in re.finditer(r"(?m)/[^][/,]+?/|\[[^]0-9,/][^],/]*?\]",
                                 ipa_text):
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
                    if prefix:
                        audios[idx]["form"] = prefix
                else:
                    pron = {field: v}
                    if prefix:
                        pron["form"] = prefix
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
            for audio in audios:
                if "audio" in audio:
                    # Compute audio file URLs
                    fn = audio["audio"]
                    # Strip certain characters, e.g., left-to-right mark
                    fn = re.sub(r"[\u200f\u200e]", "", fn)
                    fn = fn.strip()
                    fn = urllib.parse.unquote(fn)
                    # First character is usually uppercased
                    if re.match(r"^[a-z][a-z]+", fn):
                        fn = fn[0].upper() + fn[1:]
                    # File extension is lowercased
                    # XXX some words seem to need this, some don't seem to
                    # have this??? what is the exact rule?
                    # fn = re.sub(r"\.[^.]*$", lambda m: m.group(0).lower(), fn)
                    # Spaces are converted to underscores
                    fn = re.sub(r"\s+", "_", fn)
                    # Compute hash digest part
                    h = hashlib.md5()
                    hname = fn.encode("utf-8")
                    h.update(hname)
                    digest = h.hexdigest()
                    # Quote filename for URL
                    qfn = urllib.parse.quote(fn)
                    # For safety when writing files
                    qfn = re.sub(r"/", "__slash__", qfn)
                    if re.search(r"(?i)\.(ogg|oga)$", fn):
                        ogg = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/{}/{}/{}"
                               .format(digest[:1], digest[:2], qfn))
                    else:
                        ogg = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/transcoded/"
                               "{}/{}/{}/{}.ogg"
                               .format(digest[:1], digest[:2], qfn, qfn))
                    if re.search(r"(?i)\.(mp3)$", fn):
                        mp3 = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/{}/{}/{}"
                               .format(digest[:1], digest[:2], qfn))
                    else:
                        mp3 = ("https://upload.wikimedia.org/wikipedia/"
                               "commons/transcoded/"
                               "{}/{}/{}/{}.mp3"
                               .format(digest[:1], digest[:2], qfn, qfn))
                    audio["ogg_url"] = ogg
                    audio["mp3_url"] = mp3
                if audio not in data.get("sounds", ()):
                    data_append(ctx, data, "sounds", audio)
            have_pronunciations = True
        for enpr in enprs:
            pron = {"enpr": enpr}
            # XXX need to parse enpr separately for each list item to get
            # tags correct!
            # parse_pronunciation_tags(ctx, tagstext, pron)
            if pron not in data.get("sounds", ()):
                data_append(ctx, data, "sounds", pron)
            have_pronunciations = True

        # if not have_pronunciations and not have_panel_templates:
        #     ctx.debug("no pronunciations found from pronunciation section")

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

    def get_subpage_section(title, subtitle, seq):
        """Loads a subpage of the given page, and finds the section
        for the given language, part-of-speech, and section title.  This
        is used for finding translations and other sections on subpages."""
        assert isinstance(language, str)
        assert isinstance(title, str)
        assert isinstance(subtitle, str)
        assert isinstance(seq, (list, tuple))
        for x in seq:
            assert isinstance(x, str)
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
        ret = recurse(tree, seq)
        if ret is None:
            ctx.debug("Failed to find subpage section {}/{} seq {}"
                      .format(title, subtitle, seq))
        return ret

    def parse_linkage(data, field, linkagenode):
        assert isinstance(data, dict)
        assert isinstance(field, str)
        assert isinstance(linkagenode, WikiNode)
        # print("PARSE_LINKAGE:", linkagenode)
        if not config.capture_linkages:
            return
        have_panel_template = False
        toplevel_text = []
        next_navframe_sense = None  # Used for "(sense):" before NavFrame

        def parse_linkage_item(contents, field, sense):
            assert isinstance(contents, (list, tuple))
            assert isinstance(field, str)
            assert sense is None or isinstance(sense, str)

            # print("PARSE_LINKAGE_ITEM: {} ({}): {}"
            #       .format(field, sense, contents))

            parts = []
            ruby = ""

            def item_recurse(contents, italic=False):
                assert isinstance(contents, (list, tuple))
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
                        elif node.args == "math":
                            parts.append(clean_node(config, ctx, None, node))
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
                                v = node.args[-1]
                                if (len(node.args) == 1 and
                                    len(v) > 0 and
                                    isinstance(v[0], str) and
                                    v[0][0] == ":"):
                                    v = [v[0][1:]] + list(v[1:])
                                item_recurse(v, italic=italic)
                    elif kind == NodeKind.URL:
                        print("linkage recurse URL {}".format(node))
                        item_recurse(node.args[-1], italic=italic)
                    elif kind in (NodeKind.PREFORMATTED, NodeKind.BOLD):
                        item_recurse(node.children, italic=italic)
                    else:
                        ctx.debug("linkage item_recurse unhandled {}: {}"
                                  .format(node.kind, node))

            # print("LINKAGE CONTENTS BEFORE ITEM_RECURSE: {!r}"
            #       .format(contents))
            item_recurse(contents)
            item = clean_node(config, ctx, None, parts)
            # print("LINKAGE ITEM CONTENTS:", parts)
            # print("CLEANED ITEM: {!r}".format(item))

            return parse_linkage_item_text(ctx, word, data, field, item,
                                           sense, ruby, pos_datas)

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
            nonlocal next_navframe_sense
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
                    v = parse_linkage_item(node.children, field, sense)
                    if v:
                        # parse_linkage_item() can return a value that should
                        # be used as the sense for the follow-on linkages,
                        # which are typically provided in a table (see 滿)
                        next_navframe_sense = v
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
                    elif "NavFrame" in classes:
                        # NavFrame uses previously assigned next_navframe_sense
                        # (from a "(sense):" item) and clears it afterwards
                        parse_linkage_recurse(node.children, field,
                                              sense or next_navframe_sense)
                        next_navframe_sense = None
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
                    # Apparently ":/" is used as a link to "/", so strip
                    # initial value
                    parse_linkage_recurse(node.args[-1], field, sense)
                else:
                    ctx.debug("parse_linkage_recurse unhandled {}: {}"
                              .format(kind, node))

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
        if not data.get(field) and not have_panel_template:
            text = "".join(toplevel_text).strip()
            if (text.find("\n") < 0 and text.find(",") > 0 and
                text.count(",") > 3):
                if not text.startswith("See "):
                    parse_linkage_item([text], field, None)

    def parse_translations(data, xlatnode):
        """Parses translations for a word.  This may also pull in translations
        from separate translation subpages."""
        assert isinstance(data, dict)
        assert isinstance(xlatnode, WikiNode)
        # print("===== PARSE_TRANSLATIONS {} {}".format(ctx.title, ctx.section))
        # print("parse_translations xlatnode={}".format(xlatnode))
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
                if sense.endswith("—"):
                    sense = sense[:-1].strip()
            sense_detail = None
            translations_from_template = []

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
                if name in ("t", "t+", "t-simple", "tt", "tt+"):
                    code = ht.get(1)
                    if code:
                        if langcode and code != langcode:
                            ctx.debug("inconsistent language codes {} vs "
                                      "{} in translation item: {!r} {}"
                                      .format(langcode, code, name, ht))
                        langcode = code
                    tr = ht.get(2)
                    if tr:
                        tr = clean_node(config, ctx, None, [tr])
                        translations_from_template.append(tr)
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

            # Parse the translation item.
            lang = parse_translation_item_text(ctx, word, data, item, sense,
                                               pos_datas, lang, langcode,
                                               translations_from_template)

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
                    sub = ht.get(1)
                    if not isinstance(sub, str):
                        ctx.error("no part-of-speech in "
                                  "{{see translation subpage|...}}")
                        return

                    if sub.lower() in part_of_speech_map:
                        seq = [language, sub, "Translations"]
                    else:
                        pos = ctx.subsection
                        if pos.lower() not in part_of_speech_map:
                            ctx.debug("unhandled see translation subpage: "
                                      "language={} sub={} ctx.subsection={}"
                                      .format(language, sub, ctx.subsection))
                        seq = [language, sub, pos, "Translations"]
                    subnode = get_subpage_section(ctx.title, "translations",
                                                  seq)
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
                if name in ("trans-bottom", "trans-mid",
                            "checktrans-mid", "checktrans-bottom"):
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
                ctx.error("UNIMPLEMENTED parse_translation_template: {} {}"
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
                    # Kludge: I've seen occasional normal links to translation
                    # subpages from main pages (e.g., language/English/Noun
                    # in July 2021) instead of the normal
                    # {{see translation subpage|...}} template.  This should
                    # handle them.  Note: must be careful not to read other
                    # links, particularly things like in "human being":
                    # "a human being -- see [[man/translations]]" (group title)
                    if (isinstance(arg0, (list, tuple)) and
                        arg0 and
                        isinstance(arg0[0], str) and
                        arg0[0].endswith("/translations") and
                        arg0[0][:-len("/translations")] == ctx.title):
                        ctx.debug("translations subpage link found on main "
                                  "page instead "
                                  "of normal {{see translation subpage|...}}")
                        sub = ctx.subsection
                        if sub.lower() in part_of_speech_map:
                            seq = [language, sub, "Translations"]
                            subnode = get_subpage_section(ctx.title,
                                                          "translations", seq)
                            if subnode is not None:
                                parse_translations(data, subnode)
                        else:
                            ctx.errors("/translations link outside "
                                       "part-of-speech")

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

    def parse_etymology(data, node):
        """Parses an etymology section."""
        assert isinstance(data, dict)
        assert isinstance(node, WikiNode)

        templates = []

        def etym_post_template_fn(name, ht, expansion):
            if is_panel_template(name):
                return ""
            if name in wikipedia_templates:
                parse_wikipedia_template(config, ctx, data, ht)
            if re.match(ignored_etymology_templates_re, name):
                return None
            ht = clean_template_args(config, ht)
            expansion = clean_node(config, ctx, None, expansion)
            templates.append({"name": name, "args": ht, "expansion": expansion})
            return None

        # Remove any subsections
        contents = list(x for x in node.children
                        if not isinstance(x, WikiNode) or
                        x.kind not in LEVEL_KINDS)
        # Convert to text, also capturing templates using post_template_fn
        text = clean_node(config, ctx, None, contents,
                          post_template_fn=etym_post_template_fn)
        # Save the collected information.
        data["etymology-text"] = text
        data["etymology-templates"] = templates

    def process_children(treenode):
        """This recurses into a subtree in the parse tree for a page."""
        nonlocal etym_data
        nonlocal pos_data

        def skip_template_fn(name, ht):
            """This is called for otherwise unprocessed parts of the page.
            We still expand them so that e.g. Category links get captured."""
            if name in wikipedia_templates:
                data = select_data()
                parse_wikipedia_template(config, ctx, data, ht)
                return None
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
                if config.capture_etymologies:
                    parse_etymology(etym_data, node)
            elif t == "Translations":
                data = select_data()
                parse_translations(data, node)
            elif t in ignored_section_titles:
                # XXX does the Descendants section have something we'd like
                # to capture?
                pass
            elif t in inflection_section_titles:
                parse_inflection(node)
            else:
                lst = t.split()
                while len(lst) > 1 and lst[-1].isdigit():
                    lst = lst[:-1]
                pos = " ".join(lst).lower()
                if pos in part_of_speech_map:
                    push_pos()
                    dt = part_of_speech_map[pos]
                    pos = dt["pos"]
                    ctx.start_subsection(t)
                    if "debug" in dt:
                        ctx.warning("{} in section {}"
                                    .format(dt["debug"], t))
                    if "warning" in dt:
                        ctx.warning("{} in section {}"
                                    .format(dt["warning"], t))
                    if "error" in dt:
                        ctx.error("{} in section {}"
                                  .format(dt["error"], t))
                    # Parse word senses for the part-of-speech
                    parse_part_of_speech(node, pos)
                    if "tags" in dt:
                        for pdata in pos_datas:
                            data_extend(ctx, pdata, "tags", dt["tags"])
                elif pos in linkage_map:
                    rel = linkage_map[pos]
                    data = select_data()
                    parse_linkage(data, rel, node)
                elif pos == "compounds":
                    data = select_data()
                    if config.capture_compounds:
                        parse_linkage(data, "derived", node)

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
        merge_base(data, base_data)
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
            return None
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
        ctx.debug("UNIMPLEMENTED top-level template: {} {}"
                  .format(name, ht))
        return ""

    clean_node(config, ctx, None, [node], template_fn=top_template_fn)


def fix_subtitle_hierarchy(ctx, text):
    """Fix subtitle hierarchy to be strict Language -> Etymology ->
    Part-of-Speech -> Translation/Linkage."""
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)

    # Known language names are in languages_by_name
    # Known lowercase PoS names are in part_of_speech_map
    # Known lowercase linkage section names are in linkage_map

    old = re.split(r"(?m)^(==+)[ \t]*([^= \t]([^=\n]|=[^=])*?)"
                     r"[ \t]*(==+)[ \t]*$",
                     text)

    parts = []
    npar = 4  # Number of parentheses in above expression
    parts.append(old[0])
    for i in range(1, len(old), npar + 1):
        left = old[i]
        right = old[i + npar - 1]
        title = old[i + 1]
        level = len(left)
        part = old[i + npar]
        if level != len(right):
            ctx.debug("subtitle has unbalanced levels: "
                      "{!r} has {} on the left and {} on the right"
                      .format(title, left, right))
        lc = title.lower()
        if title in languages_by_name:
            if level > 2:
                ctx.debug("subtitle has language name {} at level {}"
                          .format(title, level))
            level = 2
        elif lc.startswith("etymology"):
            if level > 3:
                ctx.debug("etymology section {} at level {}"
                          .format(title, level))
            level = 3
        elif lc.startswith("pronunciation"):
            level = 3
        elif lc in part_of_speech_map:
            level = 4
        elif lc == "translations":
            level = 5
        elif lc in linkage_map or lc == "compounds":
            level = 5
        elif title in inflection_section_titles:
            level = 5
        elif title in ignored_section_titles:
            level = 5
        else:
            level = 6
        parts.append("{}{}{}".format("=" * level, title, "=" * level))
        parts.append(part)
        # print("=" * level, title)
        # if level != len(left):
        #     print("  FIXED LEVEL OF {} {} -> {}"
        #           .format(title, len(left), level))

    text = "".join(parts)
    # print(text)
    return text


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
    ctx.start_page(word)

    # Fix up the subtitle hierarchy.  There are hundreds if not thousands of
    # pages that have, for example, Translations section under Linkage, or
    # Translations section on the same level as Noun.  Enforce a proper
    # hierarchy by manipulating the subtitle levels in certain cases.
    text = fix_subtitle_hierarchy(ctx, text)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
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
            ctx.debug("unexpected top-level node: {}".format(langnode))
            continue
        lang = clean_node(config, ctx, None, langnode.args)
        if lang not in languages_by_name:
            ctx.debug("unrecognized language name at top-level {!r}"
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
                ctx.debug("internal error -- no lang in data: {}".format(data))
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
            m = re.match(starts_lang_re, cat)
            if m:
                catlang = m.group(2)
                if (catlang != lang and
                    not (catlang == "English" and lang == "Translingual")):
                    continue  # Ignore categories for a different language
            new_cats.append(cat)
        if not new_cats:
            if "categories" in data:
                del data["categories"]
        else:
            data["categories"] = new_cats

    # Remove duplicates from tags, categories, etc.
    for data in ret:
        for field in ("categories", "topics", "tags", "wikidata", "wikipedia"):
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
            # print("clean_value recurse node_to_html value={!r} ret={!r}"
            #      .format(value, ret))
        else:
            ret = str(value)
        return ret

    # print("clean_node: value={!r}".format(value))
    v = recurse(value)
    # print("clean_node: v={!r}".format(v))

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
            cat = re.sub(r"\s+", " ", cat)
            cat = cat.strip()
            if not cat:
                continue
            if cat not in category_data.get("categories", ()):
                data_append(ctx, category_data, "categories", cat)

    v = clean_value(config, v)
    # print("After clean_value:", repr(v))

    # Strip any unhandled templates and other stuff.  This is mostly intended
    # to clean up erroneous codings in the original text.
    # v = re.sub(r"(?s)\{\{.*", "", v)
    # Some templates create <sup>(Category: ...)</sup>; remove
    v = re.sub(r"(?si)\s*(^\s*)?\(Category:[^)]*\)", "", v)
    # Some templates create question mark in <sup>, e.g., some Korean Hanja form
    v = re.sub(r"\^\?", "", v)
    return v

# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import copy
import html
import collections

from wikitextprocessor import Wtp, WikiNode, NodeKind
from .parts_of_speech import PARTS_OF_SPEECH
from .config import WiktionaryConfig
from .linkages import parse_linkage_item_text
from .translations import parse_translation_item_text
from .clean import clean_value, clean_template_args
from .unsupported_titles import unsupported_title_map
from .datautils import data_append, data_extend, ns_title_prefix_tuple
from .tags import valid_tags

from wiktextract.form_descriptions import (
    decode_tags, parse_word_head, parse_sense_qualifier,
    distw, parse_alt_or_inflection_of, classify_desc)
from wiktextract.inflection import parse_inflection_section, TableContext

# NodeKind values for subtitles
LEVEL_KINDS = (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
               NodeKind.LEVEL5, NodeKind.LEVEL6)

# Matches head tag
head_tag_re = None

# Additional templates to be expanded in the pre-expand phase
additional_expand_templates = {
    "multitrans",
    "multitrans-nowiki",
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
    "ru-verb-alt-ё",
    "ru-noun-alt-ё",
    "ru-adj-alt-ё",
    "ru-proper noun-alt-ё",
    "ru-pos-alt-ё",
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

# Templates that are used to form panels on pages and that
# should be ignored in various positions
panel_templates = {
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
    "reconstructed",
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
}

# lookup table for the tags of Chinese dialectal synonyms
zh_tag_lookup = {
    "Formal": ["formal"],
    "Written-Standard-Chinese": ["Standard-Chinese"],
    "historical or Internet slang": ["historical", "internet-slang"],
    "now usually derogatory or offensive": ["offensive", "derogatory"],
    "lofty": [],
}

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
panel_prefixes = [
    "list:compass points/",
    "list:Gregorian calendar months/",
    "RQ:",
]

# Templates used for wikipedia links.
wikipedia_templates = {
    "wikipedia",
    "slim-wikipedia",
    "w",
    "W",
    "swp",
    "wiki",
    "Wikipedia",
    "wtorw",
}
for x in panel_templates & wikipedia_templates:
    print("WARNING: {!r} in both panel_templates and wikipedia_templates"
          .format(x))

# Mapping from a template name (without language prefix) for the main word
# (e.g., fi-noun, fi-adj, en-verb) to permitted parts-of-speech in which
# it could validly occur.  This is used as just a sanity check to give
# warnings about probably incorrect coding in Wiktionary.
template_allowed_pos_map = {
    "abbr": ["abbrev"],
    "noun": ["noun", "abbrev", "pron", "name", "num", "adj_noun"],
    "plural noun": ["noun", "name"],
    "plural-noun": ["noun", "name"],
    "proper noun": ["noun", "name"],
    "proper-noun": ["name", "noun"],
    "prop": ["name", "noun"],
    "verb": ["verb", "phrase"],
    "gerund": ["verb"],
    "particle": ["adv", "particle"],
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


# Templates ignored during etymology extraction, i.e., these will not be listed
# in the extracted etymology templates.
ignored_etymology_templates = [
    "...",
    "IPAchar",
    "ipachar",
    "ISBN",
    "isValidPageName",
    "redlink category",
    "deprecated code",
    "check deprecated lang param usage",
    "para",
    "p",
    "cite",
    "Cite news",
    "Cite newsgroup",
    "cite paper",
    "cite MLLM 1976",
    "cite journal",
    "cite news/documentation",
    "cite paper/documentation",
    "cite video game",
    "cite video game/documentation",
    "cite newsgroup",
    "cite newsgroup/documentation",
    "cite web/documentation",
    "cite news",
    "Cite book",
    "Cite-book",
    "cite book",
    "cite web",
    "cite-usenet",
    "cite-video/documentation",
    "Cite-journal",
    "rfe",
]
# Regexp for matching ignored etymology template names.  This adds certain
# prefixes to the names listed above.
ignored_etymology_templates_re = re.compile(
    r"^((cite-|R:|RQ:).*|" +
    r"|".join(re.escape(x) for x in ignored_etymology_templates) +
    r")$")

# Regexp for matching ignored descendants template names. Right now we just
# copy the ignored etymology templates
ignored_descendants_templates_re = ignored_etymology_templates_re

# Regexp for matching category tags that start with a language name.
# Group 2 will be the language name.  The category tag should be without
# the namespace prefix.
starts_lang_re = None

# Set of template names that are used to define usage examples.  If the usage
# example contains one of these templates, then it its type is set to
# "example"
usex_templates = {
    "afex",
    "affixusex",
    "el-example",
    "el-x",
    "example",
    "examples",
    "he-usex",
    "he-x",
    "hi-usex",
    "hi-x",
    "ja-usex-inline",
    "ja-usex",
    "ja-x",
    "jbo-example",
    "jbo-x",
    "km-usex",
    "km-x",
    "ko-usex",
    "ko-x",
    "lo-usex",
    "lo-x",
    "ne-x",
    "ne-usex",
    "prefixusex",
    "ryu-usex",
    "ryu-x",
    "shn-usex",
    "shn-x",
    "suffixusex",
    "th-usex",
    "th-x",
    "ur-usex",
    "ur-x"
    "usex",
    "usex-suffix",
    "ux",
    "uxi",
    "zh-usex",
    "zh-x",
}

stop_head_at_these_templates = {
    "category",
    "cat",
    "topics",
    "catlangname",
    "c",
    "C",
    "top",
    "cln",
}

# Set of template names that are used to define quotation examples.  If the
# usage example contains one of these templates, then its type is set to
# "quotation".
quotation_templates = {
    "collapse-quote",
    "quote-av",
    "quote-book",
    "quote-GYLD",
    "quote-hansard",
    "quotei",
    "quote-journal",
    "quotelite",
    "quote-mailing list",
    "quote-meta",
    "quote-newsgroup",
    "quote-song",
    "quote-text",
    "quote",
    "quote-us-patent",
    "quote-video game",
    "quote-web",
    "quote-wikipedia",
    "wikiquote",
    "Wikiquote",
}

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
    ["coordinate terms", "coordinate_terms"],
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
        if w.startswith(ns_title_prefix_tuple(ctx, "Thesaurus")):
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


def init_head_tag_re(ctx):
    global head_tag_re
    if head_tag_re is None:
        head_tag_re = re.compile(
            r"^(head|Han char|arabic-noun|arabic-noun-form|"
            r"hangul-symbol|syllable-hangul)$|" +
            r"^(latin|" +
            "|".join(ctx.LANGUAGES_BY_CODE) + r")-(" +
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
            r")(-|/|\+|$)")


def parse_language(ctx, config, langnode, language, lang_code):
    """Iterates over the text of the page, returning words (parts-of-speech)
    defined on the page one at a time.  (Individual word senses for the
    same part-of-speech are typically encoded in the same entry.)"""
    # imported here to avoid circular import
    from wiktextract.pronunciations import parse_pronunciation
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(langnode, WikiNode)
    assert isinstance(language, str)
    assert isinstance(lang_code, str)
    # print("parse_language", language)

    init_head_tag_re(ctx)
    is_reconstruction = False
    word = ctx.title
    unsupported_prefix = "Unsupported titles/"
    if word.startswith(unsupported_prefix):
        w = word[len(unsupported_prefix):]
        if w in unsupported_title_map:
            word = unsupported_title_map[w]
        else:
            ctx.error("Unimplemented unsupported title: {}".format(word),
                      sortid="page/870")
            word = w
    elif word.startswith("Reconstruction:"):
        word = re.sub(r"^Reconstruction:.*/", "", word)
        is_reconstruction = True

    base_data = {"word": word, "lang": language, "lang_code": lang_code}
    if is_reconstruction:
        data_append(ctx, base_data, "tags", "reconstruction")
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
                            .format(k, data[k], v),
                            sortid="page/904")

        def complementary_pop(pron, key):
            """Remove unnecessary keys from dict values
            in a list comprehension..."""
            if key in pron:
                pron.pop(key)
            return pron
            
        # If the result has sounds, eliminate sounds that have a prefix that
        # does not match "word" or one of "forms"
        if "sounds" in data and "word" in data:
            accepted = [data["word"]]
            accepted.extend(f["form"] for f in data.get("forms", ()))
            data["sounds"] = list(complementary_pop(s, "pos")
                                  for s in data["sounds"]
                                  if "form" not in s or s["form"] in accepted)
        # If the result has sounds, eliminate sounds that have a pos that
        # does not match "pos"
        if "sounds" in data and "pos" in data:
            data["sounds"] = list(s for s in data["sounds"]
                                  if "pos" not in s or s["pos"] == data["pos"])

    def push_sense():
        """Starts collecting data for a new word sense.  This returns True
        if a sense was added."""
        nonlocal sense_data
        tags = sense_data.get("tags", ())
        if (not sense_data.get("glosses") and
            "translation-hub" not in tags and
            "no-gloss" not in tags):
            return False

        if (("participle" in sense_data.get("tags", ()) or
             "infinitive" in sense_data.get("tags", ())) and
            "alt_of" not in sense_data and
            "form_of" not in sense_data and
            "etymology_text" in etym_data):
            etym = etym_data["etymology_text"]
            etym = etym.split(". ")[0]
            ret = parse_alt_or_inflection_of(ctx, etym, set())
            if ret is not None:
                tags, lst = ret
                assert isinstance(lst, (list, tuple))
                if "form-of" in tags:
                    data_extend(ctx, sense_data, "form_of", lst)
                    data_extend(ctx, sense_data, "tags", tags)
                elif "alt-of" in tags:
                    data_extend(ctx, sense_data, "alt_of", lst)
                    data_extend(ctx, sense_data, "tags", tags)

        if (not sense_data.get("glosses") and
            "no-gloss" not in sense_data.get("tags", ())):
            data_append(ctx, sense_data, "tags", "no-gloss")

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
        pre = [[]]  # list of lists
        lists = [[]]  # list of lists
        have_subtitle = False
        first_para = True
        first_head_tmplt = True
        collecting_head = True
        start_of_paragraph = True
        for node in posnode.children:
            if isinstance(node, str):
                for m in re.finditer(r"\n+|[^\n]+", node):
                    p = m.group(0)
                    if p.startswith("\n\n") and pre:
                        first_para = False
                        start_of_paragraph = True
                        break
                    if p and collecting_head:
                        pre[-1].append(p)
                continue
            assert isinstance(node, WikiNode)
            kind = node.kind
            if kind == NodeKind.LIST:
                lists[-1].append(node)
                collecting_head = False
                start_of_paragraph = True
                continue
            elif kind in LEVEL_KINDS:
                # Stop parsing section if encountering any kind of
                # level header (like ===Noun=== or ====Further Reading====).
                # At a quick glance, this should be the default behavior,
                # but if some kinds of source articles have sub-sub-sections
                # that should be parsed XXX it should be handled by changing
                # this break.
                break
            elif collecting_head and kind == NodeKind.LINK:
                # We might collect relevant links as they are often pictures
                # relating to the word
                if (len(node.args[0]) >= 1 and
                    isinstance(node.args[0][0], str)):
                    if node.args[0][0].startswith(ns_title_prefix_tuple(
                                                        ctx, "Category")):
                        # [[Category:...]]
                        # We're at the end of the file, probably, so stop
                        # here. Otherwise the head will get garbage.
                        break
                    if node.args[0][0].startswith(ns_title_prefix_tuple(
                                                        ctx, "File")):
                        # Skips file links
                        continue
                start_of_paragraph = False
                pre[-1].extend(node.args[-1])
            elif kind == NodeKind.HTML:
                if node.args == "br":
                    if pre[-1]:
                        pre.append([])  # Switch to next head
                        lists.append([])  # Lists parallels pre
                        collecting_head = True
                        start_of_paragraph = True
                elif (collecting_head and
                      node.args not in ("gallery", "ref", "cite", "caption")):
                    start_of_paragraph = False
                    pre[-1].append(node)
                else:
                    start_of_paragraph = False
            elif kind == NodeKind.TEMPLATE:
                # XXX Insert code here that disambiguates between
                # templates that generate word heads and templates
                # that don't.

                # stop processing at {{category}}, {{cat}}... etc.
                if node.args[0][0] in stop_head_at_these_templates:
                    # we've reached a template that should be at the end,
                    # just break without special processing
                    break

                # skip these templates; panel_templates is already used
                # to skip certain templates else, but it also applies to
                # head parsing quite well.
                if node.args[0][0] in panel_templates:
                    continue
                # skip these templates
                # if node.args[0][0] in skip_these_templates_in_head:
                    # first_head_tmplt = False # no first_head_tmplt at all
                    # start_of_paragraph = False
                    # continue
                
                if first_head_tmplt and pre[-1]:
                    first_head_tmplt = False
                    start_of_paragraph = False
                    pre[-1].append(node)
                elif pre[-1] and start_of_paragraph:
                    pre.append([]) # Switch to the next head
                    lists.append([]) # lists parallel pre
                    collecting_head = True
                    start_of_paragraph = False
                    pre[-1].append(node)
                else:
                    pre[-1].append(node)
            elif first_para:
                start_of_paragraph = False
                if collecting_head:
                    pre[-1].append(node)
        # XXX use template_fn in clean_node to check that the head macro
        # is compatible with the current part-of-speech and generate warning
        # if not.  Use template_allowed_pos_map.

        there_are_many_heads = len(pre) > 1
        for i, (pre1, ls) in enumerate(zip(pre, lists)):
            if all(not sl for sl in lists[i:]):
                if i == 0:
                    if isinstance(node, str):
                        ctx.debug("first head without list of senses,"
                                  "string: '{}[...]', {}/{}".format(
                                  node[:20], word, language),
                                  sortid="page/1689/20221215")
                    if isinstance(node, WikiNode):
                        if node.args and node.args[0][0] in ["Han char",]:
                            # just ignore these templates
                            pass
                        else:
                            ctx.debug("first head without list of senses,"
                                  "template node "
                                  "{}, {}/{}".format(
                                  node.args, word, language),
                                  sortid="page/1694/20221215")
                    else:
                        ctx.debug("first head without list of senses, "
                                  "{}/{}".format(
                                  word, language),
                                  sortid="page/1700/20221215")
                    # no break here so that the first head always
                    # gets processed.
                else:
                    if isinstance(node, str):
                        ctx.debug("later head without list of senses,"
                                  "string: '{}[...]', {}/{}".format(
                                  node[:20], word, language),
                                  sortid="page/1708/20221215")
                    if isinstance(node, WikiNode):
                        ctx.debug("later head without list of senses,"
                                  "template node "
                                  "{}, {}/{}".format(
                                  node.args, word, language),
                                  sortid="page/1713/20221215")
                    else:
                        ctx.debug("later head without list of senses, "
                                  "{}/{}".format(
                                  word, language),
                                  sortid="page/1719/20221215")
                    break
            head_group = i + 1 if there_are_many_heads else None
            # print("parse_part_of_speech: {}: {}: pre={}"
                  # .format(ctx.section, ctx.subsection, pre1))
            text = clean_node(config, ctx, pos_data, pre1,
                              post_template_fn=head_post_template_fn)
            text = re.sub(r"\s+", " ", text)  # Any newlines etc to spaces
            parse_word_head(ctx, pos, text,
                            pos_data,
                            is_reconstruction,
                            head_group)
            text = None
            if "tags" in pos_data:
                common_tags = pos_data["tags"]
                del pos_data["tags"]
            else:
                common_tags = []


            for l in ls:
                # Parse each list associated with this head.
                for node in l.children:
                    # Parse nodes in l.children recursively.
                    # The recursion function uses push_sense() to
                    # add stuff into pos_data, and returns True or
                    # False if something is added, which bubbles upward.
                    # If the bubble is "True", then higher levels of
                    # the recursion will not push_sense(), because
                    # the data is already pushed into a sub-gloss
                    # downstream, unless the higher level has examples
                    # that need to be put somewhere.
                    common_data = {"tags": list(common_tags)}
                    if head_group:
                        common_data["head_nr"] = head_group
                    parse_sense_node(node, common_data, pos)


        # If there are no senses extracted, add a dummy sense.  We want to
        # keep tags extracted from the head for the dummy sense.
        push_sense()  # Make sure unfinished data pushed, and start clean sense
        if not pos_datas:
            data_extend(ctx, sense_data, "tags", common_tags)
            data_append(ctx, sense_data, "tags", "no-gloss")
            push_sense()

    def parse_sense_node(node, sense_base, pos):
        """Recursively (depth first) parse LIST_ITEM nodes for sense data.
        Uses push_sense() to attempt adding data to pos_data in the scope
        of parse_language() when it reaches deep in the recursion. push_sense()
        returns True if it succeeds, and that is bubbled up the stack; if
        a sense was added downstream, the higher levels (whose shared data
        was already added by a subsense) do not push_sense(), unless it
        has examples that need to be put somewhere.
        """
        assert isinstance(sense_base, dict)  # Added to every sense deeper in
        if not isinstance(node, WikiNode):
            ctx.debug("{}: parse_sense_node called with"
                      "something that isn't a WikiNode".format(pos),
                      sortid="page/1287/20230119")
            return False
            
        if node.kind != NodeKind.LIST_ITEM:
            ctx.debug("{}: non-list-item inside list".format(pos),
                      sortid="page/1678")
            return False
            
        if node.args == ":":
        # Skip example entries at the highest level, ones without
        # a sense ("...#") above them.
        # If node.args is exactly and only ":", then it's at
        # the highest level; lower levels would have more
        # "indentation", like "#:" or "##:"
            return False

        # If a recursion call succeeds in push_sense(), bubble it up with added.
        # added |= push_sense() or added |= parse_sense_node(...) to OR.
        added = False

        gloss_template_args = set()

        # For LISTs and LIST_ITEMS, their argument is something like
        # "##" or "##:", and using that we can rudimentally determine
        # list 'depth' if need be, and also what kind of list or
        # entry it is; # is for normal glosses, : for examples (indent)
        # and * is used for quotations on wiktionary.
        current_depth = node.args
    
        children = node.children

        # subentries, (presumably) a list
        # of subglosses below this. The list's
        # argument ends with #, and its depth should
        # be bigger than parent node.
        subentries = [x for x in children
                    if isinstance(x, WikiNode) and
                    x.kind == NodeKind.LIST and
                    x.args == current_depth + "#"]

        # sublists of examples and quotations. .args
        # does not end with "#".
        others = [x for x in children
                  if isinstance(x, WikiNode) and
                  x.kind == NodeKind.LIST and
                  x.args != current_depth + "#"]

        # the actual contents of this particular node.
        # can be a gloss (or a template that expands into
        # many glosses which we can't easily pre-expand)
        # or could be an "outer gloss" with more specific
        # subglosses, or could be a qualfier for the subglosses.
        contents = [x for x in children
                 if not isinstance(x, WikiNode) or
                 x.kind != NodeKind.LIST]
        # If this entry has sublists of entries, we should combine
        # gloss information from both the "outer" and sublist content.
        # Sometimes the outer gloss 
        # is more non-gloss or tags, sometimes it is a coarse sense
        # and the inner glosses are more specific.  The outer one
        # does not seem to have qualifiers.

        # If we have one sublist with one element, treat it
        # specially as it may be a Wiktionary error; raise
        # that nested element to the same level.
        # XXX If need be, this block can be easily removed in
        # the current recursive logicand the result is one sense entry
        # with both glosses in the glosses list, as you would
        # expect. If the higher entry has examples, there will
        # be a higher entry with some duplicated data.
        if len(subentries) == 1:
            slc = subentries[0].children
            if len(slc) == 1:
                # copy current node and modify it so it doesn't
                # loop infinitely.
                cropped_node = copy.copy(node)
                cropped_node.children = [x for x in children
                                        if not (isinstance(x, WikiNode) and
                                                x.kind == NodeKind.LIST and
                                                x.args == current_depth + "#")]
                added |= parse_sense_node(cropped_node, sense_base, pos)
                added |= parse_sense_node(slc[0], sense_base, pos)
                return added

        def sense_template_fn(name, ht):
            if name in wikipedia_templates:
                # parse_wikipedia_template(config, ctx, pos_data, ht)
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
                # print(f"SENSE_TEMPLATE_FN: {name}")
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
                # These templates may slip through inside another item, but
                # currently we're separating out example entries (..#:)
                # well enough that there seems to very little contamination.
                return ""
            if name == "w":
                if ht.get(2) == "Wp":
                    return ""
            for k, v in ht.items():
                v = v.strip()
                if v and v.find("<") < 0:
                    gloss_template_args.add(v)
            if config.dump_file_lang_code == "zh":
                add_form_of_tags(ctx, name, config.FORM_OF_TEMPLATES, sense_base)
            return None

        def extract_link_texts(item):
            """Recursively extracts link texts from the gloss source.  This
            information is used to select whether to remove final "." from
            form_of/alt_of (e.g., ihm/Hunsrik)."""
            if isinstance(item, (list, tuple)):
                for x in item:
                    extract_link_texts(x)
                return
            if isinstance(item, str):
                # There seem to be HTML sections that may futher contain
                # unparsed links.
                for m in re.finditer(r"\[\[([^]]*)\]\]", item):
                    print("ITER:", m.group(0))
                    v = m.group(1).split("|")[-1].strip()
                    if v:
                        gloss_template_args.add(v)
                return
            if not isinstance(item, WikiNode):
                return
            if item.kind == NodeKind.LINK:
                v = item.args[-1]
                if (isinstance(v, list) and len(v) == 1 and
                    isinstance(v[0], str)):
                    gloss_template_args.add(v[0].strip())
            for x in item.children:
                extract_link_texts(x)

        extract_link_texts(contents)

        # get the raw text of non-list contents of this node, and other stuff
        # like tag and category data added to sense_base
        rawgloss = clean_node(config, ctx, sense_base, contents,
                              template_fn=sense_template_fn)

        if not rawgloss:
            return False
            
        # get stuff like synonyms and categories from "others",
        # maybe examples and quotations
        clean_node(config, ctx, sense_base, others,
                              template_fn=sense_template_fn)


        # Generate no gloss for translation hub pages, but add the
        # "translation-hub" tag for them
        if rawgloss == "(This entry is a translation hub.)":
            data_append(ctx, sense_data, "tags", "translation-hub")
            return push_sense()

        # Remove certain substrings specific to outer glosses
        strip_ends = [", particularly:"]
        for x in strip_ends:
            if rawgloss.endswith(x):
                rawgloss = rawgloss[:-len(x)]
                break

        # The gloss could contain templates that produce more list items.
        # This happens commonly with, e.g., {{inflection of|...}}.  Split
        # to parts.  However, e.g. Interlingua generates multiple glosses
        # in HTML directly without Wikitext markup, so we must also split
        # by just newlines.
        subglosses = re.split(r"(?m)^[#*]*\s*", rawgloss)
                                       
        if len(subglosses) == 0:
            return False

        # A single gloss, or possibly an outer gloss.
        # Check if the possible outer gloss starts with
        # parenthesized tags/topics

        m = re.match(r"\(([^()]+)\):?\s*", rawgloss)
                    # ( ..\1.. ): ... or ( ..\1.. ) ...
        if m:
            q = m.group(1)
            rawgloss = rawgloss[m.end():].strip()
            parse_sense_qualifier(ctx, q, sense_base)
        if rawgloss == "A pejorative:":
            data_append(ctx, sense_base, "tags", "pejorative")
            rawgloss = None
        elif rawgloss == "Short forms.":
            data_append(ctx, sense_base, "tags", "abbreviation")
            rawgloss = None
        elif rawgloss == "Technical or specialized senses.":
            rawgloss = None
        if rawgloss:
            data_append(ctx, sense_base, "glosses", rawgloss)
            if rawgloss in ("A person:",):
                data_append(ctx, sense_base, "tags", "g-person")

        # The main recursive call (except for the exceptions at the
        # start of this function).
        for sublist in subentries:
            if not (isinstance(sublist, WikiNode) and
                    sublist.kind == NodeKind.LIST):
                ctx.debug(f"'{repr(rawgloss[:20])}.' gloss has `subentries`"
                          f"with items that are not LISTs",
                          sortid="page/1511/20230119")
                continue
            for item in sublist.children:
                if not (isinstance(item, WikiNode) and
                        item.kind == NodeKind.LIST_ITEM):
                    continue
                # copy sense_base to prevent cross-contamination between
                # subglosses and other subglosses and superglosses
                sense_base2 = copy.deepcopy(sense_base)
                if parse_sense_node(item, sense_base2, pos):
                    added = True

        # Capture examples.
        # This is called after the recursive calls above so that
        # sense_base is not contaminated with meta-data from
        # example entries for *this* gloss.
        examples = []
        if config.capture_examples:
            examples = extract_examples(others, sense_base)

        # push_sense() succeeded somewhere down-river, so skip this level
        if added:
            if examples:
            # this higher-up gloss has examples that we do not want to skip
                ctx.debug("'{}[...]' gloss has examples we want to keep, "
                          "but there are subglosses."
                          .format(repr(rawgloss[:30])),
                      sortid="page/1498/20230118")
            else:
                return True

        # Some entries, e.g., "iacebam", have weird sentences in quotes
        # after the gloss, but these sentences don't seem to be intended
        # as glosses.  Skip them.
        subglosses = list(gl for gl in subglosses
                          if gl.strip() and
                          not re.match(r'\s*(\([^)]*\)\s*)?"[^"]*"\s*$',
                                       gl))

        if len(subglosses) > 1 and "form_of" not in sense_base:
            gl = subglosses[0].strip()
            if gl.endswith(":"):
                gl = gl[:-1].strip()
            parsed = parse_alt_or_inflection_of(ctx, gl, gloss_template_args)
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
        for gloss_i, gloss in enumerate(subglosses):
            gloss = gloss.strip()
            if not gloss and len(subglosses) > 1:
                continue
            if gloss.startswith("; ") and gloss_i > 0:
                gloss = gloss[1:].strip()
            # Push a new sense (if the last one is not empty)
            if push_sense():
                added = True
            data_append(ctx, sense_data, "raw_glosses", gloss)
            if gloss_i == 0 and examples:
                # In a multi-line gloss, associate examples
                # with only one of them.
                # XXX or you could use gloss_i == len(subglosses)
                # to associate examples with the *last* one.
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
                        # (...): ... or (...(...)...): ... 
            if m:
                parse_sense_qualifier(ctx, m.group(1), sense_data)
                gloss = gloss[m.end():].strip()

            # Remove common suffix "[from 14th c.]" and similar
            gloss = re.sub(r"\s\[[^]]*\]\s*$", "", gloss)

            # Check to make sure we don't have unhandled list items in gloss
            ofs = max(gloss.find("#"), gloss.find("* "))
            if ofs > 10 and gloss.find("(#)") < 0:
                ctx.debug("gloss may contain unhandled list items: {}"
                          .format(gloss),
                          sortid="page/1412")
            elif gloss.find("\n") >= 0:
                ctx.debug("gloss contains newline: {}".format(gloss),
                          sortid="page/1416")

            # Kludge, some glosses have a comma after initial qualifiers in
            # parentheses
            if gloss.startswith((",", ":")):
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
                parsed = parse_alt_or_inflection_of(ctx, gloss,
                                                    gloss_template_args)
                if parsed is not None:
                    infl_tags, infl_dts = parsed
                    if not infl_dts and infl_tags:
                        # Interpret as a particular form under "inflection of"
                        data_extend(ctx, sense_data, "tags", infl_tags)

            if not gloss:
                data_append(ctx, sense_data, "tags", "empty-gloss")
            elif gloss != "-" and gloss not in sense_data.get("glosses", []):
                # Add the gloss for the sense.
                data_append(ctx, sense_data, "glosses", gloss)

            # Kludge: there are cases (e.g., etc./Swedish) where there are
            # two abbreviations in the same sense, both generated by the
            # {{abbreviation of|...}} template.  Handle these with some magic.
            position = 0
            split_glosses = []
            for m in re.finditer(r"Abbreviation of ", gloss):
                if m.start() != position:
                    split_glosses.append(gloss[position: m.start()])
                    position = m.start()
            split_glosses.append(gloss[position:])
            for gloss in split_glosses:
                # Check if this gloss describes an alt-of or inflection-of
                if (lang_code != "en" and " " not in gloss and distw([word], gloss) < 0.3):
                    # Don't try to parse gloss if it is one word
                    # that is close to the word itself for non-English words
                    # (probable translations of a tag/form name)
                    continue
                parsed = parse_alt_or_inflection_of(ctx, gloss,
                                                    gloss_template_args)
                if parsed is None:
                    continue
                tags, dts = parsed
                if not dts and tags:
                    data_extend(ctx, sense_data, "tags", tags)
                    continue
                for dt in dts:
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
            # push_sense succeded in adding a sense to pos_data
            added = True
            # print("PARSE_SENSE DONE:", pos_datas[-1])
        return added

    def parse_inflection(node, section, pos):
        """Parses inflection data (declension, conjugation) from the given
        page.  This retrieves the actual inflection template
        parameters, which are very useful for applications that need
        to learn the inflection classes and generate inflected
        forms."""
        assert isinstance(node, WikiNode)
        assert isinstance(section, str)
        assert pos is None or isinstance(pos, str)
        # print("parse_inflection:", node)

        if pos is None:
            ctx.debug("inflection table outside part-of-speech",
                      sortid="page/1812")
            return

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
                args_ht = clean_template_args(config, ht)
                dt = {"name": name, "args": args_ht}
                data_append(ctx, pos_data, "inflection_templates", dt)

            return None

        # Convert the subtree back to Wikitext, then expand all and parse,
        # capturing templates in the process
        text = ctx.node_to_wikitext(node.children)

        # Split text into separate sections for each to-level template
        brace_matches = re.split("({{+|}}+)", text) # ["{{", "template", "}}"]
        template_sections = []
        template_nesting = 0  # depth of SINGLE BRACES { { nesting } }
        # Because there is the possibility of triple curly braces
        # ("{{{", "}}}") in addition to normal ("{{ }}"), we do not
        # count nesting depth using pairs of two brackets, but
        # instead use singular braces ("{ }").
        # Because template delimiters should be balanced, regardless
        # of whether {{ or {{{ is used, and because we only care
        # about the outer-most delimiters (the highest level template)
        # we can just count the single braces when those single
        # braces are part of a group.
        
        # print(text)
        # print(repr(brace_matches))
        if len(brace_matches) > 1:
            tsection = []
            after_templates = False  # kludge to keep any text
                                     # before first template
                                     # with the first template;
                                     # otherwise, text
                                     # goes with preceding template
            for m in brace_matches:
                if m.startswith("{{"):
                    if (template_nesting == 0 and
                        after_templates):
                        template_sections.append(tsection)
                        tsection = []
                        # start new section
                    after_templates = True
                    template_nesting += len(m)
                    tsection.append(m)
                elif m.startswith("}}"):
                    template_nesting -= len(m)
                    if template_nesting < 0:
                        ctx.error("Negatively nested braces, "
                                  "couldn't split inflection templates, "
                                  "{}/{} section {}"
                                  .format(word, language, section),
                                  sortid="page/1871")
                        template_sections = [] # use whole text
                        break
                    tsection.append(m)
                else:
                    tsection.append(m)
            if tsection:  # dangling tsection
                template_sections.append(tsection)
                # Why do it this way around? The parser has a preference
                # to associate bits outside of tables with the preceding
                # table (`after`-variable), so a new tsection begins
                # at {{ and everything before it belongs to the previous
                # template.
        
        texts = []
        if not template_sections:
            texts = [text]
        else:
            for tsection in template_sections:
                texts.append("".join(tsection))
        if template_nesting != 0:
            ctx.error("Template nesting error: "
                      "template_nesting = {} "
                      "couldn't split inflection templates, "
                      "{}/{} section {}"
                      .format(template_nesting, word, language, section),
                      sortid="page/1896")
            texts = [text]
        for text in texts:
            tree = ctx.parse(text, expand_all=True,
                             template_fn=inflection_template_fn)
    
            # Parse inflection tables from the section.  The data is stored
            # under "forms".
            if config.capture_inflections:
                tblctx = None
                m = re.search("{{([^}{|]+)\|?", text)
                if m:
                    template_name = m.group(1)
                    tblctx = TableContext(template_name)

                parse_inflection_section(config, ctx, pos_data,
                                         word, language,
                                         pos, section, tree,
                                         tblctx=tblctx)

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
                      "{{see translation subpage|...}}",
                      sortid="page/1934")

        def recurse(node, seq):
            # print(f"seq: {seq}")
            if not seq:
                return node
            if not isinstance(node, WikiNode):
                return None
            # print(f"node.kind: {node.kind}")
            if node.kind in LEVEL_KINDS:
                t = clean_node(config, ctx, None, node.args[0])
                # print(f"t: {t} == seq[0]: {seq[0]}?")
                if t.lower() == seq[0].lower():
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
                      .format(title, subtitle, seq),
                      sortid="page/1963")
        return ret

    def parse_linkage(data, field, linkagenode):
        assert isinstance(data, dict)
        assert isinstance(field, str)
        assert isinstance(linkagenode, WikiNode)
        # if field == "synonyms" and True == False:
        #     print("field", field)
        #     print("data", data)
        #     print("children:")
        #     print(linkagenode.children)
        if not config.capture_linkages:
            return
        have_panel_template = False
        toplevel_text = []
        next_navframe_sense = None  # Used for "(sense):" before NavFrame

        def parse_linkage_item(contents, field, sense):
            assert isinstance(contents, (list, tuple))
            assert isinstance(field, str)
            assert sense is None or isinstance(sense, str)

            #print("PARSE_LINKAGE_ITEM: {} ({}): {}"
            #      .format(field, sense, contents))

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
                                sense1 = sense1[1:-1].strip()
                            if sense1.lower() == config.OTHER_SUBTITLES["translations"]:
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
                            if v.startswith(ns_title_prefix_tuple(ctx,
                                                            "Category", True) \
                                            + ns_title_prefix_tuple(ctx,
                                                            "File", True)):
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
                        # print("linkage recurse URL {}".format(node))
                        item_recurse(node.args[-1], italic=italic)
                    elif kind in (NodeKind.PREFORMATTED, NodeKind.BOLD):
                        item_recurse(node.children, italic=italic)
                    else:
                        ctx.debug("linkage item_recurse unhandled {}: {}"
                                  .format(node.kind, node),
                                  sortid="page/2073")

            # print("LINKAGE CONTENTS BEFORE ITEM_RECURSE: {!r}"
            #       .format(contents))
            item_recurse(contents)
            item = clean_node(config, ctx, None, parts)
            # print("LINKAGE ITEM CONTENTS:", parts)
            # print("CLEANED ITEM: {!r}".format(item))

            return parse_linkage_item_text(ctx, word, data, field, item,
                                           sense, ruby, pos_datas,
                                           is_reconstruction)

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
            parse_linkage_recurse(parsed.children, field, None)

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
                                      .format(sense, sense1),
                                      sortid="page/2170")
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
                              .format(kind, node),
                              sortid="page/2196")

        def linkage_template_fn1(name, ht):
            nonlocal have_panel_template
            if is_panel_template(name):
                have_panel_template = True
                return ""
            return None

        def parse_zh_synonyms(parsed, data, hdrs, root_word):
            """Parses Chinese dialectal synonyms tables"""
            for item in parsed:
                if isinstance(item, WikiNode):
                    if item.kind == NodeKind.TABLE_ROW:
                        cleaned = clean_node(config, ctx, None, item.children)
                        #print("cleaned:", repr(cleaned))
                        if any(["Variety" in cleaned,
                               "Location" in cleaned,
                               "Words" in cleaned]):
                            pass
                        else:
                            split = cleaned.split("\n")
                            new_hdrs = split[:-1]
                            if len(new_hdrs) == 2:
                                hdrs = [new_hdrs[0]]
                                new_hdrs.pop(0)
                            combined_hdrs = [x.strip() for x in hdrs + new_hdrs]
                            tags = []
                            words = split[-1].split(",")
                            for hdr in combined_hdrs:
                                hdr = hdr.replace("(", ",")
                                hdr = hdr.replace(")", "")
                                hdr = hdr.replace("N.", "Northern,")
                                hdr = hdr.replace("S.", "Southern,")
                                new = hdr.split(",")
                                for tag in sorted(new):
                                    tag = tag.strip()
                                    tag = tag.replace(" ", "-")
                                    if tag in valid_tags:
                                        tags.append(tag)
                                    else:
                                        if tag in zh_tag_lookup:
                                            tags.extend(zh_tag_lookup[tag])
                                        else:
                                            print(f"MISSING ZH SYNONYM TAG for root {root_word}, word {words}: {tag}")
                                            sys.stdout.flush()

                            for word in words:
                                data.append({"word": word.strip(), "tags": tags})
                    elif item.kind == NodeKind.HTML:
                        cleaned = clean_node(config, ctx, None, item.children)
                        if cleaned.find("Synonyms of") >= 0:
                            cleaned = cleaned.replace("Synonyms of ", "")
                            root_word = cleaned
                        parse_zh_synonyms(item.children, data, hdrs, root_word)
                    else:
                        parse_zh_synonyms(item.children, data, hdrs, root_word)

        def parse_zh_synonyms_list(parsed, data, hdrs, root_word):
            """Parses Chinese dialectal synonyms tables (list format)"""
            for item in parsed:
                if isinstance(item, WikiNode):
                    if item.kind == NodeKind.LIST_ITEM:
                        cleaned = clean_node(config, ctx, None, item.children)
                        #print("cleaned:", repr(cleaned))
                        if any(["Variety" in cleaned,
                               "Location" in cleaned,
                               "Words" in cleaned]):
                            pass
                        else:
                            cleaned = cleaned.replace("(", ",")
                            cleaned = cleaned.replace(")", "")
                            split = cleaned.split(",")
                            # skip empty words / titles
                            if split[0] == "":
                                continue
                            words = split[0].split("/")
                            new_hdrs = [x.strip() for x in split[1:]]
                            tags = []
                            roman = None
                            for tag in sorted(new_hdrs):
                                if tag in valid_tags:
                                    tags.append(tag)
                                elif tag in zh_tag_lookup:
                                    tags.extend(zh_tag_lookup[tag])
                                elif classify_desc(tag) == "romanization" \
                                        and roman is None:
                                    roman = tag
                                else:
                                    print(f"MISSING ZH SYNONYM TAG (possibly pinyin) - root {root_word}, word {words}: {tag}")
                                    sys.stdout.flush()

                            for word in words:
                                dt = {"word": word.strip()}
                                if tags:
                                    dt["tags"] = tags
                                if roman is not None:
                                    dt["roman"] = roman
                                data.append(dt)
                    elif item.kind == NodeKind.HTML:
                        cleaned = clean_node(config, ctx, None, item.children)
                        if cleaned.find("Synonyms of") >= 0:
                            cleaned = cleaned.replace("Synonyms of ", "")
                            root_word = cleaned
                        parse_zh_synonyms_list(item.children, data, hdrs, root_word)
                    else:
                        parse_zh_synonyms_list(item.children, data, hdrs, root_word)

        def contains_kind(children, nodekind):
            assert isinstance(children, list)
            for item in children:
                if not isinstance(item, WikiNode):
                    continue
                if item.kind == nodekind:
                    return True
                elif contains_kind(item.children, nodekind):
                    return True
            return False

        # Main body of parse_linkage()
        text = ctx.node_to_wikitext(linkagenode.children)
        parsed = ctx.parse(text, expand_all=True,
                           template_fn=linkage_template_fn1)
        if field == "synonyms" and lang_code == "zh":
            synonyms = []
            if contains_kind(parsed.children, NodeKind.LIST):
                parse_zh_synonyms_list(parsed.children, synonyms, [], "")
            else:
                parse_zh_synonyms(parsed.children, synonyms, [], "")
            #print(json.dumps(synonyms, indent=4, ensure_ascii=False))
            data_extend(ctx, data, "synonyms", synonyms)
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
        # print("===== PARSE_TRANSLATIONS {} {} {}"
            # .format(ctx.title, ctx.section, ctx.subsection))
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
                    ctx.debug("Skipping translation see also: {}".format(sense),
                              sortid="page/2361")
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
                                      .format(langcode, code, name, ht),
                                      sortid="page/2386")
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
                    ctx.error("UNIMPLEMENTED trans-see template",
                              sortid="page/2405")
                    return ""
                if name.endswith("-top"):
                    return ""
                if name.endswith("-bottom"):
                    return ""
                if name.endswith("-mid"):
                    return ""
                #ctx.debug("UNHANDLED TRANSLATION ITEM TEMPLATE: {!r}"
                #             .format(name),
                #          sortid="page/2414")
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
            if item:
                lang = parse_translation_item_text(ctx, word, data, item, sense,
                                                   pos_datas, lang, langcode,
                                                   translations_from_template,
                                                   is_reconstruction, config)

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
                    sub = ht.get(1, None)
                    m = re.match(r"\s*(([^:\d]*)\s*\d*)\s*:\s*([^:]*)\s*", sub)
                    etym = ""
                    etym_numbered = ""
                    pos = ""
                    if m:
                        etym_numbered = m.group(1)
                        etym = m.group(2)
                        pos = m.group(3)
                    if not isinstance(sub, str):
                        ctx.debug("no part-of-speech in "
                                  "{{see translation subpage|...}}, "
                                  "defaulting to just ctx.section "
                                  "(= language)",
                                  sortid="page/2468")
                        # seq sent to get_subpage_section without sub and pos
                        seq = [language, config.OTHER_SUBTITLES["translations"]]
                    elif (m and etym.lower().strip()
                                in config.OTHER_SUBTITLES["etymology"]
                            and pos.lower() in config.POS_SUBTITLES):
                            print("REACHED")
                            seq = [language,
                                   etym_numbered,
                                   pos,
                                   config.OTHER_SUBTITLES["translations"]]
                    elif sub.lower() in config.POS_SUBTITLES:
                        # seq with sub but not pos
                        seq = [language,
                               sub,
                               config.OTHER_SUBTITLES["translations"]]
                    else:
                        # seq with sub and pos
                        pos = ctx.subsection
                        if pos.lower() not in config.POS_SUBTITLES:
                            ctx.debug("unhandled see translation subpage: "
                                      "language={} sub={} ctx.subsection={}"
                                      .format(language, sub, ctx.subsection),
                                      sortid="page/2478")
                        seq = [language,
                               sub,
                               pos,
                               config.OTHER_SUBTITLES["translations"]]
                    subnode = get_subpage_section(
                        ctx.title, config.OTHER_SUBTITLES["translations"], seq)
                    if subnode is not None:
                        parse_translations(data, subnode)
                    else:
                        # Failed to find the normal subpage section
                        seq = [config.OTHER_SUBTITLES["translations"]]
                        subnode = get_subpage_section(
                            ctx.title, config.OTHER_SUBTITLES["translations"], seq)
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
                          .format(name, ht),
                          sortid="page/2517")
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
                                      "translations: {}".format(node),
                                      sortid="page/2530")
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
                elif kind in (NodeKind.ITALIC,
                              NodeKind.BOLD):
                    parse_translation_recurse(node)
                elif kind == NodeKind.PREFORMATTED:
                    print("parse_translation_recurse: PREFORMATTED:", node)
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
                        arg0[0].endswith("/" + config.OTHER_SUBTITLES["translations"]) and
                        arg0[0][:-(1 + len(config.OTHER_SUBTITLES["translations"]))] == ctx.title):
                        ctx.debug("translations subpage link found on main "
                                  "page instead "
                                  "of normal {{see translation subpage|...}}",
                                  sortid="page/2595")
                        sub = ctx.subsection
                        if sub.lower() in config.POS_SUBTITLES:
                            seq = [language, sub, config.OTHER_SUBTITLES["translations"]]
                            subnode = get_subpage_section(
                                ctx.title, config.OTHER_SUBTITLES["translations"], seq)
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
                              "{}".format(node),
                              sortid="page/2621")

        # Main code of parse_translation().  We want ``sense`` to be assigned
        # regardless of recursion levels, and thus the code is structured
        # to define at this level and recurse in parse_translation_recurse().
        parse_translation_recurse(xlatnode)

    def parse_etymology(data, node):
        """Parses an etymology section."""
        assert isinstance(data, dict)
        assert isinstance(node, WikiNode)

        templates = []

        # Counter for preventing the capture of etymology templates
        # when we are inside templates that we want to ignore (i.e.,
        # not capture).
        ignore_count = 0

        def etym_template_fn(name, ht):
            nonlocal ignore_count
            if is_panel_template(name):
                return ""
            if re.match(ignored_etymology_templates_re, name):
                ignore_count += 1

        def etym_post_template_fn(name, ht, expansion):
            nonlocal ignore_count
            if name in wikipedia_templates:
                parse_wikipedia_template(config, ctx, data, ht)
                return None
            if re.match(ignored_etymology_templates_re, name):
                ignore_count -= 1
                return None
            if ignore_count == 0:
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
                          template_fn=etym_template_fn,
                          post_template_fn=etym_post_template_fn)
        # Save the collected information.
        data["etymology_text"] = text
        data["etymology_templates"] = templates

    def parse_descendants(data, node, is_proto_root_derived_section=False):
        """Parses a Descendants section. Also used on Derived terms and
        Extensions sections when we are dealing with a root of a reconstructed
        language (i.e. is_proto_root_derived_section == True), as they use the
        same structure. In the latter case, The wiktionary convention is not to
        title the section as descendants since the immediate offspring of the
        roots are morphologically derived terms within the same proto-language.
        Still, since the rest of the section lists true descendants, we use the
        same function. Entries in the descendants list that are technically
        derived terms will have a field "tags": ["derived"]."""
        assert isinstance(data, dict)
        assert isinstance(node, WikiNode)
        assert isinstance(is_proto_root_derived_section, bool)

        descendants = []

        def process_list_item_children(args, children):
            item_data = {"depth": 0 if args == ";" else len(args)}
            templates = []
            is_derived = False

            # Counter for preventing the capture of templates when we are inside
            # templates that we want to ignore (i.e., not capture).
            ignore_count = 0

            def desc_template_fn(name, ht):
                nonlocal ignore_count
                if is_panel_template(name):
                    return ""
                if re.match(ignored_descendants_templates_re, name):
                    ignore_count += 1                

            def desc_post_template_fn(name, ht, expansion):
                nonlocal ignore_count
                if name in wikipedia_templates:
                    parse_wikipedia_template(config, ctx, data, ht)
                    return None
                if re.match(ignored_descendants_templates_re, name):
                    ignore_count -= 1
                    return None
                if ignore_count == 0:
                    ht = clean_template_args(config, ht)
                    nonlocal is_derived
                    # If we're in a proto-root Derived terms or Extensions section,
                    # and the current list item has a link template to a term in the
                    # same proto-language, then we tag this descendant entry with
                    # "derived"
                    is_derived = (
                        is_proto_root_derived_section and
                        (name == "l" or name == "link") and
                        ("1" in ht and ht["1"] == lang_code)
                    )
                    expansion = clean_node(config, ctx, None, expansion)
                    templates.append({
                        "name": name, "args": ht, "expansion": expansion
                    })
                return None

            text = clean_node(config, ctx, None, children, 
                template_fn=desc_template_fn,
                post_template_fn=desc_post_template_fn
            )
            item_data["templates"] = templates
            item_data["text"] = text
            if is_derived: item_data["tags"] = ["derived"]
            descendants.append(item_data)
        
        def is_list(c):
            return isinstance(c, WikiNode) and c.kind == NodeKind.LIST
        def is_list_item(c):
            return isinstance(c, WikiNode) and c.kind == NodeKind.LIST_ITEM
        def get_sublist_index(list_item):
            for i, child in enumerate(list_item.children):
                if is_list(child): return i
            return None

        def get_descendants(node):
            """Appends the data for every list item in every list in node
             to descendants."""
            for c in node.children:
                if is_list(c): 
                    get_descendants(c)
                elif is_list_item(c):
                    # If a LIST_ITEM has subitems in a sublist, usually its 
                    # last child is a LIST. However, sometimes after the LIST
                    # there is one or more trailing LIST_ITEMs, like "\n" or
                    # a reference template. If there is a sublist, we discard
                    # everything after it. 
                    i = get_sublist_index(c)
                    if i is not None:
                        process_list_item_children(c.args, c.children[:i])
                        get_descendants(c.children[i])
                    else:
                        process_list_item_children(c.args, c.children)

        # parse_descendants() actual work starts here
        get_descendants(node)

        # if e.g. on a PIE page, there may be both Derived terms and Extensions
        # sections, in which case this function will be called multiple times,
        # so we have to check if descendants exists first.
        if "descendants" in data: 
            data["descendants"].extend(descendants)
        else:
            data["descendants"] = descendants

    def process_children(treenode, pos):
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
            t = t.lower()
            config.section_counts[t] += 1
            # print("PROCESS_CHILDREN: T:", repr(t))
            if t.startswith(tuple(config.OTHER_SUBTITLES["pronunciation"])):
                if t.startswith(tuple(pron_title + " " for pron_title in config.OTHER_SUBTITLES["pronunciation"])):
                    # Pronunciation 1, etc, are used in Chinese Glyphs,
                    # and each of them may have senses under Definition
                    push_etym()
                    ctx.start_subsection(None)
                if config.capture_pronunciation:
                    data = select_data()
                    parse_pronunciation(ctx,
                                        config,
                                        node,
                                        data,
                                        etym_data,
                                        have_etym,
                                        base_data,
                                        lang_code,
                                        )
            elif t.startswith(tuple(config.OTHER_SUBTITLES["etymology"])):
                push_etym()
                ctx.start_subsection(None)
                if config.capture_etymologies:
                    m = re.search(r"\s(\d+)$", t)
                    if m:
                        etym_data["etymology_number"] = int(m.group(1))
                    parse_etymology(etym_data, node)
            elif t == config.OTHER_SUBTITLES["descendants"] and config.capture_descendants:
                data = select_data()
                parse_descendants(data, node)
            elif (t in config.OTHER_SUBTITLES["proto_root_derived_sections"] and 
                pos == "root" and is_reconstruction and 
                config.capture_descendants
            ):
                data = select_data()
                parse_descendants(data, node, True)
            elif t == config.OTHER_SUBTITLES["translations"]:
                data = select_data()
                parse_translations(data, node)
            elif t in config.OTHER_SUBTITLES["ignored_sections"]:
                pass
            elif t in config.OTHER_SUBTITLES["inflection_sections"]:
                parse_inflection(node, t, pos)
            else:
                lst = t.split()
                while len(lst) > 1 and lst[-1].isdigit():
                    lst = lst[:-1]
                t_no_number = " ".join(lst).lower()
                if t_no_number in config.POS_SUBTITLES:
                    push_pos()
                    dt = config.POS_SUBTITLES[t_no_number]
                    pos = dt["pos"]
                    ctx.start_subsection(t)
                    if "debug" in dt:
                        ctx.warning("{} in section {}"
                                    .format(dt["debug"], t),
                                    sortid="page/2755")
                    if "warning" in dt:
                        ctx.warning("{} in section {}"
                                    .format(dt["warning"], t),
                                    sortid="page/2759")
                    if "error" in dt:
                        ctx.error("{} in section {}"
                                  .format(dt["error"], t),
                                  sortid="page/2763")
                    # Parse word senses for the part-of-speech
                    parse_part_of_speech(node, pos)
                    if "tags" in dt:
                        for pdata in pos_datas:
                            data_extend(ctx, pdata, "tags", dt["tags"])
                elif t_no_number in config.LINKAGE_SUBTITLES:
                    rel = config.LINKAGE_SUBTITLES[t_no_number]
                    data = select_data()
                    parse_linkage(data, rel, node)
                elif t_no_number == config.OTHER_SUBTITLES["compounds"]:
                    data = select_data()
                    if config.capture_compounds:
                        parse_linkage(data, "derived", node)

            # XXX parse interesting templates also from other sections.  E.g.,
            # {{Letter|...}} in ===See also===
            # Also <gallery>

            # Recurse to children of this node, processing subtitles therein
            stack.append(t)
            process_children(node, pos)
            stack.pop()

    def extract_examples(others, sense_base):
        """Parses through a list of definitions and quotes to find examples.
        Returns a list of example dicts to be added to sense data. Adds
        meta-data, mostly categories, into sense_base."""
        assert isinstance(others, list)
        examples = []
        
        for sub in others:
            if not sub.args.endswith((":", "*")):
                continue
            for item in sub.children:
                if not isinstance(item, WikiNode):
                    continue
                if item.kind != NodeKind.LIST_ITEM:
                    continue
                usex_type = None
    
                def usex_template_fn(name, ht):
                    nonlocal usex_type
                    if name in panel_templates:
                        return ""
                    if name in usex_templates:
                        usex_type = "example"
                    elif name in quotation_templates:
                        usex_type = "quotation"
                    for prefix, t in template_linkage_mappings:
                        if re.search(r"(^|[-/\s]){}($|\b|[0-9])"
                                     .format(prefix),
                                     name):
                            return ""
                    return None
    
                subtext = clean_node(config, ctx, sense_base, item.children,
                                     template_fn=usex_template_fn)
                subtext = re.sub(r"\s*\(please add an English "
                                 r"translation of this "
                                 "(example|usage example|quote)\)",
                                 "", subtext).strip()
                subtext = re.sub(r"\^\([^)]*\)", "", subtext)
                subtext = re.sub(r"\s*[―—]+$", "", subtext)
                # print("subtext:", repr(subtext))
    
                lines = subtext.splitlines()
                lines = list(x for x in lines
                             if not re.match(
                                     r"(Synonyms: |Antonyms: |Hyponyms: |"
                                     r"Synonym: |Antonym: |Hyponym: |"
                                     r"Hypernyms: |Derived terms: |"
                                     r"Related terms: |"
                                     r"Hypernym: |Derived term: |"
                                     r"Coordinate terms:|"
                                     r"Related term: |"
                                     r"For more quotations using )",
                                     x))
                tr = ""
                ref = ""
                roman = ""
                # for line in lines:
                #     print("LINE:", repr(line))
                if len(lines) == 1 and lang_code != "en":
                    parts = re.split(r"\s*[―—]+\s*", lines[0])
                    if (len(parts) == 2 and
                        classify_desc(parts[1]) == "english"):
                        lines = [parts[0].strip()]
                        tr = parts[1].strip()
                    elif (len(parts) == 3 and
                          classify_desc(parts[1]) in ("romanization",
                                                      "english") and
                          classify_desc(parts[2]) == "english"):
                        lines = [parts[0].strip()]
                        roman = parts[1].strip()
                        tr = parts[2].strip()
                    else:
                        parts = re.split(r"\s+-\s+", lines[0])
                        if (len(parts) == 2 and
                            classify_desc(parts[1]) == "english"):
                            lines = [parts[0].strip()]
                            tr = parts[1].strip()
                elif len(lines) > 1:
                    if any(re.search(r"[]\d:)]\s*$", x)
                           for x in lines[:-1]):
                        ref = []
                        for i in range(len(lines)):
                            if re.match(r"^[#*]*:+(\s*$|\s+)", lines[i]):
                                break
                            ref.append(lines[i].strip())
                            if re.search(r"[]\d:)]\s*$", lines[i]):
                                break
                        ref = " ".join(ref)
                        lines = lines[i + 1:]
                        if (lang_code != "en" and len(lines) >= 2 and
                            classify_desc(lines[-1]) == "english"):
                            i = len(lines) - 1
                            while (i > 1 and
                                   classify_desc(lines[i - 1])
                                   == "english"):
                                i -= 1
                            tr = "\n".join(lines[i:])
                            lines = lines[:i]
    
                    elif (lang_code == "en" and
                          re.match(r"^[#*]*:+", lines[1])):
                        ref = lines[0]
                        lines = lines[1:]
                    elif lang_code != "en" and len(lines) == 2:
                        cls1 = classify_desc(lines[0])
                        cls2 = classify_desc(lines[1])
                        if cls2 == "english" and cls1 != "english":
                            tr = lines[1]
                            lines = [lines[0]]
                        elif cls1 == "english" and cls2 != "english":
                            tr = lines[0]
                            lines = [lines[1]]
                        elif (re.match(r"^[#*]*:+", lines[1]) and
                              classify_desc(re.sub(r"^[#*:]+\s*", "",
                                                   lines[1])) == "english"):
                            tr = re.sub(r"^[#*:]+\s*", "", lines[1])
                            lines = [lines[0]]
                        elif cls1 == "english" and cls2 == "english":
                            # Both were classified as English, but
                            # presumably one is not.  Assume first is
                            # non-English, as that seems more common.
                            tr = lines[1]
                            lines = [lines[0]]
                    elif (usex_type == "quotation" and
                          lang_code != "en" and len(lines) > 2):
                        # for x in lines:
                        #     print("  LINE: {}: {}"
                        #           .format(classify_desc(x), x))
                        if re.match(r"^[#*]*:+\s*$", lines[1]):
                            ref = lines[0]
                            lines = lines[2:]
                        cls1 = classify_desc(lines[-1])
                        if cls1 == "english":
                            i = len(lines) - 1
                            while (i > 1 and
                                   classify_desc(lines[i - 1])
                                   == "english"):
                                i -= 1
                            tr = "\n".join(lines[i:])
                            lines = lines[:i]
    
                roman = re.sub(r"[ \t\r]+", " ", roman).strip()
                roman = re.sub(r"\[\s*…\s*\]", "[…]", roman)
                tr = re.sub(r"^[#*:]+\s*", "", tr)
                tr = re.sub(r"[ \t\r]+", " ", tr).strip()
                tr = re.sub(r"\[\s*…\s*\]", "[…]", tr)
                ref = re.sub(r"^[#*:]+\s*", "", ref)
                ref = re.sub(r", (volume |number |page )?“?"
                             r"\(please specify ([^)]|\(s\))*\)”?|"
                             ", text here$",
                             "", ref)
                ref = re.sub(r"\[\s*…\s*\]", "[…]", ref)
                lines = list(re.sub(r"^[#*:]+\s*", "", x) for x in lines)
                subtext = "\n".join(x for x in lines if x)
                if not tr and lang_code != "en":
                    m = re.search(r"([.!?])\s+\(([^)]+)\)\s*$", subtext)
                    if m and classify_desc(m.group(2)) == "english":
                        tr = m.group(2)
                        subtext = subtext[:m.start()] + m.group(1)
                    elif lines:
                        parts = re.split(r"\s*[―—]+\s*", lines[0])
                        if (len(parts) == 2 and
                            classify_desc(parts[1]) == "english"):
                            subtext = parts[0].strip()
                            tr = parts[1].strip()
                subtext = re.sub(r'^[“"`]([^“"`”\']*)[”"\']$', r"\1",
                                 subtext)
                subtext = re.sub(r"(please add an English translation of "
                                 r"this (quote|usage example))",
                                 "", subtext)
                subtext = re.sub(r"\s*→New International Version "
                                 "translation$",
                                 "", subtext)  # e.g. pis/Tok Pisin (Bible)
                subtext = re.sub(r"[ \t\r]+", " ", subtext).strip()
                subtext = re.sub(r"\[\s*…\s*\]", "[…]", subtext)
                note = None
                m = re.match(r"^\(([^)]*)\):\s+", subtext)
                if (m is not None and lang_code != "en" and
                    (m.group(1).startswith("with ") or
                     classify_desc(m.group(1)) == "english")):
                    note = m.group(1)
                    subtext = subtext[m.end():]
                ref = re.sub(r"\s*\(→ISBN\)", "", ref)
                ref = re.sub(r",\s*→ISBN", "", ref)
                ref = ref.strip()
                if ref.endswith(":") or ref.endswith(","):
                    ref = ref[:-1].strip()
                ref = re.sub(r"\s+,\s+", ", ", ref)
                ref = re.sub(r"\s+", " ", ref)
                if ref and not subtext:
                    subtext = ref
                    ref = ""
                if subtext:
                    dt = {"text": subtext}
                    if ref:
                        dt["ref"] = ref
                    if tr:
                        dt["english"] = tr
                    if usex_type:
                        dt["type"] = usex_type
                    if note:
                        dt["note"] = note
                    if roman:
                        dt["roman"] = roman
                    examples.append(dt)
    
        return examples


    # Main code of parse_language()
    # Process the section
    stack.append(language)
    process_children(langnode, None)
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
        if name in ("reconstruction",):
            return ""
        if name.lower() == "also":
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
        if name == "wrongtitle":
            # XXX this should be captured to replace page title with the
            # correct title.  E.g. ⿰亻革家
            return ""
        if name == "wikidata":
            arg = clean_node(config, ctx, data, ht.get(1, ()))
            if arg.startswith("Q") or arg.startswith("Lexeme:L"):
                data_append(ctx, data, "wikidata", arg)
            return ""
        ctx.debug("UNIMPLEMENTED top-level template: {} {}"
                  .format(name, ht),
                  sortid="page/2870")
        return ""

    clean_node(config, ctx, None, [node], template_fn=top_template_fn)


def fix_subtitle_hierarchy(ctx: Wtp, config: WiktionaryConfig, text: str) -> str:
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
        # remove Wikilinks in title
        title = re.sub(r"^\[\[", "", old[i + 1])
        title = re.sub(r"\]\]$", "", title)
        level = len(left)
        part = old[i + npar]
        if level != len(right):
            ctx.debug("subtitle has unbalanced levels: "
                      "{!r} has {} on the left and {} on the right"
                      .format(title, left, right),
                      sortid="page/2904")
        lc = title.lower()
        if title in config.LANGUAGES_BY_NAME:
            if level > 2:
                ctx.debug("subtitle has language name {} at level {}"
                          .format(title, level),
                          sortid="page/2911")
            level = 2
        elif lc.startswith(tuple(config.OTHER_SUBTITLES["etymology"])):
            if level > 3:
                ctx.debug("etymology section {} at level {}"
                          .format(title, level),
                          sortid="page/2917")
            level = 3
        elif lc.startswith(tuple(config.OTHER_SUBTITLES["pronunciation"])):
            level = 3
        elif lc in config.POS_SUBTITLES:
            level = 4
        elif lc == config.OTHER_SUBTITLES["translations"]:
            level = 5
        elif lc in config.LINKAGE_SUBTITLES or lc == config.OTHER_SUBTITLES["compounds"]:
            level = 5
        elif lc in config.OTHER_SUBTITLES["inflection_sections"]:
            level = 5
        elif lc == config.OTHER_SUBTITLES["descendants"]:
            level = 5
        elif title in  config.OTHER_SUBTITLES["proto_root_derived_sections"]:
            level = 5
        elif lc in config.OTHER_SUBTITLES["ignored_sections"]:
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


def parse_page(ctx: Wtp, word: str, text: str, config: WiktionaryConfig) -> list:  # list[dict[str, str]]
    """Parses the text of a Wiktionary page and returns a list of
    dictionaries, one for each word/part-of-speech defined on the page
    for the languages specified by ``capture_language_codes`` (None means
    all available languages).  ``word`` is page title, and ``text`` is
    page text in Wikimedia format.  Other arguments indicate what is
    captured."""
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(text, str)
    assert isinstance(config, WiktionaryConfig)

    global starts_lang_re
    if starts_lang_re is None:
        starts_lang_re = re.compile(
            r"^(" + ctx.NAMESPACE_DATA.get("Rhymes", {}).get("name", "") + ":)?(" +
            "|".join(re.escape(x) for x in config.LANGUAGES_BY_NAME) +
            ")[ /]")

    # Skip words that have been moved to the Attic
    if word.startswith("/(Attic) "):
        return []

    if config.verbose:
        print("Parsing page:", word)

    config.word = word
    ctx.start_page(word)

    # Remove <noinclude> and similar tags from main pages.  They
    # should not appear there, but at least net/Elfdala has one and it
    # is probably not the only one.
    text = re.sub(r"(?si)<\s*(/\s*)?noinclude\s*>", "", text)
    text = re.sub(r"(?si)<\s*(/\s*)?onlyinclude\s*>", "", text)
    text = re.sub(r"(?si)<\s*(/\s*)?includeonly\s*>", "", text)

    # Expand Chinese Wiktionary language and POS heading templates
    # Language templates: https://zh.wiktionary.org/wiki/Category:语言模板
    # POS templates: https://zh.wiktionary.org/wiki/Category:詞類模板
    if config.dump_file_lang_code == "zh" and ("{{-" in text or "{{=" in text):
        text = ctx.expand(text, pre_expand=True)

    # Fix up the subtitle hierarchy.  There are hundreds if not thousands of
    # pages that have, for example, Translations section under Linkage, or
    # Translations section on the same level as Noun.  Enforce a proper
    # hierarchy by manipulating the subtitle levels in certain cases.
    text = fix_subtitle_hierarchy(ctx, config, text)

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
            ctx.debug("unexpected top-level node: {}".format(langnode),
                      sortid="page/3014")
            continue
        lang = clean_node(config, ctx, None, langnode.args)
        if lang not in config.LANGUAGES_BY_NAME:
            ctx.debug("unrecognized language name at top-level {!r}"
                      .format(lang), sortid="page/3019")
            continue
        lang_code = config.LANGUAGES_BY_NAME.get(lang)
        if config.capture_language_codes and lang_code not in config.capture_language_codes:
            continue
        ctx.start_section(lang)

        # Collect all words from the page.
        datas = parse_language(ctx, config, langnode, lang, lang_code)

        # Propagate fields resulting from top-level templates to this
        # part-of-speech.
        for data in datas:
            if "lang" not in data:
                ctx.debug("internal error -- no lang in data: {}".format(data),
                          sortid="page/3034")
                continue
            for k, v in top_data.items():
                assert isinstance(v, (list, tuple))
                data_extend(ctx, data, k, v)
            by_lang[data["lang"]].append(data)

    # XXX this code is clearly out of date.  There is no longer a "conjugation"
    # field.  FIX OR REMOVE.
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
                    dt["roman"] = xlit
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
                catlang_code = config.LANGUAGES_BY_NAME.get(catlang)
                if (catlang != lang and not (catlang_code == "en" and
                                             data.get("lang_code") == "mul")):
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
            if value.kind in (NodeKind.TABLE_CELL, NodeKind.TABLE_HEADER_CELL):
                ret = recurse(value.children)
            else:
                ret = ctx.node_to_html(value, template_fn=clean_template_fn,
                                       post_template_fn=post_template_fn)
            # print("clean_value recurse node_to_html value={!r} ret={!r}"
            #      .format(value, ret))
        else:
            ret = str(value)
        return ret

    def clean_node_handler_fn(node):
        assert isinstance(node, WikiNode)
        kind = node.kind
        if kind in (NodeKind.TABLE_CELL, NodeKind.TABLE_HEADER_CELL,
                    NodeKind.BOLD, NodeKind.ITALIC):
            return node.children
        return None

    # print("clean_node: value={!r}".format(value))
    v = ctx.node_to_html(value, node_handler_fn=clean_node_handler_fn,
                         template_fn=template_fn,
                         post_template_fn=post_template_fn)
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


def add_form_of_tags(ctx, template_name, form_of_templates, sense_data):
    # https://en.wiktionary.org/wiki/Category:Form-of_templates
    if template_name in form_of_templates:
        data_append(ctx, sense_data, "tags", "form-of")

        if template_name in ("abbreviation of", "abbr of"):
            data_append(ctx, sense_data, "tags", "abbreviation")
        elif template_name.startswith(("alt ", "alternative")):
            data_append(ctx, sense_data, "tags", "alt-of")
        elif template_name.startswith(("female", "feminine")):
            data_append(ctx, sense_data, "tags", "feminine")
        elif template_name == "initialism of":
            data_extend(ctx, sense_data, "tags", ["abbreviation", "initialism"])
        elif template_name.startswith("masculine"):
            data_append(ctx, sense_data, "tags", "masculine")
        elif template_name.startswith("misspelling"):
            data_append(ctx, sense_data, "tags", "misspelling")
        elif template_name.startswith(("obsolete", "obs ")):
            data_append(ctx, sense_data, "tags", "obsolete")

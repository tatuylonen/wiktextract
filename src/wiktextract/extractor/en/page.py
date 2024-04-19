# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import copy
import html
import re
import sys
from collections import defaultdict
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Optional,
    Set,
    Union,
    cast,
)

from mediawiki_langcodes import get_all_names, name_to_code
from wikitextprocessor import NodeKind, WikiNode
from wikitextprocessor.core import TemplateArgs, TemplateFnCallable
from wikitextprocessor.parser import GeneralNode, TemplateNode
from wiktextract.clean import clean_template_args
from wiktextract.datautils import (
    data_append,
    data_extend,
    ns_title_prefix_tuple,
)
from wiktextract.form_descriptions import (
    classify_desc,
    decode_tags,
    distw,
    parse_alt_or_inflection_of,
    parse_sense_qualifier,
    parse_word_head,
)
from wiktextract.inflection import TableContext, parse_inflection_section
from wiktextract.linkages import parse_linkage_item_text
from wiktextract.logging import logger
from wiktextract.page import (
    LEVEL_KINDS,
    clean_node,
    is_panel_template,
    recursively_extract,
)
from wiktextract.parts_of_speech import PARTS_OF_SPEECH
from wiktextract.tags import valid_tags
from wiktextract.translations import parse_translation_item_text
from wiktextract.type_utils import SenseData, SoundData, WordData, LinkageData
from wiktextract.wxr_context import WiktextractContext

from ..ruby import extract_ruby, parse_ruby
from ..share import strip_nodes
from .section_titles import (
    COMPOUNDS_TITLE,
    DESCENDANTS_TITLE,
    ETYMOLOGY_TITLES,
    IGNORED_TITLES,
    INFLECTION_TITLES,
    LINKAGE_TITLES,
    POS_TITLES,
    PRONUNCIATION_TITLE,
    PROTO_ROOT_DERIVED_TITLES,
    TRANSLATIONS_TITLE,
)
from .unsupported_titles import unsupported_title_map

# Matches head tag
HEAD_TAG_RE = re.compile(
    r"^(head|Han char|arabic-noun|arabic-noun-form|"
    r"hangul-symbol|syllable-hangul)$|"
    + r"^(latin|"
    + "|".join(lang_code for lang_code, *_ in get_all_names("en"))
    + r")-("
    + "|".join(
        [
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
        ]
    )
    + r")(-|/|\+|$)"
)

FLOATING_TABLE_TEMPLATES: set[str] = {
    # az-suffix-form creates a style=floatright div that is otherwise
    # deleted; if it is not pre-expanded, we can intercept the template
    # so we add this set into do_not_pre_expand, and intercept the
    # templates in parse_part_of_speech
    "az-suffix-forms",
    "az-inf-p",
    "kk-suffix-forms",
    "ky-suffix-forms",
    "tr-inf-p",
    "tr-suffix-forms",
    "tt-suffix-forms",
    "uz-suffix-forms",
}
# These two should contain template names that should always be
# pre-expanded when *first* processing the tree, or not pre-expanded
# so that the template are left in place with their identifying
# name intact for later filtering.

DO_NOT_PRE_EXPAND_TEMPLATES: set[str] = set()
DO_NOT_PRE_EXPAND_TEMPLATES.update(FLOATING_TABLE_TEMPLATES)

# Additional templates to be expanded in the pre-expand phase
ADDITIONAL_EXPAND_TEMPLATES: set[str] = {
    "multitrans",
    "multitrans-nowiki",
    "trans-top",
    "trans-top-also",
    "trans-bottom",
    "checktrans-top",
    "checktrans-bottom",
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
    "ru-alt-ё",
    "inflection of",
    "no deprecated lang param usage",
}

# Inverse linkage for those that have them
linkage_inverses: dict[str, str] = {
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
PANEL_TEMPLATES: set[str] = {
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
zh_tag_lookup: dict[str, list[str]] = {
    "Formal": ["formal"],
    "Written-Standard-Chinese": ["Standard-Chinese"],
    "historical or Internet slang": ["historical", "internet-slang"],
    "now usually derogatory or offensive": ["offensive", "derogatory"],
    "lofty": [],
}

# Template name prefixes used for language-specific panel templates (i.e.,
# templates that create side boxes or notice boxes or that should generally
# be ignored).
PANEL_PREFIXES: set[str] = {
    "list:compass points/",
    "list:Gregorian calendar months/",
    "RQ:",
}

# Templates used for wikipedia links.
wikipedia_templates: set[str] = {
    "wikipedia",
    "slim-wikipedia",
    "w",
    "W",
    "swp",
    "wiki",
    "Wikipedia",
    "wtorw",
}
for x in PANEL_PREFIXES & wikipedia_templates:
    print(
        "WARNING: {!r} in both panel_templates and wikipedia_templates".format(
            x
        )
    )

# Mapping from a template name (without language prefix) for the main word
# (e.g., fi-noun, fi-adj, en-verb) to permitted parts-of-speech in which
# it could validly occur.  This is used as just a sanity check to give
# warnings about probably incorrect coding in Wiktionary.
template_allowed_pos_map: dict[str, list[str]] = {
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
            print(
                "BAD PART OF SPEECH {!r} IN template_allowed_pos_map: {}={}"
                "".format(x, k, v)
            )
            assert False


# Templates ignored during etymology extraction, i.e., these will not be listed
# in the extracted etymology templates.
ignored_etymology_templates: list[str] = [
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
    "catlangname",
    "cln",
]
# Regexp for matching ignored etymology template names.  This adds certain
# prefixes to the names listed above.
ignored_etymology_templates_re = re.compile(
    r"^((cite-|R:|RQ:).*|"
    + r"|".join(re.escape(x) for x in ignored_etymology_templates)
    + r")$"
)

# Regexp for matching ignored descendants template names. Right now we just
# copy the ignored etymology templates
ignored_descendants_templates_re = ignored_etymology_templates_re

# Set of template names that are used to define usage examples.  If the usage
# example contains one of these templates, then it its type is set to
# "example"
usex_templates: set[str] = {
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
    "ur-x",
    "usex",
    "usex-suffix",
    "ux",
    "uxi",
    "zh-usex",
    "zh-x",
}

stop_head_at_these_templates: set[str] = {
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
quotation_templates: set[str] = {
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
# XXX not used anymore, except for the first elements: moved to
# template_linkages
# template_linkage_mappings: list[list[Union[str, int]]] = [
#     ["syn", "synonyms"],
#     ["synonyms", "synonyms"],
#     ["ant", "antonyms"],
#     ["antonyms", "antonyms"],
#     ["hyp", "hyponyms"],
#     ["hyponyms", "hyponyms"],
#     ["der", "derived"],
#     ["derived terms", "derived"],
#     ["coordinate terms", "coordinate_terms"],
#     ["rel", "related"],
#     ["col", 2],
# ]

# Template names, this was exctracted from template_linkage_mappings,
# because the code using template_linkage_mappings was actually not used
# (but not removed).
template_linkages: set[str] = {
    "syn",
    "synonyms",
    "ant",
    "antonyms",
    "hyp",
    "hyponyms",
    "der",
    "derived terms",
    "coordinate terms",
    "rel",
    "col",
}

# Maps template name used in a word sense to a linkage field that it adds.
sense_linkage_templates: dict[str, str] = {
    "syn": "synonyms",
    "synonyms": "synonyms",
    "hyp": "hyponyms",
    "hyponyms": "hyponyms",
    "ant": "antonyms",
    "antonyms": "antonyms",
}


def decode_html_entities(v: Union[str, int]) -> str:
    """Decodes HTML entities from a value, converting them to the respective
    Unicode characters/strings."""
    if isinstance(v, int):
        # I changed this to return str(v) instead of v = str(v),
        # but there might have been the intention to have more logic
        # here. html.unescape would not do anything special with an integer,
        # it needs html escape symbols (&xx;).
        return str(v)
    return html.unescape(v)


def parse_sense_linkage(
    wxr: WiktextractContext,
    data: SenseData,
    name: str,
    ht: TemplateArgs,
) -> None:
    """Parses a linkage (synonym, etc) specified in a word sense."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(data, dict)
    assert isinstance(name, str)
    assert isinstance(ht, dict)
    field = sense_linkage_templates[name]
    for i in range(2, 20):
        w = ht.get(i) or ""
        w = clean_node(wxr, data, w)
        for alias in ns_title_prefix_tuple(wxr, "Thesaurus"):
            if w.startswith(alias):
                w = w[len(alias) :]
                break
        if not w:
            break
        tags: list[str] = []
        topics: list[str] = []
        english: Optional[str] = None
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
            w = w[: m.start()].strip()
            alt = m.group(1)

        dt = {"word": w}
        if tags:
            data_extend(dt, "tags", tags)
        if topics:
            data_extend(dt, "topics", topics)
        if english:
            dt["english"] = english
        if alt:
            dt["alt"] = alt
        data_append(data, field, dt)


def parse_language(
    wxr: WiktextractContext, langnode: WikiNode, language: str, lang_code: str
) -> list[WordData]:
    """Iterates over the text of the page, returning words (parts-of-speech)
    defined on the page one at a time.  (Individual word senses for the
    same part-of-speech are typically encoded in the same entry.)"""
    # imported here to avoid circular import
    from .pronunciations import parse_pronunciation

    assert isinstance(wxr, WiktextractContext)
    assert isinstance(langnode, WikiNode)
    assert isinstance(language, str)
    assert isinstance(lang_code, str)
    # print("parse_language", language)

    is_reconstruction = False
    word: str = wxr.wtp.title  # type: ignore[assignment]
    unsupported_prefix = "Unsupported titles/"
    if word.startswith(unsupported_prefix):
        w = word[len(unsupported_prefix) :]
        if w in unsupported_title_map:
            word = unsupported_title_map[w]
        else:
            wxr.wtp.error(
                "Unimplemented unsupported title: {}".format(word),
                sortid="page/870",
            )
            word = w
    elif word.startswith("Reconstruction:"):
        word = word[word.find("/") + 1 :]
        is_reconstruction = True

    base_data: WordData = {
        "word": word,
        "lang": language,
        "lang_code": lang_code,
    }
    if is_reconstruction:
        data_append(base_data, "tags", "reconstruction")
    sense_data: SenseData = {}
    pos_data: WordData = {}  # For a current part-of-speech
    etym_data: WordData = {}  # For one etymology
    pos_datas: list[SenseData] = []
    etym_datas: list[WordData] = []
    page_datas: list[WordData] = []
    have_etym = False
    stack: list[str] = []  # names of items on the "stack"

    def merge_base(data: WordData, base: WordData) -> None:
        for k, v in base.items():
            # Copy the value to ensure that we don't share lists or
            # dicts between structures (even nested ones).
            v = copy.deepcopy(v)
            if k not in data:
                # The list was copied above, so this will not create shared ref
                data[k] = v  # type: ignore[literal-required]
                continue
            if data[k] == v:  # type: ignore[literal-required]
                continue
            if (
                isinstance(data[k], (list, tuple))  # type: ignore[literal-required]
                or isinstance(
                    v,
                    (list, tuple),  # Should this be "and"?
                )
            ):
                data[k] = list(data[k]) + list(v)  # type: ignore
            elif data[k] != v:  # type: ignore[literal-required]
                wxr.wtp.warning(
                    "conflicting values for {} in merge_base: "
                    "{!r} vs {!r}".format(k, data[k], v),  # type: ignore[literal-required]
                    sortid="page/904",
                )

        def complementary_pop(pron: SoundData, key: str) -> SoundData:
            """Remove unnecessary keys from dict values
            in a list comprehension..."""
            if key in pron:
                pron.pop(key)  # type: ignore
            return pron

        # If the result has sounds, eliminate sounds that have a prefix that
        # does not match "word" or one of "forms"
        if "sounds" in data and "word" in data:
            accepted = [data["word"]]
            accepted.extend(f["form"] for f in data.get("forms", dict()))
            data["sounds"] = list(
                s
                for s in data["sounds"]
                if "form" not in s or s["form"] in accepted
            )
        # If the result has sounds, eliminate sounds that have a pos that
        # does not match "pos"
        if "sounds" in data and "pos" in data:
            data["sounds"] = list(
                complementary_pop(s, "pos")
                for s in data["sounds"]
                # "pos" is not a field of SoundData, correctly, so we're
                # removing it here. It's a kludge on a kludge on a kludge.
                if "pos" not in s or s["pos"] == data["pos"]  # type: ignore[typeddict-item]
            )

    def push_sense() -> bool:
        """Starts collecting data for a new word sense.  This returns True
        if a sense was added."""
        nonlocal sense_data
        tags = sense_data.get("tags", ())
        if (
            not sense_data.get("glosses")
            and "translation-hub" not in tags
            and "no-gloss" not in tags
        ):
            return False

        if (
            (
                "participle" in sense_data.get("tags", ())
                or "infinitive" in sense_data.get("tags", ())
            )
            and "alt_of" not in sense_data
            and "form_of" not in sense_data
            and "etymology_text" in etym_data
            and etym_data["etymology_text"] != ""
        ):
            etym = etym_data["etymology_text"]
            etym = etym.split(". ")[0]
            ret = parse_alt_or_inflection_of(wxr, etym, set())
            if ret is not None:
                tags, lst = ret
                assert isinstance(lst, (list, tuple))
                if "form-of" in tags:
                    data_extend(sense_data, "form_of", lst)
                    data_extend(sense_data, "tags", tags)
                elif "alt-of" in tags:
                    data_extend(sense_data, "alt_of", lst)
                    data_extend(sense_data, "tags", tags)

        if not sense_data.get("glosses") and "no-gloss" not in sense_data.get(
            "tags", ()
        ):
            data_append(sense_data, "tags", "no-gloss")

        pos_datas.append(sense_data)
        sense_data = {}
        return True

    def push_pos() -> None:
        """Starts collecting data for a new part-of-speech."""
        nonlocal pos_data
        nonlocal pos_datas
        push_sense()
        if wxr.wtp.subsection:
            data: WordData = {"senses": pos_datas}
            merge_base(data, pos_data)
            etym_datas.append(data)
        pos_data = {}
        pos_datas = []
        wxr.wtp.start_subsection(None)

    def push_etym() -> None:
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

    def select_data() -> WordData:
        """Selects where to store data (pos or etym) based on whether we
        are inside a pos (part-of-speech)."""
        if wxr.wtp.subsection is not None:
            return pos_data
        if stack[-1] == language:
            return base_data
        return etym_data

    def head_post_template_fn(
        name: str, ht: TemplateArgs, expansion: str
    ) -> Optional[str]:
        """Handles special templates in the head section of a word.  Head
        section is the text after part-of-speech subtitle and before word
        sense list. Typically it generates the bold line for the word, but
        may also contain other useful information that often ends in
        side boxes.  We want to capture some of that additional information."""
        # print("HEAD_POST_TEMPLATE_FN", name, ht)
        if is_panel_template(wxr, name):
            # Completely ignore these templates (not even recorded in
            # head_templates)
            return ""
        if name == "head":
            # XXX are these also captured in forms?  Should this special case
            # be removed?
            t = ht.get(2, "")
            if t == "pinyin":
                data_append(pos_data, "tags", "Pinyin")
            elif t == "romanization":
                data_append(pos_data, "tags", "romanization")
        if HEAD_TAG_RE.fullmatch(name) is not None:
            args_ht = clean_template_args(wxr, ht)
            cleaned_expansion = clean_node(wxr, None, expansion)
            dt = {"name": name, "args": args_ht, "expansion": cleaned_expansion}
            data_append(pos_data, "head_templates", dt)

        # The following are both captured in head_templates and parsed
        # separately

        if name in wikipedia_templates:
            # Note: various places expect to have content from wikipedia
            # templates, so cannot convert this to empty
            parse_wikipedia_template(wxr, pos_data, ht)
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

    def parse_part_of_speech(posnode: WikiNode, pos: str) -> None:
        """Parses the subsection for a part-of-speech under a language on
        a page."""
        assert isinstance(posnode, WikiNode)
        assert isinstance(pos, str)
        # print("parse_part_of_speech", pos)
        pos_data["pos"] = pos
        pre: list[list[Union[str, WikiNode]]] = [[]]  # list of lists
        lists: list[list[WikiNode]] = [[]]  # list of lists
        first_para = True
        first_head_tmplt = True
        collecting_head = True
        start_of_paragraph = True

        # XXX extract templates from posnode with recursively_extract
        # that break stuff, like ja-kanji or az-suffix-form.
        # Do the extraction with a list of template names, combined from
        # different lists, then separate out them into different lists
        # that are handled at different points of the POS section.
        # First, extract az-suffix-form, put it in `inflection`,
        # and parse `inflection`'s content when appropriate later.
        # The contents of az-suffix-form (and ja-kanji) that generate
        # divs with "floatright" in their style gets deleted by
        # clean_value, so templates that slip through from here won't
        # break anything.
        # XXX bookmark
        # print(posnode.children)

        floaters, poschildren = recursively_extract(
            posnode.children,
            lambda x: (
                isinstance(x, WikiNode)
                and x.kind == NodeKind.TEMPLATE
                and x.largs[0][0] in FLOATING_TABLE_TEMPLATES
            ),
        )
        tempnode = WikiNode(NodeKind.LEVEL5, 0)
        tempnode.largs = [["Inflection"]]
        tempnode.children = floaters
        parse_inflection(tempnode, "Floating Div", pos)
        # print(poschildren)
        # XXX new above

        if not poschildren:
            if not floaters:
                wxr.wtp.debug(
                    "PoS section without contents",
                    sortid="en/page/1051/20230612",
                )
            else:
                wxr.wtp.debug(
                    "PoS section without contents except for a floating table",
                    sortid="en/page/1056/20230612",
                )
            return

        for node in poschildren:
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
                if len(node.largs[0]) >= 1 and isinstance(
                    node.largs[0][0], str
                ):
                    if node.largs[0][0].startswith(
                        ns_title_prefix_tuple(wxr, "Category")
                    ):
                        # [[Category:...]]
                        # We're at the end of the file, probably, so stop
                        # here. Otherwise the head will get garbage.
                        break
                    if node.largs[0][0].startswith(
                        ns_title_prefix_tuple(wxr, "File")
                    ):
                        # Skips file links
                        continue
                start_of_paragraph = False
                pre[-1].extend(node.largs[-1])
            elif kind == NodeKind.HTML:
                if node.sarg == "br":
                    if pre[-1]:
                        pre.append([])  # Switch to next head
                        lists.append([])  # Lists parallels pre
                        collecting_head = True
                        start_of_paragraph = True
                elif collecting_head and node.sarg not in (
                    "gallery",
                    "ref",
                    "cite",
                    "caption",
                ):
                    start_of_paragraph = False
                    pre[-1].append(node)
                else:
                    start_of_paragraph = False
            elif kind == NodeKind.TEMPLATE:
                # XXX Insert code here that disambiguates between
                # templates that generate word heads and templates
                # that don't.
                # There's head_tag_re that seems like a regex meant
                # to identify head templates. Too bad it's None.

                # ignore {{category}}, {{cat}}... etc.
                if node.largs[0][0] in stop_head_at_these_templates:
                    # we've reached a template that should be at the end,
                    continue

                # skip these templates; panel_templates is already used
                # to skip certain templates else, but it also applies to
                # head parsing quite well.
                # node.largs[0][0] should always be str, but can't type-check
                # that.
                if is_panel_template(wxr, node.largs[0][0]):  # type: ignore[arg-type]
                    continue
                # skip these templates
                # if node.largs[0][0] in skip_these_templates_in_head:
                # first_head_tmplt = False # no first_head_tmplt at all
                # start_of_paragraph = False
                # continue

                if first_head_tmplt and pre[-1]:
                    first_head_tmplt = False
                    start_of_paragraph = False
                    pre[-1].append(node)
                elif pre[-1] and start_of_paragraph:
                    pre.append([])  # Switch to the next head
                    lists.append([])  # lists parallel pre
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

        # Clean up empty pairs, and fix messes with extra newlines that
        # separate templates that are followed by lists wiktextract issue #314

        cleaned_pre: list[list[Union[str, WikiNode]]] = []
        cleaned_lists: list[list[WikiNode]] = []
        pairless_pre_index = None

        for pre1, ls in zip(pre, lists):
            if pre1 and not ls:
                pairless_pre_index = len(cleaned_pre)
            if not pre1 and not ls:
                # skip [] + []
                continue
            if not ls and all(
                (isinstance(x, str) and not x.strip()) for x in pre1
            ):
                # skip ["\n", " "] + []
                continue
            if ls and not pre1:
                if pairless_pre_index is not None:
                    cleaned_lists[pairless_pre_index] = ls
                    pairless_pre_index = None
                    continue
            cleaned_pre.append(pre1)
            cleaned_lists.append(ls)

        pre = cleaned_pre
        lists = cleaned_lists

        there_are_many_heads = len(pre) > 1
        header_tags: list[str] = []

        if not any(g for g in lists):
            process_gloss_without_list(poschildren, pos, pos_data, header_tags)
        else:
            for i, (pre1, ls) in enumerate(zip(pre, lists)):
                # if len(ls) == 0:
                #     # don't have gloss list
                #     # XXX add code here to filter out 'garbage', like text
                #     # that isn't a head template or head.
                # continue

                if all(not sl for sl in lists[i:]):
                    if i == 0:
                        if isinstance(node, str):
                            wxr.wtp.debug(
                                "first head without list of senses,"
                                "string: '{}[...]', {}/{}".format(
                                    node[:20], word, language
                                ),
                                sortid="page/1689/20221215",
                            )
                        if isinstance(node, WikiNode):
                            if node.largs and node.largs[0][0] in [
                                "Han char",
                            ]:
                                # just ignore these templates
                                pass
                            else:
                                wxr.wtp.debug(
                                    "first head without "
                                    "list of senses, "
                                    "template node "
                                    "{}, {}/{}".format(
                                        node.largs, word, language
                                    ),
                                    sortid="page/1694/20221215",
                                )
                        else:
                            wxr.wtp.debug(
                                "first head without list of senses, "
                                "{}/{}".format(word, language),
                                sortid="page/1700/20221215",
                            )
                        # no break here so that the first head always
                        # gets processed.
                    else:
                        if isinstance(node, str):
                            wxr.wtp.debug(
                                "later head without list of senses,"
                                "string: '{}[...]', {}/{}".format(
                                    node[:20], word, language
                                ),
                                sortid="page/1708/20221215",
                            )
                        if isinstance(node, WikiNode):
                            wxr.wtp.debug(
                                "later head without list of senses,"
                                "template node "
                                "{}, {}/{}".format(
                                    node.sarg if node.sarg else node.largs,
                                    word,
                                    language,
                                ),
                                sortid="page/1713/20221215",
                            )
                        else:
                            wxr.wtp.debug(
                                "later head without list of senses, "
                                "{}/{}".format(word, language),
                                sortid="page/1719/20221215",
                            )
                        break
                head_group = i + 1 if there_are_many_heads else None
                # print("parse_part_of_speech: {}: {}: pre={}"
                # .format(wxr.wtp.section, wxr.wtp.subsection, pre1))
                process_gloss_header(
                    pre1, pos, head_group, pos_data, header_tags
                )
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
                        common_data: SenseData = {"tags": list(header_tags)}
                        if head_group:
                            common_data["head_nr"] = head_group
                        parse_sense_node(node, common_data, pos)  # type: ignore[arg-type]

        # If there are no senses extracted, add a dummy sense.  We want to
        # keep tags extracted from the head for the dummy sense.
        push_sense()  # Make sure unfinished data pushed, and start clean sense
        if not pos_datas:
            data_extend(sense_data, "tags", header_tags)
            data_append(sense_data, "tags", "no-gloss")
            push_sense()

    def process_gloss_header(
        header_nodes: list[Union[WikiNode, str]],
        pos_type: str,
        header_group: Optional[int],
        pos_data: WordData,
        header_tags: list[str],
    ) -> None:
        ruby = []
        links: list[str] = []
        if not word.isalnum():
            # if the word contains non-letter or -number characters, it might
            # have something that messes with split-at-semi-comma; we collect
            # links so that we can skip splitting them.
            exp = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(header_nodes), expand_all=True
            )
            link_nodes, _ = recursively_extract(
                exp.children,
                lambda x: isinstance(x, WikiNode) and x.kind == NodeKind.LINK,
            )
            for ln in link_nodes:
                ltext = clean_node(wxr, None, ln.largs[-1])  # type: ignore[union-attr]
                if not ltext.isalnum():
                    links.append(ltext)
            if word not in links:
                links.append(word)
        if lang_code == "ja":
            exp = wxr.wtp.parse(
                wxr.wtp.node_to_wikitext(header_nodes), expand_all=True
            )
            rub, _ = recursively_extract(
                exp.children,
                lambda x: isinstance(x, WikiNode)
                and x.kind == NodeKind.HTML
                and x.sarg == "ruby",
            )
            if rub is not None:
                for r in rub:
                    if TYPE_CHECKING:
                        # we know the lambda above in recursively_extract
                        # returns only WikiNodes in rub
                        assert isinstance(r, WikiNode)
                    rt = parse_ruby(wxr, r)
                    if rt is not None:
                        ruby.append(rt)
        header_text = clean_node(
            wxr, pos_data, header_nodes, post_template_fn=head_post_template_fn
        )
        header_text = re.sub(r"\s+", " ", header_text)
        # print(f"{header_text=}")
        parse_word_head(
            wxr,
            pos_type,
            header_text,
            pos_data,
            is_reconstruction,
            header_group,
            ruby=ruby,
            links=links,
        )
        if "tags" in pos_data:
            # pos_data can get "tags" data from some source; type-checkers
            # doesn't like it, so let's ignore it.
            header_tags[:] = pos_data["tags"]  # type: ignore[typeddict-item]
            del pos_data["tags"]  # type: ignore[typeddict-item]
        else:
            header_tags.clear()

    def process_gloss_without_list(
        nodes: list[Union[WikiNode, str]],
        pos_type: str,
        pos_data: WordData,
        header_tags: list[str],
    ) -> None:
        # gloss text might not inside a list
        header_nodes: list[Union[str, WikiNode]] = []
        gloss_nodes: list[Union[str, WikiNode]] = []
        for node in strip_nodes(nodes):
            if isinstance(node, WikiNode):
                if node.kind == NodeKind.TEMPLATE:
                    template_name = node.largs[0][0]
                    if TYPE_CHECKING:
                        assert isinstance(template_name, str)
                    if template_name == "head" or template_name.startswith(
                        f"{lang_code}-"
                    ):
                        header_nodes.append(node)
                        continue
                elif node.kind in LEVEL_KINDS:  # following nodes are not gloss
                    break
            gloss_nodes.append(node)

        if len(header_nodes) > 0:
            process_gloss_header(
                header_nodes, pos_type, None, pos_data, header_tags
            )
        if len(gloss_nodes) > 0:
            process_gloss_contents(
                gloss_nodes, pos_type, {"tags": list(header_tags)}
            )

    def parse_sense_node(
        node: Union[str, WikiNode],  # never receives str
        sense_base: SenseData,
        pos: str,
    ) -> bool:
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
            # This doesn't seem to ever happen in practice.
            wxr.wtp.debug(
                "{}: parse_sense_node called with"
                "something that isn't a WikiNode".format(pos),
                sortid="page/1287/20230119",
            )
            return False

        if node.kind != NodeKind.LIST_ITEM:
            wxr.wtp.debug(
                "{}: non-list-item inside list".format(pos), sortid="page/1678"
            )
            return False

        if node.sarg == ":":
            # Skip example entries at the highest level, ones without
            # a sense ("...#") above them.
            # If node.sarg is exactly and only ":", then it's at
            # the highest level; lower levels would have more
            # "indentation", like "#:" or "##:"
            return False

        # If a recursion call succeeds in push_sense(), bubble it up with
        # `added`.
        # added |= push_sense() or added |= parse_sense_node(...) to OR.
        added = False

        gloss_template_args: set[str] = set()

        # For LISTs and LIST_ITEMS, their argument is something like
        # "##" or "##:", and using that we can rudimentally determine
        # list 'depth' if need be, and also what kind of list or
        # entry it is; # is for normal glosses, : for examples (indent)
        # and * is used for quotations on wiktionary.
        current_depth = node.sarg

        children = node.children

        # subentries, (presumably) a list
        # of subglosses below this. The list's
        # argument ends with #, and its depth should
        # be bigger than parent node.
        subentries = [
            x
            for x in children
            if isinstance(x, WikiNode)
            and x.kind == NodeKind.LIST
            and x.sarg == current_depth + "#"
        ]

        # sublists of examples and quotations. .sarg
        # does not end with "#".
        others = [
            x
            for x in children
            if isinstance(x, WikiNode)
            and x.kind == NodeKind.LIST
            and x.sarg != current_depth + "#"
        ]

        # the actual contents of this particular node.
        # can be a gloss (or a template that expands into
        # many glosses which we can't easily pre-expand)
        # or could be an "outer gloss" with more specific
        # subglosses, or could be a qualfier for the subglosses.
        contents = [
            x
            for x in children
            if not isinstance(x, WikiNode) or x.kind != NodeKind.LIST
        ]
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
                cropped_node.children = [
                    x
                    for x in children
                    if not (
                        isinstance(x, WikiNode)
                        and x.kind == NodeKind.LIST
                        and x.sarg == current_depth + "#"
                    )
                ]
                added |= parse_sense_node(cropped_node, sense_base, pos)
                nonlocal sense_data  # this kludge causes duplicated raw_
                # glosses data if this is not done;
                # if the top-level (cropped_node)
                # does not push_sense() properly or
                # parse_sense_node() returns early,
                # sense_data is not reset. This happens
                # for example when you have a no-gloss
                # string like "(intransitive)":
                # no gloss, push_sense() returns early
                # and sense_data has duplicate data with
                # sense_base
                sense_data = {}
                added |= parse_sense_node(slc[0], sense_base, pos)
                return added

        return process_gloss_contents(
            contents,
            pos,
            sense_base,
            subentries,
            others,
            gloss_template_args,
            added,
        )

    def process_gloss_contents(
        contents: list[Union[str, WikiNode]],
        pos: str,
        sense_base: SenseData,
        subentries: list[WikiNode] = [],
        others: list[WikiNode] = [],
        gloss_template_args: Set[str] = set(),
        added: bool = False,
    ) -> bool:
        def sense_template_fn(
            name: str, ht: TemplateArgs, is_gloss: bool = False
        ) -> Optional[str]:
            # print(f"sense_template_fn: {name}, {ht}")
            if name in wikipedia_templates:
                # parse_wikipedia_template(wxr, pos_data, ht)
                return None
            if is_panel_template(wxr, name):
                return ""
            if name in ("defdate",):
                return ""
            if name == "senseid":
                langid = clean_node(wxr, None, ht.get(1, ()))
                arg = clean_node(wxr, sense_base, ht.get(2, ()))
                if re.match(r"Q\d+$", arg):
                    data_append(sense_base, "wikidata", arg)
                data_append(sense_base, "senseid", langid + ":" + arg)
            if name in sense_linkage_templates:
                # print(f"SENSE_TEMPLATE_FN: {name}")
                parse_sense_linkage(wxr, sense_base, name, ht)
                return ""
            if name == "†" or name == "zh-obsolete":
                data_append(sense_base, "tags", "obsolete")
                return ""
            if name in {
                "ux",
                "uxi",
                "usex",
                "afex",
                "zh-x",
                "prefixusex",
                "ko-usex",
                "ko-x",
                "hi-x",
                "ja-usex-inline",
                "ja-x",
                "quotei",
                "zh-x",
                "he-x",
                "hi-x",
                "km-x",
                "ne-x",
                "shn-x",
                "th-x",
                "ur-x",
            }:
                # Usage examples are captured separately below.  We don't
                # want to expand them into glosses even when unusual coding
                # is used in the entry.
                # These templates may slip through inside another item, but
                # currently we're separating out example entries (..#:)
                # well enough that there seems to very little contamination.
                if is_gloss:
                    wxr.wtp.warning(
                        "Example template is used for gloss text",
                        sortid="extractor.en.page.sense_template_fn/1415",
                    )
                else:
                    return ""
            if name == "w":
                if ht.get(2) == "Wp":
                    return ""
            for k, v in ht.items():
                v = v.strip()
                if v and "<" not in v:
                    gloss_template_args.add(v)
            return None

        def extract_link_texts(item: GeneralNode) -> None:
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
                v = item.largs[-1]
                if (
                    isinstance(v, list)
                    and len(v) == 1
                    and isinstance(v[0], str)
                ):
                    gloss_template_args.add(v[0].strip())
            for x in item.children:
                extract_link_texts(x)

        extract_link_texts(contents)

        # get the raw text of non-list contents of this node, and other stuff
        # like tag and category data added to sense_base
        # cast = no-op type-setter for the type-checker
        partial_template_fn = cast(
            TemplateFnCallable,
            partial(sense_template_fn, is_gloss=True),
        )
        rawgloss = clean_node(
            wxr,
            sense_base,
            contents,
            template_fn=partial_template_fn,
            collect_links=True,
        )

        if not rawgloss:
            return False

        # remove manually typed ordered list text at the start("1. ")
        rawgloss = re.sub(r"^\d+\.\s+", "", rawgloss)

        # get stuff like synonyms and categories from "others",
        # maybe examples and quotations
        clean_node(wxr, sense_base, others, template_fn=sense_template_fn)

        # Generate no gloss for translation hub pages, but add the
        # "translation-hub" tag for them
        if rawgloss == "(This entry is a translation hub.)":
            data_append(sense_data, "tags", "translation-hub")
            return push_sense()

        # Remove certain substrings specific to outer glosses
        strip_ends = [", particularly:"]
        for x in strip_ends:
            if rawgloss.endswith(x):
                rawgloss = rawgloss[: -len(x)]
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

        if rawgloss and rawgloss not in sense_base.get("raw_glosses", ()):
            data_append(sense_base, "raw_glosses", subglosses[1])
        m = re.match(r"\(([^()]+)\):?\s*", rawgloss)
        # ( ..\1.. ): ... or ( ..\1.. ) ...
        if m:
            q = m.group(1)
            rawgloss = rawgloss[m.end() :].strip()
            parse_sense_qualifier(wxr, q, sense_base)
        if rawgloss == "A pejorative:":
            data_append(sense_base, "tags", "pejorative")
            rawgloss = ""
        elif rawgloss == "Short forms.":
            data_append(sense_base, "tags", "abbreviation")
            rawgloss = ""
        elif rawgloss == "Technical or specialized senses.":
            rawgloss = ""
        elif rawgloss.startswith("inflection of "):
            data_append(sense_base, "tags", "form-of")
        if rawgloss:
            data_append(sense_base, "glosses", rawgloss)
            if rawgloss in ("A person:",):
                data_append(sense_base, "tags", "g-person")

        # The main recursive call (except for the exceptions at the
        # start of this function).
        for sublist in subentries:
            if not (
                isinstance(sublist, WikiNode) and sublist.kind == NodeKind.LIST
            ):
                wxr.wtp.debug(
                    f"'{repr(rawgloss[:20])}.' gloss has `subentries`"
                    f"with items that are not LISTs",
                    sortid="page/1511/20230119",
                )
                continue
            for item in sublist.children:
                if not (
                    isinstance(item, WikiNode)
                    and item.kind == NodeKind.LIST_ITEM
                ):
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
        if wxr.config.capture_examples:
            examples = extract_examples(others, sense_base)

        # push_sense() succeeded somewhere down-river, so skip this level
        if added:
            if examples:
                # this higher-up gloss has examples that we do not want to skip
                wxr.wtp.debug(
                    "'{}[...]' gloss has examples we want to keep, "
                    "but there are subglosses.".format(repr(rawgloss[:30])),
                    sortid="page/1498/20230118",
                )
            else:
                return True

        # Some entries, e.g., "iacebam", have weird sentences in quotes
        # after the gloss, but these sentences don't seem to be intended
        # as glosses.  Skip them.
        subglosses = list(
            gl
            for gl in subglosses
            if gl.strip() and not re.match(r'\s*(\([^)]*\)\s*)?"[^"]*"\s*$', gl)
        )

        if len(subglosses) > 1 and "form_of" not in sense_base:
            gl = subglosses[0].strip()
            if gl.endswith(":"):
                gl = gl[:-1].strip()
            parsed = parse_alt_or_inflection_of(wxr, gl, gloss_template_args)
            if parsed is not None:
                infl_tags, infl_dts = parsed
                if infl_dts and "form-of" in infl_tags and len(infl_tags) == 1:
                    # Interpret others as a particular form under
                    # "inflection of"
                    data_extend(sense_base, "tags", infl_tags)
                    data_extend(sense_base, "form_of", infl_dts)
                    subglosses = subglosses[1:]
                elif not infl_dts:
                    data_extend(sense_base, "tags", infl_tags)
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
            # if gloss not in sense_data.get("raw_glosses", ()):
            #     data_append(sense_data, "raw_glosses", gloss)
            if gloss_i == 0 and examples:
                # In a multi-line gloss, associate examples
                # with only one of them.
                # XXX or you could use gloss_i == len(subglosses)
                # to associate examples with the *last* one.
                data_extend(sense_data, "examples", examples)
            # If the gloss starts with †, mark as obsolete
            if gloss.startswith("^†"):
                data_append(sense_data, "tags", "obsolete")
                gloss = gloss[2:].strip()
            elif gloss.startswith("^‡"):
                data_extend(sense_data, "tags", ["obsolete", "historical"])
                gloss = gloss[2:].strip()
            # Copy data for all senses to this sense
            for k, v in sense_base.items():
                if isinstance(v, (list, tuple)):
                    if k != "tags":
                        # Tags handled below (countable/uncountable special)
                        data_extend(sense_data, k, v)
                else:
                    assert k not in ("tags", "categories", "topics")
                    sense_data[k] = v  # type:ignore[literal-required]
            # Parse the gloss for this particular sense
            m = re.match(r"^\((([^()]|\([^()]*\))*)\):?\s*", gloss)
            # (...): ... or (...(...)...): ...
            if m:
                parse_sense_qualifier(wxr, m.group(1), sense_data)
                gloss = gloss[m.end() :].strip()

            # Remove common suffix "[from 14th c.]" and similar
            gloss = re.sub(r"\s\[[^]]*\]\s*$", "", gloss)

            # Check to make sure we don't have unhandled list items in gloss
            ofs = max(gloss.find("#"), gloss.find("* "))
            if ofs > 10 and "(#)" not in gloss:
                wxr.wtp.debug(
                    "gloss may contain unhandled list items: {}".format(gloss),
                    sortid="page/1412",
                )
            elif "\n" in gloss:
                wxr.wtp.debug(
                    "gloss contains newline: {}".format(gloss),
                    sortid="page/1416",
                )

            # Kludge, some glosses have a comma after initial qualifiers in
            # parentheses
            if gloss.startswith((",", ":")):
                gloss = gloss[1:]
            gloss = gloss.strip()
            if gloss.endswith(":"):
                gloss = gloss[:-1].strip()
            if gloss.startswith("N. of "):
                gloss = "Name of " + gloss[6:]
            if gloss.startswith("†"):
                data_append(sense_data, "tags", "obsolete")
                gloss = gloss[1:]
            elif gloss.startswith("^†"):
                data_append(sense_data, "tags", "obsolete")
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
                    data_append(sense_data, "tags", tag)
            if countability_tags:
                if (
                    "countable" not in sense_tags
                    and "uncountable" not in sense_tags
                ):
                    data_extend(sense_data, "tags", countability_tags)

            # If outer gloss specifies a form-of ("inflection of", see
            # aquamarine/German), try to parse the inner glosses as
            # tags for an inflected form.
            if "form-of" in sense_base.get("tags", ()):
                parsed = parse_alt_or_inflection_of(
                    wxr, gloss, gloss_template_args
                )
                if parsed is not None:
                    infl_tags, infl_dts = parsed
                    if not infl_dts and infl_tags:
                        # Interpret as a particular form under "inflection of"
                        data_extend(sense_data, "tags", infl_tags)

            if not gloss:
                data_append(sense_data, "tags", "empty-gloss")
            elif gloss != "-" and gloss not in sense_data.get("glosses", []):
                # Add the gloss for the sense.
                data_append(sense_data, "glosses", gloss)

            # Kludge: there are cases (e.g., etc./Swedish) where there are
            # two abbreviations in the same sense, both generated by the
            # {{abbreviation of|...}} template.  Handle these with some magic.
            position = 0
            split_glosses = []
            for m in re.finditer(r"Abbreviation of ", gloss):
                if m.start() != position:
                    split_glosses.append(gloss[position : m.start()])
                    position = m.start()
            split_glosses.append(gloss[position:])
            for gloss in split_glosses:
                # Check if this gloss describes an alt-of or inflection-of
                if (
                    lang_code != "en"
                    and " " not in gloss
                    and distw([word], gloss) < 0.3
                ):
                    # Don't try to parse gloss if it is one word
                    # that is close to the word itself for non-English words
                    # (probable translations of a tag/form name)
                    continue
                parsed = parse_alt_or_inflection_of(
                    wxr, gloss, gloss_template_args
                )
                if parsed is None:
                    continue
                tags, dts = parsed
                if not dts and tags:
                    data_extend(sense_data, "tags", tags)
                    continue
                for dt in dts:
                    ftags = list(tag for tag in tags if tag != "form-of")
                    if "alt-of" in tags:
                        data_extend(sense_data, "tags", ftags)
                        data_append(sense_data, "alt_of", dt)
                    elif "compound-of" in tags:
                        data_extend(sense_data, "tags", ftags)
                        data_append(sense_data, "compound_of", dt)
                    elif "synonym-of" in tags:
                        data_extend(dt, "tags", ftags)
                        data_append(sense_data, "synonyms", dt)
                    elif tags and dt.get("word", "").startswith("of "):
                        dt["word"] = dt["word"][3:]
                        data_append(sense_data, "tags", "form-of")
                        data_extend(sense_data, "tags", ftags)
                        data_append(sense_data, "form_of", dt)
                    elif "form-of" in tags:
                        data_extend(sense_data, "tags", tags)
                        data_append(sense_data, "form_of", dt)

        if len(sense_data) == 0:
            if len(sense_base.get("tags", [])) == 0:
                del sense_base["tags"]
            sense_data.update(sense_base)
        if push_sense():
            # push_sense succeded in adding a sense to pos_data
            added = True
            # print("PARSE_SENSE DONE:", pos_datas[-1])
        return added

    def parse_inflection(
        node: WikiNode, section: str, pos: Optional[str]
    ) -> None:
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
            wxr.wtp.debug(
                "inflection table outside part-of-speech", sortid="page/1812"
            )
            return

        def inflection_template_fn(
            name: str, ht: TemplateArgs
        ) -> Optional[str]:
            # print("decl_conj_template_fn", name, ht)
            if is_panel_template(wxr, name):
                return ""
            if name in ("is-u-mutation",):
                # These are not to be captured as an exception to the
                # generic code below
                return None
            m = re.search(
                r"-(conj|decl|ndecl|adecl|infl|conjugation|"
                r"declension|inflection|mut|mutation)($|-)",
                name,
            )
            if m:
                args_ht = clean_template_args(wxr, ht)
                dt = {"name": name, "args": args_ht}
                data_append(pos_data, "inflection_templates", dt)

            return None

        # Convert the subtree back to Wikitext, then expand all and parse,
        # capturing templates in the process
        text = wxr.wtp.node_to_wikitext(node.children)

        # Split text into separate sections for each to-level template
        brace_matches = re.split("({{+|}}+)", text)  # ["{{", "template", "}}"]
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
            tsection: list[str] = []
            after_templates = False  # kludge to keep any text
            # before first template
            # with the first template;
            # otherwise, text
            # goes with preceding template
            for m in brace_matches:
                if m.startswith("{{"):
                    if template_nesting == 0 and after_templates:
                        template_sections.append(tsection)
                        tsection = []
                        # start new section
                    after_templates = True
                    template_nesting += len(m)
                    tsection.append(m)
                elif m.startswith("}}"):
                    template_nesting -= len(m)
                    if template_nesting < 0:
                        wxr.wtp.error(
                            "Negatively nested braces, "
                            "couldn't split inflection templates, "
                            "{}/{} section {}".format(word, language, section),
                            sortid="page/1871",
                        )
                        template_sections = []  # use whole text
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
            wxr.wtp.error(
                "Template nesting error: "
                "template_nesting = {} "
                "couldn't split inflection templates, "
                "{}/{} section {}".format(
                    template_nesting, word, language, section
                ),
                sortid="page/1896",
            )
            texts = [text]
        for text in texts:
            tree = wxr.wtp.parse(
                text, expand_all=True, template_fn=inflection_template_fn
            )

            # Parse inflection tables from the section.  The data is stored
            # under "forms".
            if wxr.config.capture_inflections:
                tablecontext = None
                m = re.search(r"{{([^}{|]+)\|?", text)
                if m:
                    template_name = m.group(1)
                    tablecontext = TableContext(template_name)

                parse_inflection_section(
                    wxr,
                    pos_data,
                    word,
                    language,
                    pos,
                    section,
                    tree,
                    tablecontext=tablecontext,
                )

    def get_subpage_section(
        title: str, subtitle: str, seq: Union[list[str], tuple[str, ...]]
    ) -> Optional[Union[WikiNode, str]]:
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
        subpage_content = wxr.wtp.get_page_body(subpage_title, 0)
        if subpage_content is None:
            wxr.wtp.error(
                "/translations not found despite "
                "{{see translation subpage|...}}",
                sortid="page/1934",
            )
            return None

        def recurse(
            node: Union[str, WikiNode], seq: Union[list[str], tuple[str, ...]]
        ) -> Optional[Union[str, WikiNode]]:
            # print(f"seq: {seq}")
            if not seq:
                return node
            if not isinstance(node, WikiNode):
                return None
            # print(f"node.kind: {node.kind}")
            if node.kind in LEVEL_KINDS:
                t = clean_node(wxr, None, node.largs[0])
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

        tree = wxr.wtp.parse(
            subpage_content,
            pre_expand=True,
            additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
            do_not_pre_expand=DO_NOT_PRE_EXPAND_TEMPLATES,
        )
        assert tree.kind == NodeKind.ROOT
        ret = recurse(tree, seq)
        if ret is None:
            wxr.wtp.debug(
                "Failed to find subpage section {}/{} seq {}".format(
                    title, subtitle, seq
                ),
                sortid="page/1963",
            )
        return ret

    def parse_linkage(
        data: WordData, field: str, linkagenode: WikiNode
    ) -> None:
        assert isinstance(data, dict)
        assert isinstance(field, str)
        assert isinstance(linkagenode, WikiNode)
        # if field == "synonyms":
        #     print("field", field)
        #     print("data", data)
        #     print("children:")
        #     print(linkagenode.children)
        if not wxr.config.capture_linkages:
            return
        have_panel_template = False
        toplevel_text = []
        next_navframe_sense = None  # Used for "(sense):" before NavFrame

        def parse_linkage_item(
            contents: list[Union[str, WikiNode]],
            field: str,
            sense: Optional[str] = None,
        ):
            assert isinstance(contents, (list, tuple))
            assert isinstance(field, str)
            assert sense is None or isinstance(sense, str)

            # print("PARSE_LINKAGE_ITEM: {} ({}): {}"
            #    .format(field, sense, contents))

            parts: list[str] = []
            ruby: list[tuple[str, str]] = []
            urls: list[str] = []
            # data about link text; this is used to skip splitting on
            # linkage text items that contain stuff like commas; for
            # example "Hunde, die bellen, beißen nicht" in article
            # beißen is split into "Hunde", "die bellen" etc.
            # We take that link text and use it, eventually,
            # in split_at_comma_semi to skip splitting on those
            # commas.
            links_that_should_not_be_split: list[str] = []

            def item_recurse(
                contents: list[Union[str, WikiNode]], italic=False
            ) -> None:
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
                    # print("ITEM_RECURSE KIND:", kind,
                    #        node.sarg if node.sarg else node.largs)
                    if kind == NodeKind.LIST:
                        if parts:
                            sense1: Optional[str]
                            sense1 = clean_node(wxr, None, parts)
                            if sense1.endswith(":"):
                                sense1 = sense1[:-1].strip()
                            if sense1.startswith("(") and sense1.endswith(")"):
                                sense1 = sense1[1:-1].strip()
                            if sense1.lower() == TRANSLATIONS_TITLE:
                                sense1 = None
                            # print("linkage item_recurse LIST sense1:", sense1)
                            parse_linkage_recurse(
                                node.children, field, sense=sense1 or sense
                            )
                            parts = []
                        else:
                            parse_linkage_recurse(node.children, field, sense)
                    elif kind in (
                        NodeKind.TABLE,
                        NodeKind.TABLE_ROW,
                        NodeKind.TABLE_CELL,
                    ):
                        parse_linkage_recurse(node.children, field, sense)
                    elif kind in (
                        NodeKind.TABLE_HEADER_CELL,
                        NodeKind.TABLE_CAPTION,
                    ):
                        continue
                    elif kind == NodeKind.HTML:
                        classes = (node.attrs.get("class") or "").split()
                        if node.sarg in ("gallery", "ref", "cite", "caption"):
                            continue
                        elif node.sarg == "ruby":
                            rb = parse_ruby(wxr, node)
                            if rb:
                                ruby.append(rb)
                                parts.append(rb[0])
                            continue
                        elif node.sarg == "math":
                            parts.append(clean_node(wxr, None, node))
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
                        if isinstance(node.largs[0][0], str):
                            v1 = node.largs[0][0].strip().lower()
                            if v1.startswith(
                                ns_title_prefix_tuple(wxr, "Category", True)
                                + ns_title_prefix_tuple(wxr, "File", True)
                            ):
                                ignore = True
                            if not ignore:
                                v = node.largs[-1]
                                if (
                                    len(node.largs) == 1
                                    and len(v) > 0
                                    and isinstance(v[0], str)
                                    and v[0][0] == ":"
                                ):
                                    v = [v[0][1:]] + list(v[1:])  # type:ignore
                                if (
                                    isinstance(v[0], str)
                                    and v[0].isalnum() == False
                                ):
                                    links_that_should_not_be_split.append(
                                        "".join(v[0])
                                    )  # type: ignore
                                item_recurse(v, italic=italic)
                    elif kind == NodeKind.URL:
                        if len(node.largs) < 2 and node.largs:
                            # Naked url captured
                            urls.extend(node.largs[-1])  # type:ignore[arg-type]
                            continue
                        if len(node.largs) == 2:
                            # Url from link with text
                            urls.append(node.largs[0][-1])  # type:ignore[arg-type]
                        # print(f"{node.largs=!r}")
                        # print("linkage recurse URL {}".format(node))
                        item_recurse(node.largs[-1], italic=italic)
                    elif kind in (NodeKind.PREFORMATTED, NodeKind.BOLD):
                        item_recurse(node.children, italic=italic)
                    else:
                        wxr.wtp.debug(
                            "linkage item_recurse unhandled {}: {}".format(
                                node.kind, node
                            ),
                            sortid="page/2073",
                        )

            # print("LINKAGE CONTENTS BEFORE ITEM_RECURSE: {!r}"
            #       .format(contents))

            item_recurse(contents)
            item = clean_node(wxr, None, parts)
            # print("LINKAGE ITEM CONTENTS:", parts)
            # print("CLEANED ITEM: {!r}".format(item))
            # print(f"URLS {urls=!r}")

            return parse_linkage_item_text(
                wxr,
                word,
                data,
                field,
                item,
                sense,
                ruby,
                pos_datas,
                is_reconstruction,
                urls or None,
                links_that_should_not_be_split or None,
            )

        def parse_linkage_recurse(
            contents: list[Union[WikiNode, str]],
            field: str,
            sense: Optional[str],
        ) -> None:
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
                elif kind in (
                    NodeKind.TABLE_CAPTION,
                    NodeKind.TABLE_HEADER_CELL,
                    NodeKind.PREFORMATTED,
                    NodeKind.BOLD,
                ):
                    continue
                elif kind == NodeKind.HTML:
                    # Recurse to process inside the HTML for most tags
                    if node.sarg in ("gallery", "ref", "cite", "caption"):
                        continue
                    classes = (node.attrs.get("class") or "").split()
                    if node.sarg == "li":
                        # duplicates code from if kind == NodeKind.LIST_ITEM ⇑
                        v = parse_linkage_item(node.children, field, sense)
                        if v:
                            next_navframe_sense = v
                    elif "qualifier-content" in classes:
                        sense1 = clean_node(wxr, None, node.children)
                        if sense1.endswith(":"):
                            sense1 = sense1[:-1].strip()
                        if sense and sense1:
                            wxr.wtp.debug(
                                "linkage qualifier-content on multiple "
                                "levels: {!r} and {!r}".format(sense, sense1),
                                sortid="page/2170",
                            )
                        parse_linkage_recurse(node.children, field, sense1)
                    elif "NavFrame" in classes:
                        # NavFrame uses previously assigned next_navframe_sense
                        # (from a "(sense):" item) and clears it afterwards
                        parse_linkage_recurse(
                            node.children, field, sense or next_navframe_sense
                        )
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
                    parse_linkage_recurse(node.largs[-1], field, sense)
                else:
                    wxr.wtp.debug(
                        "parse_linkage_recurse unhandled {}: {}".format(
                            kind, node
                        ),
                        sortid="page/2196",
                    )

        def linkage_template_fn1(name: str, ht: TemplateArgs) -> Optional[str]:
            nonlocal have_panel_template
            if is_panel_template(wxr, name):
                have_panel_template = True
                return ""
            return None

        def parse_zh_synonyms(
            parsed: list[Union[WikiNode, str]],
            data: list[LinkageData],
            hdrs: list[str],
            root_word: str,
        ) -> None:
            """Parses Chinese dialectal synonyms tables"""
            for item in parsed:
                if isinstance(item, WikiNode):
                    if item.kind == NodeKind.TABLE_ROW:
                        cleaned = clean_node(wxr, None, item.children)
                        # print("cleaned:", repr(cleaned))
                        if any(
                            [
                                "Variety" in cleaned,
                                "Location" in cleaned,
                                "Words" in cleaned,
                            ]
                        ):
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
                                            print(
                                                f"MISSING ZH SYNONYM TAG for root {root_word}, word {words}: {tag}"
                                            )
                                            sys.stdout.flush()

                            for word in words:
                                data.append(
                                    {"word": word.strip(), "tags": tags}
                                )
                    elif item.kind == NodeKind.HTML:
                        cleaned = clean_node(wxr, None, item.children)
                        if "Synonyms of" in cleaned:
                            cleaned = cleaned.replace("Synonyms of ", "")
                            root_word = cleaned
                        parse_zh_synonyms(item.children, data, hdrs, root_word)
                    else:
                        parse_zh_synonyms(item.children, data, hdrs, root_word)

        def parse_zh_synonyms_list(
            parsed: list[Union[WikiNode, str]],
            data: list[LinkageData],
            hdrs: list[str],
            root_word: str,
        ) -> None:
            """Parses Chinese dialectal synonyms tables (list format)"""
            for item in parsed:
                if isinstance(item, WikiNode):
                    if item.kind == NodeKind.LIST_ITEM:
                        cleaned = clean_node(wxr, None, item.children)
                        # print("cleaned:", repr(cleaned))
                        if any(
                            [
                                "Variety" in cleaned,
                                "Location" in cleaned,
                                "Words" in cleaned,
                            ]
                        ):
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
                                elif (
                                    classify_desc(tag) == "romanization"
                                    and roman is None
                                ):
                                    roman = tag
                                else:
                                    print(
                                        f"MISSING ZH SYNONYM TAG (possibly pinyin) - root {root_word}, word {words}: {tag}"
                                    )
                                    sys.stdout.flush()

                            for word in words:
                                dt: LinkageData = {"word": word.strip()}
                                if tags:
                                    dt["tags"] = tags
                                if roman is not None:
                                    dt["roman"] = roman
                                data.append(dt)
                    elif item.kind == NodeKind.HTML:
                        cleaned = clean_node(wxr, None, item.children)
                        if cleaned.find("Synonyms of") >= 0:
                            cleaned = cleaned.replace("Synonyms of ", "")
                            root_word = cleaned
                        parse_zh_synonyms_list(
                            item.children, data, hdrs, root_word
                        )
                    else:
                        parse_zh_synonyms_list(
                            item.children, data, hdrs, root_word
                        )

        def contains_kind(
            children: list[Union[WikiNode, str]], nodekind: NodeKind
        ) -> bool:
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
        text = wxr.wtp.node_to_wikitext(linkagenode.children)
        parsed = wxr.wtp.parse(
            text, expand_all=True, template_fn=linkage_template_fn1
        )
        if field == "synonyms" and lang_code == "zh":
            synonyms: list[LinkageData] = []
            if contains_kind(parsed.children, NodeKind.LIST):
                parse_zh_synonyms_list(parsed.children, synonyms, [], "")
            else:
                parse_zh_synonyms(parsed.children, synonyms, [], "")
            # print(json.dumps(synonyms, indent=4, ensure_ascii=False))
            data_extend(data, "synonyms", synonyms)
        parse_linkage_recurse(parsed.children, field, None)
        if not data.get(field) and not have_panel_template:
            text = "".join(toplevel_text).strip()
            if "\n" not in text and "," in text and text.count(",") > 3:
                if not text.startswith("See "):
                    parse_linkage_item([text], field, None)

    def parse_translations(data: WordData, xlatnode: WikiNode) -> None:
        """Parses translations for a word.  This may also pull in translations
        from separate translation subpages."""
        assert isinstance(data, dict)
        assert isinstance(xlatnode, WikiNode)
        # print("===== PARSE_TRANSLATIONS {} {} {}"
        #   .format(wxr.wtp.title, wxr.wtp.section, wxr.wtp.subsection))
        # print("parse_translations xlatnode={}".format(xlatnode))
        if not wxr.config.capture_translations:
            return
        sense_parts: list[Union[WikiNode, str]] = []
        sense = None

        def parse_translation_item(contents, lang=None):
            nonlocal sense
            assert isinstance(contents, list)
            assert lang is None or isinstance(lang, str)
            # print("PARSE_TRANSLATION_ITEM:", contents)

            langcode = None
            if sense is None:
                sense = clean_node(wxr, data, sense_parts).strip()
                # print("sense <- clean_node: ", sense)
                idx = sense.find("See also translations at")
                if idx > 0:
                    wxr.wtp.debug(
                        "Skipping translation see also: {}".format(sense),
                        sortid="page/2361",
                    )
                    sense = sense[:idx].strip()
                if sense.endswith(":"):
                    sense = sense[:-1].strip()
                if sense.endswith("—"):
                    sense = sense[:-1].strip()
            translations_from_template = []

            def translation_item_template_fn(
                name: str, ht: TemplateArgs
            ) -> Optional[str]:
                nonlocal langcode
                # print("TRANSLATION_ITEM_TEMPLATE_FN:", name, ht)
                if is_panel_template(wxr, name):
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
                            wxr.wtp.debug(
                                "inconsistent language codes {} vs "
                                "{} in translation item: {!r} {}".format(
                                    langcode, code, name, ht
                                ),
                                sortid="page/2386",
                            )
                        langcode = code
                    tr = ht.get(2)
                    if tr:
                        tr = clean_node(wxr, None, [tr])
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
                    wxr.wtp.error(
                        "UNIMPLEMENTED trans-see template", sortid="page/2405"
                    )
                    return ""
                if name.endswith("-top"):
                    return ""
                if name.endswith("-bottom"):
                    return ""
                if name.endswith("-mid"):
                    return ""
                # wxr.wtp.debug("UNHANDLED TRANSLATION ITEM TEMPLATE: {!r}"
                #             .format(name),
                #          sortid="page/2414")
                return None

            sublists = list(
                x
                for x in contents
                if isinstance(x, WikiNode) and x.kind == NodeKind.LIST
            )
            contents = list(
                x
                for x in contents
                if not isinstance(x, WikiNode) or x.kind != NodeKind.LIST
            )

            item = clean_node(
                wxr, data, contents, template_fn=translation_item_template_fn
            )
            # print("    TRANSLATION ITEM: {!r}  [{}]".format(item, sense))

            # Parse the translation item.
            if item:
                lang = parse_translation_item_text(
                    wxr,
                    word,
                    data,
                    item,
                    sense,
                    pos_datas,
                    lang,
                    langcode,
                    translations_from_template,
                    is_reconstruction,
                )

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

        def parse_translation_template(node: WikiNode) -> None:
            assert isinstance(node, WikiNode)

            def template_fn(name: str, ht: TemplateArgs) -> Optional[str]:
                nonlocal sense_parts
                nonlocal sense
                if is_panel_template(wxr, name):
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
                    sub = ht.get(1, "")
                    if sub:
                        m = re.match(
                            r"\s*(([^:\d]*)\s*\d*)\s*:\s*([^:]*)\s*", sub
                        )
                    else:
                        m = None
                    etym = ""
                    etym_numbered = ""
                    pos = ""
                    if m:
                        etym_numbered = m.group(1)
                        etym = m.group(2)
                        pos = m.group(3)
                    if not sub:
                        wxr.wtp.debug(
                            "no part-of-speech in "
                            "{{see translation subpage|...}}, "
                            "defaulting to just wxr.wtp.section "
                            "(= language)",
                            sortid="page/2468",
                        )
                        # seq sent to get_subpage_section without sub and pos
                        seq = [
                            language,
                            TRANSLATIONS_TITLE,
                        ]
                    elif (
                        m
                        and etym.lower().strip() in ETYMOLOGY_TITLES
                        and pos.lower() in POS_TITLES
                    ):
                        seq = [
                            language,
                            etym_numbered,
                            pos,
                            TRANSLATIONS_TITLE,
                        ]
                    elif sub.lower() in POS_TITLES:
                        # seq with sub but not pos
                        seq = [
                            language,
                            sub,
                            TRANSLATIONS_TITLE,
                        ]
                    else:
                        # seq with sub and pos
                        pos = wxr.wtp.subsection or "MISSING_SUBSECTION"
                        if pos.lower() not in POS_TITLES:
                            wxr.wtp.debug(
                                "unhandled see translation subpage: "
                                "language={} sub={} wxr.wtp.subsection={}".format(
                                    language, sub, wxr.wtp.subsection
                                ),
                                sortid="page/2478",
                            )
                        seq = [language, sub, pos, TRANSLATIONS_TITLE]
                    subnode = get_subpage_section(
                        wxr.wtp.title or "MISSING_TITLE",
                        TRANSLATIONS_TITLE,
                        seq,
                    )
                    if subnode is not None and isinstance(subnode, WikiNode):
                        parse_translations(data, subnode)
                    else:
                        # Failed to find the normal subpage section
                        seq = [TRANSLATIONS_TITLE]
                        subnode = get_subpage_section(
                            wxr.wtp.title or "MISSING_TITLE",
                            TRANSLATIONS_TITLE,
                            seq,
                        )
                        if subnode is not None and isinstance(
                            subnode, WikiNode
                        ):
                            parse_translations(data, subnode)
                    return ""
                if name in (
                    "c",
                    "C",
                    "categorize",
                    "cat",
                    "catlangname",
                    "topics",
                    "top",
                    "qualifier",
                    "cln",
                ):
                    # These are expanded in the default way
                    return None
                if name in ("trans-top",):
                    # XXX capture id from trans-top?  Capture sense here
                    # instead of trying to parse it from expanded content?
                    if ht.get(1):
                        sense_parts = []
                        sense = ht.get(1)
                    else:
                        sense_parts = []
                        sense = None
                    return None
                if name in (
                    "trans-bottom",
                    "trans-mid",
                    "checktrans-mid",
                    "checktrans-bottom",
                ):
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
                wxr.wtp.error(
                    "UNIMPLEMENTED parse_translation_template: {} {}".format(
                        name, ht
                    ),
                    sortid="page/2517",
                )
                return ""

            wxr.wtp.expand(
                wxr.wtp.node_to_wikitext(node), template_fn=template_fn
            )

        def parse_translation_recurse(xlatnode: WikiNode) -> None:
            nonlocal sense
            nonlocal sense_parts
            for node in xlatnode.children:
                # print(node)
                if isinstance(node, str):
                    if sense:
                        if not node.isspace():
                            wxr.wtp.debug(
                                "skipping string in the middle of "
                                "translations: {}".format(node),
                                sortid="page/2530",
                            )
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
                        if item.sarg == ":":
                            continue
                        parse_translation_item(item.children)
                elif kind == NodeKind.LIST_ITEM and node.sarg == ":":
                    # Silently skip list items that are just indented; these
                    # are used for text between translations, such as indicating
                    # translations that need to be checked.
                    pass
                elif kind == NodeKind.TEMPLATE:
                    parse_translation_template(node)
                elif kind in (
                    NodeKind.TABLE,
                    NodeKind.TABLE_ROW,
                    NodeKind.TABLE_CELL,
                ):
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
                elif kind == NodeKind.PREFORMATTED:
                    print("parse_translation_recurse: PREFORMATTED:", node)
                elif kind == NodeKind.LINK:
                    arg0 = node.largs[0]
                    # Kludge: I've seen occasional normal links to translation
                    # subpages from main pages (e.g., language/English/Noun
                    # in July 2021) instead of the normal
                    # {{see translation subpage|...}} template.  This should
                    # handle them.  Note: must be careful not to read other
                    # links, particularly things like in "human being":
                    # "a human being -- see [[man/translations]]" (group title)
                    if (
                        isinstance(arg0, (list, tuple))
                        and arg0
                        and isinstance(arg0[0], str)
                        and arg0[0].endswith("/" + TRANSLATIONS_TITLE)
                        and arg0[0][: -(1 + len(TRANSLATIONS_TITLE))]
                        == wxr.wtp.title
                    ):
                        wxr.wtp.debug(
                            "translations subpage link found on main "
                            "page instead "
                            "of normal {{see translation subpage|...}}",
                            sortid="page/2595",
                        )
                        sub = wxr.wtp.subsection or "MISSING_SUBSECTION"
                        if sub.lower() in POS_TITLES:
                            seq = [
                                language,
                                sub,
                                TRANSLATIONS_TITLE,
                            ]
                            subnode = get_subpage_section(
                                wxr.wtp.title,
                                TRANSLATIONS_TITLE,
                                seq,
                            )
                            if subnode is not None and isinstance(
                                subnode, WikiNode
                            ):
                                parse_translations(data, subnode)
                        else:
                            wxr.wtp.error(
                                "/translations link outside part-of-speech"
                            )

                    if (
                        len(arg0) >= 1
                        and isinstance(arg0[0], str)
                        and not arg0[0].lower().startswith("category:")
                    ):
                        for x in node.largs[-1]:
                            if isinstance(x, str):
                                sense_parts.append(x)
                            else:
                                parse_translation_recurse(x)
                elif not sense:
                    sense_parts.append(node)
                else:
                    wxr.wtp.debug(
                        "skipping text between translation items/senses: "
                        "{}".format(node),
                        sortid="page/2621",
                    )

        # Main code of parse_translation().  We want ``sense`` to be assigned
        # regardless of recursion levels, and thus the code is structured
        # to define at this level and recurse in parse_translation_recurse().
        parse_translation_recurse(xlatnode)

    def parse_etymology(data: WordData, node: WikiNode) -> None:
        """Parses an etymology section."""
        assert isinstance(data, dict)
        assert isinstance(node, WikiNode)

        templates = []

        # Counter for preventing the capture of etymology templates
        # when we are inside templates that we want to ignore (i.e.,
        # not capture).
        ignore_count = 0

        def etym_template_fn(name: str, ht: TemplateArgs) -> Optional[str]:
            nonlocal ignore_count
            if is_panel_template(wxr, name):
                return ""
            if re.match(ignored_etymology_templates_re, name):
                ignore_count += 1
            return None

        # CONTINUE_HERE

        def etym_post_template_fn(name, ht, expansion):
            nonlocal ignore_count
            if name in wikipedia_templates:
                parse_wikipedia_template(wxr, data, ht)
                return None
            if re.match(ignored_etymology_templates_re, name):
                ignore_count -= 1
                return None
            if ignore_count == 0:
                ht = clean_template_args(wxr, ht)
                expansion = clean_node(wxr, None, expansion)
                templates.append(
                    {"name": name, "args": ht, "expansion": expansion}
                )
            return None

        # Remove any subsections
        contents = list(
            x
            for x in node.children
            if not isinstance(x, WikiNode) or x.kind not in LEVEL_KINDS
        )
        # Convert to text, also capturing templates using post_template_fn
        text = clean_node(
            wxr,
            None,
            contents,
            template_fn=etym_template_fn,
            post_template_fn=etym_post_template_fn,
        )
        # Save the collected information.
        if text:
            data["etymology_text"] = text
        if templates:
            # Some etymology templates, like Template:root do not generate
            # text, so they should be added here. Elsewhere, we check
            # for Template:root and add some text to the expansion to please
            # the validation.
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

        # Most templates that are not in a LIST should be ignored as they only
        # add formatting, like "desc-top", "der-top3", etc. Any template in
        # unignored_non_list_templates actually contains relevant descendant
        # info. E.g. "CJKV" is often the only line at all in descendants
        # sections in many Chinese/Japanese/Korean/Vietnamese pages, but would
        # be skipped if we didn't handle it specially as it is not part of a
        # LIST, and additionally is in panel_templates. There are probably more
        # such templates that should be added to this...
        unignored_non_list_templates = ["CJKV"]

        def process_list_item_children(sarg, children):
            assert isinstance(sarg, str)
            assert isinstance(children, list)
            # The descendants section is a hierarchical bulleted listed. sarg is
            # usually some number of "*" characters indicating the level of
            # indentation of the line, e.g. "***" indicates the line will be
            # thrice-indented. A bare ";" is used to indicate a subtitle-like
            # line with no indentation. ":" at the end of one or more "*"s is
            # used to indicate that the bullet will not be displayed.
            item_data = {"depth": sarg.count("*")}
            templates = []
            is_derived = False

            # Counter for preventing the capture of templates when we are inside
            # templates that we want to ignore (i.e., not capture).
            ignore_count = 0

            def desc_template_fn(name, ht):
                nonlocal ignore_count
                if (
                    is_panel_template(wxr, name)
                    and name not in unignored_non_list_templates
                ):
                    return ""
                if re.match(ignored_descendants_templates_re, name):
                    ignore_count += 1

            def desc_post_template_fn(name, ht, expansion):
                nonlocal ignore_count
                if name in wikipedia_templates:
                    parse_wikipedia_template(wxr, data, ht)
                    return None
                if re.match(ignored_descendants_templates_re, name):
                    ignore_count -= 1
                    return None
                if ignore_count == 0:
                    ht = clean_template_args(wxr, ht)
                    nonlocal is_derived
                    # If we're in a proto-root Derived terms or Extensions section,
                    # and the current list item has a link template to a term in the
                    # same proto-language, then we tag this descendant entry with
                    # "derived"
                    is_derived = (
                        is_proto_root_derived_section
                        and (name == "l" or name == "link")
                        and ("1" in ht and ht["1"] == lang_code)
                    )
                    expansion = clean_node(wxr, None, expansion)
                    templates.append(
                        {"name": name, "args": ht, "expansion": expansion}
                    )
                return None

            text = clean_node(
                wxr,
                None,
                children,
                template_fn=desc_template_fn,
                post_template_fn=desc_post_template_fn,
            )
            item_data["templates"] = templates
            item_data["text"] = text
            if is_derived:
                item_data["tags"] = ["derived"]
            descendants.append(item_data)

        def node_children(node):
            for i, child in enumerate(node.children):
                if isinstance(child, WikiNode):
                    yield (i, child)

        def get_sublist_index(list_item):
            for i, child in node_children(list_item):
                if child.kind == NodeKind.LIST:
                    return i
            return None

        def get_descendants(node):
            """Appends the data for every list item in every list in node
            to descendants."""
            for _, c in node_children(node):
                if (
                    c.kind == NodeKind.TEMPLATE
                    and c.largs
                    and len(c.largs[0]) == 1
                    and isinstance(c.largs[0][0], str)
                    and c.largs[0][0] in unignored_non_list_templates
                ):
                    # Some Descendants sections have no wikitext list. Rather,
                    # the list is entirely generated by a single template (see
                    # e.g. the use of {{CJKV}} in Chinese entries).
                    process_list_item_children("", [c])
                elif c.kind == NodeKind.HTML:
                    # The Descendants sections for many languages feature
                    # templates that generate html to add styling (e.g. using
                    # multiple columns) to the list, so that the actual wikitext
                    # list items are found within a <div>. We look within the
                    # children of the html node for the actual list items.
                    get_descendants(c)
                elif c.kind == NodeKind.LIST:
                    get_descendants(c)
                elif c.kind == NodeKind.LIST_ITEM:
                    # If a LIST_ITEM has subitems in a sublist, usually its
                    # last child is a LIST. However, sometimes after the LIST
                    # there is one or more trailing LIST_ITEMs, like "\n" or
                    # a reference template. If there is a sublist, we discard
                    # everything after it.
                    i = get_sublist_index(c)
                    if i is not None:
                        process_list_item_children(c.sarg, c.children[:i])
                        get_descendants(c.children[i])
                    else:
                        process_list_item_children(c.sarg, c.children)

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

        redirect_list: list[str] = []  # for `zh-see` template

        def skip_template_fn(name, ht):
            """This is called for otherwise unprocessed parts of the page.
            We still expand them so that e.g. Category links get captured."""
            if name in wikipedia_templates:
                data = select_data()
                parse_wikipedia_template(wxr, data, ht)
                return None
            if is_panel_template(wxr, name):
                return ""
            return None

        for node in treenode.children:
            # print(node)
            if not isinstance(node, WikiNode):
                # print("  X{}".format(repr(node)[:40]))
                continue
            if isinstance(
                node, TemplateNode
            ) and process_soft_redirect_template(wxr, node, redirect_list):
                continue

            if node.kind not in LEVEL_KINDS:
                # XXX handle e.g. wikipedia links at the top of a language
                # XXX should at least capture "also" at top of page
                if node.kind in (
                    NodeKind.HLINE,
                    NodeKind.LIST,
                    NodeKind.LIST_ITEM,
                ):
                    continue
                # print("      UNEXPECTED: {}".format(node))
                # Clean the node to collect category links
                clean_node(wxr, etym_data, node, template_fn=skip_template_fn)
                continue
            t = clean_node(
                wxr, etym_data, node.sarg if node.sarg else node.largs
            )
            t = t.lower()
            # XXX these counts were never implemented fully, and even this
            # gets discarded: Search STATISTICS_IMPLEMENTATION
            wxr.config.section_counts[t] += 1
            # print("PROCESS_CHILDREN: T:", repr(t))
            if t in IGNORED_TITLES:
                pass
            elif t.startswith(PRONUNCIATION_TITLE):
                if t.startswith(PRONUNCIATION_TITLE + " "):
                    # Pronunciation 1, etc, are used in Chinese Glyphs,
                    # and each of them may have senses under Definition
                    push_etym()
                    wxr.wtp.start_subsection(None)
                if wxr.config.capture_pronunciation:
                    data = select_data()
                    parse_pronunciation(
                        wxr,
                        node,
                        data,
                        etym_data,
                        have_etym,
                        base_data,
                        lang_code,
                    )
            elif t.startswith(tuple(ETYMOLOGY_TITLES)):
                push_etym()
                wxr.wtp.start_subsection(None)
                if wxr.config.capture_etymologies:
                    m = re.search(r"\s(\d+)$", t)
                    if m:
                        etym_data["etymology_number"] = int(m.group(1))
                    parse_etymology(etym_data, node)
            elif t == DESCENDANTS_TITLE and wxr.config.capture_descendants:
                data = select_data()
                parse_descendants(data, node)
            elif (
                t in PROTO_ROOT_DERIVED_TITLES
                and pos == "root"
                and is_reconstruction
                and wxr.config.capture_descendants
            ):
                data = select_data()
                parse_descendants(data, node, True)
            elif t == TRANSLATIONS_TITLE:
                data = select_data()
                parse_translations(data, node)
            elif t in INFLECTION_TITLES:
                parse_inflection(node, t, pos)
            else:
                lst = t.split()
                while len(lst) > 1 and lst[-1].isdigit():
                    lst = lst[:-1]
                t_no_number = " ".join(lst).lower()
                if t_no_number in POS_TITLES:
                    push_pos()
                    dt = POS_TITLES[t_no_number]
                    pos = dt["pos"]
                    wxr.wtp.start_subsection(t)
                    if "debug" in dt:
                        wxr.wtp.debug(
                            "{} in section {}".format(dt["debug"], t),
                            sortid="page/2755",
                        )
                    if "warning" in dt:
                        wxr.wtp.warning(
                            "{} in section {}".format(dt["warning"], t),
                            sortid="page/2759",
                        )
                    if "error" in dt:
                        wxr.wtp.error(
                            "{} in section {}".format(dt["error"], t),
                            sortid="page/2763",
                        )
                    # Parse word senses for the part-of-speech
                    parse_part_of_speech(node, pos)
                    if "tags" in dt:
                        for pdata in pos_datas:
                            data_extend(pdata, "tags", dt["tags"])
                elif t_no_number in LINKAGE_TITLES:
                    rel = LINKAGE_TITLES[t_no_number]
                    data = select_data()
                    parse_linkage(data, rel, node)
                elif t_no_number == COMPOUNDS_TITLE:
                    data = select_data()
                    if wxr.config.capture_compounds:
                        parse_linkage(data, "derived", node)

            # XXX parse interesting templates also from other sections.  E.g.,
            # {{Letter|...}} in ===See also===
            # Also <gallery>

            # Recurse to children of this node, processing subtitles therein
            stack.append(t)
            process_children(node, pos)
            stack.pop()

        if len(redirect_list) > 0:
            if len(pos_data) > 0:
                pos_data["redirects"] = redirect_list
                if "pos" not in pos_data:
                    pos_data["pos"] = "soft-redirect"
            else:
                new_page_data = copy.deepcopy(base_data)
                new_page_data["redirects"] = redirect_list
                if "pos" not in new_page_data:
                    new_page_data["pos"] = "soft-redirect"
                page_datas.append(new_page_data)

    def extract_examples(others, sense_base):
        """Parses through a list of definitions and quotes to find examples.
        Returns a list of example dicts to be added to sense data. Adds
        meta-data, mostly categories, into sense_base."""
        assert isinstance(others, list)
        examples = []

        for sub in others:
            if not sub.sarg.endswith((":", "*")):
                continue
            for item in sub.children:
                if not isinstance(item, WikiNode):
                    continue
                if item.kind != NodeKind.LIST_ITEM:
                    continue
                usex_type = None

                def usex_template_fn(name, ht):
                    nonlocal usex_type
                    if is_panel_template(wxr, name):
                        return ""
                    if name in usex_templates:
                        usex_type = "example"
                    elif name in quotation_templates:
                        usex_type = "quotation"
                    for prefix in template_linkages:
                        if re.search(
                            r"(^|[-/\s]){}($|\b|[0-9])".format(prefix), name
                        ):
                            return ""
                    return None

                # bookmark
                ruby = []
                contents = item.children
                if lang_code == "ja":
                    # print(contents)
                    if (
                        contents
                        and isinstance(contents, str)
                        and re.match(r"\s*$", contents[0])
                    ):
                        contents = contents[1:]
                    exp = wxr.wtp.parse(
                        wxr.wtp.node_to_wikitext(contents),
                        # post_template_fn=head_post_template_fn,
                        expand_all=True,
                    )
                    rub, rest = extract_ruby(wxr, exp.children)
                    if rub:
                        for r in rub:
                            ruby.append(r)
                        contents = rest
                subtext = clean_node(
                    wxr, sense_base, contents, template_fn=usex_template_fn
                )
                subtext = re.sub(
                    r"\s*\(please add an English "
                    r"translation of this "
                    r"(example|usage example|quote)\)",
                    "",
                    subtext,
                ).strip()
                subtext = re.sub(r"\^\([^)]*\)", "", subtext)
                subtext = re.sub(r"\s*[―—]+$", "", subtext)
                # print("subtext:", repr(subtext))

                lines = subtext.splitlines()
                # print(lines)

                lines = list(re.sub(r"^[#:*]*", "", x).strip() for x in lines)
                lines = list(
                    x
                    for x in lines
                    if not re.match(
                        r"(Synonyms: |Antonyms: |Hyponyms: |"
                        r"Synonym: |Antonym: |Hyponym: |"
                        r"Hypernyms: |Derived terms: |"
                        r"Related terms: |"
                        r"Hypernym: |Derived term: |"
                        r"Coordinate terms:|"
                        r"Related term: |"
                        r"For more quotations using )",
                        x,
                    )
                )
                tr = ""
                ref = ""
                roman = ""
                # for line in lines:
                #     print("LINE:", repr(line))
                #     print(classify_desc(line))
                if len(lines) == 1 and lang_code != "en":
                    parts = re.split(r"\s*[―—]+\s*", lines[0])
                    if len(parts) == 2 and classify_desc(parts[1]) == "english":
                        lines = [parts[0].strip()]
                        tr = parts[1].strip()
                    elif (
                        len(parts) == 3
                        and classify_desc(parts[1])
                        in ("romanization", "english")
                        and classify_desc(parts[2]) == "english"
                    ):
                        lines = [parts[0].strip()]
                        roman = parts[1].strip()
                        tr = parts[2].strip()
                    else:
                        parts = re.split(r"\s+-\s+", lines[0])
                        if (
                            len(parts) == 2
                            and classify_desc(parts[1]) == "english"
                        ):
                            lines = [parts[0].strip()]
                            tr = parts[1].strip()
                elif len(lines) > 1:
                    if any(re.search(r"[]\d:)]\s*$", x) for x in lines[:-1]):
                        ref = []
                        for i in range(len(lines)):
                            if re.match(r"^[#*]*:+(\s*$|\s+)", lines[i]):
                                break
                            ref.append(lines[i].strip())
                            if re.search(r"[]\d:)]\s*$", lines[i]):
                                break
                        ref = " ".join(ref)
                        lines = lines[i + 1 :]
                        if (
                            lang_code != "en"
                            and len(lines) >= 2
                            and classify_desc(lines[-1]) == "english"
                        ):
                            i = len(lines) - 1
                            while (
                                i > 1
                                and classify_desc(lines[i - 1]) == "english"
                            ):
                                i -= 1
                            tr = "\n".join(lines[i:])
                            lines = lines[:i]
                        if len(lines) >= 2:
                            if classify_desc(lines[-1]) == "romanization":
                                roman = lines[-1].strip()
                                lines = lines[:-1]

                    elif lang_code == "en" and re.match(r"^[#*]*:+", lines[1]):
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
                        elif (
                            re.match(r"^[#*]*:+", lines[1])
                            and classify_desc(
                                re.sub(r"^[#*:]+\s*", "", lines[1])
                            )
                            == "english"
                        ):
                            tr = re.sub(r"^[#*:]+\s*", "", lines[1])
                            lines = [lines[0]]
                        elif cls1 == "english" and cls2 == "english":
                            # Both were classified as English, but
                            # presumably one is not.  Assume first is
                            # non-English, as that seems more common.
                            tr = lines[1]
                            lines = [lines[0]]
                    elif (
                        usex_type != "quotation"
                        and lang_code != "en"
                        and len(lines) == 3
                    ):
                        cls1 = classify_desc(lines[0])
                        cls2 = classify_desc(lines[1])
                        cls3 = classify_desc(lines[2])
                        if (
                            cls3 == "english"
                            and cls2 in ["english", "romanization"]
                            and cls1 != "english"
                        ):
                            tr = lines[2].strip()
                            roman = lines[1].strip()
                            lines = [lines[0].strip()]
                    elif (
                        usex_type == "quotation"
                        and lang_code != "en"
                        and len(lines) > 2
                    ):
                        # for x in lines:
                        #     print("  LINE: {}: {}"
                        #           .format(classify_desc(x), x))
                        if re.match(r"^[#*]*:+\s*$", lines[1]):
                            ref = lines[0]
                            lines = lines[2:]
                        cls1 = classify_desc(lines[-1])
                        if cls1 == "english":
                            i = len(lines) - 1
                            while (
                                i > 1
                                and classify_desc(lines[i - 1]) == "english"
                            ):
                                i -= 1
                            tr = "\n".join(lines[i:])
                            lines = lines[:i]

                roman = re.sub(r"[ \t\r]+", " ", roman).strip()
                roman = re.sub(r"\[\s*…\s*\]", "[…]", roman)
                tr = re.sub(r"^[#*:]+\s*", "", tr)
                tr = re.sub(r"[ \t\r]+", " ", tr).strip()
                tr = re.sub(r"\[\s*…\s*\]", "[…]", tr)
                ref = re.sub(r"^[#*:]+\s*", "", ref)
                ref = re.sub(
                    r", (volume |number |page )?“?"
                    r"\(please specify ([^)]|\(s\))*\)”?|"
                    ", text here$",
                    "",
                    ref,
                )
                ref = re.sub(r"\[\s*…\s*\]", "[…]", ref)
                lines = list(re.sub(r"^[#*:]+\s*", "", x) for x in lines)
                subtext = "\n".join(x for x in lines if x)
                if not tr and lang_code != "en":
                    m = re.search(r"([.!?])\s+\(([^)]+)\)\s*$", subtext)
                    if m and classify_desc(m.group(2)) == "english":
                        tr = m.group(2)
                        subtext = subtext[: m.start()] + m.group(1)
                    elif lines:
                        parts = re.split(r"\s*[―—]+\s*", lines[0])
                        if (
                            len(parts) == 2
                            and classify_desc(parts[1]) == "english"
                        ):
                            subtext = parts[0].strip()
                            tr = parts[1].strip()
                subtext = re.sub(r'^[“"`]([^“"`”\']*)[”"\']$', r"\1", subtext)
                subtext = re.sub(
                    r"(please add an English translation of "
                    r"this (quote|usage example))",
                    "",
                    subtext,
                )
                subtext = re.sub(
                    r"\s*→New International Version " "translation$",
                    "",
                    subtext,
                )  # e.g. pis/Tok Pisin (Bible)
                subtext = re.sub(r"[ \t\r]+", " ", subtext).strip()
                subtext = re.sub(r"\[\s*…\s*\]", "[…]", subtext)
                note = None
                m = re.match(r"^\(([^)]*)\):\s+", subtext)
                if (
                    m is not None
                    and lang_code != "en"
                    and (
                        m.group(1).startswith("with ")
                        or classify_desc(m.group(1)) == "english"
                    )
                ):
                    note = m.group(1)
                    subtext = subtext[m.end() :]
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
                    if ruby:
                        dt["ruby"] = ruby
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
        # WordData should not have a 'tags' field, but if it does, it's
        # deleted and its contents removed and placed in each sense;
        # that's why the type ignores.
        tags: Iterable = data.get("tags", ())  # type: ignore[assignment]
        if "tags" in data:
            del data["tags"]  # type: ignore[typeddict-item]
        for sense in data["senses"]:
            data_extend(sense, "tags", tags)

    return ret


def parse_wikipedia_template(wxr, data, ht):
    """Helper function for parsing {{wikipedia|...}} and related templates."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(data, dict)
    assert isinstance(ht, dict)
    langid = clean_node(wxr, data, ht.get("lang", ()))
    pagename = clean_node(wxr, data, ht.get(1, ())) or wxr.wtp.title
    if langid:
        data_append(data, "wikipedia", langid + ":" + pagename)
    else:
        data_append(data, "wikipedia", pagename)


def parse_top_template(wxr, node, data):
    """Parses a template that occurs on the top-level in a page, before any
    language subtitles."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(node, WikiNode)
    assert isinstance(data, dict)

    def top_template_fn(name, ht):
        if name in wikipedia_templates:
            parse_wikipedia_template(wxr, data, ht)
            return None
        if is_panel_template(wxr, name):
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
            arg = clean_node(wxr, data, ht.get(1, ()))
            if arg.startswith("Q") or arg.startswith("Lexeme:L"):
                data_append(data, "wikidata", arg)
            return ""
        wxr.wtp.debug(
            "UNIMPLEMENTED top-level template: {} {}".format(name, ht),
            sortid="page/2870",
        )
        return ""

    clean_node(wxr, None, [node], template_fn=top_template_fn)


def fix_subtitle_hierarchy(wxr: WiktextractContext, text: str) -> str:
    """Fix subtitle hierarchy to be strict Language -> Etymology ->
    Part-of-Speech -> Translation/Linkage."""

    # Known lowercase PoS names are in part_of_speech_map
    # Known lowercase linkage section names are in linkage_map

    old = re.split(
        r"(?m)^(==+)[ \t]*([^= \t]([^=\n]|=[^=])*?)" r"[ \t]*(==+)[ \t]*$", text
    )

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
            wxr.wtp.debug(
                "subtitle has unbalanced levels: "
                "{!r} has {} on the left and {} on the right".format(
                    title, left, right
                ),
                sortid="page/2904",
            )
        lc = title.lower()
        if name_to_code(title, "en") != "":
            if level > 2:
                wxr.wtp.debug(
                    "subtitle has language name {} at level {}".format(
                        title, level
                    ),
                    sortid="page/2911",
                )
            level = 2
        elif lc.startswith(tuple(ETYMOLOGY_TITLES)):
            if level > 3:
                wxr.wtp.debug(
                    "etymology section {} at level {}".format(title, level),
                    sortid="page/2917",
                )
            level = 3
        elif lc.startswith(PRONUNCIATION_TITLE):
            level = 3
        elif lc in POS_TITLES:
            level = 4
        elif lc == TRANSLATIONS_TITLE:
            level = 5
        elif lc in LINKAGE_TITLES or lc == COMPOUNDS_TITLE:
            level = 5
        elif lc in INFLECTION_TITLES:
            level = 5
        elif lc == DESCENDANTS_TITLE:
            level = 5
        elif title in PROTO_ROOT_DERIVED_TITLES:
            level = 5
        elif lc in IGNORED_TITLES:
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


def parse_page(
    wxr: WiktextractContext, word: str, text: str
) -> list[dict[str, Any]]:
    # Skip translation pages
    if word.endswith("/" + TRANSLATIONS_TITLE):
        return []

    if wxr.config.verbose:
        logger.info(f"Parsing page: {word}")

    wxr.config.word = word
    wxr.wtp.start_page(word)

    # Remove <noinclude> and similar tags from main pages.  They
    # should not appear there, but at least net/Elfdala has one and it
    # is probably not the only one.
    text = re.sub(r"(?si)<(/)?noinclude\s*>", "", text)
    text = re.sub(r"(?si)<(/)?onlyinclude\s*>", "", text)
    text = re.sub(r"(?si)<(/)?includeonly\s*>", "", text)

    # Fix up the subtitle hierarchy.  There are hundreds if not thousands of
    # pages that have, for example, Translations section under Linkage, or
    # Translations section on the same level as Noun.  Enforce a proper
    # hierarchy by manipulating the subtitle levels in certain cases.
    text = fix_subtitle_hierarchy(wxr, text)

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    tree = wxr.wtp.parse(
        text,
        pre_expand=True,
        additional_expand=ADDITIONAL_EXPAND_TEMPLATES,
        do_not_pre_expand=DO_NOT_PRE_EXPAND_TEMPLATES,
    )
    # from wikitextprocessor.parser import print_tree
    # print("PAGE PARSE:", print_tree(tree))

    top_data = {}

    # Iterate over top-level titles, which should be languages for normal
    # pages
    by_lang = defaultdict(list)
    for langnode in tree.children:
        if not isinstance(langnode, WikiNode):
            continue
        if langnode.kind == NodeKind.TEMPLATE:
            parse_top_template(wxr, langnode, top_data)
            continue
        if langnode.kind == NodeKind.LINK:
            # Some pages have links at top level, e.g., "trees" in Wiktionary
            continue
        if langnode.kind != NodeKind.LEVEL2:
            wxr.wtp.debug(
                f"unexpected top-level node: {langnode}", sortid="page/3014"
            )
            continue
        lang = clean_node(
            wxr, None, langnode.sarg if langnode.sarg else langnode.largs
        )
        lang_code = name_to_code(lang, "en")
        if lang_code == "":
            wxr.wtp.debug(
                f"unrecognized language name: {lang}", sortid="page/3019"
            )
        if (
            wxr.config.capture_language_codes
            and lang_code not in wxr.config.capture_language_codes
        ):
            continue
        wxr.wtp.start_section(lang)

        # Collect all words from the page.
        # print(f"{langnode=}")
        datas = parse_language(wxr, langnode, lang, lang_code)

        # Propagate fields resulting from top-level templates to this
        # part-of-speech.
        for data in datas:
            if "lang" not in data:
                wxr.wtp.debug(
                    "internal error -- no lang in data: {}".format(data),
                    sortid="page/3034",
                )
                continue
            for k, v in top_data.items():
                assert isinstance(v, (list, tuple))
                data_extend(data, k, v)
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
                    if (
                        pos == cpos
                        or (pos, cpos)
                        in (
                            ("noun", "adj"),
                            ("noun", "name"),
                            ("name", "noun"),
                            ("name", "adj"),
                            ("adj", "noun"),
                            ("adj", "name"),
                        )
                        or (
                            pos == "adj"
                            and cpos == "verb"
                            and any(
                                "participle" in s.get("tags", ())
                                for s in dt.get("senses", ())
                            )
                        )
                    ):
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

    for x in ret:
        if x["word"] != word:
            if word.startswith("Unsupported titles/"):
                wxr.wtp.debug(
                    f"UNSUPPORTED TITLE: '{word}' -> '{x['word']}'",
                    sortid="20231101/3578page.py",
                )
            else:
                wxr.wtp.debug(
                    f"DIFFERENT ORIGINAL TITLE: '{word}' " f"-> '{x['word']}'",
                    sortid="20231101/3582page.py",
                )
            x["original_title"] = word
        # validate tag data
        recursively_separate_raw_tags(wxr, x)
    return ret


def recursively_separate_raw_tags(wxr: WiktextractContext, data: dict) -> None:
    if not isinstance(data, dict):
        wxr.wtp.error(
            "'data' is not dict; most probably "
            "data has a list that contains at least one dict and "
            "at least one non-dict item",
            sortid="en/page-4016/20240419",
        )
        return
    new_tags = []
    raw_tags = data.get("raw_tags", [])
    for field, val in data.items():
        if field == "tags":
            for tag in val:
                if tag not in valid_tags:
                    raw_tags.append(tag)
                else:
                    new_tags.append(tag)
        if isinstance(val, list):
            if len(val) > 0 and isinstance(val[0], dict):
                for d in val:
                    recursively_separate_raw_tags(wxr, d)
    if "tags" in data and not new_tags:
        del data["tags"]
    elif new_tags:
        data["tags"] = new_tags
    if raw_tags:
        data["raw_tags"] = raw_tags


def process_soft_redirect_template(
    wxr: WiktextractContext,
    template_node: TemplateNode,
    redirect_pages: list[str],
) -> bool:
    # return `True` if the template is soft redirect template
    if template_node.template_name == "zh-see":
        # https://en.wiktionary.org/wiki/Template:zh-see
        title = clean_node(
            wxr, None, template_node.template_parameters.get(1, "")
        )
        if title != "":
            redirect_pages.append(title)
        return True
    elif template_node.template_name in ["ja-see", "ja-see-kango"]:
        # https://en.wiktionary.org/wiki/Template:ja-see
        for key, value in template_node.template_parameters.items():
            if isinstance(key, int):
                title = clean_node(wxr, None, value)
                if title != "":
                    redirect_pages.append(title)
        return True
    return False

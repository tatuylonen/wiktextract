# Code for parsing linguistic form descriptions and tags for word senses
# (both the word entry head - initial part and parenthesized parts -
# and tags at the beginning of word senses)
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import functools
import re
import unicodedata
from typing import (
    Any,
    Literal,
    Optional,
    Sequence,
    Union,
)

import Levenshtein
from nltk import TweetTokenizer  # type:ignore[import-untyped]

from wiktextract.type_utils import (
    AltOf,
    FormData,
    LinkageData,
    SenseData,
    SoundData,
    WordData,
)
from wiktextract.wxr_context import WiktextractContext

from .datautils import data_append, data_extend, split_at_comma_semi
from .english_words import (
    english_words,
    not_english_words,
    potentially_english_words,
)
from .form_descriptions_known_firsts import known_firsts
from .tags import (
    alt_of_tags,
    form_of_tags,
    head_final_bantu_langs,
    head_final_bantu_map,
    head_final_numeric_langs,
    head_final_other_langs,
    head_final_other_map,
    head_final_semitic_langs,
    head_final_semitic_map,
    uppercase_tags,
    valid_tags,
    xlat_descs_map,
    xlat_head_map,
    xlat_tags_map,
)
from .taxondata import known_species
from .topics import topic_generalize_map, valid_topics
from .type_utils import TranslationData

# Tokenizer for classify_desc()
tokenizer = TweetTokenizer()

# These are ignored as the value of a related form in form head.
IGNORED_RELATED: set[str] = set(
    [
        "-",
        "־",
        "᠆",
        "‐",
        "‑",
        "‒",
        "–",
        "—",
        "―",
        "−",
        "⸺",
        "⸻",
        "﹘",
        "﹣",
        "－",
        "?",
        "(none)",
    ]
)


# First words of unicodedata.name() that indicate scripts that cannot be
# accepted in romanizations or english (i.e., should be considered "other"
# in classify_desc()).
non_latin_scripts: list[str] = [
    "ADLAM",
    "ARABIC",
    "ARABIC-INDIC",
    "ARMENIAN",
    "BALINESE",
    "BENGALI",
    "BRAHMI",
    "BRAILLE",
    "CANADIAN",
    "CHAKMA",
    "CHAM",
    "CHEROKEE",
    "CJK",
    "COPTIC",
    "COUNTING ROD",
    "CUNEIFORM",
    "CYRILLIC",
    "DOUBLE-STRUCK",
    "EGYPTIAN",
    "ETHIOPIC",
    "EXTENDED ARABIC-INDIC",
    "GEORGIAN",
    "GLAGOLITIC",
    "GOTHIC",
    "GREEK",
    "GUJARATI",
    "GURMUKHI",
    "HANGUL",
    "HANIFI ROHINGYA",
    "HEBREW",
    "HIRAGANA",
    "JAVANESE",
    "KANNADA",
    "KATAKANA",
    "KAYAH LI",
    "KHMER",
    "KHUDAWADI",
    "LAO",
    "LEPCHA",
    "LIMBU",
    "MALAYALAM",
    "MEETEI",
    "MYANMAR",
    "NEW TAI LUE",
    "NKO",
    "OL CHIKI",
    "OLD PERSIAN",
    "OLD SOUTH ARABIAN",
    "ORIYA",
    "OSMANYA",
    "PHOENICIAN",
    "SAURASHTRA",
    "SHARADA",
    "SINHALA",
    "SUNDANESE",
    "SYLOTI",
    "TAI THAM",
    "TAKRI",
    "TAMIL",
    "TELUGU",
    "THAANA",
    "THAI",
    "TIBETAN",
    "TIFINAGH",
    "TIRHUTA",
    "UGARITIC",
    "WARANG CITI",
    "YI",
]
non_latin_scripts_re = re.compile(
    r"(" + r"|".join(re.escape(x) for x in non_latin_scripts) + r")\b"
)

# Sanity check xlat_head_map values
for k, v in xlat_head_map.items():
    if v.startswith("?"):
        v = v[1:]
    for tag in v.split():
        if tag not in valid_tags:
            print(
                "WARNING: xlat_head_map[{}] contains unrecognized tag {}".format(
                    k, tag
                )
            )

# Regexp for finding nested translations from translation items (these are
# used in, e.g., year/English/Translations/Arabic).  This is actually used
# in page.py.
nested_translations_re = re.compile(
    r"\s+\((({}): ([^()]|\([^()]+\))+)\)".format(
        "|".join(
            re.escape(x.removeprefix("?"))
            for x in sorted(xlat_head_map.values(), key=len, reverse=True)
            if x and not x.startswith("class-")
        )
    )
)

# Regexp that matches head tag specifiers.  Used to match tags from end of
# translations and linkages
head_final_re_text = r"( -)?( ({}))+".format(
    "|".join(
        re.escape(x)
        for x in
        # The sort is to put longer ones first, preferring them in
        # the regexp match
        sorted(xlat_head_map.keys(), key=len, reverse=True)
    )
)
head_final_re = re.compile(head_final_re_text + "$")

# Regexp used to match head tag specifiers at end of a form for certain
# Bantu languages (particularly Swahili and similar languages).
head_final_bantu_re_text = r" ({})".format(
    "|".join(re.escape(x) for x in head_final_bantu_map.keys())
)
head_final_bantu_re = re.compile(head_final_bantu_re_text + "$")

# Regexp used to match head tag specifiers at end of a form for certain
# Semitic languages (particularly Arabic and similar languages).
head_final_semitic_re_text = r" ({})".format(
    "|".join(re.escape(x) for x in head_final_semitic_map.keys())
)
head_final_semitic_re = re.compile(head_final_semitic_re_text + "$")

# Regexp used to match head tag specifiers at end of a form for certain
# other languages (e.g., Lithuanian, Finnish, French).
head_final_other_re_text = r" ({})".format(
    "|".join(re.escape(x) for x in head_final_other_map.keys())
)
head_final_other_re = re.compile(head_final_other_re_text + "$")

# Regexp for splitting heads.  See parse_word_head().
head_split_re_text = (
    "("
    + head_final_re_text
    + "|"
    + head_final_bantu_re_text
    + "|"
    + head_final_semitic_re_text
    + "|"
    + head_final_other_re_text
    + ")?( or |[,;]+)"
)
head_split_re = re.compile(head_split_re_text)
head_split_re_parens = 0
for m in re.finditer(r"(^|[^\\])[(]+", head_split_re_text):
    head_split_re_parens += m.group(0).count("(")

# Parenthesized parts that are ignored in translations
tr_ignored_parens: set[str] = set(
    [
        "please verify",
        "(please verify)",
        "transliteration needed",
        "(transliteration needed)",
        "in words with back vowel harmony",
        "(in words with back vowel harmony)",
        "in words with front vowel harmony",
        "(in words with front vowel harmony)",
        "see below",
        "see usage notes below",
    ]
)
tr_ignored_parens_re = re.compile(
    r"^("
    + "|".join(re.escape(x) for x in tr_ignored_parens)
    + ")$"
    + r"|^(Can we clean up|Can we verify|for other meanings see "
    r"lit\. )"
)

# Translations that are ignored
ignored_translations: set[str] = set(
    [
        "[script needed]",
        "please add this translation if you can",
    ]
)

# Put english text into the "note" field in a translation if it contains one
# of these words
tr_note_re = re.compile(
    r"(\b(article|definite|indefinite|superlative|comparative|pattern|"
    r"adjective|adjectives|clause|clauses|pronoun|pronouns|preposition|prep|"
    r"postposition|postp|action|actions|articles|"
    r"adverb|adverbs|noun|nouns|verb|verbs|before|"
    r"after|placed|prefix|suffix|used with|translated|"
    r"nominative|genitive|dative|infinitive|participle|past|perfect|imperfect|"
    r"perfective|imperfective|auxiliary|negative|future|present|tense|aspect|"
    r"conjugation|declension|class|category|plural|singular|positive|"
    r"seldom used|formal|informal|familiar|unspoken|spoken|written|"
    r"indicative|progressive|conditional|potential|"
    r"accusative|adessive|inessive|superessive|elative|allative|"
    r"dialect|dialects|object|subject|predicate|movies|recommended|language|"
    r"locative|continuous|simple|continuousness|gerund|subjunctive|"
    r"periphrastically|no equivalent|not used|not always used|"
    r"used only with|not applicable|use the|signifying|wordplay|pronounced|"
    r"preconsonantal|spelled|spelling|respelling|respellings|phonetic|"
    r"may be replaced|stricter sense|for nonhumans|"
    r"sense:|used:|in full:|informally used|followed by|"
    r"not restricted to|pertaining to|or optionally with|are optional|"
    r"in conjunction with|in compounds|depending on the relationship|"
    r"person addressed|one person|multiple persons|may be replaced with|"
    r"optionally completed with|in the phrase|in response to|"
    r"before a|before an|preceded by|verbs ending|very common|after a verb|"
    r"with verb|with uncountable|with the objects|with stative|"
    r"can be replaced by|often after|used before|used after|"
    r"used in|clipping of|spoken|somewhat|capitalized|"
    r"short form|shortening of|shortened form|initialism of|"
    r"said to|rare:|rarer also|is rarer|negatively connoted|"
    r"previously mentioned|uncountable noun|countable noun|"
    r"countable nouns|uncountable nouns|"
    r"with predicative|with -|with imperfect|with a negated|"
    r"colloquial|misspelling|holophrastic|frequently|esp\.|especially|"
    r'"|'
    r"general term|after a vowel|before a vowel|"
    r"form|regular|irregular|alternative)"
    r")($|[) ])|^("
    # Following are only matched at the beginning of the string
    r"pl|pl\.|see:|pl:|sg:|plurals:|e\.g\.|e\.g\.:|e\.g\.,|cf\.|compare|such as|"
    r"see|only|often|usually|used|usage:|of|not|in|compare|usu\.|"
    r"as|about|abbrv\.|abbreviation|abbr\.|that:|optionally|"
    r"mainly|from|for|also|also:|acronym|"
    r"\+|with) "
)
# \b does not work at the end???

# Related forms matching this regexp will be considered suspicious if the
# page title does not also match one of these.
suspicious_related_re = re.compile(
    r"(^| )(f|m|n|c|or|pl|sg|inan|anim|pers|anml|impf|pf|vir|nvir)( |$)"
    r"|[][:=<>&#*|]"
    r"| \d+$"
)

# Word forms (head forms, translations, etc) that will be considered ok and
# silently accepted even if they would otherwise trigger a suspicious
# form warning.
ok_suspicious_forms: set[str] = set(
    [
        "but en or",  # "golden goal"/English/Tr/French
        "cœur en or",  # "heart of gold"/Eng/Tr/French
        "en or",  # golden/Eng/Tr/French
        "men du",  # jet/Etym2/Noun/Tr/Cornish
        "parachute en or",  # "golden parachute"/Eng/Tr/French
        "vieil or",  # "old gold"/Eng/Tr/French
        # "all that glitters is not gold"/Eng/Tr/French
        "tout ce qui brille n’est pas or",
        "μη αποκλειστικό or",  # inclusive or/Eng/Tr/Greek
        "period or full stop",
    ]
)


# Replacements to be done in classify_desc before tokenizing.  This is a
# workaround for shortcomings in TweetTokenizer.
tokenizer_fixup_map = {
    r"a.m.": "AM",
    r"p.m.": "PM",
}
tokenizer_fixup_re = re.compile(
    r"\b("
    + "|".join(
        re.escape(x)
        for x in sorted(
            tokenizer_fixup_map.keys(), key=lambda x: len(x), reverse=True
        )
    )
    + r")"
)

# Unknown tags starting with these words will be silently ignored.
ignored_unknown_starts: set[str] = set(
    [
        "originally",
        "e.g.",
        "c.f.",
        "supplanted by",
        "supplied by",
    ]
)

ignored_unknown_starts_re = re.compile(
    r"^("
    + "|".join(
        re.escape(x)
        for x in sorted(ignored_unknown_starts, key=lambda x: -len(x))
    )
    + ") "
)

# If an unknown sequence starts with one of these, it will continue as an
# unknown sequence until the end, unless it turns out to have a replacement.
allowed_unknown_starts: set[str] = set(
    [
        "Relating",
        "accompanied",
        "added",
        "after",
        "answering",
        "as",
        "based",
        "before",
        "conjugated",
        "conjunction",
        "construed",
        "especially",
        "expression:",
        "figurative:",
        "followed",
        "for",
        "forms",
        "from",
        "governs",
        "in",
        "indicating",
        "modifying",
        "normally",
        "not",
        "of",
        "preceding",
        "prefixed",
        "referring",
        "relating",
        "revived",
        "said",
        "since",
        "takes",
        "used",
        "with",
        "With",
        "without",
    ]
)
# Allow the ignored unknown starts without complaining
allowed_unknown_starts.update(ignored_unknown_starts)

# Full unknown tags that will be ignored in decode_tags()
# XXX this is unused, ask Tatu where the contents is now
ignored_unknown_tags: set[str] = set([])

# Head endings that are mapped to tags
head_end_map = {
    " 1st conj.": "conjugation-1",
    " 2nd conj.": "conjugation-2",
    " 3rd conj.": "conjugation-3",
    " 4th conj.": "conjugation-4",
    " 5th conj.": "conjugation-5",
    " 6th conj.": "conjugation-6",
    " 7th conj.": "conjugation-7",
}
head_end_re = re.compile(
    r"(" + "|".join(re.escape(x) for x in head_end_map.keys()) + r")$"
)

# Words that can be part of form description
valid_words: set[str] = set(["or", "and"])
for x in valid_tags:
    valid_words.update(x.split(" "))
for x in xlat_tags_map.keys():
    valid_words.update(x.split(" "))


# Dictionary of language-specific parenthesized head part starts that
# either introduce new tags or modify previous tags.  The value for each
# language is a dictionary that maps the first word of the head part to
# (rem_tags, add_tags), where ``rem_tags`` can be True to remove all previous
# tags or a space-separated string of tags to remove, and ``add_tags`` should
# be a string of tags to add.
lang_specific_head_map: dict[
    str, dict[str, Union[tuple[str, str], tuple[Literal[True], str]]]
] = {
    "Danish": {
        # prefix: (rem_tags space separate string/True, add_tags s-sep str)
        "c": ("neuter", "common-gender"),
        "n": ("common-gender", "neuter"),
        "pl": ("singular neuter common-gender", "plural"),
        "sg": ("plural neuter common-gender", "singular"),
    },
}


# Regular expression used to strip additional stuff from the end of alt_of and
# form_of.
alt_of_form_of_clean_re = re.compile(
    r"(?s)("
    + "|".join(
        [
            r":",
            r'[“"]',
            r";",
            r" \(",
            r" - ",
            r" ־ ",
            r" ᠆ ",
            r" ‐ ",
            r" ‑ ",
            r" ‒ ",
            r" – ",
            r" — ",
            r" ― ",
            r" − ",
            r" ⸺ ",
            r" ⸻ ",
            r" ﹘ ",
            r" ﹣ ",
            r" － ",
            r" \+ ",
            r" \(with ",
            r" with -ra/-re",
            r"\. Used ",
            r"\. Also ",
            r"\. Since ",
            r"\. A ",
            r"\.\. A ",
            r"\. An ",
            r"\.\. An ",
            r"\. an ",
            r"\. The ",
            r"\. Spanish ",
            r"\. Language ",
            r"\. former name of ",
            r"\. AIM",
            r"\. OT",
            r"\. Not ",
            r"\. Now ",
            r"\. Nowadays ",
            r"\. Early ",
            r"\. ASEAN",
            r"\. UN",
            r"\. IMF",
            r"\. WHO",
            r"\. WIPO",
            r"\. AC",
            r"\. DC",
            r"\. DNA",
            r"\. RNA",
            r"\. SOB",
            r"\. IMO",
            r"\. Behavior",
            r"\. Income ",
            r"\. More ",
            r"\. Most ",
            r"\. Only ",
            r"\. Also ",
            r"\. From ",
            r"\. Of ",
            r"\.\. Of ",
            r"\. To ",
            r"\. For ",
            r"\. If ",
            r"\. Praenominal ",
            r"\. This ",
            r"\. Replaced ",
            r"\. CHCS is the ",
            r"\. Equivalent ",
            r"\. Initialism ",
            r"\. Note ",
            r"\. Alternative ",
            r"\. Compare ",
            r"\. Cf\. ",
            r"\. Comparable ",
            r"\. Involves ",
            r"\. Sometimes ",
            r"\. Commonly ",
            r"\. Often ",
            r"\. Typically ",
            r"\. Possibly ",
            r"\. Although ",
            r"\. Rare ",
            r"\. Instead ",
            r"\. Integrated ",
            r"\. Distinguished ",
            r"\. Given ",
            r"\. Found ",
            r"\. Was ",
            r"\. In ",
            r"\. It ",
            r"\.\. It ",
            r"\. One ",
            r"\. Any ",
            r"\. They ",
            r"\. Members ",
            r"\. Each ",
            r"\. Original ",
            r"\. Especially ",
            r"\. Usually ",
            r"\. Known ",
            r"\.\. Known ",
            r"\. See ",
            r"\. see ",
            r"\. target was not ",
            r"\. Popular ",
            r"\. Pedantic ",
            r"\. Positive ",
            r"\. Society ",
            r"\. Plan ",
            r"\. Environmentally ",
            r"\. Affording ",
            r"\. Encompasses ",
            r"\. Expresses ",
            r"\. Indicates ",
            r"\. Text ",
            r"\. Large ",
            r"\. Sub-sorting ",
            r"\. Sax",
            r"\. First-person ",
            r"\. Second-person ",
            r"\. Third-person ",
            r"\. 1st ",
            r"\. 2nd ",
            r"\. 3rd ",
            r"\. Term ",
            r"\. Northeastern ",
            r"\. Northwestern ",
            r"\. Southeast ",
            r"\. Egyptian ",
            r"\. English ",
            r"\. Cape Province was split into ",
            r"\. Pañcat",
            r"\. of the ",
            r"\. is ",
            r"\. after ",
            r"\. or ",
            r"\. chromed",
            r"\. percussion",
            r"\. with his ",
            r"\. a\.k\.a\. ",
            r"\. comparative form ",
            r"\. singular ",
            r"\. plural ",
            r"\. present ",
            r"\. his ",
            r"\. her ",
            r"\. equivalent ",
            r"\. measuring ",
            r"\. used in ",
            r"\. cutely ",
            r"\. Protects",
            r'\. "',
            r"\.^",
            r"\. \+ ",
            r"\., ",
            r". — ",
            r", a ",
            r", an ",
            r", the ",
            r", obsolete ",
            r", possessed",  # 'd/English
            r", imitating",  # 1/English
            r", derived from",
            r", called ",
            r", especially ",
            r", slang for ",
            r" corresponding to ",
            r" equivalent to ",
            r" popularized by ",
            r" denoting ",
            r" in its various senses\.",
            r" used by ",
            r" but not for ",
            r" since ",
            r" i\.e\. ",
            r" i\. e\. ",
            r" e\.g\. ",
            r" eg\. ",
            r" etc\. ",
            r"\[http",
            r" — used as ",
            r" by K\. Forsyth ",
            r" by J\. R\. Allen ",
            r" by S\. Ferguson ",
            r" by G\. Donaldson ",
            r" May refer to ",
            r" An area or region ",
        ]
    )
    + r").*$"
)


class ValidNode:
    """Node in the valid_sequences tree. Each node is part of a chain
    or chains that form sequences built out of keys in key->tags
    maps like xlat_tags, etc. The ValidNode's 'word' is the key
    by which it is refered to in the root dict or a `children` dict,
    `end` marks that the node is the end-terminus of a sequence (but
    it can still continue if the sequence is shared by the start of
    other sequences: "nominative$" and "nominative plural$" for example),
    `tags` and `topics` are the dicts containing tag and topic strings
    for terminal nodes (end==True)."""

    __slots__ = (
        "end",
        "tags",
        "topics",
        "children",
    )

    def __init__(
        self,
        end=False,
        tags: Optional[list[str]] = None,
        topics: Optional[list[str]] = None,
        children: Optional[dict[str, "ValidNode"]] = None,
    ) -> None:
        self.end = end
        self.tags: list[str] = tags or []
        self.topics: list[str] = topics or []
        self.children: dict[str, "ValidNode"] = children or {}


def add_to_valid_tree(tree: ValidNode, desc: str, v: Optional[str]) -> None:
    """Helper function for building trees of valid tags/sequences during
    initialization."""
    assert isinstance(tree, ValidNode)
    assert isinstance(desc, str)
    assert v is None or isinstance(v, str)
    node = tree

    # Build the tree structure: each node has children nodes
    # whose names are denoted by their dict key.
    for w in desc.split(" "):
        if w in node.children:
            node = node.children[w]
        else:
            new_node = ValidNode()
            node.children[w] = new_node
            node = new_node
    if not node.end:
        node.end = True
    if not v:
        return None  # Terminate early because there are no tags

    tagslist = []
    topicslist = []
    for vv in v.split():
        if vv in valid_tags:
            tagslist.append(vv)
        elif vv in valid_topics:
            topicslist.append(vv)
        else:
            print(
                "WARNING: tag/topic {!r} maps to unknown {!r}".format(desc, vv)
            )
    topics = " ".join(topicslist)
    tags = " ".join(tagslist)
    # Changed to "_tags" and "_topics" to avoid possible key-collisions.
    if topics:
        node.topics.extend([topics])
    if tags:
        node.tags.extend([tags])


def add_to_valid_tree1(
    tree: ValidNode,
    k: str,
    v: Union[list[str], tuple[str, ...], str],
    valid_values: Union[set[str], dict[str, Any]],
) -> list[str]:
    assert isinstance(tree, ValidNode)
    assert isinstance(k, str)
    assert v is None or isinstance(v, (list, tuple, str))
    assert isinstance(valid_values, (set, dict))
    if not v:
        add_to_valid_tree(valid_sequences, k, None)
        return []
    elif isinstance(v, str):
        v = [v]
    q = []
    for vv in v:
        assert isinstance(vv, str)
        add_to_valid_tree(valid_sequences, k, vv)
        vvs = vv.split()
        for x in vvs:
            q.append(x)
    # return each individual tag
    return q


def add_to_valid_tree_mapping(
    tree: ValidNode,
    mapping: Union[dict[str, Union[list[str], str]], dict[str, str]],
    valid_values: Union[set[str], dict[str, Any]],
    recurse: bool,
) -> None:
    assert isinstance(tree, ValidNode)
    assert isinstance(mapping, dict)
    assert isinstance(valid_values, (set, dict))
    assert recurse in (True, False)
    for k, v in mapping.items():
        assert isinstance(k, str)
        assert isinstance(v, (list, str))
        if isinstance(v, str):
            q = add_to_valid_tree1(tree, k, [v], valid_values)
        else:
            q = add_to_valid_tree1(tree, k, v, valid_values)
        if recurse:
            visited = set()
            while q:
                v = q.pop()
                if v in visited:
                    continue
                visited.add(v)
                if v not in mapping:
                    continue
                vv = mapping[v]
                qq = add_to_valid_tree1(tree, k, vv, valid_values)
                q.extend(qq)


# Tree of sequences considered to be tags (includes sequences that are
# mapped to something that becomes one or more valid tags)
valid_sequences = ValidNode()
sequences_with_slashes: set[str] = set()
for tag in valid_tags:
    # The basic tags used in our tag system; some are a bit weird, but easier
    # to implement this with 'false' positives than filter out stuff no one else
    # uses.
    if "/" in tag:
        sequences_with_slashes.add(tag)
    add_to_valid_tree(valid_sequences, tag, tag)
for tag in uppercase_tags:
    hyphenated = re.sub(r"\s+", "-", tag)
    if hyphenated in valid_tags:
        print(
            "DUPLICATE TAG: {} (from uppercase tag {!r})".format(
                hyphenated, tag
            )
        )
    assert hyphenated not in valid_tags
    # Might as well, while we're here: Add hyphenated location tag.
    valid_tags[hyphenated] = "dialect"
    add_to_valid_tree(valid_sequences, hyphenated, hyphenated)
for tag in uppercase_tags:
    hyphenated = re.sub(r"\s+", "-", tag)
    # XXX Move to above loop? Or is this here for readability?
    if "/" in tag:
        sequences_with_slashes.add(tag)
    add_to_valid_tree(valid_sequences, tag, hyphenated)
# xlat_tags_map!
add_to_valid_tree_mapping(valid_sequences, xlat_tags_map, valid_tags, False)
for k in xlat_tags_map:
    if "/" in k:
        sequences_with_slashes.add(k)
# Add topics to the same table, with all generalized topics also added
for topic in valid_topics:
    assert " " not in topic
    if "/" in topic:
        sequences_with_slashes.add(topic)
    add_to_valid_tree(valid_sequences, topic, topic)
# Let each original topic value stand alone.  These are not generally on
# valid_topics.  We add the original topics with spaces replaced by hyphens.
for topic in topic_generalize_map.keys():
    hyphenated = topic.replace(" ", "-")
    valid_topics.add(hyphenated)
    if "/" in topic:
        sequences_with_slashes.add(tag)
    add_to_valid_tree(valid_sequences, topic, hyphenated)
# Add canonicalized/generalized topic values
add_to_valid_tree_mapping(
    valid_sequences, topic_generalize_map, valid_topics, True
)

# Regex used to divide a decode candidate into parts that shouldn't
# have their slashes turned into spaces
slashes_re = re.compile(
    r"(" + "|".join((re.escape(s) for s in sequences_with_slashes)) + r")"
)

# Regexp used to find "words" from word heads and linguistic descriptions
word_pattern = (
    r"[^ ,;()\u200e]+|"
    r"\([^ ,;()\u200e]+\)[^ ,;()\u200e]+|"
    r"[\u2800-\u28ff]|"  # Braille characters
    r"\(([^()]|\([^()]*\))*\)"
)

word_re_global = re.compile(word_pattern)


def distw(titleparts: Sequence[str], word: str) -> float:
    """Computes how distinct ``word`` is from the most similar word in
    ``titleparts``.  Returns 1 if words completely distinct, 0 if
    identical, or otherwise something in between."""
    assert isinstance(titleparts, (list, tuple))
    assert isinstance(word, str)
    w = min(
        Levenshtein.distance(word, tw) / max(len(tw), len(word))
        for tw in titleparts
    )
    return w


def map_with(
    ht: Union[dict[str, Union[str, list[str]]], dict[str, str]],
    lst: Sequence[str],
) -> list[str]:
    """Takes alternatives from ``lst``, maps them using ``ht`` to zero or
    more alternatives each, and returns a combined list of alternatives."""
    assert isinstance(ht, dict)
    assert isinstance(lst, (list, tuple))
    ret = []
    for x in lst:
        assert isinstance(x, str)
        x = x.strip()
        x = ht.get(x, x)
        if isinstance(x, str):
            if x:
                ret.append(x)
        elif isinstance(x, (list, tuple)):
            ret.extend(x)
        else:
            raise RuntimeError("map_with unexpected value: {!r}".format(x))
    return ret


TagList = list[str]
PosPathStep = tuple[int, TagList, TagList]


def check_unknown(
    from_i: int,
    to_i: int,
    i: int,
    wordlst: Sequence[str],
    allow_any: bool,
    no_unknown_starts: bool,
) -> list[PosPathStep]:
    """Check if the current section from_i->to_i is actually unknown
    or if it needs some special handling. We already presupposed that
    this is UNKNOWN; this is just called to see what *kind* of UNKNOWN."""
    assert isinstance(to_i, int)
    assert isinstance(from_i, int)
    assert isinstance(i, int)
    # Adds unknown tag if needed.  Returns new last_i
    # print("check_unknown to_i={} from_i={} i={}"
    #       .format(to_i, from_i, i))
    if from_i >= to_i:
        return []
    words = wordlst[from_i:to_i]
    tag = " ".join(words)
    assert tag
    if re.match(ignored_unknown_starts_re, tag):
        # Tags with this start are to be ignored
        return [(from_i, ["UNKNOWN"], [])]
    if tag in ignored_unknown_tags:
        return []  # One of the tags listed as to be ignored
    if tag in ("and", "or"):
        return []
    if (
        not allow_any
        and not words[0].startswith("~")
        and (
            no_unknown_starts
            or words[0] not in allowed_unknown_starts
            or len(words) <= 1
        )
    ):
        # print("ERR allow_any={} words={}"
        #       .format(allow_any, words))
        return [
            (from_i, ["UNKNOWN"], ["error-unknown-tag"])
        ]  # Add ``tag`` here to include
    else:
        return [(from_i, ["UNKNOWN"], [tag])]


def add_new1(
    node: ValidNode,
    i: int,
    start_i: int,
    last_i: int,
    new_paths: list[list[PosPathStep]],
    new_nodes: list[tuple[ValidNode, int, int]],
    pos_paths: list[list[list[PosPathStep]]],
    wordlst: list[str],
    allow_any: bool,
    no_unknown_starts: bool,
    max_last_i: int,
) -> int:
    assert isinstance(new_paths, list)
    # print("add_new: start_i={} last_i={}".format(start_i, last_i))
    # print("$ {} last_i={} start_i={}"
    # .format(w, last_i, start_i))
    max_last_i = max(max_last_i, last_i)  # if last_i has grown
    if (node, start_i, last_i) not in new_nodes:
        new_nodes.append((node, start_i, last_i))
    if node.end:
        # We can see a terminal point in the search tree.
        u = check_unknown(
            last_i, start_i, i, wordlst, allow_any, no_unknown_starts
        )
        # Create new paths candidates based on different past possible
        # paths; pos_path[last_i] contains possible paths, so add this
        # new one at the beginning(?)
        # The list comprehension inside the parens generates an iterable
        # of lists, so this is .extend( [(last_i...)], [(last_i...)], ... )
        # XXX: this is becoming impossible to annotate, nodes might
        # need to become classed objects and not just dicts, or at least
        # a TypedDict with a "children" node
        new_paths.extend(
            [(last_i, node.tags, node.topics)] + u + x
            for x in pos_paths[last_i]
        )
        max_last_i = i + 1
    return max_last_i


@functools.lru_cache(maxsize=65536)
def decode_tags(
    src: str,
    allow_any=False,
    no_unknown_starts=False,
) -> tuple[list[tuple[str, ...]], list[str]]:
    tagsets, topics = decode_tags1(src, allow_any, no_unknown_starts)

    # Insert retry-code here that modifies the text source
    if (
        any(s.startswith("error-") for tagset in tagsets for s in tagset)
        # I hate Python's *nested* list comprehension syntax ^
        or any(s.startswith("error-") for s in topics)
    ):
        # slashes_re contains valid key entries with slashes; we're going to
        # skip them by splitting the string and skipping handling every
        # second entry, which contains the splitting group like "masculine/
        # feminine" style keys.
        if "/" in src:
            split_parts = re.split(slashes_re, src)
            new_parts: list[str] = []
            if len(split_parts) > 1:
                for i, s in enumerate(split_parts):
                    if i % 2 == 0:
                        new_parts.append(s.replace("/", " "))
                    else:
                        new_parts.append(s)
                new_src = "".join(new_parts)
            else:
                new_src = src
            new_tagsets, new_topics = decode_tags1(
                new_src, allow_any, no_unknown_starts
            )

            old_errors = sum(
                1 for tagset in tagsets for s in tagset if s.startswith("error")
            )
            old_errors += sum(1 for s in topics if s.startswith("error"))
            new_errors = sum(
                1
                for new_tagset in new_tagsets
                for s in new_tagset
                if s.startswith("error")
            )
            new_errors += sum(1 for s in new_topics if s.startswith("error"))

            if new_errors <= old_errors:
                return new_tagsets, new_topics

    return tagsets, topics


def decode_tags1(
    src: str,
    allow_any=False,
    no_unknown_starts=False,
) -> tuple[list[tuple[str, ...]], list[str]]:
    """Decodes tags, doing some canonicalizations.  This returns a list of
    lists of tags and a list of topics."""
    assert isinstance(src, str)

    # print("decode_tags: src={!r}".format(src))

    pos_paths: list[list[list[PosPathStep]]] = [[[]]]
    wordlst: list[str] = []
    max_last_i = 0  # pre-initialized here so that it can be used as a ref

    add_new = functools.partial(
        add_new1,  # pre-set parameters and references for function
        pos_paths=pos_paths,
        wordlst=wordlst,
        allow_any=allow_any,
        no_unknown_starts=no_unknown_starts,
        max_last_i=max_last_i,
    )
    # First split the tags at commas and semicolons.  Their significance is that
    # a multi-word sequence cannot continue across them.
    parts = split_at_comma_semi(src, extra=[";", ":"])

    for part in parts:
        max_last_i = len(wordlst)  # "how far have we gone?"
        lst1 = part.split()
        if not lst1:
            continue
        wordlst.extend(lst1)
        cur_nodes: list[tuple[ValidNode, int, int]] = []  # Currently seen
        for w in lst1:
            i = len(pos_paths) - 1
            new_nodes: list[tuple[ValidNode, int, int]] = []
            # replacement nodes for next loop
            new_paths: list[list[PosPathStep]] = []
            # print("ITER i={} w={} max_last_i={} wordlst={}"
            #       .format(i, w, max_last_i, wordlst))
            node: ValidNode
            start_i: int
            last_i: int
            for node, start_i, last_i in cur_nodes:
                # ValidNodes are part of a search tree that checks if a
                # phrase is found in xlat_tags_map and other text->tags dicts.
                if w in node.children:
                    # the phrase continues down the tree
                    # print("INC", w)
                    max_last_i = add_new(
                        node.children[w],
                        i,
                        start_i,
                        last_i,
                        new_paths,
                        new_nodes,
                    )
                if node.end:
                    # we've hit an end point, the tags and topics have already
                    # been gathered at some point, don't do anything with the
                    # old stuff
                    if w in valid_sequences.children:
                        # This starts a *new* possible section
                        max_last_i = add_new(
                            valid_sequences.children[w],  # root->
                            i,
                            i,
                            i,
                            new_paths,
                            new_nodes,
                        )
                if w not in node.children and not node.end:
                    # print("w not in node and $: i={} last_i={} wordlst={}"
                    #       .format(i, last_i, wordlst))
                    # If i == last_i == 0, for example (beginning)
                    if (
                        i == last_i
                        or no_unknown_starts
                        or wordlst[last_i] not in allowed_unknown_starts
                    ):
                        # print("NEW", w)
                        if w in valid_sequences.children:
                            # Start new sequences here
                            max_last_i = add_new(
                                valid_sequences.children[w],
                                i,
                                i,
                                last_i,
                                new_paths,
                                new_nodes,
                            )
            if not new_nodes:
                # This is run at the start when i == max_last_i == 0,
                # which is what populates the first node in new_nodes.
                # Some initial words cause the rest to be interpreted as unknown
                # print("not new nodes: i={} last_i={} wordlst={}"
                #       .format(i, max_last_i, wordlst))
                if (
                    i == max_last_i
                    or no_unknown_starts
                    or wordlst[max_last_i] not in allowed_unknown_starts
                ):
                    # print("RECOVER w={} i={} max_last_i={} wordlst={}"
                    #       .format(w, i, max_last_i, wordlst))
                    if w in valid_sequences.children:
                        max_last_i = add_new(
                            # new sequence from root
                            valid_sequences.children[w],
                            i,
                            i,
                            max_last_i,
                            new_paths,
                            new_nodes,
                        )
            cur_nodes = new_nodes  # Completely replace nodes!
            # 2023-08-18, fix to improve performance
            # Decode tags does a big search of the best-shortest matching
            # sequences of tags, but the original algorithm didn't have
            # any culling happen during operation, so in a case with
            # a lot of tags (for example, big blocks of text inserted
            # somewhere by mistake that is processed by decode_tags),
            # it would lead to exponential growth of new_paths contents.
            # This culling, using the same weighting algorithm code as
            # in the original is just applied to new_paths before it is
            # added to pos_paths. Basically it's "take the 10 best paths".
            # This *can* cause bugs if it gets stuck in a local minimum
            # or something, but this whole process is one-dimensional
            # and not that complex, so hopefully it works out...
            pw = []
            path: list[PosPathStep]
            for path in new_paths:
                weight = len(path)
                if any(x[1] == ["UNKNOWN"] for x in path):
                    weight += 100  # Penalize unknown paths
                pw.append((weight, path))
            new_paths = [weightpath[1] for weightpath in sorted(pw)[:10]]
            pos_paths.append(new_paths)

        # print("END max_last_i={} len(wordlst)={} len(pos_paths)={}"
        #       .format(max_last_i, len(wordlst), len(pos_paths)))

        if cur_nodes:
            # print("END HAVE_NODES")
            for node, start_i, last_i in cur_nodes:
                if node.end:
                    # print("$ END start_i={} last_i={}"
                    #       .format(start_i, last_i))
                    for path in pos_paths[start_i]:
                        pos_paths[-1].append(
                            [(last_i, node.tags, node.topics)] + path
                        )
                else:
                    # print("UNK END start_i={} last_i={} wordlst={}"
                    #       .format(start_i, last_i, wordlst))
                    u = check_unknown(
                        last_i,
                        len(wordlst),
                        len(wordlst),
                        wordlst,
                        allow_any,
                        no_unknown_starts,
                    )
                    if pos_paths[start_i]:
                        for path in pos_paths[start_i]:
                            pos_paths[-1].append(u + path)
                    else:
                        pos_paths[-1].append(u)
        else:
            # Check for a final unknown tag
            # print("NO END NODES max_last_i={}".format(max_last_i))
            paths = pos_paths[max_last_i] or [[]]
            u = check_unknown(
                max_last_i,
                len(wordlst),
                len(wordlst),
                wordlst,
                allow_any,
                no_unknown_starts,
            )
            if u:
                # print("end max_last_i={}".format(max_last_i))
                for path in list(paths):  # Copy in case it is the last pos
                    pos_paths[-1].append(u + path)

    # import json
    # print("POS_PATHS:", json.dumps(pos_paths, indent=2, sort_keys=True))

    if not pos_paths[-1]:
        # print("decode_tags: {}: EMPTY POS_PATHS[-1]".format(src))
        return [], []

    # Find the best path
    pw = []
    for path in pos_paths[-1]:
        weight = len(path)
        if any(x[1] == ["UNKNOWN"] for x in path):
            weight += 100  # Penalize unknown paths
        pw.append((weight, path))
    path = min(pw)[1]

    # Convert the best path to tagsets and topics
    tagsets: list[list[str]] = [[]]
    topics: list[str] = []
    for i, tagspec, topicspec in path:
        if len(tagsets or "") > 16:
            # ctx.error("Too many tagsets! This is probably exponential",
            #           sortid="form_descriptions/20230818")
            return [("error-unknown-tag", "error-exponential-tagsets")], []
        if tagspec == ["UNKNOWN"]:
            new_tagsets = []
            for x in tagsets:
                new_tagsets.append(x + topicspec)
            tagsets = new_tagsets
            continue
        if tagspec:
            new_tagsets = []
            for x in tagsets:
                for t in tagspec:
                    if t:
                        new_tags = list(x)
                        for tag in t.split():
                            if tag not in new_tags:
                                new_tags.append(tag)
                        new_tagsets.append(new_tags)
                    else:
                        new_tagsets.append(x)
            tagsets = new_tagsets
        if topicspec:
            for t in topicspec:
                for topic in t.split():
                    if topic not in topics:
                        topics.append(topic)

    # print("unsorted tagsets:", tagsets)
    ret_tagsets = sorted(set(tuple(sorted(set(tags))) for tags in tagsets))
    # topics = list(sorted(set(topics)))   XXX tests expect not sorted
    # print("decode_tags: {} -> {} topics {}".format(src, tagsets, topics))
    # Yes, ret_tagsets is a list of tags in tuples, while topics is a LIST
    # of tags. Turning topics into a tuple breaks tests, turning the tuples
    # inside tagsets into lists breaks tests, I'm leaving them mismatched
    # for now. XXX
    return ret_tagsets, topics


def parse_head_final_tags(
    wxr: WiktextractContext, lang: str, form: str
) -> tuple[str, list[str]]:
    """Parses tags that are allowed at the end of a form head from the end
    of the form.  This can also be used for parsing the final gender etc tags
    from translations and linkages."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(lang, str)  # Should be language that "form" is for
    assert isinstance(form, str)

    # print("parse_head_final_tags: lang={} form={!r}".format(lang, form))

    # Make sure there are no double spaces in the form as this code does not
    # handle them otherwise.
    form = re.sub(r"\s+", " ", form.strip())
    if not form:
        return form, []

    origform = form

    tags = []

    # If parsing for certain Bantu languages (e.g., Swahili), handle
    # some extra head-final tags first
    if lang in head_final_bantu_langs:
        m = re.search(head_final_bantu_re, form)
        if m is not None:
            tagkeys = m.group(1)
            if not wxr.wtp.title.endswith(tagkeys):  # type:ignore[union-attr]
                form = form[: m.start()]
                v = head_final_bantu_map[tagkeys]
                if v.startswith("?"):
                    v = v[1:]
                    wxr.wtp.debug(
                        "suspicious suffix {!r} in language {}: {}".format(
                            tagkeys, lang, origform
                        ),
                        sortid="form_descriptions/1028",
                    )
                tags.extend(v.split())

    # If parsing for certain Semitic languages (e.g., Arabic), handle
    # some extra head-final tags first
    if lang in head_final_semitic_langs:
        m = re.search(head_final_semitic_re, form)
        if m is not None:
            tagkeys = m.group(1)
            if not wxr.wtp.title.endswith(tagkeys):  # type:ignore[union-attr]
                form = form[: m.start()]
                v = head_final_semitic_map[tagkeys]
                if v.startswith("?"):
                    v = v[1:]
                    wxr.wtp.debug(
                        "suspicious suffix {!r} in language {}: {}".format(
                            tagkeys, lang, origform
                        ),
                        sortid="form_descriptions/1043",
                    )
                tags.extend(v.split())

    # If parsing for certain other languages (e.g., Lithuanian,
    # French, Finnish), handle some extra head-final tags first
    if lang in head_final_other_langs:
        m = re.search(head_final_other_re, form)
        if m is not None:
            tagkeys = m.group(1)
            if not wxr.wtp.title.endswith(tagkeys):  # type:ignore[union-attr]
                form = form[: m.start()]
                tags.extend(head_final_other_map[tagkeys].split(" "))

    # Handle normal head-final tags
    m = re.search(head_final_re, form)
    if m is not None:
        tagkeys = m.group(3)
        # Only replace tags ending with numbers in languages that have
        # head-final numeric tags (e.g., Bantu classes); also, don't replace
        # tags if the main title ends with them (then presume they are part
        # of the word)
        # print("head_final_tags form={!r} tagkeys={!r} lang={}"
        #       .format(form, tagkeys, lang))
        tagkeys_contains_digit = re.search(r"\d", tagkeys)
        if (
            (not tagkeys_contains_digit or lang in head_final_numeric_langs)
            and not wxr.wtp.title.endswith(" " + tagkeys)  # type:ignore[union-attr]
            and
            # XXX the above test does not capture when the whole word is a
            # xlat_head_map key, so I added the below test to complement
            # it; does this break anything?
            not wxr.wtp.title == tagkeys
        ):  # defunct/English,
            # "more defunct" -> "more" ["archaic"]
            if not tagkeys_contains_digit or lang in head_final_numeric_langs:
                form = form[: m.start()]
                v = xlat_head_map[tagkeys]
                if v.startswith("?"):
                    v = v[1:]
                    wxr.wtp.debug(
                        "suspicious suffix {!r} in language {}: {}".format(
                            tagkeys, lang, origform
                        ),
                        sortid="form_descriptions/1077",
                    )
                tags.extend(v.split())

    # Generate warnings about words ending in " or" after processing
    if (
        (form.endswith(" or") and not origform.endswith(" or"))
        or re.search(
            r" (1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|"
            r"1a|2a|9a|10a|m1|f1|f2|m2|f3|m3|f4|m4|f5|m5|or|\?)"
            r"($|/| (f|m|sg|pl|anim|inan))",
            form,
        )
        or form.endswith(" du")
    ):
        if form not in ok_suspicious_forms:
            wxr.wtp.debug(
                "suspicious unhandled suffix in {}: {!r}, originally {!r}".format(
                    lang, form, origform
                ),
                sortid="form_descriptions/1089",
            )

    # print("parse_head_final_tags: form={!r} tags={}".format(form, tags))
    return form, tags


def quote_kept_parens(s: str) -> str:
    """Changes certain parenthesized expressions so that they won't be
    interpreted as parentheses.  This is used for parts that are kept as
    part of the word, such as "read admiral (upper half)"."""
    return re.sub(
        r"\((lower half|upper half|k|s|n|II|III|A|C|G|U|Y|"
        r"vinyl|p-phenylene vinylene|\(\(\s*\)\))\)",
        r"__lpar__\1__rpar__",
        s,
    )


def quote_kept_ruby(
    wxr: WiktextractContext,
    ruby_tuples: list[
        tuple[
            str,
            str,
        ]
    ],
    s: str,
) -> str:
    if len(ruby_tuples) < 1:
        wxr.wtp.debug(
            "quote_kept_ruby called with no ruby",
            sortid="form_description/1114/20230517",
        )
        return s
    ks = []
    rs = []
    for k, r in ruby_tuples:
        ks.append(re.escape(k))
        rs.append(re.escape(r))
    if not (ks and rs):
        wxr.wtp.debug(
            f"empty column in ruby_tuples: {ruby_tuples}",
            sortid="form_description/1124/20230606",
        )
        return s
    newm = re.compile(
        r"({})\s*\(\s*({})\s*\)".format("|".join(ks), "|".join(rs))
    )
    rub_re = re.compile(
        r"({})".format(
            r"|".join(
                r"{}\(*{}\)*".format(
                    re.escape(k),
                    re.escape(r),
                )
                for k, r in ruby_tuples
            )
        )
    )

    def paren_replace(m: re.Match) -> str:
        return re.sub(newm, r"\1__lrub__\2__rrub__", m.group(0))

    return re.sub(rub_re, paren_replace, s)


def unquote_kept_parens(s: str) -> str:
    """Conerts the quoted parentheses back to normal parentheses."""
    return re.sub(r"__lpar__(.*?)__rpar__", r"(\1)", s)


def add_romanization(
    wxr: WiktextractContext,
    data: WordData,
    roman: str,
    text: str,
    is_reconstruction: bool,
    head_group: Optional[int],
    ruby: Sequence[tuple[str, str]],
) -> None:
    tags_lst = ["romanization"]
    m = re.match(r"([^:]+):(.+)", roman)
    # This function's purpose is to intercept broken romanizations,
    # like "Yale: hēnpyeng" style tags. Most romanization styles
    # are already present as tags, so we can use decode_tags to find
    # them.
    if m:
        tagsets, topics = decode_tags(m.group(1))
        if tagsets:
            for tags in tagsets:
                tags_lst.extend(tags)
            roman = m.group(2)
    add_related(
        wxr,
        data,
        tags_lst,
        [roman],
        text,
        True,
        is_reconstruction,
        head_group,
        ruby,
    )


def add_related(
    wxr: WiktextractContext,
    data: WordData,
    tags_lst: Union[list[str], tuple[str, ...]],
    related_list: list[str],
    origtext: str,
    add_all_canonicals: bool,
    is_reconstruction: bool,
    head_group: Optional[int],
    ruby_data: Optional[Sequence[tuple[str, str]]] = None,
) -> Optional[list[tuple[str, ...]]]:
    """Internal helper function for some post-processing entries for related
    forms (e.g., in word head).  This returns a list of list of tags to be
    added to following related forms or None (cf. walrus/English word head,
    parenthesized part starting with "both")."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(tags_lst, (list, tuple))
    for x in tags_lst:
        assert isinstance(x, str)
    assert isinstance(related_list, (list, tuple))
    assert isinstance(origtext, str)
    assert add_all_canonicals in (True, False)
    assert isinstance(ruby_data, (list, tuple)) or ruby_data is None
    if ruby_data is None:
        ruby_data = []
    # print("add_related: tags_lst={} related={}".format(tags_lst, related))
    related = " ".join(related_list)
    if related == "[please provide]":
        return None
    if related in IGNORED_RELATED:
        return None
    if is_reconstruction and related.startswith("*") and len(related) > 1:
        related = related[1:]

    # Get title word, with any reconstruction prefix removed
    titleword = re.sub(r"^Reconstruction:[^/]*/", "", wxr.wtp.title)  # type:ignore[arg-type]

    def check_related(related: str) -> None:
        # Warn about some suspicious related forms
        m = re.search(suspicious_related_re, related)
        if (m and m.group(0) not in titleword) or (
            related in ("f", "m", "n", "c") and len(titleword) >= 3
        ):
            if "eumhun" in tags_lst:
                return
            if "cangjie-input" in tags_lst:
                return
            if "class" in tags_lst:
                return
            if wxr.wtp.section == "Korean" and re.search(
                r"^\s*\w*>\w*\s*$", related
            ):
                # ignore Korean "i>ni" / "라>나" values
                return
            if (
                wxr.wtp.section == "Burmese"
                and "romanization" in tags_lst
                and re.search(r":", related)
            ):
                # ignore Burmese with ":", that is used in Burmese
                # translitteration of "း", the high-tone visarga.
                return
            wxr.wtp.debug(
                "suspicious related form tags {}: {!r} in {!r}".format(
                    tags_lst, related, origtext
                ),
                sortid="form_descriptions/1147",
            )

    following_tagsets = None  # Tagsets to add to following related forms
    roman = None
    tagsets1: list[tuple[str, ...]] = [tuple()]
    topics1: list[str] = []

    m = re.match(r"\((([^()]|\([^()]*\))*)\)\s+", related)
    if m:
        paren = m.group(1)
        related = related[m.end() :]
        m = re.match(r"^(all|both) (.*)", paren)
        if m:
            tagsets1, topics1 = decode_tags(m.group(2))
            following_tagsets = tagsets1
        else:
            tagsets1, topics1 = decode_tags(paren)
    else:
        m = re.search(r"\s+\((([^()]|\([^()]*\))*)\)$", related)
        if m:
            paren = m.group(1)
            if paren.startswith("U+"):
                related = related[: m.start()]
            else:
                cls = classify_desc(paren)
                if (
                    cls in ("romanization", "english")
                    and classify_desc(related[: m.start()]) == "other"
                ):
                    roman = paren
                    related = related[: m.start()]
                else:
                    related = related[: m.start()]
                    tagsets1, topics1 = decode_tags(paren)
    if related and related.startswith("{{"):
        wxr.wtp.debug(
            "{{ in word head form - possible Wiktionary error: {!r}".format(
                related
            ),
            sortid="form_descriptions/1177",
        )
        return None  # Likely Wiktionary coding error
    related = unquote_kept_parens(related)
    # Split related by "/" (e.g., grande/Spanish) superlative in head
    # Do not split if / in word title, see π//Japanese
    if len(related) > 5 and "/" not in wxr.wtp.title:  # type:ignore[operator]
        alts = split_at_comma_semi(related, separators=["/"])
    else:
        alts = [related]
    if ruby_data:
        # prepare some regex stuff in advance
        ks, rs = [], []
        for k, r in ruby_data:
            ks.append(re.escape(k))
            rs.append(re.escape(r))
        splitter = r"((?:{})__lrub__(?:{})__rrub__)".format(
            "|".join(ks), "|".join(rs)
        )
    for related in alts:
        ruby: list[tuple[str, str]] = []
        if ruby_data:
            new_related = []
            rub_split = re.split(splitter, related)
            for s in rub_split:
                m = re.match(r"(.+)__lrub__(.+)__rrub__", s)
                if m:
                    # add ruby with (\1, \2)
                    ruby.append((m.group(1), m.group(2)))
                    new_related.append(m.group(1))
                else:
                    new_related.append(s)
            related = "".join(new_related)
        tagsets2, topics2 = decode_tags(" ".join(tags_lst))
        for tags1 in tagsets1:
            assert isinstance(tags1, (list, tuple))
            for tags2 in tagsets2:
                assert isinstance(tags1, (list, tuple))
                dt: LinkageData = {"word": related}
                if roman:
                    dt["roman"] = roman
                if ruby:
                    dt["ruby"] = ruby
                if "alt-of" in tags2:
                    check_related(related)
                    data_extend(data, "tags", tags1)
                    data_extend(data, "tags", tags2)
                    data_extend(data, "topics", topics1)
                    data_extend(data, "topics", topics2)
                    data_append(data, "alt_of", dt)
                elif "form-of" in tags2:
                    check_related(related)
                    data_extend(data, "tags", tags1)
                    data_extend(data, "tags", tags2)
                    data_extend(data, "topics", topics1)
                    data_extend(data, "topics", topics2)
                    data_append(data, "form_of", dt)
                elif "compound-of" in tags2:
                    check_related(related)
                    data_extend(data, "tags", tags1)
                    data_extend(data, "tags", tags2)
                    data_extend(data, "topics", topics1)
                    data_extend(data, "topics", topics2)
                    data_append(data, "compound", related)
                else:
                    lang = wxr.wtp.section or "LANG_MISSING"
                    related, final_tags = parse_head_final_tags(
                        wxr, lang, related
                    )
                    # print("add_related: related={!r} tags1={!r} tags2={!r} "
                    #       "final_tags={!r}"
                    #       .format(related, tags1, tags2, final_tags))
                    tags = list(tags1) + list(tags2) + list(final_tags)
                    check_related(related)
                    form: FormData = {"form": related}
                    if head_group:
                        form["head_nr"] = head_group
                    if roman:
                        form["roman"] = roman
                    if ruby:
                        form["ruby"] = ruby
                    data_extend(form, "topics", topics1)
                    data_extend(form, "topics", topics2)
                    if topics1 or topics2:
                        wxr.wtp.debug(
                            "word head form has topics: {}".format(form),
                            sortid="form_descriptions/1233",
                        )
                    # Add tags from canonical form into the main entry
                    if "canonical" in tags:
                        if related in ("m", "f") and len(titleword) > 1:
                            wxr.wtp.debug(
                                "probably incorrect canonical form "
                                "{!r} ignored (probably tag combination "
                                "missing from xlat_head_map)".format(related),
                                sortid="form_descriptions/1241",
                            )
                            continue
                        if (
                            related != titleword
                            or add_all_canonicals
                            or topics1
                            or topics2
                            or ruby
                        ):
                            data_extend(form, "tags", list(sorted(set(tags))))
                        else:
                            # We won't add canonical form here
                            filtered_tags = list(
                                x for x in tags if x != "canonical"
                            )
                            data_extend(data, "tags", filtered_tags)
                            continue
                    else:
                        data_extend(form, "tags", list(sorted(set(tags))))
                    # Only insert if the form is not already there
                    for old in data.get("forms", ()):
                        if form == old:
                            break
                    else:
                        data_append(data, "forms", form)

    # If this form had pre-tags that started with "both" or "all", add those
    # tags also to following related forms that don't have their own tags
    # specified.
    return following_tagsets


def parse_word_head(
    wxr: WiktextractContext,
    pos: str,
    text: str,
    data: WordData,
    is_reconstruction: bool,
    head_group: Optional[int],
    ruby=None,
    links=None,
) -> None:
    """Parses the head line for a word for in a particular language and
    part-of-speech, extracting tags and related forms."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    assert isinstance(ruby, (list, tuple)) or ruby is None
    if ruby is None:
        ruby = []
    assert is_reconstruction in (True, False)
    # print("PARSE_WORD_HEAD: {}: {!r}".format(wxr.wtp.section, text))
    # print(f"PARSE_WORD_HEAD: {data=}")
    if links is None:
        links = []

    if len(links) > 0:
        # if we have link data (that is, links with stuff like commas and
        # spaces, replace word_re with a modified local scope pattern
        word_re = re.compile(
            r"|".join(
                sorted((re.escape(s) for s in links), key=lambda x: -len(x))
            )
            + r"|"
            + word_pattern
        )
    else:
        word_re = word_re_global

    if "Lua execution error" in text or "Lua timeout error" in text:
        return

    # In Aug 2021, some words had spurious Template:en at the end of head forms
    # due to a Wiktionary error.
    text = re.sub(r"\s+Template:[-a-zA-Z]+\s*$", "", text)

    # Fix words with "superlative:" or "comparative:" at end of head
    # e.g. grande/Spanish/Adj
    text = re.sub(r" (superlative|comparative): (.*)", r" (\1 \2)", text)

    # Parse Arabic non-past forms, e.g. أبلع/Arabic/Verb
    m = re.search(r", non-past ([^)]+ \([^)]+\))", text)
    if m:
        add_related(
            wxr,
            data,
            ["non-past"],
            [m.group(1)],
            text,
            True,
            is_reconstruction,
            head_group,
            ruby,
        )
        text = text[: m.start()] + text[m.end() :]

    language = wxr.wtp.section
    titleword = re.sub(
        r"^Reconstruction:[^/]*/", "", wxr.wtp.title or "MISSING_TITLE"
    )
    titleparts = list(
        m.group(0)
        for m in re.finditer(word_re, wxr.wtp.title or "MISSING_TITLE")
    )
    if not titleparts:
        return

    # Remove " or" from the end to prevent weird canonical forms
    if text.endswith(" or"):
        for tp in titleparts:
            if text.endswith(tp):
                break
        else:
            text = re.sub(r"\s+or$", "", text)

    # Handle the part of the head that is not in parentheses.  However, certain
    # parenthesized parts are part of word, and those must be handled
    # specially here.
    if ruby:
        text = quote_kept_ruby(wxr, ruby, text)
    base = text
    base = quote_kept_parens(base)
    base = re.sub(r"\(([^()]|\([^(]*\))*\)($|\s)", r"\2", base)
    base = re.sub(r"(^|\s)\(([^()]|\([^(]*\))*\)", r"\1", base)
    base = re.sub(r"(\s?)\^\(([^()]|\([^(]*\))*\)", r"\1", base)
    base = re.sub(r"\?", " ", base)  # Removes uncertain articles etc
    base = re.sub(r"\s+", " ", base)
    base = re.sub(r" ([,;])", r"\1", base)
    base = re.sub(r"(.*) •.*", r"\1", base)
    # Many languages use • as a punctuation mark separating the base
    # from the rest of the head. στάδιος/Ancient Greek, issue #176
    base = base.strip()

    # Check for certain endings in head (mostly for compatibility with weird
    # heads, e.g. rata/Romanian "1st conj." at end)
    m = re.search(head_end_re, base)
    tags: Union[tuple[str, ...], list[str]] = []
    if m:
        tags = head_end_map[m.group(1).lower()].split()
        data_extend(data, "tags", tags)
        base = base[: m.start()]

    # Special case: handle Hán Nôm readings for Vietnamese characters
    m = re.match(
        r"{}: (Hán Nôm) readings: (.*)".format(re.escape(titleword)), base
    )
    if m:
        tag, readings = m.groups()
        tag = re.sub(r"\s+", "-", tag)
        for reading in split_at_comma_semi(readings, skipped=links):
            add_related(
                wxr,
                data,
                [tag],
                [reading],
                text,
                True,
                is_reconstruction,
                head_group,
                ruby,
            )
        return

    # Special case: Hebrew " [pattern: nnn]" ending
    m = re.search(r"\s+\[pattern: ([^]]+)\]", base)
    if m:
        add_related(
            wxr,
            data,
            ["class"],
            [m.group(1)],
            text,
            True,
            is_reconstruction,
            head_group,
            ruby,
        )
        base = base[: m.start()] + base[m.end() :]

    # Clean away some messy "Upload an image" template text used in
    # American Sign Language:
    # S@NearBaseForearm-PalmUp Frontandback S@BaseForearm-PalmUp
    m = re.search(r"Upload .+ gif image.", base)
    if m:
        base = base[: m.start()] + base[m.end() :]

    # Split the head into alternatives.  This is a complicated task, as
    # we do not want so split on "or" or "," when immediately followed by more
    # head-final tags, but otherwise do want to split by them.
    # 20230907 added "or" to this to handle 'true or false', titles with 'or'
    if wxr.wtp.title and ("," in wxr.wtp.title or " or " in wxr.wtp.title):
        # A kludge to handle article titles/phrases with commas.
        # Preprocess splits to first capture the title, then handle
        # all the others as usual.
        presplits = re.split(r"({})".format(wxr.wtp.title), base)
        splits = []
        for psplit in presplits:
            if psplit == wxr.wtp.title:
                splits.append(psplit)
            else:
                splits.extend(re.split(head_split_re, psplit))
    else:
        # Do the normal split; previous only-behavior.
        splits = re.split(head_split_re, base)
    # print("SPLITS:", splits)
    alts: list[str] = []
    # print("parse_word_head: splits:", splits,
    # "head_split_re_parens:", head_split_re_parens)
    for i in range(
        0, len(splits) - head_split_re_parens, head_split_re_parens + 1
    ):
        v = splits[i]
        ending = splits[i + 1] or ""  # XXX is this correct???
        # print("parse_word_head alts v={!r} ending={!r} alts={}"
        # .format(v, ending, alts))
        if alts and (v == "" and ending):
            assert ending[0] == " "
            alts[-1] += " or" + ending  # endings starts with space
        elif v or ending:
            alts.append((v or "") + (ending or ""))
    last = splits[-1].strip()
    conn = "" if len(splits) < 3 else splits[-2]
    # print("parse_word_head alts last={!r} conn={!r} alts={}"
    # .format(last, conn, alts))
    if (
        alts
        and last
        and (
            last.split()[0] in xlat_head_map
            or (
                conn == " or "
                and (alts[-1] + " or " + last).strip() in xlat_head_map
            )
        )
    ):
        alts[-1] += " or " + last
    elif last:
        alts.append(last)

    # print("parse_word_head alts: {}".format(alts))
    # print(f"{base=}")

    # Process the head alternatives
    canonicals: list[tuple[list[str], list[str]]] = []
    mode: Optional[str] = None
    for alt_i, alt in enumerate(alts):
        alt = alt.strip()
        if alt.startswith("compound form:"):
            mode = "compound-form"
            alt = alt[14:].strip()
        if mode == "compound-form":
            add_related(
                wxr,
                data,
                ["in-compounds"],
                [alt],
                text,
                True,
                is_reconstruction,
                head_group,
                ruby,
            )
            continue
        # For non-first parts, see if it can be treated as tags-only
        if alt_i == 0:
            expanded_alts = [alt]
        else:
            expanded_alts = map_with(xlat_descs_map, [alt])
        # print("EXPANDED_ALTS:", expanded_alts)
        tagsets: Optional[list[tuple[str, ...]]]
        for alt in expanded_alts:
            baseparts = list(m.group(0) for m in re.finditer(word_re, alt))
            if alt_i > 0:
                tagsets, topics = decode_tags(" ".join(baseparts))
                if not any("error-unknown-tag" in x for x in tagsets):
                    data_extend(data, "topics", topics)
                    for tags1 in tagsets:
                        data_extend(data, "tags", tags1)
                    continue

            alt, tags = parse_head_final_tags(
                wxr, language or "MISSING_LANG", alt
            )
            tags = list(tags)  # Make sure we don't modify anything cached
            tags.append("canonical")
            if alt_i == 0 and "," in wxr.wtp.title:  # type:ignore[operator]
                # Kludge to handle article titles/phrases with commas.
                # basepart's regex strips commas, which leads to a
                # canonical form that is the title phrase without a comma.
                # basepart in add_related is almost immediately joined with
                # spaces anyhow. XXX not exactly sure why it's
                # canonicals.append((tags, baseparts)) and not (tags, [alt])
                baseparts = [alt]
            canonicals.append((tags, baseparts))
    for tags, baseparts in canonicals:
        add_related(
            wxr,
            data,
            tags,
            baseparts,
            text,
            len(canonicals) > 1,
            is_reconstruction,
            head_group,
            ruby,
        )

    # Handle parenthesized descriptors for the word form and links to
    # related words
    text = quote_kept_parens(text)
    parens = list(
        m.group(2)
        for m in re.finditer(r"(^|\s)\((([^()]|\([^()]*\))*)\)", text)
    )
    parens.extend(
        m.group(1)
        for m in re.finditer(r"[^\s]\((([^()]|\([^()]*\))*)\)($|\s)", text)
    )
    have_romanization = False
    have_ruby = False
    hiragana = ""
    katakana = ""
    for paren in parens:
        paren = paren.strip()
        if not paren:
            continue
        if paren.startswith("see "):
            continue
        if paren.startswith("U+"):
            continue
        # In some rare cases, strip word that inflects form the form
        # description, e.g. "look through rose-tinted glasses"/English.
        paren = re.sub(r"\s*\(\[[^])]*\]\)", "", paren)

        # If it starts with hiragana or katakana, treat as such form.  Note
        # that each hiragana/katakana character is in separate parentheses,
        # so we must concatenate them.
        try:
            un = unicodedata.name(paren[0]).split()[0]
        except ValueError:
            un = "INVALID"
        if un == "KATAKANA":
            katakana += paren
            have_ruby = True
            continue
        if un == "HIRAGANA":
            hiragana += paren
            have_ruby = True
            continue

        # Parse format ", 16 (Japan, Mainland), 17 (Hong Kong, Taiwan) strokes,"
        # in the middle of the parenthesized expression, e.g. 薄
        def strokes_repl(m: re.Match) -> str:
            strokes1, tags1, strokes2, tags2 = m.groups()
            for strokes, tags in [[strokes1, tags1], [strokes2, tags2]]:
                tags = tags.split(", ")
                tags = list(
                    "Mainland China" if t == "Mainland" else t for t in tags
                )
                tags.append("strokes")
                add_related(
                    wxr,
                    data,
                    tags,
                    [strokes],
                    text,
                    True,
                    is_reconstruction,
                    head_group,
                    ruby,
                )
            return ", "

        paren = re.sub(
            r", (\d+) \(([^()]+)\), (\d+) \(([^()]+)\) strokes, ",
            strokes_repl,
            paren,
        )

        descriptors = map_with(xlat_descs_map, [paren])
        new_desc = []
        for desc in descriptors:
            new_desc.extend(
                map_with(
                    xlat_tags_map,
                    split_at_comma_semi(desc, extra=[", or "], skipped=links),
                )
            )
        prev_tags: Union[list[list[str]], list[tuple[str, ...]], None] = None
        following_tags = None  # Added to prev_tags from previous parenthesized
        # part, e.g. walrus/English
        # "(both nonstandard, proscribed, uncommon)"
        for desc_i, desc in enumerate(new_desc):
            # print("HEAD DESC: {!r}".format(desc))

            # Abort on certain descriptors (assume remaining values are
            # examples or uninteresting, cf. gaan/Navajo, horior/Latin)
            if re.match(r"^(per |e\.g\.$)", desc):
                break

            # If it all consists of CJK characters, add it with the
            # CJK tag.  This is used at least for some Vietnamese
            # words (e.g., ba/Vietnamese)
            try:
                if all(unicodedata.name(x).startswith("CJK ") for x in desc):
                    add_related(
                        wxr,
                        data,
                        ["CJK"],
                        [desc],
                        text,
                        True,
                        is_reconstruction,
                        head_group,
                        ruby,
                    )
                    continue
            except ValueError:
                pass

            # Handle some special cases
            splitdesc = desc.split()
            if (
                len(splitdesc) >= 3
                and splitdesc[1] == "superlative"
                and classify_desc(splitdesc[0]) != "tags"
                and prev_tags
            ):
                # Handle the special case of second comparative after comma,
                # followed by superlative without comma.  E.g.
                # mal/Portuguese/Adv
                for ts in prev_tags:
                    add_related(
                        wxr,
                        data,
                        ts,
                        [splitdesc[0]],
                        text,
                        True,
                        is_reconstruction,
                        head_group,
                        ruby,
                    )
                desc = " ".join(splitdesc[1:])
            elif (
                len(splitdesc) == 2
                and splitdesc[0] in ("also", "and")
                and prev_tags
                and classify_desc(splitdesc[1]) != "tags"
            ):
                # Sometimes alternative forms are prefixed with "also" or
                # "and"
                for ts in prev_tags:
                    add_related(
                        wxr,
                        data,
                        ts,
                        [splitdesc[1]],
                        text,
                        True,
                        is_reconstruction,
                        head_group,
                        ruby,
                    )
                continue
            elif len(splitdesc) >= 2 and splitdesc[0] in ("including",):
                continue

            # If only one word, assume it is comma-separated alternative
            # to the previous one
            if " " not in desc:
                cls = classify_desc(desc)
                if cls != "tags":
                    if prev_tags:
                        # Assume comma-separated alternative to previous one
                        for ts in prev_tags:
                            add_related(
                                wxr,
                                data,
                                ts,
                                [desc],
                                text,
                                True,
                                is_reconstruction,
                                head_group,
                                ruby,
                            )
                        continue
                    elif distw(titleparts, desc) <= 0.5:
                        # Similar to head word, assume a dialectal variation to
                        # the base form.  Cf. go/Alemannic German/Verb
                        add_related(
                            wxr,
                            data,
                            ["alternative"],
                            [desc],
                            text,
                            True,
                            is_reconstruction,
                            head_group,
                            ruby,
                        )
                        continue
                    elif (
                        cls in ("romanization", "english")
                        and not have_romanization
                        and classify_desc(titleword) == "other"
                        and not (
                            "categories" in data and desc in data["categories"]
                        )
                    ):
                        # Assume it to be a romanization
                        add_romanization(
                            wxr,
                            data,
                            desc,
                            text,
                            is_reconstruction,
                            head_group,
                            ruby,
                        )
                        have_romanization = True
                        continue

            m = re.match(r"^(\d+) strokes?$", desc)
            if m:
                # Special case, used to give #strokes for Han characters
                add_related(
                    wxr,
                    data,
                    ["strokes"],
                    [m.group(1)],
                    text,
                    True,
                    is_reconstruction,
                    head_group,
                    ruby,
                )
                continue

            # See if it is radical+strokes
            m = re.match(
                r"^([\u2F00-\u2FDF\u2E80-\u2EFF\U00018800-\U00018AFF"
                r"\uA490-\uA4CF\u4E00-\u9FFF]\+\d+)"
                r"( in (Japanese|Chinese|traditional Chinese|"
                r"simplified Chinese))?$",
                desc,
            )
            if m:
                # Special case, used to give radical + strokes for Han
                # characters
                radical_strokes = m.group(1)
                lang = m.group(3)
                t = ["radical+strokes"]
                if lang:
                    t.extend(lang.split())
                add_related(
                    wxr,
                    data,
                    t,
                    [radical_strokes],
                    text,
                    True,
                    is_reconstruction,
                    head_group,
                    ruby,
                )
                prev_tags = None
                following_tags = None
                continue

            # See if it indicates historical Katakana ortography (←) or
            # just otherwise katakana/hiragana form
            m = re.match(r"←\s*|kana\s+", desc)
            if m:
                if desc.startswith("←"):
                    t1 = "historical "
                else:
                    t1 = ""
                x = desc[m.end() :]
                if x.endswith("?"):
                    x = x[:-1]
                    # XXX should we add a tag indicating uncertainty?
                if x:
                    name = unicodedata.name(x[0])
                    if name.startswith("HIRAGANA "):
                        desc = t1 + "hiragana " + x
                    elif name.startswith("KATAKANA "):
                        desc = t1 + "katakana " + x

            # See if it is "n strokes in Chinese" or similar
            m = re.match(
                r"(\d+) strokes in (Chinese|Japanese|"
                r"traditional Chinese|simplified Chinese)$",
                desc,
            )
            if m:
                # Special case, used to give just strokes for some Han chars
                strokes = m.group(1)
                lang = m.group(2)
                t = ["strokes"]
                t.extend(lang.split())
                add_related(
                    wxr,
                    data,
                    t,
                    [strokes],
                    text,
                    True,
                    is_reconstruction,
                    head_group,
                    ruby,
                )
                prev_tags = None
                following_tags = None
                continue

            # American Sign Language has images (or requests for image)
            # as heads, + this ASL gloss after.
            m2 = re.search(r"\(ASL gloss:\s+(.*)\)", text)
            if m2:
                add_related(
                    wxr,
                    data,
                    ["ASL-gloss"],
                    [m2.group(1)],
                    text,
                    True,
                    is_reconstruction,
                    head_group,
                    ruby,
                )
                continue

            parts = list(m.group(0) for m in re.finditer(word_re, desc))
            if not parts:
                prev_tags = None
                following_tags = None
                continue

            # Check for certain language-specific header part starts that
            # modify
            if len(parts) == 2 and language in lang_specific_head_map:
                ht = lang_specific_head_map[language]
                if parts[0] in ht:
                    rem_tags, add_tags = ht[parts[0]]
                    new_prev_tags1: list[list[str]] = []
                    tags2: Union[tuple[str, ...], list[str]]
                    for tags2 in prev_tags or [()]:
                        if rem_tags is True:  # Remove all old tags
                            tsets = set()
                        else:
                            tsets = set(tags2) - set(rem_tags.split())
                        tsets = tsets | set(add_tags.split())
                        tags = list(sorted(tsets))
                        add_related(
                            wxr,
                            data,
                            tags,
                            [parts[1]],
                            text,
                            True,
                            is_reconstruction,
                            head_group,
                            ruby,
                        )
                        new_prev_tags1.append(tags)
                    prev_tags = new_prev_tags1
                    following_tags = None
                    continue

            # Handle the special case of descriptors that are parenthesized,
            # e.g., (archaic or Scotland)
            m = re.match(r"\(([^)]+)\)\s+(.*)$", desc)
            if m is not None and classify_desc(m.group(1)) == "tags":
                tagpart = m.group(1)
                related = [m.group(2)]
                tagsets, topics = decode_tags(tagpart, no_unknown_starts=True)
                if topics:
                    wxr.wtp.debug(
                        "parenthized head part {!r} contains topics: {}".format(
                            tagpart, topics
                        ),
                        sortid="form_descriptions/1647",
                    )
            elif m is not None and re.match(r"in the sense ", m.group(1)):
                # Handle certain ignored cases
                # e.g. bord/Danish: in the sense "plank"
                related = [m.group(2)]
                tagsets = [()]
            else:
                # Normal parsing of the descriptor
                alt_related = None
                alt_tagsets = None
                tagsets = None
                for i in range(len(parts), 0, -1):
                    related = parts[i:]
                    tagparts = parts[:i]
                    # print("  i={} related={} tagparts={}"
                    #       .format(i, related, tagparts))
                    tagsets, topics = decode_tags(
                        " ".join(tagparts), no_unknown_starts=True
                    )
                    # print("tagparts={!r} tagsets={} topics={} related={} "
                    #       "alt_related={} distw={:.2f}"
                    #       .format(tagparts, tagsets, topics, related,
                    #               alt_related,
                    #               distw(titleparts, parts[i - 1])))
                    if (
                        topics
                        or not tagsets
                        or any("error-unknown-tag" in x for x in tagsets)
                    ):
                        if alt_related is not None:
                            break
                        continue
                    if (
                        i > 1
                        and len(parts[i - 1]) >= 4
                        and distw(titleparts, parts[i - 1]) <= 0.4
                    ):
                        alt_related = related
                        alt_tagsets = tagsets
                        continue
                    alt_related = None
                    alt_tagsets = None
                    break
                else:
                    if alt_related is None:
                        # Check if the parenthesized part is likely a
                        # romanization
                        if (
                            (have_ruby or classify_desc(base) == "other")
                            and classify_desc(paren) == "romanization"
                            and not (
                                "categories" in data
                                and desc in data["categories"]
                            )
                        ):
                            for r in split_at_comma_semi(
                                paren, extra=[" or "], skipped=links
                            ):
                                add_romanization(
                                    wxr,
                                    data,
                                    r,
                                    text,
                                    is_reconstruction,
                                    head_group,
                                    ruby,
                                )
                            have_romanization = True
                            continue
                        tagsets = [("error-unrecognized-head-form",)]
                        wxr.wtp.debug(
                            "unrecognized head form: {}".format(desc),
                            sortid="form_descriptions/1698",
                        )
                        continue

                if alt_related is not None:
                    related = alt_related
                    tagsets = alt_tagsets

            # print("FORM END: tagsets={} related={}".format(tagsets, related))
            if not tagsets:
                continue

            assert isinstance(related, (list, tuple))
            related_str = " ".join(related)
            if "or" in titleparts:
                alts = [related_str]
            else:
                alts = split_at_comma_semi(
                    related_str, separators=[" or "], skipped=links
                )
                if not alts:
                    alts = [""]
            for related_str in alts:
                if related_str:
                    if prev_tags and (
                        all(
                            all(
                                t in ["nonstandard", "dialectal"]
                                or valid_tags[t] == "dialect"
                                for t in tags
                            )
                            for ts in tagsets
                        )
                        or (
                            any("participle" in ts for ts in prev_tags)
                            and all(
                                "attributive" in ts
                                or any(valid_tags[t] == "gender" for t in ts)
                                for ts in tagsets
                            )
                        )
                    ):
                        # Merged with previous tags.  Don't update previous
                        # tags here; cf. burn/English/Verb
                        for tags_l in tagsets:
                            for ts in prev_tags:
                                tags_l1 = list(sorted(set(tags_l) | set(ts)))
                                add_related(
                                    wxr,
                                    data,
                                    tags_l1,
                                    [related_str],
                                    text,
                                    True,
                                    is_reconstruction,
                                    head_group,
                                    ruby,
                                )
                    else:
                        # Not merged with previous tags
                        for tags_l in tagsets:
                            if following_tags is not None:
                                for ts in following_tags:
                                    tags_l1 = list(
                                        sorted(set(tags_l) | set(ts))
                                    )
                                    add_related(
                                        wxr,
                                        data,
                                        tags_l1,
                                        [related_str],
                                        text,
                                        True,
                                        is_reconstruction,
                                        head_group,
                                        ruby,
                                    )
                            else:
                                ret = add_related(
                                    wxr,
                                    data,
                                    tags_l,
                                    [related_str],
                                    text,
                                    True,
                                    is_reconstruction,
                                    head_group,
                                    ruby,
                                )
                                if ret is not None:
                                    following_tags = ret
                        prev_tags = tagsets
                else:
                    if desc_i < len(new_desc) - 1 and all(
                        "participle" in ts or "infinitive" in ts
                        for ts in tagsets
                    ):
                        # Interpret it as a standalone form description
                        # in the middle, probably followed by forms or
                        # language-specific descriptors. cf. drikke/Danish
                        new_prev_tags2 = []
                        for ts1 in prev_tags or [()]:
                            for ts2 in tagsets:
                                ts = tuple(sorted(set(ts1) | set(ts2)))
                                new_prev_tags2.append(ts)
                        prev_tags = new_prev_tags2
                        continue
                    for tags in tagsets:
                        data_extend(data, "tags", tags)
                    prev_tags = tagsets
                    following_tags = None

    # Finally, if we collected hirakana/katakana, add them now
    if hiragana:
        add_related(
            wxr,
            data,
            ["hiragana"],
            [hiragana],
            text,
            True,
            is_reconstruction,
            head_group,
            ruby,
        )
    if katakana:
        add_related(
            wxr,
            data,
            ["katakana"],
            [katakana],
            text,
            True,
            is_reconstruction,
            head_group,
            ruby,
        )

    # XXX check if this is actually relevant, tags in word root data
    # is extremely rare (not sure where they slip through).
    tags = data.get("tags", [])  # type:ignore
    if tags:
        # wxr.wtp.debug(
        #     f"Tags appear in word root data: {data['tags']=}",  # type:ignore
        #     sortid="form_descriptions/2620/20240606",
        # )  # Messes up tests.
        data["tags"] = list(sorted(set(tags)))  # type:ignore


def parse_sense_qualifier(
    wxr: WiktextractContext, text: str, data: Union[SenseData, LinkageData]
) -> None:
    """Parses tags or topics for a sense or some other data.  The values are
    added into the dictionary ``data``."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_sense_qualifier:", text)
    if re.match(r"\([^()]+\)$", text):
        text = text[1:-1]
    if re.match(r'"[^"]+"$', text):
        text = text[1:-1]
    lst = map_with(xlat_descs_map, [text])
    sense_tags: list[str] = []
    for text in lst:
        for semi in split_at_comma_semi(text):
            if not semi:
                continue
            orig_semi = semi
            idx = semi.find(":")
            if idx >= 0:
                semi = semi[:idx]
            cls = classify_desc(semi, allow_unknown_tags=True)
            # print("parse_sense_qualifier: classify_desc: {} -> {}"
            #       .format(semi, cls))
            if cls == "tags":
                tagsets, topics = decode_tags(semi)
                data_extend(data, "topics", topics)
                # XXX should think how to handle distinct options better,
                # e.g., "singular and plural genitive"; that can't really be
                # done with changing the calling convention of this function.
                # Should split sense if more than one category of tags differs.
                for tags in tagsets:
                    sense_tags.extend(tags)
            elif cls == "taxonomic":
                if re.match(r"×[A-Z]", semi):
                    sense_tags.append("extinct")
                    semi = semi[1:]
                data["taxonomic"] = semi
            elif cls == "english":
                if "qualifier" in data and data["qualifier"] != orig_semi:
                    data["qualifier"] += "; " + orig_semi
                else:
                    data["qualifier"] = orig_semi
            else:
                wxr.wtp.debug(
                    "unrecognized sense qualifier: {}".format(text),
                    sortid="form_descriptions/1831",
                )
    sense_tags = list(sorted(set(sense_tags)))
    data_extend(data, "tags", sense_tags)


def parse_pronunciation_tags(
    wxr: WiktextractContext, text: str, data: SoundData
) -> None:
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    text = text.strip()
    if not text:
        return
    cls = classify_desc(text)
    notes = []
    if cls == "tags":
        tagsets, topics = decode_tags(text)
        data_extend(data, "topics", topics)
        for tagset in tagsets:
            for t in tagset:
                if " " in t:
                    notes.append(t)
                else:
                    data_append(data, "tags", t)
    else:
        notes.append(text)
    if notes:
        data["note"] = "; ".join(notes)


def parse_translation_desc(
    wxr: WiktextractContext, lang: str, text: str, tr: TranslationData
) -> None:
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(lang, str)  # The language of ``text``
    assert isinstance(text, str)
    assert isinstance(tr, dict)
    # print("parse_translation_desc:", text)

    # Process all parenthesized parts from the translation item
    note = None
    restore_beginning = ""
    restore_end = ""
    while True:
        beginning = False
        # See if we can find a parenthesized expression at the end
        m = re.search(r"\s*\((([^()]|\([^()]+\))+)\)\.?$", text)
        if m:
            par = m.group(1)
            text = text[: m.start()]
            if par.startswith(("literally ", "lit.")):
                continue  # Not useful for disambiguation in many idioms
        else:
            # See if we can find a parenthesized expression at the start
            m = re.match(r"^\^?\((([^()]|\([^()]+\))+)\):?(\s+|$)", text)
            if m:
                par = m.group(1)
                text = text[m.end() :]
                beginning = True
                if re.match(r"^(\d|\s|,| or | and )+$", par):
                    # Looks like this beginning parenthesized expression only
                    # contains digits or their combinations.  We assume such
                    # to be sense descriptions if no sense has been selected,
                    # or otherwise just ignore them.
                    if not tr.get("sense"):
                        tr["sense"] = par
                    continue
            else:
                # See if we can find a parenthesized expression in the middle.
                # Romanizations are sometimes between word and gender marker,
                # e.g. wife/English/Tr/Yiddish.
                m = re.search(r"\s+\((([^()]|\([^()]+\))+)\)", text)
                if m:
                    par = m.group(1)
                    text = text[: m.start()] + text[m.end() :]
                else:
                    # No more parenthesized expressions - break out of the loop
                    break

        # Some cleanup of artifacts that may result from skipping some templates
        # in earlier stages
        if par.startswith(": "):
            par = par[2:]
        if par.endswith(","):
            par = par[:-1]
        if re.match(r'^[“"]([^“”"]*)[“”"]$', par):
            par = par[1:-1]
        par = par.strip()

        # Check for special script pronunciation followed by romanization,
        # used in many Asian languages.
        lst = par.split(", ")
        if len(lst) == 2:
            a, r = lst
            if classify_desc(a) == "other":
                cls = classify_desc(r)
                # print("parse_translation_desc: r={} cls={}".format(r, cls))
                if cls == "romanization" or (
                    cls == "english" and len(r.split()) == 1 and r[0].islower()
                ):
                    if tr.get("alt") and tr.get("alt") != a:
                        wxr.wtp.debug(
                            'more than one value in "alt": {} vs. {}'.format(
                                tr["alt"], a
                            ),
                            sortid="form_descriptions/1930",
                        )
                    tr["alt"] = a
                    if tr.get("roman") and tr.get("roman") != r:
                        wxr.wtp.debug(
                            'more than one value in "roman": '
                            "{} vs. {}".format(tr["roman"], r),
                            sortid="form_descriptions/1936",
                        )
                    tr["roman"] = r
                    continue

        # Check for certain comma-separated tags combined with English text
        # at the beginning or end of a comma-separated parenthesized list
        while len(lst) > 1:
            cls = classify_desc(lst[0])
            if cls == "tags":
                tagsets, topics = decode_tags(lst[0])
                for t in tagsets:
                    data_extend(tr, "tags", t)
                data_extend(tr, "topics", topics)
                lst = lst[1:]
                continue
            cls = classify_desc(lst[-1])
            if cls == "tags":
                tagsets, topics = decode_tags(lst[-1])
                for t in tagsets:
                    data_extend(tr, "tags", t)
                data_extend(tr, "topics", topics)
                lst = lst[:-1]
                continue
            break
        par = ", ".join(lst)

        if not par:
            continue
        if re.search(tr_ignored_parens_re, par):
            continue
        if par.startswith("numeral:"):
            par = par[8:].strip()

        # Classify the part in parenthesis and process accordingly
        cls = classify_desc(par)
        # print("parse_translation_desc classify: {!r} -> {}"
        #       .format(par, cls))
        if par == text:
            pass
        if par == "f":
            data_append(tr, "tags", "feminine")
        elif par == "m":
            data_append(tr, "tags", "masculine")
        elif cls == "tags":
            tagsets, topics = decode_tags(par)
            for tags in tagsets:
                data_extend(tr, "tags", tags)
            data_extend(tr, "topics", topics)
        elif cls == "english":
            # If the text contains any of certain grammatical words, treat it
            # as a "note" instead of "english"
            if re.search(tr_note_re, par):
                if par.endswith(":"):
                    par = par[:-1]
                if par not in ("see entry for forms",):
                    if note:
                        note = note + ";" + par
                    else:
                        note = par
            else:
                # There can be more than one parenthesized english item, see
                # e.g. Aunt/English/Translations/Tamil
                if tr.get("english"):
                    tr["english"] += "; " + par
                else:
                    tr["english"] = par
        elif cls == "romanization":
            # print("roman text={!r} text cls={}"
            #       .format(text, classify_desc(text)))
            if classify_desc(text) in (
                "english",
                "romanization",
            ) and lang not in ("Egyptian",):
                if beginning:
                    restore_beginning += "({}) ".format(par)
                else:
                    restore_end = " ({})".format(par) + restore_end
            else:
                if tr.get("roman"):
                    wxr.wtp.debug(
                        'more than one value in "roman": {} vs. {}'.format(
                            tr["roman"], par
                        ),
                        sortid="form_descriptions/2013",
                    )
                tr["roman"] = par
        elif cls == "taxonomic":
            if tr.get("taxonomic"):
                wxr.wtp.debug(
                    'more than one value in "taxonomic": {} vs. {}'.format(
                        tr["taxonomic"], par
                    ),
                    sortid="form_descriptions/2019",
                )
            if re.match(r"×[A-Z]", par):
                data_append(tr, "tags", "extinct")
                par = par[1:]
            tr["taxonomic"] = par
        elif cls == "other":
            if tr.get("alt"):
                wxr.wtp.debug(
                    'more than one value in "alt": {} vs. {}'.format(
                        tr["alt"], par
                    ),
                    sortid="form_descriptions/2028",
                )
            tr["alt"] = par
        else:
            wxr.wtp.debug(
                "parse_translation_desc unimplemented cls {}: {}".format(
                    cls, par
                ),
                sortid="form_descriptions/2033",
            )

    # Check for gender indications in suffix
    text, final_tags = parse_head_final_tags(wxr, lang, text)
    data_extend(tr, "tags", final_tags)

    # Restore those parts that we did not want to remove (they are often
    # optional words or words that are always used with the given translation)
    text = restore_beginning + text + restore_end

    if note:
        tr["note"] = note.strip()
    if text and text not in ignored_translations:
        tr["word"] = text.strip()

    # Sometimes gender seems to be at the end of "roman" field, see e.g.
    # fire/English/Noun/Translations/Egyptian (for "oxidation reaction")
    roman = tr.get("roman")
    if roman:
        if roman.endswith(" f"):
            data_append(tr, "tags", "feminine")
            tr["roman"] = roman[:-2].strip()
        elif roman.endswith(" m"):
            data_append(tr, "tags", "masculine")
            tr["roman"] = roman[:-2].strip()

    # If the word now has "english" field but no "roman" field, and
    # the word would be classified "other" (generally non-latin
    # characters), and the value in "english" is only one lowercase
    # word, move it to "roman".  This happens semi-frequently when the
    # translation is transliterated the same as some English word.
    roman = tr.get("roman")
    english = tr.get("english")
    if english and not roman and "word" in tr:
        cls = classify_desc(tr["word"])
        if cls == "other" and " " not in english and english[0].islower():
            del tr["english"]
            tr["roman"] = english

    # If the entry now has both tr["roman"] and tr["word"] and they have
    # the same value, delete tr["roman"] (e.g., man/English/Translations
    # Evenki)
    if tr.get("word") and tr.get("roman") == tr.get("word"):
        del tr["roman"]


def parse_alt_or_inflection_of(
    wxr: WiktextractContext, gloss: str, gloss_template_args: set[str]
) -> Optional[tuple[list[str], Optional[list[AltOf]]]]:
    """Tries to parse an inflection-of or alt-of description.  If successful,
    this returns (tags, alt-of/inflection-of-dict).  If the description cannot
    be parsed, this returns None.  This may also return (tags, None) when the
    gloss describes a form (or some other tags were extracted from it), but
    there was no alt-of/form-of/synonym-of word."""
    # print("parse_alt_or_inflection_of: {!r}".format(gloss))
    # Occasionally inflection_of/alt_of have "A(n) " etc. at the beginning.

    # Never interpret a gloss that is equal to the word itself as a tag
    # (e.g., instrumental/Romanian, instrumental/Spanish).
    if gloss.lower() == wxr.wtp.title.lower() or (  # type:ignore[union-attr]
        len(gloss) >= 5 and distw([gloss.lower()], wxr.wtp.title.lower()) < 0.2  # type:ignore[union-attr]
    ):
        return None

    # First try parsing it as-is
    parsed = parse_alt_or_inflection_of1(wxr, gloss, gloss_template_args)
    if parsed is not None:
        return parsed

    # Next try parsing it with the first character converted to lowercase if
    # it was previously uppercase.
    if gloss and gloss[0].isupper():
        gloss = gloss[0].lower() + gloss[1:]
        parsed = parse_alt_or_inflection_of1(wxr, gloss, gloss_template_args)
        if parsed is not None:
            return parsed

    return None


# These tags are not allowed in alt-or-inflection-of parsing
alt_infl_disallowed: set[str] = set(
    [
        "error-unknown-tag",
        "place",  # Not in inflected forms and causes problems e.g. house/English
    ]
)


def parse_alt_or_inflection_of1(
    wxr: WiktextractContext, gloss: str, gloss_template_args: set[str]
) -> Optional[tuple[list[str], Optional[list[AltOf]]]]:
    """Helper function for parse_alt_or_inflection_of.  This handles a single
    capitalization."""
    if not gloss or not gloss.strip():
        return None

    # Prevent some common errors where we would parse something we shouldn't
    if re.search(r"(?i)form of address ", gloss):
        return None

    gloss = re.sub(r"only used in [^,]+, ", "", gloss)

    # First try all formats ending with "of" (or other known last words that
    # can end a form description)
    matches = list(re.finditer(r"\b(of|for|by|as|letter|number) ", gloss))
    m: Optional[re.Match]
    for m in reversed(matches):
        desc = gloss[: m.end()].strip()
        base = gloss[m.end() :].strip()
        tagsets, topics = decode_tags(desc, no_unknown_starts=True)
        if not topics and any(
            not (alt_infl_disallowed & set(ts)) for ts in tagsets
        ):
            # Successfully parsed, including "of" etc.
            tags: list[str] = []
            # If you have ("Western-Armenian", ..., "form-of") as your
            # tag set, it's most probable that it's something like
            # "Western Armenian form of խոսել (xosel)", which should
            # get "alt-of" instead of "form-of" (inflection).
            # խօսիլ/Armenian
            for ts_t in tagsets:
                if "form-of" in ts_t and any(
                    valid_tags.get(tk) == "dialect" for tk in ts_t
                ):
                    ts_s = (set(ts_t) - {"form-of"}) | {"alt-of"}
                else:
                    ts_s = set(ts_t)
                if not (alt_infl_disallowed & ts_s):
                    tags.extend(ts_s)
            if (
                "alt-of" in tags
                or "form-of" in tags
                or "synonym-of" in tags
                or "compound-of" in tags
            ):
                break
        if m.group(1) == "of":
            # Try parsing without the final "of".  This is commonly used in
            # various form-of expressions.
            desc = gloss[: m.start()]
            base = gloss[m.end() :]
            tagsets, topics = decode_tags(desc, no_unknown_starts=True)
            # print("ALT_OR_INFL: desc={!r} base={!r} tagsets={} topics={}"
            # .format(desc, base, tagsets, topics))
            if not topics and any(
                not (alt_infl_disallowed & set(t)) for t in tagsets
            ):
                tags = []
                for t in tagsets:
                    if not (alt_infl_disallowed & set(t)):
                        tags.extend(t)
                # It must have at least one tag from form_of_tags
                if set(tags) & form_of_tags:
                    # Accept this as form-of
                    tags.append("form-of")
                    break
                if set(tags) & alt_of_tags:
                    # Accept this as alt-of
                    tags.append("alt-of")
                    break

    else:
        # Did not find a form description based on last word; see if the
        # whole description is tags
        tagsets, topics = decode_tags(gloss, no_unknown_starts=True)
        if not topics and any(
            not (alt_infl_disallowed & set(ts)) and form_of_tags & set(ts)
            for ts in tagsets
        ):
            tags = []
            for ts in tagsets:
                if not (alt_infl_disallowed & set(ts)) and form_of_tags & set(
                    ts
                ):
                    tags.extend(ts)
            base = ""
        else:
            return None

    # kludge for Spanish (again): 'x of [word] combined with [clitic]'
    m = re.search(r"combined with \w+$", base)
    if m:
        tagsets, topics = decode_tags(m.group(0), no_unknown_starts=True)
        if not topics:
            for ts in tagsets:
                tags.extend(ts)
            base = base[: m.start()]

    # It is fairly common for form_of glosses to end with something like
    # "ablative case" or "in instructive case".  Parse that ending.
    base = base.strip()
    lst = base.split()
    # print("parse_alt_or_inflection_of: lst={}".format(lst))
    if len(lst) >= 3 and lst[-1] in ("case", "case."):
        node = valid_sequences.children.get(lst[-2])
        if node and node.end:
            for s in node.tags:
                tags.extend(s.split(" "))
            lst = lst[:-2]
            if lst[-1] == "in" and len(lst) > 1:
                lst = lst[:-1]

    # Eliminate empty and duplicate tags
    tags = list(sorted(set(t for t in tags if t)))

    # Clean up some extra stuff from the linked word, separating the text
    # into ``base`` (the linked word) and ``extra`` (additional information,
    # such as English translation or clarifying word sense information).
    orig_base = base
    base = re.sub(alt_of_form_of_clean_re, "", orig_base)
    base = re.sub(r" [(⟨][^()]*[)⟩]", "", base)  # Remove all (...) groups
    extra = orig_base[len(base) :]
    extra = re.sub(r"^[- :;.,，—]+", "", extra)
    if extra.endswith(".") and extra.count(".") == 1:
        extra = extra[:-1].strip()
    m = re.match(r"^\(([^()]*)\)$", extra)
    if m:
        extra = m.group(1)
    else:
        # These weird backets used in "slash mark"
        m = re.match(r"^⟨([^()]*)⟩$", extra)
        if m:
            extra = m.group(1)
    m = re.match(r'^[“"]([^"“”]*)["”]$', extra)
    if m:
        extra = m.group(1)
    # Note: base might still contain comma-separated values and values
    # separated by "and"
    base = base.strip()
    if base.endswith(",") and len(base) > 2:
        base = base[:-1].strip()
    while (
        base.endswith(".")
        and not wxr.wtp.page_exists(base)
        and base not in gloss_template_args
    ):
        base = base[:-1].strip()
    if base.endswith('(\u201cconjecture")'):
        base = base[:-14].strip()
        tags.append("conjecture")
    while (
        base.endswith(".")
        and not wxr.wtp.page_exists(base)
        and base not in gloss_template_args
    ):
        base = base[:-1].strip()
    if (
        base.endswith(".")
        and base not in gloss_template_args
        and base[:-1] in gloss_template_args
    ):
        base = base[:-1]
    base = base.strip()
    if not base:
        return tags, None

    # Kludge: Spanish verb forms seem to have a dot added at the end.
    # Remove it; we know of no Spanish verbs ending with a dot.
    language = wxr.wtp.section
    pos = wxr.wtp.subsection
    # print("language={} pos={} base={}".format(language, pos, base))
    if (
        base.endswith(".")
        and len(base) > 1
        and base[-2].isalpha()
        and (language == "Spanish" and pos == "Verb")
    ):
        base = base[:-1]

    # Split base to alternatives when multiple alternatives provided
    parts = split_at_comma_semi(base, extra=[" / ", "／", r" \+ "])
    titleword = re.sub(r"^Reconstruction:[^/]*/", "", wxr.wtp.title or "")
    if (
        len(parts) <= 1
        or base.startswith("/")
        or base.endswith("/")
        or "/" in titleword
    ):
        parts = [base]
    # Split base to alternatives when of form "a or b" and "a" and "b" are
    # similar (generally spelling variants of the same word or similar words)
    if len(parts) == 1:
        pp = base.split()
        if len(pp) == 3 and pp[1] == "or" and distw([pp[0]], pp[2]) < 0.4:
            parts = [pp[0], pp[2]]

    # Create form-of/alt-of entries based on the extracted data
    dt_lst: list[AltOf] = []
    for p in parts:
        # Check for some suspicious base forms
        m = re.search(r"[.,] |[{}()]", p)
        if m and not wxr.wtp.page_exists(p):
            wxr.wtp.debug(
                "suspicious alt_of/form_of with {!r}: {}".format(m.group(0), p),
                sortid="form_descriptions/2278",
            )
        if p.startswith("*") and len(p) >= 3 and p[1].isalpha():
            p = p[1:]
        dt: AltOf = {"word": p}
        if extra:
            dt["extra"] = extra
        dt_lst.append(dt)
    # print("alt_or_infl_of returning tags={} lst={} base={!r}"
    #       .format(tags, lst, base))
    return tags, dt_lst


@functools.lru_cache(maxsize=65536)
def classify_desc(
    desc: str, allow_unknown_tags=False, no_unknown_starts=False
) -> str:
    """Determines whether the given description is most likely tags, english,
    a romanization, or something else.  Returns one of: "tags", "english",
    "romanization", or "other".  If ``allow_unknown_tags`` is True, then
    allow "tags" classification even when the only tags are those starting
    with a word in allowed_unknown_starts."""
    assert isinstance(desc, str)
    # Empty and whitespace-only strings are treated as "other"
    desc = desc.strip()
    if not desc:
        return "other"

    normalized_desc = unicodedata.normalize("NFKD", desc)

    # If it can be fully decoded as tags without errors, treat as tags
    tagsets, topics = decode_tags(desc, no_unknown_starts=no_unknown_starts)
    for tagset in tagsets:
        assert isinstance(tagset, (list, tuple, set))
        if "error-unknown-tag" not in tagset and (
            topics or allow_unknown_tags or any(" " not in x for x in tagset)
        ):
            return "tags"

    # Check if it looks like the taxonomic name of a species
    if desc in known_species:
        return "taxonomic"
    desc1 = re.sub(r"^×([A-Z])", r"\1", desc)
    desc1 = re.sub(r"\s*×.*", "", desc1)
    lst = desc1.split()
    if len(lst) > 1 and len(lst) <= 5 and lst[0] in known_firsts:
        have_non_english = 1 if lst[0].lower() not in english_words else 0
        for x in lst[1:]:
            if x in ("A", "B", "C", "D", "E", "F", "I", "II", "III", "IV", "V"):
                continue
            if x[0].isupper():
                break
            if x not in english_words:
                have_non_english += 1
        else:
            # Starts with known taxonomic term, does not contain uppercase
            # words (except allowed letters) and at least one word is not
            # English
            if have_non_english >= len(lst) - 1 and have_non_english > 0:
                return "taxonomic"

    # If all words are in our English dictionary, interpret as English.
    # [ -~] is regex black magic, "all characters from space to tilde"
    # in ASCII. Took me a while to figure out.
    if re.match(r"^[ -~―—“”…'‘’ʹ€]+$", normalized_desc) and len(desc) > 1:
        if desc in english_words and desc[0].isalpha():
            return "english"  # Handles ones containing whitespace
        desc1 = re.sub(
            tokenizer_fixup_re, lambda m: tokenizer_fixup_map[m.group(0)], desc
        )
        tokens = tokenizer.tokenize(desc1)
        if not tokens:
            return "other"
        lst_bool = list(
            x not in not_english_words
            and
            # not x.isdigit() and
            (
                x in english_words
                or x.lower() in english_words
                or x in known_firsts
                or x[0].isdigit()
                or
                # (x[0].isupper() and x.find("-") < 0 and x.isascii()) or
                (
                    x.endswith("s") and len(x) >= 4 and x[:-1] in english_words
                )  # Plural
                or (
                    x.endswith("ies")
                    and len(x) >= 5
                    and x[:-3] + "y" in english_words
                )  # E.g. lily - lilies
                or (
                    x.endswith("ing")
                    and len(x) >= 5
                    and x[:-3] in english_words
                )  # E.g. bring - bringing
                or (
                    x.endswith("ing")
                    and len(x) >= 5
                    and x[:-3] + "e" in english_words
                )  # E.g., tone - toning
                or (
                    x.endswith("ed") and len(x) >= 5 and x[:-2] in english_words
                )  # E.g. hang - hanged
                or (
                    x.endswith("ed")
                    and len(x) >= 5
                    and x[:-2] + "e" in english_words
                )  # E.g. atone - atoned
                or (x.endswith("'s") and x[:-2] in english_words)
                or (x.endswith("s'") and x[:-2] in english_words)
                or (
                    x.endswith("ise")
                    and len(x) >= 5
                    and x[:-3] + "ize" in english_words
                )
                or (
                    x.endswith("ised")
                    and len(x) >= 6
                    and x[:-4] + "ized" in english_words
                )
                or (
                    x.endswith("ising")
                    and len(x) >= 7
                    and x[:-5] + "izing" in english_words
                )
                or (
                    re.search(r"[-/]", x)
                    and all(
                        ((y in english_words and len(y) > 2) or not y)
                        for y in re.split(r"[-/]", x)
                    )
                )
            )
            for x in tokens
        )
        cnt = lst_bool.count(True)
        rejected_words = tuple(
            x for i, x in enumerate(tokens) if not lst_bool[i]
        )
        if (
            any(
                lst_bool[i] and x[0].isalpha() and len(x) > 1
                for i, x in enumerate(tokens)
            )
            and not desc.startswith("-")
            and not desc.endswith("-")
            and re.search(r"\w+", desc)
            and (
                cnt == len(lst_bool)
                or (
                    any(
                        lst_bool[i] and len(x) > 3 for i, x in enumerate(tokens)
                    )
                    and cnt >= len(lst_bool) - 1
                )
                or cnt / len(lst_bool) >= 0.8
                or (
                    all(x in potentially_english_words for x in rejected_words)
                    and cnt / len(lst_bool) >= 0.50
                )
            )
        ):
            return "english"
    # Some translations have apparent pronunciation descriptions in /.../
    # which we'll put in the romanization field (even though they probably are
    # not exactly romanizations).
    if desc.startswith("/") and desc.endswith("/"):
        return "romanization"
    # If all characters are in classes that could occur in romanizations,
    # treat as romanization
    classes = list(
        unicodedata.category(x) if x not in ("-", ",", ":", "/", '"') else "OK"
        for x in normalized_desc
    )
    classes1 = []
    num_latin = 0
    num_greek = 0
    # part = ""
    # for ch, cl in zip(normalized_desc, classes):
    #     part += f"{ch}({cl})"
    # print(part)
    for ch, cl in zip(normalized_desc, classes):
        if ch in (
            "'",  # ' in Arabic, / in IPA-like parenthesized forms
            ".",  # e.g., "..." in translations
            ";",
            ":",
            "!",
            "‘",
            "’",
            '"',
            "“",
            "”",
            "/",
            "?",
            "…",  # alternative to "..."
            "⁉",  # 見る/Japanese automatic transcriptions...
            "？",
            "！",
            "⁻",  # superscript -, used in some Cantonese roman, e.g. "we"
            "ʔ",
            "ʼ",
            "ʾ",
            "ʹ",
        ):  # ʹ e.g. in understand/English/verb Russian transl
            classes1.append("OK")
            continue
        if cl not in ("Ll", "Lu"):
            classes1.append(cl)
            continue
        try:
            name = unicodedata.name(ch)
            first = name.split()[0]
            if first == "LATIN":
                num_latin += 1
            elif first == "GREEK":
                num_greek += 1
            elif first == "COMBINING":  # Combining diacritic
                cl = "OK"
            elif re.match(non_latin_scripts_re, name):
                cl = "NO"  # Not acceptable in romanizations
        except ValueError:
            cl = "NO"  # Not acceptable in romanizations
        classes1.append(cl)
    # print("classify_desc: {!r} classes1: {}".format(desc, classes1))
    # print(set(classes1)    )
    if all(
        x in ("Ll", "Lu", "Lt", "Lm", "Mn", "Mc", "Zs", "Nd", "OK")
        for x in classes1
    ):
        if (
            (num_latin >= num_greek + 2 or num_greek == 0)
            and classes1.count("OK") < len(classes1)
            and classes1.count("Nd") < len(classes1)
        ):
            return "romanization"
    # Otherwise it is something else, such as hanji version of the word
    return "other"

# Code for parsing inflection tables.
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org.

import re
import copy
import html
import functools
import collections
import unicodedata
from typing import Optional
from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor import WikiNode, NodeKind, MAGIC_FIRST
from wiktextract.tags import valid_tags
from wiktextract.inflectiondata import infl_map, infl_start_map, infl_start_re
from wiktextract.datautils import data_append, freeze, split_at_comma_semi
from wiktextract.form_descriptions import (
    classify_desc,
    decode_tags,
    parse_head_final_tags,
    distw,
)
from wiktextract.clean import (
    clean_value,
)
from wiktextract.table_headers_heuristics_data import (
    LANGUAGES_WITH_CELLS_AS_HEADERS,
)
from wiktextract.lang_specific_configs import get_lang_conf, lang_specific_tags

# --debug-text-cell WORD
# Command-line parameter for debugging. When parsing inflection tables,
# print out debug messages when encountering this text.
debug_cell_text: Optional[str] = None


def set_debug_cell_text(text: str) -> None:
    global debug_cell_text
    debug_cell_text = text


TagSets = list[tuple[str, ...]]

# Column texts that are interpreted as an empty column.
IGNORED_COLVALUES = {
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
    "/",
    "?",
    "not used",
    "not applicable",
}

# These tags are never inherited from above
# XXX merge with lang_specific
noinherit_tags = {
    "infinitive-i",
    "infinitive-i-long",
    "infinitive-ii",
    "infinitive-iii",
    "infinitive-iv",
    "infinitive-v",
}

# Subject->object transformation mapping, when using dummy-object-concord
# to replace subject concord tags with object concord tags
object_concord_replacements = {
    "first-person": "object-first-person",
    "second-person": "object-second-person",
    "third-person": "object-third-person",
    "singular": "object-singular",
    "plural": "object-plural",
    "definite": "object-definite",
    "indefinite": "object-indefinite",
    "class-1": "object-class-1",
    "class-2": "object-class-2",
    "class-3": "object-class-3",
    "class-4": "object-class-4",
    "class-5": "object-class-5",
    "class-6": "object-class-6",
    "class-7": "object-class-7",
    "class-8": "object-class-8",
    "class-9": "object-class-9",
    "class-10": "object-class-10",
    "class-11": "object-class-11",
    "class-12": "object-class-12",
    "class-13": "object-class-13",
    "class-14": "object-class-14",
    "class-15": "object-class-15",
    "class-16": "object-class-16",
    "class-17": "object-class-17",
    "class-18": "object-class-18",
    "masculine": "object-masculine",
    "feminine": "object-feminine",
}

# Words in title that cause addition of tags in all entries
title_contains_global_map = {
    "possessive": "possessive",
    "possessed forms of": "possessive",
    "predicative forms of": "predicative",
    "negative": "negative",
    "positive definite forms": "positive definite",
    "positive indefinite forms": "positive indefinite",
    "comparative": "comparative",
    "superlative": "superlative",
    "combined forms": "combined-form",
    "mutation": "mutation",
    "definite article": "definite",
    "indefinite article": "indefinite",
    "indefinite declension": "indefinite",
    "bare forms": "indefinite",  # e.g., cois/Irish
    "definite declension": "definite",
    "pre-reform": "dated",
    "personal pronouns": "personal pronoun",
    "composed forms of": "multiword-construction",
    "subordinate-clause forms of": "subordinate-clause",
    "participles of": "participle",
    "variation of": "dummy-skip-this",  # a'/Scottish Gaelic
    "command form of": "imperative",  # a راتلل/Pashto
    "historical inflection of": "dummy-skip-this",  # kork/Norwegian Nynorsk
}
for k, v in title_contains_global_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_CONTAINS_GLOBAL_MAP UNRECOGNIZED TAG: {}: {}".format(k, v))
table_hdr_ign_part = r"(Inflection|Conjugation|Declension|Mutation) of [^\s]"

table_hdr_ign_part_re = re.compile(r"(?i)(" + table_hdr_ign_part + ")")
# (?i) python regex extension, ignore case
title_contains_global_re = re.compile(
    r"(?i)(^|\b)({}|{})($|\b)".format(
        table_hdr_ign_part,
        "|".join(re.escape(x) for x in title_contains_global_map.keys()),
    )
)

# Words in title that cause addition of tags to table-tags "form"
title_contains_wordtags_map = {
    "pf": "perfective",
    "impf": "imperfective",
    "strong": "strong",
    "weak": "weak",
    "countable": "countable",
    "uncountable": "uncountable",
    "inanimate": "inanimate",
    "animate": "animate",
    "transitive": "transitive",
    "intransitive": "intransitive",
    "ditransitive": "ditransitive",
    "ambitransitive": "ambitransitive",
    "archaic": "archaic",
    "dated": "dated",
    "affirmative": "affirmative",
    "negative": "negative",
    "subject pronouns": "subjective",
    "object pronouns": "objective",
    "emphatic": "emphatic",
    "proper noun": "proper-noun",
    "no plural": "no-plural",
    "imperfective": "imperfective",
    "perfective": "perfective",
    "no supine stem": "no-supine",
    "no perfect stem": "no-perfect",
    "deponent": "deponent",
    "irregular": "irregular",
    "no short forms": "no-short-form",
    "iō-variant": "iō-variant",
    "1st declension": "declension-1",
    "2nd declension": "declension-2",
    "3rd declension": "declension-3",
    "4th declension": "declension-4",
    "5th declension": "declension-5",
    "6th declension": "declension-6",
    "first declension": "declension-1",
    "second declension": "declension-2",
    "third declension": "declension-3",
    "fourth declension": "declension-4",
    "fifth declension": "declension-5",
    "sixth declension": "declension-6",
    "1st conjugation": "conjugation-1",
    "2nd conjugation": "conjugation-2",
    "3rd conjugation": "conjugation-3",
    "4th conjugation": "conjugation-4",
    "5th conjugation": "conjugation-5",
    "6th conjugation": "conjugation-6",
    "7th conjugation": "conjugation-7",
    "first conjugation": "conjugation-1",
    "second conjugation": "conjugation-2",
    "third conjugation": "conjugation-3",
    "fourth conjugation": "conjugation-4",
    "fifth conjugation": "conjugation-5",
    "sixth conjugation": "conjugation-6",
    "seventh conjugation": "conjugation-7",
    # Corsican regional tags in table header
    "cismontane": "Cismontane",
    "ultramontane": "Ultramontane",
    "western lombard": "Western-Lombard",
    "eastern lombard": "Eastern-Lombard",
}
for k, v in title_contains_wordtags_map.items():
    if any(t not in valid_tags for t in v.split()):
        print(
            "TITLE_CONTAINS_WORDTAGS_MAP UNRECOGNIZED TAG: {}: {}".format(k, v)
        )
title_contains_wordtags_re = re.compile(
    r"(?i)(^|\b)({}|{})($|\b)".format(
        table_hdr_ign_part,
        "|".join(re.escape(x) for x in title_contains_wordtags_map.keys()),
    )
)

# Parenthesized elements in title that are converted to tags in
# "table-tags" form
title_elements_map = {
    "weak": "weak",
    "strong": "strong",
    "separable": "separable",
    "masculine": "masculine",
    "feminine": "feminine",
    "neuter": "neuter",
    "singular": "singular",
    "plural": "plural",
    "archaic": "archaic",
    "dated": "dated",
    "Attic": "Attic",  # e.g. καλός/Greek/Adj
    "Epic": "Epic",  # e.g. καλός/Greek/Adj
}
for k, v in title_elements_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_ELEMENTS_MAP UNRECOGNIZED TAG: {}: {}".format(k, v))

# Parenthized element starts to map them to tags for form for the rest of
# the element
title_elemstart_map = {
    "auxiliary": "auxiliary",
    "Kotus type": "class",
    "ÕS type": "class",
    "class": "class",
    "short class": "class",
    "type": "class",
    "strong class": "class",
    "weak class": "class",
    "accent paradigm": "accent-paradigm",
    "stem in": "class",
}
for k, v in title_elemstart_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_ELEMSTART_MAP UNRECOGNIZED TAG: {}: {}".format(k, v))
title_elemstart_re = re.compile(
    r"^({}) ".format("|".join(re.escape(x) for x in title_elemstart_map.keys()))
)


# Regexp for cell starts that are likely definitions of reference symbols.
# See also nondef_re.
def_re = re.compile(
    r"(\s*•?\s+)?"
    r"((\*+|[△†0123456789⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+)([⁾):]|\s)|"
    r"\^(\*+|[△†])|"
    r"([¹²³⁴⁵⁶⁷⁸⁹])|"
    r"([ᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿᵀᵁⱽᵂᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻᵝᵞᵟᶿᶥᵠᵡ]))"
)
# ᴺᴸᴴ persan/Old Irish

# Regexp for cell starts that are exceptions to def_re and do not actually
# start a definition.
nondef_re = re.compile(
    r"(^\s*(1|2|3)\s+(sg|pl)\s*$|"  # 1s or 3p etc.
    r"\s*\d\d?\s*/\s*\d\d?\s*$)"
)  # taka/Swahili "15 / 17"

# Certain tags are moved from headers in tables into word tags, as they always
# apply to the whole word.
TAGS_FORCED_WORDTAGS: set[str] = set(
    [
        # This was originally created for a issue with number paradigms in
        # Arabic, but that is being handled elsewhere now.
    ]
)


class InflCell:
    """Cell in an inflection table."""

    __slots__ = (
        "text",
        "is_title",
        "colspan",
        "rowspan",
        "target",
    )

    def __init__(
        self,
        text: str,
        is_title: bool,
        colspan: int,
        rowspan: int,
        target: Optional[str],
    ) -> None:
        assert isinstance(text, str)
        assert is_title in (True, False)
        assert isinstance(colspan, int) and colspan >= 1
        assert isinstance(rowspan, int) and rowspan >= 1
        assert target is None or isinstance(target, str)
        self.text = text.strip()
        self.is_title = text and is_title
        self.colspan = colspan
        self.rowspan = rowspan
        self.target = target

    def __str__(self) -> str:
        v = "{}/{}/{}/{!r}".format(
            self.text, self.is_title, self.colspan, self.rowspan
        )
        if self.target:
            v += ": {!r}".format(self.target)
        return v

    def __repr__(self) -> str:
        return str(self)


class HdrSpan:
    """Saved information about a header cell/span during the parsing
    of a table."""

    __slots__ = (
        "start",
        "colspan",
        "rowspan",
        "rownum",  # Row number where this occurred
        "tagsets",  # list of tuples
        "text",  # For debugging
        "all_headers_row",
        "expanded",  # The header has been expanded to cover whole row/part
    )

    def __init__(
        self,
        start: int,
        colspan: int,
        rowspan: int,
        rownum: int,
        tagsets: TagSets,
        text: str,
        all_headers_row: bool,
    ) -> None:
        assert isinstance(start, int) and start >= 0
        assert isinstance(colspan, int) and colspan >= 1
        assert isinstance(rownum, int)
        assert isinstance(tagsets, list)
        for x in tagsets:
            assert isinstance(x, tuple)
        assert all_headers_row in (True, False)
        self.start = start
        self.colspan = colspan
        self.rowspan = rowspan
        self.rownum = rownum
        self.tagsets = list(tuple(sorted(set(tags))) for tags in tagsets)
        self.text = text
        self.all_headers_row = all_headers_row
        self.expanded = False


def is_superscript(ch: str) -> bool:
    """Returns True if the argument is a superscript character."""
    assert isinstance(ch, str) and len(ch) == 1
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return False
    return (
        re.match(
            r"SUPERSCRIPT |"
            r"MODIFIER LETTER SMALL |"
            r"MODIFIER LETTER CAPITAL ",
            name,
        )
        is not None
    )


def remove_useless_tags(lang: str, pos: str, tags: set[str]) -> None:
    """Remove certain tag combinations from ``tags`` when they serve no purpose
    together (cover all options)."""
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(tags, set)
    if (
        "animate" in tags
        and "inanimate" in tags
        and get_lang_conf(lang, "animate_inanimate_remove")
    ):
        tags.remove("animate")
        tags.remove("inanimate")
    if (
        "virile" in tags
        and "nonvirile" in tags
        and get_lang_conf(lang, "virile_nonvirile_remove")
    ):
        tags.remove("virile")
        tags.remove("nonvirile")
    # If all numbers in the language are listed, remove them all
    numbers = get_lang_conf(lang, "numbers")
    if numbers and all(x in tags for x in numbers):
        for x in numbers:
            tags.remove(x)
    # If all genders in the language are listed, remove them all
    genders = get_lang_conf(lang, "genders")
    if genders and all(x in tags for x in genders):
        for x in genders:
            tags.remove(x)
    # If all voices in the language are listed, remove them all
    voices = get_lang_conf(lang, "voices")
    if voices and all(x in tags for x in voices):
        for x in voices:
            tags.remove(x)
    # If all strengths of the language are listed, remove them all
    strengths = get_lang_conf(lang, "strengths")
    if strengths and all(x in tags for x in strengths):
        for x in strengths:
            tags.remove(x)
    # If all persons of the language are listed, remove them all
    persons = get_lang_conf(lang, "persons")
    if persons and all(x in tags for x in persons):
        for x in persons:
            tags.remove(x)
    # If all definitenesses of the language are listed, remove them all
    definitenesses = get_lang_conf(lang, "definitenesses")
    if definitenesses and all(x in tags for x in definitenesses):
        for x in definitenesses:
            tags.remove(x)


def tagset_cats(tagset: TagSets) -> set[str]:
    """Returns a set of tag categories for the tagset (merged from all
    alternatives)."""
    return set(valid_tags[t] for ts in tagset for t in ts)


def or_tagsets(
    lang: str, pos: str, tagsets1: TagSets, tagsets2: TagSets
) -> TagSets:
    """Merges two tagsets (the new tagset just merges the tags from both, in
    all combinations).  If they contain simple alternatives (differ in
    only one category), they are simply merged; otherwise they are split to
    more alternatives.  The tagsets are assumed be sets of sorted tuples."""
    assert isinstance(tagsets1, list)
    assert all(isinstance(x, tuple) for x in tagsets1)
    assert isinstance(tagsets2, list)
    assert all(isinstance(x, tuple) for x in tagsets1)
    tagsets: TagSets = []  # This will be the result

    def add_tags(tags1: tuple[str, ...]) -> None:
        # CONTINUE
        if not tags1:
            return  # empty set would merge with anything, won't change result
        if not tagsets:
            tagsets.append(tags1)
            return
        for tags2 in tagsets:
            # Determine if tags1 can be merged with tags2
            num_differ = 0
            if tags1 and tags2:
                cats1 = set(valid_tags[t] for t in tags1)
                cats2 = set(valid_tags[t] for t in tags2)
                cats = cats1 | cats2
                for cat in cats:
                    tags1_in_cat = set(t for t in tags1 if valid_tags[t] == cat)
                    tags2_in_cat = set(t for t in tags2 if valid_tags[t] == cat)
                    if (
                        tags1_in_cat != tags2_in_cat
                        or not tags1_in_cat
                        or not tags2_in_cat
                    ):
                        num_differ += 1
                        if not tags1_in_cat or not tags2_in_cat:
                            # Prevent merging if one is empty
                            num_differ += 1
            # print("tags1={} tags2={} num_differ={}"
            #       .format(tags1, tags2, num_differ))
            if num_differ <= 1:
                # Yes, they can be merged
                tagsets.remove(tags2)
                tags_s = set(tags1) | set(tags2)
                remove_useless_tags(lang, pos, tags_s)
                tags_t = tuple(sorted(tags_s))
                add_tags(tags_t)  # Could result in further merging
                return
        # If we could not merge, add to tagsets
        tagsets.append(tags1)

    for tags in tagsets1:
        add_tags(tags)
    for tags in tagsets2:
        add_tags(tags)
    if not tagsets:
        tagsets.append(())

    # print("or_tagsets: {} + {} -> {}"
    #       .format(tagsets1, tagsets2, tagsets))
    return tagsets


def and_tagsets(lang, pos, tagsets1, tagsets2):
    """Merges tagsets by taking union of all cobinations, without trying
    to determine whether they are compatible."""
    assert isinstance(tagsets1, list) and len(tagsets1) >= 1
    assert all(isinstance(x, tuple) for x in tagsets1)
    assert isinstance(tagsets2, list) and len(tagsets2) >= 1
    assert all(isinstance(x, tuple) for x in tagsets1)
    new_tagsets = []
    for tags1 in tagsets1:
        for tags2 in tagsets2:
            tags = set(tags1) | set(tags2)
            remove_useless_tags(lang, pos, tags)
            if "dummy-ignored-text-cell" in tags:
                tags.remove("dummy-ignored-text-cell")
            tags = tuple(sorted(tags))
            if tags not in new_tagsets:
                new_tagsets.append(tags)
    # print("and_tagsets: {} + {} -> {}"
    #       .format(tagsets1, tagsets2, new_tagsets))
    return new_tagsets


@functools.lru_cache(65536)
def extract_cell_content(lang, word, col):
    """Cleans a row/column header for later processing.  This returns
    (cleaned, refs, defs, tags)."""
    # print("EXTRACT_CELL_CONTENT {!r}".format(col))
    hdr_tags = []
    orig_col = col
    col = re.sub(r"(?s)\s*,\s*$", "", col)
    col = re.sub(r"(?s)\s*•\s*$", "", col)
    col = re.sub(r"\s+", " ", col)
    col = col.strip()
    if re.search(
        r"^\s*(There are |"
        r"\* |"
        r"see |"
        r"Use |"
        r"use the |"
        r"Only used |"
        r"The forms in |"
        r"these are also written |"
        r"The genitive can be |"
        r"Genitive forms are rare or non-existant|"
        r"Accusative Note: |"
        r"Classifier Note: |"
        r"Noun: Assamese nouns are |"
        r"the active conjugation|"
        r"the instrumenal singular|"
        r"Note:|"
        r"\^* Note:|"
        r"possible mutated form |"
        r"The future tense: )",
        col,
    ):
        return "dummy-ignored-text-cell", [], [], []

    # Temporarily remove final parenthesized part (if separated by whitespace),
    # so that we can extract reference markers before it.
    final_paren = ""
    m = re.search(r"\s+\([^)]*\)$", col)
    if m is not None:
        final_paren = m.group(0)
        col = col[: m.start()]

    # Extract references and tag markers
    refs = []
    special_references = get_lang_conf(lang, "special_references")
    while True:
        m = re.search(r"\^(.|\([^)]*\))$", col)
        if not m:
            break
        r = m.group(1)
        if r.startswith("(") and r.endswith(")"):
            r = r[1:-1]
        if r == "rare":
            hdr_tags.append("rare")
        elif special_references and r in special_references:
            hdr_tags.extend(special_references[r].split())
        else:
            v = m.group(1)
            if v.startswith("(") and v.endswith(")"):
                v = v[1:-1]
            refs.append(v)
        col = col[: m.start()]
    # See if it is a ref definition
    # print("BEFORE REF CHECK: {!r}".format(col))
    m = re.match(def_re, col)
    if m and not re.match(nondef_re, col):
        ofs = 0
        ref = None
        deflst = []
        for m in re.finditer(def_re, col):
            if ref:
                deflst.append((ref, col[ofs : m.start()].strip()))
            ref = m.group(3) or m.group(5) or m.group(6)
            ofs = m.end()
        if ref:
            deflst.append((ref, col[ofs:].strip()))
        # print("deflst:", deflst)
        return "", [], deflst, []
    # See if it *looks* like a reference to a definition
    while col:
        if is_superscript(col[-1]) or col[-1] in ("†",):
            if col.endswith("ʳᵃʳᵉ"):
                hdr_tags.append("rare")
                col = col[:-4].strip()
                continue
            if special_references:
                stop_flag = False
                for r in special_references:
                    if col.endswith(r):
                        hdr_tags.extend(special_references[r].split())
                        col = col[: -len(r)].strip()
                        stop_flag = True
                        break  # this for loop
                if stop_flag:
                    continue  # this while loop
            # Numbers and H/L/N are useful information
            refs.append(col[-1])
            col = col[:-1]
        else:
            break

    # Check for another form of note definition
    if (
        len(col) > 2
        and col[1] in (")", " ", ":")
        and col[0].isdigit()
        and not re.match(nondef_re, col)
    ):
        return "", [], [[col[0], col[2:].strip()]], []
    col = col.strip()

    # Extract final "*" reference symbols.  Sometimes there are multiple.
    m = re.search(r"\*+$", col)
    if m is not None:
        col = col[: m.start()]
        refs.append(m.group(0))
    if col.endswith("(*)"):
        col = col[:-3].strip()
        refs.append("*")

    # Put back the final parenthesized part
    col = col.strip() + final_paren
    # print("EXTRACT_CELL_CONTENT: orig_col={!r} col={!r} refs={!r} hdr_tags={}"
    #       .format(orig_col, col, refs, hdr_tags))
    return col.strip(), refs, [], hdr_tags


@functools.lru_cache(10000)
def parse_title(title, source):
    """Parses inflection table title.  This returns (global_tags, table_tags,
    extra_forms), where ``global_tags`` is tags to be added to each inflection
    entry, ``table_tags`` are tags for the word but not to be added to every
    form, and ``extra_forms`` is dictionary describing additional forms to be
    included in the part-of-speech entry)."""
    assert isinstance(title, str)
    assert isinstance(source, str)
    title = html.unescape(title)
    title = re.sub(r"(?i)<[^>]*>", "", title).strip()
    title = re.sub(r"\s+", " ", title)
    # print("PARSE_TITLE:", title)
    global_tags = []
    table_tags = []
    extra_forms = []
    # Add certain global tags based on contained words
    for m in re.finditer(title_contains_global_re, title):
        v = m.group(0).lower()
        if re.match(table_hdr_ign_part_re, v):
            continue
        global_tags.extend(title_contains_global_map[v].split())
    # Add certain tags to table-tags "form" based on contained words
    for m in re.finditer(title_contains_wordtags_re, title):
        v = m.group(0).lower()
        if re.match(table_hdr_ign_part_re, v):
            continue
        table_tags.extend(title_contains_wordtags_map[v].split())
    if re.search(r"Conjugation of (s’|se ).*French verbs", title):
        global_tags.append("reflexive")
    # Check for <x>-type at the beginning of title (e.g., Armenian) and various
    # other ways of specifying an inflection class.
    for m in re.finditer(
        r"\b("
        r"[\w/]+-type|"
        r"accent-\w+|"
        r"[\w/]+-stem|"
        r"[^ ]+ gradation|"
        r"\b(stem in [\w/ ]+)|"
        r"[^ ]+ alternation|"
        r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh) "
        r"(Conjugation|declension)|"
        r"First and second declension|"
        r"(1st|2nd|3rd|4th|5th|6th) declension|"
        r"\w[\w/ ]* harmony"
        r")\b",
        title,
    ):
        dt = {"form": m.group(1), "source": source, "tags": ["class"]}
        extra_forms.append(dt)
    # Parse parenthesized part from title
    for m in re.finditer(r"\(([^)]*)\)", title):
        for elem in m.group(1).split(","):
            # group(0) is the whole string, group(1) first parens
            elem = elem.strip()
            if elem in title_elements_map:
                table_tags.extend(title_elements_map[elem].split())
            else:
                m = re.match(title_elemstart_re, elem)
                if m:
                    tags = title_elemstart_map[m.group(1)].split()
                    dt = {
                        "form": elem[m.end() :],
                        "source": source,
                        "tags": tags,
                    }
                    extra_forms.append(dt)
    # For titles that contains no parenthesized parts, do some special
    # handling to still interpret parts from them
    if "(" not in title:
        # No parenthesized parts
        m = re.search(r"\b(Portuguese) (-.* verb) ", title)
        if m is not None:
            dt = {"form": m.group(2), "tags": ["class"], "source": source}
            extra_forms.append(dt)
        for elem in title.split(","):
            elem = elem.strip()
            if elem in title_elements_map:
                table_tags.extend(title_elements_map[elem].split())
            elif elem.endswith("-stem"):
                dt = {"form": elem, "tags": ["class"], "source": source}
                extra_forms.append(dt)
    return global_tags, table_tags, extra_forms


def expand_header(
    wxr,
    tablecontext,
    word,
    lang,
    pos,
    text,
    base_tags,
    silent=False,
    ignore_tags=False,
    depth=0,
):
    """Expands a cell header to tagset, handling conditional expressions
    in infl_map.  This returns list of tuples of tags, each list element
    describing an alternative interpretation.  ``base_tags`` is combined
    column and row tags for the cell in which the text is being interpreted
    (conditional expressions in inflection data may depend on it).
    If ``silent`` is True, then no warnings will be printed.  If ``ignore_tags``
    is True, then tags listed in "if" will be ignored in the test (this is
    used when trying to heuristically detect whether a non-<th> cell is anyway
    a header)."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(base_tags, (list, tuple, set))
    assert silent in (True, False)
    assert isinstance(depth, int)
    # print("EXPAND_HDR: text={!r} base_tags={!r}".format(text, base_tags))
    # First map the text using the inflection map
    text = clean_value(wxr, text)
    combined_return = []
    parts = split_at_comma_semi(text, separators=[";"])
    for text in parts:
        if not text:
            continue
        if text in infl_map:
            v = infl_map[text]  # list or string
        else:
            m = re.match(infl_start_re, text)
            if m is not None:
                v = infl_start_map[m.group(1)]
                # print("INFL_START {} -> {}".format(text, v))
            elif re.match(r"Notes", text):
                # Ignored header
                # print("IGNORING NOTES")
                combined_return = or_tagsets(
                    lang, pos, combined_return, [("dummy-skip-this",)]
                )
                # this just adds dummy-skip-this
                continue
            elif text in IGNORED_COLVALUES:
                combined_return = or_tagsets(
                    lang, pos, combined_return, [("dummy-ignore-skipped",)]
                )
                continue
            # Try without final parenthesized part
            text_without_parens = re.sub(r"[,/]?\s+\([^)]*\)\s*$", "", text)
            if text_without_parens in infl_map:
                v = infl_map[text_without_parens]
            elif m is None:
                if not silent:
                    wxr.wtp.debug(
                        "inflection table: unrecognized header: {}".format(
                            repr(text)
                        ),
                        sortid="inflection/735",
                    )
                # Unrecognized header
                combined_return = or_tagsets(
                    lang, pos, combined_return, [("error-unrecognized-form",)]
                )
                continue

        # Then loop interpreting the value, until the value is a simple string.
        # This may evaluate nested conditional expressions.
        default_then = None
        while True:
            # If it is a string, we are done.
            if isinstance(v, str):
                tags = set(v.split())
                remove_useless_tags(lang, pos, tags)
                tagset = [tuple(sorted(tags))]
                break
            # For a list, just interpret it as alternatives.  (Currently the
            # alternatives must directly be strings.)
            if isinstance(v, (list, tuple)):
                tagset = []
                for x in v:
                    tags = set(x.split())
                    remove_useless_tags(lang, pos, tags)
                    tags = tuple(sorted(tags))
                    if tags not in tagset:
                        tagset.append(tags)
                break
            # Otherwise the value should be a dictionary describing a
            # conditional expression.
            if not isinstance(v, dict):
                wxr.wtp.debug(
                    "inflection table: internal: "
                    "UNIMPLEMENTED INFL_MAP VALUE: {}".format(infl_map[text]),
                    sortid="inflection/767",
                )
                tagset = [()]
                break
            # Evaluate the conditional expression.
            assert isinstance(v, dict)
            cond = "default-true"
            c = ""
            # Handle "lang" condition.  The value must be either a
            # single language or a list of languages, and the
            # condition evaluates to True if the table is one of
            # those languages.
            if "lang" in v:
                c = v["lang"]
                if isinstance(c, str):
                    cond = c == lang
                else:
                    assert isinstance(c, (list, tuple, set))
                    cond = lang in c
            # Handle "nested-table-depth" condition. The value must
            # be an int or list of ints, and the condition evaluates
            # True if the depth is one of those values.
            # "depth" is how deep into a nested table tree the current
            # table lies. It is first started in handle_wikitext_table,
            # so only applies to tables-within-tables, not other
            # WikiNode content. `depth` is currently only passed as a
            # parameter down the table parsing stack, and not stored.
            if cond and "nested-table-depth" in v:
                d = v["nested-table-depth"]
                if isinstance(d, int):
                    cond = d == depth
                else:
                    assert isinstance(d, (list, tuple, set))
                    cond = depth in d
            # Handle inflection-template condition. Must be a string
            # or list of strings, and if tablecontext.template_name is in
            # those, accept the condition.
            # TableContext.template_name is passed down from page/
            # parse_inflection, before parsing and expanding itself
            # has begun.
            if cond and tablecontext and "inflection-template" in v:
                d = v["inflection-template"]
                if isinstance(d, str):
                    cond = d == tablecontext.template_name
                else:
                    assert isinstance(d, (list, tuple, set))
                    cond = tablecontext.template_name in d
            # Handle "pos" condition.  The value must be either a single
            # part-of-speech or a list of them, and the condition evaluates to
            # True if the part-of-speech is any of those listed.
            if cond and "pos" in v:
                c = v["pos"]
                if isinstance(c, str):
                    cond = c == pos
                else:
                    assert isinstance(c, (list, tuple, set))
                    cond = pos in c
            # Handle "if" condition.  The value must be a string containing
            # a space-separated list of tags.  The condition evaluates to True
            # if ``base_tags`` contains all of the listed tags.  If the condition
            # is of the form "any: ...tags...", then any of the tags will be
            # enough.
            if cond and "if" in v and not ignore_tags:
                c = v["if"]
                assert isinstance(c, str)
                # "if" condition is true if any of the listed tags is present if
                # it starts with "any:", otherwise all must be present
                if c.startswith("any: "):
                    cond = any(t in base_tags for t in c[5:].split())
                else:
                    cond = all(t in base_tags for t in c.split())

            # Handle "default" assignment. Store the value to be used
            # as a default later.
            if "default" in v:
                assert isinstance(v["default"], str)
                default_then = v["default"]

            # Warning message about missing conditions for debugging.

            if cond == "default-true" and not default_then and not silent:
                wxr.wtp.debug(
                    "inflection table: IF MISSING COND: word={} "
                    "lang={} text={} base_tags={} c={} cond={}".format(
                        word, lang, text, base_tags, c, cond
                    ),
                    sortid="inflection/851",
                )
            # Based on the result of evaluating the condition, select either
            # "then" part or "else" part.
            if cond:
                v = v.get("then", "")
            else:
                v = v.get("else")
                if v is None:
                    if default_then:
                        v = default_then
                    else:
                        if not silent:
                            wxr.wtp.debug(
                                "inflection table: IF WITHOUT ELSE EVALS "
                                "False: "
                                "{}/{} {!r} base_tags={}".format(
                                    word, lang, text, base_tags
                                ),
                                sortid="inflection/865",
                            )
                        v = "error-unrecognized-form"

        # Merge the resulting tagset from this header part with the other
        # tagsets from the whole header
        combined_return = or_tagsets(lang, pos, combined_return, tagset)

    # Return the combined tagsets, or empty tagset if we got no tagsets
    if not combined_return:
        combined_return = [()]
    return combined_return


def compute_coltags(lang, pos, hdrspans, start, colspan, celltext):
    """Computes column tags for a column of the given width based on the
    current header spans."""
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(hdrspans, list)
    assert isinstance(start, int) and start >= 0
    assert isinstance(colspan, int) and colspan >= 1
    assert isinstance(celltext, str)  # For debugging only
    # print("COMPUTE_COLTAGS CALLED start={} colspan={} celltext={!r}"
    #       .format(start, colspan, celltext))
    # For debugging, set this to the form for whose cell you want debug prints
    if celltext == debug_cell_text:
        print(
            "COMPUTE_COLTAGS CALLED start={} colspan={} celltext={!r}".format(
                start, colspan, celltext
            )
        )
        for hdrspan in hdrspans:
            print(
                "  row={} start={} colspans={} tagsets={}".format(
                    hdrspan.rownum,
                    hdrspan.start,
                    hdrspan.colspan,
                    hdrspan.tagsets,
                )
            )
    used = set()
    coltags = [()]
    last_header_row = 1000000
    # Iterate through the headers in reverse order, i.e., headers lower in the
    # table (closer to the cell) first.
    row_tagsets = [()]
    row_tagsets_rownum = 1000000
    used_hdrspans = set()
    for hdrspan in reversed(hdrspans):
        if (
            hdrspan.start + hdrspan.colspan <= start
            or hdrspan.start >= start + colspan
        ):
            # Does not horizontally overlap current cell. Ignore this hdrspan.
            if celltext == debug_cell_text:
                print(
                    "Ignoring row={} start={} colspan={} tagsets={}".format(
                        hdrspan.rownum,
                        hdrspan.start,
                        hdrspan.colspan,
                        hdrspan.tagsets,
                    )
                )
            continue
        # If the cell partially overlaps the current cell, assume we have
        # reached something unrelated and abort.
        if (
            hdrspan.start < start
            and hdrspan.start + hdrspan.colspan > start
            and hdrspan.start + hdrspan.colspan < start + colspan
        ):
            if celltext == debug_cell_text:
                print(
                    "break on partial overlap at start {} {} {}".format(
                        hdrspan.start, hdrspan.colspan, hdrspan.tagsets
                    )
                )
            break
        if (
            hdrspan.start < start + colspan
            and hdrspan.start > start
            and hdrspan.start + hdrspan.colspan > start + colspan
            and not hdrspan.expanded
        ):
            if celltext == debug_cell_text:
                print(
                    "break on partial overlap at end {} {} {}".format(
                        hdrspan.start, hdrspan.colspan, hdrspan.tagsets
                    )
                )
            break
        # Check if we have already used this cell.
        if id(hdrspan) in used_hdrspans:
            continue
        # We are going to use this cell.
        used_hdrspans.add(id(hdrspan))
        tagsets = hdrspan.tagsets
        # If the hdrspan is fully inside the current cell and does not cover
        # it fully, check if we should merge information from multiple cells.
        if not hdrspan.expanded and (
            hdrspan.start > start
            or hdrspan.start + hdrspan.colspan < start + colspan
        ):
            # Multiple columns apply to the current cell, only
            # gender/number/case tags present
            # If there are no tags outside the range in any of the
            # categories included in these cells, don't add anything
            # (assume all choices valid in the language are possible).
            in_cats = set(
                valid_tags[t]
                for x in hdrspans
                if x.rownum == hdrspan.rownum
                and x.start >= start
                and x.start + x.colspan <= start + colspan
                for tt in x.tagsets
                for t in tt
            )
            if celltext == debug_cell_text:
                print("in_cats={} tagsets={}".format(in_cats, tagsets))
            # Merge the tagsets into existing tagsets.  This merges
            # alternatives into the same tagset if there is only one
            # category different; otherwise this splits the tagset into
            # more alternatives.
            includes_all_on_row = True
            for x in hdrspans:
                # print("X: x.rownum={} x.start={}".format(x.rownum, x.start))
                if x.rownum != hdrspan.rownum:
                    continue
                if x.start < start or x.start + x.colspan > start + colspan:
                    if celltext == debug_cell_text:
                        print(
                            "NOT IN RANGE: {} {} {}".format(
                                x.start, x.colspan, x.tagsets
                            )
                        )
                    includes_all_on_row = False
                    continue
                if id(x) in used_hdrspans:
                    if celltext == debug_cell_text:
                        print(
                            "ALREADY USED: {} {} {}".format(
                                x.start, x.colspan, x.tagsets
                            )
                        )
                    continue
                used_hdrspans.add(id(x))
                if celltext == debug_cell_text:
                    print(
                        "Merging into wide col: x.rownum={} "
                        "x.start={} x.colspan={} "
                        "start={} colspan={} tagsets={} x.tagsets={}".format(
                            x.rownum,
                            x.start,
                            x.colspan,
                            start,
                            colspan,
                            tagsets,
                            x.tagsets,
                        )
                    )
                tagsets = or_tagsets(lang, pos, tagsets, x.tagsets)
            # If all headers on the row were included, ignore them.
            # See e.g. kunna/Swedish/Verb.
            ts_cats = tagset_cats(tagsets)
            if (
                includes_all_on_row
                or
                # Kludge, see fut/Hungarian/Verb
                ("tense" in ts_cats and "object" in ts_cats)
            ):
                tagsets = [()]
            # For limited categories, if the category doesn't appear
            # outside, we won't include the category
            if not in_cats - set(
                ("gender", "number", "person", "case", "category", "voice")
            ):
                # Sometimes we have masc, fem, neut and plural, so treat
                # number and gender as the same here (if one given, look for
                # the other too)
                if "number" in in_cats or "gender" in in_cats:
                    in_cats.update(("number", "gender"))
                # Determine which categories occur outside on
                # the same row.  Ignore headers that have been expanded
                # to cover the whole row/part of it.
                out_cats = set(
                    valid_tags[t]
                    for x in hdrspans
                    if x.rownum == hdrspan.rownum
                    and not x.expanded
                    and (
                        x.start < start or x.start + x.colspan > start + colspan
                    )
                    for tt in x.tagsets
                    for t in tt
                )
                if celltext == debug_cell_text:
                    print("in_cats={} out_cats={}".format(in_cats, out_cats))
                # Remove all inside categories that do not appear outside

                new_tagsets = []
                for ts in tagsets:
                    tags = tuple(
                        sorted(t for t in ts if valid_tags[t] in out_cats)
                    )
                    if tags not in new_tagsets:
                        new_tagsets.append(tags)
                if celltext == debug_cell_text and new_tagsets != tagsets:
                    print(
                        "Removed tags that do not appear outside {} -> {}".format(
                            tagsets, new_tagsets
                        )
                    )
                tagsets = new_tagsets
        key = (hdrspan.start, hdrspan.colspan)
        if key in used:
            if celltext == debug_cell_text:
                print(
                    "Cellspan already used: start={} colspan={} rownum={} {}".format(
                        hdrspan.start,
                        hdrspan.colspan,
                        hdrspan.rownum,
                        hdrspan.tagsets,
                    )
                )
            action = get_lang_conf(lang, "reuse_cellspan")
            # can be "stop", "skip" or "reuse"
            if action == "stop":
                break
            if action == "skip":
                continue
            assert action == "reuse"
        tcats = tagset_cats(tagsets)
        # Most headers block using the same column position above.  However,
        # "register" tags don't do this (cf. essere/Italian/verb: "formal")
        if len(tcats) != 1 or "register" not in tcats:
            used.add(key)
        # If we have moved to a different row, merge into column tagsets
        # (we use different and_tagsets within the row)
        if row_tagsets_rownum != hdrspan.rownum:
            # row_tagsets_rownum was initialized as 10000000
            ret = and_tagsets(lang, pos, coltags, row_tagsets)
            if celltext == debug_cell_text:
                print(
                    "merging rows: {} {} -> {}".format(
                        coltags, row_tagsets, ret
                    )
                )
            coltags = ret
            row_tagsets = [()]
            row_tagsets_rownum = hdrspan.rownum
        # Merge into coltags
        if hdrspan.all_headers_row and hdrspan.rownum + 1 == last_header_row:
            # If this row is all headers and immediately preceeds the last
            # header we accepted, take any header from there.
            row_tagsets = and_tagsets(lang, pos, row_tagsets, tagsets)
            if celltext == debug_cell_text:
                print("merged (next header row): {}".format(row_tagsets))
        else:
            # new_cats is for the new tags (higher up in the table)
            new_cats = tagset_cats(tagsets)
            # cur_cats is for the tags already collected (lower in the table)
            cur_cats = tagset_cats(coltags)
            if celltext == debug_cell_text:
                print(
                    "row={} start={} colspan={} tagsets={} coltags={} "
                    "new_cats={} cur_cats={}".format(
                        hdrspan.rownum,
                        hdrspan.start,
                        hdrspan.colspan,
                        tagsets,
                        coltags,
                        new_cats,
                        cur_cats,
                    )
                )
            if "detail" in new_cats:
                if not any(coltags):  # Only if no tags so far
                    coltags = or_tagsets(lang, pos, coltags, tagsets)
                if celltext == debug_cell_text:
                    print("stopping on detail after merge")
                break
            # Here, we block bleeding of categories from above
            elif "non-finite" in cur_cats and "non-finite" in new_cats:
                stop = get_lang_conf(lang, "stop_non_finite_non_finite")
                if stop:
                    if celltext == debug_cell_text:
                        print("stopping on non-finite-non-finite")
                    break
            elif "non-finite" in cur_cats and "voice" in new_cats:
                stop = get_lang_conf(lang, "stop_non_finite_voice")
                if stop:
                    if celltext == debug_cell_text:
                        print("stopping on non-finite-voice")
                    break
            elif "non-finite" in new_cats and cur_cats & set(
                ("person", "number")
            ):
                if celltext == debug_cell_text:
                    print("stopping on non-finite new")
                break
            elif "non-finite" in new_cats and "tense" in new_cats:
                stop = get_lang_conf(lang, "stop_non_finite_tense")
                if stop:
                    if celltext == debug_cell_text:
                        print("stopping on non-finite new")
                    break
            elif "non-finite" in cur_cats and new_cats & set(("mood",)):
                if celltext == debug_cell_text:
                    print("stopping on non-finite cur")
                break
            if (
                "tense" in new_cats
                and any("imperative" in x for x in coltags)
                and get_lang_conf(lang, "imperative_no_tense")
            ):
                if celltext == debug_cell_text:
                    print("skipping tense in imperative")
                continue
            elif (
                "mood" in new_cats
                and "mood" in cur_cats
                and
                # Allow if all new tags are already in current set
                any(
                    t not in ts1
                    for ts1 in coltags  # current
                    for ts2 in tagsets  # new (from above)
                    for t in ts2
                )
            ):
                skip = get_lang_conf(lang, "skip_mood_mood")
                if skip:
                    if celltext == debug_cell_text:
                        print("skipping on mood-mood")
                        # we continue to next header
                else:
                    if celltext == debug_cell_text:
                        print("stopping on mood-mood")
                    break
            elif "tense" in new_cats and "tense" in cur_cats:
                skip = get_lang_conf(lang, "skip_tense_tense")
                if skip:
                    if celltext == debug_cell_text:
                        print("skipping on tense-tense")
                        # we continue to next header
                else:
                    if celltext == debug_cell_text:
                        print("stopping on tense-tense")
                    break
            elif "aspect" in new_cats and "aspect" in cur_cats:
                if celltext == debug_cell_text:
                    print("skipping on aspect-aspect")
                continue
            elif "number" in cur_cats and "number" in new_cats:
                if celltext == debug_cell_text:
                    print("stopping on number-number")
                break
            elif "number" in cur_cats and "gender" in new_cats:
                if celltext == debug_cell_text:
                    print("stopping on number-gender")
                break
            elif "person" in cur_cats and "person" in new_cats:
                if celltext == debug_cell_text:
                    print("stopping on person-person")
                break
            else:
                # Merge tags and continue to next header up/left in the table.
                row_tagsets = and_tagsets(lang, pos, row_tagsets, tagsets)
                if celltext == debug_cell_text:
                    print("merged: {}".format(coltags))
        # Update the row number from which we have last taken headers
        last_header_row = hdrspan.rownum
    # Merge the final row tagset into coltags
    coltags = and_tagsets(lang, pos, coltags, row_tagsets)
    # print("HDRSPANS:", list((x.start, x.colspan, x.tagsets) for x in hdrspans))
    if celltext == debug_cell_text:
        print("COMPUTE_COLTAGS {} {}: {}".format(start, colspan, coltags))
    assert isinstance(coltags, list)
    assert all(isinstance(x, tuple) for x in coltags)
    return coltags


def parse_simple_table(
    wxr, tablecontext, word, lang, pos, rows, titles, source, after, depth
):
    """This is the default table parser.  Despite its name, it can parse
    complex tables.  This returns a list of forms to be added to the
    part-of-speech, or None if the table could not be parsed."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(tablecontext, TableContext)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(rows, list)
    assert isinstance(source, str)
    assert isinstance(after, str)
    assert isinstance(depth, int)
    for row in rows:
        for col in row:
            assert isinstance(col, InflCell)
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)

    # print("PARSE_SIMPLE_TABLE: TITLES:", titles)
    if debug_cell_text:
        print("ROWS:")
        for row in rows:
            print("  ", row)

    # Check for forced rowspan kludge.  See e.g.
    # maorski/Serbo-Croatian.  These are essentially multi-row
    # cells implemented using <br> rather than separate cell.  We fix this
    # by identifying rows where this happens, and splitting the current row
    # to multiple rows by synthesizing additional cells.
    new_rows = []
    for row in rows:
        split_row = (
            any(x.is_title and x.text in ("inanimate\nanimate",) for x in row)
            and
            # x is an InflCell
            all(x.rowspan == 1 for x in row)
        )
        if not split_row:
            new_rows.append(row)
            continue
        row1 = []
        row2 = []
        for cell in row:
            cell1 = copy.deepcopy(cell)
            if "\n" in cell.text:
                # Has more than one line - split this cell
                parts = cell.text.strip().splitlines()
                if len(parts) != 2:
                    wxr.wtp.debug(
                        "forced rowspan kludge got {} parts: {!r}".format(
                            len(parts), cell.text
                        ),
                        sortid="inflection/1234",
                    )
                cell2 = copy.deepcopy(cell)
                cell1.text = parts[0]
                cell2.text = parts[1]
            else:
                cell1.rowspan = 2
                cell2 = cell1  # ref, not a copy
            row1.append(cell1)
            row2.append(cell2)
        new_rows.append(row1)
        new_rows.append(row2)
    rows = new_rows
    # print("ROWS AFTER FORCED ROWSPAN KLUDGE:")
    # for row in rows:
    #     print("  ", row)

    # Parse definitions for references (from table itself and from text
    # after it)
    def_ht = {}

    def add_defs(defs):
        for ref, d in defs:
            # print("DEF: ref={} d={}".format(ref, d))
            d = d.strip()
            d = d.split(". ")[0].strip()  # text before ". "
            if not d:
                continue
            if d.endswith("."):  # catc ".."??
                d = d[:-1]
            tags, topics = decode_tags(d, no_unknown_starts=True)
            if topics or any("error-unknown-tag" in ts for ts in tags):
                d = d[0].lower() + d[1:]
                tags, topics = decode_tags(d, no_unknown_starts=True)
                if topics or any("error-unknown-tag" in ts for ts in tags):
                    # Failed to parse as tags
                    # print("Failed: topics={} tags={}"
                    #       .format(topics, tags))
                    continue
            tags1 = set()
            for ts in tags:
                tags1.update(ts)
            tags1 = tuple(sorted(tags1))
            # print("DEFINED: {} -> {}".format(ref, tags1))
            def_ht[ref] = tags1

    def generate_tags(rowtags, table_tags):
        new_coltags = []
        all_hdr_tags = []  # list of tuples
        new_rowtags = []
        for rt0 in rowtags:
            for ct0 in compute_coltags(
                lang,
                pos,
                hdrspans,
                col_idx,  # col_idx=>start
                colspan,
                col,  # cell_text
            ):
                base_tags = (
                    set(rt0) | set(ct0) | set(global_tags) | set(table_tags)
                )  # Union.
                alt_tags = expand_header(
                    wxr,
                    tablecontext,
                    word,
                    lang,
                    pos,
                    text,
                    base_tags,
                    depth=depth,
                )
                # base_tags are used in infl_map "if"-conds.
                for tt in alt_tags:
                    if tt not in all_hdr_tags:
                        all_hdr_tags.append(tt)
                    tt = set(tt)
                    # Certain tags are always moved to word-level tags
                    if tt & TAGS_FORCED_WORDTAGS:
                        table_tags.extend(tt & TAGS_FORCED_WORDTAGS)
                        tt = tt - TAGS_FORCED_WORDTAGS
                    # Add tags from referenced footnotes
                    tt.update(refs_tags)
                    # Sort, convert to tuple, and add to set of
                    # alternatives.
                    tt = tuple(sorted(tt))
                    if tt not in new_coltags:
                        new_coltags.append(tt)
                    # Kludge (saprast/Latvian/Verb): ignore row tags
                    # if trying to add a non-finite after mood.
                    if any(valid_tags[t] == "mood" for t in rt0) and any(
                        valid_tags[t] == "non-finite" for t in tt
                    ):
                        tags = tuple(sorted(set(tt) | set(hdr_tags)))
                    else:
                        tags = tuple(sorted(set(tt) | set(rt0) | set(hdr_tags)))
                    if tags not in new_rowtags:
                        new_rowtags.append(tags)
        return new_rowtags, new_coltags, all_hdr_tags

    def add_new_hdrspan(
        col,
        hdrspans,
        store_new_hdrspan,
        col0_followed_by_nonempty,
        col0_hdrspan,
    ):
        hdrspan = HdrSpan(
            col_idx, colspan, rowspan, rownum, new_coltags, col, all_headers
        )
        hdrspans.append(hdrspan)

        # infl-map tag "dummy-store-hdrspan" causes this new hdrspan
        # to be added to a register of stored hdrspans to be used
        # later with "dummy-load-stored-hdrspans".
        if store_new_hdrspan:
            tablecontext.stored_hdrspans.append(hdrspan)

        # Handle headers that are above left-side header
        # columns and are followed by personal pronouns in
        # remaining columns (basically headers that
        # evaluate to no tags).  In such cases widen the
        # left-side header to the full row.
        if previously_seen:  # id(cell) in seen_cells previously
            col0_followed_by_nonempty = True
            return col, col0_followed_by_nonempty, col0_hdrspan
        elif col0_hdrspan is None:
            col0_hdrspan = hdrspan
        elif any(all_hdr_tags):
            col0_cats = tagset_cats(col0_hdrspan.tagsets)
            later_cats = tagset_cats(all_hdr_tags)
            col0_allowed = get_lang_conf(lang, "hdr_expand_first")
            later_allowed = get_lang_conf(lang, "hdr_expand_cont")
            later_allowed = later_allowed | set(["dummy"])
            # dummy2 has different behavior than plain dummy
            # and does not belong here.

            # print("col0_cats={} later_cats={} "
            #       "fol_by_nonempty={} col_idx={} end={} "
            #       "tagsets={}"
            #       .format(col0_cats, later_cats,
            #               col0_followed_by_nonempty, col_idx,
            #               col0_hdrspan.start +
            #               col0_hdrspan.colspan,
            #               col0_hdrspan.tagsets))
            # print("col0.rowspan={} rowspan={}"
            #       .format(col0_hdrspan.rowspan, rowspan))
            # Only expand if [col0_cats and later_cats are allowed
            # and don't overlap] and [col0 has tags], and there have
            # been [no disallowed cells in between].
            #
            # There are three cases here:
            #   - col0_hdrspan set, continue with allowed current
            #   - col0_hdrspan set, expand, start new
            #   - col0_hdrspan set, no expand, start new
            if (
                not col0_followed_by_nonempty
                and
                # XXX Only one cat of tags: kunna/Swedish
                # XXX len(col0_cats) == 1 and
                col0_hdrspan.rowspan >= rowspan
                and
                # from hdrspan
                not (later_cats - later_allowed)
                and not (col0_cats & later_cats)
            ):
                # First case: col0 set, continue
                return col, col0_followed_by_nonempty, col0_hdrspan
            # We are going to start new col0_hdrspan.  Check if
            # we should expand.
            if (
                not col0_followed_by_nonempty
                and not (col0_cats - col0_allowed)
                and
                # Only "allowed" allowed
                # XXX len(col0_cats) == 1 and
                col_idx > col0_hdrspan.start + col0_hdrspan.colspan
            ):
                # col_idx is beyond current colspan
                # *Expand* current col0_hdrspan
                # print("EXPANDING COL0 MID: {} from {} to {} "
                #       "cols {}"
                #       .format(col0_hdrspan.text,
                #               col0_hdrspan.colspan,
                #               col_idx - col0_hdrspan.start,
                #               col0_hdrspan.tagsets))
                col0_hdrspan.colspan = col_idx - col0_hdrspan.start
                col0_hdrspan.expanded = True
            # Clear old col0_hdrspan
            if col == debug_cell_text:
                print("START NEW {}".format(hdrspan.tagsets))
            col0_hdrspan = None
            # Now start new, unless it comes from previous row
            if not previously_seen:
                col0_hdrspan = hdrspan
                col0_followed_by_nonempty = False
        return col, col0_followed_by_nonempty, col0_hdrspan

    def split_text_into_alts(col):
        # Split the cell text into alternatives
        split_extra_tags = []
        if col and is_superscript(col[0]):
            alts = [col]
        else:
            separators = [";", "•", r"\n", " or "]
            if " + " not in col:
                separators.append(",")
                if not col.endswith("/"):
                    separators.append("/")
            if col in special_phrase_splits:
                # Use language-specific special splits.
                # These are phrases and constructions that have
                # unique ways of splitting, not specific characters
                # to split on like with the default splitting.
                alts, tags = special_phrase_splits[col]
                split_extra_tags = tags.split()
                for x in split_extra_tags:
                    assert x in valid_tags
                assert isinstance(alts, (list, tuple))
                assert isinstance(tags, str)
            else:
                # Use default splitting.  However, recognize
                # language-specific replacements and change them to magic
                # characters before splitting.  This way we won't split
                # them.  This is important for, e.g., recognizing
                # alternative pronouns.
                # The magic characters are characters out of Unicode scope
                # that are given a simple incremental value, int > unicode.
                repls = {}
                magic_ch = MAGIC_FIRST
                trs = get_lang_conf(lang, "form_transformations")
                # trs is a list of lists of strings
                for _, v, _, _ in trs:
                    # v is a pattern string, like "^ich"
                    # form_transformations data is doing double-duty here,
                    # because the pattern strings are already known to us and
                    # not meant to be split.
                    m = re.search(v, col)
                    if m is not None:
                        # if pattern found in text
                        magic = chr(magic_ch)
                        magic_ch += 1  # next magic character value
                        col = re.sub(v, magic, col)  # replace with magic ch
                        repls[magic] = m.group(0)
                        # remember what regex match string each magic char
                        # replaces. .group(0) is the whole match.
                alts0 = split_at_comma_semi(col, separators=separators)
                # with magic characters in place, split the text so that
                # pre-transformation text is out of the way.
                alts = []
                for alt in alts0:
                    # create a new list with the separated items and
                    # the magic characters replaced with the original texts.
                    for k, v in repls.items():
                        alt = re.sub(k, v, alt)
                    alts.append(alt)
        # Remove "*" from beginning of forms, as in non-attested
        # or reconstructed forms.  Otherwise it might confuse romanization
        # detection.
        alts = list(re.sub(r"^\*\*?([^ ])", r"\1", x) for x in alts)
        alts = list(
            x for x in alts if not re.match(r"pronounced with |\(with ", x)
        )
        alts = list(
            re.sub(r"^\((in the sense [^)]*)\)\s+", "", x) for x in alts
        )
        # Check for parenthesized alternatives, e.g. ripromettersi/Italian
        if all(
            re.match(r"\w+( \w+)* \(\w+( \w+)*(, \w+( \w+)*)*\)$", alt)
            # word word* \(word word*(, word word*)*\)
            and all(
                distw([re.sub(r" \(.*", "", alt)], x) < 0.5
                # Levenshtein distance
                for x in re.sub(r".*\((.*)\)", r"\1", alt).split(", ")
            )
            # Extract from parentheses for testin
            for alt in alts
        ):
            new_alts = []
            for alt in alts:
                # Replace parentheses before splitting
                alt = alt.replace(" (", ", ")
                alt = alt.replace(")", "")
                for new_alt in alt.split(", "):
                    new_alts.append(new_alt)
            alts = new_alts
        return col, alts, split_extra_tags

    def handle_mixed_lines(alts):
        # Handle the special case where romanization is given under
        # normal form, e.g. in Russian.  There can be multiple
        # comma-separated forms in each case.  We also handle the case
        # where instead of romanization we have IPA pronunciation
        # (e.g., avoir/French/verb).
        len2 = len(alts) // 2
        # Check for IPAs (forms first, IPAs under)
        # base, base, IPA, IPA
        if (
            len(alts) % 2 == 0  # Divisibly by two
            and all(
                re.match(r"^\s*/.*/\s*$", x)  # Inside slashes = IPA
                for x in alts[len2:]
            )
        ):  # In the second half of alts
            alts = list(
                (alts[i], "", alts[i + len2])
                # List of tuples: (base, "", ipa)
                for i in range(len2)
            )
        # base, base, base, IPA
        elif (
            len(alts) > 2
            and re.match(r"^\s*/.*/\s*$", alts[-1])
            and all(not x.startswith("/") for x in alts[:-1])
        ):
            # Only if the last alt is IPA
            alts = list((alts[i], "", alts[-1]) for i in range(len(alts) - 1))
        # base, IPA, IPA, IPA
        elif (
            len(alts) > 2
            and not alts[0].startswith("/")
            and all(
                re.match(r"^\s*/.*/\s*$", alts[i]) for i in range(1, len(alts))
            )
        ):
            # First is base and the rest is IPA alternatives
            alts = list((alts[0], "", alts[i]) for i in range(1, len(alts)))

        # Check for romanizations, forms first, romanizations under
        elif (
            len(alts) % 2 == 0
            and not any("(" in x for x in alts)
            and all(
                classify_desc(
                    re.sub(
                        r"\^.*$",
                        "",
                        # Remove ends of strings starting from ^.
                        # Supescripts have been already removed
                        # from the string, while ^xyz needs to be
                        # removed separately, though it's usually
                        # something with a single letter?
                        "".join(xx for xx in x if not is_superscript(xx)),
                    )
                )
                == "other"
                for x in alts[:len2]
            )
            and all(
                classify_desc(
                    re.sub(
                        r"\^.*$",
                        "",
                        "".join(xx for xx in x if not is_superscript(xx)),
                    )
                )
                in ("romanization", "english")
                for x in alts[len2:]
            )
        ):
            alts = list((alts[i], alts[i + len2], "") for i in range(len2))
        # Check for romanizations, forms and romanizations alternating
        elif (
            len(alts) % 2 == 0
            and not any("(" in x for x in alts)
            and all(
                classify_desc(
                    re.sub(
                        r"\^.*$",
                        "",
                        "".join(xx for xx in alts[i] if not is_superscript(xx)),
                    )
                )
                == "other"
                for i in range(0, len(alts), 2)
            )
            and all(
                classify_desc(
                    re.sub(
                        r"\^.*$",
                        "",
                        "".join(xx for xx in alts[i] if not is_superscript(xx)),
                    )
                )
                in ("romanization", "english")
                for i in range(1, len(alts), 2)
            )
        ):
            # odds
            alts = list(
                (alts[i], alts[i + 1], "") for i in range(0, len(alts), 2)
            )
            # evens
        else:
            new_alts = []
            for alt in alts:
                lst = [""]
                idx = 0
                for m in re.finditer(
                    r"(^|\w|\*)\((\w+" r"(/\w+)*)\)",
                    # start OR letter OR asterisk (word/word*)
                    # \\___________group 1_______/ \    \_g3_///
                    # \                            \__gr. 2_//
                    #  \_____________group 0________________/
                    alt,
                ):
                    v = m.group(2)  # (word/word/word...)
                    if (
                        classify_desc(v) == "tags"  # Tags inside parens
                        or m.group(0) == alt
                    ):  # All in parens
                        continue
                    new_lst = []
                    for x in lst:
                        x += alt[idx : m.start()] + m.group(1)
                        # alt until letter or asterisk
                        idx = m.end()
                        vparts = v.split("/")
                        # group(2) = ["word", "wörd"...]
                        if len(vparts) == 1:
                            new_lst.append(x)
                            new_lst.append(x + v)
                            # "kind(er)" -> ["kind", "kinder"]
                        else:
                            for vv in vparts:
                                new_lst.append(x + vv)
                            # "lampai(tten/den)" ->
                            # ["lampaitten", "lampaiden"]
                    lst = new_lst
                for x in lst:
                    new_alts.append(x + alt[idx:])
                    # add the end of alt
            alts = list((x, "", "") for x in new_alts)
            # [form, no romz, no ipa]
        return alts

    def find_semantic_parens(form):
        # "Some languages" (=Greek) use brackets to mark things that
        # require tags, like (informality), [rarity] and {archaicity}.
        extra_tags = []
        if re.match(r"\([^][(){}]*\)$", form):
            if get_lang_conf(lang, "parentheses_for_informal"):
                form = form[1:-1]
                extra_tags.append("informal")
            else:
                form = form[1:-1]
        elif re.match(r"\{\[[^][(){}]*\]\}$", form):
            if get_lang_conf(
                lang, "square_brackets_for_rare"
            ) and get_lang_conf(lang, "curly_brackets_for_archaic"):
                # είμαι/Greek/Verb
                form = form[2:-2]
                extra_tags.extend(["rare", "archaic"])
            else:
                form = form[2:-2]
        elif re.match(r"\{[^][(){}]*\}$", form):
            if get_lang_conf(lang, "curly_brackets_for_archaic"):
                # είμαι/Greek/Verb
                form = form[1:-1]
                extra_tags.extend(["archaic"])
            else:
                form = form[1:-1]
        elif re.match(r"\[[^][(){}]*\]$", form):
            if get_lang_conf(lang, "square_brackets_for_rare"):
                # είμαι/Greek/Verb
                form = form[1:-1]
                extra_tags.append("rare")
            else:
                form = form[1:-1]
        return form, extra_tags

    def handle_parens(form, roman, clitic, extra_tags):
        if re.match(r"[’'][a-z]([a-z][a-z]?)?$", paren):
            # is there a clitic starting with apostrophe?
            clitic = paren
            # assume the whole paren is a clitic
            # then remove paren from form
            form = (form[: m.start()] + subst + form[m.end() :]).strip()
        elif classify_desc(paren) == "tags":
            tagsets1, topics1 = decode_tags(paren)
            if not topics1:
                for ts in tagsets1:
                    ts = list(x for x in ts if " " not in x)
                    # There are some generated tags containing
                    # spaces; do not let them through here.
                    extra_tags.extend(ts)
                form = (form[: m.start()] + subst + form[m.end() :]).strip()
        # brackets contain romanization
        elif (
            m.start() > 0
            and not roman
            and classify_desc(form[: m.start()]) == "other"
            and
            # "other" ~ text
            classify_desc(paren) in ("romanization", "english")
            and not re.search(r"^with |-form$", paren)
        ):
            roman = paren
            form = (form[: m.start()] + subst + form[m.end() :]).strip()
        elif re.search(r"^with |-form", paren):
            form = (form[: m.start()] + subst + form[m.end() :]).strip()
        return form, roman, clitic

    def merge_row_and_column_tags(form, some_has_covered_text):
        # Merge column tags and row tags.  We give preference
        # to moods etc coming from rowtags (cf. austteigen/German/Verb
        # imperative forms).

        # In certain cases, what a tag means depends on whether
        # it is a row or column header. Depending on the language,
        # we replace certain tags with others if they're in
        # a column or row

        ret = []
        # rtagreplacs = get_lang_conf(lang, "rowtag_replacements")
        # ctagreplacs = get_lang_conf(lang, "coltag_replacements")
        for rt in sorted(rowtags):
            if "dummy-use-as-coltags" in rt:
                continue
            # if lang was in rowtag_replacements)
            # if not rtagreplacs == None:
            # rt = replace_directional_tags(rt, rtagreplacs)
            for ct in sorted(coltags):
                if "dummy-use-as-rowtags" in ct:
                    continue
                # if lang was in coltag_replacements
                # if not ctagreplacs == None:
                # ct = replace_directional_tags(ct,
                # ctagreplacs)
                tags = set(global_tags)
                tags.update(extra_tags)
                tags.update(rt)
                tags.update(refs_tags)
                tags.update(tablecontext.section_header)
                # Merge tags from column.  For certain kinds of tags,
                # those coming from row take precedence.
                old_tags = set(tags)
                for t in ct:
                    c = valid_tags[t]
                    if c in ("mood", "case", "number") and any(
                        valid_tags[tt] == c for tt in old_tags
                    ):
                        continue
                    tags.add(t)

                # Extract language-specific tags from the
                # form.  This may also adjust the form.
                form, lang_tags = lang_specific_tags(lang, pos, form)
                tags.update(lang_tags)

                # For non-finite verb forms, see if they have
                # a gender/class suffix
                if pos == "verb" and any(
                    valid_tags[t] == "non-finite" for t in tags
                ):
                    form, tt = parse_head_final_tags(wxr, lang, form)
                    tags.update(tt)

                # Remove "personal" tag if have nth person; these
                # come up with e.g. reconhecer/Portuguese/Verb.  But
                # not if we also have "pronoun"
                if (
                    "personal" in tags
                    and "pronoun" not in tags
                    and any(
                        x in tags
                        for x in [
                            "first-person",
                            "second-person",
                            "third-person",
                        ]
                    )
                ):
                    tags.remove("personal")

                # If we have impersonal, remove person and number.
                # This happens with e.g. viajar/Portuguese/Verb
                if "impersonal" in tags:
                    tags = tags - set(
                        [
                            "first-person",
                            "second-person",
                            "third-person",
                            "singular",
                            "plural",
                        ]
                    )

                # Remove unnecessary "positive" tag from verb forms
                if pos == "verb" and "positive" in tags:
                    if "negative" in tags:
                        tags.remove("negative")
                    tags.remove("positive")

                # Many Russian (and other Slavic) inflection tables
                # have animate/inanimate distinction that generates
                # separate entries for neuter/feminine, but the
                # distinction only applies to masculine.  Remove them
                # form neuter/feminine and eliminate duplicates.
                if get_lang_conf(lang, "masc_only_animate"):
                    for t1 in ("animate", "inanimate"):
                        for t2 in ("neuter", "feminine"):
                            if (
                                t1 in tags
                                and t2 in tags
                                and "masculine" not in tags
                                and "plural" not in tags
                            ):
                                tags.remove(t1)

                # German adjective tables contain "(keiner)" etc
                # for mixed declension plural.  When the adjective
                # disappears and it becomes just one word, remove
                # the "includes-article" tag.  e.g. eiskalt/German
                if "includes-article" in tags and " " not in form:
                    tags.remove("includes-article")

                # Handle ignored forms.  We mark that the form was
                # provided.  This is important information; some words
                # just do not have a certain form.  However, there also
                # many cases where no word in a language has a
                # particular form.  Post-processing could detect and
                # remove such cases.
                if form in IGNORED_COLVALUES:
                    # if cell text seems to be ignorable
                    if "dummy-ignore-skipped" in tags:
                        continue
                    if (
                        col_idx not in has_covering_hdr
                        and some_has_covered_text
                    ):
                        continue
                    # don't ignore this cell if there's been a header
                    # above it
                    form = "-"
                elif col_idx in has_covering_hdr:
                    some_has_covered_text = True

                # Handle ambiguous object concord. If a header
                # gives the "dummy-object-concord"-tag to a word,
                # replace person, number and gender tags with
                # their "object-" counterparts so that the verb
                # agrees with the object instead.
                # Use only when the verb has ONLY object agreement!
                # a پخول/Pashto
                if "dummy-object-concord" in tags:
                    for subtag, objtag in object_concord_replacements.items():
                        if subtag in tags:
                            tags.remove(subtag)
                            tags.add(objtag)

                # Remove the dummy mood tag that we sometimes
                # use to block adding other mood and related
                # tags
                tags = tags - set(
                    [
                        "dummy-mood",
                        "dummy-tense",
                        "dummy-ignore-skipped",
                        "dummy-object-concord",
                        "dummy-reset-headers",
                        "dummy-use-as-coltags",
                        "dummy-use-as-rowtags",
                        "dummy-store-hdrspan",
                        "dummy-load-stored-hdrspans",
                        "dummy-reset-stored-hdrspans",
                        "dummy-section-header",
                    ]
                )

                # Perform language-specific tag replacements according
                # to rules in a table.
                lang_tag_mappings = get_lang_conf(lang, "lang_tag_mappings")
                if lang_tag_mappings is not None:
                    for pre, post in lang_tag_mappings.items():
                        if all(t in tags for t in pre):
                            tags = (tags - set(pre)) | set(post)

                # Warn if there are entries with empty tags
                if not tags:
                    wxr.wtp.debug(
                        "inflection table: empty tags for {}".format(form),
                        sortid="inflection/1826",
                    )

                # Warn if form looks like IPA
                ########## XXX ########
                # Because IPA is its own unicode block, we could also
                # technically do a Unicode name check to see if a string
                # contains IPA. Not all valid IPA characters are in the
                # IPA extension block, so you can technically have false
                # negatives if it's something like /toki/, but it
                # shouldn't give false positives.
                # Alternatively, you could make a list of IPA-admissible
                # characters and reject non-IPA stuff with that.
                if re.match(r"\s*/.*/\s*$", form):
                    wxr.wtp.debug(
                        "inflection table form looks like IPA: "
                        "form={} tags={}".format(form, tags),
                        sortid="inflection/1840",
                    )

                # Note that this checks `form`, not `in tags`
                if form == "dummy-ignored-text-cell":
                    continue

                if "dummy-remove-this-cell" in tags:
                    continue

                # Add the form
                tags = list(sorted(tags))
                dt = {"form": form, "tags": tags, "source": source}
                if roman:
                    dt["roman"] = roman
                if ipa:
                    dt["ipa"] = ipa
                ret.append(dt)
                # If we got separate clitic form, add it
                if clitic:
                    dt = {
                        "form": clitic,
                        "tags": tags + ["clitic"],
                        "source": source,
                    }
                    ret.append(dt)
        return ret, form, some_has_covered_text

    # First extract definitions from cells
    # See defs_ht for footnote defs stuff
    for row in rows:
        for cell in row:
            text, refs, defs, hdr_tags = extract_cell_content(
                lang, word, cell.text
            )
            # refs, defs = footnote stuff, defs -> (ref, def)
            add_defs(defs)
    # Extract definitions from text after table
    text, refs, defs, hdr_tags = extract_cell_content(lang, word, after)
    add_defs(defs)

    # Then extract the actual forms
    ret = []
    hdrspans = []
    first_col_has_text = False
    rownum = 0
    title = None
    global_tags = []
    table_tags = []
    special_phrase_splits = get_lang_conf(lang, "special_phrase_splits")
    form_replacements = get_lang_conf(lang, "form_replacements")
    possibly_ignored_forms = get_lang_conf(lang, "conditionally_ignored_cells")
    cleanup_rules = get_lang_conf(lang, "minor_text_cleanups")

    for title in titles:
        more_global_tags, more_table_tags, extra_forms = parse_title(
            title, source
        )
        global_tags.extend(more_global_tags)
        table_tags.extend(more_table_tags)
        ret.extend(extra_forms)
    cell_rowcnt = collections.defaultdict(int)
    seen_cells = set()
    has_covering_hdr = set()
    some_has_covered_text = False
    for row in rows:
        # print("ROW:", row)
        # print("====")
        # print(f"Start of PREVIOUS row hdrspans:"
        # f"{tuple(sp.tagsets for sp in hdrspans)}")
        # print(f"Start of row txt: {tuple(t.text for t in row)}")
        if not row:
            continue  # Skip empty rows
        all_headers = all(x.is_title or not x.text.strip() for x in row)
        text = row[0].text
        if (
            row[0].is_title
            and text
            and not is_superscript(text[0])
            and text not in infl_map  # zealous inflation map?
            and (
                re.match(r"Inflection ", text)
                or re.sub(
                    r"\s+",
                    " ",  # flatten whitespace
                    re.sub(
                        r"\s*\([^)]*\)",
                        "",
                        # Remove whitespace+parens
                        text,
                    ),
                ).strip()
                not in infl_map
            )
            and not re.match(infl_start_re, text)
            and all(
                x.is_title == row[0].is_title and x.text == text
                # all InflCells in `row` have the same is_title and text
                for x in row
            )
        ):
            if text and title is None:
                # Only if there were no titles previously make the first
                # text that is found the title
                title = text
                if re.match(r"(Note:|Notes:)", title):
                    continue  # not a title
                more_global_tags, more_table_tags, extra_forms = parse_title(
                    title, source
                )
                global_tags.extend(more_global_tags)
                table_tags.extend(more_table_tags)
                ret.extend(extra_forms)
            continue  # Skip title rows without incrementing i
        if "dummy-skip-this" in global_tags:
            return []
        rowtags = [()]
        have_hdr = False
        have_text = False
        samecell_cnt = 0
        col0_hdrspan = None  # col0 or later header (despite its name)
        col0_followed_by_nonempty = False
        row_empty = True
        for col_idx, cell in enumerate(row):
            colspan = cell.colspan  # >= 1
            rowspan = cell.rowspan  # >= 1
            previously_seen = id(cell) in seen_cells
            # checks to see if this cell was in the previous ROW
            seen_cells.add(id(cell))
            if samecell_cnt == 0:
                # First column of a (possible multi-column) cell
                samecell_cnt = colspan - 1
            else:
                assert samecell_cnt > 0
                samecell_cnt -= 1
                continue
            is_first_row_of_cell = cell_rowcnt[id(cell)] == 0
            # defaultdict(int) around line 1900
            cell_rowcnt[id(cell)] += 1
            # => how many cols this spans
            col = cell.text
            if not col:
                continue
            row_empty = False
            is_title = cell.is_title

            # If the cell has a target, i.e., text after colon, interpret
            # it as simply specifying a value for that value and ignore
            # it otherwise.
            if cell.target:
                text, refs, defs, hdr_tags = extract_cell_content(
                    lang, word, col
                )
                if not text:
                    continue
                refs_tags = set()
                for ref in refs:  # gets tags from footnotes
                    if ref in def_ht:
                        refs_tags.update(def_ht[ref])
                rowtags = expand_header(
                    wxr,
                    tablecontext,
                    word,
                    lang,
                    pos,
                    text,
                    [],
                    silent=True,
                    depth=depth,
                )
                rowtags = list(
                    set(tuple(sorted(set(x) | refs_tags)) for x in rowtags)
                )
                is_title = False
                col = cell.target

            # print(rownum, col_idx, col)
            # print(f"is_title: {is_title}")
            if is_title:
                # It is a header cell
                text, refs, defs, hdr_tags = extract_cell_content(
                    lang, word, col
                )
                if not text:
                    continue
                # Extract tags from referenced footnotes
                refs_tags = set()
                for ref in refs:
                    if ref in def_ht:
                        refs_tags.update(def_ht[ref])

                # Expand header to tags
                v = expand_header(
                    wxr,
                    tablecontext,
                    word,
                    lang,
                    pos,
                    text,
                    [],
                    silent=True,
                    depth=depth,
                )
                # print("EXPANDED {!r} to {}".format(text, v))

                if col_idx == 0:
                    # first_col_has_text is used for a test to ignore
                    # upper-left cells that are just text without
                    # header info
                    first_col_has_text = True
                # Check if the header expands to reset hdrspans
                if any("dummy-reset-headers" in tt for tt in v):
                    new_hdrspans = []
                    for hdrspan in hdrspans:
                        # if there are HdrSpan objects (abstract headers with
                        # row- and column-spans) that are to the left or at the
                        # same row or below, KEEP those; things above and to
                        # the right of the hdrspan with dummy-reset-headers
                        # are discarded. Tags from the header together with
                        # dummy-reset-headers are kept as normal.
                        if (
                            hdrspan.start + hdrspan.colspan < col_idx
                            or hdrspan.rownum > rownum - cell.rowspan
                        ):
                            new_hdrspans.append(hdrspan)
                    hdrspans = new_hdrspans

                for tt in v:
                    if "dummy-section-header" in tt:
                        tablecontext.section_header = tt
                        break
                    if "dummy-reset-section-header" in tt:
                        tablecontext.section_header = []
                # Text between headers on a row causes earlier headers to
                # be reset
                if have_text:
                    # print("  HAVE_TEXT BEFORE HDR:", col)
                    # Reset rowtags if new title column after previous
                    # text cells
                    #  +-----+-----+-----+-----+
                    #  |hdr-a|txt-a|hdr-B|txt-B|
                    #  +-----+-----+-----+-----+
                    #               ^reset rowtags=>
                    # XXX beware of header "—": "" - must not clear on that if
                    # it expands to no tags
                    rowtags = [()]
                have_hdr = True
                # print("HAVE_HDR: {} rowtags={}".format(col, rowtags))
                # Update rowtags and coltags
                has_covering_hdr.add(col_idx)  # col_idx == current column
                # has_covering_hdr is a set that has the col_idx-ids of columns
                # that have previously had some kind of header. It is never
                # resetted inside the col_idx-loops OR the bigger rows-loop, so
                # applies to the whole table.

                rowtags, new_coltags, all_hdr_tags = generate_tags(
                    rowtags, table_tags
                )

                if any("dummy-skip-this" in ts for ts in rowtags):
                    continue  # Skip this cell

                if any("dummy-load-stored-hdrspans" in ts for ts in v):
                    hdrspans.extend(tablecontext.stored_hdrspans)

                if any("dummy-reset-stored-hdrspans" in ts for ts in v):
                    tablecontext.stored_hdrspans = []

                if any("dummy-store-hdrspan" in ts for ts in v):
                    # print(f"STORED: {col}")
                    store_new_hdrspan = True
                else:
                    store_new_hdrspan = False

                new_coltags = list(
                    x
                    for x in new_coltags
                    if not any(t in noinherit_tags for t in x)
                )
                # print("new_coltags={} previously_seen={} all_hdr_tags={}"
                #       .format(new_coltags, previously_seen, all_hdr_tags))
                if any(new_coltags):
                    (
                        col,
                        col0_followed_by_nonempty,
                        col0_hdrspan,
                    ) = add_new_hdrspan(
                        col,
                        hdrspans,
                        store_new_hdrspan,
                        col0_followed_by_nonempty,
                        col0_hdrspan,
                    )

                continue

            # These values are ignored, at least for now
            if re.match(r"^(# |\(see )", col):
                continue

            if any("dummy-skip-this" in ts for ts in rowtags):
                continue  # Skip this cell

            # If the word has no rowtags and is a multi-row cell, then
            # ignore this.  This happens with empty separator rows
            # within a rowspan>1 cell.  cf. wander/English/Conjugation.
            if rowtags == [()] and rowspan > 1:
                continue

            # Minor cleanup.  See e.g. είμαι/Greek/Verb present participle.
            if cleanup_rules:
                for regx, substitution in cleanup_rules.items():
                    col = re.sub(regx, substitution, col)

            if (
                col_idx == 0
                and not first_col_has_text
                and get_lang_conf(lang, "ignore_top_left_text_cell") == True
            ):
                continue  # Skip text at top left, as in Icelandic, Faroese

            # if col0_hdrspan is not None:
            #     print("COL0 FOLLOWED NONHDR: {!r} by {!r}"
            #           .format(col0_hdrspan.text, col))
            col0_followed_by_nonempty = True
            have_text = True

            # Determine column tags for the multi-column cell
            combined_coltags = compute_coltags(
                lang, pos, hdrspans, col_idx, colspan, col
            )
            if any("dummy-ignored-text-cell" in ts for ts in combined_coltags):
                continue

            # print("HAVE_TEXT:", repr(col))
            # Split the text into separate forms.  First simplify spaces except
            # newline.
            col = re.sub(r"[ \t\r]+", " ", col)
            # Split the cell text into alternatives

            col, alts, split_extra_tags = split_text_into_alts(col)

            # Some cells have mixed form content, like text and romanization,
            # or text and IPA. Handle these.
            alts = handle_mixed_lines(alts)

            alts = list((x, combined_coltags) for x in alts)

            # Generate forms from the alternatives
            # alts is a list of (tuple of forms, tuple of tags)
            for (form, base_roman, ipa), coltags in alts:
                form = form.strip()
                extra_tags = []
                extra_tags.extend(split_extra_tags)
                # Handle special splits again here, so that we can have custom
                # mappings from form to form and tags.
                if form in form_replacements:
                    replacement, tags = form_replacements[form]
                    for x in tags.split():
                        assert x in valid_tags
                    assert isinstance(replacement, str)
                    assert isinstance(tags, str)
                    form = replacement
                    extra_tags.extend(tags.split())
                # Clean the value, extracting reference symbols
                form, refs, defs, hdr_tags = extract_cell_content(
                    lang, word, form
                )
                # if refs:
                #     print("REFS:", refs)
                extra_tags.extend(hdr_tags)
                # Extract tags from referenced footnotes
                # Extract tags from referenced footnotes
                refs_tags = set()
                for ref in refs:
                    if ref in def_ht:
                        refs_tags.update(def_ht[ref])

                if base_roman:
                    base_roman, _, _, hdr_tags = extract_cell_content(
                        lang, word, base_roman
                    )
                    extra_tags.extend(hdr_tags)

                # Do some additional cleanup on the cell.
                form = re.sub(r"^\s*,\s*", "", form)
                form = re.sub(r"\s*,\s*$", "", form)
                form = re.sub(r"\s*(,\s*)+", ", ", form)
                form = re.sub(r"(?i)^Main:", "", form)
                form = re.sub(r"\s+", " ", form)
                form = form.strip()

                # Look for parentheses that have semantic meaning
                form, et = find_semantic_parens(form)
                extra_tags.extend(et)

                # Handle parentheses in the table element.  We parse
                # tags anywhere and romanizations anywhere but beginning.
                roman = base_roman
                paren = None
                clitic = None
                m = re.search(r"(\s+|^)\(([^)]*)\)", form)
                # start|spaces + (anything)
                if m is not None:
                    subst = m.group(1)
                    paren = m.group(2)
                else:
                    m = re.search(r"\(([^)]*)\)(\s+|$)", form)
                    # (anything) + spaces|end
                    if m is not None:
                        paren = m.group(1)
                        subst = m.group(2)
                if paren is not None:
                    form, roman, clitic = handle_parens(
                        form, roman, clitic, extra_tags
                    )

                # Ignore certain forms that are not really forms,
                # unless they're really, really close to the article title
                if form in (
                    "",
                    "unchanged",
                    "after an",  # in sona/Irish/Adj/Mutation
                ):
                    Lev = distw([form], word)
                    if form and Lev < 0.1:
                        wxr.wtp.debug(
                            "accepted possible false positive '{}' with"
                            "> 0.1 Levenshtein distance in {}/{}".format(
                                form, word, lang
                            ),
                            sortid="inflection/2213",
                        )
                    elif form and Lev < 0.3:
                        wxr.wtp.debug(
                            "skipped possible match '{}' with > 0.3"
                            "Levenshtein distance in {}/{}".format(
                                form, word, lang
                            ),
                            sortid="inflection/2218",
                        )
                        continue
                    else:
                        continue
                # print("ROWTAGS={} COLTAGS={} REFS_TAGS={} "
                #       "FORM={!r} ROMAN={!r}"
                #       .format(rowtags, coltags, refs_tags,
                #               form, roman))

                # Merge tags from row and column and do miscellaneous
                # tag-related handling.
                (
                    merge_ret,
                    form,
                    some_has_covered_text,
                ) = merge_row_and_column_tags(form, some_has_covered_text)
                ret.extend(merge_ret)

        # End of row.
        rownum += 1
        # For certain languages, if the row was empty, reset
        # hdrspans (saprast/Latvian/Verb, but not aussteigen/German/Verb).
        if row_empty and get_lang_conf(lang, "empty_row_resets"):
            hdrspans = []
        # Check if we should expand col0_hdrspan.
        if col0_hdrspan is not None:
            col0_allowed = get_lang_conf(lang, "hdr_expand_first")
            col0_cats = tagset_cats(col0_hdrspan.tagsets)
            # Only expand if col0_cats and later_cats are allowed
            # and don't overlap and col0 has tags, and there have
            # been no disallowed cells in between.
            if (
                not col0_followed_by_nonempty
                and not (col0_cats - col0_allowed)
                and
                # len(col0_cats) == 1 and
                col_idx > col0_hdrspan.start + col0_hdrspan.colspan
            ):
                # If an earlier header is only followed by headers that yield
                # no tags, expand it to entire row
                # print("EXPANDING COL0: {} from {} to {} cols {}"
                #       .format(col0_hdrspan.text, col0_hdrspan.colspan,
                #               len(row) - col0_hdrspan.start,
                #               col0_hdrspan.tagsets))
                col0_hdrspan.colspan = len(row) - col0_hdrspan.start
                col0_hdrspan.expanded = True
    # XXX handle refs and defs
    # for x in hdrspans:
    #     print("  HDRSPAN {} {} {} {!r}"
    #           .format(x.start, x.colspan, x.tagsets, x.text))

    # Post-process German nouns with articles in separate columns.  We move the
    # definite/indefinite/usually-without-article markers into the noun and
    # remove the article entries.
    if get_lang_conf(lang, "articles_in_separate_columns") and any(
        "noun" in x["tags"] for x in ret
    ):
        new_ret = []
        saved_tags = set()
        had_noun = False
        for dt in ret:
            tags = dt["tags"]
            # print(tags)
            if "noun" in tags:
                tags = list(
                    sorted(set(t for t in tags if t != "noun") | saved_tags)
                )
                had_noun = True
            elif (
                "indefinite" in tags
                or "definite" in tags
                or "usually-without-article" in tags
                or "without-article" in tags
            ):
                if had_noun:
                    saved_tags = set(tags)
                else:
                    saved_tags = saved_tags | set(tags)  # E.g. Haus/German
                    remove_useless_tags(lang, pos, saved_tags)
                saved_tags = saved_tags & set(
                    [
                        "masculine",
                        "feminine",
                        "neuter",
                        "singular",
                        "plural",
                        "indefinite",
                        "definite",
                        "usually-without-article",
                        "without-article",
                    ]
                )
                had_noun = False
                continue  # Skip the articles

            dt = dt.copy()
            dt["tags"] = tags
            new_ret.append(dt)
        ret = new_ret

    elif possibly_ignored_forms:
        # Some languages have tables with cells that are kind of separated
        # and difficult to handle, like eulersche Formel/German where
        # the definite and indefinite articles are just floating.
        # If a language has a dict of conditionally_ignored_cells,
        # and if the contents of a cell is found in one of the rules
        # there, ignore that cell if it
        # 1. Does not have the appropriate tag (like "definite" for "die")
        # and
        # 2. The title of the article is not one of the other co-words
        #    (ie. it's an article for the definite articles in german etc.)
        # pass
        new_ret = []
        for cell_data in ret:
            tags = cell_data["tags"]
            text = cell_data["form"]
            skip_this = False
            for key_tag, ignored_forms in possibly_ignored_forms.items():
                if text not in ignored_forms:
                    continue
                if word in ignored_forms:
                    continue
                if key_tag not in tags:
                    skip_this = True

            if skip_this:
                continue
            new_ret.append(cell_data)

        ret = new_ret

    # Post-process English inflection tables, addding "multiword-construction"
    # when the number of words has increased.
    if lang == "English" and pos == "verb":
        word_words = len(word.split())
        new_ret = []
        for dt in ret:
            form = dt.get("form", "")
            if len(form.split()) > word_words:
                dt = dt.copy()
                dt["tags"] = list(dt.get("tags", []))
                # This strange copy-assigning shuffle is preventative black
                # magic; do not touch lest you invoke deep bugs.
                data_append(dt, "tags", "multiword-construction")
            new_ret.append(dt)
        ret = new_ret

    # Always insert "table-tags" detail as the first entry in any inflection
    # table.  This way we can reliably detect where a new table starts.
    # Table-tags applies until the next table-tags entry.
    if ret or table_tags:
        table_tags = list(sorted(set(table_tags)))
        dt = {
            "form": " ".join(table_tags),
            "source": source,
            "tags": ["table-tags"],
        }
        if dt["form"] == "":
            dt["form"] = "no-table-tags"
        if tablecontext.template_name:
            tn = {
                "form": tablecontext.template_name,
                "source": source,
                "tags": ["inflection-template"],
            }
            ret = [dt] + [tn] + ret
        else:
            ret = [dt] + ret

    return ret


def handle_generic_table(
    wxr, tablecontext, data, word, lang, pos, rows, titles, source, after, depth
):
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(data, dict)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(rows, list)
    assert isinstance(source, str)
    assert isinstance(after, str)
    assert isinstance(depth, int)
    for row in rows:
        assert isinstance(row, list)
        for x in row:
            assert isinstance(x, InflCell)
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)

    # Try to parse the table as a simple table
    ret = parse_simple_table(
        wxr, tablecontext, word, lang, pos, rows, titles, source, after, depth
    )
    if ret is None:
        # XXX handle other table formats
        # We were not able to handle the table
        wxr.wtp.debug(
            "unhandled inflection table format, {}/{}".format(word, lang),
            sortid="inflection/2370",
        )
        return

    # Add the returned forms but eliminate duplicates.
    have_forms = set()
    for dt in ret:
        fdt = freeze(dt)
        if fdt in have_forms:
            continue  # Don't add duplicates
        # Some Russian words have Declension and Pre-reform declension partially
        # duplicating same data.  Don't add "dated" tags variant if already have
        # the same without "dated" from the modern declension table

        tags = dt.get("tags", [])
        for dated_tag in ("dated",):
            if dated_tag in tags:
                dt2 = dt.copy()
                tags2 = list(x for x in tags if x != dated_tag)
                dt2["tags"] = tags2
                if tags2 and freeze(dt2) in have_forms:
                    break  # Already have without archaic
        else:
            if "table-tags" not in tags:
                have_forms.add(fdt)
            data_append(data, "forms", dt)


def determine_header(
    wxr,
    tablecontext,
    lang,
    word,
    pos,
    table_kind,
    kind,
    style,
    row,
    col,
    celltext,
    titletext,
    cols_headered,
    target,
    cellstyle,
):
    assert isinstance(table_kind, NodeKind)
    assert isinstance(kind, (NodeKind, str))
    assert style is None or isinstance(style, str)
    assert cellstyle is None or isinstance(cellstyle, str)

    if table_kind == NodeKind.TABLE:
        header_kind = NodeKind.TABLE_HEADER_CELL
    elif table_kind == NodeKind.HTML:
        header_kind = "th"
    idx = celltext.find(": ")
    is_title = False
    # remove anything in parentheses, compress whitespace, .strip()
    cleaned_titletext = re.sub(
        r"\s+", " ", re.sub(r"\s*\([^)]*\)", "", titletext)
    ).strip()
    cleaned, _, _, _ = extract_cell_content(lang, word, celltext)
    cleaned = re.sub(r"\s+", " ", cleaned)
    hdr_expansion = expand_header(
        wxr,
        tablecontext,
        word,
        lang,
        pos,
        cleaned,
        [],
        silent=True,
        ignore_tags=True,
    )
    candidate_hdr = not any(
        any(t.startswith("error-") for t in ts) for ts in hdr_expansion
    )
    # KJ candidate_hdr says that a specific cell is a candidate
    # for being a header because it passed through expand_header
    # without getting any "error-" tags; that is, the contents
    # is "valid" for being a header; these are the false positives
    # we want to catch
    ignored_cell = any(
        any(t.startswith("dummy-") for t in ts) for ts in hdr_expansion
    )
    # ignored_cell should NOT be used to filter for headers, like
    # candidate_hdr is used, but only to filter for related *debug
    # messages*: some dummy-tags are actually half-way to headers,
    # like ones with "Notes", so they MUST be headers, but later
    # on they're ignored *as* headers so they don't need to print
    # out any cells-as-headers debug messages.
    if (
        candidate_hdr
        and kind != header_kind
        and cleaned != ""
        and cleaned != "dummy-ignored-text-cell"
        and cleaned not in IGNORED_COLVALUES
    ):
        # print("col: {}".format(col))
        if not ignored_cell and lang not in LANGUAGES_WITH_CELLS_AS_HEADERS:
            wxr.wtp.debug(
                "rejected heuristic header: "
                "table cell identified as header and given "
                "candidate status, BUT {} is not in "
                "LANGUAGES_WITH_CELLS_AS_HEADERS; "
                "cleaned text: {}".format(lang, cleaned),
                sortid="inflection/2447",
            )
            candidate_hdr = False
        elif cleaned not in LANGUAGES_WITH_CELLS_AS_HEADERS.get(lang, ""):
            wxr.wtp.debug(
                "rejected heuristic header: "
                "table cell identified as header and given "
                "candidate status, BUT the cleaned text is "
                "not in LANGUAGES_WITH_CELLS_AS_HEADERS[{}]; "
                "cleaned text: {}".format(lang, cleaned),
                sortid="inflection/2457",
            )
            candidate_hdr = False
        else:
            wxr.wtp.debug(
                "accepted heuristic header: "
                "table cell identified as header and given "
                "candidate status, AND the cleaned text is "
                "in LANGUAGES_WITH_CELLS_AS_HEADERS[{}]; "
                "cleaned text: {}".format(lang, cleaned),
                sortid="inflection/2466",
            )

    # If the cell starts with something that could start a
    # definition (typically a reference symbol), make it a candidate
    # regardless of whether the language is listed.
    if re.match(def_re, cleaned) and not re.match(nondef_re, cleaned):
        candidate_hdr = True

    # print("titletext={!r} hdr_expansion={!r} candidate_hdr={!r} "
    #      "lang={} pos={}"
    #      .format(titletext, hdr_expansion, candidate_hdr,
    #              lang, pos))
    if idx >= 0 and titletext[:idx] in infl_map:
        target = titletext[idx + 2 :].strip()
        celltext = celltext[:idx]
        is_title = True
    elif (
        kind == header_kind
        and " + " not in titletext  # For "avoir + blah blah"?
        and not any(
            isinstance(x, WikiNode)
            and x.kind == NodeKind.HTML
            and x.sarg == "span"
            and x.attrs.get("lang") in ("az",)
            for x in col.children
        )
    ):
        is_title = True
    elif (
        candidate_hdr
        and cleaned_titletext not in IGNORED_COLVALUES
        and distw([cleaned_titletext], word) > 0.3
        and cleaned_titletext not in ("I", "es")
    ):
        is_title = True
    #  if first column or same style as first column
    elif (
        style == cellstyle
        and
        # and title is not identical to word name
        titletext != word
        and cleaned not in IGNORED_COLVALUES
        and cleaned != "dummy-ignored-text-cell"
        and
        #  the style composite string is not broken
        not style.startswith("////")
        and " + " not in titletext
    ):
        if not ignored_cell and lang not in LANGUAGES_WITH_CELLS_AS_HEADERS:
            wxr.wtp.debug(
                "rejected heuristic header: "
                "table cell identified as header based "
                "on style, BUT {} is not in "
                "LANGUAGES_WITH_CELLS_AS_HEADERS; "
                "cleaned text: {}, style: {}".format(lang, cleaned, style),
                sortid="inflection/2512",
            )
        elif (
            not ignored_cell
            and cleaned not in LANGUAGES_WITH_CELLS_AS_HEADERS.get(lang, "")
        ):
            wxr.wtp.debug(
                "rejected heuristic header: "
                "table cell identified as header based "
                "on style, BUT the cleaned text is "
                "not in LANGUAGES_WITH_CELLS_AS_HEADERS[{}]; "
                "cleaned text: {}, style: {}".format(lang, cleaned, style),
                sortid="inflection/2522",
            )
        else:
            wxr.wtp.debug(
                "accepted heuristic header: "
                "table cell identified as header based "
                "on style, AND the cleaned text is "
                "in LANGUAGES_WITH_CELLS_AS_HEADERS[{}]; "
                "cleaned text: {}, style: {}".format(lang, cleaned, style),
                sortid="inflection/2530",
            )
            is_title = True
    if (
        not is_title
        and len(row) < len(cols_headered)
        and cols_headered[len(row)]
    ):
        # Whole column has title suggesting they are headers
        # (e.g. "Case")
        is_title = True
    if re.match(
        r"Conjugation of |Declension of |Inflection of |"
        r"Mutation of |Notes\b",  # \b is word-boundary
        titletext,
    ):
        is_title = True
    return is_title, hdr_expansion, target, celltext


class TableContext:
    """Saved context used when parsing a table and its subtables."""

    __slot__ = (
        "stored_hdrspans",
        "section_header",
        "template_name",
    )

    def __init__(self, template_name=None):
        self.stored_hdrspans = []
        self.section_header = []
        if not template_name:
            self.template_name = ""
        else:
            self.template_name = template_name


def handle_wikitext_or_html_table(
    wxr, word, lang, pos, data, tree, titles, source, after, tablecontext=None
):
    """Parses a table from parsed Wikitext format into rows and columns of
    InflCell objects and then calls handle_generic_table() to parse it into
    forms.  This adds the forms into ``data``."""
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(data, dict)
    assert isinstance(tree, WikiNode)
    assert tree.kind == NodeKind.TABLE or (
        tree.kind == NodeKind.HTML and tree.sarg == "table"
    )
    assert isinstance(titles, list)
    assert isinstance(source, str)
    for x in titles:
        assert isinstance(x, str)
    assert isinstance(after, str)
    assert tablecontext is None or isinstance(tablecontext, TableContext)
    # Imported here to avoid a circular import
    from wiktextract.page import clean_node, recursively_extract

    if not tablecontext:
        tablecontext = TableContext()

    def handle_table1(
        wxr,
        tablecontext,
        word,
        lang,
        pos,
        data,
        tree,
        titles,
        source,
        after,
        depth,
    ):
        """Helper function allowing the 'flattening' out of the table
        recursion: instead of handling the tables in the wrong order
        (recursively), this function adds to new_row that is then
        iterated through in the main function at the end, creating
        a longer table (still in pieces) in the correct order."""

        assert isinstance(data, dict)
        assert isinstance(titles, list)
        assert isinstance(source, str)
        for x in titles:
            assert isinstance(x, str)
        assert isinstance(after, str)
        assert isinstance(depth, int)
        # print("HANDLE_WIKITEXT_TABLE", titles)

        col_gap_data = []  # Filling for columns with rowspan > 1
        # col_gap_data contains None or InflCell
        vertical_still_left = []  # Number of remaining rows for which to fill
        # the column; vertical_still_left contains int
        cols_headered = []  # [F, T, F, F...]
        # True when the whole column contains headers, even
        # when the cell is not considered a header; triggered
        # by the "*" inflmap meta-tag.
        rows = []

        sub_ret = []

        for node in tree.children:
            if not isinstance(node, WikiNode):
                continue
            if node.kind == NodeKind.HTML:
                kind = node.sarg
            else:
                kind = node.kind

            # print("  {}".format(node))
            if kind in (NodeKind.TABLE_CAPTION, "caption"):
                # print("  CAPTION:", node)
                pass
            elif kind in (NodeKind.TABLE_ROW, "tr"):
                if "vsShow" in node.attrs.get("class", "").split():
                    # vsShow rows are those that are intially shown in tables that
                    # have more data.  The hidden data duplicates these rows, so
                    # we skip it and just process the hidden data.
                    continue

                # Parse a table row.
                row = []
                style = None
                row_has_nonempty_cells = False
                # Have nonempty cell not from rowspan
                for col in node.children:
                    # loop through each cell in the ROW
                    if not isinstance(col, WikiNode):
                        # This skip is not used for counting,
                        # "None" is not used in
                        # indexing or counting or looping.
                        continue
                    if col.kind == NodeKind.HTML:
                        kind = col.sarg
                    else:
                        kind = col.kind
                    if kind not in (
                        NodeKind.TABLE_HEADER_CELL,
                        NodeKind.TABLE_CELL,
                        "th",
                        "td",
                    ):
                        print("    UNEXPECTED ROW CONTENT: {}".format(col))
                        continue

                    while (
                        len(row) < len(vertical_still_left)
                        and vertical_still_left[len(row)] > 0
                    ):
                        # vertical_still_left is [...0, 0, 2...] for each column.
                        # It is populated at the end of the loop, at the same time
                        # as col_gap_data.
                        # This needs to be looped and filled this way because each
                        # `for col`-looping jumps straight to the next meaningful
                        # cell; there is no "None" cells, only emptiness between,
                        # and rowspan and colspan are just to generate the "fill-
                        vertical_still_left[len(row)] -= 1
                        row.append(col_gap_data[len(row)])

                        # appending row is how "indexing" is
                        # done here; something is appended,
                        # like a filler-cell here or a "start"
                        # cell at the end of the row-loop,
                        # which increased len(row) which is
                        # then used as the target-index to check
                        # for gaps. vertical_still_left is
                        # the countdown to when to stop
                        # filling in gaps, and goes down to 0,
                        # and col_gap_data is not touched
                        # except when a new rowspan is needed,
                        # at the same time that
                        # vertical_still_left gets reassigned.

                    try:
                        rowspan = int(col.attrs.get("rowspan", "1"))  # 🡙
                        colspan = int(col.attrs.get("colspan", "1"))  # 🡘
                    except ValueError:
                        rowspan = 1
                        colspan = 1
                    # print("COL:", col)

                    # Process any nested tables recursively.
                    tables, rest = recursively_extract(
                        col,
                        lambda x: isinstance(x, WikiNode)
                        and (x.kind == NodeKind.TABLE or x.sarg == "table"),
                    )

                    # Clean the rest of the cell.
                    celltext = clean_node(wxr, None, rest)
                    # print("CLEANED:", celltext)

                    # Handle nested tables.
                    for tbl in tables:
                        # Some nested tables (e.g., croí/Irish) have subtitles
                        # as normal paragraphs in the same cell under a descrip-
                        # tive text that should be treated as a title (e.g.,
                        # "Forms with the definite article", with "definite" not
                        # mentioned elsewhere).
                        new_titles = list(titles)
                        if celltext:
                            new_titles.append(celltext)
                        subtbl = handle_table1(
                            wxr,
                            tablecontext,
                            word,
                            lang,
                            pos,
                            data,
                            tbl,
                            new_titles,
                            source,
                            "",
                            depth + 1,
                        )
                        if subtbl:
                            sub_ret.append((rows, titles, after, depth))
                            rows = []
                            titles = []
                            after = ""
                            sub_ret.extend(subtbl)

                    # This magic value is used as part of header detection
                    cellstyle = (
                        col.attrs.get("style", "")
                        + "//"
                        + col.attrs.get("class", "")
                        + "//"
                        + str(kind)
                    )

                    if not row:  # if first column in row
                        style = cellstyle
                    target = None
                    titletext = celltext.strip()
                    while titletext and is_superscript(titletext[-1]):
                        titletext = titletext[:-1]

                    (
                        is_title,
                        hdr_expansion,
                        target,
                        celltext,
                    ) = determine_header(
                        wxr,
                        tablecontext,
                        lang,
                        word,
                        pos,
                        tree.kind,
                        kind,
                        style,
                        row,
                        col,
                        celltext,
                        titletext,
                        cols_headered,
                        None,
                        cellstyle,
                    )

                    if is_title:
                        # If this cell gets a "*" tag, make the whole column
                        # below it (toggling it in cols_headered = [F, F, T...])
                        # into headers.
                        while len(cols_headered) <= len(row):
                            cols_headered.append(False)
                        if any("*" in tt for tt in hdr_expansion):
                            cols_headered[len(row)] = True
                            celltext = ""
                    # if row_has_nonempty_cells has been True at some point, it
                    # keeps on being True.
                    # if row_has_nonempty_cells or is_title or celltext != "":
                    #   row_has_nonempty_cells = True
                    #   ⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓⇓
                    row_has_nonempty_cells |= is_title or celltext != ""
                    cell = InflCell(
                        celltext, is_title, colspan, rowspan, target
                    )
                    for _ in range(0, colspan):
                        # colspan🡘 current loop (col) or 1
                        # All the data-filling for colspan
                        # is done simply in this loop,
                        # while rowspan needs to use
                        # vertical_still_left to count gaps
                        # and col_gap_data to fill in
                        # those gaps with InflCell data.
                        if rowspan > 1:  # rowspan🡙 current loop (col) or 1
                            while len(col_gap_data) <= len(row):
                                # Initialize col_gap_data/ed if
                                # it is lacking slots
                                # for each column; col_gap_data and
                                # vertical_still_left are never
                                # reset to [], during
                                # the whole table function.
                                col_gap_data.append(None)
                                vertical_still_left.append(0)
                            # Below is where the "rectangle" block of rowspan
                            # and colspan is filled for the future.
                            col_gap_data[len(row)] = cell
                            # col_gap_data contains cells that
                            # will be used in the
                            # future, or None
                            vertical_still_left[len(row)] = rowspan - 1
                            # A counter for how many gaps🡙 are still left to be
                            # filled (row.append or
                            # row[col_gap_data[len(row)] =>
                            # rows), it is not reset to [], but decremented to 0
                            # each time a row gets something from col_gap_data.
                        # Append this cell 1+ times for colspan🡘
                        row.append(cell)
                if not row:
                    continue
                # After looping the original row-nodes above, fill
                # in the rest of the row if the final cell has colspan
                # (inherited from above, so a cell with rowspan and colspan)
                for i in range(len(row), len(vertical_still_left)):
                    if vertical_still_left[i] <= 0:
                        continue
                    vertical_still_left[i] -= 1
                    while len(row) < i:
                        row.append(InflCell("", False, 1, 1, None))
                    row.append(col_gap_data[i])
                # print("  ROW {!r}".format(row))
                if row_has_nonempty_cells:
                    rows.append(row)
            elif kind in (
                NodeKind.TABLE_HEADER_CELL,
                NodeKind.TABLE_CELL,
                "th",
                "td",
                "span",
            ):
                # print("  TOP-LEVEL CELL", node)
                pass

        if sub_ret:
            main_ret = sub_ret
            main_ret.append((rows, titles, after, depth))
        else:
            main_ret = [(rows, titles, after, depth)]
        return main_ret

    new_rows = handle_table1(
        wxr, tablecontext, word, lang, pos, data, tree, titles, source, after, 0
    )

    # Now we have a table that has been parsed into rows and columns of
    # InflCell objects.  Parse the inflection table from that format.
    if new_rows:
        for rows, titles, after, depth in new_rows:
            handle_generic_table(
                wxr,
                tablecontext,
                data,
                word,
                lang,
                pos,
                rows,
                titles,
                source,
                after,
                depth,
            )


def handle_html_table(
    wxr, word, lang, pos, data, tree, titles, source, after, tablecontext=None
):
    """A passer-on function for html-tables, XXX, remove these?"""
    handle_wikitext_or_html_table(
        wxr, word, lang, pos, data, tree, titles, source, after, tablecontext
    )


def handle_wikitext_table(
    wxr, word, lang, pos, data, tree, titles, source, after, tablecontext=None
):
    """A passer-on function for html-tables, XXX, remove these?"""
    handle_wikitext_or_html_table(
        wxr, word, lang, pos, data, tree, titles, source, after, tablecontext
    )


def parse_inflection_section(
    wxr, data, word, lang, pos, section, tree, tablecontext=None
):
    """Parses an inflection section on a page.  ``data`` should be the
    data for a part-of-speech, and inflections will be added to it."""

    # print("PARSE_INFLECTION_SECTION {}/{}/{}/{}"
    #       .format(word, lang, pos, section))
    assert isinstance(wxr, WiktextractContext)
    assert isinstance(data, dict)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(section, str)
    assert isinstance(tree, WikiNode)
    assert tablecontext is None or isinstance(tablecontext, TableContext)
    source = section
    tables = []
    titleparts = []

    def process_tables():
        for kind, node, titles, after in tables:
            after = "".join(after).strip()
            after = clean_value(wxr, after)
            if kind == "wikitext":
                handle_wikitext_table(
                    wxr,
                    word,
                    lang,
                    pos,
                    data,
                    node,
                    titles,
                    source,
                    after,
                    tablecontext=tablecontext,
                )
            elif kind == "html":
                handle_html_table(
                    wxr,
                    word,
                    lang,
                    pos,
                    data,
                    node,
                    titles,
                    source,
                    after,
                    tablecontext=tablecontext,
                )
            else:
                raise RuntimeError(
                    "{}: unimplemented table kind {}".format(word, kind)
                )

    def recurse_navframe(node, titles):
        nonlocal tables
        nonlocal titleparts
        titleparts = []
        old_tables = tables
        tables = []

        recurse(node, [], navframe=True)

        process_tables()
        tables = old_tables

    def recurse(node, titles, navframe=False):
        nonlocal tables
        if isinstance(node, (list, tuple)):
            for x in node:
                recurse(x, titles, navframe)
            return
        if isinstance(node, str):
            if tables:
                tables[-1][-1].append(node)
            elif navframe:
                titleparts.append(node)
            return
        if not isinstance(node, WikiNode):
            if navframe:
                wxr.wtp.debug(
                    "inflection table: unhandled in NavFrame: {}".format(node),
                    sortid="inflection/2907",
                )
            return
        kind = node.kind
        if navframe:
            if kind == NodeKind.HTML:
                classes = node.attrs.get("class", "").split()
                if "NavToggle" in classes:
                    return
                if "NavHead" in classes:
                    # print("NAVHEAD:", node)
                    recurse(node.children, titles, navframe)
                    return
                if "NavContent" in classes:
                    # print("NAVCONTENT:", node)
                    title = "".join(titleparts).strip()
                    title = html.unescape(title)
                    title = title.strip()
                    new_titles = list(titles)
                    if not re.match(r"(Note:|Notes:)", title):
                        new_titles.append(title)
                    recurse(node, new_titles, navframe=False)
                    return
        else:
            if kind == NodeKind.TABLE:
                tables.append(["wikitext", node, titles, []])
                return
            elif kind == NodeKind.HTML and node.sarg == "table":
                classes = node.attrs.get("class", ())
                if "audiotable" in classes:
                    return
                tables.append(["html", node, titles, []])
                return
            elif kind in (
                NodeKind.LEVEL2,
                NodeKind.LEVEL3,
                NodeKind.LEVEL4,
                NodeKind.LEVEL5,
                NodeKind.LEVEL6,
            ):
                return  # Skip subsections
            if (
                kind == NodeKind.HTML
                and node.sarg == "div"
                and "NavFrame" in node.attrs.get("class", "").split()
            ):
                recurse_navframe(node, titles)
                return
        if kind == NodeKind.LINK:
            if len(node.largs) > 1:
                recurse(node.largs[1:], titles, navframe)
            else:
                recurse(node.largs[0], titles, navframe)
            return
        for x in node.children:
            recurse(x, titles, navframe)

    assert tree.kind == NodeKind.ROOT
    for x in tree.children:
        recurse(x, [])

    # Process the tables we found
    process_tables()

    # XXX this code is used for extracting tables for inflection tests
    if wxr.config.expand_tables:
        if section != "Mutation":
            with open(wxr.config.expand_tables, "w") as f:
                f.write(word + "\n")
                f.write(lang + "\n")
                f.write(pos + "\n")
                f.write(section + "\n")
                text = wxr.wtp.node_to_wikitext(tree)
                f.write(text + "\n")

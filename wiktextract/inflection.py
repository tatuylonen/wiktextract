# Code for parsing inflection tables.
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org.

import re
import copy
import enum
import html
import unicodedata
from wikitextprocessor import Wtp, WikiNode, NodeKind, ALL_LANGUAGES
from wiktextract.config import WiktionaryConfig
from wiktextract.tags import valid_tags
from wiktextract.inflectiondata import infl_map, infl_start_map, infl_start_re
from wiktextract.datautils import data_extend

# Column texts that are interpreted as an empty column.
IGNORED_COLVALUES = set([
    "-", "־", "᠆", "‐", "‑", "‒", "–", "—", "―", "−",
    "⸺", "⸻", "﹘", "﹣", "－", "/"])

# Words in title that cause addition of tags in all entries
title_contains_global_map = {
    "possessive": "possessive",
    "positive": "positive",
    "negative": "negative",
    "future": "future",
    "pf": "perfective",
    "impf": "imperfective",
    "comparative": "comparative",
    "superlative": "superlative",
    "combined forms": "combined-form",
    "mutation": "mutation",
    "definite article": "definite",
    "indefinite article": "indefinite",
}
for k, v in title_contains_global_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_CONTAINS_GLOBAL_MAP UNRECOGNIZED TAG: {}: {}"
              .format(k, v))
title_contains_global_re = re.compile(
    r"(?i)(^|\b)({})($|\b)"
    .format("|".join(re.escape(x)
                     for x in title_contains_global_map.keys())))

# Words in title that cause addition of tags to word-tags "form"
title_contains_wordtags_map = {
    "strong": "strong",
    "weak": "weak",
    "countable": "countable",
    "uncountable": "uncountable",
    "transitive": "transitive",
    "intransitive": "intransitive",
    "ditransitive": "ditransitive",
    "ambitransitive": "ambitransitive",
    "proper noun": "proper-noun",
    "no plural": "no-plural",
    "imperfective": "imperfective",
    "perfective": "perfective",
}
for k, v in title_contains_wordtags_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_CONTAINS_WORDTAGS_MAP UNRECOGNIZED TAG: {}: {}"
              .format(k, v))
title_contains_wordtags_re = re.compile(
    r"(?i)(^|\b)({})($|\b)"
    .format("|".join(re.escape(x)
                     for x in title_contains_wordtags_map.keys())))

# Parenthesized elements in title that are converted to tags in "word-tags" form
title_elements_map = {
    "weak": "weak",
    "strong": "strong",
    "masculine": "masculine",
    "feminine": "feminine",
    "neuter": "neuter",
    "singular": "singular",
    "plural": "plural",
    "no gradation": "no-gradation",
    "t-d gradation": "gradation-t-d",
    "tt-t gradation": "gradation-tt-t",
    "kk-k gradation": "gradation-kk-k",
    "nt-nn gradation": "gradation-nt-nn",
    "pp-p gradation": "gradation-pp-p",
    "k- gradation": "gradation-k-",
    "p-v gradation": "gradation-p-v",
    "mp-mm gradation": "gradation-mp-mm",
    "nk-ng gradation": "gradation-nk-ng",
    "lt-ll gradation": "gradation-lt-ll",
    "rt-rr gradation": "gradation-rt-rr",
    "ik-j gradation": "gradation-ik-j",
    "k-v gradation": "gradation-k-v",
    "1st declension": "declension-1",
    "2nd declension": "declension-2",
    "3rd declension": "declension-3",
    "4th declension": "declension-4",
    "5th declension": "declension-5",
    "first declension": "declension-1",
    "second declension": "declension-2",
    "third declension": "declension-3",
    "fourth declension": "declension-4",
    "fifth declension": "declension-5",
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
}
for k, v in title_elements_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_ELEMENTS_MAP UNRECOGNIZED TAG: {}: {}"
              .format(k, v))

# Parenthized element starts to map them to tags for form for the rest of
# the element
title_elemstart_map = {
    "auxiliary": "auxiliary",
    "Kotus type": "class",
    "class": "class",
    "type": "class",
    "accent paradigm": "accent-paradigm",
}
for k, v in title_elemstart_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_ELEMSTART_MAP UNRECOGNIZED TAG: {}: {}"
              .format(k, v))
title_elemstart_re = re.compile(
    r"^({}) "
    .format("|".join(re.escape(x) for x in title_elemstart_map.keys())))


class InflCell(object):
    """Cell in an inflection table."""
    __slots__ = (
        "text",
        "is_title",
        "start",
        "colspan",
        "rowspan",
    )
    def __init__(self, text, is_title, start, colspan, rowspan):
        assert isinstance(text, str)
        assert is_title in (True, False)
        assert isinstance(start, int)
        assert isinstance(colspan, int) and colspan >= 1
        assert isinstance(rowspan, int) and rowspan >= 1
        self.text = text.strip()
        self.is_title = text and is_title
        self.colspan = colspan
        self.rowspan = rowspan
    def __str__(self):
        return "{}/{}/{}/{}".format(
            self.text, self.is_title, self.colspan, self.rowspan)
    def __repr__(self):
        return str(self)


class HdrSpan(object):
    """Saved information about a header cell/span during the parsing
    of a table."""
    __slots__ = (
        "start",
        "colspan",
        "tagsets",  # list of sets
        "used",  # At least one text cell after this
        "text",  # For debugging
    )
    def __init__(self, start, colspan, tagsets, text):
        assert isinstance(start, int) and start >= 0
        assert isinstance(colspan, int) and colspan >= 1
        assert isinstance(tagsets, set)
        for x in tagsets:
            assert isinstance(x, tuple)
        self.start = start
        self.colspan = colspan
        self.tagsets = list(set(tags) for tags in tagsets)
        self.used = False
        self.text = text


def is_superscript(ch):
    """Returns True if the argument is a superscript character."""
    assert isinstance(ch, str) and len(ch) == 1
    return unicodedata.name(ch).startswith("SUPERSCRIPT ")


def clean_header(word, col):
    """Cleans a row/column header for later processing."""
    orig_col = col
    col = re.sub(r"\s*\^\([^)]*\)", "", col)
    col = re.sub(r"(?s)\s*➤\s*$", "", col)
    col = re.sub(r"(?s)\s*,\s*$", "", col)
    col = re.sub(r"(?s)\s*•\s*$", "", col)
    if col not in infl_map:
        col = re.sub(r",?\s*\([^)]*\)\s*$", "", col)
    col = col.strip()
    if re.search(r"^(There are |"
                 r"\*|"
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
                 r"Notes:)",
                col):
        return "", [], []
    refs = []
    ref_symbols = "*△†0123456789"
    if len(col) > 2 and col[-2] == "^" and col[-1] in ref_symbols:
        col = col[:-2]
        refs.append("*")
    while col and is_superscript(col[0]):
        if len(col) > 1 and col[1] in ("⁾", " ", ":"):
            # Note definition
            return "", [], [[col[0], col[2:].strip()]]
        refs.append(col[0])
        col = col[1:]
    while col and (is_superscript(col[-1]) or col[-1] in ("†",)):
        # Numbers and H/L/N are useful information
        refs.append(col[-1])
        col = col[:-1]
    if len(col) > 2 and col[1] in (")", " ", ":") and col[0].isdigit():
        # Another form of note definition
        return "", [], [[col[0], col[2:].strip()]]
    col = col.strip()
    if col.endswith("*"):
        col = col[:-1].strip()
        refs.append("*")
    if col.endswith("(*)"):
        col = col[:-3].strip()
        refs.append("*")
    #print("CLEAN_HEADER: orig_col={!r} col={!r} refs={!r}"
    #      .format(orig_col, col, refs))
    return col.strip(), refs, []


def parse_title(title, source):
    """Parses inflection table title.  This returns (global_tags, word_tags,
    extra_forms), where ``global_tags`` is tags to be added to each inflection
    entry, ``word_tags`` are tags for the word but not to be added to every
    form, and ``extra_forms`` is dictionary describing additional forms to be
    included in the part-of-speech entry)."""
    assert isinstance(title, str)
    assert isinstance(source, str)
    title = html.unescape(title)
    title = re.sub(r"(?i)<[^>]*>", "", title).strip()
    title = re.sub(r"\s+", " ", title)
    # print("PARSING TITLE:", title)
    global_tags = []
    word_tags = []
    extra_forms = []
    # Check for the case that the title is in infl_map
    if title in infl_map:
        return infl_map[title].split(), [], []
    if title.lower() in infl_map:
        return infl_map[title.lower()].split(), [], []
    # Add certain global tags based on contained words
    for m in re.finditer(title_contains_global_re, title):
        global_tags.extend(title_contains_global_map[
            m.group(0).lower()].split())
    # Add certain tags to word-tags "form" based on contained words
    for m in re.finditer(title_contains_wordtags_re, title):
        word_tags.extend(title_contains_wordtags_map[
            m.group(0).lower()].split())
    # Parse parenthesized part from title
    for m in re.finditer(r"\(([^)]*)\)", title):
        for elem in m.group(1).split(","):
            elem = elem.strip()
            if elem in title_elements_map:
                word_tags.extend(title_elements_map[elem].split())
            else:
                m = re.match(title_elemstart_re, elem)
                if m:
                    tags = title_elemstart_map[m.group(1)].split()
                    dt = {"form": elem[m.end():],
                          "source": source + " title",
                          "tags": tags}
                    extra_forms.append(dt)
    # For titles that contains no parenthesized parts, do some special
    # handling to still interpret parts from them
    if title.find("(") < 0:
        # No parenthesized parts
        m = re.search(r"\b(Portuguese) (-.* verb) ", title)
        if m is not None:
            dt = {"form": m.group(2),
                  "tags": ["class"],
                  "source": source + " title"}
            extra_forms.append(dt)
        for elem in title.split(","):
            elem = elem.strip()
            if elem in title_elements_map:
                word_tags.extend(title_elements_map[elem].split())
            elif elem.endswith("-stem"):
                dt = {"form": elem,
                      "tags": ["class"],
                      "source": source + " title"}
                extra_forms.append(dt)
    return global_tags, word_tags, extra_forms


def expand_header(word, lang, text, tags0):
    """Expands a cell header to tags, handling conditional expressions
    in infl_map.  This returns list of tuples of tags, each list element
    describing an alternative interpretation.  ``tags0`` is combined
    column and row tags for the cell in which the text is being interpreted
    (conditional expressions in inflection data may depend on it)."""
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(text, str)
    assert isinstance(tags0, (list, tuple, set))
    # print("EXPAND_HDR:", text)
    # First map the text using the inflection map
    if text in infl_map:
        v = infl_map[text]
    else:
        m = re.match(infl_start_re, text)
        assert m is not None
        v = infl_start_map[m.group(1)]
        # print("INFL_START {} -> {}".format(text, v))

    # Then loop interpreting the value, until the value is a simple string.
    # This may evaluate nested conditional expressions.
    while True:
        # If it is a string, we are done.
        if isinstance(v, str):
            return [tuple(sorted(v.split()))]
        # For a list, just interpret it as alternatives.  (Currently the
        # alternatives must directly be strings.)
        if isinstance(v, (list, tuple)):
            lst = []
            return list(tuple(sorted(x.split())) for x in v)
        # Otherwise the value should be a dictionary describing a conditional
        # expression.
        if not isinstance(v, dict):
            print("UNIMPLEMENTED INFL_MAP VALUE: {}/{}/{}: {}"
                  .format(word, lang, text, infl_map[text]))
            return [()]
        # Evaluate the conditional expression.
        assert isinstance(v, dict)
        cond = "default-true"
        # Handle "lang" condition.  The value must be either a single language
        # or a list of languages, and the condition evaluates to True if
        # the table is in one of those languages.
        if cond and "lang" in v:
            c = v["lang"]
            if isinstance(c, str):
                cond = c == lang
            else:
                assert isinstance(c, (list, tuple, set))
                cond = lang in c
        # Handle "if" condition.  The value must be a string containing
        # a space-separated list of tags.  The condition evaluates to True
        # if ``tags0`` contains at least one of the listed tags.
        if cond and "if" in v:
            c = v["if"]
            assert isinstance(c, str)
            # "if" condition is true if any of the listed tags is present
            cond = any(t in tags0 for t in c.split())
        # Warning message about missing conditions for debugging.
        if cond == "default-true":
            print("IF MISSING COND: word={} lang={} text={} tags0={} "
                  "c={} cond={}"
                  .format(word, lang, text, tags0, c, cond))
        # Based on the result of evaluating the condition, select either
        # "then" part or "else" part.
        if cond:
            v = v.get("then", "")
        else:
            v = v.get("else")
            if v is None:
                print("IF WITHOUT ELSE EVALS False: {}/{} {!r} tags0={}"
                      .format(word, lang, text, tags0))
                v = ""


def compute_coltags(hdrspans, start, colspan, mark_used):
    """Computes column tags for a column of the given width based on the
    current header spans."""
    assert isinstance(hdrspans, list)
    assert isinstance(start, int) and start >= 0
    assert isinstance(colspan, int) and colspan >= 1
    assert mark_used in (True, False)
    used = set()
    coltags = None
    # XXX should look at tag classes and not take tags in the same class(es)
    # from higher up
    done = False
    for hdrspan in reversed(hdrspans):
        if done:
            break
        if (hdrspan.start > start or
            hdrspan.start + hdrspan.colspan < start + colspan):
            continue
        # XXX this breaks persons in soutenir/French/Verb
        # if any(hdrspan.start > x[0] or
        #        hdrspan.start + hdrspan.colspan < x[0] + x[1]
        #        for x in used):
        #     continue
        key = (hdrspan.start, hdrspan.colspan)
        if key in used:
            continue
        # XXX if hdrspan.used:
        used.add(key)
        if mark_used:
            hdrspan.used = True
        # Merge into coltags
        if coltags is None:
            coltags = list(tuple(sorted(tt)) for tt in hdrspan.tagsets)
        else:
            new_coltags = set()
            for tags2 in hdrspan.tagsets:  # Earlier header
                for tags1 in coltags:      # Tags found for current cell so far
                    if (any(valid_tags[t] in ("mood", "tense", "person",
                                              "number")
                            for t in tags1) and
                        any(valid_tags[t] in ("non-finite",)
                            for t in tags2)):
                        tags2 = set()
                    elif (any(valid_tags[t] == "number" for t in tags1) and
                          any(valid_tags[t] == "number" for t in tags2)):
                        tags2 = set()
                    tags = tuple(sorted(set(tags1) | tags2))
                    new_coltags.add(tags)
            coltags = list(new_coltags)
    if coltags is None:
        coltags = [()]
    #print("HDRSPANS:", list((x.start, x.colspan, x.tagsets) for x in hdrspans))
    # print("COMPUTE_COLTAGS {} {} {}: {}"
    #       .format(start, colspan, mark_used, coltags))
    return coltags


def parse_simple_table(ctx, word, lang, rows, titles, source):
    """This is the default table parser.  Despite its name, it can parse
    complex tables.  This returns a list of forms to be added to the
    part-of-speech, or None if the table could not be parsed."""
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(rows, list)
    assert isinstance(source, str)
    for row in rows:
        for col in row:
            assert isinstance(col, InflCell)
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)
    # print("ROWS:")
    # for row in rows:
    #     print("  ", row)
    ret = []
    hdrspans = []
    col_has_text = []
    i = 0
    title = None
    global_tags = []
    word_tags = []
    for title in titles:
        more_global_tags, more_word_tags, extra_forms = \
            parse_title(title, source)
        global_tags.extend(more_global_tags)
        word_tags.extend(more_word_tags)
        ret.extend(extra_forms)
    for row in rows:
        # print("ROW:", row)
        if not row:
            continue  # Skip empty rows without incrementing i
        if (row[0].is_title and
            row[0].text and
            not is_superscript(row[0].text[0]) and
            row[0].text not in infl_map and
            not re.match(infl_start_re, row[0].text) and
            all(x.is_title == row[0].is_title and
                x.text == row[0].text
                for x in row)):
            if row[0].text and title is None:
                title = row[0].text
                if re.match(r"(Note:|Notes:)", title):
                    continue
                more_global_tags, more_word_tags, extra_forms = \
                    parse_title(title, source)
                global_tags.extend(more_global_tags)
                word_tags.extend(more_word_tags)
                ret.extend(extra_forms)
            continue  # Skip title rows without incrementing i
        rowtags = [()]
        have_hdr = False
        have_text = False
        samecell_cnt = 0
        col0_hdrspan = None
        col0_followed_by_nonempty = False
        for j, cell in enumerate(row):
            colspan = cell.colspan
            if samecell_cnt == 0:
                # First column of a (possible multi-column) cell
                samecell_cnt = colspan - 1
            else:
                assert samecell_cnt > 0
                cell_initial = False
                samecell_cnt -= 1
                continue
            # print("  COL:", col)
            col = cell.text
            if not col:
                continue
            # print(i, j, col)
            if cell.is_title:
                # It is a header cell
                col = re.sub(r"\s+", " ", col)
                text, refs, defs = clean_header(word, col)
                if not text:
                    continue
                if text not in infl_map:
                    text1 = re.sub(r"\s*\([^)]*\)", "", text)
                    if text1 in infl_map:
                        text = text1
                    else:
                        text1 = re.sub(r"\s*,+\s+", " ", text)
                        text1 = re.sub(r"\s+", " ", text1)
                        if text1 in infl_map:
                            text = text1
                        elif not re.match(infl_start_re, text):
                            if text not in IGNORED_COLVALUES:
                                print("  UNHANDLED HEADER: {!r}".format(col))
                                return None
                            continue
                if infl_map.get(text, "") == "!":
                    # Reset column headers
                    hdrspans = []
                    continue
                if have_text:
                    #print("  HAVE_TEXT BEFORE HDR:", col)
                    # Reset rowtags if new title column after previous
                    # text cells
                    # XXX beware of header "—": "" - must not clear on that if
                    # it expands to no tags
                    rowtags = [()]
                have_hdr = True
                # print("HAVE_HDR:", col)
                # Update rowtags and coltags
                new_rowtags = set()
                new_coltags = set()
                all_hdr_tags = set()
                for rt0 in rowtags:
                    for ct0 in compute_coltags(hdrspans, j, colspan, False):
                        tags0 = set(rt0) | set(ct0) | set(global_tags)
                        alt_tags = expand_header(word, lang, text, tags0)
                        all_hdr_tags.update(alt_tags)
                        for tt in alt_tags:
                            new_coltags.add(tt)
                            # XXX which ones need to be removed?
                            tags = tuple(sorted(set(tt) | set(rt0)))
                            new_rowtags.add(tags)
                rowtags = list(new_rowtags)
                if any(new_coltags):
                    hdrspan = HdrSpan(j, colspan, new_coltags, col)
                    hdrspans.append(hdrspan)
                    # Handle headers that are above left-side header
                    # columns and are followed by personal pronouns in
                    # remaining columns (basically headers that
                    # evaluate to no tags).  In such cases widen the
                    # left-side header to the full row.
                    if j == 0:
                        assert col0_hdrspan is None
                        col0_hdrspan = hdrspan
                    elif any(all_hdr_tags):
                        # if col0_hdrspan is not None:
                        #     print("COL0 FOLLOWED HDR: {!r} by {!r} TAGS {}"
                        #           .format(col0_hdrspan.text, col,
                        #                   all_hdr_tags))
                        col0_followed_by_nonempty = True
                continue

            # It is a normal text cell
            if col in IGNORED_COLVALUES:
                continue

            if j == 0 and (not col_has_text or not col_has_text[0]):
                continue  # Skip text at top left, as in Icelandic, Faroese
            # if col0_hdrspan is not None:
            #     print("COL0 FOLLOWED NONHDR: {!r} by {!r}"
            #           .format(col0_hdrspan.text, col))
            col0_followed_by_nonempty = True
            have_text = True
            while len(col_has_text) <= j:
                col_has_text.append(False)
            col_has_text[j] = True
            # Determine column tags for the multi-column cell
            combined_coltags = compute_coltags(hdrspans, j, colspan, True)

            # print("HAVE_TEXT:", repr(col))
            col = re.sub(r"[ \t\r]+", " ", col)
            text, refs, defs = clean_header(word, col)
            if text.find(" + ") >= 0:
                extra_split = ""
            else:
                extra_split = "," if text.endswith("/") else ",/"
            for form in re.split(r"[;•\n{}]| or ".format(extra_split), text):
                form = form.strip()
                extra_tags = []
                ipas = []
                if form.find("/") >= 0:
                    for m in re.finditer(r"/[^/]*/", form):
                        ipas.append(m.group(0))
                    form = re.sub(r"/[^/]*/", "", form)
                form = re.sub(r"^\s*,\s*", "", form)
                form = re.sub(r"\s*,\s*$", "", form)
                form = re.sub(r"\s*(,\s*)+", ", ", form)
                form = re.sub(r"(?i)^Main:", "", form)
                form = re.sub(r"\s+", " ", form)
                form = form.strip()
                if form.endswith("ʳᵃʳᵉ"):
                    extra_tags.append("rare")
                    form = form[:-4].strip()
                while form and is_superscript(form[-1]):
                    # XXX handle refences in form
                    form = form[:-1]
                if form.startswith("*"):
                    form = form[1:]
                roman = None
                m = re.search(r"\s*\(([^)]*)\)", form)
                if m is not None:
                    # XXX besides roman, it can be tags, e.g., (archaic)
                    roman = m.group(1)
                    form = (form[:m.start()] + " " + form[m.end():]).strip()
                # Ignore certain forms that are not really forms
                if form in ("", "not used", "not applicable"):
                    continue
                # print("ROWTAGS:", rowtags)
                # print("COLTAGS:", combined_coltags)
                # print("TEXT:", repr(form))
                for rt in rowtags:
                    for ct in combined_coltags:
                        tags = set(global_tags)
                        tags.update(extra_tags)
                        tags.update(rt)
                        old_tags = set(tags)
                        for t in ct:
                            c = valid_tags[t]
                            if (c in ("mood",) and
                                any(valid_tags[tt] == c
                                    for tt in old_tags)):
                                continue
                            tags.add(t)
                        # Remove "personal" tag if have nth person; these
                        # come up with e.g. reconhecer/Portuguese/Verb.
                        if ("personal" in tags and
                            any(x in tags for x in
                               ["first-person", "second-person",
                                "third-person"])):
                            tags.remove("personal")
                        tags = list(sorted(tags))
                        dt = {"form": form, "tags": tags,
                              "source": source}
                        if roman:
                            dt["roman"] = roman
                        if ipas:
                            dt["ipa"] = ", ".join(ipas)
                        ret.append(dt)
        # End of row
        if col0_hdrspan is not None and not col0_followed_by_nonempty:
            # If a column-0 header is only followed by headers that yield
            # no tags, expand it to entire row
            # print("EXPANDING COL0: {} from {} to {} cols"
            #       .format(col0_hdrspan.text, col0_hdrspan.colspan,
            #               len(row)))
            col0_hdrspan.colspan = len(row)
        i += 1
    # XXX handle refs and defs
    # for x in hdrspans:
    #     print("  HDRSPAN {} {} {} {!r}"
    #           .format(x.start, x.colspan, x.tagsets, x.text))

    # Post-process German nouns with articles
    if any("noun" in x["tags"] for x in ret):
        if lang in ("Alemannic German", "Cimbrian", "German",
                    "German Low German", "Hunsrik", "Luxembourish",
                    "Pennsylvania German"):
            new_ret = []
            for dt in ret:
                tags = dt["tags"]
                if "noun" in tags:
                    tags = list(t for t in tags if t != "noun")
                elif "indefinite" in tags or "definite" in tags:
                    tags = list(sorted(set(tags) | set(["article"])))
                dt = dt.copy()
                dt["tags"] = tags
                new_ret.append(dt)
            ret = new_ret
        else:
            print("UNHANDLED NOUN IN {}/{}".format(word, lang))

    if word_tags:
        word_tags = list(sorted(set(word_tags)))
        dt = {"form": " ".join(word_tags),
              "source": source + " title",
              "tags": ["word-tags"]}
        ret.append(dt)

    return ret


def handle_generic_table(ctx, word, lang, rows, titles, source):
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(rows, list)
    assert isinstance(source, str)
    for row in rows:
        assert isinstance(row, list)
        for x in row:
            assert isinstance(x, InflCell)
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)

    # Try to parse the table as a simple table
    ret = parse_simple_table(ctx, word, lang, rows, titles, source)
    if ret is not None:
        return ret

    # XXX handle other table formats

    # We were not able to handle the table
    print("UNHANDLED TABLE FORMAT in {}/{}".format(word, lang))
    return []


def handle_wikitext_table(config, ctx, word, lang, data, tree, titles, source):
    """Parses a table from parsed Wikitext format into rows and columns of
    InflCell objects and then calls handle_generic_table() to parse it into
    forms.  This adds the forms into ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(data, dict)
    assert isinstance(tree, WikiNode)
    assert tree.kind == NodeKind.TABLE
    assert isinstance(titles, list)
    assert isinstance(source, str)
    for x in titles:
        assert isinstance(x, str)
    # Imported here to avoid a circular import
    from wiktextract.page import clean_node, recursively_extract
    # print("HANDLE_WIKITEXT_TABLE", titles)

    cols_fill = []    # Filling for columns with rowspan > 1
    cols_filled = []  # Number of remaining rows for which to fill the column
    cols_headered = []  # True when column contains headers even if normal fmt
    rows = []
    assert tree.kind == NodeKind.TABLE
    for node in tree.children:
        if not isinstance(node, WikiNode):
            continue
        kind = node.kind
        # print("  {}".format(node))
        if kind == NodeKind.TABLE_CAPTION:
            # print("  CAPTION:", node)
            pass
        elif kind == NodeKind.TABLE_ROW:
            if "vsShow" in node.attrs.get("class", "").split():
                # vsShow rows are those that are intially shown in tables that
                # have more data.  The hidden data duplicates these rows, so
                # we skip it and just process the hidden data.
                continue

            # Parse a table row.
            row = []
            style = None
            for col in node.children:
                if not isinstance(col, WikiNode):
                    continue
                kind = col.kind
                if kind not in (NodeKind.TABLE_HEADER_CELL,
                                NodeKind.TABLE_CELL):
                    print("    UNEXPECTED ROW CONTENT: {}".format(col))
                    continue
                while len(row) < len(cols_filled) and cols_filled[len(row)] > 0:
                    cols_filled[len(row)] -= 1
                    row.append(cols_fill[len(row)])
                try:
                    rowspan = int(col.attrs.get("rowspan", "1"))
                    colspan = int(col.attrs.get("colspan", "1"))
                except ValueError:
                    rowspan = 1
                    colspan = 1
                # print("COL:", col)

                # Process any nested tables recursively.  XXX this
                # should also take prior text before nested tables as
                # headers, e.g., see anglais/Irish/Declension ("Forms
                # with the definite article" before the table)
                tables, rest = recursively_extract(col, lambda x:
                                                   isinstance(x, WikiNode) and
                                                   x.kind == NodeKind.TABLE)
                for tbl in tables:
                    handle_wikitext_table(config, ctx, word, lang, data,
                                          tbl, titles, source)
                # print("REST:", rest)

                celltext = clean_node(config, ctx, None, rest)
                # print("CLEANED:", celltext)

                # This magic value is used as part of header detection
                cellstyle = (col.attrs.get("style", "") + "//" +
                             col.attrs.get("class", "") + "//" +
                             str(kind))
                if not row:
                    style = cellstyle
                target = None
                idx = celltext.find(": ")
                is_title = False
                if idx >= 0 and celltext[:idx] in infl_map:
                    target = celltext[idx + 2:].strip()
                    # XXX add tags from target
                    celltext = celltext[:idx]
                    is_title = True
                elif (kind == NodeKind.TABLE_HEADER_CELL or
                      (celltext in infl_map and celltext != word) or
                      (style == cellstyle and
                       celltext != word and
                       not style.startswith("////"))):
                    if celltext.find(" + ") < 0:
                        is_title = True
                if (not is_title and len(row) < len(cols_headered) and
                    cols_headered[len(row)]):
                    # Whole column has title suggesting they are headers
                    # (e.g. "Case")
                    is_title = True
                if is_title:
                    while len(cols_headered) <= len(row):
                        cols_headered.append(False)
                    v = infl_map.get(celltext, "")
                    if v == "*":
                        cols_headered[len(row)] = True
                        celltext = ""
                # XXX extra tags, see "target" above
                cell = InflCell(celltext, is_title, len(row), colspan, rowspan)
                for i in range(0, colspan):
                    if rowspan > 1:
                        while len(cols_fill) <= len(row):
                            cols_fill.append(None)
                            cols_filled.append(0)
                        cols_fill[len(row)] = cell
                        cols_filled[len(row)] = rowspan - 1
                    row.append(cell)
            if not row:
                continue
            while len(row) < len(cols_fill) and cols_filled[len(row)] > 0:
                cols_filled[len(row)] -= 1
                row.append(cols_fill[len(row)])
            # print("  ROW {!r}".format(row))
            rows.append(row)
        elif kind in (NodeKind.TABLE_HEADER_CELL, NodeKind.TABLE_CELL):
            # print("  TOP-LEVEL CELL", node)
            pass

    # Now we have a table that has been parsed into rows and columns of
    # InflCell objects.  Parse the inflection table from that format.
    ret = handle_generic_table(ctx, word, lang, rows, titles, source)
    if not ret:
        return
    data_extend(ctx, data, "forms", ret)


def handle_html_table(config, ctx, word, lang, data, tree, titles, source):
    """Parses a table from parsed HTML format into rows and columns of
    InflCell objects and then calls handle_generic_table() to parse it into
    forms.  This adds the forms into ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(data, dict)
    assert isinstance(tree, WikiNode)
    assert tree.kind == NodeKind.HTML and tree.args == "table"
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)
    assert isinstance(source, str)

    print("HTML TABLES NOT YET IMPLEMENTED at {}/{}"
          .format(word, lang))


def parse_inflection_section(config, ctx, data, word, lang, section, tree):
    """Parses an inflection section on a page.  ``data`` should be the
    data for a part-of-speech, and inflections will be added to it."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(word, str)
    assert isinstance(section, str)
    assert isinstance(tree, WikiNode)
    source = section

    # print("PARSE_INFLECTION_SECTION {}/{}/{}".format(word, lang, section))

    def recurse_navframe(node, titles):
        titleparts = []

        def recurse1(node, in_navhead):
            if isinstance(node, (list, tuple)):
                for x in node:
                    recurse1(x, in_navhead)
                return
            if isinstance(node, str):
                titleparts.append(node)
                return
            if not isinstance(node, WikiNode):
                print("UNHANDLED IN NAVFRAME:", repr(node))
                return
            kind = node.kind
            if kind == NodeKind.HTML:
                classes = node.attrs.get("class", "").split()
                if "NavToggle" in classes:
                    return
                if "NavHead" in classes:
                    # print("NAVHEAD:", node)
                    for x in node.children:
                        recurse1(x, True)
                    return
                if "NavContent" in classes:
                    title = "".join(titleparts).strip()
                    title = html.unescape(title)
                    title = title.strip()
                    new_titles = list(titles)
                    if not re.match(r"(Note:|Notes:)", title):
                        new_titles.append(title)
                    recurse(node, new_titles)
                    return
            elif kind == NodeKind.LINK:
                if len(node.args) > 1:
                    for x in node.args[1:]:
                        recurse1(x, in_navhead)
                else:
                    recurse1(node.args[0], in_navhead)
            for x in node.children:
                recurse1(x, in_navhead)
        recurse1(node, False)

    def recurse(node, titles):
        if not isinstance(node, WikiNode):
            return
        kind = node.kind
        if kind == NodeKind.TABLE:
            handle_wikitext_table(config, ctx, word, lang, data, node, titles,
                                  source)
            return
        elif kind == NodeKind.HTML and node.args == "table":
            handle_html_table(config, ctx, word, lang, data, node, titles,
                              source)
            return
        elif kind in (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
                      NodeKind.LEVEL5, NodeKind.LEVEL6):
            return  # Skip subsections
        if (kind == NodeKind.HTML and node.args == "div" and
            "NavFrame" in node.attrs.get("class", "").split()):
            recurse_navframe(node, titles)
        for x in node.children:
            recurse(x, titles)

    assert tree.kind == NodeKind.ROOT
    for x in tree.children:
        recurse(x, [])

# XXX change to use ctx.debug
# XXX check interdecir/Spanish - singular/plural issues
# XXX check anglais/Irish/Declension - should take titles/tags from outer table

# Code for parsing linguistic form descriptions and tags for word senses
# (both the word entry head - initial part and parenthesized parts -
# and tags at the beginning of word senses)
#
# Copyright (c) 2020-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import unicodedata
import Levenshtein
from nltk import TweetTokenizer
from wikitextprocessor import Wtp
from .datautils import data_append, data_extend, split_at_comma_semi
from .taxondata import known_species, known_firsts
from .topics import valid_topics, topic_generalize_map
from .tags import (xlat_head_map, valid_tags,
                   uppercase_tags, xlat_tags_map, xlat_descs_map,
                   head_final_extra_langs, head_final_extra_map)
from .english_words import english_words

# Tokenizer for classify_desc()
tokenizer = TweetTokenizer()

# Regexp for finding nested translations from translation items (these are
# used in, e.g., year/English/Translations/Arabic).  This is actually used
# in page.py.
nested_translations_re = re.compile(
    r"\s+\((({}): ([^()]|\([^()]+\))+)\)"
    .format("|".join(x for x in xlat_head_map.values()
                     if x and not x.startswith("class-"))))

# Regexp that matches head tag specifiers.  Used to match tags from end of
# translations and linkages
head_final_re = re.compile(
    r"( -)?(( ({}))+( or ({}))*)$".format(
        "|".join(re.escape(x) for x in xlat_head_map.keys()),
        "|".join(re.escape(x) for x in xlat_head_map.keys())))

# Regexp used to match head tag specifiers at end of a form for certain
# languages (particularly Swahili and similar languages).
head_final_extra_re = re.compile(
    r" ({})$".format(
        "|".join(re.escape(x) for x in head_final_extra_map.keys())))

# Parenthesized parts that are ignored in translations
ignored_parens = set([
    "please verify",
    "(please verify)",
    "transliteration needed",
    "(transliteration needed)",
    "in words with back vowel harmony",
    "(in words with back vowel harmony)",
    "in words with front vowel harmony",
    "(in words with front vowel harmony)",
])

# Translations that are ignored
ignored_translations = set([
    "[script needed]",
    "please add this translation if you can",
])

# Put english text into the "note" field in a translation if it contains one
# of these words
tr_note_re = re.compile(
    r"\b(article|definite|indefinite|superlative|comparative|pattern|"
    "adjective|adjectives|clause|clauses|pronoun|pronouns|preposition|prep|"
    "postposition|postp|action|actions|"
    "adverb|adverbs|noun|nouns|verb|verbs|before|"
    "after|placed|prefix|suffix|used with|"
    "nominative|genitive|dative|infinitive|participle|past|perfect|imperfect|"
    "perfective|imperfective|auxiliary|negative|future|present|tense|aspect|"
    "conjugation|declension|class|category|plural|singular|positive|"
    "seldom used|formal|informal|familiar|unspoken|spoken|written|"
    "indicative|progressive|conditional|potential|"
    "accusative|adessive|inessive|"
    "dialect|dialects|object|subject|predicate|movies|recommended|language|"
    "locative|continuous|simple|continuousness|gerund|subjunctive|"
    "form|regular|irregular)($|\s)")  # \b does not work at the end???

# Words that can be part of form description
valid_words = set(["or", "and"])
for x in valid_tags:
    valid_words.update(x.split(" "))
for x in xlat_tags_map.keys():
    valid_words.update(x.split(" "))


def add_to_valid_tree(tree, field, tag, v):
    """Helper function for building trees of valid tags/sequences during
    initialization."""
    assert isinstance(tree, dict)
    assert field in ("tags", "topics")
    assert isinstance(tag, str)
    assert v is None or isinstance(v, str)
    node = tree
    for w in tag.split(" "):
        if w in node:
            node = node[w]
        else:
            new_node = {}
            node[w] = new_node
            node = new_node
    if "$" not in node:
        node["$"] = {}
    node = node["$"]
    if field not in node:
        node[field] = ()
    if v is not None and v not in node[field]:
        node[field] += (v,)


def add_to_valid_tree1(tree, field, k, v, valid_values):
    assert isinstance(tree, dict)
    assert isinstance(field, str)
    assert isinstance(k, str)
    assert v is None or isinstance(v, (list, tuple, str))
    assert isinstance(valid_values, set)
    if not v:
        add_to_valid_tree(valid_sequences, field, k, None)
        return
    elif isinstance(v, str):
        v = [v]
    q = []
    for vv in v:
        assert isinstance(vv, str)
        add_to_valid_tree(valid_sequences, field, k, vv)
        vvs = vv.split(" ")
        for x in vvs:
            if not x or x.isspace():
                continue
            q.append(x)
            if x not in valid_values and x[0].islower():
                print("WARNING: {} in mapping {!r} but not in valid_values"
                      .format(x, k))
    return q


def add_to_valid_tree_mapping(tree, field, mapping, valid_values, recurse):
    assert isinstance(tree, dict)
    assert isinstance(field, str)
    assert isinstance(mapping, dict)
    assert isinstance(valid_values, set)
    assert recurse in (True, False)
    for k, v in mapping.items():
        assert isinstance(k, str)
        assert isinstance(v, (list, str))
        if isinstance(v, str):
            v = [v]
        q = add_to_valid_tree1(tree, field, k, v, valid_values)
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
                qq = add_to_valid_tree1(tree, field, k, vv, valid_values)
                q.extend(qq)


# Tree of sequences considered to be tags (includes sequences that are
# mapped to something that becomes one or more valid tags)
valid_sequences = {}
for tag in valid_tags:
    add_to_valid_tree(valid_sequences, "tags", tag, tag)
for tag in uppercase_tags:
    add_to_valid_tree(valid_sequences, "tags", tag, re.sub(r"\s+", "-", tag))
add_to_valid_tree_mapping(valid_sequences, "tags", xlat_tags_map,
                          valid_tags, False)
# Add topics to the same table, with all generalized topics also added
for topic in valid_topics:
    add_to_valid_tree(valid_sequences, "topics", topic, topic)
# Let each original topic value stand alone.  These are not generally on
# valid_topics.  We add the original topics with spaces replaced by hyphens.
for topic in topic_generalize_map.keys():
    add_to_valid_tree(valid_sequences, "topics", topic,
                      re.sub(r" ", "-", topic))
# Add canonicalized/generalized topic values
add_to_valid_tree_mapping(valid_sequences, "topics", topic_generalize_map,
                          valid_topics, True)

# Regexp used to find "words" from word heads and linguistic descriptions
word_re = re.compile(r"[^ ,;()\u200e]+|\(([^()]|\([^()]*\))*\)")


def distw(titleparts, word):
    """Computes how distinct ``word`` is from the most similar word in
    ``titleparts``.  Returns 1 if words completely distinct, 0 if
    identical, or otherwise something in between."""
    assert isinstance(titleparts, (list, tuple))
    assert isinstance(word, str)
    w = min(Levenshtein.distance(word, tw) / max(len(tw), len(word)) for
            tw in titleparts)
    return w


def map_with(ht, lst):
    assert isinstance(ht, dict)
    assert isinstance(lst, (list, tuple))
    ret = []
    for x in lst:
        x = x.strip()
        x = ht.get(x, x)
        if isinstance(x, str):
            ret.append(x)
        elif isinstance(x, (list, tuple)):
            ret.extend(x)
        else:
            raise RuntimeError("map_with unexpected value: {!r}".format(x))
    return ret


# If an unknown sequence starts with one of these, it will continue as an
# unknown sequence until the end, unless it turns out to have a replacement.
allowed_unknown_starts = set([
    "Relating",
    "accompanied",
    "added",
    "after",
    "answering",
    "as",
    "based",
    "before",
    "conjunction",
    "construed",
    "e.g.",
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
    "not",
    "of",
    "originally",
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
])

def decode_tags(input_tags, allow_any=False, allow_upper=False):
    """Decodes tags, doing some canonicalizations.  This returns a list of
    lists of tags and a list of topics."""
    assert isinstance(input_tags, (list, tuple))
    lst = list(x for x in input_tags if x)
    lsts = [[]]
    for x in lst:
        assert isinstance(x, str)
        x = re.sub(r",\s*", " ", x)  # Replace commas by space if they get here
        for alt in map_with(xlat_tags_map, [x]):
            lsts = list(lst1 + [alt] for lst1 in lsts)
    lsts = map_with(xlat_tags_map, list(map(lambda x: " ".join(x), lsts)))
    lsts = list(map(lambda x: x.split(), lsts))

    def check_unknown(start_i, last_i, i, tags):
        # Adds unknown tag if needed.  Returns new last_i
        # print("check_unknown start_i={} last_i={} i={}"
        #       .format(start_i, last_i, i))
        if last_i >= start_i:
            return last_i
        words = lst[last_i: start_i]
        # print("unknown words:", words)
        tag = " ".join(words)
        if not tag:
            return last_i
        if tag in ("and", "or"):
            return last_i
        tags.append(tag)
        if (not allow_any and
            (not allow_upper or not all(x[0].isupper() for x in words)) and
            not words[0].startswith("~") and
            (words[0] not in allowed_unknown_starts or len(words) <= 1)):
            # print("ERR allow_any={} allow_upper={} words={}"
            #       .format(allow_any, allow_upper, words))
            tags.append("error-unknown-tag")
        return i + 1

    topics = []
    tagsets = set()
    for lst in lsts:
        tags = []
        nodes = []
        max_last_i = 0
        for i, w in enumerate(lst):
            if not w:
                continue
            new_nodes = []

            def add_new(node, start_i, last_i):
                # print("add_new: start_i={} last_i={}".format(start_i, last_i))
                nonlocal max_last_i
                max_last_i = max(max_last_i, last_i)
                for node2, start_i2, last_i2 in new_nodes:
                    if (node2 is node and start_i2 == start_i and
                        last_i2 == last_i):
                        break
                else:
                    new_nodes.append((node, start_i, last_i))

            # print("ITER", i, w)
            for node, start_i, last_i in nodes:
                if w in node:
                    # print("INC", w)
                    add_new(node[w], start_i, last_i)
                if "$" in node:
                    # print("$", w)
                    for t in node["$"].get("tags", ()):
                        tags.extend(t.split(" "))
                    for t in node["$"].get("topics", ()):
                        topics.extend(t.split(" "))
                    max_last_i = max(max_last_i, i)
                    check_unknown(start_i, last_i, i, tags)
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i, i)
                if w not in node and "$" not in node:
                    # print("NEW", w)
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i, last_i)
            if not new_nodes:
                if lst[max_last_i] in allowed_unknown_starts:
                    # These cause the rest to be interpreted as unknown
                    break
                # print("RECOVER", w, max_last_i)
                if w in valid_sequences:
                    add_new(valid_sequences[w], i, max_last_i)
            nodes = new_nodes

        # print("END")
        valid_end = False
        for node, start_i, last_i in nodes:
            if "$" in node:
                # print("$ END")
                for t in node["$"].get("tags", ()):
                    tags.extend(t.split(" "))
                for t in node["$"].get("topics", ()):
                    topics.extend(t.split(" "))
                check_unknown(start_i, last_i, len(lst), tags)
                valid_end = True
        if not valid_end:
            # print("NOT VALID END")
            if nodes:
                for node, start_i, last_i in nodes:
                    check_unknown(len(lst), last_i, len(lst), tags)
            else:
                check_unknown(len(lst), max_last_i, len(lst), tags)

        tagsets.add(tuple(sorted(set(tags))))
    ret = list(sorted(set(tagsets)))
    # print("decode_tags: {} -> {} topics {}".format(input_tags, ret, topics))
    return ret, topics


def add_tags(ctx, data, lst, allow_any=False):
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(lst, (list, tuple))
    for x in lst:
        assert isinstance(x, str)
    tagsets, topics = decode_tags(lst, allow_any=allow_any)
    data_extend(ctx, data, "topics", topics)
    for tags in tagsets:
        data_extend(ctx, data, "tags", tags)


def parse_head_final_tags(ctx, lang, form):
    """Parses tags that are allowed at the end of a form head from the end
    of the form.  This can also be used for parsing the final gender etc tags
    from translations and linkages."""
    assert isinstance(ctx, Wtp)
    assert isinstance(lang, str)  # Should be language that "form" is for
    assert isinstance(form, str)

    tags = []

    # If parsing for certain languages (e.g., Swahili), handle some extra
    # head-final tags first
    if lang in head_final_extra_langs:
        m = re.search(head_final_extra_re, form)
        if m is not None:
            tagkeys = m.group(1)
            form = form[:m.start()]
            tags.extend(head_final_extra_map[tagkeys].split(" "))

    # Handle normal head-final tags
    m = re.search(head_final_re, form)
    if m is not None:
        tagkeys = m.group(2)
        form = form[:m.start()]
        for t in tagkeys.split():
            if t == "or":
                continue
            tags.extend(xlat_head_map[t].split(" "))
    return form, tags


def add_related(ctx, data, lst, related):
    """Internal helper function for some post-processing entries for related
    forms (e.g., in word head)."""
    assert isinstance(ctx, Wtp)
    assert isinstance(lst, (list, tuple))
    for x in lst:
        assert isinstance(x, str)
    assert isinstance(related, (list, tuple))
    # print("add_related: lst={} related={}".format(lst, related))
    related = " ".join(related)
    if related == "[please provide]":
        return
    if related == "-":
        return

    # Split to altenratives by "or".  However, if the right side of the "or"
    # is all words that are head tags, then merge with previous alternative.
    related_alts = []
    for x in related.split(" or "):
        if not related:
            continue
        if related_alts and all(y in xlat_head_map for y in x.split(" ")):
            related_alts[-1] += " or " + x
        else:
            related_alts.append(x)

    for related in related_alts:
        m = re.match(r"\((([^()]|\([^()]*\))*)\)\s*", related)
        if m:
            paren = m.group(1)
            related = related[m.end():]
            tagsets1, topics1 = decode_tags(split_at_comma_semi(paren))
        else:
            tagsets1 = [[]]
            topics1 = []
        tagsets2, topics2 = decode_tags(lst)
        for tags1 in tagsets1:
            assert isinstance(tags1, (list, tuple))
            for tags2 in tagsets2:
                assert isinstance(tags1, (list, tuple))
                if "alt-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "alt_of", related)
                elif "form-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "inflection_of", related)
                elif "compound-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "compound", related)
                else:
                    lang = ctx.section
                    related, final_tags = parse_head_final_tags(ctx, lang,
                                                                related)
                    tags = list(tags1) + list(tags2) + list(final_tags)
                    form = {"form": related}
                    data_extend(ctx, form, "tags", list(sorted(set(tags))))
                    data_extend(ctx, form, "topics", topics1)
                    data_extend(ctx, form, "topics", topics2)
                    data_append(ctx, data, "forms", form)
                    # Add tags from canonical form into the main entry
                    if "canonical" in tags:
                        for x in tags:
                            if x != "canonical":
                                data_append(ctx, data, "tags", x)


def parse_word_head(ctx, pos, text, data):
    """Parses the head line for a word for in a particular language and
    part-of-speech, extracting tags and related forms."""
    assert isinstance(ctx, Wtp)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("PARSE_WORD_HEAD: {}: {}".format(ctx.section, text))

    if text.find("Lua execution error") >= 0:
        return
    if text.find("Lua timeout error") >= 0:
        return

    language = ctx.section
    title = ctx.title
    titleparts = list(m.group(0) for m in re.finditer(word_re, title))
    if not titleparts:
        return

    # Handle the part of the head that is not in parentheses
    base = re.sub(r"\(([^()]|\([^(]*\))*\)", " ", text)
    base = re.sub(r"\?", " ", base)  # Removes uncertain articles etc
    base = re.sub(r"\s+", " ", base).strip()
    descs = split_at_comma_semi(base)
    for desc_i, desc in enumerate(descs):
        desc = desc.strip()
        if desc_i > 0 and desc.startswith("also "):
            break  # There seems to be exactly one of these, "Benen"
        for alt in desc.split(" or "):
            baseparts = list(m.group(0) for m in re.finditer(word_re, alt))
            # For non-first parts, see if it an be treated as tags-only
            if desc_i > 0:
                tagsets, topics = decode_tags([" ".join(baseparts)])
                if (not any("error-unknown-tag" in x for x in tagsets) and
                    not topics):
                    for tags in tagsets:
                        data_extend(ctx, data, "tags", tags)
                    continue
            if title != " ".join(baseparts):
                add_related(ctx, data, ["canonical"], baseparts)

    # Handle parenthesized descriptors for the word form and links to
    # related words
    parens = list(m.group(1) for m in
                  re.finditer(r"\((([^()]|\([^()]*\))*)\)", text))
    for paren in parens:
        paren = paren.strip()
        # print("HEAD PAREN:", paren)
        descriptors = map_with(xlat_descs_map, [paren])
        new_desc = []
        for desc in descriptors:
            new_desc.extend(map_with(xlat_tags_map, split_at_comma_semi(desc)))
        for desc in new_desc:
            m = re.match(r"^(\d+) strokes?$", desc)
            if m:
                # Special case, used to give #strokes for Han characters
                add_related(ctx, data, ["strokes"], [m.group(1)])
                continue
            m = re.match(r"^[\u2F00-\u2FDF\u2E80-\u2EFF\U00018800-\U00018AFF"
                         r"\uA490-\uA4CF\u4E00-\u9FFF]\+\d+$", desc)
            if m:
                # Special case, used to give radical + strokes for Han
                # characters
                add_related(ctx, data, ["radical+strokes"], [desc])
                continue
            parts = list(m.group(0) for m in re.finditer(word_re, desc))
            if not parts:
                continue

            alt_related = None
            alt_tagsets = None
            for i in range(len(parts), 0, -1):
                related = parts[i:]
                tagparts = parts[:i]
                # print("  i={} related={} tagparts={}"
                #       .format(i, related, tagparts))
                if tagparts:
                    tagsets, topics = decode_tags([" ".join(tagparts)])
                    if (topics or
                        any("error-unknown-tag" in x for x in tagsets)):
                        if alt_related is not None:
                            break
                        continue
                else:
                    tagsets = [["error-unrecognized-form"]]
                    break
                if (i > 1 and
                    len(parts[i - 1]) >= 4 and
                    distw(titleparts, parts[i - 1]) <= 0.4):
                    alt_related = related
                    alt_tagsets = tagsets
                    continue
                alt_related = None
                alt_tagsets = None
                break
            if alt_related is not None:
                related = alt_related
                tagsets = alt_tagsets

            for tags in tagsets:
                if related:
                    add_related(ctx, data, tags, related)
                else:
                    data_extend(ctx, data, "tags", tags)

def parse_sense_qualifier(ctx, text, data):
    """Parses tags or topics for a sense or some other data.  The values are
    added into the dictionary ``data``."""
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_sense_qualifier:", text)
    lst = map_with(xlat_descs_map, [text])
    for text in lst:
        for semi in split_at_comma_semi(text):
            if not semi:
                continue
            orig_semi = semi
            idx = semi.find(":")
            if idx >= 0:
                semi = semi[:idx]
            cls = classify_desc(semi)
            # print("parse_sense_qualifier: classify_desc: {} -> {}"
            #       .format(semi, cls))
            if cls == "tags":
                tagsets, topics = decode_tags([semi])
                data_extend(ctx, data, "topics", topics)
                # XXX should think how to handle distinct options better,
                # e.g., "singular and plural genitive"; that can't really be
                # done with changing the calling convention of this function.
                for tags in tagsets:
                    data_extend(ctx, data, "tags", tags)
            elif cls == "taxonomic":
                data_append(ctx, data, "taxonomic", semi)
            elif cls == "english":
                data_append(ctx, data, "english", orig_semi)
            else:
                ctx.debug("parse_sense_qualifier: unrecognized qualifier: {}"
                          .format(text))


def parse_pronunciation_tags(ctx, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    tagsets, topics = decode_tags(split_at_comma_semi(text))
    for tagset in tagsets:
        data_extend(ctx, data, "tags", tagset)
    data_extend(ctx, data, "topics", topics)


def parse_translation_desc(ctx, lang, text, tr):
    assert isinstance(ctx, Wtp)
    assert isinstance(lang, str)  # The language of ``text``
    assert isinstance(text, str)
    assert isinstance(tr, dict)
    # print("parse_translation_desc:", text)

    # Process all parenthesized parts from the translation item
    note = None
    while True:
        # See if we can find a parenthesized expression at the end
        m = re.search(r"\s*\((([^()]|\([^()]+\))+)\)\.?$", text)
        if m:
            par = m.group(1)
            text = text[:m.start()]
            if par.startswith("literally "):
                continue  # Not useful for disambiguation in many idioms
        else:
            # See if we can find a parenthesized expression at the start
            m = re.match(r"^\^?\((([^()]|\([^()]+\))+)\):?(\s+|$)", text)
            if m:
                par = m.group(1)
                text = text[m.end():]
                if re.match(r"^(\d|\s|,| or | and )+$", par):
                    # Looks like this beginning parenthesized expression only
                    # contains digits or their combinations.  We assume such
                    # to be sense descriptions if no sense has been selected,
                    # or otherwise just ignore them.
                    if not tr.get("sense"):
                        tr["sense"] = par
                    continue
            else:
                # No more parenthesized expressions - break out of the loop
                break

        # Some cleanup of artifacts that may result from skipping some templates
        # in earlier stages
        if par.startswith(": "):
            par = par[2:]
        if par.endswith(","):
            par = par[:-1]
        par = par.strip()

        # Check for special script pronunciation followed by romanization,
        # used in many Asian languages.
        lst = par.split(", ")
        if len(lst) == 2:
            a, r = lst
            if classify_desc(a) == "other":
                cls = classify_desc(r)
                # print("parse_translation_desc: r={} cls={}".format(r, cls))
                if (cls == "romanization" or
                    (cls == "english" and len(r.split()) == 1 and
                     r[0].islower())):
                    if tr.get("alt"):
                        ctx.warning("more than one value in \"alt\": {} vs. {}"
                                    .format(tr["alt"], a))
                    tr["alt"] = lst[0]
                    if tr.get("roman"):
                        ctx.warning("more than one value in \"roman\": "
                                    "{} vs. {}"
                                    .format(tr["roman"], r))
                    tr["roman"] = lst[1]
                    continue

        # Check for certain comma-separated tags combined with English text
        # at the beginning or end of a comma-separated parenthesized list
        while len(lst) > 1:
            cls = classify_desc(lst[0])
            if cls == "tags":
                tagsets, topics = decode_tags([lst[0]])
                for t in tagsets:
                    data_extend(ctx, tr, "tags", t)
                data_extend(ctx, tr, "topics", topics)
                lst = lst[1:]
                continue
            cls = classify_desc(lst[-1])
            if cls == "tags":
                tagsets, topics = decode_tags([lst[-1]])
                for t in tagsets:
                    data_extend(ctx, tr, "tags", t)
                data_extend(ctx, tr, "topics", topics)
                lst = lst[:-1]
                continue
            break
        par = ", ".join(lst)

        if not par:
            continue
        if par in ignored_parens:
            continue
        if par.startswith("Can we clean up"):
            continue
        if par.startswith("Can we verify"):
            continue
        if par.startswith("numeral:"):
            par = par[8:].strip()

        # Classify the part in parenthesis and process accordingly
        cls = classify_desc(par)
        # print("parse_translation_desc classify: {!r} -> {}"
        #       .format(par, cls))
        if cls == "tags":
            tagsets, topics = decode_tags([par])
            for tags in tagsets:
                data_extend(ctx, tr, "tags", tags)
            data_extend(ctx, tr, "topics", topics)
        elif cls == "english":
            # If the text contains any of certain grammatical words, treat it
            # as a "note" instead of "english"
            if re.search(tr_note_re, par):
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
            if tr.get("roman"):
                ctx.warning("more than one value in \"roman\": {} vs. {}"
                            .format(tr["roman"], par))
            tr["roman"] = par
        elif cls == "taxonomic":
            if tr.get("taxonomic"):
                ctx.warning("more than one value in \"taxonomic\": {} vs. {}"
                            .format(tr["taxonomic"], par))
            tr["taxonomic"] = par
        elif cls == "other":
            if tr.get("alt"):
                ctx.warning("more than one value in \"alt\": {} vs. {}"
                            .format(tr["alt"], par))
            tr["alt"] = par
        else:
            ctx.warning("parse_translation_desc: unimplemented cls: {}: {}"
                        .format(par, cls))

    # Check for gender indications in suffix
    text, final_tags = parse_head_final_tags(ctx, lang, text)
    data_extend(ctx, tr, "tags", final_tags)

    if note:
        tr["note"] = note
    if text and text not in ignored_translations:
        tr["word"] = text

    # Sometimes gender seems to be at the end of "roman" field, see e.g.
    # fire/English/Noun/Translations/Egyptian (for "oxidation reaction")
    roman = tr.get("roman")
    if roman:
        if roman.endswith(" f"):
            data_append(ctx, tr, "tags", "feminine")
            tr["roman"] = roman[:-2]
        elif roman.endswith(" m"):
            data_append(ctx, tr, "tags", "masculine")
            tr["roman"] = roman[:-2]

    # If the word now has "english" field but no "roman" field, and
    # the word would be classified "other" (generally non-latin
    # characters), and the value in "english" is only one lowercase
    # word, move it to "roman".  This happens semi-frequently when the
    # translation is transliterated the same as some English word.
    roman = tr.get("roman")
    english = tr.get("english")
    if english and not roman and "word" in tr:
        cls = classify_desc(tr["word"])
        if (cls == "other" and
            english.find(" ") < 0 and
            english[0].islower()):
            del tr["english"]
            tr["roman"] = english

    # If the entry now has both tr["roman"] and tr["word"] and they have
    # the same value, delete tr["roman"] (e.g., man/English/Translations
    # Evenki)
    if tr.get("word") and tr.get("roman") == tr.get("word"):
        del tr["roman"]

    # import json
    # print("TR:", json.dumps(tr, sort_keys=True))

# Regular expression used to strip additional stuff from the end of alt_of and
# form_of.
alt_of_form_of_clean_re = re.compile(
    r"(?s)(" +
    "|".join([
        r":",
        r";",
        r" - ",
        r" \(with ",
        r" with -ra/-re",
        r"\. Used ",
        r"\. Also ",
        r", a ",
        r", an ",
        r", the ",
        r", obsolete ",
        ]) +
    r").*$")

def parse_alt_or_inflection_of(ctx, gloss):
    """Tries to parse an inflection-of or alt-of description.  If successful,
    this returns (tags, alt-of/inflection-of-dict).  If the description cannot
    be parsed, this returns None."""
    tags = set()
    nodes = [(valid_sequences, 0)]
    gloss = re.sub(r"\s+", " ", gloss)
    lst = gloss.strip().split(" ")
    last = 0
    for i, w in enumerate(lst):
        if not w:
            continue
        new_nodes = []

        def add_new(node, next_i):
            for node2, next_i2 in new_nodes:
                if node2 is node and next_i2 == next_i:
                    break
            else:
                new_nodes.append((node, next_i))

        max_next_i = max(x[1] for x in nodes)
        for node, next_i in nodes:
            if w in node:
                add_new(node[w], next_i)
            elif w.lower() in node:
                add_new(node[w.lower()], next_i)
            if "$" in node:
                for x in node["$"].get("tags", ()):
                    tags.update(x.split(" "))
                if w in valid_sequences:
                    add_new(valid_sequences[w], i)
                elif w.lower() in valid_sequences:
                    add_new(valid_sequences[w.lower()], i)
                last = i
        if not new_nodes:
            break
        nodes = new_nodes
    else:
        # We've reached the end of the gloss
        for node, next_i in nodes:
            if "$" in node:
                for x in node["$"].get("tags", ()):
                    tags.update(x.split(" "))
                last = len(lst)

    if last == 0:
        return None

    # It is fairly common for form_of glosses to end with something like
    # "ablative case" or "in instructive case".  Parse that ending.
    # print("parse_alt_or_inflection_of: lst={}".format(lst))
    lst = lst[last:]
    if len(lst) >= 3 and lst[-1] in ("case", "case."):
        node = valid_sequences.get(lst[-2])
        if node and "$" in node:
            for t in node["$"].get("tags", ()):
                tags.update(t.split(" "))
            lst = lst[:-2]
            if lst[-1] == "in" and len(lst) > 1:
                lst = lst[:-1]

    tags = list(sorted(t for t in tags if t))
    orig_base = " ".join(lst).strip()
    # Clean up some extra stuff from the linked word
    base = re.sub(alt_of_form_of_clean_re, "", orig_base)
    base = re.sub(r" \([^()]*\)", "", base)  # Remove all (...) groups
    extra = orig_base[len(base):]
    extra = re.sub(r"^[- :;,—]+", "", extra)
    if extra.startswith("(") and extra.endswith(")"):
        extra = extra[1:-1]
    if extra.startswith('“') and extra.endswith('"'):
        extra = extra[1:-1]
    # Note: base might still contain comma-separated values and values
    # separated by "and"
    base = base.strip()
    if base.endswith("."):
        base = base[:-1]
    if base.endswith("(\u201cconjecture\")"):
        base = base[:-14].strip()
        tags.append("conjecture")
    if base.endswith("."):
        base = base[:-1].strip()
    if extra.endswith(".") and extra.count(".") == 1:
        extra = extra[:-1].strip()
    base = base.strip()
    if base.find(".") >= 0:
        ctx.debug(". remains in alt_of/inflection_of: {}".format(base))
    if not base:
        return tags, None
    dt = { "word": base }
    if extra:
        dt["extra"] = extra
    return tags, dt


def classify_desc(desc):
    """Determines whether the given description is most likely tags, english,
    a romanization, or something else.  Returns one of: "tags", "english",
    "romanization", or "other"."""
    assert isinstance(desc, str)
    # Empty and whitespace-only strings are treated as "other"
    if not desc.strip():
        return "other"

    # Check if it looks like the taxonomic name of a species
    if desc in known_species:
        return "taxonomic"
    lst = desc.split()
    if lst[0] in known_firsts and len(lst) > 1 and len(lst) < 4:
        have_non_english = lst[0].lower() not in english_words
        for x in lst[1:]:
            if x in ("A", "B", "C", "D", "E", "F", "I", "II", "III", "IV", "V"):
                continue
            if x[0].isupper():
                break
            if x not in english_words:
                have_non_english = True
        else:
            # Starts with known taxonomic term, does not contain uppercase
            # words (except allowed letters) and at least one word is not
            # English
            if have_non_english:
                return "taxonomic"

    # If it can be fully decoded as tags without errors, treat as tags
    tagsets, topics = decode_tags([desc])
    for tagset in tagsets:
        assert isinstance(tagset, (list, tuple, set))
        if ("error-unknown-tag" not in tagset and
            (topics or
             any(x.find(" ") < 0 for x in tagset))):
            return "tags"

    # If all words are in our English dictionary, interpret as English
    tokens = tokenizer.tokenize(desc)
    lst = list(x in english_words or x.lower() in english_words or
               x in known_firsts or
               x[0].isdigit() or
               (x[0].isupper() and x.find("-") < 0) or
               (x.endswith("s") and len(x) >= 4 and x[:-1] in english_words) or
               (x.endswith("ing") and len(x) >= 5 and
                x[:-3] in english_words) or
               x.endswith("'s") or
               (x.endswith("ise") and len(x) >= 5 and
                x[:-3] + "ize" in english_words) or
               (x.endswith("ised") and len(x) >= 6 and
                x[:-4] + "ized" in english_words) or
               (x.endswith("ising") and len(x) >= 7 and
                x[:-5] + "izing" in english_words) or
               (x.find("-") >= 0 and all((y in english_words or not y)
                                         for y in x.split("-")))
               for x in tokens)
    lst1 = list(m.group(0) in english_words
                for m in re.finditer(r"[\w']+", desc))
    maxlen = max(len(x) for x in tokens)
    if maxlen > 1 and lst1.count(True) > 0:
        if ((len(lst) < 5 and all(lst)) or
            lst.count(True) / len(lst) >= 0.8):
            return "english"
    # Some translations have apparent pronunciation descriptions in /.../
    # which we'll put in the romanization field (even though they probably are
    # not exactly romanizations).
    if desc.startswith("/") and desc.endswith("/"):
        return "romanization"
    # If all characters are in classes that could occur in romanizations,
    # treat as romanization
    classes = list(unicodedata.category(x)
                   if x not in ("-", ",", ":", "/", '"') else "OK"
                   for x in unicodedata.normalize("NFKD", desc))
    classes1 = []
    num_latin = 0
    num_greek = 0
    for ch, cl in zip(desc, classes):
        if ch in ("'",  # ' in Arabic, / in IPA-like parenthesized forms
                  ".",  # e.g., "..." in translations
                  ";",
                  ":",
                  "…",  # alternative to "..."
                  "ʹ"):  # ʹ e.g. in understand/English/verb Russian transl
            classes1.append("OK")
            continue
        if cl not in ("Ll", "Lu"):
            classes1.append(cl)
            continue
        name = unicodedata.name(ch)
        first = name.split()[0]
        if first == "LATIN":
            num_latin += 1
        elif first == "GREEK":
            num_greek += 1
        elif (first in ("CYRILLIC", "GUJARATI", "CJK",
                      "BENGALI", "GURMUKHI", "LAO", "KHMER",
                      "THAI", "GLAGOLITIC") or
            name.startswith("NEW TAI LUE ")):
            cl = "NO"
        classes1.append(cl)
    # print("classify_desc: {!r} classes1: {}".format(desc, classes1))
    if all(x in ("Ll", "Lu", "Lt", "Lm", "Mn", "Mc", "Zs", "Nd", "OK")
           for x in classes1):
        if num_latin >= num_greek + 2 or num_greek == 0:
            return "romanization"
    # Otherwise it is something else, such as hanji version of the word
    return "other"

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
                   head_final_numeric_langs,
                   head_final_extra_langs, head_final_extra_map)
from .english_words import english_words

# Tokenizer for classify_desc()
tokenizer = TweetTokenizer()

# Add some additional known taxonomic species names.  Adding the family name
# here may be the answer if a taxonomic name goes in "alt".
known_firsts.update([
    "Albulidae",
    "Bubo",
    "Caprobrotus",
    "Chaetodontinae",
    "Citriobatus",
    "Citrofortunella",
    "Coriandum",
    "Lagerstomia",
    "Maulisa",
    "Mercenaria",
    "Monetaria",
    "Mugillidae",
    "Onchorhynchus",
    "Plebidonax",
    "Poncirus",
    "Tanagra",
])

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
    r"(\b(article|definite|indefinite|superlative|comparative|pattern|"
    "adjective|adjectives|clause|clauses|pronoun|pronouns|preposition|prep|"
    "postposition|postp|action|actions|articles|"
    "adverb|adverbs|noun|nouns|verb|verbs|before|"
    "after|placed|prefix|suffix|used with|"
    "nominative|genitive|dative|infinitive|participle|past|perfect|imperfect|"
    "perfective|imperfective|auxiliary|negative|future|present|tense|aspect|"
    "conjugation|declension|class|category|plural|singular|positive|"
    "seldom used|formal|informal|familiar|unspoken|spoken|written|"
    "indicative|progressive|conditional|potential|"
    "accusative|adessive|inessive|superessive|elative|allative|"
    "dialect|dialects|object|subject|predicate|movies|recommended|language|"
    "locative|continuous|simple|continuousness|gerund|subjunctive|"
    "periphrastically|no equivalent|not used|not always used|"
    "used only with|not applicable|use the|signifying|wordplay|pronounced|"
    "preconsonantal|spelled|spelling|respelling|respellings|phonetic|"
    "may be replaced|stricter sense|for nonhumans|"
    "sense:|used:|in full:|informally used|followed by|"
    "not restricted to|pertaining to|or optionally with|are optional|"
    "in conjunction with|in compounds|depending on the relationship|"
    "person addressed|one person|multiple persons|may be replaced with|"
    "optionally completed with|in the phrase|in response to|"
    "before a|before an|preceded by|verbs ending|very common|after a verb|"
    "with verb|with uncountable|with the objects|with stative|"
    "can be replaced by|often after|used before|used after|"
    "used in|clipping of|spoken|somewhat|capitalized|"
    "short form|shortening of|shortened form|initialism of|"
    "said to|rare:|rarer also|is rarer|negatively connoted|"
    "previously mentioned|uncountable noun|countable noun|"
    "countable nouns|uncountable nouns|"
    "with predicative|with -|with imperfect|with a negated|"
    "colloquial|misspelling|holophrastic|frequently|esp\.|especially|"
    '"|'
    "form|regular|irregular|alternative)"
    ")($| )|^("
    # Following are only matched at the beginning of the string
    "pl|pl\.|see:|pl:|sg:|plurals:|e\.g\.|e\.g\.:|e\.g\.,|cf\.|compare|such as|"
    "see|only|often|usually|used|usage:|of|not|in|compare|usu\.|"
    "as|about|abbrv\.|abbreviation|abbr\.|that:|optionally|"
    "mainly|from|for|also|also:|acronym|"
    "with) ")
# \b does not work at the end???

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
    "conjugated",
    "conjunction",
    "construed",
    "e.g.",
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
    "With",
    "without",
])

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
    hyphenated = re.sub(r"\s+", "-", tag)
    add_to_valid_tree(valid_sequences, "tags", tag, hyphenated)
    add_to_valid_tree(valid_sequences, "tags", hyphenated, hyphenated)
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


def decode_tags(src, allow_any=False):
    """Decodes tags, doing some canonicalizations.  This returns a list of
    lists of tags and a list of topics."""
    assert isinstance(src, str)

    # print("decode_tags: src={!r}".format(src))

    pos_paths = [[[]]]

    def check_unknown(to_i, from_i, i):
        assert isinstance(to_i, int)
        assert isinstance(from_i, int)
        assert isinstance(i, int)
        # Adds unknown tag if needed.  Returns new last_i
        # print("check_unknown to_i={} from_i={} i={}"
        #       .format(to_i, from_i, i))
        if from_i >= to_i:
            return []
        words = lst[from_i: to_i]
        # print("unknown words:", words)
        tag = " ".join(words)
        if not tag:
            return from_i
        if tag in ("and", "or"):
            return []

        if (not allow_any and
            not words[0].startswith("~") and
            (words[0] not in allowed_unknown_starts or
             len(words) <= 1)):
            # print("ERR allow_any={} words={}"
            #       .format(allow_any, words))
            return [(from_i, "UNKNOWN",
                     ["error-unknown-tag", tag])]
        else:
            return [(from_i, "UNKNOWN", [tag])]
        return i + 1

    # First split the tags at commas and semicolons.  Their significance is that
    # a multi-word sequence cannot continue across them.
    lst = []
    for part in split_at_comma_semi(src, extra=[";", ":"]):
        max_last_i = len(lst)
        lst1 = part.split()
        if not lst1:
            continue
        lst.extend(lst1)
        nodes = []
        for w in lst1:
            i = len(pos_paths) - 1
            new_nodes = []

            def add_new(node, start_i, last_i, new_paths):
                assert isinstance(new_paths, list)
                # print("add_new: start_i={} last_i={}".format(start_i, last_i))
                nonlocal max_last_i
                # print("$ {} last_i={} start_i={}"
                #       .format(w, last_i, start_i))
                max_last_i = max(max_last_i, last_i)
                for node2, start_i2, last_i2 in new_nodes:
                    if (node2 is node and start_i2 == start_i and
                        last_i2 == last_i):
                        break
                else:
                    new_nodes.append((node, start_i, last_i))
                if "$" in node:
                    u = check_unknown(start_i, last_i, i)
                    new_paths.extend([(last_i,
                                       node["$"].get("tags"),
                                       node["$"].get("topics"))] + u + x
                                     for x in pos_paths[last_i])
                    max_last_i = i + 1

            new_paths = []
            # print("ITER", i, w)
            for node, start_i, last_i in nodes:
                if w in node:
                    # print("INC", w)
                    add_new(node[w], start_i, last_i, new_paths)
                if "$" in node:
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i, i, new_paths)
                if w not in node and "$" not in node:
                    # print("NEW", w)
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i, last_i, new_paths)
            if not new_nodes:
                # Some initial words cause the rest to be interpreted as unknown
                if (i == max_last_i or
                    lst[max_last_i] not in allowed_unknown_starts):
                    # print("RECOVER", w, max_last_i)
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i, max_last_i, new_paths)
            nodes = new_nodes
            pos_paths.append(new_paths)

        # print("END max_last_i={} len(lst)={} len(pos_paths)={}"
        #       .format(max_last_i, len(lst), len(pos_paths)))
        # Check for a final unknown tag
        paths = pos_paths[max_last_i] or [[]]
        u = check_unknown(len(lst), max_last_i, len(lst))
        if u:
            # print("end max_last_i={}".format(max_last_i))
            last_paths = pos_paths[-1]
            for path in list(paths):  # Copy in case it is the last pos
                pos_paths[-1].append(u + path)

        # final_paths = []
        # for node, start_i, last_i in nodes:
        #     if "$" in node:
        #         print("$ END")
        #         final_paths.append([(last_i,
        #                              node["$"].get("tags"),
        #                              node["$"].get("topics"))] +
        #                            pos_paths[start_i])
        #         # check_unknown(start_i, last_i, len(lst), final_paths)
        # if not final_paths:
        #     # print("NOT VALID END")
        #     if nodes:
        #         for node, start_i, last_i in nodes:
        #             check_unknown(len(lst), last_i, len(lst), final_paths)
        #     else:
        #         check_unknown(len(lst), max_last_i, len(lst), final_paths)
        # pos_paths[-1].extend(final_paths)

    # import json
    # print("POS_PATHS:", json.dumps(pos_paths, indent=2, sort_keys=True))

    if not pos_paths[-1]:
        # print("decode_tags: {}: EMPTY POS_PATHS[-1]".format(src))
        return [], []

    # Find the best path
    pw = []
    for path in pos_paths[-1]:
        weight = len(path)
        if any(x[1] == "UNKNOWN" for x in path):
            weight += 100  # Penalize unknown paths
        pw.append((weight, path))
    path = min(pw)[1]

    # Convert the best path to tagsets and topics
    tagsets = [[]]
    topics = []
    for i, tagspec, topicspec in path:
        if tagspec == "UNKNOWN":
            new_tagsets = []
            for x in tagsets:
                new_tagsets.append(x + topicspec)
            tagsets = new_tagsets
            continue
        if tagspec:
            new_tagsets = []
            for x in tagsets:
                for t in tagspec:
                    new_tagsets.append(x + t.split())
            tagsets = new_tagsets
        if topicspec:
            for t in topicspec:
                topics.extend(t.split())

    # print("unsorted tagsets:", tagsets)
    tagsets = list(sorted(set(tuple(sorted(set(tags))) for tags in tagsets)))
    # topics = list(sorted(set(topics)))   XXX tests expect not sorted
    # print("decode_tags: {} -> {} topics {}".format(src, tagsets, topics))
    return tagsets, topics


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
            if not ctx.title.endswith(tagkeys):
                form = form[:m.start()]
                tags.extend(head_final_extra_map[tagkeys].split(" "))

    # Handle normal head-final tags
    m = re.search(head_final_re, form)
    if m is not None:
        tagkeys = m.group(2)
        if not ctx.title.endswith(tagkeys):
            if not tagkeys[0].isdigit() or lang in head_final_numeric_langs:
                form = form[:m.start()]
                for t in tagkeys.split():
                    if t == "or":
                        continue
                    tags.extend(xlat_head_map[t].split(" "))
    return form, tags


def add_related(ctx, data, tags_lst, related):
    """Internal helper function for some post-processing entries for related
    forms (e.g., in word head)."""
    assert isinstance(ctx, Wtp)
    assert isinstance(tags_lst, (list, tuple))
    for x in tags_lst:
        assert isinstance(x, str)
    assert isinstance(related, (list, tuple))
    # print("add_related: tags_lst={} related={}".format(lst, related))
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
            tagsets1, topics1 = decode_tags(paren)
        else:
            tagsets1 = [[]]
            topics1 = []
        tagsets2, topics2 = decode_tags(" ".join(tags_lst))
        for tags1 in tagsets1:
            assert isinstance(tags1, (list, tuple))
            for tags2 in tagsets2:
                assert isinstance(tags1, (list, tuple))
                if "alt-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "alt_of", {"word": related})
                elif "form-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "form_of", {"word": related})
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
                    # Add tags from canonical form into the main entry
                    if "canonical" in tags:
                        for x in tags:
                            if x != "canonical":
                                data_append(ctx, data, "tags", x)
                        data_append(ctx, form, "tags", "canonical")
                        if ctx.title != related or topics1 or topics2:
                            data_append(ctx, data, "forms", form)
                    else:
                        data_extend(ctx, form, "tags", list(sorted(set(tags))))
                        data_append(ctx, data, "forms", form)
                    data_extend(ctx, form, "topics", topics1)
                    data_extend(ctx, form, "topics", topics2)
                    if topics1 or topics2:
                        ctx.debug("head form has topics: {}".format(form))


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
                tagsets, topics = decode_tags(" ".join(baseparts))
                if (not any("error-unknown-tag" in x for x in tagsets) and
                    not topics):
                    for tags in tagsets:
                        data_extend(ctx, data, "tags", tags)
                    continue
            add_related(ctx, data, ["canonical"], baseparts)

    # Handle parenthesized descriptors for the word form and links to
    # related words
    parens = list(m.group(1) for m in
                  re.finditer(r"\((([^()]|\([^()]*\))*)\)", text))
    for paren in parens:
        paren = paren.strip()
        if (len(paren.split()) == 1 and classify_desc(base) == "other" and
            classify_desc(paren) == "romanization"):
            add_related(ctx, data, ["romanization"], [paren])
            continue
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
                    tagsets, topics = decode_tags(" ".join(tagparts))
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

            # print("related={} tagsets={}".format(related, tagsets))
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
            cls = classify_desc(semi, allow_unknown_tags=True)
            # print("parse_sense_qualifier: classify_desc: {} -> {}"
            #       .format(semi, cls))
            if cls == "tags":
                tagsets, topics = decode_tags(semi)
                data_extend(ctx, data, "topics", topics)
                # XXX should think how to handle distinct options better,
                # e.g., "singular and plural genitive"; that can't really be
                # done with changing the calling convention of this function.
                for tags in tagsets:
                    data_extend(ctx, data, "tags", tags)
            elif cls == "taxonomic":
                if re.match(r"×[A-Z]", semi):
                    data_append(ctx, dt, "tags", "extinct")
                    semi = semi[1:]
                data["taxonomic"] = semi
            elif cls == "english":
                if "english" in data:
                    data["english"] += "; " + orig_semi
                else:
                    data["english"] = orig_semi
            else:
                ctx.debug("parse_sense_qualifier: unrecognized qualifier: {}"
                          .format(text))


def parse_pronunciation_tags(ctx, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    tagsets, topics = decode_tags(text)
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
    restore_beginning = ""
    restore_end = ""
    while True:
        beginning = False
        # See if we can find a parenthesized expression at the end
        m = re.search(r"\s*\((([^()]|\([^()]+\))+)\)\.?$", text)
        if m:
            par = m.group(1)
            text = text[:m.start()]
            if par.startswith("literally ") or par.startswith("lit."):
                continue  # Not useful for disambiguation in many idioms
        else:
            # See if we can find a parenthesized expression at the start
            m = re.match(r"^\^?\((([^()]|\([^()]+\))+)\):?(\s+|$)", text)
            if m:
                par = m.group(1)
                text = text[m.end():]
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
                # No more parenthesized expressions - break out of the loop
                break

        # Some cleanup of artifacts that may result from skipping some templates
        # in earlier stages
        if par.startswith(": "):
            par = par[2:]
        if par.endswith(","):
            par = par[:-1]
        if re.match(r'^["“]([^"]*)"$', par):
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
                if (cls == "romanization" or
                    (cls == "english" and len(r.split()) == 1 and
                     r[0].islower())):
                    if tr.get("alt"):
                        ctx.warning("more than one value in \"alt\": {} vs. {}"
                                    .format(tr["alt"], a))
                    tr["alt"] = a
                    if tr.get("roman"):
                        ctx.warning("more than one value in \"roman\": "
                                    "{} vs. {}"
                                    .format(tr["roman"], r))
                    tr["roman"] = r
                    continue

        # Check for certain comma-separated tags combined with English text
        # at the beginning or end of a comma-separated parenthesized list
        while len(lst) > 1:
            cls = classify_desc(lst[0])
            if cls == "tags":
                tagsets, topics = decode_tags(lst[0])
                for t in tagsets:
                    data_extend(ctx, tr, "tags", t)
                data_extend(ctx, tr, "topics", topics)
                lst = lst[1:]
                continue
            cls = classify_desc(lst[-1])
            if cls == "tags":
                tagsets, topics = decode_tags(lst[-1])
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
            tagsets, topics = decode_tags(par)
            for tags in tagsets:
                data_extend(ctx, tr, "tags", tags)
            data_extend(ctx, tr, "topics", topics)
        elif cls == "english":
            # If the text contains any of certain grammatical words, treat it
            # as a "note" instead of "english"
            if re.search(tr_note_re, par):
                if par.endswith(":"):
                    par = par[:-1]
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
            if classify_desc(text) in ("english", "romanization"):
                if beginning:
                    restore_beginning += "({}) ".format(par)
                else:
                    restore_end = " ({})".format(par) + restore_end
            if tr.get("roman"):
                ctx.warning("more than one value in \"roman\": {} vs. {}"
                            .format(tr["roman"], par))
            tr["roman"] = par
        elif cls == "taxonomic":
            if tr.get("taxonomic"):
                ctx.warning("more than one value in \"taxonomic\": {} vs. {}"
                            .format(tr["taxonomic"], par))
            if re.match(r"×[A-Z]", par):
                data_append(ctx, dt, "tags", "extinct")
                par = par[1:]
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
            data_append(ctx, tr, "tags", "feminine")
            tr["roman"] = roman[:-2].strip()
        elif roman.endswith(" m"):
            data_append(ctx, tr, "tags", "masculine")
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
    # Occasionally inflection_of/alt_of have "A(n) " at the beginning.
    m = re.match(r"(A\(n\)|A|a|an|An) ", gloss)
    if m:
        gloss = gloss[m.end():]
    # First try parsing it as-is
    parsed = parse_alt_or_inflection_of1(ctx, gloss)
    if parsed is not None:
        return parsed
    # Next try parsing it with the first character converted to lowercase if
    # it was previously uppercase.
    if gloss and gloss[0].isupper():
        gloss = gloss[0].lower() + gloss[1:]
        parsed = parse_alt_or_inflection_of1(ctx, gloss)
        if parsed is not None:
            return parsed
    # Cannot parse it as an alt-of or form-of.
    return None

def parse_alt_or_inflection_of1(ctx, gloss):
    """Helper function for parse_alt_or_inflection_of.  This handles a single
    capitalization."""
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
    base = re.sub(r" [(⟨][^()]*[)⟩]", "", base)  # Remove all (...) groups
    extra = orig_base[len(base):]
    extra = re.sub(r"^[- :;,—]+", "", extra)
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
    if base.endswith("."):
        base = base[:-1]
    if base.endswith("(\u201cconjecture\")"):
        base = base[:-14].strip()
        tags.append("conjecture")
    if base.endswith("."):
        base = base[:-1].strip()
    base = base.strip()
    if base.find(".") >= 0:
        ctx.debug(". remains in alt_of/inflection_of: {}".format(base))
    if not base:
        return tags, None
    dt = { "word": base }
    if extra:
        dt["extra"] = extra
    return tags, dt


def classify_desc(desc, allow_unknown_tags=False):
    """Determines whether the given description is most likely tags, english,
    a romanization, or something else.  Returns one of: "tags", "english",
    "romanization", or "other".  If ``allow_unknown_tags`` is True, then
    allow "tags" classification even when the only tags are those starting
    with a word in allowed_unknown_starts. """
    assert isinstance(desc, str)
    # Empty and whitespace-only strings are treated as "other"
    if not desc.strip():
        return "other"

    # Check if it looks like the taxonomic name of a species
    if desc in known_species:
        return "taxonomic"
    desc1 = re.sub(r"^×([A-Z])", r"\1", desc)
    desc1 = re.sub(r"\s*×.*", "", desc1)
    lst = desc1.split()
    if len(lst) > 1 and len(lst) <= 5 and lst[0] in known_firsts:
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
    tagsets, topics = decode_tags(desc)
    for tagset in tagsets:
        assert isinstance(tagset, (list, tuple, set))
        if ("error-unknown-tag" not in tagset and
            (topics or allow_unknown_tags or
             any(x.find(" ") < 0 for x in tagset))):
            return "tags"

    # If all words are in our English dictionary, interpret as English
    if desc in english_words and desc[0].isalpha():
        return "english"   # Handles ones containing whitespace
    tokens = tokenizer.tokenize(desc)
    lst = list(x in english_words or x.lower() in english_words or
               x in known_firsts or
               x[0].isdigit() or
               (x[0].isupper() and x.find("-") < 0) or
               (x.endswith("s") and len(x) >= 4 and x[:-1] in english_words) or
               (x.endswith("ing") and len(x) >= 5 and
                x[:-3] in english_words) or
               x.endswith("'s") or
               x.endswith("s'") or
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
    if (maxlen > 1
        and lst1.count(True) >= len(lst1) / 2 and
        len(list(re.finditer(r"\w+", desc))) > 0):
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
        if ((num_latin >= num_greek + 2 or num_greek == 0) and
            classes1.count("OK") < len(classes1) and
            classes1.count("Nd") < len(classes1)):
            return "romanization"
    # Otherwise it is something else, such as hanji version of the word
    return "other"

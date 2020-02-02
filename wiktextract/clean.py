# This file contains code to clean Wiktionary annotations from a string and to
# produce plain text from it, typically for glossary entries but this is also
# called for various other data to produce clean strings.
#
# This file also contains code for cleaning qualifiers for the "tags" field.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import html
from .wikttemplates import *
from .places import place_prefixes

# XXX
lang_codes = set(["en", "fr", "fi", "de", "it", "pt", "es", "ja", "zh", "sv"])

######################################################################
# Cleaning values into plain text.
######################################################################

# Note: arg_re contains two sets of parenthesis
arg_re = (r"\|(("
          r"[^][|{}]|"
          #r"\{\{[^{}]+?\}\}|"
          r"\{[^{}]+?\}"
          r")*)")

# Matches more arguments and end of template
args_end_re = r"\}\}"

# Regexp used in clean_replace_regexp
clean_rege = (r"(?s)\{\{([^}|]+)" +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              # 10
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              # 20
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              # 30
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r"(" + arg_re +
              r")?)?)?)?)?)?)?)?)?)?" +
              r")?)?)?)?)?)?)?)?)?)?" +
              r")?)?)?)?)?)?)?)?)?)?" +
              r")?)?)?)?)?)?)?)?)?)?" +
              args_end_re +
              r"|\[\[[^][{}]+?\]\]" +
              r"|\[[^][{}]+?\]")
clean_re = re.compile(clean_rege)

# Indexes of groups in clean_re
template_groupidxs = tuple(3 + 3 * i for i in range(0, 9))

# Regular expression for matching template arguments that have a name
template_arg_with_name_re = re.compile(r"^([-_a-zA-Z0-9\s]+)=(.*)$")

# def prepare_dest(v):
#     for i in range(len(template_groupidxs) - 1, 0, -1):
#         src = r"\\{}([^0-9]|$)".format(i)
#         dst = r"\\{}\1".format(template_groupidxs[i])
#         v = re.sub(src, dst, v)
#     return v

arg1_dest = ["{arg1}"]
arg2_dest = ["{arg2}"]
arg3_dest = ["{arg3}"]
clean_dest_ht = {}
for k in clean_arg1_tags:
    clean_dest_ht[k] = arg1_dest
for k in clean_arg2_tags:
    if k in clean_dest_ht:
        print("TAG {} MULTIPLY DEFINED".format(k))
        assert False
    clean_dest_ht[k] = arg2_dest
for k in clean_arg3_tags:
    if k in clean_dest_ht:
        print("TAG {} MULTIPLY DEFINED".format(k))
        assert False
    clean_dest_ht[k] = arg3_dest
for k, dests in clean_replace_map.items():
    if k in clean_dest_ht:
        print("TAG {} MULTIPLY DEFINED".format(k))
        assert False
    if not isinstance(dests, (list, tuple)):
        print("NON-LIST DESTS in clean_replace_map: {}: {}".format(k, dests))
        assert False
    clean_dest_ht[k] = dests


def clean_replace_regexp(word, v):
    """Performs regexp substitutions on a string being cleaned up."""

    def clean_gen_repl(m):
        """Finds the substitution for for a clean-up match."""
        #print("{} CLEAN_GEN_REPL {}".format(word, m.group(0)))
        t = m.group(0)
        if t.startswith("[["):
            vec = t[2:-2].split("|")
            if len(vec) > 2:
                print("{} LINK WITH TOO MANY ARGS: {}".format(word, t))
            if len(vec) >= 2:
                return vec[1]
            v = vec[0]
            if v.startswith("Category:"):
                return ""
            if v.startswith(":Category:"):
                v = v[10:]
            return v
        if t.startswith("["):
            vec = t[1:-1].split(" ")
            if vec[0].startswith("http:") or vec[0].startswith("https:"):
                vec = vec[1:]
            return " ".join(vec)
        # Otherwise it must be a template
        assert t.startswith("{{")
        tag = m.group(1).strip()
        tag = re.sub(r"\s+", " ", tag)
        for prefix in ("R:", "RQ:", "table:", "list:", "DEFAULTSORT:"):
            if tag.startswith(prefix):
                return ""
        if tag not in clean_dest_ht:
            if tag in ignored_templates:
                return ""
            # Fall to using default expansion
        else:
            lst = list(x or "" for x in m.groups())
            parts = list(lst[i - 1].strip()
                         for i in template_groupidxs if i <= len(lst))
            kwargs = {"word": word}
            argnum = 1
            for g in parts:
                argm = re.match(template_arg_with_name_re, g)
                if argm is None:
                    if g != "":
                        kwargs["arg{}".format(argnum)] = g
                    argnum += 1
                else:
                    k = argm.group(1).strip()
                    v = argm.group(2).strip()
                    k = re.sub(r"\s+", " ", k)
                    if k.isdigit():
                        k = "arg" + k
                    kwargs[k] = v
            dests = clean_dest_ht[tag]
            #print("{} CLEAN: dests={} kwargs={} lst={} parts={}"
            #      "".format(word, dests, kwargs, lst, parts))
            for dest in dests:
                try:
                    ret = dest.format(**kwargs)
                    return ret
                except (KeyError, ValueError):
                    #print("{} CLEAN_GEN_REPL: FAILED DEST {} FOR {} IN {}"
                    #      "".format(word, dest, kwargs, m.group(0)))
                    continue
            else:
                print("{} CLEAN_GEN_REPL: BAD DESTS IN {} FOR {}"
                      "".format(word, dests, m.group(0)))
        # Default expansion for the template concatenates arguments, except
        # named arguments
        groups = list(x or "" for x in m.groups())
        lst = []
        for i in range(0, len(groups)):
            x = groups[i]
            idx = x.find("/")
            if idx >= 0:
                if x[:idx] in place_prefixes and not x[idx + 1:].find("/"):
                    x = x[idx + 1:]
            lst.append(x)
        parts = list(lst[i - 1].strip() for i in template_groupidxs
                     if i <= len(lst) and
                     re.match(template_arg_with_name_re, lst[i - 1]) is None and
                     lst[i - 1] not in ("_", ""))
        if parts and parts[0] in lang_codes:
            parts = parts[1:]
        ret = " ".join(parts).strip()
        if tag in default_parenthesize_tags:
            ret = "(" + ret + ")"
        if tag not in default_tags and tag not in default_parenthesize_tags:
            print("{} NO REPLACEMENT FOR {} IN {}"
                  "".format(word, tag, m.group(0)))
            #print("{} CLEAN_GEN_REPL {} {} {} -> {}"
            #      "".format(word, tag, m.group(0), parts, ret))
        return ret

    # Repeat replacements as there could be nested structures
    try:
        iter = 0
        while True:
            v, count = re.subn(clean_re, clean_gen_repl, v)
            #print("CLEAN_REPLACE_REGEXP", count)
            if count == 0:
                break
            iter += 1
            if iter > 10:
                print("CLEAN_REPLACE_REGEXP EXCESS ITERATIONS", repr(v))
                assert False
    except re.error:
        print("CLEAN_REPLACE_REGEXP ERROR CLEANING {}".format(repr(v)))
    return v


def clean_value(word, title):
    """Cleans a title or value into a normal string.  This should basically
    remove any Wikimedia formatting from it: HTML tags, templates, links,
    emphasis, etc.  This will also merge multiple whitespaces into one
    normal space and will remove any surrounding whitespace."""
    # Replace templates according to our our replacement tables
    # clean_arg_arg1_tags, clean_arg2_tags, clean_arg3_tags, clean_replace_map.
    title = clean_replace_regexp(word, title)
    # Remove any remaining templates.
    for m in re.finditer(r"\{\{[^}]+\}\}", title):
        print("{} CLEAN_VALUE REMAINING TEMPLATE: {}"
              "".format(word, m.group(0)))
    title = re.sub(r"\{\{[^}]+\}\}", "", title)
    # Remove references (<ref>...</ref>).
    title = re.sub(r"(?s)<ref>.*?</ref>", "", title)
    # Replace <br/> by comma space (it is used to express alternatives in some
    # declensions)
    title = re.sub(r"(?s)<br/?>", ", ", title)
    # Remove any remaining HTML tags.
    title = re.sub(r"(?s)<[^>]+>", "", title)
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
    # Replace strange unicode quotes with normal quotes
    title = re.sub(r"”", '"', title)
    # Replace unicode long dash by normal dash
    title = re.sub(r"–", "-", title)
    # Replace whitespace sequences by a single space.
    title = re.sub(r"\s+", " ", title)
    # Remove whitespace before periods and commas etc
    title = re.sub(r" ([.,;:!?)])", r"\1", title)
    # Strip surrounding whitespace.
    title = title.strip()
    return title


######################################################################
# Cleaning qualifier values; these are generally used for the "tags"
# field and may encode things like "archaic", "dialectical", "UK",
# topic areas, inflectional forms, etc.
######################################################################

quals_left_connect = set(["usually", "often", "rarely", "strongly",
                          "extremely", "including", "slightly", "possibly",
                          "especially", "of", "a", "mildly", "specifically",
                          "more", "generally", "particularly", "mainly",
                          "literally", "somewhat",
                          "narrowly", "quite", "not", "originally",
                          "except", "formerly", "properly", "always", "later",
                          "chiefly", "sometimes", "mostly", "then", "strictly"])
quals_strip = set(["usually", "often", "strongly", "extremely", "chiefly",
                   "mostly", "especially", "highly", "particularly"])
quals_both_connect = ("in", "_", "with", "outside")
quals_skip = ("or", "and", "&", ",", "now", "very", "also", "later")
quals_standalone = set([#"present", "past", "participle", "infinitive",
                        #"future", "subjunctive", "imperative",
                        #"transitive", "intransitive", "reflexive",
                        #"nominative", "genitive", "accusative", "dative",
                        #"plural", "singular", "feminine", "masculine",
                        #"neuter",
                        #"modal", "auxiliary",
                        #"definite", "indefinite",
                        #"countable", "uncountable",
])
quals_map = {
    "in the plural": ["plural"],
    "in the singular": ["singular"],
    "dated": ["archaic"],
}

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
    i = 0
    if vec and vec[0] in lang_codes:
        # If the qualifiers are from a template that has language tags,
        # those hould be removed from the vector before passing it to
        # this function.  This warning indicates the caller probably
        # forgot to remove the language tag.
        print("clean_quals: WARNING: {} in vec: {}".format(x, vec))
        i += 1
    while i < len(vec):
        if vec[i] in quals_skip:
            i += 1
            continue
        tagparts = [vec[i]]
        i += 1
        # Certain modifiers are often written as separate arguments but
        # actually modify the following value.  We combine them with the
        # following value using a space.
        while (i < len(vec) and
               vec[i - 1] not in quals_skip and
               vec[i] not in quals_skip and
               vec[i] not in quals_standalone and
               (vec[i - 1] in quals_left_connect or
                vec[i - 1] in quals_both_connect or
                vec[i] in quals_both_connect)):
            v = vec[i]
            if v != "_":
                tagparts.append(v)
            i += 1
        tag = " ".join(tagparts)
        if tag in quals_map:
            tags.extend(quals_map[tag])
        elif tag in quals_skip:
            pass
        elif len(tagparts) == 2 and tagparts[1] in quals_strip:
            tags.append(tagparts[1])
            tags.append(tag)
        else:
            tags.append(tag)
    # print("CLEAN_QUALS: {} -> {}".format(vec, tags))

    # XXX filter out qualifiers that we do not consider valid, for example
    # very long ones

    # XXX map variant qualifier values to canonical values

    return tags

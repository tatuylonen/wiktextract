# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import collections
import wikitextparser
from .parts_of_speech import part_of_speech_map, PARTS_OF_SPEECH
from .config import WiktionaryConfig
from .sectitle_corrections import sectitle_corrections
from .clean import clean_value, clean_quals
from .places import place_prefixes  # XXX move processing to places.py
from .wikttemplates import *
from .languages import all_languages
from .unsupported_titles import unsupported_title_map
from .form_of import form_of_map
from .head_map import head_pos_map

# Mapping from language name to language info
languages_by_name = {x["name"]: x for x in all_languages}

# Mapping from language code to language info
languages_by_code = {x["code"]: x for x in all_languages}

# Matches en:, fr:, etc.
langtag_colon_re = re.compile(r"^(" + "|".join(languages_by_code.keys()) +
                              r"):")

# Mapping from German verb form arguments to "canonical" values in
# word sense tags."""
de_verb_form_map = {
    # Keys under which to look for values
    "_keys": [2, 3, 4, 5, 6, 7, 8, 9],
    # Mapping of values in arguments to canonical values
    "1": ["first-person"],
    "2": ["second-person"],
    "3": ["third-person"],
    "pr": ["present participle"],
    "pp": ["past participle"],
    "i": ["imperative"],
    "s": ["singular"],
    "sg": ["singular"],
    "p": ["plural"],
    "g": ["present"],
    "v": ["past"],
    "k1": ["subjunctive 1"],
    "k2": ["subjunctive 2"],
    "a": ["subordinate"],
    "yes": ["subordinate"],
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
    # ??? imperative or imperfect? "imp": ["past"],
    "imperfect": ["imperfect"],
    "past": ["past"],
    "fut": ["future"],
    "future": ["future"],
    "cond": ["conditional"],
    "conditional": ["conditional"],
    "s": ["singular"],
    "sg": ["singular"],
    "sing": ["singular"],
    "singular": ["singular"],
    "p": ["plural"],
    "pl": ["plural"],
    "plural": ["plural"],
    "1": ["first-person"],
    "first": ["first-person"],
    "first-person": ["first-person"],
    "2": ["second-person"],
    "second": ["second-person"],
    "second person": ["second-person"],
    "second-person": ["second-person"],
    "3": ["third-person"],
    "third": ["third-person"],
    "third person": ["third-person"],
    "third-person": ["third-person"],
    "impersonal": ["impersonal"],
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
    "n": ["informal"],
}

nl_verb_form_map = {
    # Argument names under which we search for values.
    "_keys": ["p", "n", "t", "m"],
    # Mapping of values in arguments to canonical values
    "1": ["first-person"],
    "2": ["second-person"],
    "2-gij": ["second-person"],
    "2-u": ["second-person"],
    "3": ["third-person"],
    "123": ["first-person", "second-person", "third-person"],
    "13": ["first-person", "third-person"],
    "23": ["second-person", "third-person"],
    "imp": ["imperative"],
    "sg": ["singular"],
    "pl": ["plural"],
    "pres": ["present"],
    "past": ["past"],
    "ind": ["indicative"],
    "indc": ["indicative"],
    "subj": ["subjunctive"],
    "ind+subj": ["indicative", "subjective"],
    "ptc": ["participle"],
}

generic_verb_form_map = {
    "_keys": ["4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"],
    "1": ["first-person"],
    "2": ["second-person"],
    "3": ["third-person"],
    "s": ["singular"],
    "p": ["plural"],
    "1s": ["first-person", "singular"],
    "2s": ["second-person", "singular"],
    "3s": ["third-person", "singular"],
    "1p": ["first-person", "plural"],
    "2p": ["second-person", "plural"],
    "3p": ["third-person", "plural"],
    "pres": ["present"],
    "past": ["past"],
    "impf": ["imperfect"],
    "perf": ["perfect"],
    "plup": ["pluperfect"],
    "ind": ["indicative"],
    "sub": ["subjunctive"],
    "ind//sub": ["indicative", "subjunctive"],
    "imp": ["imperative"],
    "aor": ["aorist"],
    "sim": ["simple"],
    "cond": ["conditional"],
    "conditional": ["conditional"],
    "conj": ["conjunctive"],
    "conjunctive": ["conjunctive"],
    "quot": ["quotative"],
    "quotative": ["quotative"],
    "deb": ["debitive"],
    "debitive": ["debitive"],
}

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
    "letter": ["letter"],
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


# Keys in ``data`` that can only have string values (a list of them)
str_keys = ("tags", "glosses")
# Keys in ``data`` that can only have dict values (a list of them)
dict_keys = ("pronunciations", "senses", "synonyms", "related",
             "antonyms", "hypernyms", "holonyms")


def remove_html_comments(text):
    """Removes HTML comments from the value."""
    assert isinstance(text, str)
    text = re.sub(r"(?s)<!--.*?-->", "", text)
    text = text.strip()
    return text


def split_subsections(config, text):
    """Split the text into a linear sequence of sections.  Note that we
    ignore the nesting structure of subtitles, since that seems to be
    poorly enforced in Wiktionary.  This returns a list of (subtitle,
    text).  The subtitle has been fully cleaned, and HTML comments
    have been removed from the text."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(text, str)
    # Remove HTML comments from the whole page.  We want to do this before
    # analyzing subsections, as they could be commented out.
    text = remove_html_comments(text)
    # Find start and end offsets and titles for all subsections
    regexp = r"(?s)(^|\n)==+([^=\n]+?)==+"
    offsets = list((m.start(), m.end(), clean_value(config, m.group(2)))
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
        subtitle = clean_value(config, subtitle)
        # Add an entry for the subsection.
        subsection = text[start: end]
        subsections.append((subtitle, subsection))
    return subsections


def data_append(config, data, key, value):
    """Appends ``value`` under ``key`` in the dictionary ``data``.  The key
    is created if it does not exist."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(key, str)

    if key in str_keys:
        assert isinstance(value, str)
    elif key in dict_keys:
        assert isinstance(value, dict)
    if key == "tags":
        if value == "":
            return
        if value in languages_by_code:
            if value not in ("law", "toy", "and", "etc", "the", "god", "adj",
                             "man", "an", "tax", "or", "war", "job", "box",
                             "pop", "cay", "lay", "nut", "bay", "sea"):
                config.debug("language code {} in tags: {}".format(value, data))
    lst = data.get(key, [])
    lst.append(value)
    data[key] = lst


def data_extend(config, data, key, values):
    """Appends all values in a list under ``key`` in the dictionary ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(key, str)
    assert isinstance(values, (list, tuple))

    for x in values:
        data_append(config, data, key, x)


def data_inflection_of(config, data, t, tags):
    """Adds an "inflection_of" value to ``data`` for the last argument of
    template ``t``.  Adds ``tags`` to the "tags" value in ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(tags, (list, tuple))

    vec = t_vec(config, t)
    if len(vec) == 0:
        config.debug("data_inflection_of empty vec: {} {} {}"
                     "".format(str(t), data, tags))
        return
    data_append(config, data, "inflection_of", vec[-1])
    data_extend(config, data, "tags", tags)


def data_alt_of(config, data, t, tags):
    """Adds an "alt_of" value to ``data`` for the last argument of
    template ``t``.  Adds ``tags`` to the "tags" value in ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(tags, (list, tuple))

    vec = t_vec(config, t)
    if len(vec) == 0:
        config.debug("data_alt_of empty vec: {} {} {}"
                     "".format(str(t), data, tags))
        return
    data_append(config, data, "alt_of", vec[-1])
    data_extend(config, data, "tags", tags)


def t_dict(config, t):
    """Returns a dictionary containing the template arguments.  This is
    typically used when the argument dictionary will be returned from the
    parsing.  Positional arguments will be keyed by numeric strings.
    The name of the template will be added under the key "template_name"."""
    assert isinstance(config, WiktionaryConfig)

    ht = {}
    for x in t.arguments:
        name = x.name.strip()
        value = x.value
        ht[name] = clean_value(config, value)
    ht["template_name"] = t.name.strip()
    return ht


def t_vec(config, t):
    """Returns a list containing positional template arguments.  Empty strings
    will be added for any omitted arguments.  The vector will include the last
    non-empty supplied argument, but not values beyond it."""
    assert isinstance(config, WiktionaryConfig)

    vec = []
    for i in range(1, 20):
        v = t_arg(config, t, i)
        vec.append(v)
    while vec and not vec[-1]:
        vec.pop()
    return vec


def t_arg(config, t, arg):
    """Retrieves argument ``arg`` from the template.  The argument may be
    identified either by its number or a string name.  Positional argument
    numbers start at 1.  This returns the empty string for arguments that
    don't exist.  The argument value is cleaned before returning."""
    # If the argument specifier is an integer, convert it to a string.
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(arg, (str, int))

    if isinstance(arg, int):
        arg = str(arg)
    assert isinstance(arg, str)
    # Get the argument value from the template.
    v = t.get_arg(arg)
    # If it does not exist, return empty string.
    if v is None:
        return ""
    # Otherwise clean the value.
    return clean_value(config, v.value)


def verb_form_map_fn(config, data, name, t, form_map):
    """Maps values in a language-specific verb form map into values for "tags"
    that are reasonably uniform across languages.  This also deals with a
    lot of misspellings and inconsistencies in how the values are entered in
    Wiktionary.  ``data`` here is the word sense."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(name, str)
    assert isinstance(form_map, dict)
    # Add an indication that the word sense is a form of an other word.
    data_append(config, data, "inflection_of", t_arg(config, t, 1))
    # Iterate over the specified keys in the template.
    for k in form_map["_keys"]:
        v = t_arg(config, t, k)
        if not v:
            continue
        # Got a value for key.  Now map the value.  Each entry in the
        # dictionary should be a list of tags to add.
        if v in form_map:
            lst = form_map[v]
            assert isinstance(lst, (list, tuple))
            for x in lst:
                assert isinstance(x, str)
                data_append(config, data, "tags", x)
        else:
            config.unknown_value(t, v)


def parse_sense(config, data, text, use_text):
    """Parses a word sense from the text.  The text is usually a list item
    from the beginning of the dictionary entry (i.e., before the first
    subtitle).  There is a lot of information and linkings in the sense
    description, which we try to gather here.  We also try to convert the
    various encodings used in Wiktionary into a fairly uniform form.
    The goal here is to obtain any information that might be helpful in
    automatically determining the meaning of the word sense."""
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
        if gloss:
            # Got a gloss for this sense.
            data_append(config, data, "glosses", gloss)

    # Parse the Wikimedia coding from the text.
    p = wikitextparser.parse(text)

    # Iterate over all templates in the text.
    for t in p.templates:
        name = t.name.strip()

        # Labels and various other links are used for qualifiers. However,
        # they also seem to be sometimes used for other purposes, so this
        # may result in extra tags that perhaps should be elsewhere.
        if name in ("lb", "label", "context", "term-context", "term-label",
                      "lbl", "tlb", "tcx"):
            # XXX make sure these all start with a language code
            data_extend(config, data, "tags",
                        clean_quals(config, t_vec(config, t)[1:]))
        elif name == "g2":
            v = t_arg(config, t, 1)
            if v == "m":
                data_append(config, data, "tags", "masculine")
            elif v == "f":
                data_append(config, data, "tags", "feminine")
            elif v == "n":
                data_append(config, data, "tags", "neuter")
            else:
                config.unknown_value(t, v)
        # Qualifiers are pretty clear; they provide useful information about
        # the word sense, such as field of study, dialect, or usage notes.
        elif name in ("qual", "qualifier", "q", "qf", "i", "a", "accent"):
            data_extend(config, data, "tags",
                        clean_quals(config, t_vec(config, t)))
        # Usage examples are collected under "examples"
        elif name in ("ux", "uxi", "usex", "afex", "zh-x", "prefixusex",
                      "ko-usex", "ko-x", "hi-x", "ja-usex-inline", "ja-x",
                      "quotei"):
            data_append(config, data, "examples", t_dict(config, t))
        # XXX check these, I think they should go away
        # Additional "gloss" templates are added under "glosses"
        #elif name == "gloss":
        #    gloss = t_arg(config, t, 1)
        #    data_append(config, data, "glosses", gloss)
        # Various words have non-gloss definitions; we collect them under
        # "nonglosses".  For many purposes they might be treated similar to
        # glosses, though.
        elif name in ("non-gloss definition", "n-g", "ngd", "non-gloss",
                      "non gloss definition"):
            gloss = t_arg(config, t, 1)
            data_append(config, data, "nonglosses", gloss)
        # The senseid template seems to have varied uses. Sometimes it contains
        # a Wikidata id Q<numbers>; at other times it seems to be something
        # else.  We collect them under "senseid".  XXX this needs more study
        elif name == "senseid":
            data_append(config, data, "wikidata", t_arg(config, t, 2))
        # The "sense" templates are treated as additional glosses.
        elif name in ("sense", "Sense"):
            data_append(config, data, "tags", t_arg(config, t, 1))
        # These weird templates seem to be used to indicate a literal sense.
        elif name in ("&lit", "&oth"):
            data_append(config, data, "tags", "literal")
        # Many given names (first names) are tagged as such.  We tag them as
        # such, and tag with gender when available.  We also tag the term
        # as meaning an organism (though this might not be the case in rare
        # cases) and "person" (if it has a gender).
        elif name in ("given name",
                      "forename",
                      "historical given name"):
            data_extend(config, data, "tags", ["person", "given_name"])
            for k, v in t_dict(config, t).items():
                if k in ("template_name", "usage", "f", "var", "var2",
                         "from", "from2", "from3", "from4", "from5", "fron",
                         "fromt", "meaning", "m", "mt", "f",
                         "diminutive", "diminutive2",
                         "dim", "dim2", "dim3", "dim4", "dim5",
                         "dim6", "dim7", "dim8", "eq", "eq2", "eq3", "eq4",
                         "eq5", "A", "3"):
                    continue
                if k == "sort":
                    data_append(config, data, "sort", v)
                    continue
                if v == "en" or (k == "1" and len(v) <= 3):
                    continue
                if v in ("male_or_female", "unisex"):
                    pass
                elif v == "male":
                    data_append(config, data, "tags", "masculine")
                elif v == "female":
                    data_append(config, data, "tags", "feminine")
                else:
                    config.unknown_value(t, v)
        # Surnames are also often tagged as such, and we tag the sense
        # with "surname" and "person".
        elif name == "surname":
            data_extend(config, data, "tags", ["surname", "person"])
            from_ = t_arg(config, t, "from")
            if from_:
                data_append(config, data, "origin", from_)
        # Many nouns that are species and other organism types have taxon
        # links using various templates.  Store those links under
        # "taxon" (try to extract the species name).
        elif name in ("taxlink", "taxlinkwiki"):
            x = t_arg(config, t, 1)
            m = re.search(r"(.*) (subsp\.|f.)", x)
            if m:
                x = m.group(1)
            data_append(config, data, "taxon", t_vec(config, t))
            data_append(config, data, "tags", "organism")
        elif name == "taxon":
            data_append(config, data, "taxon", t_arg(config, t, 3))
            data_append(config, data, "tags", "organism")
        # Many organisms have vernacular names.
        elif name == "vern":
            data_append(config, data, "taxon", t_arg(config, t, 1))
            data_append(config, data, "tags", "organism")
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
        # SI units of measurement appear to have tags that identify them
        # as such.  Add the information under "unit" and tag them as "unit".
        elif name in ("SI-unit", "SI-unit-2",
                      "SI-unit-np", "SI-unit-abb", "SI-unit-abbnp",
                      "SI-unit-abb2"):
            data_append(config, data, "unit", t_dict(config, t))
            data_append(config, data, "tags", "unit-of-measurement")
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
        # There are even morse code sequences (and semaphore (flag)) positions
        # defined in the Translingual portion of Wiktionary.  Collect
        # morse code information under "morse_code".
        elif name in ("morse code for", "morse code of",
                      "morse code abbreviation",
                      "morse code prosign"):
            data_append(config, data, "morse_code", t_arg(config, t, 1))
        elif name in ("mul-semaphore-for", "mul-semaphore for",
                      "ja-semaphore for"):
            data_append(config, data, "semaphore", t_arg(config, t, 1))
        # Some glosses identify the word as a character.  If so, tag it as
        # "character".
        elif (name == "Latn-def" or re.search("-letter$", name)):
            data_append(config, data, "tags", "character")
        elif name in ("translation hub", "translation only"):
            data_append(config, data, "tags", "translation_hub")
        # There are various ways to specify that a word is a synonym or
        # alternative spelling/form of another word.  We record these all
        # under "alt_of".
        elif name in ("alternative form of", "alt form", "alt form of",
                      "alternative_form_of",
                      "alternative spelling of", "aspirate mutation of",
                      "alternate spelling of", "altspelling",
                      "pt-apocopic-verb",
                      "soft mutation of",
                      "hard mutation of", "mixed mutation of", "lenition of",
                      "alt form", "altform", "alt-form",
                      "apocopic form of", "altcaps",
                      "alternative name of",
                      "alternative capitalisation of", "alt case",
                      "alternative capitalization of", "alternate form of",
                      "Template:alternative case form of",
                      "alternative case form of", "alt-sp", "alt sp",
                      "alternative typography of",
                      "elongated form of", "alternative name of",
                      "city nickname", "Nom form of", "han tu form of",
                      "han form of",
                      "caret notation of", "syncopic form of",
                      "alternative term for", "altspell", "alter"):
            data_alt_of(config, data, t, ["alternative_spelling"])
        elif name in ("combining form of",):
            data_alt_of(config, data, t, ["combining_form"])
        elif name == "spelling of":
            data_alt_of(config, data, t, t_arg(config, t, 2).lower().split())
        elif name in ("honoraltcaps", "honor alt case"):
            data_alt_of(config, data, t, ["honorific"])
        elif name in ("standspell", "standard spelling of", "stand sp",
                      "standard form of"):
            data_alt_of(config, data, t, ["standard_spelling"])
        elif name in ("synonyms", "synonym of", "syonyms",
                      "syn of", "altname", "synonym"):
            data_alt_of(config, data, t, ["synonym"])
        elif name in ("Br. English form of",):
            data_alt_of(config, data, t, ["UK"])
        # Some words are marked as being pronunciation spellings, or
        # "eye dialect" words.  Record the canonical word under "alt_of" and
        # add a "spoken" tag.
        elif name in ("eye dialect of", "eye dialect", "eye-dialect of",
                      "pronunciation spelling",
                      "pronunciation respelling of",
                      "pronunciation spelling of"):
            data_alt_of(config, data, t, ["spoken"])
        # If the gloss is marked as an obsolete/archaic spelling,
        # include "alt_of" and tag the gloss as "archaic".
        elif name in ("obsolete spelling of", "obsolete form of", "obs sp",
                      "obs form", "obsolete typography of", "obsolete sp",
                      "medieval spelling of"):
            data_alt_of(config, data, t, ["archaic", "obsolete"])
        elif name in ("superseded spelling of", "former name of", "sup sp",
                      "archaic spelling of", "dated spelling of",
                      "archaic form of", "dated form of"):
            data_alt_of(config, data, t, ["archaic"])
        # If the gloss is marked as an informal spqlling, include "alt_of" and
        # tag it as "colloquial".
        elif name in ("informal spelling of", "informal form of"):
            data_alt_of(config, data, t, ["informal"])
        # If the gloss is marked as an euphemistic spelling, include "alt_of"
        # and tag it as "euphemism".
        elif name in ("euphemistic form of", "euphemistic spelling of"):
            data_alt_of(config, data, t, ["euphemism"])
        # Eclipsis refers to mutation of initial sound, e.g., in Irish
        elif name == "eclipsis of":
            data_alt_of(config, data, t, ["eclipsis"])
        # Singulative form is an individuation of a collective or mass noun
        elif name == "singulative of":
            data_alt_of(config, data, t, ["singulative"])
        # Lenition refers to a weakening of the articularion of a consonant
        elif name in ("lenition of", "ga-lenition of"):
            data_alt_of(config, data, t, ["lenition"])
        # Prothesis is prepending of phonemes without changing morphology
        elif name in ("t-prothesis of", "h-prothesis of"):
            data_alt_of(config, data, t, ["prothesis"])
        # If the gloss is indicated as a misspelling or non-standard spelling
        # of another word, include "alt_of" and tag it as a "misspelling".
        elif name in ("deliberate misspelling of", "misconstruction of",
                      "misspelling of", "common misspelling of",
                      "misspelling form of", "missp",
                      "de-umlautless spelling of"):
            data_alt_of(config, data, t, ["misspelling"])
        elif name in ("nonstandard form of", "nonstandard spelling of"):
            data_alt_of(config, data, t, ["nonstandard"])
        # If the gloss is indicated as a rare form of another word, include
        # "alt_of" and tag it as "rare".
        elif name in ("rare form of", "rare spelling of",
                      "rareform", "uncommon spelling of",
                      "uncommon form of", "rare sp"):
            data_alt_of(config, data, t, ["rare"])
        # If the gloss is marked as an abbreviation of another term
        # (there are many ways to do this!), include "alt_of" and tag it
        # as an "abbreviation".  Also, if it includes wikipedia links,
        # include those under "wikipedia".
        elif name in ("initialism of", "init of",
                      "abbreviation of", "abbr of", "short for",
                      "acronym of", "clipping of", "clip", "clipping",
                      "clip of", "aphetic form of",
                      "short form of", "ellipsis of", "ellipse of",
                      "short of", "abbreviation", "abb", "contraction of"):
            x = t_arg(config, t, 2)
            if x.startswith("w:"):
                x = x[2:]
                if use_text:  # Skip wikipedia links in examples
                    data_append(config, data, "wikipedia", x)
            data_append(config, data, "alt_of", x)
            data_append(config, data, "tags", "abbreviation")
        elif name in ("only used in", "only in"):
            # This appears to be used in "man" for "man enough"
            data_append(config, data, "only_in", t_arg(config, t, 2))
        # This tag indicates the word is an inflection of another word, but
        # in a complicated way that we won't try to parse here.  We include
        # the information under "complex_inflection_of".
        elif name in ("inflection of", "infl of"):
            data_append(config, data, "complex_inflection_of",
                        t_dict(config, t))
        # There are many templates that indicate a word is an inflected form
        # of another word.  Such tags are handled here.  For all of them,
        # we include the base form under "inflection_of" and add tags to
        # indicate the type of inflection/derivation.
        elif name in ("inflected form of", "form of"):
            # At least for "form of", tags here is plain wrong for most
            # cases, while in some cases it may be appropriate.
            form = t_arg(config, t, 2)
            term = t_arg(config, t, 3)
            if form in form_of_map:
                dt = form_of_map[form]
                if dt.get("error"):
                    config.error("Potentially erroneus word form specifier: "
                                 "{!r}".format(form))
                if "alt_of" in dt:
                    data_extend(config, data, "tags", dt["alt_of"])
                    data_append(config, data, "alt_of", term)
                elif "inflection_of" in dt:
                    data_extend(config, data, "tags", dt["inflection_of"])
                    data_append(config, data, "inflection_of", term)
                else:
                    config.debug("Internal unimplemented word form specifier: "
                                 "{!r}".format(form))
            else:
                config.error("Unrecognized work form specifier: {!r}"
                             "".format(form))
        elif name == "native or resident of":
            data_inflection_of(config, data, t, ["person"])
        elif name == "agent noun of":
            data_inflection_of(config, data, t, ["agent"])
        elif name == "nominalization of":
            data_inflection_of(config, data, t, ["nominalization"])
        elif name == "feminine plural of":
            data_inflection_of(config, data, t, ["feminine", "plural"])
        elif name == "feminine singular of":
            data_inflection_of(config, data, t, ["feminine", "singular"])
        elif name == "masculine plural of":
            data_inflection_of(config, data, t, ["masculine", "plural"])
        elif name == "neuter plural of":
            data_inflection_of(config, data, t, ["neuter", "plural"])
        elif name in ("feminine noun of", "feminine equivalent of"):
            data_inflection_of(config, data, t, ["feminine"])
        elif name in ("verbal noun of", "ar-verbal noun of"):
            data_inflection_of(config, data, t, ["verbal noun"])
        elif name == "abstract noun of":
            data_inflection_of(config, data, t, ["abstract noun"])
        elif name == "masculine singular of":
            data_inflection_of(config, data, t, ["masculine", "singular"])
        elif name == "neuter singular of":
            data_inflection_of(config, data, t, ["neuter", "singular"])
        elif name == "feminine of":
            data_inflection_of(config, data, t, ["feminine"])
        elif name in ("masculine of", "masculine noun of"):
            data_inflection_of(config, data, t, ["masculine"])
        elif name == "participle of":
            data_inflection_of(config, data, t, ["participle"])
        elif name in ("present participle of", "gerund of",
                      "en-ing form of"):
            data_inflection_of(config, data, t, ["participle", "present"])
        elif name in ("present tense of", "present of"):
            data_inflection_of(config, data, t, ["present"])
        elif name in ("past of", "past sense of", "en-past of",
                      "past tense of", "en-simple past of"):
            data_inflection_of(config, data, t, ["past"])
        elif name == "passive of":
            data_inflection_of(config, data, t, ["passive"])
        elif name == "past participle of":
            data_inflection_of(config, data, t, ["past", "participle"])
        elif name == "feminine plural past participle of":
            data_inflection_of(config, data, t,
                               ["feminine", "plural", "past", "participle"])
        elif name == "feminine singular past participle of":
            data_inflection_of(config, data, t,
                               ["feminine", "singular", "past", "participle"])
        elif name == "masculine plural past participle of":
            data_inflection_of(config, data, t,
                               ["masculine", "plural", "past", "participle"])
        elif name == "masculine singular past participle of":
            data_inflection_of(config, data, t,
                               ["masculine", "singular", "past", "participle"])
        elif name == "perfective form of":
            data_inflection_of(config, data, t, ["perfective"])
        elif name in ("en-third-person singular of",
                      "en-third person singular of"):
            data_inflection_of(config, data, t,
                               ["present", "singular", "third-person"])
        elif name == "imperative of":
            data_inflection_of(config, data, t, ["imperative"])
        elif name == "nominative plural of":
            data_inflection_of(config, data, t, ["plural", "nominative"])
        elif name in ("alternative plural of", "plural of",
                      "en-plural noun",
                      "plural form of"):
            data_inflection_of(config, data, t, ["plural"])
        elif name in ("singular of", "singular form of"):
            data_inflection_of(config, data, t, ["singular"])
        elif name in ("diminutive of", "dim of"):
            data_inflection_of(config, data, t, ["diminutive"])
        elif name == "endearing form of":
            data_inflection_of(config, data, t, ["endearing"])
        elif name == "vocative plural of":
            data_inflection_of(config, data, t, ["vocative", "plural"])
        elif name == "vocative singular of":
            data_inflection_of(config, data, t, ["vocative", "plural"])
        elif name == "imperfective form of":
            data_inflection_of(config, data, t, ["imperfective"])
        elif name == "perfective form of":
            data_inflection_of(config, data, t, ["perfective"])
        elif name in ("comparative of", "en-comparative of"):
            data_inflection_of(config, data, t, ["comparative"])
        elif name in ("superlative of", "en-superlative of"):
            data_inflection_of(config, data, t, ["superlative"])
        elif name in ("attributive of", "attributive form of"):
            data_inflection_of(config, data, t, ["attributive"])
        elif name == "accusative singular of":
            data_inflection_of(config, data, t, ["accusative", "singular"])
        elif name == "accusative plural of":
            data_inflection_of(config, data, t, ["accusative", "plural"])
        elif name == "genitive of":
            data_inflection_of(config, data, t, ["genitive"])
        elif name == "genitive singular of":
            data_inflection_of(config, data, t, ["genitive", "singular"])
        elif name == "genitive plural of":
            data_inflection_of(config, data, t, ["genitive", "plural"])
        elif name == "dative plural of":
            data_inflection_of(config, data, t, ["dative", "plural"])
        elif name == "dative of":
            data_inflection_of(config, data, t, ["dative"])
        elif name == "dative singular of":
            data_inflection_of(config, data, t, ["dative", "singular"])
        elif name == "female equivalent of":
            data_inflection_of(config, data, t, ["feminine"])
        elif name == "augmentative of":
            data_inflection_of(config, data, t, ["augmentative"])
        elif name == "reflexive of":
            data_inflection_of(config, data, t, ["reflexive"])
        elif name == "en-irregular plural of":
            data_inflection_of(config, data, t, ["plural", "irregular"])
        elif name == "en-archaic second-person singular of":
            data_inflection_of(config, data, t,
                               ["archaic", "singular", "present",
                                "second-person"])
        elif name == "en-archaic second-person singular past of":
            data_inflection_of(config, data, t,
                               ["archaic", "singular", "past", "second-person"])
        elif name == "second-person singular of":
            data_inflection_of(config, data, t,
                               ["singular", "present", "second-person"])
        elif name == "topic form":
            data_inflection_of(config, data, t, ["topic"])
        elif name in ("en-second-person singular past of",
                      "en-second person singular past of",
                      "second-person singular past of",
                      "second person singular past of"):
            data_inflection_of(config, data, t,
                               ["singular", "past", "second-person"])
        elif name == "en-archaic third-person singular of":
            data_inflection_of(config, data, t,
                               ["archaic", "singular", "third-person"])
        elif name == "pejorative of":
            data_inflection_of(config, data, t, ["pejorative"])
        elif name == "noun form of":
            data_append(config, data, "inflection_of", t_arg(config, t, 2))
            for x in t_vec(config, t)[2:]:
                if not x:
                    continue
                if x in ("acc", "accusative"):
                    data_append(config, data, "tags", "accusative")
                elif x in ("gen", "genitive"):
                    data_append(config, data, "tags", "genitive")
                elif x in ("dat", "dative"):
                    data_append(config, data, "tags", "dative")
                elif x in ("nom", "nominative"):
                    data_append(config, data, "tags", "nominative")
                elif x in ("s", "sg", "singular"):
                    data_append(config, data, "tags", "singular")
                elif x in ("p", "pl", "plural"):
                    data_append(config, data, "tags", "plural")
                elif x in ("def", "definite"):
                    data_append(config, data, "tags", "definite")
                elif x in ("loc", "locative"):
                    data_append(config, data, "tags", "locative")
                elif x in ("voc", "vocative"):
                    data_append(config, data, "tags", "vocative")
                elif x in ("ins", "instrumental"):
                    data_append(config, data, "tags", "instrumental")
                elif x in ("ess", "essive"):
                    data_append(config, data, "tags", "essive")
                elif x in ("ela", "elative"):
                    data_append(config, data, "tags", "elative")
                elif x in ("ade", "adessive"):
                    data_append(config, data, "tags", "adessive")
                elif x in ("ine", "inessive"):
                    data_append(config, data, "tags", "inessive")
                elif x in ("par", "partitive"):
                    data_append(config, data, "tags", "partitive")
                elif x in ("acc//dat"):
                    data_extend(config, data, "tags", ["accusative", "dative"])
                elif x in ("nom//acc"):
                    data_extend(config, data, "tags",
                                ["accusative", "nominative"])
                else:
                    config.unknown_value(t, x)
        elif name == "+preo":
            data_append(config, data, "object_preposition", t_arg(config, t, 2))
        elif name in ("+obj", "+OBJ", "construed with"):
            if t_arg(config, t, "lang"):
                v = t_arg(config, t, 1)
            else:
                v = t_arg(config, t, 2)
            if v in ("dat", "dative"):
                data_append(config, data, "tags", "object_dative")
            elif v in ("acc", "accusative"):
                data_append(config, data, "tags", "object_accusative")
            elif v in ("ela", "elative"):
                data_append(config, data, "tags", "object_elative")
            elif v in ("abl", "ablative"):
                data_append(config, data, "tags", "object_ablative")
            elif v in ("gen", "genitive"):
                data_append(config, data, "tags", "object_genitive")
            elif v in ("nom", "nominative"):
                data_append(config, data, "tags", "object_nominative")
            elif v in ("ins", "instructive"):
                data_append(config, data, "tags", "object_instructive")
            elif v in ("obl", "oblique"):
                data_append(config, data, "tags", "object_oblique")
            elif v in ("loc", "locative"):
                data_append(config, data, "tags", "object_locative")
            elif v in ("participial",):
                data_append(config, data, "tags", "object_participial")
            elif v in ("subj", "subjunctive"):
                # (??? not really sure if subjunctive)
                data_append(config, data, "tags", "object_subjunctive")
            elif v == "with":
                data_append(config, data, "object_preposition", "with")
            elif v == "avec":
                data_append(config, data, "object_preposition", "avec")
            elif not v:
                config.warning("empty/missing object construction argument "
                               "in {}".format(t))
            else:
                config.unknown_value(t, v)
        elif name == "verb form of":
            verb_form_map_fn(config, data, name, t, generic_verb_form_map)
        # Handle some Spanish-specific tags
        elif name == "es-adj form of":
            vec = t_vec(config, t)
            data_append(config, data, "inflection_of", vec[0])
            for x in vec[1:]:
                if x == "f":
                    data_append(config, data, "tags", "feminine")
                elif x == "m":
                    data_append(config, data, "tags", "masculine")
                elif x == "sg":
                    data_append(config, data, "tags", "singular")
                elif x == "pl":
                    data_append(config, data, "tags", "plural")
                else:
                    config.unknown_value(t, x)
        elif name == "es-compound of":
            stem = t_arg(config, t, 1)
            inf_ending = t_arg(config, t, 2)
            infinitive = stem + inf_ending
            form = t_arg(config, t, 3) or infinitive
            pron1 = t_arg(config, t, 4)
            pron2 = t_arg(config, t, 5)
            mood = t_arg(config, t, "mood")
            person = t_arg(config, t, "person")
            data_append(config, data, "inflection_of", infinitive)
            data_append(config, data, "tags", "pron-compound")
            data_append(config, data, "pron1", pron1)
            if pron2:
                data_append(config, data, "pron2", pron2)
            if mood in ("inf", "infinitive"):
                data_append(config, data, "tags", "infinitive")
            elif mood in ("part", "participle", "adv", "adverbial", "ger",
                          "gedund", "gerundive", "gerundio",
                          "present participle", "present-participle"):
                data_append(config, data, "tags", "participle")
            elif mood in ("imp", "imperative"):
                data_append(config, data, "tags", "imperative")
            elif mood in ("pret", "preterite"):
                data_append(config, data, "tags", "preterite")
            elif mood in ("pres", "present"):
                data_append(config, data, "tags", "present")
            elif mood in ("refl", "reflexive"):
                data_append(config, data, "tags", "reflexive")
            elif mood in ("impf", "imperfect"):
                data_append(config, data, "tags", "imperfect")
            elif mood == "subjunctive":
                data_append(config, data, "tags", "subjunctive")
            else:
                config.unknown_value(t, mood)
            if person in ("tú", "tu", "inf"):
                data_extend(config, data, "tags",
                            ["second-person", "singular", "informal"])
            elif person in ("vosotros", "v", "inf-pl"):
                data_extend(config, data, "tags",
                            ["second-person", "plural", "informal"])
            elif person in ("nosotros",):
                data_extend(config, data, "tags", ["third-person"])
            elif person in ("usted", "ud", "f"):
                data_extend(config, data, "tags",
                            ["second-person", "singular", "formal"])
            elif person in ("ustedes", "uds", "uds.", "f-pl"):
                data_extend(config, data, "tags",
                            ["second-person", "plural", "formal"])
            elif person == "vos":
                data_extend(config, data, "tags",
                            ["first-person", "singular", "nominative"])
            elif person == "él":
                data_extend(config, data, "tags",
                            ["third-person", "singular", "masculine"])
            elif person == "s":
                data_extend(config, data, "tags", ["singular"])
            elif person == "me":
                data_extend(config, data, "tags",
                            ["first-person", "singular", "accusative"])
            elif person == "se":
                data_extend(config, data, "tags",
                            ["first-person", "singular", "reflexive"])
            elif person == "le":
                data_extend(config, data, "tags",
                            ["third-person", "singular", "dative"])
            elif person:
                config.unknown_value(t, person)
        elif name == "es-verb form of":
            verb_form_map_fn(config, data, name, t, es_verb_form_map)
        elif name == "es-demonstrative-accent-usage":
            data_append(config, data, "tags", "demonstrative-accent")
        # Handle some Italian-specific tags
        elif name == "it-adj form of":
            data_append(config, data, "inflection_of", t_arg(config, t, 1))
            for x in t_vec(config, t)[1:]:
                if x in ("f", "feminine"):
                    data_append(config, data, "tags", "feminine")
                elif x in ("m", "male"):
                    data_append(config, data, "tags", "masculine")
                elif x in ("s", "sg", "singular"):
                    data_append(config, data, "tags", "singular")
                elif x in ("p", "pl", "plural"):
                    data_append(config, data, "tags", "plural")
                else:
                    config.unknown_value(t, x)
        # Handle some Dutch-specific tags
        elif name == "nl-verb form of":
            verb_form_map_fn(config, data, name, t, nl_verb_form_map)
        elif name == "nl-noun form of":
            form = t_arg(config, t, 1)
            base = t_arg(config, t, 2)
            data_append(config, data, "inflection_of", base)
            if form == "sg":
                data_append(config, data, "tags", "singular")
            elif form == "pl":
                data_append(config, data, "tags", "plural")
            elif form == "dim":
                data_append(config, data, "tags", "diminutive")
            elif form == "gen":
                data_append(config, data, "tags", "genitive")
            elif form == "dat":
                data_append(config, data, "tags", "dative")
            elif form == "acc":
                data_append(config, data, "tags", "accusative")
            else:
                config.unknown_value(t, form)
        elif name == "nl-adj form of":
            form = t_arg(config, t, 1)
            base = t_arg(config, t, 2)
            data_append(config, data, "inflection_of", base)
            if form == "part":
                data_append(config, data, "tags", "partitive")
            elif form == "comp":
                data_append(config, data, "tags", "comparative")
            elif form == "sup":
                data_append(config, data, "tags", "superlative")
            elif form == "infl":
                pass  # XXX does this have special meaning?
            else:
                config.unknown_value(t, form)
        elif name == "nl-pronadv of":
            # XXX two arguments that the word is made of?
            data_append(config, data, "tags", "pronadv")
        # Handle some Swedish-specific word form taggings
        elif name == "sv-noun-form-def":
            data_inflection_of(config, data, t, ["definite"])
        elif name == "definite singular of":
            data_inflection_of(config, data, t, ["definite", "singular"])
        elif name == "definite plural of":
            data_inflection_of(config, data, t, ["definite", "plural"])
        elif name == "indefinite plural of":
            data_inflection_of(config, data, t, ["indefinite", "plural"])
        elif name == "sv-noun-form-def-pl":
            data_inflection_of(config, data, t, ["definite", "plural"])
        elif name == "sv-noun-form-indef-pl":
            data_inflection_of(config, data, t, ["plural", "indefinite"])
        elif name == "sv-noun-form-indef-gen":
            data_inflection_of(config, data, t, ["genitive", "indefinite"])
        elif name == "sv-noun-form-indef-gen-pl":
            data_inflection_of(config, data, t,
                               ["genitive", "indefinite", "plural"])
        elif name == "sv-noun-form-def-gen-pl":
            data_inflection_of(config, data, t,
                               ["genitive", "definite", "plural"])
        elif name == "sv-proper-noun-gen":
            data_inflection_of(config, data, t, ["genitive"])
        elif name == "sv-noun-form-def-gen":
            data_inflection_of(config, data, t, ["genitive", "definite"])
        elif name == "sv-noun-form-abs-def+pl":
            data_inflection_of(config, data, t,
                               ["absolute", "definite", "plural"])
        elif name == "sv-noun-form-abs-pl":
            data_inflection_of(config, data, t, ["absolute", "plural"])
        elif name == "sv-adj-form-abs-def-m":
            data_inflection_of(config, data, t,
                               ["absolute", "definite", "masculine"])
        elif name == "sv-adj-form-abs-indef-n":
            data_inflection_of(config, data, t,
                               ["absolute", "indefinite", "neuter"])
        elif name == "sv-adj-form-abs-def+pl":
            data_inflection_of(config, data, t,
                               ["absolute", "definite", "plural"])
        elif name == "sv-adj-form-abs-pl":
            data_inflection_of(config, data, t, ["absolute", "plural"])
        elif name == "sv-adj-form-abs-def":
            data_inflection_of(config, data, t, ["absolute", "definite"])
        elif name in ("sv-adj-form-comp", "sv-adv-form-comp"):
            data_inflection_of(config, data, t, ["comparative"])
        elif name in ("sv-adj-form-sup", "sv-adv-form-sup"):
            data_inflection_of(config, data, t, ["superlative"])
        elif name == "sv-adj-form-sup-attr":
            data_inflection_of(config, data, t, ["superlative", "attributive"])
        elif name == "sv-adj-form-sup-attr-m":
            data_inflection_of(config, data, t,
                               ["superlative", "attributive", "masculine"])
        elif name in ("sv-adj-form-sup-pred", "superlative predicative of"):
            data_inflection_of(config, data, t, ["superlative", "predicative"])
        elif name == "sv-verb-form-pre":
            data_inflection_of(config, data, t, ["present"])
        elif name == "sv-verb-form-imp":
            data_inflection_of(config, data, t, ["imperative"])
        elif name == "sv-verb-form-past":
            data_inflection_of(config, data, t, ["past"])
        elif name in ("supine of", "sv-verb-form-sup"):
            data_inflection_of(config, data, t, ["supine"])
        elif name == "sv-verb-form-sup-pass":
            data_inflection_of(config, data, t, ["supine", "passive"])
        elif name == "sv-verb-form-subjunctive":
            data_inflection_of(config, data, t, ["subjunctive"])
        elif name == "sv-verb-form-inf-pass":
            data_inflection_of(config, data, t, ["infinitive", "passive"])
        elif name == "sv-verb-form-pre-pass":
            data_inflection_of(config, data, t, ["present", "passive"])
        elif name == "sv-verb-form-past-pass":
            data_inflection_of(config, data, t, ["past", "passive"])
        elif name == "sv-verb-form-prepart":
            data_inflection_of(config, data, t, ["participle", "present"])
        elif name == "sv-verb-form-pastpart":
            data_inflection_of(config, data, t, ["participle", "past"])
        # Handle some German-specific word form taggings
        elif name == "de-verb form of":
            verb_form_map_fn(config, data, name, t, de_verb_form_map)
        elif name == "de-zu-infinitive of":
            data_inflection_of(config, data, t, ["infinitive"])
        elif name == "de-superseded spelling of":
            data_append(config, data, "alt_of", t_arg(config, t, 1))
            data_append(config, data, "tags", "archaic")
        # Handle some Portuguese-specific tags
        elif name in ("pt-verb form of", "pt-verb-form-of"):
            data_inflection_of(config, data, t, [])
        elif name in ("pt-obsolete-hellenism", "pt-obsolete hellenism"):
            data_alt_of(config, data, t, ["archaic", "obsolete", "hellenism"])
        elif name in ("pt-superseded-silent-letter-1990",
                      "pt-superseded-hyphen",
                      "pt-superseded-paroxytone"):
            data_alt_of(config, data, t, ["archaic"])
        elif name in ("pt-obsolete-éia",
                      "pt-obsolete-ü",
                      "pt-obsolete-ôo",
                      "pt-obsolete-secondary-stress",
                      "pt-obsolete-differential-accent",
                      "pt-obsolete-silent-letter-1911"):
            data_alt_of(config, data, t, ["archaic", "obsolete"])
        elif name in ("pt-adj form of", "pt-adj-form-of"):
            data_append(config, data, "inflection_of", t_arg(config, t, 1))
            for x in t_vec(config, t)[1:]:
                if x in ("f", "female"):
                    data_append(config, data, "tags", "feminine")
                elif x in ("m", "male"):
                    data_append(config, data, "tags", "masculine")
                elif x in ("s", "sg", "singular"):
                    data_append(config, data, "tags", "singular")
                elif x in ("p", "pl", "plural"):
                    data_append(config, data, "tags", "plural")
                elif x in ("mf", "m-f", "f-m"):
                    pass
                elif x in ("dim", "diminutive"):
                    data_append(config, data, "tags", "diminutive")
                else:
                    config.unknown_value(t, x)
        elif name == "pt-noun form of":
            data_append(config, data, "inflection_of", t_arg(config, t, 1))
            for x in t_vec(config, t)[1:]:
                if x in ("onlym", "m", "male"):
                    data_append(config, data, "tags", "masculine")
                elif x in ("onlyf", "f", "female"):
                    data_append(config, data, "tags", "feminine")
                elif x in ("s", "sg", "singular"):
                    data_append(config, data, "tags", "singular")
                elif x in ("p", "pl", "plural"):
                    data_append(config, data, "tags", "plural")
                else:
                    config.unknown_value(t, x)
        # Handle some Japanese-specific tags
        elif name in ("ja-kyujitai spelling of", "ja-kyu sp"):
            data_append(config, data, "kyujitai_spelling", t_arg(config, t, 1))
        elif name == "ja-past of verb":
            data_inflection_of(config, data, t, ["past"])
        elif name == "ja-usex":
            pass
            #data_append(config, data, "examples", ("ja", t_arg(config, t, 1)))
        elif name == "ja-verb":
            for k, v in t_dict(config, t).items():
                data_append(config, data, "inflection_of", v)
        # Handle some Chinese-specific tags
        elif name in ("zh-old-name", "18th c."):
            data_append(config, data, "tags", "archaic")
        elif name in ("zh-alt-form", "zh-altname", "zh-alt-name",
                      "zh-alt-term", "zh-altterm"):
            data_append(config, data, "alt_of", t_arg(config, t, 1))
        elif name in ("zh-short", "zh-abbrev", "zh-short-comp", "mfe-short of"):
            data_append(config, data, "tags", "abbreviation")
            for x in t_vec(config, t):
                data_append(config, data, "alt_of", x)
        elif name == "zh-misspelling":
            data_append(config, data, "alt_of", t_arg(config, t, 1))
            data_append(config, data, "tags", "misspelling")
        elif name in ("zh-synonym", "zh-synonym of", "zh-syn-saurus"):
            data_append(config, data, "tags", "synonym")
            base = t_arg(config, t, 1)
            if base != config:
                data_append(config, data, "alt_of", base)
        elif name in ("zh-dial", "zh-erhua form of"):
            base = t_arg(config, t, 1)
            if base != config:
                data_append(config, data, "alt_of", base)
                data_append(config, data, "tags", "dialectical")
        elif name == "zh-mw":
            data_extend(config, data, "classifier", t_vec(config, t))
        elif name == "zh-classifier":
            data_append(config, data, "tags", "classifier")
        elif name == "zh-div":
            # Seems to indicate type of a place (town, etc) in some entries
            # but the value is in Chinese
            # XXX check this
            data_append(config, data, "hypernyms",
                        {"word": t_arg(config, t, 1)})
        elif name in ("ant", "antonym", "antonyms"):
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "antonyms", {"word": x})
        elif name in ("hypo", "hyponym", "hyponyms"):
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "hyponyms", {"word": x})
        elif name == "coordinate terms":
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "coordinate_terms", {"word": x})
        elif name in ("hyper", "hypernym", "hypernyms"):
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "hypernyms", {"word": x})
        elif name in ("mer", "meronym", "meronyms",):
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "meronyms", {"word": x})
        elif name in ("holonyms", "holonym"):
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "holonyms", {"word": x})
        elif name in ("troponyms", "troponym"):
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "troponyms", {"word": x})
        elif name in ("derived", "derived terms"):
            for x in t_vec(config, t)[1:]:
                data_append(config, data, "derived", {"word": x})
        elif name in ("†", "zh-obsolete"):
            data_extend(config, data, "tags", ["archaic", "obsolete"])
        # Handle some Finnish-specific tags
        elif name == "fi-infinitive of":
            data_inflection_of(config, data, t, ["infinitive"])
            if t_arg(config, t, "t"):
                data_append(config, data, "tags",
                            "infinitive-" + t_arg(config, t, "t"))
        elif name == "fi-participle of":
            data_inflection_of(config, data, t, ["participle"])
            if t_arg(config, t, "t"):
                data_append(config, data, "tags",
                            "participle-" + t_arg(config, t, "t"))
        elif name == "fi-verb form of":
            data_append(config, data, "inflection_of", t_arg(config, t, 1))
            mapping = {"1s": ["first-person", "singular"],
                       "2s": ["second-person", "singular"],
                       "3s": ["third-person", "singular"],
                       "1p": ["first-person", "plural"],
                       "2p": ["second-person", "plural"],
                       "3p": ["third-person", "plural"],
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
                v = t_arg(config, t, k)
                if v in mapping:
                    v = mapping[v]
                else:
                    config.unknown_value(t, v)
                    v = [v]
                data_extend(config, data, "tags", v)
        elif name in ("fi-form of", "conjugation of"):
            data_append(config, data, "inflection_of", t_arg(config, t, 1))
            for k in ("suffix", "suffix2", "suffix3"):
                suffix = t_arg(config, t, k)
                if suffix:
                    data_append(config, data, "suffix", suffix)
            for k in t.arguments:
                k = k.name.strip()
                if k in ("1", "2", "3", "suffix", "suffix2", "suffix3",
                         "c", "n", "type", "lang"):
                    continue
                v = t_arg(config, t, k)
                if not v or v == "-":
                    continue
                if v in ("first-person", "first person", "1p"):
                    v = "first-person"
                elif v in ("second-person", "second person", "2p"):
                    v = "second-person"
                elif v in ("third-person", "third person", "3p"):
                    v = "third-person"
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
                                 "first-person",
                                 "second-person",
                                 "third-person",
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
                        config.unknown_value(t, v)
                if v in ("singular and plural", "singular or plural"):
                    data_append(config, data, "tags", "singular")
                    data_append(config, data, "tags", "plural")
                elif v == "first-person singular":
                    data_append(config, data, "tags", "singular")
                    data_append(config, data, "tags", "first-person")
                elif v == "first-person plural":
                    data_append(config, data, "tags", "plural")
                    data_append(config, data, "tags", "first-person")
                elif v == "second-person singular":
                    data_append(config, data, "tags", "singular")
                    data_append(config, data, "tags", "second-person")
                elif v == "second-person plural":
                    data_append(config, data, "tags", "plural")
                    data_append(config, data, "tags", "second-person")
                elif v == "third-person singular":
                    data_append(config, data, "tags", "singular")
                    data_append(config, data, "tags", "third-person")
                elif v == "third-person plural":
                    data_append(config, data, "tags", "plural")
                    data_append(config, data, "tags", "third-person")
                elif v == "first, second, and third person":
                    pass
                elif v == "present connegative":
                    data_append(config, data, "tags", "present")
                    data_append(config, data, "tags", "connegative")
                elif v == "indicative connegative":
                    data_append(config, data, "tags", "indicative")
                    data_append(config, data, "tags", "connegative")
                elif v == "potential present connegative":
                    data_append(config, data, "tags", "potential")
                    data_append(config, data, "tags", "connegative")
                elif v == "potential present":
                    data_append(config, data, "tags", "potential")
                elif v == "conditional present":
                    data_append(config, data, "tags", "conditional")
                elif v == "indicative present":
                    data_append(config, data, "tags", "present")
                elif v == "indicative past":
                    data_append(config, data, "tags", "past")
                else:
                    data_append(config, data, "tags", v)
        # Various words are marked as place names.  Tag such words as a
        # "place", by the place type, and add a link under "holonyms" if what
        # the place is part of has been specified.
        elif name == "place":
            data_append(config, data, "tags", "place")
            transl = t_arg(config, t, "t")
            if transl:
                data_append(config, data, "alt_of", transl)
            vec = t_vec(config, t)
            if len(vec) < 2:
                config.unknown_value(t, "TOO FEW ARGS")
                continue
            for x in vec[1].split("/"):
                data_append(config, data, "tags", x)
                data_append(config, data, "hypernyms", {"word": x})
            # XXX many templates have non-first arguments not containing /
            # that are a definition/gloss, and some have def=
            for x in vec[2:]:
                if not x:
                    continue
                idx = x.find("/")
                if idx >= 0:
                    prefix = x[:idx]
                    if prefix in place_prefixes:
                        kind = place_prefixes[prefix]
                        v = x[idx + 1:]
                        m = re.match(langtag_colon_re, v)
                        if m:
                            v = v[m.end():]
                        if v.find(":") >= 0:
                            config.unknown_value(t, x)
                        data_append(config, data, "holonyms",
                                    {"word": v,
                                     "type": kind})
                    else:
                        config.unknown_value(t, x)
                else:
                    data_append(config, data, "holonyms", {"word": x})
        # US state names seem to have a special tagging as such.  We tag them
        # as places, indicate that they are a part of the Unites States, and
        # are places of type "state".
        elif name == "USstate":
            data_append(config, data, "tags", "place")
            data_append(config, data, "holonyms", "United States")
            data_append(config, data, "place", {"type": "state",
                                        "english": [word]})
        # Brazilian states and state capitals seem to use their own tagging.
        # Collect this information in tags and links.
        elif name == "place:Brazil/state":
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "province")
            capital = t_arg(config, t, "capital")
            if capital:
                data_append(config, data, "meronyms", {"word": capital,
                                               "type": "city"})
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})
        elif name in ("place:Brazil/capital",):
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "city")
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})
        elif name in ("place:Brazil/state capital",
                      "place:state capital of Brazil"):
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "city")
            state = t_arg(config, t, "state")
            if state:
                data_append(config, data, "holonyms", {"word": state,
                                               "type": "province"})
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})
        elif name in ("place:Brazil/municipality",
                      "place:municipality of Brazil"):
            data_append(config, data, "tags", "place")
            data_append(config, data, "tags", "municipality")
            if state:
                data_append(config, data, "holonyms", {"word": state,
                                               "type": "province"})
            data_append(config, data, "holonyms", {"word": "Brazil",
                                           "type": "country"})
        # Skip various templates in this processing.  We silence warnings
        # about unhandled tags for these.  (Many of them are handled
        # elsewhere.)
        elif name in ("audio", "audio-pron",  #XXX audio seems more common, CHK
                      "IPA", "ipa", "l", "link", "l-self", "m", "m+",
                      "zh-m", "zh-l", "ja-l", "ja-def", "sumti", "ko-l", "vi-l",
                      "alter", "ISBN", "syn", "ISSN", "gbooks", "OCLC",
                      "hyph", "hyphenation", "ja-r", "ja-l", "l/ja", "l-ja",
                      "ja-r/args", "th-l", "ja-r/multi",
                      "lj", "c.", "ca.", "a.", "CURRENTDAY", "CURRENTMONTHNAME",
                      "CURRENTYEAR", "...", "…", "mdash", "SIC", "LCC",
                      "homophones", "wsource", "nobr", "NNBS", "@", "CE", "BC",
                      "pinyin reading of", "enPR", "J2G", "C.E.", "BCE", "A.D.",
                      "B.C.E.", "B.C.", "AD", "C.", "S", "nb...", "..", "sic",
                      "mul-kangxi radical-def", "speciesabbrev", "'", "smc",
                      "mul-shuowen radical-def",
                      "mul-kanadef",
                      "mul-domino def",
                      "mul-cjk stroke-def", "ryu-def", "ja-def",
                      "ja-kanjitab", "ja-kana-def",
                      "ja-see",
                      "Han char", "zh-only", "sqbrace",
                      "Brai-def",
                      "abbreviated", "ruby", "hanja form of",
                      "transterm",
                      "phrasal verb", "compound",
                      "quote", "quote-booken", "quote-jounalen", "quotebook",
                      "quote-hansard", "quote-video game",
                      "quote-us-patent", "quote-wikipedia",
                      "quote web", "quote-web", "quote-webpage",
                      "quote-article", "cite-av",
                      "glossary", "The Last Man",
                      "tpi-cite-bible",
                      "small", "bottom5", "source",
                      "glink", "projectlink", "maintenance line", "JSTOR",
                      "gloss", "gl", "clear", "abbr", "nc",
                      "upright", "tea room sense", "1", "0",
                      "wCharles Molloy Westmacott",
                      "source Louis-Ferdinand Céline",
                      "presidential nomics",
                      "video frames",
                      "w:William Logan (poet)", "w:",
                      "blockquote", "comment",
                      "non-gloss definition", "n-g", "ngd", "non-gloss"):
            continue
        # There are whole patterns of templates that we don't want warnings for.
        elif re.search(r"IPA|^(RQ:|Template:RQ:|R:)|"
                       r"-romanization$|-romanji$|romanization of$",
                       name):
            continue
        elif name == "hot sense":
            data_append(config, data, "tags", "hot_sense")
        # Otherwise warn about an unhandled template.  It is normal to get
        # a few of these warnings whenever this is run; such templates may
        # later be added to the silencing list above or proper handling may
        # be added for them.  For a few templates, they have intentionally
        # not yet been silenced because they could be useful but their use is
        # still too rare to bother collecting them.
        elif (name not in ignored_templates and name not in default_tags and
              name not in default_parenthesize_tags):
            m = re.match(r"^table:([^/]*)(/[a-z0-9]+)?$", name)
            if m:
                category = m.group(1)
                data_append(config, data, "topics", {"word": category})
                continue
            config.unrecognized_template(t, "inside gloss")

    # Various fields should only contain strings.  Check that they do
    # (helps find bugs fast).  Also remove any duplicates from the lists and
    # sort them into ascending order for easier reading.
    for k in ("tags", "glosses", "alt_of",
              "inflection_of", "color", "wikidata"):
        if k not in data:
            continue
        for x in data[k]:
            if not isinstance(x, str):
                config.debug("produced incorrect non-string data for {}: {}"
                             "".format(k, data))

    return data


def parse_preamble(config, data, pos_sectitle, text, p):
    """Parse the head template for the word (part-of-speech) and other
    stuff that affects all senses.  Then parse the word sense defintions."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(pos_sectitle, str)
    assert isinstance(text, str)

    heads = []
    add_tags = []
    for t in p.templates:
        name = t.name.strip()
        if re.search("plural", name):
            add_tags.append("plural")
        # Note: want code below in addition to code above.
        # Record the head template fo the word entry. This often contains
        # important inflection information (e.g., comparatives and verb
        # forms).
        #
        # Also Warn about potentially incorrect templates for the
        # part-of-speech (common error in Wiktionary that should be corrected
        # there).
        m = re.search(r"^(head|Han char)$|" +
                      r"^(" + "|".join(languages_by_code.keys()) + r")" +
                      r"-(plural-noun|plural noun|noun|verb|adj|adv|name|proper-noun|proper noun|prop|pron|phrase|decl noun|decl-noun|prefix|clitic|number|ordinal|syllable|suffix|affix|pos|gerund|combining form|combining-form|converb|cont|con|interj|det|part|part-form|postp|prep)(-|$)", name)
        if m:
            tagpos = m.group(1)
            if tagpos == "head":
                tagpos = t_arg(config, t, 2)
                if tagpos in head_pos_map:
                    tagpos = head_pos_map[tagpos]
                else:
                    config.unknown_value(t, tagpos)
            elif tagpos == "Han char":
                tagpos = "character"
            else:
                tagpos = m.group(3)
            # XXX some of them need to be mapped, e.g., clitic, ordinal
            if ((tagpos not in template_allowed_pos_map or
                 config.pos not in template_allowed_pos_map[tagpos]) and
                m.group(0) != "head" and
                tagpos != config.pos):
                config.warning("suspect part-of-speech: {} under {}"
                               "".format(t, pos_sectitle))
            # Record the head template under "heads".
            data_append(config, data, "heads", t_dict(config, t))
        # If hyphenation information has been provided, record it.
        elif name in ("hyphenation", "hyph"):
            data_append(config, data, "hyphenation", t_vec(config, t))
        # If pinyin reading has been provided, record it (this is reading
        # of a Chinese word in romanized forms, i.e., western characters).
        elif name == "pinyin reading of":
            data_extend(config, data, "pinyin", t_vec(config, t))
        # XXX what other potentially useful information might be available?

    # Parse word senses for the part-of-speech.
    for node in p.lists():
        for index, item in enumerate(node.items):
            txt = str(item)
            if txt.startswith("*::"):
                continue  # Possibly a bug in wikitextparser
            sense = {}
            parse_sense(config, sense, txt, True)
            for node2 in node.sublists(index):
                for item2 in node2.items:
                    parse_sense(config, sense, str(item2), False)
                for node3 in node2.sublists():
                    for item3 in node3.items:
                        parse_sense(config, sense, str(item3), False)
            for tag in add_tags:
                if tag not in sense.get("tags", ()):
                    data_append(config, sense, "tags", "plural")
            data_append(config, data, "senses", sense)

    # XXX there might be word senses encoded in other ways, without using
    # a list for them.  Do some tests to find out how common this is.
    if not data.get("senses"):
        if config.pos not in ("character", "symbol", "letter"):
            config.warning("no senses found in section {}"
                           "".format(pos_sectitle))


def parse_pronunciation(config, data, text, p):
    """Extracts pronunciation information for the word."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(text, str)

    def parse_variant(text):
        variant = {}
        sense = None

        p = wikitextparser.parse(text)
        for t in p.templates:
            name = t.name.strip()
            # Silently ignore templates that we don't care about.
            if name == "sense":
                # Some words, like "house" (English) have a two-level structure
                # with different pronunciations for verbs and nouns, with
                # {{sense|...}} used to distinguish them
                sense = t_arg(config, t, 1)
            # Pronunciation may be qualified by
            # accent/dialect/variant.  These are recorded under
            # "tags".  See
            # https://en.wiktionary.org/wiki/Module:accent_qualifier/data
            elif name in ("a", "accent"):
                data_extend(config, variant, "accent", clean_quals(config, t_vec(config, t)))
            # These other qualifiers and context markers may be used for
            # similar things, but their values are less well defined.
            elif name in ("qual", "qualifier", "q", "qf"):
                data_extend(config, variant, "tags", t_vec(config, t))
            elif name in ("lb", "context",
                          "term-context", "tcx", "term-label", "tlb", "i"):
                data_extend(config, variant, "tags", clean_quals(config, t_vec(config, t)[1:]))
            # Various tags seem to indicate topical categories that the
            # word belongs to.  These are added under "topics".
            elif name in ("topics", "categorize", "catlangname", "c", "C",
                          "cln",
                          "top", "categorise", "catlangcode"):
                for topic in t_vec(config, t)[1:]:
                    data_append(config, data, "topics", {"word": topic})
            # Extact IPA pronunciation specification under "ipa".
            elif name in ("IPA", "ipa"):
                vec = t_vec(config, t)
                for ipa in vec[1:]:
                    data_append(config, variant, "ipa", ipa)
            elif name in ("IPAchar", "audio-IPA"):
                # These are used in text to format as IPA characters
                # or to specify inline audio
                pass
            # Extract special variants of the IPA template.  Store these as
            # dictionaries under "special_ipa".
            elif re.search("IPA", name):
                data_append(config, variant, "special_ipa",
                            t_dict(config, t))
            # If English pronunciation (enPR) has been specified, record them
            # under "enpr".
            elif name == "enPR":
                data_append(config, variant, "enpr", t_arg(config, t, 1))
            # There are also some other forms of pronunciation information that
            # we collect; it is not yet clear what all these mean.
            elif name in ("it-stress",):
                data_append(config, variant, "stress", t_arg(config, t, 1))
            elif name == "PIE root":
                data_append(config, variant, "pie_root", t_arg(config, t, 2))
            # If an audio file has been specified for the word,
            # collect those under "audios".
            elif name in ("audio", "audio-pron"):
                data_append(config, variant, "audios",
                            (t_arg(config, t, "lang"),
                             t_arg(config, t, 1),
                             t_arg(config, t, 2)))
            # If homophones have been specified, collect those under
            # "homophones".
            elif name in ("homophones", "homophone"):
                data_extend(config, variant, "homophones", t_vec(config, t))
            elif name == "hyphenation":
                # This is often in pronunciation, but we'll store it at top
                # level in the entry
                data_append(config, data, "hyphenation", t_vec(config, t))
            # These templates are silently ignored for pronunciation information
            # collection purposes.
            elif name in ("inflection of", "l", "link", "l-self",
                          "m", "w", "W", "label",
                          "gloss", "zh-m", "zh-l", "ja-l", "wtorw",
                          "ux", "ant", "syn", "synonyms", "antonyms",
                          "wikipedia", "Wikipedia",
                          "alternative form of", "alt form",
                          "altform", "alt-form", "abb", "rareform",
                          "alter", "hyph", "honoraltcaps",
                          "non-gloss definition", "n-g", "non-gloss",
                          "ngd",
                          "senseid", "defn", "ja-r", "ja-l", "ja-r/args",
                          "ja-r/multi",
                          "place:Brazil/state",
                          "place:Brazil/municipality",
                          "place", "taxlink",
                          "pedlink", "vern", "prefix", "affix",
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
                config.unrecognized_template(t, "pronunciation")

        if sense:
            variant["sense"] = sense

        # If we got some useful pronunciation information, save it
        # under "sounds" in the word entry.
        if len(set(variant.keys()) - set(["tags", "sense", "accent"])):
            data_append(config, data, "pronunciations", variant)

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


def parse_linkage(config, data, kind, text, p, sense_text=None):
    """Parses links to other words, such as synonyms, hypernyms, etc.
    ```kind``` identifies the default type for such links (based on section
    header); however, it is not entirely reliable.  The particular template
    types used may also indicate what type of link it is; we trust that
    information more."""

    added = set()

    def parse_item(text, kind, is_item):

        sense_text = None
        qualifiers = []

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
            if v in ("", "en",):
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
            data_append(config, data, kind, v)
            qualifiers = []

        # Parse the item text.
        p = wikitextparser.parse(text)
        if len(text) < 200 and text and text[0] not in "*:":
            item = clean_value(config, text)
            if item:
                if item.startswith("For more, see "):
                    item = item[14:]

                links = []
                for t in p.templates:
                    name = t.name.strip()
                    if name == "sense":
                        sense_text = t_arg(config, t, 1)
                    elif name == "l":
                        links.append((kind, t_arg(config, t, 2)))
                    elif name == "qualifier":
                        qualifiers.extend(t_vec(config, t))
                if links:
                    saved_qualifiers = []
                    for kind, link in links:
                        qualifiers = saved_qualifiers
                        add_linkage(kind, link)
                        return

                found = False
                for m in re.finditer(r"''+([^']+)''+", text):
                    v = m.group(1)
                    v = clean_value(config, v)
                    if v.startswith("(") and v.endswith(")"):
                        # XXX These seem to often be qualifiers
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
            # Link tags just use the default kind
            if name in ("l", "link", "l/ja", "1"):
                add_linkage(kind, t_arg(config, t, 2))
            # Wikipedia links also suggest a linkage of the default kind
            elif name in ("wikipedia", "Wikipedia", "w", "wp"):
                add_linkage(kind, t_arg(config, t, 1))
            elif name in ("w2",):
                add_linkage(kind, t_arg(config, t, 2))
            # Japanese links seem to commonly use "ja-r" template.
            # Use the default linkage for them, and collect the
            # "hiragana" mapping for the catagana term when available
            # (actually using them would require later
            # postprocessing).
            elif name in ("ja-r", "ja-r/args"):
                kata = t_arg(config, t, 1)
                hira = t_arg(config, t, 2)
                add_linkage(kind, kata)
                # XXX this goes into wrong place
                #if hira:
                #    data_append(config, data, "hiragana", (kata, hira))
            # Handle various types of common Japanese/Chinese links.
            elif name in ("ja-l", "lang", "zh-l", "ko-l", "vi-l", "th-l"):
                add_linkage(kind, t_arg(config, t, 1))
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
            elif name in ("q", "qual", "qualifier", "qf", "i",
                          "lb", "lbl", "label", "a", "accent"):
                qualifiers.extend(clean_quals(config, t_vec(config, t)[1:]))
            # Various tags seem to indicate topical categories that the
            # word belongs to.  These are added under "topics".
            elif name in ("topics", "categorize", "catlangname", "c", "C",
                          "cln",
                          "top", "categorise", "catlangcode"):
                for topic in t_vec(config, t)[1:]:
                    data_append(config, data, "topics", {"word": topic})
            elif name in ("zh-cat",):
                for topic in t_vec(config, t):
                    data_append(config, data, "topics", {"word": topic})
            # XXX temporary tag accroding to its documentation
            elif name == "g2":
                v = t_arg(config, t, 1)
                if v == "m":
                    qualifiers.append("masculine")
                elif v == "f":
                    qualifiers.append("feminine")
                elif v == "n":
                    qualifiers.append("neuter")
                elif v == "c":
                    qualifiers.append("common")
                elif v == "p":
                    qualifiers.append("plural")
                elif v == "m-p":
                    qualifiers.extend(["masculine", "plural"])
                elif v == "f-p":
                    qualifiers.extend(["feminine", "plural"])
                else:
                    config.unknown_value(t, v)
            # Gloss templates are sometimes used to qualify the sense
            # in which the link is intended.
            elif name in ("sense", "gloss", "s"):
                sense_text = t_arg(config, t, 1)
            # Synonym templates expressly indicate the link as a synonym.
            elif name in ("syn", "synonyms"):
                for x in t_vec(config, t)[1:]:
                    add_linkage("synonyms", x)
            elif name in ("syn2", "syn3", "syn4", "syn5", "syn1",
                          "syn2-u", "syn3-u", "syn4-u", "syn5-u"):
                qualifiers = []
                sense_text = t_arg(config, t, "title")
                for x in t_vec(config, t):
                    add_linkage("synonyms", x)
                sense_text = None
            # Antonym templates expressly indicate the link as an antonym.
            elif name in ("ant", "antonyms"):
                add_linkage("antonyms", t_arg(config, t, 2))
            elif name in ("ant5", "ant4", "ant3", "ant2", "ant1",
                          "ant5-u", "ant4-u", "ant3-u", "ant2-u"):
                qualifiers = []
                sense_text = t_arg(config, t, "title")
                for x in t_vec(config, t):
                    add_linkage("antonyms", x)
                sense_text = None
            # Hyponym templates expressly indicate the link as a hyponym.
            elif name in ("hyp5", "hyp4", "hyp3", "hyp2", "hyp1",
                          "hyp5-u", "hyp4-u", "hyp3-u", "hyp2-u"):
                qualifiers = []
                sense_text = t_arg(config, t, "title")
                for x in t_vec(config, t):
                    add_linkage("hyponyms", x)
                sense_text = None
            # Derived term links expressly indicate the link as a derived term.
            # XXX is this semantic meaning always clear, or are these also used
            # in other linkage subsections for just formatting purposes?
            elif name in ("der5", "der4", "der3", "der2", "der1", "zh-der",
                          "der5-u", "der4-u", "der3-u", "der2-u",
                          "zh-der", "vi-der",
                          "Template:User:Donnanz/der3-u",
                          "derived terms", "rootsee", "prefixsee"):
                qualifiers = []
                sense_text = t_arg(config, t, "title")
                for x in t_vec(config, t):
                    add_linkage("derived", x)
                sense_text = None
            # Related term links expressly indicate the link is a related term.
            # XXX are these also used for other purposes?
            elif name in ("rel5", "rel4", "rel3", "rel2", "rel1",
                          "rel5-u", "rel4-u", "rel3-u", "rel2-u"):
                qualifiers = []
                sense_text = t_arg(config, t, "title")
                for x in t_vec(config, t):
                    add_linkage("related", x)
                sense_text = None
            # Some languages mark compass directions as linkages
            elif name in "compass":
                args = t_dict(config, t)
                for key in ("n", "ne", "e", "se", "s", "sw", "w", "ne"):
                    v = args.get(key)
                    if v:
                        add_linkage("related", v)
            # These templates start a range with links of the specific kind.
            elif name in ("rel-top3", "rel-top4", "rel-top5",
                          "rel-top2", "rel-top"):
                qualifiers = []
                sense_text = t_arg(config, t, 1)
                kind = "related"
            elif name in ("hyp-top3", "hyp-top4", "hyp-top5", "hyp-top2"):
                qualifiers = []
                sense_text = t_arg(config, t, 1)
                kind = "hyponym"
            elif name in ("der-top", "der-top2", "der-top3", "der-top4",
                          "der-top5", "der top", "der bottom"):
                qualifiers = []
                sense_text = t_arg(config, t, 1)
                kind = "derived"
            # These templates end a range with links of the specific kind.
            elif name in ("rel-bottom", "rel-bottom1", "rel-bottom2",
                          "rel-bottom3", "rel-bottom4", "rel-bottom5"):
                qualifiers = []
                sense_text = None
            elif name in ("col1", "col1-u", "col2", "col2-u", "col3", "col3-u",
                          "col4", "col4-u", "col5", "col5-u"):
                qualifiers = []
                sense_text = t_arg(config, t, "title")
                for x in t_vec(config, t)[1:]:
                    add_linkage(kind, x)
            elif name == "bullet list":
                qualifiers = []
                sense_text = None
                for x in t_vec(config, t):
                    add_linkage(kind, x)
            elif name in ("zh-synonym", "zh-syn-saurus"):
                kind = "synonyms"
                base = t_arg(config, t, 1)
                if base != config.word:
                    add_linkage(kind, base)
            elif name in ("zh-ant-saurus"):
                kind = "antonyms"
                base = t_arg(config, t, 1)
                if base != config.word:
                    add_linkage(kind, base)
            elif name == "zh-dial":
                qualifiers.append("dialectical")
                kind = "synonyms"
                base = t_arg(config, t, 1)
                if base != config.word:
                    add_linkage(kind, base)
            elif name in ("Template:letter-shaped", "letter-shaped"):
                data_append(config, data, "topics",
                            {"word":
                             "English terms defived from the shape of letters"})
            elif name in ("Template:object-shaped", "object-shaped"):
                data_append(config, data, "topics",
                            {"word":
                             "English terms defived from the shape of objects"})
            # These templates seem to be frequently used for things that
            # aren't particularly useful for linking.
            elif name in ("t", "t+", "ux", "trans-top", "w", "pedlink",
                          "affixes", "ISBN", "specieslite", "projectlink",
                          "wikispecies", "comcatlite", "wikidata",
                          "mid5", "top5", "compass-fi", "derivsee",
                          "small",
                          "presidential nomics",
                          "video frames",
                          "polyominoes",
                          "mediagenic terms",
                          "common names of Valerianella locusta",
                          "ga-prepositional contractions",
                          "ga-copular forms",
                          "compoundsee",
                          "Japanese demonstratives",
                          "Spanish possessive adjectives",
                          "Spanish possessive pronouns",
                          "French possessive adjectives",
                          "French possessive pronouns",
                          "French personal pronouns"):
                continue
            # Silently skip any templates matching these.
            elif re.search("^(list:|R:|table:)", name):
                continue
            # It is common to use special templates to indicate genus or higher
            # classes for species.  We just convert those templates to hypernym
            # links.
            elif re.match("^[A-Za-z].*? Hypernyms$", name):
                m = re.match("^([A-Za-z].*?) Hypernyms$", name)
                v = m.group(1)
                add_linkage("hypernyms", v)

            elif name not in ignored_templates:
                # Warn about unhandled templates.
                config.unrecognized_template(t, "linkage")

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


def parse_any(config, data, text, sectitle, p):
    """This function is called for all subsections of a word entry to parse
    information that might be in any section and that can be interpreted
    without knowing the specific section."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(text, str)
    assert isinstance(sectitle, str)

    translation_sense = None
    for t in p.templates:
        name = t.name.strip()
        # Alternative forms seem to provide alternative forms with dialectal
        # descriptions.  XXX see how to handle these, and if they should be
        # merged with "alt_of" in word senses.
        if name == "alter":
            vec = t_vec(config, t)
            for brk in range(0, len(vec)):
                if vec[brk] == "":
                    break
            for i in range(0, brk):
                alt = vec[i]
                dialect = ""
                if brk + 1 + i < len(vec):
                    dialect = vec[brk + 1 + i]
                dt = {"word": alt}
                if dialect:
                    dt["dialect"] = dialect
                data_append(config, data, "alternative", dt)
        # Section links are used to refer to separate translation pages in many
        # word entry pages.  However, there are also other ways to refer
        # to translation pages.
        elif name == "section link":
            target = t_arg(config, t, 1)
            m = re.match(r"^(([^/]+)/translations)(#(.*))?$", target)
            if m:
                tpage = m.group(1)
                tword = m.group(2)
                tsect = m.group(4)
                if tword != config.word:
                    config.unknown_value(t, "TRANSLATIONS LINK")
                data_append(config, data, "translation_link", (tpage, tsect))
        # If a reference to a book by ISBN has been provided, save its ISBN.
        #elif name == "ISBN":
        #    data_append(config, data, "isbn", t_arg(config, t, 1))
        # This template marks the beginning of a group of translations, and
        # may provide a word sense for the translations.
        elif name == "trans-top":
            translation_sense = t_arg(config, t, 1)
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
            if config.capture_translations:
                vec = t_vec(config, t)
                if len(vec) < 2:
                    continue
                lang = vec[0]
                transl = vec[1]
                markers = vec[2:]  # gender/class markers
                alt = t_arg(config, t, "alt")
                roman = t_arg(config, t, "tr")
                script = t_arg(config, t, "sc")
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
                data_append(config, data, "translations", t)
        # Collect any conjugation/declension information for the word.
        # These are highly language-specific, and this may require tweaking
        # as support for more languages is added.
        elif re.match(r"^[a-z][a-z][a-z]?-(conj|decl|infl|conjugation|"
                      r"declension|inflection)($|-)", name):
            args = t_dict(config, t)
            data_append(config, data, "conjugation", args)
        # The "enum" template links words that are in a sequence to the next
        # and previous words in the sequence, as well as may provide a topic
        # for the sequence.  Collect this information when available, but
        # we don't try to interpret it here (there seems to be some variation).
        elif name == "enum":
            lang = t_arg(config, t, 1)
            prev_value = t_arg(config, t, 2)
            next_value = t_arg(config, t, 3)
            value = t_arg(config, t, 4)
            data_append(config, data, "enum", {"lang": lang,
                                       "prev": prev_value,
                                       "next": next_value,
                                       "value": value})
        elif name == "IPA" and sectitle != "pronunciation":
            config.error("IPA outside pronunciation in section {}"
                         "".format(sectitle))

    # Parse category links.  These may provide semantic and other information
    # about the word.  Note that category links are global for the word; we
    # cannot associate them with any particular word sense or part-of-speech.
    for t in p.wikilinks:
        target = t.target.strip()
        if target.startswith("Category:"):
            target = target[9:]
            m = re.match(r"^[a-z][a-z][a-z]?:(.*)", target)
            if m:
                target = m.group(1)
            data_append(config, data, "topics", {"word": target})


def parse_etymology(config, data, text, p):
    """From the etymology section we parse "compound", "affix", and
    "suffix" templates.  These may suggest that the word is a compound
    word.  They are stored under "compound"."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(text, str)

    for t in p.templates:
        name = t.name.strip()
        if name in ("compound", "affix", "prefix"):
            data_append(config, data, "compound", t_dict(config, t))


def page_iter(config, text):
    """Iterates over the text of the page, returning words (parts-of-speech)
    defined on the page one at a time.  (Individual word senses for the
    same part-of-speech are typically encoded in the same entry.)"""
    assert isinstance(text, str)
    assert isinstance(config, WiktionaryConfig)

    # Divide the text into subsections.  We ignore the tree structure of
    # sections because it has so many inconsistencies.
    sections = split_subsections(config, text)

    def iter_fn():
        language = None
        config.language = None
        config.pos = None
        pos = None
        pos_sectitle = None
        base = {}
        datas = []
        data = {}

        def flush():
            # Flushes information about the current part-of-speech entry.
            nonlocal data
            if pos is None:
                return
            if (config.capture_languages is None or
                language in config.capture_languages):
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
            if sectitle in languages_by_name:
                # Found section for a langauge.  First flush any information
                # for the previous language.
                flush()
                flush_datas()
                for x in flush_datas():
                    yield x

                # Initialize for parsing words in the new language.
                langdata = languages_by_name[sectitle]
                language = sectitle
                config.language_counts[language] += 1
                pos = None
                base = {"word": config.word,
                        "lang": language,
                        "lang_code": langdata["code"]}
                data = {}
                datas = []
                sectitle = ""
                config.language = language
                config.pos = None
            else:
                # This title continues the previous language or could be
                # a new language or a misspelling or a previously unsupported
                # subtitle.
                sectitle = sectitle.lower()
                if sectitle in part_of_speech_map:
                    # New part-of-speech.  Flush the old part-of-speech.
                    flush()
                    # Initialize for parsing the new part-of-speech.
                    pos_ht = part_of_speech_map[sectitle]
                    pos = pos_ht["pos"]
                    pos_sectitle = sectitle
                    # XXX errors if pos_ht["error"]
                    # XXX warnings if pos_ht["warning"]
                    config.pos_counts[pos] += 1
                    config.pos = pos
                    data = {}
                    if "tags" in pos_ht:
                        data_extend(config, data, "tags", pos_ht["tags"])
                    sectitle = ""
                else:
                    # We don't recognize this subtitle.  Include it in the
                    # counts; the counts should be periodically investigates
                    # to find out if new languages have been added.
                    config.section_counts[sectitle] += 1

            # Check if this is a language we are capturing.  If not, just
            # skip the section.
            if (config.capture_languages is not None and
                language not in config.capture_languages):
                continue

            if pos is None:
                # Have not yet seen a part-of-speech.  However, this initial
                # part frequently contains pronunciation information that
                # is shared by all parts of speech.  We don't care here
                # whether it is under a ``pronunciation`` subsection, because
                # the structure may vary.
                if config.capture_pronunciation:
                    p = wikitextparser.parse(text)
                    parse_pronunciation(config, base, text, p)
                continue

            # Remove any numbers at the end of the section title.
            sectitle = re.sub(r"\s+\d+(\.\d+)$", "", sectitle)

            # Apply corrections to common misspellings in sectitle
            if sectitle in sectitle_corrections:
                dt = sectitle_corrections[sectitle]
                correct = dt["correct"]
                #if dt.get("error"):
                #    XXX report error, displaying sectitle and correct
                sectitle = correct

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
                parse_etymology(config, data, text, p)
                continue

            # Parse the section contents.
            p = wikitextparser.parse(text)

            # If the section title is empty, it is the preamble (text before
            # the first subsection for the language).
            if sectitle == "":  # Preamble
                parse_preamble(config, data, pos_sectitle, text, p)
            # If the section title title indicates pronunciation, parse it here.
            elif sectitle == "pronunciation":
                if config.capture_pronunciation:
                    parse_pronunciation(config, data, text, p)
            # Parse various linkage sections, defaulting to the linkage type
            # indicated by the section header.
            elif sectitle == "synonyms":
                if config.capture_linkages:
                    parse_linkage(config, data, "synonyms", text, p)
            elif sectitle == "hypernyms":
                if config.capture_linkages:
                    parse_linkage(config, data, "hypernyms", text, p)
            elif sectitle == "hyponyms":
                if config.capture_linkages:
                    parse_linkage(config, data, "hyponyms", text, p)
            elif sectitle == "antonyms":
                if config.capture_linkages:
                    parse_linkage(config, data, "antonyms", text, p)
            elif sectitle == "derived terms":
                if config.capture_linkages:
                    parse_linkage(config, data, "derived", text, p)
            elif sectitle in ("related terms", "related characters"):
                if config.capture_linkages:
                    parse_linkage(config, data, "related", text, p)
            # Parse abbreviations.
            elif sectitle == "abbreviations":
                parse_linkage(config, data, "abbreviations", text, p)
            # Parse proverbs.
            elif sectitle == "proverbs":
                parse_linkage(config, data, "abbreviations", text, p)
            # Parse compounds using the word.
            elif sectitle == "compounds":
                if config.capture_compounds:
                    parse_linkage(config, data, "compounds", text, p)
            # We skip declension information here, as it is parsed from all
            # sections in parse_any().
            elif sectitle in ("declension", "conjugation"):
                pass
            # XXX warn on other sections

            # Some information is parsed from any section.
            parse_any(config, data, text, sectitle, p)

        # Finally flush the last language.
        flush()
        for x in flush_datas():
            yield x

    return iter_fn()


def parse_page(word, text, config):
    """Parses the text of a Wiktionary page and returns a list of
    dictionaries, one for each word/part-of-speech defined on the page
    for the languages specified by ``capture_languages`` (None means
    all available languages).  ``word`` is page title, and ``text`` is
    page text in Wikimedia format.  Other arguments indicate what is
    captured."""
    assert isinstance(word, str)
    assert isinstance(text, str)
    assert isinstance(config, WiktionaryConfig)

    if config.verbose:
        print("parsing page:", word)

    unsupported_prefix = "Unsupported titles/"
    if word.startswith(unsupported_prefix):
        w = word[len(unsupported_prefix):]
        if w in unsupported_title_map:
            word = unsupported_title_map[w]
        else:
            config.debug("Unimplemented title: {}"
                         "".format(word))

    config.word = word
    config.language = None
    config.pos = None

    # Collect all words from the page.
    datas = list(x for x in page_iter(config, text))

    # Do some post-processing on the words.  For example, we may distribute
    # conjugation information to all the words.
    by_lang = collections.defaultdict(list)
    for data in datas:
        if "lang" not in data:
            config.debug("no lang in data: {}".format(data))
            continue
        by_lang[data["lang"]].append(data)
    for lang, lang_datas in by_lang.items():
        # If one of the words coming from this article does not have
        # conjugation information, but another one for the same
        # language and a compatible part-of-speech has, use the
        # information from the other one also for the one without.
        for data in lang_datas:
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
                        data["conjugation"] = conjs
                        break
        # Add topics from the last sense of a language to its other senses,
        # marking them inaccurate as they may apply to all or some sense
        if len(lang_datas) > 1:
            topics = lang_datas[-1].get("topics", [])
            for t in topics:
                t["inaccurate"] = True
            for data in lang_datas[:-1]:
                data["topics"] = data.get("topics", []) + topics

    # Return the resulting words
    return datas

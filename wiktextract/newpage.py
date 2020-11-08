# Code for parsing information from a single Wiktionary page.
#
# Copyright (c) 2018-2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import sys
import html
import collections
import wikitextparser
from wikitextprocessor import Wtp, WikiNode, NodeKind, ALL_LANGUAGES
from .parts_of_speech import part_of_speech_map, PARTS_OF_SPEECH
from .config import WiktionaryConfig
from .sectitle_corrections import sectitle_corrections
from .clean import clean_value, clean_quals
from .places import place_prefixes  # XXX move processing to places.py
from .wikttemplates import *
from .unsupported_titles import unsupported_title_map
from .form_of import form_of_map
from .head_map import head_pos_map
from .datautils import (data_append, data_extend, data_inflection_of,
                        data_alt_of, split_at_comma_semi)
from wiktextract.form_descriptions import (
    decode_tags, parse_word_head, parse_sense_tags, parse_pronunciation_tags,
    parse_translation_desc, xlat_tags_map, valid_tags)


# Mapping from language name to language info
languages_by_name = {x["name"]: x for x in ALL_LANGUAGES}

# Mapping from language code to language info
languages_by_code = {x["code"]: x for x in ALL_LANGUAGES}

# Matches en:, fr:, etc.
# XXX remove this
langtag_colon_re = re.compile(r"^(" + "|".join(languages_by_code.keys()) +
                              r"):")

# Matches head tag
head_tag_re = re.compile(r"^(head|Han char)$|" +
                         r"^(" + "|".join(languages_by_code.keys()) + r")"
                         r"-(plural-noun|plural noun|noun|verb|adj|adv|"
                         r"name|proper-noun|proper noun|prop|pron|phrase|"
                         r"decl noun|decl-noun|prefix|clitic|number|ordinal|"
                         r"syllable|suffix|affix|pos|gerund|combining form|"
                         r"combining-form|converb|cont|con|interj|det|part|"
                         r"part-form|postp|prep)(-|$)")

# Regular expression for removing links to specific languages from
# translation items
langlink_re = re.compile(r"\s*\((" + "|".join(languages_by_code.keys()) +
                         r")\)|"
                         r"\(\s*\[\[:[-a-zA-Z0-9]+:[^]]+\]\]\s*\)")

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
        gloss = re.sub(r"\s*\[\d\d\d\d\]", "", gloss)  # Remove first years
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
        elif name in ("combining form of",):
            data_alt_of(config, data, t, ["combining_form"])
        elif name in ("only used in", "only in"):
            # This appears to be used in "man" for "man enough"
            data_append(config, data, "only_in", t_arg(config, t, 2))
        elif name == "native or resident of":
            data_inflection_of(config, data, t, ["person"])
        elif name == "topic form":
            data_inflection_of(config, data, t, ["topic"])
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
        elif name == "es-demonstrative-accent-usage":
            data_append(config, data, "tags", "demonstrative-accent")
        # Handle some Japanese-specific tags
        elif name in ("ja-kyujitai spelling of", "ja-kyu sp"):
            data_append(config, data, "kyujitai_spelling", t_arg(config, t, 1))
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
                    m = re.match(r"(?i)^(.+):(pref|suf|Suf)$", prefix)
                    if m:
                        prefix = m.group(1)
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


def parse_pronunciation(config, data, text, p):
    """Extracts pronunciation information for the word."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(text, str)

    # XXX this function being removed

    # Pronunciation may be qualified by
    # accent/dialect/variant.  These are recorded under
    # "tags".  See
    # https://en.wiktionary.org/wiki/Module:accent_qualifier/data
    if name in ("a", "accent"):
        data_extend(config, variant, "accent", clean_quals(config, t_vec(config, t)))
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


######################################################################
# XXX Above this is old junk
######################################################################

# Template name component to linkage section listing.  Integer section means
# default section, starting at that argument.
template_linkage_mappings = [
    ["syn", "synonyms"],
    ["synonyms", "synonyms"],
    ["ant", "antonyms"],
    ["hyp", "hyponyms"],
    ["der", "derived"],
    ["derived terms", "derived"],
    ["rootsee", "derived"],   # XXX ???
    ["prefixsee", "derived"],  # XXX ???
    ["rel", "related"],
    ["col", 2],
]


def decode_html_entities(v):
    if not isinstance(v, str):
        return v
    return html.unescape(v)


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

    config.pos = None
    config.subsection = None
    word = ctx.title  # XXX translations for titles to words
    base = {"word": word, "lang": language, "lang_code": lang_code}
    sense_data = {}
    pos_data = {}  # For a current part-of-speech
    etym_data = {}  # For one etymology
    pos_datas = []
    etym_datas = []
    page_datas = []
    stack = []

    def merge_base(data, base):
        for k, v in base.items():
            if k not in data:
                data[k] = v
            elif isinstance(data[k], list):
                data[k].extend(v)
            elif data[k] != v:
                ctx.warning("conflicting values for {}: {} vs {}"
                            .format(k, data[k], v))

    def push_sense():
        nonlocal sense_data
        if not sense_data:
            return
        pos_datas.append(sense_data)
        sense_data = {}

    def push_pos():
        nonlocal pos_data
        nonlocal pos_datas
        push_sense()
        if pos_datas:
            data = {"senses": pos_datas}
            merge_base(data, pos_data)
            etym_datas.append(data)
        elif config.pos:
            config.warning("no senses found")
        pos_data = {}
        pos_datas = []

    def push_etym():
        nonlocal etym_data
        nonlocal etym_datas
        push_pos()
        for data in etym_datas:
            merge_base(data, etym_data)
            page_datas.append(data)
        etym_data = {}
        etym_datas = []

    def sense_template_fn(name, ht):
        if name in ("LDL",):
            return ""
        if name in ("syn", "synonyms"):
            for i in range(2, 20):
                w = ht.get(i)
                if not w:
                    break
                data_append(config, sense_data, "synonyms",
                            {"word": w})
            return ""
        return None

    def parse_sense(pos, node):
        assert isinstance(pos, str)
        assert isinstance(node, WikiNode)
        push_sense()
        assert node.kind == NodeKind.LIST_ITEM
        lst = [x for x in node.children
               if not isinstance(x, WikiNode) or
               x.kind not in (NodeKind.LIST,)]
        gloss = clean_node(config, ctx, lst, template_fn=sense_template_fn)
        if not gloss:
            config.warning("{}: empty gloss".format(pos))
        m = re.match(r"^\((([^()]|\([^)]*\))*)\):?\s*", gloss)
        if m:
            parse_sense_tags(ctx, config, m.group(1), sense_data)
            gloss = gloss[m.end():].strip()
        # Kludge, some glosses have a comma after initial qualifiers in
        # parentheses
        if gloss.startswith(", "):
            gloss = gloss[2:]
        data_append(config, sense_data, "glosses", gloss)

    def head_template_fn(name, ht):
        # print("HEAD_TEMPLATE_FN", name, ht)
        if name in ("examples", "wikipedia", "stroke order",
                    "zh-forms", "rfc"):
            return ""
        if name == "number box":
            # XXX extract numeric value?
            return ""
        if name == "enum":
            # XXX extract?
            return ""
        if name == "Han simplified forms":
            # XXX extract?
            return ""
        if name == "ja-kanji forms":
            # XXX extract?
            return ""
        if name == "vi-readings":
            # XXX extract?
            return ""
        if name == "picdic" or name == "picdicimg":
            # XXX extract?
            return ""
        m = re.search(head_tag_re, name)
        if m:
            new_ht = {}
            for k, v in ht.items():
                new_ht[decode_html_entities(k)] = decode_html_entities(v)
            new_ht["template_name"] = name
            data_append(config, pos_data, "heads", new_ht)
        return None

    def parse_part_of_speech(posnode, pos):
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
                for p in re.split(r"\n\n+", node):
                    if pre:
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
            elif kind in (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
                          NodeKind.LEVEL5, NodeKind.LEVEL6):
                break
            elif kind == NodeKind.LINK:
                # We might collect relevant links as they are often pictures
                # relating to the word
                continue
            elif kind == NodeKind.HTML:
                if node.args not in ("gallery", "ref", "cite", "caption"):
                    pre.append(node)
            elif first_para:
                pre.append(node)
        if not lists:
            config.warning("{}: no sense list found".format(pos))
            return
        # XXX use template_fn in clean_node to check that the head macro
        # is compatible with the current part-of-speech and generate warning
        # if not.  Use template_allowed_pos_map.
        text = clean_node(config, ctx, pre, template_fn=head_template_fn)
        parse_word_head(ctx, config, pos, text, pos_data)
        for node in lists:
            for node in node.children:
                if node.kind != NodeKind.LIST_ITEM:
                    config.warning("{}: non-list-item inside list".format(pos))
                    continue
                if node.args[-1] == ":":
                    # Sometimes there may be lists with indented examples
                    # in otherwise the same level as real sense entries.
                    # I assume those will get parsed as separate lists, but
                    # we don't want to include such examples as word senses.
                    continue
                parse_sense(pos, node)

    def parse_pronunciation(node):
        assert isinstance(node, WikiNode)
        if node.kind in (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
                         NodeKind.LEVEL5, NodeKind.LEVEL6):
            node = node.children
        data = etym_data if etym_data else base
        enprs = []
        audios = []
        rhymes = []

        def parse_pronunciation_template_fn(name, ht):
            if name == "enPR":
                enpr = ht.get(1)
                if enpr:
                    enprs.append(enpr)
                return ""
            if name == "audio":
                filename = ht.get(2) or ""
                desc = ht.get(3) or ""
                audio = {"file": filename}
                m = re.search(r"\((([^()]|\([^)]*\))*)\)", desc)
                if m:
                    parse_pronunciation_tags(ctx, config, m.group(1), audio)
                if desc:
                    audio["text"] = desc
                audios.append(audio)
                return ""
            if name in ("picdic", "picdicimg", "langname", "rfc"):
                return ""
            return None

        # XXX change this code to iterate over node as a LIST, warning about
        # anything else.  Don't try to split by "*".
        # XXX fix enpr tags
        text = clean_node(config, ctx, node,
                          template_fn=parse_pronunciation_template_fn)
        for origtext in text.split("*"):  # List items generated by macros
            text = origtext
            m = re.match("^[*#\s]*\((([^()]|\([^)]*\))*?)\)", text)
            if m:
                tagstext = m.group(1)
                text = text[m.end():]
            else:
                tagstext = ""
            if origtext.find("IPA") >= 0:
                field = "ipa"
            else:
                field = "other"
            # Check if it contains Japanese "Tokyo" pronunciation with
            # special syntax
            m = re.search(r"\(Tokyo\) +([^ ]+) +\[", origtext)
            if m:
                pron = {field: m.group(1)}
                parse_pronunciation_tags(ctx, config, tagstext, pron)
                data_append(config, data, "sounds", pron)
            # Check if it contains Rhymes
            m = re.search(r"\bRhymes: ([^\s,]+(,\s*[^\s,]+)*)", text)
            if m:
                for ending in m.group(1).split(","):
                    ending = ending.strip()
                    if ending:
                        pron = {"rhymes": ending}
                        parse_pronunciation_tags(ctx, config, tagstext, pron)
                        data_append(config, data, "sounds", pron)
            # Check if it contains homophones
            m = re.search(r"\bHomophones?: ([^\s,]+(,\s*[^\s,]+)*)", text)
            if m:
                for word in m.group(1).split(","):
                    word = ending.strip()
                    if word:
                        pron = {"homophone": word}
                        parse_pronunciation_tags(ctx, config, tagstext, pron)
                        data_append(config, data, "sounds", pron)

            #print("parse_pronunciation tagstext={} text={}"
            #      .format(tagstext, text))
            for m in re.finditer("/[^/,]+?/|\[[^]0-9,/][^],/]*?\]", text):
                pron = {field: m.group(0)}
                parse_pronunciation_tags(ctx, config, tagstext, pron)
                data_append(config, data, "sounds", pron)
            # XXX what about {{hyphenation|...}}, {{hyph|...}}
            # and those used to be stored under "hyphenation"
            m = re.search(r"\bSyllabification: ([^\s,]*)", text)
            if m:
                data_append(config, data, "syllabification", m.group(1))


        # Add data that was collected in template_fn
        data_extend(config, data, "sounds", audios)
        for enpr in enprs:
            pron = {"enpr": enpr}
            # XXX need to parse enpr separately for each list item to get
            # tags correct!
            # parse_pronunciation_tags(ctx, config, tagstext, pron)
            data_append(config, data, "sounds", pron)

    def parse_declension_conjugation(node):
        # print("parse_decl_conj:", node)
        assert isinstance(node, WikiNode)
        captured = False

        def decl_conj_template_fn(name, ht):
            # print("decl_conj_template_fn", name, ht)
            m = re.search(r"-(conj|decl|ndecl|adecl|infl|conjugation|"
                          r"declension|inflection)($|-)", name)
            if m:
                new_ht = {}
                # Convert html entities that may be used in the arguments
                for k, v in ht.items():
                    new_ht[decode_html_entities(k)] = decode_html_entities(v)
                new_ht["template_name"] = name
                data_append(config, pos_data, "conjugation", new_ht)
                nonlocal captured
                captured = True
                return ""

            # XXX this should be in sense parsing
            # if name == "pinyin reading of" and 1 in ht:
            #     data_append(config, pos_data, "forms",
            #                 {"form": ht[1], "tags": ["pinyin of"]})
            #     return ""

            return None

        text = ctx.node_to_html(node, template_fn=decl_conj_template_fn)
        if not captured:
            # XXX try to parse either a WikiText table or a HTML table that
            # contains the inflectional paradigm
            # XXX should we try to capture it even if we got the template?
            pass

    def parse_linkage(data, field, linkagenode):
        assert isinstance(data, dict)
        assert isinstance(field, str)
        assert isinstance(linkagenode, WikiNode)
        # print("PARSE_LINKAGE:", linkagenode)
        if not config.capture_linkages:
            return

        def parse_linkage_item(item, field, sense=None):
            assert isinstance(item, (str, list, tuple))
            assert isinstance(field, str)
            if not isinstance(item, (list, tuple)):
                item = [item]
            qualifier = None
            english = None

            # XXX recognize items that refer to thesaurus, e.g.:
            # "word" synonyms: "vocable; see also Thesaurus:word"

            sublists = [x for x in item if isinstance(x, WikiNode) and
                        x.kind == NodeKind.LIST]
            item = [x for x in item if not isinstance(x, WikiNode) or
                    x.kind != NodeKind.LIST]

            def linkage_item_template_fn(name, ht):
                nonlocal sense
                if name in ("sense", "s"):
                    sense = ht.get(1)
                    return ""
                if name == "qualifier":
                    q = ht.get(1)
                    if q and (q in valid_tags or q in xlat_tags_map
                              or q[0].isupper()):
                        qualifier = q
                    elif not english:
                        english = q
                if name in ("gloss", "bullet list"):
                    # XXX check how this is used in linkage
                    ctx.warning("UNIMPLEMENTED - check linkage template: {} {}"
                                .format(name, ht))
                    return None
                # XXX wikipedia, Wikipedia, w, wp, w2 link types
                return None

            item = clean_node(config, ctx, item,
                              template_fn=linkage_item_template_fn)

            def english_repl(m):
                nonlocal english
                english = m.group(1).strip()

            item = re.sub(r'\([“"]([^"]+)[“"]\)\s*', english_repl, item)
            if item.startswith(":"):
                item = item[1:]
            item = item.strip()

            # print("    LINKAGE ITEM:", item, field)
            m = re.match(r"\((([^()]|\([^)]*\))*)\):?\s*", item)
            if m:
                qualifier = m.group(1)
                item = item[m.end():]
            else:
                m = re.search(" \((([^()]|\([^)]*\))*)\)$", item)
                if m:
                    qualifier = m.group(1)
                    item = item[:m.start()]
            m = re.search(r"\s*\((([^()]|\([^)]*\))*)\)", item)
            if m:
                t = m.group(1)
                if t in valid_tags or t in xlat_tags_map:
                    if qualifier:
                        qualifier = qualifier + ", " + t
                    else:
                        qualifier = t
                    item = item[:m.start()] + item[m.end():]
            if item.find("(") >= 0:
                config.debug("linkage item has remaining parentheses: {}"
                             .format(item))

            item = item.strip()
            # XXX stripped item text starts with "See also [[...]]"
            if item and not sublists:
                dt = {"word": item}
                if qualifier:
                    parse_sense_tags(ctx, config, qualifier, dt)
                if english:
                    dt["translation"] = english
                if sense:
                    dt["sense"] = sense
                data_append(config, data, field, dt)

            # Some words have a word sense in a top-level list item and
            # use sublists for actual links
            for listnode in sublists:
                assert listnode.kind == NodeKind.LIST
                for node in listnode.children:
                    if not isinstance(node, WikiNode):
                        continue
                    if node.kind != NodeKind.LIST_ITEM:
                        continue
                    parse_linkage_item(node.children, field, sense=sense)


        def parse_linkage_ext(title, field):
            assert isinstance(title, str)
            assert isinstance(field, str)
            config.error("UNIMPLEMENTED: parse_linkage_ext: {} / {}"
                         .format(title, field))

        def parse_dialectal_synonyms(name, ht):
            config.error("UNIMPLEMENTED: parse_dialectal_synonyms: {} {}"
                         .format(name, ht))

        def parse_linkage_template(node):
            # print("LINKAGE TEMPLATE:", node)

            def linkage_template_fn(name, ht):
                # print("LINKAGE_TEMPLATE_FN:", name, ht)
                nonlocal field
                if name == "see also":
                    parse_linkage_ext(ht.get(1, ""), field)
                    return ""
                if name.endswith("-syn-saurus"):
                    parse_linkage_ext(ht.get(1, ""), "synonyms")
                    return ""
                if name.endswith("-ant-saurus"):
                    parse_linkage_ext(ht.get(1, ""), "antonyms")
                    return ""
                if name == "zh-dial":
                    parse_dialectal_synonyms(name, ht)
                    return ""
                if name in ("checksense", "predidential nomics",
                            "video frames", "polyominoes",
                            "list:compass points/en",
                            "compass-fi",
                            "mediagenic terms",
                            "Japanese demonstratives",
                            "Spanish possessive adjectives",
                            "Spanish possessive pronouns",
                            "French possessive adjectives",
                            "French possessive pronouns",
                            "French personal pronouns"):
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
                            parse_linkage_item(v, f)
                            i += 1
                        return ""
                # print("UNHANDLED LINKAGE TEMPLATE:", name, ht)
                return None

            # Main body of parse_linkage_template()
            text = ctx.node_to_html(node, template_fn=linkage_template_fn)
            # XXX certain things can only be parsed from the output, e.g.,
            # zh-dial

        def parse_linkage_table(node):
            config.warning("UNIMPLEMENTED: parse_linkage_table: {}"
                           .format(node))

        for node in linkagenode.children:
            if isinstance(node, str):
                node = node.strip()
                if node:
                    print("LINKAGE STR:", repr(node))
                continue
            assert isinstance(node, WikiNode)
            kind = node.kind
            if kind == NodeKind.LIST:
                for item in node.children:
                    if not isinstance(item, WikiNode):
                        continue
                    if item.kind != NodeKind.LIST_ITEM:
                        continue
                    parse_linkage_item(item.children, field)
            elif kind == NodeKind.TEMPLATE:
                parse_linkage_template(node)
            elif kind == NodeKind.TABLE:
                parse_linkage_table(node)
            elif kind == NodeKind.HTML:
                # Recurse to process inside the HTML for most tags
                if node.args not in ("gallery", "ref", "cite", "caption"):
                    parse_linkage(data, field, node)
            else:
                config.warning("LINKAGE UNEXPECTED: {}".format(node))

    def parse_translations(data, xlatnode):
        assert isinstance(data, dict)
        assert isinstance(xlatnode, WikiNode)
        #print("PARSE_TRANSLATIONS:", xlatnode)
        if not config.capture_translations:
            return
        sense_parts = []
        sense = None

        def parse_translation_item(contents, lang=None):
            nonlocal sense
            assert isinstance(contents, list)
            assert lang is None or isinstance(lang, str)
            # print("PARSE_TRANSLATION_ITEM:", contents)

            langcode = None
            if sense is None:
                sense = clean_node(config, ctx, sense_parts)

            def translation_item_template_fn(name, ht):
                nonlocal langcode
                # print("TRANSLATION_ITEM_TEMPLATE_FN:", name, ht)
                if name in ("t+", "t-simple", "t", "t+check"):
                    code = ht.get(1)
                    if code:
                        if langcode and code != langcode:
                            config.warning("differing language codes {} vs "
                                           "{} in translation item: {!r} {}"
                                           .format(langcode, code, name, ht))
                        langcode = code
                    return None
                if name in ("t-needed", "checktrans-top"):
                    return ""
                if name == "trans-see":
                    config.error("UNIMPLEMENTED trans-see template")
                    return ""
                if name.endswith("-top"):
                    return ""
                if name.endswith("-bottom"):
                    return ""
                if name.endswith("-mid"):
                    return ""
                #config.debug("UNHANDLED TRANSLATION ITEM TEMPLATE: {!r}"
                #             .format(name))
                return None

            sublists = list(x for x in contents
                            if isinstance(x, WikiNode) and
                            x.kind == NodeKind.LIST)
            contents = list(x for x in contents
                            if not isinstance(x, WikiNode) or
                            x.kind != NodeKind.LIST)

            item = clean_node(config, ctx, contents,
                              template_fn=translation_item_template_fn)
            # print("    TRANSLATION ITEM: {}  [{}]".format(item, sense))

            if re.search(r"\(\d+\)|\[\d+\]", item):
                if not item.find("numeral:"):
                    config.warning("POSSIBLE SENSE NUMBER IN ITEM: {}"
                                   .format(item))

            # Translation items should start with a language name
            m = re.match("\*?\s*([-' \w][-' \w]*):\s*", item)
            if not m:
                if not lang or item.find(":") >= 0:
                    config.error("no language name in translation item {!r}"
                                 .format(item))
                return
            sublang = m.group(1)
            item = item[m.end():]
            tags = []
            if lang is not None:
                tags.append(sublang)
            else:
                lang = sublang

            # Certain values indicate it is not actually a translation
            for prefix in ("Use ", "use ", "suffix ", "prefix "):
                if item.startswith(prefix):
                    return
            if item in ("please add this translation if you can",):
                return

            # There may be multiple translations, separated by comma
            for part in split_at_comma_semi(item):
                part = part.strip()
                if not part:
                    continue
                # Strip language links
                part = re.sub(langlink_re, "", part)
                tr = {"lang": lang, "code": langcode}
                if tags:
                    tr["tags"] = tags
                if sense:
                    if sense == "Translations to be checked":
                        data_append(config, tr, "tags", "to be checked")
                    else:
                        tr["sense"] = sense
                parse_translation_desc(ctx, config, part, tr)
                if tr.get("word"):  # Set and not empty
                    data_append(config, data, "translations", tr)

            m = re.match(r"\((([^()]|\([^)]*\))*)\) ", item)
            qualifier = None
            if m:
                qualifier = m.group(1)
                item = item[m.end():]
            else:
                m = re.search(" \((([^()]|\([^)]*\))*)\)$", item)
                if m:
                    qualifier = m.group(1)
                    item = item[:m.start()]

            # Handle sublists.  They are frequently used for different scripts
            # for the language and different variants of the langauge.  We will
            # include the lower-level header as a tag in those cases.
            for listnode in sublists:
                assert listnode.kind == NodeKind.LIST
                for node in listnode.children:
                    if not isinstance(node, WikiNode):
                        continue
                    if node.kind == NodeKind.LIST_ITEM:
                        parse_translation_item(node.children, lang=sublang)

        def parse_translation_template(node):
            assert isinstance(node, WikiNode)

            def template_fn(name, ht):
                if name == "see also":
                    # XXX capture
                    return ""
                if name == "see translation subpage":
                    # XXX capture
                    return ""
                if name == "rfc":
                    return ""
                config.error("UNIMPLEMENTED: parse_translation_template: {} {}"
                             .format(name, ht))
                return ""
            clean_node(config, ctx, [node], template_fn=template_fn)

        def parse_translation_table(tablenode):
            assert isinstance(tablenode, WikiNode)
            # print("PARSE_TRANSLATION_TABLE:", tablenode)
            for node in tablenode.children:
                #print("TABLE NODE", node)
                if not isinstance(node, WikiNode):
                    continue
                if node.kind == NodeKind.TABLE_ROW:
                    for cell in node.children:
                        #print("TABLE CELL", cell)
                        if not isinstance(cell, WikiNode):
                            continue
                        if cell.kind == NodeKind.TABLE_CELL:
                            parse_translation_recurse(cell)

        def parse_translation_recurse(xlatnode):
            nonlocal sense
            nonlocal sense_parts
            for node in xlatnode.children:
                if isinstance(node, str):
                    node = node.strip()
                    if node:
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
                    sense_parts = []
                    sense = None
                elif kind == NodeKind.TEMPLATE:
                    # XXX should these go into sense_parts?  What kind
                    # of templates do we encounter here?
                    parse_translation_template(node)
                elif kind == NodeKind.TABLE:
                    parse_translation_table(node)
                elif kind == NodeKind.HTML:
                    for item in node.children:
                        if not isinstance(item, WikiNode):
                            continue
                        parse_translation_recurse(item)
                else:
                    sense_parts.append(node)
                    sense = None

        # Main code of parse_translation().  We want ``sense`` to be assigned
        # regardless of recursion levels, and thus the code is structured
        # to define at this level and recurse in parse_translation_recurse().
        parse_translation_recurse(xlatnode)

    def process_children(langnode):
        nonlocal etym_data
        nonlocal pos_data
        for node in langnode.children:
            if not isinstance(node, WikiNode):
                # print("  X{}".format(repr(node)[:40]))
                continue
            if node.kind not in (NodeKind.LEVEL3, NodeKind.LEVEL4,
                                 NodeKind.LEVEL5, NodeKind.LEVEL6):
                # XXX handle e.g. wikipedia links at the top of a language
                # XXX should at least capture "also" at top of page
                if node.kind in (NodeKind.HLINE,):
                    continue
                # print("      UNEXPECTED: {}".format(node))
                continue
            t = clean_node(config, ctx, node.args)
            config.subsection = t
            config.section_counts[t] += 1
            pos = t.lower()
            # print("PROCESS_CHILDREN: T:", repr(t))
            if t == "Pronunciation":
                if config.capture_pronunciation:
                    parse_pronunciation(node)
                    if "sounds" not in etym_data and "sounds" not in base:
                        config.warning("no pronunciations found from "
                                       "pronunciation section")
            elif t.startswith("Etymology"):
                push_etym()
                config.pos = None
                # XXX parse etymology section, up to the next subtitle
            elif pos in part_of_speech_map:
                push_pos()
                dt = part_of_speech_map[pos]
                pos = dt["pos"]
                config.pos = pos
                if "warning" in dt:
                    config.warning("{}: {}".format(t, dt["warning"]))
                if "error" in dt:
                    config.error("{}: {}".format(t, dt["error"]))
                # Parse word senses for the part-of-speech
                if "tags" in dt:
                    data_extend(config, pos_data, "tags", dt["tags"])
                parse_part_of_speech(node, pos)
            elif t == "Translations":
                if stack[-1] in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                parse_translations(data, node)
            elif t in ("Declension", "Conjugation"):
                parse_declension_conjugation(node)
            elif pos in ("hypernyms", "hyponyms", "antonyms", "synonyms",
                         "abbreviations", "proverbs"):
                if stack[-1] in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                parse_linkage(data, pos, node)
            elif pos == "compounds":
                if stack[-1] in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                if config.capture_compounds:
                    parse_linkage(data, "compounds", node)
            elif pos == "derived terms":
                if stack[-1] in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                parse_linkage(data, "derived", node)
            elif pos in ("related terms", "related characters"):
                if stack[-1] in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                parse_linkage(data, "related", node)
            elif pos == "coordinate terms":
                if stack[-1] in part_of_speech_map:
                    data = pos_data
                else:
                    data = etym_data
                parse_linkage(data, "coordinates", node)
            elif t in ("Anagrams", "Further reading", "References",
                       "Quotations", "Descendants"):
                pass

            # XXX parse interesting templates also from other sections.  E.g.,
            # {{Letter|...}} in ===See also===
            # Also <gallery>

            # Recurse to children of this node, processing subtitles therein
            stack.append(pos)
            process_children(node)
            stack.pop()

    # Process the section
    stack.append("TOP")
    process_children(langnode)
    stack.pop()

    # Finalize word entires
    push_etym()
    ret = []
    for data in page_datas:
        merge_base(data, base)
        # XXX merge any other data that should be merged from other parts of
        # the page or from related pages
        ret.append(data)

    return ret


def parse_top_template(config, ctx, node):
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(node, WikiNode)

    def template_fn(name, ht):
        if name == "also":
            # XXX shows related words that might really have been the intended
            # word, capture them
            return ""
        config.warning("UNIMPLEMENTED top-level template: {} {}"
                       .format(name, ht))
        return ""

    clean_node(config, ctx, [node], template_fn=template_fn)


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

    if config.verbose:
        print("Parsing page:", word)

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
    config.subsection = None

    # Parse the page, pre-expanding those templates that are likely to
    # influence parsing
    ctx.start_page(word)
    tree = ctx.parse(text, pre_expand=True)

    # Iterate over top-level titles, which should be languages for normal
    # pages
    by_lang = collections.defaultdict(list)
    for langnode in tree.children:
        if not isinstance(langnode, WikiNode):
            continue
        if langnode.kind == NodeKind.TEMPLATE:
            parse_top_template(config, ctx, langnode)
            continue
        if langnode.kind != NodeKind.LEVEL2:
            ctx.error("unexpected top-level node: {}".format(langnode))
            continue
        lang = clean_node(config, ctx, langnode.args)
        if lang not in languages_by_name:
            ctx.error("unrecognized language name at top-level {!r}"
                      .format(lang))
            continue
        if config.capture_languages and lang not in config.capture_languages:
            continue
        langdata = languages_by_name[lang]
        lang_code = langdata["code"]
        config.language = lang

        # Collect all words from the page.
        datas = parse_language(ctx, config, langnode, lang, lang_code)

        # Do some post-processing on the words.  For example, we may distribute
        # conjugation information to all the words.
        for data in datas:
            if "lang" not in data:
                config.debug("no lang in data: {}".format(data))
                continue
            by_lang[data["lang"]].append(data)

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
                        data["conjugation"] = conjs
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
                    data["topics"] = new_topics
        ret.extend(lang_datas)
    # Return the resulting words
    return ret


def clean_node(config, ctx, value, template_fn=None):
    """Expands the node to text, cleaning up any HTML and duplicate spaces.
    This is intended for expanding things like glosses for a single sense."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert template_fn is None or callable(template_fn)
    # print("CLEAN_NODE:", repr(value))

    def recurse(value):
        if isinstance(value, str):
            ret = value
        elif isinstance(value, (list, tuple)):
            ret = "".join(map(recurse, value))
        elif isinstance(value, WikiNode):
            ret = ctx.node_to_html(value, template_fn=template_fn)
        else:
            ret = str(value)
        return ret

    v = recurse(value)
    v = clean_value(config, v)
    # Strip any unhandled templates and other stuff.  This is mostly intended
    # to clean up erroneous codings in the original text.
    v = re.sub(r"(?s)\{\{.*", "", v)
    return v

# XXX cf "word" translations under "watchword" and "proverb" - what kind of
# link/ext is this?  {{trans-see|watchword}}

# XXX for translations, when there is more than one sense in the correct
# part-of-speech, mark translations as inexact (we don't usually know which
# sense they refer to)

# XXX Review link extraction code - which cases are not yet handled?

# XXX add parsing chinese pronunciations, see 傻瓜 https://en.wiktionary.org/wiki/%E5%82%BB%E7%93%9C#Chinese

# XXX need to change when html.unescape is called to decode html entities.
# Now done in node_to_text, but must be moved to some later step to
# distinguish IPA brackets from [https://...] links.  Fix clean, it should
# remove link brackets.  Fix related tests.

# XXX implement parsing {{ja-see-kango|xxx}} specially, see むひ

# XXX handle <ruby> specially in clean or perhaps already earler, see
# e.g. 無比 (Japanese)

# XXX test ISBN / Japanese - how does word entry work, how do synonyms
# work (relates to <ruby> handling)

# XXX linkages may have senses, e.g. "singular" English "(being only one):"

# XXX check use of sense numbers in translations

# XXX check how common are "## especially ''[[Pica pica]]'' as in "magpie"

# XXX capture {{taxlink|...}} and {{verb|...}} in linkage and gloss.
# Handle the parenthesized expression.  Note that sometimes it is not taxlink,
# just an italicized link in parenthesis

# XXX debug and fix "The gender specification "{{{g}}}" is not valid" error

# XXX figure out:  (maybe string vs. ustring error in my lua code?)
# duck: ERROR: invalid unicode returned by ('translations', 'show') parent ('Template:t', {1: 'xal', 2: 'нуһсн'}) at ['duck', 't', '#invoke', 'Lua:translations:show()']

# XXX in Coordinate terms, handle bullet point titles like Previous:, Next:
# (see "ten", both Coordinate terms and Synonyms)

# XXX change pronunciation parsing to traverse LIST and then expand individual
# items (warn about non-list content), similar to already done for linkage

# XXX parse translations from referenced translation pages; "section link"
# is one tag that is used for this

# XXX parse synonyms and other linkages from (referenced) thesaurus pages

# XXX parse etymology; take "compound", "affix", prefix" templates and save
# as dictionaries under "compound"

# XXX extract category links under "topics"

# XXX parse "alter" tags; see where they are used (they seem to be alternate
# forms)

# XXX parse "enum" tags (args: lang, prev, next, value)

# XXX investigate linkage sections that do not contain a link. What are they
# like and how to handle them?

# XXX check use of ja-r and ja-r/args templates in linkage and capture
# hira, kana

# XXX parse <form> of ... glosses.  There are LOTS of these.

# XXX make sure parenthesized parts in the middle of form-of descriptions
# in gloss are handled properly.  Check "vise" (Swedish verb).

# XXX check translation hub

# XXX warn if no senses found for a part-of-speech

# XXX warn if no parts-of-speech found for a language

# XXX warn if no languages found for a page

# XXX check allowed head templates, see template_allowed_pos_map

# XXX test that config.capture_* options work

# XXX distinguish non-gloss definition from gloss

# XXX check "unsupported tag component 'E' warning / in "word"

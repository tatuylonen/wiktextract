# Code for parsing inflection tables.
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org.

import re
import copy
import enum
import html
import functools
import collections
import unicodedata
from wikitextprocessor import Wtp, WikiNode, NodeKind, MAGIC_FIRST
from wiktextract.config import WiktionaryConfig
from wiktextract.tags import valid_tags, tag_categories
from wiktextract.inflectiondata import infl_map, infl_start_map, infl_start_re
from wiktextract.datautils import (data_append, data_extend, freeze,
                                   split_at_comma_semi, languages_by_name)
from wiktextract.form_descriptions import (classify_desc, decode_tags,
                                           parse_head_final_tags, distw)
from wiktextract.parts_of_speech import PARTS_OF_SPEECH
from wiktextract.clean import clean_value


# Set this to a word form to debug how that is analyzed, or None to disable
debug_word = None

# Column texts that are interpreted as an empty column.
IGNORED_COLVALUES = set([
    "-", "־", "᠆", "‐", "‑", "‒", "–", "—", "―", "−",
    "⸺", "⸻", "﹘", "﹣", "－", "/", "?",
    "not used", "not applicable"])

# Languages with known badly-formatted tables, specifically where <td>-elements
# are used for cells that should be <th>. If the languages has these bad <td>s,
# then they have to be parsed heuristically to find out whether a cell is a
# header or not.
# If a language is not in this set and a cell is heuristically made a header
# or given header candidate status, there is a debug message telling of this;
# at that point, determine if the language has well or badly formatted tables,
# and if it's too much work to fix them on Wiktionary, add the language to this
# list. XXX At some point, this list will be used to block cells-as-headers
# parsing in languages not in the list. See XXX CELLS-AS-HEADERS
LANGUAGES_WITH_CELLS_AS_HEADERS = set([
    "Greek",
    ])


# These tags are never inherited from above
# XXX merge with lang_specific
noinherit_tags = set([
    "infinitive-i",
    "infinitive-i-long",
    "infinitive-ii",
    "infinitive-iii",
    "infinitive-iv",
    "infinitive-v",
])

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
    "variation of": "dummy-skip-this",  #a'/Scottish Gaelic
    "command form of": "imperative",  #a راتلل/Pashto
    "historical inflection of": "dummy-skip-this",  #kork/Norwegian Nynorsk

}
for k, v in title_contains_global_map.items():
    if any(t not in valid_tags for t in v.split()):
        print("TITLE_CONTAINS_GLOBAL_MAP UNRECOGNIZED TAG: {}: {}"
              .format(k, v))
table_hdr_ign_part = r"(Inflection|Conjugation|Declension|Mutation) of [^\s]"
table_hdr_ign_part_re = re.compile(r"(?i)(" + table_hdr_ign_part + ")")
title_contains_global_re = re.compile(
    r"(?i)(^|\b)({}|{})($|\b)"
    .format(table_hdr_ign_part,
            "|".join(re.escape(x)
                     for x in title_contains_global_map.keys())))

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
        print("TITLE_CONTAINS_WORDTAGS_MAP UNRECOGNIZED TAG: {}: {}"
              .format(k, v))
title_contains_wordtags_re = re.compile(
    r"(?i)(^|\b)({}|{})($|\b)"
    .format(table_hdr_ign_part,
            "|".join(re.escape(x)
                     for x in title_contains_wordtags_map.keys())))

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
    "Epic": "Epic",    # e.g. καλός/Greek/Adj
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
        print("TITLE_ELEMSTART_MAP UNRECOGNIZED TAG: {}: {}"
              .format(k, v))
title_elemstart_re = re.compile(
    r"^({}) "
    .format("|".join(re.escape(x) for x in title_elemstart_map.keys())))


# Certain tags are moved from headers in tables into word tags, as they always
# apply to the whole word.
TAGS_FORCED_WORDTAGS = set([
    # XXX diptote/triptote do not seem to always be global.  See
    # https://en.wiktionary.org/wiki/%D8%AC%D8%A7%D8%B0%D8%A8
    # (جاذب/Arabic/Verb)
    # "diptote",
    # "triptote",
])


# Language-specific configuration for various aspects of inflection table
# parsing.
lang_specific = {
    "default": {
        "hdr_expand_first": set(["number", "mood", "referent", "aspect",
                                 "tense", "voice", "non-finite", "case",
                                 "possession"]),
        "hdr_expand_cont": set(["person", "gender", "number", "degree",
                                "polarity", "voice", "misc"]),
        "animate_inanimate_remove": True,
        "both_active_passive_remove": True,
        "both_strong_weak_remove": True,
        "definitenesses": ["indefinite", "definite"],
        "empty_row_resets": False,
        "form_transformations": [],
        "genders": None,
        "imperative_no_tense": False,
        "masc_only_animate": False,  # Slavic special
        "numbers": ["singular", "plural"],
        "persons": ["first-person", "second-person", "third-person"],
        "pl_virile_nonvirile": False,
        "reuse_cellspan": "skip",  # stop/skip/reuse
        "skip_mood_mood": False,
        "skip_tense_tense": False,
        "stop_non_finite_non_finite": True,
        "stop_non_finite_voice": False,
        "stop_non_finite_tense": False,
        "strengths": ["strong", "weak"],
        "virile_nonvirile_remove": True,
        "voices": ["active", "passive"],
        "special_splits": {},  # value: (splits, tags)
    },
    "austronesian-group": {
        "numbers": ["singular", "dual", "plural"],
    },
    "bantu-group": {
        "genders": None,
    },
    "indo-european-group": {
        "genders": ["masculine", "feminine", "neuter"],
        "numbers": ["singular", "plural"],
    },
    "romance-group": {
    },
    "slavic-group": {
        "numbers": ["singular", "plural", "dual"],
        "masc_only_animate": True,
    },
    "samojedic-group": {
        "next": "uralic-group",
    },
    "semitic-group": {
        "numbers": ["singular", "dual", "plural"],
        "definitenesses": ["indefinite", "definite", "construct"],
    },
    "uralic-group": {
        "numbers": ["singular", "dual", "plural"],
    },
    "Akkadian": {
        "next": "semitic-group",
    },
    "Amharic": {
        "next": "semitic-group",
    },
    "Ancient Greek": {
        "next": "Proto-Indo-European",  # Has dual
    },
    # "Anejom̃": {
    #     "numbers": ["singular", "dual", "trial", "plural"],
    # },
    "Arabic": {
        "next": "semitic-group",
        "numbers": ["singular", "dual", "paucal", "plural", "collective", "singulative"],
        "reuse_cellspan": "reuse",
        "hdr_expand_first": set(["number"]),
        "hdr_expand_cont": set(["gender", "referent", "misc", "number",
                                "class"]),
    },
    "Aragonese": {
        "next": "romance-group",
    },
    "Aromanian": {
        "next": "romance-group",
    },
    "Aramaic": {
        "next": "semitic-group",
    },
    "Avestan": {
        "next": "Proto-Indo-European",
    },
    "Baiso": {
        "numbers": ["singular", "paucal", "plural"],
    },
    "Belarusian": {
        "next": "slavic-group",
    },
    "Bende": {
        "next": "bantu-group",
    },
    # "Berber": {
    #     "definitenesses": ["indefinite", "definite", "construct"],
    # },
    "Catalan": {
        "next": "romance-group",
    },
    "Chichewa": {
        "next": "bantu-group",
    },
    "Chimwiini": {
        "next": "bantu-group",
    },
    "Corsican": {
        "next": "romance-group",
    },
    "Czech": {
        "next": "slavic-group",
        "hdr_expand_first": set(["tense", "mood", "non-finite"]),
        "hdr_expand_cont": set(["tense", "mood", "voice"]),
    },
    "Dalmatian": {
        "next": "romance-group",
    },
    "Danish": {
        "genders": ["common-gender", "feminine", "masculine", "neuter"],
        "form_transformations": [
            ["noun", "^\(as a measure\) ", "", ""],
        ],
    },
    "Eblaite": {
        "next": "semitic-group",
    },
    "Egyptian": {
        "definitenesses": ["indefinite", "definite", "construct"],
    },
    "Emilian": {
        "next": "romance-group",
    },
    "English": {
        "stop_non_finite_tense": True,  # affect/English/Verb
        "form_transformations": [
            ["verb", r"^\(to\) ", "", ""],
            ["verb", "^to ", "", ""],
            ["verb", r"^I ", "", "first-person singular"],
            ["verb", r"^you ", "", "second-person"],
            ["verb", r"^he ", "", "third-person singular"],
            ["verb", r"^we ", "", "first-person plural"],
            ["verb", r"^you ", "", "second-person plural"],
            ["verb", r"^they ", "", "third-person plural"],
            ["verb", r"^it ", "", "third-person singular"],
            ["verb", r"^thou ", "", "second-person singular"],
            ["verb", r"^ye ", "", "second-person plural"],
            ["verb", r" \(thou\)$", "", "second-person singular"],
            ["verb", r" \(ye\)$", "", "second-person plural"],
            ["verb", r"^he/she/it ", "", "third-person singular"],
            ["verb", r"^he/she/it/they ", "", "third-person singular"],
            ["verb", r"\bhim/her/it/them ", "", "third-person singular"],
            ["verb", r"\bthem ", "", "third-person plural"],
            ["verb", r"\bus ", "", "first-person plural"],
            ["verb", r"\bme ", "", "first-person singular"],
        ],
        "special_splits": {
            "let’s be": [["let's be"], "first-person plural pronoun-included"],
            "I am (’m)/be": [["am (’m)", "be"], "first-person singular"],
            "we are (’re)/be/been": [["are (’re)", "be", "been"],
                                     "first-person plural"],
            "thou art (’rt)/beest": [["art (’rt)", "beest"],
                                     "second-person singular"],
            "ye are (’re)/be/been": [["are (’re)", "be", "been"],
                                     "second-person plural"],
            "thou be/beest": [["be", "beest"], "second-person singular"],
            "he/she/it is (’s)/beeth/bes": [["is (’s)", "beeth", "bes"],
                                            "third-person singular"],
            "they are (’re)/be/been": [["are (’re)", "be", "been"],
                                       "third-person plural"],
            "thou wert/wast": [["wert", "wast"],
                               "second-person singular"],
            "thou were/wert": [["were", "wert"],
                               "second-person singular"],
            "there has been": [["there has been"], "singular"],
            "there have been": [["there have been"], "plural"],
            "there is ('s)": [["there is", "there's"], "singular"],
            "there are ('re)": [["there are", "there're"], "plural"],
            "there was": [["there was"], "singular"],
            "there were": [["there were"], "plural"],
        },
    },
    "Estonian": {
        "hdr_expand_first": set(["non-finite"]),
        "hdr_expand_cont": set(["voice"]),
    },
    "Fijian": {
        "numbers": ["singular", "paucal", "plural"],
    },
    "Finnish": {
        "hdr_expand_first": set([]),
    },
    "French": {
        "next": "romance-group",
    },
    "Friulian": {
        "next": "romance-group",
    },
    "Galician": {
        "next": "romance-group",
    },
    "German": {
        "next": "Proto-Germanic",
        "form_transformations": [
            ["verb", "^ich ", "", "first-person singular"],
            ["verb", "^du ", "", "second-person singular"],
            ["verb", "^er ", "", "third-person singular"],
            ["verb", "^wir ", "", "first-person plural"],
            ["verb", "^ihr ", "", "second-person plural"],
            ["verb", "^sie ", "", "third-person plural"],
            ["verb", "^dass ich ", "",
             "first-person singular subordinate-clause"],
            ["verb", "^dass du ", "",
             "second-person singular subordinate-clause"],
            ["verb", "^dass er ", "",
             "third-person singular subordinate-clause"],
            ["verb", "^dass wir ", "",
             "first-person plural subordinate-clause"],
            ["verb", "^dass ihr ", "",
             "second-person plural subordinate-clause"],
            ["verb", "^dass sie ", "",
             "third-person plural subordinate-clause"],
            ["verb", " \(du\)$", "", "second-person singular"],
            ["verb", " \(ihr\)$", "", "second-person plural"],
            ["adj", "^er ist ", "", "masculine singular"],
            ["adj", "^sie ist ", "", "feminine singular"],
            ["adj", "^es ist ", "", "neuter singular"],
            ["adj", "^sie sind ", "", "plural"],
            ["adj", "^keine ", "keine ", "negative"],
            ["adj", "^keiner ", "keiner ", "negative"],
            ["adj", "^keinen ", "keinen ", "negative"],
         ],
    },
    "German Low German": {
        "next": "German",
        "hdr_expand_first": set(["mood", "non-finite"]),
        "hdr_expand_cont": set(["tense"]),
    },
    "Gothic": {
        "next": "Proto-Indo-European",  # Has dual
    },
    "Greek": {
        "next": "indo-european-group",
        "hdr_expand_first": set(["mood", "tense", "aspect", "dummy"]),
        "hdr_expand_cont": set(["tense", "person", "number", "aspect"]),
        "imperative_no_tense": True,
        "reuse_cellspan": "reuse",
        "skip_mood_mood": True,
        "skip_tense_tense": True,
    },
    "Hawaiian": {
        "next": "austronesian-group",
    },
    "Hebrew": {
        "next": "semitic-group",
    },
    "Hijazi Arabic": {
        "next": "semitic-group",
    },
    "Hopi": {
        "numbers": ["singular", "paucal", "plural"],
    },
    "Hungarian": {
        "hdr_expand_first": set([]),
        "hdr_expand_cont": set([]),
    },
    "Ilokano": {
        "next": "austronesian-group",
    },
    "Inari Sami": {
        "next": "samojedic-group",
    },
    "Inuktitut": {
        "numbers": ["singular", "dual", "plural"],
    },
    "Italian": {
        "next": "romance-group",
        "hdr_expand_first": set(["mood", "tense"]),
        "hdr_expand_cont": set(["person", "register", "number", "misc"]),
        "form_transformations": [
            ["verb", "^non ", "", "negative"],
        ],
    },
    "Irish": {
        "next": "Old Irish",
        "genders": ["masculine", "feminine"],
    },
    "Kamba": {
        "next": "bantu-group",
    },
    "Kapampangan": {
        "next": "austronesian-group",
    },
    # "Khoe": {
    #     "numbers": ["singular", "dual", "plural"],
    # },
    "Kikuyu": {
        "next": "bantu-group",
    },
    "Ladin": {
        "next": "romance-group",
    },
    # "Larike": {
    #     "numbers": ["singular", "dual", "trial", "plural"],
    # },
    "Latin": {
        "next": "romance-group",
        "stop_non_finite_voice": True,
    },
    "Latvian": {
        "empty_row_resets": True,
    },
    "Ligurian": {
        "next": "romance-group",
    },
    "Lihir": {
       "numbers": ["singular", "dual", "trial", "paucal", "plural"],
    },
    "Lingala": {
        "next": "bantu-group",
    },
    "Lombard": {
        "next": "romance-group",
    },
    "Lower Sorbian": {
        "next": "slavic-group",
    },
    "Luganda": {
        "next": "bantu-group",
    },
    "Lule Sami": {
        "next": "samojedic-group",
    },
    "Maltese": {
        "next": "semitic-group",
    },
    "Maore Comorian": {
        "next": "bantu-group",
    },
    "Masaba": {
        "next": "bantu-group",
    },
    "Mirandese": {
        "next": "romance-group",
    },
    "Moroccan Arabic": {
        "next": "semitic-group",
    },
    # "Motuna": {
    #     "numbers": ["singular", "paucal", "plural"],
    # },
    "Mwali Comorian": {
        "next": "bantu-group",
    },
    "Mwani": {
        "next": "bantu-group",
    },
    "Navajo": {
        "numbers": ["singular", "plural", "dual", "duoplural",],
    },
    "Neapolitan": {
        "next": "romance-group",
    },
    "Nenets": {
        "next": "uralic-group",
    },
    "Ngazidja Comorian": {
        "next": "bantu-group",
    },
    "Niuean": {
        "next": "austronesian-group",
    },
    "Northern Kurdish": {
        "numbers": ["singular", "paucal", "plural"],
    },
    "Northern Ndebele": {
        "next": "bantu-group",
    },
    "Northern Sami": {
        "next": "samojedic-group",
    },
    # "Mussau": {
    #     "numbers": ["singular", "dual", "trial", "plural"],
    # },
    "Nyankole": {
        "next": "bantu-group",
    },
    "Occitan": {
        "next": "romance-group",
    },
    "Old Church Slavonic": {
        "next": "Proto-Indo-European",  # Has dual
    },
    "Old English": {
        "next": "Proto-Indo-European",  # Had dual in pronouns
    },
    "Old Norse": {
        "next": "Proto-Indo-European",  # Had dual in pronouns
    },
    "Old Irish": {
        "next": "Proto-Indo-European",  # Has dual
    },
    "Phoenician": {
        "next": "semitic-group",
    },
    "Phuthi": {
        "next": "bantu-group",
    },
    "Pite Sami": {
        "next": "samojedic-group",
    },
    "Polish": {
        "next": "slavic-group",
    },
    "Portuguese": {
        "next": "romance-group",
        "genders": ["masculine", "feminine"],
    },
    "Proto-Germanic": {
        "next": "Proto-Indo-European",  # Has dual
    },
    "Proto-Indo-European": {
        "numbers": ["singular", "dual", "plural"],
    },
    "Proto-Samic": {
        "next": "samojedic-group",
    },
    "Proto-Uralic": {
        "next": "uralic-group",
    },
    "Raga": {
        "numbers": ["singular", "dual", "trial", "plural"],
    },
    "Romagnol": {
        "next": "romance-group",
    },
    "Romanian": {
        "next": "romance-group",
    },
    "Romansch": {
        "next": "romance-group",
    },
    "Russian": {
        "next": "slavic-group",
        "hdr_expand_first": set(["non-finite", "mood", "tense"]),
        "hdr_expand_cont": set(["tense", "number"]),
        "reuse_cellspan": "stop",
    },
    "Rwanda-Rundi": {
        "next": "bantu-group",
    },
    "Sanskrit": {
        "next": "Proto-Indo-European",
    },
    "Sardinian": {
        "next": "romance-group",
    },
    "Sassarese": {
        "next": "romance-group",
    },
    "Scottish Gaelic": {
        "numbers": ["singular", "dual", "plural"],
    },
    "Serbo-Croatian": {
        "next": "slavic-group",
        "numbers": ["singular", "dual", "paucal", "plural"],
    },
    "Sicilian": {
        "next": "romance-group",
    },
    "Skolt Sami": {
        "next": "samojedic-group",
    },
    "Slovene": {
        "next": "slavic-group",
    },
    "Shona": {
        "next": "bantu-group",
    },
    "Sotho": {
        "next": "bantu-group",
    },
    "South Levantine Arabic": {
        "next": "semitic-group",
    },
    "Southern Ndebele": {
        "next": "bantu-group",
    },
    "Spanish": {
        "next": "romance-group",
        "form_transformations": [
            ["verb", "^no ", "", "negative"],
        ],
    },
    "Swahili": {
        "next": "bantu-group",
    },
    "Swedish": {
        "hdr_expand_first": set(["referent"]),
        "hdr_expand_cont": set(["degree", "polarity"]),
        "genders": ["common-gender", "feminine", "masculine", "neuter"],
    },
    "Swazi": {
        "next": "bantu-group",
    },
    # "Syriac": {
    #     "next": "semitic-group",
    # },
    "Tagalog": {
        "next": "austronesian-group",
    },
    "Tausug": {
        "next": "austronesian-group",
    },
    "Tigre": {
        "next": "semitic-group",
    },
    "Tigrinya": {
        "next": "semitic-group",
    },
    "Tongan": {
        "next": "austronesian-group",
    },
    "Tsonga": {
        "next": "bantu-group",
    },
    "Tswana": {
        "next": "bantu-group",
    },
    "Tumbuka": {
        "next": "bantu-group",
    },
    # "Tuscan": {
    #     "next": "romance-group",
    # },
    "Ugaritic": {
        "next": "semitic-group",
    },
    "Ukrainian": {
        "next": "slavic-group",
    },
    "Upper Sorbian": {
        "next": "slavic-group",
    },
    # "Valencian": {
    #     "next": "romance-group",
    # },
    "Venetian": {
        "next": "romance-group",
    },
    "Warlpiri": {
        "numbers": ["singular", "paucal", "plural"],
    },
    "Xhosa": {
        "next": "bantu-group",
    },
    "Zulu": {
        "next": "bantu-group",
    },
    "ǃXóõ": {
        "next": "bantu-group",
    },
}
# Sanity check lang_specific
def_ls_keys = lang_specific["default"].keys()
for k, v in lang_specific.items():
    if k[0].isupper() and k not in languages_by_name:
        raise AssertionError("key {!r} in lang_specific is not a valid language"
                             .format(k))
    assert isinstance(v, dict)
    for kk, vv in v.items():
        if kk not in def_ls_keys and kk != "next":
            raise AssertionError("{} key {!r} not in default entry"
                                 .format(k, kk))
        if kk in ("hdr_expand_first", "hdr_expand_cont"):
            if not isinstance(vv, set):
                raise AssertionError("{} key {!r} must be set"
                                     .format(lang, kk))
            for t in vv:
                if t not in tag_categories:
                    raise AssertionError("{} key {!r} invalid tag category {}"
                                         .format(k, kk, t))
        elif kk in ("genders", "numbers", "persons", "strengths", "voices"):
            if not vv:
                continue
            if not isinstance(vv, (list, tuple, set)):
                raise AssertionError("{} key {!r} must be list/tuple/set"
                                     .format(k, kk))
            for t in vv:
                if t not in valid_tags:
                    raise AssertionError("{} key {!r} invalid tag {!r}"
                                         .format(k, kk, t))
        elif kk == "next":
            if vv not in lang_specific:
                raise AssertionError("{} key {!r} value {!r} is not defined"
                                     .format(k, kk, vv))

def get_lang_specific(lang, field):
    """Returns the given field from language-specific data or "default"
    if the language is not listed or does not have the field."""
    assert isinstance(lang, str)
    assert isinstance(field, str)
    while True:
        dt = lang_specific.get(lang)
        if dt is None:
            if lang == "default":
                raise RuntimeError("Invalid lang_specific field {!r}"
                                   .format(field))
            lang = "default"
        else:
            if field in dt:
                return dt[field]
            lang = dt.get("next", "default")
    if dt is None or field not in dt:
        dt = lang_specific.get("default")
    assert field in dt
    return dt[field]


# Tag combination mappings for specific languages/part-of-speech.  These are
# used as a post-processing step for forms extracted from tables.  Each
# element has list of languages, list of part-of-speech, and one or more
# source set - replacement set pairs.
lang_tag_mappings = [
    [["Armenian"], ["noun"],
     [["possessive", "singular"], ["possessive", "possessive-single"]],
     [["possessive", "plural"], ["possessive", "possessive-many"]],
    ],
]
for lst in lang_tag_mappings:
    assert len(lst) >= 3
    assert all(isinstance(x, str) for x in lst[0])  # languages
    assert all(x in PARTS_OF_SPEECH for x in lst[1])  # parts of speech
    for src, dst in lst[2:]:
        assert all(t in valid_tags for t in src)
        assert all(t in valid_tags for t in dst)


class InflCell(object):
    """Cell in an inflection table."""
    __slots__ = (
        "text",
        "is_title",
        "start",
        "colspan",
        "rowspan",
        "target",
    )
    def __init__(self, text, is_title, start, colspan, rowspan, target):
        assert isinstance(text, str)
        assert is_title in (True, False)
        assert isinstance(start, int)
        assert isinstance(colspan, int) and colspan >= 1
        assert isinstance(rowspan, int) and rowspan >= 1
        assert target is None or isinstance(target, str)
        self.text = text.strip()
        self.is_title = text and is_title
        self.colspan = colspan
        self.rowspan = rowspan
        self.target = target
    def __str__(self):
        v = "{}/{}/{}/{!r}".format(
                self.text, self.is_title, self.colspan, self.rowspan)
        if self.target:
            v += ": {!r}".format(self.target)
        return v
    def __repr__(self):
        return str(self)


class HdrSpan(object):
    """Saved information about a header cell/span during the parsing
    of a table."""
    __slots__ = (
        "start",
        "colspan",
        "rowspan",
        "rownum",      # Row number where this occurred
        "tagsets",  # list of tuples
        "used",  # At least one text cell after this
        "text",  # For debugging
        "all_headers_row",
        "expanded",  # The header has been expanded to cover whole row/part
    )
    def __init__(self, start, colspan, rowspan, rownum, tagsets,
                 text, all_headers_row):
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
        self.used = False
        self.text = text
        self.all_headers_row = all_headers_row
        self.expanded = False


def is_superscript(ch):
    """Returns True if the argument is a superscript character."""
    assert isinstance(ch, str) and len(ch) == 1
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return False
    return re.match(r"SUPERSCRIPT |MODIFIER LETTER SMALL ", name) is not None


def remove_useless_tags(lang, pos, tags):
    """Remove certain tag combinations from ``tags`` when they serve no purpose
    together (cover all options)."""
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(tags, set)
    if ("animate" in tags and "inanimate" in tags and
        get_lang_specific(lang, "animate_inanimate_remove")):
        tags.remove("animate")
        tags.remove("inanimate")
    if ("virile" in tags and "nonvirile" in tags and
        get_lang_specific(lang, "virile_nonvirile_remove")):
        tags.remove("virile")
        tags.remove("nonvirile")
    # If all numbers in the language are listed, remove them all
    numbers = get_lang_specific(lang, "numbers")
    if numbers and all(x in tags for x in numbers):
        for x in numbers:
            tags.remove(x)
    # If all genders in the language are listed, remove them all
    genders = get_lang_specific(lang, "genders")
    if genders and all(x in tags for x in genders):
        for x in genders:
            tags.remove(x)
    # If all voices in the language are listed, remove them all
    voices = get_lang_specific(lang, "voices")
    if voices and all(x in tags for x in voices):
        for x in voices:
            tags.remove(x)
    # If all strengths of the language are listed, remove them all
    strengths = get_lang_specific(lang, "strengths")
    if strengths and all(x in tags for x in strengths):
        for x in strengths:
            tags.remove(x)
    # If all persons of the language are listed, remove them all
    persons = get_lang_specific(lang, "persons")
    if persons and all(x in tags for x in persons):
        for x in persons:
            tags.remove(x)
    # If all definitenesses of the language are listed, remove them all
    definitenesses = get_lang_specific(lang, "definitenesses")
    if definitenesses and all(x in tags for x in definitenesses):
        for x in definitenesses:
            tags.remove(x)


def tagset_cats(tagset):
    """Returns a set of tag categories for the tagset (merged from all
    alternatives)."""
    return set(valid_tags[t]
               for ts in tagset
               for t in ts)


def or_tagsets(lang, pos, tagsets1, tagsets2):
    """Merges two tagsets (the new tagset just merges the tags from both, in
    all combinations).  If they contain simple alternatives (differ in
    only one category), they are simply merged; otherwise they are split to
    more alternatives.  The tagsets are assumed be sets of sorted tuples."""
    assert isinstance(tagsets1, list)
    assert all(isinstance(x, tuple) for x in tagsets1)
    assert isinstance(tagsets2, list)
    assert all(isinstance(x, tuple) for x in tagsets1)
    tagsets = []  # This will be the result

    def add_tags(tags1):
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
                    if (tags1_in_cat != tags2_in_cat or
                        not tags1_in_cat or not tags2_in_cat):
                        num_differ += 1
                        if not tags1_in_cat or not tags2_in_cat:
                            # Prevent merging if one is empty
                            num_differ += 1
            # print("tags1={} tags2={} num_differ={}"
            #       .format(tags1, tags2, num_differ))
            if num_differ <= 1:
                # Yes, they can be merged
                tagsets.remove(tags2)
                tags = set(tags1) | set(tags2)
                remove_useless_tags(lang, pos, tags)
                tags = tuple(sorted(tags))
                add_tags(tags)  # Could result in further merging
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
def clean_header(word, col):
    """Cleans a row/column header for later processing.  This returns
    (cleaned, refs, defs, tags)."""
    # print("CLEAN_HEADER {!r}".format(col))
    hdr_tags = []
    orig_col = col
    # XXX this is used in Greek, but perhaps better to use separate infl_map
    # entries.  Pending removal:
    # XXX col = re.sub(r"(?s)\s*➤\s*$", "", col)
    col = re.sub(r"(?s)\s*,\s*$", "", col)
    col = re.sub(r"(?s)\s*•\s*$", "", col)
    col = re.sub(r"\s+", " ", col)
    col = col.strip()
    if re.search(r"^\s*(There are |"
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
                col):
        return "dummy-ignored-text-cell", [], [], []
    # Temporarily remove final parenthesized part (if separated by whitespace),
    # so that we can extract reference markers before it.
    final_paren = ""
    m = re.search(r"\s+\([^)]*\)$", col)
    if m is not None:
        final_paren = m.group(0)
        col = col[:m.start()]

    # ᴺᴸᴴ persin/Old Irish <- where does this go?? -KJ
    # Extract references and tag markers
    refs = []
    def_re = re.compile(r"(^|\s*•?\s+)"
                        r"((\*+|[△†0123456789⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+)([⁾):]|\s)|"
                        r"\^(\*+|[△†]))")
    nondef_re = re.compile(r"^\s*(1|2|3)\s+(sg|pl)\s*$")
    while True:
        m = re.search(r"\^(.|\([^)]*\))$", col)
        if not m:
            break
        r = m.group(1)
        if r.startswith("(") and r.endswith(")"):
            r = r[1:-1]
        if r == "rare":
            hdr_tags.append("rare")
        elif r == "vos":
            hdr_tags.append("informal")
            hdr_tags.append("vos-form")
            hdr_tags.append("second-person")
            hdr_tags.append("singular")
        elif r == "tú":
            hdr_tags.append("informal")
            hdr_tags.append("second-person")
            hdr_tags.append("singular")
        else:
            v = m.group(1)
            if v.startswith("(") and v.endswith(")"):
                v = v[1:-1]
            refs.append(v)
        col = col[:m.start()]

    # See if it is a ref definition
    # print("BEFORE REF CHECK: {!r}".format(col))
    m = re.match(def_re, col)
    if m and not re.match(nondef_re, col):
        ofs = 0
        ref = None
        deflst = []
        for m in re.finditer(def_re, col):
            if ref:
                deflst.append((ref, col[ofs:m.start()].strip()))
            ref = m.group(3) or m.group(5)
            ofs = m.end()
        if ref:
            deflst.append((ref, col[ofs:].strip()))
        return "", [], deflst, []

    # See if it references a definition
    while col:
        if (is_superscript(col[-1]) or col[-1] in ("†",)):
            if col.endswith("ʳᵃʳᵉ"):
                hdr_tags.append("rare")
                col = col[:-4].strip()
                continue
            if col.endswith("ᵛᵒˢ"):
                hdr_tags.append("informal")
                hdr_tags.append("vos-form")
                hdr_tags.append("second-person")
                hdr_tags.append("singular")
                col = col[:-3].strip()
                continue
            # Numbers and H/L/N are useful information
            refs.append(col[-1])
            col = col[:-1]
        else:
            break

    # Check for another form of note definition
    if (len(col) > 2 and col[1] in (")", " ", ":") and
        col[0].isdigit() and
        not re.match(nondef_re, col)):
        return "", [], [[col[0], col[2:].strip()]], []
    col = col.strip()

    # Extract final "*" reference symbols.  Sometimes there are multiple.
    m = re.search(r"\*+$", col)
    if m is not None:
        col = col[:m.start()]
        refs.append(m.group(0))
    if col.endswith("(*)"):
        col = col[:-3].strip()
        refs.append("*")

    # Put back the final parenthesized part
    col = col.strip() + final_paren

    # print("CLEAN_HEADER: orig_col={!r} col={!r} refs={!r} hdr_tags={}"
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
    # XXX This code section causes crashes, e.g. "i" 2022-07-05.
    # (infl_map can contain conditional expressions, which are dicts,
    # and this code assumes it contains strings.  Also, this does not
    # appear necessary.  Any tags coming from full titles should be handled
    # by separate tables/regexps if needed.)
    # XXX this code is pending removal after testing
    # Check for the case that the title is in infl_map
    #if title in infl_map:
    #    return infl_map[title].split(), [], []
    #if title.lower() in infl_map:
    #    return infl_map[title.lower()].split(), [], []
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
    for m in re.finditer(r"\b([\w/]+-type|accent-\w+|"
                         r"[\w/]+-stem|[^ ]+ gradation|"
                         r"\b(stem in [\w/ ]+)|"
                         r"[^ ]+ alternation|(First|Second|Third|Fourth|Fifth|"
                         r"Sixth|Seventh) (Conjugation|declension)|"
                         r"First and second declension|"
                         r"(1st|2nd|3rd|4th|5th|6th) declension|"
                         r"\w[\w/ ]* harmony)\b", title):
        dt = {"form": m.group(1),
              "source": source,
              "tags": ["class"]}
        extra_forms.append(dt)
    # Parse parenthesized part from title
    for m in re.finditer(r"\(([^)]*)\)", title):
        for elem in m.group(1).split(","):
            elem = elem.strip()
            if elem in title_elements_map:
                table_tags.extend(title_elements_map[elem].split())
            else:
                m = re.match(title_elemstart_re, elem)
                if m:
                    tags = title_elemstart_map[m.group(1)].split()
                    dt = {"form": elem[m.end():],
                          "source": source,
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
                  "source": source}
            extra_forms.append(dt)
        for elem in title.split(","):
            elem = elem.strip()
            if elem in title_elements_map:
                table_tags.extend(title_elements_map[elem].split())
            elif elem.endswith("-stem"):
                dt = {"form": elem,
                      "tags": ["class"],
                      "source": source}
                extra_forms.append(dt)
    return global_tags, table_tags, extra_forms


def expand_header(config, ctx, word, lang, pos, text, tags0, silent=False,
                  ignore_tags=False):
    """Expands a cell header to tagset, handling conditional expressions
    in infl_map.  This returns list of tuples of tags, each list element
    describing an alternative interpretation.  ``tags0`` is combined
    column and row tags for the cell in which the text is being interpreted
    (conditional expressions in inflection data may depend on it).
    If ``silent`` is True, then no warnings will be printed.  If ``ignore_tags``
    is True, then tags listed in "if" will be ignored in the test (this is
    used when trying to heuristically detect whether a non-<th> cell is anyway
    a header)."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(tags0, (list, tuple, set))
    assert silent in (True, False)
    # print("EXPAND_HDR: text={!r} tags0={!r}".format(text, tags0))
    # First map the text using the inflection map
    text = clean_value(config, text)
    combined_return = []
    parts = split_at_comma_semi(text, separators=[";"])
    for text in parts:
        if not text:
            continue
        if text in infl_map:
            v = infl_map[text]
        else:
            m = re.match(infl_start_re, text)
            if m is not None:
                v = infl_start_map[m.group(1)]
                # print("INFL_START {} -> {}".format(text, v))
            elif re.match(r"Notes", text):
                # Ignored header
                # print("IGNORING NOTES")
                combined_return = or_tagsets(lang, pos, combined_return,
                                             [("dummy-skip-this",)])
                continue
            elif text in IGNORED_COLVALUES:
                combined_return = or_tagsets(lang, pos, combined_return,
                                             [("dummy-ignore-skipped",)])
                continue
            # Try without final parenthesized part
            text_without_parens = re.sub(r"[,/]?\s+\([^)]*\)\s*$", "", text)
            if text_without_parens in infl_map:
                v = infl_map[text_without_parens]
            elif m is None:
                if not silent:
                    ctx.debug("inflection table: unrecognized header: {}"
                              .format(text))
                # Unrecognized header
                combined_return = or_tagsets(lang, pos, combined_return,
                                             [("error-unrecognized-form",)])
                continue

        # Then loop interpreting the value, until the value is a simple string.
        # This may evaluate nested conditional expressions.
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
                ctx.debug("inflection table: internal: "
                          "UNIMPLEMENTED INFL_MAP VALUE: {}"
                          .format(infl_map[text]))
                tagset = [()]
                break
            # Evaluate the conditional expression.
            assert isinstance(v, dict)
            cond = "default-true"
            # Handle "lang" condition.  The value must be either a
            # single language or a list of languages, and the
            # condition evaluates to True if the table is in one of
            # those languages.
            if cond and "lang" in v:
                c = v["lang"]
                if isinstance(c, str):
                    cond = c == lang
                else:
                    assert isinstance(c, (list, tuple, set))
                    cond = lang in c
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
            # if ``tags0`` contains all of the listed tags.  If the condition
            # is of the form "any: ...tags...", then any of the tags will be
            # enough.
            if cond and "if" in v and not ignore_tags:
                c = v["if"]
                assert isinstance(c, str)
                # "if" condition is true if any of the listed tags is present if
                # it starts with "any:", otherwise all must be present
                if c.startswith("any: "):
                    cond = any(t in tags0 for t in c[5:].split())
                else:
                    cond = all(t in tags0 for t in c.split())
            # Warning message about missing conditions for debugging.
            if cond == "default-true" and not silent:
                ctx.debug("inflection table: IF MISSING COND: word={} "
                          "lang={} text={} tags0={} c={} cond={}"
                          .format(word, lang, text, tags0, c, cond))
            # Based on the result of evaluating the condition, select either
            # "then" part or "else" part.
            if cond:
                v = v.get("then", "")
            else:
                v = v.get("else")
                if v is None:
                    if not silent:
                        ctx.debug("inflection table: IF WITHOUT ELSE EVALS "
                                  "False: "
                                  "{}/{} {!r} tags0={}"
                                  .format(word, lang, text, tags0))
                    v = "error-unrecognized-form"

        # Merge the resulting tagset from this header part with the other
        # tagsets from the whole header
        combined_return = or_tagsets(lang, pos, combined_return, tagset)

    # Return the combined tagsets, or empty tagset if we got no tagsets
    if not combined_return:
        combined_return = [()]
    return combined_return


def compute_coltags(lang, pos, hdrspans, start, colspan, mark_used, celltext):
    """Computes column tags for a column of the given width based on the
    current header spans."""
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(hdrspans, list)
    assert isinstance(start, int) and start >= 0
    assert isinstance(colspan, int) and colspan >= 1
    assert mark_used in (True, False)
    assert isinstance(celltext, str)  # For debugging only
    # print("COMPUTE_COLTAGS CALLED start={} colspan={} celltext={!r}"
    #       .format(start, colspan, celltext))
    # For debugging, set this to the form for whose cell you want debug prints
    if celltext == debug_word:
        print("COMPUTE_COLTAGS CALLED start={} colspan={} celltext={!r}"
              .format(start, colspan, celltext))
        for hdrspan in hdrspans:
            print("  row={} start={} colspans={} tagsets={}"
                  .format(hdrspan.rownum, hdrspan.start, hdrspan.colspan,
                          hdrspan.tagsets))
    used = set()
    coltags = [()]
    last_header_row = 1000000
    # Iterate through the headers in reverse order, i.e., headers lower in the
    # table (closer to the cell) first.
    row_tagsets = [()]
    row_tagsets_rownum = 1000000
    used_hdrspans = set()
    for hdrspan in reversed(hdrspans):
        if (hdrspan.start + hdrspan.colspan <= start or
            hdrspan.start >= start + colspan):
            # Does not horizontally overlap current cell. Ignore this hdrspan.
            if celltext == debug_word:
                print("Ignoring row={} start={} colspan={} tagsets={}"
                      .format(hdrspan.rownum, hdrspan.start,
                              hdrspan.colspan, hdrspan.tagsets))
            continue
        # If the cell partially overlaps the current cell, assume we have
        # reached something unrelated and abort.
        if (hdrspan.start < start and
            hdrspan.start + hdrspan.colspan > start and
            hdrspan.start + hdrspan.colspan < start + colspan):
            if celltext == debug_word:
                print("break on partial overlap at start {} {} {}"
                      .format(hdrspan.start, hdrspan.colspan, hdrspan.tagsets))
            break
        if (hdrspan.start < start + colspan and
            hdrspan.start > start and
            hdrspan.start + hdrspan.colspan > start + colspan and
            not hdrspan.expanded):
            if celltext == debug_word:
                print("break on partial overlap at end {} {} {}"
                      .format(hdrspan.start, hdrspan.colspan, hdrspan.tagsets))
            break
        # Check if we have already used this cell.
        if id(hdrspan) in used_hdrspans:
            continue
        # We are going to use this cell.
        used_hdrspans.add(id(hdrspan))
        tagsets = hdrspan.tagsets
        # If the hdrspan is fully inside the current cell and does not cover
        # it fully, check if we should merge information from multiple cells.
        if (not hdrspan.expanded and
            (hdrspan.start > start or
             hdrspan.start + hdrspan.colspan < start + colspan)):
            # Multiple columns apply to the current cell, only
            # gender/number/case tags present
            # If there are no tags outside the range in any of the
            # categories included in these cells, don't add anything
            # (assume all choices valid in the language are possible).
            in_cats = set(valid_tags[t]
                          for x in hdrspans
                          if x.rownum == hdrspan.rownum and
                          x.start >= start and
                          x.start + x.colspan <= start + colspan
                          for tt in x.tagsets
                          for t in tt)
            if celltext == debug_word:
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
                if (x.start < start or
                    x.start + x.colspan > start + colspan):
                    if celltext == debug_word:
                        print("NOT IN RANGE: {} {} {}"
                              .format(x.start, x.colspan, x.tagsets))
                    includes_all_on_row = False
                    continue
                if id(x) in used_hdrspans:
                    if celltext == debug_word:
                        print("ALREADY USED: {} {} {}"
                              .format(x.start, x.colspan, x.tagsets))
                    continue
                used_hdrspans.add(id(x))
                if celltext == debug_word:
                    print("Merging into wide col: x.rownum={} "
                          "x.start={} x.colspan={} "
                          "start={} colspan={} tagsets={} x.tagsets={}"
                          .format(x.rownum, x.start, x.colspan, start, colspan,
                                  tagsets, x.tagsets))
                tagsets = or_tagsets(lang, pos, tagsets, x.tagsets)
            # If all headers on the row were included, ignore them.
            # See e.g. kunna/Swedish/Verb.
            ts_cats = tagset_cats(tagsets)
            if (includes_all_on_row or
                # Kludge, see fut/Hungarian/Verb
                ("tense" in ts_cats and "object" in ts_cats)):
                tagsets = [()]
            # For limited categories, if the category doesn't appear
            # outside, we won't include the category
            if not in_cats - set(("gender", "number", "person", "case",
                                  "category", "voice")):
                # Sometimes we have masc, fem, neut and plural, so treat
                # number and gender as the same here (if one given, look for
                # the other too)
                if "number" in in_cats or "gender" in in_cats:
                    in_cats.update(("number", "gender"))
                # Determine which categories occur outside on
                # the same row.  Ignore headers that have been expanded
                # to cover the whole row/part of it.
                out_cats = set(valid_tags[t]
                               for x in hdrspans
                               if x.rownum == hdrspan.rownum and
                               not x.expanded and
                               (x.start < start or
                                x.start + x.colspan > start + colspan)
                               for tt in x.tagsets
                               for t in tt)
                if celltext == debug_word:
                    print("in_cats={} out_cats={}"
                          .format(in_cats, out_cats))
                # Remove all inside categories that do not appear outside
                new_tagsets = []
                for ts in tagsets:
                    tags = tuple(sorted(t for t in ts
                                        if valid_tags[t] in out_cats))
                    if tags not in new_tagsets:
                        new_tagsets.append(tags)
                if celltext == debug_word and new_tagsets != tagsets:
                    print("Removed tags that do not appear outside {} -> {}"
                          .format(tagsets, new_tagsets))
                tagsets = new_tagsets
        key = (hdrspan.start, hdrspan.colspan)
        if key in used:
            if celltext == debug_word:
                print("Cellspan already used: start={} colspan={} rownum={} {}"
                      .format(hdrspan.start, hdrspan.colspan, hdrspan.rownum,
                              hdrspan.tagsets))
            action = get_lang_specific(lang, "reuse_cellspan")
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
        if mark_used:
            # XXX I don't think this case is used any more, check!
            hdrspan.used = True
        # If we have moved to a different row, merge into column tagsets
        # (we use different and_tagsets within the row)
        if row_tagsets_rownum != hdrspan.rownum:
            ret = and_tagsets(lang, pos, coltags, row_tagsets)
            if celltext == debug_word:
                print("merging rows: {} {} -> {}"
                      .format(coltags, row_tagsets, ret))
            coltags = ret
            row_tagsets = [()]
            row_tagsets_rownum = hdrspan.rownum
        # Merge into coltags
        if hdrspan.all_headers_row and hdrspan.rownum + 1 == last_header_row:
            # If this row is all headers and immediately preceeds the last
            # header we accepted, take any header from there.
            row_tagsets = and_tagsets(lang, pos, row_tagsets, tagsets)
            if celltext == debug_word:
                print("merged (next header row): {}".format(row_tagsets))
        else:
            # new_cats is for the new tags (higher up in the table)
            new_cats = tagset_cats(tagsets)
            # cur_cats is for the tags already collected (lower in the table)
            cur_cats = tagset_cats(coltags)
            if celltext == debug_word:
                print("row={} start={} colspan={} tagsets={} coltags={} "
                      "new_cats={} cur_cats={}"
                      .format(hdrspan.rownum, hdrspan.start, hdrspan.colspan,
                              tagsets, coltags, new_cats, cur_cats))
            if "detail" in new_cats:
                if not any(coltags):  # Only if no tags so far
                    coltags = or_tagsets(lang, pos, coltags, tagsets)
                if celltext == debug_word:
                    print("stopping on detail after merge")
                break
            elif ("non-finite" in cur_cats and
                  "non-finite" in new_cats):
                stop = get_lang_specific(lang, "stop_non_finite_non_finite")
                if stop:
                    if celltext == debug_word:
                        print("stopping on non-finite-non-finite")
                    break
            elif ("non-finite" in cur_cats and
                  "voice" in new_cats):
                stop = get_lang_specific(lang, "stop_non_finite_voice")
                if stop:
                    if celltext == debug_word:
                        print("stopping on non-finite-voice")
                    break
            elif ("non-finite" in new_cats and
                  cur_cats & set(("person", "number"))):
                if celltext == debug_word:
                    print("stopping on non-finite new")
                break
            elif ("non-finite" in new_cats and
                  "tense" in new_cats):
                stop = get_lang_specific(lang, "stop_non_finite_tense")
                if stop:
                    if celltext == debug_word:
                        print("stopping on non-finite new")
                    break
            elif ("non-finite" in cur_cats and
                  new_cats & set(("mood",))):
                if celltext == debug_word:
                    print("stopping on non-finite cur")
                break
            if ("tense" in new_cats and
                any("imperative" in x for x in coltags) and
                get_lang_specific(lang, "imperative_no_tense")):
                if celltext == debug_word:
                    print("skipping tense in imperative")
                continue
            elif ("mood" in new_cats and
                  "mood" in cur_cats and
                  # Allow if all new tags are already in current set
                  any(t not in ts1
                      for ts1 in coltags  # current
                      for ts2 in tagsets  # new (from above)
                      for t in ts2)):
                skip = get_lang_specific(lang, "skip_mood_mood")
                if skip:
                    if celltext == debug_word:
                        print("skipping on mood-mood")
                        # we continue to next header
                else:
                    if celltext == debug_word:
                        print("stopping on mood-mood")
                    break
            elif ("tense" in new_cats and
                  "tense" in cur_cats):
                skip = get_lang_specific(lang, "skip_tense_tense")
                if skip:
                    if celltext == debug_word:
                        print("skipping on tense-tense")
                        # we continue to next header
                else:
                    if celltext == debug_word:
                        print("stopping on tense-tense")
                    break
            elif ("aspect" in new_cats and
                  "aspect" in cur_cats):
                if celltext == debug_word:
                    print("skipping on aspect-aspect")
                continue
            elif "number" in cur_cats and "number" in new_cats:
                if celltext == debug_word:
                    print("stopping on number-number")
                break
            elif "number" in cur_cats and "gender" in new_cats:
                if celltext == debug_word:
                    print("stopping on number-gender")
                break
            elif "person" in cur_cats and "person" in new_cats:
                if celltext == debug_word:
                    print("stopping on person-person")
                break
            else:
                # Merge tags and continue to next header up/left in the table.
                row_tagsets = and_tagsets(lang, pos, row_tagsets, tagsets)
                if celltext == debug_word:
                    print("merged: {}".format(coltags))
        # Update the row number from which we have last taken headers
        last_header_row = hdrspan.rownum
    # Merge the final row tagset into coltags
    coltags = and_tagsets(lang, pos, coltags, row_tagsets)
    #print("HDRSPANS:", list((x.start, x.colspan, x.tagsets) for x in hdrspans))
    if celltext == debug_word:
        print("COMPUTE_COLTAGS {} {} {}: {}"
              .format(start, colspan, mark_used, coltags))
    assert isinstance(coltags, list)
    assert all(isinstance(x, tuple) for x in coltags)
    return coltags


def lang_specific_tags(lang, pos, form):
    """Extracts tags from the word form itself in a language-specific way.
    This may also adjust the word form.
    For example, German inflected verb forms don't have person and number
    specified in the table, but include a pronoun.  This returns adjusted
    form and a list of tags."""
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(form, str)
    rules = get_lang_specific(lang, "form_transformations")
    for patpos, pattern, dst, tags in rules:
        assert patpos in PARTS_OF_SPEECH
        if pos != patpos:
            continue
        m = re.search(pattern, form)
        if not m:
            continue
        form = form[:m.start()] + dst + form[m.end():]
        tags = tags.split()
        for t in tags:
            assert t in valid_tags
        return form, tags
    return form, []


def parse_simple_table(config, ctx, word, lang, pos, rows, titles, source,
                       after):
    """This is the default table parser.  Despite its name, it can parse
    complex tables.  This returns a list of forms to be added to the
    part-of-speech, or None if the table could not be parsed."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(rows, list)
    assert isinstance(source, str)
    assert isinstance(after, str)
    for row in rows:
        for col in row:
            assert isinstance(col, InflCell)
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)
    # print("PARSE_SIMPLE_TABLE: TITLES:", titles)
    if debug_word:
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
        split_row = (any(x.is_title and
                         x.text in ("inanimate\nanimate",)
                         for x in row) and
                     all(x.rowspan == 1
                         for x in row))
        if not split_row:
            new_rows.append(row)
            continue
        row1 = []
        row2 = []
        for cell in row:
            cell1 = copy.deepcopy(cell)
            if cell.text.find("\n") >= 0:
                # Has more than one line - split this cell
                parts = cell.text.strip().split("\n")
                if len(parts) != 2:
                    ctx.debug("forced rowspan kludge got {} parts: {!r}"
                              .format(len(parts), cell.text))
                cell2 = copy.deepcopy(cell)
                cell1.text = parts[0]
                cell2.text = parts[1]
            else:
                cell1.rowspan = 2
                cell2 = cell1
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
            d = d.split(". ")[0].strip()
            if not d:
                continue
            if d.endswith("."):
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

    # First extract definitions from cells
    for row in rows:
        for cell in row:
            text, refs, defs, hdr_tags = clean_header(word, cell.text)
            add_defs(defs)
    # Extract definitions from text after table
    text, refs, defs, hdr_tags = clean_header(word, after)
    add_defs(defs)

    # Then extract the actual forms
    ret = []
    hdrspans = []
    col_has_text = []
    rownum = 0
    title = None
    global_tags = []
    table_tags = []
    special_splits = get_lang_specific(lang, "special_splits")
    for title in titles:
        more_global_tags, more_table_tags, extra_forms = \
            parse_title(title, source)
        global_tags.extend(more_global_tags)
        table_tags.extend(more_table_tags)
        ret.extend(extra_forms)
    cell_rowcnt = collections.defaultdict(int)
    seen_cells = set()
    has_covering_hdr = set()
    some_has_covered_text = False
    for row in rows:
        # print("ROW:", row)
        if not row:
            continue  # Skip empty rows without incrementing i
        all_headers = all(x.is_title or not x.text.strip()
                          for x in row)
        text = row[0].text
        if (row[0].is_title and
            text and
            not is_superscript(text[0]) and
            text not in infl_map and  # zealous inflation map?
            (re.match(r"Inflection ", text) or
             re.sub(r"\s+", " ",
                    re.sub(r"\s*\([^)]*\)", "",
                           text)).strip() not in infl_map) and
            not re.match(infl_start_re, text) and
            all(x.is_title == row[0].is_title and
                x.text == text
                for x in row)):
            if text and title is None:
                title = text
                if re.match(r"(Note:|Notes:)", title):
                    continue
                more_global_tags, more_table_tags, extra_forms = \
                    parse_title(title, source)
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
        for j, cell in enumerate(row):
            colspan = cell.colspan
            rowspan = cell.rowspan
            previously_seen = id(cell) in seen_cells
            seen_cells.add(id(cell))
            if samecell_cnt == 0:
                # First column of a (possible multi-column) cell
                samecell_cnt = colspan - 1
            else:
                assert samecell_cnt > 0
                cell_initial = False
                samecell_cnt -= 1
                continue
            first_row_of_cell = cell_rowcnt[id(cell)] == 0
            cell_rowcnt[id(cell)] += 1
            # print("  COL:", col)
            col = cell.text
            if not col:
                continue
            row_empty = False
            is_title = cell.is_title

            # If the cell has a target, i.e., text after colon, interpret
            # it as simply specifying a value for that value and ignore
            # it otherwise.
            if cell.target:
                text, refs, defs, hdr_tags = clean_header(word, col)
                if not text:
                    continue
                refs_tags = set()
                for ref in refs:
                    if ref in def_ht:
                        refs_tags.update(def_ht[ref])
                rowtags = expand_header(config, ctx, word, lang, pos, text, [],
                                        silent=True)
                rowtags = list(set(tuple(sorted(set(x) | refs_tags))
                                   for x in rowtags))
                is_title = False
                col = cell.target

            # print(rownum, j, col)
            if is_title:
                # It is a header cell
                text, refs, defs, hdr_tags = clean_header(word, col)
                if not text:
                    continue
                # Extract tags from referenced footnotes
                refs_tags = set()
                for ref in refs:
                    if ref in def_ht:
                        refs_tags.update(def_ht[ref])

                # Expand header to tags
                v = expand_header(config, ctx, word, lang, pos, text, [],
                                  silent=True)
                # print("EXPANDED {!r} to {}".format(text, v))

                # Mark that the column has text (we are not at top)
                while len(col_has_text) <= j:
                    col_has_text.append(False)
                col_has_text[j] = True
                # Check if the header expands to reset hdrspans
                if any("!" in tt for tt in v):
                    # Reset column headers (only on first row of cell)
                    if first_row_of_cell:
                        # print("RESET HDRSPANS on: {}".format(text))
                        hdrspans = []
                    continue
                # Text between headers on a row causes earlier headers to
                # be reset
                if have_text:
                    #print("  HAVE_TEXT BEFORE HDR:", col)
                    # Reset rowtags if new title column after previous
                    # text cells
                    # XXX beware of header "—": "" - must not clear on that if
                    # it expands to no tags
                    rowtags = [()]
                have_hdr = True
                # print("HAVE_HDR: {} rowtags={}".format(col, rowtags))
                # Update rowtags and coltags
                has_covering_hdr.add(j)
                new_rowtags = []
                new_coltags = []
                all_hdr_tags = []
                for rt0 in rowtags:
                    for ct0 in compute_coltags(lang, pos, hdrspans, j,
                                               colspan, False, col):
                        tags0 = (set(rt0) | set(ct0) | set(global_tags) |
                                 set(table_tags))
                        alt_tags = expand_header(config, ctx, word, lang, pos,
                                                 text, tags0)
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
                            if (any(valid_tags[t] == "mood" for t in rt0) and
                                any(valid_tags[t] == "non-finite" for t in tt)):
                                tags = tuple(sorted(set(tt) | set(hdr_tags)))
                            else:
                                tags = tuple(sorted(set(tt) | set(rt0) |
                                                    set(hdr_tags)))
                            if tags not in new_rowtags:
                                new_rowtags.append(tags)
                rowtags = new_rowtags
                if any("dummy-skip-this" in ts for ts in rowtags):
                    continue  # Skip this cell
                new_coltags = list(x for x in new_coltags
                                   if not any(t in noinherit_tags for t in x))
                # print("new_coltags={} previously_seen={} all_hdr_tags={}"
                #       .format(new_coltags, previously_seen, all_hdr_tags))
                if any(new_coltags):
                    hdrspan = HdrSpan(j, colspan, rowspan, rownum,
                                      new_coltags, col, all_headers)
                    hdrspans.append(hdrspan)
                    # Handle headers that are above left-side header
                    # columns and are followed by personal pronouns in
                    # remaining columns (basically headers that
                    # evaluate to no tags).  In such cases widen the
                    # left-side header to the full row.
                    if previously_seen:
                        col0_followed_by_nonempty = True
                        continue
                    elif col0_hdrspan is None:
                        assert col0_hdrspan is None
                        col0_hdrspan = hdrspan
                    elif any(all_hdr_tags):
                        col0_cats = tagset_cats(col0_hdrspan.tagsets)
                        later_cats = tagset_cats(all_hdr_tags)
                        col0_allowed = get_lang_specific(lang,
                                                         "hdr_expand_first")
                        later_allowed = get_lang_specific(lang,
                                                          "hdr_expand_cont")
                        later_allowed = later_allowed | set(["dummy"])
                        # print("col0_cats={} later_cats={} "
                        #       "fol_by_nonempty={} j={} end={} "
                        #       "tagsets={}"
                        #       .format(col0_cats, later_cats,
                        #               col0_followed_by_nonempty, j,
                        #               col0_hdrspan.start +
                        #               col0_hdrspan.colspan,
                        #               col0_hdrspan.tagsets))
                        # print("col0.rowspan={} rowspan={}"
                        #       .format(col0_hdrspan.rowspan, rowspan))
                        # Only expand if col0_cats and later_cats are allowed
                        # and don't overlap and col0 has tags, and there have
                        # been no disallowed cells in between.
                        #
                        # There are three cases here:
                        #   - col0_hdrspan set, continue with allowed current
                        #   - col0_hdrspan set, expand, start new
                        #   - col0_hdrspan set, no expand, start new
                        if (not col0_followed_by_nonempty and
                            # XXX Only one cat of tags: kunna/Swedish
                            # XXX len(col0_cats) == 1 and
                            col0_hdrspan.rowspan >= rowspan and
                            not (later_cats - later_allowed) and
                            not (col0_cats & later_cats)):
                            # First case: col0 set, continue
                            continue
                        # We are going to start new col0_hdrspan.  Check if
                        # we should expand.
                        if (not col0_followed_by_nonempty and
                            not (col0_cats - col0_allowed) and
                            # XXX len(col0_cats) == 1 and
                            j > col0_hdrspan.start + col0_hdrspan.colspan):
                            # Expand current col0_hdrspan
                            # print("EXPANDING COL0 MID: {} from {} to {} "
                            #       "cols {}"
                            #       .format(col0_hdrspan.text,
                            #               col0_hdrspan.colspan,
                            #               j - col0_hdrspan.start,
                            #               col0_hdrspan.tagsets))
                            col0_hdrspan.colspan = j - col0_hdrspan.start
                            col0_hdrspan.expanded = True
                        # Clear old col0_hdrspan
                        if col == debug_word:
                            print("START NEW {}".format(hdrspan.tagsets))
                        col0_hdrspan = None
                        # Now start new, unless it comes from previous row
                        if not previously_seen:
                            col0_hdrspan = hdrspan
                            col0_followed_by_nonempty = False
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
            col = re.sub(r"\s+➤\s*$", "", col)

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
            combined_coltags = compute_coltags(lang, pos, hdrspans, j,
                                               colspan, True, col)
            if any("dummy-ignored-text-cell" in ts for ts in combined_coltags):
                continue

            # print("HAVE_TEXT:", repr(col))
            # Split the text into separate forms.  First simplify spaces except
            # newline.
            split_extra_tags = []
            col = re.sub(r"[ \t\r]+", " ", col)
            # Split the cell text into alternatives
            if col and is_superscript(col[0]):
                alts = [col]
            else:
                separators = [";", "•", r"\n", " or "]
                if col.find(" + ") < 0:
                    separators.append(",")
                    if not col.endswith("/"):
                        separators.append("/")
                if col in special_splits:
                    # Use language-specific special splits
                    alts, tags = special_splits[col]
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
                    repls = {}
                    magic_ch = MAGIC_FIRST
                    trs = get_lang_specific(lang, "form_transformations")
                    for _, v, _, _ in trs:
                        m = re.search(v, col)
                        if m is not None:
                            magic = chr(magic_ch)
                            magic_ch += 1
                            col = re.sub(v, magic, col)
                            repls[magic] = m.group(0)
                    alts0 = split_at_comma_semi(col, separators=separators)
                    alts = []
                    for alt in alts0:
                        for k, v in repls.items():
                            alt = re.sub(k, v, alt)
                        alts.append(alt)
            # Remove "*" from beginning of forms, as in non-attested
            # or reconstructed forms.  Otherwise it might confuse romanization
            # detection.
            alts = list(re.sub(r"^\*\*?([^ ])", r"\1", x)
                               for x in alts)
            alts = list(x for x in alts
                        if not re.match(r"pronounced with |\(with ", x))
            alts = list(re.sub(r"^\((in the sense [^)]*)\)\s+", "", x)
                        for x in alts)
            # Check for parenthesized alternatives, e.g. ripromettersi/Italian
            if all(re.match(r"\w+( \w+)* \(\w+( \w+)*(, \w+( \w+)*)*\)$", alt)
                     and
                     all(distw([re.sub(r" \(.*", "", alt)], x) < 0.5
                         for x in re.sub(r".*\((.*)\)", r"\1", alt).split(", "))
                     for alt in alts):
                new_alts = []
                for alt in alts:
                    alt = re.sub(r" \(", ", ", alt)
                    alt = re.sub(r"\)", "", alt)
                    for new_alt in alt.split(", "):
                        new_alts.append(new_alt)
                alts = new_alts

            # Handle the special case where romanization is given under
            # normal form, e.g. in Russian.  There can be multiple
            # comma-separated forms in each case.  We also handle the case
            # where instead of romanization we have IPA pronunciation
            # (e.g., avoir/French/verb).
            len2 = len(alts) // 2
            # Check for IPAs (forms first, IPAs under)
            if (len(alts) % 2 == 0 and
                all(re.match(r"^\s*/.*/\s*$", x)
                    for x in alts[len2:])):
                alts = list((alts[i], "", alts[i + len2])
                            for i in range(len2))
            elif (len(alts) > 2 and re.match(r"^\s*/.*/\s*$", alts[-1]) and
                  all(not x.startswith("/") for x in alts[:-1])):
                alts = list((alts[i], "", alts[-1])
                            for i in range(len(alts) - 1))
            elif (len(alts) > 2 and
                  not alts[0].startswith("/") and
                  all(re.match(r"^\s*/.*/\s*$", alts[i])
                      for i in range(1, len(alts)))):
                alts = list((alts[0], "", alts[i])
                            for i in range(1, len(alts)))
            # Check for IPAs where only the last entry is IPA and it applies
            # to all preceding
            # Check for romanizations, forms first, romanizations under
            elif (len(alts) % 2 == 0 and
                  not any(x.find("(") >= 0 for x in alts) and
                  all(classify_desc(re.sub(r"\^.*$", "",
                                           "".join(xx for xx in x
                                                   if not is_superscript(xx))))
                      == "other"
                      for x in alts[:len2]) and
                  all(classify_desc(re.sub(r"\^.*$", "",
                                           "".join(xx for xx in x
                                                   if not is_superscript(xx))))
                      in ("romanization", "english")
                      for x in alts[len2:])):
                alts = list((alts[i], alts[i + len2], "")
                            for i in range(len2))
            # Check for romanizations, forms and romanizations alternating
            elif (len(alts) % 2 == 0 and
                  not any(x.find("(") >= 0 for x in alts) and
                  all(classify_desc(re.sub(r"\^.*$", "",
                                           "".join(xx for xx in alts[i]
                                                   if not is_superscript(xx))))
                      == "other"
                      for i in range(0, len(alts), 2)) and
                  all(classify_desc(re.sub(r"\^.*$", "",
                                           "".join(xx for xx in alts[i]
                                                   if not is_superscript(xx))))
                      in ("romanization", "english")
                      for i in range(1, len(alts), 2))):
                alts = list((alts[i], alts[i + 1], "")
                            for i in range(0, len(alts), 2))
            else:
                new_alts = []
                for alt in alts:
                    lst = [""]
                    idx = 0
                    for m in re.finditer(r"(^|\w|\*)\((\w+"
                                         r"(/\w+)*)\)",
                                         alt):
                        v = m.group(2)
                        if (classify_desc(v) == "tags" or  # Tags inside parens
                            m.group(0) == alt):  # All in parens
                            continue
                        new_lst = []
                        for x in lst:
                            x += alt[idx: m.start()] + m.group(1)
                            idx = m.end()
                            vparts = v.split("/")
                            if len(vparts) == 1:
                                new_lst.append(x)
                                new_lst.append(x + v)
                            else:
                                for vv in vparts:
                                    new_lst.append(x + vv)
                        lst = new_lst
                    for x in lst:
                        new_alts.append(x + alt[idx:])
                alts = list((x, "", "") for x in new_alts)
            # Some Arabic adjectives have both sound feminine plural and
            # broken plural diptote (e.g., جاذب/Arabic/Adj).  Handle these
            # specially.
            if (len(combined_coltags) == 2 and
                len(alts) == 2 and
                all(set(x) & set(["sound-feminine-plural",
                                  "sound-masculine-plural",
                                  "broken-plural"])
                    for x in combined_coltags)):
                alts = list((x, set([ts]))
                             for x, ts in zip(alts, combined_coltags))
            else:
                alts = list((x, combined_coltags) for x in alts)
            # Generate forms from the alternatives
            for (form, base_roman, ipa), coltags in alts:
                form = form.strip()
                extra_tags = []
                extra_tags.extend(split_extra_tags)
                # Handle special splits again here, so that we can have custom
                # mappings from form to form and tags.
                if form in special_splits:
                    alts1, tags = special_splits[form]
                    for x in split_extra_tags:
                        assert x in valid_tags
                    assert isinstance(alts1, (list, tuple))
                    assert len(alts1) == 1
                    assert isinstance(tags, str)
                    form = alts1[0]
                    extra_tags.extend(tags.split())
                # Clean the value, extracting reference symbols
                form, refs, defs, hdr_tags = clean_header(word, form)
                # if refs:
                #     print("REFS:", refs)
                extra_tags.extend(hdr_tags)
                # Extract tags from referenced footnotes
                refs_tags = set()
                for ref in refs:
                    if ref in def_ht:
                        refs_tags.update(def_ht[ref])

                if base_roman:
                    base_roman, _, _, hdr_tags = clean_header(word, base_roman)
                    extra_tags.extend(hdr_tags)
                # Do some additional clenanup on the cell.
                form = re.sub(r"^\s*,\s*", "", form)
                form = re.sub(r"\s*,\s*$", "", form)
                form = re.sub(r"\s*(,\s*)+", ", ", form)
                form = re.sub(r"(?i)^Main:", "", form)
                form = re.sub(r"\s+", " ", form)
                form = form.strip()
                if re.match(r"\([^][(){}]*\)$", form):
                    form = form[1:-1]
                    extra_tags.append("informal")
                elif re.match(r"\{\[[^][(){}]*\]\}$", form):
                    # είμαι/Greek/Verb
                    form = form[2:-2]
                    extra_tags.extend(["rare", "archaic"])
                elif re.match(r"\{[^][(){}]*\}$", form):
                    # είμαι/Greek/Verb
                    form = form[1:-1]
                    extra_tags.extend(["archaic"])
                elif re.match(r"\[[^][(){}]*\]$", form):
                    # είμαι/Greek/Verb
                    form = form[1:-1]
                    extra_tags.append("rare")
                # Handle parentheses in the table element.  We parse
                # tags anywhere and romanizations anywhere but beginning.
                roman = base_roman
                paren = None
                clitic = None
                m = re.search(r"(\s+|^)\(([^)]*)\)", form)
                if m is not None:
                    subst = m.group(1)
                    paren = m.group(2)
                else:
                    m = re.search(r"\(([^)]*)\)(\s+|$)", form)
                    if m is not None:
                        paren = m.group(1)
                        subst = m.group(2)
                if paren is not None:
                    if re.match(r"[’'][a-z]([a-z][a-z]?)?$", paren):
                        clitic = paren
                        form = (form[:m.start()] + subst +
                                form[m.end():]).strip()
                    elif classify_desc(paren) == "tags":
                        tagsets1, topics1 = decode_tags(paren)
                        if not topics1:
                            for ts in tagsets1:
                                ts = list(x for x in ts
                                          if x.find(" ") < 0)
                                extra_tags.extend(ts)
                            form = (form[:m.start()] + subst +
                                    form[m.end():]).strip()
                    elif (m.start() > 0 and not roman and
                          classify_desc(form[:m.start()]) == "other" and
                          classify_desc(paren) in ("romanization", "english")
                          and not re.search(r"^with |-form$", paren)):
                        roman = paren
                        form = (form[:m.start()] + subst +
                                form[m.end():]).strip()
                    elif re.search(r"^with |-form", paren):
                        form = (form[:m.start()] + subst +
                                form[m.end():]).strip()
                # Ignore certain forms that are not really forms
                if form in ("", "unchanged",
                            "after an",  # in sona/Irish/Adj/Mutation
                ):
                    continue
                # print("ROWTAGS={} COLTAGS={} REFS_TAGS={} "
                #       "FORM={!r} ROMAN={!r}"
                #       .format(rowtags, coltags, refs_tags,
                #               form, roman))
                # Merge column tags and row tags.  We give preference
                # to moods etc coming from rowtags (cf. austteigen/German/Verb
                # imperative forms).
                for rt in sorted(rowtags):
                    for ct in sorted(coltags):
                        tags = set(global_tags)
                        tags.update(extra_tags)
                        tags.update(rt)
                        tags.update(refs_tags)
                        # Merge tags from column.  For certain kinds of tags,
                        # those coming from row take precedence.
                        old_tags = set(tags)
                        for t in ct:
                            c = valid_tags[t]
                            if (c in ("mood", "case", "number") and
                                any(valid_tags[tt] == c
                                    for tt in old_tags)):
                                continue
                            tags.add(t)

                        # Extract language-specific tags from the
                        # form.  This may also adjust the form.
                        form, lang_tags = lang_specific_tags(lang, pos, form)
                        tags.update(lang_tags)

                        # For non-finite verb forms, see if they have
                        # a gender/class suffix
                        if pos == "verb" and any(valid_tags[t] == "non-finite"
                               for t in tags):
                            form, tt = parse_head_final_tags(ctx, lang, form)
                            tags.update(tt)

                        # Remove "personal" tag if have nth person; these
                        # come up with e.g. reconhecer/Portuguese/Verb.  But
                        # not if we also have "pronoun"
                        if ("personal" in tags and
                            "pronoun" not in tags and
                            any(x in tags for x in
                               ["first-person", "second-person",
                                "third-person"])):
                            tags.remove("personal")

                        # If we have impersonal, remove person and number.
                        # This happens with e.g. viajar/Portuguese/Verb
                        if "impersonal" in tags:
                            tags = tags - set(["first-person", "second-person",
                                               "third-person",
                                               "singular", "plural"])

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
                        if get_lang_specific(lang, "masc_only_animate"):
                            for t1 in ("animate", "inanimate"):
                                for t2 in ("neuter", "feminine"):
                                    if (t1 in tags and t2 in tags and
                                        "masculine" not in tags and
                                        "plural" not in tags):
                                        tags.remove(t1)

                        # German adjective tables contain "(keiner)" etc
                        # for mixed declension plural.  When the adjective
                        # disappears and it becomes just one word, remove
                        # the "includes-article" tag.  e.g. eiskalt/German
                        if "includes-article" in tags and form.find(" ") < 0:
                            tags.remove("includes-article")

                        # Handle ignored forms.  We mark that the form was
                        # provided.  This is important information; some words
                        # just do not have a certain form.  However, there also
                        # many cases where no word in a language has a
                        # particular form.  Post-processing could detect and
                        # remove such cases.
                        if form in IGNORED_COLVALUES:
                            if "dummy-ignore-skipped" in tags:
                                continue
                            if (j not in has_covering_hdr and
                                some_has_covered_text):
                                continue
                            form = "-"
                        elif j in has_covering_hdr:
                            some_has_covered_text = True

                        # Remove the dummy mood tag that we sometimes
                        # use to block adding other mood and related
                        # tags
                        tags = tags - set(["dummy-mood", "dummy-tense",
                                           "dummy-ignore-skipped"])

                        # Perform language-specific tag replacements according
                        # to rules in a table.
                        changed = True
                        while changed:
                            changed = False
                            for lst in lang_tag_mappings:
                                assert isinstance(lst, (list, tuple))
                                assert len(lst) >= 3
                                if lang not in lst[0] or pos not in lst[1]:
                                    continue
                                for src, dst in lst[2:]:
                                    assert isinstance(src, (list, tuple))
                                    assert isinstance(dst, (list, tuple))
                                    if all(t in tags for t in src):
                                        tags = (tags - set(src)) | set(dst)
                                        changed = True

                        # Warn if there are entries with empty tags
                        if not tags:
                            ctx.debug("inflection table: empty tags for {}"
                                      .format(form))

                        # Warn if form looks like IPA
                        if re.match(r"\s*/.*/\s*$", form):
                            ctx.debug("inflection table form looks like IPA: "
                                      "form={} tags={}"
                                      .format(form, tags))

                        if form == "dummy-ignored-text-cell":
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
                            dt = {"form": clitic, "tags": tags + ["clitic"],
                                  "source": source}
                            ret.append(dt)
        # End of row.
        rownum += 1
        # For certain languages, if the row was empty, reset
        # hdrspans (saprast/Latvian/Verb, but not aussteigen/German/Verb).
        if row_empty and get_lang_specific(lang, "empty_row_resets"):
            hdrspans = []
        # Check if we should expand col0_hdrspan.
        if col0_hdrspan is not None:
            col0_allowed = get_lang_specific(lang, "hdr_expand_first")
            col0_cats = tagset_cats(col0_hdrspan.tagsets)
            # Only expand if col0_cats and later_cats are allowed
            # and don't overlap and col0 has tags, and there have
            # been no disallowed cells in between.
            if (not col0_followed_by_nonempty and
                not (col0_cats - col0_allowed) and
                # len(col0_cats) == 1 and
                j > col0_hdrspan.start + col0_hdrspan.colspan):
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
    if any("noun" in x["tags"] for x in ret):
        if lang in ("Alemannic German", "Bavarian", "Cimbrian", "German",
                    "German Low German", "Hunsrik", "Luxembourish",
                    "Pennsylvania German"):
            new_ret = []
            saved_tags = set()
            had_noun = False
            for dt in ret:
                tags = dt["tags"]
                if "noun" in tags:
                    tags = list(sorted(set(t for t in tags if t != "noun") |
                                           saved_tags))
                    had_noun = True
                elif ("indefinite" in tags or "definite" in tags or
                      "usually-without-article" in tags or
                      "without-article" in tags):
                    if had_noun:
                        saved_tags = set(tags)
                    else:
                        saved_tags = saved_tags | set(tags)  # E.g. Haus/German
                        remove_useless_tags(lang, pos, saved_tags)
                    saved_tags = saved_tags & set(["masculine", "feminine",
                                                   "neuter", "singular",
                                                   "plural",
                                                   "indefinite",
                                                   "definite",
                                                   "usually-without-article",
                                                   "without-article"])
                    had_noun = False
                    continue  # Skip the articles
                dt = dt.copy()
                dt["tags"] = tags
                new_ret.append(dt)
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
                data_append(ctx, dt, "tags", "multiword-construction")
            new_ret.append(dt)
        ret = new_ret

    # Always insert "table-tags" detail as the first entry in any inflection
    # table.  This way we can reliably detect where a new table starts.
    # Table-tags applies until the next table-tags entry.
    if ret or table_tags:
        table_tags = list(sorted(set(table_tags)))
        dt = {"form": " ".join(table_tags),
              "source": source,
              "tags": ["table-tags"]}
        ret = [dt] + ret
    return ret


def handle_generic_table(config, ctx, data, word, lang, pos, rows, titles,
                         source, after):
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(rows, list)
    assert isinstance(source, str)
    assert isinstance(after, str)
    for row in rows:
        assert isinstance(row, list)
        for x in row:
            assert isinstance(x, InflCell)
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)

    # Try to parse the table as a simple table
    ret = parse_simple_table(config, ctx, word, lang, pos, rows, titles,
                             source, after)
    if ret is None:
        # XXX handle other table formats
        # We were not able to handle the table
        return

    # Add the returned forms but eliminate duplicates.
    have_forms = set()
    # XXX Pending removal - we now include all forms from tables, even if
    # they might duplicate those in word head, as that gives a more accurate
    # picture of what is extracted from inflection tables.
    # for dt in data.get("forms", ()):
    #     tags = dt.get("tags", ())
    #     if "table-tags" not in tags:
    #         have_forms.add(freeze(dt))
    for dt in ret:
        fdt = freeze(dt)
        if fdt in have_forms:
            continue  # Don't add duplicates Some Russian words have
        # Declension and Pre-reform declension partially duplicating
        # same data.  Don't add "dated" tags variant if already have
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
            data_append(ctx, data, "forms", dt)


def handle_wikitext_table(config, ctx, word, lang, pos,
                          data, tree, titles, source, after):
    """Parses a table from parsed Wikitext format into rows and columns of
    InflCell objects and then calls handle_generic_table() to parse it into
    forms.  This adds the forms into ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(data, dict)
    assert isinstance(tree, WikiNode)
    assert tree.kind == NodeKind.TABLE
    assert isinstance(titles, list)
    assert isinstance(source, str)
    for x in titles:
        assert isinstance(x, str)
    assert isinstance(after, str)
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
            have_nonempty = False  # Have nonempty cell not from rowspan
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

                # Clean the rest of the cell.
                celltext = clean_node(config, ctx, None, rest)
                # print("CLEANED:", celltext)

                # Handle nested tables.
                for tbl in tables:
                    # Some nested tables (e.g., croí/Irish) have subtitles
                    # as normal paragraphs in the same cell under a descriptive
                    # test that should be treated as a title (e.g.,
                    # "Forms with the definite article", with "definite" not
                    # mentioned elsewhere).
                    new_titles = list(titles)
                    if celltext:
                        new_titles.append(celltext)
                    handle_wikitext_table(config, ctx, word, lang, pos, data,
                                          tbl, new_titles, source, "")

                # This magic value is used as part of header detection
                cellstyle = (col.attrs.get("style", "") + "//" +
                             col.attrs.get("class", "") + "//" +
                             str(kind))
                             
                if not row:  # if first column in row
                    style = cellstyle
                target = None
                titletext = celltext.strip()
                while titletext and is_superscript(titletext[-1]):
                    titletext = titletext[:-1]
                idx = celltext.find(": ")
                is_title = False
                # remove anything in parentheses, compress whitespace, .strip()
                cleaned_titletext = re.sub(r"\s+", " ",
                                           re.sub(r"\s*\([^)]*\)", "",
                                                  titletext)).strip()
                cleaned, _, _, _ = clean_header(word, celltext)
                cleaned = re.sub(r"\s+", " ", cleaned)
                hdr_expansion = expand_header(config, ctx, word, lang, pos,
                                              cleaned, [],
                                              silent=True, ignore_tags=True)
                candidate_hdr = (not any(any(t.startswith("error-") for t in ts)
                                         for ts in hdr_expansion))
                # KJ candidate_hdr says that a specific cell is a candidate
                # for being a header because it passed through expand_header
                # without getting any "error-" tags; that is, the contents
                # is "valid" for being a header; these are the false positives
                # we want to catch
                if (candidate_hdr and
                   kind != NodeKind.TABLE_HEADER_CELL and
                   lang not in LANGUAGES_WITH_CELLS_AS_HEADERS):
                    ctx.debug("table cell identified as header and given "\
                              "candidate status, but {} is not in " \
                              "LANGUAGES_WITH_CELLS_AS_HEADERS; " \
                              "cleaned text: {}" \
                              .format(lang, cleaned))
                    # KJ the simplest way to implement LANGUAGES_WITH...
                    # is to stop candidate_hdr with = False here if LWCAH == True
                    # XXX ENABLE ME CELLS-AS-HEADERS when LANGUAGES_WITH... is populated!
                    # ~ candidate_hdr = False
                    
                #print("titletext={!r} hdr_expansion={!r} candidate_hdr={!r} "
                #      "lang={} pos={}"
                #      .format(titletext, hdr_expansion, candidate_hdr,
                #              lang, pos))
                if idx >= 0 and titletext[:idx] in infl_map:
                    target = titletext[idx + 2:].strip()
                    celltext = celltext[:idx]
                    is_title = True
                elif (kind == NodeKind.TABLE_HEADER_CELL and
                      titletext.find(" + ") < 0 and  # For "avoir + blah blah"?
                      not any(isinstance(x, WikiNode) and
                              x.kind == NodeKind.HTML and
                              x.args == "span" and
                              x.attrs.get("lang") in ("az",)
                              for x in col.children)):
                    is_title = True
                elif (candidate_hdr and
                      cleaned_titletext not in IGNORED_COLVALUES and
                      distw([cleaned_titletext], word) > 0.3 and
                      cleaned_titletext not in ("I", "es")):
                    is_title = True
                #  if first column or same style as first column
                elif (style == cellstyle and
                      # and title is not identical to word name
                      titletext != word and
                      #  the style composite string is not broken
                      not style.startswith("////") and
                      # allow is_title = True if
                      # XXX ENABLE ME CELLS-AS-HEADERS when LANGUAGES_WITH... is populated!
                      # ~ lang in LANGUAGES_WITH_CELLS_AS_HEADERS and
                      titletext.find(" + ") < 0):
                    is_title = True
                    ctx.debug("table cell identified as header based " \
                              "on style, but {} is not in " \
                              "LANGUAGES_WITH_CELLS_AS_HEADERS; " \
                              "cleaned text: {}, style: {}" \
                              .format(lang, cleaned, style))
                if (not is_title and len(row) < len(cols_headered) and
                    cols_headered[len(row)]):
                    # Whole column has title suggesting they are headers
                    # (e.g. "Case")
                    is_title = True
                if re.match(r"Conjugation of |Declension of |Inflection of|"
                            r"Mutation of|Notes\b", # \b is word-boundary
                            titletext):
                    is_title = True
                if is_title:
                    while len(cols_headered) <= len(row):
                        cols_headered.append(False)
                    if any("*" in tt for tt in hdr_expansion):
                        cols_headered[len(row)] = True
                        celltext = ""
                have_nonempty |= is_title or celltext != ""
                cell = InflCell(celltext, is_title, len(row), colspan, rowspan,
                                target)
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
            for i in range(len(row), len(cols_filled)):
                if cols_filled[i] <= 0:
                    continue
                cols_filled[i] -= 1
                while len(row) < i:
                    row.append(InflCell("", False, len(row), 1, 1, None))
                row.append(cols_fill[i])
            # print("  ROW {!r}".format(row))
            if have_nonempty:
                rows.append(row)
        elif kind in (NodeKind.TABLE_HEADER_CELL, NodeKind.TABLE_CELL):
            # print("  TOP-LEVEL CELL", node)
            pass

    # Now we have a table that has been parsed into rows and columns of
    # InflCell objects.  Parse the inflection table from that format.
    handle_generic_table(config, ctx, data, word, lang, pos, rows, titles,
                         source, after)


def handle_html_table(config, ctx, word, lang, pos, data, tree, titles, source,
                      after):
    """Parses a table from parsed HTML format into rows and columns of
    InflCell objects and then calls handle_generic_table() to parse it into
    forms.  This adds the forms into ``data``."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(data, dict)
    assert isinstance(tree, WikiNode)
    assert tree.kind == NodeKind.HTML and tree.args == "table"
    assert isinstance(titles, list)
    for x in titles:
        assert isinstance(x, str)
    assert isinstance(source, str)
    assert isinstance(after, str)

    ctx.debug("HTML TABLES NOT YET IMPLEMENTED at {}/{}"
              .format(word, lang))


def parse_inflection_section(config, ctx, data, word, lang, pos, section, tree):
    """Parses an inflection section on a page.  ``data`` should be the
    data for a part-of-speech, and inflections will be added to it."""

    # print("PARSE_INFLECTION_SECTION {}/{}/{}/{}"
    #       .format(word, lang, pos, section))
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(word, str)
    assert isinstance(lang, str)
    assert pos in PARTS_OF_SPEECH
    assert isinstance(section, str)
    assert isinstance(tree, WikiNode)
    source = section
    tables = []

    def process_tables():
        for kind, node, titles, after in tables:
            after = "".join(after).strip()
            after = clean_value(config, after)
            if kind == "wikitext":
                handle_wikitext_table(config, ctx, word, lang, pos,
                                      data, node, titles, source, after)
            elif kind == "html":
                handle_html_table(config, ctx, word, lang, pos, data, node,
                                  titles, source, after)
            else:
                raise RuntimeError("{}: unimplemented table kind {}"
                                   .format(word, kind))

    def recurse_navframe(node, titles):
        nonlocal tables
        titleparts = []
        old_tables = tables
        tables = []

        def recurse1(node):
            nonlocal tables
            if isinstance(node, (list, tuple)):
                for x in node:
                    recurse1(x)
                return
            if isinstance(node, str):
                if tables:
                    tables[-1][-1].append(node)
                else:
                    titleparts.append(node)
                return
            if not isinstance(node, WikiNode):
                ctx.debug("inflection table: unhandled in NavFrame: {}"
                          .format(node))
                return
            kind = node.kind
            if kind == NodeKind.HTML:
                classes = node.attrs.get("class", "").split()
                if "NavToggle" in classes:
                    return
                if "NavHead" in classes:
                    # print("NAVHEAD:", node)
                    recurse1(node.children)
                    return
                if "NavContent" in classes:
                    # print("NAVCONTENT:", node)
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
                    recurse1(node.args[1:])
                else:
                    recurse1(node.args[0])
            recurse1(node.children)
        recurse1(node)

        process_tables()
        tables = old_tables

    def recurse(node, titles):
        # XXX could this function be merged with recurse1 above?
        nonlocal tables
        if isinstance(node, (list, tuple)):
            for x in node:
                recurse(x, titles)
            return
        if tables and isinstance(node, str):
            tables[-1][-1].append(node)
            return
        if not isinstance(node, WikiNode):
            return
        kind = node.kind
        if kind == NodeKind.TABLE:
            tables.append(["wikitext", node, titles, []])
            return
        elif kind == NodeKind.HTML and node.args == "table":
            classes = node.attrs.get("class", ())
            if "audiotable" in classes:
                return
            tables.append(["html", node, titles, []])
            return
        elif kind in (NodeKind.LEVEL2, NodeKind.LEVEL3, NodeKind.LEVEL4,
                      NodeKind.LEVEL5, NodeKind.LEVEL6):
            return  # Skip subsections
        if (kind == NodeKind.HTML and node.args == "div" and
            "NavFrame" in node.attrs.get("class", "").split()):
            recurse_navframe(node, titles)
            return
        if kind == NodeKind.LINK:
            if len(node.args) > 1:
                recurse(node.args[1:], titles)
            else:
                recurse(node.args[0], titles)
            return
        for x in node.children:
            recurse(x, titles)

    assert tree.kind == NodeKind.ROOT
    for x in tree.children:
        recurse(x, [])

    # Process the tables we found
    process_tables()

    # XXX this code is used for extracting tables for inflection tests
    if True:
        if section != "Mutation":
            with open("temp.XXX", "w") as f:
                f.write(word + "\n")
                f.write(lang + "\n")
                f.write(pos + "\n")
                f.write(section + "\n")
                text = ctx.node_to_wikitext(tree)
                f.write(text + "\n")

# XXX check interdecir/Spanish - singular/plural issues

# XXX viajar/Portuguese: gerund has singular+plural - check if all columns
# containing same tag category are included, and then don't include anything

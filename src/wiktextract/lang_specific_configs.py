# Language-specific configuration for various aspects of inflection table
# parsing.

import re

from typing import Optional, TypedDict, Union
from wiktextract.tags import valid_tags, tag_categories
from wiktextract.parts_of_speech import PARTS_OF_SPEECH

LangConfDict = TypedDict(
    "LangConfDict",
    {
        "next": str,
        "hdr_expand_first": set[str],
        "hdr_expand_cont": set[str],
        "animate_inanimate_remove": bool,
        "both_active_passive_remove": bool,
        "both_strong_weak_remove": bool,
        "definitenesses": list[str],
        "empty_row_resets": bool,
        "form_transformations": list[
            list[str]
        ],  # tag extraction, lang_specific_tags()
        "genders": Optional[list[str]],
        "imperative_no_tense": bool,
        "masc_only_animate": bool,  # Slavic special
        "numbers": list[str],
        "persons": list[str],
        "pl_virile_nonvirile": bool,
        "reuse_cellspan": str,  # stop/skip/reuse
        "skip_mood_mood": bool,
        "skip_tense_tense": bool,
        "stop_non_finite_non_finite": bool,
        "stop_non_finite_voice": bool,
        "stop_non_finite_tense": bool,
        "strengths": list[str],
        "virile_nonvirile_remove": bool,
        "voices": list[str],
        "special_phrase_splits": dict[
            str, list[Union[list[str], str]]
        ],  # value: (split phrase, tags)
        "form_replacements": dict[
            str, Union[str, list[str]]
        ],  # value: [replacement, tags]
        # Greek-style bracket semantics
        "parentheses_for_informal": bool,
        "square_brackets_for_rare": bool,
        "curly_brackets_for_archaic": bool,
        # Armenian; migrated old data here
        "lang_tag_mappings": Optional[
            dict[str, dict[tuple[str, ...], list[str]]]
        ],
        # Spanish has a lot of "vos" and "tú" in its tables that look like
        # references, and they give their form certain tags.
        # Dict of references ("vos") that point to tag strings "first-person
        # singular" that *extend* tags.
        "special_references": Optional[dict[str, str]],
        # Some languages like Icelandic and Faroese have text cells in the
        # upper left that we'd like to ignore.
        "ignore_top_left_text_cell": bool,
        # Minor regex replacements for cleanup in parse_simple_table()
        "minor_text_cleanups": Optional[
            dict[str, str]
        ],  # dict of {regex: substitution}
        "articles_in_separate_columns": bool,
        # Cells to ignore in this language, unless the cell has the key
        # as a tag.
        "conditionally_ignored_cells": dict[str, list[str]],
    },
    total=False,
)

lang_specific: dict[str, LangConfDict] = {
    "default": {
        "hdr_expand_first": set(
            [
                "number",
                "mood",
                "referent",
                "aspect",
                "tense",
                "voice",
                "non-finite",
                "case",
                "possession",
            ]
        ),
        "hdr_expand_cont": set(
            [
                "person",
                "gender",
                "number",
                "degree",
                "polarity",
                "voice",
                "misc",
            ]
        ),
        "animate_inanimate_remove": True,
        "both_active_passive_remove": True,
        "both_strong_weak_remove": True,
        "definitenesses": ["indefinite", "definite"],
        "empty_row_resets": False,
        "form_transformations": [],  # tag extraction, lang_specific_tags()
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
        "special_phrase_splits": {},  # value: (split phrase, tags)
        "form_replacements": {},  # value: [replacement, tags]
        # Greek-style bracket semantics
        "parentheses_for_informal": False,
        "square_brackets_for_rare": False,
        "curly_brackets_for_archaic": False,
        # Armenian; migrated old data here
        "lang_tag_mappings": None,
        # Spanish has a lot of "vos" and "tú" in its tables that look like
        # references, and they give their form certain tags.
        # Dict of references ("vos") that point to tag strings "first-person
        # singular" that *extend* tags.
        "special_references": None,
        # Some languages like Icelandic and Faroese have text cells in the
        # upper left that we'd like to ignore.
        "ignore_top_left_text_cell": False,
        # Minor regex replacements for cleanup in parse_simple_table()
        "minor_text_cleanups": None,  # dict of {regex: substitution}
        "articles_in_separate_columns": False,
        # Cells to ignore in this language, unless the cell has the key
        # as a tag.
        "conditionally_ignored_cells": {},
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
    "romance-group": {},
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
    "german-group": {  # languages closely related to or offshot from German
        "next": "germanic-group",
        "articles_in_separate_columns": True,
    },
    "germanic-group": {  # Germanic languages as a whole
        "next": "indo-european-group",
    },
    "Akkadian": {
        "next": "semitic-group",
    },
    "Alemannic German": {
        "next": "German",
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
        "numbers": [
            "singular",
            "dual",
            "paucal",
            "plural",
            "collective",
            "singulative",
        ],
        "reuse_cellspan": "reuse",
        "hdr_expand_first": set(["number"]),
        "hdr_expand_cont": set(
            ["gender", "referent", "misc", "number", "class"]
        ),
    },
    "Aragonese": {
        "next": "romance-group",
    },
    "Armenian": {
        "lang_tag_mappings": {
            "noun": {
                ("possessive", "singular"): ["possessive", "possessed-single"],
                ("possessive", "plural"): ["possessive", "possessed-single"],
            },
        },
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
    "Bavarian": {
        "next": "German",
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
    "Cimbrian": {
        "next": "German",
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
            ["noun", r"^\(as a measure\) ", "", ""],
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
        "form_replacements": {
            "let’s be": ["let's be", "first-person plural pronoun-included"],
        },
        "special_phrase_splits": {
            "I am (’m)/be": [["am (’m)", "be"], "first-person singular"],
            "we are (’re)/be/been": [
                ["are (’re)", "be", "been"],
                "first-person plural",
            ],
            "thou art (’rt)/beest": [
                ["art (’rt)", "beest"],
                "second-person singular",
            ],
            "ye are (’re)/be/been": [
                ["are (’re)", "be", "been"],
                "second-person plural",
            ],
            "thou be/beest": [["be", "beest"], "second-person singular"],
            "he/she/it is (’s)/beeth/bes": [
                ["is (’s)", "beeth", "bes"],
                "third-person singular",
            ],
            "they are (’re)/be/been": [
                ["are (’re)", "be", "been"],
                "third-person plural",
            ],
            "thou wert/wast": [["wert", "wast"], "second-person singular"],
            "thou were/wert": [["were", "wert"], "second-person singular"],
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
    "Faroese": {
        "ignore_top_left_text_cell": True,
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
        "next": "german-group",
        "form_transformations": [
            ["verb", "^ich ", "", "first-person singular"],
            ["verb", "^du ", "", "second-person singular"],
            ["verb", "^er ", "", "third-person singular"],
            ["verb", "^wir ", "", "first-person plural"],
            ["verb", "^ihr ", "", "second-person plural"],
            ["verb", "^sie ", "", "third-person plural"],
            [
                "verb",
                "^dass ich ",
                "",
                "first-person singular subordinate-clause",
            ],
            [
                "verb",
                "^dass du ",
                "",
                "second-person singular subordinate-clause",
            ],
            [
                "verb",
                "^dass er ",
                "",
                "third-person singular subordinate-clause",
            ],
            [
                "verb",
                "^dass wir ",
                "",
                "first-person plural subordinate-clause",
            ],
            [
                "verb",
                "^dass ihr ",
                "",
                "second-person plural subordinate-clause",
            ],
            [
                "verb",
                "^dass sie ",
                "",
                "third-person plural subordinate-clause",
            ],
            ["verb", r" \(du\)$", "", "second-person singular"],
            ["verb", r" \(ihr\)$", "", "second-person plural"],
            ["adj", "^er ist ", "", "masculine singular"],
            ["adj", "^sie ist ", "", "feminine singular"],
            ["adj", "^es ist ", "", "neuter singular"],
            ["adj", "^sie sind ", "", "plural"],
            ["adj", "^keine ", "keine ", "negative"],
            ["adj", "^keiner ", "keiner ", "negative"],
            ["adj", "^keinen ", "keinen ", "negative"],
        ],
        "conditionally_ignored_cells": {
            "definite": [
                "der",
                "die",
                "das",
                "des",
                "dem",
                "den",
            ],
            "indefinite": [
                "ein",
                "eine",
                "eines",
                "einer",
                "einem",
                "einen",
            ],
        },
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
        # είμαι/Greek
        "parentheses_for_informal": True,
        "square_brackets_for_rare": True,
        "curly_brackets_for_archaic": True,
        # For greek originally
        "minor_text_cleanups": {
            r"\s+➤\s*$": "",
        },
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
    "Hunsrik": {
        "next": "German",
    },
    "Icelandic": {
        "ignore_top_left_text_cell": True,
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
    "Luxembourgish": {
        "next": "German",
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
        "numbers": [
            "singular",
            "plural",
            "dual",
            "duoplural",
        ],
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
    "Pennsylvania German": {
        "next": "German",
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
        "special_references": {
            "vos": "informal vos-form second-person singular",
            "ᵛᵒˢ": "informal vos-form second-person singular",
            "tú": "informal second-person singular",
        },
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
# def_ls_keys = lang_specific["default"].keys()
# for k, v in lang_specific.items():
#     if k[0].isupper() and k not in languages_by_name:
#         raise AssertionError("key {!r} in lang_specific is not a valid language"
#                              .format(k))
#     assert isinstance(v, dict)
#     for kk, vv in v.items():
#         if kk not in def_ls_keys and kk != "next":
#             raise AssertionError("{} key {!r} not in default entry"
#                                  .format(k, kk))
#         if kk in ("hdr_expand_first", "hdr_expand_cont"):
#             if not isinstance(vv, set):
#                 raise AssertionError("{} key {!r} must be set"
#                                      .format(lang, kk))
#             for t in vv:
#                 if t not in tag_categories:
#                     raise AssertionError("{} key {!r} invalid tag category {}"
#                                          .format(k, kk, t))
#         elif kk in ("genders", "numbers", "persons", "strengths", "voices"):
#             if not vv:
#                 continue
#             if not isinstance(vv, (list, tuple, set)):
#                 raise AssertionError("{} key {!r} must be list/tuple/set"
#                                      .format(k, kk))
#             for t in vv:
#                 if t not in valid_tags:
#                     raise AssertionError("{} key {!r} invalid tag {!r}"
#                                          .format(k, kk, t))
#         elif kk == "lang_tag_mappings" and vv is not None:
#             for pos, transf in vv.items():
#                 assert pos in PARTS_OF_SPEECH
#                 assert isinstance(transf, dict)
#                 for pre, post in transf.items():
#                     assert isinstance(pre, tuple)
#                     assert all(t in valid_tags for t in pre)
#                     assert isinstance(post, list)
#                     assert all(t in valid_tags for t in post)
#         elif kk == "next":
#             if vv not in lang_specific:
#                 raise AssertionError("{} key {!r} value {!r} is not defined"
#                                      .format(k, kk, vv))


def get_lang_conf(lang, field):
    """Returns the given field from language-specific data or "default"
    if the language is not listed or does not have the field."""
    assert isinstance(lang, str)
    assert isinstance(field, str)
    while True:
        lconfigs = lang_specific.get(lang)
        if lconfigs is None:
            lang = "default"
        elif lang == "default" and field not in lconfigs:
            raise RuntimeError("Invalid lang_specific field {!r}".format(field))
        else:
            if field in lconfigs:
                return lconfigs[field]
            lang = lconfigs.get("next", "default")


def lang_specific_tags(lang, pos, form):
    """Extracts tags from the word form itself in a language-specific way.
    This may also adjust the word form.
    For example, German inflected verb forms don't have person and number
    specified in the table, but include a pronoun.  This returns adjusted
    form and a list of tags."""
    assert isinstance(lang, str)
    assert isinstance(pos, str)
    assert isinstance(form, str)
    rules = get_lang_conf(lang, "form_transformations")
    for patpos, pattern, dst, tags in rules:
        #   PoS, regex, replacement, tags; pattern -> dst :: "^ich " > ""
        assert patpos in PARTS_OF_SPEECH
        if pos != patpos:
            continue
        m = re.search(pattern, form)
        if not m:
            continue
        form = form[: m.start()] + dst + form[m.end() :]
        tags = tags.split()
        for t in tags:
            assert t in valid_tags
        return form, tags
    return form, []

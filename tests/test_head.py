# Tests for parse_word_head()
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.form_descriptions import parse_word_head

class HeadTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")
        self.ctx.start_section("English")

    def test_reconstruction1(self):
        data = {}
        self.ctx.start_page("Reconstruction:Proto-Germanic/testpage")
        self.ctx.start_section("Proto-Germanic")
        parse_word_head(self.ctx, "noun", "*testpage", data, True)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {})

    def test_reconstruction2(self):
        data = {}
        self.ctx.start_page("Reconstruction:Proto-Germanic/testpage")
        self.ctx.start_section("Proto-Germanic")
        parse_word_head(self.ctx, "noun", "*testfoo", data, True)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testfoo",
                                           "tags": ["canonical"]}]})

    def test_reconstruction3(self):
        data = {}
        parse_word_head(self.ctx, "noun", "*testpage", data, False)
        self.assertEqual(data, {"forms": [{"form": "*testpage",
                                           "tags": ["canonical"]}]})

    def test_head1(self):
        data = {}
        parse_word_head(self.ctx, "noun", "", data, False)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {})

    def test_head2(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage", data, False)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {})

    def test_head3(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpAge", data, False)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testpAge",
                                           "tags": ["canonical"]}]})

    def test_head4(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage f", data, False)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine"]})

    def test_head5(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpAge m", data, False)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "testpAge", "tags": ["canonical", "masculine"]},
        ]})

    def test_head6(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage n", data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["neuter"]})

    def test_head7(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage c", data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["common-gender"]})

    def test_head8(self):
        data = {}
        self.ctx.start_section("Zulu")
        parse_word_head(self.ctx, "noun", "testpage 1", data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["class-1"]})

    def test_head8b(self):
        # Trying to parse suffix 1 in English - should not get parsed
        data = {}
        parse_word_head(self.ctx, "noun", "testpage 1", data, False)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertNotEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testpage 1",
                                           "tags": ["canonical"]}]})

    def test_head9(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, inanimate)", data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "inanimate",
                                         "plural", "plural-only"]})

    def test_head10(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate)",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "inanimate",
                                         "plural", "plural-only"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

    def test_head11(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate) "
                        "(+ dative)",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        print(data)
        self.assertEqual(data, {"tags": ["feminine", "inanimate",
                                         "plural", "plural-only",
                                         "with-dative"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

    def test_head12(self):
        # McCune-Reischauer is used in Korean characters; we're really testing
        # the hyphen in keyword names
        data = {}
        parse_word_head(self.ctx, "noun",
                        "foo (McCune-Reischauer bar)", data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical"]},
            {"form": "bar", "tags": ["McCune-Reischauer"]}]})

    def test_head13(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f or m",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine"]})

    def test_head14(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f, m",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine"]})

    def test_head15(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f, m, n",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine", "neuter"]})

    def test_head16(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f or m or n",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine", "neuter"]})

    def test_head17(self):
        data = {}
        self.ctx.start_page("index")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun",
                        "index n",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["neuter"]})

    def test_head18(self):
        data = {}
        self.ctx.start_page("index")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun",
                        "index m or f (genitive indicis); third declension",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["declension-3", "feminine",
                                         "masculine"],
                                "forms": [
                                    {"tags": ["genitive"],
                                     "form": "indicis"},
                                ]})

    def test_head19(self):
        data = {}
        self.ctx.start_page("index")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun", "foo f or bar m", data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical", "feminine"]},
            {"form": "bar", "tags": ["canonical", "masculine"]},
        ]})

    def test_head20(self):
        data = {}
        self.ctx.start_page("index")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun", "foo or bar", data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical"]},
            {"form": "bar", "tags": ["canonical"]},
        ]})

    def test_head21(self):
        data = {}
        self.ctx.start_page("index")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun", "foo f or n or bar m or c", data,
                        False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical", "feminine", "neuter"]},
            {"form": "bar", "tags": ["canonical", "common-gender",
                                     "masculine"]},
        ]})

    def test_head22(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f or testpage2 m; person",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["person"],
                                "forms": [
                                    {"tags": ["canonical", "feminine"],
                                     "form": "testpage"},
                                    {"tags": ["canonical", "masculine"],
                                     "form": "testpage2"},
                                ]})

    def test_head23(self):
        data = {}
        self.ctx.start_page("indubitables")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Adjective")
        parse_word_head(self.ctx, "adj", "indubitables m pl or f pl", data,
                        False)
        # print(json.dumps(data, indent=2))
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine", "plural"]})

    def test_head24(self):
        data = {}
        self.ctx.start_page("foo")
        self.ctx.start_section("Japanese")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun",
                        "foo (12 strokes)",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [
            {"tags": ["strokes"],
             "form": "12"},
            ]})

    def test_head25(self):
        data = {}
        self.ctx.start_page("smiley")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun",
                        "smiley m (plural smileys, diminutive smileytje n)",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["masculine"],
                                "forms": [
            {"tags": ["plural"],
             "form": "smileys"},
            {"tags": ["diminutive", "neuter"],
             "form": "smileytje"},
            ]})

    def test_head26(self):
        data = {}
        self.ctx.start_page("foos")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun",
                        "foos (plural of foo)",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [
            {"tags": ["plural-of"],
             "form": "foo"},
            ]})

    def test_head27(self):
        data = {}
        self.ctx.start_page("أَبْلَعَ")
        self.ctx.start_section("Arabic")
        self.ctx.start_subsection("Verb")
        parse_word_head(self.ctx, "verb",
                        "أَبْلَعَ (ʾablaʿa) IV, non-past يُبْلِعُ‎‎ (yubliʿu)",
                        data, False)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {
            "forms": [
                {
                  "form": "يُبْلِعُ‎‎",
                  "roman": "yubliʿu",
                  "tags": [
                    "non-past"
                  ]
                },
                {
                  "form": "ʾablaʿa",
                  "tags": [
                    "romanization"
                  ]
                },
            ],
            "tags": ["form-iv"]
            })

    def test_head28(self):
        data = {}
        self.maxDiff = 10000
        self.ctx.start_page("tell")
        self.ctx.start_section("English")
        self.ctx.start_subsection("Noun")
        parse_word_head(self.ctx, "noun",
                        "tell (third-person singular simple present tells, present participle telling, simple past and past participle told or (dialectal or nonstandard) telled)",
                        data, False)
        print(json.dumps(data, indent=2, sort_keys=True))
        self.assertEqual(data, {
            "forms": [
                {"form": "tells",
                 "tags": ["present", "singular", "third-person"]},
                {"form": "telling",
                 "tags": ["participle", "present"]},
                {"form": "told",
                 "tags": ["participle", "past"]},
                {"form": "told",
                 "tags": ["past"]},
                {"form": "telled",
                 "tags": ["dialectal", "participle", "past"]},
                {"form": "telled",
                 "tags": ["dialectal", "past"]},
                ],
            })

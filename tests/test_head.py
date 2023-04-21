# Tests for parse_word_head()
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.form_descriptions import parse_word_head

class HeadTests(unittest.TestCase):

    def setUp(self):
        self.wxr = WiktextractContext(WiktionaryConfig(), Wtp())
        
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def test_reconstruction1(self):
        data = {}
        self.wxr.wtp.start_page("Reconstruction:Proto-Germanic/testpage")
        self.wxr.wtp.start_section("Proto-Germanic")
        parse_word_head(self.wxr, "noun", "*testpage", data, True, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {})

    def test_reconstruction2(self):
        data = {}
        self.wxr.wtp.start_page("Reconstruction:Proto-Germanic/testpage")
        self.wxr.wtp.start_section("Proto-Germanic")
        parse_word_head(self.wxr, "noun", "*testfoo", data, True, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testfoo",
                                           "tags": ["canonical"]}]})

    def test_reconstruction3(self):
        data = {}
        parse_word_head(self.wxr, "noun", "*testpage", data, False, None)
        self.assertEqual(data, {"forms": [{"form": "*testpage",
                                           "tags": ["canonical"]}]})

    def test_head1(self):
        data = {}
        parse_word_head(self.wxr, "noun", "", data, False, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {})

    def test_head2(self):
        data = {}
        parse_word_head(self.wxr, "noun", "testpage", data, False, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {})

    def test_head3(self):
        data = {}
        parse_word_head(self.wxr, "noun", "testpAge", data, False, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testpAge",
                                           "tags": ["canonical"]}]})

    def test_head4(self):
        data = {}
        parse_word_head(self.wxr, "noun", "testpage f", data, False, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine"]})

    def test_head5(self):
        data = {}
        parse_word_head(self.wxr, "noun", "testpAge m", data, False, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "testpAge", "tags": ["canonical", "masculine"]},
        ]})

    def test_head6(self):
        data = {}
        parse_word_head(self.wxr, "noun", "testpage n", data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["neuter"]})

    def test_head7(self):
        data = {}
        parse_word_head(self.wxr, "noun", "testpage c", data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["common-gender"]})

    def test_head8(self):
        data = {}
        self.wxr.wtp.start_section("Zulu")
        parse_word_head(self.wxr, "noun", "testpage 1", data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["class-1"]})

    def test_head8b(self):
        # Trying to parse suffix 1 in English - should not get parsed
        data = {}
        parse_word_head(self.wxr, "noun", "testpage 1", data, False, None)
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertNotEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testpage 1",
                                           "tags": ["canonical"]}]})

    def test_head9(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f (plurale tantum, inanimate)",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "inanimate",
                                         "plural", "plural-only"]})

    def test_head10(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate)",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "inanimate",
                                         "plural", "plural-only"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

    def test_head11(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate) "
                        "(+ dative)",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
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
        parse_word_head(self.wxr, "noun",
                        "foo (McCune-Reischauer bar)", data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical"]},
            {"form": "bar", "tags": ["McCune-Reischauer"]}]})

    def test_head13(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f or m",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine"]})

    def test_head14(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f, m",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine"]})

    def test_head15(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f, m, n",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine", "neuter"]})

    def test_head16(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f or m or n",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine", "neuter"]})

    def test_head17(self):
        data = {}
        self.wxr.wtp.start_page("index")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "index n",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["neuter"]})

    def test_head18(self):
        data = {}
        self.wxr.wtp.start_page("index")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "index m or f (genitive indicis); third declension",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["declension-3", "feminine",
                                         "masculine"],
                                "forms": [
                                    {"tags": ["genitive"],
                                     "form": "indicis"},
                                ]})

    def test_head19(self):
        data = {}
        self.wxr.wtp.start_page("index")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun", "foo f or bar m", data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical", "feminine"]},
            {"form": "bar", "tags": ["canonical", "masculine"]},
        ]})

    def test_head20(self):
        data = {}
        self.wxr.wtp.start_page("index")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun", "foo or bar", data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical"]},
            {"form": "bar", "tags": ["canonical"]},
        ]})

    def test_head21(self):
        data = {}
        self.wxr.wtp.start_page("index")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun", "foo f or n or bar m or c", data,
                        False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [
            {"form": "foo", "tags": ["canonical", "feminine", "neuter"]},
            {"form": "bar", "tags": ["canonical", "common-gender",
                                     "masculine"]},
        ]})

    def test_head22(self):
        data = {}
        parse_word_head(self.wxr, "noun",
                        "testpage f or testpage2 m; person",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["person"],
                                "forms": [
                                    {"tags": ["canonical", "feminine"],
                                     "form": "testpage"},
                                    {"tags": ["canonical", "masculine"],
                                     "form": "testpage2"},
                                ]})

    def test_head23(self):
        data = {}
        self.wxr.wtp.start_page("indubitables")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Adjective")
        parse_word_head(self.wxr, "adj", "indubitables m pl or f pl", data,
                        False, None)
        # print(json.dumps(data, indent=2))
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["feminine", "masculine", "plural"]})

    def test_head24(self):
        data = {}
        self.wxr.wtp.start_page("foo")
        self.wxr.wtp.start_section("Japanese")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "foo (12 strokes)",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [
            {"tags": ["strokes"],
             "form": "12"},
            ]})

    def test_head25(self):
        data = {}
        self.wxr.wtp.start_page("smiley")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "smiley m (plural smileys, diminutive smileytje n)",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"tags": ["masculine"],
                                "forms": [
            {"tags": ["plural"],
             "form": "smileys"},
            {"tags": ["diminutive", "neuter"],
             "form": "smileytje"},
            ]})

    def test_head26(self):
        data = {}
        self.wxr.wtp.start_page("foos")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "foos (plural of foo)",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(data, {"forms": [
            {"tags": ["plural-of"],
             "form": "foo"},
            ]})

    def test_head27(self):
        data = {}
        self.wxr.wtp.start_page("أَبْلَعَ")
        self.wxr.wtp.start_section("Arabic")
        self.wxr.wtp.start_subsection("Verb")
        parse_word_head(self.wxr, "verb",
                        "أَبْلَعَ (ʾablaʿa) IV, non-past يُبْلِعُ‎‎ (yubliʿu)",
                        data, False, None)
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
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
        self.wxr.wtp.start_page("tell")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "tell (third-person singular simple present tells, present participle telling, simple past and past participle told or (dialectal or nonstandard) telled)",
                        data, False, None)
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

    def test_head29(self):
        data = {}
        self.maxDiff = 10000
        self.wxr.wtp.start_page("take")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "take (third-person singular simple present takes, present participle taking, simple past took, past participle taken or (archaic or Scotland) tane)",
                        data, False, None)
        print(json.dumps(data, indent=2, sort_keys=True))
        self.assertEqual(data, {
            "forms": [
              {
                "form": "takes",
                "tags": [
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "taking",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "took",
                "tags": [
                  "past"
                ]
              },
              {
                "form": "taken",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "tane",
                "tags": [
                  "Scotland",
                  "archaic",
                  "participle",
                  "past"
                ]
              },
            ],
        })

    def test_head30(self):
        data = {}
        self.maxDiff = 10000
        self.wxr.wtp.start_page("burn")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "burn (third-person singular simple present burns, present participle burning, simple past and past participle burned or (mostly Commonwealth) burnt or (obsolete) brent)",
                        data, False, None)
        print(json.dumps(data, indent=2, sort_keys=True))
        self.assertEqual(data, {
            "forms": [
                {
                  "form": "burns",
                  "tags": [
                    "present",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "burning",
                  "tags": [
                    "participle",
                    "present"
                  ]
                },
                {
                  "form": "burned",
                  "tags": [
                    "participle",
                    "past"
                  ]
                },
                {
                  "form": "burned",
                  "tags": [
                    "past"
                  ]
                },
                {
                  "form": "burnt",
                  "tags": [
                    "Commonwealth",
                    "participle",
                    "past"
                  ]
                },
                {
                  "form": "burnt",
                  "tags": [
                    "Commonwealth",
                    "past"
                  ]
                },
                {
                  "form": "brent",
                  "tags": [
                    "obsolete",
                    "participle",
                    "past"
                  ]
                },
                {
                  "form": "brent",
                  "tags": [
                    "obsolete",
                    "past"
                  ]
                },
            ],
        })

    def test_head31(self):
        data = {}
        self.maxDiff = 10000
        self.wxr.wtp.start_page("grind")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "grind (third-person singular simple present grinds, present participle grinding, simple past and past participle ground or grinded) (see usage notes below)",
                        data, False, None)
        print(json.dumps(data, indent=2, sort_keys=True))
        self.assertEqual(data, {
            "forms": [
                {
                  "form": "grinds",
                  "tags": [
                    "present",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "grinding",
                  "tags": [
                    "participle",
                    "present"
                  ]
                },
                {
                  "form": "ground",
                  "tags": [
                    "participle",
                    "past"
                  ]
                },
                {
                  "form": "ground",
                  "tags": [
                    "past"
                  ]
                },
                {
                  "form": "grinded",
                  "tags": [
                    "participle",
                    "past"
                  ]
                },
                {
                  "form": "grinded",
                  "tags": [
                    "past"
                  ]
                },
            ],
        })

    def test_head32(self):
        data = {}
        self.maxDiff = 10000
        self.wxr.wtp.start_page("rive")
        self.wxr.wtp.start_section("Danish")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "rive (past tense rev, past participle revet, common gender attributive reven, plural or definite attributive revne)",
                        data, False, None)
        print(json.dumps(data, indent=2, sort_keys=True))
        self.assertEqual(data, {
            "forms": [
                {
                  "form": "rev",
                  "tags": [
                    "past"
                  ]
                },
                {
                  "form": "revet",
                  "tags": [
                    "participle",
                    "past"
                  ]
                },
                {
                  "form": "reven",
                  "tags": [
                    "attributive",
                    "common-gender",
                    "participle",
                    "past"
                  ]
                },
                {
                  "form": "revne",
                  "tags": [
                    "attributive",
                    "definite",
                    "participle",
                    "past",
                    "singular"
                  ]
                },
                {
                  "form": "revne",
                  "tags": [
                    "attributive",
                    "participle",
                    "past",
                    "plural"
                  ]
                },
            ],
        })

    def test_head33(self):
        data = {}
        self.maxDiff = 10000
        self.wxr.wtp.start_page("rear admiral (lower half)")
        self.wxr.wtp.start_section("English")
        self.wxr.wtp.start_subsection("Noun")
        parse_word_head(self.wxr, "noun",
                        "rear admiral (lower half) (plural rear admirals "
                        "(lower half))",
                        data, False, None)
        print(json.dumps(data, indent=2, sort_keys=True))
        self.assertEqual(data, {
            "forms": [
                {
                  "form": "rear admirals (lower half)",
                  "tags": [
                    "plural"
                  ]
                }]})

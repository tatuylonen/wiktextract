# Tests for parsing a page
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import json
import unittest
from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.page import parse_page

class PageTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 20000
        conf1 = WiktionaryConfig(capture_language_codes=None,
                                       capture_translations=True,
                                       capture_pronunciation=True,
                                       capture_linkages=True,
                                       capture_compounds=True,
                                       capture_redirects=True,
                                       capture_examples=True)
        self.wxr = WiktextractContext(Wtp(), conf1)
        self.wxr.wtp.analyze_templates()
        self.wxr.wtp.start_page("testpage")

    def runpage(self, text):
        assert isinstance(text, str)
        return parse_page(self.wxr, self.wxr.wtp.title, text)

    def test_page1(self):
        lst = self.runpage("""
==Swedish==
===Noun===
foo f

# sense 1
# sense 2
""")
        # XXX should also capture examples
        self.assertEqual(lst, [
            {
                "forms": [
                    {
                        "form": "foo",
                        "tags": [
                            "canonical",
                            "feminine"
                        ]
                    }
                ],
                "lang": "Swedish",
                "lang_code": "sv",
                "pos": "noun",
                "senses": [
                    {
                        "glosses": [
                            "sense 1"
                        ],
                    },
                    {
                        "glosses": [
                            "sense 2"
                        ],
                    }
                ],
                "word": "testpage"
            }
        ])

    def test_page2(self):
        lst = self.runpage("""
==Swedish==
===Noun===
testpage f

# sense 1
""")
        # XXX should also capture examples
        self.assertEqual(lst, [
            {
                "lang": "Swedish",
                "lang_code": "sv",
                "pos": "noun",
                "senses": [
                    {
                        "glosses": ["sense 1"],
                        "tags": ["feminine"],
                    },
                ],
                "word": "testpage"
            }
        ])

    def test_page3(self):
        self.wxr.wtp.start_page("Unsupported titles/C sharp")
        lst = self.runpage("""
==Swedish==
===Noun===
foo

# sense 1
""")
        # XXX should also capture examples
        self.assertEqual(lst, [
            {
                "forms": [
                    {"form": "foo", "tags": ["canonical"]},
                ],
                "lang": "Swedish",
                "lang_code": "sv",
                "pos": "noun",
                "senses": [
                    {
                        "glosses": ["sense 1"],
                    },
                ],
                "word": "C#"
            }
        ])

    def test_page4(self):
        self.wxr.wtp.start_page("foo")
        lst = self.runpage("""
==English==

===Noun===
foo

# sense 1
# sense 2
# (mycology) mushroom
# (person) one who foos

====Translations====
* Finnish: fuu
* Swedish: bar m, hop f

====Related terms====
* (sense abc) zap
* verbs: zip, zump

""")
        print("RETURNED:", json.dumps(lst, indent=2, sort_keys=True))
        # XXX should also capture examples
        self.assertEqual(lst, [
            {
                "lang": "English",
                "lang_code": "en",
                "pos": "noun",
                "related": [
                    {"sense": "sense abc", "word": "zap"},
                    {"word": "zip", "tags": ["verb"]},
                    {"word": "zump", "tags": ["verb"]},
                ] ,
                "senses": [
                    {
                        "glosses": ["sense 1"],
                    },
                    {
                        "glosses": ["sense 2"],
                    },
                    {
                        "glosses": ["mushroom"],
                        "raw_glosses": ["(mycology) mushroom"],
                        "topics": ["biology", "mycology","natural-sciences"],
                    },
                    {
                        "glosses": ["one who foos"],
                        "raw_glosses": ["(person) one who foos"],
                        "tags": ["person"],
                    },
                ],
                "translations": [
                    {"word": "fuu", "lang": "Finnish", "code": "fi"},
                    {"word": "bar", "lang": "Swedish", "code": "sv",
                     "tags": ["masculine"]},
                    {"word": "hop", "lang": "Swedish", "code": "sv",
                     "tags": ["feminine"]},
                ],
                "word": "foo",
            }
        ])

    def test_page5(self):
        self.wxr.wtp.start_page("foo")
        lst = self.runpage("""
==English==

===Noun===
foo

# sense 1
#: example 1 causes sense 1 to get pushed
## subsense 1
##: subexample 1
## subsense 2
# sense 2
# (mycology) mushroom
#: example 2
#: example 3
# (person) one who foos
## one who foos more specifically
## another one who foos

====Translations====
* Finnish: fuu
* Swedish: bar m, hop f

====Related terms====
* (sense abc) zap
* verbs: zip, zump

""")
        print("RETURNED:", json.dumps(lst, indent=2, sort_keys=True))
        self.assertEqual(lst, [
            {
                "lang": "English",
                "lang_code": "en",
                "pos": "noun",
                "related": [
                    {"sense": "sense abc", "word": "zap"},
                    {"word": "zip", "tags": ["verb"]},
                    {"word": "zump", "tags": ["verb"]},
                ] ,
                "senses": [
                    {
                        "glosses": ["sense 1", "subsense 1"],
                        "examples": [{"text": "subexample 1"}]
                    },
                    {
                        "glosses": ["sense 1", "subsense 2"],
                    },
                    {
                        "glosses": ["sense 1"],
                        "examples": [{"text":
                                    "example 1 causes sense 1 to get pushed"}]
                    },
                    {
                        "glosses": ["sense 2"],
                    },
                    {
                        "glosses": ["mushroom"],
                        "raw_glosses": ["(mycology) mushroom"],
                        "topics": ["biology", "mycology", "natural-sciences"],
                        "examples": [{"text": "example 2"},
                                     {"text": "example 3"}],
                    },
                    {
                        "glosses": ["one who foos",
                                    "one who foos more specifically"],
                        "raw_glosses": ["(person) one who foos",
                                    "one who foos more specifically"],
                        "tags": ["person"],
                    },
                    {
                        "glosses": ["one who foos",
                                    "another one who foos"],
                        "raw_glosses": ["(person) one who foos",
                                    "another one who foos"],
                        "tags": ["person"],
                    },
                ],
                "translations": [
                    {"word": "fuu", "lang": "Finnish", "code": "fi"},
                    {"word": "bar", "lang": "Swedish", "code": "sv",
                     "tags": ["masculine"]},
                    {"word": "hop", "lang": "Swedish", "code": "sv",
                     "tags": ["feminine"]},
                ],
                "word": "foo",
            }
        ])

    def test_page6(self):
        lst = self.runpage("""
==Japanese==
===Verb===
foo

# sense 1
#: <dl><dd><span class="Jpan" lang="ja"><a href="/wiki/%E3%81%94%E9%A3%AF#Japanese" title="ご飯">ご<ruby>飯<rp>(</rp><rt>はん</rt><rp>)</rp></ruby></a>を<b><ruby>食<rp>(</rp><rt>た</rt><rp>)</rp></ruby>べる</b></span><dl><dd><i>go-han o <b>taberu</b></i></dd><dd>to <b>eat</b> a meal</dd></dl></dd></dl>
""")
        self.assertEqual(lst, [
            {
                "forms": [
                    {
                        "form": "foo",
                        "tags": [
                            "canonical",
                        ]
                    }
                ],
                "lang": "Japanese",
                "lang_code": "ja",
                "pos": "verb",
                "senses": [
                    {
                        "glosses": [
                            "sense 1"
                        ],
                        "examples":
                            [{"english": "to eat a meal",
                              "roman": "go-han o taberu",
                              "ruby": [
                                       ('飯', 'はん'),
                                       ('食', 'た')
                                      ],
                              "text": "ご飯を食べる"}],
                    },
                ],
                "word": "testpage"
            }
        ])

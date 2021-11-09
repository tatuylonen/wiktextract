# Tests for parsing a page
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import json
import unittest
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.page import parse_page

class PageTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 20000
        self.ctx = Wtp()
        self.ctx.analyze_templates()
        self.ctx.start_page("testpage")
        self.config = WiktionaryConfig(capture_languages=None,
                                       capture_translations=True,
                                       capture_pronunciation=True,
                                       capture_linkages=True,
                                       capture_compounds=True,
                                       capture_redirects=True,
                                       capture_examples=True)

    def runpage(self, text):
        assert isinstance(text, str)
        return parse_page(self.ctx, self.ctx.title, text, self.config)

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
                        "raw_glosses": [
                            "sense 1"
                        ],
                    },
                    {
                        "glosses": [
                            "sense 2"
                        ],
                        "raw_glosses": [
                            "sense 2"
                        ]
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
                        "raw_glosses": ["sense 1"],
                        "tags": ["feminine"],
                    },
                ],
                "word": "testpage"
            }
        ])

    def test_page3(self):
        self.ctx.start_page("Unsupported titles/C sharp")
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
                        "raw_glosses": ["sense 1"],
                    },
                ],
                "word": "C#"
            }
        ])

    def test_page4(self):
        self.ctx.start_page("foo")
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
                        "raw_glosses": ["sense 1"],
                    },
                    {
                        "glosses": ["sense 2"],
                        "raw_glosses": ["sense 2"],
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




#     def test_page1(self):
#         lst = self.runpage("""
# ==Swedish==
# ===Noun===
# foo f

# # sense 1
# #: example 1.1
# # sense 2
# #: example 2.1
# #: example 2.2
# """)
#         print(json.dumps(lst, indent=2, sort_keys=True))
#         # XXX should also capture examples
#         self.assertEqual(lst, [
#             {
#                 "forms": [
#                     {
#                         "form": "foo",
#                         "tags": [
#                             "canonical",
#                             "feminine"
#                         ]
#                     }
#                 ],
#                 "lang": "Swedish",
#                 "lang_code": "sv",
#                 "pos": "noun",
#                 "senses": [
#                     {
#                         "glosses": [
#                             "sense 1"
#                         ]
#                     },
#                     {
#                         "glosses": [
#                             "sense 2"
#                         ]
#                     }
#                 ],
#                 "word": "testpage"
#             }
#         ])

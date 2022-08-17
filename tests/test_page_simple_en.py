# Tests for parsing a Simple English page, which has a different structure from other Wiktionaries
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
                                       capture_examples=True,
                                       edition="simple")

    def runpage(self, text):
        assert isinstance(text, str)
        return parse_page(self.ctx, self.ctx.title, text, self.config)

    def test_page1(self):
        lst = self.runpage("""
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
                "lang": "English",
                "lang_code": "en",
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
===Noun===
testpage f

# sense 1
""")
        # XXX should also capture examples
        self.assertEqual(lst, [
            {
                "lang": "English",
                "lang_code": "en",
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
                "lang": "English",
                "lang_code": "en",
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


# TODO: extract Pronunciations
# TODO: extract noun and verb inflection charts
    def test_real_page_freeze(self):
        self.ctx.start_page("freeze")
        lst = self.runpage("""
=== Pronunciation ===
* {{SAMPA|/"fri:z/}}
* {{IPA|/ˈfriːz/}}
* {{audio|en-us-freeze.ogg|Audio (US)}}

==== Homophones ====
*[[frees]]

== Verb ==
{{verb2|freeze|freezes|froze|frozen|freezing}}
{{ti verb}}
#If you '''freeze''' something, you [[cool]] it until it becomes [[solid]].
#:''Water '''freezes''' at 0°C.''
#:''The chicken will go bad soon. We should '''freeze''' it and then we can cook it next week.''
#If you '''freeze''', you feel very cold.
#:''I was '''freezing''' because I had forgotten my [[coat]].''

== Noun ==
{{noun}}
#{{countable}} A '''freeze''' is a time when the temperature is cold.
#{{countable}} A '''freeze''' is when the usual way things are done is stopped.

=== Related words ===
* [[freezer]]

[[Category:Weather]]

""")
        print("RETURNED:", json.dumps(lst, indent=2, sort_keys=True))
        # XXX should also capture examples
        self.assertEqual(lst, [
  {
    "categories": [
      "Weather"
    ],
    "lang": "English",
    "lang_code": "en",
    "pos": "verb",
    "senses": [
      {
        "examples": [
          {
            "text": "Water freezes at 0\u00b0C."
          },
          {
            "text": "The chicken will go bad soon. We should freeze it and then we can cook it next week."
          }
        ],
        "glosses": [
          "If you freeze something, you cool it until it becomes solid."
        ],
        "raw_glosses": [
          "If you freeze something, you cool it until it becomes solid."
        ]
      },
      {
        "examples": [
          {
            "text": "I was freezing because I had forgotten my coat."
          }
        ],
        "glosses": [
          "If you freeze, you feel very cold."
        ],
        "raw_glosses": [
          "If you freeze, you feel very cold."
        ]
      }
    ],
    "word": "freeze"
  },
  {
    "categories": [
      "Weather"
    ],
    "lang": "English",
    "lang_code": "en",
    "pos": "noun",
    "related": [
      {
        "word": "freezer"
      }
    ],
    "senses": [
      {
        "glosses": [
          "A freeze is a time when the temperature is cold."
        ],
        "raw_glosses": [
          "A freeze is a time when the temperature is cold."
        ]
      },
      {
        "glosses": [
          "A freeze is when the usual way things are done is stopped."
        ],
        "raw_glosses": [
          "A freeze is when the usual way things are done is stopped."
        ]
      }
    ],
    "word": "freeze"
  }
])


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
#: example 1.1
# sense 2
#: example 2.1
#: example 2.2
""")
        print(json.dumps(lst, indent=2, sort_keys=True))
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
                        ]
                    },
                    {
                        "glosses": [
                            "sense 2"
                        ]
                    }
                ],
                "word": "testpage"
            }
        ])

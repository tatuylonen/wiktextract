# Tests for parse_word_head()
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.form_descriptions import parse_word_head

class HeadTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")
        self.ctx.start_section("English")

    def test_head1(self):
        data = {}
        parse_word_head(self.ctx, "noun", "", data)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {})

    def test_head2(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage", data)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {})

    def test_head3(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpAge", data)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testpAge",
                                           "tags": ["canonical"]}]})

    def test_head4(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage f", data)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"tags": ["feminine"]})

    def test_head5(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpAge m", data)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"forms": [{"form": "testpAge",
                                           "tags": ["canonical"]}],
                                "tags": ["masculine"]})

    def test_head6(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage n", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["neuter"]})

    def test_head7(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage c", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["common"]})

    def test_head8(self):
        data = {}
        self.ctx.start_section("Zulu")
        parse_word_head(self.ctx, "noun", "testpage 1", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["class-1"]})

    def test_head8b(self):
        # Trying to parse suffix 1 in English - should not get parsed
        data = {}
        parse_word_head(self.ctx, "noun", "testpage 1", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"forms": [{"form": "testpage 1",
                                           "tags": ["canonical"]}]})

    def test_head9(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, inanimate)", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["feminine", "plurale-tantum",
                                         "inanimate"]})

    def test_head10(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate)",
                        data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["feminine", "plurale-tantum",
                                         "inanimate"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

    def test_head11(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate) "
                        "(+ dative)",
                        data)
        self.assertEqual(self.ctx.warnings, [])
        print(data)
        self.assertEqual(data, {"tags": ["feminine", "plurale-tantum",
                                         "inanimate", "with-dative"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

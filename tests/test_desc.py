import unittest
import collections
import wiktextract
from wiktextract.form_descriptions import (
    decode_tags, parse_word_head, classify_desc)
from wiktextract import WiktionaryConfig
from wikitextprocessor import Wtp
from wiktextract.datautils import split_at_comma_semi


class DescTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")
        self.ctx.start_section("English")

    def test_head1(self):
        data = {}
        parse_word_head(self.ctx, "noun", "", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {})

    def test_head2(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {})

    def test_head3(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpAge", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"forms": [{"form": "testpAge",
                                           "tags": ["canonical"]}]})

    def test_head4(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpage f", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["feminine"]})

    def test_head5(self):
        data = {}
        parse_word_head(self.ctx, "noun", "testpAge m", data)
        self.assertEqual(self.ctx.warnings, [])
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
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, inanimate)", data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["feminine", "plurale-tantum",
                                         "inanimate"]})

    def test_head9(self):
        data = {}
        parse_word_head(self.ctx, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate)",
                        data)
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(data, {"tags": ["feminine", "plurale-tantum",
                                         "inanimate"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

    def test_head10(self):
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

    def test_comma_semi1(self):
        self.assertEqual(split_at_comma_semi(""), [])

    def test_comma_semi2(self):
        self.assertEqual(split_at_comma_semi("foo bar"), ["foo bar"])

    def test_comma_semi3(self):
        self.assertEqual(split_at_comma_semi("foo bar, zappa"),
                         ["foo bar", "zappa"])

    def test_comma_semi4(self):
        self.assertEqual(split_at_comma_semi("foo , bar; zappa"),
                         ["foo", "bar", "zappa"])

    def test_comma_semi5(self):
        self.assertEqual(split_at_comma_semi("a (foo, bar); zappa"),
                         ["a (foo bar)", "zappa"])

    def test_comma_semi5(self):
        self.assertEqual(split_at_comma_semi("a (foo, bar)[1; zappa], z"),
                         ["a (foo, bar)[1; zappa]", "z"])

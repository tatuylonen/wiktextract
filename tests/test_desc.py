import unittest
import collections
import wiktextract
from wiktextract.form_descriptions import decode_tags, parse_word_head
from wiktextract import WiktionaryConfig
from wikitextprocessor import Wtp


class WiktExtractTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")

    def test_empty(self):
        ret = decode_tags(self.config, [])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, [])

    def test_singular(self):
        ret = decode_tags(self.config, ["singular"])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, ["singular"])

    def test_unknown(self):
        ret = decode_tags(self.config, ["unknowntag"])
        self.assertNotEqual(self.config.warnings, [])
        self.assertEqual(ret, ["error"])

    def test_plural_partitive(self):
        ret = decode_tags(self.config, ["plural", "partitive"])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, ["plural", "partitive"])

    def test_combo(self):
        ret = decode_tags(self.config, ["class", "2a",
                                        "stress", "pattern", "1"])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, ["class 2a", "stress pattern 1"])

    def test_combo_err(self):
        ret = decode_tags(self.config, ["class", "2a",
                                        "stress", "pattern", "xyz"])
        self.assertNotEqual(self.config.warnings, [])
        self.assertEqual(ret, ["class 2a", "error"])

    def test_head1(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun", "", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {})

    def test_head2(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun", "testpage", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {})

    def test_head3(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpAge", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {"forms": [{"form": "testpAge",
                                           "tags": ["canonical"]}]})

    def test_head4(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpage f", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {"tags": ["feminine"]})

    def test_head5(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpAge m", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {"forms": [{"form": "testpAge",
                                           "tags": ["canonical"]}],
                                "tags": ["masculine"]})

    def test_head6(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpage n", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {"tags": ["neuter"]})

    def test_head7(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpage c", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {"tags": ["common"]})

    def test_head8(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpage f (plurale tantum, inanimate)", data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {"tags": ["feminine", "plurale tantum",
                                         "inanimate"]})

    def test_head9(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate)",
                        data)
        self.assertEqual(self.config.warnings, [])
        print(data)
        self.assertEqual(data, {"tags": ["feminine", "plurale tantum",
                                         "inanimate"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

    def test_head10(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate) "
                        "(+ dative)",
                        data)
        self.assertEqual(self.config.warnings, [])
        print(data)
        self.assertEqual(data, {"tags": ["feminine", "plurale tantum",
                                         "inanimate", "with dative"],
                                "forms": [{"tags": ["stem"],
                                           "form": "testpag"}]})

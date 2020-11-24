import unittest
import collections
import wiktextract
from wiktextract.form_descriptions import decode_tags, parse_word_head
from wiktextract import WiktionaryConfig
from wikitextprocessor import Wtp
from wiktextract.datautils import split_at_comma_semi


class WiktExtractTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")

    def test_empty(self):
        ret = decode_tags(self.config, [])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, ([()], []))

    def test_singular(self):
        ret, topics = decode_tags(self.config, ["singular"])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, [("singular",)])

    def test_topics(self):
        ret, topics = decode_tags(self.config, ["singular", "nautical"])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, [("singular",)])
        self.assertEqual(topics, ["nautical"])

    def test_unknown(self):
        ret, topics = decode_tags(self.config, ["unknowntag"])
        self.assertNotEqual(self.config.warnings, [])
        self.assertEqual(ret, [("error",)])

    def test_plural_partitive(self):
        ret, topics = decode_tags(self.config, ["partitive", "plural"])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, [("partitive", "plural")])

    def test_combo(self):
        ret, topics = decode_tags(self.config, ["class", "2a",
                                                "stress", "pattern", "1"])
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(ret, [("class-2a", "stress-pattern-1")])

    def test_combo_err(self):
        ret, topics = decode_tags(self.config, ["class", "2a",
                                                "stress", "pattern", "xyz"])
        self.assertNotEqual(self.config.warnings, [])
        self.assertEqual(ret, [("class-2a", "error")])

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
        self.assertEqual(data, {"tags": ["feminine", "plurale-tantum",
                                         "inanimate"]})

    def test_head9(self):
        data = {}
        parse_word_head(self.ctx, self.config, "noun",
                        "testpage f (plurale tantum, stem testpag, inanimate)",
                        data)
        print(data)
        self.assertEqual(self.config.warnings, [])
        self.assertEqual(data, {"tags": ["feminine", "plurale-tantum",
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

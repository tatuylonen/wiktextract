import unittest
import collections
import wiktextract
from wiktextract.form_descriptions import (
    decode_tags, parse_word_head, classify_desc)
from wiktextract import WiktionaryConfig
from wikitextprocessor import Wtp
from wiktextract.datautils import split_at_comma_semi


class WiktExtractTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")
        self.ctx.start_section("English")

    def test_empty(self):
        ret = decode_tags("")
        self.assertEqual(ret, ([()], []))

    def test_singular(self):
        ret, topics = decode_tags("singular")
        self.assertEqual(ret, [("singular",)])

    def test_topics(self):
        ret, topics = decode_tags("singular, nautical")
        self.assertEqual(ret, [("singular",)])
        self.assertEqual(topics, ["nautical"])

    def test_unknown(self):
        ret, topics = decode_tags("unknowntag")
        self.assertEqual(ret, [("error-unknown-tag", "unknowntag")])

    def test_plural_partitive(self):
        ret, topics = decode_tags("plural partitive")
        self.assertEqual(ret, [("partitive", "plural")])

    def test_combo(self):
        ret, topics = decode_tags("class 2a stress pattern 1")
        self.assertEqual(ret, [("class-2a", "stress-pattern-1")])

    def test_combo_err(self):
        ret, topics = decode_tags("class 2a stress pattern xyz")
        self.assertEqual(ret, [("class-2a", "error-unknown-tag",
                                "stress pattern xyz")])

    def test_decode1(self):
        ret, topics = decode_tags("Cockney rhyming slang")
        self.assertEqual(ret, [("Cockney", "slang")])

    def test_decode3(self):
        ret, topics = decode_tags("colloquial slang sailing")
        self.assertEqual(ret, [("colloquial", "slang")])
        self.assertEqual(topics, ["sailing", "nautical"])

    def test_decode4(self):
        ret, topics = decode_tags("colloquial Cockney rhyming slang")
        self.assertEqual(ret, [("Cockney", "colloquial", "slang")])

    def test_decode5(self):
        ret, topics = decode_tags("colloquial Cockney Test rhyming slang")
        self.assertEqual(ret, [("Cockney", "Test", "colloquial",
                                "error-unknown-tag", "slang")])

    def test_decode6(self):
        ret, topics = decode_tags("colloquial Cockney Test unknown1 "
                                  "rhyming slang")
        self.assertEqual(ret, [("Cockney", "Test unknown1", "colloquial",
                                "error-unknown-tag", "slang")])

    def test_decode7(self):
        ret, topics = decode_tags("colloquial Cockney Test unknown1 "
                                  "rhyming slang",
                                  allow_any=True)
        self.assertEqual(ret, [("Cockney", "Test unknown1", "colloquial",
                                "slang")])

    def test_decode8(self):
        ret, topics = decode_tags("colloquial Cockney rhyming slang "
                                  "Test unknown1",
                                  allow_any=True)
        self.assertEqual(ret, [("Cockney", "Test unknown1", "colloquial",
                                "slang")])

    def test_decode9(self):
        ret, topics = decode_tags("simple past and past participle")
        self.assertEqual(topics, [])
        self.assertEqual(ret, [("participle", "past"), ("past", "simple")])

    def test_decode10(self):
        ret, topics = decode_tags("colloquial Cockney Test, unknown1; "
                                  "rhyming slang",
                                  allow_any=True)
        self.assertEqual(ret, [("Cockney", "Test", "colloquial",
                                "slang", "unknown1")])
    def test_decode11(self):
        ret, topics = decode_tags("intransitive, in perfect tenses, "
                                  "without predicate")
        self.assertEqual(ret, [("in perfect tenses",
                                "intransitive",
                                "without predicate")])

    def test_decode12(self):
        ret, topics = decode_tags("as a modifier in compound words")
        self.assertEqual(ret, [("in-compounds",)])

    def test_decode13(self):
        ret, topics = decode_tags("with a cardinal numeral")
        self.assertEqual(ret, [("with a cardinal numeral",)])

    def test_decode14(self):
        ret, topics = decode_tags("usually in the negative")
        self.assertEqual(ret, [("usually", "with-negation")])

    def test_decode15(self):
        ret, topics = decode_tags("Lepcha numerals")
        self.assertEqual(ret, [("Lepcha", "numeral")])

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

    def test_classify1(self):
        cls = classify_desc("predicative particle")
        self.assertEqual(cls, "tags")

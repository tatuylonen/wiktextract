# Tests for decode_tags() and generally tag and topic handling
#
# Copyright (c) 2020-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
from wiktextract.form_descriptions import decode_tags
from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor import Wtp

class TagTests(unittest.TestCase):

    def test_empty(self):
        ret = decode_tags("")
        self.assertEqual(ret, ([()], []))

    def test_unknown(self):
        ret, topics = decode_tags("unknowntag")
        self.assertEqual(ret, [("error-unknown-tag",)])

    def test_tags1(self):
        ret, topics = decode_tags("singular")
        self.assertEqual(ret, [("singular",)])

    def test_tags2(self):
        ret, topics = decode_tags("plural")
        self.assertEqual(ret, [("plural",)])

    def test_tags3(self):
        ret, topics = decode_tags("plural partitive")
        self.assertEqual(ret, [("partitive", "plural")])

    def test_tags4(self):
        ret, topics = decode_tags("progressive")
        self.assertEqual(ret, [("progressive",)])

    def test_tags5(self):
        ret, topics = decode_tags("past")
        self.assertEqual(ret, [("past",)])

    def test_tags6(self):
        ret, topics = decode_tags("present participle")
        self.assertEqual(ret, [("participle", "present")])

    def test_tags7(self):
        ret, topics = decode_tags("third-person singular")
        self.assertEqual(ret, [("singular", "third-person")])

    def test_tags8(self):
        ret, topics = decode_tags("past participle")
        self.assertEqual(ret, [("participle", "past")])

    def test_tags9(self):
        ret, topics = decode_tags("transitive")
        self.assertEqual(ret, [("transitive",)])

    def test_tags10(self):
        ret, topics = decode_tags("intransitive")
        self.assertEqual(ret, [("intransitive",)])

    def test_tags11(self):
        ret, topics = decode_tags("obsolete archaic, dialectal slang")
        self.assertEqual(ret, [("archaic", "dialectal", "obsolete", "slang")])

    def test_tags12(self):
        ret, topics = decode_tags("class 2a stress pattern 1")
        self.assertEqual(ret, [("class-2a", "stress-pattern-1")])

    def test_tags13(self):
        ret, topics = decode_tags("class 2a stress pattern xyz")
        self.assertEqual(ret, [("class-2a", "error-unknown-tag",)])

    def test_tags14(self):
        ret, topics = decode_tags("Cockney rhyming slang")
        self.assertEqual(ret, [("Cockney", "slang")])

    def test_tags15(self):
        ret, topics = decode_tags("colloquial slang sailing")
        self.assertEqual(ret, [("colloquial", "slang")])
        self.assertEqual(topics, ["sailing", "nautical", "transport"])

    def test_tags16(self):
        ret, topics = decode_tags("colloquial Cockney rhyming slang")
        self.assertEqual(ret, [("Cockney", "colloquial", "slang")])

    def test_tags17(self):
        ret, topics = decode_tags("colloquial Cockney Test rhyming slang")
        self.assertEqual(ret, [("Cockney", "colloquial",
                                "error-unknown-tag", "slang")])

    def test_tags18(self):
        ret, topics = decode_tags("colloquial Cockney Test unknown1 "
                                  "rhyming slang")
        self.assertEqual(ret, [("Cockney", "colloquial",
                                "error-unknown-tag", "slang")])

    def test_tags19(self):
        ret, topics = decode_tags("colloquial Cockney Test unknown1 "
                                  "rhyming slang",
                                  allow_any=True)
        self.assertEqual(ret, [("Cockney", "Test unknown1", "colloquial",
                                "slang")])

    def test_tags20(self):
        ret, topics = decode_tags("colloquial Cockney rhyming slang "
                                  "Test unknown1",
                                  allow_any=True)
        self.assertEqual(ret, [("Cockney", "Test unknown1", "colloquial",
                                "slang")])

    def test_tags21(self):
        ret, topics = decode_tags("simple past and past participle")
        self.assertEqual(topics, [])
        self.assertEqual(ret, [("participle", "past"), ("past",)])

    def test_tags22(self):
        ret, topics = decode_tags("colloquial Cockney Test, unknown1; "
                                  "rhyming slang",
                                  allow_any=True)
        self.assertEqual(ret, [("Cockney", "Test", "colloquial",
                                "slang", "unknown1")])
    def test_tags23(self):
        ret, topics = decode_tags("intransitive, in perfect tenses, "
                                  "without predicate")
        self.assertEqual(ret, [("in perfect tenses",
                                "intransitive",
                                "without predicate")])

    def test_tags24(self):
        ret, topics = decode_tags("as a modifier in compound words")
        self.assertEqual(ret, [("in-compounds",)])

    def test_tags25(self):
        ret, topics = decode_tags("with a cardinal numeral")
        self.assertEqual(ret, [("with a cardinal numeral",)])

    def test_tags26(self):
        ret, topics = decode_tags("usually in the negative")
        self.assertEqual(ret, [("usually", "with-negation")])

    def test_tags27(self):
        ret, topics = decode_tags("Lepcha numerals")
        self.assertEqual(ret, [("Lepcha", "numeral")])

    def test_tags28(self):
        ret, topics = decode_tags("next 4")
        self.assertEqual(ret, [("error-unknown-tag", "next")])

    def test_tags29(self):
        ret, topics = decode_tags("Baan Nong Duu")
        self.assertEqual(ret, [("Baan-Nong-Duu",)])

    def test_tags30(self):
        ret, topics = decode_tags("Devanagari numerals")
        self.assertEqual(ret, [("Devanagari", "numeral")])

    def test_tags31(self):
        ret, topics = decode_tags("US")
        self.assertEqual(ret, [("US",)])

    def test_tags32(self):
        ret, topics = decode_tags("UK")
        self.assertEqual(ret, [("UK",)])

    def test_tags32(self):
        ret, topics = decode_tags("UK")
        self.assertEqual(ret, [("UK",)])

    def test_tags33(self):
        ret, topics = decode_tags("British")
        self.assertEqual(ret, [("British",)])

    def test_tags34(self):
        ret, topics = decode_tags("Audio")
        self.assertEqual(ret, [()])

    def test_tags35(self):
        ret, topics = decode_tags("US/UK")
        self.assertEqual(ret, [("UK", "US")])

    def test_tags36(self):
        ret, topics = decode_tags("slang, dialectal term")
        self.assertEqual(ret, [("dialectal", "slang")])

    def test_tags37(self):
        ret, topics = decode_tags("usually plural")
        self.assertEqual(ret, [("plural", "usually")])

    def test_tags38(self):
        ret, topics = decode_tags("sometimes colloquial")
        self.assertEqual(ret, [("colloquial", "sometimes")])

    def test_tags39(self):
        ret, topics = decode_tags("with inf., obsolescent")
        self.assertEqual(ret, [("obsolete", "possibly","with-infinitive")])

    def test_tags40(self):
        ret, topics = decode_tags("transitive of people")
        self.assertEqual(ret, [("of people", "transitive")])

    def test_tags41(self):
        ret, topics = decode_tags("transitive of")
        self.assertEqual(ret, [("error-unknown-tag", "transitive")])

    def test_tags42(self):
        ret, topics = decode_tags("first/third-person singular present "
                                  "subjunctive")
        self.assertEqual(ret, [("first-person", "present",
                                "singular", "subjunctive", "third-person")])

    def test_tags43(self):
        ret, topics = decode_tags("inflection of")
        self.assertEqual(ret, [("form-of",)])

    def test_tags44(self):
        ret, topics = decode_tags("third-person singular present indicative")
        self.assertEqual(ret, [("indicative", "present", "singular",
                                "third-person",)])

    def test_tags45(self):
        ret, topics = decode_tags("ordinal form of")
        self.assertEqual(ret, [("form-of", "ordinal")])

    def test_tags46(self):
        ret, topics = decode_tags("first-person singular (eu) present "
                                  "subjunctive")
        self.assertEqual(ret, [("first-person", "present", "singular",
                                "subjunctive", "with-eu")])

    def test_tags47(self):
        ret, topics = decode_tags("third-person singular (él, ella, also "
                                  "used with usted) present subjunctive "
                                  "form of")
        self.assertEqual(ret, [("form-of", "present", "singular", "subjunctive",
                                "third-person",
                                "with-ella", "with-usted", "with-él")])

    def test_tags48(self):
        ret, topics = decode_tags("instant messaging")
        self.assertEqual(ret, [("Internet",)])

    def test_tags49(self):
        ret, topics = decode_tags("plural and definite singular attributive")
        self.assertEqual(ret, [("attributive", "definite", "singular"),
                               ("attributive", "plural")])

    def test_tags50(self):
        ret, topics = decode_tags("alternative spelling of")
        self.assertEqual(ret, [("alt-of", "alternative")])

    def test_tags51(self):
        ret, topics = decode_tags("feminine")
        self.assertEqual(ret, [("feminine",)])

    def test_tags52(self):
        ret, topics = decode_tags("masculine")
        self.assertEqual(ret, [("masculine",)])

    def test_tags53(self):
        ret, topics = decode_tags("neuter")
        self.assertEqual(ret, [("neuter",)])

    def test_tags54(self):
        ret, topics = decode_tags("common")
        self.assertEqual(ret, [("common",)])

    def test_tags55(self):
        ret, topics = decode_tags("plural and definite singular attributive")
        self.assertEqual(ret, [("attributive", "definite", "singular"),
                               ("attributive", "plural",)])

    def test_tags56(self):
        ret, topics = decode_tags("comparative")
        self.assertEqual(ret, [("comparative",)])

    def test_tags57(self):
        ret, topics = decode_tags("superlative")
        self.assertEqual(ret, [("superlative",)])

    def test_tags58(self):
        ret, topics = decode_tags("superlative (predicative)")
        self.assertEqual(ret, [("predicative", "superlative")])

    def test_tags59(self):
        ret, topics = decode_tags("superlative (attributive)")
        self.assertEqual(ret, [("attributive", "superlative")])

    def test_tags60(self):
        ret, topics = decode_tags("indefinite superlative")
        self.assertEqual(ret, [("indefinite", "superlative")])

    def test_tags61(self):
        ret, topics = decode_tags("definite superlative")
        self.assertEqual(ret, [("definite", "superlative")])

    def test_tags62(self):
        ret, topics = decode_tags("definite singular and plural")
        self.assertEqual(ret, [("definite", "plural", "singular")])

    def test_tags63(self):
        ret, topics = decode_tags("first-person plural "
                                  "reflexive/dative/accusative form")
        self.assertEqual(ret, [("accusative", "dative", "first-person",
                                "plural", "reflexive")])

        self.assertEqual(topics, [])

    def test_tags64(self):
        # This has an ignored part
        ret, topics = decode_tags("archaic, supplanted by stato")
        self.assertEqual(ret, [("archaic",)])

    def test_tags65(self):
        ret, topics = decode_tags("archaic, totallyinvalidgarbage")
        self.assertEqual(ret, [("archaic", "error-unknown-tag")])

    def test_topics1(self):
        ret, topics = decode_tags("nautical")
        self.assertEqual(topics, ["nautical", "transport"])

    def test_topics2(self):
        ret, topics = decode_tags("ropemaking")
        self.assertEqual(topics, ["ropemaking", "crafts",
                                  "nautical", "transport",
                                  "arts", "hobbies", "lifestyle"])

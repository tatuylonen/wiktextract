# Tests for parse_alt_or_inflection_of()
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.form_descriptions import parse_alt_or_inflection_of

class FormOfTests(unittest.TestCase):

    def setUp(self):
        self.wxr = WiktextractContext(WiktionaryConfig(), Wtp()) 
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def test_non_of1(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "inalienable", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertIs(ret, None)

    def test_non_of2(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "inflection of", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, None)

    def test_non_of3(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "genitive", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, (["genitive"], None))

    def test_simple1(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "abbreviation of foo", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, (["abbreviation", "alt-of"], [{"word": "foo"}]))

    def test_simple2(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr,
                    "abbreviation of New York, a city in the United States",
                    set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, (["abbreviation", "alt-of"],
                               [{"word": "New York",
                                 "extra": "a city in the United States"}]))

    def test_simple3(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "inflection of foo", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, (["form-of"], [{"word": "foo"}]))

    def test_simple4(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "plural of instrumental",
                                         set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, (["form-of", "plural"],
                               [{"word": "instrumental"}]))

    def test_simple5(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "plural of corgi or corgy",
                                         set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, (["form-of", "plural"],
                               [{"word": "corgi"},
                                {"word": "corgy"}]))

    def test_simple6(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "plural of fish or chips",
                                         set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, (["form-of", "plural"],
                               [{"word": "fish or chips"}]))

    def test_simple7(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "abbreviation of OK.",
                                         set(["OK."]))
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, (["abbreviation", "alt-of"],
                               [{"word": "OK."}]))

    def test_simple8(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.wxr, "abbreviation of OK.",
                                         set(["OK"]))
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        print(ret)
        self.assertEqual(ret, (["abbreviation", "alt-of"],
                               [{"word": "OK"}]))

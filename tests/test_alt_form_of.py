# Tests for parse_alt_or_inflection_of()
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.form_descriptions import parse_alt_or_inflection_of

class HeadTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")
        self.ctx.start_section("English")

    def test_non_of1(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.ctx, "inalienable")
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertIs(ret, None)

    def test_non_of2(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.ctx, "inflection of")
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        print(ret)
        self.assertEqual(ret, None)

    def test_non_of3(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.ctx, "genitive")
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        print(ret)
        self.assertEqual(ret, (["genitive"], None))

    def test_simple1(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.ctx, "abbreviation of foo")
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(ret, (["abbreviation", "alt-of"], [{"word": "foo"}]))

    def test_simple2(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.ctx,
            "abbreviation of New York, a city in the United States")
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(ret, (["abbreviation", "alt-of"],
                               [{"word": "New York",
                                 "extra": "a city in the United States"}]))

    def test_simple3(self):
        data = {}
        ret = parse_alt_or_inflection_of(self.ctx, "inflection of foo")
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        print(ret)
        self.assertEqual(ret, (["form-of"], [{"word": "foo"}]))

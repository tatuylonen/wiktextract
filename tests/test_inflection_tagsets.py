# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.inflection import or_tagsets, and_tagsets

class TagsetTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 100000
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())

        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def xop(self, op, ts1, ts2, expected, lang="English", pos="verb"):
        assert callable(op)
        assert isinstance(ts1, list) and len(ts1) >= 1
        assert isinstance(ts2, list) and len(ts2) >= 1
        assert isinstance(expected, list) and len(ts2) >= 1
        assert all(isinstance(x, (list, tuple)) for x in ts1)
        assert all(isinstance(x, (list, tuple)) for x in ts2)
        assert all(isinstance(x, (list, tuple)) for x in expected)
        ts1 = list(tuple(sorted(x)) for x in ts1)
        ts2 = list(tuple(sorted(x)) for x in ts2)
        expected = list(tuple(sorted(x)) for x in expected)
        ret = op(lang, pos, ts1, ts2)
        print("ts1={} ts2={} ret={} expected={}"
              .format(ts1, ts2, ret, expected))
        self.assertEqual(ret, expected)

    def test_or1(self):
        self.xop(or_tagsets, [[]], [[]], [[]])

    def test_or2(self):
        self.xop(or_tagsets, [["masculine"]], [[]], [["masculine"]])

    def test_or3(self):
        self.xop(or_tagsets, [[]], [["masculine"]], [["masculine"]])

    def test_or4(self):
        self.xop(or_tagsets, [["masculine"]], [["masculine"]], [["masculine"]])

    def test_or5(self):
        self.xop(or_tagsets, [["masculine"]], [["singular"]],
                 [["masculine"], ["singular"]])

    def test_or6(self):
        self.xop(or_tagsets, [["masculine", "singular"]],
                 [["singular"]],
                 [["masculine", "singular"], ["singular"]])

    def test_or7(self):
        self.xop(or_tagsets, [["masculine", "singular"]],
                 [["singular", "feminine"]],
                 [["masculine", "feminine", "singular"]])

    def test_or8(self):
        self.xop(or_tagsets, [["masculine", "singular"]],
                 [["singular", "masculine"]],
                 [["masculine", "singular"]])

    def test_or8(self):
        self.xop(or_tagsets, [["masculine", "animate"]],
                 [["inanimate", "masculine"]],
                 [["masculine"]], lang="Russian")

    def test_or9(self):
        self.xop(or_tagsets, [["plural", "virile"]],
                 [["plural", "nonvirile"]],
                 [["plural"]], lang="Russian")

    def test_or10(self):
        self.xop(or_tagsets, [["virile"]], [["nonvirile"]],
                 [[]], lang="Russian")

    def test_or12(self):
        self.xop(or_tagsets, [["singular"]], [["plural"]],
                 [[]])

    def test_and1(self):
        self.xop(and_tagsets, [[]], [[]], [[]])

    def test_and2(self):
        self.xop(and_tagsets, [["singular"]], [[]], [["singular"]])

    def test_and3(self):
        self.xop(and_tagsets, [["singular"]], [["singular"]], [["singular"]])

    def test_and4(self):
        self.xop(and_tagsets, [["singular"]], [["third-person"]],
                 [["singular", "third-person"]])

    def test_and5(self):
        self.xop(and_tagsets, [["masculine", "feminine"], ["neuter", "plural"]],
                 [["nominative"]],
                 [["feminine", "masculine", "nominative"],
                  ["neuter", "nominative", "plural"]])

    def test_and6(self):
        self.xop(and_tagsets, [["singular", "plural"]], [["third-person"]],
                 [["third-person"]], lang="Finnish")

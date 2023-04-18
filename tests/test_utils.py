# Tests for datautils.py
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.datautils import *

class UtilsTests(unittest.TestCase):

    def setUp(self):
        self.wtpctx = Wtp()
        self.config = WiktionaryConfig()
        self.wtpctx.start_page("testpage")
        self.wtpctx.start_section("English")

    def test_slashes1(self):
        ret = split_slashes(self.wtpctx, "foo ")
        self.assertEqual(ret, ["foo"])

    def test_slashes2(self):
        ret = split_slashes(self.wtpctx, "foo bar /  zap")
        self.assertEqual(ret, ["foo bar", "zap"])

    def test_slashes3(self):
        ret = split_slashes(self.wtpctx, "foo/bar/zap ")
        self.assertEqual(ret, ["foo", "bar", "zap"])

    def test_slashes4(self):
        ret = split_slashes(self.wtpctx, "foo bar/zap ")
        self.assertEqual(ret, ["foo bar", "foo zap"])

    def test_slashes5(self):
        ret = split_slashes(self.wtpctx, "foo bar/zap ")
        self.assertEqual(ret, ["foo bar", "foo zap"])

    def test_slashes6(self):
        ret = split_slashes(self.wtpctx, "foo/bar zap a/b")
        print("ret:", ret)
        self.assertEqual(ret, ["bar zap a", "bar zap b",
                               "foo zap a", "foo zap b"])

    def test_slashes7(self):
        self.wtpctx.add_page("wikitext", "foo", "x")
        assert self.wtpctx.page_exists("foo")
        ret = split_slashes(self.wtpctx, "foo/bar zap a/b")
        print("ret:", ret)
        # XXX this response is still perhaps not what we want with the page
        # existing
        self.assertEqual(ret, ["bar zap a", "bar zap b",
                               "foo zap a", "foo zap b"])

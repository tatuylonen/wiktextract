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
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")
        self.ctx.start_section("English")

    def test_slashes1(self):
        ret = split_slashes(self.ctx, "foo ")
        self.assertEqual(ret, ["foo"])

    def test_slashes2(self):
        ret = split_slashes(self.ctx, "foo bar /  zap")
        self.assertEqual(ret, ["foo bar", "zap"])

    def test_slashes3(self):
        ret = split_slashes(self.ctx, "foo/bar/zap ")
        self.assertEqual(ret, ["foo", "bar", "zap"])

    def test_slashes4(self):
        ret = split_slashes(self.ctx, "foo bar/zap ")
        self.assertEqual(ret, ["foo bar", "foo zap"])

    def test_slashes5(self):
        ret = split_slashes(self.ctx, "foo bar/zap ")
        self.assertEqual(ret, ["foo bar", "foo zap"])

    def test_slashes6(self):
        ret = split_slashes(self.ctx, "foo/bar zap a/b")
        print("ret:", ret)
        self.assertEqual(ret, ["bar zap a", "bar zap b",
                               "foo zap a", "foo zap b"])

    def test_slashes7(self):
        self.ctx.add_page("foo", 0, "x")
        assert self.ctx.page_exists("foo")
        ret = split_slashes(self.ctx, "foo/bar zap a/b")
        print("ret:", ret)
        # XXX this response is still perhaps not what we want with the page
        # existing
        self.assertEqual(ret, ["bar zap a", "bar zap b",
                               "foo zap a", "foo zap b"])

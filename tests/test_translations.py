# Tests for parse_translation_desc()
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.form_descriptions import parse_translation_desc

class TrTests(unittest.TestCase):

    def setUp(self):
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("abolitionism")  # Note: some tests use last char
        self.ctx.start_section("English")

    def test_tr1(self):
        tr = {}
        # Note: this test uses last char of title
        parse_translation_desc(self.ctx, "French", "abolitionnisme m", tr)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(tr, {"word": "abolitionnisme",
                              "tags": ["masculine"]})

    def test_tr2(self):
        tr = {}
        parse_translation_desc(self.ctx, "French", "abolitionnisme f", tr)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(tr, {"word": "abolitionnisme",
                              "tags": ["feminine"]})

    def test_tr3(self):
        tr = {}
        # m is in page title, should not interpret as tag
        self.ctx.start_page("m m m")
        parse_translation_desc(self.ctx, "French", "m m m", tr)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(tr, {"word": "m m m"})

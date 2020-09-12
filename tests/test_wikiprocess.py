# Tests for processing WikiText templates and macros
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
from wiktextract.wikiprocess import ExpandCtx, phase1_to_ctx, expand_wikitext

class WikiProcTests(unittest.TestCase):

    def test_basic(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some text", None)
        self.assertEqual(ret, "Some text")

    def test_basic2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some [[link]] x", None)
        self.assertEqual(ret, "Some [[link]] x")

    def test_basic3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some {{{unknown_arg}}} x", None)
        self.assertEqual(ret, "Some {{{unknown_arg}}} x")

    def test_basic4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some {{unknown template}} x", None)
        self.assertEqual(ret, "Some {{unknown template}} x")

    def test_basic5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "Some {{unknown template|arg1||arg3}}", None)
        self.assertEqual(ret, "Some {{unknown template|arg1||arg3}}")

    def test_if1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#if:|T|F}}", None)
        self.assertEqual(ret, "F")

    def test_if2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#if:x|T|F}}", None)
        self.assertEqual(ret, "T")

    def test_if3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#if:|T}}b", None)
        self.assertEqual(ret, "ab")

    def test_if4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#if:x|T}}b", None)
        self.assertEqual(ret, "aTb")

    def test_ifeq1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq:a|b|T|F}}", None)
        self.assertEqual(ret, "F")

    def test_ifeq2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq:a|a|T|F}}", None)
        self.assertEqual(ret, "T")

    def test_ifeq3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq: a |a|T|F}}", None)
        self.assertEqual(ret, "T")

    def test_ifeq4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq: ||T|F}}", None)
        self.assertEqual(ret, "T")

    def test_ifeq5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#ifeq:a||T}}b", None)
        self.assertEqual(ret, "ab")

    def test_ifexists1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifexist:Nonexxxx|T|F}}", None)
        self.assertEqual(ret, "F")

    def test_ifexists2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifexist:Nonexxxx|T}}", None)
        self.assertEqual(ret, "")

    # XXX test #ifexists with a page that exists

    def test_switch1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:a|a=one|b=two|three}}", None)
        self.assertEqual(ret, "one")

    def test_switch2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:b|a=one|b=two|three}}", None)
        self.assertEqual(ret, "two")

    def test_switch3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:c|a=one|b=two|three}}", None)
        self.assertEqual(ret, "three")

    def test_switch4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:|a=one|b=two|three}}", None)
        self.assertEqual(ret, "three")

    def test_switch5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:|a=one|#default=three|b=two}}", None)
        self.assertEqual(ret, "three")

    def test_switch6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:b|a=one|#default=three|b=two}}", None)
        self.assertEqual(ret, "two")

    def test_switch7(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:c|a=one|c|d=four|b=two}}", None)
        self.assertEqual(ret, "four")

    def test_switch8(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:d|a=one|c|d=four|b=two}}", None)
        self.assertEqual(ret, "four")

    def test_switch9(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:b|a=one|c|d=four|b=two}}", None)
        self.assertEqual(ret, "two")

    def test_switch10(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:e|a=one|c|d=four|b=two}}", None)
        self.assertEqual(ret, "")

    def test_switch11(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch: d |\na\n=\none\n|\nc\n|"
                              "\nd\n=\nfour\n|\nb\n=\ntwo\n}}", None)
        self.assertEqual(ret, "four")

    # XXX test that both sides of switch are evaluated

    def test_tag1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#tag:br}}", None)
        self.assertEqual(ret, "<br />")

    def test_tag2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#tag:div|foo bar}}", None)
        self.assertEqual(ret, "<div>foo bar</div>")

    def test_tag3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              """{{#tag:div|foo bar|class=foo|id=me}}""",
                              None)
        self.assertEqual(ret, """<div class="foo" id="me">foo bar</div>""")

    def test_tag4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              """{{#tag:div|foo bar|class=foo|text=m"e'a}}""",
                              None)
        self.assertEqual(ret,
                         """<div class="foo" text="m&quot;e&#x27;a">"""
                         """foo bar</div>""")

    def test_tag5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#tag:div|foo bar<dangerous>z}}", None)
        self.assertEqual(ret, "<div>foo bar&lt;dangerous&gt;z</div>")

    def test_fullpagename1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{FULLPAGENAME}}", None)
        self.assertEqual(ret, "Tt")

    def test_fullpagename2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{FULLPAGENAME}}", None)
        self.assertEqual(ret, "Help:Tt/doc")

    def test_pagename1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{PAGENAME}}", None)
        self.assertEqual(ret, "Tt")

    def test_pagename2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{PAGENAME}}", None)
        self.assertEqual(ret, "Tt/doc")

    def test_namespace1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{NAMESPACE}}", None)
        self.assertEqual(ret, "Help")

    def test_namespace2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt/doc", "{{NAMESPACE}}", None)
        self.assertEqual(ret, "")

    def test_uc(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{uc:foo}}", None)
        self.assertEqual(ret, "FOO")

    def test_lc(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{lc:FOO}}", None)
        self.assertEqual(ret, "foo")

    def test_lcfirst(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{lcfirst:FOO}}", None)
        self.assertEqual(ret, "fOO")

    def test_ucfirst(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{ucfirst:foo}}", None)
        self.assertEqual(ret, "Foo")

    def test_dateformat1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|ymd}}", None)
        self.assertEqual(ret, "2009 Dec 25")

    def test_dateformat2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|mdy}}", None)
        self.assertEqual(ret, "Dec 25, 2009")

    def test_dateformat3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|ISO 8601}}", None)
        self.assertEqual(ret, "2009-12-25")

    def test_dateformat4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009}}", None)
        self.assertEqual(ret, "2009-12-25")

    def test_dateformat5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|dmy}}", None)
        self.assertEqual(ret, "25 Dec 2009")

    def test_dateformat6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:2011-11-09|dmy}}", None)
        self.assertEqual(ret, "09 Nov 2011")

    def test_dateformat7(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:2011 Nov 9|dmy}}", None)
        self.assertEqual(ret, "09 Nov 2011")

    def test_dateformat8(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:2011 NovEmber 9|dmy}}", None)
        self.assertEqual(ret, "09 Nov 2011")

    def test_dateformat9(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 December|mdy}}", None)
        self.assertEqual(ret, "Dec 25")

    def test_dateformat10(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 December|dmy}}", None)
        self.assertEqual(ret, "25 Dec")

    def test_urlencode1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z k}}", None)
        self.assertEqual(ret, "x%3Ay%2Fz+k")

    def test_urlencode2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z kä|QUERY}}", None)
        self.assertEqual(ret, "x%3Ay%2Fz+k%C3%A4")

    def test_urlencode3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z kä|WIKI}}", None)
        self.assertEqual(ret, "x:y/z_k%C3%A4")

    def test_urlencode4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z kä|PATH}}", None)
        self.assertEqual(ret, "x%3Ay%2Fz%20k%C3%A4")

    # XXX next: anchorencode

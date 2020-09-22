# Tests for processing WikiText templates and macros
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import math
import unittest
from wiktextract.wikiprocess import ExpandCtx, phase1_to_ctx, expand_wikitext

class WikiProcTests(unittest.TestCase):

    def test_basic(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some text")
        self.assertEqual(ret, "Some text")

    def test_basic2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some [[link]] x")
        self.assertEqual(ret, "Some [[link]] x")

    def test_basic3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some {{{unknown_arg}}} x")
        self.assertEqual(ret, "Some {{{unknown_arg}}} x")

    def test_basic4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "Some {{unknown template}} x")
        self.assertEqual(ret, "Some {{unknown template}} x")

    def test_basic5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "Some {{unknown template|arg1||arg3}}")
        self.assertEqual(ret, "Some {{unknown template|arg1||arg3}}")

    def test_if1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#if:|T|F}}")
        self.assertEqual(ret, "F")

    def test_if2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#if:x|T|F}}")
        self.assertEqual(ret, "T")

    def test_if3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#if:|T}}b")
        self.assertEqual(ret, "ab")

    def test_if4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#if:x|T}}b")
        self.assertEqual(ret, "aTb")

    def test_ifeq1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq:a|b|T|F}}")
        self.assertEqual(ret, "F")

    def test_ifeq2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq:a|a|T|F}}")
        self.assertEqual(ret, "T")

    def test_ifeq3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq: a |a|T|F}}")
        self.assertEqual(ret, "T")

    def test_ifeq4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifeq: ||T|F}}")
        self.assertEqual(ret, "T")

    def test_ifeq5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#ifeq:a||T}}b")
        self.assertEqual(ret, "ab")

    def test_ifexpr1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#ifexpr:1+3>2|T|F}}b")
        self.assertEqual(ret, "aTb")

    def test_ifexpr2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "a{{#ifexpr:1-4>sin(pi/2)|T|F}}b")
        self.assertEqual(ret, "aFb")

    def test_ifexists1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifexist:Nonexxxx|T|F}}")
        self.assertEqual(ret, "F")

    def test_ifexists2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#ifexist:Nonexxxx|T}}")
        self.assertEqual(ret, "")

    # XXX test #ifexists with a page that exists

    def test_switch1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:a|a=one|b=two|three}}")
        self.assertEqual(ret, "one")

    def test_switch2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:b|a=one|b=two|three}}")
        self.assertEqual(ret, "two")

    def test_switch3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:c|a=one|b=two|three}}")
        self.assertEqual(ret, "three")

    def test_switch4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:|a=one|b=two|three}}")
        self.assertEqual(ret, "three")

    def test_switch5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:|a=one|#default=three|b=two}}")
        self.assertEqual(ret, "three")

    def test_switch6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:b|a=one|#default=three|b=two}}")
        self.assertEqual(ret, "two")

    def test_switch7(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:c|a=one|c|d=four|b=two}}")
        self.assertEqual(ret, "four")

    def test_switch8(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:d|a=one|c|d=four|b=two}}")
        self.assertEqual(ret, "four")

    def test_switch9(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:b|a=one|c|d=four|b=two}}")
        self.assertEqual(ret, "two")

    def test_switch10(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch:e|a=one|c|d=four|b=two}}")
        self.assertEqual(ret, "")

    def test_switch11(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#switch: d |\na\n=\none\n|\nc\n|"
                              "\nd\n=\nfour\n|\nb\n=\ntwo\n}}")
        self.assertEqual(ret, "four")

    # XXX test that both sides of switch are evaluated

    def test_tag1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#tag:br}}")
        self.assertEqual(ret, "<br />")

    def test_tag2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#tag:div|foo bar}}")
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
                              "{{#tag:div|foo bar<dangerous>z}}")
        self.assertEqual(ret, "<div>foo bar&lt;dangerous&gt;z</div>")

    def test_fullpagename1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{FULLPAGENAME}}")
        self.assertEqual(ret, "Tt")

    def test_fullpagename2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{FULLPAGENAME}}")
        self.assertEqual(ret, "Help:Tt/doc")

    def test_fullpagename3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc",
                              "{{FULLPAGENAME:Template:Mark/doc}}")
        self.assertEqual(ret, "Template:Mark/doc")

    def test_pagename1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{PAGENAME}}")
        self.assertEqual(ret, "Tt")

    def test_pagename2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{PAGENAME}}")
        self.assertEqual(ret, "Tt/doc")

    def test_pagename3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc",
                              "{{PAGENAME:Template:Mark/doc}}")
        self.assertEqual(ret, "Mark/doc")

    def test_subpagename1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc/subdoc",
                              "{{SUBPAGENAME}}")
        self.assertEqual(ret, "subdoc")

    def test_subpagename2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc/subdoc",
                              "{{SUBPAGENAME:Template:test/subtest}}")
        self.assertEqual(ret, "subtest")

    def test_subpagename3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt",
                              "{{SUBPAGENAME}}")
        self.assertEqual(ret, "Tt")

    def test_subpagename4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt",
                              "{{SUBPAGENAME:Foo/bar}}")
        self.assertEqual(ret, "bar")

    def test_subpagename5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc",
                              "{{SUBPAGENAME}}")
        self.assertEqual(ret, "doc")

    def test_subpagename6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt",
                              "{{SUBPAGENAME:Help:TestPage}}")
        self.assertEqual(ret, "TestPage")

    def test_namespace1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{NAMESPACE}}")
        self.assertEqual(ret, "Help")

    def test_namespace2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt/doc", "{{NAMESPACE}}")
        self.assertEqual(ret, "")

    def test_namespace3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc",
                              "{{NAMESPACE:Template:Kk}}")
        self.assertEqual(ret, "Template")

    def test_uc(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{uc:foo}}")
        self.assertEqual(ret, "FOO")

    def test_lc(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{lc:FOO}}")
        self.assertEqual(ret, "foo")

    def test_lcfirst(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{lcfirst:FOO}}")
        self.assertEqual(ret, "fOO")

    def test_ucfirst(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{ucfirst:foo}}")
        self.assertEqual(ret, "Foo")

    def test_dateformat1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|ymd}}")
        self.assertEqual(ret, "2009 Dec 25")

    def test_dateformat2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|mdy}}")
        self.assertEqual(ret, "Dec 25, 2009")

    def test_dateformat3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|ISO 8601}}")
        self.assertEqual(ret, "2009-12-25")

    def test_dateformat4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009}}")
        self.assertEqual(ret, "2009-12-25")

    def test_dateformat5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 dec 2009|dmy}}")
        self.assertEqual(ret, "25 Dec 2009")

    def test_dateformat6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:2011-11-09|dmy}}")
        self.assertEqual(ret, "09 Nov 2011")

    def test_dateformat7(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:2011 Nov 9|dmy}}")
        self.assertEqual(ret, "09 Nov 2011")

    def test_dateformat8(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:2011 NovEmber 9|dmy}}")
        self.assertEqual(ret, "09 Nov 2011")

    def test_dateformat9(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 December|mdy}}")
        self.assertEqual(ret, "Dec 25")

    def test_dateformat10(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#dateformat:25 December|dmy}}")
        self.assertEqual(ret, "25 Dec")

    def test_fullurl1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{fullurl:Test page|action=edit}}")
        self.assertEqual(ret, "//dummy.host/index.php?"
                         "title=Test+page&action=edit")

    # XXX implement and test interwiki prefixes for fullurl

    def test_urlencode1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z k}}")
        self.assertEqual(ret, "x%3Ay%2Fz+k")

    def test_urlencode2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z kä|QUERY}}")
        self.assertEqual(ret, "x%3Ay%2Fz+k%C3%A4")

    def test_urlencode3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z kä|WIKI}}")
        self.assertEqual(ret, "x:y/z_k%C3%A4")

    def test_urlencode4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{urlencode:x:y/z kä|PATH}}")
        self.assertEqual(ret, "x%3Ay%2Fz%20k%C3%A4")

    def test_achorencode1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{anchorencode:x:y/z kä}}")
        self.assertEqual(ret, "x:y/z_kä")

    def test_ns1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{ns:6}}")
        self.assertEqual(ret, "File")

    def test_ns2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{ns:File}}")
        self.assertEqual(ret, "File")

    def test_ns3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{ns:Image}}")
        self.assertEqual(ret, "File")

    def test_ns4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{ns:Nonexistentns}}")
        self.assertEqual(ret, "")

    def test_titleparts1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:foo}}")
        self.assertEqual(ret, "foo")

    def test_titleparts2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:foo/bar/baz}}")
        self.assertEqual(ret, "foo/bar/baz")

    def test_titleparts3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:Help:foo/bar/baz}}")
        self.assertEqual(ret, "Help:foo/bar/baz")

    def test_titleparts4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:foo|1|-1}}")
        self.assertEqual(ret, "foo")

    def test_titleparts5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:foo/bar/baz|1|-2}}")
        self.assertEqual(ret, "bar")

    def test_titleparts6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:Help:foo/bar/baz|2|1}}")
        self.assertEqual(ret, "foo/bar")

    def test_titleparts7(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:Help:foo/bar/baz||-2}}")
        self.assertEqual(ret, "bar/baz")

    def test_titleparts8(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#titleparts:Help:foo/bar/baz|2}}")
        self.assertEqual(ret, "Help:foo")

    def test_expr1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr}}")
        self.assertEqual(ret, "Expression error near <end>")

    def test_expr2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|1 + 2.34}}")
        self.assertEqual(ret, "3.34")

    def test_expr3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|1 + 2.34}}")
        self.assertEqual(ret, "3.34")

    def test_expr4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|-12}}")
        self.assertEqual(ret, "-12")

    def test_expr5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|-trunc12}}")
        self.assertEqual(ret, "-12")

    def test_expr6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|-trunc(-2^63)}}")
        self.assertEqual(ret, "9223372036854775808")

    def test_expr7(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|-trunc(-2^63)}}")
        self.assertEqual(ret, "9223372036854775808")

    def test_expr8(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|2e3}}")
        self.assertEqual(ret, "2000")

    def test_expr9(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|-2.3e-4}}")
        self.assertEqual(ret, "-0.00022999999999999998")

    def test_expr10(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|(trunc2)e(trunc-3)}}")
        self.assertEqual(ret, "0.002")

    def test_expr11(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|(trunc2)e(trunc0)}}")
        self.assertEqual(ret, "2")

    def test_expr12(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|(trunc2)e(trunc18)}}")
        self.assertEqual(ret, "2000000000000000000")

    def test_expr13(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|6e(5-2)e-2}}")
        self.assertEqual(ret, "60")

    def test_expr14(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|1e.5}}")
        self.assertEqual(ret, "3.1622776601683795")

    def test_expr15(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|exp43}}")
        self.assertEqual(ret, "4727839468229346304")

    def test_expr16(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|exp trunc0}}")
        self.assertEqual(ret, "1")

    def test_expr17(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|ln2}}")
        self.assertEqual(ret, "0.6931471805599453")

    def test_expr18(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|ln trunc1}}")
        self.assertEqual(ret, "0")

    def test_expr19(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|ln.5e-323}}")
        self.assertEqual(ret, "-744.4400719213812")

    def test_expr20(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|abs-2}}")
        self.assertEqual(ret, "2")

    def test_expr21(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|sqrt 4}}")
        self.assertEqual(ret, "2")

    def test_expr22(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|trunc1.2}}")
        self.assertEqual(ret, "1")

    def test_expr23(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|trunc-1.2}}")
        self.assertEqual(ret, "-1")

    def test_expr24(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|floor1.2}}")
        self.assertEqual(ret, "1")

    def test_expr25(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|floor-1.2}}")
        self.assertEqual(ret, "-2")

    def test_expr26(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|ceil1.2}}")
        self.assertEqual(ret, "2")

    def test_expr27(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|ceil-1.2}}")
        self.assertEqual(ret, "-1")

    def test_expr28(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|sin(30*pi/180)}}")
        self.assertEqual(ret, "0.49999999999999994")

    def test_expr29(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|cos.1}}")
        self.assertEqual(ret, "0.9950041652780258")

    def test_expr30(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|tan.1}}")
        self.assertEqual(ret, "0.10033467208545055")

    def test_expr31(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|asin.1}}")
        self.assertEqual(ret, "0.1001674211615598")

    def test_expr32(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|acos.1}}")
        self.assertEqual(ret, "1.4706289056333368")

    def test_expr33(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|atan.1}}")
        self.assertEqual(ret, "0.09966865249116204")

    def test_expr34(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|not0}}")
        self.assertEqual(ret, "1")

    def test_expr35(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|not1}}")
        self.assertEqual(ret, "0")

    def test_expr36(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|not trunc2.1}}")
        self.assertEqual(ret, "0")

    def test_expr37(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|2^3}}")
        self.assertEqual(ret, "8")

    def test_expr38(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|2^-3}}")
        self.assertEqual(ret, "0.125")

    def test_expr39(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|2*3}}")
        self.assertEqual(ret, "6")

    def test_expr40(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|(trunc2)*3}}")
        self.assertEqual(ret, "6")

    def test_expr41(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|1 + 2 * 3}}")
        self.assertEqual(ret, "7")

    def test_expr42(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|4/2}}")
        self.assertEqual(ret, "2")

    def test_expr43(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|5 div 2}}")
        self.assertEqual(ret, "2.5")

    def test_expr44(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|5 mod 2}}")
        self.assertEqual(ret, "1")

    def test_expr45(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|5+2}}")
        self.assertEqual(ret, "7")

    def test_expr46(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|5.1--2.7}}")
        self.assertEqual(ret, "7.8")

    def test_expr47(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|9.876round2}}")
        self.assertEqual(ret, "9.88")

    def test_expr48(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|trunc1234round trunc-2}}")
        self.assertEqual(ret, "1200")

    def test_expr49(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.0=3}}")
        self.assertEqual(ret, "1")

    def test_expr50(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.1=3.0}}")
        self.assertEqual(ret, "0")

    def test_expr51(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.0<>3.0}}")
        self.assertEqual(ret, "0")

    def test_expr52(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.1!=3.0}}")
        self.assertEqual(ret, "1")

    def test_expr53(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.0<3.1}}")
        self.assertEqual(ret, "1")

    def test_expr54(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.0<3.0}}")
        self.assertEqual(ret, "0")

    def test_expr55(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.1>3.0}}")
        self.assertEqual(ret, "1")

    def test_expr56(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.1>3.1}}")
        self.assertEqual(ret, "0")

    def test_expr57(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.1>=3.0}}")
        self.assertEqual(ret, "1")

    def test_expr58(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.1>=3.1}}")
        self.assertEqual(ret, "1")

    def test_expr59(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.0<=3.1}}")
        self.assertEqual(ret, "1")

    def test_expr60(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.0<=3.0}}")
        self.assertEqual(ret, "1")

    def test_expr61(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|3.1<=3.0}}")
        self.assertEqual(ret, "0")

    def test_expr62(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|e}}")
        self.assertEqual(ret, str(math.e))

    def test_expr63(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|pi}}")
        self.assertEqual(ret, str(math.pi))

    def test_expr64(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#expr|+trunc1.1}}")
        self.assertEqual(ret, "1")

    def test_padleft1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padleft:xyz|5}}")
        self.assertEqual(ret, "00xyz")

    def test_padleft2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padleft:xyz|5|_}}")
        self.assertEqual(ret, "__xyz")

    def test_padleft3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padleft:xyz|5|abc}}")
        self.assertEqual(ret, "abxyz")

    def test_padleft4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padleft:xyz|2}}")
        self.assertEqual(ret, "xyz")

    def test_padleft5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padleft:|1|xyz}}")
        self.assertEqual(ret, "x")

    def test_padright1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padright:xyz|5}}")
        self.assertEqual(ret, "xyz00")

    def test_padright2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padright:xyz|5|_}}")
        self.assertEqual(ret, "xyz__")

    def test_padright3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padright:xyz|5|abc}}")
        self.assertEqual(ret, "xyzab")

    def test_padright4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padright:xyz|2}}")
        self.assertEqual(ret, "xyz")

    def test_padright5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{padright:|1|xyz}}")
        self.assertEqual(ret, "x")

    def test_len1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#len: xyz }}")
        self.assertEqual(ret, "3")

    # XXX we currently don't implement <nowiki> ... </nowiki> handling
    # in #len, #pos etc according to spec.  See:
    # https://www.mediawiki.org/wiki/Extension:StringFunctions

    def test_pos1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pos: xyzayz |yz}}")
        self.assertEqual(ret, "1")

    def test_pos2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pos: xyzayz |zz}}")
        self.assertEqual(ret, "")

    def test_pos3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pos: xyz ayz }}")
        self.assertEqual(ret, "3")

    def test_rpos1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#rpos: xyzayz |yz}}")
        self.assertEqual(ret, "4")

    def test_rpos2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#rpos: xyzayz |zz}}")
        self.assertEqual(ret, "-1")

    def test_rpos3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#rpos: xy za yz }}")
        self.assertEqual(ret, "5")

    def test_sub1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub: xyzayz |3}}")
        self.assertEqual(ret, "ayz")

    def test_sub2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|3}}")
        self.assertEqual(ret, "cream")

    def test_sub3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|0|3}}")
        self.assertEqual(ret, "Ice")

    def test_sub4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|-3}}")
        self.assertEqual(ret, "eam")

    def test_sub5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|3|3}}")
        self.assertEqual(ret, "cre")

    def test_sub6(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|3|-3}}")
        self.assertEqual(ret, "cr")

    def test_sub7(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|-3|2}}")
        self.assertEqual(ret, "ea")

    def test_sub8(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|3|0}}")
        self.assertEqual(ret, "cream")

    def test_sub9(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub:Icecream|3|-6}}")
        self.assertEqual(ret, "")

    def test_pad1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pad:Ice|10|xX}}")
        self.assertEqual(ret, "xXxXxXxIce")

    def test_pad2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pad:Ice|5|x|left}}")
        self.assertEqual(ret, "xxIce")

    def test_pad3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pad:Ice|5|x|right}}")
        self.assertEqual(ret, "Icexx")

    def test_pad4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pad:Ice|5|x|center}}")
        self.assertEqual(ret, "xIcex")

    def test_pad5(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pad:Ice|5|x}}")
        self.assertEqual(ret, "xxIce")

    def test_replace1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#replace:Icecream|e|E}}")
        self.assertEqual(ret, "IcEcrEam")

    def test_replace2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#replace:Icecream|e|}}")
        self.assertEqual(ret, "Iccram")

    def test_replace3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#replace:Icecream|ea|EAEA}}")
        self.assertEqual(ret, "IcecrEAEAm")

    def test_explode1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#explode:And if you tolerate this| |2}}")
        self.assertEqual(ret, "you")

    def test_explode2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#explode:String/Functions/Code|/|-1}}")
        self.assertEqual(ret, "Code")

    def test_explode3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#explode:Split%By%Percentage%Signs|%|2}}",
                              None)
        self.assertEqual(ret, "Percentage")

    def test_explode4(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#explode:And if you tolerate this thing| "
                              "|2|3}}",
                              None)
        self.assertEqual(ret, "you tolerate this thing")

    def test_f_urlencode1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#urlencode:x:y/z kä}}")
        self.assertEqual(ret, "x%3Ay%2Fz+k%C3%A4")

    def test_f_urldecode1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt",
                              "{{#urldecode:x%3Ay%2Fz+k%C3%A4}}")
        self.assertEqual(ret, "x:y/z kä")

    def test_template1(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test content"]])
        ret = expand_wikitext(ctx, "Tt", "a{{testmod}}b")
        self.assertEqual(ret, "atest contentb")

    def test_template2(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", " test content "]])
        ret = expand_wikitext(ctx, "Tt", "a{{testmod}}b")
        self.assertEqual(ret, "a test content b")

    def test_template3(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "* test content\n"]])
        ret = expand_wikitext(ctx, "Tt", "a{{testmod}}b")
        self.assertEqual(ret, "a\n* test content\nb")

    def test_template4(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{1}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod}}")
        self.assertEqual(ret, "test {{{1}}} content")

    def test_template5(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{1}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|foo}}")
        self.assertEqual(ret, "test foo content")

    def test_template6(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{1}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|}}")
        self.assertEqual(ret, "test  content")

    def test_template7(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{1|}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod}}")
        self.assertEqual(ret, "test  content")

    def test_template8(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{1|def}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod}}")
        self.assertEqual(ret, "test def content")

    def test_template9(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{1|def}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|foo}}")
        self.assertEqual(ret, "test foo content")

    def test_template10(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{{{{1}}}}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|2|foo|bar}}")
        self.assertEqual(ret, "test foo content")

    def test_template11(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{{{{1}}}}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|3|foo|bar}}")
        self.assertEqual(ret, "test bar content")

    def test_template12(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{foo|{{{1}}}}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod}}")
        self.assertEqual(ret, "test {{{1}}} content")

    def test_template13(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{foo|{{{1}}}}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|foo=zap}}")
        self.assertEqual(ret, "test zap content")

    def test_template14(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{foo|{{{1}}}}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|Zap}}")
        self.assertEqual(ret, "test Zap content")

    def test_template15(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "test {{{foo|{{{1}}}}}} content"]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|bar=kak|Zap}}")
        self.assertEqual(ret, "test Zap content")

    def test_template16(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod",
             "{{#if:{{{1}}}|{{#sub:{{{1}}}|0|1}}"
             "{{testmod|{{#sub:{{{1}}}|1}}}}"
             "{{testmod|{{#sub:{{{1}}}|1}}}}"
             "x|}}"
            ]])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|abc}}")
        self.assertEqual(ret, "abcxcxxbcxcxxx")

    def test_template17(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{testmod2|{{{1}}}}}b"],
            ["Template", "testmod2", "x{{{1}}}y"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|zz}}")
        self.assertEqual(ret, "axzzyb")

    def test_template18(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{testmod2|{{{1}}}}}b"],
            ["Template", "testmod2", "{{#if:{{{1}}}|x|y}}"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|zz}}")
        self.assertEqual(ret, "axb")

    def test_template19(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{testmod2|{{{1}}}}}b"],
            ["Template", "testmod2", "{{#if:{{{1}}}|x|y}}"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|}}")
        self.assertEqual(ret, "ayb")

    def test_template20(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{testmod2|{{{1}}}}}b"],
            ["Template", "testmod2", "{{#if:{{{1}}}|x|y}}"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod}}")
        self.assertEqual(ret, "axb")  # condition expands to {{{1}}}

    def test_template21(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{testmod2|{{{1}}}}}b"],
            ["Template", "testmod2", "c{{testmod3|{{{1}}}}}d"],
            ["Template", "testmod3", "f{{{1}}}g"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod}}")
        self.assertEqual(ret, "acf{{{1}}}gdb")

    def test_template22(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{testmod2|{{{1}}}}}b"],
            ["Template", "testmod2", "c{{testmod3|{{{1}}}}}d"],
            ["Template", "testmod3", "f{{{1}}}g"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|}}")
        self.assertEqual(ret, "acfgdb")

    def test_template23(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{testmod2|{{{1}}}}}b"],
            ["Template", "testmod2", "c{{testmod3|{{{1}}}}}d"],
            ["Template", "testmod3", "f{{{1}}}g"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|zz}}")
        self.assertEqual(ret, "acfzzgdb")

    def test_template24(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{{1}}}b"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{testmod|{{!}}}}")
        self.assertEqual(ret, "a&vert;b")

    def test_template25(self):
        ctx = phase1_to_ctx([
            ["Template", "testmod", "a{{{1}}}b"],
        ])
        # This example is from
        # https://www.mediawiki.org/wiki/Extension:Scribunto/Lua_reference_manual#frame:getTitle,
        # under frame:expandTemplate examples
        ret = expand_wikitext(ctx, "Tt", "{{testmod|{{((}}!{{))}}}}")
        self.assertEqual(ret, "a&lbrace;&lbrace;!&rbrace;&rbrace;b")

    def test_template26(self):
        ctx = phase1_to_ctx([
            ["Template", "foo", 'a{{{1}}}b'],
        ])
        # This tests that the "=" is not interpretated as indicating argument
        # name on the left.
        ret = expand_wikitext(ctx, "Tt", '{{foo|<span class="foo">bar</span>}}')
        self.assertEqual(ret, 'a<span class="foo">bar</span>b')

    # def test_templateXXX(self):
    #     ctx = phase1_to_ctx([
    #         ["#redirect", "Template:rel3", "Template:col3"],
    #         ["Template", "col3", "{{check|lang={{{lang|}}}|"
    #          "{{#invoke:columns|display|sort=1|collapse=1|columns=3}}}}"],
    #         ["Template", "check",
    #          "{{deprecated code|active={{#if:{{{lang|}}}|yes|no}}|"
    #          "text=deprecated use of {{para|lang}} parameter|"
    #          "tooltip=deprecated 'lang'|{{{1}}}}}"],
    #         ["Template", "deprecated code",
    #          """{{#ifeq:{{{active|}}}|no|{{{1}}}|"""
    #          """<div class="deprecated" title="{{#if:{{{tooltip|}}}|"""
    #          """{{{tooltip}}}|This is a deprecated template usage.}}">''"""
    #          """([[:Category:Successfully deprecated templates|"""
    #          """{{#if:{{{text|}}}|{{{text}}}|deprecated template usage}}]])''"""
    #          """{{{1}}}</div>"""
    #          """{{categorize|und|Pages using deprecated templates}}}}"""],
    #         ["Template", "para",
    #          """<code>&#124;{{#if:{{{}}}|{{#if:{{{1|}}}|{{{1}}}=}}{{{2|}}}|="""
    #          """{{{1|}}}}}</code>{{#if:{{{3|}}}|&nbsp;({{#if:{{{req|}}}|"""
    #          """'''''required''''',&nbsp;}}"""
    #          """{{#if:{{{opt|}}}|''optional'',&nbsp;}}{{{3}}})|"""
    #          """{{#if:{{{req|}}}|&nbsp;('''''required''''')}}"""
    #          """{{#if:{{{opt|}}}|&nbsp;(''optional'')}}}}"""],
    #         ["Template", "categorize",
    #          """{{#invoke:utilities|template_categorize}}"""],
    #     ])
    #     ret = expand_wikitext(ctx, "Tt", "{{rel3|es|animálculo|animalidad}}")
    #     self.assertEqual(ret, "XXX")

    def test_redirect1(self):
        ctx = phase1_to_ctx([
            ["#redirect", "Template:oldtemp", "Template:testtemp"],
            ["Template", "testtemp", "a{{{1}}}b"],
        ])
        ret = expand_wikitext(ctx, "Tt", "{{oldtemp|foo}}")
        self.assertEqual(ret, "afoob")

    def test_invoke1(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return "in test"
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "a{{#invoke:testmod|testfn}}b")
        self.assertEqual(ret, "ain testb")

    def test_invoke2(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(#frame.args)
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "0")

    def test_invoke3(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(#frame.args)
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|a|b}}")
        self.assertEqual(ret, "2")

    def test_invoke4(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame.args[1]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|a|b}}")
        self.assertEqual(ret, "a")

    def test_invoke5(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame.args.foo
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|foo=bar|a}}")
        self.assertEqual(ret, "bar")

    def test_invoke6(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame.args["foo"]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|foo=bar|a}}")
        self.assertEqual(ret, "bar")

    def test_invoke7(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn|foo={{{1}}}|{{{2}}}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame.args["foo"]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|a|b}}")
        self.assertEqual(ret, "a")

    def test_invoke8(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn|foo={{{1}}}|{{{2}}}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame.args["foo"]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|a|b}}")
        self.assertEqual(ret, "a")

    def test_invoke9(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn|foo={{{1}}}|{{{2}}}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame.args.foo
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|a|b}}")
        self.assertEqual(ret, "a")

    def test_invoke10(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn|foo={{{1}}}|{{{2}}}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame.args[1]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|a|b}}")
        self.assertEqual(ret, "b")

    def test_invoke11(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(frame.args.foo)
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl}}")
        self.assertEqual(ret, "nil")

    def test_invoke12(self):
        # Testing that intervening template call does not mess up arguments
        # (this was once a bug)
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{templ2|{{#invoke:testmod|testfn}}}}"],
            ["Template", "templ2", "{{{1}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(frame:getParent().args[1])
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|arg1}}")
        self.assertEqual(ret, "arg1")

    def test_invoke13(self):
        # Testing that intervening template call does not mess up arguments
        # (this was once a bug)
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{templ2|{{#invoke:testmod|testfn}}}}"],
            ["Template", "templ2", "{{{1}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(frame:getParent().args[1])
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|arg1}}")
        self.assertEqual(ret, "arg1")

    def test_invoke14(self):
        # Testing that argument names are handled correctly if = inside HTML tag
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             """{{#invoke:testmod|testfn|<span class="foo">bar</span>}}"""],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(frame.args[1])
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl}}")
        self.assertEqual(ret, """<span class="foo">bar</span>""")

    def test_invoke15(self):
        # Testing safesubst:
        ctx = phase1_to_ctx([
            ["Template", "testtempl", "{{safesubst:#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return "correct"
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl}}")
        self.assertEqual(ret, """correct""")

    def test_invoke16(self):
        # Testing safesubst:, with space before
        ctx = phase1_to_ctx([
            ["Template", "testtempl", "{{ safesubst:#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return "correct"
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl}}")
        self.assertEqual(ret, """correct""")

    def test_invoke17(self):
        # Testing safesubst: coming from template
        ctx = phase1_to_ctx([
            ["Template", "testtempl", "{{ {{templ2}}#invoke:testmod|testfn}}"],
            ["Template", "templ2", "safesubst:"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return "correct"
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl}}")
        self.assertEqual(ret, """correct""")

    def test_invoke18(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl", "{{#invoke:\ntestmod\n|\ntestfn\n}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return "correct"
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl}}")
        self.assertEqual(ret, """correct""")

    def test_frame_parent1(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(frame:getParent().args[1])
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl}}")
        self.assertEqual(ret, "nil")

    def test_frame_parent2(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getParent().args[1]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|foo|bar}}")
        self.assertEqual(ret, "foo")

    def test_frame_parent3(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getParent().args[2]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|foo|bar}}")
        self.assertEqual(ret, "bar")

    def test_frame_parent4(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return tostring(frame:getParent().args[3])
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|foo|bar}}")
        self.assertEqual(ret, "nil")

    def test_frame_parent5(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getParent().args.foo
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|foo|bar|foo=zap}}")
        self.assertEqual(ret, "zap")

    def test_frame_parent6(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl", "{{#invoke:testmod|testfn}}"],
            ["Template", "testtempl2", "foo{{{1|}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  local parent = frame:getParent()
  return parent.args[1] .. parent.args[2]
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|{{testtempl2|zz}}|yy}}")
        self.assertEqual(ret, "foozzyy")

    def test_frame_parent7(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Template", "testtempl2", "foo{{{1|}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getTitle()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|{{testtempl2|zz}}|yy}}")
        self.assertEqual(ret, "testmod")

    def test_frame_parent8(self):
        ctx = phase1_to_ctx([
            ["Template", "testtempl",
             "{{#invoke:testmod|testfn}}"],
            ["Template", "testtempl2", "foo{{{1|}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getParent():getTitle()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl|{{testtempl2|zz}}|yy}}")
        self.assertEqual(ret, "testtempl")

    def test_frame_parent9(self):
        # parent of parent should be nil
        ctx = phase1_to_ctx([
            ["Template", "testtempl", "{{#invoke:testmod|testfn}}"],
            ["Template", "testtempl2", "{{testtempl}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getParent():getParent()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{testtempl2}}")
        self.assertEqual(ret, "nil")

    def test_frame_callParserFunction1(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:callParserFunction("#tag", {"br"})
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "<br />")

    def test_frame_callParserFunction2(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:callParserFunction{name = "#tag", args = {"br"}}
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "<br />")

    def test_frame_callParserFunction3(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:callParserFunction("#tag", "br")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "<br />")

    def test_frame_callParserFunction4(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:callParserFunction("#tag", "div", "content")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "<div>content</div>")

    def test_frame_getArgument1(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getArgument(1).expand()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|a|b}}")
        self.assertEqual(ret, "a")

    def test_frame_getArgument2(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getArgument(2).expand()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|a|b}}")
        self.assertEqual(ret, "b")

    def test_frame_getArgument3(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getArgument(3)
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|a|b}}")
        self.assertEqual(ret, "nil")

    def test_frame_getArgument4(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getArgument("foo").expand()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|foo=bar}}")
        self.assertEqual(ret, "bar")

    def test_frame_getArgument5(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getArgument{name = "foo"}.expand()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|foo=bar}}")
        self.assertEqual(ret, "bar")

    def test_frame_getArgument6(self):
        ctx = phase1_to_ctx([
            ["Template", "templ", "{{#invoke:testmod|testfn|a|b}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:getParent():getArgument(2).expand()
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{templ|x|y}}")
        self.assertEqual(ret, "y")

    def test_frame_preprocess1(self):
        ctx = phase1_to_ctx([
            ["Template", "testtemplate", "foo{{{1}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:preprocess("a{{testtemplate|a}}b")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|foo=bar}}")
        self.assertEqual(ret, "afooab")

    def test_frame_preprocess2(self):
        ctx = phase1_to_ctx([
            ["Template", "testtemplate", "foo{{{1}}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:preprocess{text = "a{{testtemplate|a}}b"}
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|foo=bar}}")
        self.assertEqual(ret, "afooab")

    def test_frame_argumentPairs1(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  local ret = ""
  for k, v in frame:argumentPairs() do
    ret = ret .. "|" .. tostring(k) .. "=" .. tostring(v)
  end
  return ret
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|foo=bar}}")
        self.assertEqual(ret, "|foo=bar")

    def test_frame_argumentPairs2(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  local ret = ""
  for k, v in frame:argumentPairs() do
    ret = ret .. "|" .. tostring(k) .. "=" .. tostring(v)
  end
  return ret
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn|a|b}}")
        self.assertEqual(ret, "|1=a|2=b")

    def test_frame_argumentPairs3(self):
        ctx = phase1_to_ctx([
            ["Template", "templ", "{{#invoke:testmod|testfn|a|b}}"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  local ret = ""
  for k, v in frame:getParent():argumentPairs() do
    ret = ret .. "|" .. tostring(k) .. "=" .. tostring(v)
  end
  return ret
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{templ|x|y}}")
        self.assertEqual(ret, "|1=x|2=y")

    def test_frame_expandTemplate1(self):
        ctx = phase1_to_ctx([
            ["Template", "templ", "a{{{1}}}b{{{2}}}c{{{k}}}d"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:expandTemplate{title="templ", args={"foo", "bar", k=4}}
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "afoobbarc4d")

    def test_frame_expandTemplate2(self):
        ctx = phase1_to_ctx([
            ["Template", "templ", "a{{{1}}}b"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:expandTemplate{title="templ", args={"|"}}
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "a|b")

    def test_frame_expandTemplate3(self):
        ctx = phase1_to_ctx([
            ["Template", "templ", "a{{{1}}}b"],
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:expandTemplate{title="templ", args={"{{!}}"}}
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "a{{!}}b")

    def test_frame_extensionTag1(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:extensionTag("ref", "some text")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "<ref>some text</ref>")

    def test_frame_extensionTag2(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:extensionTag("ref", "some text", "class=foo")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, '<ref class="foo">some text</ref>')

    def test_frame_extensionTag3(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:extensionTag{name="ref", content="some text",
                            args={class="bar", id="test"}}
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, '<ref class="bar" id="test">some text</ref>')

    def test_frame_extensionTag4(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return frame:extensionTag("br")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, '<br />')



    def test_mw_text_nowiki1(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", """
local export = {}
function export.testfn(frame)
  return mw.text.nowiki("#[foo]{{a|b}}")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "&num;&lsqb;foo&rsqb;&lbrace;&lbrace;a&vert;"
                         "b&rbrace;&rbrace;")

    def test_mw_text_nowiki2(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", r"""
local export = {}
function export.testfn(frame)
  return mw.text.nowiki("\n#<foo>'#=\n\nX\n")
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "\n&num;&lt;foo&gt;&apos;#&#61;\n&NewLine;X\n")

    def test_mw_text_nowiki3(self):
        ctx = phase1_to_ctx([
            ["Scribunto", "testmod", r"""
local export = {}
function export.testfn(frame)
  return mw.text.nowiki('"test"\n----\nhttp://example.com\n')
end
return export
"""]])
        ret = expand_wikitext(ctx, "Tt", "{{#invoke:testmod|testfn}}")
        self.assertEqual(ret, "&quot;test&quot;\n&minus;---\n"
                         "http&colon;//example.com\n")


# XXX figure out why template R:L&S not found in luatest3.py
# XXX figure out why module:parameters:196 fails (mw.title.getCurrentTitle()?)

# XXX test frame:newParserValue
# XXX test frame:newTemplateParserValue
# XXX test frame:newChild
# XXX test redirects for Lua modules.  Are they possible?
# XXX test case variations of template names and parser function names

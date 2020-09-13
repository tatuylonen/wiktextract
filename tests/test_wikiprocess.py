# Tests for processing WikiText templates and macros
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

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

    def test_pagename1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{PAGENAME}}")
        self.assertEqual(ret, "Tt")

    def test_pagename2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{PAGENAME}}")
        self.assertEqual(ret, "Tt/doc")

    def test_namespace1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Help:Tt/doc", "{{NAMESPACE}}")
        self.assertEqual(ret, "Help")

    def test_namespace2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt/doc", "{{NAMESPACE}}")
        self.assertEqual(ret, "")

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
        self.assertEqual(ret, "2")

    def test_pos2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pos: xyzayz |zz}}")
        self.assertEqual(ret, "")

    def test_pos3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#pos: xyzayz }}")
        self.assertEqual(ret, "")

    def test_rpos1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#rpos: xyzayz |yz}}")
        self.assertEqual(ret, "5")

    def test_rpos2(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#rpos: xyzayz |zz}}")
        self.assertEqual(ret, "")

    def test_rpos3(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#rpos: xyzayz }}")
        self.assertEqual(ret, "")

    def test_sub1(self):
        ctx = phase1_to_ctx([])
        ret = expand_wikitext(ctx, "Tt", "{{#sub: xyzayz |3}}")
        self.assertEqual(ret, "zayz ")

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

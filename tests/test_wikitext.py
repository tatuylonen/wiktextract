import unittest
from wiktextract.wikitext import parse, parse_with_ctx, NodeKind



class WikiTextTests(unittest.TestCase):

    def test_empty(self):
        tree = parse("test", "")
        self.assertEqual(tree.kind, NodeKind.ROOT)
        self.assertEqual(tree.children, [])
        self.assertEqual(tree.args, ["test"])

    def test_text(self):
        tree = parse("test", "some text")
        self.assertEqual(tree.children, ["some text"])

    def test_text2(self):
        tree = parse("test", "some:text")
        self.assertEqual(tree.children, ["some:text"])

    def test_text3(self):
        tree = parse("test", "some|text")
        self.assertEqual(tree.children, ["some|text"])

    def test_text4(self):
        tree = parse("test", "some}}text")
        self.assertEqual(tree.children, ["some}}text"])

    def test_text5(self):
        tree = parse("test", "some* text")
        self.assertEqual(tree.children, ["some* text"])

    def test_hdr2a(self):
        tree = parse("test", "==Foo==")
        assert len(tree.children) == 1
        child = tree.children[0]
        self.assertEqual(child.kind, NodeKind.LEVEL2)
        self.assertEqual(child.args, [["Foo"]])
        self.assertEqual(child.children, [])

    def test_hdr2b(self):
        tree = parse("test", "== Foo:Bar ==\nZappa\n")
        assert len(tree.children) == 1
        child = tree.children[0]
        self.assertEqual(child.kind, NodeKind.LEVEL2)
        self.assertEqual(child.args, [["Foo:Bar"]])
        self.assertEqual(child.children, ["\nZappa\n"])

    def test_hdr2c(self):
        tree = parse("test", "=== Foo:Bar ===\nZappa\n")
        assert len(tree.children) == 1
        child = tree.children[0]
        self.assertEqual(child.kind, NodeKind.LEVEL3)
        self.assertEqual(child.args, [["Foo:Bar"]])
        self.assertEqual(child.children, ["\nZappa\n"])

    def test_hdr23a(self):
        tree = parse("test", "==Foo==\na\n===Bar===\nb\n===Zappa===\nc\n")
        assert len(tree.children) == 1
        h2 = tree.children[0]
        self.assertEqual(h2.kind, NodeKind.LEVEL2)
        self.assertEqual(len(h2.children), 3)
        self.assertEqual(h2.children[0], "\na\n")
        h3a = h2.children[1]
        h3b = h2.children[2]
        self.assertEqual(h3a.kind, NodeKind.LEVEL3)
        self.assertEqual(h3b.kind, NodeKind.LEVEL3)
        self.assertEqual(h3a.args, [["Bar"]])
        self.assertEqual(h3a.children, ["\nb\n"])
        self.assertEqual(h3b.args, [["Zappa"]])
        self.assertEqual(h3b.children, ["\nc\n"])

    def test_hdr23b(self):
        tree = parse("test", "==Foo==\na\n===Bar===\nb\n==Zappa==\nc\n")
        assert len(tree.children) == 2
        h2a = tree.children[0]
        h2b = tree.children[1]
        self.assertEqual(h2a.kind, NodeKind.LEVEL2)
        self.assertEqual(h2b.kind, NodeKind.LEVEL2)
        self.assertEqual(len(h2a.children), 2)
        self.assertEqual(h2a.children[0], "\na\n")
        h3a = h2a.children[1]
        self.assertEqual(h3a.kind, NodeKind.LEVEL3)
        self.assertEqual(h3a.args, [["Bar"]])
        self.assertEqual(h3a.children, ["\nb\n"])
        self.assertEqual(h2b.args, [["Zappa"]])
        self.assertEqual(h2b.children, ["\nc\n"])

    def test_hdr23456(self):
        tree = parse("test", """
==Foo2==
dasfdasfas
===Foo3===
adsfdasfas
====Foo4====
dasfdasfdas
=====Foo5=====
dsfasasdd
======Foo6======
dasfasddasfdas
""")
        self.assertEqual(len(tree.children), 2)
        h2 = tree.children[1]
        h3 = h2.children[1]
        h4 = h3.children[1]
        h5 = h4.children[1]
        h6 = h5.children[1]
        self.assertEqual(h6.kind, NodeKind.LEVEL6)
        self.assertEqual(h6.children, ["\ndasfasddasfdas\n"])

    def test_hdr_anchor(self):
        tree = parse("test", """==<span id="anchor">hdr text</span>==\ndata""")
        self.assertEqual(len(tree.children), 1)
        h = tree.children[0]
        self.assertEqual(h.kind, NodeKind.LEVEL2)
        self.assertEqual(len(h.args), 1)
        self.assertEqual(len(h.args[0]), 3)
        a, b, c = h.args[0]
        self.assertEqual(a.kind, NodeKind.HTML)
        self.assertEqual(a.attrs.get("_close", False), False)
        self.assertEqual(a.attrs.get("_also_close", False), False)
        self.assertEqual(a.children, [])
        self.assertEqual(b, "hdr text")
        self.assertEqual(c.kind, NodeKind.HTML)
        self.assertEqual(c.attrs.get("_close", False), True)
        self.assertEqual(c.attrs.get("_also_close", False), False)
        self.assertEqual(c.children, [])
        self.assertEqual(h.children, ["\ndata"])

    def test_nowiki1(self):
        tree = parse("test", "==Foo==\na<nowiki>\n===Bar===\nb</nowiki>\n==Zappa==\nc\n")
        assert len(tree.children) == 2
        h2a = tree.children[0]
        h2b = tree.children[1]
        self.assertEqual(h2a.kind, NodeKind.LEVEL2)
        self.assertEqual(h2b.kind, NodeKind.LEVEL2)
        self.assertEqual(h2a.children, ["\na\n===Bar===\nb\n"])
        self.assertEqual(h2b.args, [["Zappa"]])
        self.assertEqual(h2b.children, ["\nc\n"])

    def test_nowiki2(self):
        tree = parse("test", "<<nowiki/>foo>")
        assert tree.children == ["<foo>"]

    def test_nowiki3(self):
        tree = parse("test", "&<nowiki/>amp;")
        self.assertEqual(tree.children, ["&amp;"])  # Should be expanded later

    def test_nowiki4(self):
        tree, ctx = parse_with_ctx("test", "a</nowiki>b")
        self.assertEqual(tree.children, ["a</nowiki>b"])
        self.assertEqual(len(ctx.errors), 1)

    def test_entity_noexpand(self):
        tree = parse("test", "R&amp;D")
        self.assertEqual(tree.children, ["R&amp;D"])  # Should be expanded later

    def test_html1(self):
        tree = parse("test", "<b>foo</b>")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a.kind, NodeKind.HTML)
        self.assertEqual(a.args, "b")
        self.assertEqual(a.children, [])
        self.assertEqual(b, "foo")
        self.assertEqual(c.kind, NodeKind.HTML)
        self.assertEqual(c.args, "b")
        self.assertEqual(c.children, [])

    def test_html2(self):
        tree = parse("test", """<div style='color: red' width="40" """
                     """max-width=100 bogus>red text</div>""")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a.kind, NodeKind.HTML)
        self.assertEqual(a.args, "div")
        self.assertEqual(a.attrs.get("_close", False), False)
        self.assertEqual(a.attrs.get("_also_close", False), False)
        self.assertEqual(a.attrs.get("style", False), "color: red")
        self.assertEqual(a.attrs.get("width", False), "40")
        self.assertEqual(a.attrs.get("max-width", False), "100")
        self.assertEqual(a.attrs.get("bogus", False), "")
        self.assertEqual(a.children, [])
        self.assertEqual(b, "red text")
        self.assertEqual(c.kind, NodeKind.HTML)
        self.assertEqual(c.args, "div")
        self.assertEqual(c.attrs.get("_close", False), True)
        self.assertEqual(c.children, [])

    def test_html3(self):
        tree = parse("test", """<br class="big" />""")
        self.assertEqual(len(tree.children), 1)
        h = tree.children[0]
        self.assertEqual(h.kind, NodeKind.HTML)
        self.assertEqual(h.args, "br")
        self.assertEqual(h.attrs.get("class", False), "big")
        self.assertEqual(h.attrs.get("_close", False), False)
        self.assertEqual(h.attrs.get("_also_close", False), True)
        self.assertEqual(h.children, [])

    def test_html_unknown(self):
        tree, ctx = parse_with_ctx("test", "a<unknown>foo</unknown>b")
        self.assertEqual(tree.children, ["a<unknown>foo</unknown>b"])
        self.assertEqual(len(ctx.errors), 2)

    def test_italic(self):
        tree = parse("test", "a ''italic test'' b")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a ")
        self.assertEqual(b.kind, NodeKind.ITALIC)
        self.assertEqual(b.children, ["italic test"])
        self.assertEqual(c, " b")

    def test_bold(self):
        tree = parse("test", "a '''bold test''' b")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a ")
        self.assertEqual(b.kind, NodeKind.BOLD)
        self.assertEqual(b.children, ["bold test"])
        self.assertEqual(c, " b")

    def test_bolditalic(self):
        tree = parse("test", "a '''''bold italic test''''' b")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a ")
        self.assertEqual(b.kind, NodeKind.BOLD)
        self.assertEqual(len(b.children), 1)
        ba = b.children[0]
        self.assertEqual(ba.kind, NodeKind.ITALIC)
        self.assertEqual(ba.children, ["bold italic test"])

    def test_hline(self):
        tree = parse("test", "foo\n----\nmore")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "foo\n")
        self.assertEqual(b.kind, NodeKind.HLINE)
        self.assertEqual(c, "\nmore")

    def test_ul(self):
        tree = parse("test", "foo\n\n* item1\n** item1.1\n** item1.2\n"
                     "* item2\n")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "foo\n\n")
        self.assertEqual(b.kind, NodeKind.LIST_ITEM)
        self.assertEqual(b.args, "*")
        self.assertEqual(len(b.children), 3)
        ba, bb, bc = b.children
        self.assertEqual(ba, "item1\n")
        self.assertEqual(bb.kind, NodeKind.LIST_ITEM)
        self.assertEqual(bb.args, "**")
        self.assertEqual(bb.children, ["item1.1\n"])
        self.assertEqual(bc.kind, NodeKind.LIST_ITEM)
        self.assertEqual(bc.args, "**")
        self.assertEqual(bc.children, ["item1.2\n"])
        self.assertEqual(c.kind, NodeKind.LIST_ITEM)
        self.assertEqual(c.args, "*")
        self.assertEqual(c.children, ["item2\n"])

    def test_ol(self):
        tree = parse("test", "foo\n\n# item1\n## item1.1\n## item1.2\n"
                     "# item2\n")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "foo\n\n")
        self.assertEqual(b.kind, NodeKind.LIST_ITEM)
        self.assertEqual(b.args, "#")
        self.assertEqual(len(b.children), 3)
        ba, bb, bc = b.children
        self.assertEqual(ba, "item1\n")
        self.assertEqual(bb.kind, NodeKind.LIST_ITEM)
        self.assertEqual(bb.args, "##")
        self.assertEqual(bb.children, ["item1.1\n"])
        self.assertEqual(bc.kind, NodeKind.LIST_ITEM)
        self.assertEqual(bc.args, "##")
        self.assertEqual(bc.children, ["item1.2\n"])
        self.assertEqual(c.kind, NodeKind.LIST_ITEM)
        self.assertEqual(c.args, "#")
        self.assertEqual(c.children, ["item2\n"])

    def test_link1(self):
        tree = parse("test", "a [[Main Page]] b")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a ")
        self.assertEqual(b.kind, NodeKind.LINK)
        self.assertEqual(b.args, [["Main Page"]])
        self.assertEqual(b.children, [])
        self.assertEqual(c, " b")

    def test_link2(self):
        tree = parse("test", "[[Help:Contents]]")
        self.assertEqual(len(tree.children), 1)
        p = tree.children[0]
        self.assertEqual(p.kind, NodeKind.LINK)
        self.assertEqual(p.args, [["Help:Contents"]])
        self.assertEqual(p.children, [])

    def test_link3(self):
        tree = parse("test", "[[#See also|different text]]")
        self.assertEqual(len(tree.children), 1)
        p = tree.children[0]
        self.assertEqual(p.kind, NodeKind.LINK)
        self.assertEqual(p.args, [["#See also"], ["different text"]])
        self.assertEqual(p.children, [])

    def test_link4(self):
        tree = parse("test", "[[User:John Doe|]]")
        self.assertEqual(len(tree.children), 1)
        p = tree.children[0]
        self.assertEqual(p.kind, NodeKind.LINK)
        self.assertEqual(p.args, [["User:John Doe"], []])
        self.assertEqual(p.children, [])

    def test_link5(self):
        tree = parse("test", "[[Help]]<nowiki />ful advise")
        self.assertEqual(len(tree.children), 2)
        a, b = tree.children
        self.assertEqual(a.kind, NodeKind.LINK)
        self.assertEqual(a.args, [["Help"]])
        self.assertEqual(a.children, [])
        self.assertEqual(b, "ful advise")

    def test_link_trailing(self):
        tree = parse("test", "[[Help]]ing heal")
        self.assertEqual(len(tree.children), 2)
        a, b = tree.children
        self.assertEqual(a.kind, NodeKind.LINK)
        self.assertEqual(a.args, [["Help"]])
        self.assertEqual(a.children, ["ing"])
        self.assertEqual(b, " heal")

    def test_url1(self):
        tree = parse("test", "this https://wikipedia.com link")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "this ")
        self.assertEqual(b.kind, NodeKind.URL)
        self.assertEqual(b.args, [["https://wikipedia.com"]])
        self.assertEqual(b.children, [])

        self.assertEqual(c, " link")

    def test_url2(self):
        tree = parse("test", "this [https://wikipedia.com] link")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "this ")
        self.assertEqual(b.kind, NodeKind.URL)
        self.assertEqual(b.args, [["https://wikipedia.com"]])
        self.assertEqual(b.children, [])
        self.assertEqual(c, " link")

    def test_url3(self):
        tree = parse("test", "this [https://wikipedia.com here] link")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "this ")
        self.assertEqual(b.kind, NodeKind.URL)
        self.assertEqual(b.args, [["https://wikipedia.com"], ["here"]])
        self.assertEqual(b.children, [])
        self.assertEqual(c, " link")

    def test_url4(self):
        tree = parse("test", "this [https://wikipedia.com here multiword] link")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "this ")
        self.assertEqual(b.kind, NodeKind.URL)
        self.assertEqual(b.args, [["https://wikipedia.com"],
                                  ["here multiword"]])
        self.assertEqual(b.children, [])
        self.assertEqual(c, " link")

    def test_preformatted1(self):
        tree = parse("test", """
 Start each line with a space.
 Text is '''preformatted''' and
 markups can be done.
Next para""")
        self.assertEqual(len(tree.children), 3)
        self.assertEqual(tree.children[0], "\n")
        p = tree.children[1]
        self.assertEqual(p.kind, NodeKind.PREFORMATTED)
        a, b, c = p.children
        self.assertEqual(a, " Start each line with a space.\n Text is ")
        self.assertEqual(b.kind, NodeKind.BOLD)
        self.assertEqual(b.children, ["preformatted"])
        self.assertEqual(c, " and\n markups can be done.\n")
        self.assertEqual(tree.children[2], "Next para")

    def test_preformatted2(self):
        tree = parse("test", """
 <nowiki>
def foo(x):
  print(foo)
</nowiki>""")
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[0], "\n")
        p = tree.children[1]
        self.assertEqual(p.kind, NodeKind.PREFORMATTED)
        self.assertEqual(p.children, [" \ndef foo(x):\n  print(foo)\n"])

    def test_pre1(self):
        tree = parse("test", """
<PRE>preformatted &amp; '''not bold''' text</pre> after""")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "\n")
        self.assertEqual(b.kind, NodeKind.PRE)
        self.assertEqual(b.children, ["preformatted &amp; '''not bold''' text"])
        self.assertEqual(c, " after")

    def test_pre2(self):
        tree = parse("test", """<PRE style="color: red">line1\nline2</pre>""")
        self.assertEqual(len(tree.children), 1)
        h = tree.children[0]
        self.assertEqual(h.kind, NodeKind.PRE)
        self.assertEqual(h.args, [])
        self.assertEqual(h.attrs.get("_close", False), False)
        self.assertEqual(h.attrs.get("_also_close", False), False)
        self.assertEqual(h.attrs.get("style", False), "color: red")

    def test_comment1(self):
        tree = parse("test", "foo<!-- not\nshown-->bar")
        self.assertEqual(tree.children, ["foobar"])

    def test_comment2(self):
        tree = parse("test", "foo<!-- not\nshown-->bar <! -- second -- > now")
        self.assertEqual(tree.children, ["foobar  now"])

    def test_magicword1(self):
        tree = parse("test", "a __NOTOC__ b")
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a ")
        self.assertEqual(b.kind, NodeKind.MAGIC_WORD)
        self.assertEqual(b.args, "__NOTOC__")
        self.assertEqual(b.children, [])
        self.assertEqual(c, " b")

    def test_template1(self):
        tree = parse("test", "a{{foo}}b")
        print(tree)
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a")
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(b.args, [["foo"]])
        self.assertEqual(b.children, [])
        self.assertEqual(c, "b")

    def test_template2(self):
        tree = parse("test", "{{foo|bar||z|1-1/2|}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(b.args, [["foo"], ["bar"], [], ["z"], ["1-1/2"], []])
        self.assertEqual(b.children, [])

    def test_template3(self):
        tree = parse("test", "{{\nfoo\n|\nname=testi|bar\n|\nbaz}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(b.args, [["\nfoo\n"], ["\nname=testi"], ["bar\n"],
                                  ["\nbaz"]])
        self.assertEqual(b.children, [])

    def test_template4(self):
        tree = parse("test", "{{foo bar|name=test word|tässä}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(b.args, [["foo bar"], ["name=test word"],
                                  ["tässä"]])
        self.assertEqual(b.children, [])

    def test_template5(self):
        tree = parse("test", "{{foo bar|name=test word|tässä}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(b.args, [["foo bar"], ["name=test word"],
                                  ["tässä"]])
        self.assertEqual(b.children, [])

    def test_template6(self):
        tree = parse("test", "{{foo bar|{{nested|[[link]]}}}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(len(b.args), 2)
        self.assertEqual(b.args[0], ["foo bar"])
        c = b.args[1]
        self.assertIsInstance(c, list)
        self.assertEqual(len(c), 1)
        d = c[0]
        self.assertEqual(d.kind, NodeKind.TEMPLATE)
        self.assertEqual(len(d.args), 2)
        self.assertEqual(d.args[0], ["nested"])
        self.assertEqual(len(d.args[1]), 1)
        e = d.args[1][0]
        self.assertEqual(e.kind, NodeKind.LINK)
        self.assertEqual(e.args, [["link"]])

    def test_template7(self):
        tree = parse("test", "{{{{{foo}}}|bar}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(len(b.args), 2)
        c = b.args[0]
        self.assertIsInstance(c, list)
        self.assertEqual(len(c), 1)
        d = c[0]
        self.assertEqual(d.kind, NodeKind.TEMPLATEVAR)
        self.assertEqual(d.args, [["foo"]])
        self.assertEqual(d.children, [])
        self.assertEqual(b.args[1], ["bar"])

    def test_template8(self):
        # Namespace specifiers, e.g., {{int:xyz}} should not generate
        # parser functions
        tree = parse("test", "{{int:xyz}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(b.args, [["int:xyz"]])

    def test_template9(self):
        # Main namespace references, e.g., {{:xyz}} should not
        # generate parser functions
        tree = parse("test", "{{:xyz}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATE)
        self.assertEqual(b.args, [[":xyz"]])

    def test_templatevar1(self):
        tree = parse("test", "{{{foo}}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATEVAR)
        self.assertEqual(b.args, [["foo"]])
        self.assertEqual(b.children, [])

    def test_templatevar2(self):
        tree = parse("test", "{{{foo|bar|baz}}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATEVAR)
        self.assertEqual(b.args, [["foo"], ["bar"], ["baz"]])
        self.assertEqual(b.children, [])

    def test_templatevar3(self):
        tree = parse("test", "{{{{{{foo}}}|bar|baz}}}")
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.TEMPLATEVAR)
        c = b.args[0][0]
        self.assertEqual(c.kind, NodeKind.TEMPLATEVAR)
        self.assertEqual(c.args, [["foo"]])
        self.assertEqual(b.args[1:], [["bar"], ["baz"]])
        self.assertEqual(b.children, [])

    def test_parserfn1(self):
        tree = parse("test", "{{CURRENTYEAR}}x")
        self.assertEqual(len(tree.children), 2)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.PARSERFN)
        self.assertEqual(b.args, [["CURRENTYEAR"]])
        self.assertEqual(b.children, [])
        self.assertEqual(tree.children[1], "x")

    def test_parserfn2(self):
        tree = parse("test", "{{PAGESIZE:TestPage}}")
        print(tree)
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.PARSERFN)
        self.assertEqual(b.args, [["PAGESIZE"], ["TestPage"]])
        self.assertEqual(b.children, [])

    def test_parserfn3(self):
        tree = parse("test", "{{#invoke:testmod|testfn|testarg1|testarg2}}")
        print(tree)
        self.assertEqual(len(tree.children), 1)
        b = tree.children[0]
        self.assertEqual(b.kind, NodeKind.PARSERFN)
        self.assertEqual(b.args, [["#invoke"], ["testmod"], ["testfn"],
                                  ["testarg1"], ["testarg2"]])
        self.assertEqual(b.children, [])


# XXX test:
# XXX TABLE and its subnodes

# Note: Magic links (e.g., ISBN, RFC) are not supported.  They are
# disabled by default in MediaWiki since version 1.28 and Wiktionary
# does not really seem to use them and they are not particularly
# important.  See https://www.mediawiki.org/wiki/Help:Magic_links

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
        print(h2.children)
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
        print(h2a.children)
        print(h2b.children)
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

    def test_nowiki1(self):
        tree = parse("test", "==Foo==\na<nowiki>\n===Bar===\nb</nowiki>\n==Zappa==\nc\n")
        print(tree)
        assert len(tree.children) == 2
        h2a = tree.children[0]
        h2b = tree.children[1]
        self.assertEqual(h2a.kind, NodeKind.LEVEL2)
        self.assertEqual(h2b.kind, NodeKind.LEVEL2)
        print(h2a.children)
        print(h2b.children)
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
        self.assertEqual(a.args, ["b"])
        self.assertEqual(a.children, ["<b>"])
        self.assertEqual(b, "foo")
        self.assertEqual(c.kind, NodeKind.HTML)
        self.assertEqual(c.args, ["b"])
        self.assertEqual(c.children, ["</b>"])

    def test_html_unknown(self):
        tree, ctx = parse_with_ctx("test", "a<unknown>foo</unknown>b")
        self.assertEqual(tree.children, ["a<unknown>foo</unknown>b"])
        self.assertEqual(len(ctx.errors), 2)

    def test_italic(self):
        tree = parse("test", "a ''italic test'' b")
        print(tree)
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a ")
        self.assertEqual(b.kind, NodeKind.ITALIC)
        self.assertEqual(b.children, ["italic test"])
        self.assertEqual(c, " b")

    def test_bold(self):
        tree = parse("test", "a '''bold test''' b")
        print(tree)
        self.assertEqual(len(tree.children), 3)
        a, b, c = tree.children
        self.assertEqual(a, "a ")
        self.assertEqual(b.kind, NodeKind.BOLD)
        self.assertEqual(b.children, ["bold test"])
        self.assertEqual(c, " b")

    def test_bolditalic(self):
        tree = parse("test", "a '''''bold italic test''''' b")
        print(tree)
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
        print(tree)
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
        print(tree)
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

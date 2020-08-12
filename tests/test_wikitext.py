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
        self.assertEqual(tree.children, ["some", ":", "text"])

    def test_text3(self):
        tree = parse("test", "some|text")
        self.assertEqual(tree.children, ["some", "|", "text"])

    def test_text4(self):
        tree = parse("test", "some}}text")
        self.assertEqual(tree.children, ["some", "}}", "text"])

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
        self.assertEqual(child.args, [["Foo", ":", "Bar"]])
        self.assertEqual(child.children, ["\nZappa\n"])

    def test_hdr2c(self):
        tree = parse("test", "=== Foo:Bar ===\nZappa\n")
        assert len(tree.children) == 1
        child = tree.children[0]
        self.assertEqual(child.kind, NodeKind.LEVEL3)
        self.assertEqual(child.args, [["Foo", ":", "Bar"]])
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
        self.assertEqual(len(h2a.children), 7)
        self.assertEqual(h2a.children, ["\na", "\n", "===", "Bar", "===",
                                        "\nb", "\n"])
        self.assertEqual(h2b.args, [["Zappa"]])
        self.assertEqual(h2b.children, ["\nc\n"])

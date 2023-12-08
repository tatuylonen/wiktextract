import unittest

from wiktextract.extractor.de.utils import match_senseid


class TestDEUtils(unittest.TestCase):
    def test_match_senseid1(self):
        senseid, node_text = match_senseid("[1a] foo bar")
        self.assertEqual(senseid, "1a")
        self.assertEqual(node_text, "foo bar")

    def test_match_senseid2(self):
        senseid, node_text = match_senseid("[42] baz")
        self.assertEqual(senseid, "42")
        self.assertEqual(node_text, "baz")

    def test_match_senseid3(self):
        senseid, node_text = match_senseid("[abc] qux")
        self.assertEqual(senseid, None)
        self.assertEqual(node_text, "[abc] qux")

    def test_match_senseid4(self):
        senseid, node_text = match_senseid("no senseid")
        self.assertIsNone(senseid)
        self.assertEqual(node_text, "no senseid")

    def test_match_senseid5(self):
        senseid, node_text = match_senseid("[123] ")
        self.assertEqual(senseid, "123")
        self.assertEqual(node_text, "")

    def test_match_senseid6(self):
        senseid, node_text = match_senseid("[a1b2c3] foo [xyz] bar")
        self.assertEqual(senseid, None)
        self.assertEqual(node_text, "[a1b2c3] foo [xyz] bar")

    def test_match_senseid7(self):
        senseid, node_text = match_senseid("[1.1] foo bar")
        self.assertEqual(senseid, "1.1")
        self.assertEqual(node_text, "foo bar")

    def test_match_senseid8(self):
        senseid, node_text = match_senseid("[1.1a] foo bar")
        self.assertEqual(senseid, None)
        self.assertEqual(node_text, "[1.1a] foo bar")

    def test_match_senseid9(self):
        senseid, node_text = match_senseid("[1.1.1] foo bar")
        self.assertEqual(senseid, None)
        self.assertEqual(node_text, "[1.1.1] foo bar")

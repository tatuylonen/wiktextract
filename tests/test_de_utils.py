import unittest

from wiktextract.extractor.de.utils import extract_sense_index


class TestDEUtils(unittest.TestCase):
    def test_match_senseid1(self):
        senseid, node_text = extract_sense_index("[1a] foo bar")
        self.assertEqual(senseid, "1a")
        self.assertEqual(node_text, "foo bar")

    def test_match_senseid2(self):
        senseid, node_text = extract_sense_index("[42] baz")
        self.assertEqual(senseid, "42")
        self.assertEqual(node_text, "baz")

    def test_match_senseid4(self):
        senseid, node_text = extract_sense_index("no senseid")
        self.assertEqual(senseid, "")
        self.assertEqual(node_text, "no senseid")

    def test_match_senseid5(self):
        senseid, node_text = extract_sense_index("[123] ")
        self.assertEqual(senseid, "123")
        self.assertEqual(node_text, "")

    def test_match_senseid7(self):
        senseid, node_text = extract_sense_index("[1.1] foo bar")
        self.assertEqual(senseid, "1.1")
        self.assertEqual(node_text, "foo bar")

    def test_match_senseid8(self):
        senseid, node_text = extract_sense_index("[1.1a] foo bar")
        self.assertEqual(senseid, "1.1a")
        self.assertEqual(node_text, "foo bar")

    def test_match_senseid9(self):
        senseid, node_text = extract_sense_index("[1.1.1] foo bar")
        self.assertEqual(senseid, "1.1.1")
        self.assertEqual(node_text, "foo bar")

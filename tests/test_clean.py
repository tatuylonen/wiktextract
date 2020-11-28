import unittest
import collections
import wiktextract
from wiktextract.clean import clean_value, clean_quals
from wiktextract import WiktionaryConfig


class WiktExtractTests(unittest.TestCase):

    config = WiktionaryConfig()

    def test_pos(self):
        poses = wiktextract.PARTS_OF_SPEECH
        assert isinstance(poses, set)
        assert "noun" in poses
        assert "verb" in poses
        assert "pron" in poses
        assert "adj" in poses
        assert "adv" in poses
        assert "num" in poses
        assert len(poses) < 50

    def test_cv_plain(self):
        v = "This is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_comment(self):
        v = "This <!--comment--> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_unk(self):
        v = "This is a {{unknown-asdxfa}} test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_ref(self):
        v = "This <ref>junk\nmore junk</ref> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html(self):
        v = "This <thispurportstobeatag> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html2(self):
        v = "This </thispurportstobeatag> is a test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link1(self):
        v = "This is a [[test]]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link2(self):
        v = "This is a [[w:foo|test]]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link3(self):
        v = "This is a [[w:foo|]]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a foo.")

    def test_cv_link4(self):
        v = "This is a [[bar]]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a bar.")

    def test_cv_htmllink(self):
        v = "This is a [http://ylonen.org test]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q2(self):
        v = "This is a ''test''."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q3(self):
        v = "This is a '''test'''."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_nbsp(self):
        v = "This is a&nbsp;test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_gt(self):
        v = "This is a &lt;test&gt;."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a <test>.")

    def test_cv_gt(self):
        v = "This is a t\u2019est."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a t'est.")

    def test_cv_sp(self):
        v = "  This\nis \na\n   test.\t"
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_presp(self):
        v = " This : is a test . "
        v = clean_value(self.config, v)
        self.assertEqual(v, "This: is a test.")

    def test_cv_presp(self):
        v = " This ; is a test , "
        v = clean_value(self.config, v)
        self.assertEqual(v, "This; is a test,")

    def test_cv_excl(self):
        v = " Run !\n"
        v = clean_value(self.config, v)
        self.assertEqual(v, "Run!")

    def test_cv_ques(self):
        v = " Run ?\n"
        v = clean_value(self.config, v)
        self.assertEqual(v, "Run?")

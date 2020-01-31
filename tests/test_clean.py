import unittest
import collections
import wiktextract
from wiktextract.page import clean_value

class WiktExtractTests(unittest.TestCase):

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
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_comment(self):
        v = "This <!--comment--> is a test."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_repl0(self):
        v = "This is 1500 {{BC}}"
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is 1500 BC")

    def test_cv_repl1(self):
        v = "This is a {{given name|en|female}}"
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a female given name")

    def test_cv_repl1_arg1(self):
        v = "This is a {{given name|en|lang=fi|female}}"
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a female given name")

    def test_cv_repl1_arg2(self):
        v = "This is a {{given name|en|female|lang=fi}}"
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a female given name")

    def test_cv_repl1_surname(self):
        v = "This is a {{surname|from=nickname|lang=fi}}"
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a surname")

    def test_cv_repl1_taxon(self):
        v = "{{taxon|genus|family|Talpidae|[[insectivore]] mammals; typical [[mole]]s}}"
        v = clean_value("WORD", v)
        self.assertEqual(v, "taxonomic genus")

    def test_cv_arg1(self):
        v = "This is a {{w|test}}."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_arg2(self):
        v = "This is a {{w|test article|test value}}."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test value.")

    def test_cv_arg3(self):
        v = "This is a {{w2|fi||test}}."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_arg_nest(self):
        v = "This is a {{w2|fi||{{given name|en|male}}}}."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a male given name.")

    def test_cv_unk(self):
        v = "This is a {{unknown-asdxfa}} test."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_ref(self):
        v = "This <ref>junk\nmore junk</ref> is a test."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html(self):
        v = "This <thispurportstobeatag> is a test."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html2(self):
        v = "This </thispurportstobeatag> is a test."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link1(self):
        v = "This is a [[test]]."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link2(self):
        v = "This is a [[w:foo|test]]."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_htmllink(self):
        v = "This is a [http://ylonen.org test]."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q2(self):
        v = "This is a ''test''."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q3(self):
        v = "This is a '''test'''."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_nbsp(self):
        v = "This is a&nbsp;test."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_gt(self):
        v = "This is a &lt;test&gt;."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a <test>.")

    def test_cv_gt(self):
        v = "This is a t\u2019est."
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a t'est.")

    def test_cv_sp(self):
        v = "  This\nis \na\n   test.\t"
        v = clean_value("WORD", v)
        self.assertEqual(v, "This is a test.")

    def test_cv_presp(self):
        v = " This : is a test . "
        v = clean_value("WORD", v)
        self.assertEqual(v, "This: is a test.")

    def test_cv_presp(self):
        v = " This ; is a test , "
        v = clean_value("WORD", v)
        self.assertEqual(v, "This; is a test,")

    def test_cv_excl(self):
        v = " Run !\n"
        v = clean_value("WORD", v)
        self.assertEqual(v, "Run!")

    def test_cv_ques(self):
        v = " Run ?\n"
        v = clean_value("WORD", v)
        self.assertEqual(v, "Run?")

    def test_cv_nested1(self):
        v = "{{acronym of|es|{{w|Geroa Bai|lang=es}}}}"
        v = clean_value("WORD", v)
        self.assertEqual(v, "acronym of Geroa Bai")

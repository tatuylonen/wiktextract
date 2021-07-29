import unittest
import collections
import wiktextract
from wiktextract.clean import clean_value
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

    def test_cv_unk1(self):
        # We no longer clean unknown templates
        v = "This is a {{unknown-asdxfa}} test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a {{unknown-asdxfa}} test.")

    def test_cv_unk(self):
        # We no longer clean unknown template arguments
        v = "This is a {{{1}}} test."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a {{{1}}} test.")

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

    def test_cv_link5(self):
        v = "([[w:Jurchen script|Jurchen script]]: , Image: [[FIle:Da (Jurchen script).png|25px]])"
        v = clean_value(self.config, v)
        self.assertEqual(v, "(Jurchen script: , Image: )")

    def test_cv_url1(self):
        v = "This is a [http://ylonen.org test]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test.")

    def test_cv_url2(self):
        v = "This is a [http://ylonen.org test1 test2]."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a test1 test2.")

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

    def test_cv_unicode_apostrophe(self):
        v = "This is a t\u2019est."
        v = clean_value(self.config, v)
        self.assertEqual(v, "This is a t\u2019est.")

    def test_cv_sp(self):
        v = "  This\nis \na\n   test.\t"
        v = clean_value(self.config, v)
        # The code has been changed to keep newlines
        self.assertEqual(v, "This\nis\na\n test.")

    def test_cv_presp(self):
        v = " This : is a test . "
        v = clean_value(self.config, v)
        self.assertEqual(v, "This: is a test.")

    def test_cv_presp(self):
        v = " This ; is a test , "
        v = clean_value(self.config, v)
        self.assertEqual(v, "This ; is a test ,")

    def test_cv_excl(self):
        v = " Run !\n"
        v = clean_value(self.config, v)
        self.assertEqual(v, "Run !")

    def test_cv_ques(self):
        v = " Run ?\n"
        v = clean_value(self.config, v)
        self.assertEqual(v, "Run ?")

    def test_cv_math1(self):
        v = r"foo <math>a \times \zeta = c</math> bar"
        v = clean_value(self.config, v)
        self.assertEqual(v, "foo a⨯𝜁=c bar")

    def test_cv_math2(self):
        v = r"<math>\frac{a}{b + c}</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "a/(b+c)")

    def test_cv_math3(self):
        v = r"<math>\frac{a + 1}{b + c}</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "(a+1)/(b+c)")

    def test_cv_math4(self):
        v = r"<math>\frac\alpha\beta</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "𝛼/𝛽")

    def test_cv_math5(self):
        v = r"<math>{\mathfrak A} - {\mathbb B} \cup {\mathcal K}</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "𝔄-𝔹∪𝒦")

    def test_cv_math6(self):
        v = r"<math>\sum_{i=0}^100 1/i</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "∑ᵢ₌₀¹⁰⁰1/i")

    def test_cv_math7(self):
        v = r"<math>x^\infty</math>"
        v = clean_value(self.config, v)
        print(ascii(v))
        self.assertEqual(v, "x\u2002᪲")

    def test_cv_math8(self):
        v = r"<math>4 7</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "4 7")

    def test_cv_math9(self):
        v = r"<math>a x + b</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "ax+b")

    def test_cv_math9(self):
        v = r"<math>4^7</math>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "4⁷")

    def test_cv_sup1(self):
        v = r"x<sup>3</sup>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "x³")

    def test_cv_sub1(self):
        v = r"x<sub>3</sub>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "x₃")

    def test_cv_chem1(self):
        v = r"<chem>H2O</chem>"
        v = clean_value(self.config, v)
        self.assertEqual(v, "H₂O")

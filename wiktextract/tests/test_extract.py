import unittest
import collections
import wiktextract
from wiktextract import wiktionary

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
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_comment(self):
        v = "This <!--comment--> is a test."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_repl0(self):
        v = "This is 1500 {{BC}}"
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is 1500 BC")

    def test_cv_repl1(self):
        v = "This is a {{given name|female}}"
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a female given name")

    def test_cv_arg1(self):
        v = "This is a {{w|test}}."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_arg2(self):
        v = "This is a {{w|test article|test value}}."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test value.")

    def test_cv_arg3(self):
        v = "This is a {{w2|fi||test}}."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_arg_nest(self):
        v = "This is a {{w2|fi||{{given name|male}}}}."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a male given name.")

    def test_cv_unk(self):
        v = "This is a {{unknown-asdxfa}} test."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_ref(self):
        v = "This <ref>junk\nmore junk</ref> is a test."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html(self):
        v = "This <thispurportstobeatag> is a test."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_html2(self):
        v = "This </thispurportstobeatag> is a test."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link1(self):
        v = "This is a [[test]]."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_link2(self):
        v = "This is a [[w:foo|test]]."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_htmllink(self):
        v = "This is a [http://ylonen.org test]."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q2(self):
        v = "This is a ''test''."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_q3(self):
        v = "This is a '''test'''."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_nbsp(self):
        v = "This is a&nbsp;test."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_gt(self):
        v = "This is a &lt;test&gt;."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a <test>.")

    def test_cv_gt(self):
        v = "This is a t\u2019est."
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a t'est.")

    def test_cv_sp(self):
        v = "  This\nis \na\n   test.\t"
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This is a test.")

    def test_cv_presp(self):
        v = " This : is a test . "
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This: is a test.")

    def test_cv_presp(self):
        v = " This ; is a test , "
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "This; is a test,")

    def test_cv_excl(self):
        v = " Run !\n"
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "Run!")

    def test_cv_ques(self):
        v = " Run ?\n"
        v = wiktionary.clean_value(v)
        self.assertEqual(v, "Run?")

    def test_all(self):
        # Just parse through the data and make sure that we find some words

        langs = collections.defaultdict(int)
        words = collections.defaultdict(int)
        poses = collections.defaultdict(int)
        num_transl = 0
        num_pron = 0
        num_conj = 0
        num_redirects = 0

        def word_cb(data):
            nonlocal num_transl
            nonlocal num_pron
            nonlocal num_conj
            nonlocal num_redirects
            word = data["word"]
            assert word
            words[word] += 1
            if "redirect" in data:
                assert isinstance(data["redirect"], str)
                num_redirects += 1
                return
            lang = data["lang"]
            pos = data["pos"]
            assert word and lang and pos
            langs[lang] += 1
            poses[pos] += 1
            if data.get("conjugation"):
                num_conj += 1
            if data.get("translations"):
                num_transl += 1
            sounds = data.get("pronunciations", ())
            if sounds and any("ipa" in x for x in sounds):
                num_pron += 1

        path = "wiktextract/tests/test-pages-articles.xml.bz2"
        print("Parsing test data")
        wiktextract.parse_wiktionary(path, word_cb,
                                     languages=["English", "Finnish",
                                                "Translingual"],
                                     translations=True,
                                     pronunciations=True,
                                     linkages=True,
                                     compounds=True,
                                     redirects=True)
        print("Test data parsing complete")
        assert num_redirects > 0
        assert len(words) > 100
        assert all(x < 50 for x in words.values())
        assert langs["English"] > 0
        assert langs["Finnish"] > 0
        assert langs["Translingual"] > 0
        assert len(langs.keys()) == 3
        assert len(poses.keys()) <= len(wiktextract.PARTS_OF_SPEECH)
        assert sum(poses.values()) == sum(langs.values())
        assert sum(words.values()) == sum(poses.values()) + num_redirects
        assert num_conj > 0
        assert num_transl > 0
        assert num_pron > 0

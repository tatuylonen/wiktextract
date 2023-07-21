import collections
import unittest

from wiktextract.config import WiktionaryConfig
from wiktextract.wiktionary import parse_wiktionary
from wiktextract.wxr_context import WiktextractContext
from wiktextract.thesaurus import close_thesaurus_db, search_thesaurus
from wikitextprocessor import Wtp


class LongTests(unittest.TestCase):
    def test_long(self):
        # Just parse through the data and make sure that we find some words
        # This takes about 0.5 minutes.

        langs = collections.defaultdict(int)
        words = collections.defaultdict(int)
        poses = collections.defaultdict(int)
        num_transl = 0
        num_redirects = 0

        def word_cb(data):
            nonlocal num_transl
            nonlocal num_redirects
            if "redirect" in data:
                assert isinstance(data["redirect"], str)
                word = data["title"]
                words[word] += 1
                num_redirects += 1
                return
            word = data["word"]
            assert word
            words[word] += 1
            lang = data["lang"]
            pos = data["pos"]
            assert word and lang and pos
            langs[lang] += 1
            poses[pos] += 1
            if data.get("translations"):
                num_transl += 1
            for sense in data.get("senses", ()):
                if sense.get("translations"):
                    num_transl += 1

        path = "tests/test-pages-articles.xml.bz2"
        print("Parsing test data")
        conf1 = WiktionaryConfig(
            dump_file_lang_code="en",
            capture_language_codes=[
                "en",
                "fi",
                "es",
                "de",
                "zh",
                "ja",
                "it",
                "pt",
                "mul",
            ],
            capture_translations=True,
            capture_pronunciation=True,
            capture_linkages=True,
            capture_compounds=True,
            capture_redirects=True,
        )
        wxr = WiktextractContext(Wtp(), conf1)
        parse_wiktionary(
            wxr, path, word_cb, False, False, {0, 4, 10, 14, 100, 110, 118, 828}
        )
        print("Test data parsing complete")
        self.assertGreater(num_redirects, 0)
        self.assertGreater(len(words), 100)
        self.assertTrue(all(x < 50 for x in words.values()))
        self.assertGreater(langs["English"], 0)
        self.assertGreater(langs["Finnish"], 0)
        self.assertGreater(langs["Translingual"], 0)
        self.assertEqual(len(langs.keys()), 9)
        self.assertLessEqual(len(poses.keys()), len(wxr.config.POS_TYPES))
        self.assertEqual(sum(poses.values()), sum(langs.values()))
        self.assertEqual(
            sum(words.values()), sum(poses.values()) + num_redirects
        )
        self.assertGreater(num_transl, 0)
        thesaurus_data = [data for data in search_thesaurus(
            wxr.thesaurus_db_conn, "hieno", "fi", "adj"
        )]
        self.assertEqual(len(thesaurus_data), 17)
        wxr.wtp.close_db_conn()
        close_thesaurus_db(wxr.thesaurus_db_path, wxr.thesaurus_db_conn)

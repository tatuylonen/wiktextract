import collections
import json
import logging
import tempfile
import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.thesaurus import close_thesaurus_db, search_thesaurus
from wiktextract.wiktionary import parse_wiktionary
from wiktextract.wxr_context import WiktextractContext


class LongTests(unittest.TestCase):
    def setUp(self):
        conf = WiktionaryConfig(
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
        self.wxr = WiktextractContext(Wtp(), conf)

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_long(self):
        # Just parse through the data and make sure that we find some words
        # This takes about 0.5 minutes.
        langs = collections.defaultdict(int)
        words = collections.defaultdict(int)
        poses = collections.defaultdict(int)
        num_transl = 0
        num_redirects = 0

        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as f:
            print("Parsing test data")
            parse_wiktionary(
                self.wxr,
                "tests/test-pages-articles.xml.bz2",
                None,
                False,
                {0, 4, 10, 14, 100, 110, 118, 828},
                f,
                False,
            )
            print("Test data parsing complete")
            f.seek(0)
            for line in f:
                data = json.loads(line)
                if "redirect" in data:
                    self.assertTrue(isinstance(data["redirect"], str))
                    word = data["title"]
                    words[word] += 1
                    num_redirects += 1
                    continue
                word = data.get("word", "")
                self.assertGreater(len(word), 0)
                words[word] += 1
                lang = data.get("lang", "")
                self.assertGreater(len(lang), 0)
                pos = data.get("pos", "")
                self.assertGreater(len(pos), 0)
                langs[lang] += 1
                poses[pos] += 1
                if data.get("translations"):
                    num_transl += 1
                for sense in data.get("senses", ()):
                    if sense.get("translations"):
                        num_transl += 1

        self.assertEqual(num_redirects, 6)
        self.assertGreater(len(words), 100)
        self.assertTrue(all(x < 50 for x in words.values()))
        self.assertGreater(langs["English"], 0)
        self.assertGreater(langs["Finnish"], 0)
        self.assertGreater(langs["Translingual"], 0)
        self.assertEqual(len(langs.keys()), 9)
        self.assertLessEqual(len(poses.keys()), len(self.wxr.config.POS_TYPES))
        self.assertEqual(sum(poses.values()), sum(langs.values()))
        self.assertEqual(
            sum(words.values()), sum(poses.values()) + num_redirects
        )
        self.assertGreater(num_transl, 0)
        thesaurus_data = [
            data
            for data in search_thesaurus(
                self.wxr.thesaurus_db_conn, "hieno", "fi", "adj"
            )
        ]
        self.assertEqual(len(thesaurus_data), 17)

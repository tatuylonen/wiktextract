import unittest
import collections
import wiktextract
from wiktextract.wiktionary import WiktionaryConfig, parse_wiktionary
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
        ctx = Wtp()
        config = WiktionaryConfig(capture_languages=["English", "Finnish",
                                                     "Spanish", "German",
                                                     "Chinese", "Japanese",
                                                     "Italian", "Portuguese",
                                                     "Translingual"],
                                  capture_translations=True,
                                  capture_pronunciation=True,
                                  capture_linkages=True,
                                  capture_compounds=True,
                                  capture_redirects=True)
        parse_wiktionary(ctx, path, config, word_cb, None, False, False)
        print("Test data parsing complete")
        assert num_redirects > 0
        assert len(words) > 100
        assert all(x < 50 for x in words.values())
        assert langs["English"] > 0
        assert langs["Finnish"] > 0
        assert langs["Translingual"] > 0
        assert len(langs.keys()) == 9
        assert len(poses.keys()) <= len(wiktextract.PARTS_OF_SPEECH)
        assert sum(poses.values()) == sum(langs.values())
        assert sum(words.values()) == sum(poses.values()) + num_redirects
        assert num_transl > 0

import unittest
from collections import defaultdict

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.pronunciation import extract_pronunciation
from wiktextract.wxr_context import WiktextractContext


class TestPronunciation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_pron_list(self):
        page_data = [
            defaultdict(list, {"lang_code": "en"}),
            defaultdict(list, {"lang_code": "fr"}),
            defaultdict(list, {"lang_code": "fr"}),
        ]
        self.wxr.wtp.add_page("Modèle:pron", 10, body="\\bɔ̃.ʒuʁ\\")
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            "=== Prononciation ===\n* {{pron|bɔ̃.ʒuʁ|fr}}\n** {{écouter|France (Paris)|bõ.ʒuːʁ|audio=Fr-bonjour.ogg|lang=fr}}"
        )
        extract_pronunciation(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data,
            [
                {"lang_code": "en"},
                {
                    "lang_code": "fr",
                    "sounds": [
                        {
                            "ipa": "bõ.ʒuːʁ",
                            "tags": ["France (Paris)"],
                            "audio": "Fr-bonjour.ogg",
                            "ogg_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Fr-bonjour.ogg",
                            "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/b/bc/Fr-bonjour.ogg/Fr-bonjour.ogg.mp3",
                        }
                    ],
                },
                {
                    "lang_code": "fr",
                    "sounds": [
                        {
                            "ipa": "bõ.ʒuːʁ",
                            "tags": ["France (Paris)"],
                            "audio": "Fr-bonjour.ogg",
                            "ogg_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Fr-bonjour.ogg",
                            "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/b/bc/Fr-bonjour.ogg/Fr-bonjour.ogg.mp3",
                        }
                    ],
                },
            ],
        )

    def test_str_pron(self):
        page_data = [defaultdict(list, {"lang_code": "zh"})]
        self.wxr.wtp.add_page("Modèle:Yale-zh", 10, body="Yale")
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            "=== {{S|prononciation}} ===\n* '''cantonais''' {{pron||yue}}\n** {{Yale-zh}} : nei⁵hou²"
        )
        extract_pronunciation(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data[0].get("sounds"),
            [{"tags": ["cantonais", "Yale"], "zh-pron": "nei⁵hou²"}],
        )

    def test_no_ipa(self):
        """
        The pronunciation block could have no IPA data but contain some audio
        files.
        Test wikitext from https://fr.wiktionary.org/wiki/mars
        """
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            """=== {{S|prononciation}} ===
{{ébauche-pron|sv}}
* {{écouter|lang=sv|Suède||audio=LL-Q9027 (swe)-Moonhouse-mars.wav}}"""
        )
        extract_pronunciation(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data[0].get("sounds"),
            [
                {
                    "tags": ["Suède"],
                    "audio": "LL-Q9027 (swe)-Moonhouse-mars.wav",
                    "wav_url": "https://commons.wikimedia.org/wiki/Special:FilePath/LL-Q9027 (swe)-Moonhouse-mars.wav",
                    "ogg_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/3/3f/LL-Q9027_(swe)-Moonhouse-mars.wav/LL-Q9027_(swe)-Moonhouse-mars.wav.ogg",
                    "mp3_url": "https://upload.wikimedia.org/wikipedia/commons/transcoded/3/3f/LL-Q9027_(swe)-Moonhouse-mars.wav/LL-Q9027_(swe)-Moonhouse-mars.wav.mp3",
                }
            ],
        )

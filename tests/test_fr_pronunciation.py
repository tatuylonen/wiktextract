import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.pronunciation import extract_pronunciation
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestPronunciation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    @patch(
        "wiktextract.extractor.fr.pronunciation.clean_node",
        return_value="\\bɔ̃.ʒuʁ\\",
    )
    def test_pron_list(self, mock_clean_node):
        page_data = [
            defaultdict(list, {"lang_code": "en"}),
            defaultdict(list, {"lang_code": "fr"}),
            defaultdict(list, {"lang_code": "fr"}),
        ]
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            "=== Prononciation  ===\n* {{pron|bɔ̃.ʒuʁ|fr}}\n** {{écouter|France (Paris)|bõ.ʒuːʁ|audio=Fr-bonjour.ogg|lang=fr}}"
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

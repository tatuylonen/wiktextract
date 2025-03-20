from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ms"),
            WiktionaryConfig(
                dump_file_lang_code="ms", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_pos_title(self):
        page_data = parse_page(
            self.wxr,
            "dance",
            """== Bahasa Inggeris ==
=== Takrifan ===
==== Kata nama ====
# [[tarian]]
==== Kata kerja ====
# [[menari]], [[tari]]""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "lang": "Bahasa Inggeris",
                    "lang_code": "en",
                    "pos": "noun",
                    "pos_title": "Kata nama",
                    "senses": [{"glosses": ["tarian"]}],
                    "word": "dance",
                },
                {
                    "lang": "Bahasa Inggeris",
                    "lang_code": "en",
                    "pos": "verb",
                    "pos_title": "Kata kerja",
                    "senses": [{"glosses": ["menari, tari"]}],
                    "word": "dance",
                },
            ],
        )

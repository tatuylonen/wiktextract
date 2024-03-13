from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext


class TestEnCategory(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"), WiktionaryConfig(dump_file_lang_code="en")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_filter_language_categories(self):
        # GH issue #537
        from wiktextract.page import process_categories

        page_data = [
            {
                "categories": [
                    "Rhymes:Afrikaans/als",
                    "English phrasal verbs",
                    "A'ou language",
                ],
                "lang_code": "en",
                "lang": "English",
            }
        ]
        process_categories(self.wxr, page_data)
        self.assertEqual(page_data[0]["categories"], ["English phrasal verbs"])

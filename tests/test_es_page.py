import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.models import WordEntry
from wiktextract.extractor.es.page import parse_entries
from wiktextract.wxr_context import WiktextractContext


class TestESPage(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_page_data(self) -> list[WordEntry]:
        return [WordEntry(word="test", lang_code="es", lang_name="Language")]

    def test_es_parse_entries(self):
        """
        Writes data affecting multiple entries to all affected WordEntry objects.
        """
        self.wxr.wtp.start_page("love")

        # https://es.wiktionary.org/wiki/love
        root = self.wxr.wtp.parse(
            """== {{lengua|en}} ==
{{pron-graf|leng=en|fone=lʌv}}
=== {{verbo|en}} ===
=== {{sustantivo|en}} ===
"""
        )

        base_data = self.get_default_page_data()[0]
        page_data = []

        parse_entries(self.wxr, page_data, base_data, root.children[0])

        self.assertEqual(len(page_data), 2)

        self.assertEqual(page_data[0].sounds, page_data[1].sounds)

        self.assertNotEqual(
            page_data[0].sounds,
            base_data.sounds,
        )

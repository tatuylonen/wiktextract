import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.note import extract_note
from wiktextract.wxr_context import WiktextractContext


class TestNotes(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_list_notes(self):
        # list created from template "note-féminisation"
        # https://fr.wiktionary.org/wiki/autrice
        self.wxr.wtp.add_page(
            "Modèle:note-féminisation", 10, "* list 1\n* list 2"
        )
        self.wxr.wtp.start_page("autrice")
        nodes = self.wxr.wtp.parse(
            """==== {{S|notes}} ====
paragrapy 1
{{note-féminisation}}"""
        )
        page_data = [defaultdict(list)]
        extract_note(self.wxr, page_data, nodes.children[0])
        self.assertEqual(
            page_data, [{"notes": ["paragrapy 1", "list 1", "list 2"]}]
        )

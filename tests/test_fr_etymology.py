import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.page import extract_etymology
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestEtymology(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_ebauche_etym(self):
        # https://fr.wiktionary.org/wiki/Hörsaal
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(": {{ébauche-étym|de}}")
        base_data = defaultdict(list, {"lang_code": "de"})
        page_data = [base_data]
        extract_etymology(self.wxr, page_data, base_data, root.children)
        self.assertEqual(page_data, [{"lang_code": "de"}])

import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.linkage import extract_linkage
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_tags(self):
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:Canada", 10, body="(Canada)")
        self.wxr.wtp.add_page("Modèle:Louisiane", 10, body="(Louisiane)")
        root = self.wxr.wtp.parse(
            "==== {{S|synonymes}} ====\n* [[bon matin]] {{Canada|nocat=1}} {{Louisiane|nocat=1}}"
        )
        extract_linkage(self.wxr, page_data, root.children[0], "synonyms")
        self.assertEqual(
            page_data,
            [
                {
                    "synonyms": [
                        {"word": "bon matin", "tags": ["Canada", "Louisiane"]}
                    ]
                }
            ],
        )

    def test_zh_synonyms(self):
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            "==== {{S|synonymes}} ====\n* {{zh-lien|你们好|nǐmen hǎo|你們好}} — Bonjour (au pluriel)."
        )
        extract_linkage(self.wxr, page_data, root.children[0], "synonyms")
        self.assertEqual(
            page_data,
            [
                {
                    "synonyms": [
                        {
                            "word": "你们好",
                            "roman": "nǐmen hǎo",
                            "alt": "你們好",
                            "translation": "Bonjour (au pluriel).",
                        }
                    ]
                }
            ],
        )

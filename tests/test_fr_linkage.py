import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.linkage import extract_linkage
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_tags(self):
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:Canada", 10, body="(Canada)")
        self.wxr.wtp.add_page("Modèle:Louisiane", 10, body="(Louisiane)")
        root = self.wxr.wtp.parse(
            "* [[bon matin]] {{Canada|nocat=1}} {{Louisiane|nocat=1}}"
        )
        extract_linkage(self.wxr, page_data, root, "synonyms")
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
        self.wxr.wtp.start_page("你好")
        root = self.wxr.wtp.parse(
            "* {{zh-lien|你们好|nǐmen hǎo|你們好}} — Bonjour (au pluriel)."
        )
        extract_linkage(self.wxr, page_data, root, "synonyms")
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

    def test_template_as_partial_tag(self):
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:lien", 10, body="kwei")
        self.wxr.wtp.add_page("Modèle:Canada", 10, body="(Canada)")
        self.wxr.wtp.add_page("Modèle:L", 10, body="Atikamekw")
        root = self.wxr.wtp.parse(
            "* {{lien|kwei|fr}} {{Canada|nocat=1}} (mot {{L|atj}})"
        )
        extract_linkage(self.wxr, page_data, root, "synonyms")
        self.assertEqual(
            page_data,
            [
                {
                    "synonyms": [
                        {"word": "kwei", "tags": ["Canada", "mot Atikamekw"]}
                    ]
                }
            ],
        )

    def test_list_item_has_two_words(self):
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("masse")
        root = self.wxr.wtp.parse(
            "* [[être à la masse]], [[mettre à la masse]]"
        )
        extract_linkage(self.wxr, page_data, root, "derived")
        self.assertEqual(
            page_data,
            [
                {
                    "derived": [
                        {"word": "être à la masse"},
                        {"word": "mettre à la masse"},
                    ]
                }
            ],
        )

    def test_sub_list(self):
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("lézard ocellé")
        root = self.wxr.wtp.parse(
            """* [[saurien]]s (Sauria)
** [[lacertidé]]s (Lacertidae) (famille des lézards typiques)
"""
        )
        extract_linkage(self.wxr, page_data, root, "hypernyms")
        self.assertEqual(
            page_data,
            [
                {
                    "hypernyms": [
                        {"tags": ["Sauria"], "word": "sauriens"},
                        {
                            "tags": [
                                "Lacertidae",
                                "famille des lézards typiques",
                            ],
                            "word": "lacertidés",
                        },
                    ]
                }
            ],
        )

    def test_sense(self):
        page_data = [defaultdict(list)]
        self.wxr.wtp.start_page("autrice")
        root = self.wxr.wtp.parse(
            """{{(|Celle qui est à l’origine de quelque chose|1}}
* [[artisane]]
"""
        )
        extract_linkage(self.wxr, page_data, root, "synonyms")
        self.assertEqual(
            page_data,
            [
                {
                    "synonyms": [
                        {
                            "word": "artisane",
                            "sense": "Celle qui est à l’origine de quelque chose",
                            "sense_index": 1,
                        },
                    ]
                }
            ],
        )

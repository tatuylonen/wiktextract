import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.gloss import extract_glosses
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestGlossList(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_de_extract_glosses(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(":[1] gloss1 \n:[2] gloss2")

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root.children[0])

        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "glosses": ["gloss1"],
                        },
                        {
                            "glosses": ["gloss2"],
                        },
                    ]
                }
            ],
        )

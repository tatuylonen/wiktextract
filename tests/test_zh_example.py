import unittest

from unittest.mock import patch

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.extractor.zh.example import extract_examples
from wiktextract.thesaurus import close_thesaurus_db


class TestExample(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"), WiktionaryConfig(dump_file_lang_code="zh")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_example_list(self) -> None:
        page_data = [
            {
                "lang": "跨語言",
                "lang_code": "mul",
                "word": "%",
                "senses": [{"glosses": ["百分比"]}],
            }
        ]
        wikitext = """
#* ref text
#*: example text
        """
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, page_data, node)
        self.assertEqual(
            page_data[0]["senses"][0].get("examples"),
            [
                {"ref": "ref text", "text": "example text", "type": "quote"},
            ],
        )

    @patch(
        "wiktextract.extractor.zh.example.clean_node",
        return_value="""ref text
quote text
translation text""",
    )
    def test_quote_example(self, mock_clean_node) -> None:
        page_data = [
            {
                "lang": "跨語言",
                "lang_code": "mul",
                "word": "%",
                "senses": [{"glosses": ["百分比"]}],
            }
        ]
        wikitext = "#* {{RQ:Schuster Hepaticae}}"
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, page_data, node)
        self.assertEqual(
            page_data[0]["senses"][0].get("examples"),
            [
                {
                    "ref": "ref text",
                    "text": "quote text",
                    "translation": "translation text",
                    "type": "quote",
                },
            ],
        )

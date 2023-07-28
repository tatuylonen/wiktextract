import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.example import extract_examples
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


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
        sense_data = {}
        wikitext = """
#* ref text
#*: example text
        """
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, sense_data, node)
        self.assertEqual(
            sense_data.get("examples"),
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
        sense_data = defaultdict(list)
        wikitext = "#* {{RQ:Schuster Hepaticae}}"
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, sense_data, node)
        self.assertEqual(
            sense_data.get("examples"),
            [
                {
                    "ref": "ref text",
                    "text": "quote text",
                    "translation": "translation text",
                    "type": "quote",
                },
            ],
        )

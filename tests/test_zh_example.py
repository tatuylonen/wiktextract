import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.extractor.zh.example import extract_examples


class TestExample(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"), WiktionaryConfig(dump_file_lang_code="zh")
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_example_list(self):
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

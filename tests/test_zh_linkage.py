import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.extractor.zh.linkage import extract_linkages


class TestLinkage(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"), WiktionaryConfig(dump_file_lang_code="zh")
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_sense_term_list(self):
        page_data = [
            {
                "lang": "跨語言",
                "lang_code": "mul",
                "word": "%",
                "senses": [{"glosses": ["百分比"]}],
            }
        ]
        wikitext = "* {{sense|百分比}} {{l|mul|cU}}、[[centiuno]]"
        self.wxr.wtp.add_page("Template:Sense", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Template:L", 10, "{{{2}}}")
        self.wxr.wtp.db_conn.commit()
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_linkages(self.wxr, page_data, node.children, "synonyms", None)
        self.assertEqual(
            page_data[0]["senses"][0].get("synonyms"),
            [
                {"sense": "百分比", "word": "cU"},
                {"sense": "百分比", "word": "centiuno"},
            ],
        )

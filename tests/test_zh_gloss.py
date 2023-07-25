import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.extractor.zh.page import extract_gloss
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
                "lang": "日語",
                "lang_code": "ja",
                "word": "可笑しい",
                "senses": [],
            }
        ]
        wikitext = """# [[好玩]]的：
## 有趣的，滑稽的，可笑的
## 奇怪的，不正常的
## 不合理的，不合邏輯的
# (棄用) [[有趣]]的：
## [[有趣]]的
## [[美味]]的
## [[漂亮]]的
## [[很好]]的，[[卓越]]的"""
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_gloss(self.wxr, page_data, node.children[0], {})
        self.assertEqual(
            page_data[0]["senses"],
            [
                {"glosses": ["好玩的：", "有趣的，滑稽的，可笑的"]},
                {"glosses": ["好玩的：", "奇怪的，不正常的"]},
                {"glosses": ["好玩的：", "不合理的，不合邏輯的"]},
                {
                    "glosses": ["有趣的：", "有趣的"],
                    "raw_glosses": ["(棄用) 有趣的："],
                    "tags": ["棄用"],
                },
                {
                    "glosses": ["有趣的：", "美味的"],
                    "raw_glosses": ["(棄用) 有趣的："],
                    "tags": ["棄用"],
                },
                {
                    "glosses": ["有趣的：", "漂亮的"],
                    "raw_glosses": ["(棄用) 有趣的："],
                    "tags": ["棄用"],
                },
                {
                    "glosses": ["有趣的：", "很好的，卓越的"],
                    "raw_glosses": ["(棄用) 有趣的："],
                    "tags": ["棄用"],
                },
            ],
        )

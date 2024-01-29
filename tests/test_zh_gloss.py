from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import NodeKind, WikiNode, Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.models import Sense, WordEntry
from wiktextract.extractor.zh.page import (
    extract_gloss,
    parse_page,
    parse_section,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestExample(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"),
            WiktionaryConfig(
                capture_language_codes=None, dump_file_lang_code="zh"
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_example_list(self) -> None:
        page_data = [
            WordEntry(
                lang="日語",
                lang_code="ja",
                word="可笑しい",
            )
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
        extract_gloss(self.wxr, page_data, node.children[0], Sense())
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in page_data[0].senses],
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

    @patch("wiktextract.extractor.zh.page.process_pos_block")
    @patch("wiktextract.extractor.zh.page.clean_node", return_value="名詞1")
    def test_pos_title_number(
        self,
        mock_clean_node,
        mock_process_pos_block,
    ) -> None:
        node = WikiNode(NodeKind.LEVEL3, 0)
        base_data = WordEntry(word="", lang_code="", lang="")
        parse_section(self.wxr, [base_data], base_data, node)
        mock_process_pos_block.assert_called()

    @patch("wiktextract.extractor.zh.page.process_pos_block")
    @patch(
        "wiktextract.extractor.zh.page.clean_node", return_value="名詞（一）"
    )
    def test_pos_title_chinese_numeral(
        self,
        mock_clean_node,
        mock_process_pos_block,
    ) -> None:
        node = WikiNode(NodeKind.LEVEL3, 0)
        base_data = WordEntry(word="", lang_code="", lang="")
        parse_section(self.wxr, [base_data], base_data, node)
        mock_process_pos_block.assert_called()

    def test_soft_redirect_zh_see(self):
        self.assertEqual(
            parse_page(
                self.wxr,
                "別个",
                """==漢語==
{{zh-see|別個}}""",
            ),
            [
                {
                    "lang": "漢語",
                    "lang_code": "zh",
                    "redirects": ["別個"],
                    "word": "別个",
                }
            ],
        )

    def test_soft_redirect_ja_see(self):
        self.assertEqual(
            parse_page(
                self.wxr,
                "きさらぎ",
                """==日語==
{{ja-see|如月|二月|更衣|衣更着}}""",
            ),
            [
                {
                    "lang": "日語",
                    "lang_code": "ja",
                    "redirects": ["如月", "二月", "更衣", "衣更着"],
                    "word": "きさらぎ",
                }
            ],
        )

    def test_gloss_text_only_page(self):
        self.assertEqual(
            parse_page(
                self.wxr,
                "paraphrase",
                """== 英语 ==
释义；意译""",
            ),
            [
                {
                    "lang": "英语",
                    "lang_code": "en",
                    "senses": [{"glosses": ["释义；意译"]}],
                    "word": "paraphrase",
                }
            ],
        )

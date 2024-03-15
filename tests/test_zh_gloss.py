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


class TestGloss(TestCase):
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
                pos="adj",
            )
        ]
        wikitext = """# [[好玩]]的：
## 有趣的，滑稽的，可笑的
## 奇怪的，不正常的
## 不合理的，不合邏輯的
# {{lb|ja|棄用}} [[有趣]]的：
## [[有趣]]的
## [[美味]]的
## [[漂亮]]的
## [[很好]]的，[[卓越]]的"""
        self.wxr.wtp.start_page("可笑しい")
        self.wxr.wtp.add_page("Template:lb", 10, "({{{2|}}})")
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
                    "tags": ["obsolete"],
                },
                {
                    "glosses": ["有趣的：", "美味的"],
                    "tags": ["obsolete"],
                },
                {
                    "glosses": ["有趣的：", "漂亮的"],
                    "tags": ["obsolete"],
                },
                {
                    "glosses": ["有趣的：", "很好的，卓越的"],
                    "tags": ["obsolete"],
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
        base_data = WordEntry(word="", lang_code="", lang="", pos="")
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
        base_data = WordEntry(word="", lang_code="", lang="", pos="")
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
                    "pos": "soft-redirect",
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
                    "pos": "soft-redirect",
                    "redirects": ["如月", "二月", "更衣", "衣更着"],
                    "word": "きさらぎ",
                }
            ],
        )

    def test_gloss_text_only_page(self):
        # title, page wikitext, results
        test_cases = [
            [
                "paraphrase",
                "== 英语 ==\n释义；意译",
                [
                    {
                        "lang": "英语",
                        "lang_code": "en",
                        "pos": "unknown",
                        "senses": [{"glosses": ["释义；意译"]}],
                        "word": "paraphrase",
                    }
                ],
            ],
            [
                "鐵面無私",
                "==漢語==\n===釋義===\n形容[[公正]]严明，绝不因[[徇私]]或畏权而讲情面。",
                [
                    {
                        "lang": "漢語",
                        "lang_code": "zh",
                        "pos": "unknown",
                        "senses": [
                            {
                                "glosses": [
                                    "形容公正严明，绝不因徇私或畏权而讲情面。"
                                ]
                            }
                        ],
                        "word": "鐵面無私",
                    }
                ],
            ],
        ]
        for title, wikitext, results in test_cases:
            with self.subTest(title=title, wikitext=wikitext, results=results):
                self.assertEqual(
                    parse_page(self.wxr, title, wikitext),
                    results,
                )

    def test_gloss_template(self):
        self.wxr.wtp.start_page("CC")
        self.wxr.wtp.add_page("Template:n-g", 10, "{{{1|}}}")
        root = self.wxr.wtp.parse(
            "# {{n-g|[[ISO]] 3166-1 對科科斯群島（[[Cocos Islands]]）的兩字母代碼。}}"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "glosses": [
                        "ISO 3166-1 對科科斯群島（Cocos Islands）的兩字母代碼。"
                    ]
                }
            ],
        )

    def test_gloss_lable_topic(self):
        self.wxr.wtp.start_page("DC")
        self.wxr.wtp.add_page("Template:lb", 10, "(航空学)")
        root = self.wxr.wtp.parse(
            "# {{lb|en|aviation}} 道格拉斯飞行器公司的產品名稱"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "glosses": ["道格拉斯飞行器公司的產品名稱"],
                    "topics": ["aeronautics"],
                }
            ],
        )

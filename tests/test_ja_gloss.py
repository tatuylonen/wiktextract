from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestJaGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ja"),
            WiktionaryConfig(
                dump_file_lang_code="ja",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_gloss(self):
        self.wxr.wtp.add_page("テンプレート:L", 10, "日本語")
        self.wxr.wtp.add_page("テンプレート:noun", 10, "名詞")
        self.wxr.wtp.add_page(
            "テンプレート:おくりがな2",
            10,
            "<ruby>[[引]]<rp>（</rp><rt>[[ひく|ひ]]</rt><rp>）</rp></ruby>き",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "辞典",
                """=={{L|ja}}==
==={{noun}}===
#{{おくりがな2|引|ひ|き|ひく}}やすいように言語ごとの[[字母]]順などによって[[配列]]してある。""",
            ),
            [
                {
                    "lang": "日本語",
                    "lang_code": "ja",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "senses": [
                        {
                            "glosses": [
                                "引きやすいように言語ごとの字母順などによって配列してある。"
                            ],
                            "ruby": [("引", "ひ")],
                        }
                    ],
                    "word": "辞典",
                }
            ],
        )

    def test_nested_gloss_lists(self):
        self.wxr.wtp.add_page("テンプレート:ja", 10, "日本語")
        self.wxr.wtp.add_page("テンプレート:name", 10, "固有名詞")
        page_data = parse_page(
            self.wxr,
            "東京",
            """=={{ja}}==
[[category:{{ja}}]]
==={{name}}===
#（とうきょう）[[日本]]の事実上の[[首都]]。以下、語源・関連語・訳語は本義のもの。
##[[東京二十三区]]。[[東京都]]のうち、[[多摩]]と島嶼部を除いた地域。かつての[[東京市]]。""",
        )
        self.assertEqual(page_data[0]["categories"], ["日本語"])
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": [
                        "（とうきょう）日本の事実上の首都。以下、語源・関連語・訳語は本義のもの。"
                    ]
                },
                {
                    "glosses": [
                        "（とうきょう）日本の事実上の首都。以下、語源・関連語・訳語は本義のもの。",
                        "東京二十三区。東京都のうち、多摩と島嶼部を除いた地域。かつての東京市。",
                    ]
                },
            ],
        )

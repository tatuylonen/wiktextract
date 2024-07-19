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

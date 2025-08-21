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

    def test_topic(self):
        self.wxr.wtp.add_page("テンプレート:L", 10, "日本語")
        self.wxr.wtp.add_page("テンプレート:noun", 10, "名詞")
        self.wxr.wtp.add_page(
            "テンプレート:context", 10, "(占星術[[カテゴリ:日本語 占星術]])"
        )
        page_data = parse_page(
            self.wxr,
            "東京",
            """=={{L|ja}}==
==={{noun}}===
#{{context|astrology|lang=ja}}[[うお座]]。[[占星術]]における、[[黄道十二星座]]・[[十二宮]]のひとつ。""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["日本語 占星術"],
                    "glosses": [
                        "うお座。占星術における、黄道十二星座・十二宮のひとつ。"
                    ],
                    "topics": ["astrology"],
                }
            ],
        )

    def test_two_topics(self):
        self.wxr.wtp.add_page("テンプレート:L", 10, "日本語")
        self.wxr.wtp.add_page("テンプレート:noun", 10, "名詞")
        self.wxr.wtp.add_page(
            "テンプレート:context",
            10,
            '<span class="ib-brac"><span class="qualifier-brac"> (</span></span><span class="ib-content"><span class="qualifier-content">野球<span class="ib-comma"><span class="qualifier-comma">,</span></span>&#32;[[カテゴリ:日本語 野球]]ゴルフ[[カテゴリ:日本語 ゴルフ]]</span></span><span class="ib-brac"><span class="qualifier-brac">) </span></span>',
        )
        page_data = parse_page(
            self.wxr,
            "てんぷら",
            """=={{L|ja}}==
==={{noun}}===
#{{context|baseball|golf|lang=ja}}高く上がりすぎて[[飛距離]]が出ない[[打球]]。""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["日本語 野球", "日本語 ゴルフ"],
                    "glosses": ["高く上がりすぎて飛距離が出ない打球。"],
                    "topics": ["baseball", "golf"],
                }
            ],
        )

    def test_link_node_form_of(self):
        self.wxr.wtp.add_page("テンプレート:ja", 10, "日本語")
        page_data = parse_page(
            self.wxr,
            "天麩羅",
            """=={{ja}}==
===和語の漢字表記===
#「[[てんぷら]]」参照。""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "form_of": [{"word": "てんぷら"}],
                    "glosses": ["「てんぷら」参照。"],
                    "tags": ["form-of"],
                }
            ],
        )

    def test_wagokanji_of(self):
        self.wxr.wtp.add_page("テンプレート:L", 10, "日本語")
        self.wxr.wtp.add_page(
            "テンプレート:wagokanji of", 10, "'''[[{{{1}}}]]'''の漢字表記。"
        )
        self.wxr.wtp.add_page("テンプレート:wago", 10, "和語の漢字表記")
        page_data = parse_page(
            self.wxr,
            "天麩羅",
            """=={{L|ja}}==
==={{wago}}===
#{{wagokanji of|てんぷら}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "form_of": [{"word": "てんぷら"}],
                    "glosses": ["てんぷらの漢字表記。"],
                }
            ],
        )

    def test_wikipedia_s(self):
        self.wxr.wtp.add_page("テンプレート:L", 10, "英語")
        self.wxr.wtp.add_page(
            "テンプレート:wikipedia-s",
            10,
            "[[摩擦音]] [[w:摩擦音 | <sup><small>(wp)</small></sup>]]",
        )
        page_data = parse_page(
            self.wxr,
            "fricative",
            """=={{L|en}}==
===形容詞===
# [[摩擦]]による。{{wikipedia-s|摩擦音}}の。""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["摩擦による。摩擦音の。"],
                }
            ],
        )

    def test_lb(self):
        self.wxr.wtp.add_page(
            "テンプレート:lb",
            10,
            '<span class="ib-brac"><span class="qualifier-brac"> (</span></span><span class="ib-content"><span class="qualifier-content">他動詞<span class="ib-comma"><span class="qualifier-comma">,</span></span>&#32;[[カテゴリ:ハンガリー語 他動詞]]演算</span></span><span class="ib-brac"><span class="qualifier-brac">) </span></span>',
        )
        page_data = parse_page(
            self.wxr,
            "ad",
            """=={{hu}}==
===動詞===
# {{lb|hu|transitive|演算}} hozzáad「足す」の類義語。""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["ハンガリー語 他動詞"],
                    "glosses": ["hozzáad「足す」の類義語。"],
                    "tags": ["transitive"],
                    "topics": ["arithmetic"],
                }
            ],
        )

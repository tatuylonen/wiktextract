from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="it"),
            WiktionaryConfig(
                dump_file_lang_code="it", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_list_example(self):
        self.wxr.wtp.add_page("Template:-br-", 10, "Bretone")
        data = parse_page(
            self.wxr,
            "dog",
            """== {{-br-}} ==
===Sostantivo===
# mutazione
#* ''Da '''dog''', e '''dog'''.''
#*: Il tuo cappello, il suo cappello.""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["mutazione"],
                    "examples": [
                        {
                            "text": "Da dog, e dog.",
                            "translation": "Il tuo cappello, il suo cappello.",
                        }
                    ],
                }
            ],
        )

    def test_all_in_one_line(self):
        self.wxr.wtp.add_page("Template:-zh-", 10, "Cinese")
        data = parse_page(
            self.wxr,
            "幼虫",
            """== {{-zh-}} ==
===Sostantivo===
# larva
#* [[苍蝇]] [[的]]'''幼虫''' ''cāngyíng de '''yòuchóng''''' - [[larva]] di [[mosca]], [[bigattino]]""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["larva"],
                    "examples": [
                        {
                            "text": "苍蝇的幼虫",
                            "roman": "cāngyíng de yòuchóng",
                            "translation": "larva di mosca, bigattino",
                        }
                    ],
                }
            ],
        )

    def test_ja_r(self):
        self.wxr.wtp.add_page("Template:-ja-", 10, "Giapponese")
        self.wxr.wtp.add_page(
            "Template:ja-r",
            10,
            """{{#switch:{{{1}}}
| 今 = <span class="Jpan" lang="ja">[[今#Giapponese|<span><ruby>今<rp>&nbsp;(</rp><rt>いま</rt><rp>)</rp></ruby></span>]]</span>
| 行く = <span class="Jpan" lang="ja">[[行く#Giapponese|<span><ruby>行<rp>&nbsp;(</rp><rt>い</rt><rp>)</rp></ruby>く</span>]]</span>
| よ = <span class="Jpan" lang="ja">[[よ#Giapponese|<span>よ</span>]]</span>
}}""",
        )
        data = parse_page(
            self.wxr,
            "行く",
            """== {{-ja-}} ==
===Verbo===
# andare
#* {{ja-r|今|いま|rom=-}}'''{{ja-r|行く|いく|rom=-}}'''{{ja-r|よ|rom=-}}! (''ima '''iku''' yo!'')
#: ''sto '''andando'''!''""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["andare"],
                    "examples": [
                        {
                            "text": "今行くよ!",
                            "roman": "ima iku yo!",
                            "translation": "sto andando!",
                            "ruby": [("今", "いま"), ("行", "い")],
                        }
                    ],
                }
            ],
        )

    def test_zh_tradsem(self):
        self.wxr.wtp.add_page("Template:-zh-", 10, "Cinese")
        data = parse_page(
            self.wxr,
            "可能",
            """== {{-zh-}} ==
===Aggettivo===
# probabile
#* {{zh-tradsem|[[一]] [[個]]'''可能'''[[的]] [[事件]]|[[一]] [[个]]'''可能'''[[的]] [[事件]]}} ''yī ge '''kěnéng''' de shìjiàn'' - un [[evento]] [[possibile]]""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["probabile"],
                    "examples": [
                        {
                            "text": "一個可能的事件",
                            "roman": "yī ge kěnéng de shìjiàn",
                            "translation": "un evento possibile",
                            "tags": ["Traditional Chinese"],
                        },
                        {
                            "text": "一个可能的事件",
                            "roman": "yī ge kěnéng de shìjiàn",
                            "translation": "un evento possibile",
                            "tags": ["Simplified Chinese"],
                        },
                    ],
                }
            ],
        )

    def test_double_italic_nodes_with_translation(self):
        self.wxr.wtp.add_page("Template:-en-", 10, "Inglese")
        data = parse_page(
            self.wxr,
            "water",
            """== {{-en-}} ==
===Sostantivo===
# acqua
#: ''May I have a glass of '''water'''?'' - ''Posso avere un bicchiere d''''acqua'''''?""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["acqua"],
                    "examples": [
                        {
                            "text": "May I have a glass of water?",
                            "translation": "Posso avere un bicchiere d'acqua?",
                        }
                    ],
                }
            ],
        )

    def test_double_italic_nodes_no_translation(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "essere",
            """== {{-it-}} ==
===Sostantivo===
#chi [[esiste]]
#* ''gli '''esseri''' viventi''; ''gli '''esseri''' animati''""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["chi esiste"],
                    "examples": [
                        {"text": "gli esseri viventi; gli esseri animati"}
                    ],
                }
            ],
        )

    def test_term_ref_template(self):
        self.wxr.wtp.add_page("Template:-la-", 10, "Latino")
        self.wxr.wtp.add_page("Template:Term", 10, "({{{1}}})")
        data = parse_page(
            self.wxr,
            "libero",
            """== {{-la-}} ==
===Verbo===
# [[assolvere]], [[liberare]] dalle [[accuse]], [[giudicare]] [[innocente]]
#* ''et eum omni [[ignominia]] '''liberat''''' - e lo [[assolve]] da ogni [[ignominia]] {{Term|[[:w:Marco Tullio Cicerone|Cicerone]], [[:w:Pro Cluentio|Pro Cluentio]], [[:s:la:Pro_Aulo_Cluentio_Habito|XLVII, 132]]}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": [
                        "assolvere, liberare dalle accuse, giudicare innocente"
                    ],
                    "examples": [
                        {
                            "text": "et eum omni ignominia liberat",
                            "translation": "e lo assolve da ogni ignominia",
                            "ref": "Cicerone, Pro Cluentio, XLVII, 132",
                        }
                    ],
                }
            ],
        )

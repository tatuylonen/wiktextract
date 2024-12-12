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

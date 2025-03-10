from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="tr"),
            WiktionaryConfig(
                dump_file_lang_code="tr", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_adam(self):
        self.wxr.wtp.add_page(
            "Şablon:ç",
            10,
            """{{#switch:{{{2}}}
| رَجُل = <span class="Arab" lang="ar">[[رجل#Arapça|رَجُل]]</span>&lrm;<span class="tpos">&nbsp;[[:ar:رجل|(ar)]]</span>&nbsp;<span class="gender"><abbr title="eril cinsiyet">e</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ar-Latn" class="tr Latn">racül</span><span class="mention-gloss-paren annotation-paren">)</span>
| 男 = <span class="Jpan" lang="ja">[[男#Japonca|男]]</span><span class="tpos">&nbsp;[[:ja:男|(ja)]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">おとこ, otoko</span><span class="mention-gloss-paren annotation-paren">)</span>
| 男性 = <span class="Jpan" lang="ja">[[男性#Japonca|男性]]</span><span class="tpos">&nbsp;[[:ja:男性|(ja)]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">だんせい, dansei</span><span class="mention-gloss-paren annotation-paren">)</span>
| άνθρωπος = <span class="Grek" lang="el">[[άνθρωπος#Yunanca|άνθρωπος]]</span><span class="tpos">&nbsp;[[:el:άνθρωπος|(el)]]</span>&nbsp;<span class="gender"><abbr title="eril cinsiyet">e</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="el-Latn" class="tr Latn">ánthropos</span><span class="mention-gloss-paren annotation-paren">)</span>
}}""",
        )

        page_data = parse_page(
            self.wxr,
            "adam",
            """==Türkçe==
===Ad===
# bir [[alan]]ı benimseyen [[kişi]]
====Çeviriler====
{{Üst|erkek kişi|tip=çeviriler}}
* Arapça: {{ç|ar|رَجُل|m}}
* Japonca: {{ç|ja|男|tr=おとこ, otoko}},  {{ç|ja|男性|tr=だんせい, dansei}}
* Yunanca:
*: Modern Yunanca: {{ç|el|άνθρωπος|m}}""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "lang": "Arapça",
                    "lang_code": "ar",
                    "word": "رَجُل",
                    "roman": "racül",
                    "tags": ["masculine"],
                    "sense": "erkek kişi",
                },
                {
                    "lang": "Japonca",
                    "lang_code": "ja",
                    "word": "男",
                    "roman": "おとこ, otoko",
                    "sense": "erkek kişi",
                },
                {
                    "lang": "Japonca",
                    "lang_code": "ja",
                    "word": "男性",
                    "roman": "だんせい, dansei",
                    "sense": "erkek kişi",
                },
                {
                    "lang": "Modern Yunanca",
                    "lang_code": "el",
                    "word": "άνθρωπος",
                    "roman": "ánthropos",
                    "tags": ["masculine"],
                    "sense": "erkek kişi",
                },
            ],
        )

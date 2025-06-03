from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrLinkage(TestCase):
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

    def test_list(self):
        self.wxr.wtp.add_page("Şablon:mânâ", 10, "({{{1}}}):")
        self.wxr.wtp.add_page("Şablon:şerh", 10, "({{{1}}})")
        page_data = parse_page(
            self.wxr,
            "adam",
            """==Türkçe==
===Ad===
# bir [[alan]]ı benimseyen [[kişi]]
=====Eş anlamlılar=====
* {{mânâ|koca}} [[zevc]] {{şerh|eskimiş}}""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [{"word": "zevc", "sense": "koca", "tags": ["obsolete"]}],
        )

    def test_link(self):
        page_data = parse_page(
            self.wxr,
            "adam",
            """==Türkçe==
===Ad===
# bir [[alan]]ı benimseyen [[kişi]]
=====Deyimler=====
[[adam başı]],
[[adam gibi adam]]""",
        )
        self.assertEqual(
            page_data[0]["idioms"],
            [{"word": "adam başı"}, {"word": "adam gibi adam"}],
        )

    def test_symbol(self):
        page_data = parse_page(
            self.wxr,
            "iki",
            """==Türkçe==
===Ad===
# [[bir]]den [[sonra]] [[gelmek|gelen]] [[sayı]]nın [[ad]]ı
====Sembol====
* [[2]], [[II]]""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [
                {"word": "2", "tags": ["symbol"]},
                {"word": "II", "tags": ["symbol"]},
            ],
        )

    def test_gloss_list_template(self):
        self.wxr.wtp.add_page(
            "Şablon:alt kavramlar",
            10,
            'alt kavramsı: <span class="Arab" lang="ar">[[سيل#Arapça|سَيْل]]</span>&lrm; <span class="mention-gloss-paren annotation-paren">(</span><span lang="ar-Latn" class="tr Latn">seyl</span><span class="mention-gloss-paren annotation-paren">)</span>',
        )
        self.wxr.wtp.add_page(
            "Şablon:eş anlamlılar",
            10,
            'eş anlamlısı: <span class="Arab" lang="ar">[[فضاء#Arapça|فَضَاء]]</span>&lrm; <span class="mention-gloss-paren annotation-paren">(</span><span lang="ar-Latn" class="tr Latn">faḍāʾ</span><span class="mention-gloss-paren annotation-paren">)</span>',
        )
        page_data = parse_page(
            self.wxr,
            "سماء",
            """==Arapça==
===Ad===
# [[gök]], [[sema]]
## [[sema]]nın [[bulut]], [[yağış]] gibi [[üretme|ürettikleri]]
##: {{alt kavramlar|ar|سَيْل|t1=bulutlar}}
## [[dış uzay]]
##: {{eş anlamlılar|ar|فَضَاء|t=bir uzay/boşluk}}""",
        )
        self.assertEqual(
            page_data[0]["hyponyms"],
            [
                {
                    "word": "سَيْل",
                    "sense": "gök, sema semanın bulut, yağış gibi ürettikleri",
                    "roman": "seyl",
                }
            ],
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [{"word": "فَضَاء", "sense": "gök, sema dış uzay", "roman": "faḍāʾ"}],
        )

    def test_l_template(self):
        self.wxr.wtp.add_page(
            "Şablon:l",
            10,
            '<span class="Latn" lang="tr">[[BK#Türkçe|BK]]</span>',
        )
        page_data = parse_page(
            self.wxr,
            "Birleşik Krallık",
            """==Türkçe==
===Özel ad===
# [[İngiltere]]
====Kısaltma====
* {{l|tr|BK}}""",
        )
        self.assertEqual(
            page_data[0]["related"], [{"tags": ["abbreviation"], "word": "BK"}]
        )

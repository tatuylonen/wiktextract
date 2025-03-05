from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrEtymology(TestCase):
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
            "Şablon:ek",
            10,
            '<span class="Latn" lang="tr">[[ada#Türkçe|ada]]</span> + <span class="Latn" lang="tr">[[-m#Türkçe|-m]]</span>[[Kategori:Türkçe -m son ekiyle oluşmuş sözcükler]]',
        )
        self.wxr.wtp.add_page(
            "Şablon:k",
            10,
            "[[w:Arapça|Arapça]][[Kategori:Arapça kökenli Türkçe sözcükler]]",
        )
        self.wxr.wtp.add_page(
            "Şablon:z",
            10,
            '<i class="Arab mention" lang="ar">[[آدم#Arapça|آدَم]]</i>&lrm; <span class="mention-gloss-paren annotation-paren">(</span><span lang="ar-Latn" class="mention-tr tr Latn">ʾādem</span><span class="mention-gloss-paren annotation-paren">)</span>',
        )
        page_data = parse_page(
            self.wxr,
            "adam",
            """==Türkçe==
===Köken 1===
:{{ek|dil=tr|ada|m}}
====Ad====
# gloss 1

===Köken 2===
:{{k|dil=tr|ar}} {{z|ar|آدَم}}
====Ad====
# gloss 2""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            ["Türkçe -m son ekiyle oluşmuş sözcükler"],
        )
        self.assertEqual(page_data[0]["etymology_texts"], ["ada + -m"])
        self.assertEqual(
            page_data[1]["categories"], ["Arapça kökenli Türkçe sözcükler"]
        )
        self.assertEqual(
            page_data[1]["etymology_texts"], ["Arapça آدَم (ʾādem)"]
        )

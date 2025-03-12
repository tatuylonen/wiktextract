from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrInflection(TestCase):
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

    def test_tr_eylem_tablo(self):
        self.wxr.wtp.add_page(
            "Şablon:tr-eylem-tablo",
            10,
            """<div><div>''acıkmak'' eyleminin çekimi</div><div>
{|
|-
! olumlu çekimler
|-
! colspan='3' rowspan='2' |
! colspan='3' |'''[[tekil]]'''
! colspan='3' |'''[[çoğul]]'''
|-
! '''ben'''
! '''sen'''
! '''o'''
! '''biz'''
! '''siz'''
! '''onlar'''
|-
! rowspan='20' |'''bildirme (haber)<br>kipleri'''
! rowspan='4' |'''belirli geçmiş'''
! '''basit'''
| [[acıktım]]
|-
! '''rivayet'''
| [[—]]
|-
! '''şart'''
| [[acıktıysalar]]<br>[[acıktılarsa]]
|-
|-
|-
! colspan='9' |olumsuz çekimler
|-
! colspan='3' rowspan='2' |
! colspan='3' |'''[[tekil]]'''
! colspan='3' |'''[[çoğul]]'''
|-
! '''ben'''
! '''sen'''
! '''o'''
! '''biz'''
! '''siz'''
! '''onlar'''
|-
! rowspan='20' |'''bildirme (haber)<br>kipleri'''
! rowspan='4' |'''belirli geçmiş'''
! '''basit'''
| [[acıkmadım]]
|}</div></div> [[Kategori:Çekimleme tablosu bulunan Türkçe eylemler]]""",
        )
        page_data = parse_page(
            self.wxr,
            "acıkmak",
            """==Türkçe==
===Eylem===
# [[yemek]] [[yeme]] [[gerek]]sinimi [[duymak]]
====Çekimleme====
{{tr-eylem-tablo}}""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            ["Çekimleme tablosu bulunan Türkçe eylemler"],
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "acıktım",
                    "tags": ["positive", "singular", "definite", "past"],
                    "raw_tags": ["ben", "bildirme (haber)\nkipleri", "basit"],
                },
                {
                    "form": "acıktıysalar",
                    "tags": [
                        "positive",
                        "singular",
                        "definite",
                        "past",
                        "conditional",
                    ],
                    "raw_tags": ["ben", "bildirme (haber)\nkipleri"],
                },
                {
                    "form": "acıktılarsa",
                    "tags": [
                        "positive",
                        "singular",
                        "definite",
                        "past",
                        "conditional",
                    ],
                    "raw_tags": ["ben", "bildirme (haber)\nkipleri"],
                },
                {
                    "form": "acıkmadım",
                    "tags": ["negative", "singular", "definite", "past"],
                    "raw_tags": ["ben", "bildirme (haber)\nkipleri", "basit"],
                },
            ],
        )

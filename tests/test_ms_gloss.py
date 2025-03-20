from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ms"),
            WiktionaryConfig(
                dump_file_lang_code="ms", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_pos_title(self):
        page_data = parse_page(
            self.wxr,
            "dance",
            """== Bahasa Inggeris ==
=== Takrifan ===
==== Kata nama ====
# [[tarian]]
==== Kata kerja ====
# [[menari]], [[tari]]""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "lang": "Bahasa Inggeris",
                    "lang_code": "en",
                    "pos": "noun",
                    "pos_title": "Kata nama",
                    "senses": [{"glosses": ["tarian"]}],
                    "word": "dance",
                },
                {
                    "lang": "Bahasa Inggeris",
                    "lang_code": "en",
                    "pos": "verb",
                    "pos_title": "Kata kerja",
                    "senses": [{"glosses": ["menari, tari"]}],
                    "word": "dance",
                },
            ],
        )

    def test_no_pos_title(self):
        self.wxr.wtp.add_page(
            "Templat:ms-kk",
            10,
            '<span class="headword-line"><strong class="Latn headword" lang="ms">makan</strong></span>[[Kategori:Lema bahasa Melayu|MAKAN]][[Kategori:Kata kerja bahasa Melayu|MAKAN]]',
        )
        self.wxr.wtp.add_page(
            "Templat:ms-kn",
            10,
            '<span class="headword-line"><strong class="Latn headword" lang="ms">makan</strong></span>[[Kategori:Lema bahasa Melayu|MAKAN]][[Kategori:Kata nama bahasa Melayu|MAKAN]]',
        )
        page_data = parse_page(
            self.wxr,
            "makan",
            """==Bahasa Melayu==
=== Takrifan ===
{{ms-kk}}
# [[mamah|memamah]]

{{ms-kn}}
# [[rezeki]].""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "categories": [
                        "Lema bahasa Melayu",
                        "Kata kerja bahasa Melayu",
                    ],
                    "lang": "Bahasa Melayu",
                    "lang_code": "ms",
                    "pos": "verb",
                    "pos_title": "Takrifan",
                    "senses": [{"glosses": ["memamah"]}],
                    "word": "makan",
                },
                {
                    "categories": [
                        "Lema bahasa Melayu",
                        "Kata nama bahasa Melayu",
                    ],
                    "lang": "Bahasa Melayu",
                    "lang_code": "ms",
                    "pos": "noun",
                    "pos_title": "Takrifan",
                    "senses": [{"glosses": ["rezeki."]}],
                    "word": "makan",
                },
            ],
        )

    def test_pos_header_forms(self):
        self.wxr.wtp.add_page(
            "Templat:ms-kgn",
            10,
            '<span class="headword-line"><strong class="Latn headword" lang="ms">apa</strong> (<i>ejaan Jawi</i> <b class="Arab ms-Arab" lang="ms">[[اڤ#Melayu|اڤ]]</b>)</span>[[Kategori:Lema bahasa Melayu|APA]][[Kategori:Kata ganti nama bahasa Melayu|APA]]',
        )
        page_data = parse_page(
            self.wxr,
            "apa",
            """==Bahasa Melayu==
=== Takrifan ===
====Kata ganti nama====
{{ms-kgn|j=اڤ}}
# kata yang digunakan untuk [[soal|menyoal]]""",
        )
        self.assertEqual(
            page_data[0]["forms"], [{"form": "اڤ", "raw_tags": ["ejaan Jawi"]}]
        )

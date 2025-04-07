from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsLinkage(TestCase):
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

    def test_forms(self):
        self.wxr.wtp.add_page("Templat:ARchar", 10, "{{{1}}}")
        page_data = parse_page(
            self.wxr,
            "lembu",
            """== Bahasa Melayu ==
=== Takrifan ===
# Sejenis
===Tulisan Jawi===
{{ARchar|لمبو}}""",
        )
        self.assertEqual(
            page_data[0]["forms"], [{"form": "لمبو", "tags": ["Jawi"]}]
        )

    def test_list(self):
        page_data = parse_page(
            self.wxr,
            "abadi",
            """== Bahasa Melayu ==
=== Takrifan ===
# kekal untuk selamanya.
=== Tesaurus ===
; Sinonim: [[abadiah]], [[abadiat]], baqa, wujud.""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [
                {"word": "abadiah"},
                {"word": "abadiat"},
                {"word": "baqa"},
                {"word": "wujud"},
            ],
        )

    def test_nyms_template(self):
        self.wxr.wtp.add_page(
            "Templat:ant",
            10,
            '<span class="nyms antonim"><span class="defdate">Antonim:</span> <span class="Latn" lang="ms">[[masa lalu#Melayu|masa lalu]]</span>, <span class="Latn" lang="ms">[[masa lampau#Melayu|masa lampau]]</span></span>',
        )
        page_data = parse_page(
            self.wxr,
            "abadi",
            """== Bahasa Melayu ==
=== Takrifan ===
# [[zaman|Zaman]] yang akan datang.
#: {{ant|ms|masa lalu|masa lampau}}""",
        )
        self.assertEqual(
            page_data[0]["antonyms"],
            [
                {"word": "masa lalu", "sense": "Zaman yang akan datang."},
                {"word": "masa lampau", "sense": "Zaman yang akan datang."},
            ],
        )

    def test_normal_list(self):
        self.wxr.wtp.add_page("Templat:sense", 10, "({{{1}}}):")
        page_data = parse_page(
            self.wxr,
            "makan",
            """== Bahasa Melayu ==
=== Takrifan ===
====Kata kerja====
# memamah serta
====Kata nama====
# [[rezeki]].
=== Tesaurus ===
; Sinonim:
* {{sense|santap}} [[bahau]]""",
        )
        self.assertEqual(
            page_data[0]["synonyms"], [{"word": "bahau", "sense": "santap"}]
        )
        self.assertEqual(page_data[0]["synonyms"], page_data[1]["synonyms"])

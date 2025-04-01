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

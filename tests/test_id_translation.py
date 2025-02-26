from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.id.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestIdTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="id"),
            WiktionaryConfig(
                dump_file_lang_code="id", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_page_air(self):
        self.wxr.wtp.add_page(
            "Templat:t-simple",
            10,
            """<span lang="avd" class="fa-Arab">[[او#Alviri-Vidari|او]]</span>&#32;<span class="mention-gloss-paren annotation-paren">(</span><span lang="-Latn" class="tr Latn" xml:lang="-Latn">ov</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        self.wxr.wtp.add_page("Templat:q", 10, "(Vidari)")
        page_data = parse_page(
            self.wxr,
            "air",
            """==bahasa Indonesia==
===Nomina===
# senyawa dengan
====Terjemahan====
{{kotak mulai|Terjemahan}}
* bahasa Alviri-Vidari: {{t-simple|avd|او|tr=ov|sc=fa-Arab|langname=Alviri-Vidari}} {{q|Vidari}}""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "word": "او",
                    "lang": "Alviri-Vidari",
                    "lang_code": "avd",
                    "roman": "ov",
                    "raw_tags": ["Vidari"],
                    "sense": "Terjemahan",
                }
            ],
        )

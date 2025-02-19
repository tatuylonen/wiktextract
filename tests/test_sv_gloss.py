from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.sv.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestSvGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="sv"),
            WiktionaryConfig(
                dump_file_lang_code="sv", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_gloss_list(self):
        self.wxr.wtp.add_page("Mall:tagg", 10, "[[Kategori:Svenska/Fordon|a]]")
        page_data = parse_page(
            self.wxr,
            "cykel",
            """==Svenska==
===Substantiv===
#{{tagg|kat=fordon}} [[pedal]]drivet""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [{"glosses": ["pedaldrivet"], "categories": ["Svenska/Fordon"]}],
        )

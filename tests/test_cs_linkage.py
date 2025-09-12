from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.cs.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestCsLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="cs"),
            WiktionaryConfig(
                dump_file_lang_code="cs", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_alt_form(self):
        data = parse_page(
            self.wxr,
            "pondělí",
            """== čeština ==
=== varianty ===
* [[pondělek]]
=== podstatné jméno ===
==== význam ====
# [[den]]""",
        )
        self.assertEqual(
            data[0]["forms"], [{"form": "pondělek", "tags": ["alternative"]}]
        )

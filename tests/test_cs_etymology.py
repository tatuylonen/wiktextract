from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.cs.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestCsEtymology(TestCase):
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

    def test_etymology_list(self):
        data = parse_page(
            self.wxr,
            "automobil",
            """== čeština ==
=== etymologie ===
* Z francouzského substantiva [[automobile]] (automobil).
* Složenina, viz česká předpona [[auto-]] a francouzské substantivum [[mobile]].
=== podstatné jméno ===
==== význam ====
# [[motorový|motorové]]""",
        )
        self.assertEqual(
            data[0]["etymology_texts"],
            [
                "Z francouzského substantiva automobile (automobil).",
                "Složenina, viz česká předpona auto- a francouzské substantivum mobile.",
            ],
        )

    def test_etymology_under_pos(self):
        data = parse_page(
            self.wxr,
            "chleba",
            """== čeština ==
=== podstatné jméno (1) ===
==== význam ====
* [[chléb]]
=== podstatné jméno (2) ===
==== etymologie ====
Jde vlastně o tzv.
==== význam ====
# ''genitiv singuláru substantiva [[chléb]]''"""
        )
        self.assertTrue("etymology_texts" not in data[0])
        self.assertEqual(
            data[1]["etymology_texts"], ["Jde vlastně o tzv."]
        )

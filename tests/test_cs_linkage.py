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

    def test_linkage_list(self):
        self.wxr.wtp.add_page(
            "Šablona:Příznak2",
            10,
            """<span class="priznaky">(zdrobněle)</span>""",
        )
        data = parse_page(
            self.wxr,
            "pes",
            """== čeština ==
=== podstatné jméno (1) ===
==== význam ====
# [[psovitý|psovitá]]
==== synonyma ====
# {{Příznak2|zdrob.}} [[pejsek]], [[ratlík]]
==== související ====
* [[psík]]""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {"tags": ["diminutive"], "sense_index": 1, "word": "pejsek"},
                {"word": "ratlík", "sense_index": 1},
            ],
        )
        self.assertEqual(data[0]["related"], [{"word": "psík"}])

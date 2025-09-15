from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.cs.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestCsDeclension(TestCase):
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

    def test_noun_table(self):
        self.wxr.wtp.add_page(
            "Šablona:Substantivum (cs)",
            10,
            """{| class="deklinace substantivum"
|-
! <span title="substantivum (podstatné jméno)">pád \\ číslo</span>
! <span title="singulár (jednotné číslo)">jednotné</span>
! <span title="plurál (množné číslo)">množné</span>
|-
! <span title="nominativ (1. pád: kdo? co?)">nominativ</span>
| pes
| [[psi]] / [[psové]]
|}
""",
        )
        data = parse_page(
            self.wxr,
            "pes",
            """==čeština==
===podstatné jméno (1)===
====skloňování====
{{Substantivum (cs)
  | snom = pes
  | sgen = [[psa]]
  | sdat = [[psovi]] / [[psu]]
}}
==== význam ====
# [[psovitý|psovitá]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "psi", "tags": ["nominative", "plural"]},
                {"form": "psové", "tags": ["nominative", "plural"]},
            ],
        )

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
|}""",
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

    def test_adj_table(self):
        self.wxr.wtp.add_page(
            "Šablona:Adjektivum (cs)",
            10,
            """{| class="deklinace adjektivum" style="text-align: center"
|-
! číslo
! colspan="4" title="singulár = jednotné číslo" | jednotné
! colspan="4" title="plurál = množné číslo" | množné
|-
! pád \\ rod
! mužský<br />životný
! mužský<br />neživotný
! ženský
! střední
! mužský<br />životný
! mužský<br />neživotný
! ženský
! střední
|-
! title="nominativ = 1. pád: kdo? co?" | nominativ
| směšný
| směšný
| směšná
| směšné
| směšní
| směšné
| směšné
| směšná
|}""",
        )
        self.wxr.wtp.add_page(
            "Šablona:Stupňování (cs)",
            10,
            """{| class="komparace" style="text-align: center"
|-
! stupeň
! tvar
|-
! pozitiv
| směšný
|-
! komparativ
| [[směšnější]]
|-
! superlativ
| [[nejsměšnější]]
|}""",
        )
        data = parse_page(
            self.wxr,
            "směšný",
            """==čeština==
=== přídavné jméno ===
====skloňování====
{{Adjektivum (cs)
  | snomm = směšný
}}
==== stupňování ====
{{Stupňování (cs)
  | poz = směšný
  | komp = směšnější
  | sup = nejsměšnější
}}
==== význam ====
# [[vyvolávat|vyvolávající]] [[smích]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "směšná",
                    "tags": ["nominative", "singular", "feminine"],
                },
                {
                    "form": "směšné",
                    "tags": ["nominative", "singular", "neuter"],
                },
                {
                    "form": "směšní",
                    "tags": ["nominative", "plural", "masculine", "animate"],
                },
                {
                    "form": "směšné",
                    "tags": ["nominative", "plural", "masculine", "inanimate"],
                },
                {
                    "form": "směšné",
                    "tags": ["nominative", "plural", "feminine"],
                },
                {"form": "směšná", "tags": ["nominative", "plural", "neuter"]},
                {
                    "form": "směšnější",
                    "raw_tags": ["tvar"],
                    "tags": ["comparative"],
                },
                {
                    "form": "nejsměšnější",
                    "raw_tags": ["tvar"],
                    "tags": ["superlative"],
                },
            ],
        )

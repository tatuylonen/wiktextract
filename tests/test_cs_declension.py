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

    def test_verb_tables(self):
        self.wxr.wtp.add_page(
            "Šablona:Příznak2",
            10,
            """<span class="priznaky">(zastarale)</span>""",
        )
        self.wxr.wtp.add_page(
            "Šablona:Sloveso (cs)",
            10,
            """{| class="konjugace verbum" style="text-align: center"
|+ Oznamovací způsob
|-
!rowspan="2"|osoba
!colspan="3"|číslo jednotné !! colspan="3"|číslo množné
|-
!1.!!2.!!3.!!1.!!2.!!3.
|-
!přítomný čas
|[[běžím]]
|[[běžíš]]
|[[běží]]
|[[běžíme]]
|[[běžíte]]
|[[běží]]
|}

{| class="konjugace verbum" style="text-align: center"
|+ Přechodníky
|-
!rowspan="2"|rod
!colspan="2"|číslo jednotné !! |číslo množné
|-
!mužský!!ženský<br/>střední!!mužský<br/>ženský<br/>střední
|-
!přítomný
|[[běže]]
|[[běžíc]]
|[[běžíce]]
|-
[[Kategorie:Monitoring:Sloveso (cs)/mtra/skrýt]]
|}""",
        )
        data = parse_page(
            self.wxr,
            "běžet",
            """==čeština==
=== sloveso ===
==== varianty ====
* {{Příznak2|zast.}} [[běžeti]]
==== časování ====
{{Sloveso (cs)
  | spre1 = [[běžím]]
}}
==== význam ====
# [[pohybovat se]] [[rychle]] [[po]] [[noha|nohách]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "běžeti", "tags": ["alternative", "obsolete"]},
                {
                    "form": "běžím",
                    "tags": [
                        "indicative",
                        "present",
                        "singular",
                        "first-person",
                    ],
                },
                {
                    "form": "běžíš",
                    "tags": [
                        "indicative",
                        "present",
                        "singular",
                        "second-person",
                    ],
                },
                {
                    "form": "běží",
                    "tags": [
                        "indicative",
                        "present",
                        "singular",
                        "third-person",
                    ],
                },
                {
                    "form": "běžíme",
                    "tags": ["indicative", "present", "plural", "first-person"],
                },
                {
                    "form": "běžíte",
                    "tags": [
                        "indicative",
                        "present",
                        "plural",
                        "second-person",
                    ],
                },
                {
                    "form": "běží",
                    "tags": ["indicative", "present", "plural", "third-person"],
                },
                {
                    "form": "běže",
                    "tags": [
                        "transgressive",
                        "present",
                        "singular",
                        "masculine",
                    ],
                },
                {
                    "form": "běžíc",
                    "tags": [
                        "transgressive",
                        "present",
                        "singular",
                        "feminine",
                        "neuter",
                    ],
                },
                {
                    "form": "běžíce",
                    "tags": [
                        "transgressive",
                        "present",
                        "plural",
                        "masculine",
                        "feminine",
                        "neuter",
                    ],
                },
            ],
        )
        self.assertEqual(
            data[0]["categories"], ["Monitoring:Sloveso (cs)/mtra/skrýt"]
        )

    def test_de_verb_table(self):
        self.wxr.wtp.add_page(
            "Šablona:Sloveso (de)",
            10,
            """{| class="konjugace verbum" style="text-align: center"
|+ Indikativ
! rowspan="2" | čas
! rowspan="2" | osoba
! colspan="2" | aktivum
|-
! singulár !! plurál
|-
! rowspan="3" | prézens
! 1.
| lang="de" | ich gehe
| lang="de" | wir gehen
|-
! 3.
| lang="de" | er/sie/es geht
| lang="de" | sie gehen
|}""",
        )
        data = parse_page(
            self.wxr,
            "gehen",
            """== němčina ==
=== sloveso ===
==== časování ====
{{Sloveso (de)
  | papr = gehend
}}
==== význam ====
# [[jít]], [[chodit]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "ich gehe",
                    "tags": [
                        "indicative",
                        "present",
                        "first-person",
                        "active",
                        "singular",
                    ],
                },
                {
                    "form": "wir gehen",
                    "tags": [
                        "indicative",
                        "present",
                        "first-person",
                        "active",
                        "plural",
                    ],
                },
                {
                    "form": "er/sie/es geht",
                    "tags": [
                        "indicative",
                        "present",
                        "third-person",
                        "active",
                        "singular",
                    ],
                },
                {
                    "form": "sie gehen",
                    "tags": [
                        "indicative",
                        "present",
                        "third-person",
                        "active",
                        "plural",
                    ],
                },
            ],
        )

    def test_tag_in_table_cell(self):
        self.wxr.wtp.add_page(
            "Šablona:Sloveso (cs)",
            10,
            """{| class="konjugace verbum" style="text-align: center"
|+ Oznamovací způsob
|-
!rowspan="2"|osoba
!colspan="3"|číslo jednotné !! colspan="3"|číslo množné
|-
!1.!!2.!!3.!!1.!!2.!!3.
|-
!přítomný čas
|[[biji]] / <span class="priznaky">(hovorově)</span> [[biju]]
|}""",
        )
        data = parse_page(
            self.wxr,
            "bít",
            """== čeština ==
=== sloveso ===
==== časování ====
{{Sloveso (cs)
  | spre1 = [[biji]] / {{Příznak2|hovor.}} [[biju]]
}}
==== význam ====
# [[dávat]] [[rána|rány]], [[úder]]y""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "biji",
                    "tags": [
                        "indicative",
                        "present",
                        "singular",
                        "first-person",
                    ],
                },
                {
                    "form": "biju",
                    "tags": [
                        "colloquially",
                        "indicative",
                        "present",
                        "singular",
                        "first-person",
                    ],
                },
            ],
        )

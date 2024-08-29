from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.inflection import extract_inflection_section
from wiktextract.extractor.pl.models import Sense, WordEntry
from wiktextract.extractor.pl.page import (
    extract_zapis_section,
    extract_transliteracja_section,
)
from wiktextract.wxr_context import WiktextractContext


class TestPlInflection(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_odmiana_rzeczownik_polski(self):
        self.wxr.wtp.start_page("pies")
        root = self.wxr.wtp.parse(""": (2.1-3) {{odmiana-rzeczownik-polski
|Biernik lm = psy / psów
}}""")
        page_data = [
            WordEntry(
                word="pies",
                lang="język polski",
                lang_code="pl",
                pos="noun",
                senses=[Sense(sense_index="1.1")],
            ),
            WordEntry(
                word="pies",
                lang="język polski",
                lang_code="pl",
                pos="noun",
                senses=[Sense(sense_index="2.1")],
            ),
        ]
        extract_inflection_section(self.wxr, page_data, "pl", root)
        self.assertEqual(len(page_data[0].forms), 0)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[1].forms],
            [
                {
                    "form": "psy",
                    "tags": ["accusative", "plural"],
                    "sense_index": "2.1-3",
                },
                {
                    "form": "psów",
                    "tags": ["accusative", "plural"],
                    "sense_index": "2.1-3",
                },
            ],
        )

    def test_tag_template_in_noun_table(self):
        self.wxr.wtp.start_page("durian")
        self.wxr.wtp.add_page("Szablon:pot", 10, "pot.")
        root = self.wxr.wtp.parse(""": (1.1-2) {{odmiana-rzeczownik-polski
|Biernik lp = durian / {{pot}} duriana
}}""")
        page_data = [
            WordEntry(
                word="durian",
                lang="język polski",
                lang_code="pl",
                pos="noun",
                senses=[Sense(sense_index="1.1")],
            ),
        ]
        extract_inflection_section(self.wxr, page_data, "pl", root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[0].forms],
            [
                {
                    "form": "duriana",
                    "tags": ["accusative", "singular", "colloquial"],
                    "sense_index": "1.1-2",
                },
            ],
        )

    def test_noun_template_forma_arg(self):
        self.wxr.wtp.start_page("Urban")
        root = self.wxr.wtp.parse(""": (1.1) {{odmiana-rzeczownik-polski
|Forma depr = Urbany<ref name="SGJPonline">{{SGJPonline|id=22616|hasło=Urban}}</ref>
}}""")
        page_data = [
            WordEntry(
                word="Urban",
                lang="język polski",
                lang_code="pl",
                pos="noun",
                senses=[Sense(sense_index="1.1")],
            ),
        ]
        extract_inflection_section(self.wxr, page_data, "pl", root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[0].forms],
            [
                {
                    "form": "Urbany",
                    "tags": [
                        "depreciative",
                        "nominative",
                        "vocative",
                        "plural",
                    ],
                    "sense_index": "1.1",
                },
            ],
        )

    def test_potential_noun(self):
        self.wxr.wtp.add_page("Szablon:potencjalnie", 10, "{{{1}}}")
        self.wxr.wtp.start_page("ryż")
        root = self.wxr.wtp.parse(""": (1.1-3) {{odmiana-rzeczownik-polski
|Mianownik lm = {{potencjalnie|ryże}}
}}""")
        page_data = [
            WordEntry(
                word="ryż",
                lang="język polski",
                lang_code="pl",
                pos="noun",
                senses=[Sense(sense_index="1.1")],
            ),
        ]
        extract_inflection_section(self.wxr, page_data, "pl", root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[0].forms],
            [
                {
                    "form": "ryże",
                    "tags": ["potential", "rare", "nominative", "plural"],
                    "sense_index": "1.1-3",
                },
            ],
        )

    def test_odmiana_przymiotnik_polski(self):
        self.wxr.wtp.add_page(
            "Szablon:odmiana-przymiotnik-polski",
            10,
            """<div><table><tr><th rowspan="2">[[przypadek]]</th><th colspan="4">''liczba pojedyncza''</th><th colspan="2">''liczba mnoga''</th></tr><tr><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#M|<span><span>mos</span></span>]]</span>/<span>[[Aneks:Skróty używane w Wikisłowniku#M|<span><span>mzw</span></span>]]</span></td><td class="forma"><span >[[Aneks:Skróty używane w Wikisłowniku#M|<span><span>mrz</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#Ż|<span><span>ż</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#N|<span><span>n</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#M|<span><span>mos</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#N|<span><span>nmos</span></span>]]</span></td></tr><tr><td class="forma">[[mianownik]]</td><td colspan="2">smutny</td><td>smutna</td><td>smutne</td><td>smutni</td><td>smutne</td></tr><tr><td colspan="7"><table><tr><th colspan="7">&nbsp;stopień wyższy '''smutniejszy'''</th></tr><tr><th rowspan="2">[[przypadek]]</th><th colspan="4">''liczba pojedyncza''</th><th colspan="2">''liczba mnoga''</th></tr><tr><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#M|<span><span>mos</span></span>]]</span>/<span>[[Aneks:Skróty używane w Wikisłowniku#M|<span><span>mzw</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#M|<span><span>mrz</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#Ż|<span><span>ż</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#N|<span><span >n</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#M|<span ><span>mos</span></span>]]</span></td><td class="forma"><span>[[Aneks:Skróty używane w Wikisłowniku#N|<span><span>nmos</span></span>]]</span></td></tr><tr><td class="forma">[[mianownik]]</td><td colspan="2">smutniejszy</td><td>smutniejsza</td><td>smutniejsze</td><td>smutniejsi</td><td>smutniejsze</td></tr></table></td></tr></table></div>""",
        )
        self.wxr.wtp.start_page("smutny")
        root = self.wxr.wtp.parse(
            ": (1.1-3) {{odmiana-przymiotnik-polski|smutniejszy}}"
        )
        page_data = [
            WordEntry(
                word="smutny",
                lang="język polski",
                lang_code="pl",
                pos="adj",
                senses=[Sense(sense_index="1.1")],
            ),
        ]
        extract_inflection_section(self.wxr, page_data, "pl", root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[0].forms],
            [
                {
                    "form": "smutna",
                    "tags": ["nominative", "singular", "feminine"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutne",
                    "tags": ["nominative", "singular", "neuter"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutni",
                    "tags": ["nominative", "plural", "masculine"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutne",
                    "tags": ["nominative", "plural", "nonvirile"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutniejszy",
                    "tags": ["comparative"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutniejszy",
                    "tags": [
                        "nominative",
                        "singular",
                        "masculine",
                        "animate",
                        "inanimate",
                    ],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutniejsza",
                    "tags": ["nominative", "singular", "feminine"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutniejsze",
                    "tags": ["nominative", "singular", "neuter"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutniejsi",
                    "tags": ["nominative", "plural", "masculine"],
                    "sense_index": "1.1-3",
                },
                {
                    "form": "smutniejsze",
                    "tags": ["nominative", "plural", "nonvirile"],
                    "sense_index": "1.1-3",
                },
            ],
        )

    def test_odmiana_czasownik_polski(self):
        self.wxr.wtp.add_page(
            "Szablon:odmiana-czasownik-polski",
            10,
            """<div><div><table><tr><th rowspan="2" colspan="2">[[forma]]</th><th colspan="3">[[liczba pojedyncza]]</th><th colspan="3">[[liczba mnoga]]</th></tr><tr><th>''1.'' <span>[[Aneks:Skróty używane w Wikisłowniku#O|<span><span>os.</span></span>]]</span></th><th>''2.'' <span>[[Aneks:Skróty używane w Wikisłowniku#O|<span><span>os.</span></span>]]</span></th><th>''3.'' <span>[[Aneks:Skróty używane w Wikisłowniku#O|<span><span>os.</span></span>]]</span></th><th >''1.'' <span>[[Aneks:Skróty używane w Wikisłowniku#O|<span><span>os.</span></span>]]</span></th><th>''2.'' <span >[[Aneks:Skróty używane w Wikisłowniku#O|<span><span>os.</span></span>]]</span></th><th >''3.'' <span>[[Aneks:Skróty używane w Wikisłowniku#O|<span><span>os.</span></span>]]</span></th></tr><tr><td><table><tr><th colspan="8">&nbsp;pozostałe formy</th></tr><tr><th colspan="2">[[forma bezosobowa]] [[czas przeszły|czasu przeszłego]]</th><td colspan="6">biegnięto </td></tr><tr><th rowspan="2">[[tryb przypuszczający]]</th><th>''m''</th><td width="14%">biegłbym</td></tr><tr><th>''n''</th><td><span class="potential-form" title="forma potencjalna lub rzadka" tabindex="0">biegłobym,<br/>[[być|byłobym]]  biegło</span></td></tr><tr><th rowspan="3">[[imiesłów przymiotnikowy czynny]]</th></tr><tr><th>''ż''</th><td colspan="3">biegnąca, niebiegnąca </td><td rowspan="2" colspan="3">biegnące, niebiegnące </td></tr><tr><th rowspan="1">''n''</th></tr></table></td></tr></table></div></div>""",
        )
        self.wxr.wtp.start_page("biec")
        root = self.wxr.wtp.parse(
            "===odmiana===\n {{odmiana-czasownik-polski}}"
        )
        page_data = [
            WordEntry(
                word="biec",
                lang="język polski",
                lang_code="pl",
                pos="verb",
                senses=[Sense(sense_index="1.1")],
            ),
        ]
        extract_inflection_section(self.wxr, page_data, "pl", root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[0].forms],
            [
                {
                    "form": "biegnięto",
                    "tags": [
                        "singular",
                        "plural",
                        "first-person",
                        "second-person",
                        "third-person",
                        "impersonal",
                        "past",
                    ],
                },
                {
                    "form": "biegłbym",
                    "tags": [
                        "singular",
                        "first-person",
                        "conditional",
                        "masculine",
                    ],
                },
                {
                    "form": "biegłobym",
                    "tags": [
                        "singular",
                        "first-person",
                        "conditional",
                        "neuter",
                        "potential",
                        "rare",
                    ],
                },
                {
                    "form": "byłobym biegło",
                    "tags": [
                        "singular",
                        "first-person",
                        "conditional",
                        "neuter",
                        "potential",
                        "rare",
                    ],
                },
                {
                    "form": "biegnąca",
                    "tags": [
                        "singular",
                        "first-person",
                        "second-person",
                        "third-person",
                        "active",
                        "participle",
                        "feminine",
                    ],
                },
                {
                    "form": "niebiegnąca",
                    "tags": [
                        "singular",
                        "first-person",
                        "second-person",
                        "third-person",
                        "active",
                        "participle",
                        "feminine",
                    ],
                },
                {
                    "form": "biegnące",
                    "tags": [
                        "plural",
                        "first-person",
                        "second-person",
                        "third-person",
                        "active",
                        "participle",
                        "feminine",
                        "neuter",
                    ],
                },
                {
                    "form": "niebiegnące",
                    "tags": [
                        "plural",
                        "first-person",
                        "second-person",
                        "third-person",
                        "active",
                        "participle",
                        "feminine",
                        "neuter",
                    ],
                },
            ],
        )

    def test_eo_noun_table(self):
        self.wxr.wtp.add_page(
            "Szablon:odmiana-rzeczownik-esperanto",
            10,
            """<span class="short-container<nowiki/> short-variant1">[[Aneks:Skróty używane w Wikisłowniku#B|<span class="short-wrapper" title="bez liczby mnogiej" data-expanded="bez liczby mnogiej"><span class="short-content">blm</span></span>]]</span>,&nbsp;<div><div>&nbsp;</div><div><table class="wikitable odmiana"><tr><th>&nbsp;</th><th>[[ununombro#eo|ununombro]]</th><th>[[multenombro#eo|multenombro]]&#32;([[virtuala#eo|virtuala]])</th></tr><tr><th>[[nominativo#eo|nominativo]]</th><td>'''neĝo'''</td><td>'''<span class="potential-form" title="forma potencjalna lub rzadka" tabindex="0">neĝoj</span>'''</td></tr><tr><th>[[akuzativo#eo|akuzativo]]</th><td>neĝon</td><td><span class="potential-form" title="forma potencjalna lub rzadka" tabindex="0">neĝojn</span></td></tr></table></div></div>""",
        )
        self.wxr.wtp.start_page("neĝo")
        root = self.wxr.wtp.parse(
            ": (1.2) {{odmiana-rzeczownik-esperanto|blm}}"
        )
        page_data = [
            WordEntry(
                word="neĝo",
                lang="esperanto",
                lang_code="eo",
                pos="verb",
                senses=[Sense(sense_index="1.1")],
            ),
        ]
        extract_inflection_section(self.wxr, page_data, "eo", root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[0].forms],
            [
                {
                    "form": "neĝoj",
                    "sense_index": "1.2",
                    "tags": [
                        "no-plural",
                        "potential",
                        "rare",
                        "nominative",
                        "plural",
                        "virtual",
                    ],
                },
                {
                    "form": "neĝon",
                    "sense_index": "1.2",
                    "tags": ["no-plural", "accusative", "singular"],
                },
                {
                    "form": "neĝojn",
                    "sense_index": "1.2",
                    "tags": [
                        "no-plural",
                        "potential",
                        "rare",
                        "accusative",
                        "plural",
                        "virtual",
                    ],
                },
            ],
        )

    def test_ptrad(self):
        self.wxr.wtp.start_page("银行")
        root = self.wxr.wtp.parse("===zapis===\n {{ptrad|銀行}}")
        base_data = WordEntry(
            word="银行",
            lang="język chiński standardowy",
            lang_code="zh",
            pos="noun",
        )
        extract_zapis_section(self.wxr, base_data, root.children[0])
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in base_data.forms],
            [{"form": "銀行", "tags": ["Traditional Chinese"]}],
        )

    def test_transliteracja_section(self):
        self.wxr.wtp.start_page("開く")
        root = self.wxr.wtp.parse("""===transliteracja===
: (1.1) aku""")
        base_data = WordEntry(
            word="開く",
            lang="język japoński",
            lang_code="ja",
            pos="verb",
        )
        extract_transliteracja_section(self.wxr, base_data, root.children[0])
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in base_data.forms],
            [{"form": "aku", "sense_index": "1.1", "tags": ["romanization"]}],
        )

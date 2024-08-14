from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.inflection import extract_inflection_section
from wiktextract.extractor.pl.models import Sense, WordEntry
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
        self.wxr.wtp.add_page(
            "Szablon:odmiana-rzeczownik-polski",
            10,
            """<div><table class="wikitable odmiana"><tr><th class="forma">[[przypadek#pl|przypadek]]</th><th>[[liczba pojedyncza#pl|liczba pojedyncza]]</th><th style="font-weight:normal" >[[liczba mnoga#pl|liczba mnoga]]</th></tr><tr class="forma"><td class="forma">[[mianownik#pl|mianownik]]</td><td class="mianownik" >pies</td><td class="mianownik" >psy</td></tr><tr class="forma"><td class="forma">[[biernik#pl|biernik]]</td><td  >psa</td><td  >psy / psów</td></tr></table></div>""",
        )
        self.wxr.wtp.start_page("pies")
        root = self.wxr.wtp.parse(": (2.1-3) {{odmiana-rzeczownik-polski}}")
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
                    "tags": ["plural", "nominative"],
                    "sense_index": "2.1-3",
                },
                {
                    "form": "psa",
                    "tags": ["singular", "accusative"],
                    "sense_index": "2.1-3",
                },
                {
                    "form": "psy",
                    "tags": ["plural", "accusative"],
                    "sense_index": "2.1-3",
                },
                {
                    "form": "psów",
                    "tags": ["plural", "accusative"],
                    "sense_index": "2.1-3",
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

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
                    "raw_tags": ["liczba mnoga", "mianownik"],
                    "sense_index": "2.1-3",
                },
                {
                    "form": "psa",
                    "raw_tags": ["liczba pojedyncza", "biernik"],
                    "sense_index": "2.1-3",
                },
                {
                    "form": "psy",
                    "raw_tags": ["liczba mnoga", "biernik"],
                    "sense_index": "2.1-3",
                },
                {
                    "form": "psów",
                    "raw_tags": ["liczba mnoga", "biernik"],
                    "sense_index": "2.1-3",
                },
            ],
        )

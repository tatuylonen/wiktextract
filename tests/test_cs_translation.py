from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.cs.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestCsTranslation(TestCase):
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

    def test_tr_list(self):
        self.wxr.wtp.add_page(
            "Šablona:Překlady",
            10,
            """{{#switch:{{{význam}}}
| společenství potomků jedněch rodičů = <div class="translations"><dfn>společenství potomků jedněch rodičů</dfn><ul><li style="page-break-inside: avoid;">němčina: <span class="translation-item" lang="de" dir="ltr">[[Geschlecht#němčina|Geschlecht]]</span>&nbsp;<abbr class="genus" title="neutrum (střední rod)">s</abbr>[[Kategorie:Monitoring:P/1/de]], <span class="translation-item" lang="de" dir="ltr">[[Haus#němčina|Haus]]</span>&nbsp;<abbr class="genus" title="neutrum (střední rod)">s</abbr>[[Kategorie:Monitoring:P/1/de]]</li></ul></div>
| #default = <div class="translations"><dfn>sociálněekonomická skupina lidí blízkých narozením</dfn><ul><li style="page-break-inside: avoid;">němčina: <span class="translation-item" lang="de" dir="ltr">[[Stamm#němčina|Stamm]]</span>&nbsp;<abbr class="genus" title="maskulinum (mužský rod)">m</abbr>[[Kategorie:Monitoring:P/1/de]]</li></ul></div>
}}""",
        )
        data = parse_page(
            self.wxr,
            "rod",
            """==čeština==
===podstatné jméno===
# gloss
====překlady====
# {{Překlady
  | význam = společenství potomků jedněch rodičů
  | de = {{P|de|Geschlecht|n}}, {{P|de|Haus|n}}
}}
# {{Překlady
  | význam = sociálněekonomická skupina lidí blízkých narozením
  | de = {{P|de|Stamm|m}}
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "němčina",
                    "lang_code": "de",
                    "tags": ["neuter"],
                    "sense": "společenství potomků jedněch rodičů",
                    "sense_index": 1,
                    "word": "Geschlecht",
                },
                {
                    "lang": "němčina",
                    "lang_code": "de",
                    "tags": ["neuter"],
                    "sense": "společenství potomků jedněch rodičů",
                    "sense_index": 1,
                    "word": "Haus",
                },
                {
                    "lang": "němčina",
                    "lang_code": "de",
                    "tags": ["masculine"],
                    "sense": "sociálněekonomická skupina lidí blízkých narozením",
                    "sense_index": 2,
                    "word": "Stamm",
                },
            ],
        )
        self.assertEqual(data[0]["categories"], ["Monitoring:P/1/de"])

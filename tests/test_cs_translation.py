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

    def test_multi_word_translation(self):
        self.wxr.wtp.add_page(
            "Šablona:Překlady",
            10,
            """<div class="translations"><dfn>mající nízkou finanční hodnotu</dfn><ul><li style="page-break-inside: avoid;">francouzština: <span class="translation-item" lang="fr" dir="ltr">[[peu#francouzština|peu]]</span>[[Kategorie:Monitoring:P/1/fr]] <span class="translation-item" lang="fr" dir="ltr">[[cher#francouzština|cher]]</span>[[Kategorie:Monitoring:P/1/fr]], <span class="translation-item" lang="fr" dir="ltr">[[pas#francouzština|pas]]</span>[[Kategorie:Monitoring:P/1/fr]] <span class="translation-item" lang="fr" dir="ltr">[[cher#francouzština|cher]]</span>[[Kategorie:Monitoring:P/1/fr]], <span class="translation-item" lang="fr" dir="ltr">[[bon marché#francouzština|bon marché]]</span>[[Kategorie:Monitoring:P/1/fr]]</li></ul></div>""",
        )
        data = parse_page(
            self.wxr,
            "levný",
            """==čeština==
===přídavné jméno===
# gloss
====překlady====
# {{Překlady
  | význam = mající nízkou finanční hodnotu
  | fr = {{P|fr|peu}} {{P|fr|cher}}, {{P|fr|pas}} {{P|fr|cher}}, {{P|fr|bon marché}}
}}""",
        )
        self.assertEqual(
            [t["word"] for t in data[0]["translations"]],
            ["peu cher", "pas cher", "bon marché"],
        )

    def test_multi_word_translation_gender(self):
        self.wxr.wtp.add_page(
            "Šablona:Překlady",
            10,
            """<div class="translations"><dfn>test</dfn><ul><li style="page-break-inside: avoid;">francouzština: <span class="translation-item" lang="fr" dir="ltr">[[soupe#francouzština|soupe]]</span>&nbsp;<abbr class="genus" title="femininum (ženský rod)">ž</abbr>[[Kategorie:Monitoring:P/1/fr]] <span class="translation-item" lang="fr" dir="ltr">[[à#francouzština|à]]</span>[[Kategorie:Monitoring:P/1/fr]] <span class="translation-item" lang="fr" dir="ltr">[[l’oignon#francouzština|l’oignon]]</span>[[Kategorie:Monitoring:P/1/fr]], <span class="translation-item" lang="fr" dir="ltr">[[une#francouzština|une]]</span>[[Kategorie:Monitoring:P/1/fr]] <span class="translation-item" lang="fr" dir="ltr">[[fois#francouzština|fois]]</span>&nbsp;<abbr class="genus" title="femininum (ženský rod)">ž</abbr>[[Kategorie:Monitoring:P/1/fr]]</li></ul></div>""",
        )
        data = parse_page(
            self.wxr,
            "test",
            """==čeština==
===podstatné jméno===
# gloss
====překlady====
# {{Překlady
  | význam = test
  | fr = {{P|fr|soupe|f}} {{P|fr|à}} {{P|fr|l’oignon}}, {{P|fr|une}} {{P|fr|fois|f}}
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "francouzština",
                    "lang_code": "fr",
                    "tags": ["feminine"],
                    "sense": "test",
                    "sense_index": 1,
                    "word": "soupe à l’oignon",
                },
                {
                    "lang": "francouzština",
                    "lang_code": "fr",
                    "sense": "test",
                    "sense_index": 1,
                    "word": "une fois",
                },
            ],
        )

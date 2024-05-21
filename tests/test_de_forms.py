from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.inflection import extract_forms
from wiktextract.extractor.de.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestDeForms(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_noun_table(self):
        self.wxr.wtp.start_page("Wörterbuch")
        self.wxr.wtp.add_page(
            "Vorlage:Deutsch Substantiv Übersicht",
            10,
            """{|
! style="width: 65px;" |
! [[Hilfe:Singular|Singular]]
! [[Hilfe:Plural|Plural]]
|-
! style="text-align:left;" | [[Hilfe:Genitiv|Genitiv]]
| des [[Wörterbuches|Wörterbuches]]<br />des [[Wörterbuchs|Wörterbuchs]]
| der [[Wörterbücher|Wörterbücher]]
|}""",
        )
        root = self.wxr.wtp.parse("{{Deutsch Substantiv Übersicht}}")
        word_entry = WordEntry(
            word="Wörterbuch", lang="Deutsch", lang_code="de"
        )
        extract_forms(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "des Wörterbuches", "tags": ["genitive", "singular"]},
                {"form": "des Wörterbuchs", "tags": ["genitive", "singular"]},
                {"form": "der Wörterbücher", "tags": ["genitive", "plural"]},
            ],
        )

    def test_adj_flexion_page(self):
        self.wxr.wtp.start_page("arm")
        self.wxr.wtp.add_page(
            "Vorlage:Deutsch Adjektiv Übersicht",
            10,
            """{|
! [[Hilfe:Positiv|Positiv]]
! [[Hilfe:Komparativ|Komparativ]]
! [[Hilfe:Superlativ|Superlativ]]
|- align="center"
| arm
| [[ärmer|ärmer]]
| am&#32;[[ärmsten|ärmsten]]
|-
! colspan="5" | ''All other forms:'' [[Flexion:arm|Flexion:arm]]
|}""",
        )
        self.wxr.wtp.add_page(
            "Flexion:arm",
            108,
            """== arm (Deklination) ({{Adjektivdeklination|Deutsch}}) ==
{{Deklinationsseite Adjektiv
|Positiv-Stamm=arm
|Komparativ-Stamm=ärmer
|Superlativ-Stamm=ärmst
}}""",
        )
        self.wxr.wtp.add_page(
            "Vorlage:Deklinationsseite Adjektiv",
            10,
            """<h4>[[Hilfe:Positiv|Positiv]]</h4>
{|
! colspan="9" | [[Hilfe:Deklination|Schwache Deklination]]
|-
! rowspan="3" |
! colspan="6" | [[Hilfe:Singular|Singular]]
! colspan="2" | [[Hilfe:Plural|Plural]]
|-
! colspan="2" | [[Hilfe:Maskulinum|Maskulinum]]
! colspan="2" | [[Hilfe:Femininum|Femininum]]
! colspan="2" | [[Hilfe:Neutrum|Neutrum]]
! colspan="2" | —
|-
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
|-
! [[Hilfe:Nominativ|Nominativ]]
| der
| [[arme]]
| die
| [[arme]]
| das
| [[arme]]
| die
| [[armen]]
|-
! colspan="9" | [[Hilfe:Prädikativ|Prädikativ]]
|-
! rowspan="3" |
! colspan="6" | [[Hilfe:Singular|Singular]]
! colspan="2" | [[Hilfe:Plural|Plural]]
|-
! colspan="2" | [[Hilfe:Maskulinum|Maskulinum]]
! colspan="2" | [[Hilfe:Femininum|Femininum]]
! colspan="2" | [[Hilfe:Neutrum|Neutrum]]
! colspan="2" | —
|-
| colspan="2" | er ist [[arm]]
| colspan="2" | sie ist [[arm]]
| colspan="2" | es ist [[arm]]
| colspan="2" | sie sind [[arm]]
|}""",
        )
        root = self.wxr.wtp.parse("{{Deutsch Adjektiv Übersicht}}")
        word_entry = WordEntry(
            word="arm", lang="Deutsch", lang_code="de", pos="adj"
        )
        extract_forms(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "arm", "tags": ["positive"]},
                {"form": "ärmer", "tags": ["comparative"]},
                {"form": "am ärmsten", "tags": ["superlative"]},
                {
                    "form": "der arme",
                    "tags": [
                        "positive",
                        "nominative",
                        "weak",
                        "singular",
                        "masculine",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "die arme",
                    "tags": [
                        "positive",
                        "nominative",
                        "weak",
                        "singular",
                        "feminine",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "das arme",
                    "tags": [
                        "positive",
                        "nominative",
                        "weak",
                        "singular",
                        "neuter",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "die armen",
                    "tags": ["positive", "nominative", "weak", "plural"],
                    "source": "Flexion:arm",
                },
                {
                    "form": "er ist arm",
                    "tags": [
                        "positive",
                        "predicative",
                        "singular",
                        "masculine",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "sie ist arm",
                    "tags": ["positive", "predicative", "singular", "feminine"],
                    "source": "Flexion:arm",
                },
                {
                    "form": "es ist arm",
                    "tags": ["positive", "predicative", "singular", "neuter"],
                    "source": "Flexion:arm",
                },
                {
                    "form": "sie sind arm",
                    "tags": ["positive", "predicative", "plural"],
                    "source": "Flexion:arm",
                },
            ],
        )

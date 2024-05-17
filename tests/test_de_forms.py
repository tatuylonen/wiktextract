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

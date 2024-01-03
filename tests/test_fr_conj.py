from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.conjugation import extract_conjugation
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestNotes(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_fr_conj_1(self):
        self.wxr.wtp.start_page("lancer")
        self.wxr.wtp.add_page(
            "Conjugaison:français/lancer", 116, "{{fr-conj-1-cer|lan|lɑ̃}}"
        )
        self.wxr.wtp.add_page(
            "Modèle:fr-conj-1-cer",
            10,
            """<h3> Modes impersonnels </h3>
<div>
{|
|-[[mode|Mode]]
!colspan=\"3\"|[[présent|Présent]]
!colspan=\"3\"|[[passé|Passé]]
|-
|'''[[infinitif|Infinitif]]'''
|&nbsp;&nbsp;
|[[lancer]]
|<span>\\lɑ̃.se\\</span>
|avoir
|[[lancé]]
|<span>\\a.vwaʁ<nowiki> </nowiki>lɑ̃.se\\</span>
|}
</div>""",
        )
        entry = WordEntry(lang_code="fr", lang_name="Français", word="lancer")
        extract_conjugation(self.wxr, entry)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in entry.forms],
            [
                {
                    "form": "lancer",
                    "ipas": ["\\lɑ̃.se\\"],
                    "source": "Conjugaison page",
                    "tags": ["Modes impersonnels", "Infinitif", "Présent"],
                },
                {
                    "form": "avoir lancé",
                    "ipas": ["\\a.vwaʁ lɑ̃.se\\"],
                    "source": "Conjugaison page",
                    "tags": ["Modes impersonnels", "Infinitif", "Passé"],
                },
            ],
        )

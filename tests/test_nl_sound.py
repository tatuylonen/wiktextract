from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlSound(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="nl"),
            WiktionaryConfig(
                dump_file_lang_code="nl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_common_lists(self):
        self.wxr.wtp.add_page("Sjabloon:pn", 10, "hond")
        self.wxr.wtp.add_page(
            "Sjabloon:pron-reg",
            10,
            "''([[WikiWoordenboek:Uitspraakverschillen binnen het Nederlandse taalgebied|Vlaanderen]], [[WikiWoordenboek:Uitspraakverschillen binnen het Nederlandse taalgebied|Brabant]])'':",
        )
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
=====Uitspraak=====
*{{sound}}: {{audio|nl-{{pn}}.ogg|{{pn}}|nld}}
*{{WikiW|IPA}}: {{IPA-nl-standaard|hɔnt}}
**{{pron-reg|V=a}} {{IPA|/ˈɦɔnt/|nld}}
====Zelfstandig naamwoord====
# zoogdier
            """,
        )
        self.assertEqual(len(data[0]["sounds"]), 3)
        self.assertEqual(data[0]["sounds"][0]["audio"], "nl-hond.ogg")
        self.assertEqual(data[0]["sounds"][1], {"ipa": "hɔnt"})
        self.assertEqual(
            data[0]["sounds"][2],
            {"ipa": "/ˈɦɔnt/", "raw_tags": ["Vlaanderen", "Brabant"]},
        )

    def test_hyphenation(self):
        data = parse_page(
            self.wxr,
            "lopen",
            """==Nederlands==
=====Woordafbreking=====
*lo·pen
====Werkwoord====
# stappen""",
        )
        self.assertEqual(data[0]["hyphenations"], [{"parts": ["lo", "pen"]}])

    def test_sound_section(self):
        data = parse_page(
            self.wxr,
            "vin",
            """==Deens==
===Zelfstandig naamwoord===
# [[wijn]]

==Frans==
===Uitspraak===
*{{sound}}: {{audio|Fr-vin.ogg|vin|fra}}
===Zelfstandig naamwoord===
# [[wijn]]""",
        )
        self.assertTrue("sounds" not in data[0])
        self.assertTrue("sounds" in data[1])

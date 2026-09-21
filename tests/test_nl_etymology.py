from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlEtymology(TestCase):
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

    def test_two_lists(self):
        self.wxr.wtp.add_page(
            "Sjabloon:erfwoord",
            10,
            """[[WikiWoordenboek:Erfwoord|<span>erfwoord</span>]][[Categorie:Erfwoord_in_het_Nederlands]]""",
        )
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
=====Woordherkomst en -opbouw=====
*[A] {{erfwoord|nld}}, uiteindelijk te herleiden tot Indo-Europees *ḱun-to-.
*[B] Van Latijn centum (zie ook honderd).
*{{((}}
*{{erfwoord|nld}} afkomstig van:
:{{dum}}: ''{{Q|hont|dum}}''
{{))}}
====Zelfstandig naamwoord====
[A] {{-l-|m}}
# zoogdier uit de familie van de hondachtigen
====Zelfstandig naamwoord====
[B] {{-l-|o}}
# [[landmaat]] ter waarde van 100""",
        )
        self.assertEqual(data[0]["categories"], ["Erfwoord_in_het_Nederlands"])
        self.assertEqual(
            data[0]["etymology_texts"],
            ["erfwoord, uiteindelijk te herleiden tot Indo-Europees *ḱun-to-."],
        )
        self.assertEqual(
            data[1]["etymology_texts"], ["Van Latijn centum (zie ook honderd)."]
        )

    def test_links_follow_etymology_indices_and_language(self):
        self.wxr.wtp.add_page(
            "Sjabloon:herkomst-test",
            10,
            "[[canis#Latijn|canis]][[Categorie:Latijnse herkomst]]",
        )
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
=====Woordherkomst en -opbouw=====
*[A] Uit {{herkomst-test}} en [[canis#Latijn|canis]].
*[B] Uit [[centum#Latijn|centum]].
====Zelfstandig naamwoord====
[A] {{-l-|m}}
# Een dier.
====Zelfstandig naamwoord====
[B] {{-l-|o}}
# Een landmaat.
====Werkwoord====
[C]
# Andere betekenis.
==Engels==
====Zelfstandig naamwoord====
# Other meaning.""",
        )
        self.assertEqual(
            data[0]["etymology_links"],
            [("canis", "canis#Latijn"), ("canis", "canis#Latijn")],
        )
        self.assertEqual(
            data[1]["etymology_links"], [("centum", "centum#Latijn")]
        )
        self.assertNotIn("etymology_links", data[2])
        self.assertNotIn("etymology_links", data[3])
        self.assertEqual(data[0]["categories"], ["Latijnse herkomst"])
        self.assertNotIn("categories", data[1])

    def test_unindexed_links_apply_to_each_pos(self):
        data = parse_page(
            self.wxr,
            "test",
            """==Nederlands==
=====Woordherkomst en -opbouw=====
* Uit [[test#Engels|test]].
====Zelfstandig naamwoord====
# Een test.
====Werkwoord====
# Testen.""",
        )
        self.assertEqual(len(data), 2)
        for entry in data:
            self.assertEqual(
                entry["etymology_links"], [("test", "test#Engels")]
            )

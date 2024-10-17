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

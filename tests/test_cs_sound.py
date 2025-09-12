from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.cs.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestCsSound(TestCase):
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

    def test_sound_list(self):
        self.wxr.wtp.add_page(
            "Šablona:IPA",
            10,
            """[[Wikislovník:Výslovnost|IPA]]: <span title="Toto je transkripce výslovnosti pomocí mezinárodní fonetické abecedy IPA." class="IPA" >[ˈmɔnːdɑːg]</span>""",
        )
        data = parse_page(
            self.wxr,
            "måndag",
            """== švédština ==
=== výslovnost ===
* {{IPA|ˈmɔnːdɑːg}}, ''hovorově'' [{{IPA2|ˈmɔnːda}}], {{Audio|Sv-måndag.ogg|måndag}}
=== podstatné jméno ===
==== význam ====
# [[pondělí]]""",
        )
        self.assertEqual(
            data[0]["sounds"][:2],
            [
                {"ipa": "[ˈmɔnːdɑːg]"},
                {"ipa": "[ˈmɔnːda]", "raw_tags": ["hovorově"]},
            ],
        )
        self.assertEqual(data[0]["sounds"][2]["audio"], "Sv-måndag.ogg")

    def test_hyphenation(self):
        data = parse_page(
            self.wxr,
            "dělení",
            """== čeština ==
=== dělení ===
* dě-le-ní
=== podstatné jméno ===
==== význam ====
# [[proces]]""",
        )
        self.assertEqual(
            data[0]["hyphenations"], [{"parts": ["dě", "le", "ní"]}]
        )

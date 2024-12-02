import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestDEPronunciation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_normal_page(self):
        self.wxr.wtp.add_page(
            "Vorlage:Audio",
            10,
            """[[Datei:Loudspeaker.svg|15px|Lautsprecherbild|link=]]<span class="aplay">&nbsp;</span>[[Media:De-at-Hund.ogg|Hund&nbsp;(Österreich)]]<sup>&nbsp;([[:Datei:De-at-Hund.ogg|Info]])</sup>[[Kategorie:Wiktionary:Audio-Datei]]""",
        )
        data = parse_page(
            self.wxr,
            "Hund",
            """== Hund ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{m}} ===
==== Aussprache ====
:{{IPA}} {{Lautschrift|hʊnt}}
:{{Hörbeispiele}} {{Audio|De-at-Hund.ogg|spr=at}}
:{{Reime}} {{Reim|ʊnt|Deutsch}}
==== Bedeutungen ====
:[1] [[Haustier]]""",
        )
        self.assertEqual(data[0]["sounds"][0], {"ipa": "hʊnt"})
        self.assertEqual(data[0]["sounds"][1]["audio"], "De-at-Hund.ogg")
        self.assertEqual(data[0]["sounds"][1]["tags"], ["Austrian German"])
        self.assertEqual(data[0]["sounds"][2], {"rhymes": "ʊnt"})

    def test_nested_lists(self):
        data = parse_page(
            self.wxr,
            "Garage",
            """== Garage ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{f}} ===
==== Aussprache ====
:{{IPA}}
::''[[Deutschland]]:'' {{Lautschrift|ɡaˈʁaːʒə}}
==== Bedeutungen ====
:[1] [[Raum]]""",
        )
        self.assertEqual(
            data[0]["sounds"][0], {"ipa": "ɡaˈʁaːʒə", "tags": ["Germany"]}
        )

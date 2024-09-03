# Tests for parsing a page from the German Wiktionary

import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestDEPage(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de", capture_language_codes=None
            ),
        )
        self.maxDiff = None

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_de_parse_page(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "")
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "")
        lst = parse_page(
            self.wxr,
            "Beispiel",
            """== Beispiel ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}} ===
""",
        )
        self.assertEqual(
            lst,
            [
                {
                    "lang": "Deutsch",
                    "lang_code": "de",
                    "word": "Beispiel",
                    "pos": "noun",
                    "senses": [{"tags": ["no-gloss"]}],
                }
            ],
        )

    def test_de_parse_page_skipping_head_templates(self):
        self.wxr.wtp.add_page("Vorlage:Wort der Woche", 10, "")
        self.wxr.wtp.add_page("Vorlage:Siehe auch", 10, "")
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "")
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "")
        lst = parse_page(
            self.wxr,
            "Beispiel",
            """{{Wort der Woche|46|2020}}
{{Siehe auch|[[cát]]}}
== Beispiel ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}} ===
""",
        )
        self.assertEqual(
            lst,
            [
                {
                    "lang": "Deutsch",
                    "lang_code": "de",
                    "word": "Beispiel",
                    "pos": "noun",
                    "senses": [{"tags": ["no-gloss"]}],
                }
            ],
        )

    def test_multiple_pos(self):
        self.wxr.wtp.add_page("Vorlage:n", 10, "n")
        self.wxr.wtp.start_page("Griechenland")
        self.assertEqual(
            parse_page(
                self.wxr,
                "Griechenland",
                """== Griechenland ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{n}}, {{Wortart|Toponym|Deutsch}} ===
====Bedeutungen====
:[1] [[Staat]] in [[Südosteuropa]], im [[Süden]] der [[Balkanhalbinsel]]""",
            ),
            [
                {
                    "lang": "Deutsch",
                    "lang_code": "de",
                    "pos": "noun",
                    "other_pos": ["name"],
                    "senses": [
                        {
                            "glosses": [
                                "Staat in Südosteuropa, im Süden der "
                                "Balkanhalbinsel"
                            ],
                            "sense_index": "1",
                        }
                    ],
                    "word": "Griechenland",
                    "tags": ["neuter"],
                }
            ],
        )

    def test_umschrift(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "{{{1}}}")
        self.wxr.wtp.start_page("iku")
        self.assertEqual(
            parse_page(
                self.wxr,
                "iku",
                """== hiki ({{Sprache|Umschrift}}) ==
{{Ähnlichkeiten Umschrift
|1=行く|spr1=ja
|2=幾|spr2=ja
|3=𒃷#𒃷 (iku) (Sumerisch)|spr3=sux|link3=𒃷
}}""",
            ),
            [
                {
                    "lang_code": "unknown",
                    "lang": "Umschrift",
                    "pos": "soft-redirect",
                    "redirects": ["行く", "幾", "𒃷"],
                    "senses": [{"tags": ["no-gloss"]}],
                    "word": "iku",
                }
            ],
        )

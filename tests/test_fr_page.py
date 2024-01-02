# Tests for parsing a page
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestFrPage(TestCase):
    def setUp(self):
        self.maxDiff = None
        conf1 = WiktionaryConfig(
            dump_file_lang_code="fr",
            capture_language_codes=None,
        )
        self.wxr = WiktextractContext(Wtp(lang_code="fr"), conf1)

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_fr_parse_page(self):
        # https://fr.wiktionary.org/wiki/anthracite
        self.wxr.wtp.add_page(
            "Modèle:langue",
            10,
            "{{#switch: {{{1}}} | fr = Français | en = Anglais }}",
        )
        self.wxr.wtp.add_page(
            "Modèle:S",
            10,
            """{{#switch: {{{1}}}
| étymologie = Étymologie
| nom = Nom commun
| adjectif = Adjectif
}}""",
        )
        self.wxr.wtp.add_page("Modèle:roches", 10, "''(Pétrographie)''")
        self.wxr.wtp.add_page("Modèle:indénombrable", 10, "''(Indénombrable)''")

        page_data = parse_page(
            self.wxr,
            "anthracite",
            """== {{langue|fr}} ==
=== {{S|étymologie}} ===
: (1549) Du latin anthracites.

=== {{S|nom|fr}} ===
# {{roches|fr}} [[variété|Variété]] de [[charbon de terre]], à [[reflet]] [[métallique]] et à [[combustion]] [[lent]]e.

=== {{S|adjectif|fr}} ===
# De couleur anthracite, gris très foncé, du nom de la variété de charbon du même nom.

== {{langue|en}} ==

=== {{S|étymologie}} ===
: Du latin anthracites.

=== {{S|nom|en}} ===
# {{indénombrable|en}} [[anthracite#fr|Anthracite]].""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "lang_name": "Français",
                    "lang_code": "fr",
                    "pos": "noun",
                    "pos_title": "Nom commun",
                    "word": "anthracite",
                    "senses": [
                        {
                            "glosses": [
                                "Variété de charbon de terre, à reflet métallique et à combustion lente."
                            ],
                            "tags": ["Pétrographie"],
                        }
                    ],
                    "etymology_texts": ["(1549) Du latin anthracites."],
                },
                {
                    "lang_name": "Français",
                    "lang_code": "fr",
                    "pos": "adj",
                    "pos_title": "Adjectif",
                    "word": "anthracite",
                    "senses": [
                        {
                            "glosses": [
                                "De couleur anthracite, gris très foncé, du nom de la variété de charbon du même nom."
                            ]
                        }
                    ],
                    "etymology_texts": ["(1549) Du latin anthracites."],
                },
                {
                    "lang_name": "Anglais",
                    "lang_code": "en",
                    "pos": "noun",
                    "pos_title": "Nom commun",
                    "word": "anthracite",
                    "senses": [
                        {"glosses": ["Anthracite."], "tags": ["Indénombrable"]}
                    ],
                    "etymology_texts": ["Du latin anthracites."],
                },
            ],
        )

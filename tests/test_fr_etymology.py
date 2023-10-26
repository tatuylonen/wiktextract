import unittest
from collections import defaultdict

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.etymology import (
    extract_etymology,
    insert_etymology_data,
)
from wiktextract.wxr_context import WiktextractContext


class TestEtymology(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_ebauche_etym(self):
        # https://fr.wiktionary.org/wiki/Hörsaal
        # missing etymology template "ébauche-étym" should be ignored
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(": {{ébauche-étym|de}}")
        etymology_data = extract_etymology(self.wxr, root.children)
        self.assertIsNone(etymology_data)

    def test_list_etymologies(self):
        # https://fr.wiktionary.org/wiki/lenn
        self.wxr.wtp.start_page("lenn")
        root = self.wxr.wtp.parse(
            """* [[#br-nom-1|Nom commun 1 :]]
: Du vieux breton lin (« lac, étang ; liquide, humeur »).
: Du moyen breton lenn.
* [[#br-nom-2|Nom commun 2 :]]
:Du vieux breton lenn (« pièce de toile, voile, manteau, rideau »)."""
        )
        etymology_data = extract_etymology(self.wxr, root.children)
        self.assertEqual(
            etymology_data,
            {
                "Nom commun 1": [
                    "Du vieux breton lin (« lac, étang ; liquide, humeur »).",
                    "Du moyen breton lenn.",
                ],
                "Nom commun 2": [
                    "Du vieux breton lenn (« pièce de toile, voile, manteau, rideau »)."
                ],
            },
        )
        page_data = [
            defaultdict(
                list,
                {"lang_code": "fr", "pos": "noun", "pos_title": "Nom commun 1"},
            ),
            defaultdict(
                list,
                {"lang_code": "fr", "pos": "noun", "pos_title": "Nom commun 2"},
            ),
        ]
        insert_etymology_data("fr", page_data, etymology_data)
        self.assertEqual(
            page_data,
            [
                {
                    "lang_code": "fr",
                    "pos": "noun",
                    "pos_title": "Nom commun 1",
                    "etymology_texts": [
                        "Du vieux breton lin (« lac, étang ; liquide, humeur »).",
                        "Du moyen breton lenn.",
                    ],
                },
                {
                    "lang_code": "fr",
                    "pos": "noun",
                    "pos_title": "Nom commun 2",
                    "etymology_texts": [
                        "Du vieux breton lenn (« pièce de toile, voile, manteau, rideau »)."
                    ],
                },
            ],
        )

    def test_indent_etymology_with_pos_template(self):
        # https://fr.wiktionary.org/wiki/dame
        self.wxr.wtp.start_page("dame")
        self.wxr.wtp.add_page("Modèle:lien-ancre-étym", 10, "({{{2}}} {{{3}}})")
        root = self.wxr.wtp.parse(
            """: {{lien-ancre-étym|fr|Nom commun|1}} Du latin domina (« maîtresse de maison »).
: {{lien-ancre-étym|fr|Nom commun|2}} Du moyen néerlandais dam (« digue »).
: {{lien-ancre-étym|fr|Interjection|1}} Abréviation de « [[Notre-Dame]] ! » ou de « dame Dieu ! » (« [[Seigneur Dieu]] ! »).
"""
        )
        etymology_data = extract_etymology(self.wxr, root.children)
        self.assertEqual(
            etymology_data,
            {
                "Nom commun 1": ["Du latin domina (« maîtresse de maison »)."],
                "Nom commun 2": ["Du moyen néerlandais dam (« digue »)."],
                "Interjection 1": [
                    "Abréviation de « Notre-Dame ! » ou de « dame Dieu ! » (« Seigneur Dieu ! »)."
                ],
            },
        )
        page_data = [
            defaultdict(
                list,
                {"lang_code": "fr", "pos": "noun", "pos_title": "Nom commun 1"},
            ),
            defaultdict(
                list,
                {"lang_code": "fr", "pos": "noun", "pos_title": "Nom commun 2"},
            ),
            defaultdict(
                list,
                {"lang_code": "fr", "pos": "intj", "pos_title": "Interjection"},
            ),
        ]
        insert_etymology_data("fr", page_data, etymology_data)
        self.assertEqual(
            page_data,
            [
                {
                    "lang_code": "fr",
                    "pos": "noun",
                    "pos_title": "Nom commun 1",
                    "etymology_texts": [
                        "Du latin domina (« maîtresse de maison »)."
                    ],
                },
                {
                    "lang_code": "fr",
                    "pos": "noun",
                    "pos_title": "Nom commun 2",
                    "etymology_texts": [
                        "Du moyen néerlandais dam (« digue »)."
                    ],
                },
                {
                    "lang_code": "fr",
                    "pos": "intj",
                    "pos_title": "Interjection",
                    "etymology_texts": [
                        "Abréviation de « Notre-Dame ! » ou de « dame Dieu ! » (« Seigneur Dieu ! »)."
                    ],
                },
            ],
        )

    def test_indent_etymology_with_italic_pos(self):
        # https://fr.wiktionary.org/wiki/hélas
        self.wxr.wtp.start_page("hélas")
        root = self.wxr.wtp.parse(
            """: (''[[#Interjection|Interjection]]'') XIIe siècle, elas ; composé de hé et de las, au sens ancien de « malheureux ».
: (''[[#fr-nom|Nom]]'') Par [[substantivation]] de l’interjection.
"""
        )
        etymology_data = extract_etymology(self.wxr, root.children)
        self.assertEqual(
            etymology_data,
            {
                "Interjection": [
                    "XIIe siècle, elas ; composé de hé et de las, au sens ancien de « malheureux »."
                ],
                "Nom commun": ["Par substantivation de l’interjection."],
            },
        )

    def test_no_list_etymology_block(self):
        self.wxr.wtp.start_page("autrice")
        root = self.wxr.wtp.parse("Paragraph 1\nParagraph 2")
        etymology_data = extract_etymology(self.wxr, root.children)
        self.assertEqual(etymology_data, {None: ["Paragraph 1\nParagraph 2"]})

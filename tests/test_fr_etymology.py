from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.etymology import (
    extract_etymology,
    insert_etymology_data,
)
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestEtymology(TestCase):
    maxDiff = None

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
        etymology_data = extract_etymology(self.wxr, root, None)
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
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("br-nom-1", "Nom commun 1"): [
                    "Du vieux breton lin (« lac, étang ; liquide, humeur »).",
                    "Du moyen breton lenn.",
                ],
                ("br-nom-2", "Nom commun 2"): [
                    "Du vieux breton lenn (« pièce de toile, voile, manteau, rideau »)."
                ],
            },
        )
        page_data = [
            WordEntry(
                word="test",
                lang_code="fr",
                lang="Français",
                pos="noun",
                pos_id="br-nom-1",
                pos_title="Nom commun 1",
            ),
            WordEntry(
                word="test",
                lang_code="fr",
                lang="Français",
                pos="noun",
                pos_title="Nom commun 2",
                pos_id="br-nom-2",
            ),
        ]
        insert_etymology_data("fr", page_data, etymology_data)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "test",
                    "lang_code": "fr",
                    "lang": "Français",
                    "pos": "noun",
                    "pos_title": "Nom commun 1",
                    "pos_id": "br-nom-1",
                    "etymology_texts": [
                        "Du vieux breton lin (« lac, étang ; liquide, humeur »).",
                        "Du moyen breton lenn.",
                    ],
                },
                {
                    "word": "test",
                    "lang_code": "fr",
                    "lang": "Français",
                    "pos": "noun",
                    "pos_title": "Nom commun 2",
                    "pos_id": "br-nom-2",
                    "etymology_texts": [
                        "Du vieux breton lenn (« pièce de toile, voile, manteau, rideau »)."
                    ],
                },
            ],
        )

    def test_indent_etymology_with_pos_template(self):
        # https://fr.wiktionary.org/wiki/dame
        self.wxr.wtp.start_page("dame")
        self.wxr.wtp.add_page(
            "Modèle:lien-ancre-étym",
            10,
            "''([[#{{{1}}}-{{{2}}}-{{{3}}}|{{#switch:{{{2}}}| nom = Nom commun | interj = Interjection}} {{{3}}}]])''",
        )
        root = self.wxr.wtp.parse(
            """: {{lien-ancre-étym|fr|nom|1}} Du latin domina (« maîtresse de maison »).
: {{lien-ancre-étym|fr|nom|2}} Du moyen néerlandais dam (« digue »).
: {{lien-ancre-étym|fr|interj|1}} Abréviation de « [[Notre-Dame]] ! » ou de « dame Dieu ! » (« [[Seigneur Dieu]] ! »).
"""
        )
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("fr-nom-1", "Nom commun 1"): [
                    "Du latin domina (« maîtresse de maison »)."
                ],
                ("fr-nom-2", "Nom commun 2"): [
                    "Du moyen néerlandais dam (« digue »)."
                ],
                ("fr-interj-1", "Interjection 1"): [
                    "Abréviation de « Notre-Dame ! » ou de « dame Dieu ! » (« Seigneur Dieu ! »)."
                ],
            },
        )
        page_data = [
            WordEntry(
                word="test",
                lang_code="fr",
                lang="Français",
                pos="noun",
                pos_title="Nom commun 1",
                pos_id="fr-nom-1",
            ),
            WordEntry(
                word="test",
                lang_code="fr",
                lang="Français",
                pos="noun",
                pos_title="Nom commun 2",
                pos_id="fr-nom-2",
            ),
            WordEntry(
                word="test",
                lang_code="fr",
                lang="Français",
                pos="intj",
                pos_title="Interjection",
                pos_id="fr-interj-1",
            ),
        ]
        insert_etymology_data("fr", page_data, etymology_data)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "test",
                    "lang_code": "fr",
                    "lang": "Français",
                    "pos": "noun",
                    "pos_title": "Nom commun 1",
                    "pos_id": "fr-nom-1",
                    "etymology_texts": [
                        "Du latin domina (« maîtresse de maison »)."
                    ],
                },
                {
                    "word": "test",
                    "lang_code": "fr",
                    "lang": "Français",
                    "pos": "noun",
                    "pos_title": "Nom commun 2",
                    "pos_id": "fr-nom-2",
                    "etymology_texts": [
                        "Du moyen néerlandais dam (« digue »)."
                    ],
                },
                {
                    "word": "test",
                    "lang_code": "fr",
                    "lang": "Français",
                    "pos": "intj",
                    "pos_title": "Interjection",
                    "pos_id": "fr-interj-1",
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
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("Interjection", "Interjection"): [
                    "XIIe siècle, elas ; composé de hé et de las, au sens ancien de « malheureux »."
                ],
                ("fr-nom", "Nom"): ["Par substantivation de l’interjection."],
            },
        )
        page_data = [
            WordEntry(
                word="hélas",
                lang_code="fr",
                lang="Français",
                pos="intj",
                pos_title="Interjection",
                pos_id="fr-interj-1",
            ),
            WordEntry(
                word="hélas",
                lang_code="fr",
                lang="Français",
                pos="noun",
                pos_title="Nom commun",
                pos_id="fr-nom-1",
            ),
        ]
        insert_etymology_data("fr", page_data, etymology_data)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "hélas",
                    "lang_code": "fr",
                    "lang": "Français",
                    "pos": "intj",
                    "pos_title": "Interjection",
                    "pos_id": "fr-interj-1",
                    "etymology_texts": [
                        "XIIe siècle, elas ; composé de hé et de las, au sens ancien de « malheureux »."
                    ],
                },
                {
                    "word": "hélas",
                    "lang_code": "fr",
                    "lang": "Français",
                    "pos": "noun",
                    "pos_title": "Nom commun",
                    "pos_id": "fr-nom-1",
                    "etymology_texts": [
                        "Par substantivation de l’interjection."
                    ],
                },
            ],
        )

    def test_no_list_etymology_block(self):
        self.wxr.wtp.start_page("autrice")
        root = self.wxr.wtp.parse("Paragraph 1\nParagraph 2")
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(etymology_data, {None: ["Paragraph 1\nParagraph 2"]})

    def test_etymology_examples(self):
        self.wxr.wtp.start_page("autrice")
        self.wxr.wtp.add_page("Modèle:S", 10, "Attestations historiques")
        self.wxr.wtp.add_page("Modèle:siècle", 10, "(XVᵉ siècle)")
        root = self.wxr.wtp.parse("""=== {{S|étymologie}} ===
etymology text

==== {{S|attestations}} ====

* {{siècle|XV}} {{exemple|example text
|lang=frm
|source=source text
|pas-trad=1
}}""")
        word_entry = WordEntry(
            lang="Français", lang_code="fr", word="autrice", pos="noun"
        )
        extract_etymology(self.wxr, root, word_entry)
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["etymology_examples"],
            [
                {
                    "time": "XVᵉ siècle",
                    "text": "example text",
                    "ref": "source text",
                }
            ],
        )

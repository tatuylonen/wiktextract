from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.etymology import (
    EtymologyData,
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
        self.assertEqual(len(etymology_data), 0)

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
                ("br-nom-1", "Nom commun 1"): EtymologyData(
                    texts=[
                        "Du vieux breton lin (« lac, étang ; liquide, humeur »).",
                        "Du moyen breton lenn.",
                    ]
                ),
                ("br-nom-2", "Nom commun 2"): EtymologyData(
                    texts=[
                        "Du vieux breton lenn (« pièce de toile, voile, manteau, rideau »)."
                    ]
                ),
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
"""  # noqa:E501
        )
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("fr-nom-1", "Nom commun 1"): EtymologyData(
                    texts=["Du latin domina (« maîtresse de maison »)."]
                ),
                ("fr-nom-2", "Nom commun 2"): EtymologyData(
                    texts=["Du moyen néerlandais dam (« digue »)."]
                ),
                ("fr-interj-1", "Interjection 1"): EtymologyData(
                    texts=[
                        "Abréviation de « Notre-Dame ! » ou de « dame Dieu ! » (« Seigneur Dieu ! »)."
                    ]
                ),
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
"""  # noqa:E501
        )
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("Interjection", "Interjection"): EtymologyData(
                    texts=[
                        "XIIe siècle, elas ; composé de hé et de las, au sens ancien de « malheureux »."
                    ]
                ),
                ("fr-nom", "Nom"): EtymologyData(
                    texts=["Par substantivation de l’interjection."]
                ),
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
        self.assertEqual(
            etymology_data,
            {("", ""): EtymologyData(texts=["Paragraph 1\nParagraph 2"])},
        )

    def test_etymology_examples(self):
        self.wxr.wtp.start_page("autrice")
        self.wxr.wtp.add_page("Modèle:S", 10, "Attestations historiques")
        self.wxr.wtp.add_page("Modèle:siècle", 10, "(XVᵉ siècle)")
        self.wxr.wtp.add_page(
            "Modèle:exemple",
            10,
            "[[Catégorie:Exemples en moyen français avec traduction désactivée]][[Catégorie:Exemples en moyen français]]",
        )
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
        data = word_entry.model_dump(exclude_defaults=True)
        self.assertEqual(
            data["etymology_examples"],
            [
                {
                    "time": "XVᵉ siècle",
                    "text": "example text",
                    "ref": "source text",
                }
            ],
        )
        self.assertEqual(
            data["categories"],
            [
                "Exemples en moyen français avec traduction désactivée",
                "Exemples en moyen français",
            ],
        )

    def test_nata(self):
        self.wxr.wtp.start_page("nata")
        self.wxr.wtp.add_page(
            "Modèle:étyl",
            10,
            """espagnol ''<bdi lang="es" xml:lang="es" class="lang-es">[[nata#es|nata]]</bdi>''[[Catégorie:Mots en français issus d’un mot en espagnol]]""",
        )
        root = self.wxr.wtp.parse(
            """: (''[[#fr-nom-1|Nom commun 1]]'') De l’{{étyl|es|fr|nata}}, « crème », d'origine inconnue.
: (''[[#fr-nom-2|Nom commun 2]]'') {{ébauche-étym|fr}}
: (''[[#fr-nom-3|Nom commun 3]]'') Du kanak de Maré ou nengone nata (« messager ; celui qui raconte »)
"""  # noqa:E501
        )
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("fr-nom-1", "Nom commun 1"): EtymologyData(
                    texts=[
                        "De l’espagnol nata, « crème », d'origine inconnue."
                    ],
                    categories=["Mots en français issus d’un mot en espagnol"],
                ),
                ("fr-nom-3", "Nom commun 3"): EtymologyData(
                    texts=[
                        "Du kanak de Maré ou nengone nata (« messager ; celui qui raconte »)"
                    ]
                ),
            },
        )

    def test_non_str_link_node(self):
        self.wxr.wtp.start_page("-huzunisha")
        root = self.wxr.wtp.parse(
            ": Dérivé du substantif [[''huzuni'']] (« tristesse »)."
        )
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("", ""): EtymologyData(
                    texts=["Dérivé du substantif huzuni (« tristesse »)."]
                ),
            },
        )

    def test_italic_pos_title_no_id(self):
        self.wxr.wtp.start_page("appel du pied")
        root = self.wxr.wtp.parse(": ''(Locution nominale 1)'' etymology text.")
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("", "Locution nominale 1"): EtymologyData(
                    texts=["etymology text."]
                )
            },
        )

    def test_not_pos_italic_node(self):
        self.wxr.wtp.start_page("métrifier")
        root = self.wxr.wtp.parse(
            ": Composé de ''[[mètre]]'' avec le suffixe ''[[-ifier]]''."
        )
        etymology_data = extract_etymology(self.wxr, root, None)
        self.assertEqual(
            etymology_data,
            {
                ("", ""): EtymologyData(
                    texts=["Composé de mètre avec le suffixe -ifier."]
                )
            },
        )

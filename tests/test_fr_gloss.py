from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Page, Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.gloss import extract_gloss
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.extractor.fr.page import process_pos_block
from wiktextract.wxr_context import WiktextractContext


class TestFrGloss(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            "Modèle:sportifs",
            10,
            body="(Sport)[[Catégorie:Sportifs en français]]",
        ),
    )
    def test_theme_templates(self, mock_get_page):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse("# {{sportifs|fr}} gloss.\n#* example")
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": ["gloss."],
                    "tags": ["Sport"],
                    "categories": ["Sportifs en français"],
                    "examples": [{"text": "example"}],
                }
            ],
        )

    def test_example_template(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            "# gloss.\n#* {{exemple|text|translation|roman|source=source}}"
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": ["gloss."],
                    "examples": [
                        {
                            "text": "text",
                            "translation": "translation",
                            "roman": "roman",
                            "ref": "source",
                        }
                    ],
                }
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page("Modèle:source", 10, body="source_title"),
    )
    def test_example_source_template(self, mock_node_to_html):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            "# gloss.\n#* example {{source|source_title}}"
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": ["gloss."],
                    "examples": [
                        {
                            "text": "example",
                            "ref": "source_title",
                        }
                    ],
                }
            ],
        )

    def test_zh_exemple_template(self):
        # https://fr.wiktionary.org/wiki/马
        self.wxr.wtp.start_page("马")
        root = self.wxr.wtp.parse(
            "=== {{S|nom|zh}} ===\n# Cheval.\n{{zh-exemple|这匹'''马'''很大。|Ce cheval est grand.|Zhè pǐ '''mǎ''' hěn dà.<br/>⠌⠢⠆ ⠏⠊⠄ ⠍⠔⠄ ⠓⠴⠄ ⠙⠔⠆⠐⠆}}"
        )
        page_data = []
        process_pos_block(
            self.wxr,
            page_data,
            WordEntry(word="马", lang_code="zh", lang="Chinois"),
            root.children[0],
            "nom",
            "Nom commun",
        )
        self.assertEqual(
            page_data[-1].model_dump(exclude_defaults=True),
            {
                "word": "马",
                "lang_code": "zh",
                "lang": "Chinois",
                "pos": "noun",
                "pos_title": "Nom commun",
                "senses": [
                    {
                        "glosses": ["Cheval."],
                        "examples": [
                            {
                                "text": "这匹马很大。",
                                "translation": "Ce cheval est grand.",
                                "roman": "Zhè pǐ mǎ hěn dà.\n⠌⠢⠆ ⠏⠊⠄ ⠍⠔⠄ ⠓⠴⠄ ⠙⠔⠆⠐⠆",
                            }
                        ],
                    }
                ],
            },
        )

    def test_variante_de(self):
        # https://fr.wiktionary.org/wiki/basket-ball
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:désuet", 10, body="(Désuet)")
        self.wxr.wtp.add_page("Modèle:sports", 10, body="(Sport)")
        self.wxr.wtp.add_page(
            "Modèle:indénombrable", 10, body="(Indénombrable)"
        )
        self.wxr.wtp.add_page(
            "Modèle:variante de", 10, body="Variante de basketball"
        )
        root = self.wxr.wtp.parse(
            "# {{désuet|en}} {{sports|en}} {{indénombrable|en}} {{variante de|basketball|en}}."
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": ["Variante de basketball."],
                    "tags": ["Désuet", "Sport", "Indénombrable", "alt-of"],
                    "alt_of": [{"word": "basketball"}],
                }
            ],
        )

    def test_italic_tag(self):
        # https://fr.wiktionary.org/wiki/lenn
        self.wxr.wtp.start_page("lenn")
        root = self.wxr.wtp.parse(
            "# (''localement'') [[bassin#Nom_commun|Bassin]], [[lavoir#Nom_commun|lavoir]]."
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [{"glosses": ["Bassin, lavoir."], "tags": ["localement"]}],
        )

    def test_not_italic_tag(self):
        # https://fr.wiktionary.org/wiki/bec-en-ciseaux
        self.wxr.wtp.start_page("bec-en-ciseaux")
        root = self.wxr.wtp.parse(
            "# [[oiseau|Oiseau]] aquatique de taille moyenne du genre ''[[Rhynchops]]''."
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": [
                        "Oiseau aquatique de taille moyenne du genre Rhynchops."
                    ]
                }
            ],
        )

    def test_preserve_space_between_tags(self):
        # https://fr.wiktionary.org/wiki/becs-en-ciseaux
        # the space between italic node and the link node should be preserved
        self.wxr.wtp.start_page("becs-en-ciseaux")
        root = self.wxr.wtp.parse("# ''Pluriel de'' [[bec-en-ciseaux]].")
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [{"glosses": ["Pluriel de bec-en-ciseaux."]}],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page("Modèle:lien", 10, body="Autrice"),
    )
    def test_template_is_not_tag(self, mock_get_page):
        # https://fr.wiktionary.org/wiki/autrice#Nom_commun_3
        self.wxr.wtp.start_page("autrice")
        root = self.wxr.wtp.parse(
            "# {{lien|autrice|fr|dif=Autrice}}, [[celle]] qui est à l’[[origine]] de [[quelque chose]]."
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": [
                        "Autrice, celle qui est à l’origine de quelque chose."
                    ]
                }
            ],
        )

    def test_nest_gloss(self):
        self.maxDiff = None
        self.wxr.wtp.start_page("eau")
        root = self.wxr.wtp.parse(
            """# [[fluide|Fluides]], [[sérosité]]s qui se trouvent ou qui se forment dans le [[corps]] de l’[[homme]] ou de l’[[animal]].
#* example 1
## [[salive|Salive]].
##* nest example
            """
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "examples": [
                        {
                            "text": "example 1",
                        }
                    ],
                    "glosses": [
                        "Fluides, sérosités qui se trouvent ou qui se forment dans le corps de l’homme ou de l’animal."
                    ],
                },
                {
                    "examples": [
                        {
                            "text": "nest example",
                        }
                    ],
                    "glosses": [
                        "Fluides, sérosités qui se trouvent ou qui se forment dans le corps de l’homme ou de l’animal.",
                        "Salive.",
                    ],
                },
            ],
        )

    def test_sandwich_tag(self):
        # https://fr.wiktionary.org/wiki/autrice#Nom_commun_4
        self.wxr.wtp.start_page("autrice")
        self.wxr.wtp.add_page("Modèle:lexique", 10, "''(Littérature)''")
        self.wxr.wtp.add_page("Modèle:rare", 10, "''(Rare)''")
        self.wxr.wtp.add_page("Modèle:lien", 10, "Autrice")
        self.wxr.wtp.add_page("Modèle:absolument", 10, "''(Absolument)''")
        root = self.wxr.wtp.parse(
            "# {{lexique|littérature|nl}} {{rare|nl}} {{lien|autrice|fr|dif=Autrice}}, femme qui a créé une œuvre littéraire. {{absolument}} [[écrivaine|Écrivaine]]."
        )
        page_data = [
            WordEntry(word="autrice", lang_code="nl", lang="Néerlandais")
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": [
                        "Autrice, femme qui a créé une œuvre littéraire. Écrivaine."
                    ],
                    "tags": ["Littérature", "Rare", "Absolument"],
                }
            ],
        )

    def test_gloss_note_template(self):
        # https://fr.wiktionary.org/wiki/autrice#Nom_commun
        self.wxr.wtp.start_page("autrice")
        self.wxr.wtp.add_page("Modèle:plus rare", 10, "''(Plus rare)''")
        root = self.wxr.wtp.parse(
            "# {{plus rare}} [[génitrice|Génitrice]] ; [[ascendante]] ({{note}} ce sens n’est plus guère utilisé que sous la forme de la locution « [[autrice de mes jours]] »)."
        )
        page_data = [WordEntry(word="autrice", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": ["Génitrice ; ascendante"],
                    "note": "ce sens n’est plus guère utilisé que sous la forme de la locution « autrice de mes jours »",
                    "tags": ["Plus rare"],
                }
            ],
        )

    def test_typographic_variant_alt_of_template(self):
        self.wxr.wtp.start_page("abajhuro")
        self.wxr.wtp.add_page(
            "Modèle:eo-sys-h",
            10,
            """''Orthographe par contrainte typographique par [[Annexe:Systèmes h et x en espéranto#Système h|système h]] de'' <bdi>[[abaĵuro#eo|abaĵuro]]</bdi>""",
        )
        root = self.wxr.wtp.parse("# {{eo-sys-h|abaĵuro}}.")
        page_data = [
            WordEntry(
                word="abajhuro",
                lang_code="fr",
                lang="Français",
                pos="typographic variant",
            )
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": [
                        "Orthographe par contrainte typographique par système h de abaĵuro."
                    ],
                    "alt_of": [{"word": "abaĵuro"}],
                }
            ],
        )

    def test_typographic_variant_alt_of_text(self):
        self.wxr.wtp.start_page("alphoenix")
        root = self.wxr.wtp.parse(
            "# ''Variante par contrainte typographique de'' [[alphœnix]]."
        )
        page_data = [
            WordEntry(
                word="alphoenix",
                lang_code="fr",
                lang="Français",
                pos="typographic variant",
            )
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": [
                        "Variante par contrainte typographique de alphœnix."
                    ],
                    "alt_of": [{"word": "alphœnix"}],
                }
            ],
        )

    def test_variante_de_dif(self):
        self.wxr.wtp.start_page("Me.")
        self.wxr.wtp.add_page("Modèle:e", 10, "<sup>e</sup>")
        self.wxr.wtp.add_page(
            "Modèle:variante ortho de",
            10,
            "''Variante orthographique de'' {{{dif}}}",
        )
        root = self.wxr.wtp.parse(
            "# ''[[abréviation|Abréviation]] de'' [[maître]]. {{variante ortho de|Me|dif=M{{e}}}}."
        )
        page_data = [
            WordEntry(word="Me.", lang_code="fr", lang="Français", pos="noun")
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {
                    "glosses": [
                        "Abréviation de maître. Variante orthographique de Mᵉ."
                    ],
                    "alt_of": [{"word": "Mᵉ"}],
                    "tags": ["alt-of"],
                }
            ],
        )

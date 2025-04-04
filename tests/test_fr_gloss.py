from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Page, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.gloss import extract_gloss
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.extractor.fr.page import parse_page, process_pos_block
from wiktextract.wxr_context import WiktextractContext


class TestFrGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"),
            WiktionaryConfig(
                dump_file_lang_code="fr",
                capture_language_codes=None,
            ),
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
                    "topics": ["sports"],
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
            """=== {{S|nom|zh}} ===
# Cheval.
{{zh-exemple|这匹'''马'''很大。|Ce cheval est grand.|Zhè pǐ '''mǎ''' hěn dà.<br/>⠌⠢⠆ ⠏⠊⠄ ⠍⠔⠄ ⠓⠴⠄ ⠙⠔⠆⠐⠆}}"""
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
                                "bold_text_offsets": [(2, 3)],
                                "translation": "Ce cheval est grand.",
                                "roman": "Zhè pǐ mǎ hěn dà.\n"
                                "⠌⠢⠆ ⠏⠊⠄ ⠍⠔⠄ ⠓⠴⠄ ⠙⠔⠆⠐⠆",
                                "bold_roman_offsets": [(7, 9)],
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
                    "tags": ["alt-of", "obsolete", "uncountable"],
                    "topics": ["sports"],
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
            [{"glosses": ["Bassin, lavoir."], "raw_tags": ["localement"]}],
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
            """# [[fluide|Fluides]]
#* example 1
## [[salive|Salive]].
##* nest example"""
        )
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].senses],
            [
                {"examples": [{"text": "example 1"}], "glosses": ["Fluides"]},
                {
                    "examples": [{"text": "nest example"}],
                    "glosses": ["Fluides", "Salive."],
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
                        "Autrice, femme qui a créé une œuvre littéraire. "
                        "Écrivaine."
                    ],
                    "raw_tags": ["Absolument"],
                    "tags": ["rare"],
                    "topics": ["literature"],
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
                    "note": "ce sens n’est plus guère utilisé que sous "
                    "la forme de la locution « autrice de mes jours »",
                    "raw_tags": ["Plus rare"],
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
                        "Orthographe par contrainte typographique par système "
                        "h de abaĵuro."
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

    def test_form_of(self):
        self.wxr.wtp.start_page("dièse")
        self.wxr.wtp.add_page("Modèle:langue", 10, "Français")
        self.wxr.wtp.add_page("Modèle:S", 10, "Forme de verbe")
        self.assertEqual(
            parse_page(
                self.wxr,
                "dièse",
                """== {{langue|fr}} ==
=== {{S|verbe|fr|flexion}} ===
# ''Première personne du singulier de l’indicatif présent du verbe'' [[diéser]].
# ''Troisième personne du singulier de l’indicatif présent du verbe'' [[diéser]].""",  # noqa:E501
            ),
            [
                {
                    "lang": "Français",
                    "lang_code": "fr",
                    "pos": "verb",
                    "pos_title": "Forme de verbe",
                    "senses": [
                        {
                            "form_of": [{"word": "diéser"}],
                            "glosses": [
                                "Première personne du singulier de "
                                "l’indicatif présent du verbe diéser."
                            ],
                        },
                        {
                            "form_of": [{"word": "diéser"}],
                            "glosses": [
                                "Troisième personne du singulier de "
                                "l’indicatif présent du verbe diéser."
                            ],
                        },
                    ],
                    "tags": ["form-of"],
                    "word": "dièse",
                }
            ],
        )

    def test_variante_kyujitai_de(self):
        self.wxr.wtp.start_page("萬歲")
        self.wxr.wtp.add_page("Modèle:langue", 10, "Japonais")
        self.wxr.wtp.add_page("Modèle:S", 10, "Interjection")
        self.wxr.wtp.add_page(
            "Modèle:variante kyujitai de",
            10,
            "{{désuet|ja}} ''Orthographe en [[kyūjitai]] de'' {{lien|{{{1}}}|ja|{{{2|}}}|dif={{{dif|}}}|tr={{{tr|}}}|sens={{{sens|}}}}}",
        )
        self.wxr.wtp.add_page(
            "Modèle:désuet",
            10,
            '<span class="emploi"><span id="désuet"></span>'
            '(<span class="texte">[[Annexe:Glossaire grammatical#D|Désuet]]</span>)'
            "</span>[[Catégorie:Termes désuets en japonais]]",
        )
        self.wxr.wtp.add_page(
            "Modèle:lien",
            10,
            '<bdi lang="ja" xml:lang="ja" class="lang-ja">[[万歳#ja|万歳]]</bdi> («&nbsp;[[vive#fr-interj|vive]] !&nbsp;»)',
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "萬歲",
                """== {{langue|ja}} ==
=== {{S|interjection|ja}} ===
# {{variante kyujitai de|万歳|sens=[[vive#fr-interj|vive]] !}}""",
            ),
            [
                {
                    "pos": "intj",
                    "pos_title": "Interjection",
                    "lang": "Japonais",
                    "lang_code": "ja",
                    "word": "萬歲",
                    "senses": [
                        {
                            "alt_of": [{"word": "万歳"}],
                            "categories": ["Termes désuets en japonais"],
                            "tags": ["alt-of", "obsolete"],
                            "glosses": [
                                "Orthographe en kyūjitai de 万歳 (« vive ! »)"
                            ],
                        }
                    ],
                }
            ],
        )

    def test_example_translation_list(self):
        self.wxr.wtp.start_page("advena")
        self.wxr.wtp.add_page("Modèle:source", 10, "{{{1}}}")
        root = self.wxr.wtp.parse(
            """# [[étranger|Étranger]], de passage, venu du dehors.
#* '''''advena''' belli'' {{source|Sil.}}
#*: étranger à la guerre."""
        )
        page_data = [
            WordEntry(word="advena", lang_code="la", lang="Latin", pos="adj")
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data[0].model_dump(
                exclude_defaults=True,
                exclude=["word", "lang_code", "lang", "pos"],
            ),
            {
                "senses": [
                    {
                        "examples": [
                            {
                                "text": "advena belli",
                                "ref": "Sil.",
                                "translation": "étranger à la guerre.",
                            }
                        ],
                        "glosses": ["Étranger, de passage, venu du dehors."],
                    }
                ]
            },
        )

    def test_topic(self):
        self.wxr.wtp.start_page("агроботанічний")
        self.wxr.wtp.add_page("Modèle:lexique", 10, "(Agriculture, Botanique)")
        root = self.wxr.wtp.parse(
            "# {{lexique|agriculture|botanique|uk}} [[agrobotanique|Agrobotanique]]."
        )
        page_data = [
            WordEntry(
                word="агроботанічний",
                lang_code="uk",
                lang="Ukrainien",
                pos="adj",
            )
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data[0].model_dump(
                exclude_defaults=True,
                exclude=["word", "lang_code", "lang", "pos"],
            ),
            {
                "senses": [
                    {
                        "glosses": ["Agrobotanique."],
                        "topics": ["agriculture", "botany"],
                    }
                ]
            },
        )

    def test_empty_gloss_str(self):
        self.wxr.wtp.start_page("affine")
        self.wxr.wtp.add_page("Modèle:lexique", 10, "({{{1}}})")
        root = self.wxr.wtp.parse(
            """# {{lexique|mathématiques|fr}}
## ''Application '''affine'''''
## ''Espace '''affine'''''"""
        )
        page_data = [
            WordEntry(
                word="affine",
                lang_code="fr",
                lang="Français",
                pos="adj",
            )
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data[0].model_dump(
                exclude_defaults=True,
                exclude=["word", "lang_code", "lang", "pos"],
            ),
            {
                "senses": [
                    {"tags": ["no-gloss"], "topics": ["mathematics"]},
                    {
                        "glosses": ["Application affine"],
                        "topics": ["mathematics"],
                    },
                    {
                        "glosses": ["Espace affine"],
                        "topics": ["mathematics"],
                    },
                ]
            },
        )

    def test_no_gloss_list(self):
        self.wxr.wtp.start_page("Alta Normandia")
        self.wxr.wtp.add_page("Modèle:langue", 10, "Ido")
        self.wxr.wtp.add_page("Modèle:S", 10, "Nom propre")
        page_data = parse_page(
            self.wxr,
            "Alta Normandia",
            """== {{langue|io}} ==
=== {{S|nom propre|io}} ===
'''Alta Normandia'''
[[Haute-Normandie]] (ancienne région de France).""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["Haute-Normandie (ancienne région de France)."],
                },
            ],
        )

    def test_mutation_de(self):
        self.wxr.wtp.start_page("hwythnos")
        self.wxr.wtp.add_page("Modèle:langue", 10, "Gallois")
        self.wxr.wtp.add_page("Modèle:S", 10, "Forme de nom commun")
        self.wxr.wtp.add_page(
            "Modèle:mutation de",
            10,
            """''Forme mutée de ''<bdi lang="cy" xml:lang="cy" class="lang-cy">[[wythnos#cy|wythnos]]</bdi>'' par [[Annexe:Mutations en gallois|ajout d’une prothèse h]]''""",
        )
        page_data = parse_page(
            self.wxr,
            "hwythnos",
            """== {{langue|cy}} ==

=== {{S|nom|cy|flexion}} ===
'''hwythnos'''
# {{mutation de|wythnos|h|cy}}.
""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "form_of": [{"word": "wythnos"}],
                    "glosses": [
                        "Forme mutée de wythnos par ajout d’une prothèse h."
                    ],
                },
            ],
        )

    def test_lien_form_of(self):
        self.wxr.wtp.start_page("écuyère")
        self.wxr.wtp.add_page("Modèle:langue", 10, "Français")
        self.wxr.wtp.add_page("Modèle:S", 10, "Forme d’adjectif")
        self.wxr.wtp.add_page(
            "Modèle:lien",
            10,
            """<bdi lang="fr" xml:lang="fr" class="lang-fr">[[écuyer#fr-adj|écuyer]]</bdi>""",
        )
        page_data = parse_page(
            self.wxr,
            "écuyère",
            """== {{langue|fr}} ==
=== {{S|adjectif|fr|flexion}} ===
'''écuyères'''
# ''Féminin pluriel de'' {{lien|écuyer|fr|adj}}.
""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "form_of": [{"word": "écuyer"}],
                    "glosses": ["Féminin pluriel de écuyer."],
                },
            ],
        )

    def test_zh_exemple_template_in_list(self):
        self.wxr.wtp.start_page("千辛萬苦")
        root = self.wxr.wtp.parse(
            """# [[souffrir#fr|Souffrir]] de [[tribulation]]s [[innommable]]s.
#* {{zh-exemple|之後十年，越南人民吃盡'''千辛萬苦'''|lang=zh|sens=Au cours de la décennie suivante, le peuple vietnamien a beaucoup souffert|source=source}}"""
        )
        page_data = [
            WordEntry(
                word="千辛萬苦",
                lang_code="ja",
                lang="Chinois",
                pos="verb",
            )
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [
                e.model_dump(exclude_defaults=True)
                for e in page_data[0].senses[0].examples
            ],
            [
                {
                    "ref": "source",
                    "text": "之後十年，越南人民吃盡千辛萬苦",
                    "bold_text_offsets": [(11, 15)],
                    "translation": "Au cours de la décennie suivante, le peuple vietnamien a beaucoup souffert",
                }
            ],
        )

    def test_équiv_pour_in_gloss(self):
        self.wxr.wtp.start_page("aumônière")
        self.wxr.wtp.add_page(
            "Modèle:équiv-pour",
            10,
            """''(pour un homme, on dit'' : <bdi lang="fr" xml:lang="fr" class="lang-fr">[[aumônier#fr|aumônier]]</bdi>'')''""",
        )
        root = self.wxr.wtp.parse(
            "# gloss {{équiv-pour|un homme|aumônier|lang=fr}}."
        )
        page_data = [
            WordEntry(
                word="aumônière",
                lang_code="fr",
                lang="Français",
                pos="noun",
            )
        ]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in page_data[0].forms],
            [
                {
                    "form": "aumônier",
                    "tags": ["masculine"],
                    "source": "form line template 'équiv-pour'",
                    "sense_index": 1,
                }
            ],
        )
        self.assertEqual(page_data[0].senses[0].glosses, ["gloss."])

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        conf = WiktionaryConfig(
            dump_file_lang_code="pt",
            capture_language_codes=None,
        )
        self.wxr = WiktextractContext(
            Wtp(
                lang_code="pt",
                parser_function_aliases=conf.parser_function_aliases,
            ),
            conf,
        )

    def test_escopo(self):
        self.wxr.wtp.add_page(
            "Predefinição:-pt-",
            10,
            "Português[[Categoria:!Entrada (Português)]]",
        )
        self.wxr.wtp.add_page(
            "Predefinição:Substantivo",
            10,
            "Substantivo[[Categoria:Substantivo (Português)]]",
        )
        self.wxr.wtp.add_page(
            "Predefinição:escopo",
            10,
            """(''<span style="color:navy;">[[Categoria:Português brasileiro]]Brasil e&nbsp;[[Categoria:Coloquialismo (Português)]]popular</span>'')""",
        )
        data = parse_page(
            self.wxr,
            "cão",
            """={{-pt-}}=
=={{Substantivo|pt}}==
# {{escopo|pt|Brasil|popular}} [[gênio]] do [[mal]] em geral ("capeta")
#* ''O '''cão''' em forma de gente.''""",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "Português",
                    "lang_code": "pt",
                    "pos": "noun",
                    "pos_title": "Substantivo",
                    "categories": [
                        "!Entrada (Português)",
                        "Substantivo (Português)",
                    ],
                    "senses": [
                        {
                            "categories": [
                                "Português brasileiro",
                                "Coloquialismo (Português)",
                            ],
                            "glosses": ['gênio do mal em geral ("capeta")'],
                            "raw_tags": ["Brasil", "popular"],
                            "examples": [{"text": "O cão em forma de gente."}],
                        }
                    ],
                    "word": "cão",
                }
            ],
        )

    def test_tradex_template(self):
        self.wxr.wtp.add_page("Predefinição:-ryu-", 10, "Okinawano")
        self.wxr.wtp.add_page("Predefinição:Substantivo", 10, "Substantivo")
        self.wxr.wtp.add_page(
            "Predefinição:tradex",
            10,
            """[[Categoria:Entrada com exemplo traduzido (Okinawano)|a]]''沖縄ぬ'''政治''' (うちなーぬしーじ)'' <small>('''governo''' de Okinawa)</small>""",
        )
        data = parse_page(
            self.wxr,
            "政治",
            """={{-ryu-}}=
=={{Substantivo|ryu}}==
# [[governo]]
#*{{tradex|ryu|沖縄ぬ'''政治''' (うちなーぬしーじ)|'''governo''' de Okinawa}}""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "categories": ["Entrada com exemplo traduzido (Okinawano)"],
                "glosses": ["governo"],
                "examples": [
                    {
                        "text": "沖縄ぬ政治 (うちなーぬしーじ)",
                        "translation": "governo de Okinawa",
                    }
                ],
            },
        )

    def test_small_tag_in_example(self):
        self.wxr.wtp.add_page("Predefinição:-en-", 10, "Inglês")
        data = parse_page(
            self.wxr,
            "book",
            """={{-en-}}=
==Substantivo==
'''book'''
# [[livro]]
#* ''My life is an open '''book'''. (I have no secrets.)'': <small>Minha vida é um livro aberto. (Não tenho segredos.)</small>""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "glosses": ["livro"],
                "examples": [
                    {
                        "text": "My life is an open book. (I have no secrets.)",
                        "translation": "Minha vida é um livro aberto. (Não tenho segredos.)",
                    }
                ],
            },
        )

    def test_OESP_template(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page(
            "Predefinição:OESP",
            10,
            "(notícia do jornal ''O Estado de S. Paulo'' de 08 de abril de 2008)",
        )
        data = parse_page(
            self.wxr,
            "livro",
            """={{-pt-}}=
==Substantivo==
# objeto
#* ''Com verba pública, '''livro''' técnico ainda é restrito.'' {{OESP|2008|abril|08}}""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "glosses": ["objeto"],
                "examples": [
                    {
                        "text": "Com verba pública, livro técnico ainda é restrito.",
                        "ref": "notícia do jornal O Estado de S. Paulo de 08 de abril de 2008",
                    }
                ],
            },
        )

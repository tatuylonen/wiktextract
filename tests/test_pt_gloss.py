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
# {{escopo|pt|Brasil|popular}} [[gênio]] do [[mal]] em geral ("capeta")""",
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
                        }
                    ],
                    "word": "cão",
                }
            ],
        )

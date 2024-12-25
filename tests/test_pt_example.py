from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtExample(TestCase):
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

    def test_double_italic_nodes(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "diabo",
            """={{-pt-}}=
==Substantivo<sup>1</sup>==
# espírito
#* ''“O '''diabo''' é o pai do rock!”.'' (passagem da composição ''“Rock do Diabo”'' de Raul Seixas/Paulo Coelho, 1975)""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "glosses": ["espírito"],
                "examples": [
                    {
                        "text": "“O diabo é o pai do rock!”.",
                        "ref": "passagem da composição “Rock do Diabo” de Raul Seixas/Paulo Coelho, 1975",
                    }
                ],
            },
        )

    def test_nested_example_list(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "amor",
            """={{-pt-}}=
==Substantivo==
# [[sentimento]]
#* '''1595''', [[w:Luís de Camões|Luís de Camões]], ''Rimas'':
#*: "'''''Amor''' é fogo que arde sem se ver<br>é ferida que dói, e não se sente,<br>é um contentamento descontente,<br>é dor que desatina sem doer.''\"""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "glosses": ["sentimento"],
                "examples": [
                    {
                        "text": '"Amor é fogo que arde sem se ver\né ferida que dói, e não se sente,\né um contentamento descontente,\né dor que desatina sem doer."',
                        "ref": "1595, Luís de Camões, Rimas:",
                    }
                ],
            },
        )

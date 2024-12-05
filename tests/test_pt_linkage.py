from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtLinkage(TestCase):
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

    def test_expression(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page("Predefinição:g", 10, "''masculino''")
        data = parse_page(
            self.wxr,
            "olho",
            """={{-pt-}}=
==Substantivo==
# órgão
===Expressões===
* '''[[a beleza está nos olhos de quem vê]]''': {{escopo2|Provérbio}} cada pessoa tem uma opinião própria sobre o que lhe é belo
* '''[[abrir os olhos]]''':
*: {{escopo2|intransitivo}} perceber a verdade
*:: ''Entre amores, trapaças e muitas confusões, Katie terá que lutar para conquistar seu espaço e '''abrir os olhos''' para a realidade da cidade grande.''""",
        )
        self.assertEqual(
            data[0]["expressions"],
            [
                {
                    "senses": [
                        {
                            "glosses": [
                                "cada pessoa tem uma opinião própria sobre o que lhe é belo"
                            ],
                            "raw_tags": ["Provérbio"],
                        }
                    ],
                    "word": "a beleza está nos olhos de quem vê",
                },
                {
                    "senses": [
                        {
                            "glosses": ["perceber a verdade"],
                            "raw_tags": ["intransitivo"],
                            "examples": [
                                {
                                    "text": "Entre amores, trapaças e muitas confusões, Katie terá que lutar para conquistar seu espaço e abrir os olhos para a realidade da cidade grande."
                                }
                            ],
                        }
                    ],
                    "word": "abrir os olhos",
                },
            ],
        )

    def test_synonyms(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "olho",
            """={{-pt-}}=
==Substantivo==
# órgão
===Sinônimos===
* De '''5''' (furo, na agulha, para a passagem de linhas ou fios): [[buraco]]""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "buraco",
                    "sense": "furo, na agulha, para a passagem de linhas ou fios",
                    "sense_index": 5,
                }
            ],
        )

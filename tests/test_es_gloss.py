import unittest
from typing import List

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.gloss import extract_gloss
from wiktextract.extractor.es.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestESGloss(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_page_data(self) -> List[WordEntry]:
        return [WordEntry(word="test", lang_code="es", lang="Language")]

    def test_es_extract_glosses(self):
        # https://es.wiktionary.org/wiki/ayudar

        self.wxr.wtp.add_page("Plantilla:plm", 10, "Contribuir")
        self.wxr.wtp.start_page("")

        root = self.wxr.wtp.parse(
            """;1: {{plm|contribuir}} [[esfuerzo]] o [[recurso]]s para la [[realización]] de algo.
;2: Por antonomasia, [[cooperar]] a que alguno [[salir|salga]] de una [[situación]] [[dificultoso|dificultosa]]"""
        )

        page_data = self.get_default_page_data()

        extract_gloss(self.wxr, page_data, root.children[0])

        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "glosses": [
                        "Contribuir esfuerzo o recursos para la realización de algo."
                    ],
                    "senseid": 1,
                },
                {
                    "glosses": [
                        "Por antonomasia, cooperar a que alguno salga de una situación dificultosa"
                    ],
                    "senseid": 2,
                },
            ],
        )

    def test_es_extract_gloss_categories(self):
        # https://es.wiktionary.org/wiki/amor
        self.wxr.wtp.add_page("Plantilla:plm", 10, "Sentimiento")
        self.wxr.wtp.add_page(
            "Plantilla:sentimientos",
            10,
            "Humanidades. [[Categoría:ES:Sentimientos]]",
        )
        self.wxr.wtp.start_page("")

        root = self.wxr.wtp.parse(
            ";1 {{sentimientos}}: {{plm|sentimiento}} [[afectivo]] de [[atracción]], [[unión]] y [[afinidad]] que se experimenta hacia una persona, animal o cosa"
        )

        page_data = self.get_default_page_data()

        extract_gloss(self.wxr, page_data, root.children[0])

        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "glosses": [
                        "Sentimiento afectivo de atracción, unión y afinidad que se experimenta hacia una persona, animal o cosa"
                    ],
                    "senseid": 1,
                    "tags": ["Humanidades"],
                    "categories": ["ES:Sentimientos"],
                }
            ],
        )

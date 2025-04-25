import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.linkage import (
    extract_linkage_section,
    process_linkage_template,
)
from wiktextract.extractor.es.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestESLinkage(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_es_extract_linkage(self):
        test_cases = [
            # https://es.wiktionary.org/wiki/Fett
            {
                "input": "* {{l|de|Fettgewebe}}: ''tejido adiposo''",
                "expected": [{"word": "Fettgewebe", "sense": "tejido adiposo"}],
            },
            # https://es.wiktionary.org/wiki/presunción
            {
                "input": "* [[presunción absoluta]]\n* [[presunción de hecho y de derecho]]",
                "expected": [
                    {"word": "presunción absoluta"},
                    {"word": "presunción de hecho y de derecho"},
                ],
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                self.wxr.wtp.add_page("Plantilla:l", 10, "Fettgewebe")
                word_entry = WordEntry(word="", lang_code="", lang="")
                root = self.wxr.wtp.parse(case["input"])
                extract_linkage_section(
                    self.wxr, [word_entry], root.children[0], "compounds"
                )
                self.assertEqual(
                    word_entry.model_dump(exclude_defaults=True)["compounds"],
                    case["expected"],
                )

    def test_es_process_linkage_template(self):
        # Test cases from https://es.wiktionary.org/wiki/Plantilla:t+
        test_cases = [
            {
                "input": "{{sinónimo|leng=la|nasus|alt=nāsus}}",
                "expected": [
                    {"word": "nasus", "alternative_spelling": "nāsus"}
                ],
            },
            {
                "input": "{{sinónimo|automóvil|coche|nota2=España|carro|nota3=Colombia, Estados Unidos, México, Venezuela}}",
                "expected": [
                    {"word": "automóvil"},
                    {"word": "coche", "note": "España"},
                    {
                        "word": "carro",
                        "note": "Colombia, Estados Unidos, México, Venezuela",
                    },
                ],
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                word_entry = WordEntry(word="", lang_code="", lang="")
                root = self.wxr.wtp.parse(case["input"])
                process_linkage_template(self.wxr, word_entry, root.children[0])
                self.assertEqual(
                    word_entry.model_dump(exclude_defaults=True)["synonyms"],
                    case["expected"],
                )

    def test_two_words_in_a_list(self):
        self.wxr.wtp.start_page("perro")
        word_entry = WordEntry(word="perro", lang="Español", lang_code="es")
        root = self.wxr.wtp.parse(
            "*[[perro caliente]] o [[perrito caliente]]: sándwich de salchicha de Viena"
        )
        extract_linkage_section(self.wxr, [word_entry], root, "idioms")
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["idioms"],
            [
                {
                    "word": "perro caliente",
                    "sense": "sándwich de salchicha de Viena",
                },
                {
                    "word": "perrito caliente",
                    "sense": "sándwich de salchicha de Viena",
                },
            ],
        )

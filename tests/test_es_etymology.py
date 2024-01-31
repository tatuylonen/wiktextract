import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.etymology import process_etymology_block
from wiktextract.extractor.es.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestESEtymology(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"), WiktionaryConfig(dump_file_lang_code="es")
        )
        self.wxr.wtp.add_page(
            "Plantilla:etimología",
            10,
            """{{#switch: {{{1|}}}
 |=Si puedes, incorpórala: ver cómo.
 |Del {{{1|}}} {{{2|}}}
}}""",
        )
        self.wxr.wtp.add_page(
            "Plantilla:etimología2",
            10,
            "{{{1|Si puedes, incorpórala: ver cómo.}}}",
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_es_extract_etymology(self):
        test_cases = [
            {
                # https://es.wiktionary.org/wiki/Schreck
                "input": "{{etimología|leng=de}}",
                "expected": dict(),
            },
            {
                # https://es.wiktionary.org/wiki/bagre
                "input": "{{etimología|catalán|bagre}}, y este del latín ''[[pargus]]'', a su vez del griego ''[[φάγρος]]'' (''phágros'')",
                "expected": {
                    "etymology_templates": [
                        {
                            "args": {
                                "1": "catalán",
                                "2": "bagre",
                            },
                            "expansion": "Del catalán bagre",
                            "name": "etimología",
                        },
                    ],
                    "etymology_text": "Del catalán bagre, y este del latín pargus, a su vez del griego φάγρος (phágros)",
                },
            },
            {
                # https://es.wiktionary.org/wiki/hibridación
                "input": "{{etimología2|De ''[[hibridar]]'', y de ''[[-ción]]''}}",
                "expected": {
                    "etymology_templates": [
                        {
                            "args": {
                                "1": "De hibridar, y de -ción",
                            },
                            "expansion": "De hibridar, y de -ción",
                            "name": "etimología2",
                        },
                    ],
                    "etymology_text": "De hibridar, y de -ción",
                },
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                root = self.wxr.wtp.parse(case["input"])
                data = WordEntry(word="test", lang_code="es", lang="Español")
                process_etymology_block(self.wxr, data, root)
                case["expected"].update(
                    {
                        "word": "test",
                        "lang_code": "es",
                        "lang": "Español",
                    }
                )
                self.assertEqual(
                    data.model_dump(exclude_defaults=True), case["expected"]
                )

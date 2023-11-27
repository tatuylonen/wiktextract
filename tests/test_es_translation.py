import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.models import WordEntry
from wiktextract.extractor.es.translation import extract_translation
from wiktextract.wxr_context import WiktextractContext


class TestESTranslation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_page_data(self) -> list[WordEntry]:
        return [
            WordEntry(
                word="test",
                lang_code="es",
                lang_name="Language",
            )
        ]

    def test_es_extract_translation(self):
        # Test cases from https://es.wiktionary.org/wiki/Plantilla:t+
        test_cases = [
            {
                "input": "{{t+|af|1|kat}}",
                "expected": [
                    {"lang_code": "af", "word": "kat", "senseids": ["1"]}
                ],
            },
            {
                "input": "{{t+|de|1, 2|Katze|f|,|1|Kater|m|nota|gato macho|,|8|Tic Tac Toe}}",
                "expected": [
                    {
                        "lang_code": "de",
                        "word": "Katze",
                        "senseids": ["1", "2"],
                        "tags": ["f"],
                    },
                    {
                        "lang_code": "de",
                        "word": "Kater",
                        "senseids": ["1"],
                        "tags": ["m"],
                        "notes": ["gato macho"],
                    },
                    {
                        "lang_code": "de",
                        "word": "Tic Tac Toe",
                        "senseids": ["8"],
                    },
                ],
            },
            {
                "input": "{{t+|fr|1|profession|nl|de|bateleur}}",
                "expected": [
                    {
                        "lang_code": "fr",
                        "word": "profession de bateleur",
                        "senseids": ["1"],
                    }
                ],
            },
            {
                "input": "{{t+|hy|1|կատու|tr|katu}}",
                "expected": [
                    {
                        "lang_code": "hy",
                        "word": "կատու",
                        "roman": "katu",
                        "senseids": ["1"],
                    }
                ],
            },
            {
                "input": "{{t+|hy|1|կատու|tr=katu}}",
                "expected": [
                    {
                        "lang_code": "hy",
                        "word": "կատու",
                        "roman": "katu",
                        "senseids": ["1"],
                    }
                ],
            },
            {
                "input": "{{t+|de|amphibisch|adj|,|Amphibie|sust|,|Amphibium|sust}}",
                "expected": [
                    {"lang_code": "de", "word": "amphibisch", "tags": ["adj"]},
                    {"lang_code": "de", "word": "Amphibie", "tags": ["sust"]},
                    {"lang_code": "de", "word": "Amphibium", "tags": ["sust"]},
                ],
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                page_data = self.get_default_page_data()

                root = self.wxr.wtp.parse(case["input"])

                extract_translation(self.wxr, page_data, root.children[0])

                translations = [
                    t.model_dump(exclude_defaults=True)
                    for t in page_data[-1].translations
                ]
                self.assertEqual(
                    translations,
                    case["expected"],
                )

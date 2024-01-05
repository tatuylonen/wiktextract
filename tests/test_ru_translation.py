import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.translation import extract_translations
from wiktextract.wxr_context import WiktextractContext


class TestRUTranslation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(dump_file_lang_code="ru"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_word_entry(self) -> WordEntry:
        return WordEntry(word="test", lang_code="ru", lang="русский")

    def test_ru_extract_gloss(self):
        # Test cases adapted from: https://ru.wiktionary.org/wiki/дом
        test_cases = [
            {
                # No translations
                "input": "{{перев-блок|ab=}}",
                "expected": [],
            },
            {
                # No translations but gloss
                "input": "{{перев-блок|сооружение|ab=}}",
                "expected": [],
            },
            {
                # Translations, no gloss
                "input": "{{перев-блок|en=[[house]]|ar=[[بيت]]}}",
                "expected": [
                    {
                        "word": "house",
                        "lang_code": "en",
                        "lang": "английский",
                    },
                    {"word": "بيت", "lang_code": "ar", "lang": "арабский"},
                ],
            },
            {
                # Ignore tags for now
                "input": "{{перев-блок|сооружение|ab=|en=[[house]]|ar=[[بيت]]}}",
                "expected": [
                    {
                        "word": "house",
                        "lang_code": "en",
                        "lang": "английский",
                        "sense": "сооружение",
                    },
                    {
                        "word": "بيت",
                        "lang_code": "ar",
                        "lang": "арабский",
                        "sense": "сооружение",
                    },
                ],
            },
            {
                "input": "{{перев-блок||br=[[ti]] {{m}}|grc=[[αὐλή]] {{f}}; [[δόμος]] {{m}}; [[δῶμα]] {{n}}}}",
                "expected": [
                    {
                        "word": "ti",
                        "lang_code": "br",
                        "lang": "бретонский",
                    },
                    {
                        "word": "αὐλή",
                        "lang_code": "grc",
                        "lang": "древнегреческий",
                    },
                    {
                        "word": "δόμος",
                        "lang_code": "grc",
                        "lang": "древнегреческий",
                    },
                    {
                        "word": "δῶμα",
                        "lang_code": "grc",
                        "lang": "древнегреческий",
                    },
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                word_entry = self.get_default_word_entry()

                root = self.wxr.wtp.parse(case["input"])

                extract_translations(self.wxr, word_entry, root)

                translations = [
                    t.model_dump(exclude_defaults=True)
                    for t in word_entry.translations
                ]
                self.assertEqual(translations, case["expected"])

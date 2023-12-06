import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.models import Sense, Translation, WordEntry
from wiktextract.extractor.de.translation import (extract_translation,
                                                  process_translation_list)
from wiktextract.wxr_context import WiktextractContext


class TestDETranslation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_word_entry(self):
        return WordEntry(word="Beispiel", lang_code="de", lang_name="Deutsch")

    def test_de_extract_translation(self):
        test_cases = [
            # Adds sense data to correct sense
            {
                "input": "{{Ü-Tabelle|1|G=Beispiel|Ü-Liste=*{{en}}: {{Ü|en|example}}}}",
                "senses": [Sense(senseid="1")],
                "expected": {
                    "senses": [
                        {
                            "senseid": "1",
                            "translations": [
                                {
                                    "sense": "Beispiel",
                                    "lang_code": "en",
                                    "lang_name": "Englisch",
                                    "word": "example",
                                }
                            ],
                        }
                    ]
                },
            },
            # Adds sense data to page_data root if no senseid is given
            {
                "input": "{{Ü-Tabelle||G=Beispiel|Ü-Liste=*{{en}}: {{Ü|en|example}}}}",
                "senses": [Sense(senseid="1")],
                "expected": {
                    "senses": [
                        {
                            "senseid": "1",
                        }
                    ],
                    "translations": [
                        {
                            "sense": "Beispiel",
                            "lang_code": "en",
                            "lang_name": "Englisch",
                            "word": "example",
                        }
                    ],
                },
            },
            # Adds sense data to page_data root if senseid could not be matched
            {
                "input": "{{Ü-Tabelle|2|G=Beispiel|Ü-Liste=*{{en}}: {{Ü|en|example}}}}",
                "senses": [Sense(senseid="1")],
                "expected": {
                    "senses": [
                        {
                            "senseid": "1",
                        }
                    ],
                    "translations": [
                        {
                            "sense": "Beispiel",
                            "lang_code": "en",
                            "lang_name": "Englisch",
                            "word": "example",
                        }
                    ],
                },
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                root = self.wxr.wtp.parse(case["input"])

                word_entry = self.get_default_word_entry()
                word_entry.senses = case.get("senses", [])

                extract_translation(self.wxr, word_entry, root)

                self.assertEqual(
                    word_entry.model_dump(
                        exclude_defaults=True,
                        exclude={"word", "lang_code", "lang_name"},
                    ),
                    case["expected"],
                )

    def test_de_process_translation_list(self):
        test_cases = [
            # https://de.wiktionary.org/wiki/Beispiel
            # Ü template
            {
                "input": "{{Ü-Tabelle|||Ü-Liste=\n*{{en}}: {{Ü|en|example}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "example",
                    }
                ],
            },
            # https://de.wiktionary.org/wiki/Beispiel
            # Üt template with manual transcription
            {
                "input": "{{Ü-Tabelle|||Ü-Liste=\n*{{hy}}: {{Üt|hy|օրինակ|orinak}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "hy",
                        "lang_name": "Armenisch",
                        "word": "օրինակ",
                        "roman": "orinak",
                    }
                ],
            },
            # https://de.wiktionary.org/wiki/Beispiel
            # Üt template with automatic transcription
            {
                "pages": [("Vorlage:Üt", 10, "пример (primer^☆) → ru")],
                "input": "{{Ü-Tabelle|||Ü-Liste=\n*{{ru}}: {{Üt|ru|пример}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "ru",
                        "lang_name": "Russisch",
                        "word": "пример",
                        "roman": "primer",
                    }
                ],
            },
            # https://de.wiktionary.org/wiki/Schrift
            # Üt? template
            {
                "pages": [("Vorlage:Üt", 10, "عريضة ? () → ar")],
                "input": "{{Ü-Tabelle|||Ü-Liste=\n*{{ar}}: {{Üt?|ar|عريضة|}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "ar",
                        "lang_name": "Arabisch",
                        "word": "عريضة",
                        "uncertain": True,
                    }
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                if "pages" in case:
                    for page in case["pages"]:
                        self.wxr.wtp.add_page(*page)

                root = self.wxr.wtp.parse(case["input"])

                sense_translations = []
                base_translation_data = Translation()

                translation_list = root.children[0].template_parameters.get(
                    "Ü-Liste"
                )

                process_translation_list(
                    self.wxr,
                    sense_translations,
                    base_translation_data,
                    translation_list,
                )
                translations = [
                    t.model_dump(exclude_defaults=True)
                    for t in sense_translations
                ]
                self.assertEqual(
                    translations, case["expected_sense_translations"]
                )

    def test_de_process_translation_list_with_modifiers(self):
        test_cases = [
            # https://de.wiktionary.org/wiki/Beispiel
            # Modifying the following translation
            {
                "input": "{{Ü-Tabelle|||Ü-Liste=\n*{{en}}: {{Ü|en|instance}}, '''Vorbild:''' {{Ü|en|model}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "instance",
                    },
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "model",
                        "tags": ["Vorbild"],
                    },
                ],
            },
            # https://de.wiktionary.org/wiki/Beispiel
            # Modifying the previous translation
            {
                "pages": [("Vorlage:m", 10, "m")],
                "input": "{{Ü-Tabelle|||Ü-Liste=\n**{{fr}}: {{Ü|fr|exemple}} {{m}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "fr",
                        "lang_name": "Französisch",
                        "word": "exemple",
                        "tags": ["m"],
                    }
                ],
            },
            # https://de.wiktionary.org/wiki/Bein
            # Multiple modifiers
            {
                "pages": [("Vorlage:f", 10, "f")],
                "input": "{{Ü-Tabelle|||Ü-Liste=\n*{{la}}: {{Ü|la|crus}} {{f}}, {{Ü|la|camba}} (vulgärlateinisch) {{f}}, {{Ü|la|gamba}} (vulgärlateinisch) {{f}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "la",
                        "lang_name": "Latein",
                        "word": "crus",
                        "tags": ["f"],
                    },
                    {
                        "lang_code": "la",
                        "lang_name": "Latein",
                        "word": "camba",
                        "tags": ["vulgärlateinisch", "f"],
                    },
                    {
                        "lang_code": "la",
                        "lang_name": "Latein",
                        "word": "gamba",
                        "tags": ["vulgärlateinisch", "f"],
                    },
                ],
            },
            #  https://de.wiktionary.org/wiki/Beitrag
            # With senseids in the modifiers
            # This is just to document the current behaviour. When these cases
            # get sense disambiguated, update this test case.
            {
                "pages": [("Vorlage:f", 10, "f")],
                "input": "{{Ü-Tabelle|||Ü-Liste=\n*{{en}}: [1] {{Ü|en|subscription}}; [1a] {{Ü|en|dues}}, {{Ü|en|membership fee}}; [1, 2] {{Ü|en|contribution}}; [3] {{Ü|en|article}}}}",
                "expected_sense_translations": [
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "subscription",
                        "tags": ["[1a]"],
                    },
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "dues",
                    },
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "membership fee",
                        "tags": ["[1", "2]"],
                    },
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "contribution",
                        "tags": ["[3]"],
                    },
                    {
                        "lang_code": "en",
                        "lang_name": "Englisch",
                        "word": "article",
                    },
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                if "pages" in case:
                    for page in case["pages"]:
                        self.wxr.wtp.add_page(*page)

                root = self.wxr.wtp.parse(case["input"])

                sense_translations = []
                base_translation_data = Translation()

                translation_list = root.children[0].template_parameters.get(
                    "Ü-Liste"
                )

                process_translation_list(
                    self.wxr,
                    sense_translations,
                    base_translation_data,
                    translation_list,
                )
                translations = [
                    t.model_dump(exclude_defaults=True)
                    for t in sense_translations
                ]
                self.assertEqual(
                    translations, case["expected_sense_translations"]
                )

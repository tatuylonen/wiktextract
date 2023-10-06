import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.pronunciation import (
    process_ipa,
    process_hoerbeispiele,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestDEPronunciation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_de_process_ipa(self):
        test_cases = [
            {
                "input": "{{Lautschrift|ipa1}}",
                "expected": [
                    {
                        "ipa": ["ipa1"],
                    }
                ],
            },
            {
                "input": "{{Lautschrift|ipa1|spr=de}}",
                "expected": [
                    {"ipa": ["ipa1"], "language": "Deutsch", "lang_code": "de"}
                ],
            },
            {
                "input": "{{Lautschrift|ipa1}} {{Lautschrift|ipa2}}{{Lautschrift|ipa3|spr=de}}",
                "expected": [
                    {"ipa": ["ipa1", "ipa2"]},
                    {"ipa": ["ipa3"], "language": "Deutsch", "lang_code": "de"},
                ],
            },
            {
                "input": "{{Lautschrift|ipa1}}, ''tag1'' {{Lautschrift|ipa2}}",
                "expected": [
                    {"ipa": ["ipa1"]},
                    {"ipa": ["ipa2"], "tags": ["tag1"]},
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                self.wxr.wtp.add_page("Vorlage:IPA", 10, "")
                self.wxr.wtp.add_page("Vorlage:Lautschrift", 10, "(Deutsch)")

                self.wxr.wtp.LANGUAGES_BY_CODE["de"] = "Deutsch"

                root = self.wxr.wtp.parse(case["input"])

                sound_data = [defaultdict(list)]

                process_ipa(
                    self.wxr, sound_data, list(root.filter_empty_str_child())
                )

                self.assertEqual(sound_data, case["expected"])

    def test_de_process_hoerbeispiele(self):
        # https://de.wiktionary.org/wiki/Beispiel
        filename1 = "De-Beispiel.ogg"
        # https://de.wiktionary.org/wiki/butineur
        filename2 = "LL-Q150 (fra)-WikiLucas00-butineur.wav"
        test_cases = [
            {
                "input": "{{Audio|" + filename1 + "}}",
                "expected": [
                    {
                        "audio": filename1,
                        "mp3_url": None,  # None indicates we don't care about the exact value
                        "ogg_url": None,
                    }
                ],
            },
            {
                "input": "{{Audio|"
                + filename1
                + "}} {{Audio|"
                + filename2
                + "}}",
                "expected": [
                    {
                        "audio": filename1,
                        "mp3_url": None,
                        "ogg_url": None,
                    },
                    {
                        "audio": filename2,
                        "ogg_url": None,
                        "mp3_url": None,
                        "wav_url": None,
                    },
                ],
            },
            {
                "input": "{{Audio|"
                + filename1
                + "}} ''tag1'', ''tag2'' {{Audio|"
                + filename2
                + "}}",
                "expected": [
                    {
                        "audio": filename1,
                        "mp3_url": None,
                        "ogg_url": None,
                        "tags": ["tag1"],
                    },
                    {
                        "audio": filename2,
                        "mp3_url": None,
                        "ogg_url": None,
                        "wav_url": None,
                        "tags": ["tag2"],
                    },
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                self.wxr.wtp.add_page("Vorlage:IPA", 10, "")
                self.wxr.wtp.add_page("Vorlage:Audio", 10, "")

                self.wxr.wtp.LANGUAGES_BY_CODE["de"] = "Deutsch"

                root = self.wxr.wtp.parse(case["input"])

                sound_data = [defaultdict(list)]

                process_hoerbeispiele(
                    self.wxr, sound_data, list(root.filter_empty_str_child())
                )

                self.assertSoundDataMatchesExpected(
                    sound_data, case["expected"]
                )

    def assertSoundDataMatchesExpected(self, sound_data, expected):
        self.assertEqual(
            len(sound_data),
            len(expected),
            f"Mismatch in number of sound data entries{sound_data}",
        )

        for data, exp in zip(sound_data, expected):
            for key, value in exp.items():
                if value is None:
                    self.assertIn(key, data)
                else:
                    self.assertEqual(data[key], value)

            for key in data:
                self.assertIn(key, exp)
                if exp[key] is not None:
                    self.assertEqual(data[key], exp[key])

import unittest
from typing import Callable

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.page import parse_page
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.pronunciation import (
    process_transcription_grc_template,
    process_transcription_la_template,
    process_transcription_ru_template,
    process_transcription_template,
    process_transcriptions_ru_template,
    process_transcriptions_template,
)
from wiktextract.wxr_context import WiktextractContext


class TestRUPronunciation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(
                dump_file_lang_code="ru", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_word_entry(self) -> WordEntry:
        return WordEntry(word="тест", lang_code="ru", lang="русский")

    def process_template_and_assert(
        self,
        template: str,
        process_function: Callable,
        expected_results: list[dict],
    ):
        self.wxr.wtp.start_page("")
        word_entry = self.get_default_word_entry()
        root = self.wxr.wtp.parse(template)
        process_function(self.wxr, word_entry, root.children[0])

        sounds = [
            s.model_dump(exclude_defaults=True) for s in word_entry.sounds
        ]

        self.assertEqual(
            len(expected_results),
            len(sounds),
            msg=f"Template: {template}, expected: {expected_results}, actual: {sounds}",
        )

        for expected, sound in zip(expected_results, sounds):
            self.assertEqual(sound, sound | expected)

    def test_process_transcription_template(self):
        # https://ru.wiktionary.org/wiki/Шаблон:transcription
        test_cases = [
            {
                "input": "{{transcription|məɫɐˈko|Ru-молоко.ogg|норма=московская норма}}",
                "expected": {
                    "ipa": "[məɫɐˈko]",
                    "audio": "Ru-молоко.ogg",
                    "raw_tags": ["московская норма"],
                },
            },
            {
                "input": "{{transcription|vot|Ru-вот.ogg|омофоны=вод}}",
                "expected": {
                    "ipa": "[vot]",
                    "audio": "Ru-вот.ogg",
                    "homophones": ["вод"],
                },
            },
        ]

        for test_case in test_cases:
            self.process_template_and_assert(
                test_case["input"],
                process_transcription_template,
                [test_case["expected"]],
            )

    def test_process_transcriptions_template(self):
        # https://ru.wiktionary.org/wiki/Шаблон:transcriptions
        test_cases = [
            {
                "input": "{{transcriptions|ˈɫoʂɨtʲ|ˈɫoʂɨdʲɪ|Ru-лошадь.ogg|норма=московская норма}}",
                "expected": [
                    {
                        "ipa": "[ˈɫoʂɨtʲ]",
                        "audio": "Ru-лошадь.ogg",
                        "raw_tags": ["московская норма"],
                        "tags": ["singular"],
                    },
                    {
                        "ipa": "[ˈɫoʂɨdʲɪ]",
                        "raw_tags": ["московская норма"],
                        "tags": ["plural"],
                    },
                ],
            },
            {
                "input": "{{transcriptions|bɐˈlʲit|bɐˈlʲidɨ|омофоны=болит|источник=Зарва}}",
                "expected": [
                    {
                        "ipa": "[bɐˈlʲit]",
                        "homophones": ["болит"],
                        "tags": ["singular"],
                    },
                    {
                        "ipa": "[bɐˈlʲidɨ]",
                        "tags": ["plural"],
                    },
                ],
            },
            {
                "input": "{{transcriptions|ˈkʌl.ə(ɹ)|норма=брит.}}",
                "expected": [
                    {
                        "ipa": "[ˈkʌl.ə(ɹ)]",
                        "raw_tags": ["брит."],
                        "tags": ["singular"],
                    }
                ],
            },
        ]

        for test_case in test_cases:
            self.process_template_and_assert(
                test_case["input"],
                process_transcriptions_template,
                test_case["expected"],
            )

    def test_process_transcription_ru_template_1(self):
        # https://ru.wiktionary.org/wiki/Шаблон:transcription-ru
        self.wxr.wtp.add_page("Шаблон:transcription-ru", 10, "[məlɐˈko]")

        self.process_template_and_assert(
            "{{transcription-ru|молоко́|Ru-молоко.ogg|норма=московская норма}}",
            process_transcription_ru_template,
            [
                {
                    "ipa": "[məlɐˈko]",
                    "audio": "Ru-молоко.ogg",
                    "raw_tags": ["московская норма"],
                }
            ],
        )

    def test_process_transcription_ru_template_2(self):
        # https://ru.wiktionary.org/wiki/Шаблон:transcription-ru
        self.wxr.wtp.add_page("Шаблон:transcription-ru", 10, "[vot]")

        self.process_template_and_assert(
            "{{transcription-ru|вот|Ru-вот.ogg|омофоны=вод}}",
            process_transcription_ru_template,
            [
                {
                    "ipa": "[vot]",
                    "audio": "Ru-вот.ogg",
                    "homophones": ["вод"],
                }
            ],
        )

    def test_process_transcriptions_ru_template_1(self):
        # https://ru.wiktionary.org/wiki/Шаблон:transcriptions-ru
        self.wxr.wtp.add_page(
            "Шаблон:transcriptions-ru", 10, "ед. ч. [ˈɫoʂətʲ] мн. ч. [ˈɫoʂədʲɪ]"
        )
        self.process_template_and_assert(
            "{{transcriptions-ru|ло́шадь|ло́шади|Ru-лошадь.ogg|норма=московская норма}}",
            process_transcriptions_ru_template,
            [
                {
                    "ipa": "[ˈɫoʂətʲ]",
                    "audio": "Ru-лошадь.ogg",
                    "raw_tags": ["московская норма"],
                    "tags": ["singular"],
                },
                {
                    "ipa": "[ˈɫoʂədʲɪ]",
                    "raw_tags": ["московская норма"],
                    "tags": ["plural"],
                },
            ],
        )

    def test_process_transcriptions_ru_template_2(self):
        # https://ru.wiktionary.org/wiki/Шаблон:transcriptions-ru
        self.wxr.wtp.add_page(
            "Шаблон:transcriptions-ru",
            10,
            "ед. ч. [bɐˈlʲit], мн. ч. [bɐˈlʲidɨ]",
        )
        self.process_template_and_assert(
            "{{transcriptions-ru|боли́д|боли́ды|омофоны=болит}}",
            process_transcriptions_ru_template,
            [
                {
                    "ipa": "[bɐˈlʲit]",
                    "homophones": ["болит"],
                    "tags": ["singular"],
                },
                {
                    "ipa": "[bɐˈlʲidɨ]",
                    "tags": ["plural"],
                },
            ],
        )

    def test_process_transcription_la_template(self):
        # https://ru.wiktionary.org/wiki/procrastinatio
        self.wxr.wtp.add_page(
            "Шаблон:transcription-la",
            10,
            "МФА (классическое произношение): [proː.kraːs.tiˈnaː.ti.oː]",
        )
        self.process_template_and_assert(
            "{{transcription-la|prōcrāstinātiō |}}",
            process_transcription_la_template,
            [
                {
                    "ipa": "[proː.kraːs.tiˈnaː.ti.oː]",
                    "raw_tags": ["классическое произношение"],
                }
            ],
        )

    def test_process_transcription_grc_template(self):
        # https://ru.wiktionary.org/wiki/Ζεύς
        self.wxr.wtp.add_page(
            "Шаблон:transcription-grc",
            10,
            """МФА: <span class="IPA" lang="grc">[zde͜ʊ́s]</span> → <span class="IPA" lang="grc">[zeɸs]</span> → <span class="IPA" lang="grc">[zefs]</span>
* '''Аттическое произношение''': [zde͜ʊ́s]
* Египетское произношение: [zeʍs]""",
        )
        self.process_template_and_assert(
            "{{transcription-grc|Ζεύς}}",
            process_transcription_grc_template,
            [
                {"ipa": "[zde͜ʊ́s]"},
                {"ipa": "[zeɸs]"},
                {"ipa": "[zefs]"},
                {"ipa": "[zde͜ʊ́s]", "raw_tags": ["Аттическое произношение"]},
                {"ipa": "[zeʍs]", "raw_tags": ["Египетское произношение"]},
            ],
        )

    def test_rhyme_section(self):
        page_data = parse_page(
            self.wxr,
            "",
            """= {{-ru-}} =
== {{з|ударение=вода́}} ==
=== Морфологические и синтаксические свойства ===
{{сущ-ru}}
=== Произношение ===
==== Рифмы ====
* Ед. ч., им. п.: [[Рифмы:ˈda|-ˈd̪a]]
==== Значение ====
# [[влага]]""",
        )
        self.assertEqual(
            page_data[0]["sounds"],
            [{"rhymes": "-ˈd̪a", "tags": ["singular", "nominative"]}],
        )

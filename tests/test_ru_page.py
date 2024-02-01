from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestRUPage(TestCase):
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

    def test_level_2_layout(self):
        # Navigates homonyms/homographs
        # E.g. https://ru.wiktionary.org/wiki/овощ
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.wxr.wtp.add_page("Шаблон:з", 10, "{{PAGENAME}} {{{1|}}}")
        self.wxr.wtp.add_page("Шаблон:сущ ru m ina 4e", 10, "Существительное")
        self.assertEqual(
            parse_page(
                self.wxr,
                "овощ",
                """= {{-ru-}} =
== {{з|I}} ==
=== Морфологические и синтаксические свойства ===
{{сущ ru m ina 4e
|основа=о́вощ
|основа1=овощ
}}
=== Семантические свойства ===
==== Значение ====
# растение

== {{з|II}} ==
=== Морфологические и синтаксические свойства ===
{{сущ ru m ina 4e
|основа=о́вощ
|основа1=овощ
}}
=== Семантические свойства ===
==== Значение ====
# половой член""",
            ),
            [
                {
                    "lang": "Русский",
                    "lang_code": "ru",
                    "pos": "noun",
                    "word": "овощ",
                    "senses": [{"glosses": ["растение"]}],
                },
                {
                    "lang": "Русский",
                    "lang_code": "ru",
                    "pos": "noun",
                    "word": "овощ",
                    "senses": [{"glosses": ["половой член"]}],
                },
            ],
        )

    def test_no_level_2_layout(self):
        # Navigates in case of absence of H2 headings (homonyms/homographs)
        # E.g. https://ru.wiktionary.org/wiki/сарлык
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "сарлык",
                """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
{{сущ-ru|сарлы́к|мо 3a}}
=== Семантические свойства ===
==== Значение ====
# домашнее животное""",
            ),
            [
                {
                    "lang": "Русский",
                    "lang_code": "ru",
                    "pos": "noun",
                    "word": "сарлык",
                    "senses": [{"glosses": ["домашнее животное"]}],
                },
            ],
        )

    def test_pos_in_title(self):
        self.wxr.wtp.start_page("difference")
        self.wxr.wtp.add_page("Шаблон:-en-", 10, "Английский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "difference",
                """= {{-en-}} =
=== существительное ===
*[[различие]], [[отличие]], [[разница]]""",
            ),
            [
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "pos": "noun",
                    "word": "difference",
                    "senses": [{"glosses": ["различие, отличие, разница"]}],
                }
            ],
        )

    def test_level_3_sense(self):
        self.wxr.wtp.start_page("-ability")
        self.wxr.wtp.add_page("Шаблон:-en-", 10, "Английский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "-ability",
                """= {{-en-}} =
=== Значение ===
# при добавлении к прилагательным""",
            ),
            [
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "word": "-ability",
                    "senses": [
                        {"glosses": ["при добавлении к прилагательным"]}
                    ],
                }
            ],
        )

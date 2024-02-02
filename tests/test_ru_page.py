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
{{morph|тип=s|lang=en|}}
=== Значение ===
# при добавлении к прилагательным""",
            ),
            [
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "word": "-ability",
                    "pos": "suffix",
                    "tags": ["morpheme"],
                    "senses": [
                        {"glosses": ["при добавлении к прилагательным"]}
                    ],
                }
            ],
        )

    def test_pos_in_header_template(self):
        self.wxr.wtp.start_page("go")
        self.wxr.wtp.add_page("Шаблон:-romaji-", 10, "Ромадзи")
        self.assertEqual(
            parse_page(
                self.wxr,
                "go",
                """= {{-romaji-}} =
== {{заголовок|(существительное I)}} ==
=== Семантические свойства ===
==== Значение ====
# язык""",
            ),
            [
                {
                    "lang": "Ромадзи",
                    "lang_code": "romaji",
                    "word": "go",
                    "pos": "noun",
                    "senses": [{"glosses": ["язык"]}],
                }
            ],
        )

    def test_level_3_pronunciation(self):
        self.wxr.wtp.start_page("wait")
        self.wxr.wtp.add_page("Шаблон:-en-", 10, "Английский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "wait",
                """= {{-en-}} =
=== Произношение ===
{{transcription|weɪt}}

== {{заголовок|(глагол)}} ==
=== Морфологические и синтаксические свойства ===
{{гл en reg|wait}}
=== Семантические свойства ===
==== Значение ====
# ждать

== {{заголовок|(существительное)}} ==
=== Морфологические и синтаксические свойства ===
{{сущ en|wait}}

=== Семантические свойства ===
==== Значение ====
# ожидание""",
            ),
            [
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "word": "wait",
                    "pos": "verb",
                    "senses": [{"glosses": ["ждать"]}],
                },
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "word": "wait",
                    "pos": "noun",
                    "sounds": [{"ipa": "weɪt"}],
                    "senses": [{"glosses": ["ожидание"]}],
                },
            ],
        )

    def test_plain_text_pos(self):
        self.wxr.wtp.start_page("anima")
        self.wxr.wtp.add_page("Шаблон:-eo-", 10, "Эсперанто")
        self.assertEqual(
            parse_page(
                self.wxr,
                "anima",
                """= {{-eo-}} =
Прилагательное.
=== Семантические свойства ===
==== Значение ====
[[душевный]], [[духовный]]""",
            ),
            [
                {
                    "lang": "Эсперанто",
                    "lang_code": "eo",
                    "word": "anima",
                    "pos": "adj",
                    "senses": [{"glosses": ["душевный, духовный"]}],
                },
            ],
        )

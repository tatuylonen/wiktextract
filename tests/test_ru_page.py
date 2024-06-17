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
        # "Прилагательное" -> "adj"
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

    def test_suffix_pos_template(self):
        self.wxr.wtp.start_page("-ен")
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "-ен",
                """= {{-ru-}} =
== {{заголовок|I}} ==
{{suffix ru|ен|оконч=ь}}
=== Значение ===
# при""",
            ),
            [
                {
                    "lang": "Русский",
                    "lang_code": "ru",
                    "word": "-ен",
                    "pos": "suffix",
                    "tags": ["morpheme"],
                    "senses": [{"glosses": ["при"]}],
                },
            ],
        )

    def test_form_of_template(self):
        self.wxr.wtp.start_page("ними")
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.wxr.wtp.add_page(
            "Шаблон:Форма-мест",
            10,
            """<b>ни́<span class="hyph" style="color:lightgreen;">-</span>ми</b> <br/><ul class="transcription" style="margin-left:0; list-style:none;"><li>[[w:Международный фонетический алфавит|МФА]]:&nbsp;&#91;<span class="IPA" style="white-space: nowrap;">ˈnʲimʲɪ</span>&#93;</li></ul>

* форма творительного падежа множественного числа  местоимения&#32;''[[они#Русский|они]]''[[Категория:Формы местоимений/ru]][[Категория:Формы местоимений/ru]][[Категория:Словоформы/ru]]""",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "ними",
                """= {{-ru-|nocat}} =
{{Форма-мест|они|творительного|мн|слоги={{по-слогам|ни́|ми}}|МФА=ˈnʲimʲɪ}}""",
            ),
            [
                {
                    "categories": ["Формы местоимений/ru", "Словоформы/ru"],
                    "lang": "Русский",
                    "lang_code": "ru",
                    "word": "ними",
                    "pos": "pron",
                    "senses": [
                        {
                            "glosses": [
                                "форма творительного падежа множественного числа местоимения они"
                            ],
                            "form_of": [{"word": "они"}],
                            "tags": ["form-of"],
                        }
                    ],
                    "sounds": [{"ipa": "ˈnʲimʲɪ"}],
                },
            ],
        )

    def test_morphological_section_tags(self):
        self.wxr.wtp.start_page("вода")
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")
        self.wxr.wtp.add_page(
            "Шаблон:сущ-ru",
            10,
            """[[существительное|Существительное]], неодушевлённое, женский род, 1-е [[склонение]]&#32;(тип склонения 1d&#39;  по [[Викисловарь:Использование словаря Зализняка|классификации А.&#160;А.&#160;Зализняка]]).&#32;В сочетаниях типа «''на́ воду''», «''по́д воду''», «''по́ воду''», «''за́ воду''» ударение может падать на предлог; слово «''вода''» при этом превращается в [[клитика|клитику]].[[Категория:Русские лексемы]][[Категория:Русские существительные]][[Категория:Неодушевлённые/ru]][[Категория:Женский род/ru]][[Категория:Русские существительные,  склонение 1d&#39;]][[Категория:Русские лексемы]]""",
        )
        page_data = parse_page(
            self.wxr,
            "вода",
            """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
{{сущ-ru}}

=== Семантические свойства ===
==== Значение ====

# gloss""",
        )
        self.assertEqual(
            page_data[0]["tags"], ["inanimate", "feminine", "declension-1"]
        )

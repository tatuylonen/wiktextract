import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.gloss import extract_gloss
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestRUGloss(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(
                dump_file_lang_code="ru", capture_language_codes=None
            ),
        )
        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "Русский")

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_ru_extract_gloss(self):
        # https://ru.wiktionary.org/wiki/овощ
        test_cases = [
            # Cleans examples from gloss and raw_glosses
            {
                "input": "==== Значение ====\n# [[съедобный|съедобная]] [[часть]] овоща [1] {{пример|Недолго думая, отправляю овощ в рот.|М. И. Саитов|Островки||Бельские Просторы|2010|источник=НКРЯ}}",
                "expected": {
                    "glosses": ["съедобная часть овоща [1]"],
                },
            },
            # Extracts tags
            {
                "input": "==== Значение ====\n# {{разг.|ru}}, {{неодобр.|ru}} или {{пренебр.|ru}} [[бесхарактерный]], [[безвольный]] человек, лишённый активной жизненной позиции {{пример|}}",
                "expected": {
                    "tags": ["colloquial", "disapproving", "derogatory"],
                    "glosses": [
                        "бесхарактерный, безвольный человек, лишённый активной жизненной позиции"
                    ],
                },
            },
            # Extracts notes
            {
                "input": "==== Значение ====\n# {{помета|часто мн}} обобщающее [[название]] растительной пищи, не включающей [[фрукт]]ы ''и'' [[крупа|крупы]]",
                "expected": {
                    "glosses": [
                        "обобщающее название растительной пищи, не включающей фрукты и крупы"
                    ],
                    "tags": ["often", "plural"],
                },
            },
        ]

        self.wxr.wtp.add_page(
            "Шаблон:разг.",
            10,
            '[[Викисловарь:Условные сокращения|<span style="font-style: italic;background-color:#CCFFFF;cursor:help;" title="разговорное">разг.</span>]]',
        )
        self.wxr.wtp.add_page(
            "Шаблон:неодобр.",
            10,
            '[[Викисловарь:Условные сокращения|<span style="font-style: italic;background-color:#CCFFFF;cursor:help;" title="неодобрительное">неодобр.</span>]]',
        )
        self.wxr.wtp.add_page(
            "Шаблон:пренебр.",
            10,
            '[[Викисловарь:Условные сокращения|<span style="font-style: italic;background-color:#CCFFFF;cursor:help;" title="пренебрежительное">пренебр.</span>]]',
        )
        self.wxr.wtp.add_page("Шаблон:помета", 10, "часто мн. ч.")

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("овощ")
                page_data = [
                    WordEntry(word="овощ", lang_code="ru", lang="Русский")
                ]

                root = self.wxr.wtp.parse(case["input"])

                extract_gloss(self.wxr, page_data[-1], root.children[0])

                new_sense = (
                    page_data[-1]
                    .senses[-1]
                    .model_dump(exclude_defaults=True, exclude={"examples"})
                )
                self.assertEqual(new_sense, case["expected"])

    def test_no_list_gloss(self):
        self.wxr.wtp.start_page("east")
        self.wxr.wtp.add_page("Шаблон:-en-", 10, "Английский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "east",
                """= {{-en-}} =
== {{заголовок|(существительное)}} ==
=== Морфологические и синтаксические свойства ===
{{сущ en -}}
=== Семантические свойства ===
==== Значение ====
[[восток]]""",
            ),
            [
                {
                    "lang": "Английский",
                    "lang_code": "en",
                    "word": "east",
                    "pos": "noun",
                    "senses": [{"glosses": ["восток"]}],
                }
            ],
        )

    def test_gloss_under_morphological_section(self):
        self.wxr.wtp.start_page("-гез")
        self.wxr.wtp.add_page("Шаблон:-tt-", 10, "Татарский")
        self.assertEqual(
            parse_page(
                self.wxr,
                "-гез",
                """= {{-tt-}} =
== {{заголовок|I}} ==
=== Морфологические и синтаксические свойства ===
{{affix tt|гез|вид=аффикс принадлежности}}
==== Значение ====
# при""",
            ),
            [
                {
                    "lang": "Татарский",
                    "lang_code": "tt",
                    "word": "-гез",
                    "pos": "affix",
                    "senses": [{"glosses": ["при"]}],
                },
            ],
        )

    def test_gloss_under_sounds_section(self):
        self.wxr.wtp.start_page("туп")
        self.wxr.wtp.add_page("Шаблон:-tt-", 10, "Татарский")
        self.wxr.wtp.add_page("Шаблон:по слогам", 10, "туп")
        self.assertEqual(
            parse_page(
                self.wxr,
                "туп",
                """= {{-tt-}} =
== {{з|II}} ==
=== Морфологические и синтаксические свойства ===
{{сущ tt задн согласн глух|туп|слоги={{по слогам|туп}}|alt=tup}}
=== Произношение ===
{{transcription|}}
==== Значение ====
# ''подр.'' [[топ]]""",
            ),
            [
                {
                    "hyphenation": "туп",
                    "lang": "Татарский",
                    "lang_code": "tt",
                    "word": "туп",
                    "pos": "noun",
                    "senses": [{"glosses": ["подр. топ"]}],
                },
            ],
        )

    def test_gloss_topic(self):
        self.wxr.wtp.start_page("прыгать")
        self.wxr.wtp.add_page(
            "Шаблон:=",
            10,
            "то же, что прыгать с парашютом; покидать летательный аппарат (как правило, неисправный, подбитый и т.п.) в полёте с парашютом",
        )
        self.wxr.wtp.add_page(
            "Шаблон:гл ru 1a",
            10,
            "[[глагол|Глагол]], [[несовершенный вид]], [[Категория:Русские лексемы]][[Категория:Русские глаголы]][[Категория:Русские глаголы несовершенного вида]] [[непереходный]][[Категория:Русские непереходные глаголы]],    тип спряжения по [[Викисловарь:Использование словаря Зализняка|классификации А.&#160;Зализняка]]&#160;—&#32;1a.      Соответствующий глагол совершенного вида&#160;—&#32;[[прыгнуть]].[[Категория:Глаголы в видовых парах]][[Категория:Глаголы, спряжение 1a]]",
        )
        self.wxr.wtp.add_page(
            "Шаблон:по-слогам",
            10,
            'пры́<span class="hyph" style="color:lightgreen;">-</span>гать',
        )
        self.wxr.wtp.add_page(
            "Шаблон:авиац.",
            10,
            '[[Викисловарь:Условные сокращения|<span style="font-style: italic;background-color:#CCFFFF;cursor:help;" title="авиационный термин">авиац.</span>]][[Категория:Авиационные термины/ru|африканочка]]',
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "прыгать",
                """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
{{гл ru 1a
|основа = пры́га
|слоги={{по-слогам|пры́|гать}}
|НП=1
|соотв=прыгнуть
}}
=== Семантические свойства ===
==== Значение ====
# {{авиац.|ru}} то же""",
            ),
            [
                {
                    "categories": [
                        "Русские лексемы",
                        "Русские глаголы",
                        "Русские глаголы несовершенного вида",
                        "Русские непереходные глаголы",
                        "Глаголы в видовых парах",
                        "Глаголы, спряжение 1a",
                    ],
                    "lang": "Русский",
                    "lang_code": "ru",
                    "word": "прыгать",
                    "pos": "verb",
                    "senses": [
                        {
                            "categories": ["Авиационные термины/ru"],
                            "glosses": ["то же"],
                            "topics": ["aeronautics"],
                        }
                    ],
                    "tags": ["imperfective", "intransitive"],
                    "hyphenation": "пры́-гать",
                },
            ],
        )

    def test_gloss_slang_topic(self):
        self.wxr.wtp.start_page("фуражка")
        self.wxr.wtp.add_page(
            "Шаблон:воен. жарг.",
            10,
            '[[Викисловарь:Условные сокращения|<span style="font-style: italic;background-color:#CCFFFF;cursor:help;" title="военный жаргон">воен. жарг.</span>]][[Категория:Военный жаргон/ru|африканочка]]',
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "фуражка",
                """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
{{сущ-ru}}
=== Семантические свойства ===
==== Значение ====
# {{воен. жарг.|ru}} то же, что фуражная шапка""",
            ),
            [
                {
                    "lang": "Русский",
                    "lang_code": "ru",
                    "word": "фуражка",
                    "pos": "noun",
                    "senses": [
                        {
                            "categories": ["Военный жаргон/ru"],
                            "glosses": ["то же, что фуражная шапка"],
                            "tags": ["slang"],
                            "topics": ["military"],
                        }
                    ],
                },
            ],
        )

    def test_tag_gloss_template(self):
        self.wxr.wtp.start_page("перехаживать")
        self.wxr.wtp.add_page("Шаблон:многокр.", 10, "многокр. к переходить")
        self.assertEqual(
            parse_page(
                self.wxr,
                "перехаживать",
                """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
{{гл ru 1a}}
=== Семантические свойства ===
==== Значение ====
# {{многокр.|переходить}} """,
            ),
            [
                {
                    "lang": "Русский",
                    "lang_code": "ru",
                    "word": "перехаживать",
                    "pos": "verb",
                    "senses": [
                        {
                            "glosses": ["многокр. к переходить"],
                            "tags": ["iterative"],
                        }
                    ],
                },
            ],
        )

    def test_meaning_template_under_level4_title(self):
        self.wxr.wtp.start_page("организм")
        self.wxr.wtp.add_page("Шаблон:биол.", 10, "биол.")
        root = self.wxr.wtp.parse("""==== Значение ====
# {{значение
|определение=[[совокупность]] [[система органов|систем органов]] как единая работоспособная система
|пометы={{биол.|ru}}
|примеры={{пример|Организм человека имеет значительный запас прочности, каждое движение обеспечивается совместной работой различных групп мышц в дублирующем режиме.|Олег Васильев|Художественная йога. Теория и практика|издание=Боевое искусство планеты|2004|источник=НКРЯ}}
|антонимы=-
|гипонимы=организм человека, организм животного; кибернетический организм
|якорь=физиология
|язык=ru
}}""")  # noqa: E501
        word_entry = WordEntry(
            word="организм", lang="Русский", lang_code="ru", pos="noun"
        )
        extract_gloss(self.wxr, word_entry, root.children[0])
        data = word_entry.model_dump(exclude_defaults=True)
        del data["senses"][0]["examples"]
        self.assertEqual(
            data,
            {
                "lang": "Русский",
                "lang_code": "ru",
                "word": "организм",
                "pos": "noun",
                "senses": [
                    {
                        "glosses": [
                            "совокупность систем органов как единая работоспособная система"
                        ],
                        "topics": ["biology"],
                    }
                ],
                "hyponyms": [
                    {
                        "word": "организм человека",
                        "sense": "совокупность систем органов как единая работоспособная система",
                    },
                    {
                        "word": "организм животного",
                        "sense": "совокупность систем органов как единая работоспособная система",
                    },
                    {
                        "word": "кибернетический организм",
                        "sense": "совокупность систем органов как единая работоспособная система",
                    },
                ],
            },
        )
        self.assertEqual(len(word_entry.senses[0].examples), 1)

    def test_meaning_template_under_level3_title(self):
        self.wxr.wtp.add_page("Шаблон:-cmn-", 10, "Китайский (Гуаньхуа)")
        self.assertEqual(
            parse_page(
                self.wxr,
                "猫",
                """= {{-cmn-}} =
=== Морфологические и синтаксические свойства ===
{{cmn-noun|s|pin=māo|pint=mao1|tra=貓|sim=猫|mw=只|rs=犬09}}
=== Семантические свойства ===
# {{значение
  |определение = [[кот]], [[кошка]]
  |пометы      = [[зоол.]]
  |гиперонимы  = [[动物]]
  |язык        = cmn
}}""",
            ),
            [
                {
                    "lang": "Китайский (Гуаньхуа)",
                    "lang_code": "cmn",
                    "word": "猫",
                    "pos": "noun",
                    "senses": [
                        {"glosses": ["кот, кошка"], "topics": ["zoology"]}
                    ],
                    "hypernyms": [{"word": "动物", "sense": "кот, кошка"}],
                },
            ],
        )

    def test_nested_lists(self):
        self.wxr.wtp.add_page("Шаблон:-en-", 10, "Английский")
        page_data = parse_page(
            self.wxr,
            "keep",
            """= {{-en-}} =
=== Морфологические и синтаксические свойства ===
{{гл en irreg|keep|keeps|kept|kept|keeping|слоги={{по-слогам|keep}}
}}
=== Семантические свойства ===
==== Значение ====
# [[сохраняться]], не портиться
## [[хранить]], [[сохранять]], не давать портиться
## сохранять новизну, не устаревать""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {"glosses": ["сохраняться, не портиться"]},
                {
                    "glosses": [
                        "сохраняться, не портиться",
                        "хранить, сохранять, не давать портиться",
                    ]
                },
                {
                    "glosses": [
                        "сохраняться, не портиться",
                        "сохранять новизну, не устаревать",
                    ]
                },
            ],
        )

    def test_not_tag_dot_template(self):
        self.wxr.wtp.add_page("Шаблон:-en-", 10, "Английский")
        self.wxr.wtp.add_page(
            "Шаблон:аббр.",
            10,
            '[[Викисловарь:Условные сокращения|<span style="font-style: italic;cursor:help;" title="сокращённое">сокр.</span>]][[Категория:Аббревиатуры/en|африканочка]]&#x0020;от [[what you see is what you get]]&#x003B; что видишь, то и получишь',
        )
        page_data = parse_page(
            self.wxr,
            "WYSIWYG",
            """= {{-en-}} =
=== Семантические свойства ===
==== Значение ====
# {{аббр.|en|what you see is what you get|что видишь, то и получишь}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": [
                        "сокр. от what you see is what you get; что видишь, то и получишь"
                    ],
                    "categories": ["Аббревиатуры/en"],
                }
            ],
        )

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
                "input": "# [[съедобный|съедобная]] [[часть]] овоща [1] {{пример|Недолго думая, отправляю овощ в рот.|М. И. Саитов|Островки||Бельские Просторы|2010|источник=НКРЯ}}",
                "expected": {
                    "glosses": ["съедобная часть овоща [1]"],
                },
            },
            # Extracts tags
            {
                "input": "# {{разг.|ru}}, {{неодобр.|ru}} или {{пренебр.|ru}} [[бесхарактерный]], [[безвольный]] человек, лишённый активной жизненной позиции {{пример|}}",
                "expected": {
                    "tags": ["colloquial", "disapproving", "derogatory"],
                    "glosses": [
                        "бесхарактерный, безвольный человек, лишённый активной жизненной позиции"
                    ],
                    "raw_glosses": [
                        "разг., неодобр. или пренебр. бесхарактерный, безвольный человек, лишённый активной жизненной позиции"
                    ],
                },
            },
            # Extracts notes
            {
                "input": "# {{помета|часто мн}} обобщающее [[название]] растительной пищи, не включающей [[фрукт]]ы ''и'' [[крупа|крупы]]",
                "expected": {
                    "notes": ["часто мн. ч."],
                    "glosses": [
                        "обобщающее название растительной пищи, не включающей фрукты и крупы"
                    ],
                    "raw_glosses": [
                        "часто мн. ч. обобщающее название растительной пищи, не включающей фрукты и крупы"
                    ],
                },
            },
        ]

        self.wxr.wtp.add_page("Шаблон:разг.", 10, "разг.")
        self.wxr.wtp.add_page("Шаблон:неодобр.", 10, "неодобр.")
        self.wxr.wtp.add_page("Шаблон:пренебр.", 10, "пренебр.")
        self.wxr.wtp.add_page("Шаблон:помета", 10, "часто мн. ч.")

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("овощ")
                page_data = [
                    WordEntry(word="овощ", lang_code="ru", lang="Русский")
                ]

                root = self.wxr.wtp.parse(case["input"])

                extract_gloss(self.wxr, page_data[-1], root)

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
        self.wxr.wtp.add_page("Шаблон:авиац.", 10, "авиац.")
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
                    "lang": "Русский",
                    "lang_code": "ru",
                    "word": "прыгать",
                    "pos": "verb",
                    "senses": [
                        {
                            "glosses": ["то же"],
                            "raw_glosses": ["авиац. то же"],
                            "topics": ["aeronautics"],
                        }
                    ],
                },
            ],
        )

    def test_gloss_slang_topic(self):
        self.wxr.wtp.start_page("фуражка")
        self.wxr.wtp.add_page("Шаблон:воен. жарг.", 10, "воен. жарг.")
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
                            "glosses": ["то же, что фуражная шапка"],
                            "raw_glosses": [
                                "воен. жарг. то же, что фуражная шапка"
                            ],
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
}}""")
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

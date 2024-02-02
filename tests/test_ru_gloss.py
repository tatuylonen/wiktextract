import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.gloss import extract_gloss
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestRUGloss(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(dump_file_lang_code="ru"),
        )

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
                    "tags": ["разг.", "неодобр.", "пренебр."],
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

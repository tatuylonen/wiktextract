import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestRUPage(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(
                dump_file_lang_code="ru", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    # def get_default_page_data(self) -> list[WordEntry]:
    #     return [WordEntry(word="test", lang_code="es", lang="Language")]

    def test_ru_parse_page_1(self):
        # Navigates homonyms/homographs
        # E.g. https://ru.wiktionary.org/wiki/овощ

        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "")
        self.wxr.wtp.add_page("Шаблон:з", 10, "")

        page_text = """= {{-ru-}} =
== {{з|I}} ==
=== Морфологические и синтаксические свойства ===
== {{з|II}} ==
=== Морфологические и синтаксические свойства ===
"""

        page_data_dicts = parse_page(self.wxr, "овощ", page_text)

        self.assertEqual(len(page_data_dicts), 2)

    def test_ru_parse_page_2(self):
        # Navigates in case of absence of H2 headings (homonyms/homographs)
        # E.g. https://ru.wiktionary.org/wiki/сарлык

        self.wxr.wtp.add_page("Шаблон:-ru-", 10, "")

        page_text = """= {{-ru-}} =
=== Морфологические и синтаксические свойства ===
"""

        page_data_dicts = parse_page(self.wxr, "овощ", page_text)

        self.assertEqual(len(page_data_dicts), 1)

    def test_pos_in_title(self):
        self.maxDiff = None
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

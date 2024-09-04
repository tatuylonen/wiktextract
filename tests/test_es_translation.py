import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.models import WordEntry
from wiktextract.extractor.es.translation import extract_translation_section
from wiktextract.wxr_context import WiktextractContext


class TestESTranslation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_t_roman(self):
        self.wxr.wtp.start_page("hola")
        self.wxr.wtp.add_page(
            "Plantilla:t",
            10,
            "* Chino: &#91;1&#93;&nbsp;[[你好#Chino|你好]] <sup>[[:zh:你好|(zh)]]</sup> “nĭ hăo”[[Categoría:Español-Chino]], [[您好#Chino|您好]] <sup>[[:zh:您好|(zh)]]</sup> “nín hăo”&nbsp;(formal)",
        )
        word_entry = WordEntry(word="hola", lang_code="es", lang="Español")
        root = self.wxr.wtp.parse(
            "{{t|zh|a1=1|t1=你好|tl1=nĭ hăo|t2=您好|tl2=nín hăo|nota2=formal}}"
        )
        extract_translation_section(self.wxr, word_entry, root)
        self.assertEqual(
            [
                t.model_dump(exclude_defaults=True)
                for t in word_entry.translations
            ],
            [
                {
                    "lang": "Chino",
                    "lang_code": "zh",
                    "word": "你好",
                    "senseids": ["1"],
                    "roman": "nĭ hăo",
                },
                {
                    "lang": "Chino",
                    "lang_code": "zh",
                    "word": "您好",
                    "roman": "nín hăo",
                    "raw_tags": ["formal"],
                },
            ],
        )

    def test_t_gender(self):
        self.wxr.wtp.start_page("hola")
        self.wxr.wtp.add_page(
            "Plantilla:t",
            10,
            "* Tailandés: &#91;1&#93;&nbsp;[[สวัสดีครับ#Tailandés|สวัสดีครับ]] <sup>[[:th:สวัสดีครับ|(th)]]</sup>&nbsp;(''masculino'')[[Categoría:Español-Tailandés]], [[สวัสดีค่ะ#Tailandés|สวัสดีค่ะ]] <sup>[[:th:สวัสดีค่ะ|(th)]]</sup>&nbsp;(''femenino'')",
        )
        word_entry = WordEntry(word="hola", lang_code="es", lang="Español")
        root = self.wxr.wtp.parse(
            "{{t|th|a1=1|t1=สวัสดีครับ|g1=m|t2=สวัสดีค่ะ|g2=f}}"
        )
        extract_translation_section(self.wxr, word_entry, root)
        self.assertEqual(
            [
                t.model_dump(exclude_defaults=True)
                for t in word_entry.translations
            ],
            [
                {
                    "lang": "Tailandés",
                    "lang_code": "th",
                    "word": "สวัสดีครับ",
                    "senseids": ["1"],
                    "tags": ["masculine"],
                },
                {
                    "lang": "Tailandés",
                    "lang_code": "th",
                    "word": "สวัสดีค่ะ",
                    "tags": ["feminine"],
                },
            ],
        )

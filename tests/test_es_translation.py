import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.models import WordEntry
from wiktextract.extractor.es.translation import extract_translation
from wiktextract.wxr_context import WiktextractContext


class TestESTranslation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_page_data(self) -> list[WordEntry]:
        return [
            WordEntry(
                word="test",
                lang_code="es",
                lang="Language",
            )
        ]

    def test_es_extract_translation(self):
        # Test cases from https://es.wiktionary.org/wiki/Plantilla:t+
        self.wxr.wtp.add_page(
            "Plantilla:t+",
            10,
            """* {{#switch:{{{1}}}
| af = afrikáans
| de = alemán
| fr = francés
| hy = armenio
}}: {{{3}}}""",
        )

        test_cases = [
            {
                # https://es.wiktionary.org/wiki/calderón
                "input": "{{t+|ar|}}",
                "expected": [],
            },
            {
                "input": "{{t+|af|1|kat}}",
                "expected": [
                    {
                        "lang": "afrikáans",
                        "lang_code": "af",
                        "word": "kat",
                        "senseids": ["1"],
                    }
                ],
            },
            {
                "input": "{{t+|de|1, 2|Katze|f|,|1|Kater|m|nota|gato macho|,|8|Tic Tac Toe}}",
                "expected": [
                    {
                        "lang": "alemán",
                        "lang_code": "de",
                        "word": "Katze",
                        "senseids": ["1", "2"],
                        "raw_tags": ["f"],
                    },
                    {
                        "lang_code": "de",
                        "lang": "alemán",
                        "word": "Kater",
                        "senseids": ["1"],
                        "raw_tags": ["m"],
                        "notes": ["gato macho"],
                    },
                    {
                        "lang_code": "de",
                        "lang": "alemán",
                        "word": "Tic Tac Toe",
                        "senseids": ["8"],
                    },
                ],
            },
            {
                "input": "{{t+|fr|1|profession|nl|de|bateleur}}",
                "expected": [
                    {
                        "lang": "francés",
                        "lang_code": "fr",
                        "word": "profession de bateleur",
                        "senseids": ["1"],
                    }
                ],
            },
            {
                "input": "{{t+|hy|1|կատու|tr|katu}}",
                "expected": [
                    {
                        "lang": "armenio",
                        "lang_code": "hy",
                        "word": "կատու",
                        "roman": "katu",
                        "senseids": ["1"],
                    }
                ],
            },
            {
                "input": "{{t+|hy|1|կատու|tr=katu}}",
                "expected": [
                    {
                        "lang": "armenio",
                        "lang_code": "hy",
                        "word": "կատու",
                        "roman": "katu",
                        "senseids": ["1"],
                    }
                ],
            },
            {
                "input": "{{t+|de|amphibisch|adj|,|Amphibie|sust|,|Amphibium|sust}}",
                "expected": [
                    {
                        "lang": "alemán",
                        "lang_code": "de",
                        "word": "amphibisch",
                        "raw_tags": ["adj"],
                    },
                    {
                        "lang": "alemán",
                        "lang_code": "de",
                        "word": "Amphibie",
                        "raw_tags": ["sust"],
                    },
                    {
                        "lang": "alemán",
                        "lang_code": "de",
                        "word": "Amphibium",
                        "raw_tags": ["sust"],
                    },
                ],
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                page_data = self.get_default_page_data()

                root = self.wxr.wtp.parse(case["input"])

                extract_translation(self.wxr, page_data[-1], root.children[0])

                translations = [
                    t.model_dump(exclude_defaults=True)
                    for t in page_data[-1].translations
                ]
                self.assertEqual(
                    translations,
                    case["expected"],
                )

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
        extract_translation(self.wxr, word_entry, root.children[0])
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
        extract_translation(self.wxr, word_entry, root.children[0])
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

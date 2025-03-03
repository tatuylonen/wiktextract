from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.id.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestIdGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="id"),
            WiktionaryConfig(
                dump_file_lang_code="id", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_gloss_nested_list(self):
        self.wxr.wtp.add_page("Templat:bhs", 10, "bahasa Indonesia")
        page_data = parse_page(
            self.wxr,
            "cinta",
            """=={{bhs|id}}==
===Nomina===
[[Kategori:id:Nomina ]]
# rasa sayang atau kasih yang kuat
## rasa [[sayang]]""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "categories": ["id:Nomina"],
                    "lang": "bahasa Indonesia",
                    "lang_code": "id",
                    "pos": "noun",
                    "pos_title": "Nomina",
                    "word": "cinta",
                    "senses": [
                        {"glosses": ["rasa sayang atau kasih yang kuat"]},
                        {
                            "glosses": [
                                "rasa sayang atau kasih yang kuat",
                                "rasa sayang",
                            ]
                        },
                    ],
                }
            ],
        )

    def test_plural_form(self):
        page_data = parse_page(
            self.wxr,
            "anjing",
            """==bahasa Indonesia==
===Nomina===
'''anjing''' (plural: [[anjing-anjing]])
# mamalia""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [{"form": "anjing-anjing", "tags": ["plural"]}],
        )

    def test_variasi(self):
        self.wxr.wtp.add_page(
            "Templat:variasi",
            10,
            """''variasi dari kata [[bengkarung]]''
[[Kategori:Turunan kata bengkarung]]
[[Kategori:id:Variasi kata]]""",
        )
        page_data = parse_page(
            self.wxr,
            "mengkarung",
            """==bahasa Indonesia==
===Nomina===
# {{variasi|bengkarung}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": [
                        "Turunan kata bengkarung",
                        "id:Variasi kata",
                    ],
                    "glosses": ["variasi dari kata bengkarung"],
                    "alt_of": [{"word": "bengkarung"}],
                    "tags": ["alt-of"],
                }
            ],
        )

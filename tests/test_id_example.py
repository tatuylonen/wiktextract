from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.id.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestIdExample(TestCase):
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

    def test_example_list(self):
        self.wxr.wtp.add_page("Templat:bhs", 10, "bahasa Indonesia")
        page_data = parse_page(
            self.wxr,
            "cinta",
            """==bahasa Palembang==
===Verba===
# [[tambah]]
#: ''payo '''bubuh''' pempeknyo, jangan semon-semon''
#:: ayo '''tambah''' pempeknya, jangan malu-malu""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "examples": [
                        {
                            "text": "payo bubuh pempeknyo, jangan semon-semon",
                            "translation": "ayo tambah pempeknya, jangan malu-malu",
                        }
                    ],
                    "glosses": ["tambah"],
                }
            ],
        )

    def test_italic_after_br(self):
        page_data = parse_page(
            self.wxr,
            "angin",
            """==bahasa Indonesia==
===Nomina===
# hawa; udara: <br />''ban berisi angin''""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["hawa; udara:"],
                    "examples": [{"text": "ban berisi angin"}],
                }
            ],
        )

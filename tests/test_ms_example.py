from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ms"),
            WiktionaryConfig(
                dump_file_lang_code="ms", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_italic(self):
        page_data = parse_page(
            self.wxr,
            "makan",
            """==Bahasa Melayu==
=== Takrifan ===
# memasukkan sesuatu ke dalam mulut
#: ''Jemputlah '''makan''' kuih ini.''
#:: ''.جمڤوتله '''ماکن''' کو<sup>ء</sup>يه اين''""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "examples": [
                        {
                            "text": "Jemputlah makan kuih ini.",
                            "translation": ".جمڤوتله ماکن کو^ءيه اين",
                        }
                    ],
                    "glosses": ["memasukkan sesuatu ke dalam mulut"],
                }
            ],
        )

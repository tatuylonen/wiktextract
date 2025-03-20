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

    def test_cp(self):
        self.wxr.wtp.add_page(
            "Templat:ko-usex",
            10,
            """<div class="h-usage-example"><i class="Kore mention e-example" lang="ko"><span style="background&#45;color:#FEF8EA"><b>젓가락</b></span>으로 먹다</i>&nbsp;<dl><dd><i lang="ko-Latn" class="e-transliteration tr Latn">'''jeotgarak'''euro meokda</i></dd><dd><span class="e-translation">makan menggunakan '''penyepit'''</span></dd></dl></div>[[Kategori:Kata bahasa Korea dengan contoh penggunaan|젓가락]]""",
        )
        page_data = parse_page(
            self.wxr,
            "젓가락",
            """==Bahasa Korea==
==== Kata nama ====
# [[penyepit]]
#* {{ko-usex|'''젓가락'''으로 먹다|makan menggunakan '''penyepit'''}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": [
                        "Kata bahasa Korea dengan contoh penggunaan"
                    ],
                    "examples": [
                        {
                            "text": "젓가락으로 먹다",
                            "roman": "jeotgarakeuro meokda",
                            "translation": "makan menggunakan penyepit",
                        }
                    ],
                    "glosses": ["penyepit"],
                }
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="tr"),
            WiktionaryConfig(
                dump_file_lang_code="tr", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_nested_list(self):
        self.wxr.wtp.add_page(
            "Şablon:t",
            10,
            """{{#switch:{{{1}}}
| bilişim = (''bilişim'')[[Kategori:İngilizcede bilişim]]
| #default = (''bazen'', ''özellikle'')
}}""",
        )
        page_data = parse_page(
            self.wxr,
            "FAT",
            """==İngilizce==
===Kısaltma===
# {{t|dil=en|bilişim}} File Allocation Table
## Bir veya
### {{t|dil=en|bazen|özellikle}} [[FAT12]].""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["İngilizcede bilişim"],
                    "glosses": ["File Allocation Table"],
                    "topics": ["informatics"],
                },
                {
                    "categories": ["İngilizcede bilişim"],
                    "glosses": ["File Allocation Table", "Bir veya"],
                    "topics": ["informatics"],
                },
                {
                    "categories": ["İngilizcede bilişim"],
                    "glosses": ["File Allocation Table", "Bir veya", "FAT12."],
                    "topics": ["informatics"],
                    "tags": ["sometimes", "especially"],
                },
            ],
        )

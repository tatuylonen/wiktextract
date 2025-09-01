from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.vi.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestViGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="vi"),
            WiktionaryConfig(
                dump_file_lang_code="vi", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_nested_list(self):
        self.wxr.wtp.add_page("Bản mẫu:term", 10, "(''[[Hóa học|Hóa học]]'')")
        data = parse_page(
            self.wxr,
            "băng",
            """==Tiếng Việt==
===Danh từ===
# [[nước|Nước]]
## {{term|Hóa học}} [[khoảng|Khoảng]]""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {"glosses": ["Nước"]},
                {"glosses": ["Nước", "Khoảng"], "topics": ["chemistry"]},
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.vi.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestViLinkage(TestCase):
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

    def test_synonym_in_gloss_list(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:synonym",
            10,
            """<span class="nyms đồng-nghĩa"><span class="defdate">Đồng nghĩa:</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">không còn dùng</span><span class="ib-brac qualifier-brac">)</span> <span class="Latn" lang="vi">[[:kỷ hà học#Tiếng&#95;Việt|kỷ hà học]]</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "hình học",
            """==Tiếng Việt==
===Danh từ===
# Ngành liên quan đến [[hình dạng]]
#: {{synonym|vi|kỷ hà học|q=không còn dùng}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "kỷ hà học",
                    "tags": ["obsolete"],
                    "sense": "Ngành liên quan đến hình dạng",
                }
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ko.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKoTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ko"),
            WiktionaryConfig(
                dump_file_lang_code="ko",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_tr_template(self):
        data = parse_page(
            self.wxr,
            "개",
            """== 한국어 ==
=== 명사 ===
==== 명사 1 ====
#  가축으로
===== 번역 =====
{{외국어|
* 구자라트어(gu): [[કુતરો]](kutro) (남성)
|
* 노비알(nov): [[hunde]] ((수컷/암컷) 개)
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "word": "કુતરો",
                    "roman": "kutro",
                    "raw_tags": ["남성"],
                    "lang": "구자라트어",
                    "lang_code": "gu",
                },
                {
                    "word": "hunde",
                    "raw_tags": ["수컷/암컷 개"],
                    "lang": "노비알",
                    "lang_code": "nov",
                },
            ],
        )

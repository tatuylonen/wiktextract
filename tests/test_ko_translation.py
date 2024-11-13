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
            "개",  # and page "아이"
            """== 한국어 ==
=== 명사 ===
==== 명사 1 ====
#  가축으로
===== 번역 =====
{{외국어|
* 구자라트어(gu): [[કુતરો]](kutro) (남성)
|
* 노비알(nov): [[hunde]] ((수컷/암컷) 개)
* 라트갈레어(bat-ltg): [[bārns]] (남성)
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
                {
                    "word": "bārns",
                    "raw_tags": ["남성"],
                    "lang": "라트갈레어",
                    "lang_code": "bat-ltg",
                },
            ],
        )

    def test_tr_after_gloss_list(self):
        data = parse_page(
            self.wxr,
            "하다",
            """== 한국어 ==
=== 동사 ===
# 사람이나 동물 또는 물체가 행동하거나 작용을 이루다.
{{외국어|
* 네덜란드어(nl): [[doen]]
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "word": "doen",
                    "lang": "네덜란드어",
                    "lang_code": "nl",
                    "sense": "사람이나 동물 또는 물체가 행동하거나 작용을 이루다.",
                }
            ],
        )

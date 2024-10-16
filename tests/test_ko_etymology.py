from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ko.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKoEtymology(TestCase):
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

    def test_lists(self):
        data = parse_page(
            self.wxr,
            "한글",
            """== 중국어 ==
=== 어원 ===
* 1) '[[크다]]'라는 뜻의 '[[한]]'에 '[[글]]'을 붙여 만듦.
* 2) 한국의 민족 또는 국가를 일컫는 '[[한]]'([[韓]])에 '[[글]]'([[㐎]])을 붙여 만듦.
=== 명사 ===
# 한국 고유의 글자이자 문자.""",
        )
        self.assertEqual(
            data[0]["etymology_texts"],
            [
                "1) '크다'라는 뜻의 '한'에 '글'을 붙여 만듦.",
                "2) 한국의 민족 또는 국가를 일컫는 '한'(韓)에 '글'(㐎)을 붙여 만듦.",
            ],
        )

    def test_no_list(self):
        data = parse_page(
            self.wxr,
            "애기",
            """== 한국어 ==
===어원 1===
[[아기]]의 이 모음 역행 동화
=== 명사 ===
# '[[아기]]'의 비규범 표기.""",
        )
        self.assertEqual(
            data[0]["etymology_texts"], ["아기의 이 모음 역행 동화"]
        )

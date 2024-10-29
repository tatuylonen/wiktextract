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

    def test_not_include_subsection_lists(self):
        data = parse_page(
            self.wxr,
            "병신",
            """== 한국어 ==
=== 어원 1 ===
* 욕설로 사용되는 용례는 1950년대부터 확인됨.
==== 명사 ====
# 다쳐서 몸이 온전하지 못하거나 혹은 태어나면서부터 기형의 몸을 가진 사람.

=== 어원 2 ===
* <span class="etyl">[[w:한문|한문]][[Category:한국어 terms borrowed from 한문|없다]]</span> <i class="Hant mention" lang="xzh">[[丙申|丙申]]</i>.
==== 명사 ====
# 육십 간지 가운데 하나.""",
        )
        self.assertEqual(
            data[0]["etymology_texts"],
            ["욕설로 사용되는 용례는 1950년대부터 확인됨."],
        )
        self.assertEqual(data[1]["etymology_texts"], ["한문 丙申."])
        self.assertEqual(
            data[1]["categories"], ["한국어 terms borrowed from 한문"]
        )

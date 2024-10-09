from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ko.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKoGloss(TestCase):
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

    def test_ignore_gloss_index_bold_node(self):
        data = parse_page(
            self.wxr,
            "我們",
            """== 중국어 ==
=== 대명사 ===
* '''1.''' [[우리]].""",
        )
        self.assertEqual(data[0]["senses"], [{"glosses": ["우리."]}])

    def test_no_pos_section(self):
        data = parse_page(
            self.wxr,
            "大家",
            """== 한국어 ==
* '''1.''' 모든""",
        )
        self.assertEqual(data[0]["senses"], [{"glosses": ["모든"]}])

    def test_level_4_pos(self):
        data = parse_page(
            self.wxr,
            "개",
            """== 한국어 ==
=== 명사 ===
==== 명사 1 ====
# 가축으로 많이 기르는 갯과 포유류 동물.
==== 명사 2 ====
* 어원: < [[중세국어|중세 한국어]] 개〮 [H] (분류두공부시언해 초간본(1481)).
# 강이나 내에 바닷물이 드나드는 곳.""",
        )
        self.assertEqual(data[0]["pos"], "noun")
        self.assertEqual(
            data[0]["senses"],
            [{"glosses": ["가축으로 많이 기르는 갯과 포유류 동물."]}],
        )
        self.assertEqual(data[1]["pos"], "noun")
        self.assertEqual(
            data[1]["senses"],
            [{"glosses": ["강이나 내에 바닷물이 드나드는 곳."]}],
        )
        self.assertEqual(
            data[1]["etymology_text"],
            "< 중세 한국어 개〮 [H] (분류두공부시언해 초간본(1481)).",
        )

    def test_note_list(self):
        data = parse_page(
            self.wxr,
            "개",
            """== 한국어 ==
=== 종별사 ===
# 물건을 하나 하나 세는 단위.
*참고: 특정 업계에서는 '[[ea#영어|ea]]'란 표현을 쓰기도 한다.""",
        )
        self.assertEqual(
            data[0]["senses"][0]["note"],
            "특정 업계에서는 'ea'란 표현을 쓰기도 한다.",
        )

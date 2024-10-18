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
        data = parse_page(
            self.wxr,
            "보다",
            """== 한국어 ==
=== 동사 ===
* '''1-1.''' 눈으로 무엇을 알아차리다.""",
        )
        self.assertEqual(
            data[0]["senses"], [{"glosses": ["눈으로 무엇을 알아차리다."]}]
        )

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
            data[1]["etymology_texts"],
            ["< 중세 한국어 개〮 [H] (분류두공부시언해 초간본(1481))."],
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

    def test_form_of_template(self):
        self.wxr.wtp.add_page(
            "틀:ko-hanja form of",
            10,
            """<span class="form-of-definition"><i class="None mention" lang="ko">[[전화#한국어|전화]]</i> <span class="mention-gloss-paren annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">전화기로 말을 주고받는 일</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>[[Category:한국어 비표준 문자가 포함된 낱말 (링크)|電話]]의 [[한자#한국어|한자]] 형태.</span>""",
        )
        data = parse_page(
            self.wxr,
            "電話",
            """== 한국어 ==
=== 명사 ===
# {{ko-hanja form of|전화|전화기로 말을 주고받는 일}}""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "categories": ["한국어 비표준 문자가 포함된 낱말 (링크)"],
                "form_of": [{"word": "전화"}],
                "tags": ["form-of"],
                "glosses": ["전화 (“전화기로 말을 주고받는 일”)의 한자 형태."],
            },
        )

    def test_label_template(self):
        self.wxr.wtp.add_page(
            "틀:라벨",
            10,
            """<span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[부록:용어사전#잘 쓰이지 않는 표현과 그 정도|고어]][[Category:한국어 고어|열다]]<span class="ib-comma">,</span>&#32;[[부록:용어사전#자동사|자동사]][[Category:한국어 자동사|열다]]</span><span class="ib-brac">)</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "열다",
            """== 한국어 ==
=== 명사 ===
# {{라벨|ko|고어|자동사}} [[열매가 맺히다]]""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "categories": ["한국어 고어", "한국어 자동사"],
                "tags": ["archaic", "intransitive"],
                "glosses": ["열매가 맺히다"],
            },
        )

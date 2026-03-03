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

    def test_note_list_above_gloss_list(self):
        data = parse_page(
            self.wxr,
            "놓치다",
            """== 한국어 ==
=== 명사 ===
*활용: 놓치어(놓쳐), 놓치니
# 손에 잡거나 쥐고 있던 것을 잘못하여 놓아 버리다.
# 일을 하기에 적절한 때나 기회를 그냥 보내다.""",
        )
        self.assertEqual(data[0]["note"], "놓치어(놓쳐), 놓치니")

    def test_ko_verb(self):
        self.wxr.wtp.add_page(
            "틀:ko-verb",
            10,
            """<span class="headword-line"><strong class="Kore headword" lang="ko">없다</strong> (<span lang="ko-Latn" class="headword-tr manual-tr tr Latn" dir="ltr">eopda</span>) (<i>연결형</i> <b class="Kore" lang="ko">[[:없으니#한국어|없으니]]</b>, <i>명사형</i> <b class="Kore" lang="ko">[[:없음#한국어|없음]]</b>, <i>사동사</i> <b class="Kore" lang="ko">[[:없애다#한국어|없애다]]</b>)</span>[[분류:한국어 기본형|없다]]""",
        )
        data = parse_page(
            self.wxr,
            "없다",
            """== 한국어 ==
=== 형용사 ===
{{ko-verb|nm=없음|cv=없애다}}
# 대상이 실제로 존재하지 않는 상태이다.""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "eopda", "tags": ["romanization"]},
                {"form": "없으니", "tags": ["sequential"]},
                {"form": "없음", "tags": ["noun"]},
                {"form": "없애다", "tags": ["causative"]},
            ],
        )
        self.assertEqual(data[0]["categories"], ["한국어 기본형"])

    def test_nested_gloss_lists(self):
        data = parse_page(
            self.wxr,
            "병신",
            """== 한국어 ==
=== 어원 1 ===
==== 명사 ====
# 하는 짓이나 생각이 변변치 못한 사람을 낮잡아 이르는 말.
## 남에게 [[당하다|당하거나]] [[헌신하다|헌신하기만]] 하는 대상을 동정하거나, 혹은 그런 사람이 자신의 [[처지]]를 [[하소연하다|하소연할]] 때 사용하는 표현.""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": [
                        "하는 짓이나 생각이 변변치 못한 사람을 낮잡아 이르는 말."
                    ]
                },
                {
                    "glosses": [
                        "하는 짓이나 생각이 변변치 못한 사람을 낮잡아 이르는 말.",
                        "남에게 당하거나 헌신하기만 하는 대상을 동정하거나, 혹은 그런 사람이 자신의 처지를 하소연할 때 사용하는 표현.",
                    ]
                },
            ],
        )

    def test_pattern_list(self):
        data = parse_page(
            self.wxr,
            "대하다",
            """== 한국어 ==
=== 동사 ===
==== 동사 2 ====
*문형: […을] [(…과) …을]
# 마주 향하여 있다.
*문형: […에/에게 -게] […을 …으로] […을 -게]
# 어떤 태도로 상대하다.""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["마주 향하여 있다."],
                    "pattern": "[…을] [(…과) …을]",
                },
                {
                    "glosses": ["어떤 태도로 상대하다."],
                    "pattern": "[…에/에게 -게] […을 …으로] […을 -게]",
                },
            ],
        )

    def test_ja_verb(self):
        self.wxr.wtp.add_page(
            "틀:ja-verb",
            10,
            """<span class="headword-line"><strong class="Jpan headword" lang="ja"><ruby>電<rp>(</rp><rt>[[:でんわ#일본어|でん]]</rt><rp>)</rp></ruby><ruby>話<rp>(</rp><rt>[[:でんわ#일본어|わ]]</rt><rp>)</rp></ruby>[[:する#일본어|する]]</strong> (<span class="headword-tr tr" dir="ltr"><span class="Latn" lang="ja">[[:den'wa#일본어|den'wa]] [[:suru#일본어|suru]]</span></span>)&nbsp;<i><abbr title="サ행 변격 (3류) 동사">サ행 변격</abbr></i> (<i>연용형</i> <b class="Jpan" lang="ja"><span style="font-size: 120%;"><ruby>電<rp>(</rp><rt>でん</rt><rp>)</rp></ruby><ruby>話<rp>(</rp><rt>わ</rt><rp>)</rp></ruby>[[:し#일본어|し]]</span></b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">den'wa [[shi#일본어|shi]]</span><span class="mention-gloss-paren annotation-paren">)</span>, <i>과거형</i> <b class="Jpan" lang="ja"><span style="font-size: 120%;"><ruby>電<rp>(</rp><rt>でん</rt><rp>)</rp></ruby><ruby>話<rp>(</rp><rt>わ</rt><rp>)</rp></ruby>[[:した#일본어|した]]</span></b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">den'wa [[shita#일본어|shita]]</span><span class="mention-gloss-paren annotation-paren">)</span>)</span>[[분류:일본어 기본형|てんわ']]""",
        )
        data = parse_page(
            self.wxr,
            "電話",
            """== 일본어 ==
=== 동사 ===
{{ja-verb|type=suru|でんわ}}
# [[전화하다]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "電話する",
                    "ruby": [("電", "でん"), ("話", "わ")],
                    "tags": ["canonical"],
                },
                {"form": "den'wa suru", "tags": ["romanization"]},
                {
                    "form": "電話し",
                    "roman": "den'wa shi",
                    "ruby": [("電", "でん"), ("話", "わ")],
                    "tags": ["stem"],
                },
                {
                    "form": "電話した",
                    "roman": "den'wa shita",
                    "ruby": [("電", "でん"), ("話", "わ")],
                    "tags": ["past"],
                },
            ],
        )
        self.assertEqual(data[0]["tags"], ["suru"])
        self.assertEqual(data[0]["categories"], ["일본어 기본형"])

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="th"),
            WiktionaryConfig(
                dump_file_lang_code="th", capture_language_codes=None
            ),
        )

    def test_nested_list(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:trans-top",
            10,
            """<div><div>ชื่อสัตว์สะเทินน้ำสะเทินบกชนิดหนึ่ง</div><div class="NavContent"><table class="translations" role="presentation" data-gloss="ชื่อสัตว์สะเทินน้ำสะเทินบกชนิดหนึ่ง"><tr><td class="translations-cell multicolumn-list" colspan="3">[[Category:รายการที่มีกล่องคำแปล|กบ]]""",
        )
        self.wxr.wtp.add_page(
            "แม่แบบ:t+",
            10,
            """<span class="Hani" lang="cmn">[[蛙#ภาษาจีนกลาง|蛙]]</span><span class="tpos">&nbsp;[[:zh&#x3A;蛙|(zh)]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="cmn-Latn" class="tr Latn">wā</span><span class="mention-gloss-paren annotation-paren">)</span>[[Category:หน้าที่มีคำแปลภาษาจีนกลาง|กบ]]""",
        )
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาไทย ==
=== รากศัพท์ 2 ===
==== คำนาม ====
# [[ชื่อ]]
===== คำแปลภาษาอื่น =====
{{trans-top|ชื่อสัตว์สะเทินน้ำสะเทินบกชนิดหนึ่ง}}
* จีน:
*: จีนกลาง: {{t+|cmn|蛙|tr=wā}}
{{trans-bottom}} """,
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "word": "蛙",
                    "lang": "จีนกลาง",
                    "lang_code": "cmn",
                    "roman": "wā",
                    "sense": "ชื่อสัตว์สะเทินน้ำสะเทินบกชนิดหนึ่ง",
                }
            ],
        )
        self.assertEqual(
            page_data[0]["categories"],
            ["รายการที่มีกล่องคำแปล", "หน้าที่มีคำแปลภาษาจีนกลาง"],
        )

    def test_t_tag(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:t+",
            10,
            """<span class="Latn" lang="gl">[[ra#ภาษากาลิเซีย|ra]]</span><span class="tpos">&nbsp;[[:gl&#x3A;ra|(gl)]]</span>&nbsp;<span class="gender"><abbr title="เพศหญิง">ญ.</abbr></span>[[Category:หน้าที่มีคำแปลภาษากาลิเซีย|กบ]]""",
        )
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาไทย ==
=== รากศัพท์ 2 ===
==== คำนาม ====
# [[ชื่อ]]
===== คำแปลภาษาอื่น =====
{{trans-top}}
* กาลิเซีย: {{t+|gl|ra|f}}
{{trans-bottom}} """,
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "word": "ra",
                    "lang": "กาลิเซีย",
                    "lang_code": "gl",
                    "tags": ["feminine"],
                }
            ],
        )

    def test_no_template(self):
        page_data = parse_page(
            self.wxr,
            "เกาหลี",
            """== ภาษาไทย ==
=== คำวิสามานยนาม ===
# ชื่อ
==== คำแปลภาษาอื่น ====
* [[อินเทอร์ลิงกวา]] : [[Corea]]""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "word": "Corea",
                    "lang": "อินเทอร์ลิงกวา",
                    "lang_code": "unknown",
                }
            ],
            )

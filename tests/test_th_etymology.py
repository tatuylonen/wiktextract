import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThEtymology(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="th"),
            WiktionaryConfig(
                dump_file_lang_code="th", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_level3_section(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:alt",
            10,
            """(''เลิกใช้'') <span class="Thai" lang="th">[[ไท#ภาษาไทย|ไท]]</span>, <span class="Thai" lang="th">[[ไทย์#ภาษาไทย|ไทย์]]</span>""",
        )
        data = parse_page(
            self.wxr,
            "ไทย",
            """== ภาษาไทย ==
=== รากศัพท์ 1 ===
แผลงมาจาก
==== รูปแบบอื่น ====
* {{alt|th|ไท|ไทย์||เลิกใช้}}
==== คำวิสามานยนาม ====
# [[ชื่อ]]

=== รากศัพท์ 2 ===
ยืมมาจากบาลี เทยฺย
==== คำคุณศัพท์ ====
[[ควร]][[ให]]""",
        )
        self.assertEqual(data[0]["etymology_text"], "แผลงมาจาก")
        self.assertEqual(data[1]["etymology_text"], "ยืมมาจากบาลี เทยฺย")
        self.assertTrue(len(data[0]["forms"]) > 0)
        self.assertTrue("forms" not in data[1])

    def test_ja_see_in_etymology_section(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ja-see",
            10,
            """{| class="wikitable ja-see" style="min-width:70%"
|-
| <b>สำหรับการออกเสียงและความหมายของ <span lang="ja" class="Jpan">コメ</span> – ดูที่รายการต่อไปนี้ </b>: <span style="font-size:120%"><span lang="ja" class="Jpan">[[米#ภาษาญี่ปุ่น|米]]</span></span>
|}
<small class="attentionseeking">(รายการต่อไปนี้ยังไม่ได้สร้างขึ้น: <span lang="ja" class="Jpan">[[米#ภาษาญี่ปุ่น|米]]</span>)</small>[[Category:ภาษาญี่ปุ่น redlinks/ja-see|こめ]][[Category:หน้าที่มีรายการ|コメ]][[Category:หน้าที่มี 1 รายการ|コメ]]""",
        )
        data = parse_page(
            self.wxr,
            "コメ",
            """== ภาษาญี่ปุ่น ==
=== รากศัพท์ 1 ===
{{ja-see|米}}

=== รากศัพท์ 2 ===
==== คำนาม ====
# gloss""",
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["redirects"], ["米"])
        self.assertEqual(
            data[0]["categories"],
            ["ภาษาญี่ปุ่น redlinks/ja-see", "หน้าที่มีรายการ", "หน้าที่มี 1 รายการ"],
        )
        self.assertTrue("etymology_text" not in data[0])
        self.assertTrue("redirects" not in data[1])
        self.assertTrue("categories" not in data[1])

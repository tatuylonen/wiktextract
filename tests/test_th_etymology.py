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

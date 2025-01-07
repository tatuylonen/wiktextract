from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="th"),
            WiktionaryConfig(
                dump_file_lang_code="th", capture_language_codes=None
            ),
        )

    def test_do_not_share_etymology_data(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:inh+",
            10,
            """สืบทอดจาก<span class="etyl">[[w:ภาษาไทดั้งเดิม|ไทดั้งเดิม]][[Category:ศัพท์ภาษาไทยที่สืบทอดจากภาษาไทดั้งเดิม|กบ]][[Category:ศัพท์ภาษาไทยที่รับมาจากภาษาไทดั้งเดิม|กบ]]</span> <i class="Latn mention" lang="tai-pro">[[การสืบสร้าง&#x3A;ไทดั้งเดิม&#x2F;kɤpᴰ|&#x2A;kɤpᴰ]]</i>""",
        )
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาไทย ==
=== รากศัพท์ 2 ===
{{inh+|th|tai-pro|*kɤpᴰ}}

==== คำนาม ====
{{th-noun|ตัว}}

# [[ชื่อ]]

=== รากศัพท์ 3 ===

==== คำนาม ====
{{th-noun|ตัว}}

# [[ปลา]]""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "categories": [
                        "ศัพท์ภาษาไทยที่สืบทอดจากภาษาไทดั้งเดิม",
                        "ศัพท์ภาษาไทยที่รับมาจากภาษาไทดั้งเดิม",
                    ],
                    "etymology_text": "สืบทอดจากไทดั้งเดิม *kɤpᴰ",
                    "senses": [{"glosses": ["ชื่อ"]}],
                    "pos": "noun",
                    "pos_title": "คำนาม",
                    "word": "กบ",
                    "lang": "ไทย",
                    "lang_code": "th",
                },
                {
                    "senses": [{"glosses": ["ปลา"]}],
                    "pos": "noun",
                    "pos_title": "คำนาม",
                    "word": "กบ",
                    "lang": "ไทย",
                    "lang_code": "th",
                },
            ],
        )

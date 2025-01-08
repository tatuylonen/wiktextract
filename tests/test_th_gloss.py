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

    def test_label_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:lb",
            10,
            """<span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[Appendix:Glossary#ไม่ทางการ|ไม่ทางการ]][[Category:ศัพท์ภาษาญี่ปุ่นที่ไม่เป็นทางการ|にいはお]][[Category:ญี่ปุ่น terms with non-redundant non-automated sortkeys|にいはお]]<span class="ib-comma">,</span>&#32;พบได้ยาก[[Category:ศัพท์ภาษาญี่ปุ่นที่มีนัยพบได้ยาก|にいはお]][[Category:ญี่ปุ่น terms with non-redundant non-automated sortkeys|にいはお]]</span><span class="ib-brac">)</span></span> """,
        )
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาญี่ปุ่น ==
=== คำอุทาน ===
# {{lb|ja|ไม่ทางการ|พบยาก|sort=にいはお}} [[สวัสดี]]""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": [
                    "ศัพท์ภาษาญี่ปุ่นที่ไม่เป็นทางการ",
                    "ญี่ปุ่น terms with non-redundant non-automated sortkeys",
                    "ศัพท์ภาษาญี่ปุ่นที่มีนัยพบได้ยาก",
                ],
                "raw_tags": ["ไม่ทางการ", "พบได้ยาก"],
                "glosses": ["สวัสดี"],
            },
        )

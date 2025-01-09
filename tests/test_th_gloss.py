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
        self.wxr.wtp.add_page(
            "แม่แบบ:th-noun",
            10,
            """<span class="headword-line"><strong class="Thai headword" lang="th">กบ</strong> (<i>คำลักษณนาม</i> <b class="Thai" lang="th">[[ตัว#ภาษาไทย|ตัว]]</b>)</span>[[Category:คำหลักภาษาไทย|กบ]]""",
        )
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาไทย ==
=== รากศัพท์ 2 ===
{{inh+|th|tai-pro|*kɤpᴰ}}

==== คำนาม ====

# [[ชื่อ]]

=== รากศัพท์ 3 ===

==== คำนาม ====
{{th-noun|ตัว}}

# [[ปลา]][[คางคก]]""",
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
                    "categories": ["คำหลักภาษาไทย"],
                    "senses": [{"glosses": ["ปลาคางคก"]}],
                    "pos": "noun",
                    "pos_title": "คำนาม",
                    "word": "กบ",
                    "lang": "ไทย",
                    "lang_code": "th",
                    "classifiers": ["ตัว"],
                },
            ],
        )

    def test_label_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:lb",
            10,
            """<span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[Appendix:Glossary#ไม่ทางการ|ไม่ทางการ]][[Category:ศัพท์ภาษาญี่ปุ่นที่ไม่เป็นทางการ|にいはお]][[Category:ญี่ปุ่น terms with non-redundant non-automated sortkeys|にいはお]]<span class="ib-comma">,</span>&#32;พบได้ยาก[[Category:ศัพท์ภาษาญี่ปุ่นที่มีนัยพบได้ยาก|にいはお]][[Category:ญี่ปุ่น terms with non-redundant non-automated sortkeys|にいはお]]</span><span class="ib-brac">)</span></span>""",
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

    def test_cls_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:cls",
            10,
            """<span><span>(''คำลักษณนาม'': '''<span class="Thai" lang="th">[[ตัว#ภาษาไทย|ตัว]]</span>'''[[หมวดหมู่:คำนามภาษาไทยที่ใช้คำลักษณนาม ตัว]]&nbsp;''หรือ''&nbsp;'''<span class="Thai" lang="th">[[อัน#ภาษาไทย|อัน]]</span>'''[[หมวดหมู่:คำนามภาษาไทยที่ใช้คำลักษณนาม อัน]])</span></span>""",
        )
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาญี่ปุ่น ==
=== รากศัพท์ 4 ===
==== คำนาม ====
# [[อุปกรณ์]][[ใช้]][[เหลา]][[ดินสอ]] {{cls|th|ตัว|อัน}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": [
                    "คำนามภาษาไทยที่ใช้คำลักษณนาม ตัว",
                    "คำนามภาษาไทยที่ใช้คำลักษณนาม อัน",
                ],
                "classifiers": ["ตัว", "อัน"],
                "glosses": ["อุปกรณ์ใช้เหลาดินสอ"],
            },
        )

    def test_th_noun(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:th-noun",
            10,
            """<span class="headword-line"><strong class="Thai headword" lang="th">กิ๊ก</strong> (<i>คำลักษณนาม</i> <b class="Thai" lang="th">[[กิ๊ก#ภาษาไทย|กิ๊ก]]</b>)</span>[[Category:คำหลักภาษาไทย|กิ๊ก]]""",
        )
        page_data = parse_page(
            self.wxr,
            "กิ๊ก",
            """== ภาษาไทย ==
=== รากศัพท์ 3 ===
==== คำนาม ====
{{th-noun|*}}

# [[กิกะไบต์]], [[จิกะไบต์]]""",
        )
        self.assertEqual(
            page_data[0],
            {
                "categories": ["คำหลักภาษาไทย"],
                "classifiers": ["กิ๊ก"],
                "senses": [{"glosses": ["กิกะไบต์, จิกะไบต์"]}],
                "word": "กิ๊ก",
                "pos": "noun",
                "pos_title": "คำนาม",
                "lang": "ไทย",
                "lang_code": "th",
            },
        )

    def test_th_verb(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:th-verb",
            10,
            """<span class="headword-line"><strong class="Thai headword" lang="th">กลัว</strong> (<i>คำอาการนาม</i> <b class="Thai form-of lang-th abstract-noun-form-of pos-คำนาม" lang="th">[[การกลัว#ภาษาไทย|การกลัว]]</b> <i>หรือ</i> <b class="Thai form-of lang-th abstract-noun-form-of pos-คำนาม" lang="th">[[ความกลัว#ภาษาไทย|ความกลัว]]</b>)</span>[[Category:คำหลักภาษาไทย|กลัว]]""",
        )
        page_data = parse_page(
            self.wxr,
            "กลัว",
            """== ภาษาไทย ==
=== คำกริยา ===
{{th-verb|~}}

# [[รู้สึก]][[ไม่]][[อยาก]][[ประสบ]][[สิ่ง]][[ที่]]ไม่[[ดี]][[แก่]][[ตัว]]""",
        )
        self.assertEqual(
            page_data[0],
            {
                "categories": ["คำหลักภาษาไทย"],
                "forms": [
                    {"form": "การกลัว", "tags": ["abstract-noun"]},
                    {"form": "ความกลัว", "tags": ["abstract-noun"]},
                ],
                "senses": [{"glosses": ["รู้สึกไม่อยากประสบสิ่งที่ไม่ดีแก่ตัว"]}],
                "word": "กลัว",
                "pos": "verb",
                "pos_title": "คำกริยา",
                "lang": "ไทย",
                "lang_code": "th",
            },
        )

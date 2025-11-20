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

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

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
                    "classifiers": [{"classifier": "ตัว"}],
                },
            ],
        )

    def test_label_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:lb",
            10,
            """<span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[Appendix:Glossary#ภาษาปาก|ภาษาปาก]][[Category:ศัพท์ภาษาไทยที่เป็นภาษาปาก|ไข่]]<span class="ib-comma">,</span>&#32;[[Appendix:Glossary#สแลง|สแลง]][[Category:สแลงภาษาไทย|ไข่]]</span><span class="ib-brac">)</span></span>""",
        )
        page_data = parse_page(
            self.wxr,
            "ไข่",
            """== ภาษาญี่ปุ่น ==
=== คำกริยา ===
# {{lb|th|ปาก|สแลง}} ทำให้[[ผู้หญิง]][[ท้อง]]แล้วมักไม่รับผิดชอบ""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": ["ศัพท์ภาษาไทยที่เป็นภาษาปาก", "สแลงภาษาไทย"],
                "tags": ["colloquial", "slang"],
                "glosses": ["ทำให้ผู้หญิงท้องแล้วมักไม่รับผิดชอบ"],
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
                "classifiers": [{"classifier": "ตัว"}, {"classifier": "อัน"}],
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
                "classifiers": [{"classifier": "กิ๊ก"}],
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

    def test_alt_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:alt",
            10,
            """(''เลิกใช้'') <span class="Thai" lang="th">[[เดอร#ภาษาไทย|เดอร]]</span>, <span class="Thai" lang="th">[[เดิร#ภาษาไทย|เดิร]]</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "เดิน",
            """== ภาษาไทย ==
=== รูปแบบอื่น ===
* {{alt|th|เดอร|เดิร||เลิกใช้}}
=== คำกริยา ===
# [[ยก]][[เท้า]][[ก้าว]][[ไป]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "เดอร", "tags": ["obsolete"]},
                {"form": "เดิร", "tags": ["obsolete"]},
            ],
        )

    def test_lo_alt(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:lo-alt",
            10,
            """* (''ล้าสมัย'') <span class="Laoo" lang="lo">[[ທຸຣຽນ#ภาษาลาว|ທຸຣຽນ]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="lo-Latn" class="tr Latn">ทุรย̂น</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "ທຸລຽນ",
            """== ภาษาลาว ==
=== รูปแบบอื่น ===
{{lo-alt|d=ທຸຣຽນ}}
=== คำนาม ===
{{lo-noun}}
# [[ทุเรียน]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "ທຸຣຽນ", "tags": ["dated"], "roman": "ทุรย̂น"},
            ],
        )

    def test_alt_form_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:altform",
            10,
            """<span class='form-of-definition use-with-mention'>อีกรูปหนึ่งของ <span class='form-of-definition-link'><i class="Lana mention" lang="nod">[[ᨸᩣ᩠ᨠ#ภาษาคำเมือง|ᨸᩣ᩠ᨠ]]</i> <span class="mention-gloss-paren annotation-paren">(</span><span lang="nod-Latn" class="mention-tr tr Latn">ปาก</span><span class="mention-gloss-paren annotation-paren">)</span></span></span>""",
        )
        page_data = parse_page(
            self.wxr,
            "ปาก",
            """== ภาษาคำเมือง ==
=== คำนาม ===
{{nod-noun}}

# {{altform|nod|ᨸᩣ᩠ᨠ}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "glosses": ["อีกรูปหนึ่งของ ᨸᩣ᩠ᨠ (ปาก)"],
                "alt_of": [{"word": "ᨸᩣ᩠ᨠ", "roman": "ปาก"}],
                "tags": ["alt-of"],
            },
        )

    def test_alt_form_second_language_section(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:alt",
            10,
            """(''เลิกใช้'') <span class="Thai" lang="th">[[เดอร#ภาษาไทย|เดอร]]</span>, <span class="Thai" lang="th">[[เดิร#ภาษาไทย|เดิร]]</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "ข้าว",
            """== ภาษาไทย ==
=== คำกริยา ===
# [[ชื่อ]]

== ภาษาญ้อ ==
=== รูปแบบอื่น ===
* {{l|nyw|เข้า}}
=== คำนาม ===
# [[ข้าว]]""",
        )
        self.assertTrue("forms" not in page_data[0])
        self.assertEqual(page_data[1]["forms"], [{"form": "เข้า"}])

    def test_alt_form_after_pos(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:lo-alt",
            10,
            """* (''ล้าสมัย'') <span class="Laoo" lang="lo">[[ໄທຍ໌#ภาษาลาว|ໄທຍ໌]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="lo-Latn" class="tr Latn">ไทย์</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "ໄທ",
            """== ภาษาลาว ==
=== คำนาม ===
# [[ไทย]]

=== คำวิสามานยนาม ===
# [[ไทย]]
==== รูปแบบอื่น ====
{{lo-alt|d=ໄທຍ}}""",
        )
        self.assertTrue("forms" not in page_data[0])
        self.assertEqual(
            page_data[1]["forms"],
            [{"form": "ໄທຍ໌", "tags": ["dated"], "roman": "ไทย์"}],
        )

    def test_inflection_of(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:inflection of",
            10,
            """<span>การผันรูปของ <span><i>[[achten#ภาษาเยอรมัน|achten]]</i></span>:</span>
## <span>[[ภาคผนวก:อภิธานศัพท์#บุรุษที่หนึ่ง|บุรุษที่หนึ่ง]] [[ภาคผนวก:อภิธานศัพท์#เอกพจน์|เอกพจน์]] [[ภาคผนวก:อภิธานศัพท์#ปัจจุบันกาล|ปัจจุบันกาล]]</span>
## <span><span>[[ภาคผนวก:อภิธานศัพท์#บุรุษที่หนึ่ง|บุรุษที่หนึ่ง]]<span>/</span>[[ภาคผนวก:อภิธานศัพท์#บุรุษที่สาม|บุรุษที่สาม]]</span> [[ภาคผนวก:อภิธานศัพท์#เอกพจน์|เอกพจน์]] [[ภาคผนวก:อภิธานศัพท์#มาลาสมมุติ|มาลาสมมุติ]] I</span>
## <span>[[ภาคผนวก:อภิธานศัพท์#เอกพจน์|เอกพจน์]] [[ภาคผนวก:อภิธานศัพท์#มาลาสั่ง|มาลาสั่ง]]</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "achte",
            """== ภาษาเยอรมัน ==
=== คำกริยา ===
# {{inflection of|de|achten||1|s|pres|;|1//3|s|sub|I|;|s|imp}}
""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["การผันรูปของ achten:"],
                    "form_of": [{"word": "achten"}],
                    "tags": ["form-of"],
                },
                {
                    "glosses": [
                        "การผันรูปของ achten:",
                        "บุรุษที่หนึ่ง เอกพจน์ ปัจจุบันกาล",
                    ],
                    "form_of": [{"word": "achten"}],
                    "tags": ["form-of"],
                },
                {
                    "glosses": [
                        "การผันรูปของ achten:",
                        "บุรุษที่หนึ่ง/บุรุษที่สาม เอกพจน์ มาลาสมมุติ I",
                    ],
                    "form_of": [{"word": "achten"}],
                    "tags": ["form-of"],
                },
                {
                    "glosses": ["การผันรูปของ achten:", "เอกพจน์ มาลาสั่ง"],
                    "form_of": [{"word": "achten"}],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_nested_gloss_lists(self):
        page_data = parse_page(
            self.wxr,
            "-",
            """== ภาษาร่วม ==
=== สัญลักษณ์ ===
# [[ขีด]]ที่อยู่กึ่งกลาง ซึ่งสามารถใช้แทนได้หลายเครื่องหมายดังนี้
## [[ยัติภังค์]]""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {"glosses": ["ขีดที่อยู่กึ่งกลาง ซึ่งสามารถใช้แทนได้หลายเครื่องหมายดังนี้"]},
                {
                    "glosses": [
                        "ขีดที่อยู่กึ่งกลาง ซึ่งสามารถใช้แทนได้หลายเครื่องหมายดังนี้",
                        "ยัติภังค์",
                    ]
                },
            ],
        )

    def test_roman_section_not_pos(self):
        page_data = parse_page(
            self.wxr,
            "ข้าวหน้าเป็ด",
            """== ภาษาไทย ==
=== การถอดเป็นอักษรโรมัน ===
* {{RTGS|khao na pet}}
=== คำนาม ===
# ข้าวสุกมีเป็ดย่างสับเป็นชิ้นวางข้างบน ราดด้วยน้ำเป็ดย่าง""",
        )
        self.assertEqual(len(page_data), 1)
        self.assertEqual(
            page_data[0]["forms"],
            [{"form": "khao na pet", "tags": ["romanization", "RTGS"]}],
        )

    def test_lb_or(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:lb",
            10,
            """<span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[Appendix:Glossary#ภาษาหนังสือ|ภาษาหนังสือ]]&#32;หรือ&#32;[[Appendix:Glossary#ภาษาถิ่น|ภาษาถิ่น]]</span><span class="ib-brac">)</span></span>""",
        )
        page_data = parse_page(
            self.wxr,
            "日頭",
            """== ภาษาจีน ==
=== คำนาม ===
# {{lb|zh|literary|or|dialectal}} [[ดวงอาทิตย์]]""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [{"glosses": ["ดวงอาทิตย์"], "tags": ["literary", "dialect"]}],
        )

    def test_ru_noun_plus(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ru-noun+",
            10,
            """<span class="headword-line"><strong class="Cyrl headword" lang="ru">абза́ц</strong> (<span lang="ru" class="headword-tr tr" dir="ltr">อับซฺัต͜ซ</span>)&nbsp;<span class="gender"><abbr title="เพศชาย">ช.</abbr>&nbsp;<abbr title="ไม่มีชีวิต">อชีว.</abbr></span> (<i>สัมพันธการก</i> <b class="Cyrl" lang="ru">[[:абзаца#ภาษารัสเซีย|абза́ца]]</b>[[Category:รัสเซีย links with redundant wikilinks|АБЗАЦ]][[Category:รัสเซีย links with redundant alt parameters|АБЗАЦ]], <i>กรรตุการกพหูพจน์</i> <b class="Cyrl" lang="ru">[[:абзацы#ภาษารัสเซีย|абза́цы]]</b>[[Category:รัสเซีย links with redundant wikilinks|АБЗАЦ]][[Category:รัสเซีย links with redundant alt parameters|АБЗАЦ]], <i>สัมพันธการกพหูพจน์</i> <b class="Cyrl" lang="ru">[[:абзацев#ภาษารัสเซีย|абза́цев]]</b>[[Category:รัสเซีย links with redundant wikilinks|АБЗАЦ]][[Category:รัสเซีย links with redundant alt parameters|АБЗАЦ]])</span>[[Category:คำหลักภาษารัสเซีย|АБЗАЦ]][[Category:คำนามภาษารัสเซีย|АБЗАЦ]][[Category:รัสเซีย entries with incorrect language header|АБЗАЦ]][[Category:หน้าที่มีรายการ|АБЗАЦ]][[Category:หน้าที่มี 1 รายการ|АБЗАЦ]]""",
        )
        page_data = parse_page(
            self.wxr,
            "абзац",
            """== ภาษารัสเซีย ==
=== คำนาม ===
{{ru-noun+|абза́ц}}
# [[ย่อหน้า]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "абза́ц", "tags": ["canonical"]},
                {"form": "อับซฺัต͜ซ", "tags": ["romanization"]},
                {"form": "абза́ца", "tags": ["genitive"]},
                {"form": "абза́цы", "tags": ["nominative", "plural"]},
                {"form": "абза́цев", "tags": ["genitive", "plural"]},
            ],
        )
        self.assertEqual(page_data[0]["tags"], ["masculine", "inanimate"])
        self.assertEqual(
            page_data[0]["categories"],
            [
                "รัสเซีย links with redundant wikilinks",
                "รัสเซีย links with redundant alt parameters",
                "คำหลักภาษารัสเซีย",
                "คำนามภาษารัสเซีย",
                "รัสเซีย entries with incorrect language header",
                "หน้าที่มีรายการ",
                "หน้าที่มี 1 รายการ",
            ],
        )

    def test_en_adv_i_tag(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:en-adv",
            10,
            """<span class="headword-line"><strong class="Latn headword" lang="en">again</strong> (<i>[[ภาคผนวก:อภิธานศัพท์#เปรียบเทียบไม่ได้|เปรียบเทียบไม่ได้]]</i>)</span>[[Category:คำหลักภาษาอังกฤษ|AGAIN]]""",
        )
        data = parse_page(
            self.wxr,
            "again",
            """== ภาษาอังกฤษ ==
=== คำกริยาวิเศษณ์ ===
{{en-adv|-}}
# [[อีก]]""",
        )
        self.assertEqual(data[0]["tags"], ["not-comparable"])
        self.assertEqual(data[0]["categories"], ["คำหลักภาษาอังกฤษ"])

    def test_ja_noun_two_headword_forms(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ja-noun",
            10,
            """<span class="headword-line"><strong class="Jpan headword" lang="ja"><ruby>日<rp>(</rp><rt>[[:にほんじん#ภาษาญี่ปุ่น|に]]</rt><rp>)</rp></ruby><ruby>本<rp>(</rp><rt>[[:にほんじん#ภาษาญี่ปุ่น|ほん]]</rt><rp>)</rp></ruby><ruby>人<rp>(</rp><rt>[[:にほんじん#ภาษาญี่ปุ่น|じん]]</rt><rp>)</rp></ruby></strong> <i>หรือ</i> <strong class="Jpan headword" lang="ja"><ruby>日本人<rp>(</rp><rt>[[:にっぽんじん#ภาษาญี่ปุ่น|にっぽんじん]]</rt><rp>)</rp></ruby></strong> (<span class="headword-tr manual-tr tr" dir="ltr"><span class="Latn" lang="ja">[[:nihonjin#ภาษาญี่ปุ่น|nihonjin]]</span>[[Category:ญี่ปุ่น links with redundant wikilinks|日本人]][[Category:ญี่ปุ่น links with redundant alt parameters|日本人]]</span> <i>หรือ</i> <span class="headword-tr manual-tr tr" dir="ltr"><span class="Latn" lang="ja">[[:nipponjin#ภาษาญี่ปุ่น|nipponjin]]</span>[[Category:ญี่ปุ่น links with redundant wikilinks|日本人]][[Category:ญี่ปุ่น links with redundant alt parameters|日本人]]</span>)&nbsp;<i></i></span>""",
        )
        data = parse_page(
            self.wxr,
            "日本人",
            """== ภาษาญี่ปุ่น ==
=== คำนาม ===
{{ja-noun|にほんじん|にっぽんじん}}
# คนญี่ปุ่น""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "日本人",
                    "ruby": [("日", "に"), ("本", "ほん"), ("人", "じん")],
                    "tags": ["canonical"],
                },
                {
                    "form": "日本人",
                    "ruby": [("日本人", "にっぽんじん")],
                    "tags": ["canonical"],
                },
                {"form": "nihonjin", "tags": ["romanization"]},
                {"form": "nipponjin", "tags": ["romanization"]},
            ],
        )

    def test_ja_adj(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ja-adj",
            10,
            """<span class="headword-line"><strong class="Jpan headword" lang="ja"><ruby>悄<rp>(</rp><rt>[[:しょうぜん#ภาษาญี่ปุ่น|しょう]]</rt><rp>)</rp></ruby><ruby>然<rp>(</rp><rt>[[:しょうぜん#ภาษาญี่ปุ่น|ぜん]]</rt><rp>)</rp></ruby></strong> (<span class="headword-tr manual-tr tr" dir="ltr"><span class="Latn" lang="ja">[[:shōzen#ภาษาญี่ปุ่น|shōzen]]</span>[[Category:ญี่ปุ่น links with redundant wikilinks|悄然]][[Category:ญี่ปุ่น links with redundant alt parameters|悄然]]</span>)&nbsp;<sup>←<strong class="Jpan headword" lang="ja">[[:せうぜん#ภาษาญี่ปุ่น|せうぜん]]</strong> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">seuzen</span></span><span class="mention-gloss-paren annotation-paren">)</span>[[Category:ญี่ปุ่น links with redundant alt parameters|悄然]]<sup>[[w:Historical kana orthography|?]]</sup></sup><i><abbr title="-tari inflection (classical)"><sup><small>†</small></sup>-ตาริ</abbr></i> (<i>adnominal</i> <b class="Jpan" lang="ja"><ruby>悄<rp>(</rp><rt>しょう</rt><rp>)</rp></ruby><ruby>然<rp>(</rp><rt>ぜん</rt><rp>)</rp></ruby>[[:とした#ภาษาญี่ปุ่น|とした]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">shōzen [[to shita]]</span><span class="mention-gloss-paren annotation-paren">)</span> <i>หรือ</i> <b class="Jpan" lang="ja"><ruby>悄<rp>(</rp><rt>しょう</rt><rp>)</rp></ruby><ruby>然<rp>(</rp><rt>ぜん</rt><rp>)</rp></ruby>[[:たる#ภาษาญี่ปุ่น|たる]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">shōzen [[taru]]</span><span class="mention-gloss-paren annotation-paren">)</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "悄然",
            """== ภาษาญี่ปุ่น ==
=== คำคุณศัพท์ ===
{{ja-adj|しょうぜん|infl=tari|hhira=せうぜん}}
# สลดใจ""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "悄然",
                    "ruby": [("悄", "しょう"), ("然", "ぜん")],
                    "tags": ["canonical"],
                },
                {"form": "shōzen", "tags": ["romanization"]},
                {"form": "せうぜん", "roman": "seuzen", "tags": ["archaic"]},
                {
                    "form": "悄然とした",
                    "tags": ["adnominal"],
                    "roman": "shōzen to shita",
                    "ruby": [("悄", "しょう"), ("然", "ぜん")],
                },
                {
                    "form": "悄然たる",
                    "tags": ["adnominal"],
                    "roman": "shōzen taru",
                    "ruby": [("悄", "しょう"), ("然", "ぜん")],
                },
            ],
        )
        self.assertEqual(data[0]["tags"], ["-tari"])

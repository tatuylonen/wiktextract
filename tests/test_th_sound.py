import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThSound(unittest.TestCase):
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

    def test_th_pron(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:th-pron",
            10,
            """<table>
<tr><th colspan="2">''[[w:อักษรไทย|การแบ่งพยางค์]]''</th><td><span lang="th" class="Thai th-reading">รด</span></td><td><span><small>[เสียงสมาส]</small></span><br><span lang="th" class="Thai th-reading">ระ-ถะ-</span></td></tr>
<tr><th rowspan="2">''[[วิกิพจนานุกรม:การแผลงเป็นอักษรโรมันของภาษาไทย|การแผลงเป็น<br>อักษรโรมัน]]''</th><th colspan="1">''[[วิกิพจนานุกรม:การแผลงเป็นอักษรโรมันของภาษาไทย|ไพบูลย์พับบลิชชิง]]''</th><td><span class="tr">rót</span></td></tr><tr><th colspan="1">''[[วิกิพจนานุกรม:การแผลงเป็นอักษรโรมันของภาษาไทย|ราชบัณฑิตยสภา]]''</th><td><span class="tr">rot</span></td></tr>
<tr><th colspan="2">(''[[w:ภาษาไทย|มาตรฐาน]]'') [[วิกิพจนานุกรม:สัทอักษรสากล|สัทอักษรสากล]]<sup>([[ภาคผนวก:การออกเสียงภาษาไทย|คำอธิบาย]])</sup></th><td><span class="IPA">/rot̚˦˥/</span><sup>([[:หมวดหมู่:สัมผัส:ภาษาไทย/ot̚|สัมผัส]])</sup>[[หมวดหมู่:สัมผัส:ภาษาไทย/ot̚]]</td></tr>
<tr><th colspan="2">''คำพ้องเสียง''<div><span class="plainlinks"></span></div></th><td><div><span>&nbsp;</span><div></div><div><span class="Thai" lang="th">[[รด#ภาษาไทย|รด]]</span><br><span class="Thai" lang="th">[[รท#ภาษาไทย|รท]]</span><br><span class="Thai" lang="th">[[รส#ภาษาไทย|รส]]</span>[[Category:ศัพท์ภาษาไทยที่มีคำพ้องเสียง|รถ]]</div></div></td><td></td></tr>
</table>[[หมวดหมู่:ศัพท์ภาษาไทยที่มีการออกเสียงไอพีเอ]][[หมวดหมู่:ศัพท์ภาษาไทยที่มี 1 พยางค์]]""",
        )
        data = parse_page(
            self.wxr,
            "รถ",
            """== ภาษาไทย ==
=== การออกเสียง ===
{{th-pron|รด|ระ-ถะ-}}
=== คำนาม ===
# [[ยาน]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {"other": "รด", "tags": ["phoneme"]},
                {"other": "ระ-ถะ-", "tags": ["compound", "phoneme"]},
                {
                    "roman": "rót",
                    "tags": ["romanization", "Paiboon"],
                },
                {
                    "roman": "rot",
                    "tags": ["romanization", "Royal-Institute"],
                },
                {"ipa": "/rot̚˦˥/"},
                {"homophone": "รด"},
                {"homophone": "รท"},
                {"homophone": "รส"},
            ],
        )
        self.assertEqual(
            data[0]["categories"],
            [
                "สัมผัส:ภาษาไทย/ot̚",
                "ศัพท์ภาษาไทยที่มีคำพ้องเสียง",
                "ศัพท์ภาษาไทยที่มีการออกเสียงไอพีเอ",
                "ศัพท์ภาษาไทยที่มี 1 พยางค์",
            ],
        )

    def test_lo_pron(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:lo-pron",
            10,
            """* <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content"><span class="usage-label-accent">เวียงจันทน์</span></span><span class="ib-brac qualifier-brac">)</span> [[วิกิพจนานุกรม:สัทอักษรสากล|สัทอักษรสากล]]<sup>([[wikipedia:ระบบเสียงภาษาลาว|คำอธิบาย]])</sup>:&#32;<span class="IPA">[tʰaj˧˥]</span>[[Category:ศัพท์ภาษาลาวที่มีการออกเสียงไอพีเอ|ໄທ]][[Category:ศัพท์ภาษาลาวที่มี 1 พยางค์|ໄທ]]
* <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content"><span class="usage-label-accent">หลวงพระบาง</span></span><span class="ib-brac qualifier-brac">)</span> [[วิกิพจนานุกรม:สัทอักษรสากล|สัทอักษรสากล]]<sup>([[wikipedia:ระบบเสียงภาษาลาว|คำอธิบาย]])</sup>:&#32;<span class="IPA">[tʰaj˩˨]</span>[[Category:ศัพท์ภาษาลาวที่มีการออกเสียงไอพีเอ|ໄທ]][[Category:ศัพท์ภาษาลาวที่มี 1 พยางค์|ໄທ]]
* การแบ่งพยางค์: <span class='Laoo lo-reading' lang='lo'>ໄທ</span>
* สัมผัส: [[:หมวดหมู่:สัมผัส:ภาษาลาว/aj|<span class="IPA">-aj</span>]][[Category:สัมผัส:ภาษาลาว/aj|ໄທ]]""",
        )
        data = parse_page(
            self.wxr,
            "ໄທ",
            """== ภาษาลาว ==
=== การออกเสียง ===
{{lo-pron}}
=== คำนาม ===
# [[ไทย]]""",
        )
        self.assertEqual(data[0]["hyphenations"], [{"parts": ["ໄທ"]}])
        self.assertEqual(
            data[0]["sounds"],
            [
                {"ipa": "[tʰaj˧˥]", "raw_tags": ["เวียงจันทน์"]},
                {"ipa": "[tʰaj˩˨]", "raw_tags": ["หลวงพระบาง"]},
                {"rhymes": "-aj"},
            ],
        )
        self.assertEqual(
            data[0]["categories"],
            [
                "ศัพท์ภาษาลาวที่มีการออกเสียงไอพีเอ",
                "ศัพท์ภาษาลาวที่มี 1 พยางค์",
                "สัมผัส:ภาษาลาว/aj",
            ],
        )

    def test_ja_pron(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ja-pron",
            10,
            """<ul><li><span class="usage-label-accent"><span class="ib-brac">(</span><span class="ib-content">[[w:ภาษาถิ่นโตเกียว|โตเกียว]]</span><span class="ib-brac">)</span></span> <span lang="ja" class="Jpan"><span style="border-top:1px solid black;position:relative;padding:1px;">あ<span style="position:absolute;top:0;bottom:67%;right:0%;border-right:1px solid black;">&#8203;</span></span>い<span style="border:1px dotted gray; border-radius:50%;">し</span>ている</span> <span class="Latn"><samp>[áꜜìsh<del>ì</del>tè ìrù]</samp></span> ([[頭高型|อาตามาดากะ]] – [1])</li><li>[[วิกิพจนานุกรม:สัทอักษรสากล|สัทอักษรสากล]]<sup>([[ภาคผนวก:การออกเสียงภาษาญี่ปุ่น|คำอธิบาย]])</sup>:&#32;<span class="IPA">[a̠iɕi̥te̞ iɾɯ̟ᵝ]</span>[[Category:ศัพท์ภาษาญี่ปุ่นที่มีการออกเสียงไอพีเอ|あいしている]][[Category:ญี่ปุ่น terms with non-redundant non-automated sortkeys|愛している]]</li></ul>""",
        )
        data = parse_page(
            self.wxr,
            "愛している",
            """==ภาษาญี่ปุ่น==
=== การออกเสียง ===
* {{ja-pron|あいして いる|acc=1|dev=3}}
=== วลี ===
# [[ฉันรักคุณ]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "other": "あいしている",
                    "raw_tags": ["โตเกียว"],
                    "tags": ["Atamadaka"],
                    "roman": "[áꜜìshìtè ìrù]",
                },
                {"ipa": "[a̠iɕi̥te̞ iɾɯ̟ᵝ]"},
            ],
        )
        self.assertEqual(
            data[0]["categories"],
            [
                "ศัพท์ภาษาญี่ปุ่นที่มีการออกเสียงไอพีเอ",
                "ญี่ปุ่น terms with non-redundant non-automated sortkeys",
            ],
        )

    def test_rhymes(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:rhymes",
            10,
            """สัมผัส: [[:หมวดหมู่:สัมผัส:ภาษาอังกฤษ/ɪʃɪŋ|<span class="IPA">-ɪʃɪŋ</span>]][[Category:สัมผัส:ภาษาอังกฤษ/ɪʃɪŋ|ຊ່ອງ]]""",
        )
        data = parse_page(
            self.wxr,
            "fishing",
            """==ภาษาอังกฤษ==
=== การออกเสียง ===
* {{rhymes|ɪʃɪŋ|lang=en}}
=== คำนาม ===
# การจับปลา""",
        )
        self.assertEqual(data[0]["sounds"], [{"rhymes": "-ɪʃɪŋ"}])
        self.assertEqual(data[0]["categories"], ["สัมผัส:ภาษาอังกฤษ/ɪʃɪŋ"])

    def test_homophones(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:homophones",
            10,
            """<span class="homophones">[[ภาคผนวก:อภิธานศัพท์#คำพ้องเสียง|คำพ้องเสียง]]: <span class="Laoo" lang="lo">[[:ສ່ອງ#ภาษาลาว|ສ່ອງ]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="lo" class="tr">ส่อง</span><span class="mention-gloss-paren annotation-paren">)</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">ในถิ่นที่มีการออกเสียงอักษรคู่เหมือนกันเมื่อมีไม้เอก</span><span class="ib-brac qualifier-brac">)</span></span>[[Category:ศัพท์ภาษาลาวที่มีคำพ้องเสียง|ຊ່ອງ]]""",
        )
        data = parse_page(
            self.wxr,
            "ຊ່ອງ",
            """== ภาษาลาว ==
=== การออกเสียง ===
* {{homophones|lo|qq1=ในถิ่นที่มีการออกเสียงอักษรคู่เหมือนกันเมื่อมีไม้เอก|ສ່ອງ}}
=== คำนาม ===
# [[ช่อง]]""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "homophone": "ສ່ອງ",
                    "raw_tags": ["ในถิ่นที่มีการออกเสียงอักษรคู่เหมือนกันเมื่อมีไม้เอก"],
                    "roman": "ส่อง",
                }
            ],
        )
        self.assertEqual(data[0]["categories"], ["ศัพท์ภาษาลาวที่มีคำพ้องเสียง"])

    def test_vi_ipa(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:vi-pron",
            10,
            """* (''[[นครโฮจิมินห์|นครโฮจิมินห์]]'') [[วิกิพจนานุกรม:สัทอักษรสากล|สัทอักษรสากล]] <sup>([[ภาคผนวก:การออกเสียงภาษาเวียดนาม|คำอธิบาย]])</sup>: <span class="IPA">[ʔɓuəŋ˨˩ ŋʊw˨˩˦]</span>[[หมวดหมู่:ศัพท์ภาษาเวียดนามที่มีการออกเสียงไอพีเอ]]""",
        )
        data = parse_page(
            self.wxr,
            "buồng ngủ",
            """== ภาษาเวียดนาม ==
=== การออกเสียง ===
{{vi-pron}}
=== คำนาม ===
# [[ห้องนอน]]""",
        )
        self.assertEqual(
            data[0]["sounds"], [{"ipa": "[ʔɓuəŋ˨˩ ŋʊw˨˩˦]", "tags": ["Saigon"]}]
        )
        self.assertEqual(
            data[0]["categories"], ["ศัพท์ภาษาเวียดนามที่มีการออกเสียงไอพีเอ"]
        )

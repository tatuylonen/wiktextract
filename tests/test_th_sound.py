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
                {
                    "other": "rót",
                    "tags": ["romanization", "Paiboon"],
                },
                {
                    "other": "rot",
                    "tags": ["romanization", "Royal-Institute"],
                },
                {"ipa": "/rot̚˦˥/^((สัมผัส))"},
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

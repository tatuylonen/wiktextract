from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThLinkage(TestCase):
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

    def test_col(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:col2",
            10,
            """<div class="list-switcher" data-toggle-category="derived terms"><div class="columns-bg term-list ul-column-count" data-column-count="2"><ul><li><span class="Thai" lang="th">[[กบทูด#ภาษาไทย|กบทูด]]</span></li></ul></div><div class="list-switcher-element" data-showtext=" show more ▼ " data-hidetext=" show less ▲ " style="display:none"> </div></div>""",
        )
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาไทย ==
=== รากศัพท์ 2 ===
==== คำนาม ====
# [[ชื่อ]]
===== ลูกคำ =====
{{col2|th|กบทูด}}""",
        )
        self.assertEqual(
            page_data[0]["derived"],
            [{"word": "กบทูด"}],
        )

    def test_list(self):
        page_data = parse_page(
            self.wxr,
            "กบ",
            """== ภาษาไทย ==
=== รากศัพท์ 2 ===
==== คำนาม ====
# [[ชื่อ]]
===== คำพ้องความ =====
* {{l|th|มณฑก}}""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [{"word": "มณฑก"}],
        )

    def test_theasurus_page(self):
        self.wxr.wtp.add_page(
            "อรรถาภิธาน:ระดู",
            110,
            """== ภาษาไทย ==
=== คำนาม ===
==== {{ws sense|th|เลือดที่ถูกขับถ่ายจากมดลูกออกมาทางช่องคลอดทุก ๆ ประมาณ 1 เดือน}} ====
===== คำพ้องความ =====
{{ws beginlist}}
{{ws|th|ต่อมโลหิต}}
{{ws endlist}}""",
        )
        page_data = parse_page(
            self.wxr,
            "ระดู",
            """== ภาษาไทย ==
=== คำนาม ===
# [[เลือด]]
==== คำพ้องความ ====
:''ดูที่ [[อรรถาภิธาน:ระดู]]''""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [{"word": "ต่อมโลหิต", "source": "อรรถาภิธาน:ระดู"}],
        )

    def test_syn_template(self):
        page_data = parse_page(
            self.wxr,
            "โทรทัศน์",
            """== ภาษาไทย ==
=== คำนาม ===
# กระบวนการถ่ายทอด
#: {{syn|th|ทีวี|โทรภาพ}}""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [
                {"word": "ทีวี", "sense": "กระบวนการถ่ายทอด"},
                {"word": "โทรภาพ", "sense": "กระบวนการถ่ายทอด"},
            ],
        )

    def test_col3_zh_pinyin(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:col3",
            10,
            """<div><div><ul><li><span class="Hant" lang="zh">[[電腦遊戲#ภาษาจีน|電腦遊戲]]</span><span class="Zsym mention">&nbsp;/ </span><span class="Hans" lang="zh">[[电脑游戏#ภาษาจีน|电脑游戏]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="zh-Latn" class="tr Latn">diànnǎo yóuxì</span><span class="mention-gloss-paren annotation-paren">)</span></li></ul></div></div>""",
        )
        page_data = parse_page(
            self.wxr,
            "電腦",
            """== ภาษาจีน ==
=== คำนาม ===
# [[คอมพิวเตอร์]]
==== ลูกคำ ====
{{col3|zh|電腦遊戲}}""",
        )
        self.assertEqual(
            page_data[0]["derived"],
            [
                {
                    "word": "電腦遊戲",
                    "roman": "diànnǎo yóuxì",
                    "tags": ["Traditional-Chinese"],
                },
                {
                    "word": "电脑游戏",
                    "roman": "diànnǎo yóuxì",
                    "tags": ["Simplified-Chinese"],
                },
            ],
        )

    def test_sense(self):
        page_data = parse_page(
            self.wxr,
            "aback",
            """== ภาษาอังกฤษ ==
=== คำกริยาวิเศษณ์ ===
# ไป[[ข้าง]][[หลัง]]
=== วลี ===
* [[take aback]] - ทำให้[[สะดุ้ง]], ทำให้[[ตกใจ]]""",
        )
        self.assertEqual(
            page_data[0]["derived"],
            [{"word": "take aback", "sense": "ทำให้สะดุ้ง, ทำให้ตกใจ"}],
        )

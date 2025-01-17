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
            [{"word": "ทีวี"}, {"word": "โทรภาพ"}],
        )

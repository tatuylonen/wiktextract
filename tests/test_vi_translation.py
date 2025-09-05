from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.vi.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestViTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="vi"),
            WiktionaryConfig(
                dump_file_lang_code="vi", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_zh(self):
        self.wxr.wtp.add_page("Bản mẫu:langname", 10, "Tiếng Quan Thoại")
        self.wxr.wtp.add_page(
            "Bản mẫu:t+",
            10,
            """<span class="Hant" lang="cmn">[[:幾何#Tiếng&#95;Quan&#95;Thoại|幾何]]</span><span class="Zsym mention" style="font-size:100%;">&nbsp;/ </span><span class="Hans" lang="cmn">[[:几何#Tiếng&#95;Quan&#95;Thoại|几何]]</span><span class="tpos">&nbsp;[[:zh&#58;幾何|(zh)]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="cmn-Latn" class="tr Latn">jǐhé</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        data = parse_page(
            self.wxr,
            "hình học",
            """==Tiếng Việt==
===Danh từ===
# Ngành liên quan đến
====Dịch====
{{trans-top|Ngành toán học}}
* {{langname|zh}}:
*: {{langname|cmn}}: {{t+|cmn|幾何|tr=jǐhé}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang_code": "cmn",
                    "lang": "Tiếng Quan Thoại",
                    "word": "幾何",
                    "roman": "jǐhé",
                    "sense": "Ngành toán học",
                    "tags": ["Traditional-Chinese"],
                },
                {
                    "lang_code": "cmn",
                    "lang": "Tiếng Quan Thoại",
                    "word": "几何",
                    "roman": "jǐhé",
                    "sense": "Ngành toán học",
                    "tags": ["Simplified-Chinese"],
                },
            ],
        )

    def test_multitrans(self):
        self.wxr.wtp.add_page("Bản mẫu:aas", 10, "[[tiếng Aasax|Tiếng Aasax]]")
        self.wxr.wtp.add_page("Bản mẫu:t2", 10, "{{t|1=aas|2=wa-t}}")
        self.wxr.wtp.add_page(
            "Bản mẫu:t",
            10,
            """<span class="Latn" lang="aas">[[:wa-t#Tiếng&#95;Aasax|wa-t]]</span>[[Category:Mục từ có bản dịch tiếng Aasax|QUAN]]""",
        )
        data = parse_page(
            self.wxr,
            "chó",
            """==Tiếng Việt==
===Danh từ===
# Loài động vật thuộc nhóm ăn thịt
====Dịch====
{{multitrans|data=
{{trans-top|Loài động vật}}
* {{aas}}: {{t2|aas|wa-t}}
{{trans-bottom}}
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "Tiếng Aasax",
                    "lang_code": "aas",
                    "sense": "Loài động vật",
                    "word": "wa-t",
                }
            ],
        )
        self.assertEqual(
            data[0]["categories"], ["Mục từ có bản dịch tiếng Aasax"]
        )

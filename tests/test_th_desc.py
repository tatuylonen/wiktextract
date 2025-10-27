import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThDesc(unittest.TestCase):
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

    def test_desc_template(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:desc",
            10,
            """<span class="desc-arr" title="borrowed">→</span> พม่า: <span class="Mymr" lang="{{{1}}}">[[{{{2}}}]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="my-Latn" class="tr Latn">{{{tr|}}}</span>, <span class="mention-gloss-double-quote">“</span><span class="mention-gloss">{{{t|}}}</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "สยาม",
            """== ภาษาไทย ==
=== คำคุณศัพท์ ===
# [[ของ]]ประเทศไทย (โบราณหรือปัจจุบัน)
===== คำสืบทอด =====
* {{desc|my|သျှမ်း|bor=1|t=Shan}}
* {{desc|pt|Sciam|bor=1}}
** {{desc|en|Siam|bor=1}}""",
        )
        self.assertEqual(
            page_data[0]["descendants"],
            [
                {
                    "lang": "พม่า",
                    "lang_code": "my",
                    "word": "သျှမ်း",
                    "sense": "Shan",
                },
                {
                    "lang": "โปรตุเกส",
                    "lang_code": "pt",
                    "word": "Sciam",
                    "descendants": [
                        {"lang": "อังกฤษ", "lang_code": "en", "word": "Siam"}
                    ],
                },
            ],
        )

    def test_cjkv(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:CJKV",
            10,
            """<div>''[[ซีโน-เซนิก]]'' (<span class="Hant" lang="zh">醫生</span>):
* <span class="desc-arr" title="borrowed">→</span> ญี่ปุ่น: <span class="Jpan" lang="ja">[[:医生#ภาษาญี่ปุ่น|<ruby>医生<rp>(</rp><rt>いせい</rt><rp>)</rp></ruby>]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">isei</span></span><span class="mention-gloss-paren annotation-paren">)</span></div>""",
        )
        data = parse_page(
            self.wxr,
            "醫生",
            """== ภาษาจีน ==
=== คำนาม ===
# [[หมอ]]; [[แพทย์]]
=== คำสืบทอด ===
{{CJKV||s=医生|いせい|의생|y sinh}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang": "ญี่ปุ่น",
                    "lang_code": "ja",
                    "raw_tags": ["borrowed"],
                    "roman": "isei",
                    "ruby": [("医生", "いせい")],
                    "word": "医生",
                }
            ],
        )

    def test_tr_class(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:desc",
            10,
            """<span class="desc-arr" title="borrowed">→</span> เบลารุส: <span class="Cyrl" lang="be">[[:інтэр'ер#ภาษาเบลารุส|інтэр'е́р]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="be" class="tr">อินแตรʺแยร</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        data = parse_page(
            self.wxr,
            "intérieur",
            """== ภาษาฝรั่งเศส ==
=== คำนาม ===
# [[ภาย]][[ใน]], [[ข้าง]]ใน
==== คำสืบทอด ====
* {{desc|be|інтэр'е́р|bor=1}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang": "เบลารุส",
                    "lang_code": "be",
                    "roman": "อินแตรʺแยร",
                    "word": "інтэр'е́р",
                }
            ],
        )

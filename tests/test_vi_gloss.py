from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.vi.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestViGloss(TestCase):
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

    def test_nested_list(self):
        self.wxr.wtp.add_page("Bản mẫu:term", 10, "(''[[Hóa học|Hóa học]]'')")
        data = parse_page(
            self.wxr,
            "băng",
            """==Tiếng Việt==
===Danh từ===
# [[nước|Nước]]
## {{term|Hóa học}} [[khoảng|Khoảng]]""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {"glosses": ["Nước"]},
                {"glosses": ["Nước", "Khoảng"], "topics": ["chemistry"]},
            ],
        )

    def test_italic_example(self):
        data = parse_page(
            self.wxr,
            "war",
            """==Tiếng Anh==
===Danh từ===
# [[chiến tranh|Chiến tranh]].
#: ''aggressive '''war''''' —  chiến tranh xâm lược""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["Chiến tranh."],
                    "examples": [
                        {
                            "text": "aggressive war",
                            "bold_text_offsets": [(11, 14)],
                            "translation": "chiến tranh xâm lược",
                        }
                    ],
                }
            ],
        )

    def test_vi_ruby(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:RQ:Truyện Kiều",
            10,
            """<div class="citation-whole"><span class="cited-source"><span class="None" lang="und">'''1820'''</span>, [[w:Nguyễn Du|Nguyễn Du]] (<span class="Hani" lang="vi">阮攸</span>), <cite>[[:w&#58;Truyện Kiều|Đoạn trường tân thanh (Truyện Kiều)]]</cite>&lrm;<sup>[https://vi.wikisource.org/wiki/Truyện_Kiều_(bản_Liễu_Văn_Ðường_1866)]</sup>, xuất bản <span class="None" lang="und">1866</span>, dòng <span class="None" lang="und">1269</span>:</span><dl><dd><div class="h-quotation"><span class="Latn e-quotation cited-passage" lang="vi"><span lang='vi' style='font-size: 135%25;'><ruby><rb><span class='Hani'>吝</span></rb><rp>(</rp><rt><span style='padding: 0 0.25em;'>Lần</span></rt><rp>)</rp></ruby><ruby><rb><span class='Hani'>吝</span></rb><rp>(</rp><rt><span style='padding: 0 0.25em;'>lần</span></rt><rp>)</rp></ruby><ruby><rb><span class='Hani'>兎</span></rb><rp>(</rp><rt><span style='padding: 0 0.25em;'>thỏ</span></rt><rp>)</rp></ruby><ruby><rb><span class='Hani'>鉑</span></rb><rp>(</rp><rt><span style='padding: 0 0.25em;'>bạc</span></rt><rp>)</rp></ruby>'''<ruby><rb><span class='Hani'>鵶</span></rb><rp>(</rp><rt><span style='padding: 0 0.25em;'>ác</span></rt><rp>)</rp></ruby><ruby><rb><span class='Hani'>鐄</span></rb><rp>(</rp><rt><span style='padding: 0 0.25em;'>vàng</span></rt><rp>)</rp></ruby>'''</span></span></div>[[Category:Định nghĩa mục từ tiếng Việt có trích dẫn ngữ liệu|BANH&#37;]]</dd></dl></div>""",
        )
        data = parse_page(
            self.wxr,
            "ác vàng",
            """==Tiếng Việt==
===Danh từ===
# Mặt trời.
#* {{RQ:Truyện Kiều|year_published=1866|line=1269|passage={{vi-ruby|吝吝兎鉑'''鵶鐄'''|Lần lần thỏ bạc '''ác vàng'''}}}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "categories": [
                        "Định nghĩa mục từ tiếng Việt có trích dẫn ngữ liệu"
                    ],
                    "glosses": ["Mặt trời."],
                    "examples": [
                        {
                            "ref": "1820, Nguyễn Du (阮攸), Đoạn trường tân thanh (Truyện Kiều)^(https://vi.wikisource.org/wiki/Truyện_Kiều_(bản_Liễu_Văn_Ðường_1866)), xuất bản 1866, dòng 1269:",
                            "ruby": [
                                ("吝", "Lần"),
                                ("吝", "lần"),
                                ("兎", "thỏ"),
                                ("鉑", "bạc"),
                                ("鵶", "ác"),
                                ("鐄", "vàng"),
                            ],
                            "text": "吝吝兎鉑鵶鐄",
                        }
                    ],
                }
            ],
        )

    def test_headword_form(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:eng-noun",
            10,
            """<span class="infl-inline">'''dog''' (''số nhiều''&nbsp;<span class="form-of plural-form-of lang-en">'''[[dogs]]'''</span>)</span>[[Category:Danh từ  tiếng Anh|dog]]""",
        )
        data = parse_page(
            self.wxr,
            "dog",
            """==Tiếng Anh==
===Danh từ===
{{eng-noun}}
# [[chó|Chó]].""",
        )
        self.assertEqual(
            data[0]["forms"], [{"form": "dogs", "tags": ["plural"]}]
        )
        self.assertEqual(data[0]["categories"], ["Danh từ tiếng Anh"])

    def test_ja_headword(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:ja-verb-suru",
            10,
            """<span class="headword-line"><strong class="Jpan headword" lang="ja"><ruby>完<rp>(</rp><rt>[[:かんりょう#Tiếng&#95;Nhật|かん]]</rt><rp>)</rp></ruby><ruby>了<rp>(</rp><rt>[[:かんりょう#Tiếng&#95;Nhật|りょう]]</rt><rp>)</rp></ruby>[[:する#Tiếng&#95;Nhật|する]]</strong> (<span class="headword-tr tr" dir="ltr"><span class="Latn" lang="ja">[[:kanryō#Tiếng&#95;Nhật|kanryō]] [[:suru#Tiếng&#95;Nhật|suru]]</span></span>)&nbsp;<i>ngoại hoặc nội động từ&nbsp;<abbr title="chia động từ nhóm サ (nhóm 3)">suru</abbr></i> (<i>stem</i> <b class="Jpan" lang="ja"><ruby>完<rp>(</rp><rt>かん</rt><rp>)</rp></ruby><ruby>了<rp>(</rp><rt>りょう</rt><rp>)</rp></ruby>[[:し#Tiếng&#95;Nhật|し]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">kanryō [[shi]]</span><span class="mention-gloss-paren annotation-paren">)</span>)</span>[[Category:Mục từ tiếng Nhật|かんりょう]]""",
        )
        data = parse_page(
            self.wxr,
            "完了",
            """=={{langname|ja}}==
===Danh từ===
{{ja-verb-suru|tr=both|かんりょう}}
# [[hoàn tất]]; [[hoàn thành]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "完了する",
                    "roman": "kanryō suru",
                    "ruby": [("完", "かん"), ("了", "りょう")],
                    "tags": ["canonical"],
                },
                {
                    "form": "完了し",
                    "roman": "kanryō shi",
                    "ruby": [("完", "かん"), ("了", "りょう")],
                    "tags": ["stem"],
                },
            ],
        )
        self.assertEqual(
            data[0]["tags"], ["transitive", "intransitive", "suru"]
        )
        self.assertEqual(data[0]["categories"], ["Mục từ tiếng Nhật"])

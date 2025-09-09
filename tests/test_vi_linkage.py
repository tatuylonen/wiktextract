from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.vi.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestViLinkage(TestCase):
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

    def test_synonym_in_gloss_list(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:synonyms",
            10,
            """<span class="nyms đồng-nghĩa"><span class="defdate">Đồng nghĩa:</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">từ Hán-Việt</span><span class="ib-brac qualifier-brac">)</span> <span class="Latn" lang="vi">[[:cẩu#Tiếng&#95;Việt|cẩu]]</span>, <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">về mặt để ăn thịt</span><span class="ib-brac qualifier-brac">)</span> <span class="Latn" lang="vi">[[:cầy#Tiếng&#95;Việt|cầy]]</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "chó",
            """==Tiếng Việt==
===Danh từ===
# Loài [[động vật]] thuộc nhóm [[ăn thịt]]
#: {{synonyms|vi|cẩu|cầy|q1=từ Hán-Việt|q2=về mặt để ăn thịt}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "cẩu",
                    "raw_tags": ["từ Hán-Việt"],
                    "sense": "Loài động vật thuộc nhóm ăn thịt",
                },
                {
                    "word": "cầy",
                    "raw_tags": ["về mặt để ăn thịt"],
                    "sense": "Loài động vật thuộc nhóm ăn thịt",
                },
            ],
        )

    def test_alti(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:infl of",
            10,
            """''Dạng'' <span class='form-of-definition use-with-mention'>[[Phụ lục:Từ điển thuật ngữ#giống_đực|giống đực]] [[Phụ lục:Từ điển thuật ngữ#số_ít|số ít]] [[Phụ lục:Từ điển thuật ngữ#thì_quá_khứ|quá khứ]] [[Phụ lục:Từ điển thuật ngữ#thức_trần_thuật|trần thuật]] của <span class='form-of-definition-link'><i class="Cyrl mention" lang="uk">[[:кинутися#Tiếng&#95;Ukraina|ки́нутися]]</i>&nbsp;<span class="gender"><abbr title="thể hoàn thành">h.thành</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="uk-Latn" class="mention-tr tr Latn">kýnutysja</span><span class="mention-gloss-paren annotation-paren">)</span></span></span>""",
        )
        self.wxr.wtp.add_page(
            "Bản mẫu:alti",
            10,
            """<span class="nyms Dạng-thay-thế"><span class="defdate">Dạng thay thế:</span> <span class="Cyrl" lang="uk">[[:кинувся#Tiếng&#95;Ukraina|ки́нувся]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="uk-Latn" class="tr Latn">kýnuvsja</span><span class="mention-gloss-paren annotation-paren">)</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "кинувсь",
            """==Tiếng Ukraina==
===Danh từ===
# {{infl of|uk|ки́нутися||m|s|past|ind|g=pf}}
#: {{alti|uk|ки́нувся}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "ки́нувся",
                    "roman": "kýnuvsja",
                    "tags": ["alternative"],
                    "sense": "Dạng giống đực số ít quá khứ trần thuật của ки́нутися h.thành (kýnutysja)",
                }
            ],
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": [
                        "Dạng giống đực số ít quá khứ trần thuật của ки́нутися h.thành (kýnutysja)"
                    ],
                    "tags": ["form-of"],
                    "form_of": [{"word": "ки́нутися", "roman": "kýnutysja"}],
                }
            ],
        )

    def test_alter(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:q",
            10,
            """<span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">từ lóng Internet</span><span class="ib-brac qualifier-brac">)</span>""",
        )
        self.wxr.wtp.add_page(
            "Bản mẫu:alter",
            10,
            """<span class="Latn" lang="vi">[[:cờ hó#Tiếng&#95;Việt|cờ hó]]</span>""",
        )
        data = parse_page(
            self.wxr,
            "chó",
            """==Tiếng Việt==
===Cách viết khác===
* {{q|từ lóng Internet}} {{alter|vi|cờ hó}}
===Danh từ===
# Loài động vật thuộc nhóm ăn thịt""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "cờ hó",
                    "raw_tags": ["từ lóng Internet"],
                    "tags": ["alternative"],
                }
            ],
        )

    def test_ko_col3(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:col3",
            10,
            """<div class="list-switcher-wrapper"><div class="list-switcher" data-toggle-category="từ phái sinh"><div class="term-list columns-bg ul-column-count" data-column-count="3"><ul><li><span lang="ko" class="Kore">[[천도 복숭아]]</span> (<span lang="ko" class="Kore">[[:天桃#Tiếng&#95;Triều&#95;Tiên|天桃]]‒</span>, <span lang="ko-Latn" class="mention-tr tr Latn">cheondo boksung'a</span>, “quả xuân đào”)</li></ul></div></div></div>
""",
        )
        data = parse_page(
            self.wxr,
            "복숭아",
            """==Tiếng Triều Tiên==
===Danh từ===
# Quả đào
====Từ phái sinh====
{{col3|ko
|{{ko-l|천도 복숭아|天桃‒|quả xuân đào}}
}}""",
        )
        self.assertEqual(
            data[0]["derived"],
            [
                {
                    "word": "천도 복숭아",
                    "roman": "cheondo boksung'a",
                    "other": "天桃‒",
                    "translation": "quả xuân đào",
                }
            ],
        )

    def test_zh_col3(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:col3",
            10,
            """<div class="list-switcher-wrapper"><div class="term-list columns-bg"><ul><li><span class="Hant" lang="zh">[[:鹽溶液#Tiếng&#95;Trung&#95;Quốc|鹽溶液]]</span><span class="Zsym mention" style="font-size:100%;">&nbsp;/ </span><span class="Hans" lang="zh">[[:盐溶液#Tiếng&#95;Trung&#95;Quốc|盐溶液]]</span></li></ul></div></div>""",
        )
        data = parse_page(
            self.wxr,
            "溶液",
            """==Tiếng Trung Quốc==
===Danh từ===
# Dung dịch.
====Từ phái sinh====
{{col3|zh|鹽溶液}}""",
        )
        self.assertEqual(
            data[0]["derived"],
            [
                {"word": "鹽溶液", "tags": ["Traditional-Chinese"]},
                {"word": "盐溶液", "tags": ["Simplified-Chinese"]},
            ],
        )

    def test_link_template(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:sense",
            10,
            """<span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">khoa học</span><span class="ib-brac qualifier-brac">)</span><span class="ib-colon sense-qualifier-colon">:</span>""",
        )
        self.wxr.wtp.add_page(
            "Bản mẫu:l",
            10,
            """<span class="Latn" lang="nl">[[:scheikunde#Tiếng&#95;Hà&#95;Lan|scheikunde]]</span>""",
        )
        data = parse_page(
            self.wxr,
            "chemie",
            """==Tiếng Hà Lan==
===Danh từ===
# Hóa học
====Đồng nghĩa====
* {{sense|khoa học}} {{l|nl|scheikunde}}""",
        )
        self.assertEqual(
            data[0]["synonyms"], [{"word": "scheikunde", "sense": "khoa học"}]
        )

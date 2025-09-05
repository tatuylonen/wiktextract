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
            "Bản mẫu:synonym",
            10,
            """<span class="nyms đồng-nghĩa"><span class="defdate">Đồng nghĩa:</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">không còn dùng</span><span class="ib-brac qualifier-brac">)</span> <span class="Latn" lang="vi">[[:kỷ hà học#Tiếng&#95;Việt|kỷ hà học]]</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "hình học",
            """==Tiếng Việt==
===Danh từ===
# Ngành liên quan đến [[hình dạng]]
#: {{synonym|vi|kỷ hà học|q=không còn dùng}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "kỷ hà học",
                    "tags": ["obsolete"],
                    "sense": "Ngành liên quan đến hình dạng",
                }
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

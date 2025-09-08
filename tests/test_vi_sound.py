from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.vi.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestViSound(TestCase):
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

    def test_vie_pron(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:vie-pron",
            10,
            """{| class="wiktvi-vie-pron wikitable" style="text-align: center;"
|+ [[Wiktionary:IPA|IPA]] theo giọng
|-
! class="wiktvi-vie-pron-hn-th" | [[Hà Nội]] !! class="wiktvi-vie-pron-h-th" colspan="2" | [[Huế]] !! class="wiktvi-vie-pron-sg-th" | [[Sài Gòn]]
|- valign="top"
| class="wiktvi-vie-pron-hn" colspan="1" | <span class="IPA">ʨə̰ː<span class='IPA-tone'>˧˩˧</span> tʰa̤jŋ<span class='IPA-tone'>˨˩</span></span><td class="wiktvi-vie-pron-h" colspan="2"><span class="IPA">tʂəː<span class='IPA-tone'>˧˩˨</span> tʰan<span class='IPA-tone'>˧˧</span></span></td><td class="wiktvi-vie-pron-sg"><span class="IPA">tʂəː<span class='IPA-tone'>˨˩˦</span> tʰan<span class='IPA-tone'>˨˩</span></span></td>
|-
| colspan="4" style="background-color: #ffffff; border-left-color: #ffffff; border-right-color: #ffffff;" |
|-
! class="wiktvi-vie-pron-v-th" | [[Vinh]] !! class="wiktvi-vie-pron-tc-th" colspan="2" | [[Thanh Chương]] !! class="wiktvi-vie-pron-ht-th" | [[Hà Tĩnh]]
|- valign="top"
| class="wiktvi-vie-pron-v" colspan="3" | <span class="IPA">tʂəː<span class='IPA-tone'>˧˩</span> tʰajŋ<span class='IPA-tone'>˧˧</span></span><td class="wiktvi-vie-pron-ht"><span class="IPA">tʂə̰ːʔ<span class='IPA-tone'>˧˩</span> tʰajŋ<span class='IPA-tone'>˧˧</span></span></td>
|}[[Thể loại:Mục từ tiếng Việt có cách phát âm IPA]]""",
        )
        data = parse_page(
            self.wxr,
            "trở thành",
            """==Tiếng Việt==
===Cách phát âm===
{{vie-pron|trở|thành}}
===Ngoại động từ===
# Như trở nên""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {"ipa": "ʨə̰ː˧˩˧ tʰa̤jŋ˨˩", "tags": ["Hà-Nội"]},
                {"ipa": "tʂəː˧˩˨ tʰan˧˧", "tags": ["Huế"]},
                {"ipa": "tʂəː˨˩˦ tʰan˨˩", "tags": ["Saigon"]},
                {"ipa": "tʂəː˧˩ tʰajŋ˧˧", "tags": ["Vinh", "Thanh-Chương"]},
                {"ipa": "tʂə̰ːʔ˧˩ tʰajŋ˧˧", "tags": ["Hà-Tĩnh"]},
            ],
        )

    def test_tyz_ipa(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:tyz-IPA",
            10,
            """* (''[[:vi:w:Thạch An|Thạch An]] – [[:vi:w:Tràng Định|Tràng Định]]'') [[WT:IPA|IPA]]<sup>([[w:Tiếng Tày|ghi chú]])</sup>: <span class="IPA">[kwaːn˧˥]</span>
* (''[[:vi:w:Trùng Khánh (huyện)|Trùng Khánh]]'') [[WT:IPA|IPA]]<sup>([[w:Tiếng Tày|ghi chú]])</sup>: <span class="IPA">[kwaːn˦]</span>[[Thể loại:Mục từ tiếng Tày có cách phát âm IPA]]""",
        )
        data = parse_page(
            self.wxr,
            "quan",
            """==Tiếng Tày==
===Cách phát âm===
{{tyz-IPA}}
===Danh từ===
# vị quan.""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {"ipa": "[kwaːn˧˥]", "raw_tags": ["Thạch An – Tràng Định"]},
                {"ipa": "[kwaːn˦]", "raw_tags": ["Trùng Khánh"]},
            ],
        )
        self.assertEqual(
            data[0]["categories"], ["Mục từ tiếng Tày có cách phát âm IPA"]
        )

    def test_enpr_ipa(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:enPR",
            10,
            """<span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content"><span class="usage-label-accent">[[w:Tiếng Anh Mỹ thông dụng|Anh Mỹ thông dụng]]</span></span><span class="ib-brac qualifier-brac">)</span> [[Appendix:English pronunciation|enPR]]: <span class="AHD enPR">dôg</span>""",
        )
        self.wxr.wtp.add_page(
            "Bản mẫu:IPA4",
            10,
            """[[Wiktionary:IPA|IPA]]<sup>([[Phụ lục:Cách phát âm trong tiếng Anh|ghi chú]])</sup>:&#32;<span class="IPA">/dɔɡ/</span>[[Category:Từ tiếng Anh có 1 âm tiết|DOG]][[Category:Mục từ tiếng Anh có cách phát âm IPA|DOG]]""",
        )
        data = parse_page(
            self.wxr,
            "dog",
            """==Tiếng Anh==
===Cách phát âm===
* {{enPR|dôg|a=GA}}, {{IPA4|en|/dɔɡ/}}
===Danh từ===
# [[chó|Chó]].""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [{"ipa": "dôg", "tags": ["General-American"]}, {"ipa": "/dɔɡ/"}],
        )
        self.assertEqual(
            data[0]["categories"],
            [
                "Từ tiếng Anh có 1 âm tiết",
                "Mục từ tiếng Anh có cách phát âm IPA",
            ],
        )

    def test_rhymes_hyphenation(self):
        self.wxr.wtp.add_page(
            "Bản mẫu:rhymes",
            10,
            """Vần: [[Vần:Tiếng Anh/uːtə(ɹ)|<span class="IPA">-uːtə(ɹ)</span>]][[Category:Vần tiếng Anh/uːtə(ɹ)|COMPUTER]][[Category:Vần tiếng Anh/uːtə(ɹ)/3 âm tiết|COMPUTER]]""",
        )
        self.wxr.wtp.add_page(
            "Bản mẫu:hyphenation",
            10,
            """Tách âm: <span class="Latn" lang="en">com‧put‧er</span>""",
        )
        data = parse_page(
            self.wxr,
            "computer",
            """==Tiếng Anh==
===Cách phát âm===
* {{rhymes|en|uːtə(ɹ)|s=3}}
* {{hyphenation|en|com|put|er}}
===Danh từ===
# [[Máy tính]]""",
        )
        self.assertEqual(data[0]["sounds"], [{"rhymes": "-uːtə(ɹ)"}])
        self.assertEqual(
            data[0]["hyphenations"], [{"parts": ["com", "put", "er"]}]
        )
        self.assertEqual(
            data[0]["categories"],
            ["Vần tiếng Anh/uːtə(ɹ)", "Vần tiếng Anh/uːtə(ɹ)/3 âm tiết"],
        )

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

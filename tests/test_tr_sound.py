from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrSound(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="tr"),
            WiktionaryConfig(
                dump_file_lang_code="tr", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_sound(self):
        self.wxr.wtp.add_page(
            "Şablon:h",
            10,
            "Heceleme: <span class='mention-Latn'>ma‧yıs[[Kategori:Türkçe 2 heceli sözcükler]]</span>",
        )
        page_data = parse_page(
            self.wxr,
            "mayıs",
            """==Türkçe==
===Söyleniş===
* {{IPA|dil=tr|/ma.ˈjɯs/}}
* {{ses|dil=tr|mayıs.ogg|mayıs}}
* {{h|dil=tr||ma|yıs}}
===Ad===
# Yılın 31 gün süren beşinci ayı""",
        )
        self.assertEqual(page_data[0]["hyphenation"], "ma‧yıs")
        self.assertEqual(page_data[0]["sounds"][0], {"ipa": "/ma.ˈjɯs/"})
        self.assertEqual(page_data[0]["sounds"][1]["audio"], "mayıs.ogg")
        self.assertEqual(page_data[0]["sounds"][1]["raw_tags"], ["mayıs"])
        self.assertEqual(
            page_data[0]["categories"], ["Türkçe 2 heceli sözcükler"]
        )

    def test_sound_section_number(self):
        page_data = parse_page(
            self.wxr,
            "حب",
            """==Arapça==
===Köken===
:etymology
===Söyleniş 1===
* {{IPA|dil=ar|/ħubb/}}
====Ad====
[[sevgili]], [[sevilen]]

===Söyleniş 2===
* {{IPA|dil=ar|/ħibb/}}
====Ad====
# [[çekirdek]]ler, [[tane]]ler""",
        )
        self.assertEqual(
            page_data[0]["etymology_texts"], page_data[1]["etymology_texts"]
        )
        self.assertEqual(page_data[0]["sounds"], [{"ipa": "/ħubb/"}])
        self.assertEqual(page_data[1]["sounds"], [{"ipa": "/ħibb/"}])

    def test_cat(self):
        self.wxr.wtp.add_page(
            "Şablon:eş sesliler",
            10,
            '[[eş sesli|Eş sesliler]]: <span class="Latn" lang="en">[[Kat#İngilizce|Kat]]</span>, <span class="Latn" lang="en">[[khat#İngilizce|khat]]</span>, <span class="Latn" lang="en">[[qat#İngilizce|qat]]</span>',
        )
        page_data = parse_page(
            self.wxr,
            "cat",
            """==İngilizce==
===Söyleniş===
* {{kafiyeler|dil=en|æt|s=1}}
* {{eş sesliler|dil=en|Kat|khat|qat}}
===Ad===
[[kedi]], [[pişik]]""",
        )
        self.assertEqual(
            page_data[0]["sounds"],
            [
                {"rhymes": "-æt"},
                {"homophone": "Kat"},
                {"homophone": "khat"},
                {"homophone": "qat"},
            ],
        )

    def test_after_pos(self):
        self.wxr.wtp.add_page(
            "Şablon:h",
            10,
            "Heceleme: <span class='mention-Latn'>Ab‧düs‧sa‧met[[Kategori:Türkçe 4 heceli sözcükler]]</span>",
        )
        page_data = parse_page(
            self.wxr,
            "Abdüssamet",
            """==Türkçe==
===Özel ad===
#gloss
====Heceleme====
:{{h|e|Ab|düs|sa|met|k=1|dil=tr}}""",
        )
        self.assertEqual(page_data[0]["hyphenation"], "Ab‧düs‧sa‧met")

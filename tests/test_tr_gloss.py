from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrGloss(TestCase):
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

    def test_nested_list(self):
        self.wxr.wtp.add_page(
            "Şablon:t",
            10,
            """{{#switch:{{{1}}}
| bilişim = (''bilişim'')[[Kategori:İngilizcede bilişim]]
| #default = (''bazen'', ''özellikle'')
}}""",
        )
        page_data = parse_page(
            self.wxr,
            "FAT",
            """==İngilizce==
===Kısaltma===
# {{t|dil=en|bilişim}} File Allocation Table
## Bir veya
### {{t|dil=en|bazen|özellikle}} [[FAT12]].""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["İngilizcede bilişim"],
                    "glosses": ["File Allocation Table"],
                    "topics": ["informatics"],
                },
                {
                    "categories": ["İngilizcede bilişim"],
                    "glosses": ["File Allocation Table", "Bir veya"],
                    "topics": ["informatics"],
                },
                {
                    "categories": ["İngilizcede bilişim"],
                    "glosses": ["File Allocation Table", "Bir veya", "FAT12."],
                    "topics": ["informatics"],
                    "tags": ["sometimes", "especially"],
                },
            ],
        )

    def test_ux(self):
        page_data = parse_page(
            self.wxr,
            "Zahn",
            """==Almanca==
===Ad===
# [[diş]]
#: {{ux|de|Der Zahnarzt entfernte ihr drei '''Zähne'''.|Diş hekimi '''dişler'''inden üçünü çıkardı.}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "examples": [
                        {
                            "text": "Der Zahnarzt entfernte ihr drei Zähne.",
                            "translation": "Diş hekimi dişlerinden üçünü çıkardı.",
                        }
                    ],
                    "glosses": ["diş"],
                }
            ],
        )

    def test_örnek(self):
        page_data = parse_page(
            self.wxr,
            "game",
            """==İngilizce==
===Ad===
# Oyun oynama [[an|ânı]]; [[maç]].
#: {{örnek|Sally won the '''game'''.|dil=en}}
#:: {{örnek|Sally '''oyunu''' kazandı.|dil=tr}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "examples": [
                        {
                            "text": "Sally won the game.",
                            "translation": "Sally oyunu kazandı.",
                        }
                    ],
                    "glosses": ["Oyun oynama ânı; maç."],
                }
            ],
        )

    def test_tr_ad(self):
        self.wxr.wtp.add_page(
            "Şablon:tr-ad",
            10,
            """<strong class="Latn headword" lang="tr">göz</strong> (''belirtme hâli'' <b class="Latn" lang="tr">[[gözü#Türkçe|gözü]]</b>, ''çoğulu'' <b class="Latn" lang="tr">[[gözler#Türkçe|gözler]]</b>)[[Category:Türkçe sözcükler|GÖZ]][[Category:Türkçe adlar|GÖZ]]""",
        )
        page_data = parse_page(
            self.wxr,
            "göz",
            """==Türkçe==
===Ad===
{{tr-ad}}
# [[bakış]], [[görüş]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "gözü", "tags": ["accusative"]},
                {"form": "gözler", "tags": ["plural"]},
            ],
        )
        self.assertEqual(
            page_data[0]["categories"], ["Türkçe sözcükler", "Türkçe adlar"]
        )

    def test_low_quality(self):
        page_data = parse_page(
            self.wxr,
            "siyah",
            """==Türkçe==
===Ön ad===
:[1] siyah [[renkli]] [[olmak|olan]]
::''Siyah ekmek.''""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["siyah renkli olan"],
                    "examples": [{"text": "Siyah ekmek."}],
                }
            ],
        )

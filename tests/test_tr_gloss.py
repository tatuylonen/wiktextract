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

    def test_form_of_çekim_template_lists(self):
        self.wxr.wtp.add_page(
            "Şablon:karşılaştırma",
            10,
            """<span class='form-of-definition use-with-mention'><span class='cekim-aciklama-bag'><i class="Latn mention" lang="de">[[tauglich#Almanca|tauglich]]</i></span> sözcüğünün [[karşılaştırma derecesi]] çekimi</span>""",
        )
        self.wxr.wtp.add_page(
            "Şablon:çekim",
            10,
            """<span class='form-of-definition use-with-mention'><span class='cekim-aciklama-bag'><i class="Latn mention" lang="de">[[tauglich#Almanca|tauglich]]</i></span> sözcüğünün çekimi:</span>
##<span class='form-of-definition use-with-mention'><span class="inflection-of-conjoined">güçlü<span class="cekim_ayirici">/</span>karma</span> yalın eril tekil</span>
##<span class='form-of-definition use-with-mention'>güçlü <span class="inflection-of-conjoined">tamlayan<span class="cekim_ayirici">/</span>yönelme</span> dişil tekil</span>
##<span class='form-of-definition use-with-mention'>güçlü tamlayan çoğul</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "tauglicher",
            """==Türkçe==
===Ön ad===
# {{karşılaştırma|de|tauglich}}
# {{çekim|dil=de|tauglich||güçlü//karma|nom|e|t|;|güçlü|gen//dat|d|t|;|güçlü|gen|ç}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "form_of": [{"word": "tauglich"}],
                    "glosses": [
                        "tauglich sözcüğünün karşılaştırma derecesi çekimi"
                    ],
                    "tags": ["form-of"],
                },
                {
                    "form_of": [{"word": "tauglich"}],
                    "glosses": ["tauglich sözcüğünün çekimi:"],
                    "tags": ["form-of"],
                },
                {
                    "form_of": [{"word": "tauglich"}],
                    "glosses": [
                        "tauglich sözcüğünün çekimi:",
                        "güçlü/karma yalın eril tekil",
                    ],
                    "tags": ["form-of"],
                },
                {
                    "form_of": [{"word": "tauglich"}],
                    "glosses": [
                        "tauglich sözcüğünün çekimi:",
                        "güçlü tamlayan/yönelme dişil tekil",
                    ],
                    "tags": ["form-of"],
                },
                {
                    "form_of": [{"word": "tauglich"}],
                    "glosses": [
                        "tauglich sözcüğünün çekimi:",
                        "güçlü tamlayan çoğul",
                    ],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_form_of_kısaltma(self):
        self.wxr.wtp.add_page("Şablon:t", 10, "(''kısa'')")
        self.wxr.wtp.add_page(
            "Şablon:kısaltma",
            10,
            """'''<span class="Latn" lang="de">[[türkisch#Almanca|türkisch]]es [[Restaurant#Almanca|Restaurant]]</span>''' kavramının [[kısaltma]]sı""",
        )
        page_data = parse_page(
            self.wxr,
            "Türke",
            """==Almanca==
===Ad===
# {{t|kısa|dil=de}} {{kısaltma|[[türkisch]]es [[Restaurant]]|dil=de}}
#: ''Gehen wir heute Abend zum '''Türken'''?''
#::''Bu akşam '''Türk restoranına''' gidiyor muyuz?''""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["türkisches Restaurant kavramının kısaltması"],
                    "form_of": [
                        {
                            "word": "türkisches Restaurant",
                        }
                    ],
                    "tags": ["abbreviation", "form-of", "short-form"],
                    "examples": [
                        {
                            "text": "Gehen wir heute Abend zum Türken?",
                            "translation": "Bu akşam Türk restoranına gidiyor muyuz?",
                        }
                    ],
                }
            ],
        )

    def test_kısaltma_bold_node(self):
        self.wxr.wtp.add_page(
            "Şablon:t", 10, "(''eğitim'')[[Kategori:Türkçede eğitim]]"
        )
        self.wxr.wtp.add_page(
            "Şablon:kısaltma",
            10,
            """'''<span class="Latn" lang="tr">Türkçe [[ders#Türkçe|ders]]i</span>''' kavramının [[kısaltma]]sı""",
        )
        page_data = parse_page(
            self.wxr,
            "Türkçe",
            """==Almanca==
===Özel ad===
#{{t|dil=tr|eğitim}} {{kısaltma|dil=tr|Türkçe [[ders]]i}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["Türkçede eğitim"],
                    "glosses": ["Türkçe dersi kavramının kısaltması"],
                    "form_of": [{"word": "Türkçe dersi"}],
                    "tags": ["abbreviation", "form-of"],
                    "topics": ["education"],
                }
            ],
        )

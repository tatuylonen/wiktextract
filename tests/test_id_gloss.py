from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.id.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestIdGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="id"),
            WiktionaryConfig(
                dump_file_lang_code="id", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_gloss_nested_list(self):
        self.wxr.wtp.add_page("Templat:bhs", 10, "bahasa Indonesia")
        page_data = parse_page(
            self.wxr,
            "cinta",
            """=={{bhs|id}}==
===Nomina===
[[Kategori:id:Nomina ]]
# rasa sayang atau kasih yang kuat
## rasa [[sayang]]""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "categories": ["id:Nomina"],
                    "lang": "bahasa Indonesia",
                    "lang_code": "id",
                    "pos": "noun",
                    "pos_title": "Nomina",
                    "word": "cinta",
                    "senses": [
                        {"glosses": ["rasa sayang atau kasih yang kuat"]},
                        {
                            "glosses": [
                                "rasa sayang atau kasih yang kuat",
                                "rasa sayang",
                            ]
                        },
                    ],
                }
            ],
        )

    def test_plural_form(self):
        page_data = parse_page(
            self.wxr,
            "anjing",
            """==bahasa Indonesia==
===Nomina===
'''anjing''' (plural: [[anjing-anjing]])
# mamalia""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [{"form": "anjing-anjing", "tags": ["plural"]}],
        )

    def test_variasi(self):
        self.wxr.wtp.add_page(
            "Templat:variasi",
            10,
            """''variasi dari kata [[bengkarung]]''
[[Kategori:Turunan kata bengkarung]]
[[Kategori:id:Variasi kata]]""",
        )
        page_data = parse_page(
            self.wxr,
            "mengkarung",
            """==bahasa Indonesia==
===Nomina===
# {{variasi|bengkarung}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": [
                        "Turunan kata bengkarung",
                        "id:Variasi kata",
                    ],
                    "glosses": ["variasi dari kata bengkarung"],
                    "alt_of": [{"word": "bengkarung"}],
                    "tags": ["alt-of"],
                }
            ],
        )

    def test_form_of(self):
        page_data = parse_page(
            self.wxr,
            "berkehendaknya",
            """==bahasa Indonesia==
===Verba===
#''bentuk posesif orang ketiga dari [[berkehendak]]''""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["bentuk posesif orang ketiga dari berkehendak"],
                    "form_of": [{"word": "berkehendak"}],
                    "tags": ["form-of"],
                }
            ],
        )

    def test_imbuhan_di_kan(self):
        page_data = parse_page(
            self.wxr,
            "diabadikan",
            """==bahasa Indonesia==
===Verba===
'''diabadikan''' (''[[di-]]'' + ''[[abadi]]'' + ''[[-kan]]'' ; pasif: [[diabadikan|di-]], [[kuabadikan|ku-]], [[kauabadikan|kau-]], transitif: [[abadikan|abadikan]], imperatif: [[abadikanlah|-lah]])
#''bentuk pasif dari [[mengabadikan]] """,
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "diabadikan", "tags": ["passive"]},
                {"form": "kuabadikan", "tags": ["passive"]},
                {"form": "kauabadikan", "tags": ["passive"]},
                {"form": "abadikan", "tags": ["transitive"]},
                {"form": "abadikanlah", "tags": ["imperative"]},
            ],
        )

    def test_imbuhan_ber(self):
        page_data = parse_page(
            self.wxr,
            "bebercak",
            """==bahasa Indonesia==
===Verba===
'''bebercak''' (''[[ber-]]'' + ''[[bercak#bahasa Indonesia|bercak]]'', aktif: [[membercakkan]], pasif: [[dibercakkan]])
[[Kategori:Turunan kata bercak]]
# mempunyai bercak; ada bercaknya""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "membercakkan", "tags": ["active"]},
                {"form": "dibercakkan", "tags": ["passive"]},
            ],
        )
        self.assertEqual(page_data[0]["categories"], ["Turunan kata bercak"])

    def test_klasik(self):
        self.wxr.wtp.add_page(
            "Templat:klasik",
            10,
            """<i title="Istilah klasik"><span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">klasik</span><span class="ib-brac">)</span></span></i> [[:Kategori:id:Istilah klasik|·]][[Kategori:id:Istilah klasik|bebercak]] <i title="Istilah arkais"><span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">arkais</span><span class="ib-brac">)</span></span></i> [[:Kategori:id:Istilah arkais|·]]""",
        )
        page_data = parse_page(
            self.wxr,
            "demi",
            """==bahasa Indonesia==
===Preposisi===
#{{klasik}} sebagai; seperti (untuk membandingkan):""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["sebagai; seperti (untuk membandingkan):"],
                    "tags": ["Classical", "archaic"],
                    "categories": ["id:Istilah klasik", "id:Istilah arkais"],
                }
            ],
        )

    def test_usage_note(self):
        page_data = parse_page(
            self.wxr,
            "kamu",
            """==bahasa Indonesia==
===Pronomina===
# sense
=== Penggunaan ===
* list 1
** list 2
:Lihat pula penggunaan di lema [[-mu]]/[[-nya]].""",
        )
        self.assertEqual(
            page_data[0]["notes"],
            ["list 1", "list 2", "Lihat pula penggunaan di lema -mu/-nya."],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPlGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_gloss(self):
        self.wxr.wtp.add_page(
            "Szablon:język polski",
            10,
            '<span class="lang-code primary-lang-code lang-code-pl" id="pl">[[Słownik języka polskiego|język polski]]</span>[[Kategoria:polski (indeks)]]',
        )
        self.wxr.wtp.add_page("Szablon:kynol", 10, "kynol.")
        self.wxr.wtp.add_page(
            "Szablon:wikipedia",
            10,
            '<span><templatestyles src="skrót/styles.css" /><span class="short-container short-no-comma-next">[[Aneks:Skróty używane w Wikisłowniku#Z|<span class="short-wrapper" title="zobacz" data-expanded="zobacz"><span class="short-content">zob.</span></span>]]</span> '
            "też"
            " [[w:Dog|dog]] w Wikipedii</span>",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "dog",
                """== dog ({{język polski}}) ==
===znaczenia===
''rzeczownik, rodzaj męskozwierzęcy''
: (1.1) {{kynol}} [[nazwa]] [[rasa|rasy]] [[pies|psa]]; {{wikipedia}}""",
            ),
            [
                {
                    "categories": ["polski (indeks)"],
                    "lang": "język polski",
                    "lang_code": "pl",
                    "senses": [
                        {
                            "glosses": ["nazwa rasy psa"],
                            "topics": ["cynology"],
                            "sense_index": "1.1",
                        }
                    ],
                    "pos": "noun",
                    "pos_text": "rzeczownik",
                    "tags": ["masculine", "animate"],
                    "word": "dog",
                }
            ],
        )

    def test_abbr(self):
        self.wxr.wtp.add_page(
            "Szablon:język angielski",
            10,
            '<span class="lang-code primary-lang-code lang-code-en" id="en">[[Słownik języka angielskiego|język angielski]]</span>[[Kategoria:angielski (indeks)]]',
        )
        self.wxr.wtp.add_page("Szablon:kynol", 10, "kynol.")
        self.assertEqual(
            parse_page(
                self.wxr,
                "AYPI",
                """== AYPI ({{język angielski}}) ==
===znaczenia===
''skrótowiec''
: (1.1) = [[and|And]] [[your|Your]] [[point|Point]] [[is|Is]]? → [[co|Co]] [[chcieć|chciałeś]] [[przez]] [[to]] [[powiedzieć|powiedzieć]]?""",
            ),
            [
                {
                    "categories": ["angielski (indeks)"],
                    "lang": "język angielski",
                    "lang_code": "en",
                    "senses": [
                        {
                            "glosses": [
                                "And Your Point Is? → Co chciałeś przez to powiedzieć?"
                            ],
                            "sense_index": "1.1",
                        }
                    ],
                    "pos": "abbrev",
                    "pos_text": "skrótowiec",
                    "tags": ["abbreviation"],
                    "word": "AYPI",
                }
            ],
        )

    def test_form_of(self):
        self.wxr.wtp.add_page(
            "Szablon:język szwedzki",
            10,
            '<span class="lang-code primary-lang-code lang-code-sv" id="sv">[[Słownik języka szwedzkiego|język szwedzki]]</span>[[Kategoria:szwedzki (formy fleksyjne)]]',
        )
        self.wxr.wtp.add_page(
            "Szablon:forma czasownika",
            10,
            "<i>czasownik, forma fleksyjna</i>[[Kategoria:Formy czasowników szwedzkich]]",
        )
        self.wxr.wtp.add_page(
            "Szablon:szw-forma czas-przesz",
            10,
            "''czas przeszły ([[preteritum#sv|preteritum]]) od'' [[dö#sv|dö]]",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "dog",
                """== dog ({{język szwedzki}}) ==
===znaczenia===
''{{forma czasownika|sv}}''
: (1.1) {{szw-forma czas-przesz|dö}}""",
            ),
            [
                {
                    "categories": [
                        "szwedzki (formy fleksyjne)",
                        "Formy czasowników szwedzkich",
                    ],
                    "lang": "język szwedzki",
                    "lang_code": "sv",
                    "senses": [
                        {
                            "form_of": [{"word": "dö"}],
                            "glosses": ["czas przeszły (preteritum) od dö"],
                            "sense_index": "1.1",
                        }
                    ],
                    "tags": ["form-of"],
                    "pos": "verb",
                    "pos_text": "czasownik",
                    "word": "dog",
                }
            ],
        )

    def test_zob_ekwiw_pupr(self):
        self.wxr.wtp.add_page(
            "Szablon:język chiński standardowy",
            10,
            '<span class="lang-code primary-lang-code lang-code-zh" id="zh">[[:Kategoria:Język chiński standardowy|język chiński standardowy]]</span>',
        )
        self.wxr.wtp.add_page(
            "Szablon:zob-ekwiw-pupr",
            10,
            """zobacz ekwiwalent w piśmie uproszczonym: <span class='set-foreign'><span lang="zh" xml:lang="zh">[[爱情]]</span></span>""",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "愛情",
                """== {{zh|愛情}} ({{język chiński standardowy}}) ==
===znaczenia===
: (1.1) {{zob-ekwiw-pupr|爱情}}
                """,
            ),
            [
                {
                    "categories": ["Język chiński standardowy"],
                    "lang": "język chiński standardowy",
                    "lang_code": "zh",
                    "senses": [
                        {
                            "form_of": [{"word": "爱情"}],
                            "glosses": [
                                "zobacz ekwiwalent w piśmie uproszczonym: 爱情"
                            ],
                            "sense_index": "1.1",
                            "tags": ["form-of"],
                        }
                    ],
                    "pos": "unknown",
                    "word": "愛情",
                }
            ],
        )

    def test_two_italic_nodes(self):
        # shouldn't have no-gloss tag
        self.wxr.wtp.add_page(
            "Szablon:język polski",
            10,
            '<span class="lang-code primary-lang-code lang-code-pl" id="pl">[[Słownik języka polskiego|język polski]]</span>',
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "płakać",
                """== płakać ({{język polski}}) ==
===znaczenia===
''czasownik nieprzechodni niedokonany'' ({{dk}} ''brak'')
: (1.1) [[wylewać]] [[łza|łzy]], [[ronić łzy]]""",
            ),
            [
                {
                    "lang": "język polski",
                    "lang_code": "pl",
                    "senses": [
                        {
                            "glosses": ["wylewać łzy, ronić łzy"],
                            "sense_index": "1.1",
                        }
                    ],
                    "pos": "verb",
                    "pos_text": "czasownik",
                    "tags": ["intransitive", "imperfective"],
                    "word": "płakać",
                }
            ],
        )

    def test_not_tag_gloss_template(self):
        self.wxr.wtp.add_page(
            "Szablon:język polski",
            10,
            '<span class="lang-code primary-lang-code lang-code-pl" id="pl">[[Słownik języka polskiego|język polski]]</span>',
        )
        self.wxr.wtp.add_page(
            "Szablon:bot",
            10,
            "bot.",
        )
        self.wxr.wtp.add_page(
            "Szablon:nazwa systematyczna",
            10,
            """''[[Oryza|<span title="łacińska nazwa systematyczna">Oryza</span>]]''&#32;<span>[[L.]]</span><ref name="Oryza">ref text</ref>""",
        )
        data = parse_page(
            self.wxr,
            "ryż",
            """== ryż ({{język polski}}) ==
===znaczenia===
''rzeczownik, rodzaj męskorzeczowy''
: (1.1) {{bot}} [[roślina]] [[zboże|zbożowa]] {{nazwa systematyczna|Oryza|L.|ref=tak}}, [[z]] [[rodzina|rodziny]] [[trawa|traw]] [[występować|występująca]] [[w]] [[klimat|klimacie]] [[wilgotny]]m; {{wikipedia}}""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "glosses": [
                    "roślina zbożowa Oryza L., z rodziny traw występująca w klimacie wilgotnym"
                ],
                "topics": ["botany"],
                "sense_index": "1.1",
            },
        )

    def test_punt_pos(self):
        self.wxr.wtp.add_page(
            "Szablon:użycie międzynarodowe",
            10,
            '<span class="lang-code primary-lang-code lang-code-inter" id="inter">[[:Kategoria:Użycie międzynarodowe|użycie międzynarodowe]]</span>',
        )
        self.wxr.wtp.add_page(
            "Szablon:język polski",
            10,
            '<span class="lang-code primary-lang-code lang-code-pl" id="pl">[[Słownik języka polskiego|język polski]]</span>',
        )
        data = parse_page(
            self.wxr,
            "'",
            """== ' ({{użycie międzynarodowe}}) ==
===znaczenia===
''symbol''
: (1.1) [[apostrof]]

== ' ({{język polski}}) ==
===znaczenia===
''znak interpunkcyjny''
: (1.1) stosowany""",
        )
        self.assertEqual(
            data[0]["senses"], [{"glosses": ["apostrof"], "sense_index": "1.1"}]
        )
        self.assertEqual(data[0]["lang"], "użycie międzynarodowe")
        self.assertEqual(
            data[1]["senses"],
            [{"glosses": ["stosowany"], "sense_index": "1.1"}],
        )
        self.assertEqual(data[1]["lang"], "język polski")

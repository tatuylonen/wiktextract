from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="nl"),
            WiktionaryConfig(
                dump_file_lang_code="nl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_simple_case(self):
        self.wxr.wtp.add_page(
            "Sjabloon:=nld=",
            10,
            """== ''[[WikiWoordenboek:Nederlands|Nederlands]]'' ==
[[Categorie:Woorden in het Nederlands]]""",
            need_pre_expand=True,
        )
        self.wxr.wtp.add_page(
            "Sjabloon:-noun-",
            10,
            """====''[[WikiWoordenboek:Zelfstandig naamwoord|Zelfstandig naamwoord]]''====
[[Categorie:Zelfstandig naamwoord in het Nederlands]]""",
            need_pre_expand=True,
        )
        self.wxr.wtp.add_page(
            "Sjabloon:roofdieren",
            10,
            "<span>([[roofdieren]])</span>[[Categorie:Roofdieren_in_het_Nederlands]][[Categorie:Zoogdieren in het Nederlands]]",
        )
        self.wxr.wtp.add_page(
            "Sjabloon:species",
            10,
            "<span>[[:wikispecies:Canis lupus familiaris|<span>''Canis lupus familiaris''</span>]]&nbsp;[[File:WikiSpecies.svg|14px|link=Wikispecies|op Wikispecies]]</span> ",
        )
        data = parse_page(
            self.wxr,
            "hond",
            """{{=nld=}}
{{-noun-|nld}}
[A] {{-l-|m}}
#{{roofdieren|nld}} {{species|Canis lupus familiaris}} zoogdier uit de familie van de hondachtigen""",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "Nederlands",
                    "lang_code": "nl",
                    "pos": "noun",
                    "pos_title": "Zelfstandig naamwoord",
                    "categories": [
                        "Woorden in het Nederlands",
                        "Zelfstandig naamwoord in het Nederlands",
                    ],
                    "senses": [
                        {
                            "categories": [
                                "Roofdieren_in_het_Nederlands",
                                "Zoogdieren in het Nederlands",
                            ],
                            "glosses": [
                                "Canis lupus familiaris zoogdier uit de familie van de hondachtigen"
                            ],
                            "raw_tags": ["roofdieren"],
                        }
                    ],
                    "tags": ["masculine"],
                    "word": "hond",
                }
            ],
        )

    def test_noun_pl(self):
        self.wxr.wtp.add_page(
            "Sjabloon:noun-pl",
            10,
            """de&ensp;'''honden'''&ensp;[[WikiWoordenboek:Meervoud|<span>mv</span>]]
#meervoud van het zelfstandig naamwoord [[hond|hond]][[Categorie:Zelfstandignaamwoordsvorm in het Nederlands]]""",
        )
        data = parse_page(
            self.wxr,
            "honden",
            """==Nederlands==
====Zelfstandig naamwoord====
{{noun-pl|hond}}""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "categories": ["Zelfstandignaamwoordsvorm in het Nederlands"],
                "glosses": ["meervoud van het zelfstandig naamwoord hond"],
                "form_of": [{"word": "hond"}],
                "tags": ["form-of", "plural"],
            },
        )

    def test_noun_form(self):
        self.wxr.wtp.add_page(
            "Sjabloon:noun-form",
            10,
            """'''honden''' <br>
# <i> meervoud</i> van [[hond#Drents|hond]][[Categorie:Zelfstandignaamwoordsvorm in het Drents]]""",
        )
        data = parse_page(
            self.wxr,
            "honden",
            """==Drents==
====Zelfstandig naamwoord====
{{noun-form|hond|drt|getal=p}}""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "categories": ["Zelfstandignaamwoordsvorm in het Drents"],
                "glosses": ["meervoud van hond"],
                "form_of": [{"word": "hond"}],
                "tags": ["form-of", "plural"],
            },
        )

    def test_italic_tag(self):
        self.wxr.wtp.add_page(
            "Sjabloon:erga",
            10,
            """<span>[[WikiWoordenboek:Werkwoord#Ergativiteit|ergatief]]</span>[[Categorie:Ergatief werkwoord in het Nederlands]]""",
        )
        data = parse_page(
            self.wxr,
            "lopen",
            """==Nederlands==
====Werkwoord====
#''(Noord-Nederlands)'' {{erga|nld}} stappen, gaan, wandelen""",
        )
        self.assertEqual(
            data[0]["senses"][0],
            {
                "categories": ["Ergatief werkwoord in het Nederlands"],
                "tags": ["ergative"],
                "raw_tags": ["Noord-Nederlands"],
                "glosses": ["stappen, gaan, wandelen"],
            },
        )

    def test_2ps(self):
        self.wxr.wtp.add_page(
            "Sjabloon:2ps",
            10,
            """{| class="infobox"
! vervoeging van
|-
|[[staren/vervoeging|staren]]
|}
'''staart'''
#tweede persoon enkelvoud tegenwoordige tijd van  [[staren]]<br>
#:*''<nowiki></nowiki>Jij '''staart'''.<nowiki></nowiki>''&#160;
#derde persoon enkelvoud tegenwoordige tijd van  [[staren]]<br>
#:*''<nowiki></nowiki>Hij '''staart'''.<nowiki></nowiki>''&#160;
#<span>([[verouderd]])</span>[[Categorie:Verouderd_in_het_Nederlands]] gebiedende wijs meervoud van  [[staren]]<br>
#:*''<nowiki></nowiki>'''Staart'''!<nowiki></nowiki>''&#160;
[[Categorie:Werkwoordsvorm in het Nederlands]]""",
        )
        data = parse_page(
            self.wxr,
            "staart",
            """==Nederlands==
====Werkwoord====
{{2ps|staren}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": [
                        "tweede persoon enkelvoud tegenwoordige tijd van staren"
                    ],
                    "tags": ["form-of"],
                    "form_of": [{"word": "staren"}],
                    "examples": [{"text": "Jij staart."}],
                },
                {
                    "glosses": [
                        "derde persoon enkelvoud tegenwoordige tijd van staren"
                    ],
                    "tags": ["form-of"],
                    "form_of": [{"word": "staren"}],
                    "examples": [{"text": "Hij staart."}],
                },
                {
                    "categories": ["Verouderd_in_het_Nederlands"],
                    "glosses": ["gebiedende wijs meervoud van staren"],
                    "tags": ["obsolete", "form-of"],
                    "form_of": [{"word": "staren"}],
                    "examples": [{"text": "Staart!"}],
                },
            ],
        )
        self.assertEqual(
            data[0]["categories"], ["Werkwoordsvorm in het Nederlands"]
        )

    def test_two_tag_templates(self):
        self.wxr.wtp.add_page(
            "Sjabloon:figuurlijk",
            10,
            """<span>([[figuurlijk]])</span>[[Categorie:Figuurlijk_in_het_Nederlands]]""",
        )
        self.wxr.wtp.add_page(
            "Sjabloon:anatomie",
            10,
            """<span>([[anatomie]])</span>[[Categorie:Anatomie_in_het_Nederlands]]""",
        )
        data = parse_page(
            self.wxr,
            "staart",
            """==Nederlands==
====Zelfstandig naamwoord====
#{{figuurlijk|nld}}, {{anatomie|nld}} een bundel lang haar""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "categories": [
                        "Figuurlijk_in_het_Nederlands",
                        "Anatomie_in_het_Nederlands",
                    ],
                    "glosses": ["een bundel lang haar"],
                    "tags": ["figuratively"],
                    "topics": ["anatomy"],
                }
            ],
        )

    def test_eng_onv_d(self):
        self.wxr.wtp.add_page(
            "Sjabloon:eng-onv-d",
            10,
            """'''opening'''
#onvoltooid deelwoord van [[open#Engels|open]]

====''[[WikiWoordenboek:Zelfstandig naamwoord|Zelfstandig naamwoord]]''====
[[Categorie:Zelfstandig naamwoord in het Engels]]
'''opening'''
#gerundium van [[open#Engels|open]]""",
        )
        data = parse_page(
            self.wxr,
            "opening",
            """==Engels==
====Werkwoord====
{{eng-onv-d|open}}""",
        )
        self.assertEqual(data[0]["pos"], "verb")
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["onvoltooid deelwoord van open"],
                    "tags": ["form-of"],
                    "form_of": [{"word": "open"}],
                }
            ],
        )
        self.assertEqual(
            data[1]["senses"],
            [
                {
                    "glosses": ["gerundium van open"],
                    "tags": ["form-of"],
                    "form_of": [{"word": "open"}],
                }
            ],
        )
        self.assertEqual(data[1]["pos"], "noun")
        self.assertEqual(
            data[1]["categories"], ["Zelfstandig naamwoord in het Engels"]
        )

    def test_no_gloss_but_has_tag_example(self):
        self.wxr.wtp.add_page(
            "Sjabloon:naam-m",
            10,
            """<span>([[mannelijk]]e [[naam]])</span>[[Categorie:Mannelijke naam_in_het_Engels]]""",
        )
        data = parse_page(
            self.wxr,
            "Clark",
            """==Engels==
====Eigennaam====
'''Clark'''
#{{naam-m|eng}}
{{bijv-2|'''Clark''' Gable was a popular movie star|'''Clark''' Gable was een bekende filmster.}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "categories": ["Mannelijke naam_in_het_Engels"],
                    "tags": ["masculine", "name", "no-gloss"],
                    "examples": [
                        {
                            "text": "Clark Gable was a popular movie star",
                            "translation": "Clark Gable was een bekende filmster.",
                        }
                    ],
                }
            ],
        )

    def test_double_colons_list(self):
        self.wxr.wtp.add_page(
            "Sjabloon:oudeschrijfwijze",
            10,
            """'''Ehstland'''
# verouderde spelling of vorm van [[Estland#Duits|Estland]][[Categorie:Oude spelling van het Duits]]""",
        )
        self.wxr.wtp.add_page(
            "Sjabloon:verouderd",
            10,
            "<span>([[verouderd]])</span>[[Categorie:Verouderd_in_het_Duits]]",
        )
        data = parse_page(
            self.wxr,
            "Ehstland",
            """==Duits==
====Eigennaam====
{{oudeschrijfwijze|Estland||deu}}
::{{verouderd|deu}} nominatief enkelvoud van [[Ehstland#Duits|Ehstland]]""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "categories": [
                        "Oude spelling van het Duits",
                        "Verouderd_in_het_Duits",
                    ],
                    "glosses": [
                        "verouderde spelling of vorm van Estland",
                        "nominatief enkelvoud van Ehstland",
                    ],
                    "tags": ["form-of", "obsolete"],
                    "form_of": [{"word": "Estland"}],
                }
            ],
        )

    def test_tag_template_after_form_of_template(self):
        self.wxr.wtp.add_page(
            "Sjabloon:geologie",
            10,
            "<span>([[geologie]])</span>[[Categorie:Geologie_in_het_Nederlands]]",
        )
        data = parse_page(
            self.wxr,
            "Fanerozoïcum",
            """==Nederlands==
====Zelfstandig naamwoord====
{{oudeschrijfwijze|fanerozoïcum|2006|nld|g=n}} {{geologie|nld}}""",
        )
        self.assertEqual(data[0]["senses"][0]["topics"], ["geology"])
        self.assertEqual(
            data[0]["senses"][0]["categories"], ["Geologie_in_het_Nederlands"]
        )

    def test_double_colons_list_in_parentheses(self):
        self.wxr.wtp.add_page(
            "Sjabloon:oudeschrijfwijze",
            10,
            """'''Haafer'''
# verouderde spelling of vorm van [[Hafer#Duits|Hafer]]&#32;tot 1876[[Categorie:Oude spelling van het Duits van voor 1876]]""",
        )
        self.wxr.wtp.add_page("Sjabloon:Q", 10, "[[Haafer#Duits|Haafer]]")
        data = parse_page(
            self.wxr,
            "Haafer",
            """==Duits==
====Zelfstandig naamwoord====
{{oudeschrijfwijze|Hafer|1876|deu}}
::(nominatief mannelijk enkelvoud van {{Q|Haafer|deu}})""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": [
                        "verouderde spelling of vorm van Hafer tot 1876",
                        "nominatief mannelijk enkelvoud van Haafer",
                    ],
                    "categories": ["Oude spelling van het Duits van voor 1876"],
                    "tags": ["form-of"],
                    "form_of": [{"word": "Hafer"}],
                }
            ],
        )

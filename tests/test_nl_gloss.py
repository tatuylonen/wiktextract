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

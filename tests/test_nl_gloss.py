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
                    "sense_index": "A",
                    "tags": ["masculine"],
                    "word": "hond",
                }
            ],
        )

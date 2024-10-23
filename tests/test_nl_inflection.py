from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlInflection(TestCase):
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

    def test_nlnoun_different_pos(self):
        self.wxr.wtp.add_page(
            "Sjabloon:-nlnoun-",
            10,
            """{| class="infobox"
|-
!
! [[enkelvoud]]
! [[meervoud]]
|-
| class="infoboxrijhoofding" | [[zelfstandig naamwoord|naamwoord]]
| loop
| [[lopen]]
|-
| class="infoboxrijhoofding" | [[verkleinwoord]]
| [[loopje]]
| [[loopjes]]
|}[[Categorie:Zelfstandig naamwoord in het Nederlands]][[Categorie:Telbaar]]""",
        )
        data = parse_page(
            self.wxr,
            "loop",
            """==Nederlands==
=====Woordafbreking=====
*loop
{{-nlnoun-|{{pn}}|[[lopen]]|[[{{pn}}je]]|[[{{pn}}jes]]}}
====Zelfstandig naamwoord====
{{-l-|m}}
#voorste deel van een [[wapen]]
====Werkwoord====
{{1ps|lopen}}""",
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]["categories"],
            ["Zelfstandig naamwoord in het Nederlands", "Telbaar"],
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "lopen", "tags": ["plural"]},
                {"form": "loopje", "tags": ["diminutive", "singular"]},
                {"form": "loopjes", "tags": ["diminutive", "plural"]},
            ],
        )
        self.assertTrue("categories" not in data[1])
        self.assertTrue("forms" not in data[1])

    def test_nlnoun_same_pos(self):
        self.wxr.wtp.add_page(
            "Sjabloon:-nlnoun-",
            10,
            """{| class="infobox"
|-
!
! [[enkelvoud]]
! [[meervoud]]
|-
| class="infoboxrijhoofding" | [[zelfstandig naamwoord|naamwoord]]
| hond
| [[honden]]
|-
| class="infoboxrijhoofding" | [[verkleinwoord]]
| [[hondje]]
| [[hondjes]]
|}[[Categorie:Zelfstandig naamwoord in het Nederlands]][[Categorie:Telbaar]]
""",
        )
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
=====Woordherkomst en -opbouw=====
*[A] uiteindelijk
{{-nlnoun-|hond|[[honden]]|[[hondje]]|[[hondjes]]}}
====Zelfstandig naamwoord====
[A] {{-l-|m}}
# zoogdier
====Zelfstandig naamwoord====
[B] {{-l-|o}}
# landmaat""",
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["categories"], data[1]["categories"])
        self.assertEqual(len(data[0]["forms"]), 3)
        self.assertEqual(data[0]["forms"], data[1]["forms"])

    def test_nlstam(self):
        self.wxr.wtp.add_page(
            "Sjabloon:-nlstam-", 10, "[[Categorie:Werkwoord in het Nederlands]]"
        )
        self.wxr.wtp.add_page(
            "achten/vervoeging",
            0,
            "{{-nlverb-|achten|[[acht]]|[[acht]]|[[achten]]|[[achtte]]|[[achtten]]|hebben|[[geacht]]|[[achte]]|overg=1}}",
        )
        self.wxr.wtp.add_page(
            "Sjabloon:-nlverb-",
            10,
            """{|class="infoboxlinks"
!colspan="9"| <big>[[WikiWoordenboek:Vervoeging|vervoeging]] van de bedrijvende vorm van [[achten#Nederlands|achten]]</big>
|-
!colspan="3" class="infoboxrijhoofding"| [[WikiWoordenboek:Infinitief|onbepaalde wijs]]
! colspan="3"| kort
! colspan="3"| lang
|-
|colspan="1" rowspan="2" class="infoboxrijhoofding"| onvoltooid
|colspan="2" class="infoboxrijhoofding"| tegenwoordig
| colspan="3"| achten
| colspan="3"| te achten
|-
|colspan="2" class="infoboxrijhoofding"| toekomend
| colspan="3"| zullen achten
| colspan="3"| te zullen achten
|-
! !!colspan="2" | [[WikiWoordenboek:Onvoltooid deelwoord|onvoltooid deelwoord]]
|-
|class="infoboxrijhoofding"| ||colspan="2"| [[achtend#Nederlands|achtend]]
|}
[[Categorie:Vervoeging in het Nederlands]]""",
        )
        data = parse_page(
            self.wxr,
            "achten",
            """==Nederlands==
=====Woordherkomst en -opbouw=====
* In de betekenis
{{-nlstam-|{{pn}}|[[achtte]]|[[geacht]]|'ɑxtə(n)|'ɑxtə|ɣə'ʔɑxt|scheid=n|k=t}}
====Werkwoord====
# beschouwen""",
        )
        self.assertEqual(
            data[0]["categories"],
            ["Werkwoord in het Nederlands", "Vervoeging in het Nederlands"],
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "achtte", "tags": ["past"], "ipa": "'ɑxtə"},
                {
                    "form": "geacht",
                    "tags": ["past", "participle"],
                    "ipa": "ɣə'ʔɑxt",
                },
                {
                    "form": "te achten",
                    "raw_tags": ["lang"],
                    "source": "achten/vervoeging",
                    "tags": ["active", "infinitive", "imperfect", "present"],
                },
                {
                    "form": "zullen achten",
                    "source": "achten/vervoeging",
                    "tags": [
                        "active",
                        "infinitive",
                        "imperfect",
                        "future",
                        "short-form",
                    ],
                },
                {
                    "form": "te zullen achten",
                    "raw_tags": ["lang"],
                    "source": "achten/vervoeging",
                    "tags": ["active", "infinitive", "imperfect", "future"],
                },
                {
                    "form": "achtend",
                    "source": "achten/vervoeging",
                    "tags": ["imperfect", "participle"],
                },
            ],
        )

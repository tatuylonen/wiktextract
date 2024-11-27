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
# gloss""",
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

    def test_nlnoun_lines(self):
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
| corpus
| [[corpora]]<br>[[corpussen]]
|}""",
        )
        data = parse_page(
            self.wxr,
            "corpus",
            """==Nederlands==
=====Woordherkomst en -opbouw=====
*Leenwoord
{{-nlnoun-|{{pn}}|[[corpora]]<br>[[{{pn}}sen]]|[[corpusje]]|[[corpusjes]]}}
====Zelfstandig naamwoord====
{{-l-|n}}
# alle verzamelde""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "corpora", "tags": ["plural"]},
                {"form": "corpussen", "tags": ["plural"]},
            ],
        )

    def test_separate_forms_data(self):
        self.wxr.wtp.add_page(
            "Sjabloon:-nlstam-",
            10,
            """{| class="infobox"
! colspan="3"|[[WikiWoordenboek:Stamtijd|stamtijd]]
|-
! [[WikiWoordenboek:Infinitief|onbepaalde <br> wijs]]
! [[WikiWoordenboek:Verleden tijd|verleden <br> tijd]]
! [[WikiWoordenboek:Voltooid deelwoord|voltooid <br> deelwoord]]
|-
| width=25%|{{{1}}} <br> <span class="IPAtekst">{{{4}}}</span>
| width=25%|{{{2}}} <br> <span class="IPAtekst">{{{5}}}/</span>
| width=25%|{{{3}}} <br> <span class="IPAtekst">{{{6}}}</span>
|}""",
        )
        self.wxr.wtp.add_page(
            "scheren/vervoeging",
            0,
            """==Nederlands==
===rakelings langs iets bewegen===
{{-nlverb-|scheren|[[scheer]]|[[scheert]]|[[scheren]]|[[scheerde]]|[[scheerden]]|zijn|[[gescheerd]]|[[schere]]}}""",
        )
        self.wxr.wtp.add_page(
            "Sjabloon:-nlverb-",
            10,
            """{|class="infoboxlinks"
!colspan="9"| <big>[[WikiWoordenboek:Vervoeging|vervoeging]] van de bedrijvende vorm van [[scheren#Nederlands|scheren]]</big>
|-
!colspan="3" class="infoboxrijhoofding"| [[WikiWoordenboek:Infinitief|onbepaalde wijs]]
! colspan="3"| kort
! colspan="3"| lang
|-
|colspan="1" rowspan="2" class="infoboxrijhoofding"| onvoltooid
|colspan="2" class="infoboxrijhoofding"| tegenwoordig
| colspan="3"| scheren
| colspan="3"| te scheren
|}""",
        )
        data = parse_page(
            self.wxr,
            "scheren",
            """==Nederlands==
{{-nlstam-|scheren|[[schoor]]|[[geschoren]]|/'sxɪːrə(n)/|/sxɔːr/|/ɣə'sxɔrə(n)/|scheid=n|k=2|'''[1] - [2]'''}}
{{-nlstam-|scheren|[[scheerde]]|[[gescheerd]]|/'sxɪːrə(n)/|/sxɪːrdə/|/ɣə'sxɪːrt/|scheid=n|k=d|'''[3]'''}}
====Werkwoord====
# met een schaar of mes de huid van haar ontdoen

{{-nlstam-|scheren|[[schoor]]|[[geschoren]]|/'sxɪːrə(n)/|/sxɔːr/|/ɣə'sxɔrə(n)/|scheid=n|k=2|'''[1] - [2]'''}}
====Werkwoord====
# bespotten, de spot drijven met, grappen maken met""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "schoor", "ipa": "/sxɔːr/", "tags": ["past"]},
                {
                    "form": "geschoren",
                    "ipa": "/ɣə'sxɔrə(n)/",
                    "tags": ["past", "participle"],
                },
                {
                    "form": "te scheren",
                    "raw_tags": ["lang"],
                    "sense": "rakelings langs iets bewegen",
                    "source": "scheren/vervoeging",
                    "tags": ["active", "infinitive", "imperfect", "present"],
                },
                {"form": "scheerde", "ipa": "/sxɪːrdə/", "tags": ["past"]},
                {
                    "form": "gescheerd",
                    "ipa": "/ɣə'sxɪːrt/",
                    "tags": ["past", "participle"],
                },
            ],
        )
        self.assertEqual(
            data[1]["forms"],
            [
                {"form": "schoor", "ipa": "/sxɔːr/", "tags": ["past"]},
                {
                    "form": "geschoren",
                    "ipa": "/ɣə'sxɔrə(n)/",
                    "tags": ["past", "participle"],
                },
                {
                    "form": "te scheren",
                    "raw_tags": ["lang"],
                    "sense": "rakelings langs iets bewegen",
                    "source": "scheren/vervoeging",
                    "tags": ["active", "infinitive", "imperfect", "present"],
                },
            ],
        )

    def test_nlstam_two_lines(self):
        self.wxr.wtp.add_page("Sjabloon:-nlstam-", 10, "")
        data = parse_page(
            self.wxr,
            "zweren",
            """==Nederlands==
{{-nlstam-|{{pn}}|[[zweerde]]<br>[[zwoor]]|[[gezworen]]|/'zʋɪːrə(n)/|/'zʋɪːrdə/<br>/zʋɔːr/|/ɣə'zʋɔːrə(n)/|{{nlsterk2}}{{nlzwak-d}}</br>{{nlmix}}|2.|scheid=n}}
=====Werkwoord=====
# geïnfecteerd raken, etteren""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "zweerde", "ipa": "/'zʋɪːrdə/", "tags": ["past"]},
                {"form": "zwoor", "ipa": "/zʋɔːr/", "tags": ["past"]},
                {
                    "form": "gezworen",
                    "ipa": "/ɣə'zʋɔːrə(n)/",
                    "tags": ["past", "participle"],
                },
            ],
        )

    def test_nlverb_slash(self):
        self.wxr.wtp.add_page("Sjabloon:-nlstam-", 10, "")
        self.wxr.wtp.add_page(
            "zweren/vervoeging",
            0,
            """{{-nlverb-|zweren|[[zweer]]|[[zweert]]|[[zweren]]|[[zweerde]]/ [[zwoor]]|[[zweerden]]/ [[zworen]]|hebben|[[gezworen]]|[[zwere]]||[[zweerde(t)]]/ [[zwoort]]|erg=1}}""",
        )
        self.wxr.wtp.add_page(
            "Sjabloon:-nlverb-",
            10,
            """{|
! enkelvoud
|-
! verleden
| [[zweerde]]/ [[zwoor]]
|-
! tweede
|-
! toekomend
| zal/zult [[gezworen]] hebben
|}""",
        )
        data = parse_page(
            self.wxr,
            "zweren",
            """==Nederlands==
{{-nlstam-}}
=====Werkwoord=====
# geïnfecteerd raken, etteren""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "zweerde",
                    "tags": ["singular", "past"],
                    "source": "zweren/vervoeging",
                },
                {
                    "form": "zwoor",
                    "tags": ["singular", "past"],
                    "source": "zweren/vervoeging",
                },
                {
                    "form": "zal gezworen hebben",
                    "tags": ["second-person", "future"],
                    "source": "zweren/vervoeging",
                },
                {
                    "form": "zult gezworen hebben",
                    "tags": ["second-person", "future"],
                    "source": "zweren/vervoeging",
                },
            ],
        )

    def test_dumstam_and_dumverb_templates(self):
        self.wxr.wtp.add_page("Sjabloon:-dumstam-", 10, "")
        self.wxr.wtp.add_page(
            "graven/vervoeging",
            0,
            """==Middelnederlands==
{{-dumverb-}}""",
        )
        self.wxr.wtp.add_page(
            "Sjabloon:-dumverb-",
            10,
            """{|class="infoboxlinks"
! !!onbepaalde wijs!! gebiedende wijs!!onv. deelwoord!!volt deelwoord
|-
|class="infoboxrijhoofding"| || [[graven#Middelnederlands|graven]]<br/>te gravene|| grave<br/>gravet||gravende||gegraven
|-
!!!colspan="2"|aantonend!!colspan="2"|aanvoegend
|-
!!!tegenwoordig!!verleden!!tegenwoordig!!verleden
|-
|class="infoboxrijhoofding"|[[ic]]||grave||groef||grave||groeve
|}""",
        )
        data = parse_page(
            self.wxr,
            "graven",
            """==Middelnederlands==
{{-dumstam-|graven|groef|groeven|ghegraven|{{dumsterk6}}}}
=====Werkwoord=====
# graven""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "groef", "tags": ["past", "singular"]},
                {"form": "groeven", "tags": ["past", "plural"]},
                {"form": "ghegraven", "tags": ["past", "participle"]},
                {
                    "form": "graven",
                    "tags": ["infinitive"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "te gravene",
                    "tags": ["infinitive"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "grave",
                    "tags": ["imperative"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "gravet",
                    "tags": ["imperative"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "gravende",
                    "tags": ["imperfect", "participle"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "gegraven",
                    "tags": ["past", "participle"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "grave",
                    "raw_tags": ["ic"],
                    "tags": ["indicative", "present"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "groef",
                    "raw_tags": ["ic"],
                    "tags": ["indicative", "past"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "grave",
                    "raw_tags": ["ic"],
                    "tags": ["subjunctive", "present"],
                    "source": "graven/vervoeging",
                },
                {
                    "form": "groeve",
                    "raw_tags": ["ic"],
                    "tags": ["subjunctive", "past"],
                    "source": "graven/vervoeging",
                },
            ],
        )

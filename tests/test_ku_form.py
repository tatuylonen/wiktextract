from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ku.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKuForm(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ku"),
            WiktionaryConfig(
                dump_file_lang_code="ku", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_ku_tewîn_nav(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:ku-tewîn-nav",
            10,
            """{|
|-
! colspan="3" align="center" | Zayenda mê ya binavkirî
|-
! Rewş
! Yekjimar
! Pirjimar
|-
! Navkî
|<span lang="ku"><strong class="selflink">av</strong></span>
|<span lang="ku"><strong class="selflink">av</strong></span>
|-
! Îzafe
|<span lang="ku">[[ava#Kurmancî|av<b>a</b>]]</span>
|<span lang="ku">[[avên#Kurmancî|av<b>ên</b>]]</span>
|-
! colspan="3" align="center" | Zayenda mê ya nebinavkirî
|-
! Rewş
! Yekjimar
! Pirjimar
|-
! Navkî
|<span lang="ku">[[avek#Kurmancî|av<b>ek</b>]]</span>
|<span lang="ku">[[avin#Kurmancî|av<b>in</b>]]</span>
|}""",
        )
        page_data = parse_page(
            self.wxr,
            "av",
            """== {{ziman|ku}} ==
=== Navdêr ===
{{ku-tewîn-nav|av|mê}}
# [[vexwarin|Vexwarin]]a bê[[reng]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "ava",
                    "tags": ["feminine", "definite", "construct", "singular"],
                },
                {
                    "form": "avên",
                    "tags": ["feminine", "definite", "construct", "plural"],
                },
                {
                    "form": "avek",
                    "tags": [
                        "feminine",
                        "indefinite",
                        "nominative",
                        "singular",
                    ],
                },
                {
                    "form": "avin",
                    "tags": ["feminine", "indefinite", "nominative", "plural"],
                },
            ],
        )

    def test_ku_tewîn_lk(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:ku-tewîn-lk",
            10,
            """{|
! colspan="3" align="center"| dîtin (lêkera gerguhêz)
|-
| colspan="3" align="center" | Rehê dema niha:&nbsp;[[-bîn-|-<b>bîn</b>-]]
|-
! rowspan="5" |<kbd><span title="Raweya pêşkerî"><span>RP.</span></span></kbd><br>Niha
|-
| width="60" |ez
|<span lang="ku">[[dibînim#Kurmancî|dibînim]]</span>
|-
| colspan="3" align="center" | Rehê dema borî:&nbsp;&nbsp;/&nbsp;<span>-<b>dî</b>-</span>
|-
! rowspan="5" | <kbd><span title="Raweya pêşkerî"><span>RP.</span></span></kbd><br>Boriya<br>sade
|-
| <span style="color:green">min</span>
|<span lang="ku">[[dît#Kurmancî|dît]]</span>&nbsp;/&nbsp;<span lang="ku">[[dî#Kurmancî|dî]]</span>
|-
| colspan="3"|Formên din:[[Wêne:1rightarrow.png|15px|link=]] [[Tewandin:dîtin|Tewandin:dîtin]]
|}
""",
        )
        page_data = parse_page(
            self.wxr,
            "dîtin",
            """== {{ziman|ku}} ==
=== Lêker ===
{{ku-tewîn-lk|dîtin|form=gerguhêz|niha=bîn|borî=dît|borî2=dî}}
# Bi""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "dibînim",
                    "tags": [
                        "transitive",
                        "present",
                        "first-person",
                        "singular",
                    ],
                    "raw_tags": ["ez"],
                },
                {
                    "form": "dît",
                    "tags": ["transitive", "past", "first-person", "singular"],
                    "raw_tags": ["min"],
                },
                {
                    "form": "dî",
                    "tags": ["transitive", "past", "first-person", "singular"],
                    "raw_tags": ["min"],
                },
            ],
        )

    def test_etîket_tewandin(self):
        import wiktextract.clean as clean_module

        clean_module.IMAGE_LINK_RE = None  # clear cache
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:ku-tewîn-lk",
            10,
            """{|
| colspan="3"|Formên din:[[Wêne:1rightarrow.png|15px|link=]] [[Tewandin:gotin|Tewandin:gotin]]
|}""",
        )
        self.wxr.wtp.add_page(
            "Tewandin:gotin",
            106,
            """== Tewandin ==
{{etîket tewandin
|etîket1  = Standard
|naverok1 = {{ku-tewandin|gotin|form=gerguhêz|niha=bêj|borî=got}}
}}""",
        )
        self.wxr.wtp.add_page(
            "Şablon:ku-tewandin",
            10,
            """<div><span>vegere '''[[gotin#Kurmancî|gotin]]''' </span></div>
{| cellspacing="0" cellpadding="4"
|-
|+ colspan="8" | [[Gotûbêja modulê:ku-tewandin|Pirsgirêkan nîşan bide – Pêşniyaran bike]]
|-
! colspan="8" | Tewandina lêkera [[gotin]]<br/><span>(hevedudanî, gerguhêz)</span></big><br/>
|-
!colspan="4"|
!colspan="2" | Dema niha
!colspan="2" | Dema borî
|-
!colspan="4" | Reh
|colspan="2" | –bêj–
|colspan="2" | –got–
|-
!colspan="8" | Raweya pêşkerî (daxuyanî) - <small><i>Indicative</i></small>
|-
!colspan="4" | [[Pêvek:Rastnivîsî/Lêker/Dema niha|Dema niha]] - <small><i>Present</i></small>
!colspan="4"| [[Pêvek:Rastnivîsî/Lêker/Dema borî ya sade|Raboriya sade]] - <small><i>Preterite</i></small><br><small>Dema boriya têdeyî</small>
|-
!colspan="2" | Erênî
!colspan="2" | Neyînî
!colspan="2" | Erênî
!colspan="2" | Neyînî
|-
|colspan="2"|ez dibêjim
|colspan="2"|ez <b>na</b>bêjim
|colspan="2"|<span style="color:green">min </span> got
|colspan="2"|<span style="color:green">min </span> <b>ne</b>got
|}
== Binêre ==
* [[:Kategorî:Tewandin:lêkerên hevedudanî yên kurmancî li gel "gotin"|Tewandin:lêkerên '''hevedudanî''' yên kurmancî li gel "'''gotin'''"]]
* [[:Kategorî:Tewandin:lêkerên pêkhatî yên kurmancî li gel "gotin"|Tewandin:lêkerên '''pêkhatî''' yên kurmancî li gel "'''gotin'''"]][[Kategorî:Tewandin:lêker (kurmancî)]][[Kategorî:Tewandin:lêkerên xwerû (kurmancî)]]
[[Kategorî:Tewandin:lêkerên gerguhêz (kurmancî)]]
[[Kategorî:Tewandin:lêkerên xwerû yên gerguhêz (kurmancî)]]""",
        )
        page_data = parse_page(
            self.wxr,
            "gotin",
            """== {{ziman|ku}} ==
=== Lêker ===
{{ku-tewîn-lk|gotin|form=gerguhêz|niha=bêj|borî=got}}
# Bi""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            [
                'Tewandin:lêkerên hevedudanî yên kurmancî li gel "gotin"',
                'Tewandin:lêkerên pêkhatî yên kurmancî li gel "gotin"',
                "Tewandin:lêker (kurmancî)",
                "Tewandin:lêkerên xwerû (kurmancî)",
                "Tewandin:lêkerên gerguhêz (kurmancî)",
                "Tewandin:lêkerên xwerû yên gerguhêz (kurmancî)",
            ],
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "–bêj–",
                    "tags": ["standard", "root", "present"],
                    "raw_tags": [
                        "Tewandina lêkera gotin\n(hevedudanî, gerguhêz)"
                    ],
                    "source": "Tewandin:gotin",
                },
                {
                    "form": "–got–",
                    "tags": ["standard", "root", "past"],
                    "raw_tags": [
                        "Tewandina lêkera gotin\n(hevedudanî, gerguhêz)"
                    ],
                    "source": "Tewandin:gotin",
                },
                {
                    "form": "ez dibêjim",
                    "tags": ["standard", "indicative", "present", "positive"],
                    "source": "Tewandin:gotin",
                },
                {
                    "form": "ez nabêjim",
                    "tags": ["standard", "indicative", "present", "negative"],
                    "source": "Tewandin:gotin",
                },
                {
                    "form": "min got",
                    "tags": ["standard", "indicative", "past", "positive"],
                    "source": "Tewandin:gotin",
                },
                {
                    "form": "min negot",
                    "tags": ["standard", "indicative", "past", "negative"],
                    "source": "Tewandin:gotin",
                },
            ],
        )

    def test_ku_tewîn_rd(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:ku-tewîn-rd",
            10,
            """{|
|-
! Pozîtîv
! Komparatîv
! Sûperlatîv
|-
| aqil
| <span><span>aqil'''tir'''</span></span>
| '''herî'''&nbsp;aqil<br><span><span>aqil'''tirîn'''</span></span>
|}""",
        )
        page_data = parse_page(
            self.wxr,
            "aqil",
            """== {{ziman|ku}} ==
=== Rengdêr ===
{{ku-tewîn-rd|aqil}}
# [[jîr|Jîr]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "aqiltir", "tags": ["comparative"]},
                {"form": "herî aqil", "tags": ["superlative"]},
                {"form": "aqiltirîn", "tags": ["superlative"]},
            ],
        )

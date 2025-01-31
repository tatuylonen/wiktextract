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
                    "tags": ["transitive", "present"],
                    "raw_tags": ["ez"],
                },
                {
                    "form": "dît",
                    "tags": ["transitive", "past"],
                    "raw_tags": ["min"],
                },
                {
                    "form": "dî",
                    "tags": ["transitive", "past"],
                    "raw_tags": ["min"],
                },
            ],
        )

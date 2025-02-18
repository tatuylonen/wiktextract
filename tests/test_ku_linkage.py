from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ku.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKuLinkage(TestCase):
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

    def test_ku_ar(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:ku-ar",
            10,
            """<span class="Latn" lang="ku">[[kurdî-erebî#Kurmancî|kurdî-erebî]]</span>: <span class="Arab" lang="ku">[[کووچک#Kurmancî|کووچک]]</span>&lrm;""",
        )
        page_data = parse_page(
            self.wxr,
            "kûçik",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[heywan|Heywanek]]
==== Bi alfabeyên din ====
* {{ku-ar|کووچک}}""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [{"form": "کووچک", "raw_tags": ["kurdî-erebî"]}],
        )

    def test_kol_text(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        page_data = parse_page(
            self.wxr,
            "av",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[vexwarin|Vexwarin]]a bê[[reng]]
==== Jê ====
{{kol3|ku|cure=Jê
|kêmav
}}""",
        )
        self.assertEqual(page_data[0]["derived"], [{"word": "kêmav"}])

    def test_stûn_link(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        page_data = parse_page(
            self.wxr,
            "se",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[ajal|Ajal]]ek
==== Hevmane ====
{{stûn|
* [[kûçik]]
}}""",
        )
        self.assertEqual(page_data[0]["synonyms"], [{"word": "kûçik"}])

    def test_stûn_g(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        page_data = parse_page(
            self.wxr,
            "dar",
            """== {{ziman|ku}} ==
=== Navdêr 1 ===
# [[riwek|Riwek]]eke
==== Hevmane ====
{{stûn|
* [[kûçik]]
}}""",
        )
        self.assertEqual(page_data[0]["synonyms"], [{"word": "kûçik"}])

    def test_kol_hw(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:hw",
            10,
            """<span class="Latn" lang="ku">[[pisik#Kurmancî|pisik]]</span> &ndash; ''[[w:Reşoyî (devok)|Reşwî]]''""",
        )
        page_data = parse_page(
            self.wxr,
            "pisîk",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[heywan|Heywanek]]
==== Hevmane ====
{{kol2|ku|cure=Herwiha
| {{hw|ku|pisik||Reşwî}}
}}""",
        )
        self.assertEqual(page_data[0]["synonyms"], [{"word": "pisik"}])

    def test_mj(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:g",
            10,
            """<span class="Latn" lang="ku">[[pişê#Kurmancî|pişê]]</span>&nbsp;<span class="gender"><abbr title="zayenda mê">m</abbr></span>""",
        )
        self.wxr.wtp.add_page(
            "Şablon:mj",
            10,
            """<i><span class="ib-brac">(</span><span class="ib-content">[[{{{1}}}]]</span><span class="ib-brac">)</span></i>""",
        )
        page_data = parse_page(
            self.wxr,
            "pisîk",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[heywan|Heywanek]]
==== Hevmane ====
* {{mj|zimanê zarokan}} {{g|ku|pişê|z=m}}""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [{"word": "pişê", "tags": ["childish", "feminine"]}],
        )

    def test_kol_tag(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        page_data = parse_page(
            self.wxr,
            "aqil",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[bal]]
==== Jê ====
{{kol3|ku|cure=Jê
|aqil kirin<q:lêker>
}}""",
        )
        self.assertEqual(
            page_data[0]["derived"], [{"word": "aqil kirin", "tags": ["verb"]}]
        )

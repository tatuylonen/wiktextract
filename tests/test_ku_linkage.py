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

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ku.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKuSound(TestCase):
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

    def test_ku_ipa(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:ku-IPA",
            10,
            """[[IPA]]<sup>([[Wîkîferheng:IPA kurdî|kilîd]])</sup>: <span class="IPA">/ɑːv/</span>[[Kategorî:Bilêvkirina IPAyê bi kurmancî]]""",
        )
        page_data = parse_page(
            self.wxr,
            "av",
            """== {{ziman|ku}} ==
=== Bilêvkirin ===
* {{ku-IPA}}
=== Navdêr ===
# [[vexwarin|Vexwarin]]a bê[[reng]]""",
        )
        self.assertEqual(
            page_data[0]["categories"], ["Bilêvkirina IPAyê bi kurmancî"]
        )
        self.assertEqual(page_data[0]["sounds"], [{"ipa": "/ɑːv/"}])

    def test_deng(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:deng",
            10,
            """<phonos lang="ku" text="" wikibase="" file="LL-Q36368 (kur)-Dildadil-av.wav">Deng&nbsp;(Amed)</phonos></span>[[Kategorî:Dengên &nbsp;kurmancî ji Amedê]][[Kategorî:Deng&nbsp;bi kurmancî]]""",
        )
        page_data = parse_page(
            self.wxr,
            "av",
            """== {{ziman|ku}} ==
=== Bilêvkirin ===
* {{deng|ku|LL-Q36368 (kur)-Dildadil-av.wav|Deng|Amed}}
=== Navdêr ===
# [[vexwarin|Vexwarin]]a bê[[reng]]""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            ["Dengên kurmancî ji Amedê", "Deng bi kurmancî"],
        )
        self.assertEqual(
            page_data[0]["sounds"][0]["audio"],
            "LL-Q36368 (kur)-Dildadil-av.wav",
        )

    def test_ku_kîte(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:ku-kîte",
            10,
            """[[kîte#ku|Kîtekirin]]: lê·ker""",
        )
        page_data = parse_page(
            self.wxr,
            "lêker",
            """== {{ziman|ku}} ==
=== Bilêvkirin ===
* {{ku-kîte}}
=== Navdêr 1 ===
# [[peyv|Peyvên]]""",
        )
        self.assertEqual(page_data[0]["hyphenation"], "lê·ker")

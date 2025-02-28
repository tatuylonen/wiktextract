from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.id.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestIdSound(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="id"),
            WiktionaryConfig(
                dump_file_lang_code="id", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_air(self):
        self.wxr.wtp.add_page(
            "Templat:audio",
            10,
            """<table><tr><td>''Suara''</td><td class="audiofile">[[File:LL-Q9240 (ind)-Xbypass-air.wav|noicon|175px]]</td><td>([[:File:LL-Q9240 (ind)-Xbypass-air.wav|file]])</td></tr></table>[[Category:id:Lema dengan tautan audio|a]]""",
        )
        page_data = parse_page(
            self.wxr,
            "air",
            """==bahasa Indonesia==
===Nomina===
# senyawa dengan
====Pelafalan====
* {{IPA|/a.ir/}}
* {{audio|id|LL-Q9240 (ind)-Xbypass-air.wav|''Suara''}}""",
        )
        self.assertEqual(page_data[0]["sounds"][0], {"ipa": "/a.ir/"})
        self.assertEqual(
            page_data[0]["sounds"][1]["audio"], "LL-Q9240 (ind)-Xbypass-air.wav"
        )
        self.assertEqual(page_data[0]["sounds"][1]["raw_tags"], ["Suara"])
        self.assertEqual(
            page_data[0]["categories"], ["id:Lema dengan tautan audio"]
        )

    def test_a_tag(self):
        self.wxr.wtp.add_page("Templat:a", 10, "({{{1}}})")
        page_data = parse_page(
            self.wxr,
            "constant",
            """==bahasa Inggris==
===Nomina===
# sesuatu yang
====Ejaan====
* {{a|RP}} {{IPA|/ˈkɒnstənt/}}""",
        )
        self.assertEqual(
            page_data[0]["sounds"],
            [{"ipa": "/ˈkɒnstənt/", "tags": ["Received-Pronunciation"]}],
        )

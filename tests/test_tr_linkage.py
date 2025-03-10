from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.tr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestTrLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="tr"),
            WiktionaryConfig(
                dump_file_lang_code="tr", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_list(self):
        self.wxr.wtp.add_page("Şablon:mânâ", 10, "({{{1}}}):")
        self.wxr.wtp.add_page("Şablon:şerh", 10, "({{{1}}})")
        page_data = parse_page(
            self.wxr,
            "adam",
            """==Türkçe==
===Ad===
# bir [[alan]]ı benimseyen [[kişi]]
=====Eş anlamlılar=====
* {{mânâ|koca}} [[zevc]] {{şerh|eskimiş}}""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [{"word": "zevc", "sense": "koca", "tags": ["obsolete"]}],
        )

    def test_link(self):
        page_data = parse_page(
            self.wxr,
            "adam",
            """==Türkçe==
===Ad===
# bir [[alan]]ı benimseyen [[kişi]]
=====Deyimler=====
[[adam başı]],
[[adam gibi adam]]""",
        )
        self.assertEqual(
            page_data[0]["idioms"],
            [{"word": "adam başı"}, {"word": "adam gibi adam"}],
        )

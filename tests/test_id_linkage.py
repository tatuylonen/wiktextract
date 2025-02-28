from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.id.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestIdLinkage(TestCase):
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

    def test_syn_in_gloss_list(self):
        page_data = parse_page(
            self.wxr,
            "abang",
            """==bahasa Minangkabau==
===Nomina===
# kakak laki-laki; panggilan (istri) kepada suami:
#:{{syn|min|uda}}""",
        )
        self.assertEqual(
            page_data[0]["synonyms"],
            [
                {
                    "word": "uda",
                    "sense": "kakak laki-laki; panggilan (istri) kepada suami:",
                }
            ],
        )

    def test_linkage_list(self):
        self.wxr.wtp.add_page("Templat:q", 10, "({{{1}}})")
        page_data = parse_page(
            self.wxr,
            "constant",
            """==bahasa Inggris==
===Nomina===
# sesuatu yang
====Kata terkait====
* {{l|en|constancy}} {{q|n}}""",
        )
        self.assertEqual(
            page_data[0]["related"], [{"word": "constancy", "tags": ["neuter"]}]
        )

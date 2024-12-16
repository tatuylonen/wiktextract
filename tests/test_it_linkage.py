from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="it"),
            WiktionaryConfig(
                dump_file_lang_code="it", capture_language_codes=None
            ),
        )

    def test_synonyms(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        self.wxr.wtp.add_page(
            "Template:Fig", 10, "<small>(''senso figurato'')</small>"
        )
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
# [[animale]]
===Sinonimi===
* [[animale]], amico dell’uomo
* {{Fig}} ''(di freddo)'' [[forte]], [[intenso]]""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {"word": "animale"},
                {"word": "amico dell’uomo"},
                {"word": "forte", "raw_tags": ["senso figurato", "di freddo"]},
                {"word": "intenso"},
            ],
        )

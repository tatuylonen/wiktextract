from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlLinkage(TestCase):
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

    def test_intens_template(self):
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
====Zelfstandig naamwoord====
# zoogdier
=====Hyponiemen=====
{{intens|nld|1}} [[superhond]]
{{intens|nld|2}} [[kankerhond]], [[tyfushond]]
*[1] [[reu]]
{{L-top|01|[1] honden naar de rol de ze vervullen}}
*[[asielhond]]
{{L-bottom|01}}
*[2] [[christenhond]]""",
        )
        self.assertEqual(
            data[0]["hyponyms"],
            [
                {
                    "word": "superhond",
                    "sense_index": 1,
                    "raw_tags": ["intensivering"],
                },
                {
                    "word": "kankerhond",
                    "sense_index": 2,
                    "raw_tags": ["intensivering"],
                },
                {
                    "word": "tyfushond",
                    "sense_index": 2,
                    "raw_tags": ["intensivering"],
                },
                {"word": "reu", "sense_index": 1},
                {
                    "word": "asielhond",
                    "sense_index": 1,
                    "sense": "honden naar de rol de ze vervullen",
                },
                {"word": "christenhond", "sense_index": 2},
            ],
        )

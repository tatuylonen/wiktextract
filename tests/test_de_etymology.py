import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestDeEtymology(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_etymology_list(self):
        page_data = parse_page(
            self.wxr,
            "aus dem Effeff",
            """== aus dem Effeff ({{Sprache|Deutsch}}) ==
=== {{Wortart|Wortverbindung|Deutsch}} ===
====Bedeutungen====
:[1] sehr gut, besonders gut, ohne große Mühen, [[ausgezeichnet]]
====Herkunft====
:Es ist nicht restlos geklärt
:* So wurde beispielsweise seit dem 17.""",
        )
        self.assertEqual(
            page_data[0]["etymology_texts"],
            [
                "Es ist nicht restlos geklärt",
                "So wurde beispielsweise seit dem 17.",
            ],
        )

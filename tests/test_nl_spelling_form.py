from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlSpellingForm(TestCase):
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

    def test_italic_note(self):
        data = parse_page(
            self.wxr,
            "jij",
            """==Nederlands==
====Persoonlijk voornaamwoord====
#[[tweede persoon]] [[enkelvoud]] [[informeel]]
=====Schrijfwijzen=====
*jíȷ́ ''(sterk benadrukte vorm in officiële spelling)''
*[[je#Persoonlijk voornaamwoord|je]] ''(onbenadrukte vorm)''""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "jíȷ́",
                    "note": "sterk benadrukte vorm in officiële spelling",
                },
                {"form": "je", "note": "onbenadrukte vorm"},
            ],
        )

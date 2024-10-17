from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlDescendant(TestCase):
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

    def test_desc(self):
        self.wxr.wtp.add_page("Sjabloon:Q", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Sjabloon:nld", 10, "Nederlands")
        self.wxr.wtp.add_page("Sjabloon:afr", 10, "Afrikaans")
        self.wxr.wtp.add_page("Sjabloon:eng", 10, "Engels")
        self.wxr.wtp.add_page("Sjabloon:por", 10, "Portugees")
        data = parse_page(
            self.wxr,
            "ja",
            """==Middelnederlands==
====Bijwoord====
# ja
=====Overerving en ontlening=====
* {{nld}}: {{Q|ja|nld}}
** {{afr}}: {{Q|ja|afr}}
*** → {{eng}}: {{Q|ja|eng}}
*** → {{por}}: [[iá]]""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang": "Nederlands",
                    "lang_code": "nl",
                    "word": "ja",
                    "descendants": [
                        {
                            "lang": "Afrikaans",
                            "lang_code": "af",
                            "word": "ja",
                            "descendants": [
                                {
                                    "lang": "Engels",
                                    "lang_code": "en",
                                    "word": "ja",
                                },
                                {
                                    "lang": "Portugees",
                                    "lang_code": "pt",
                                    "word": "iá",
                                },
                            ],
                        }
                    ],
                }
            ],
        )

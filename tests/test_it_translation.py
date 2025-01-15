from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="it"),
            WiktionaryConfig(
                dump_file_lang_code="it", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_common_lists(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        self.wxr.wtp.add_page("Template:ar", 10, "arabo")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
# [[animale]]
===Traduzione===
{{Trad1|animale}}
:*{{ar}}: [[كَلْب]] (kalb) ''m''
:*[[romagnolo]]: [[chèn]] ''m''""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "word": "كَلْب",
                    "lang_code": "ar",
                    "lang": "arabo",
                    "roman": "kalb",
                    "tags": ["masculine"],
                    "sense": "animale",
                },
                {
                    "word": "chèn",
                    "lang_code": "rgn",
                    "lang": "romagnolo",
                    "tags": ["masculine"],
                    "sense": "animale",
                },
            ],
        )

    def test_no_lang_name_template(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "Italia",
            """== {{-it-}} ==
===Nome proprio===
# stato
===Traduzione===
:* võro: [[Itaalia]]""",
        )
        self.assertEqual(
            data[0]["translations"],
            [{"word": "Itaalia", "lang_code": "vro", "lang": "võro"}],
        )

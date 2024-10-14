from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlSound(TestCase):
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

    def test_normal_layout(self):
        self.wxr.wtp.add_page("Sjabloon:ara", 10, "Arabisch")
        self.wxr.wtp.add_page("Sjabloon:zho", 10, "Chinees")
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
====Zelfstandig naamwoord====
# zoogdier
=====Vertalingen=====
{{trans-top|1. ''Canis lupus familiaris'', een zoogdier dat tot huisdier getemd is}}
* {{ara}}: {{trad|ar|كلب}} (kalb) {{m}}
* {{zho}}: {{trad|zh|狗}} (gǒu, gou, [[gou3]]); {{trad|zh|犬}} (quǎn, quan, quan3)""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "word": "كلب",
                    "lang": "Arabisch",
                    "lang_code": "ar",
                    "roman": "kalb",
                    "tags": ["masculine"],
                    "sense": "Canis lupus familiaris, een zoogdier dat tot huisdier getemd is",
                    "sense_index": 1,
                },
                {
                    "word": "狗",
                    "lang": "Chinees",
                    "lang_code": "zh",
                    "roman": "gǒu, gou, gou3",
                    "sense": "Canis lupus familiaris, een zoogdier dat tot huisdier getemd is",
                    "sense_index": 1,
                },
                {
                    "word": "犬",
                    "lang": "Chinees",
                    "lang_code": "zh",
                    "roman": "quǎn, quan, quan3",
                    "sense": "Canis lupus familiaris, een zoogdier dat tot huisdier getemd is",
                    "sense_index": 1,
                },
            ],
        )

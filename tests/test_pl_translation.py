from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPlTranslation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_simple_list(self):
        self.wxr.wtp.add_page("Szablon:m", 10, "m")
        page_data = parse_page(
            self.wxr,
            "słownik",
            """== słownik ({{język polski}}) ==
===znaczenia===
''rzeczownik, rodzaj męskorzeczowy''
: (1.1) [[zbiór]]

===tłumaczenia===
* albański: (1.1) [[fjalor]] {{m}} (fyalór)
* chiński standardowy: (1.1) [[字典]] (zìdiǎn), [[词典]] (cídiǎn); (1.2) [[词典]] (cídiǎn)""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "lang": "albański",
                    "lang_code": "sq",
                    "word": "fjalor",
                    "sense_index": "1.1",
                    "tags": ["masculine"],
                    "roman": "fyalór",
                },
                {
                    "lang": "chiński standardowy",
                    "lang_code": "unknown",
                    "word": "字典",
                    "sense_index": "1.1",
                    "roman": "zìdiǎn",
                },
                {
                    "lang": "chiński standardowy",
                    "lang_code": "unknown",
                    "word": "词典",
                    "sense_index": "1.1",
                    "roman": "cídiǎn",
                },
                {
                    "lang": "chiński standardowy",
                    "lang_code": "unknown",
                    "word": "词典",
                    "sense_index": "1.2",
                    "roman": "cídiǎn",
                },
            ],
        )

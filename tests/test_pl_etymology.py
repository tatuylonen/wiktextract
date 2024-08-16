from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPlEtymology(TestCase):
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

    def test_dog(self):
        # etymology texts should be added to both sense data
        self.wxr.wtp.add_page(
            "Szablon:język angielski",
            10,
            '<span class="lang-code primary-lang-code lang-code-en" id="en">[[Słownik języka angielskiego|język angielski]]</span>',
        )
        page_data = parse_page(
            self.wxr,
            "dog",
            """== dog ({{język angielski}}) ==
===znaczenia===
''rzeczownik policzalny''
: (1.1) {{zool}} [[pies]]
''rzeczownik niepoliczalny''
: (2.1) {{kulin}} [[psi]]e [[mięso]]

===etymologia===
: Od średnioang. dogge
: por. szkoc. dug → pies""",
        )
        self.assertEqual(len(page_data), 2)
        self.assertEqual(
            page_data[0]["etymology_texts"], page_data[1]["etymology_texts"]
        )
        self.assertEqual(
            page_data[0]["etymology_texts"],
            ["Od średnioang. dogge", "por. szkoc. dug → pies"],
        )

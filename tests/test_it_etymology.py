from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItEtymology(TestCase):
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

    def test_quote_template(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
# {{Term|mammalogia|it}} [[animale]]
===Etimologia / Derivazione===
dal latino canis
====Citazione====
{{Quote
|Cane affamato non teme bastone
|[[q:Giovanni Verga|Giovanni Verga]]}}""",
        )
        self.assertEqual(data[0]["etymology_texts"], ["dal latino canis"])
        self.assertEqual(
            data[0]["etymology_examples"],
            [
                {
                    "text": "Cane affamato non teme bastone",
                    "ref": "Giovanni Verga",
                }
            ],
        )

    def test_list(self):
        self.wxr.wtp.add_page("Template:-la-", 10, "Latino")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-la-}} ==
===Sostantivo, forma flessa===
# ablativo singolare di canis
===Etimologia / Derivazione===
* (sostantivo) vedi [[canis#Latino|canis]]
* (voce verbale) vedi [[cano#Latino|canō]]""",
        )
        self.assertEqual(
            data[0]["etymology_texts"],
            ["(sostantivo) vedi canis", "(voce verbale) vedi canō"],
        )

    def test_space(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "zirconio",
            """== {{-it-}} ==
===Sostantivo===
#  [[elemento chimico]] [[solido]]
===Etimologia / Derivazione===
dall'[[arabo]] ''zarkûn'', derivato dal [[persiano]] ''zargûn'', [[colore]] dell'[[oro]]""",
        )
        self.assertEqual(
            data[0]["etymology_texts"],
            [
                "dall'arabo zarkûn, derivato dal persiano zargûn, colore dell'oro"
            ],
        )

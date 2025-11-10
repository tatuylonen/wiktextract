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

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

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
                {
                    "word": "forte",
                    "tags": ["figuratively"],
                    "raw_tags": ["di freddo"],
                },
                {"word": "intenso"},
            ],
        )

    def test_text_tag(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
# [[animale]]
===Iperonimi===
* (dominio) [[eucariote]]""",
        )
        self.assertEqual(
            data[0]["hypernyms"],
            [{"word": "eucariote", "raw_tags": ["dominio"]}],
        )
        data = parse_page(
            self.wxr,
            "areopago",
            """== {{-it-}} ==
===Sostantivo===
# nell'[[antichità]] il [[tribunale]] [[supremo]] di [[Atene]]
===Sinonimi===
* (''consesso'') [[consiglio]]""",
        )
        self.assertEqual(data[0]["synonyms"], [{"word": "consiglio"}])

    def test_proverbs(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
# [[animale]]
===Proverbi e modi di dire===
* ''Menare il '''can''' per l'aia'': tergiversare, prendere tempo""",
        )
        self.assertEqual(
            data[0]["proverbs"],
            [
                {
                    "word": "Menare il can per l'aia",
                    "sense": "tergiversare, prendere tempo",
                }
            ],
        )

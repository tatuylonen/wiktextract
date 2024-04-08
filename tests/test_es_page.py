import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestESPage(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(
                dump_file_lang_code="es", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_es_parse_entries(self):
        """
        Writes data affecting multiple entries to all affected WordEntry objects.
        https://es.wiktionary.org/wiki/love
        """
        page_data = parse_page(
            self.wxr,
            "love",
            """== {{lengua|en}} ==
{{pron-graf|leng=en|fone=lʌv}}
=== {{verbo|en}} ===
=== {{sustantivo|en}} ===
""",
        )
        self.assertEqual(len(page_data), 2)
        self.assertEqual(page_data[0]["sounds"], page_data[1]["sounds"])

    def test_gloss_under_etymology_section(self):
        # abnormal layout
        # https://es.wiktionary.org/wiki/agüero
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page("Plantilla:etimología", 10, "Del latín *agurium")
        self.wxr.wtp.add_page(
            "Plantilla:sustantivo masculino", 10, "Sustantivo masculino"
        )
        page_data = parse_page(
            self.wxr,
            "agüero",
            """=={{lengua|ES}}==
===Etimología===
{{etimología|la|*agurium}}, variante del clásico augurium.
===={{sustantivo masculino|es}}====
;1: Presagio que algunos pueblos [[gentil]]es sacaban
""",
        )
        self.assertEqual(
            page_data[0]["etymology_text"],
            "Del latín *agurium, variante del clásico augurium.",
        )
        self.assertEqual(
            page_data[0]["senses"][0]["glosses"],
            ["Presagio que algunos pueblos gentiles sacaban"],
        )

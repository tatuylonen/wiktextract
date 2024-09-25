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
        https://es.wiktionary.org/wiki/sorabo
        """  # noqa:E501
        self.wxr.wtp.add_page(
            "Plantilla:pron-graf",
            10,
            """{|
|<span>love</span>
|-
|'''pronunciación''' (AFI)
|[lʌv]<br/>
|}""",
        )
        self.wxr.wtp.add_page(
            "Plantilla:lengua", 10, "Inglés[[Categoría:Inglés]]"
        )
        self.wxr.wtp.add_page(
            "Plantilla:verbo", 10, "Verbo[[Categoría:EN:Verbos]]"
        )
        self.wxr.wtp.add_page(
            "Plantilla:sustantivo", 10, "Sustantivo[[Categoría:EN:Sustantivos]]"
        )
        page_data = parse_page(
            self.wxr,
            "love",
            """== {{lengua|en}} ==
{{pron-graf|leng=en|fone=lʌv}}
[[Categoría:ES:Gentilicios]]
=== {{verbo|en}} ===
=== {{sustantivo|en}} ===
""",
        )
        self.assertEqual(len(page_data), 2)
        self.assertEqual(page_data[0]["sounds"], page_data[1]["sounds"])
        self.assertEqual(
            page_data[0]["categories"],
            ["Inglés", "ES:Gentilicios", "EN:Verbos"],
        )
        self.assertEqual(
            page_data[1]["categories"],
            ["Inglés", "ES:Gentilicios", "EN:Sustantivos"],
        )

    def test_gloss_under_etymology_section(self):
        # abnormal layout
        # https://es.wiktionary.org/wiki/agüero
        # https://es.wiktionary.org/wiki/paya
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page("Plantilla:etimología", 10, "Del latín *agurium")
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page(
            "Plantilla:sustantivo masculino y femenino",
            10,
            "Sustantivo femenino y masculino",
        )
        page_data = parse_page(
            self.wxr,
            "agüero",
            """=={{lengua|ES}}==
===Etimología===
{{etimología|la|*agurium}}, variante del clásico augurium.
==== {{sustantivo masculino y femenino|es}} ====
;2: Persona originaria de un pueblo amerindio de origen chibcha que habita Honduras.
""",  # noqa:E501
        )
        self.assertEqual(
            page_data[0]["etymology_text"],
            "Del latín *agurium, variante del clásico augurium.",
        )
        self.assertEqual(
            page_data[0]["senses"][0]["glosses"],
            [
                "Persona originaria de un pueblo amerindio de origen "
                "chibcha que habita Honduras."
            ],
        )
        self.assertEqual(page_data[0]["pos"], "noun")

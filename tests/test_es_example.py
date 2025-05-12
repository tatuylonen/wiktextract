import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestESExample(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(
                dump_file_lang_code="es", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_ejemplo_template(self):
        self.wxr.wtp.add_page(
            "Plantilla:ejemplo",
            10,
            """:*'''Ejemplo:'''&nbsp;<span class='mw-collapsible mw-collapsed'><blockquote><span class='cita'>And He has on His robe and on His thigh a name written: KING OF KINGS AND '''LORD''' OF LORDS.</span><span class='trad'>''→&nbsp;''Y en su vestidura y en su muslo tiene escrito este nombre: REY DE REYES Y '''SEÑOR''' DE SEÑORES.</span><span class='ref'>''<span class='plainlinks'>[https://www.biblegateway.com/passage/?search=Apocalipsis+19&version=NKJV Bible]</span> Revelation 19:16''. Versión: New King James. <br>Traducción: ''<span class='plainlinks'>[https://www.biblegateway.com/passage/?search=Apocalipsis+19&version=RVR1960 Biblia]</span> Apocalipsis 19:16''. Versión: Reina-Valera 1995. </span></blockquote></span>""",
        )
        page_data = parse_page(
            self.wxr,
            "lord",
            """== {{lengua|en}} ==
=== Etimología 1 ===
==== {{sustantivo|en}} ====
;6: {{plm|señor}} (persona que gobierna).
{{ejemplo|And He has on His robe and on His thigh a name written: KING OF KINGS AND '''LORD''' OF LORDS.|c=libro|v=New King James|t=Bible|pasaje=Revelation 19:16|u=https://www.biblegateway.com/passage/?search=Apocalipsis+19&version=NKJV|trad=Y en su vestidura y en su muslo tiene escrito este nombre: REY DE REYES Y '''SEÑOR''' DE SEÑORES.|tradc=libro|tradv=Reina-Valera 1995|tradt=Biblia|tradpasaje=Apocalipsis 19:16|tradu=https://www.biblegateway.com/passage/?search=Apocalipsis+19&version=RVR1960}}""",
        )
        dump_data = page_data[0]["senses"][0]["examples"]
        self.assertEqual(
            dump_data,
            [
                {
                    "text": "And He has on His robe and on His thigh a name written: KING OF KINGS AND LORD OF LORDS.",
                    "bold_text_offsets": [(74, 78), (82, 86)],
                    "translation": "Y en su vestidura y en su muslo tiene escrito este nombre: REY DE REYES Y SEÑOR DE SEÑORES.",
                    "ref": "Bible Revelation 19:16. Versión: New King James.\nTraducción: Biblia Apocalipsis 19:16. Versión: Reina-Valera 1995.",
                }
            ],
        )

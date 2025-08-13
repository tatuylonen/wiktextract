import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestESEtymology(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(
                capture_language_codes=None, dump_file_lang_code="es"
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_same_level_as_pos(self):
        self.wxr.wtp.add_page(
            "Plantilla:etimología",
            10,
            "Del griego antiguo [[ἀνθρωποειδής#Griego antiguo|''ἀνθρωποειδής'']]",
        )
        page_data = parse_page(
            self.wxr,
            "antropoide",
            """== {{lengua|es}} ==
=== Etimología ===
{{etimología|grc|ἀνθρωποειδής}}

=== {{adjetivo|es}} ===

;1: Que recuerda""",
        )
        self.assertEqual(
            page_data[0]["etymology_text"], "Del griego antiguo ἀνθρωποειδής"
        )
        self.assertEqual(
            page_data[0]["senses"],
            [{"glosses": ["Que recuerda"], "sense_index": "1"}],
        )

    def test_not_share_etymology_data_among_same_level_pos(self):
        self.wxr.wtp.add_page(
            "Plantilla:etimología",
            10,
            "Del setsuana [[pula#Setsuana|''pula'']][[Categoría:ES:Palabras provenientes del setsuana|PULA]], del sotho norteño [[pula#Sotho norteño|''pula'']][[Categoría:ES:Palabras provenientes del sotho norteño|PULA]] y del sesoto [[pula#Sesoto|''pula'']] ('lluvia')[[Categoría:ES:Palabras provenientes del sesoto|PULA]]",
        )
        page_data = parse_page(
            self.wxr,
            "pula",
            """== {{lengua|es}} ==
=== Etimología ===
{{etimología|tn|pula||nso|pula||st|pula|glosa3=lluvia}}.
==== {{sustantivo femenino|es}} ====
;1 {{csem|monedas}}: {{plm|unidad}} [[monetario|monetaria]] de Botswana.

=== Forma flexiva ===
==== Forma verbal ====
;1: {{f.v|pulir|m=imp|p=usted}}.""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            [
                "ES:Palabras provenientes del setsuana",
                "ES:Palabras provenientes del sotho norteño",
                "ES:Palabras provenientes del sesoto",
            ],
        )
        self.assertEqual(
            page_data[0]["etymology_text"],
            "Del setsuana pula, del sotho norteño pula y del sesoto pula ('lluvia').",
        )
        self.assertTrue("categories" not in page_data[1])
        self.assertTrue("etymology_text" not in page_data[1])

    def test_missing_etymology_data(self):
        self.wxr.wtp.add_page(
            "Plantilla:etimología",
            10,
            "<span>''Si puedes, incorpórala: [[Plantilla:etimología|ver cómo]]''[[Categoría:DE:Palabras de etimología sin precisar]]</span>.",
        )
        page_data = parse_page(
            self.wxr,
            "Schreck",
            """== {{lengua|de}} ==
=== Etimología 1 ===
{{etimología|leng=de}}.
==== {{sustantivo masculino|de}} ====
;1: Miedo""",
        )
        self.assertEqual(
            page_data[0]["categories"],
            ["DE:Palabras de etimología sin precisar"],
        )
        self.assertTrue("etymology_text" not in page_data[0])

    def test_attestation(self):
        self.wxr.wtp.add_page(
            "Plantilla:datación",
            10,
            "Atestiguado desde el siglo XIII[[Categoría:EN:Palabras documentadas desde el siglo XIII]]",
        )
        data = parse_page(
            self.wxr,
            "change",
            """== {{lengua|en}} ==
=== Etimología ===
Del inglés medio changen. {{datación|leng=en|XIII}}.

Desplazó a la palabra inglesa nativa wenden.
==== {{sustantivo masculino|de}} ====
;1: Cambio, [[modificación]], [[transformación]].""",
        )
        self.assertEqual(data[0]["attestations"], [{"date": "XIII"}])
        self.assertEqual(
            data[0]["etymology_text"],
            "Del inglés medio changen. Atestiguado desde el siglo XIII.\nDesplazó a la palabra inglesa nativa wenden.",
        )
        self.assertEqual(
            data[0]["categories"],
            ["EN:Palabras documentadas desde el siglo XIII"],
        )

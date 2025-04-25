import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestESGloss(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(
                dump_file_lang_code="es", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_gloss_topics(self):
        self.wxr.wtp.start_page("helicóptero")
        self.wxr.wtp.add_page(
            "Plantilla:csem",
            10,
            "Aeronáutica, vehículos[[Categoría:ES:Aeronáutica|HELICOPTERO]][[Categoría:ES:Vehículos|HELICOPTERO]]",
        )
        page_data = parse_page(
            self.wxr,
            "helicóptero",
            """== {{lengua|es}} ==
=== {{sustantivo masculino|es}} ===
;1 {{csem|aeronáutica|vehículos}}: Vehículo para desplazarse por el aire,""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["Vehículo para desplazarse por el aire,"],
                    "sense_index": "1",
                    "topics": ["aeronautics", "vehicles"],
                    "categories": ["ES:Aeronáutica", "ES:Vehículos"],
                }
            ],
        )

    def test_uso_ambito_templates(self):
        self.wxr.wtp.add_page(
            "Plantilla:uso",
            10,
            ":*'''Uso:''' coloquial, despectivo[[Categoría:ES:Términos coloquiales|DOMINGO]][[Categoría:ES:Términos despectivos|DOMINGO]]",
        )
        page_data = parse_page(
            self.wxr,
            "domingo",
            """== {{lengua|es}} ==
=== Etimología 2 ===
==== {{sustantivo masculino|es}} ====
;1: Marido dominado por
{{uso|coloquial|despectivo}}
{{ámbito|Bolivia}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": [
                        "ES:Términos coloquiales",
                        "ES:Términos despectivos",
                    ],
                    "tags": ["colloquial", "derogatory", "Bolivia"],
                    "glosses": ["Marido dominado por"],
                    "sense_index": "1",
                }
            ],
        )

    def test_form_of(self):
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Inglés")
        self.wxr.wtp.add_page(
            "Plantilla:forma sustantivo plural", 10, "Forma del plural de apple"
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "apples",
                """== {{lengua|en}} ==
=== Forma sustantiva ===

;1: {{forma sustantivo plural|leng=en|apple}}.""",
            ),
            [
                {
                    "lang": "Inglés",
                    "lang_code": "en",
                    "pos": "noun",
                    "pos_title": "Forma sustantiva",
                    "senses": [
                        {
                            "glosses": ["Forma del plural de apple."],
                            "form_of": [{"word": "apple"}],
                            "sense_index": "1",
                        }
                    ],
                    "tags": ["form-of"],
                    "word": "apples",
                }
            ],
        )

    def test_forma_verbo(self):
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page(
            "Plantilla:f.v",
            10,
            "Primera persona del singular (yo) del presente de indicativo de amigar o de amigarse",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "amigo",
                """== {{lengua|es}} ==
=== Forma flexiva ===

==== Forma verbal ====
;1: {{f.v|amigar|yo|presente|indicativo|pronominal=s}}.""",
            ),
            [
                {
                    "lang": "Español",
                    "lang_code": "es",
                    "pos": "verb",
                    "pos_title": "Forma verbal",
                    "senses": [
                        {
                            "glosses": [
                                "Primera persona del singular (yo) del "
                                "presente de indicativo de amigar "
                                "o de amigarse."
                            ],
                            "form_of": [
                                {"word": "amigar"},
                                {"word": "amigarse"},
                            ],
                            "sense_index": "1",
                            "tags": ["form-of"],
                        }
                    ],
                    "tags": ["form-of"],
                    "word": "amigo",
                }
            ],
        )

    def test_no_list(self):
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Bretón")
        self.wxr.wtp.add_page("Plantilla:sufijo", 10, "Sufijo verbal")
        self.assertEqual(
            parse_page(
                self.wxr,
                "-fe",
                """== {{lengua|br}} ==
==== {{sufijo|br|verbo}} ====
[[desinencia]] de la tercera persona singular del [[condicional]]""",
            ),
            [
                {
                    "lang": "Bretón",
                    "lang_code": "br",
                    "pos": "suffix",
                    "pos_title": "Sufijo verbal",
                    "senses": [
                        {
                            "glosses": [
                                "desinencia de la tercera persona singular del condicional"
                            ],
                        }
                    ],
                    "word": "-fe",
                }
            ],
        )

    def test_forma_verbo_another_section_order(self):
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page(
            "Plantilla:forma verbo",
            10,
            """<span class="definicion-impropia">[[primera persona#Español|Primera persona]] del singular&nbsp;(yo)&nbsp;del <span style="" class="">[[presente#Español|presente]]</span>&nbsp;de <span style="" class="">[[modo indicativo#Español|indicativo]]</span>&nbsp;de&nbsp;</span><span style="" class="">[[caminar#Español|caminar]]</span>[[Categoría:ES:Formas verbales en indicativo]]""",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "camino",
                """== {{lengua|es}} ==
=== Forma verbal ===
==== Forma flexiva ====
;1: {{forma verbo|caminar|p=1s|t=presente|m=indicativo}}""",
            ),
            [
                {
                    "lang": "Español",
                    "lang_code": "es",
                    "pos": "verb",
                    "pos_title": "Forma flexiva",
                    "senses": [
                        {
                            "categories": ["ES:Formas verbales en indicativo"],
                            "glosses": [
                                "Primera persona del singular (yo) del presente de indicativo de caminar"
                            ],
                            "form_of": [{"word": "caminar"}],
                            "sense_index": "1",
                        }
                    ],
                    "tags": ["form-of"],
                    "word": "camino",
                }
            ],
        )

    def test_nested_list(self):
        self.wxr.wtp.add_page(
            "Plantilla:csem",
            10,
            "Sentimientos[[Categoría:LA:Sentimientos|IRA]]",
        )
        self.wxr.wtp.add_page(
            "Plantilla:uso",
            10,
            ":*'''Uso:''' literario[[Categoría:LA:Términos literarios|IRA]]",
        )
        page_data = parse_page(
            self.wxr,
            "ira",
            """== {{lengua|la}} ==
==== {{sustantivo femenino|la}} ====
;1 {{csem|leng=la|sentimientos}}: Ira, [[furia]], [[rabia]], [[indignación]].
:;d: Dícese de armas o similar.
{{uso|leng=la|poético}}.
:;e: Frenesí.
;2: Sentimientos de [[desagrado]] mutuo, de [[hostilidad]] mutua.""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["LA:Sentimientos"],
                    "glosses": ["Ira, furia, rabia, indignación."],
                    "sense_index": "1",
                    "raw_tags": ["Sentimientos"],
                },
                {
                    "categories": ["LA:Sentimientos", "LA:Términos literarios"],
                    "glosses": [
                        "Ira, furia, rabia, indignación.",
                        "Dícese de armas o similar.",
                    ],
                    "sense_index": "d",
                    "tags": ["literary"],
                    "raw_tags": ["Sentimientos"],
                },
                {
                    "categories": ["LA:Sentimientos"],
                    "glosses": ["Ira, furia, rabia, indignación.", "Frenesí."],
                    "sense_index": "e",
                    "raw_tags": ["Sentimientos"],
                },
                {
                    "glosses": [
                        "Sentimientos de desagrado mutuo, de hostilidad mutua."
                    ],
                    "sense_index": "2",
                },
            ],
        )

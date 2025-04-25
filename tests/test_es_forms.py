from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.inflection import process_inflect_template
from wiktextract.extractor.es.models import WordEntry
from wiktextract.extractor.es.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestESInflection(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(
                dump_file_lang_code="es", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_simple_inflect_template(self):
        self.wxr.wtp.start_page("diccionario")
        self.wxr.wtp.add_page(
            "Plantilla:inflect.es.sust.reg",
            10,
            """{|
! Singular
! Plural
|-
| diccionario
| <span style="" class="">[[diccionarios#Español|diccionarios]]</span>
|}""",
        )
        root = self.wxr.wtp.parse("{{inflect.es.sust.reg|diccionario}}")
        data = WordEntry(
            word="diccionario", pos="noun", lang="Español", lang_code="es"
        )
        process_inflect_template(self.wxr, data, root.children[0])
        self.assertEqual(
            data.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "diccionario", "tags": ["singular"]},
                {"form": "diccionarios", "tags": ["plural"]},
            ],
        )

    def test_es_adj_inflect_template(self):
        self.wxr.wtp.start_page("feliz")
        self.wxr.wtp.add_page(
            "Plantilla:inflect.es.adj.no-género-cons",
            10,
            """{| class="inflection-table"
!
! Singular
! Plural
! [[superlativo|Superlativo]]
|-
! Masculino
| feliz
| <span style="" class="">[[felices#Español|felices]]</span>
| rowspan="2" |<span style="" class="">[[felicísimo#Español|felicísimo]]</span>
|-
! Femenino
| feliz
| <span style="" class="">[[felices#Español|felices]]</span>
|}""",
        )
        root = self.wxr.wtp.parse(
            "{{inflect.es.adj.no-género-cons|feli|z|sup=felicísimo}}"
        )
        data = WordEntry(
            word="feliz", pos="adj", lang="Español", lang_code="es"
        )
        process_inflect_template(self.wxr, data, root.children[0])
        self.assertEqual(
            data.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "feliz", "tags": ["masculine", "singular"]},
                {"form": "felices", "tags": ["masculine", "plural"]},
                {
                    "form": "felicísimo",
                    "tags": ["masculine", "superlative", "feminine"],
                },
                {"form": "feliz", "tags": ["feminine", "singular"]},
                {"form": "felices", "tags": ["feminine", "plural"]},
            ],
        )

    def test_alt_form_section(self):
        page_data = parse_page(
            self.wxr,
            "kóutua",
            """== {{lengua|yag}} ==
=== Formas alternativas ===
koutu, koute.
=== Pronombre interrogativo ===
;1: Qué.""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "koutu", "tags": ["alt-of"]},
                {"form": "koute", "tags": ["alt-of"]},
            ],
        )
        page_data = parse_page(
            self.wxr,
            "sina",
            """== {{lengua|yag}} ==
=== Formas alternativas ===
[[sin]]
=== Pronombre interrogativo ===
;1: Tu""",
        )
        self.assertEqual(
            page_data[0]["forms"], [{"form": "sin", "tags": ["alt-of"]}]
        )

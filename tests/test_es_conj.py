from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestESConjugation(TestCase):
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

    def test_es_v(self):
        self.wxr.wtp.start_page("dar")
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page(
            "Plantilla:verbo transitivo", 10, "Verbo transitivo"
        )
        self.wxr.wtp.add_page(
            "Plantilla:verbo intransitivo", 10, "Verbo intransitivo"
        )
        self.wxr.wtp.add_page(
            "Plantilla:es.v",
            10,
            """<div>
{|
|-
! colspan=8 | Formas no personales (verboides)
|-
! Infinitivo
| colspan=3 | dar
| colspan=4 | haber [[dado|dado]]
|-
! colspan=8 | Formas personales
|-
! colspan=8 | Modo subjuntivo
|-
!
! que yo
|-
! Pretérito imperfecto
|  | <span class='movil'>que yo&ensp;</span> [[diera|diera]],  [[diese|diese]]
|}[[Categoría:ES:Verbos del paradigma dar]][[Categoría:ES:Verbos irregulares]]""",
        )
        page_data = parse_page(
            self.wxr,
            "dar",
            """== {{lengua|es}} ==
=== Etimología 1 ===
etymology text
==== {{verbo transitivo|es}} ====
;1: Traspasar algo a otra persona de forma [[gratuito|gratuita]].
==== {{verbo intransitivo|es}} ====
;12: Asestar golpes.
==== Conjugación ====
{{es.v}}""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "haber dado", "tags": ["impersonal", "infinitive"]},
                {
                    "form": "diera",
                    "tags": [
                        "first-person",
                        "singular",
                        "subjunctive",
                        "past",
                        "imperfect",
                    ],
                    "raw_tags": ["que yo"],
                },
                {
                    "form": "diese",
                    "tags": [
                        "first-person",
                        "singular",
                        "subjunctive",
                        "past",
                        "imperfect",
                    ],
                    "raw_tags": ["que yo"],
                },
            ],
        )
        self.assertEqual(page_data[0]["forms"], page_data[1]["forms"])
        self.assertEqual(
            page_data[0]["categories"],
            ["ES:Verbos del paradigma dar", "ES:Verbos irregulares"],
        )
        self.assertEqual(page_data[0]["categories"], page_data[1]["categories"])

    def test_only_add_conj_data_to_verb(self):
        self.wxr.wtp.start_page("acontecer")
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page(
            "Plantilla:es.v",
            10,
            """<div>
<div>'''Conjugación de ''acontecer'''''&emsp;&emsp;paradigma: parecer (regular)&nbsp;[<span class='fakelinks down'>▲</span><span class='fakelinks up'>▼</span>]</div>
<div>
{|
|-
! colspan=3 | Formas no personales (verboides)
|-
! Infinitivo
| colspan=0 | acontecer
| colspan=2 | haber [[acontecido|acontecido]]
|}
</div>
</div>""",
        )
        page_data = parse_page(
            self.wxr,
            "acontecer",
            """== {{lengua|es}} ==
=== {{verbo|es|intransitivo|impersonal}} ===
;1: Tener lugar un [[hecho]], [[evento]] o [[suceso]].
=== {{sustantivo masculino|es}} ===
{{inflect.es.sust.reg-cons}}
;2: {{plm|evento}}, [[acción]] o [[suceso]] que tiene lugar en un momento dado.
=== Conjugación ===
{{es.v|impersonal=36}}""",
        )
        self.assertTrue("forms" in page_data[0])
        self.assertTrue("forms" not in page_data[1])

    def test_sup_tag(self):
        self.wxr.wtp.add_page(
            "Plantilla:es.v",
            10,
            """<div>
<div>'''Conjugación de ''adscribir'''''&emsp;&emsp;paradigma: inscribir (irregular)&nbsp;[<span class='fakelinks down'>▲</span><span class='fakelinks up'>▼</span>]</div>
<div class='flex mw-collapsible-content'>
{| class='flex wikitable'
|- style='font-weight:bold;text-align:center;background:WhiteSmoke'
! colspan=8 style='background:WhiteSmoke' | Formas no personales (verboides)
|-
! style='font-weight:bold;text-align:center;background:WhiteSmoke' | Participio
| colspan=7 | [[adscrito|<span style='color:DarkGoldenrod; font-weight: bold;'>adscrito</span>]], [[adscripto|<span style='color:DarkGoldenrod; font-weight: bold;'>adscripto</span>]]<sup>ARG/URU</sup>
|}
</div>
</div>""",
        )
        page_data = parse_page(
            self.wxr,
            "adscribir",
            """== {{lengua|es}} ==
=== {{verbo transitivo|es}} ===
;1: gloss
=== Conjugación ===
{{es.v}}""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "adscrito", "tags": ["impersonal", "participle"]},
                {
                    "form": "adscripto",
                    "tags": [
                        "impersonal",
                        "participle",
                        "Argentina",
                        "Uruguay",
                    ],
                },
            ],
        )

    def test_en_v(self):
        self.wxr.wtp.add_page(
            "Plantilla:en.v",
            10,
            """<div class='flex mw-collapsible-content'>
{| class='flex wikitable' width='100%'
! colspan=5 | Formas personales
|-
! colspan=5 | Modo indicativo
|-
!
! I
! you
|-
! Presente
| <span class='movil'>I&ensp;</span>dog
| <span class='movil'>you&ensp;</span>dog, [[doggest|doggest]]<sup>†</sup>
|}
</div>""",
        )
        data = parse_page(
            self.wxr,
            "dog",
            """== {{lengua|en}} ==
=== {{verbo transitivo|en}} ===
;2: Perseguir con [[perro]]s
=== Conjugación ===
{{en.v}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "doggest",
                    "raw_tags": ["you"],
                    "tags": [
                        "second-person",
                        "indicative",
                        "present",
                        "archaic",
                    ],
                }
            ],
        )

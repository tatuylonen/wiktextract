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
                {"form": "dar", "tags": ["impersonal", "infinitive"]},
                {"form": "haber dado", "tags": ["impersonal", "infinitive"]},
                {
                    "form": "diera",
                    "tags": ["subjunctive", "past", "imperfect"],
                    "raw_tags": ["que yo"],
                },
                {
                    "form": "diese",
                    "tags": ["subjunctive", "past", "imperfect"],
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

    def test_es_v_conj(self):
        self.wxr.wtp.start_page("cantar")
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page(
            "Plantilla:es.v.conj.ar",
            10,
            """{|
|+ class="normal" |<big> '''Flexión de ''cantar''''' </big><span>
primera conjugación,&nbsp;regular</span>
! class="vertical" colspan="7" |Formas no personales
|-
! class="vertical" colspan="1" width="300px" |
! class="vertical" colspan="3" |Simples
! class="vertical" colspan="3" |Compuestas
|-
! colspan="1"|[[infinitivo|Infinitivo]]
| colspan="3"|cantar
| colspan="3"|haber <span style="" class="">[[cantado#Español|cantado]]</span>
|-
! class="vertical" colspan="7" |Formas personales
|-
! colspan="1" style="text-align:right; padding-right:10px" |[[número]]:
! class="vertical" colspan="3"|singular
! class="vertical" colspan="3"|plural
|-
! colspan="1"  style="text-align:right; padding-right:10px" |[[persona]]:
! class="vertical"| [[primera persona|primera]]
! class="vertical"| [[segunda persona|segunda]]
! class="vertical"| [[tercera persona|tercera]]
! class="vertical"| [[primera persona|primera]]
! class="vertical"| [[segunda persona|segunda]]
! class="vertical"| [[tercera persona|tercera]]
|-
! class="vertical" style="background:#c0e4c0; color:#000" colspan="1"|[[modo subjuntivo|Modo subjuntivo]]
! class="vertical" rowspan="2" style="background:#c0e4c0; color:#000"|yo
! class="vertical" rowspan="2" style="background:#c0e4c0; color:#000"|tú <br/>vos<sup style="color:red">2</sup>
! class="vertical" rowspan="2" style="background:#c0e4c0; color:#000"|él / ella<br/>usted<sup style="color:red">1</sup>
! class="vertical" rowspan="2" style="background:#c0e4c0; color:#000"|nosotros<br/>nosotras
! class="vertical" rowspan="2" style="background:#c0e4c0; color:#000"|vosotros<br/>vosotras
! class="vertical" rowspan="2" style="background:#c0e4c0; color:#000"|ellos / ellas<br/>ustedes<sup style="color:red">1</sup>
|-
! style="background:#c0e4c0; padding-left:5px; color:#000; font-size:80%; text-align:center" | Tiempos simples
|-
! style="background:#c0e4c0; padding-left:5px; color:#000" rowspan="2"|[[pretérito imperfecto#Español|Pretérito imperfecto]]&nbsp;&nbsp;<small>''o''</small>&nbsp;&nbsp;[[pretérito#Español|Pretérito]]
|| <span style="" class="">[[cantara#Español|cantara]]</span>
|-
|| <span style="" class="">[[cantase#Español|cantase]]</span>
|-
! style="background:#c0e4c0; padding-left:5px; color:#000; font-size:80%; text-align:center"|Tiempos compuestos
|-
! style="background:#c0e4c0; padding-left:5px; color:#000"|[[pretérito perfecto#Español|Pretérito perfecto]]&nbsp;&nbsp;<small>''o''</small>&nbsp;&nbsp;[[antepresente#Español|Antepresente]]
|| haya <span style="" class="">[[cantado#Español|cantado]]</span>
|-
! class="vertical" style="background:#e4d4c0; color:#000" colspan="1"|[[modo imperativo|Modo imperativo]]
! class="vertical" style="background:#e4d4c0; color:#000"|&nbsp;
! class="vertical" style="background:#e4d4c0; color:#000"|tú <br/> vos
! class="vertical" style="background:#e4d4c0; color:#000"|usted<sup style="color:red">1</sup>
! class="vertical" style="background:#e4d4c0; color:#000"|nosotros <br/> nosotras
! class="vertical" style="background:#e4d4c0; color:#000"|vosotros <br/> vosotras
! class="vertical" style="background:#e4d4c0; color:#000"|ustedes<sup style="color:red">1</sup>
|-
! colspan="2" style="background:#e4d4c0; color:#000; padding-left:5px"|Afirmativo
|| <span style="" class="">[[canta#Español|canta]]</span><sup><sup>tú</sup></sup><br/><span style="" class="">[[cantá#Español|cantá]]</span><sup><sup>vos</sup></sup>
|-
| colspan="7" style="padding-left:5px; background-color:#F0FFFF; color:#000;font-size:90%" | <sup style="color:red">1</sup> [[usted|Usted]] y [[ustedes]] son pronombres de [[segunda persona]], pero emplean las formas verbales de la [[tercera persona|tercera]].<br><sup style="color:red">2</sup> Las formas de «[[vos]]» [[w:Voseo|varían]] en diversas zonas de América. El voseo [[w:Español rioplatense|rioplatense]] prefiere para el subjuntivo las formas de «tú».
|}[[Categoría:ES:Verbos]][[Categoría:ES:Verbos regulares]][[Categoría:ES:Primera conjugación]]""",
        )
        page_data = parse_page(
            self.wxr,
            "cantar",
            """== {{lengua|es}} ==
=== Etimología 1 ===
etymology text
==== {{verbo transitivo|es}} ====
;1: Usar la voz para emitir sonido melodioso, puede ser pronunciando palabras.
==== Conjugación ====
{{es.v.conj.ar|cant}}""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "cantar",
                    "tags": ["impersonal", "simple", "infinitive"],
                },
                {
                    "form": "haber cantado",
                    "tags": ["impersonal", "compound", "infinitive"],
                },
                {
                    "form": "cantara",
                    "tags": [
                        "personal",
                        "singular",
                        "first-person",
                        "subjunctive",
                        "past",
                        "imperfect",
                        "preterite",
                    ],
                    "raw_tags": ["yo", "Tiempos simples"],
                },
                {
                    "form": "cantase",
                    "tags": [
                        "personal",
                        "singular",
                        "first-person",
                        "subjunctive",
                        "past",
                        "imperfect",
                        "preterite",
                    ],
                    "raw_tags": ["yo", "Tiempos simples"],
                },
                {
                    "form": "haya cantado",
                    "tags": [
                        "personal",
                        "singular",
                        "first-person",
                        "subjunctive",
                        "present",
                        "perfect",
                    ],
                    "raw_tags": ["yo", "Tiempos compuestos", "Antepresente"],
                },
                {
                    "form": "canta^(tú)",
                    "tags": [
                        "personal",
                        "singular",
                        "second-person",
                        "imperative",
                        "affirmative",
                    ],
                    "raw_tags": ["tú\n vos"],
                },
                {
                    "form": "cantáᵛᵒˢ",
                    "tags": [
                        "personal",
                        "singular",
                        "second-person",
                        "imperative",
                        "affirmative",
                    ],
                    "raw_tags": ["tú\n vos"],
                },
            ],
        )
        self.assertEqual(
            page_data[0]["categories"],
            ["ES:Verbos", "ES:Verbos regulares", "ES:Primera conjugación"],
        )

    def test_only_add_conj_data_to_verb(self):
        self.wxr.wtp.start_page("acontecer")
        self.wxr.wtp.add_page("Plantilla:lengua", 10, "Español")
        self.wxr.wtp.add_page(
            "Plantilla:es.v.conj.zc.cer",
            10,
            """{|
|+ class="normal" |<big> '''Flexión de ''acontecer''''' </big><span>
segunda conjugación,&nbsp;bipersonal,&nbsp;irregular</span>
! class="vertical" colspan="4" |Formas no personales
|-
! class="vertical" colspan="1" width="300px" |
! class="vertical" colspan="1" |Simples
! class="vertical" colspan="1" |Compuestas
|-
! colspan="1"|[[infinitivo|Infinitivo]]
| colspan="1"|acontecer
|}""",
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
{{es.v.conj.zc.cer|aconte|impersonal=plural}}""",
        )
        self.assertTrue("forms" in page_data[0])
        self.assertTrue("forms" not in page_data[1])

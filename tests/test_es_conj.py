from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.conjugation import process_conjugation_template
from wiktextract.extractor.es.models import WordEntry
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

    def test_es_v_conj_ver(self):
        self.wxr.wtp.start_page("ver")
        self.wxr.wtp.add_page(
            "Plantilla:es.v.conj.ver",
            10,
            """{|
|+ class="normal" |<big style="padding:10px"> '''Flexión de ''ver''''' </big><span style="padding:10px;">
segunda conjugación,&nbsp;irregular</span>
! class="vertical" colspan="7" |Formas no personales
|-
! class="vertical" colspan="1" width="300px" |
! class="vertical" colspan="3" |Simples
! class="vertical" colspan="3" |Compuestas
|-
! colspan="1" style="background:#e2e4c0; padding-left:5px"|[[infinitivo|Infinitivo]]
| colspan="3"|ver
| colspan="3"|haber [[visto|v'''isto''']]
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
! class="vertical" style="background:#c0cfe4" colspan="1"|[[modo indicativo|Modo indicativo]]
! class="vertical" rowspan="2" style="background:#c0cfe4" |yo
! class="vertical" rowspan="2" style="background:#c0cfe4" |tú <br/>vos
! class="vertical" rowspan="2" style="background:#c0cfe4" |él / ella<br/>usted<sup style="color:red">1</sup>
! class="vertical" rowspan="2" style="background:#c0cfe4" |nosotros<br/>nosotras
! class="vertical" rowspan="2" style="background:#c0cfe4" |vosotros<br/>vosotras
! class="vertical" rowspan="2" style="background:#c0cfe4" |ellos / ellas<br/>ustedes<sup style="color:red">1</sup>
|-
! class="vertical" style="background:#c0cfe4; font-size:80%;" colspan="1"|Tiempos simples
|-
! style="background:#c0cfe4; padding-left:5px"|[[presente#Español|Presente]]
|| [[veo|v'''e'''o]]
|| [[ves|ves]]<sup><sup>tú</sup></sup><br/>[[ves|ves]]<sup><sup>vos</sup></sup>||[[ve|ve]]|| [[vemos]]
|| [[veis|veis]]
|| [[ven|ven]]
|-
! colspan="2" style="background:#e4d4c0; color:#000; padding-left:5px"|Afirmativo
|| [[ve|ve]]<sup><sup>tú</sup></sup><br/>[[ve|ve]]<sup><sup>vos</sup></sup>
|}""",
        )
        root = self.wxr.wtp.parse("{{es.v.conj.ver|v}}")
        word_entry = WordEntry(
            word="ver", pos="verb", lang="Español", lang_code="es"
        )
        process_conjugation_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "ver", "tags": ["infinitive", "simple"]},
                {"form": "haber visto", "tags": ["infinitive", "compound"]},
                {
                    "form": "veo",
                    "tags": ["present", "singular", "first-person"],
                },
                {
                    "form": "ves^(tú)",
                    "tags": ["present", "singular", "second-person"],
                },
                {
                    "form": "vesᵛᵒˢ",
                    "tags": ["present", "singular", "second-person"],
                },
                {"form": "ve", "tags": ["present", "singular", "third-person"]},
                {
                    "form": "vemos",
                    "tags": ["present", "plural", "first-person"],
                },
                {
                    "form": "veis",
                    "tags": ["present", "plural", "second-person"],
                },
                {"form": "ven", "tags": ["present", "plural", "third-person"]},
                {
                    "form": "ve^(tú)",
                    "tags": ["affirmative", "singular", "second-person"],
                },
                {
                    "form": "veᵛᵒˢ",
                    "tags": ["affirmative", "singular", "second-person"],
                },
            ],
        )

    def test_es_v(self):
        self.wxr.wtp.start_page("dar")
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
|}""",
        )
        root = self.wxr.wtp.parse("{{es.v}}")
        word_entry = WordEntry(
            word="dar", pos="verb", lang="Español", lang_code="es"
        )
        process_conjugation_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["forms"],
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

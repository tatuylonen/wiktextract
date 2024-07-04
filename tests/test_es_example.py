import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.es.example import (
    extract_example,
    process_example_list,
)
from wiktextract.extractor.es.models import Sense
from wiktextract.wxr_context import WiktextractContext


class TestESExample(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_ejemplo_template(self):
        # standard format
        self.wxr.wtp.start_page("lord")
        self.wxr.wtp.add_page(
            "Plantilla:ejemplo",
            10,
            """:*'''Ejemplo:'''
::<blockquote><span class='cita'>And He has on His robe and on His thigh a name written: KING OF KINGS AND '''LORD''' OF LORDS</span><span class='trad'>''Traducción:&nbsp;''Y en su vestidura y en su muslo tiene escrito este nombre: REY DE REYES Y '''SEÑOR''' DE SEÑORES</span><span class='ref'>''<span class='plainlinks'>[//www.biblegateway.com/passage/?search=Apocalipsis+19&version=NKJV Bible]</span> Revelation 19:16''. Versión: New King James. <br>Traducción: ''<span class='plainlinks'>[//www.biblegateway.com/passage/?search=Apocalipsis+19&version=RVR1960 Biblia]</span> Apocalipsis 19:16''. Versión: Reina-Valera 1995. </span></blockquote>
""",
        )
        root = self.wxr.wtp.parse(
            "{{ejemplo|And He has on His robe and on His thigh a name written: KING OF KINGS AND '''LORD''' OF LORDS|c=libro|v=New King James|t=Bible|pasaje=Revelation 19:16|u=https://www.biblegateway.com/passage/?search=Apocalipsis+19&version=NKJV|trad=Y en su vestidura y en su muslo tiene escrito este nombre: REY DE REYES Y '''SEÑOR''' DE SEÑORES|tradc=libro|tradv=Reina-Valera 1995|tradt=Biblia|tradpasaje=Apocalipsis 19:16|tradu=https://www.biblegateway.com/passage/?search=Apocalipsis+19&version=RVR1960}}"
        )
        sense_data = Sense()
        extract_example(self.wxr, sense_data, root.children)
        dump_data = sense_data.model_dump(exclude_defaults=True)["examples"]
        del dump_data[0]["example_templates"]
        self.assertEqual(
            dump_data,
            [
                {
                    "text": "And He has on His robe and on His thigh a name "
                        "written: KING OF KINGS AND LORD OF LORDS",
                    "translation": "Y en su vestidura y en su muslo tiene "
                        "escrito este nombre: REY DE REYES Y SEÑOR DE SEÑORES",
                    "ref": "Bible Revelation 19:16. Versión: New King James."
                        "\nTraducción: Biblia Apocalipsis 19:16. "
                        "Versión: Reina-Valera 1995.",
                }
            ],
        )
        self.assertEqual(
            sense_data.examples[0].example_templates[0].name, "ejemplo"
        )

    def test_url_after_ejemplo_template(self):
        # abnormal format
        # https://es.wiktionary.org/wiki/necroporra
        self.wxr.wtp.start_page("necroporra")
        self.wxr.wtp.add_page(
            "Plantilla:ejemplo",
            10,
            """:*'''Ejemplo:'''
::<blockquote><span class='cita'>{{{1}}}</span></blockquote>""",
        )
        root = self.wxr.wtp.parse(
            "{{ejemplo|Nos gusta lo oscuro, y por eso triunfa la Necroporra, sea ético o no}}[https://www.menzig.es/a/necroporra-fantamorto-porra-famosos-muertos/ ]"
        )
        sense_data = Sense()
        extract_example(self.wxr, sense_data, root.children)
        dump_data = sense_data.model_dump(exclude_defaults=True)["examples"]
        del dump_data[0]["example_templates"]
        self.assertEqual(
            dump_data,
            [
                {
                    "text": "Nos gusta lo oscuro, y por eso triunfa "
                            "la Necroporra, sea ético o no",
                    "ref": "https://www.menzig.es/a/necroporra-"
                            "fantamorto-porra-famosos-muertos/",
                }
            ],
        )

    def test_url_in_ejemplo_template_first_param(self):
        # abnormal format
        # https://es.wiktionary.org/wiki/ser_más_viejo_que_Matusalén
        self.wxr.wtp.start_page("ser más viejo que Matusalén")
        self.wxr.wtp.add_page(
            "Plantilla:ejemplo",
            10,
            """:*'''Ejemplo:'''
::<blockquote><span class='cita'>{{{1}}}</span></blockquote>""",
        )
        root = self.wxr.wtp.parse(
            '{{ejemplo|Papel: más viejo que Matusalén, pero graduado "cum laude" en eficacia publicitaria [https://www.marketingdirecto.com/marketing-general/publicidad/papel-mas-viejo-matusalen-pero-graduado-cum-laude-eficacia-publicitaria]}}'
        )
        sense_data = Sense()
        extract_example(self.wxr, sense_data, root.children)
        dump_data = sense_data.model_dump(exclude_defaults=True)["examples"]
        del dump_data[0]["example_templates"]
        self.assertEqual(
            dump_data,
            [
                {
                    "text": 'Papel: más viejo que Matusalén, pero graduado '
                            '"cum laude" en eficacia publicitaria',
                    "ref": "https://www.marketingdirecto.com/"
                            "marketing-general/publicidad/papel-mas-viejo-"
                            "matusalen-pero-graduado-cum-laude-"
                            "eficacia-publicitaria",
                }
            ],
        )

    def test_example_after_empty_ejemplo_template(self):
        # abnormal format
        self.wxr.wtp.start_page("confesar")
        self.wxr.wtp.add_page("Plantilla:ejemplo", 10, "")
        root = self.wxr.wtp.parse(
            "{{ejemplo}} El interrogatorio fue efectivo y el detenido ''confesó''."
        )
        sense_data = Sense()
        extract_example(self.wxr, sense_data, root.children)
        self.assertEqual(
            sense_data.model_dump(exclude_defaults=True)["examples"],
            [{"text": "El interrogatorio fue efectivo y el detenido confesó."}],
        )

    def test_example_text_not_in_nested_list(self):
        # abnormal format
        self.wxr.wtp.start_page("cerebro")
        root = self.wxr.wtp.parse(
            ":*'''Ejemplo:''' Tú serás el cerebro del plan."
        )
        sense_data = Sense()
        process_example_list(self.wxr, sense_data, root.children[0].children[0])
        self.assertEqual(
            sense_data.model_dump(exclude_defaults=True)["examples"],
            [{"text": "Tú serás el cerebro del plan."}],
        )

    def test_example_in_nested_list(self):
        # abnormal format and obsolete template
        self.wxr.wtp.start_page("quicio")
        self.wxr.wtp.add_page(
            "Plantilla:cita libro",
            10,
            "<cite>Bombal, María Luisa&#32;(2012).&#32;«La Amortajada», "
            "<i>La Última Niebla/La Amortajada</i>."
            "&#32;Planeta,&#32;151.</cite>",
        )
        root = self.wxr.wtp.parse(""":*'''Ejemplo:'''
::* «Apoyado contra el ''quicio'' de la puerta, adivina, de pronto, a su marido.» {{cita libro|nombre=María Luisa|apellidos=Bombal|título=La Última Niebla/La Amortajada|capítulo=La Amortajada|fecha=2012|editorial=Planeta|páginas=151}}""")  # noqa: E501
        sense_data = Sense()
        process_example_list(self.wxr, sense_data, root.children[0].children[0])
        self.assertEqual(
            sense_data.model_dump(exclude_defaults=True)["examples"],
            [
                {
                    "text": "«Apoyado contra el quicio de la puerta, adivina, "
                            "de pronto, a su marido.»",
                    "ref": "Bombal, María Luisa (2012). «La Amortajada», "
                            "La Última Niebla/La Amortajada. Planeta, 151.",
                }
            ],
        )

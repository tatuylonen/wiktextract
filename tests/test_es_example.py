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
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="es"),
            WiktionaryConfig(dump_file_lang_code="es"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_sense_data(self) -> Sense:
        return Sense(glosses=["gloss1"])

    def test_es_extract_example(self):
        test_cases = [
            # https://es.wiktionary.org/wiki/coñazo
            {
                "input": "{{ejemplo|La conferencia ha sido un ''coñazo''}}",
                "expected": [{"text": "La conferencia ha sido un coñazo"}],
            },
            # https://es.wiktionary.org/wiki/necroporra
            {
                "input": "{{ejemplo|Nos gusta lo oscuro, y por eso triunfa la Necroporra, sea ético o no}}[https://www.menzig.es/a/necroporra-fantamorto-porra-famosos-muertos/ ]",
                "expected": [
                    {
                        "text": "Nos gusta lo oscuro, y por eso triunfa la Necroporra, sea ético o no",
                        "ref": {
                            "url": "https://www.menzig.es/a/necroporra-fantamorto-porra-famosos-muertos/"
                        },
                    }
                ],
            },
            # https://es.wiktionary.org/wiki/ser_más_viejo_que_Matusalén
            {
                "input": """{{ejemplo|Papel: más viejo que Matusalén, pero graduado "cum laude" en eficacia publicitaria [https://www.marketingdirecto.com/marketing-general/publicidad/papel-mas-viejo-matusalen-pero-graduado-cum-laude-eficacia-publicitaria]}}""",
                "expected": [
                    {
                        "text": """Papel: más viejo que Matusalén, pero graduado "cum laude" en eficacia publicitaria""",
                        "ref": {
                            "url": "https://www.marketingdirecto.com/marketing-general/publicidad/papel-mas-viejo-matusalen-pero-graduado-cum-laude-eficacia-publicitaria"
                        },
                    }
                ],
            },
            # https://es.wiktionary.org/wiki/zapotear
            {
                "input": "{{ejemplo|Era persona inteligente, culta, que me permitía ''zapotear'' los libros y me hacía comentarios sobre ellos y sus autores|título=Memorias intelectuales|apellidos=Jaramillo Uribe|nombre=Jaime|páginas=19|URL=https://books.google.com.co/books?id=X9MSAQAAIAAJ&q=zapotear|año=2007}}",
                "expected": [
                    {
                        "text": "Era persona inteligente, culta, que me permitía zapotear los libros y me hacía comentarios sobre ellos y sus autores",
                        "ref": {
                            "title": "Memorias intelectuales",
                            "first_name": "Jaime",
                            "last_name": "Jaramillo Uribe",
                            "pages": "19",
                            "url": "https://books.google.com.co/books?id=X9MSAQAAIAAJ&q=zapotear",
                            "year": "2007",
                        },
                    }
                ],
            },
            # https://es.wiktionary.org/wiki/meek
            {
                "input": "{{ejemplo_y_trad|Blessed are the '''meek''', For they shall inherit the earth|Bienaventurados los '''mansos''', porque recibirán la tierra por heredad}}",
                "expected": [
                    {
                        "text": "Blessed are the meek, For they shall inherit the earth",
                        "translation": "Bienaventurados los mansos, porque recibirán la tierra por heredad",
                    }
                ],
            },
            # https://es.wiktionary.org/wiki/confesar
            {
                "input": "{{ejemplo}} El interrogatorio fue efectivo y el detenido ''confesó''.",
                "expected": [
                    {
                        "text": "El interrogatorio fue efectivo y el detenido confesó.",
                    }
                ],
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                sense_data = self.get_default_sense_data()

                root = self.wxr.wtp.parse(case["input"])

                extract_example(self.wxr, sense_data, root.children)
                self.assertEqual(
                    sense_data.model_dump(exclude_defaults=True)["examples"],
                    case["expected"],
                )

    def test_es_process_example_list(self):
        test_cases = [
            {"input": ":*'''Ejemplo:'''\n", "expected": []},
            # https://es.wiktionary.org/wiki/cerebro
            {
                "input": ":*'''Ejemplo:''' Tú serás el cerebro del plan.",
                "expected": [{"text": "Tú serás el cerebro del plan."}],
            },
            # https://es.wiktionary.org/wiki/quicio
            {
                "input": """:*'''Ejemplo:'''
::* «Apoyado contra el ''quicio'' de la puerta, adivina, de pronto, a su marido.» {{cita libro|nombre=María Luisa|apellidos=Bombal}}""",
                "expected": [
                    {
                        "text": "«Apoyado contra el quicio de la puerta, adivina, de pronto, a su marido.»",
                        "ref": {
                            "first_name": "María Luisa",
                            "last_name": "Bombal",
                        },
                    }
                ],
            },
            # https://es.wiktionary.org/wiki/silepsis
            {
                "input": "::Su [[obra]] comprendió [[esculpir]] un [[busto]], varios [[retrato|retratos]] y uno que otro [[dibujo]] al [[carbón]].",
                "expected": [
                    {
                        "text": "Su obra comprendió esculpir un busto, varios retratos y uno que otro dibujo al carbón."
                    }
                ],
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                sense_data = self.get_default_sense_data()

                root = self.wxr.wtp.parse(case["input"])

                process_example_list(
                    self.wxr, sense_data, root.children[0].children[0]
                )
                examples = [
                    e.model_dump(exclude_defaults=True)
                    for e in sense_data.examples
                ]
                self.assertEqual(
                    examples,
                    case["expected"],
                )

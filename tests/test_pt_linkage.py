from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        conf = WiktionaryConfig(
            dump_file_lang_code="pt",
            capture_language_codes=None,
        )
        self.wxr = WiktextractContext(
            Wtp(
                lang_code="pt",
                parser_function_aliases=conf.parser_function_aliases,
            ),
            conf,
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_expression(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page("Predefinição:g", 10, "''masculino''")
        data = parse_page(
            self.wxr,
            "olho",
            """={{-pt-}}=
==Substantivo==
# órgão
===Expressões===
* '''[[a beleza está nos olhos de quem vê]]''': {{escopo2|Provérbio}} cada pessoa tem uma opinião própria sobre o que lhe é belo
* '''[[abrir os olhos]]''':
*: {{escopo2|intransitivo}} perceber a verdade
*:: ''Entre amores, trapaças e muitas confusões, Katie terá que lutar para conquistar seu espaço e '''abrir os olhos''' para a realidade da cidade grande.''""",
        )
        self.assertEqual(
            data[0]["expressions"],
            [
                {
                    "senses": [
                        {
                            "glosses": [
                                "cada pessoa tem uma opinião própria sobre o que lhe é belo"
                            ],
                            "raw_tags": ["Provérbio"],
                        }
                    ],
                    "word": "a beleza está nos olhos de quem vê",
                },
                {
                    "senses": [
                        {
                            "glosses": ["perceber a verdade"],
                            "tags": ["intransitive"],
                            "examples": [
                                {
                                    "text": "Entre amores, trapaças e muitas confusões, Katie terá que lutar para conquistar seu espaço e abrir os olhos para a realidade da cidade grande.",
                                    "bold_text_offsets": [(93, 107)],
                                }
                            ],
                        }
                    ],
                    "word": "abrir os olhos",
                },
            ],
        )

    def test_synonyms(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "olho",
            """={{-pt-}}=
==Substantivo==
# órgão
===Sinônimos===
* De '''5''' (furo, na agulha, para a passagem de linhas ou fios): [[buraco]]""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "buraco",
                    "sense": "furo, na agulha, para a passagem de linhas ou fios",
                    "sense_index": 5,
                }
            ],
        )

    def test_link_preto(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "olho",
            """={{-pt-}}=
==Substantivo==
# órgão
===Verbetes derivados===
{{fraseini|Nomes de animais derivados de ''olho''}}
* {{link preto|olho-branco}} (''[[species:Zosteropidae|Zosteropidae]]'')""",
        )
        self.assertEqual(
            data[0]["derived"],
            [
                {
                    "word": "olho-branco",
                    "sense": "Nomes de animais derivados de olho",
                    "raw_tags": ["Zosteropidae"],
                }
            ],
        )

    def test_nested_list(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "cão",
            """={{-pt-}}=
==Substantivo==
# animal
===Sinônimos===
* De '''1''' (animal mamífero, carnívoro e quadrúpede):
** [[cachorro]]
** {{escopo2|Brasil|RS}} [[cusco]]
*De '''3''' (gênio do mal):
** vide [[Wikisaurus:diabo]]""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "cachorro",
                    "sense": "animal mamífero, carnívoro e quadrúpede",
                    "sense_index": 1,
                },
                {
                    "word": "cusco",
                    "sense": "animal mamífero, carnívoro e quadrúpede",
                    "sense_index": 1,
                    "tags": ["Brazil"],
                    "raw_tags": ["RS"],
                },
            ],
        )

    def test_phraseology_equal(self):
        self.wxr.wtp.add_page("Predefinição:-en-", 10, "Inglês")
        data = parse_page(
            self.wxr,
            "aboard",
            """={{-en-}}=
== Advérbio ==
'''a.board'''
#[[a bordo]]

===Fraseologia===
* '''aboard the train''' (''locução adverbial'') = a bordo do trem""",
        )
        self.assertEqual(
            data[0]["phraseology"],
            [
                {
                    "word": "aboard the train",
                    "roman": "locução adverbial",
                    "sense": "a bordo do trem",
                }
            ],
        )

    def test_phraseology_colon(self):
        self.wxr.wtp.add_page("Predefinição:-la-", 10, "Latim")
        data = parse_page(
            self.wxr,
            "secundus",
            """={{-la-}}=
==Adjetivo==
'''se.cun.dus'''
# que [[seguir|segue]]

==Fraseologia==
* '''secundae [[res]]''': ''[[felicidade]]''
* [[secunda mensa]]: [[sobremesa]]""",
        )
        self.assertEqual(
            data[0]["phraseology"],
            [
                {"word": "secundae res", "sense": "felicidade"},
                {"word": "secunda mensa", "sense": "sobremesa"},
            ],
        )

    def test_phraseology_nested_list(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "gota",
            """={{-pt-}}=
==Substantivo==
# [[fragmento]]

===Fraseologia===
{{fraseini|De 1 (gota: pingo)}}
# ''' [[até a última gota]] ''' ([[locução]]):  [[até]] [[ser]] [[usado]] ou [[bebido]] [[totalmente]] (um [[líquido]])
#* ''' [[este|Este]] [[café]] é [[bom]] até a [[última]] gota '''  (frase comum)""",
        )
        self.assertEqual(
            data[0]["phraseology"],
            [
                {
                    "word": "até a última gota",
                    "sense": "até ser usado ou bebido totalmente (um líquido)",
                    "sense_index": 1,
                },
                {
                    "word": "Este café é bom até a última gota",
                    "sense": "gota: pingo",
                    "sense_index": 1,
                },
            ],
        )

    def test_expression_gloss_child_list(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        data = parse_page(
            self.wxr,
            "testa",
            """={{-pt-}}=
==Substantivo==
# [[parte]]

===Expressões===
* '''[[testa de boi]]''': (Portugal, Douro)
*# indivíduo com a testa avantajada;""",
        )
        self.assertEqual(
            data[0]["expressions"],
            [
                {
                    "word": "testa de boi",
                    "senses": [
                        {"glosses": ["(Portugal, Douro)"]},
                        {
                            "glosses": [
                                "(Portugal, Douro)",
                                "indivíduo com a testa avantajada;",
                            ]
                        },
                    ],
                }
            ],
        )

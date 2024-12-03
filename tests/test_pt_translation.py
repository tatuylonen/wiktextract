from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtTranslation(TestCase):
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

    def test_subpage(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page(
            "Predefinição:trad",
            10,
            """[[abenaque|Abenaque]] : <span lang="abe">[[adia#Abenaque|adia]]</span>  , <span lang="abe">[[alemos#Abenaque|alemos]]</span>""",
        )
        self.wxr.wtp.add_page(
            "Predefinição:t",
            10,
            """[[aino|Aino]]: <span lang="ain">[[セタ#ain|セタ]]</span>  ''<span title="romanização/transliteração de “セタ”">(seta)</span>''""",
        )
        self.wxr.wtp.add_page(
            "Predefinição:trad-",
            10,
            """[[búlgaro|Búlgaro]] : <span lang="bg">[[куче#Búlgaro|куче]]</span> ''(kutche)'' <span class="noprint">[[:bg:куче|<small><sup><span style="letter-spacing:1px" title="Clique aqui para ver “куче” no Wikcionário em búlgaro">(bg)</span></sup></small>]]</span>""",
        )
        self.wxr.wtp.add_page(
            "cão/traduções 1",
            0,
            """{{tradini|De 1 (mamífero domesticado - ''Canis lupus familiaris'')}}
* {{trad|abe|adia|alemos}}
* {{t|ain|セタ||seta}}
* {{trad-|bg|куче|(kutche)}}; {{xlatio|bg|пес|(pes)}} (''coloquial'')
{{tradfim}}""",
        )
        data = parse_page(
            self.wxr,
            "cão",
            """={{-pt-}}=
==Substantivo==
# animal
===Tradução===
Vide traduções nas seguintes páginas:
* [[cão/traduções 1]]""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "Abenaque",
                    "lang_code": "abe",
                    "sense": "mamífero domesticado - Canis lupus familiaris",
                    "sense_index": 1,
                    "word": "adia",
                },
                {
                    "lang": "Abenaque",
                    "lang_code": "abe",
                    "sense": "mamífero domesticado - Canis lupus familiaris",
                    "sense_index": 1,
                    "word": "alemos",
                },
                {
                    "lang": "Aino",
                    "lang_code": "ain",
                    "sense": "mamífero domesticado - Canis lupus familiaris",
                    "sense_index": 1,
                    "roman": "seta",
                    "word": "セタ",
                },
                {
                    "lang": "Búlgaro",
                    "lang_code": "bg",
                    "sense": "mamífero domesticado - Canis lupus familiaris",
                    "sense_index": 1,
                    "roman": "kutche",
                    "word": "куче",
                },
                {
                    "lang": "Búlgaro",
                    "lang_code": "bg",
                    "sense": "mamífero domesticado - Canis lupus familiaris",
                    "sense_index": 1,
                    "roman": "pes",
                    "word": "пес",
                    "raw_tags": ["coloquial"],
                },
            ],
        )

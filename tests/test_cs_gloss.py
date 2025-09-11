from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.cs.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestCsGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="cs"),
            WiktionaryConfig(
                dump_file_lang_code="cs", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_normal_list(self):
        self.wxr.wtp.add_page(
            "Šablona:Příznaky",
            10,
            """<span class="priznaky">(expresivně[[Category:Expresivní výrazy/čeština]], pejorativně)</span>""",
        )
        data = parse_page(
            self.wxr,
            "pes",
            """==čeština==
=== podstatné jméno (1) ===
* ''rod mužský životný''
==== význam ====
# {{Příznaky|cs|expr.|pejor.}} [[nedobrý]], [[krutý]] ([[člověk]])
# ''(oděvnický slang, ve zkrácené formě)'' [[polyester]]""",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "čeština",
                    "lang_code": "cs",
                    "pos": "noun",
                    "pos_title": "podstatné jméno",
                    "senses": [
                        {
                            "categories": ["Expresivní výrazy/čeština"],
                            "glosses": ["nedobrý, krutý (člověk)"],
                            "tags": ["expressively", "pejorative"],
                        },
                        {
                            "glosses": ["polyester"],
                            "raw_tags": [
                                "oděvnický slang",
                                "ve zkrácené formě",
                            ],
                        },
                    ],
                    "tags": ["masculine", "animate"],
                    "word": "pes",
                }
            ],
        )

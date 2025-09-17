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

    def test_nested_list(self):
        data = parse_page(
            self.wxr,
            "ostrožka",
            """==čeština==
=== podstatné jméno ===
==== význam ====
# rod ''[[Consolida]]''
## [[ostrožka stračka]]""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {"glosses": ["rod Consolida"]},
                {"glosses": ["rod Consolida", "ostrožka stračka"]},
            ],
        )

    def test_example_bold_offsets(self):
        data = parse_page(
            self.wxr,
            "pes",
            """==čeština==
=== podstatné jméno (1) ===
==== význam ====
# [[psovitý|psovitá]]
#* {{Příklad|cs|'''Pes''' je nejlepší přítel člověka.}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["psovitá"],
                    "examples": [
                        {
                            "bold_text_offsets": [(0, 3)],
                            "text": "Pes je nejlepší přítel člověka.",
                        }
                    ],
                }
            ],
        )

    def test_example_translation(self):
        data = parse_page(
            self.wxr,
            "ski",
            """== angličtina ==
=== podstatné jméno ===
==== význam ====
# [[lyže]]
#* {{Příklad|en|a pair of skis|pár lyží}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["lyže"],
                    "examples": [
                        {"text": "a pair of skis", "translation": "pár lyží"}
                    ],
                }
            ],
        )

    def test_form_of(self):
        data = parse_page(
            self.wxr,
            "pes",
            """== čeština ==
=== podstatné jméno (2) ===
==== význam ====
# ''genitiv plurálu substantiva [[peso]]''""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["genitiv plurálu substantiva peso"],
                    "form_of": [{"word": "peso"}],
                    "tags": ["form-of"],
                }
            ],
        )

    def test_wikinode_in_example_template_arg(self):
        data = parse_page(
            self.wxr,
            "älska",
            """== švédština ==
=== sloveso ===
==== význam ====
# [[milovat]]
#* {{Příklad|sv|[[jag älskar dig|Jag älskar dig]].|[[miluji tě|Miluji tě]].}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "examples": [
                        {"text": "Jag älskar dig.", "translation": "Miluji tě."}
                    ],
                    "glosses": ["milovat"],
                }
            ],
        )

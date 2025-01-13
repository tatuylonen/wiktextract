from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="it"),
            WiktionaryConfig(
                dump_file_lang_code="it", capture_language_codes=None
            ),
        )

    def test_gloss_list(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        self.wxr.wtp.add_page(
            "Template:Term",
            10,
            "<small>(<i>[[mammalogia]]</i>)</small>[[Categoria:Mammalogia-IT]]",
        )
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===[[Image:Open_book_01.svg|30px|]]''[[sostantivo|Sostantivo]]''===
[[Categoria:Sostantivi in italiano]]

# {{Term|mammalogia|it}} [[animale]]""",
        )
        self.assertEqual(
            data,
            [
                {
                    "categories": ["Sostantivi in italiano"],
                    "lang": "Italiano",
                    "lang_code": "it",
                    "word": "cane",
                    "pos": "noun",
                    "pos_title": "Sostantivo",
                    "senses": [
                        {
                            "glosses": ["animale"],
                            "topics": ["mammalogy"],
                            "categories": ["Mammalogia-IT"],
                        }
                    ],
                }
            ],
        )

    def test_double_pos_subsection_templates(self):
        self.wxr.wtp.add_page("Template:-la-", 10, "Latino")
        self.wxr.wtp.add_page(
            "Template:Intransitivo",
            10,
            """====[[intransitivo|Intransitivo]]====
[[Categoria:Verbi intransitivi_in_latino]]""",
        )
        self.wxr.wtp.add_page(
            "Template:Deponente",
            10,
            """====[[deponente|Deponente]]====
[[Categoria:Verbi deponenti_in_latino]]""",
        )
        data = parse_page(
            self.wxr,
            "aboriscor",
            """== {{-la-}} ==
===[[Image:Open_book_01.svg|30px|]]''[[verbo|Verbo]]''===
[[Categoria:Verbi in latino]]
{{Intransitivo|la}}
{{Deponente|la}}
'''ăbŏriscor'''

# [[venir]] [[meno]]""",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "Latino",
                    "lang_code": "la",
                    "word": "aboriscor",
                    "pos": "verb",
                    "pos_title": "Verbo",
                    "categories": [
                        "Verbi in latino",
                        "Verbi intransitivi_in_latino",
                        "Verbi deponenti_in_latino",
                    ],
                    "senses": [{"glosses": ["venir meno"]}],
                    "raw_tags": ["Intransitivo", "Deponente"],
                }
            ],
        )

    def test_subsecton_template_add_new_word_entry(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        self.wxr.wtp.add_page(
            "Template:Ausiliare",
            10,
            """====[[ausiliare|Ausiliare]]====
[[Categoria:Verbi ausiliari_in_italiano]]""",
        )
        self.wxr.wtp.add_page(
            "Template:Intransitivo",
            10,
            """====[[intransitivo|Intransitivo]]====
[[Categoria:Verbi intransitivi_in_latino]]""",
        )
        data = parse_page(
            self.wxr,
            "essere",
            """== {{-it-}} ==
===[[Image:Open_book_01.svg|30px|]]''[[verbo|Verbo]]''===
[[Categoria:Verbi in italiano]]
{{Ausiliare|it}}
# serve per la coniugazione

{{Intransitivo|it}}
# Questo verbo serve per dire""",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "Italiano",
                    "lang_code": "it",
                    "word": "essere",
                    "pos": "verb",
                    "pos_title": "Verbo",
                    "categories": [
                        "Verbi in italiano",
                        "Verbi ausiliari_in_italiano",
                    ],
                    "senses": [{"glosses": ["serve per la coniugazione"]}],
                    "raw_tags": ["Ausiliare"],
                },
                {
                    "lang": "Italiano",
                    "lang_code": "it",
                    "word": "essere",
                    "pos": "verb",
                    "pos_title": "Verbo",
                    "categories": [
                        "Verbi in italiano",
                        "Verbi intransitivi_in_latino",
                    ],
                    "senses": [{"glosses": ["Questo verbo serve per dire"]}],
                    "raw_tags": ["Intransitivo"],
                },
            ],
        )

    def test_form_of(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cani",
            """== {{-it-}} ==
===Sostantivo, forma flessa===
# plurale di [[cane]]""",
        )
        self.assertEqual(
            data[0]["senses"],
            [{"glosses": ["plurale di cane"], "form_of": [{"word": "cane"}]}],
        )

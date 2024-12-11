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
                            "raw_tags": ["mammalogia"],
                            "categories": ["Mammalogia-IT"],
                        }
                    ],
                }
            ],
        )

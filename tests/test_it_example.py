from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="it"),
            WiktionaryConfig(
                dump_file_lang_code="it", capture_language_codes=None
            ),
        )

    def test_list_example(self):
        self.wxr.wtp.add_page("Template:-br-", 10, "Bretone")
        data = parse_page(
            self.wxr,
            "dog",
            """== {{-br-}} ==
===Sostantivo===
# mutazione
#* ''Da '''dog''', e '''dog'''.''
#*: Il tuo cappello, il suo cappello.""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "glosses": ["mutazione"],
                    "examples": [
                        {
                            "text": "Da dog, e dog.",
                            "translation": "Il tuo cappello, il suo cappello.",
                        }
                    ],
                }
            ],
        )

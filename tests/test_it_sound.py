from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItSound(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="it"),
            WiktionaryConfig(
                dump_file_lang_code="it", capture_language_codes=None
            ),
        )

    def test_hyphenation_single_list(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
# {{Term|mammalogia|it}} [[animale]]
===Sillabazione===
; cà | ne""",
        )
        self.assertEqual(data[0]["hyphenations"], [{"hyphenation": "cà | ne"}])

    def test_ipa_audio_templates(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
# {{Term|mammalogia|it}} [[animale]]
===Pronuncia===
{{IPA|/ˈkaːne/}}
{{Audio|it-cane.ogg}}""",
        )
        sound = data[0]["sounds"][0]
        self.assertEqual(sound["ipa"], "/ˈkaːne/")
        self.assertEqual(sound["audio"], "it-cane.ogg")

    def test_hyphenation_lists(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "pesca",
            """== {{-it-}} ==
===Sostantivo===
# [[frutto]] del [[pesco]]
===Sillabazione===
* ''(il frutto e significati correlati)'' '''pè | sca'''
* ''(l'atto del pescare e significati correlati)'' '''pé | sca'''""",
        )
        self.assertEqual(
            data[0]["hyphenations"],
            [
                {
                    "hyphenation": "pè | sca",
                    "sense": "il frutto e significati correlati",
                },
                {
                    "hyphenation": "pé | sca",
                    "sense": "l'atto del pescare e significati correlati",
                },
            ],
        )

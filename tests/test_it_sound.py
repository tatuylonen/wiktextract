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

    def test_hyphenation(self):
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
        self.assertEqual(data[0]["hyphenation"], "cà | ne")

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

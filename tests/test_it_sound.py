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

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

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
        self.assertEqual(data[0]["hyphenations"], [{"parts": ["cà", "ne"]}])

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
                    "parts": ["pè", "sca"],
                    "sense": "il frutto e significati correlati",
                },
                {
                    "parts": ["pé", "sca"],
                    "sense": "l'atto del pescare e significati correlati",
                },
            ],
        )

    def test_hyphenation_no_list(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cespita",
            """== {{-it-}} ==
===Sostantivo===
# [[variante]] di [[ceppita]]
===Sillabazione===
'''cè | spi | ta''' o '''cé | spi | ta'''""",
        )
        self.assertEqual(
            data[0]["hyphenations"],
            [{"parts": ["cè", "spi", "ta"]}, {"parts": ["cé", "spi", "ta"]}],
        )

    def test_sampa(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "Italia",
            """== {{-it-}} ==
===Nome proprio===
# [[stato]]
===Pronuncia===
{{IPA|/iˈtalja/|/iˈtaː.li̯a/}}, {{SAMPA|/i"talja/}}
{{Audio|It-Italia.ogg}}""",
        )
        self.assertEqual(
            data[0]["sounds"][:2],
            [{"ipa": "/iˈtalja/"}, {"ipa": "/iˈtaː.li̯a/"}],
        )
        self.assertEqual(data[0]["sounds"][2]["ipa"], '/i"talja/')
        self.assertEqual(data[0]["sounds"][2]["tags"], ["SAMPA"])
        self.assertEqual(data[0]["sounds"][2]["audio"], "It-Italia.ogg")

    def test_sound_list(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "pesca",
            """== {{-it-}} ==
===Nome proprio===
# [[frutto]]
===Pronuncia===
* ''(il frutto e significati correlati)'' {{IPA|/ˈpɛska/}} {{Audio|It-pesca_(frutto).ogg}}""",
        )
        self.assertEqual(
            data[0]["sounds"][0]["sense"], "il frutto e significati correlati"
        )
        self.assertEqual(data[0]["sounds"][0]["ipa"], "/ˈpɛska/")
        self.assertEqual(data[0]["sounds"][0]["audio"], "It-pesca_(frutto).ogg")

    def test_glossa_tag(self):
        self.wxr.wtp.add_page("Template:-en-", 10, "Inglese")
        self.wxr.wtp.add_page("Template:glossa", 10, "({{{1}}})")
        data = parse_page(
            self.wxr,
            "large",
            """== {{-en-}} ==
===Aggettivo===
# [[largo]]
===Pronuncia===
*{{glossa|UK}} {{IPA|/lɑːd͡ʒ/}}""",
        )
        self.assertEqual(
            data[0]["sounds"], [{"raw_tags": ["UK"], "ipa": "/lɑːd͡ʒ/"}]
        )

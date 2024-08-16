from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.models import WordEntry
from wiktextract.extractor.pl.sound import extract_sound_section
from wiktextract.wxr_context import WiktextractContext


class TestPlSound(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_en(self):
        self.wxr.wtp.add_page("Szablon:amer", 10, "amer.")
        self.wxr.wtp.add_page("Szablon:lp", 10, "lp")
        self.wxr.wtp.add_page("Szablon:lm", 10, "lm")
        self.wxr.wtp.start_page("dog")
        root = self.wxr.wtp.parse(""": {{amer}} {{IPA|dɔɡ}}, {{SAMPA|dOɡ}}
:: {{lp}} {{audioUS|En-us-dog.ogg|wymowa amerykańska}}, {{lm}} {{audioUS|En-us-ne-dog.ogg}}""")
        base_data = WordEntry(word="dog", lang_code="en", lang="")
        extract_sound_section(self.wxr, base_data, root)
        data = base_data.model_dump(exclude_defaults=True)
        self.assertEqual(
            data["sounds"][:2],
            [
                {"ipa": "dɔɡ", "tags": ["US"]},
                {"ipa": "dOɡ", "tags": ["SAMPA", "US"]},
            ],
        )
        self.assertEqual(data["sounds"][2]["tags"], ["singular"])
        self.assertEqual(data["sounds"][2]["audio"], "En-us-dog.ogg")
        self.assertEqual(data["sounds"][3]["tags"], ["plural"])
        self.assertEqual(data["sounds"][3]["audio"], "En-us-ne-dog.ogg")

    def test_wikitext_ipa(self):
        self.wxr.wtp.start_page("polski")
        root = self.wxr.wtp.parse("* {{AS3|p'''o'''lsʹḱi}}")
        base_data = WordEntry(
            word="polski", lang_code="pl", lang="język polski"
        )
        extract_sound_section(self.wxr, base_data, root)
        data = base_data.model_dump(exclude_defaults=True)
        self.assertEqual(
            data["sounds"],
            [{"ipa": "polsʹḱi", "tags": ["Slavic-alphabet"]}],
        )

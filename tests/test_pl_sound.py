from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.models import WordEntry
from wiktextract.extractor.pl.page import parse_page
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
        base_data = WordEntry(
            word="dog", lang_code="en", lang="język angielski", pos="unknown"
        )
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
            word="polski", lang_code="pl", lang="język polski", pos="unknown"
        )
        extract_sound_section(self.wxr, base_data, root)
        data = base_data.model_dump(exclude_defaults=True)
        self.assertEqual(
            data["sounds"],
            [{"ipa": "polsʹḱi", "tags": ["Slavic-alphabet"]}],
        )

    def test_no_list(self):
        self.wxr.wtp.start_page("płakać")
        root = self.wxr.wtp.parse("===wymowa===\n {{IPA3|ˈpwakaʨ̑}}")
        base_data = WordEntry(
            word="płakać", lang_code="pl", lang="język polski", pos="unknown"
        )
        extract_sound_section(self.wxr, base_data, root.children[0])
        data = base_data.model_dump(exclude_defaults=True)
        self.assertEqual(data["sounds"], [{"ipa": "ˈpwakaʨ̑"}])

    def test_dzielenie(self):
        self.wxr.wtp.add_page(
            "Szablon:dzielenie",
            10,
            "<i>podział przy przenoszeniu wyrazu:</i> ar&#8226;bi&#8226;​ter el&#8226;​e&#8226;​gan&#8226;​ti&#8226;​a&#8226;​rum[[Kategoria:Błąd w szablonie dzielenie]]",
        )
        data = parse_page(
            self.wxr,
            "arbiter elegantiarum",
            """== arbiter elegantiarum ({{język angielski}}) ==
===wymowa===
: {{dzielenie|ar|bi|​ter el|​e|​gan|​ti|​a|​rum}}
===znaczenia===
''fraza rzeczownikowa''
: (1.1) [[znawca]] [[dobry|dobrego]] [[smak]]u, [[esteta]]""",
        )
        self.assertEqual(
            data[0]["hyphenations"],
            [
                {
                    "parts": [
                        "ar",
                        "bi",
                        "ter",
                        "el",
                        "e",
                        "gan",
                        "ti",
                        "a",
                        "rum",
                    ]
                }
            ],
        )
        self.assertEqual(data[0]["categories"], ["Błąd w szablonie dzielenie"])

    def test_homofony(self):
        data = parse_page(
            self.wxr,
            "read",
            """== read ({{język angielski}}) ==
===wymowa===
:: {{homofony|red|redd}}
===znaczenia===
''czasownik''
: (1.1) [[czytać]]""",
        )
        self.assertEqual(
            data[0]["sounds"], [{"homophone": "red"}, {"homophone": "redd"}]
        )

    def test_sound_sense_index(self):
        self.wxr.wtp.add_page(
            "Szablon:forma czasownika", 10, "<i>czasownik, forma fleksyjna</i>"
        )
        data = parse_page(
            self.wxr,
            "read",
            """== read ({{język angielski}}) ==
===wymowa===
: (1.1-6, 2.1)
:: {{IPA|riːd}}
: (3.1-2)
:: {{IPA|red}}
===znaczenia===
''czasownik''
: (1.1) [[czytać]]
''rzeczownik''
: (2.1) [[lektura]]
''{{forma czasownika|en}}''
: (3.1) {{past simple|read}}""",
        )
        self.assertEqual(
            data[0]["sounds"], [{"ipa": "riːd", "sense_index": "1.1-6, 2.1"}]
        )
        self.assertEqual(data[0]["sounds"], data[1]["sounds"])
        self.assertEqual(
            data[2]["sounds"], [{"ipa": "red", "sense_index": "3.1-2"}]
        )

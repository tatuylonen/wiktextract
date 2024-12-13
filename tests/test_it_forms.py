from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.it.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestItForms(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="it"),
            WiktionaryConfig(
                dump_file_lang_code="it", capture_language_codes=None
            ),
        )

    def test_tabs_template(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cane",
            """== {{-it-}} ==
===Sostantivo===
{{Pn|w}} ''m sing''
{{Tabs|cane|cani|cagna|cagne}}

# {{Term|mammalogia|it}} [[animale]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "cani", "tags": ["masculine", "plural"]},
                {"form": "cagna", "tags": ["feminine", "singular"]},
                {"form": "cagne", "tags": ["feminine", "plural"]},
            ],
        )
        self.assertEqual(data[0]["tags"], ["masculine", "singular"])

    def test_linkp_template(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        data = parse_page(
            self.wxr,
            "cagna",
            """== {{-it-}} ==
===Sostantivo===
{{Pn}} ''f sing'' {{Linkp|cagne}}
# {{Term|zoologia|it|mammalogia}} femmina del [[cane]]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [{"form": "cagne", "tags": ["plural"]}],
        )
        self.assertEqual(data[0]["tags"], ["feminine", "singular"])

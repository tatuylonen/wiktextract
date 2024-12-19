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

    def test_it_decl_agg(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        self.wxr.wtp.add_page(
            "Template:It-decl-agg4",
            10,
            """{|
|- align="center"
| &nbsp;
!bgcolor="#FFFFE0" color="#000"|&nbsp;''[[singolare]]''&nbsp;
!bgcolor="#FFFFE0" color="#000"|&nbsp;''[[plurale]]''&nbsp;
|- align="center"
!bgcolor="#FFFFE0" color="#000" colspan="3"|&nbsp;''[[positivo]]''&nbsp;
|- align="center"
!bgcolor="#FFFFE0" color="#000"|&nbsp;''[[maschile]]''&nbsp;
|&nbsp; [[libero]] &nbsp;
|&nbsp; [[liberi]] &nbsp;
|}""",
        )
        data = parse_page(
            self.wxr,
            "libero",
            """== {{-it-}} ==
===Aggettivo===
{{It-decl-agg4|liber}}
{{Pn|w}} ''m sing''
# non [[imprigionato]] o in [[schiavitù]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [{"form": "liberi", "tags": ["positive", "masculine", "plural"]}],
        )

    def test_a_cmp(self):
        self.wxr.wtp.add_page("Template:-en-", 10, "Inglese")
        self.wxr.wtp.add_page(
            "Template:A cmp",
            10,
            "(''comparativo'' '''[[direr]]''', '''more dire''', ''superlativo'' '''[[direst]]''', '''most dire''')",
        )
        data = parse_page(
            self.wxr,
            "dire",
            """== {{-en-}} ==
===Aggettivo===
{{Pn}} {{A cmp|direr|c2=more dire|direst|s2=most dire}}
# [[sinistro]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "direr", "tags": ["comparative"]},
                {"form": "more dire", "tags": ["comparative"]},
                {"form": "direst", "tags": ["superlative"]},
                {"form": "most dire", "tags": ["superlative"]},
            ],
        )

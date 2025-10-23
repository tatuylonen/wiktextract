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

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

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

    def test_pn_template(self):
        self.wxr.wtp.add_page("Template:-it-", 10, "Italiano")
        self.wxr.wtp.add_page(
            "Template:Pn",
            10,
            "'''dire'''<small>&nbsp;([[Appendice:Coniugazioni/Italiano/dire|vai alla coniugazione]])</small>",
        )
        self.wxr.wtp.add_page(
            "Appendice:Coniugazioni/Italiano/dire", 100, "{{It-conj}}"
        )
        self.wxr.wtp.add_page(
            "Template:It-conj",
            10,
            """{|
! colspan="2" | participio presente
| colspan="1" | [[dicente#Italiano|dicente]]
! colspan="2" | participio passato
| colspan="2" | [[detto#Italiano|detto]]
|-
! colspan="1" rowspan="2" | persona
! colspan="3" | singolare
! colspan="3" | plurale
|-
! prima
|-
! indicativo
! io
|-
! passato prossimo
| <div>
  {|
  |-
  | [[ho]] [[detto#Italiano|detto]]</br>[[sono]] [[detto#Italiano|detto]]
  |}</div>
|-
! colspan="1" rowspan="2" | imperativo
! -
! tu
|-
|
|[[di’#Italiano|di’]],</br> non [[dire#Italiano|dire]]
|}""",
        )
        data = parse_page(
            self.wxr,
            "dire",
            """== {{-it-}} ==
===Verbo===
{{Pn|c}} 3° coniugazione
# [[esternare]] ciò che si pensa parlando""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "dicente",
                    "source": "Appendice:Coniugazioni/Italiano/dire",
                    "tags": ["present", "participle"],
                },
                {
                    "form": "detto",
                    "source": "Appendice:Coniugazioni/Italiano/dire",
                    "tags": ["past", "participle"],
                },
                {
                    "form": "ho detto",
                    "raw_tags": ["io"],
                    "tags": ["singular", "first-person", "past", "perfect"],
                    "source": "Appendice:Coniugazioni/Italiano/dire",
                },
                {
                    "form": "sono detto",
                    "raw_tags": ["io"],
                    "tags": ["singular", "first-person", "past", "perfect"],
                    "source": "Appendice:Coniugazioni/Italiano/dire",
                },
                {
                    "form": "di’",
                    "raw_tags": ["tu"],
                    "tags": ["imperative"],
                    "source": "Appendice:Coniugazioni/Italiano/dire",
                },
                {
                    "form": "non dire",
                    "raw_tags": ["tu"],
                    "tags": ["imperative"],
                    "source": "Appendice:Coniugazioni/Italiano/dire",
                },
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtEtymology(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        conf = WiktionaryConfig(
            dump_file_lang_code="pt",
            capture_language_codes=None,
        )
        self.wxr = WiktextractContext(
            Wtp(
                lang_code="pt",
                parser_function_aliases=conf.parser_function_aliases,
            ),
            conf,
        )

    def test_list(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page(
            "Predefinição:etimo2",
            10,
            """:[[Categoria:Entrada de étimo latino (Português)]]Do [[latim]] ''[[oculus#la|oculus]]''<small><sup> ([[:la:oculus|<span title="ver no Wikcionário em latim">la</span>]])</sup></small>.""",
        )
        data = parse_page(
            self.wxr,
            "olho",
            """={{-pt-}}=
==Substantivo==
# órgão
==Etimologia==
{{etimo2|la|oculus|pt}}
:* '''Datação''': [[w:século XIII|século XIII]]""",
        )
        self.assertEqual(
            data[0]["etymology_texts"],
            ["Do latim oculus⁽ˡᵃ⁾.", "Datação: século XIII"],
        )
        self.assertEqual(
            data[0]["categories"], ["Entrada de étimo latino (Português)"]
        )

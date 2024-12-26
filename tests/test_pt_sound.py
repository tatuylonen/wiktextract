from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pt.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPtSound(TestCase):
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

    def test_subsection(self):
        self.wxr.wtp.add_page("Predefinição:-pt-", 10, "Português")
        self.wxr.wtp.add_page(
            "Predefinição:pronúncia",
            10,
            """<span title="Pronúncia da palavra">Pronúncia</span>[[Categoria:Entrada com pronúncia (Português)|olho]]""",
        )
        self.wxr.wtp.add_page("Predefinição:AFI", 10, "{{{1}}}")
        data = parse_page(
            self.wxr,
            "olho",
            """={{-pt-}}=
==Substantivo==
# órgão
=={{pronúncia|pt}}==
===Brasil===
* '''Forma verbal''':
** [[AFI]]: {{AFI|/ˈɔ.ʎʊ/}}
** [[X-SAMPA]]: /"O.LU/""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "ipa": "/ˈɔ.ʎʊ/",
                    "tags": ["Brazil"],
                    "raw_tags": ["Forma verbal"],
                },
                {
                    "ipa": '/"O.LU/',
                    "raw_tags": ["Forma verbal"],
                    "tags": ["X-SAMPA", "Brazil"],
                },
            ],
        )
        self.assertEqual(
            data[0]["categories"], ["Entrada com pronúncia (Português)"]
        )

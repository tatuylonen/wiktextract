from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.nl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestNlLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="nl"),
            WiktionaryConfig(
                dump_file_lang_code="nl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_intens_template(self):
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
====Zelfstandig naamwoord====
# zoogdier
=====Hyponiemen=====
{{intens|nld|1}} [[superhond]]
{{intens|nld|2}} [[kankerhond]], [[tyfushond]]
*[1] [[reu]]
{{L-top|01|[1] honden naar de rol de ze vervullen}}
*[[asielhond]]
{{L-bottom|01}}
*[2] [[christenhond]]""",
        )
        self.assertEqual(
            data[0]["hyponyms"],
            [
                {
                    "word": "superhond",
                    "sense_index": 1,
                    "raw_tags": ["intensivering"],
                },
                {
                    "word": "kankerhond",
                    "sense_index": 2,
                    "raw_tags": ["intensivering"],
                },
                {
                    "word": "tyfushond",
                    "sense_index": 2,
                    "raw_tags": ["intensivering"],
                },
                {"word": "reu", "sense_index": 1},
                {
                    "word": "asielhond",
                    "sense_index": 1,
                    "sense": "honden naar de rol de ze vervullen",
                },
                {"word": "christenhond", "sense_index": 2},
            ],
        )

    def test_nld_template(self):
        self.wxr.wtp.add_page(
            "Sjabloon:nld-rashonden",
            10,
            """<div><div>''<span>[1]</span>&#32;[[hondenrassen]]:''</div><div>
* &#160;[[Amerikaanse cockerspaniël&#35;Nederlands|Amerikaanse cockerspaniël]]&#32;&#160;
</div></div>""",
        )
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
====Zelfstandig naamwoord====
# zoogdier
=====Hyponiemen=====
{{nld-rashonden|1}}""",
        )
        self.assertEqual(
            data[0]["hyponyms"],
            [
                {
                    "sense": "hondenrassen",
                    "sense_index": 1,
                    "word": "Amerikaanse cockerspaniël",
                }
            ],
        )

    def test_expr_template(self):
        data = parse_page(
            self.wxr,
            "hond",
            """==Nederlands==
====Zelfstandig naamwoord====
# zoogdier
=====Spreekwoorden=====
{{expr|De '''hond''' zit hem op de tas.|Hij is gierig, hij is een vrek.}}""",
        )
        self.assertEqual(
            data[0]["proverbs"],
            [
                {
                    "sense": "Hij is gierig, hij is een vrek.",
                    "word": "De hond zit hem op de tas.",
                }
            ],
        )

        data = parse_page(
            self.wxr,
            "lopen",
            """==Nederlands==
====Werkwoord====
# stappen
=====Uitdrukkingen en gezegden=====
{{expr|[1] Tegen de lamp '''lopen'''|betrapt/gesnapt worden}}""",
        )
        self.assertEqual(
            data[0]["proverbs"],
            [
                {
                    "sense": "betrapt/gesnapt worden",
                    "sense_index": 1,
                    "word": "Tegen de lamp lopen",
                }
            ],
        )

    def test_sense_text_after_link(self):
        data = parse_page(
            self.wxr,
            "lopen",
            """==Nederlands==
====Werkwoord====
# stappen
=====Verwante begrippen=====
*[[benen]] = met grote passen lopen""",
        )
        self.assertEqual(
            data[0]["related"],
            [{"sense": "met grote passen lopen", "word": "benen"}],
        )

        data = parse_page(
            self.wxr,
            "omyl",
            """==Tsjechisch==
====Zelfstandig naamwoord====
# fout
=====Typische woordcombinaties=====
* justiční ''omyl'' {{m}}{{i}} –  justitiële ''dwaling''""",
        )
        self.assertEqual(
            data[0]["derived"],
            [
                {
                    "sense": "justitiële dwaling",
                    "word": "justiční omyl",
                    "tags": ["masculine", "inanimate"],
                }
            ],
        )

    def test_abbr(self):
        data = parse_page(
            self.wxr,
            "A grote terts",
            """==Nederlands==
====Zelfstandig naamwoord====
# het akkoord
=====''[[WikiWoordenboek:Afkorting|Afkorting]]''=====
*[[A]]""",
        )
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["abbreviations"], [{"word": "A"}])

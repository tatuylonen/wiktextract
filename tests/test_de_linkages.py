import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.linkage import extract_linkages
from wiktextract.wxr_context import WiktextractContext


class TestDELinkages(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_de_extract_linkages(self):
        test_cases = [
            # https://de.wiktionary.org/wiki/Beispiel
            # Extracts linkages and places them in the correct sense.
            {
                "input": "==== Sinnverwandte Wörter ====\n:[1] [[Beleg]], [[Exempel]]\n:[2] [[Muster]], [[Vorbild]]",
                "page_data": [
                    defaultdict(
                        list,
                        {
                            "senses": [
                                defaultdict(list, {"senseid": "1"}),
                                defaultdict(list, {"senseid": "2"}),
                            ]
                        },
                    )
                ],
                "expected": [
                    {
                        "senses": [
                            {
                                "senseid": "1",
                                "coordinate_terms": ["Beleg", "Exempel"],
                            },
                            {
                                "senseid": "2",
                                "coordinate_terms": ["Muster", "Vorbild"],
                            },
                        ]
                    }
                ],
            },
            # https://de.wiktionary.org/wiki/Beispiel
            # Cleans explanatory text from expressions.
            {
                "input": "====Redewendungen====\n:[[ein gutes Beispiel geben|ein gutes ''Beispiel'' geben]] – als [[Vorbild]] zur [[Nachahmung]] [[dienen]]/[[herausfordern]]",
                "page_data": [defaultdict(list)],
                "expected": [
                    {
                        "expressions": ["ein gutes Beispiel geben"],
                        "senses": [],
                    },
                ],
            },
            # Always places relations in first sense if just one sense.
            {
                "input": "====Synonyme====\n:[[Synonym1]]",
                "page_data": [
                    defaultdict(
                        list, {"senses": [defaultdict(list, {"senseid": "1"})]}
                    )
                ],
                "expected": [
                    {
                        "senses": [{"senseid": "1", "synonyms": ["Synonym1"]}],
                    },
                ],
            },
            # https://de.wiktionary.org/wiki/Kokospalme
            # Ignores modifiers of relations and all other text.
            {
                "input": "====Synonyme====\n:[1] [[Kokosnusspalme]], ''wissenschaftlich:'' [[Cocos nucifera]]",
                "page_data": [
                    defaultdict(
                        list, {"senses": [defaultdict(list, {"senseid": "1"})]}
                    )
                ],
                "expected": [
                    {
                        "senses": [
                            {
                                "senseid": "1",
                                "synonyms": [
                                    "Kokosnusspalme",
                                    "Cocos nucifera",
                                ],
                            }
                        ],
                    },
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                root = self.wxr.wtp.parse(case["input"])

                extract_linkages(self.wxr, case["page_data"], root.children[0])

                self.assertEqual(case["page_data"], case["expected"])

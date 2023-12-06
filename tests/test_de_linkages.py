import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.linkage import extract_linkages
from wiktextract.extractor.de.models import Sense, WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestDELinkages(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_word_entry(self) -> WordEntry:
        return WordEntry(word="Beispiel", lang_code="de", lang_name="Deutsch")

    def test_de_extract_linkages(self):
        test_cases = [
            # https://de.wiktionary.org/wiki/Beispiel
            # Extracts linkages and places them in the correct sense.
            {
                "input": "==== Sinnverwandte Wörter ====\n:[1] [[Beleg]], [[Exempel]]\n:[2] [[Muster]], [[Vorbild]]",
                "senses": [Sense(senseid="1"), Sense(senseid="2")],
                "expected": {
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
                },
            },
            # https://de.wiktionary.org/wiki/Beispiel
            # Cleans explanatory text from expressions.
            {
                "input": "====Redewendungen====\n:[[ein gutes Beispiel geben|ein gutes ''Beispiel'' geben]] – als [[Vorbild]] zur [[Nachahmung]] [[dienen]]/[[herausfordern]]",
                "senses": [Sense()],
                "expected": {
                    "senses": [
                        {
                            "expressions": ["ein gutes Beispiel geben"],
                        }
                    ]
                },
            },
            # Always places relations in first sense if just one sense.
            {
                "input": "====Synonyme====\n:[[Synonym1]]",
                "senses": [Sense(senseid="1")],
                "expected": {
                    "senses": [{"senseid": "1", "synonyms": ["Synonym1"]}],
                },
            },
            # https://de.wiktionary.org/wiki/Kokospalme
            # Ignores modifiers of relations and all other text.
            {
                "input": "====Synonyme====\n:[1] [[Kokosnusspalme]], ''wissenschaftlich:'' [[Cocos nucifera]]",
                "senses": [Sense(senseid="1")],
                "expected": {
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
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                root = self.wxr.wtp.parse(case["input"])

                word_entry = self.get_default_word_entry()
                word_entry.senses = case["senses"]

                extract_linkages(self.wxr, word_entry, root.children[0])

                self.assertEqual(
                    word_entry.model_dump(
                        exclude_defaults=True,
                        exclude={"word", "lang_code", "lang_name"},
                    ),
                    case["expected"],
                )

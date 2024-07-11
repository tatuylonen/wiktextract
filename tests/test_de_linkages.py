import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.linkage import extract_linkages
from wiktextract.extractor.de.models import WordEntry
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
        return WordEntry(word="Beispiel", lang_code="de", lang="Deutsch")

    def test_de_extract_linkages(self):
        test_cases = [
            # https://de.wiktionary.org/wiki/Beispiel
            # Extracts linkages and places them in the correct sense.
            {
                "input": """==== Sinnverwandte Wörter ====
:[1] [[Beleg]], [[Exempel]]
:[2] [[Muster]], [[Vorbild]]""",
                "expected": {
                    "coordinate_terms": [
                        {"word": "Beleg", "sense_id": "1"},
                        {"word": "Exempel", "sense_id": "1"},
                        {"word": "Muster", "sense_id": "2"},
                        {"word": "Vorbild", "sense_id": "2"},
                    ],
                },
            },
            # https://de.wiktionary.org/wiki/Beispiel
            # Cleans explanatory text from expressions.
            {
                "input": "====Redewendungen====\n:[[ein gutes Beispiel geben|"
                "ein gutes ''Beispiel'' geben]] – als [[Vorbild]] zur "
                "[[Nachahmung]] [[dienen]]/[[herausfordern]]",
                "expected": {
                    "expressions": [
                        {
                            "note": "als Vorbild zur Nachahmung "
                            "dienen/herausfordern",
                            "word": "ein gutes Beispiel geben",
                        }
                    ],
                },
            },
            # Always places relations in first sense if just one sense.
            {
                "input": "====Synonyme====\n:[[Synonym1]]",
                "expected": {"synonyms": [{"word": "Synonym1"}]},
            },
            # https://de.wiktionary.org/wiki/Kokospalme
            # Ignores modifiers of relations and all other text.
            {
                "input": "====Synonyme====\n:[1] [[Kokosnusspalme]], ''wissenschaftlich:'' [[Cocos nucifera]]",
                "expected": {
                    "synonyms": [
                        {"word": "Kokosnusspalme", "sense_id": "1"},
                        {"word": "Cocos nucifera", "sense_id": "1"},
                    ],
                },
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.wxr.wtp.start_page("")
                root = self.wxr.wtp.parse(case["input"])
                word_entry = self.get_default_word_entry()
                extract_linkages(self.wxr, word_entry, root.children[0])
                self.assertEqual(
                    word_entry.model_dump(
                        exclude_defaults=True,
                        exclude={"word", "lang_code", "lang"},
                    ),
                    case["expected"],
                )

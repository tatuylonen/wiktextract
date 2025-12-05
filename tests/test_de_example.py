import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.example import extract_examples
from wiktextract.extractor.de.models import Sense, WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestDEExample(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def get_default_page_data(self) -> list[WordEntry]:
        return [WordEntry(word="Beispiel", lang_code="de", lang="Deutsch")]

    def test_de_extract_examples(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            ":[1] example1A \n:[1] example1B\n:[2] example2\n:[3] example3"
        )

        page_data = self.get_default_page_data()
        page_data[-1].senses = [Sense(sense_index="1"), Sense(sense_index="2")]

        extract_examples(self.wxr, page_data[-1], root)

        senses = [
            s.model_dump(exclude_defaults=True) for s in page_data[-1].senses
        ]
        self.assertEqual(
            senses,
            [
                {
                    "examples": [
                        {"text": "example1A"},
                        {"text": "example1B"},
                    ],
                    "sense_index": "1",
                },
                {
                    "examples": [{"text": "example2"}],
                    "sense_index": "2",
                },
                {
                    "examples": [{"text": "example3"}],
                    "sense_index": "3",
                    "tags": ["no-gloss"],
                },
            ],
        )

    def test_de_extract_example_with_reference(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(":[1] example1 <ref>ref1A</ref>")

        page_data = self.get_default_page_data()
        page_data[-1].senses = [Sense(sense_index="1")]

        extract_examples(self.wxr, page_data[-1], root)

        senses = [
            s.model_dump(exclude_defaults=True) for s in page_data[-1].senses
        ]
        self.assertEqual(
            senses,
            [
                {
                    "examples": [
                        {
                            "text": "example1",
                            "ref": "ref1A",
                        },
                    ],
                    "sense_index": "1",
                },
            ],
        )

    def test_nested_example_list(self):
        self.wxr.wtp.start_page("auf")
        root = self.wxr.wtp.parse(""":[1]
::[1a] Er stand ''auf'' dem Dach.
::[1b] Er stieg ''aufs'' Dach.""")
        page_data = [
            WordEntry(
                lang="Deutsch",
                lang_code="de",
                pos="prep",
                senses=[
                    Sense(glosses=["gloss 1a"], sense_index="1a"),
                    Sense(glosses=["gloss 1b"], sense_index="1b"),
                ],
                word="auf",
            )
        ]
        extract_examples(self.wxr, page_data[-1], root)
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in page_data[-1].senses],
            [
                {
                    "examples": [
                        {
                            "text": "Er stand auf dem Dach.",
                            "bold_text_offsets": [(9, 12)],
                        }
                    ],
                    "glosses": ["gloss 1a"],
                    "sense_index": "1a",
                },
                {
                    "examples": [
                        {
                            "text": "Er stieg aufs Dach.",
                            "bold_text_offsets": [(9, 13)],
                        }
                    ],
                    "glosses": ["gloss 1b"],
                    "sense_index": "1b",
                },
            ],
        )

    def test_example_translation(self):
        self.wxr.wtp.start_page("bot")
        root = self.wxr.wtp.parse(""":[1] Un ''bot'' son quinze litres:
::Ein ''Bot'' (Weinschlauch) hat ca. fünfzehn Liter.""")
        page_data = [
            WordEntry(
                lang="Katalanisch",
                lang_code="ca",
                pos="noun",
                senses=[
                    Sense(glosses=["gloss 1"], sense_index="1"),
                ],
                word="bot",
            )
        ]
        extract_examples(self.wxr, page_data[-1], root)
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in page_data[-1].senses],
            [
                {
                    "examples": [
                        {
                            "text": "Un bot son quinze litres:",
                            "bold_text_offsets": [(3, 6)],
                            "translation": "Ein Bot (Weinschlauch) hat ca. fünfzehn Liter.",
                        }
                    ],
                    "glosses": ["gloss 1"],
                    "sense_index": "1",
                },
            ],
        )

    def test_match_two_sense_indexes(self):
        self.wxr.wtp.start_page("albanische Sprache")
        root = self.wxr.wtp.parse(":[1, 2] (1874) „Nach den „Beiträgen“ Hahn's")
        page_data = [
            WordEntry(
                lang="Deutsch",
                lang_code="de",
                pos="noun",
                senses=[
                    Sense(glosses=["gloss 1"], sense_index="1"),
                    Sense(glosses=["gloss 2"], sense_index="2"),
                ],
                word="albanische Sprache",
            )
        ]
        extract_examples(self.wxr, page_data[-1], root)
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in page_data[0].senses],
            [
                {
                    "examples": [
                        {
                            "text": "(1874) „Nach den „Beiträgen“ Hahn's",
                        }
                    ],
                    "glosses": ["gloss 1"],
                    "sense_index": "1",
                },
                {
                    "examples": [
                        {
                            "text": "(1874) „Nach den „Beiträgen“ Hahn's",
                        }
                    ],
                    "glosses": ["gloss 2"],
                    "sense_index": "2",
                },
            ],
        )

    def test_tag_list(self):
        self.wxr.wtp.start_page("Feber")
        root = self.wxr.wtp.parse("""*''[[Deutschland]]:''
:[1] „Den ganzen ''‚Feber‘'' hörte man lapidar""")
        page_data = [
            WordEntry(
                lang="Deutsch",
                lang_code="de",
                pos="noun",
                senses=[
                    Sense(glosses=["gloss 1"], sense_index="1"),
                ],
                word="albanische Sprache",
            )
        ]
        extract_examples(self.wxr, page_data[-1], root)
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in page_data[0].senses],
            [
                {
                    "examples": [
                        {
                            "tags": ["Germany"],
                            "text": "„Den ganzen ‚Feber‘ hörte man lapidar",
                            "bold_text_offsets": [(12, 19)],
                        }
                    ],
                    "glosses": ["gloss 1"],
                    "sense_index": "1",
                },
            ],
        )

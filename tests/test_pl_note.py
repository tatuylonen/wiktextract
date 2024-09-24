from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.models import Sense, WordEntry
from wiktextract.extractor.pl.note import extract_note_section
from wiktextract.wxr_context import WiktextractContext


class TestPlNote(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_pies(self):
        self.wxr.wtp.start_page("pies")
        root = self.wxr.wtp.parse(""": (1.1) zobacz też: [[Indeks:Polski - Ssaki]]
: (1.1) zobacz też: [[Indeks:Polski - Rasy psów]]""")
        base_data = WordEntry(
            word="pies", lang="język polski", lang_code="pl", pos="noun"
        )
        page_data = [
            WordEntry(
                word="pies",
                lang="język polski",
                lang_code="pl",
                pos="noun",
                senses=[Sense(sense_index="1.1")],
            ),
            WordEntry(
                word="pies",
                lang="język polski",
                lang_code="pl",
                pos="noun",
                senses=[Sense(sense_index="2.1")],
            ),
        ]
        extract_note_section(self.wxr, page_data, base_data, root)
        self.assertEqual(
            [n.model_dump(exclude_defaults=True) for n in page_data[0].notes],
            [
                {
                    "text": "zobacz też: Indeks:Polski - Ssaki",
                    "sense_index": "1.1",
                },
                {
                    "text": "zobacz też: Indeks:Polski - Rasy psów",
                    "sense_index": "1.1",
                },
            ],
        )
        self.assertEqual(page_data[1].notes, [])

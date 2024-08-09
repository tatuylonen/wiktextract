from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.linkage import extract_linkage_section
from wiktextract.extractor.pl.models import Linkage, Sense, WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestPlLinkage(TestCase):
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
        self.wxr.wtp.add_page("Szablon:neutr", 10, "neutr.")

        root = self.wxr.wtp.parse(""": (1.1) [[czworonożny przyjaciel]]
: (2.1) [[pała]]; {{neutr}} [[policjant]]""")
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
        extract_linkage_section(self.wxr, page_data, root, "synonyms", "pl")
        self.assertEqual(
            page_data[0].synonyms,
            [Linkage(word="czworonożny przyjaciel", sense_index="1.1")],
        )
        self.assertEqual(
            page_data[1].synonyms,
            [
                Linkage(word="pała", sense_index="2.1"),
                Linkage(
                    word="policjant", tags=["neutral"], sense_index="2.1"
                ),
            ],
        )

    def test_plain_text(self):
        self.wxr.wtp.start_page("polski")
        root = self.wxr.wtp.parse(
            ": (1.1) [[narodowość]] polska • [[obywatelstwo]] polskie • [[wpływ]]y polskie • [[murzyn polski]]"
        )
        page_data = [
            WordEntry(
                word="polski",
                lang="język polski",
                lang_code="pl",
                pos="adj",
                senses=[Sense(sense_index="1.1")],
            )
        ]
        extract_linkage_section(self.wxr, page_data, root, "related", "pl")
        self.assertEqual(
            [r.model_dump(exclude_defaults=True) for r in page_data[0].related],
            [
                {"word": "narodowość polska", "sense_index": "1.1"},
                {"word": "obywatelstwo polskie", "sense_index": "1.1"},
                {"word": "wpływy polskie", "sense_index": "1.1"},
                {"word": "murzyn polski", "sense_index": "1.1"},
            ],
        )

    def test_comma_separator(self):
        self.wxr.wtp.start_page("polski")
        self.wxr.wtp.add_page("Szablon:stpol", 10, "st.pol.")
        self.wxr.wtp.add_page("Szablon:żart", 10, "żart.")
        self.wxr.wtp.add_page("Szablon:poet", 10, "poet.")
        root = self.wxr.wtp.parse(
            ": (1.1) {{stpol}} [[lacki]], {{żart}} {{poet}} [[sarmacki]]"
        )
        page_data = [
            WordEntry(
                word="polski",
                lang="język polski",
                lang_code="pl",
                pos="adj",
                senses=[Sense(sense_index="1.1")],
            )
        ]
        extract_linkage_section(self.wxr, page_data, root, "synonyms", "pl")
        self.assertEqual(
            [
                r.model_dump(exclude_defaults=True)
                for r in page_data[0].synonyms
            ],
            [
                {
                    "word": "lacki",
                    "sense_index": "1.1",
                    "raw_tags": ["st.pol."],
                },
                {
                    "word": "sarmacki",
                    "sense_index": "1.1",
                    "raw_tags": ["żart."],
                    "tags": ["poetic"],
                },
            ],
        )

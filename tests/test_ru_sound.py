from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ru.models import WordEntry
from wiktextract.extractor.ru.pronunciation import extract_homophone_section
from wiktextract.wxr_context import WiktextractContext


class TestRUSound(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ru"),
            WiktionaryConfig(
                dump_file_lang_code="ru", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_homophone_section_list(self):
        self.wxr.wtp.start_page("ไทย")
        root = self.wxr.wtp.parse("* [[ไท]], [[ไถ]]")
        data = WordEntry(lang="th", lang_code="Тайский", word="ไทย")
        extract_homophone_section(self.wxr, data, root)
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.sounds],
            [{"homophones": ["ไท", "ไถ"]}]
        )

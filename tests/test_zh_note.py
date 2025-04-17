from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.note import extract_note
from wiktextract.wxr_context import WiktextractContext


class TestZhNote(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"),
            WiktionaryConfig(
                capture_language_codes=None, dump_file_lang_code="zh"
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_note_list(self):
        # https://zh.wiktionary.org/wiki/オタク
        self.wxr.wtp.start_page("オタク")
        root = self.wxr.wtp.parse("* note list 1\n* note list 2")
        page_data = [
            WordEntry(word="オタク", lang_code="ja", lang="日語", pos="noun")
        ]
        extract_note(self.wxr, page_data, root)
        self.assertEqual(page_data[-1].notes, ["note list 1", "note list 2"])

    def test_note_no_list(self):
        # https://zh.wiktionary.org/wiki/clavarder
        self.wxr.wtp.start_page("clavarder")
        root = self.wxr.wtp.parse("note text")
        page_data = [
            WordEntry(word="オタク", lang_code="fr", lang="法語", pos="verb")
        ]
        extract_note(self.wxr, page_data, root)
        self.assertEqual(page_data[-1].notes, ["note text"])

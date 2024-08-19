from unittest import TestCase
from unittest.mock import Mock

from wikitextprocessor import Wtp

from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.note import extract_note
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestNote(TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(Wtp(lang_code="zh"), Mock())

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

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

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.note import extract_note_section
from wiktextract.extractor.zh.page import parse_page
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
        data = WordEntry(word="オタク", lang_code="ja", lang="日語", pos="noun")
        extract_note_section(self.wxr, data, root)
        self.assertEqual(data.notes, ["note list 1", "note list 2"])

    def test_note_no_list(self):
        # https://zh.wiktionary.org/wiki/clavarder
        self.wxr.wtp.start_page("clavarder")
        root = self.wxr.wtp.parse("note text")
        data = WordEntry(word="オタク", lang_code="fr", lang="法語", pos="verb")
        extract_note_section(self.wxr, data, root)
        self.assertEqual(data.notes, ["note text"])

    def test_nested_lists(self):
        self.wxr.wtp.add_page("Template:w", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Template:defdate", 10, "（{{{1}}}）")
        self.wxr.wtp.add_page("Template:BCE", 10, "公元前")
        page_data = parse_page(
            self.wxr,
            "中國",
            """==漢語==
===詞源1===
etymology text
====專有名詞====
# gloss
=====使用說明=====
這個詞在歷史上分別指以下各國家和地區：
* {{w|西周}} {{defdate|{{BCE}} 1046–771}}：
*: 在商代方國聯盟制度下商王畿地區正好位於天下的中央。
* {{w|東周}} {{defdate|{{BCE}} 770–221}}：
*: 涵蓋[[黃河]]上游的所有流域。""",
        )
        self.assertEqual(
            page_data[0]["notes"],
            [
                "這個詞在歷史上分別指以下各國家和地區：",
                "西周 （公元前 1046–771）：在商代方國聯盟制度下商王畿地區正好位於天下的中央。",
                "東周 （公元前 770–221）：涵蓋黃河上游的所有流域。",
            ],
        )

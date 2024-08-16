from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.etymology import extract_etymology_section
from wiktextract.extractor.ja.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestJaEtymology(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ja"),
            WiktionaryConfig(
                dump_file_lang_code="ja",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_level3(self):
        self.wxr.wtp.start_page("うつる")
        self.wxr.wtp.add_page(
            "テンプレート:etyl",
            10,
            "[[w:古典日本語|古典日本語]][[カテゴリ:日本語]][[カテゴリ:日本語_古典日本語由来]]",
        )
        base_data = WordEntry(lang="日本語", lang_code="ja", word="うつる")
        root = self.wxr.wtp.parse("""===語源===
{{etyl|ojp|ja}}「[[#古典日本語|うつる]]」 < 「[[うつす]]」の自動詞形""")
        extract_etymology_section(
            self.wxr, [base_data], base_data, root.children[0]
        )
        self.assertEqual(
            base_data.etymology_texts,
            ["古典日本語「うつる」 < 「うつす」の自動詞形"],
        )
        self.assertEqual(
            base_data.categories, ["日本語", "日本語_古典日本語由来"]
        )

    def test_level4(self):
        self.wxr.wtp.start_page("東京")
        base_data = WordEntry(lang="日本語", lang_code="ja", word="東京")
        page_data = [base_data.model_copy(deep=True)]
        root = self.wxr.wtp.parse("""====語源====
* [[京都]]に対して[[東]]にある[[京]]（[[都]]）であることから""")
        extract_etymology_section(
            self.wxr, page_data, base_data, root.children[0]
        )
        self.assertEqual(
            page_data[0].etymology_texts,
            ["京都に対して東にある京（都）であることから"],
        )

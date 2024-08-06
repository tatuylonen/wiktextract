from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.linkage import extract_linkage_section
from wiktextract.extractor.ja.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestJaLinkage(TestCase):
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

    def test_ruby(self):
        self.wxr.wtp.start_page("全然")
        self.wxr.wtp.add_page(
            "テンプレート:おくりがな2",
            10,
            "<ruby>[[全]]<rp>（</rp><rt>[[まったく|まった]]</rt><rp>）</rp></ruby>く",
        )
        data = WordEntry(word="全然", lang="日本語", lang_code="ja", pos="adv")
        root = self.wxr.wtp.parse("* {{おくりがな2|全|まった|く|まったく}}")
        extract_linkage_section(self.wxr, data, root, "synonyms")
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in data.synonyms],
            [{"word": "全く", "ruby": [("全", "まった")]}],
        )

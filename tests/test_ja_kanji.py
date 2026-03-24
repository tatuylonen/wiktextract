import unittest

from wikitextprocessor import Wtp
from wikitextprocessor.parser import NodeKind

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.kanji import extract_ja_kanji
from wiktextract.extractor.ja.models import Sound, WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestExtractJaKanji(unittest.TestCase):
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

    def _extract_ja_kanji(self, template: str) -> WordEntry:
        word = "filler"
        self.wxr.wtp.start_page(word)
        root = self.wxr.wtp.parse(template)
        t_node = next(root.find_child(NodeKind.TEMPLATE))
        data = WordEntry(word=word, lang_code="ja", lang="日本語")
        extract_ja_kanji(self.wxr, data, t_node)
        return data

    def test_extract_ja_kanji_1(self) -> None:
        # https://ja.wiktionary.org/wiki/韻#日本語
        data = self._extract_ja_kanji(
            "{{ja-kanji|常用=イン|呉音=ウン|漢音=ウン|慣用音=イン<ヰン|訓=ひびき}}"
        )
        self.assertEqual(
            data.sounds,
            [
                Sound(other="ウン", tags=["go-on"]),
                Sound(other="ウン", tags=["kan-on"]),
                Sound(other="イン", tags=["kan-yo-on", "joyo"]),
                Sound(other="ひびき", tags=["kun"]),
            ],
        )

    def test_extract_ja_kanji_2(self) -> None:
        # https://ja.wiktionary.org/wiki/文#日本語
        data = self._extract_ja_kanji(
            "{{ja-kanji|常用=ブン,モン,ふみ|施策=教育:1|呉音=モン|漢音=ブン|訓=ふみ,あや,かざ-る}}"
        )
        self.assertEqual(
            data.sounds,
            [
                Sound(other="モン", tags=["go-on", "joyo"]),
                Sound(other="ブン", tags=["kan-on", "joyo"]),
                Sound(other="ふみ", tags=["kun", "joyo"]),
                Sound(other="あや", tags=["kun"]),
                Sound(other="かざ-る", tags=["kun"]),
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.conjugation import extract_conjugation_section
from wiktextract.extractor.ja.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestJaConjugation(TestCase):
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

    def test_ja_conjugation_table(self):
        self.wxr.wtp.add_page(
            "テンプレート:日本語下一段活用",
            10,
            """<div>
<div>活用と結合例</div>
<div class="NavContent">
{| class="wikitable"
|+ ま-ぜる 動詞活用表<small>（[[付録:日本語の活用|日本語の活用]]）</small>
! colspan="7" | [[下一段活用|ザ行下一段活用]]
|-
! [[仮定形]] !! [[命令形]]
|-
| ぜれ || ぜろ<br />ぜよ
|}
{| class="wikitable" style="text-align:center"
|+ 各活用形の基礎的な結合例
! 意味 !! 語形 !! 結合
|-
| 命令 || まぜろ<br />まぜよ || 命令形のみ
|}
</div></div>[[カテゴリ:日本語|ませる まぜる]][[カテゴリ:日本語 動詞|ませる まぜる]][[カテゴリ:日本語 動詞 ザ下一|ませる まぜる]]""",
        )
        self.wxr.wtp.start_page("まぜる")
        word_entry = WordEntry(lang="日本語", lang_code="ja", word="まぜる")
        root = self.wxr.wtp.parse("{{日本語下一段活用}}")
        extract_conjugation_section(self.wxr, word_entry, root)
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in word_entry.forms],
            [
                {
                    "form": "ぜれ",
                    "raw_tags": ["ザ行下一段活用"],
                    "tags": ["hypothetical"],
                },
                {
                    "form": "ぜろ",
                    "raw_tags": ["ザ行下一段活用"],
                    "tags": ["imperative"],
                },
                {
                    "form": "ぜよ",
                    "raw_tags": ["ザ行下一段活用"],
                    "tags": ["imperative"],
                },
                {
                    "form": "まぜろ",
                    "raw_tags": ["各活用形の基礎的な結合例", "語形"],
                    "tags": ["imperative"],
                },
                {
                    "form": "まぜよ",
                    "raw_tags": ["各活用形の基礎的な結合例", "語形"],
                    "tags": ["imperative"],
                },
                {
                    "form": "命令形のみ",
                    "raw_tags": ["各活用形の基礎的な結合例", "結合"],
                    "tags": ["imperative"],
                },
            ],
        )
        self.assertEqual(
            word_entry.categories,
            ["日本語", "日本語 動詞", "日本語 動詞 ザ下一"],
        )

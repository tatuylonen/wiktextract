from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.page import parse_page
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

    def test_ja_conjugation_table_ichidan(self):
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
! [[語幹]] !! [[命令形]]
|-
| ま || ぜろ<br />ぜよ
|}
{| class="wikitable" style="text-align:center"
|+ 各活用形の基礎的な結合例
! 意味 !! 語形 !! 結合
|-
| 命令 || まぜろ<br />まぜよ || 命令形のみ
|}
</div></div>[[カテゴリ:日本語|ませる まぜる]]""",
        )
        data = parse_page(
            self.wxr,
            "まぜる",
            """=={{L|ja}}==
===動詞===
#ある物に他の物を[[くわえる|加え]]て一つにする。[[混合]]する。
====活用====
{{日本語下一段活用}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "まぜろ",
                    "raw_tags": ["ま-ぜる 動詞活用表（日本語の活用）"],
                    "tags": ["za-row", "shimoichidan", "ichidan", "imperative"],
                },
                {
                    "form": "まぜよ",
                    "raw_tags": ["ま-ぜる 動詞活用表（日本語の活用）"],
                    "tags": ["za-row", "shimoichidan", "ichidan", "imperative"],
                },
                {
                    "form": "まぜろ",
                    "raw_tags": ["各活用形の基礎的な結合例", "命令形のみ"],
                    "tags": ["imperative"],
                },
                {
                    "form": "まぜよ",
                    "raw_tags": ["各活用形の基礎的な結合例", "命令形のみ"],
                    "tags": ["imperative"],
                },
            ],
        )
        self.assertEqual(data[0]["tags"], ["za-row", "shimoichidan", "ichidan"])
        self.assertEqual(data[0]["categories"], ["日本語"])

    def test_alter_section_tag(self):
        data = parse_page(
            self.wxr,
            "豆腐",
            """==日本語==
===異表記・別形===
*[[豆富]] （[[好字]]による書き換え、非標準的）
===名詞===
#[[大豆]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "豆富",
                    "tags": ["alternative"],
                    "raw_tags": ["好字による書き換え、非標準的"],
                }
            ],
        )
        data = parse_page(
            self.wxr,
            "color",
            """==英語==
===異表記・別形===
*[[colour]] (アメリカ合衆国以外)
===名詞===
# [[いろ|色]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "colour",
                    "tags": ["alternative"],
                    "raw_tags": ["アメリカ合衆国以外"],
                }
            ],
        )

    def test_ja_conj_table_missing_form(self):
        self.wxr.wtp.add_page(
            "テンプレート:日本語タルト活用",
            10,
            """<div class="NavFrame" style="clear:both">
<div class="NavHead" align="left">活用と結合例</div>
<div class="NavContent">
{| class="wikitable" style="text-align:center"
|+ 全然 形容動詞活用表<small>（[[付録:日本語の活用|日本語の活用]]）</small>
! colspan="7" | [[タルト活用|タルト活用]]
|-
! [[語幹]] !! [[未然形]] !! [[連用形]] !! [[終止形]]
|-
| 全然 || (無し) || と || (たり)
|}
</div></div>""",
        )
        data = parse_page(
            self.wxr,
            "全然",
            """=={{L|ja}}==
===形容動詞===
#まったくの、完全な、全面的な。
{{日本語タルト活用}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "全然と",
                    "raw_tags": [
                        "全然 形容動詞活用表（日本語の活用）",
                        "タルト活用",
                    ],
                    "tags": ["continuative"],
                },
                {
                    "form": "全然たり",
                    "raw_tags": [
                        "全然 形容動詞活用表（日本語の活用）",
                        "タルト活用",
                    ],
                    "tags": ["terminal"],
                },
            ],
        )

    def test_ja_conj_no_stem(self):
        self.wxr.wtp.add_page(
            "テンプレート:日本語上一段活用",
            10,
            """<div class="NavFrame" style="clear:both">
<div class="NavHead" align="left">活用と結合例</div>
<div class="NavContent">
{| class="wikitable" style="text-align:center"
|+ にる 動詞活用表<small>（[[付録:日本語の活用|日本語の活用]]）</small>
! colspan="7" | [[上一段活用|ナ行上一段活用]]
|-
! [[語幹]] !! [[未然形]]
|-
| (語幹無し) || に
|}
</div></div>""",
        )
        data = parse_page(
            self.wxr,
            "にる",
            """=={{L|ja}}==
===動詞：似る===
#（他の比較よりも）[[共通]]の[[性質]]が[[おおい|多く]]ある。
====活用====
{{日本語上一段活用}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "に",
                    "raw_tags": ["にる 動詞活用表（日本語の活用）"],
                    "tags": [
                        "na-row",
                        "kamiichidan",
                        "ichidan",
                        "imperfective",
                    ],
                }
            ],
        )

    def test_ja_conj_ruby(self):
        self.wxr.wtp.add_page(
            "テンプレート:日本語形容動詞活用",
            10,
            """<div class="NavFrame" style="clear:both">
<div class="NavHead" align="left">活用と結合例</div>
<div class="NavContent">
{| class="wikitable" style="text-align:center"
|+ <ruby>準静的<rp>（</rp><rt>じゅんせいてき</rt><rp>）</rp></ruby>-だ 形容動詞活用表<small>（[[付録:日本語の活用|日本語の活用]]）</small>
! colspan="7" | [[ダ活用|ダ活用]]
|-
! [[語幹]] !! [[未然形]]
|-
| <ruby>準静的<rp>（</rp><rt>じゅんせいてき</rt><rp>）</rp></ruby> || だろ
|}
{| class="wikitable" style="text-align:center"
|+ 各活用形の基礎的な結合例
! 意味 !! 語形 !! 結合
|-
| 言い切り || <ruby>準静的<rp>（</rp><rt>じゅんせいてき</rt><rp>）</rp></ruby>だ || 終止形のみ
|-
| 様態 || <ruby>準静的<rp>（</rp><rt>じゅんせいてき</rt><rp>）</rp></ruby>そうだ || 語幹 + [[そうだ]]
|}
</div></div>""",
        )
        data = parse_page(
            self.wxr,
            "準静的",
            """=={{ja}}==
===形容動詞===
# [[状態]]の[[変化]]の形態の一種で
====活用====
{{日本語形容動詞活用|{{ruby|準静的|じゅんせいてき}}|だ}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "準静的だろ",
                    "raw_tags": [
                        "準静的（じゅんせいてき）-だ 形容動詞活用表（日本語の活用）",
                        "ダ活用",
                    ],
                    "ruby": [("準静的", "じゅんせいてき")],
                    "tags": ["imperfective"],
                },
                {
                    "form": "準静的だ",
                    "raw_tags": ["各活用形の基礎的な結合例", "終止形のみ"],
                    "ruby": [("準静的", "じゅんせいてき")],
                    "tags": ["definitive", "terminal"],
                },
                {
                    "form": "準静的そうだ",
                    "raw_tags": ["各活用形の基礎的な結合例", "語幹 + そうだ"],
                    "ruby": [("準静的", "じゅんせいてき")],
                    "tags": ["appearance", "stem"],
                },
            ],
        )

    def test_ja_auxiliary_verb_conj(self):
        self.wxr.wtp.add_page(
            "テンプレート:日本語助動詞活用",
            10,
            """{| class="wikitable" style="text-align:center"
! 未然形 !! 連用形 !! 終止形 !! 連体形 !! 仮定形 !! 命令形 !! 活用型
|- align=center
| させ || させ || させる || させる || させれ || させろ<br>させよ || 動詞下一段型
|}""",
        )
        data = parse_page(
            self.wxr,
            "させる",
            """=={{L|ja}}==
===助動詞===
#（[[使役]]）勧めたり命じたりして行う・従うようにする。
====活用====
{{日本語助動詞活用|させ|させ|させる|させる|させれ|させろ<br>させよ|動詞下一段型}}""",
        )
        self.assertEqual(
            data[0]["forms"][-2:],
            [
                {
                    "form": "させろ",
                    "raw_tags": ["動詞下一段型"],
                    "tags": ["imperative"],
                },
                {
                    "form": "させよ",
                    "raw_tags": ["動詞下一段型"],
                    "tags": ["imperative"],
                },
            ],
        )

    def test_classical_ja_conj(self):
        self.wxr.wtp.add_page(
            "テンプレート:古典日本語ク活用",
            10,
            """
{| class="wikitable" style="text-align:center"
|-
!基本形!!語幹!!未然形!!連用形!!終止形!!連体形!!已然形!!命令形!!活用の種類
|-
|rowspan=2|とし
|rowspan=2|と
| (-く)
|○
|○
|○
|○
|○
|rowspan=2|ク活用
|-
| -から
|○
|○
|○
|○
|○
|}[[カテゴリ:古典日本語]]
""",
        )
        data = parse_page(
            self.wxr,
            "とし",
            """== 古典日本語 ==
=== 形容詞 ===
# [[迅速]]な。
====活用====
{{古典日本語ク活用|と}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "とく",
                    "raw_tags": ["ク活用"],
                    "tags": ["imperfective"],
                },
                {
                    "form": "とから",
                    "raw_tags": ["ク活用"],
                    "tags": ["imperfective"],
                },
            ],
        )
        self.assertEqual(data[0]["categories"], ["古典日本語"])

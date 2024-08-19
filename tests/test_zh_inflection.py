from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.inflection import extract_inflections
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestInflection(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"),
            WiktionaryConfig(
                capture_language_codes=None, dump_file_lang_code="zh"
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_zh_forms(self):
        page_data = parse_page(
            self.wxr,
            "維基詞典",
            """==漢語==
{{zh-forms|s=维基词典|type=22}}

===專有名詞===

# 一個在線的自由多語言[[詞典]]，由維基媒體基金會建立。""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [{"form": "维基词典", "tags": ["Simplified Chinese"]}],
        )

    def test_zh_forms_lit(self):
        page_data = parse_page(
            self.wxr,
            "玉石俱焚",
            """==漢語==
{{zh-forms|lit=玉和石一起燒成灰}}

===成語===

# 比喻[[好]]的和[[壞]]的一同[[毀滅]]。""",
        )
        self.assertEqual(page_data[0]["literal_meaning"], "玉和石一起燒成灰")

    def test_zh_forms_alt(self):
        page_data = parse_page(
            self.wxr,
            "新婦",
            """==漢語==
{{zh-forms|alt=新抱-粵語,心抱-粵語,新府-陽江粵語|1=-}}

===名詞===

# [[新娘]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "新抱", "raw_tags": ["粵語"]},
                {"form": "心抱", "raw_tags": ["粵語"]},
                {"form": "新府", "raw_tags": ["陽江粵語"]},
            ],
        )

    def test_ja_suru(self):
        self.wxr.wtp.add_page(
            "Template:ja-suru",
            10,
            """<div>
{|
|-
! colspan="4" | 活用形
|-
! 假定形<br/>（<span class="Jpan" lang="ja">[[仮定形#日語|-{仮定形}-]]</span>）
||<span class="Jpan" lang="ja-Jpan">腐敗すれ</span>
| | <span class="Jpan" lang="ja-Jpan">ふはいすれ</span>
| <span class="Latn" lang="ja-Latn">fuhai sure</span>
|-
! <span class="Jpan" lang="ja">[[命令形#日語|-{命令形}-]]</span>
||<span class="Jpan" lang="ja-Jpan">腐敗せよ&sup1;<br/>腐敗しろ&sup2;</span>
| | <span class="Jpan" lang="ja-Jpan">ふはいせよ&sup1;<br/>ふはいしろ&sup2;</span>
| <span class="Latn" lang="ja-Latn">fuhai seyo&sup1;<br/>fuhai shiro&sup2;</span>
|-
| colspan="5" | <small>&sup1; 書面語</small><br/>
<small>&sup2; 口語</small>
|}
</div>""",
        )
        page_data = [
            WordEntry(lang="日語", lang_code="ja", word="腐敗", pos="verb")
        ]
        wikitext = "{{ja-suru|ふはい}}"
        self.wxr.wtp.start_page("腐敗")
        node = self.wxr.wtp.parse(wikitext)
        extract_inflections(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[0].forms],
            [
                {
                    "form": "腐敗すれ",
                    "hiragana": "ふはいすれ",
                    "roman": "fuhai sure",
                    "source": "inflection table",
                    "raw_tags": ["活用形", "假定形", "仮定形"],
                },
                {
                    "form": "腐敗せよ",
                    "hiragana": "ふはいせよ",
                    "roman": "fuhai seyo",
                    "source": "inflection table",
                    "raw_tags": ["活用形", "命令形", "書面語"],
                },
                {
                    "form": "腐敗しろ",
                    "hiragana": "ふはいしろ",
                    "roman": "fuhai shiro",
                    "source": "inflection table",
                    "raw_tags": ["活用形", "命令形", "口語"],
                },
            ],
        )

    def test_ja_suru_two_columns(self):
        self.wxr.wtp.add_page(
            "Template:ja-suru",
            10,
            """<div>
{|
|-
! colspan="4" | 活用形
|-
! <span class="Jpan" lang="ja">[[未然形#日語|-{未然形}-]]</span>
||<span class="Jpan" lang="ja-Jpan">あさがえりし</span>
| <span class="Latn" lang="ja-Latn">asagaeri shi</span>
|}
</div>""",
        )
        page_data = [
            WordEntry(
                lang="日語", lang_code="ja", word="あさがえり", pos="verb"
            )
        ]
        wikitext = "{{ja-suru}}"
        self.wxr.wtp.start_page("あさがえり")
        node = self.wxr.wtp.parse(wikitext)
        extract_inflections(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[0].forms],
            [
                {
                    "form": "あさがえりし",
                    "roman": "asagaeri shi",
                    "source": "inflection table",
                    "raw_tags": ["活用形", "未然形"],
                }
            ],
        )

    def test_ja_verbconj(self):
        self.wxr.wtp.add_page(
            "Template:ja-verbconj",
            10,
            """<div>
{|
|-
! colspan="4" | '''語幹形態'''
|-
! '''未然形'''
| | <span class="Jpan" lang="ja-Jpan">-</span>
| <span class="Latn" lang="ja-Latn">-</span>
|-
| '''假定形'''
| | <span class="Jpan" lang="ja-Jpan">ね</span>
| <span class="Latn" lang="ja-Latn">ne</span>
|}
</div>""",
        )
        page_data = [
            WordEntry(lang="日語", lang_code="ja", word="ぬ", pos="suffix")
        ]
        wikitext = "{{ja-verbconj|ぬ}}"
        self.wxr.wtp.start_page("ぬ")
        node = self.wxr.wtp.parse(wikitext)
        extract_inflections(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[0].forms],
            [
                {
                    "form": "ね",
                    "roman": "ne",
                    "source": "inflection table",
                    "raw_tags": ["語幹形態", "假定形"],
                }
            ],
        )

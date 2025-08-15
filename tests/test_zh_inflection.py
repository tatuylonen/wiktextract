from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.inflection import extract_inflections
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestZhInflection(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"),
            WiktionaryConfig(
                capture_language_codes=None, dump_file_lang_code="zh"
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

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
                    "raw_tags": ["活用形"],
                    "tags": ["hypothetical"],
                },
                {
                    "form": "腐敗せよ",
                    "hiragana": "ふはいせよ",
                    "roman": "fuhai seyo",
                    "source": "inflection table",
                    "raw_tags": ["活用形"],
                    "tags": ["imperative", "literary"],
                },
                {
                    "form": "腐敗しろ",
                    "hiragana": "ふはいしろ",
                    "roman": "fuhai shiro",
                    "source": "inflection table",
                    "raw_tags": ["活用形"],
                    "tags": ["imperative", "colloquial"],
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
                    "raw_tags": ["活用形"],
                    "tags": ["imperfective"],
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
                    "raw_tags": ["語幹形態"],
                    "tags": ["hypothetical"],
                }
            ],
        )

    def test_zh_forms_sup_tag(self):
        self.wxr.wtp.add_page(
            "Template:zh-forms",
            10,
            """{| class="floatright"
|-
! colspan=2|
|-
! [[正體]]/[[繁體]] -{<span style="font-size:140%">(<span lang="zh-Hant" class="Hant"><!-- -->[[白麵#漢語|-{白麵}-]]/<!-- -->[[白麪#漢語|-{白麪}-]]</span>)</span>
| <!-- -->[[白#漢語|-{白}-]]
| <!-- -->[[麵#漢語|-{麵}-]]/<!-- -->[[麪#漢語|-{麪}-]]}-
|-
! [[簡體]] -{<span style="font-size:140%">(<span lang="zh-Hans" class="Hans"><!-- -->[[白面#漢語|-{白面}-]]<sup><span class="explain" title="此形式還有其他意義。">*</span></sup></span>)</span>
| <!-- -->[[白#漢語|-{白}-]]
| <!-- -->[[面#漢語|-{面}-]]}-
|}""",
        )
        data = parse_page(
            self.wxr,
            "白麵",
            """==漢語==
{{zh-forms|s=白面}}
===名詞===
# [[麵粉]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "白麪",
                    "tags": ["Standard-Chinese", "Traditional-Chinese"],
                },
                {
                    "form": "白面",
                    "raw_tags": ["此形式還有其他意義。"],
                    "tags": ["Simplified-Chinese"],
                },
            ],
        )

    def test_zh_forms_under_pron_alt_forms(self):
        self.wxr.wtp.add_page(
            "Template:zh-forms",
            10,
            """{| class="floatright"
|-
! colspan=2|
|-
! colspan="2" | [[簡體]]與[[正體]]/[[繁體]]<br>-{<span style="font-size:140%">(<span lang="zh-Hani" class="Hani"><!-- -->[[大家#漢語|-{大家}-]]</span>)</span>
| <!-- -->[[大#漢語|-{大}-]]
| <!-- -->[[家#漢語|-{家}-]]}-
|-
! colspan="2" |異體
| colspan="2"|-{<span style="white-space:nowrap;"><span class="Hant" lang="zh-Hant">-{<!---->[[乾家#漢語|乾家]]<!---->}-</span><span class="Hani" lang="zh">-{<!---->／<!---->}-</span><span class="Hans" lang="zh-Hans">-{<!---->[[干家#漢語|干家]]<!---->}-</span> <span style="font-size:80%"><i>閩南語</i></span></span><br><span style="white-space:nowrap;"><span class="Hani" lang="zh">-{<!---->[[唐家#漢語|唐家]]<!---->}-</span> <span style="font-size:80%"><i>閩南語</i></span></span><br><span style="white-space:nowrap;"><span class="Hant" lang="zh-Hant">-{<!---->[[臺家#漢語|臺家]]<!---->}-</span><span class="Hani" lang="zh">-{<!---->／<!---->}-</span><span class="Hans" lang="zh-Hans">-{<!---->[[台家#漢語|台家]]<!---->}-</span> <span style="font-size:80%"><i>閩東語</i></span></span>}-
|}""",
        )
        data = parse_page(
            self.wxr,
            "大家",
            """==漢語==
===發音1===
====名詞====
# [[眾人]]

===發音3===
{{zh-forms|alt=乾家-閩南語,唐家-閩南語,臺家-閩東語}}
====名詞====
# 對[[女子]]的[[尊稱]]""",
        )
        self.assertTrue("forms" not in data[0])
        self.assertEqual(
            data[1]["forms"],
            [
                {
                    "form": "乾家",
                    "tags": ["Traditional-Chinese", "alternative", "Min-Nan"],
                },
                {
                    "form": "干家",
                    "tags": ["Simplified-Chinese", "alternative", "Min-Nan"],
                },
                {"form": "唐家", "tags": ["alternative", "Min-Nan"]},
                {
                    "form": "臺家",
                    "tags": ["Traditional-Chinese", "alternative", "Min-Dong"],
                },
                {
                    "form": "台家",
                    "tags": ["Simplified-Chinese", "alternative", "Min-Dong"],
                },
            ],
        )

    def test_zh_forms_anagrams(self):
        self.wxr.wtp.add_page(
            "Template:zh-forms",
            10,
            """{| class="floatright"
|-
! colspan=2|
|-
! colspan="2" |[[正體]]/[[繁體]] -{<span style="font-size:140%">(<span lang="zh-Hant" class="Hant"><!-- -->[[門閥#漢語|-{門閥}-]]</span>)</span>
| <!-- -->[[門#漢語|-{門}-]]
| <!-- -->[[閥#漢語|-{閥}-]]}-
|-
! colspan="2" |[[簡體]] -{<span style="font-size:140%">(<span lang="zh-Hans" class="Hans"><!-- -->[[门阀#漢語|-{门阀}-]]</span>)</span>
| <!-- -->[[门#漢語|-{门}-]]
| <!-- -->[[阀#漢語|-{阀}-]]}-
|-
! colspan="2" |異體
| colspan="2"|-{<span style="white-space:nowrap;"><span class="Hant" lang="zh-Hant">-{<!---->[[門伐#漢語|門伐]]<!---->}-</span><span class="Hani" lang="zh">-{<!---->／<!---->}-</span><span class="Hans" lang="zh-Hans">-{<!---->[[门伐#漢語|门伐]]<!---->}-</span></span>}-
|-
! colspan="2" |異序詞
| colspan="2"|<span style="white-space:nowrap;"><span class="Hant" lang="zh-Hant">-{<!---->[[閥門#漢語|閥門]]<!---->}-</span><span class="Hani" lang="zh">-{<!---->／<!---->}-</span><span class="Hans" lang="zh-Hans">-{<!---->[[阀门#漢語|阀门]]<!---->}-</span></span>
|}""",
        )
        data = parse_page(
            self.wxr,
            "門閥",
            """==漢語==
{{zh-forms|s=门阀|alt=門伐}}
===名詞===
# [[家族]]的[[社會地位]]及[[聲望]]""",
        )
        self.assertEqual(
            data[0]["anagrams"],
            [
                {"tags": ["Traditional-Chinese"], "word": "閥門"},
                {"tags": ["Simplified-Chinese"], "word": "阀门"},
            ],
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "门阀", "tags": ["Simplified-Chinese"]},
                {
                    "form": "門伐",
                    "tags": ["Traditional-Chinese", "alternative"],
                },
                {"form": "门伐", "tags": ["Simplified-Chinese", "alternative"]},
            ],
        )

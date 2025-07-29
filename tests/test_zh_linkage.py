from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.linkage import extract_linkage_section
from wiktextract.extractor.zh.models import Sense, WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestZhLinkage(TestCase):
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

    def test_sense_term_list(self):
        self.wxr.wtp.add_page(
            "Template:l",
            10,
            '<span class="Latn" lang="mul">[[cU#跨語言|-{cU}-]]</span>',
        )
        page_data = [
            WordEntry(
                lang="跨語言",
                lang_code="mul",
                word="%",
                senses=[Sense(glosses=["百分比"])],
                pos="symbol",
            )
        ]
        wikitext = "* {{sense|百分比}} {{l|mul|cU}}、[[centiuno]]"
        self.wxr.wtp.add_page("Template:Sense", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Template:L", 10, "{{{2}}}")
        self.wxr.wtp.db_conn.commit()
        self.wxr.wtp.start_page("%")
        node = self.wxr.wtp.parse(wikitext)
        extract_linkage_section(self.wxr, page_data, node, "synonyms")
        self.assertEqual(
            [
                s.model_dump(exclude_defaults=True)
                for s in page_data[0].synonyms
            ],
            [
                {"sense": "百分比", "word": "cU"},
                {"sense": "百分比", "word": "centiuno"},
            ],
        )

    def test_ja_r_template(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page("Template:s", 10, "{{{1}}}")
        self.wxr.wtp.add_page(
            "Template:ja-r",
            10,
            '<span class="Jpan" lang="ja">[[家主#日語|-{<ruby>家<rp>(</rp><rt>や</rt><rp>)</rp></ruby><ruby>主<rp>(</rp><rt>ぬし</rt><rp>)</rp></ruby>}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">yanushi</span></span><span class="mention-gloss-paren annotation-paren">)</span>',
        )
        node = self.wxr.wtp.parse("{{s|房東}}\n* {{ja-r|家%主|や%ぬし}}")
        page_data = [
            WordEntry(word="大家", lang_code="zh", lang="漢語", pos="noun")
        ]
        extract_linkage_section(self.wxr, page_data, node, "synonyms")
        self.assertEqual(
            page_data[0].synonyms[0].model_dump(exclude_defaults=True),
            {
                "roman": "yanushi",
                "ruby": [("家", "や"), ("主", "ぬし")],
                "sense": "房東",
                "word": "家主",
            },
        )

    def test_qual_tag(self):
        page_data = [
            WordEntry(lang="漢語", lang_code="zh", word="駱駝", pos="noun")
        ]
        self.wxr.wtp.add_page("Template:qual", 10, "({{{1}}})")
        self.wxr.wtp.add_page(
            "Template:zh-l",
            10,
            '<span class="Hani" lang="zh">-{<!---->[[沙漠之舟#漢語|沙漠之舟]]<!---->}-</span>[[Category:漢語紅鏈/zh-l]]',
        )
        self.wxr.wtp.start_page("駱駝")
        node = self.wxr.wtp.parse("* {{qual|比喻}} {{zh-l|沙漠之舟}}")
        extract_linkage_section(self.wxr, page_data, node, "synonyms")
        self.assertEqual(
            [
                s.model_dump(exclude_defaults=True)
                for s in page_data[0].synonyms
            ],
            [
                {"tags": ["figuratively"], "word": "沙漠之舟"},
            ],
        )

    def test_linkage_above_pos(self):
        self.wxr.wtp.add_page(
            "Template:alter",
            10,
            '<span class="Latn" lang="en">[[Tec#英語|-{Tec}-]]</span>',
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "'Tec",
                """==英語==
===替代形式===
* {{alter|en|Tec}}

===專有名詞===

# 偵探漫畫""",
            ),
            [
                {
                    "lang": "英語",
                    "lang_code": "en",
                    "pos": "name",
                    "pos_title": "專有名詞",
                    "senses": [{"glosses": ["偵探漫畫"]}],
                    "forms": [{"form": "Tec", "tags": ["alternative"]}],
                    "word": "'Tec",
                }
            ],
        )

    def test_zh_l(self):
        page_data = [
            WordEntry(lang="漢語", lang_code="zh", word="發音", pos="noun")
        ]
        self.wxr.wtp.add_page("Template:qual", 10, "{{{1}}}")
        self.wxr.wtp.add_page(
            "Template:zh-l",
            10,
            '<span class="Hant" lang="zh-Hant">-{<!---->[[讀音#漢語|讀音]]<!---->}-</span><span class="Hani" lang="zh">-{<!---->／<!---->}-</span><span class="Hans" lang="zh-Hans">-{<!---->[[读音#漢語|读音]]<!---->}-</span> (<i><span class="tr Latn" lang="la">-{<!---->dúyīn<!---->}-</span></i>)',
        )
        self.wxr.wtp.start_page("發音")
        node = self.wxr.wtp.parse("* {{qual|漢字發音}} {{zh-l|讀音}}")
        extract_linkage_section(self.wxr, page_data, node, "synonyms")
        self.assertEqual(
            [
                s.model_dump(exclude_defaults=True)
                for s in page_data[0].synonyms
            ],
            [
                {
                    "raw_tags": ["漢字發音"],
                    "word": "讀音",
                    "tags": ["Traditional-Chinese"],
                    "roman": "dúyīn",
                },
                {
                    "raw_tags": ["漢字發音"],
                    "word": "读音",
                    "tags": ["Simplified-Chinese"],
                    "roman": "dúyīn",
                },
            ],
        )

    def test_zh_dial(self):
        page_data = [
            WordEntry(lang="漢語", lang_code="zh", word="工作", pos="verb")
        ]
        self.wxr.wtp.add_page(
            "Template:zh-dial",
            10,
            """	<div><div><span class="Hant" lang="zh">[[職業#漢語|-{職業}-]]</span>的各地方言用詞[[Template:zh-dial-map/職業|<small>&#91;地圖&#93;</small>]]
</div><div>
	{| class="wikitable"
	|-
	! style="background:#E8ECFA" | 語言
	! style="background:#E8ECFA" | 地區
	! style="background:#E8ECFA" | 詞
|-
!rowspan=1 colspan=2 style="background:#FAF0F2"| 書面語 <small>([[w:官話白話文|白話文]])</small>
|style="background:#FAF0F2"| <span class="Hant" lang="zh">[[職業#漢語|-{職業}-]]</span>、<span class="Hani" lang="zh">[[工作#漢語|-{工作}-]]</span>
|-
!rowspan=6 style="background:#FAF0F6"| 客家語
|style="background:#FAF0F6"| [[w:四縣話|屏東（內埔，南四縣腔）]]
|style="background:#FAF0F6"| <span class="Hant" lang="zh">[[頭路#漢語|-{頭路}-]]</span>
|-
!rowspan=7 style="background:#F4F0FA"| 吳語
|style="background:#F4F0FA"| [[w:上海話|上海]]
|style="background:#F4F0FA"| <span class="Hani" lang="zh">[[生活#漢語|-{生活}-]]</span>、<span class="Hant" lang="zh">[[飯碗頭#漢語|-{飯碗頭}-]]</span> <span style="font-size:60%">比喻</span>
|-
! style="background:#FFF7FB; padding-top:5px; padding-bottom: 5px" | <small>註解</small>
| colspan=2|<small>GT - 通用臺灣話（無特定地域區分）</small>
|}</div></div>""",
        )
        self.wxr.wtp.start_page("工作")
        node = self.wxr.wtp.parse("{{zh-dial|職業}}")
        extract_linkage_section(self.wxr, page_data, node, "synonyms")
        data = [
            s.model_dump(exclude_defaults=True) for s in page_data[0].synonyms
        ]
        self.assertEqual(
            data[0],
            {
                "raw_tags": ["書面語 (白話文)"],
                "word": "職業",
            },
        )
        self.assertEqual(data[1]["word"], "頭路")
        self.assertEqual(
            set(data[1]["raw_tags"]), {"客家語", "屏東（內埔，南四縣腔）"}
        )
        self.assertEqual(data[2]["word"], "生活")
        self.assertEqual(set(data[2]["tags"]), {"Shanghai", "Wu"})
        self.assertEqual(data[3]["word"], "飯碗頭")
        self.assertEqual(
            set(data[3]["tags"]), {"Shanghai", "Wu", "figuratively"}
        )

    def test_level_3_linkage_section(self):
        self.wxr.wtp.add_page(
            "Template:col3",
            10,
            """<div><div><ul><li><span class="Hani" lang="zh">[[愚民政策#漢語|愚民政策]]</span></li></ul></div></div>""",
        )
        self.wxr.wtp.add_page(
            "Template:CJKV",
            10,
            """<div>[[w:漢字詞|漢字詞]]（-{<!----><span class="Hani" lang="zh">愚民</span><!---->}-）：
* <span class="desc-arr" title="借詞">→</span> 日語:<templatestyles src="Module:etymology/style.css"></templatestyles> <span class="Jpan" lang="ja">[[愚民#日語|<ruby>愚<rp>(</rp><rt>ぐ</rt><rp>)</rp></ruby><ruby>民<rp>(</rp><rt>みん</rt><rp>)</rp></ruby>]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">gumin</span></span><span class="mention-gloss-paren annotation-paren">)</span></div>""",
        )
        page_data = parse_page(
            self.wxr,
            "愚民",
            """==漢語==
===名詞===
# [[愚昧]]的[[人民]]

===動詞===
# 使[[人民]][[愚昧]]

====衍生詞====
{{col3|zh|愚民政策}}

===派生詞===
{{CJKV||j=愚%民|ぐ%みん}}""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "descendants": [
                        {
                            "lang_code": "ja",
                            "lang": "日語",
                            "roman": "gumin",
                            "ruby": [("愚", "ぐ"), ("民", "みん")],
                            "word": "愚民",
                        }
                    ],
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "senses": [{"glosses": ["愚昧的人民"]}],
                    "word": "愚民",
                },
                {
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "verb",
                    "pos_title": "動詞",
                    "descendants": [
                        {
                            "lang_code": "ja",
                            "lang": "日語",
                            "roman": "gumin",
                            "ruby": [("愚", "ぐ"), ("民", "みん")],
                            "word": "愚民",
                        }
                    ],
                    "senses": [{"glosses": ["使人民愚昧"]}],
                    "derived": [{"word": "愚民政策"}],
                    "word": "愚民",
                },
            ],
        )

    def test_ja_r_multi(self):
        self.wxr.wtp.add_page(
            "Template:ja-r/multi",
            10,
            """* <span class="Jpan" lang="ja">-{[[月よ星よ#日語|-{<ruby>月<rp>(</rp><rt>つき</rt><rp>)</rp></ruby>よ<ruby>星<rp>(</rp><rt>ほし</rt><rp>)</rp></ruby>よ}-]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!----><span class="mention-tr tr">-{<!---->tsuki yo hoshi yo<!---->}-</span><!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        data = parse_page(
            self.wxr,
            "月",
            """==日語==
===詞源1===
====名詞====
# [[月亮]]
=====俗語=====
{{ja-r/multi|data=
* {{ja-r/args|月 よ 星 よ|つき よ ほし よ}}
}}""",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "日語",
                    "lang_code": "ja",
                    "pos": "noun",
                    "pos_title": "名詞",
                    "senses": [{"glosses": ["月亮"]}],
                    "related": [
                        {
                            "word": "月よ星よ",
                            "roman": "tsuki yo hoshi yo",
                            "ruby": [("月", "つき"), ("星", "ほし")],
                        }
                    ],
                    "word": "月",
                }
            ],
        )

    def test_zh_syn_template(self):
        self.wxr.wtp.add_page(
            "Template:syn",
            10,
            """<span class="nyms 近義詞"><span class="defdate">近義詞：</span><span class="Hant" lang="zh">-{[[:wuu&#58;號頭|-{號頭}-]]}-</span><span class="Zsym mention" style="font-size:100%;">／</span><span class="Hans" lang="zh">-{[[:wuu&#58;号头|-{号头}-]]}-</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "月",
            """==漢語==
===詞源1===
====釋義====
# [[月份]]
#: {{syn|zh|wuu:號頭}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "號頭",
                    "tags": ["Traditional-Chinese"],
                    "sense": "月份",
                },
                {
                    "word": "号头",
                    "tags": ["Simplified-Chinese"],
                    "sense": "月份",
                },
            ],
        )

    def test_syn_roman(self):
        self.wxr.wtp.add_page(
            "Template:syn",
            10,
            """<span class="nyms 近義詞"><span class="defdate">近義詞：</span><span class="Jpan" lang="ja">-{[[追憶#日語|-{追憶}-]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->tsuioku<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>、<span class="Jpan" lang="ja">-{[[追想#日語|-{追想}-]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->tsuisō<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "記憶",
            """==日語==
===名詞===
# [[個體]]
#: {{syn|ja|追憶|tr1=tsuioku|追想|tr2=tsuisō}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {"word": "追憶", "sense": "個體", "roman": "tsuioku"},
                {"word": "追想", "sense": "個體", "roman": "tsuisō"},
            ],
        )

    def test_syn_qualifier(self):
        self.wxr.wtp.add_page(
            "Template:syn",
            10,
            """<span class="nyms 近義詞"><span class="defdate">近義詞：</span><span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">俚语，弃用</span><span class="ib-brac qualifier-brac">)</span> <span class="Latn" lang="en">-{[[duck#英語|-{duck}-]]}-</span></span>""",
        )
        data = parse_page(
            self.wxr,
            "faggot",
            """==英语==
===名词===
# [[肉丸]]
#: {{syn|en|duck|q1=俚语，弃用}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [{"word": "duck", "sense": "肉丸", "tags": ["slang", "obsolete"]}],
        )

    def test_syn_saurus(self):
        self.wxr.wtp.add_page(
            "Template:syn-saurus",
            10,
            """<div class="list-switcher-wrapper"><div class="term-list columns-bg"><ul><li><span class="Hani" lang="zh">-{[[世#漢語|-{世}-]]}-</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">書面或用於組詞</span><span class="ib-brac qualifier-brac">)</span></li><li><span class="Hani" lang="zh">-{[[天下#漢語|-{天下}-]]}-</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">書面、比喻</span><span class="ib-brac qualifier-brac">)</span></li></ul></div></div>""",
        )
        data = parse_page(
            self.wxr,
            "世界",
            """==漢語==
===名词===
# [[地球]]上的[[所有]][[地方]]或[[國家]]
====同義詞====
{{syn-saurus|zh|世界}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {"word": "世", "tags": ["literary"], "raw_tags": ["用於組詞"]},
                {"word": "天下", "tags": ["literary", "figuratively"]},
            ],
        )

    def test_qingming(self):
        self.wxr.wtp.add_page(
            "Template:col3",
            10,
            """<div class="list-switcher-wrapper"><div class="term-list columns-bg"><ul><li><span class="Hani" lang="zh">{{{2}}}</span></li></ul></div></div>""",
        )
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """* [[w:官話|官話]]
*:<small>([[w:漢語拼音|拼音]])</small>：<span class="form-of pinyin-ts-form-of" lang="cmn" style="font-family: Consolas, monospace;">[[qīngmíng#官話|qīngmíng]]</span>""",
        )
        data = parse_page(
            self.wxr,
            "清明",
            """==漢語==
===發音1===
{{zh-pron
|m=qīngmíng
|cat=a
}}
====形容詞====
# [[清澈]][[明淨]]
=====衍生詞=====
{{col3|zh|神志清明}}

===發音2===
====專有名詞====
# [[二十四節氣]]之一
====衍生詞====
{{col3|zh|清明菜}}""",
        )
        self.assertEqual(data[0]["derived"], [{"word": "神志清明"}])
        self.assertEqual(data[1]["derived"], [{"word": "清明菜"}])

    def test_l_template(self):
        self.wxr.wtp.add_page(
            "Template:l",
            10,
            """<span class="Kore" lang="ko">-{<!-- -->[[2차원#朝鮮語|-{2차원}-]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ko-Latn" class="tr Latn">-{<!---->ichawon<!---->}-</span>，<span class="mention-gloss-double-quote">“</span><span class="mention-gloss">虚构世界</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        data = parse_page(
            self.wxr,
            "0차원",
            """==朝鮮語==
===名詞===
# [[零次元]]
====同类词汇====
{{top2}}
* {{l|ko|2차원|tr=ichawon|t=虚构世界}}
{{bottom}}""",
        )
        self.assertEqual(
            data[0]["coordinate_terms"],
            [{"word": "2차원", "roman": "ichawon", "sense": "虚构世界"}],
        )

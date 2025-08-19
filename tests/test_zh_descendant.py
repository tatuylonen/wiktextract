from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.descendant import extract_descendant_section
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestDescendant(TestCase):
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

    def test_ruby(self):
        # https://zh.wiktionary.org/wiki/你好
        self.wxr.wtp.start_page("你好")
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            '<span class="desc-arr" title="借詞">→</span> 日語:',
        )
        self.wxr.wtp.add_page(
            "Template:ja-r",
            10,
            '<span class="Jpan" lang="ja">[[你好#日語|-{<ruby>你好<rp>(</rp><rt>ニイハオ</rt><rp>)</rp></ruby>}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">nīhao</span></span><span class="mention-gloss-paren annotation-paren">)</span>',
        )
        root = self.wxr.wtp.parse(
            "* {{desc|bor=1|ja|-}} {{ja-r|你好|ニイハオ}}"
        )
        page_data = [
            WordEntry(word="你好", lang_code="ja", lang="日語", pos="intj")
        ]
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            page_data[0].descendants[0].model_dump(exclude_defaults=True),
            {
                "lang_code": "ja",
                "lang": "日語",
                "roman": "nīhao",
                "ruby": [("你好", "ニイハオ")],
                "word": "你好",
                "raw_tags": ["借詞"],
            },
        )

    def test_roman_only_list(self):
        self.wxr.wtp.start_page("你好")
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            '<span class="desc-arr" title="仿譯詞">→</span> 壯語: <span class="Latn" lang="za">[[mwngz ndei#壯語|-{mwngz ndei}-]]</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">仿譯詞</span><span class="ib-brac qualifier-brac">)</span>',
        )
        root = self.wxr.wtp.parse("* {{desc|za|mwngz ndei|cal=1}}")
        page_data = [
            WordEntry(word="你好", lang_code="zh", lang="漢語", pos="intj")
        ]
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            page_data[0].descendants[0].model_dump(exclude_defaults=True),
            {
                "lang_code": "za",
                "lang": "壯語",
                "tags": ["calque"],
                "word": "mwngz ndei",
            },
        )

    def test_nested_list(self):
        # https://zh.wiktionary.org/wiki/オタク
        self.wxr.wtp.start_page("オタク")
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            """{{#switch:{{{der}}}
| 1 = <span class="desc-arr" title="以類比或添加詞素等方式重塑">⇒</span> 官話:
| #default = 官話:
}}""",
        )
        self.wxr.wtp.add_page(
            "Template:zh-l",
            10,
            """{{#switch:{{{1}}}
| 御宅族 = <span class="Hani" lang="zh">-{<!---->[[御宅族#漢語|御宅族]]<!---->}-</span> (<i><span class="tr Latn" lang="la">-{<!---->yùzháizú<!---->}-</span></i>)
| 宅男 = <span class="Hani" lang="zh">-{<!---->[[宅男#漢語|宅男]]<!---->}-</span> (<i><span class="tr Latn" lang="la">-{<!---->zháinán<!---->}-</span></i>)
| 宅女 = <span class="Hani" lang="zh">-{<!---->[[宅女#漢語|宅女]]<!---->}-</span> (<i><span class="tr Latn" lang="la">-{<!---->zháinǚ<!---->}-</span></i>)
}}""",
        )
        root = self.wxr.wtp.parse(
            """*: {{desc|cmn|-}} {{zh-l|御宅族}}
*:* {{desc|cmn|-|der=1}} {{zh-l|宅男}}
*:* {{desc|cmn|-|der=1}} {{zh-l|宅女}}"""
        )
        page_data = [
            WordEntry(word="オタク", lang_code="ja", lang="日語", pos="noun")
        ]
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            page_data[0].descendants[0].model_dump(exclude_defaults=True),
            {
                "lang_code": "cmn",
                "lang": "官話",
                "roman": "yùzháizú",
                "word": "御宅族",
                "descendants": [
                    {
                        "lang_code": "cmn",
                        "lang": "官話",
                        "roman": "zháinán",
                        "word": "宅男",
                        "raw_tags": ["以類比或添加詞素等方式重塑"],
                    },
                    {
                        "lang_code": "cmn",
                        "lang": "官話",
                        "roman": "zháinǚ",
                        "word": "宅女",
                        "raw_tags": ["以類比或添加詞素等方式重塑"],
                    },
                ],
            },
        )

    def test_zh_l_two_forms(self):
        self.wxr.wtp.start_page("猫吸い")
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            '<span class="desc-arr" title="借詞">→</span> 漢語:',
        )
        self.wxr.wtp.add_page(
            "Template:zh-l",
            10,
            '<span class="Hant" lang="zh-Hant">-{<!---->[[吸貓#漢語|吸貓]]<!---->}-</span><span class="Hani" lang="zh">-{<!---->／<!---->}-</span><span class="Hans" lang="zh-Hans">-{<!---->[[吸猫#漢語|吸猫]]<!---->}-</span> (<i><span class="tr Latn" lang="la">-{<!---->xīmāo<!---->}-</span></i>)',
        )
        root = self.wxr.wtp.parse("* {{desc|zh|-|bor=1}} {{zh-l|吸貓}}")
        page_data = [
            WordEntry(word="猫吸い", lang_code="ja", lang="日語", pos="noun")
        ]
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[0].descendants
            ],
            [
                {
                    "lang_code": "zh",
                    "lang": "漢語",
                    "word": "吸貓",
                    "roman": "xīmāo",
                    "tags": ["Traditional-Chinese"],
                    "raw_tags": ["借詞"],
                },
                {
                    "lang_code": "zh",
                    "lang": "漢語",
                    "word": "吸猫",
                    "roman": "xīmāo",
                    "tags": ["Simplified-Chinese"],
                    "raw_tags": ["借詞"],
                },
            ],
        )

    def test_desctree(self):
        self.wxr.wtp.start_page("français")
        self.wxr.wtp.add_page(
            "Template:desctree",
            10,
            '<span class="desc-arr" title="借詞">→</span> 波斯語: <span class="Arab fa-Arab" lang="fa">[[فرانسه#波斯語|-{فرانسه}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="fa-Latn" class="tr Latn">farânse</span><span class="mention-gloss-paren annotation-paren">)</span><ul><li><span class="desc-arr" title="借詞">→</span> 普什圖語: <span class="Arab ps-Arab" lang="ps">[[فرانسه#普什圖語|-{فرانسه}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ps-Latn" class="tr Latn">farānsa</span><span class="mention-gloss-paren annotation-paren">)</span></li></ul>',
        )
        root = self.wxr.wtp.parse("* {{desctree|fa|فرانسه|tr=farânse|bor=1}}")
        page_data = [
            WordEntry(word="français", lang_code="fr", lang="法語", pos="noun")
        ]
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[0].descendants
            ],
            [
                {
                    "lang_code": "fa",
                    "lang": "波斯語",
                    "word": "فرانسه",
                    "roman": "farânse",
                    "raw_tags": ["借詞"],
                    "descendants": [
                        {
                            "lang_code": "ps",
                            "lang": "普什圖語",
                            "word": "فرانسه",
                            "roman": "farānsa",
                            "raw_tags": ["借詞"],
                        }
                    ],
                }
            ],
        )

    def test_cjvk(self):
        self.wxr.wtp.start_page("中文")
        self.wxr.wtp.add_page(
            "Template:CJKV",
            10,
            """<div>[[w:漢字詞|漢字詞]]（-{<!----><span class="Hani" lang="zh">中文</span><!---->}-）：
* <span class="desc-arr" title="借詞">→</span> 日語: <span class="Jpan" lang="ja">[[中文#日語|-{<ruby>中文<rp>(</rp><rt>ちゅうぶん</rt><rp>)</rp></ruby>}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">chūbun</span></span><span class="mention-gloss-paren annotation-paren">)</span>
* <span class="desc-arr" title="借詞">→</span> 朝鮮語: <span class="Kore" lang="ko">[[중문#朝鮮語|-{중문(中文)}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ko-Latn" class="tr Latn">jungmun</span><span class="mention-gloss-paren annotation-paren">)</span>
* <span class="desc-arr" title="借詞">→</span> 越南語: <span class="Latn" lang="vi">[[Trung văn#越南語|-{Trung văn}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="vi-Latn" class="tr Latn"><span class="Hani" lang="vi">[[中文#越南語|-{中文}-]]</span></span><span class="mention-gloss-paren annotation-paren">)</span></div>""",
        )
        root = self.wxr.wtp.parse("{{CJKV|中文|ちゅうぶん|중문|Trung văn}}")
        page_data = [
            WordEntry(word="中文", lang_code="zh", lang="漢語", pos="noun")
        ]
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[0].descendants
            ],
            [
                {
                    "lang_code": "ja",
                    "lang": "日語",
                    "word": "中文",
                    "ruby": [("中文", "ちゅうぶん")],
                    "roman": "chūbun",
                    "raw_tags": ["借詞"],
                },
                {
                    "lang_code": "ko",
                    "lang": "朝鮮語",
                    "word": "중문(中文)",
                    "roman": "jungmun",
                    "raw_tags": ["借詞"],
                },
                {
                    "lang_code": "vi",
                    "lang": "越南語",
                    "word": "Trung văn",
                    "roman": "中文",
                    "raw_tags": ["借詞"],
                },
            ],
        )

    def test_level4_pos_desc(self):
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            '<span class="desc-arr" title="借詞">→</span> 布依語: <span class="Latn" lang="pcc">-{[[Zungyguef#布依語|-{Zungyguef}-]]}-</span>',
        )
        page_data = parse_page(
            self.wxr,
            "中國",
            """==漢語==
===詞源1===
etymology
====專有名詞====
# gloss 1
====名詞====
# gloss 2
====派生詞====
* {{desc|bor=1|pcc|Zungyguef}}""",
        )
        self.assertEqual(
            page_data[0]["descendants"],
            [
                {
                    "lang": "布依語",
                    "lang_code": "pcc",
                    "word": "Zungyguef",
                    "raw_tags": ["借詞"],
                }
            ],
        )
        self.assertEqual(
            page_data[0]["descendants"], page_data[1]["descendants"]
        )

    def test_two_desc_in_one_list(self):
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            """{{#switch:{{{2}}}
| tresor = 加泰羅尼亞語: <span class="Latn" lang="ca">-{<!-- -->[[tresor#加泰羅尼亞語|-{tresor}-]]}-</span>
| tesaurus = <span class="desc-arr" title="借詞">→</span> <span class="Latn" lang="ca">-{<!-- -->[[tesaurus#加泰羅尼亞語|-{tesaurus}-]]}-</span>
}}""",
        )
        data = parse_page(
            self.wxr,
            "thesaurus",
            """==拉丁語==
===名詞===
# 貯藏處
====派生語彙====
* {{desc|ca|tresor}}、{{desc|ca|tesaurus|bor=1|nolb=1}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang_code": "ca",
                    "lang": "加泰羅尼亞語",
                    "word": "tresor",
                },
                {
                    "lang_code": "ca",
                    "lang": "加泰羅尼亞語",
                    "word": "tesaurus",
                    "raw_tags": ["借詞"],
                },
            ],
        )

    def test_bento(self):
        self.wxr.wtp.add_page(
            "Template:desctree",
            10,
            """<span class="desc-arr" title="借詞">→</span> 官話: <span class="Hant" lang="cmn">-{<!-- -->[[便當#官話|-{便當}-]]}-</span><span class="Zsym mention" style="font-size:100%;">／</span><span class="Hans" lang="cmn">-{<!-- -->[[便当#官話|-{便当}-]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="cmn-Latn" class="tr Latn">-{<!---->biàndāng<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            """{{#switch:{{{2}}}
| biandang = <span class="desc-arr" title="借詞">→</span> 英語: <span class="Latn" lang="en">-{<!-- -->[[biandang#英語|-{biandang}-]]}-</span>
| бэнто́ = <span class="desc-arr" title="借詞">→</span> 俄語: <span class="Cyrl" lang="ru">-{<!-- -->[[бэнто#俄語|-{бэнто́}-]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ru-Latn" class="tr Latn">-{<!---->bɛntó<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>，<span class="Cyrl" lang="ru">-{<!-- -->[[бэнто#俄語|-{бэ́нто}-]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ru-Latn" class="tr Latn">-{<!---->bɛ́nto<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>
}}""",
        )
        data = parse_page(
            self.wxr,
            "弁當",
            """==日語==
===名詞===
# 簡單飯菜，飯盒
====派生詞====
* {{desctree|cmn|便當|tr=biàndāng|bor=1}}
** {{desc|en|biandang|bor=1}}
* {{desc|ru|бэнто́|бэ́нто|bor=1}}""",
        )
        self.assertEqual(
            data[0]["descendants"],
            [
                {
                    "lang": "官話",
                    "lang_code": "cmn",
                    "roman": "biàndāng",
                    "tags": ["Traditional-Chinese"],
                    "word": "便當",
                    "raw_tags": ["借詞"],
                    "descendants": [
                        {
                            "lang": "英語",
                            "lang_code": "en",
                            "word": "biandang",
                            "raw_tags": ["借詞"],
                        }
                    ],
                },
                {
                    "lang": "官話",
                    "lang_code": "cmn",
                    "roman": "biàndāng",
                    "tags": ["Simplified-Chinese"],
                    "word": "便当",
                    "raw_tags": ["借詞"],
                    "descendants": [
                        {
                            "lang": "英語",
                            "lang_code": "en",
                            "word": "biandang",
                            "raw_tags": ["借詞"],
                        }
                    ],
                },
                {
                    "lang": "俄語",
                    "lang_code": "ru",
                    "roman": "bɛntó",
                    "word": "бэнто́",
                    "raw_tags": ["借詞"],
                },
                {
                    "lang": "俄語",
                    "lang_code": "ru",
                    "roman": "bɛ́nto",
                    "word": "бэ́нто",
                    "raw_tags": ["借詞"],
                },
            ],
        )

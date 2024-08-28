from unittest import TestCase
from unittest.mock import Mock

from wikitextprocessor import Wtp

from wiktextract.extractor.zh.descendant import extract_descendant_section
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestDescendant(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(Wtp(lang_code="zh"), Mock())

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

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
        page_data = WordEntry(
            word="你好", lang_code="ja", lang="日語", pos="intj"
        )
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            page_data.descendants[0].model_dump(exclude_defaults=True),
            {
                "lang_code": "ja",
                "lang": "日語",
                "roman": "nīhao",
                "ruby": [("你好", "ニイハオ")],
                "word": "你好",
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
        page_data = WordEntry(
            word="你好", lang_code="zh", lang="漢語", pos="intj"
        )
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            page_data.descendants[0].model_dump(exclude_defaults=True),
            {
                "lang_code": "za",
                "lang": "壯語",
                "raw_tags": ["仿譯詞"],
                "word": "mwngz ndei",
            },
        )

    def test_nested_list(self):
        # https://zh.wiktionary.org/wiki/オタク
        self.wxr.wtp.start_page("オタク")
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            '<span class="desc-arr" title="詞形受類比影響或添加了額外詞素">⇒</span> 官話:',
        )
        self.wxr.wtp.add_page(
            "Template:zh-l",
            10,
            '<span class="Hani" lang="zh">{{{1}}}</span> (<i><span class="tr Latn" lang="la">{{{1}}}_roman</span></i>',
        )
        root = self.wxr.wtp.parse(
            """*: {{desc|cmn|-}} {{zh-l|御宅族}}
*:* {{desc|cmn|-|der=1}} {{zh-l|宅男}}
*:* {{desc|cmn|-|der=1}} {{zh-l|宅女}}"""
        )
        page_data = WordEntry(
            word="オタク", lang_code="ja", lang="日語", pos="noun"
        )
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            page_data.descendants[0].model_dump(exclude_defaults=True),
            {
                "descendants": [
                    {
                        "lang_code": "cmn",
                        "lang": "官話",
                        "roman": "宅男_roman",
                        "word": "宅男",
                    },
                    {
                        "lang_code": "cmn",
                        "lang": "官話",
                        "roman": "宅女_roman",
                        "word": "宅女",
                    },
                ],
                "lang_code": "cmn",
                "lang": "官話",
                "roman": "御宅族_roman",
                "word": "御宅族",
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
        page_data = WordEntry(
            word="猫吸い", lang_code="ja", lang="日語", pos="noun"
        )
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data.descendants
            ],
            [
                {
                    "lang_code": "zh",
                    "lang": "漢語",
                    "word": "吸貓",
                    "roman": "xīmāo",
                    "tags": ["Traditional Chinese"],
                },
                {
                    "lang_code": "zh",
                    "lang": "漢語",
                    "word": "吸猫",
                    "roman": "xīmāo",
                    "tags": ["Simplified Chinese"],
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
        page_data = WordEntry(
            word="français", lang_code="fr", lang="法語", pos="noun"
        )
        extract_descendant_section(self.wxr, root, page_data)
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data.descendants
            ],
            [
                {
                    "lang_code": "fa",
                    "lang": "波斯語",
                    "word": "فرانسه",
                    "roman": "farânse",
                    "descendants": [
                        {
                            "lang_code": "ps",
                            "lang": "普什圖語",
                            "word": "فرانسه",
                            "roman": "farānsa",
                        }
                    ],
                }
            ],
        )

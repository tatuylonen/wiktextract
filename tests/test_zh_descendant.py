from unittest import TestCase
from unittest.mock import Mock

from wikitextprocessor import Wtp
from wiktextract.extractor.zh.descendant import extract_descendants
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestDescendant(TestCase):
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
            '<span class="desc-arr" title="借詞">→</span> 日語：',
        )
        self.wxr.wtp.add_page(
            "Template:ja-r",
            10,
            '<span class="Jpan" lang="ja">[[你好#日語|-{<ruby>你好<rp>(</rp><rt>ニイハオ</rt><rp>)</rp></ruby>}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">nīhao</span></span><span class="mention-gloss-paren annotation-paren">)</span>',
        )
        root = self.wxr.wtp.parse(
            "* {{desc|bor=1|ja|-}} {{ja-r|你好|ニイハオ}}"
        )
        page_data = WordEntry(word="你好", lang_code="ja", lang="日語")
        extract_descendants(self.wxr, root, page_data)
        self.assertEqual(
            page_data.descendants[0].model_dump(exclude_defaults=True),
            {
                "lang_code": "ja",
                "lang": "日語",
                "roman": "nīhao",
                "ruby": [["你好", "ニイハオ"]],
                "word": "你好",
            },
        )

    def test_roman_only_list(self):
        self.wxr.wtp.start_page("你好")
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            '<span class="desc-arr" title="仿譯詞">→</span> 壯語：<span class="Latn" lang="za">[[mwngz ndei#壯語|-{mwngz ndei}-]]</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">仿譯</span><span class="ib-brac qualifier-brac">)</span>',
        )
        root = self.wxr.wtp.parse("* {{desc|za|mwngz ndei|cal=1}}")
        page_data = WordEntry(word="你好", lang_code="zh", lang="漢語")
        extract_descendants(self.wxr, root, page_data)
        self.assertEqual(
            page_data.descendants[0].model_dump(exclude_defaults=True),
            {
                "lang_code": "za",
                "lang": "壯語",
                "raw_tags": ["仿譯"],
                "word": "mwngz ndei",
            },
        )

    def test_nested_list(self):
        # https://zh.wiktionary.org/wiki/オタク
        self.maxDiff = None
        self.wxr.wtp.start_page("オタク")
        self.wxr.wtp.add_page(
            "Template:desc",
            10,
            '<span class="desc-arr" title="詞形受類比影響或添加了額外詞素">⇒</span> 官話：',
        )
        self.wxr.wtp.add_page(
            "Template:zh-l",
            10,
            '<span class="Hani" lang="zh">{{{1}}}</span> (<i><span class="tr Latn" lang="la">{{{1}}}</span></i>',
        )
        root = self.wxr.wtp.parse(
            """*: {{desc|cmn|-}} {{zh-l|御宅族}}
*:* {{desc|cmn|-|der=1}} {{zh-l|宅男}}
*:* {{desc|cmn|-|der=1}} {{zh-l|宅女}}"""
        )
        page_data = WordEntry(word="オタク", lang_code="ja", lang="日語")
        extract_descendants(self.wxr, root, page_data)
        self.assertEqual(
            page_data.descendants[0].model_dump(exclude_defaults=True),
            {
                "descendants": [
                    {
                        "lang_code": "cmn",
                        "lang": "官話",
                        "roman": "宅男",
                        "word": "宅男",
                    },
                    {
                        "lang_code": "cmn",
                        "lang": "官話",
                        "roman": "宅女",
                        "word": "宅女",
                    },
                ],
                "lang_code": "cmn",
                "lang": "官話",
                "roman": "御宅族",
                "word": "御宅族",
            },
        )

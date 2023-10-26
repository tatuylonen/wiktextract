from collections import defaultdict
from unittest import TestCase
from unittest.mock import Mock

from wikitextprocessor import Wtp
from wiktextract.extractor.zh.pronunciation import (
    extract_pronunciation_recursively,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestPronunciation(TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(Wtp(lang_code="zh"), Mock())

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_homophone_table(self):
        self.wxr.wtp.start_page("大家")
        root = self.wxr.wtp.parse(
            """* <small>同音詞</small>：<table><tr><th>[展開/摺疊]</th></tr><tr><td><span class="Hani" lang="zh">[[大姑#漢語|大姑]]</span><br><span class="Hani" lang="zh">[[小姑#漢語|小姑]]</span></td></tr></table>"""
        )
        page_data = [defaultdict(list)]
        extract_pronunciation_recursively(
            self.wxr, page_data, {}, "zh", root, []
        )
        self.assertEqual(
            page_data,
            [
                {
                    "sounds": [
                        {"homophone": "大姑", "tags": ["同音詞"]},
                        {"homophone": "小姑", "tags": ["同音詞"]},
                    ]
                }
            ],
        )

    def test_homophone_template(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page(
            "Template:homophones",
            10,
            '<span class="homophones">[[Appendix:Glossary#同音词|同音词]]：<span class="Jpan" lang="ja">[[大矢#日語|-{大矢}-]]</span>, <span class="Jpan" lang="ja">[[大宅#日語|-{大宅}-]]</span>, <span class="Jpan" lang="ja">[[大谷#日語|-{大谷}-]]</span></span>[[Category:有同音詞的日語詞]]',
        )
        root = self.wxr.wtp.parse("* {{homophones|ja|大矢|大宅|大谷}}")
        page_data = [defaultdict(list)]
        extract_pronunciation_recursively(
            self.wxr, page_data, {}, "ja", root, []
        )
        self.assertEqual(
            page_data,
            [
                {
                    "sounds": [
                        {"homophone": "大矢", "tags": ["同音詞"]},
                        {"homophone": "大宅", "tags": ["同音詞"]},
                        {"homophone": "大谷", "tags": ["同音詞"]},
                    ]
                }
            ],
        )

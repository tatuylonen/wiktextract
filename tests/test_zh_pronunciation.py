from unittest import TestCase
from unittest.mock import Mock

from wikitextprocessor import Wtp
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.pronunciation import extract_pronunciation
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
        self.wxr.wtp.add_page(
            "Template:zh-pron",
            10,
            """* [[w:官話|官話]]
** <small>([[w:現代標準漢語|現代標準漢語]])</small>
*** <small>同音詞</small>：<table><tr><th>[展開/摺疊]</th></tr><tr><td><span class="Hani" lang="zh">[[大姑#漢語|大姑]]</span><br><span class="Hani" lang="zh">[[小姑#漢語|小姑]]</span></td></tr></table>""",
        )
        root = self.wxr.wtp.parse("{{zh-pron}}")
        base_data = WordEntry(
            word="大家", lang_code="zh", lang="漢語", pos="noun"
        )
        page_data = [base_data.model_copy(deep=True)]
        extract_pronunciation(self.wxr, page_data, base_data, root)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[0].sounds],
            [
                {
                    "homophone": "大姑",
                    "raw_tags": ["官話", "現代標準漢語", "同音詞"],
                },
                {
                    "homophone": "小姑",
                    "raw_tags": ["官話", "現代標準漢語", "同音詞"],
                },
            ],
        )

    def test_homophone_template(self):
        self.wxr.wtp.start_page("大家")
        root = self.wxr.wtp.parse("* {{homophones|ja|大矢|大宅|大谷}}")
        base_data = WordEntry(
            word="大家", lang_code="ja", lang="日語", pos="noun"
        )
        page_data = [base_data.model_copy(deep=True)]
        extract_pronunciation(self.wxr, page_data, base_data, root)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[0].sounds],
            [
                {"homophone": "大矢"},
                {"homophone": "大宅"},
                {"homophone": "大谷"},
            ],
        )

    def test_en_pron_list(self):
        self.wxr.wtp.start_page("hello")
        self.wxr.wtp.add_page("Template:a", 10, "(美國)")
        root = self.wxr.wtp.parse(
            "* {{a|US}} {{enPR|hĕ-lō'|hə-lō'}}、{{IPA|en|/hɛˈloʊ/|/həˈloʊ/|/ˈhɛloʊ/}}"
        )
        base_data = WordEntry(
            word="hello", lang_code="en", lang="英語", pos="intj"
        )
        page_data = [base_data.model_copy(deep=True)]
        extract_pronunciation(self.wxr, page_data, base_data, root)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[0].sounds],
            [
                {"enpr": "hĕ-lō'", "raw_tags": ["美國"]},
                {"enpr": "hə-lō'", "raw_tags": ["美國"]},
                {"ipa": "/hɛˈloʊ/", "raw_tags": ["美國"]},
                {"ipa": "/həˈloʊ/", "raw_tags": ["美國"]},
                {"ipa": "/ˈhɛloʊ/", "raw_tags": ["美國"]},
            ],
        )

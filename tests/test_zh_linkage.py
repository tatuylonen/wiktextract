from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.linkage import extract_linkages
from wiktextract.extractor.zh.models import Sense, WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"), WiktionaryConfig(dump_file_lang_code="zh")
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_sense_term_list(self):
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
        extract_linkages(self.wxr, page_data, node.children, "synonyms", "")
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
        extract_linkages(self.wxr, page_data, node.children, "synonyms", "")
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
        self.wxr.wtp.add_page("Template:zh-l", 10, "{{{1}}}")
        self.wxr.wtp.start_page("駱駝")
        node = self.wxr.wtp.parse("* {{qual|比喻}} {{zh-l|沙漠之舟}}")
        extract_linkages(self.wxr, page_data, node.children, "synonyms", "")
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
                    "senses": [{"glosses": ["偵探漫畫"]}],
                    "synonyms": [{"word": "Tec"}],
                    "word": "'Tec",
                }
            ],
        )

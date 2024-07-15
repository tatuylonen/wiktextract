from unittest import TestCase

from wikitextprocessor import Wtp, Page
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.thesaurus import extract_thesaurus_page
from wiktextract.thesaurus import ThesaurusTerm, close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestZhThesaurus(TestCase):
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
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_col3(self):
        self.wxr.wtp.add_page("Template:ws sense", 10, "{{{2}}}")
        self.wxr.wtp.add_page(
            "Template:col3",
            10,
            """<div><div><ul><li><span class="Hant" lang="zh">[[一剎#漢語|-{一剎}-]]</span><span class="Zsym mention" style="font-size:100%;">／</span><span class="Hans" lang="zh">[[一刹#漢語|-{一刹}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="zh-Latn" class="tr Latn">yīchà</span><span class="mention-gloss-paren annotation-paren">)</span></li><li><span class="Hani" lang="nan-hbl">[[一目𥍉仔#泉漳話|-{一目𥍉仔}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="nan-hbl-Latn" class="tr Latn">chi̍t-ba̍k-nih-á</span><span class="mention-gloss-paren annotation-paren">)</span> <span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">泉漳話</span><span class="ib-brac qualifier-brac">)</span></li></ul></div><div class="list-switcher-element" data-showtext=" 展開 ▼ " data-hidetext=" 收起 ▲ " style="display:none"> </div></div>""",
        )
        page = Page(
            title="Thesaurus:頃刻",
            namespace_id=110,
            body="""==漢語==

===名詞===

===={{ws sense|zh|極短的時間}}====

=====近義詞=====
{{col3|zh|一剎|nan-hbl:一目𥍉仔<tr:chi̍t-ba̍k-nih-á>}}""",
        )
        self.assertEqual(
            extract_thesaurus_page(self.wxr, page),
            [
                ThesaurusTerm(
                    entry="頃刻",
                    language_code="zh",
                    pos="noun",
                    linkage="synonyms",
                    term="一剎",
                    tags=["Traditional Chinese"],
                    roman="yīchà",
                    sense="極短的時間",
                ),
                ThesaurusTerm(
                    entry="頃刻",
                    language_code="zh",
                    pos="noun",
                    linkage="synonyms",
                    term="一刹",
                    tags=["Simplified Chinese"],
                    roman="yīchà",
                    sense="極短的時間",
                ),
                ThesaurusTerm(
                    entry="頃刻",
                    language_code="zh",
                    pos="noun",
                    linkage="synonyms",
                    term="一目𥍉仔",
                    raw_tags=["泉漳話"],
                    roman="chi̍t-ba̍k-nih-á",
                    sense="極短的時間",
                ),
            ],
        )

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

    def test_obsolete_zh_der(self):
        self.wxr.wtp.add_page("Template:ws sense", 10, "{{{2}}}")
        self.wxr.wtp.add_page(
            "Template:zh-syn-list",
            10,
            """<span>''([[:Category:成功棄用的模板|棄用的模板用法]])'' <div>
{|
|-
|
* <span class="Hani" lang="zh">-{<!---->[[認生#漢語|認生]]<!---->}-</span>／<span class="Hani" lang="zh">-{<!---->[[认生#漢語|认生]]<!---->}-</span> (<i><span class="tr Latn" lang="la">-{<!---->rènshēng<!---->}-</span></i>)
|}</div></span>[[Category:使用不推薦使用的模板的頁面]]""",
        )
        page = Page(
            title="Thesaurus:怕生",
            namespace_id=110,
            body="""==漢語==

===動詞===

===={{ws sense|zh|害怕見到陌生人}}====

=====近義詞=====
{{zh-syn-list|怕生|認生|驚生份;閩南語|怯生}}""",
        )
        self.assertEqual(
            extract_thesaurus_page(self.wxr, page),
            [
                ThesaurusTerm(
                    entry="怕生",
                    language_code="zh",
                    pos="verb",
                    linkage="synonyms",
                    term="認生",
                    roman="rènshēng",
                    sense="害怕見到陌生人",
                ),
                ThesaurusTerm(
                    entry="怕生",
                    language_code="zh",
                    pos="verb",
                    linkage="synonyms",
                    term="认生",
                    roman="rènshēng",
                    sense="害怕見到陌生人",
                ),
            ],
        )

    def test_ja_r(self):
        self.wxr.wtp.add_page("Template:ws sense", 10, "{{{2}}}")
        self.wxr.wtp.add_page("Template:qual", 10, "{{{1}}}")
        self.wxr.wtp.add_page(
            "Template:ja-r",
            10,
            """<span class="Jpan" lang="ja">[[亡くなる#日語|-{<ruby>亡<rp>(</rp><rt>な</rt><rp>)</rp></ruby>くなる}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">[[naku naru#日語|-{<span class="mention-tr tr">naku naru</span>}-]]</span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        page = Page(
            title="Thesaurus:死ぬ",
            namespace_id=110,
            body="""
==日语==

===动词===

===={{ws sense|ja|死亡}}====

=====近义词=====
{{ws beginlist}}
* {{qual|礼貌}} {{ja-r|亡くなる|なく なる}}
{{ws endlist}}""",
        )
        self.assertEqual(
            extract_thesaurus_page(self.wxr, page),
            [
                ThesaurusTerm(
                    entry="死ぬ",
                    language_code="ja",
                    pos="verb",
                    linkage="synonyms",
                    term="亡くなる",
                    sense="死亡",
                    roman="naku naru",
                    raw_tags=["礼貌"],
                ),
            ],
        )

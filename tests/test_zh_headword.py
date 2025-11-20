from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.headword_line import (
    extract_headword_line_template,
    extract_tlb_template,
)
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestZhHeadword(TestCase):
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

    def test_english_headword(self) -> None:
        # https://zh.wiktionary.org/wiki/manga#字源1
        # wikitext: {{en-noun|~|manga|s}}
        # expanded text: manga (可數 & 不可數，複數 manga 或 mangas)
        self.wxr.wtp.start_page("manga")
        self.wxr.wtp.add_page(
            "Template:en-noun",
            10,
            """<span class="headword-line"><strong class="Latn headword" lang="en">-{manga}-</strong> ([[可數|可數]] <small>和</small> [[不可數|不可數]]-{}-，複數-{ <b lang="en"><strong class="selflink">manga</strong></b> <small>或</small> <b>[[mangas#英語|-{mangas}-]]</b>}-)</span>""",
        )
        root = self.wxr.wtp.parse("{{en-noun|~|manga|s}}")
        page_data = [
            WordEntry(word="manga", lang_code="en", lang="英語", pos="noun")
        ]
        self.wxr.wtp.title = "manga"
        extract_headword_line_template(self.wxr, page_data[0], root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "manga",
                    "lang_code": "en",
                    "lang": "英語",
                    "forms": [
                        {"form": "manga", "tags": ["plural"]},
                        {"form": "mangas", "tags": ["plural"]},
                    ],
                    "tags": ["countable", "uncountable"],
                    "pos": "noun",
                }
            ],
        )

    def test_headword_gender(self) -> None:
        # https://zh.wiktionary.org/wiki/manga#字源1_2
        # wikitext: {{nl-noun|m|-'s|mangaatje}}
        # expanded text: manga m (複數 manga's，指小詞 mangaatje n)
        self.wxr.wtp.start_page("manga")
        self.wxr.wtp.add_page(
            "Template:nl-noun",
            10,
            '<span class="headword-line"><strong class="Latn headword" lang="nl">-{manga}-</strong>&nbsp;<span class="gender"><abbr title="陽性名詞">m</abbr></span> (複數-{ <b>[[manga\'s#荷蘭語|-{manga\'s}-]]</b>}-，指小詞-{ <b>[[mangaatje#荷蘭語|-{mangaatje}-]]</b>&nbsp;<span class="gender"><abbr title="中性名詞">n</abbr></span>}-)</span>',
        )
        root = self.wxr.wtp.parse("{{nl-noun|m|-'s|mangaatje}}")
        word_entry = WordEntry(
            word="manga", lang_code="nl", lang="荷蘭語", pos="noun"
        )
        self.wxr.wtp.title = "manga"
        extract_headword_line_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True),
            {
                "word": "manga",
                "lang_code": "nl",
                "lang": "荷蘭語",
                "forms": [
                    {"form": "manga's", "tags": ["plural"]},
                    {
                        "form": "mangaatje",
                        "tags": ["neuter", "diminutive"],
                    },
                ],
                "tags": ["masculine"],
                "pos": "noun",
            },
        )

    def test_headword_roman(self) -> None:
        # https://zh.wiktionary.org/wiki/-κρατίας
        # wikitext: {{head|grc|後綴變格形|g=f|head=-κρατίᾱς}}
        # expanded text: -κρατίᾱς (-kratíās) f
        self.wxr.wtp.start_page("-κρατίας")
        self.wxr.wtp.add_page(
            "Template:head",
            10,
            '<span class="headword-line"><strong class="Polyt headword" lang="grc">-{-κρατίᾱς}-</strong> (<span lang="grc-Latn" class="headword-tr tr Latn" dir="ltr">-kratíās</span>)&nbsp;<span class="gender"><abbr title="陰性名詞">f</abbr></span></span>',
        )
        root = self.wxr.wtp.parse("{{head|grc|後綴變格形|g=f|head=-κρατίᾱς}}")
        page_data = [
            WordEntry(
                word="-κρατίας", lang_code="grc", lang="古希臘語", pos="suffix"
            )
        ]
        extract_headword_line_template(self.wxr, page_data[0], root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "word": "-κρατίας",
                    "lang_code": "grc",
                    "lang": "古希臘語",
                    "forms": [
                        {"form": "-κρατίᾱς", "tags": ["canonical"]},
                        {"form": "-kratíās", "tags": ["romanization"]},
                    ],
                    "tags": ["feminine"],
                    "pos": "suffix",
                }
            ],
        )

    def test_ja_noun(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page(
            "Template:ja-noun",
            10,
            '<span class="headword-line"><span id="日語:_おおや" class="senseid"><strong class="Jpan headword" lang="ja">-{<ruby>大<rp>(</rp><rt>[[おおや#日語|-{おお}-]]</rt><rp>)</rp></ruby><ruby>家<rp>(</rp><rt>[[おおや#日語|-{や}-]]</rt><rp>)</rp></ruby>}-</strong></span> [[Wiktionary:日語轉寫|•]] (<span lang="ja-Latn" class="headword-tr tr Latn" dir="ltr">[[ōya#日語|-{ōya}-]]</span>)&nbsp;<sup>←<strong class="Jpan headword" lang="ja">-{[[おほや#日語|-{おほや}-]]}-</strong> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr"><span class="mention-tr tr">ofoya</span><span class="mention-gloss-paren annotation-paren">)</span><sup>[[w:歷史假名遣|?]]</sup></sup><i></i></span>[[Category:日語詞元|おおや]][[Category:日語名詞|おおや]][[Category:有一年級漢字的日語詞|おおや]][[Category:有二年級漢字的日語詞|おおや]][[Category:有兩個漢字的日語詞|おおや]]',
        )
        root = self.wxr.wtp.parse("{{ja-noun|おおや|hhira=おほや}}")
        page_data = [
            WordEntry(word="大家", lang_code="ja", lang="日語", pos="noun")
        ]
        extract_headword_line_template(self.wxr, page_data[0], root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data],
            [
                {
                    "categories": [
                        "日語詞元",
                        "日語名詞",
                        "有一年級漢字的日語詞",
                        "有二年級漢字的日語詞",
                        "有兩個漢字的日語詞",
                    ],
                    "word": "大家",
                    "lang_code": "ja",
                    "lang": "日語",
                    "forms": [
                        {
                            "form": "大家",
                            "ruby": [("大", "おお"), ("家", "や")],
                            "tags": ["canonical"],
                        },
                        {"form": "ōya", "tags": ["romanization"]},
                        {
                            "form": "おほや",
                            "roman": "ofoya",
                            "tags": ["archaic"],
                        },
                    ],
                    "pos": "noun",
                }
            ],
        )

    def test_tlb(self):
        self.wxr.wtp.start_page("放鴿子")
        self.wxr.wtp.add_page(
            "Template:tlb",
            10,
            '<span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[Appendix:Glossary#不及物|不及物]][[Category:漢語不及物動詞|攴04鳥06子00]]</span><span class="ib-brac">)</span></span>',
        )
        root = self.wxr.wtp.parse("{{tlb|zh|不及物}}")
        page_data = [
            WordEntry(word="放鴿子", lang_code="zh", lang="漢語", pos="verb")
        ]
        extract_tlb_template(self.wxr, page_data[0], root.children[0])
        self.assertEqual(page_data[0].tags, ["intransitive"])
        self.assertEqual(page_data[0].categories, ["漢語不及物動詞"])

    def test_tlb_tags(self):
        self.wxr.wtp.add_page(
            "Template:term-label",
            10,
            '<span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[Appendix:Glossary#俚語|俚語]][[Category:英語俚語|講大話]]<span class="ib-comma">，</span>[[Appendix:Glossary#古舊|古舊]][[Category:有古舊詞義的英語詞|講大話]]</span><span class="ib-brac">)</span></span>',
        )
        data = parse_page(
            self.wxr,
            "old hat",
            """==英語==
===名詞===
{{term-label|en|俚語|古舊}}
# gloss""",
        )
        self.assertEqual(data[0]["tags"], ["slang", "archaic"])

    def test_ar_verb(self):
        self.wxr.wtp.add_page(
            "Template:ar-verb",
            10,
            """<span class="headword-line"><strong class="Arab headword" lang="ar">-{شَلَحَ}-</strong> (<span lang="ar-Latn" class="headword-tr tr Latn" dir="ltr">-{<!---->šalaḥa<!---->}-</span>) <span class="ib-content qualifier-content">[[Appendix:阿拉伯語動詞#第I類|第I類]]</span> (非過去時-{ <b class="Arab" lang="ar"><!-- -->[[يشلح#阿拉伯語|-{يَشْلَحُ}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ar-Latn" class="tr Latn">-{<!---->yašlaḥu<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>}-，動詞性名詞-{ <b class="Arab" lang="ar"><!-- -->[[شلح#阿拉伯語|-{شَلْح}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ar-Latn" class="tr Latn">-{<!---->šalḥ<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>}-)</span>[[Category:阿拉伯語詞元|شلح]]""",
        )
        data = parse_page(
            self.wxr,
            "شلح",
            """==阿拉伯語==
===動詞===
{{ar-verb|I/a~a.vn:شَلْح}}
# [[脫掉]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "شَلَحَ", "tags": ["canonical"]},
                {"form": "šalaḥa", "tags": ["romanization"]},
                {
                    "form": "يَشْلَحُ",
                    "tags": ["non-past"],
                    "roman": "yašlaḥu",
                },
                {"form": "شَلْح", "roman": "šalḥ", "tags": ["noun-from-verb"]},
            ],
        )
        self.assertEqual(data[0]["tags"], ["form-i"])
        self.assertEqual(data[0]["categories"], ["阿拉伯語詞元"])

    def test_split_form_words1(self):
        self.wxr.wtp.add_page(
            "Template:ko-noun",
            10,
            """<span class="headword-line"><strong class="Kore headword" lang="ko">-{0차원}-</strong> (<span lang="ko-Latn" class="headword-tr manual-tr tr Latn" dir="ltr">-{<!---->yeongchawon<!---->}-</span>) (諺文-{ <b class="Kore" lang="ko"><!-- -->[[영차원#朝鮮語|-{영차원}-]]</b>}-，漢字-{ <b class="Kore" lang="ko"><!-- -->[[零次元#朝鮮語|-{零次元}-]]／<!-- -->[[0次元#朝鮮語|-{0次元}-]]</b>}-)</span>[[Category:朝鮮語詞元|영차원]]""",
        )
        data = parse_page(
            self.wxr,
            "0차원",
            """==朝鮮語==
===名詞===
{{ko-noun|hangeul=영차원|hanja=[[零次元]]／[[0次元]]}}
# {{alt sp|ko|영차원}}""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "yeongchawon", "tags": ["romanization"]},
                {"form": "영차원", "tags": ["hangeul"]},
                {"form": "零次元", "tags": ["hanja"]},
                {"form": "0次元", "tags": ["hanja"]},
            ],
        )
        self.assertEqual(data[0]["categories"], ["朝鮮語詞元"])

    def test_split_form_words2(self):
        self.wxr.wtp.add_page(
            "Template:ko-noun",
            10,
            """<span class="headword-line"><strong class="Kore headword" lang="ko">-{사과}-</strong> (<span lang="ko-Latn" class="headword-tr manual-tr tr Latn" dir="ltr">-{<!---->sagwa<!---->}-</span>) (漢字-{ <b class="Kore" lang="ko"><!-- -->[[沙果#朝鮮語|-{沙果}-]], <!-- -->[[砂果#朝鮮語|-{砂果}-]]</b>}-)</span>""",
        )
        data = parse_page(
            self.wxr,
            "사과",
            """==朝鮮語==
===名詞===
{{ko-noun|hanja=[[沙果]], [[砂果]]}}
# [[蘋果]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "sagwa", "tags": ["romanization"]},
                {"form": "沙果", "tags": ["hanja"]},
                {"form": "砂果", "tags": ["hanja"]},
            ],
        )

    def test_ja_verb_suru(self):
        self.wxr.wtp.add_page(
            "Template:ja-verb-suru",
            10,
            """<span class="headword-line"><strong class="Jpan headword" lang="ja">-{<ruby>電<rp>(</rp><rt><!-- -->[[でんわ#日語|-{でん}-]]</rt><rp>)</rp></ruby><ruby>話<rp>(</rp><rt><!-- -->[[でんわ#日語|-{わ}-]]</rt><rp>)</rp></ruby><!-- -->[[する#日語|-{する}-]]}-</strong> [[Wiktionary:日語轉寫|•]] (<span class="headword-tr tr" dir="ltr">-{<!----><span class="Latn" lang="ja">-{<!-- -->[[denwa#日語|-{denwa}-]] <!-- -->[[suru#日語|-{suru}-]]}-</span><!---->}-</span>)&nbsp;<i>自動詞&nbsp;<abbr title="サ行活用">サ行</abbr></i> (連用形-{ <b class="Jpan" lang="ja"><ruby>電<rp>(</rp><rt>でん</rt><rp>)</rp></ruby><ruby>話<rp>(</rp><rt>わ</rt><rp>)</rp></ruby><!-- -->[[し#日語|-{し}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->denwa [[shi]]<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>}-，過去式-{ <b class="Jpan" lang="ja"><ruby>電<rp>(</rp><rt>でん</rt><rp>)</rp></ruby><ruby>話<rp>(</rp><rt>わ</rt><rp>)</rp></ruby><!-- -->[[した#日語|-{した}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->denwa [[shita]]<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>}-)</span>""",
        )
        data = parse_page(
            self.wxr,
            "電話",
            """==日語==
===動詞===
{{ja-verb-suru|tr=intrans|でんわ}}
# [[打電話]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "電話する",
                    "ruby": [("電", "でん"), ("話", "わ")],
                    "tags": ["canonical"],
                },
                {"form": "denwa suru", "tags": ["romanization"]},
                {
                    "form": "電話し",
                    "roman": "denwa shi",
                    "ruby": [("電", "でん"), ("話", "わ")],
                    "tags": ["continuative"],
                },
                {
                    "form": "電話した",
                    "roman": "denwa shita",
                    "ruby": [("電", "でん"), ("話", "わ")],
                    "tags": ["past"],
                },
            ],
        )
        self.assertEqual(data[0]["tags"], ["intransitive", "suru"])

    def test_ja_adj(self):
        self.wxr.wtp.add_page(
            "Template:ja-adj",
            10,
            """<span class="headword-line"><strong class="Jpan headword" lang="ja">-{<ruby>崔<rp>(</rp><rt><!-- -->[[さいかい#日語|-{さい}-]]</rt><rp>)</rp></ruby><ruby>嵬<rp>(</rp><rt><!-- -->[[さいかい#日語|-{かい}-]]</rt><rp>)</rp></ruby>}-</strong> [[Wiktionary:日語轉寫|•]] (<span class="headword-tr tr" dir="ltr">-{<!----><span class="Latn" lang="ja">-{<!-- -->[[saikai#日語|-{saikai}-]]}-</span><!---->}-</span>)&nbsp;<sup>←<strong class="Jpan headword" lang="ja">-{<!-- -->[[さいくわい#日語|-{さいくわい}-]]}-</strong> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!----><span class="mention-tr tr">-{<!---->saikwai<!---->}-</span><!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span><sup>[[w:歷史假名遣|?]]</sup></sup><i><abbr title="タリ活用（古典）"><sup><small>†</small></sup>タリ</abbr></i> (連體形-{ <b class="Jpan" lang="ja"><ruby>崔<rp>(</rp><rt>さい</rt><rp>)</rp></ruby><ruby>嵬<rp>(</rp><rt>かい</rt><rp>)</rp></ruby><!-- -->[[とした#日語|-{とした}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->saikai to shita<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span> <small>或</small> <b class="Jpan" lang="ja"><ruby>崔<rp>(</rp><rt>さい</rt><rp>)</rp></ruby><ruby>嵬<rp>(</rp><rt>かい</rt><rp>)</rp></ruby><!-- -->[[たる#日語|-{たる}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->saikai taru<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>}-，連用形-{ <b class="Jpan" lang="ja"><ruby>崔<rp>(</rp><rt>さい</rt><rp>)</rp></ruby><ruby>嵬<rp>(</rp><rt>かい</rt><rp>)</rp></ruby><!-- -->[[と#日語|-{と}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->saikai to<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span> <small>或</small> <b class="Jpan" lang="ja"><ruby>崔<rp>(</rp><rt>さい</rt><rp>)</rp></ruby><ruby>嵬<rp>(</rp><rt>かい</rt><rp>)</rp></ruby><!-- -->[[として#日語|-{として}-]]</b> <span class="mention-gloss-paren annotation-paren">(</span><span class="tr">-{<!---->saikai to shite<!---->}-</span><span class="mention-gloss-paren annotation-paren">)</span>}-)</span>""",
        )
        data = parse_page(
            self.wxr,
            "崔嵬",
            """==日語==
===形容動詞===
{{ja-adj|さいかい|infl=tari|hhira=さいくわい}}
# [[險峻]]的""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "崔嵬",
                    "ruby": [("崔", "さい"), ("嵬", "かい")],
                    "tags": ["canonical"],
                },
                {"form": "saikai", "tags": ["romanization"]},
                {"form": "さいくわい", "roman": "saikwai", "tags": ["archaic"]},
                {
                    "form": "崔嵬とした",
                    "roman": "saikai to shita",
                    "ruby": [("崔", "さい"), ("嵬", "かい")],
                    "tags": ["attributive"],
                },
                {
                    "form": "崔嵬たる",
                    "roman": "saikai taru",
                    "ruby": [("崔", "さい"), ("嵬", "かい")],
                    "tags": ["attributive"],
                },
                {
                    "form": "崔嵬と",
                    "roman": "saikai to",
                    "ruby": [("崔", "さい"), ("嵬", "かい")],
                    "tags": ["continuative"],
                },
                {
                    "form": "崔嵬として",
                    "roman": "saikai to shite",
                    "ruby": [("崔", "さい"), ("嵬", "かい")],
                    "tags": ["continuative"],
                },
            ],
        )
        self.assertEqual(data[0]["tags"], ["-tari"])

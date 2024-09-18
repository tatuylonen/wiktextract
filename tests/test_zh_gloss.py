from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import NodeKind, WikiNode, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.models import Sense, WordEntry
from wiktextract.extractor.zh.page import (
    extract_gloss,
    parse_page,
    parse_section,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestGloss(TestCase):
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

    def test_example_list(self) -> None:
        page_data = [
            WordEntry(lang="日語", lang_code="ja", word="可笑しい", pos="adj")
        ]
        wikitext = """# [[好玩]]的：
## 有趣的，滑稽的，可笑的
## 奇怪的，不正常的
## 不合理的，不合邏輯的
# {{lb|ja|棄用}} [[有趣]]的：
## [[有趣]]的
## [[美味]]的
## [[漂亮]]的
## [[很好]]的，[[卓越]]的"""
        self.wxr.wtp.start_page("可笑しい")
        self.wxr.wtp.add_page("Template:lb", 10, "({{{2|}}})")
        node = self.wxr.wtp.parse(wikitext)
        extract_gloss(self.wxr, page_data, node.children[0], Sense())
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in page_data[0].senses],
            [
                {"glosses": ["好玩的：", "有趣的，滑稽的，可笑的"]},
                {"glosses": ["好玩的：", "奇怪的，不正常的"]},
                {"glosses": ["好玩的：", "不合理的，不合邏輯的"]},
                {
                    "glosses": ["有趣的：", "有趣的"],
                    "tags": ["obsolete"],
                },
                {
                    "glosses": ["有趣的：", "美味的"],
                    "tags": ["obsolete"],
                },
                {
                    "glosses": ["有趣的：", "漂亮的"],
                    "tags": ["obsolete"],
                },
                {
                    "glosses": ["有趣的：", "很好的，卓越的"],
                    "tags": ["obsolete"],
                },
            ],
        )

    @patch("wiktextract.extractor.zh.page.process_pos_block")
    @patch("wiktextract.extractor.zh.page.clean_node", return_value="名詞1")
    def test_pos_title_number(
        self,
        mock_clean_node,
        mock_process_pos_block,
    ) -> None:
        node = WikiNode(NodeKind.LEVEL3, 0)
        base_data = WordEntry(word="", lang_code="", lang="", pos="")
        parse_section(self.wxr, [base_data], base_data, node)
        mock_process_pos_block.assert_called()

    @patch("wiktextract.extractor.zh.page.process_pos_block")
    @patch(
        "wiktextract.extractor.zh.page.clean_node", return_value="名詞（一）"
    )
    def test_pos_title_chinese_numeral(
        self,
        mock_clean_node,
        mock_process_pos_block,
    ) -> None:
        node = WikiNode(NodeKind.LEVEL3, 0)
        base_data = WordEntry(word="", lang_code="", lang="", pos="")
        parse_section(self.wxr, [base_data], base_data, node)
        mock_process_pos_block.assert_called()

    def test_soft_redirect_zh_see(self):
        self.assertEqual(
            parse_page(
                self.wxr,
                "別个",
                """==漢語==
{{zh-see|別個}}""",
            ),
            [
                {
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "soft-redirect",
                    "redirects": ["別個"],
                    "senses": [{"tags": ["no-gloss"]}],
                    "word": "別个",
                }
            ],
        )

    def test_soft_redirect_ja_see(self):
        self.assertEqual(
            parse_page(
                self.wxr,
                "きさらぎ",
                """==日語==
{{ja-see|如月|二月|更衣|衣更着}}""",
            ),
            [
                {
                    "lang": "日語",
                    "lang_code": "ja",
                    "pos": "soft-redirect",
                    "redirects": ["如月", "二月", "更衣", "衣更着"],
                    "senses": [{"tags": ["no-gloss"]}],
                    "word": "きさらぎ",
                }
            ],
        )

    def test_gloss_text_only_page(self):
        # title, page wikitext, results
        test_cases = [
            [
                "paraphrase",
                "== 英语 ==\n释义；意译",
                [
                    {
                        "lang": "英语",
                        "lang_code": "en",
                        "pos": "unknown",
                        "senses": [{"glosses": ["释义；意译"]}],
                        "word": "paraphrase",
                    }
                ],
            ],
            [
                "鐵面無私",
                "==漢語==\n===釋義===\n形容[[公正]]严明，绝不因[[徇私]]或畏权而讲情面。",
                [
                    {
                        "lang": "漢語",
                        "lang_code": "zh",
                        "pos": "unknown",
                        "senses": [
                            {
                                "glosses": [
                                    "形容公正严明，绝不因徇私或畏权而讲情面。"
                                ]
                            }
                        ],
                        "word": "鐵面無私",
                    }
                ],
            ],
        ]
        for title, wikitext, results in test_cases:
            with self.subTest(title=title, wikitext=wikitext, results=results):
                self.assertEqual(
                    parse_page(self.wxr, title, wikitext),
                    results,
                )

    def test_gloss_template(self):
        self.wxr.wtp.start_page("CC")
        self.wxr.wtp.add_page("Template:n-g", 10, "{{{1|}}}")
        root = self.wxr.wtp.parse(
            "# {{n-g|[[ISO]] 3166-1 對科科斯群島（[[Cocos Islands]]）的兩字母代碼。}}"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "glosses": [
                        "ISO 3166-1 對科科斯群島（Cocos Islands）的兩字母代碼。"
                    ]
                }
            ],
        )

    def test_gloss_lable_topic(self):
        self.wxr.wtp.start_page("DC")
        self.wxr.wtp.add_page("Template:lb", 10, "(航空学)")
        root = self.wxr.wtp.parse(
            "# {{lb|en|aviation}} 道格拉斯飞行器公司的產品名稱"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "glosses": ["道格拉斯飞行器公司的產品名稱"],
                    "topics": ["aeronautics"],
                }
            ],
        )

    def test_two_label_topics(self):
        self.wxr.wtp.start_page("DOS")
        self.wxr.wtp.add_page(
            "Template:lb",
            10,
            '<small><span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[計算機]][[Category:英語 計算機|工作]]<span class="ib-comma">，</span>[[網路]][[Category:英語 網路|工作]]</span><span class="ib-brac">)</span></span></small>',
        )
        self.wxr.wtp.add_page(
            "Template:init of",
            10,
            "<span><i>[[denial]] of [[service]]</i></span> (“拒絕服務”)之首字母縮略詞。",
        )
        root = self.wxr.wtp.parse(
            "# {{lb|en|計算機|網路}} {{init of|en|[[denial]] of [[service]]|t=拒絕服務}}"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "categories": ["英語 計算機", "英語 網路"],
                    "form_of": [{"word": "denial of service"}],
                    "glosses": [
                        "denial of service (“拒絕服務”)之首字母縮略詞。"
                    ],
                    "topics": ["computing", "internet"],
                    "tags": ["form-of"],
                }
            ],
        )

    def test_empty_parent_gloss(self):
        self.wxr.wtp.start_page("bright")
        self.wxr.wtp.add_page("Template:lb", 10, "({{{2}}})")
        root = self.wxr.wtp.parse("""# {{lb|en|比喻义}}
## [[显然]]的，[[显眼]]的
## {{lb|en|指颜色}} [[鲜亮]]的，[[鲜艳]]的""")
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "glosses": ["显然的，显眼的"],
                    "raw_tags": ["比喻义"],
                },
                {
                    "glosses": ["鲜亮的，鲜艳的"],
                    "raw_tags": ["比喻义", "指颜色"],
                },
            ],
        )

    def test_adj_form_of_template(self):
        self.wxr.wtp.start_page("bella")
        self.wxr.wtp.add_page(
            "Template:adj form of",
            10,
            """<small></small><span class='form-of-definition-link'><i class="Latn mention" lang="es">[[bello#西班牙語|-{bello}-]]</i></span><span class='form-of-definition use-with-mention'> 的[[Appendix:Glossary#gender|陰性]][[Appendix:Glossary#singular_number|單數]]</span>""",
        )
        root = self.wxr.wtp.parse("# {{adj form of|es|bello||f|s}}")
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "form_of": [{"word": "bello"}],
                    "glosses": ["bello 的陰性單數"],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_inflection_of_template(self):
        self.wxr.wtp.start_page("linda")
        self.wxr.wtp.add_page(
            "Template:inflection of",
            10,
            """<span><i>[[{{{2}}}]]</i></span> {{#switch:{{{5}}}
| acc = 的不定賓格單數
| dat = 的不定與格單數
}}""",
        )
        page_data = parse_page(
            self.wxr,
            "linda",
            """==冰島語==
===名詞===

# {{inflection of|is|[[lindi]]||不定|acc|s}}
# {{inflection of|is|[[lindi]]||不定|dat|s}}""",
        )
        self.assertEqual(
            page_data,
            [
                {
                    "lang": "冰島語",
                    "lang_code": "is",
                    "pos": "noun",
                    "senses": [
                        {
                            "form_of": [{"word": "lindi"}],
                            "glosses": ["lindi 的不定賓格單數"],
                            "tags": ["form-of"],
                        },
                        {
                            "form_of": [{"word": "lindi"}],
                            "glosses": ["lindi 的不定與格單數"],
                            "tags": ["form-of"],
                        },
                    ],
                    "word": "linda",
                }
            ],
        )

    def test_pt_verb_form_of(self):
        self.wxr.wtp.start_page("linda")
        self.wxr.wtp.add_page(
            "Template:pt-verb form of",
            10,
            """<small></small><span class='form-of-definition-link'><i class="Latn mention" lang="pt">[[lindar#葡萄牙語|-{lindar}-]]</i></span><span class='form-of-definition use-with-mention'> 的屈折变化形式：</span>
## <span class='form-of-definition use-with-mention'>[[Appendix:Glossary#third_person|第三人稱]][[Appendix:Glossary#singular_number|單數]][[Appendix:Glossary#present_tense|現在時]][[Appendix:Glossary#indicative_mood|直陳式]]</span>
## <span class='form-of-definition use-with-mention'>[[Appendix:Glossary#second_person|第二人稱]][[Appendix:Glossary#singular_number|單數]][[Appendix:Glossary#imperative_mood|命令式]]</span>""",
        )
        root = self.wxr.wtp.parse("# {{pt-verb form of|lindar}}")
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "form_of": [{"word": "lindar"}],
                    "glosses": [
                        "lindar 的屈折变化形式：",
                        "第三人稱單數現在時直陳式",
                    ],
                    "tags": ["form-of"],
                },
                {
                    "form_of": [{"word": "lindar"}],
                    "glosses": [
                        "lindar 的屈折变化形式：",
                        "第二人稱單數命令式",
                    ],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_linkage_under_in_gloss_list(self):
        self.wxr.wtp.start_page("linda")
        self.wxr.wtp.add_page("Template:pt-verb form of", 10, "{{{2}}}")
        root = self.wxr.wtp.parse("# [[可愛]]的\n#: {{syn|eo|ĉarmeta}}")
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            [
                s.model_dump(exclude_defaults=True)
                for s in page_data[0].synonyms
            ],
            [{"word": "ĉarmeta", "sense": "可愛的"}],
        )

    def test_hanja_form_of(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page(
            "Template:hanja form of",
            10,
            """<span class="Kore" lang="ko">[[대가#朝鮮語|-{대가}-]]</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="ko-Latn" class="tr Latn">daega</span><span class="mention-gloss-paren annotation-paren">)</span><span class="use-with-mention">的漢字<sup>[[附錄:韓字|?]]</sup></span>：[[大師]]；[[名門望族]]。""",
        )
        root = self.wxr.wtp.parse(
            "# {{hanja form of|대가|[[大師]]；[[名門望族]]}}"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "form_of": [{"word": "대가"}],
                    "glosses": [
                        "대가 (daega)的漢字：大師；名門望族。",
                    ],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_han_tu_form_of(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page(
            "Template:han tu form of",
            10,
            """<span class="use-with-mention"><i class="Latn mention" lang="vi">[[đại gia#越南語|-{đại gia}-]]</i> <span class="mention-gloss-paren annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">[[富人]]；[[偉人]]</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span>的[[漢字]]。</span>[[Category:儒字]]""",
        )
        root = self.wxr.wtp.parse(
            "# {{han tu form of|đại gia|[[富人]]；[[偉人]]}}"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "categories": ["儒字"],
                    "form_of": [{"word": "đại gia"}],
                    "glosses": [
                        "đại gia (“富人；偉人”)的漢字。",
                    ],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_es_verb_form_of(self):
        self.wxr.wtp.start_page("ababillares")
        self.wxr.wtp.add_page(
            "Template:es-verb form of",
            10,
            """<small></small><span class='use-with-mention'>僅用於<i class="Latn mention" lang="es">[[te#西班牙語|-{te}-]] [[ababillares#西班牙語|-{ababillares}-]]</i></span>；<span class='form-of-definition-link'><i class="Latn mention" lang="es">[[ababillarse#西班牙語|-{ababillarse}-]]</i></span><span class='form-of-definition use-with-mention'> 的[[Appendix:Glossary#second_person|第二人稱]][[Appendix:Glossary#singular_number|單數]][[Appendix:Glossary#future_tense|將來時]][[Appendix:Glossary#subjunctive_mood|虛擬式]]</span>""",
        )
        root = self.wxr.wtp.parse("# {{es-verb form of|ababillarse}}")
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "form_of": [{"word": "ababillarse"}],
                    "glosses": [
                        "僅用於te ababillares；ababillarse 的第二人稱單數將來時虛擬式",
                    ],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_zh_alt_form(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page(
            "Template:zh-alt-form",
            10,
            "<span>-{<!---->[[大姑#漢語|大姑]]<!---->}-</span>的另一種寫法。",
        )
        root = self.wxr.wtp.parse(
            "# 對[[女子]]的[[尊稱]]；{{zh-alt-form|大姑}}"
        )
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "alt_of": [{"word": "大姑"}],
                    "glosses": ["對女子的尊稱；大姑的另一種寫法。"],
                    "tags": ["alt-of"],
                },
            ],
        )

    def test_nonstandard_form(self):
        self.wxr.wtp.start_page("солнце")
        self.wxr.wtp.add_page(
            "Template:nonstandard form",
            10,
            """<span class='form-of-definition-link'><i class="Cyrl mention" lang="mk">[[сонце#馬其頓語|-{сонце}-]]</i>&nbsp;<span class="gender"><abbr title="中性">n</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="mk-Latn" class="mention-tr tr Latn">sonce</span><span class="mention-gloss-paren annotation-paren">)</span></span><span class='form-of-definition use-with-mention'>的非標準形式</span>。[[Category:馬其頓語非標準形式|大家]]""",
        )
        root = self.wxr.wtp.parse("# {{nonstandard form|mk|сонце|g=n}}")
        page_data = [WordEntry(word="", lang_code="", lang="", pos="")]
        extract_gloss(self.wxr, page_data, root.children[0], Sense())
        self.assertEqual(
            page_data[0].model_dump(exclude_defaults=True)["senses"],
            [
                {
                    "categories": ["馬其頓語非標準形式"],
                    "form_of": [{"word": "сонце"}],
                    "glosses": ["сонце n (sonce)的非標準形式。"],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_low_quality_german_page(self):
        self.wxr.wtp.add_page(
            "Template:zhushi", 10, '〈<span title="阳性名词">阳</span>〉'
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "Übergangsbereich",
                """==德语==
[[Category:德语名词]]{{zhushi|阳|阳性名词}}  过渡区，连接区""",
            ),
            [
                {
                    "categories": ["德语名词"],
                    "lang": "德语",
                    "lang_code": "de",
                    "pos": "noun",
                    "senses": [{"glosses": ["〈阳〉 过渡区，连接区"]}],
                    "word": "Übergangsbereich",
                },
            ],
        )

    def test_erhua(self):
        self.wxr.wtp.add_page(
            "Template:zh-erhua form of",
            10,
            '<small><span class="usage-label-sense"><span class="ib-brac">(</span><span class="ib-content">[[w:官话|官話]][[Category:官話漢語|一00曰09儿06]]</span><span class="ib-brac">)</span></span></small> <span class="Hani" lang="zh">-{<!---->[[一會#漢語|一會]]<!---->}-</span>／<span class="Hani" lang="zh">-{<!---->[[一会#漢語|一会]]<!---->}-</span> (<i><span class="tr Latn" lang="la">-{<!---->yīhuì<!---->}-</span></i>) 的[[w:兒化|兒化]]形式。[[Category:官話兒化詞]]',
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "一會兒",
                """==漢語==
===副詞===
# {{zh-erhua form of|}}""",
            ),
            [
                {
                    "lang": "漢語",
                    "lang_code": "zh",
                    "pos": "adv",
                    "senses": [
                        {
                            "categories": ["官話漢語", "官話兒化詞"],
                            "form_of": [
                                {
                                    "word": "一會",
                                    "tags": ["Traditional Chinese"],
                                },
                                {
                                    "word": "一会",
                                    "tags": ["Simplified Chinese"],
                                },
                            ],
                            "glosses": ["一會／一会 (yīhuì) 的兒化形式。"],
                            "tags": ["form-of", "Mandarin", "Erhua"],
                        }
                    ],
                    "word": "一會兒",
                },
            ],
        )

    def test_zh_mw(self):
        self.wxr.wtp.add_page(
            "Template:zh-mw",
            10,
            '<span><span>(分類詞：<span class="Hani" lang="zh">-{<!---->[[部#漢語|部]]<!---->}-</span> <span title="官話">官</span> <span title="粵語">粵</span>;<span>&nbsp;</span><span class="Hant" lang="zh-Hant">-{<!---->[[臺#漢語|臺]]<!---->}-</span><span class="Hani" lang="zh">-{<!---->／<!---->}-</span><span class="Hans" lang="zh-Hans">-{<!---->[[台#漢語|台]]<!---->}-</span> <span title="官話">官</span> <span title="閩南語">南</span> <span title="吳語">吳</span>)</span></span>',
        )
        page_data = parse_page(
            self.wxr,
            "電腦",
            """==漢語==
===名詞===
# 原用於數字計算的[[電子計算機]]。{{zh-mw|m,c:部|m,mn,w:臺}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0]["classifiers"],
            [
                {"classifier": "部", "tags": ["Mandarin", "Cantonese"]},
                {
                    "classifier": "臺",
                    "tags": [
                        "Traditional Chinese",
                        "Mandarin",
                        "Southern Min",
                        "Wu",
                    ],
                },
                {
                    "classifier": "台",
                    "tags": [
                        "Simplified Chinese",
                        "Mandarin",
                        "Southern Min",
                        "Wu",
                    ],
                },
            ],
        )

    def test_low_quality_section_at_page_end(self):
        page_data = parse_page(
            self.wxr,
            "germano",
            """==因特语==
===名詞===
# 德語

==西班牙语==
德国的""",
        )
        self.assertEqual(len(page_data), 2)
        self.assertEqual(page_data[0]["senses"][0]["glosses"], ["德語"])
        self.assertEqual(page_data[1]["senses"][0]["glosses"], ["德国的"])

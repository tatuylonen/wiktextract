from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.example import extract_example_list_item
from wiktextract.extractor.zh.models import Sense
from wiktextract.extractor.zh.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestExample(TestCase):
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

    def test_example_list(self) -> None:
        sense_data = Sense()
        wikitext = """#* ref text
#*: example text"""
        self.wxr.wtp.start_page("test")
        root = self.wxr.wtp.parse(wikitext)
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            sense_data.examples[0].model_dump(exclude_defaults=True),
            {
                "ref": "ref text",
                "text": "example text",
            },
        )

    def test_zh_x(self):
        self.wxr.wtp.start_page("大家")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[王#漢語|王]][[曰#漢語|曰]]：「[[封#漢語|封]]，[[以#漢語|以]][[厥#漢語|厥]][[庶民#漢語|庶民]][[暨#漢語|暨]][[厥#漢語|厥]][[臣#漢語|臣]][[達#漢語|達]]<b>大家</b>，[[以#漢語|以]][[厥#漢語|厥]][[臣#漢語|臣]][[達#漢語|達]][[王#漢語|王]][[惟#漢語|惟]][[邦君#漢語|邦君]]。」<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[w:繁体中文|繁體]]&#93;</span><br><span lang="zh-Hans" class="Hans">-{<!-- -->[[王#漢語|王]][[曰#漢語|曰]]：「[[封#漢語|封]]，[[以#漢語|以]][[厥#漢語|厥]][[庶民#漢語|庶民]][[暨#漢語|暨]][[厥#漢語|厥]][[臣#漢語|臣]][[达#漢語|达]]<b>大家</b>，[[以#漢語|以]][[厥#漢語|厥]][[臣#漢語|臣]][[达#漢語|达]][[王#漢語|王]][[惟#漢語|惟]][[邦君#漢語|邦君]]。」<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]，[[w:简体中文|簡體]]&#93;</span><dd><small>出自：《[[s:尚書/梓材|尚書·梓材]]》</small></dd><dd><span lang="zh-Latn" style="color:#404D52"><i>Wáng yuē: “Fēng, yǐ jué shùmín jì jué chén dá <b>dàjiā</b>, yǐ jué chén dá wáng wéi bāngjūn.”</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:漢語拼音|漢語拼音]]&#93;</span></dd><dd>王說：「封啊，從殷的老百姓和他們的官員到'''卿大夫'''，從他們的官員到諸侯和國君。」</dd></dl>[[Category:有引文的文言文詞]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(
            "#* {{zh-x|王 曰：「封，以 厥 庶民 暨 厥 臣 達 大家，以 厥 臣 達 王 惟 邦君。」|王說：「封啊，從殷的老百姓和他們的官員到'''卿大夫'''，從他們的官員到諸侯和國君。」|CL|ref=《[[s:尚書/梓材|尚書·梓材]]》}}"
        )
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "ref": "《尚書·梓材》",
                    "tags": [
                        "Pinyin",
                        "Classical-Chinese",
                        "Traditional-Chinese",
                    ],
                    "text": "王曰：「封，以厥庶民暨厥臣達大家，以厥臣達王惟邦君。」",
                    "bold_text_offsets": [(14, 16)],
                    "roman": "Wáng yuē: “Fēng, yǐ jué shùmín jì jué chén dá dàjiā, yǐ jué chén dá wáng wéi bāngjūn.”",
                    "bold_roman_offsets": [(46, 51)],
                    "translation": "王說：「封啊，從殷的老百姓和他們的官員到卿大夫，從他們的官員到諸侯和國君。」",
                    "bold_translation_offsets": [(20, 23)],
                },
                {
                    "ref": "《尚書·梓材》",
                    "tags": [
                        "Pinyin",
                        "Classical-Chinese",
                        "Simplified-Chinese",
                    ],
                    "text": "王曰：「封，以厥庶民暨厥臣达大家，以厥臣达王惟邦君。」",
                    "bold_text_offsets": [(14, 16)],
                    "roman": "Wáng yuē: “Fēng, yǐ jué shùmín jì jué chén dá dàjiā, yǐ jué chén dá wáng wéi bāngjūn.”",
                    "bold_roman_offsets": [(46, 51)],
                    "translation": "王說：「封啊，從殷的老百姓和他們的官員到卿大夫，從他們的官員到諸侯和國君。」",
                    "bold_translation_offsets": [(20, 23)],
                },
            ],
        )

    def test_zh_x_no_ref(self):
        self.wxr.wtp.start_page("中文")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<span lang="zh-Hant" class="Hant">-{<!-- --><b>中文</b>[[授課#漢語|授課]]<!-- -->}-</span> / <span lang="zh-Hans" class="Hans">-{<!-- --><b>中文</b>[[授课#漢語|授课]]<!-- -->}-</span>&nbsp; ―&nbsp; <span lang="Latn" style="color:#404D52"><i><b>zhōngwén</b> shòukè</i></span>&nbsp; ―&nbsp; [[Category:有使用例的官話詞]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse("#* {{zh-x|中文 授課}}")
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "中文授課",
                    "bold_text_offsets": [(0, 2)],
                    "tags": ["Traditional-Chinese"],
                    "roman": "zhōngwén shòukè",
                    "bold_roman_offsets": [(0, 8)],
                },
                {
                    "text": "中文授课",
                    "bold_text_offsets": [(0, 2)],
                    "tags": ["Simplified-Chinese"],
                    "roman": "zhōngwén shòukè",
                    "bold_roman_offsets": [(0, 8)],
                },
            ],
        )

    def test_example_under_quote_template(self):
        self.wxr.wtp.start_page("英語")
        self.wxr.wtp.add_page(
            "Template:quote-book",
            10,
            """<div class="citation-whole"><span class="cited-source">'''2002年'''3月9日, [[w:堀田由美|堀田 由美]]</span><dl><dd></dd></dl></div>""",
        )
        self.wxr.wtp.add_page(
            "Template:ja-usex",
            10,
            """<span lang="ja" class="Jpan">-{オレの<ruby>日<rp>(</rp><rt>に</rt><rp>)</rp></ruby><ruby>本<rp>(</rp><rt>ほん</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby>どう？<ruby>悪<rp>(</rp><rt>わる</rt><rp>)</rp></ruby>くないだろ　<ruby>韓<rp>(</rp><rt>かん</rt><rp>)</rp></ruby><ruby>国<rp>(</rp><rt>こく</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby>と'''<ruby>英<rp>(</rp><rt>えい</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby>'''も<ruby>話<rp>(</rp><rt>はな</rt><rp>)</rp></ruby>すんだぜ　<ruby>趣<rp>(</rp><rt>しゅ</rt><rp>)</rp></ruby><ruby>味<rp>(</rp><rt>み</rt><rp>)</rp></ruby>だな<ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby><ruby>学<rp>(</rp><rt>がく</rt><rp>)</rp></ruby>は　<ruby>寝<rp>(</rp><rt>ね</rt><rp>)</rp></ruby><ruby>泊<rp>(</rp><rt>とま</rt><rp>)</rp></ruby>りはどこ？<ruby>近<rp>(</rp><rt>ちか</rt><rp>)</rp></ruby>くのホテル？}-</span><dl><dd><i><span lang="la" class="tr">Ore no Nihongo dō? Waruku naidaro Kankokugo to '''Eigo''' mo hanasunda ze Shumi da na gogaku wa Netomari wa doko? Chikaku no hoteru?</span></i></dd><dd>我的日語怎麼樣？不差吧？我也會講韓語和英語。學習語言很有趣。你在哪裏住？附近的賓館嗎？</dd></dl>[[Category:有使用例的日語詞|艸05言07]][[Category:有使用例的日語詞|艸05言07]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse("""#* {{quote-book|ja}}
#*: {{ja-usex|オレの日%本%語どう？悪くないだろ　韓%国%語と'''英%語'''も話すんだぜ　趣%味だな語%学は　寝%泊りはどこ？近くのホテル？|^オレ の ^に%ほん%ご どう？ ^わるく ないだろ　^かん%こく%ご と '''^えい%ご''' も はなすんだ ぜ　^しゅ%み だ な ご%がく は　^ね%とまり は どこ？ ^ちかく の ホテル？|我的日語怎麼樣？不差吧？我也會講韓語和英語。學習語言很有趣。你在哪裏住？附近的賓館嗎？}}""")
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "ref": "2002年3月9日, 堀田 由美",
                    "text": "オレの日本語どう？悪くないだろ 韓国語と英語も話すんだぜ 趣味だな語学は 寝泊りはどこ？近くのホテル？",
                    "bold_text_offsets": [(20, 22)],
                    "roman": "Ore no Nihongo dō? Waruku naidaro Kankokugo to Eigo mo hanasunda ze Shumi da na gogaku wa Netomari wa doko? Chikaku no hoteru?",
                    "bold_roman_offsets": [(47, 51)],
                    "ruby": [
                        ("日", "に"),
                        ("本", "ほん"),
                        ("語", "ご"),
                        ("悪", "わる"),
                        ("韓", "かん"),
                        ("国", "こく"),
                        ("語", "ご"),
                        ("英", "えい"),
                        ("語", "ご"),
                        ("話", "はな"),
                        ("趣", "しゅ"),
                        ("味", "み"),
                        ("語", "ご"),
                        ("学", "がく"),
                        ("寝", "ね"),
                        ("泊", "とま"),
                        ("近", "ちか"),
                    ],
                    "translation": "我的日語怎麼樣？不差吧？我也會講韓語和英語。學習語言很有趣。你在哪裏住？附近的賓館嗎？",
                },
            ],
        )

    def test_quote_book_above_zh_x(self):
        self.wxr.wtp.start_page("死人")
        self.wxr.wtp.add_page(
            "Template:quote-book",
            10,
            """<div class="citation-whole"><span class="cited-source"><span class="None" lang="und">'''1957'''</span>, <span class="Hani" lang="und">[[:w&#x3A;王力|-{王力}-]]</span></span><dl><dd></dd></dl></div>""",
        )
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[如果#漢語|如果]][[唔係#漢語|唔係]][[今日#漢語|今日]][[拆穿#漢語|拆穿]][[你#漢語|你]][[槓嘢#漢語|槓野]]，[[畀#漢語|俾]][[你#漢語|你]][[混#漢語|混]][[咗#漢語|左]][[入#漢語|入]][[稅局#漢語|稅局]][[重#漢語|重]]<b>死人</b>[[呀#漢語|呀]]！<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:廣州話|廣州話]]，[[w:繁体中文|繁體]]&#93;</span><br><span lang="zh-Hans" class="Hans">-{<!-- -->[[如果#漢語|如果]][[唔系#漢語|唔系]][[今日#漢語|今日]][[拆穿#漢語|拆穿]][[你#漢語|你]][[杠嘢#漢語|杠野]]，[[畀#漢語|俾]][[你#漢語|你]][[混#漢語|混]][[咗#漢語|左]][[入#漢語|入]][[税局#漢語|税局]][[重#漢語|重]]<b>死人</b>[[呀#漢語|呀]]！<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:廣州話|廣州話]]，[[w:简体中文|簡體]]&#93;</span><dd><span lang="zh-Latn" style="color:#404D52"><i>jyu<sup>4</sup> gwo<sup>2</sup> m<sup>4</sup> hai<sup>6</sup> gam<sup>1</sup> jat<sup>6</sup> caak<sup>3</sup> cyun<sup>1</sup> nei<sup>5</sup> lung<sup>5</sup> je<sup>5</sup>, bei<sup>2</sup> nei<sup>5</sup> wan<sup>6</sup> zo<sup>2</sup> jap<sup>6</sup> seoi<sup>3</sup> guk<sup>6-2</sup> zung<sup>6</sup> <b>sei<sup>2</sup> jan<sup>4</sup></b> aa<sup>3</sup>!</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:廣州話拼音方案|廣州話拼音]]&#93;</span></dd><dd>如果不是今天揭穿你的老底，給你混進稅務局就更'''糟糕'''了！</dd></dl>[[Category:有使用例的粵語詞]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(r"""#* {{quote-book|zh}}
#*: {{zh-x|如果 唔係 今日 拆穿 你 槓嘢\槓{lung5}野，畀\俾 你 混 咗\左 入 稅局{guk6-2} 重{zung6} 死人 呀！|如果不是今天揭穿你的老底，給你混進稅務局就更'''糟糕'''了！|C-GZ}}""")
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "ref": "1957, 王力",
                    "text": "如果唔係今日拆穿你槓野，俾你混左入稅局重死人呀！",
                    "bold_text_offsets": [(20, 22)],
                    "roman": "jyu⁴ gwo² m⁴ hai⁶ gam¹ jat⁶ caak³ cyun¹ nei⁵ lung⁵ je⁵, bei² nei⁵ wan⁶ zo² jap⁶ seoi³ guk⁶⁻² zung⁶ sei² jan⁴ aa³!",
                    "bold_roman_offsets": [(99, 108)],
                    "tags": ["Cantonese", "Pinyin", "Traditional-Chinese"],
                    "translation": "如果不是今天揭穿你的老底，給你混進稅務局就更糟糕了！",
                    "bold_translation_offsets": [(22, 24)],
                },
                {
                    "ref": "1957, 王力",
                    "text": "如果唔系今日拆穿你杠野，俾你混左入税局重死人呀！",
                    "bold_text_offsets": [(20, 22)],
                    "roman": "jyu⁴ gwo² m⁴ hai⁶ gam¹ jat⁶ caak³ cyun¹ nei⁵ lung⁵ je⁵, bei² nei⁵ wan⁶ zo² jap⁶ seoi³ guk⁶⁻² zung⁶ sei² jan⁴ aa³!",
                    "bold_roman_offsets": [(99, 108)],
                    "tags": ["Cantonese", "Pinyin", "Simplified-Chinese"],
                    "translation": "如果不是今天揭穿你的老底，給你混進稅務局就更糟糕了！",
                    "bold_translation_offsets": [(22, 24)],
                },
            ],
        )

    def test_zh_x_literal_meaning(self):
        self.wxr.wtp.start_page("黑奴")
        self.wxr.wtp.add_page("Template:w", 10, "{{{1}}}")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<span lang="zh-Hant" class="Hant">-{<!-- --><b>黑奴</b>[[籲天#漢語|籲天]][[錄#漢語|錄]]<!-- -->}-</span><span lang="zh-Hani" class="Hani">／</span><span lang="zh-Hans" class="Hans">-{<!-- --><b>黑奴</b>[[吁天#漢語|吁天]][[录#漢語|录]]<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:文言文|文言文]]&#93;</span>&nbsp; ―&nbsp; <span lang="zh-Latn" style="color:#404D52"><i><b>Hēinú</b> Yùtiānlù</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:漢語拼音|漢語拼音]]&#93;</span>&nbsp; ―&nbsp; [[w:湯姆叔叔的小屋|湯姆叔叔的小屋]]（字面義為“'''黑人奴隸'''向上天呼告的記錄”）[[Category:有使用例的文言文詞]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(
            "#: {{zh-x|^黑奴 ^籲天-錄|{{w|湯姆叔叔的小屋}}|lit='''黑人奴隸'''向上天呼告的記錄|CL}}"
        )
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "黑奴籲天錄",
                    "bold_text_offsets": [(0, 2)],
                    "roman": "Hēinú Yùtiānlù",
                    "bold_roman_offsets": [(0, 5)],
                    "tags": [
                        "Traditional-Chinese",
                        "Classical-Chinese",
                        "Pinyin",
                    ],
                    "translation": "湯姆叔叔的小屋",
                    "literal_meaning": "黑人奴隸向上天呼告的記錄",
                    "bold_literal_offsets": [(0, 4)],
                },
                {
                    "text": "黑奴吁天录",
                    "bold_text_offsets": [(0, 2)],
                    "roman": "Hēinú Yùtiānlù",
                    "bold_roman_offsets": [(0, 5)],
                    "tags": [
                        "Simplified-Chinese",
                        "Classical-Chinese",
                        "Pinyin",
                    ],
                    "translation": "湯姆叔叔的小屋",
                    "literal_meaning": "黑人奴隸向上天呼告的記錄",
                    "bold_literal_offsets": [(0, 4)],
                },
            ],
        )

    def test_ja_usex_literal_meaning(self):
        self.wxr.wtp.start_page("認識")
        self.wxr.wtp.add_page(
            "Template:ja-usex",
            10,
            """<span lang="ja" class="Jpan">-{その'''<ruby>認識<rp>(</rp><rt>にんしき</rt><rp>)</rp></ruby>'''で<ruby>正<rp>(</rp><rt>ただ</rt><rp>)</rp></ruby>しいと<ruby>思<rp>(</rp><rt>おも</rt><rp>)</rp></ruby>う。}-</span><dl><dd><i><span lang="la" class="tr">Sono '''ninshiki''' de tadashii to omou.</span></i></dd><dd>我相信你是對的。</dd><dd>(字面意思為「我相信你的'''理解'''是對的。」)</dd></dl>[[Category:有使用例的日語詞|言07言12]][[Category:有使用例的日語詞|言07言12]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(
            "#: {{ja-usex|その'''認識'''で正しいと思う。|その '''にんしき''' で ただし.い と おも.う。|我相信你是對的。|lit=我相信你的'''理解'''是對的。}}"
        )
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "その認識で正しいと思う。",
                    "bold_text_offsets": [(2, 4)],
                    "roman": "Sono ninshiki de tadashii to omou.",
                    "bold_roman_offsets": [(5, 13)],
                    "ruby": [
                        ("認識", "にんしき"),
                        ("正", "ただ"),
                        ("思", "おも"),
                    ],
                    "translation": "我相信你是對的。",
                    "literal_meaning": "我相信你的理解是對的。",
                    "bold_literal_offsets": [(5, 7)],
                },
            ],
        )

    def test_RQ_Qur_an(self):
        self.wxr.wtp.start_page("محمد")
        self.wxr.wtp.add_page(
            "Template:RQ:Qur'an",
            10,
            """<div class="citation-whole"><span class="cited-source">'''<small class='ce-date'>[[Appendix:術語表#CE|公元]]</small> 609年–632年''', <cite><span class="Jpan" lang="und">《[[古蘭經|-{古蘭經}-]]》</span></cite>, <span class="None" lang="und">[https://quran.com/3/144 3&#x3A;144]</span>:</span><dl><dd><div class="h-quotation"><span class="Arab e-quotation cited-passage" lang="ar">وَمَا '''مُحَمَّدٌ''' إِلَّا رَسُولٌ قَدْ خَلَتْ مِنْ قَبْلِهِ الرُّسُلُ</span><dl><dd><i lang="ar-Latn" class="e-transliteration tr Latn">wa-mā '''muḥammadun''' ʔillā rasūlun qad ḵalat min qablihi r-rusulu</i></dd><dd><span class="e-translation">'''穆罕默德'''只是一個使者，在他之前，有許多使者，確已逝去了。</span></dd></dl></div>[[Category:有引文的阿拉伯語詞|FACIES]]</dd></dl></div>""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(
            "#: {{RQ:Qur'an|3|144|passage=وَمَا '''مُحَمَّدٌ''' إِلَّا رَسُولٌ قَدْ خَلَتْ مِنْ قَبْلِهِ الرُّسُلُ|subst=وَمَا/وَ-مَا|translation='''穆罕默德'''只是一個使者，在他之前，有許多使者，確已逝去了。}}"
        )
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "وَمَا مُحَمَّدٌ إِلَّا رَسُولٌ قَدْ خَلَتْ مِنْ قَبْلِهِ الرُّسُلُ",
                    "bold_text_offsets": [(6, 15)],
                    "roman": "wa-mā muḥammadun ʔillā rasūlun qad ḵalat min qablihi r-rusulu",
                    "bold_roman_offsets": [(6, 16)],
                    "translation": "穆罕默德只是一個使者，在他之前，有許多使者，確已逝去了。",
                    "bold_translation_offsets": [(0, 4)],
                    "ref": "公元 609年–632年, 《古蘭經》, 3:144:",
                },
            ],
        )

    def test_ux(self):
        self.wxr.wtp.start_page("устав")
        self.wxr.wtp.add_page(
            "Template:ux",
            10,
            """<div class="h-usage-example"><i class="Cyrl mention e-example" lang="ru">[[в#俄語|-{В}-]] [[чужой#俄語|-{чужо́й}-]] [[монастырь#俄語|-{монасты́рь}-]] [[со#俄語|-{со}-]] [[свой#俄語|-{свои́м}-]] '''уста́вом''' [[не#俄語|-{не}-]] [[ходить#俄語|-{хо́дят}-]]</i> <span class="e-qualifier"><span class="ib-brac qualifier-brac">(</span><span class="ib-content qualifier-content">諺語</span><span class="ib-brac qualifier-brac">)</span></span><dl><dd><i lang="ru-Latn" class="e-transliteration tr Latn">V čužój monastýrʹ so svoím '''ustávom''' ne xódjat</i></dd><dd><span class="e-translation">入鄉隨俗，入境隨俗</span></dd><dd>(字面意思是「<span class="e-literally">你不能用你自己的憲章去另一個寺院</span>」)</dd></dl></div>""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(
            "#: {{ux|ru|[[в|В]] [[чужо́й]] [[монасты́рь]] [[со]] [[свой|свои́м]] '''уста́вом''' [[не]] [[ходить|хо́дят]]|入鄉隨俗，入境隨俗|lit=你不能用你自己的憲章去另一個寺院|q=諺語}}"
        )
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "В чужо́й монасты́рь со свои́м уста́вом не хо́дят",
                    "bold_text_offsets": [(30, 38)],
                    "roman": "V čužój monastýrʹ so svoím ustávom ne xódjat",
                    "bold_roman_offsets": [(27, 34)],
                    "translation": "入鄉隨俗，入境隨俗",
                    "literal_meaning": "你不能用你自己的憲章去另一個寺院",
                    "raw_tags": ["諺語"],
                },
            ],
        )

    def test_Q(self):
        self.wxr.wtp.start_page("кипяток")
        self.wxr.wtp.add_page(
            "Template:Q",
            10,
            """<div class="wiktQuote">P. Yershov, ''The Humpback Horse'' 駝背的馬:<dl><dd><span class="Cyrl e-quotation" lang="ru">Я кончаюсь, Горбунок: Царь велит мне в '''кипяток'''!</span><dl><dd><i lang="ru-Latn" class="e-transliteration tr Latn">Ja končajusʹ, Gorbunok&#x3A; Carʹ velit mne v '''kipjatok'''&#x21;</i></dd><dd>我將要完蛋，駝背。國王命令我跳入'''沸水'''中！</dd></dl></dd></dl></div>""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(
            "#: {{Q|ru|P. Yershov|The Humpback Horse|駝背的馬||quote=Я кончаюсь, Горбунок: Царь велит мне в '''кипяток'''!|trans=我將要完蛋，駝背。國王命令我跳入'''沸水'''中！}}"
        )
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "Я кончаюсь, Горбунок: Царь велит мне в кипяток!",
                    "bold_text_offsets": [(39, 46)],
                    "roman": "Ja končajusʹ, Gorbunok: Carʹ velit mne v kipjatok!",
                    "bold_roman_offsets": [(41, 49)],
                    "translation": "我將要完蛋，駝背。國王命令我跳入沸水中！",
                    "bold_translation_offsets": [(16, 18)],
                    "ref": "P. Yershov, The Humpback Horse 駝背的馬:",
                },
            ],
        )

    def test_ref_dd_span_tags(self):
        self.wxr.wtp.start_page("同志")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[同樣#漢語|同樣]][[受#漢語|受]][[到#漢語|到]][[歡迎#漢語|歡迎]][[的#漢語|的]]<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:現代標準漢語|現代標準漢語]]，[[w:繁体中文|繁體]]&#93;</span><br><span lang="zh-Hans" class="Hans">-{<!-- -->[[同样#漢語|同样]][[受#漢語|受]][[到#漢語|到]][[欢迎#漢語|欢迎]][[的#漢語|的]]<!-- -->}-</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:現代標準漢語|現代標準漢語]]，[[w:简体中文|簡體]]&#93;</span><dd><small>出自：'''2012'''年，-{<!----><span class="Hant" lang="zh">-{馬嘉蘭}-</span><!---->}-、-{<!----><span class="Hant" lang="zh">-{臺灣文學中的性越界}-</span><!---->}-，編輯-{<!----><span class="Hani" lang="zh">-{廖炳惠}-</span><!---->}-、-{<!----><span class="Hant" lang="zh">-{孫康宜}-</span><!---->}-、-{<!----><span class="Hani" lang="zh">-{王德威}-</span><!---->}-，-{<!----><span class="Hant" lang="zh">-{《臺灣及其脈絡》}-</span><!---->}-[https://books.google.com/books?id=cdCFqwRYNNwC&pg=PA329 第329頁]</small></dd><dd><span lang="zh-Latn" style="color:#404D52"><i>Tóngyàng shòudào huānyíng de</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:漢語拼音|漢語拼音]]&#93;</span></dd></dl>""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse(
            "#: {{zh-x|同樣 受-到 歡迎 的||ref='''2012'''年，{{lang|zh|馬嘉蘭}}、{{lang|zh|臺灣文學中的性越界}}，編輯{{lang|zh|廖炳惠}}、{{lang|zh|孫康宜}}、{{lang|zh|王德威}}，{{lang|zh|《臺灣及其脈絡》}}[https://books.google.com/books?id=cdCFqwRYNNwC&pg=PA329 第329頁]}}"
        )
        extract_example_list_item(
            self.wxr, sense_data, root.children[0].children[0], []
        )
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "同樣受到歡迎的",
                    "roman": "Tóngyàng shòudào huānyíng de",
                    "tags": [
                        "Pinyin",
                        "Standard-Chinese",
                        "Traditional-Chinese",
                    ],
                    "ref": "2012年，馬嘉蘭、臺灣文學中的性越界，編輯廖炳惠、孫康宜、王德威，《臺灣及其脈絡》第329頁",
                },
                {
                    "text": "同样受到欢迎的",
                    "roman": "Tóngyàng shòudào huānyíng de",
                    "tags": [
                        "Pinyin",
                        "Standard-Chinese",
                        "Simplified-Chinese",
                    ],
                    "ref": "2012年，馬嘉蘭、臺灣文學中的性越界，編輯廖炳惠、孫康宜、王德威，《臺灣及其脈絡》第329頁",
                },
            ],
        )

    def test_quote_under_plain_text_ref_list(self):
        self.wxr.wtp.add_page(
            "Template:ante", 10, "''[[Appendix:Glossary#a.|a.]]'' '''1937''',"
        )
        self.wxr.wtp.add_page(
            "Template:w", 10, "[[w:欧内斯特·卢瑟福|歐尼斯特·拉塞福]]"
        )
        self.wxr.wtp.add_page(
            "Template:quote",
            10,
            """<div class="h-quotation"><span class="Latn e-quotation" lang="en">-{All science is either physics or '''stamp collecting'''.}-</span><dl><dd><span class="e-translation">所有的科學不是物理學，就是'''集郵'''。</span></dd></dl></div>[[Category:有引文的英語詞|STAMPCOLLECTING]]""",
        )
        data = parse_page(
            self.wxr,
            "stamp collecting",
            """==英語==
===名詞===
# [[集郵]]
#* {{ante|1937}}，引自物理學家{{w|欧内斯特·卢瑟福|歐尼斯特·拉塞福}}：
#*: {{quote|en|All science is either physics or '''stamp collecting'''.|所有的科學不是物理學，就是'''集郵'''。}}""",
        )
        self.assertEqual(
            data[0]["senses"],
            [
                {
                    "categories": ["有引文的英語詞"],
                    "examples": [
                        {
                            "text": "All science is either physics or stamp collecting.",
                            "bold_text_offsets": [(33, 49)],
                            "ref": "a. 1937,，引自物理學家歐尼斯特·拉塞福：",
                            "translation": "所有的科學不是物理學，就是集郵。",
                            "bold_translation_offsets": [(13, 15)],
                        }
                    ],
                    "glosses": ["集郵"],
                }
            ],
        )

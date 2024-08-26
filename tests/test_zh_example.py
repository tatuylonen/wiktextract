from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.example import extract_examples
from wiktextract.extractor.zh.models import Sense
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"), WiktionaryConfig(dump_file_lang_code="zh")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_example_list(self) -> None:
        sense_data = Sense()
        wikitext = """
#* ref text
#*: example text
        """
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, sense_data, node, [])
        self.assertEqual(
            sense_data.examples[0].model_dump(exclude_defaults=True),
            {
                "ref": "ref text",
                "text": "example text",
            },
        )

    @patch(
        "wiktextract.extractor.zh.example.clean_node",
        return_value="""ref text
quote text
translation text""",
    )
    def test_quote_example(self, mock_clean_node) -> None:
        sense_data = Sense()
        wikitext = "#* {{RQ:Schuster Hepaticae}}"
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, sense_data, node, [])
        self.assertEqual(
            sense_data.examples[0].model_dump(exclude_defaults=True),
            {
                "ref": "ref text",
                "text": "quote text",
                "translation": "translation text",
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
        extract_examples(self.wxr, sense_data, root.children[0], [])
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "ref": "《尚書·梓材》",
                    "tags": [
                        "Classical Chinese",
                        "Traditional Chinese",
                        "Pinyin",
                    ],
                    "text": "王曰：「封，以厥庶民暨厥臣達大家，以厥臣達王惟邦君。」",
                    "roman": "Wáng yuē: “Fēng, yǐ jué shùmín jì jué chén dá dàjiā, yǐ jué chén dá wáng wéi bāngjūn.”",
                    "translation": "王說：「封啊，從殷的老百姓和他們的官員到卿大夫，從他們的官員到諸侯和國君。」",
                },
                {
                    "ref": "《尚書·梓材》",
                    "tags": [
                        "Classical Chinese",
                        "Simplified Chinese",
                        "Pinyin",
                    ],
                    "text": "王曰：「封，以厥庶民暨厥臣达大家，以厥臣达王惟邦君。」",
                    "roman": "Wáng yuē: “Fēng, yǐ jué shùmín jì jué chén dá dàjiā, yǐ jué chén dá wáng wéi bāngjūn.”",
                    "translation": "王說：「封啊，從殷的老百姓和他們的官員到卿大夫，從他們的官員到諸侯和國君。」",
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
        extract_examples(self.wxr, sense_data, root.children[0], [])
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "text": "中文授課",
                    "tags": ["Traditional Chinese"],
                    "roman": "zhōngwén shòukè",
                },
                {
                    "text": "中文授课",
                    "tags": ["Simplified Chinese"],
                    "roman": "zhōngwén shòukè",
                },
            ],
        )

    def test_example_under_example(self):
        self.wxr.wtp.start_page("英語")
        self.wxr.wtp.add_page("Template:quote-book", 10, "ref text")
        self.wxr.wtp.add_page(
            "Template:ja-usex",
            10,
            """<span lang="ja" class="Jpan">-{オレの<ruby>日<rp>(</rp><rt>に</rt><rp>)</rp></ruby><ruby>本<rp>(</rp><rt>ほん</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby>どう？<ruby>悪<rp>(</rp><rt>わる</rt><rp>)</rp></ruby>くないだろ　<ruby>韓<rp>(</rp><rt>かん</rt><rp>)</rp></ruby><ruby>国<rp>(</rp><rt>こく</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby>と'''<ruby>英<rp>(</rp><rt>えい</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby>'''も<ruby>話<rp>(</rp><rt>はな</rt><rp>)</rp></ruby>すんだぜ　<ruby>趣<rp>(</rp><rt>しゅ</rt><rp>)</rp></ruby><ruby>味<rp>(</rp><rt>み</rt><rp>)</rp></ruby>だな<ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby><ruby>学<rp>(</rp><rt>がく</rt><rp>)</rp></ruby>は　<ruby>寝<rp>(</rp><rt>ね</rt><rp>)</rp></ruby><ruby>泊<rp>(</rp><rt>とま</rt><rp>)</rp></ruby>りはどこ？<ruby>近<rp>(</rp><rt>ちか</rt><rp>)</rp></ruby>くのホテル？}-</span><dl><dd><i><span lang="la" class="tr">Ore no Nihongo dō? Waruku naidaro Kankokugo to '''Eigo''' mo hanasunda ze Shumi da na gogaku wa Netomari wa doko? Chikaku no hoteru?</span></i></dd><dd>我的日語怎麼樣？不差吧？我也會講韓語和英語。學習語言很有趣。你在哪裏住？附近的賓館嗎？</dd></dl>[[Category:有使用例的日語詞|廾65弋75]][[Category:有使用例的日語詞|廾65弋75]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse("""#* {{quote-book|ja}}\n#*: {{ja-usex}}""")
        extract_examples(self.wxr, sense_data, root.children[0], [])
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "ref": "ref text",
                    "text": "オレの日本語どう？悪くないだろ 韓国語と英語も話すんだぜ 趣味だな語学は 寝泊りはどこ？近くのホテル？",
                    "roman": "Ore no Nihongo dō? Waruku naidaro Kankokugo to Eigo mo hanasunda ze Shumi da na gogaku wa Netomari wa doko? Chikaku no hoteru?",
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
        self.wxr.wtp.add_page("Template:quote-book", 10, "ref text")
        self.wxr.wtp.add_page(
            "Template:zh-x",
            10,
            """<dl class="zhusex"><span lang="zh-Hant" class="Hant">-{<!-- -->[[如果#漢語|如果]][[唔係#漢語|唔係]][[今日#漢語|今日]][[拆穿#漢語|拆穿]][[你#漢語|你]][[槓嘢#漢語|槓野]]，[[畀#漢語|俾]][[你#漢語|你]][[混#漢語|混]][[咗#漢語|左]][[入#漢語|入]][[稅局#漢語|稅局]][[重#漢語|重]][[死人#漢語|死人]][[呀#漢語|呀]]！<!-- -->}-</span> <span>&#91;[[w:廣州話|廣州話]]，[[w:繁体中文|繁體]]&#93;</span><br><span lang="zh-Hans" class="Hans">-{<!-- -->[[如果#漢語|如果]][[唔系#漢語|唔系]][[今日#漢語|今日]][[拆穿#漢語|拆穿]][[你#漢語|你]][[杠嘢#漢語|杠野]]，[[畀#漢語|俾]][[你#漢語|你]][[混#漢語|混]][[咗#漢語|左]][[入#漢語|入]][[税局#漢語|税局]][[重#漢語|重]][[死人#漢語|死人]][[呀#漢語|呀]]！<!-- -->}-</span> <span>&#91;[[w:廣州話|廣州話]]，[[w:简体中文|簡體]]&#93;</span><dd><span lang="zh-Latn"><i>roman</i></span> <span>&#91;[[w:廣州話拼音方案|廣州話拼音]]&#93;</span></dd><dd>如果不是今天揭穿你的老底，給你混進稅務局就更'''糟糕'''了！</dd></dl>[[Category:有使用例的粵語詞]]""",
        )
        sense_data = Sense()
        root = self.wxr.wtp.parse("""#* {{quote-book|zh}}\n#*: {{zh-x}}""")
        extract_examples(self.wxr, sense_data, root.children[0], [])
        self.assertEqual(
            [e.model_dump(exclude_defaults=True) for e in sense_data.examples],
            [
                {
                    "raw_tags": ["廣州話", "廣州話拼音"],
                    "ref": "ref text",
                    "text": "如果唔係今日拆穿你槓野，俾你混左入稅局重死人呀！",
                    "roman": "roman",
                    "tags": ["Traditional Chinese"],
                    "translation": "如果不是今天揭穿你的老底，給你混進稅務局就更糟糕了！",
                },
                {
                    "raw_tags": ["廣州話", "廣州話拼音"],
                    "ref": "ref text",
                    "text": "如果唔系今日拆穿你杠野，俾你混左入税局重死人呀！",
                    "roman": "roman",
                    "tags": ["Simplified Chinese"],
                    "translation": "如果不是今天揭穿你的老底，給你混進稅務局就更糟糕了！",
                },
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ja.example import extract_example_list_item
from wiktextract.extractor.ja.models import Example, Sense
from wiktextract.extractor.ja.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestJaExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ja"),
            WiktionaryConfig(
                dump_file_lang_code="ja",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_puppy(self):
        self.wxr.wtp.start_page("puppy")
        root = self.wxr.wtp.parse("""#* ''I have another two [[dozen]] of these '''puppies''' to [[finish]] before I can go home.''
#*:あと、2ダースも済まさないと帰れないよ。""")
        sense = Sense()
        extract_example_list_item(
            self.wxr, None, sense, root.children[0].children[0]
        )
        self.assertEqual(
            sense.examples[0],
            Example(
                text="I have another two dozen of these puppies to finish before I can go home.",
                bold_text_offsets=[(34, 41)],
                translation="あと、2ダースも済まさないと帰れないよ。",
            ),
        )

    def test_ref_before_text(self):
        self.wxr.wtp.start_page("料理")
        root = self.wxr.wtp.parse("""#*1955年、中谷宇吉郎「面白味」<ref>青空文庫（2013年1月4日作成）（底本：「中谷宇吉郎随筆集」岩波文庫、岩波書店、2011年1月6日第26刷）https://www.aozora.gr.jp/cards/001569/files/53235_49838.html</ref>
#*:それらを買って来て、いろいろな'''料理'''をしてくれたのであるが、そのうちの牛蒡の煮附には、ちょっと驚いた。""")
        sense = Sense()
        extract_example_list_item(
            self.wxr, None, sense, root.children[0].children[0]
        )
        self.assertEqual(
            sense.examples[0],
            Example(
                text="それらを買って来て、いろいろな料理をしてくれたのであるが、そのうちの牛蒡の煮附には、ちょっと驚いた。",
                bold_text_offsets=[(15, 17)],
                ref="1955年、中谷宇吉郎「面白味」 青空文庫（2013年1月4日作成）（底本：「中谷宇吉郎随筆集」岩波文庫、岩波書店、2011年1月6日第26刷）https://www.aozora.gr.jp/cards/001569/files/53235_49838.html",
            ),
        )

    def test_one_line_ruby(self):
        self.wxr.wtp.start_page("なきむし")
        self.wxr.wtp.add_page(
            "テンプレート:ふりがな",
            10,
            "<ruby>[[{{{1}}}]]<rp>（</rp><rt>[[{{{2}}}]]</rt><rp>）</rp></ruby>",
        )
        root = self.wxr.wtp.parse(
            "#* {{ふりがな|尤|もっと|も}}も僕は[[気の毒]]にも{{ふりがな|度|たびたび}}大島を[[なく|泣か]]せては、[[なきむし|泣虫]][[なきむし|泣虫]]と[[からかう|からかひ]]しものなり。 （[[w:芥川龍之介|芥川龍之介]]『学校友だち』）〔1925年〕"
        )
        sense = Sense()
        extract_example_list_item(
            self.wxr, None, sense, root.children[0].children[0]
        )
        self.assertEqual(
            sense.examples[0],
            Example(
                text="尤も僕は気の毒にも度大島を泣かせては、泣虫泣虫とからかひしものなり。",
                bold_text_offsets=[(19, 21), (21, 23), (21, 24)],
                ref="（芥川龍之介『学校友だち』）〔1925年〕",
                ruby=[("尤", "もっと"), ("度", "たびたび")],
            ),
        )

    def test_one_line_ref_tag(self):
        self.wxr.wtp.start_page("なきむし")
        root = self.wxr.wtp.parse(
            "#* [[春夏]]と並んで、[[候鳥]]の「[[民間]][[伝承]]の[[うた|歌]]」に似たものは、秋の[[なきむし|鳴き虫]]の[[誹諧]]である。 （[[w:折口信夫|折口信夫]]『俳諧歌の研究』）〔1934年〕<ref>昭和9年5月、『続俳句講座』第3巻「特殊研究篇」初出、『折口信夫全集』13巻213ページ所収</ref>"
        )
        sense = Sense()
        extract_example_list_item(
            self.wxr, None, sense, root.children[0].children[0]
        )
        self.assertEqual(
            sense.examples[0],
            Example(
                text="春夏と並んで、候鳥の「民間伝承の歌」に似たものは、秋の鳴き虫の誹諧である。",
                bold_text_offsets=[(27, 31)],
                ref="（折口信夫『俳諧歌の研究』）〔1934年〕 昭和9年5月、『続俳句講座』第3巻「特殊研究篇」初出、『折口信夫全集』13巻213ページ所収",
            ),
        )

    def test_small_tag_ref(self):
        self.wxr.wtp.start_page("蜂窩生活")
        self.wxr.wtp.add_page(
            "テンプレート:Cite book",
            10,
            '<cite class="book" style="font-style:normal" id="Reference-[[w:關一|関一]]-1923">[[w:關一|関一]]『[https://dl.ndl.go.jp/pid/971383/1/35 住宅問題と都市計画]』弘文堂書房、1923年8月、53頁。</cite>',
        )
        root = self.wxr.wtp.parse(
            "#* 我々日本人は一日も速に旧式の一家族住ひの小住宅制度を止めて米国の'''蜂窩生活'''に倣ふべきであると教へて居る。<small>――{{Cite book|和書|author=[[w:關一|関一]]|title=住宅問題と都市計画|date=1923-08|publisher=弘文堂書房|page=53|url=https://dl.ndl.go.jp/pid/971383/1/35}}</small>"
        )
        sense = Sense()
        extract_example_list_item(
            self.wxr, None, sense, root.children[0].children[0]
        )
        self.assertEqual(
            sense.examples[0].model_dump(exclude_defaults=True),
            {
                "text": "我々日本人は一日も速に旧式の一家族住ひの小住宅制度を止めて米国の蜂窩生活に倣ふべきであると教へて居る。",
                "bold_text_offsets": [(32, 36)],
                "ref": "――関一『住宅問題と都市計画』弘文堂書房、1923年8月、53頁。",
            },
        )

    def test_ux_template(self):
        self.wxr.wtp.add_page(
            "テンプレート:ux",
            10,
            """<div class="h-usage-example"><i class="Cyrl mention e-example" lang="uk">У [[зелений#ウクライナ語|зеле́ному]] '''ча́ї''' [[багато#ウクライナ語|бага́то]] [[вітамін#ウクライナ語|вітамі́нів]].</i><dl><dd><i lang="uk-Latn" class="e-transliteration tr Latn">U zelénomu '''čáji''' baháto vitamíniv.</i></dd><dd><span class="e-translation">緑'''茶の葉'''にはたくさんのビタミンが含まれる。</span></dd></dl></div>[[カテゴリ:ウクライナ語 例文あり|ЧАЙ]]""",
        )
        page_data = parse_page(
            self.wxr,
            "чай",
            """==ウクライナ語==
===名詞===
# [[茶葉]]。
#* {{ux|uk|У [[зелений|зеле́ному]] '''ча́ї''' [[бага́то]] [[вітамін|вітамі́нів]].|緑'''茶の葉'''にはたくさんのビタミンが含まれる。}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["ウクライナ語 例文あり"],
                    "examples": [
                        {
                            "text": "У зеле́ному ча́ї бага́то вітамі́нів.",
                            "bold_text_offsets": [(12, 16)],
                            "roman": "U zelénomu čáji baháto vitamíniv.",
                            "bold_roman_offsets": [(11, 15)],
                            "translation": "緑茶の葉にはたくさんのビタミンが含まれる。",
                            "bold_translation_offsets": [(1, 4)],
                        }
                    ],
                    "glosses": ["茶葉。"],
                }
            ],
        )

    def test_ux_strong_tag(self):
        self.wxr.wtp.add_page("テンプレート:q", 10, """({{{1}}})""")
        self.wxr.wtp.add_page(
            "テンプレート:ux",
            10,
            """<div class="h-usage-example"><i class="Latn mention e-example" lang="pl">[[ty#ポーランド語|Tobie]] [[świecić#ポーランド語|świeci]] <strong class="selflink">miesiąc</strong>, [[a#ポーランド語|a]] [[ja#ポーランド語|mnie]] [[świecić#ポーランド語|świecą]] [[gwiazda#ポーランド語|gwiazdy]]. （民謡 &quot;To i hola&quot;）</i><dl><dd><span class="e-translation">[[あんた]][[の#助詞|の]][[ため]][[に#助詞|に]][[は#助詞|は]]'''月'''[[しか]][[かがやく|輝い]][[て#助詞|て]][[いる|い]][[ない]][[けれど]]、[[わたし|私]]には[[たくさん]]の[[ほし|星]][[が#助詞|が]]輝いてくれる。</span></dd></dl></div>[[カテゴリ:ポーランド語 例文あり|MIESIA􏿿C]]""",
        )
        page_data = parse_page(
            self.wxr,
            "miesiąc",
            """==ポーランド語==
===名詞===
# [[つき|月]]。
## {{q|[[こよみ|暦]]の}} [[つき|月]]。
##* '''注．''' ''月の用法に関しては、styczeń を参照。''
## 〔[[詩]]や[[方言]]で〕{{q|[[天体]]の}} 月。
##* {{ux|pl|[[ty|Tobie]] [[świecić|świeci]] [[miesiąc]], [[a]] [[ja|mnie]] [[świecić|świecą]] [[gwiazda|gwiazdy]]. （民謡 &quot;To i hola&quot;）|[[あんた]][[の#助詞|の]][[ため]][[に#助詞|に]][[は#助詞|は]]'''月'''[[しか]][[かがやく|輝い]][[て#助詞|て]][[いる|い]][[ない]][[けれど]]、[[わたし|私]]には[[たくさん]]の[[ほし|星]][[が#助詞|が]]輝いてくれる。}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {"glosses": ["月。"]},
                {
                    "glosses": ["月。", "(暦の) 月。"],
                    "notes": ["月の用法に関しては、styczeń を参照。"],
                },
                {
                    "glosses": ["月。", "〔詩や方言で〕(天体の) 月。"],
                    "categories": ["ポーランド語 例文あり"],
                    "examples": [
                        {
                            "text": 'Tobie świeci miesiąc, a mnie świecą gwiazdy. （民謡 "To i hola"）',
                            "bold_text_offsets": [(13, 20)],
                            "translation": "あんたのためには月しか輝いていないけれど、私にはたくさんの星が輝いてくれる。",
                            "bold_translation_offsets": [(8, 9)],
                        }
                    ],
                },
            ],
        )

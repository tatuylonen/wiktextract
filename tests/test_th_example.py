from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.th.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestThExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="th"),
            WiktionaryConfig(
                dump_file_lang_code="th", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_ux(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ko-usex",
            10,
            """<div class="h-usage-example"><i class="Kore mention e-example" lang="ko">^파리는 ^프랑스의 '''서울'''이다.</i><dl><dd><i lang="ko-Latn" class="e-transliteration tr Latn">Pari-neun Peurangseu-ui '''seour'''-ida.</i></dd><dd><span class="e-translation">ปารีสคือเมืองหลวงของฝรั่งเศส</span></dd></dl></div>[[Category:ศัพท์ภาษาเกาหลีที่มีตัวอย่างการใช้|서울]]""",
        )
        self.wxr.wtp.add_page(
            "แม่แบบ:audio",
            10,
            """<table><tr><td>เสียง <span class="ib-brac qualifier-brac">(</span><span class="usage-label-accent"><span class="ib-content">South Korea</span></span><span class="ib-brac qualifier-brac">)</span><span class="ib-colon qualifier-colon">:</span></td><td class="audiofile">[[File:서울에 가요.ogg|noicon|175px]]</td><td class="audiometa">([[:File:서울에 가요.ogg|file]])</td></tr></table>[[Category:ศัพท์ภาษาเกาหลีที่มีลิงก์เสียง|서울]]""",
        )
        page_data = parse_page(
            self.wxr,
            "서울",
            """== ภาษาเกาหลี ==
=== คำนาม ===
{{ko-noun}}

# [[เมืองหลวง]]; [[เมือง]][[ใหญ่]]
#: {{ko-usex|^파리-는 ^프랑스-의 '''서울'''-이다.|ปารีสคือเมืองหลวงของฝรั่งเศส}}
#:: {{audio|ko|서울에 가요.ogg|a=South Korea}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0]["examples"][0]["sounds"][0]["audio"],
            "서울에 가요.ogg",
        )
        del page_data[0]["senses"][0]["examples"][0]["sounds"]
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": [
                    "ศัพท์ภาษาเกาหลีที่มีตัวอย่างการใช้",
                    "ศัพท์ภาษาเกาหลีที่มีลิงก์เสียง",
                ],
                "glosses": ["เมืองหลวง; เมืองใหญ่"],
                "examples": [
                    {
                        "text": "^파리는 ^프랑스의 서울이다.",
                        "bold_text_offsets": [(11, 13)],
                        "roman": "Pari-neun Peurangseu-ui seour-ida.",
                        "bold_roman_offsets": [(24, 29)],
                        "translation": "ปารีสคือเมืองหลวงของฝรั่งเศส",
                    }
                ],
            },
        )

    def test_zh_x_one_line(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:zh-x",
            10,
            """<span lang="zh-Hant" class="Hant"><b>大家</b>[[都#Chinese|都]][[還#Chinese|還]][[行#Chinese|行]]。</span><span lang="zh-Hani" class="Hani">／</span><span lang="zh-Hans" class="Hans"><b>大家</b>[[都#Chinese|都]][[还#Chinese|还]][[行#Chinese|行]]。</span>&nbsp; ―&nbsp; <span lang="zh-Latn" style="color:#404D52"><i><b>Dàjiā</b> dōu hái xíng.</i></span>&nbsp; ―&nbsp; '''ทุกคน'''ยังสบายดี[[Category:ศัพท์ภาษาจีนกลางที่มีตัวอย่างการใช้]]""",
        )
        page_data = parse_page(
            self.wxr,
            "大家",
            """== ภาษาจีน ==
=== คำสรรพนาม ===
{{zh-pronoun}}

# [[ทุกคน]]; [[พวกเรา]]ทุกคน
#: {{zh-x|大家 都 還 行。|'''ทุกคน'''ยังสบายดี}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": ["ศัพท์ภาษาจีนกลางที่มีตัวอย่างการใช้"],
                "glosses": ["ทุกคน; พวกเราทุกคน"],
                "examples": [
                    {
                        "text": "大家都還行。",
                        "bold_text_offsets": [(0, 2)],
                        "roman": "Dàjiā dōu hái xíng.",
                        "bold_roman_offsets": [(0, 5)],
                        "translation": "ทุกคนยังสบายดี",
                        "bold_translation_offsets": [(0, 5)],
                        "tags": ["Traditional-Chinese"],
                    },
                    {
                        "text": "大家都还行。",
                        "bold_text_offsets": [(0, 2)],
                        "roman": "Dàjiā dōu hái xíng.",
                        "bold_roman_offsets": [(0, 5)],
                        "translation": "ทุกคนยังสบายดี",
                        "bold_translation_offsets": [(0, 5)],
                        "tags": ["Simplified-Chinese"],
                    },
                ],
            },
        )

    def test_hant_and_hans_same_text(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:zh-x",
            10,
            """<dl class="zhusex"><span lang="zh-Hant" class="Hant"><b>大家</b>[[都#Chinese|都]][[很#Chinese|很]][[尊敬#Chinese|尊敬]][[他#Chinese|他]]。</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:Standard Chinese|MSC]], <i>[[w:Traditional Chinese|trad.]]</i> and <i>[[w:Simplified Chinese|simp.]]</i>&#93;</span><dd><span lang="zh-Latn" style="color:#404D52"><i><b>Dàjiā</b> dōu hěn zūnjìng tā.</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;Pinyin&#93;</span></dd><dd>'''ทุกคน'''ต่างเคารพเขามาก</dd></dl>[[Category:ศัพท์ภาษาจีนกลางที่มีตัวอย่างการใช้]]""",
        )
        page_data = parse_page(
            self.wxr,
            "大家",
            """== ภาษาจีน ==
=== คำสรรพนาม ===
{{zh-pronoun}}

# [[ทุกคน]]; [[พวกเรา]]ทุกคน
#: {{zh-x|大家 都 很 尊敬 他。|'''ทุกคน'''ต่างเคารพเขามาก}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": ["ศัพท์ภาษาจีนกลางที่มีตัวอย่างการใช้"],
                "glosses": ["ทุกคน; พวกเราทุกคน"],
                "examples": [
                    {
                        "text": "大家都很尊敬他。",
                        "bold_text_offsets": [(0, 2)],
                        "roman": "Dàjiā dōu hěn zūnjìng tā.",
                        "bold_roman_offsets": [(0, 5)],
                        "translation": "ทุกคนต่างเคารพเขามาก",
                        "bold_translation_offsets": [(0, 5)],
                        "tags": [
                            "Modern Standard Chinese",
                            "Traditional-Chinese",
                            "Simplified-Chinese",
                            "Pinyin",
                        ],
                    }
                ],
            },
        )

    def test_zh_x_two_text_lines(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:zh-x",
            10,
            """<dl class="zhusex"><span lang="zh-Hant" class="Hant">[[請#Chinese|請]]<b>大家</b>[[保持#Chinese|保持]][[安靜#Chinese|安靜]]。</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:Standard Chinese|MSC]], <i>[[w:Traditional Chinese|trad.]]</i>&#93;</span><br><span lang="zh-Hans" class="Hans">[[请#Chinese|请]]<b>大家</b>[[保持#Chinese|保持]][[安静#Chinese|安静]]。</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:Standard Chinese|MSC]], <i>[[w:Simplified Chinese|simp.]]</i>&#93;</span><dd><span lang="zh-Latn" style="color:#404D52"><i>Qǐng <b>dàjiā</b> bǎochí ānjìng.</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;Pinyin&#93;</span></dd><dd>'''ทุกคน'''กรุณาเงียบ</dd></dl>[[Category:ศัพท์ภาษาจีนกลางที่มีตัวอย่างการใช้]]""",
        )
        page_data = parse_page(
            self.wxr,
            "大家",
            """== ภาษาจีน ==
=== คำสรรพนาม ===
{{zh-pronoun}}

# [[ทุกคน]]; [[พวกเรา]]ทุกคน
#: {{zh-x|請 大家 保持 安靜。|'''ทุกคน'''กรุณาเงียบ}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": ["ศัพท์ภาษาจีนกลางที่มีตัวอย่างการใช้"],
                "glosses": ["ทุกคน; พวกเราทุกคน"],
                "examples": [
                    {
                        "text": "請大家保持安靜。",
                        "bold_text_offsets": [(1, 3)],
                        "roman": "Qǐng dàjiā bǎochí ānjìng.",
                        "bold_roman_offsets": [(5, 10)],
                        "translation": "ทุกคนกรุณาเงียบ",
                        "bold_translation_offsets": [(0, 5)],
                        "tags": [
                            "Modern Standard Chinese",
                            "Traditional-Chinese",
                            "Pinyin",
                        ],
                    },
                    {
                        "text": "请大家保持安静。",
                        "bold_text_offsets": [(1, 3)],
                        "roman": "Qǐng dàjiā bǎochí ānjìng.",
                        "bold_roman_offsets": [(5, 10)],
                        "translation": "ทุกคนกรุณาเงียบ",
                        "bold_translation_offsets": [(0, 5)],
                        "tags": [
                            "Modern Standard Chinese",
                            "Simplified-Chinese",
                            "Pinyin",
                        ],
                    },
                ],
            },
        )

    def test_ja_x(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:quote-book",
            10,
            """<div class="citation-whole"><span class="cited-source">'''1990''' มิถุนายน 15,  [[w:Rumiko Takahashi|Takahashi, Rumiko]],  “[[:แม่แบบ:jaru]] &#91;PART.5 Snatching the Scroll of Secrets&#93;”, in  <cite>[[:แม่แบบ:wj]]</cite> &#91;<cite>[[w:Ranma ½|Ranma ½]]</cite>&#93;, volume 11 (fiction), Tokyo&#58; Shogakukan, <small>[[Special:BookSources/4-09-122431-8|→ISBN]]</small>, page 72:[[Category:ศัพท์ภาษาญี่ปุ่นที่มีการยกข้อความ|大00宀07]]</span><dl><dd></dd></dl></div>""",
        )
        self.wxr.wtp.add_page(
            "แม่แบบ:ja-usex",
            10,
            """<span lang="ja" class="Jpan"><ruby>日<rp>(</rp><rt>にっ</rt><rp>)</rp></ruby><ruby>本<rp>(</rp><rt>ぽん</rt><rp>)</rp></ruby>の<ruby>山<rp>(</rp><rt>さん</rt><rp>)</rp></ruby><ruby>中<rp>(</rp><rt>ちゅう</rt><rp>)</rp></ruby>に…'''シロクマ'''がいるか—————っ‼</span><dl><dd><i><span class="tr">Nippon no sanchū ni… '''shirokuma''' ga iru ka—————'‼</span></i></dd><dd>ทำไมถึงมี...หมีขั้วโลกบนภูเขาญี่ปุ่นได้⁉</dd></dl>[[Category:ศัพท์ภาษาญี่ปุ่นที่มีตัวอย่างการใช้|大00宀07]]""",
        )
        self.wxr.wtp.add_page(
            "แม่แบบ:syn of",
            10,
            """<span class='form-of-definition use-with-mention'>คำพ้องความของ <span class='form-of-definition-link'><i class="Jpan mention" lang="ja">[[北極熊#ภาษาญี่ปุ่น|北極熊]]</i> <span class="mention-gloss-paren annotation-paren">(</span><span class="mention-tr tr">ฮกเกียวกุงุมะ</span>, <span class="mention-gloss-double-quote">“</span><span class="mention-gloss">หมีขั้วโลก</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren annotation-paren">)</span></span></span>""",
        )
        page_data = parse_page(
            self.wxr,
            "白熊",
            """== ภาษาญี่ปุ่น ==
=== คำนาม ===
{{ja-noun|しろくま|シロクマ}}

# {{syn of|ja|北極熊|tr=ฮกเกียวกุงุมะ||หมีขั้วโลก}}
#* {{quote-book|ja
|| |{{wj|らんま1/2|らんま½}}
|| 72
| last=Takahashi
| first=Rumiko
| authorlink=Rumiko Takahashi
| chapter={{jaru|[ＰＡＲＴ] (パート).５　[秘] (ひ) [伝] (でん) [書] (しょ) を[奪] (うば) え}}
| trans-chapter=PART.5 Snatching the Scroll of Secrets
| trans-title={{w|Ranma ½}}
| genre=fiction
| location=Tokyo
| publisher=Shogakukan
| date=Jun 15 1990
| volume=11
| isbn=4-09-122431-8}}
#*: {{ja-usex|日%本の山%中に…'''シロクマ'''がいるか—————っ‼|^にっ%ぽん の さん%ちゅう に… '''シロクマ''' が いる か—————っ‼|ทำไมถึงมี...หมีขั้วโลกบนภูเขาญี่ปุ่นได้⁉}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": [
                    "ศัพท์ภาษาญี่ปุ่นที่มีการยกข้อความ",
                    "ศัพท์ภาษาญี่ปุ่นที่มีตัวอย่างการใช้",
                ],
                "glosses": ["คำพ้องความของ 北極熊 (ฮกเกียวกุงุมะ, “หมีขั้วโลก”)"],
                "examples": [
                    {
                        "text": "日本の山中に…シロクマがいるか—————っ‼",
                        "bold_text_offsets": [(7, 11)],
                        "roman": "Nippon no sanchū ni… shirokuma ga iru ka—————'‼",
                        "bold_roman_offsets": [(21, 30)],
                        "translation": "ทำไมถึงมี...หมีขั้วโลกบนภูเขาญี่ปุ่นได้⁉",
                        "ruby": [
                            ("日", "にっ"),
                            ("本", "ぽん"),
                            ("山", "さん"),
                            ("中", "ちゅう"),
                        ],
                        "ref": "1990 มิถุนายน 15, Takahashi, Rumiko, “:แม่แบบ:jaru [PART.5 Snatching the Scroll of Secrets]”, in :แม่แบบ:wj [Ranma ½], volume 11 (fiction), Tokyo: Shogakukan, →ISBN, page 72:",
                    }
                ],
                "form_of": [{"word": "北極熊", "roman": "ฮกเกียวกุงุมะ"}],
                "tags": ["form-of"],
            },
        )

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

    def test_ux(self):
        self.wxr.wtp.add_page(
            "แม่แบบ:ko-usex",
            10,
            """<div class="h-usage-example"><i class="Kore mention e-example" lang="ko">^파리는 ^프랑스의 '''서울'''이다.</i><dl><dd><i lang="ko-Latn" class="e-transliteration tr Latn">Pari-neun Peurangseu-ui '''seour'''-ida.</i></dd><dd><span class="e-translation">ปารีสคือเมืองหลวงของฝรั่งเศส</span></dd></dl></div>[[Category:ศัพท์ภาษาเกาหลีที่มีตัวอย่างการใช้|서울]]""",
        )
        page_data = parse_page(
            self.wxr,
            "서울",
            """== ภาษาเกาหลี ==
=== คำนาม ===
{{ko-noun}}

# [[เมืองหลวง]]; [[เมือง]][[ใหญ่]]
#: {{ko-usex|^파리-는 ^프랑스-의 '''서울'''-이다.|ปารีสคือเมืองหลวงของฝรั่งเศส}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "categories": ["ศัพท์ภาษาเกาหลีที่มีตัวอย่างการใช้"],
                "glosses": ["เมืองหลวง; เมืองใหญ่"],
                "examples": [
                    {
                        "text": "^파리는 ^프랑스의 서울이다.",
                        "roman": "Pari-neun Peurangseu-ui seour-ida.",
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
                        "roman": "Dàjiā dōu hái xíng.",
                        "translation": "ทุกคนยังสบายดี",
                        "tags": ["Traditional Chinese"],
                    },
                    {
                        "text": "大家都还行。",
                        "roman": "Dàjiā dōu hái xíng.",
                        "translation": "ทุกคนยังสบายดี",
                        "tags": ["Simplified Chinese"],
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
                        "roman": "Dàjiā dōu hěn zūnjìng tā.",
                        "translation": "ทุกคนต่างเคารพเขามาก",
                        "tags": [
                            "Modern Standard Chinese",
                            "Traditional Chinese",
                            "Simplified Chinese",
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
            """<dl class="zhusex"><span lang="zh-Hant" class="Hant">[[請#Chinese|請]]<b>大家</b>[[保持#Chinese|保持]][[安靜#Chinese|安靜]]。</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:Standard Chinese|MSC]], <i>[[w:Traditional Chinese|trad.]]</i>&#93;</span><br><span lang="zh-Hans" class="Hans">[[请#Chinese|请]]<b>大家</b>[[保持#Chinese|保持]][[安静#Chinese|安静]]。</span> <span style="color:darkgreen; font-size:x-small;">&#91;[[w:Standard Chinese|MSC]], <i>[[w:Simplified Chinese|simp.]]</i>&#93;</span><dd><span lang="zh-Latn" style="color:#404D52"><i>Qǐng <b>dàjiā</b> bǎochí ānjìng.</i></span> <span style="color:darkgreen; font-size:x-small;">&#91;Pinyin&#93;</span></dd><dd>'''ทุกคน'''กรุณาเงียบ</dd></dl>[[Category:ศัพท์ภาษาจีนกลางที่มีตัวอย่างการใช้]]
""",
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
                        "roman": "Qǐng dàjiā bǎochí ānjìng.",
                        "translation": "ทุกคนกรุณาเงียบ",
                        "tags": [
                            "Modern Standard Chinese",
                            "Traditional Chinese",
                            "Pinyin",
                        ],
                    },
                    {
                        "text": "请大家保持安静。",
                        "roman": "Qǐng dàjiā bǎochí ānjìng.",
                        "translation": "ทุกคนกรุณาเงียบ",
                        "tags": [
                            "Modern Standard Chinese",
                            "Simplified Chinese",
                            "Pinyin",
                        ],
                    },
                ],
            },
        )

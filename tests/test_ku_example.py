from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ku.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKuExample(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ku"),
            WiktionaryConfig(
                dump_file_lang_code="ku", capture_language_codes=None
            ),
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_jêder_example(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:jêder",
            10,
            """<i><span class="Latn" lang="ku">'''Kûçikên''' li hewşa pêş û paşî, ji hîva rûnixumandî tirsnaktir û ji ecacokê hartir, gez dikin bê.</span></i><span class="jeder">&nbsp;—&nbsp;(<span class="j-pewist">[[w:Îrfan Amîda|Îrfan Amîda]]</span>,&nbsp;<i><span class="j-pewist">Şevek Şîzofren</span></i>,&nbsp;[[w:Weşanên Lîs|Weşanên Lîs]],&nbsp;<span class="j-pewist">2018</span>,&nbsp;r. 6,&nbsp;ISBN 9786058152175[[Kategorî:Jêgirtinên kitêban bi kurmancî]][[Kategorî:Jêgirtinên ji Îrfan Amîda]])</span>[[Kategorî:Jêgirtin bi kurmancî]]<span class="example"><bdi lang="ku"></bdi></span>""",
        )
        page_data = parse_page(
            self.wxr,
            "kûçik",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[heywan|Heywanek]]
#* {{jêder|ku|jêgirtin='''Kûçikên''' li hewşa pêş û paşî, ji hîva rûnixumandî tirsnaktir û ji ecacokê hartir, gez dikin bê.|{{Jêgirtin/Îrfan Amîda/Şevek Şîzofren|r=6}}}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": [
                        "Jêgirtinên kitêban bi kurmancî",
                        "Jêgirtinên ji Îrfan Amîda",
                        "Jêgirtin bi kurmancî",
                    ],
                    "glosses": ["Heywanek"],
                    "examples": [
                        {
                            "text": "Kûçikên li hewşa pêş û paşî, ji hîva rûnixumandî tirsnaktir û ji ecacokê hartir, gez dikin bê.",
                            "bold_text_offsets": [(0, 7)],
                            "ref": "Îrfan Amîda, Şevek Şîzofren, Weşanên Lîs, 2018, r. 6, ISBN 9786058152175",
                        }
                    ],
                }
            ],
        )

    def test_ux(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Koreyî")
        self.wxr.wtp.add_page(
            "Şablon:ux",
            10,
            """<div class="h-usage-example"><i class="Kore mention e-example" lang="ko">-{[[스스로#Koreyî|스스로]] [[확인#Koreyî|확인]] '''가능'''}-</i><dl><dd><i lang="ko-Latn" class="e-transliteration tr Latn"><i>-{seuseuro hwagin '''ganeung'''}-</i></i></dd><dd><span class="e-translation">self-kontrolbar / şexsen tesdîq dibe / mimkin e şexsen piştrast bike</span></dd></dl></div>[[Category:Nimûne bi koreyî|가능]]""",
        )
        self.wxr.wtp.add_page(
            "Şablon:navdêr",
            10,
            """<strong class="Kore headword" lang="ko">-{가능}-</strong>&nbsp;<i>(ganeung)</i> <i>(</i><i>hanja</i> <span class="Kore form-of lang-ko hanja-form-of" lang="ko">-{[[:可能#koreyî|可能]]}-</span><i>)</i>[[Kategorî:Navdêr bi koreyî]]""",
        )
        page_data = parse_page(
            self.wxr,
            "가능",
            """== {{ziman|ko}} ==
=== Navdêr ===
{{navdêr|ko|hanja=可能}}
# [[îmkan|Îmkan]],  [[derfet]]; [[ihtimal]]
#: {{ux|ko|[[스스로]] [[확인]] '''가능'''|self-kontrolbar / şexsen tesdîq dibe / mimkin e şexsen piştrast bike}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["Nimûne bi koreyî"],
                    "glosses": ["Îmkan, derfet; ihtimal"],
                    "examples": [
                        {
                            "text": "스스로 확인 가능",
                            "bold_text_offsets": [(7, 9)],
                            "roman": "seuseuro hwagin ganeung",
                            "bold_roman_offsets": [(16, 23)],
                            "translation": "self-kontrolbar / şexsen tesdîq dibe / mimkin e şexsen piştrast bike",
                        }
                    ],
                }
            ],
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "可能", "tags": ["Hanja"]},
                {"form": "ganeung", "tags": ["romanization"]},
            ],
        )
        self.assertEqual(page_data[0]["categories"], ["Navdêr bi koreyî"])

    def test_deng(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Koreyî")
        self.wxr.wtp.add_page(
            "Şablon:mk",
            10,
            """<div class="h-usage-example"><i class="Kore mention e-example" lang="ko">-{서울에 '''가요'''}-</i> ― <i lang="ko-Latn" class="e-transliteration tr Latn"><i>-{Seoul-e '''gayo'''.}-</i></i> ― <span class="e-translation">(Ez, tu, em û hwd) biçin Sêûlê.</span></div>[[Category:Nimûne bi koreyî|가다]]""",
        )
        page_data = parse_page(
            self.wxr,
            "가능",
            """== {{ziman|ko}} ==
=== Lêker ===
# [[çûn]]
#: {{mk|ko|서울에 '''가요'''|tr=Seoul-e '''gayo'''.|w=(Ez, tu, em û hwd) biçin Sêûlê.|birêz=1}}
#:: {{deng|ko|서울에 가요.ogg|Deng}}""",
        )
        self.assertEqual(
            page_data[0]["senses"][0]["examples"][0]["sounds"][0]["audio"],
            "서울에 가요.ogg",
        )

    def test_italic(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        page_data = parse_page(
            self.wxr,
            "rast",
            """== {{ziman|ku}} ==
=== Rengdêr ===
# [[bêxeletî]]
#: ''Bersiva te '''rast''' e.''""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "glosses": ["bêxeletî"],
                    "examples": [
                        {
                            "bold_text_offsets": [(11, 15)],
                            "text": "Bersiva te rast e.",
                        }
                    ],
                }
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ku.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKuDesc(TestCase):
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

    def test_desc(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Erebî")
        self.wxr.wtp.add_page(
            "Şablon:dardû",
            10,
            """<span class="desc-arr" title="deynkirî">→</span> Farisî: <span class="fa-Arab" lang="fa">-{[[رسم#Farisî|رسم]]}-</span>&lrm; <span class="mention-gloss-paren annotation-paren">(</span><span lang="fa-Latn" class="tr Latn"><i>-{rasm}-</i></span><span class="mention-gloss-paren annotation-paren">)</span><ul><li>→ Hindûstanî:<dl><dd>Hindî: <span class="Deva" lang="hi">-{[[रस्म#Hindî|रस्म]]}-</span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="hi-Latn" class="tr Latn"><i>-{rasma}-</i></span><span class="mention-gloss-paren annotation-paren">)</span></dd><dd>Urdûyî: <span class="ur-Arab" lang="ur">-{[[رسم#Urdûyî|رسم]]}-</span>&lrm; <span class="mention-gloss-paren annotation-paren">(</span><span lang="ur-Latn" class="tr Latn"><i>-{rasm}-</i></span><span class="mention-gloss-paren annotation-paren">)</span></dd></dl></li></ul>""",
        )
        self.wxr.wtp.add_page(
            "Şablon:dû",
            10,
            """{{#switch: {{{1}}}
|ota=<span class="desc-arr" title="deynkirî">→</span> Osmanî: <span class="ota-Arab" lang="ota">-{[[رسم#Osmanî|رسم]]}-</span>&lrm; <span class="mention-gloss-paren annotation-paren">(</span><span lang="ota-Latn" class="tr Latn"><i>-{resm, resim}-</i></span><span class="mention-gloss-paren annotation-paren">)</span>
|tr=Tirkî: <span class="Latn" lang="tr">-{[[resim#Tirkî|resim]]}-</span>
}}""",
        )
        page_data = parse_page(
            self.wxr,
            "رسم",
            """== {{ziman|ar}} ==
=== Navdêr ===
# [[wêne]], [[nîgar]], [[foto]], [[fotograf]], [[nexş]]
==== Dûnde ====
* {{dardû|fa|رسم|tr=rasm|deyn=1}}
* {{dû|ota|رسم|tr=resm, resim|deyn=1}}
** {{dû|tr|resim}}""",
        )
        self.assertEqual(
            page_data[0]["descendants"],
            [
                {
                    "lang": "Farisî",
                    "lang_code": "fa",
                    "word": "رسم",
                    "roman": "rasm",
                    "descendants": [
                        {
                            "lang": "Hindî",
                            "lang_code": "hi",
                            "word": "रस्म",
                            "roman": "rasma",
                        },
                        {
                            "lang": "Urdûyî",
                            "lang_code": "ur",
                            "word": "رسم",
                            "roman": "rasm",
                        },
                    ],
                },
                {
                    "lang": "Osmanî",
                    "lang_code": "ota",
                    "word": "رسم",
                    "roman": "resm, resim",
                    "descendants": [
                        {"lang": "Tirkî", "lang_code": "tr", "word": "resim"}
                    ],
                },
            ],
        )

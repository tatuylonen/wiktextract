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

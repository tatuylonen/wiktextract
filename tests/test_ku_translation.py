from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ku.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKuTranslation(TestCase):
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

    def test_w_template(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page("Şablon:Z", 10, "Akadî")
        self.wxr.wtp.add_page(
            "Şablon:W-",
            10,
            """<span class="Xsux" lang="akk">[[𒌨#Akadî|𒌨]]</span>&nbsp;<span class="gender"><abbr title="zayenda nêr">n</abbr></span> <span class="mention-gloss-paren annotation-paren">(</span><span lang="akk-Latn" class="tr Latn"><i>kalbu, UR</i></span><span class="mention-gloss-paren annotation-paren">)</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "kûçik",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[heywan|Heywanek]]
==== Werger ====
{{werger-ser}}
* {{Z|akk}}: {{W-|akk|𒌨|n|tr=kalbu, UR}}
{{werger-bin}}""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [
                {
                    "word": "𒌨",
                    "lang": "Akadî",
                    "lang_code": "akk",
                    "roman": "kalbu, UR",
                    "tags": ["masculine"],
                }
            ],
        )

    def test_link(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        page_data = parse_page(
            self.wxr,
            "av",
            """== {{ziman|ku}} ==
=== Navdêr ===
# [[vexwarin|Vexwarin]]a bê[[reng]]
==== Werger ====
* [[bolognezî]]: [[âcua]]""",
        )
        self.assertEqual(
            page_data[0]["translations"],
            [{"word": "âcua", "lang": "bolognezî", "lang_code": "unknown"}],
        )

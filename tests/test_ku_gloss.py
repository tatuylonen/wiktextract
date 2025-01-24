from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ku.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKuGloss(TestCase):
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

    def test_f_template(self):
        self.wxr.wtp.add_page(
            "Şablon:ziman",
            10,
            """<span class="sectionlangue" id="ku">[[kurmancî|Kurmancî]][[Kategorî:Kurmancî]]</span>""",
        )
        self.wxr.wtp.add_page(
            "Şablon:f",
            10,
            """<i><span class="ib-brac">(</span><span class="ib-content">[[guhandar]][[Category:Guhandar bi kurmancî|A]]</span><span class="ib-brac">)</span></i>""",
        )
        page_data = parse_page(
            self.wxr,
            "kûçik",
            """== {{ziman|ku}} ==
=== Navdêr ===
# {{f|ku|guhandar}} [[heywan|Heywanek]]""",
        )
        self.assertEqual(
            page_data[0],
            {
                "categories": ["Kurmancî"],
                "lang": "Kurmancî",
                "lang_code": "ku",
                "word": "kûçik",
                "pos": "noun",
                "pos_title": "Navdêr",
                "senses": [
                    {
                        "categories": ["Guhandar bi kurmancî"],
                        "glosses": ["Heywanek"],
                        "raw_tags": ["guhandar"],
                    }
                ],
            },
        )

    def test_navdêr(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Almanî")
        page_data = parse_page(
            self.wxr,
            "Wähler",
            """== {{ziman|de}} ==
=== Navdêr ===
{{navdêr|de|z=n|m=Wählerin}}
# [[hilbijêr]]""",
        )
        self.assertEqual(page_data[0]["tags"], ["masculine"])
        self.assertEqual(
            page_data[0]["forms"], [{"form": "Wählerin", "tags": ["feminine"]}]
        )

    def test_lêker(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Farisî")
        page_data = parse_page(
            self.wxr,
            "کردن",
            """== {{ziman|fa}} ==
=== Lêker ===
{{lêker|fa|tr=kerden|niha=کن|nihatr=kon|borî=کرد|borîtr=kerd}}
# [[kirin]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "kerden", "tags": ["romanization"]},
                {"form": "کن", "tags": ["present"], "roman": "kon"},
                {"form": "کرد", "tags": ["past"], "roman": "kerd"},
            ],
        )

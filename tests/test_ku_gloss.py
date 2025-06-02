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
                        "topics": ["mammals"],
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

    def test_form_of(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:formeke peyvê",
            10,
            "Rewşa îzafeyî ya binavkirî ya pirjimar ya nêr ya kûçik.",
        )
        page_data = parse_page(
            self.wxr,
            "kûçikên",
            """== {{ziman|fa}} ==
=== Formeke navdêrê ===
# {{formeke peyvê|ku|kûçik||îzafe|ya|binavkirî|ya|pirjimar|ya|nêr}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "form_of": [{"word": "kûçik"}],
                    "glosses": [
                        "Rewşa îzafeyî ya binavkirî ya pirjimar ya nêr ya kûçik."
                    ],
                    "tags": [
                        "form-of",
                        "construct",
                        "definite",
                        "plural",
                        "masculine",
                    ],
                }
            ],
        )

    def test_nested_gloss_list(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:komparatîv",
            10,
            '<i>Forma [[komparatîv]] ji rengdêra</i>&nbsp;<strong class="Latn headword" lang="ku">[[zêde#Kurmancî|zêde]]</strong>.[[Kategorî:Komparatîv bi kurmancî]]',
        )
        page_data = parse_page(
            self.wxr,
            "zêdetir",
            """== {{ziman|ku}} ==
=== Formeke rengdêrê ===
# {{komparatîv|ku|zêde}}
## [[pirtir]]""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "categories": ["Komparatîv bi kurmancî"],
                    "form_of": [{"word": "zêde"}],
                    "glosses": ["Forma komparatîv ji rengdêra zêde."],
                    "tags": ["form-of"],
                },
                {
                    "categories": ["Komparatîv bi kurmancî"],
                    "form_of": [{"word": "zêde"}],
                    "glosses": ["Forma komparatîv ji rengdêra zêde.", "pirtir"],
                    "tags": ["form-of"],
                },
            ],
        )

    def test_bnr(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Kurmancî")
        self.wxr.wtp.add_page(
            "Şablon:bnr", 10, "''Binêre'' '''[[hejmar]]''', '''[[jimar]]'''."
        )
        page_data = parse_page(
            self.wxr,
            "jimare",
            """== {{ziman|ku}} ==
=== Navdêr ===
# {{bnr|hejmar|jimar}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "alt_of": [{"word": "hejmar"}, {"word": "jimar"}],
                    "glosses": ["Binêre hejmar, jimar."],
                    "tags": ["alt-of"],
                }
            ],
        )

    def test_binêre_el(self):
        self.wxr.wtp.add_page("Şablon:ziman", 10, "Almanî")
        page_data = parse_page(
            self.wxr,
            "Cultur",
            """== {{ziman|de}} ==
=== Navdêr ===
{{binêre/el|Kultur}}""",
        )
        self.assertEqual(
            page_data[0]["senses"],
            [
                {
                    "alt_of": [{"word": "Kultur"}],
                    "tags": ["no-gloss", "alt-of", "obsolete"],
                }
            ],
        )

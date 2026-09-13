from importlib import import_module
from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext


class TestAsianEtymologyLinks(TestCase):
    editions = ("zh", "ja", "ko", "th", "vi", "id", "ku")

    def context(self, code):
        wxr = WiktextractContext(
            Wtp(lang_code=code),
            WiktionaryConfig(
                dump_file_lang_code=code, capture_language_codes=None
            ),
        )
        self.addCleanup(wxr.wtp.close_db_conn)
        wxr.wtp.start_page("test")
        return wxr

    def entry(self, code):
        model = import_module(f"wiktextract.extractor.{code}.models").WordEntry
        return model(word="test", lang=code, lang_code=code, pos="noun")

    def extract(self, code, wxr, entry, text, page_data=None):
        extract = import_module(
            f"wiktextract.extractor.{code}.etymology"
        ).extract_etymology_section
        node = wxr.wtp.parse(text).children[0]
        if code in ("ja", "zh"):
            extract(wxr, page_data or [], entry, node)
        else:
            extract(wxr, entry, node)

    def test_expanded_and_ordinary_links_keep_scripts_anchors_and_duplicates(
        self,
    ):
        for code in self.editions:
            with self.subTest(code=code):
                wxr = self.context(code)
                wxr.wtp.add_page(
                    f"{wxr.wtp.NAMESPACE_DATA['Template']['name']}:etym-link-test",
                    10,
                    "[[水#Chinese|水]] [[Category:Etymology test]]",
                )
                entry = self.entry(code)
                self.extract(
                    code,
                    wxr,
                    entry,
                    """===Etymology===
[[ὕδωρ#Ancient Greek|ὕδωρ]] {{etym-link-test}} [[水#Chinese|水]]
====Noun====
# [[not-etymology]]""",
                )
                self.assertEqual(entry.etymology_texts, ["ὕδωρ 水 水"])
                self.assertEqual(
                    entry.etymology_links,
                    [
                        ("ὕδωρ", "ὕδωρ#Ancient Greek"),
                        ("水", "水#Chinese"),
                        ("水", "水#Chinese"),
                    ],
                )
                self.assertEqual(entry.categories, ["Etymology test"])

    def test_list_links_exclude_subsections_and_empty_defaults(self):
        for code in self.editions:
            with self.subTest(code=code):
                wxr = self.context(code)
                entry = self.entry(code)
                self.assertNotIn(
                    "etymology_links", entry.model_dump(exclude_defaults=True)
                )
                self.extract(
                    code,
                    wxr,
                    entry,
                    """===Etymology===
* From [[آب#Persian|آب]].
* Compare [[पानी#Hindi|पानी]].
====Pronunciation====
* [[not-etymology]]""",
                )
                self.assertEqual(
                    entry.etymology_links,
                    [
                        ("آب", "آب#Persian"),
                        ("पानी", "पानी#Hindi"),
                    ],
                )
                plain = self.entry(code)
                self.extract(code, wxr, plain, "===Etymology===\nUnknown.")
                self.assertEqual(plain.etymology_texts, ["Unknown."])
                self.assertNotIn(
                    "etymology_links", plain.model_dump(exclude_defaults=True)
                )

    def test_alternative_form_tables_are_not_etymology_prose(self):
        for code in ("zh", "ko", "th", "vi"):
            with self.subTest(code=code):
                wxr = self.context(code)
                wxr.wtp.add_page(
                    f"{wxr.wtp.NAMESPACE_DATA['Template']['name']}:ja-kanjitab",
                    10,
                    "[[not-etymology]]",
                )
                entry = self.entry(code)
                self.extract(
                    code,
                    wxr,
                    entry,
                    """===Etymology===
{{ja-kanjitab}}
From [[水]].""",
                )
                self.assertEqual(entry.etymology_texts, ["From 水."])
                self.assertEqual(entry.etymology_links, [("水", "水")])

    def test_japanese_pos_propagation_and_etymology_reset(self):
        wxr = self.context("ja")
        base = self.entry("ja")
        previous = self.entry("ja")
        self.extract(
            "ja", wxr, base, "====Etymology====\n[[first]]", [previous]
        )
        self.assertEqual(previous.etymology_links, [("first", "first")])
        self.extract("ja", wxr, base, "===Etymology 2===\n[[second]]")
        self.assertEqual(base.etymology_links, [("second", "second")])
        self.assertEqual(previous.etymology_links, [("first", "first")])
        self.extract("ja", wxr, base, "===Etymology 3===\nUnknown.")
        self.assertNotIn(
            "etymology_links", base.model_dump(exclude_defaults=True)
        )

    def test_korean_reset_and_inline_etymology(self):
        wxr = self.context("ko")
        entry = self.entry("ko")
        self.extract("ko", wxr, entry, "===Etymology 1===\n[[first]]")
        self.extract("ko", wxr, entry, "===Etymology 2===\n[[second]]")
        self.assertEqual(entry.etymology_texts, ["second"])
        self.assertEqual(entry.etymology_links, [("second", "second")])
        from wiktextract.extractor.ko.page import parse_page

        data = parse_page(
            wxr,
            "test",
            """==한국어==
===명사===
* 어원: [[水#Chinese|물]]
# [[not-etymology]]""",
        )
        self.assertEqual(data[0]["etymology_links"], [("물", "水#Chinese")])

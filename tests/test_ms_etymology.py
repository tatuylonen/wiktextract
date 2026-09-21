import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ms.models import WordEntry
from wiktextract.extractor.ms.page import extract_etymology_section, parse_page
from wiktextract.wxr_context import WiktextractContext


class TestMsEtymology(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="ms"),
            WiktionaryConfig(
                dump_file_lang_code="ms", capture_language_codes=None
            ),
        )
        self.wxr.wtp.start_page("test")

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def entry(self, lang="ms", pos="noun"):
        return WordEntry(word="test", lang_code=lang, lang=lang, pos=pos)

    def test_links_before_pos_survive_page_copy(self):
        self.wxr.wtp.add_page(
            "Templat:l-test", 10, "[[{{{1}}}#ms|{{{2}}}]][[Kategori:Etimologi]]"
        )
        entries = parse_page(
            self.wxr,
            "test",
            "== Bahasa Melayu ==\n=== Etimologi ===\n{{l-test|asal|asál}} + [[asal#ms|asál]]\n=== Kata nama ===\n# nama\n=== Kata kerja ===\n# kerja",
        )
        self.assertEqual(len(entries), 2)
        for entry in entries:
            self.assertEqual(
                entry["etymology_links"],
                [("asál", "asal#ms"), ("asál", "asal#ms")],
            )
            self.assertEqual(entry["etymology_texts"], ["asál + asál"])
            self.assertIn("Etimologi", entry["categories"])

    def test_language_level_assignment_excludes_other_languages(self):
        entries = [self.entry("en"), self.entry(), self.entry(pos="verb")]
        node = self.wxr.wtp.parse(
            "===Etimologi===\n* [[source#ms|source]]"
        ).children[0]
        extract_etymology_section(self.wxr, entries, self.entry(), node)
        self.assertEqual(entries[0].etymology_links, [])
        self.assertEqual(entries[1].etymology_links, [("source", "source#ms")])
        self.assertEqual(entries[2].etymology_links, entries[1].etymology_links)
        entries[1].etymology_links.append(("other", "other"))
        self.assertEqual(entries[2].etymology_links, [("source", "source#ms")])

    def test_pos_etymology_replaces_only_last_entry(self):
        entries = [self.entry(), self.entry(pos="verb")]
        node = self.wxr.wtp.parse("====Etimologi====\n[[source]]").children[0]
        extract_etymology_section(self.wxr, entries, self.entry(), node)
        self.assertEqual(entries[0].etymology_links, [])
        self.assertEqual(entries[1].etymology_links, [("source", "source")])
        plain = self.wxr.wtp.parse("====Etimologi====\nUnknown.").children[0]
        extract_etymology_section(self.wxr, entries, self.entry(), plain)
        self.assertEqual(entries[1].etymology_links, [])
        self.assertNotIn(
            "etymology_links", entries[1].model_dump(exclude_defaults=True)
        )

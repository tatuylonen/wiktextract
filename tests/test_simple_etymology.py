import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.simple.etymology import process_etym
from wiktextract.extractor.simple.models import WordEntry
from wiktextract.extractor.simple.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestSimpleEtymology(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="simple"),
            WiktionaryConfig(dump_file_lang_code="simple"),
        )
        self.wxr.wtp.start_page("test")

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_expanded_links_and_subsection_exclusion(self):
        self.wxr.wtp.add_page(
            "Template:link-test", 10, "[[{{{1}}}|{{{2}}}]][[Category:Test]]"
        )
        node = self.wxr.wtp.parse(
            "==Etymology==\n{{link-test|word#Noun|word}} + [[word#Noun|word]]\n===Other===\n[[excluded]]"
        ).children[0]
        entry = WordEntry(word="test")
        process_etym(self.wxr, node, entry)
        self.assertEqual(entry.etymology_text, "word + word")
        self.assertEqual(
            entry.etymology_links,
            [("word", "word#Noun"), ("word", "word#Noun")],
        )
        self.assertEqual(entry.categories, ["Test"])
        self.assertEqual(
            entry.model_dump(mode="json")["etymology_links"],
            [["word", "word#Noun"], ["word", "word#Noun"]],
        )

    def test_plain_text_omits_links(self):
        entry = WordEntry(word="test")
        node = self.wxr.wtp.parse("==Etymology==\nUnknown.").children[0]
        process_etym(self.wxr, node, entry)
        self.assertNotIn(
            "etymology_links", entry.model_dump(exclude_defaults=True)
        )

    def test_page_copies_etymology_to_parts_of_speech(self):
        entries = parse_page(
            self.wxr,
            "test",
            "==Etymology==\nFrom [[source]].\n==Noun==\n# a test\n==Verb==\n# to test",
        )
        self.assertEqual(len(entries), 2)
        self.assertTrue(
            all(e["etymology_links"] == [("source", "source")] for e in entries)
        )

import unittest
from unittest.mock import patch

from wikitextprocessor import Page, WikiNode, Wtp
from wikitextprocessor.parser import print_tree

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.simple.models import Sense, WordEntry
from wiktextract.extractor.simple.pos import process_pos
from wiktextract.wxr_context import WiktextractContext


class GlossTests(unittest.TestCase):
    # maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="simple"),
            WiktionaryConfig(dump_file_lang_code="simple"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def process_test(self, text: str, should_be: list[list[str]]) -> None:
        self.wxr.wtp.start_page("foo")
        entry = WordEntry(word="foo")
        root = self.wxr.wtp.parse(text)
        # print_tree(root)
        process_pos(self.wxr, root.children[0], entry, "noun")
        # print(entry.model_dump(exclude_defaults=True))
        for sense, target in zip(entry.senses, should_be):
            self.assertEqual(sense.glosses, target)

    def test_glosses1(self) -> None:
        pos = """==Noun==
# Foo.
"""
        should_be = [
            [
                "Foo.",
            ]
        ]
        self.process_test(pos, should_be)

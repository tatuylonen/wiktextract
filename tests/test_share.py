import unittest

from wikitextprocessor import NodeKind, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.share import calculate_bold_offsets, split_senseids
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


class TestShare(unittest.TestCase):
    maxDiff = None

    def test_split_senseids(self):
        test_cases = [
            ("[1]", ["1"]),
            ("[1,2]", ["1", "2"]),
            ("[1, 2]", ["1", "2"]),
            ("[1, 2 ]", ["1", "2"]),
            ("[1-3]", ["1", "2", "3"]),
            ("[1, 3-5]", ["1", "3", "4", "5"]),
            ("[1, 3-4, 6]", ["1", "3", "4", "6"]),
            ("[1a]", ["1a"]),
            ("[1, 2a]", ["1", "2a"]),
            ("[1, 2a-3]", ["1", "2", "3"]),
        ]

        for test_case in test_cases:
            self.assertEqual(split_senseids(test_case[0]), test_case[1])


class TestBoldOffsets(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_unbalanced_apostrophes(self):
        # https://de.wiktionary.org/wiki/orient
        self.wxr.wtp.start_page("orient")
        root = self.wxr.wtp.parse("El sol surt per l'''orient.''")
        text = clean_node(self.wxr, None, root)
        self.assertEqual(text, "El sol surt per l'orient.")
        data = {}
        calculate_bold_offsets(
            self.wxr,
            root,
            text,
            data,
            "bold_text_offsets",
            extra_node_kind=NodeKind.ITALIC,
        )
        self.assertEqual(data["bold_text_offsets"], [(18, 25)])

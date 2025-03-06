from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.pos import process_pos
from wiktextract.wxr_context import WiktextractContext


class TestElHeader(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="el"),
            WiktionaryConfig(
                dump_file_lang_code="el",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_el_head1(self) -> None:
        self.wxr.wtp.start_page("φώσφορος")
        data = WordEntry(lang="Greek", lang_code="el", word="φώσφορος")
        root = self.wxr.wtp.parse(
"""==={{ουσιαστικό|el}}===
'''{{PAGENAME}}''' ''ή'' '''[[φωσφόρος]]''' (''αρσενικό'') ''και'' '''[[φώσφορο]]''' (''ουδέτερο'')
* foo
"""
)
        pos_node = root.children[0]
        process_pos(self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[])
        # print(f"{data.model_dump(exclude_defaults=True)}")

        expected = [
            {"form": "φώσφορος", "raw_tags": ["αρσενικό"]},
            {"form": "φωσφόρος", "raw_tags": ["αρσενικό"]},
            {"form": "φώσφορο", "raw_tags": ["ουδέτερο"]},
        ]
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped["forms"], expected)

    def test_en_head1(self) -> None:
        self.wxr.wtp.start_page("free")
        data = WordEntry(lang="Greek", lang_code="en", word="free")
        root = self.wxr.wtp.parse(
"""==={{επίθετο|en}}===
'''{{PAGENAME}}''' (en)
# foo"""
)
        pos_node = root.children[0]
        process_pos(self.wxr, pos_node, data, None, "noun", "ουσιαστικό", pos_tags=[])
        # print(f"{data.model_dump(exclude_defaults=True)}")

        expected = [
            {"form": "free"},
        ]
        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped["forms"], expected)

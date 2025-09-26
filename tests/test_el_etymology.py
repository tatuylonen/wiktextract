from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestElEtymology(TestCase):
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

    def test_form_of_etymologies(self) -> None:
        page_datas = parse_page(
            self.wxr,
            "κατακουκουλωμένος",
            """==Νέα ελληνικά (el)==
===Ετυμολογία===
: '''{{PAGENAME}}''' < {{μτχππ}} [[φοο]] < [[κατα-]] + [[κουκουλώνω]]

===Μετοχή===
'''{{PAGENAME}}, -η, -ο'''
* (εμφατικό) εντελώς κουκουλωμένος""",
        )
        self.assertEqual(len(page_datas), 1)
        page_data = page_datas[0]
        self.assertEqual(page_data["form_of"], [{"word": "φοο"}])
        self.assertEqual(
            page_data["etymology_text"],
            # Broken templates left as is. Fix this if you make proper
            # mock templates or something for these tests
            "κατακουκουλωμένος < :Πρότυπο:μτχππ φοο < κατα- + κουκουλώνω",
        )

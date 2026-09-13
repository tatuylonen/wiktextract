from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
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

    def test_template_and_ordinary_links(self):
        self.wxr.wtp.add_page(
            "Πρότυπο:link-test",
            10,
            "[[{{{1}}}#Ελληνικά|{{{2}}}]][[Κατηγορία:Ετυμολογία]]",
        )
        entries = parse_page(
            self.wxr,
            "λέξη",
            "==Νέα ελληνικά (el)==\n===Ετυμολογία===\n"
            "{{link-test|πηγή|πηγής}} + [[πηγή#Ελληνικά|πηγής]]\n"
            "===Ουσιαστικό===\n# [[ορισμός]]",
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["etymology_links"],
            [("πηγής", "πηγή#Ελληνικά"), ("πηγής", "πηγή#Ελληνικά")],
        )
        self.assertEqual(entries[0]["etymology_text"], "πηγής + πηγής")
        self.assertIn("Ετυμολογία", entries[0]["categories"])

    def test_plain_etymology_omits_links(self):
        entries = parse_page(
            self.wxr,
            "λέξη",
            "==Νέα ελληνικά (el)==\n===Ετυμολογία===\nΆγνωστη.\n"
            "===Ουσιαστικό===\n# ορισμός",
        )
        self.assertEqual(len(entries), 1)
        self.assertNotIn("etymology_links", entries[0])

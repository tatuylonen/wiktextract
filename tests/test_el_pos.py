from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.page import parse_page
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

    def mktest_pos(self, raw, expected) -> None:
        self.wxr.wtp.add_page("Πρότυπο:-el-", 10, "Νέα ελληνικά (el)")
        self.wxr.wtp.add_page("Πρότυπο:μετοχή", 10, "Μετοχή")
        self.wxr.wtp.add_page("Πρότυπο:ετυμολογία", 10, "Ετυμολογία")

        word = "word_filler"
        page_datas = parse_page(self.wxr, word, raw)
        received = page_datas[0]["pos"]
        self.assertEqual(expected, received)

    def test_el_participle_is_adj_at_etym(self) -> None:
        # https://el.wiktionary.org/wiki/ζαρωμένος
        raw = """=={{-el-}}==

==={{ετυμολογία}}===
: '''{{PAGENAME}}''' < {{μτχππ|ζαρώνω}}

==={{μετοχή|el}}===
'''{{PAGENAME}}, -η, -ο'''
* foo
"""
        self.mktest_pos(raw, "adj")

    def test_el_participle_is_adj_at_main(self) -> None:
        # https://el.wiktionary.org/wiki/ψηφίσας
        raw = """=={{-el-}}==

==={{μετοχή|el}}===
'''{{PAGENAME}}, -ασα, -αν'''
* {{μτχεα|ψηφίζω|el|χ+=ψήφισα}}: που [[ψηφίζω|ψήφισε]]
"""
        self.mktest_pos(raw, "adj")

    def test_el_participle_is_verb_at_main(self) -> None:
        # https://el.wiktionary.org/wiki/αναδεικνύοντας
        raw = """=={{-el-}}==

==={{μετοχή|el}}===
'''{{PAGENAME}}'''
* {{μτχεε|αναδεικνύω}}
"""
        self.mktest_pos(raw, "verb")

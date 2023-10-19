# Tests for parsing a page from the German Wiktionary

import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.page import parse_page, parse_section
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestDEPage(unittest.TestCase):
    def setUp(self):
        conf1 = WiktionaryConfig(
            dump_file_lang_code="de",
            # capture_language_codes=None,
            # capture_translations=True,
            # capture_pronunciation=True,
            # capture_linkages=True,
            # capture_compounds=True,
            # capture_redirects=True,
            # capture_examples=True,
        )
        self.wxr = WiktextractContext(Wtp(lang_code="de"), conf1)
        self.maxDiff = None

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_de_parse_page(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "")
        lst = parse_page(
            self.wxr,
            "Beispiel",
            """
== Beispiel ({{Sprache|Deutsch}}) ==
""",
        )
        self.assertEqual(
            lst,
            [
                {
                    "lang": "Deutsch",
                    "lang_code": "de",
                    "word": "Beispiel",
                }
            ],
        )

    def test_de_parse_page_skipping_head_templates(self):
        self.wxr.wtp.add_page("Vorlage:Wort der Woche", 10, "")
        self.wxr.wtp.add_page("Vorlage:Siehe auch", 10, "")
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "")
        lst = parse_page(
            self.wxr,
            "Beispiel",
            """
{{Wort der Woche|46|2020}}
{{Siehe auch|[[cát]]}}
== Beispiel ({{Sprache|Deutsch}}) ==
""",
        )
        self.assertEqual(
            lst,
            [
                {
                    "lang": "Deutsch",
                    "lang_code": "de",
                    "word": "Beispiel",
                }
            ],
        )

    # The way append_base_data() works requires the presence of a sense
    # dictionary before starting a new pos section. Therefore, we need to add
    # at least one sense data point to the test case.

    def test_de_parse_section(self):
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "")
        self.wxr.wtp.add_page("Vorlage:Bedeutungen", 10, "")
        page_text = "=== {{Wortart|Adjektiv|Englisch}}, {{Wortart|Adverb|Englisch}} ===\n====Bedeutungen====\n:[1] gloss1\n=== {{Wortart|Verb|Englisch}} ===\n====Bedeutungen====\n:[1] gloss2\n=== {{Wortart|Substantiv|Englisch}} ===\n====Bedeutungen====\n:[1] gloss3"
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            page_text,
            pre_expand=True,
        )

        base_data = defaultdict(list, {"lang_code": "de"})
        page_data = [defaultdict(list, {"lang_code": "de"})]
        parse_section(self.wxr, page_data, base_data, root.children)

        self.assertEqual(
            page_data,
            [
                {
                    "lang_code": "de",
                    "pos": "adj",
                    "senses": [
                        {
                            "glosses": ["gloss1"],
                            "senseid": "1",
                            "raw_glosses": ["[1] gloss1"],
                        },
                    ],
                },
                {
                    "lang_code": "de",
                    "pos": "adv",
                    "senses": [
                        {
                            "glosses": ["gloss1"],
                            "senseid": "1",
                            "raw_glosses": ["[1] gloss1"],
                        },
                    ],
                },
                {
                    "lang_code": "de",
                    "pos": "verb",
                    "senses": [
                        {
                            "glosses": ["gloss2"],
                            "senseid": "1",
                            "raw_glosses": ["[1] gloss2"],
                        },
                    ],
                },
                {
                    "lang_code": "de",
                    "pos": "noun",
                    "senses": [
                        {
                            "glosses": ["gloss3"],
                            "senseid": "1",
                            "raw_glosses": ["[1] gloss3"],
                        },
                    ],
                },
            ],
        )

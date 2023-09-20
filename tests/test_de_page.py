# Tests for parsing a page from the German Wiktionary

import unittest
from unittest.mock import patch

from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.page import (
    parse_page,
    parse_section,
    fix_level_hierarchy_of_subsections,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class DePageTests(unittest.TestCase):
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

    def mock_append_base_data_side_effects(
        self, page_data, field: str, value, base_data
    ) -> None:
        import copy

        if page_data[-1].get(field) is not None:
            if len(page_data[-1]["senses"]) > 0:
                # append new dictionary if the last dictionary has sense data and
                # also has the same key
                page_data.append(copy.deepcopy(base_data))
            elif isinstance(page_data[-1].get(field), list):
                page_data[-1][field] += value
            else:
                page_data.append(copy.deepcopy(base_data))

        else:
            page_data[-1][field] = value

    @patch("wiktextract.extractor.de.page.append_base_data")
    def test_de_parse_section(self, mock_append_base_data):
        mock_append_base_data.side_effect = (
            self.mock_append_base_data_side_effects
        )

        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "")
        page_text = """
=== {{Wortart|Adjektiv|Englisch}}, {{Wortart|Adverb|Englisch}} ===
=== {{Wortart|Verb|Englisch}} ===
=== {{Wortart|Substantiv|Englisch}} ===
"""
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
                {"lang_code": "de", "pos": "adj", "senses": []},
                {"lang_code": "de", "pos": "adv", "senses": []},
                {"lang_code": "de", "pos": "verb", "senses": []},
                {"lang_code": "de", "pos": "noun"},
            ],
        )

    def test_de_fix_level_hierarchy_of_subsections(self):
        self.wxr.wtp.add_page("Vorlage:Englisch Substantiv Übersicht", 10, "")
        self.wxr.wtp.add_page("Vorlage:Worttrennung", 10, "")
        self.wxr.wtp.add_page("Vorlage:Aussprache", 10, "")
        self.wxr.wtp.add_page("Vorlage:Übersetzungen", 10, "")
        self.wxr.wtp.add_page("Vorlage:Ü-Tabelle", 10, "")
        self.wxr.wtp.add_page("Vorlage:Referenzen", 10, "")

        page_text = """
{{Englisch Substantiv Übersicht
|args=args}}

{{Worttrennung}}
:item

{{Aussprache}}
:item

==== {{Übersetzungen}} ====
{{Ü-Tabelle|1|G=arg|Ü-Liste=
:item
}}

{{Referenzen}}
:item
"""
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            page_text,
            pre_expand=True,
        )

        subsections = fix_level_hierarchy_of_subsections(
            self.wxr, root.children
        )

        target_page_text = """==== {{Englisch Substantiv Übersicht\n|args=args}} ====

==== {{Worttrennung}} ====
:item

==== {{Aussprache}} ====
:item

==== {{Übersetzungen}} ====
{{Ü-Tabelle|1|G=arg|Ü-Liste=
:item
}}

==== {{Referenzen}} ====
:item
"""
        root = self.wxr.wtp.parse(
            target_page_text,
            pre_expand=True,
        )

        self.assertEqual(
            [str(s) for s in subsections],
            [str(t) for t in root.children],
        )

"""Preserve entry links separately from cleaned etymology prose."""

import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class EnEtymologyLinkTests(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(capture_language_codes=None),
        )
        # Small deterministic stand-ins for the linking templates' expanded
        # output. Exercise the real parser/expander without a Wiktionary dump.
        for name in ("m", "mention", "m-self", "l", "link", "ll", "l-self"):
            self.wxr.wtp.add_page(
                f"Template:{name}",
                10,
                "<i>[[{{{2}}}#{{#switch:{{{1}}}|fr=French|la=Latin"
                "|grc=Ancient Greek}}|{{{3|{{{2}}}}}}]]</i>",
            )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def parse(self, etymology, body="===Verb===\n# to [[swallow]]"):
        return parse_page(
            self.wxr,
            "avaler",
            f"==French==\n===Etymology===\n{etymology}\n{body}\n",
        )

    def test_avaler_mentions(self):
        # Exact etymology wikitext from French avaler, revision 86488854.
        entry = self.parse("{{m|fr|aval}} + {{m|fr|-er}}")[0]
        self.assertEqual(entry["etymology_text"], "aval + -er")
        self.assertEqual(
            entry["etymology_links"],
            [("aval", "aval#French"), ("-er", "-er#French")],
        )
        self.assertNotIn("etymology_templates", entry)
        self.assertNotIn("links", entry)
        self.assertEqual(entry["senses"][0]["links"], [("swallow", "swallow")])

    def test_mention_and_link_aliases(self):
        for template in ("mention", "m-self", "l", "link", "ll", "l-self"):
            with self.subTest(template=template):
                entry = self.parse("{{" + template + "|fr|aval}}")[0]
                self.assertEqual(
                    entry["etymology_links"], [("aval", "aval#French")]
                )
                self.assertNotIn("etymology_templates", entry)

    def test_different_display_text_and_language_anchors(self):
        entry = self.parse(
            "From {{m|la|mansio|mānsiōnem}} and "
            "{{l|grc|λόγος}}; compare [[aval#French|downstream]]."
        )[0]
        self.assertEqual(
            entry["etymology_links"],
            [
                ("mānsiōnem", "mansio#Latin"),
                ("λόγος", "λόγος#Ancient Greek"),
                ("downstream", "aval#French"),
            ],
        )

    def test_plain_links_and_repeated_mentions(self):
        entry = self.parse(
            "[[aval#French|aval]] + [[-er#French|-er]]; "
            "[[aval#French|aval]] and [[word]]."
        )[0]
        self.assertEqual(
            entry["etymology_links"],
            [
                ("aval", "aval#French"),
                ("-er", "-er#French"),
                ("aval", "aval#French"),
                ("word", "word"),
            ],
        )

    def test_categories_are_not_links_or_new_entry_metadata(self):
        entry = self.parse(
            "{{m|fr|aval}} [[Category:French terms derived from Latin]]"
        )[0]
        self.assertEqual(entry["etymology_links"], [("aval", "aval#French")])
        self.assertEqual(entry["etymology_text"], "aval")
        self.assertNotIn(
            "French terms derived from Latin", entry.get("categories", [])
        )

    def test_nested_link_does_not_change_captured_templates(self):
        self.wxr.wtp.add_page("Template:bor", 10, "From {{m|{{{2}}}|{{{3}}}}}.")
        entry = self.parse("{{bor|fr|la|mansio}}")[0]
        self.assertEqual(entry["etymology_links"], [("mansio", "mansio#Latin")])
        self.assertEqual(
            entry["etymology_templates"],
            [
                {
                    "name": "bor",
                    "args": {"1": "fr", "2": "la", "3": "mansio"},
                    "expansion": "From mansio.",
                }
            ],
        )

    def test_etymology_boundaries_and_shared_parts_of_speech(self):
        entries = parse_page(
            self.wxr,
            "test",
            """==French==
===Etymology 1===
{{m|fr|aval}}
====Noun====
# first meaning
=====Derived terms=====
* [[avalable#French|avalable]]
====Verb====
# second meaning
===Etymology 2===
{{m|la|mansio}}
====Adjective====
# third meaning
===Etymology 3===
Unknown origin.
====Adverb====
# fourth meaning
""",
        )
        self.assertEqual(len(entries), 4)
        self.assertEqual(
            entries[0]["etymology_links"], [("aval", "aval#French")]
        )
        self.assertEqual(
            entries[1]["etymology_links"], [("aval", "aval#French")]
        )
        self.assertEqual(
            entries[2]["etymology_links"], [("mansio", "mansio#Latin")]
        )
        self.assertNotIn("etymology_links", entries[3])

    def test_no_links_omits_field(self):
        entry = self.parse("Unknown origin.")[0]
        self.assertEqual(entry["etymology_text"], "Unknown origin.")
        self.assertNotIn("etymology_links", entry)


if __name__ == "__main__":
    unittest.main()

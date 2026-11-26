"""Keep the output of {{etymon}} out of etymology text and expansions."""

import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext

# What Module:etymon returns, shortened from Italian "capitale" and English
# "dictionary": the attribute holds wikilinks, the tree nests divs.
ANCHOR = (
    '<ul class="etymonid" data-ety-tree-json="{ &quot;children&quot; : [ { '
    "&quot;keyword_label&quot; : "
    "&quot;[[Appendix:Glossary#derived_terms|Derived]] from&quot;, "
    "&quot;terms&quot; : [ { &quot;term&quot; : &quot;caput&quot; } ] } ] }"
    '" data-lang="it" data-title="capitale"></ul>'
    "[[Category:Pages with etymon|CAPITALE]]"
)
ANCHOR_WITHOUT_LINK = (
    '<ul class="etymonid" data-ety-tree-json="{ &quot;title&quot; : '
    '&quot;capitale&quot; }" data-lang="it" data-title="capitale"></ul>'
)
TREE = (
    '<templatestyles src="Module:etymon/styles.css" />'
    '<div class="etytree NavFrame" data-etytree-height="2">'
    '<div class="NavHead"><div>Etymology tree</div></div>'
    '<div class="NavContent"><div class="etytree-body">'
    '<div class="etytree-branch-group"><div class="etytree-branch">'
    '<div class="etytree-block"><span class="etyl">[[w:Latin|Latin]]</span> '
    '<span class="etytree-term">[[caput#Latin|caput]]</span></div>'
    '</div></div><div class="etytree-block">'
    '<span class="etyl">[[w:Italian|Italian]]</span> '
    '<span class="etytree-term">capitale</span>'
    "</div></div></div></div>"
)


class EnEtymologyTreeTests(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(capture_language_codes=None),
        )
        self.wxr.wtp.add_page("Template:m", 10, "[[{{{2}}}]]")
        self.wxr.wtp.add_page("Template:ety", 10, TREE + ANCHOR)
        self.wxr.wtp.add_page("Template:ety no tree", 10, ANCHOR)
        self.wxr.wtp.add_page("Template:ety no link", 10, ANCHOR_WITHOUT_LINK)
        self.wxr.wtp.add_page(
            "Template:ety text", 10, TREE + ANCHOR + "From [[caput]]."
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def parse(self, etymology):
        return parse_page(
            self.wxr,
            "capitale",
            "==Italian==\n===Etymology===\n"
            f"{etymology}\n===Noun===\n# [[capital]]\n",
        )[0]

    def test_attribute_does_not_leak_into_expansion(self):
        entry = self.parse("{{ety no tree}}\nFrom {{m|la|caput}}.")
        self.assertEqual(entry["etymology_text"], "From caput.")
        self.assertEqual(entry["etymology_templates"][0]["name"], "ety no tree")
        self.assertEqual(entry["etymology_templates"][0]["expansion"], "")

    def test_attribute_without_wikilink(self):
        # Already clean before: nothing in this attribute ends the tag early
        entry = self.parse("{{ety no link}}\nFrom {{m|la|caput}}.")
        self.assertEqual(entry["etymology_text"], "From caput.")
        self.assertEqual(entry["etymology_templates"][0]["expansion"], "")

    def test_tree_leaves_text_links_and_expansion(self):
        entry = self.parse("{{ety}}\nFrom {{m|la|caput}}.")
        self.assertEqual(entry["etymology_text"], "From caput.")
        self.assertEqual(entry["etymology_links"], [("caput", "caput")])
        self.assertEqual(entry["etymology_templates"][0]["expansion"], "")

    def test_tree_alone_leaves_no_text(self):
        entry = self.parse("{{ety}}")
        self.assertNotIn("etymology_text", entry)
        self.assertNotIn("etymology_links", entry)
        self.assertEqual(entry["etymology_templates"][0]["expansion"], "")

    def test_text_from_the_template_stays(self):
        entry = self.parse("{{ety text}}")
        self.assertEqual(entry["etymology_text"], "From caput.")
        self.assertEqual(entry["etymology_links"], [("caput", "caput")])
        self.assertEqual(
            entry["etymology_templates"][0]["expansion"], "From caput."
        )

    def test_text_between_two_trees_stays(self):
        entry = self.parse("{{ety}}\nFrom {{m|la|caput}}.\n{{ety}}\nOr not.")
        self.assertEqual(entry["etymology_text"], "From caput.\nOr not.")

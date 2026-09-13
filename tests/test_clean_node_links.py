import unittest

from pydantic import BaseModel
from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.page import clean_node
from wiktextract.wxr_context import WiktextractContext


class CategoryData(BaseModel):
    categories: list[str] = []
    tags: list[str] = []


class TestCleanNodeLinks(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"),
            WiktionaryConfig(dump_file_lang_code="fr"),
        )
        self.wxr.wtp.start_page("test")
        self.wxr.wtp.add_page(
            "Modèle:lien-test",
            10,
            "[[{{{1}}}#fr|{{{2}}}]][[Catégorie:Étymologie]]",
        )

    def tearDown(self):
        self.wxr.wtp.close_db_conn()

    def test_collect_without_category_destination(self):
        links = []
        text = clean_node(
            self.wxr,
            None,
            self.wxr.wtp.parse(
                "{{lien-test|aval|avál}} + [[-er#fr|-er]], [[aval#fr|avál]]"
            ),
            link_collector=links,
        )
        self.assertEqual(text, "avál + -er, avál")
        self.assertEqual(
            links, [("avál", "aval#fr"), ("-er", "-er#fr"), ("avál", "aval#fr")]
        )

    def test_category_only_model_keeps_existing_behavior(self):
        source = self.wxr.wtp.parse("{{lien-test|aval|aval}}")
        before, after = CategoryData(), CategoryData()
        expected_text = clean_node(self.wxr, before, source)
        links = []
        self.assertEqual(
            clean_node(self.wxr, after, source, link_collector=links),
            expected_text,
        )
        self.assertEqual(after, before)
        self.assertEqual(after.categories, ["Étymologie"])
        self.assertEqual(links, [("aval", "aval#fr")])

    def test_existing_sense_links_and_collector_agree(self):
        data, links = {}, []
        clean_node(
            self.wxr,
            data,
            self.wxr.wtp.parse("[[aval#fr|aval]][[Catégorie:Étymologie]]"),
            collect_links=True,
            link_collector=links,
        )
        self.assertEqual(data["links"], links)
        self.assertEqual(links, [("aval", "aval#fr")])
        self.assertEqual(data["categories"], ["Étymologie"])

    def test_append_and_anchor_option(self):
        links = [("first", "first#fr")]
        clean_node(
            self.wxr,
            None,
            self.wxr.wtp.parse("[[aval#fr|aval]]"),
            link_collector=links,
        )
        clean_node(
            self.wxr,
            None,
            self.wxr.wtp.parse("[[aval#fr|aval]]"),
            remove_anchors_from_links=True,
            link_collector=links,
        )
        self.assertEqual(
            links,
            [("first", "first#fr"), ("aval", "aval#fr"), ("aval", "aval")],
        )

    def test_suppressed_templates_do_not_supply_links(self):
        links = []
        text = clean_node(
            self.wxr,
            None,
            self.wxr.wtp.parse("{{lien-test|aval|aval}} plain"),
            template_fn=lambda name, args: "",
            link_collector=links,
        )
        self.assertEqual(text, "plain")
        self.assertEqual(links, [])

    def test_reference_links_are_excluded_even_with_matching_labels(self):
        links = []
        source = self.wxr.wtp.parse(
            '[[aval#fr|aval]]<ref name="note">[[other#fr|aval]]</ref>'
        )
        text = clean_node(self.wxr, None, source, link_collector=links)
        self.assertEqual(text, "aval")
        self.assertEqual(links, [("aval", "aval#fr")])

    def test_omitted_markup_cannot_supply_a_matching_destination(self):
        for markup in (
            '<div class="floatright">[[hidden|root]]</div>',
            '<div style="float:right">[[hidden|root]]</div>',
            '<sup class="previewonly">[[hidden|root]]</sup>',
            '<strong class="error">[[hidden|root]]</strong>',
            "\n{|\n| [[hidden|root]]\n|}",
            "\n{|\n| outer\n{|\n| [[hidden|root]]\n|}\n|}",
        ):
            with self.subTest(markup=markup):
                links = []
                # Templates produce these expanded wiki/HTML fragments.
                self.wxr.wtp.add_page("Modèle:omitted-test", 10, markup)
                text = clean_node(
                    self.wxr,
                    None,
                    self.wxr.wtp.parse("[[root]]{{omitted-test}}"),
                    link_collector=links,
                )
                self.assertEqual(text, "root")
                self.assertEqual(links, [("root", "root")])

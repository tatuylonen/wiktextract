"""Expanded etymology links follow the prose retained by each edition."""

import importlib
from unittest import TestCase

from wikitextprocessor import NodeKind, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext


class EuropeanEtymologyLinkTests(TestCase):
    maxDiff = None
    editions = ("de", "es", "it", "pt", "ru", "cs", "tr")

    def context(self, edition):
        wxr = WiktextractContext(
            Wtp(lang_code=edition),
            WiktionaryConfig(
                dump_file_lang_code=edition, capture_language_codes=None
            ),
        )
        self.addCleanup(wxr.wtp.close_db_conn)
        wxr.wtp.start_page("test")
        return wxr

    def entry(self, edition, lang="la"):
        module = importlib.import_module(
            f"wiktextract.extractor.{edition}.models"
        )
        return module.WordEntry(
            word="test", lang_code=lang, lang=lang, pos="noun"
        )

    def extract(self, edition, wxr, entry, text):
        module = importlib.import_module(
            f"wiktextract.extractor.{edition}.etymology"
        )
        node = next(
            wxr.wtp.parse("== Etymology ==\n" + text).find_child(
                NodeKind.LEVEL2
            )
        )
        fn = (
            module.extract_etymology
            if edition == "ru"
            else module.extract_etymology_section
        )
        fn(wxr, [entry] if edition in {"it", "pt"} else entry, node)

    def test_expanded_links_keep_anchors_order_and_category_behavior(self):
        for edition in self.editions:
            with self.subTest(edition=edition):
                wxr = self.context(edition)
                entry = self.entry(edition)
                template_ns = wxr.wtp.NAMESPACE_DATA["Template"]["name"]
                category_ns = wxr.wtp.NAMESPACE_DATA["Category"]["name"]
                wxr.wtp.add_page(
                    f"{template_ns}:origin-test",
                    10,
                    "[[mansio#Latin|mānsiōnem]]"
                    f"[[{category_ns}:Etymology test]]",
                )
                self.extract(
                    edition,
                    wxr,
                    entry,
                    "* [[root#Latin|rōt]] {{origin-test}} [[root#Latin|rōt]]\n",
                )
                self.assertEqual(entry.etymology_texts, ["rōt mānsiōnem rōt"])
                self.assertEqual(
                    entry.etymology_links,
                    [
                        ("rōt", "root#Latin"),
                        ("mānsiōnem", "mansio#Latin"),
                        ("rōt", "root#Latin"),
                    ],
                )
                # Italian and Czech list extraction deliberately cleaned with
                # sense_data=None before link collection was introduced.
                self.assertEqual(
                    entry.categories,
                    [] if edition in {"it", "cs"} else ["Etymology test"],
                )

    def test_inline_references_do_not_add_invisible_links(self):
        for edition in self.editions:
            with self.subTest(edition=edition):
                wxr = self.context(edition)
                entry = self.entry(edition)
                self.extract(
                    edition,
                    wxr,
                    entry,
                    "* [[root]]<ref>[[citation-only]]</ref>\n",
                )
                self.assertEqual(entry.etymology_texts, ["root"])
                self.assertEqual(entry.etymology_links, [("root", "root")])

    def test_child_sections_are_not_etymology_prose(self):
        for edition in self.editions:
            with self.subTest(edition=edition):
                wxr = self.context(edition)
                entry = self.entry(edition)
                self.extract(
                    edition,
                    wxr,
                    entry,
                    "* [[origin]]\n=== References ===\n* [[reference-only]]",
                )
                self.assertEqual(entry.etymology_texts, ["origin"])
                self.assertEqual(entry.etymology_links, [("origin", "origin")])

    def test_plain_text_omits_default_links_and_models_are_independent(self):
        for edition in self.editions:
            with self.subTest(edition=edition):
                wxr = self.context(edition)
                first = self.entry(edition)
                second = self.entry(edition)
                self.extract(edition, wxr, first, "* [[first]]\n")
                self.extract(edition, wxr, second, "* No known origin.\n")
                self.assertEqual(first.etymology_links, [("first", "first")])
                self.assertNotIn(
                    "etymology_links", second.model_dump(exclude_defaults=True)
                )

    def test_paragraph_fallbacks_collect_links(self):
        # German etymologies are list based; all other assigned editions also
        # retain prose without a list.
        for edition in self.editions[1:]:
            with self.subTest(edition=edition):
                wxr = self.context(edition)
                entry = self.entry(edition)
                self.extract(edition, wxr, entry, "From [[root#Latin|rōt]].\n")
                self.assertEqual(entry.etymology_texts, ["From rōt."])
                self.assertEqual(entry.etymology_links, [("rōt", "root#Latin")])

    def test_rejected_spanish_placeholder_does_not_leave_links(self):
        wxr = self.context("es")
        for text in (
            "Si puedes, incorpórala: [[ver cómo]]",
            "* Si puedes, incorpórala: [[ver cómo]]",
        ):
            with self.subTest(text=text):
                entry = self.entry("es")
                self.extract("es", wxr, entry, text)
                self.assertEqual(entry.etymology_texts, [])
                self.assertNotIn(
                    "etymology_links", entry.model_dump(exclude_defaults=True)
                )

    def test_italian_citations_are_separate_from_etymology_links(self):
        from wiktextract.extractor.it.etymology import extract_citation_section

        wxr = self.context("it")
        entry = self.entry("it")
        self.extract(
            "it",
            wxr,
            entry,
            "From [[origin]].\n=== Citazione ===\n"
            "{{Quote|[[example-only]]|[[reference-only]]}}",
        )
        citation = next(
            wxr.wtp.parse(
                "== Citazione ==\n{{Quote|[[example-only]]|[[reference-only]]}}"
            ).find_child(NodeKind.LEVEL2)
        )
        extract_citation_section(wxr, [entry], citation)
        self.assertEqual(entry.etymology_links, [("origin", "origin")])
        self.assertEqual(entry.etymology_examples[0].text, "example-only")
        self.assertEqual(entry.etymology_examples[0].ref, "reference-only")

    def test_portuguese_attestation_and_russian_panel_do_not_add_links(self):
        for edition, name in (("pt", "datação"), ("ru", "improve")):
            with self.subTest(edition=edition):
                wxr = self.context(edition)
                entry = self.entry(edition)
                namespace = wxr.wtp.NAMESPACE_DATA["Template"]["name"]
                wxr.wtp.add_page(f"{namespace}:{name}", 10, "[[excluded-only]]")
                self.extract(edition, wxr, entry, "[[origin]] {{" + name + "}}")
                self.assertEqual(entry.etymology_links, [("origin", "origin")])
                self.assertEqual(entry.etymology_texts, ["origin"])

    def test_shared_italian_and_portuguese_entries_copy_matching_links(self):
        for edition in ("it", "pt"):
            with self.subTest(edition=edition):
                wxr = self.context(edition)
                other_language = self.entry(edition, "fr")
                first = self.entry(edition)
                second = self.entry(edition)
                node = next(
                    wxr.wtp.parse("== Etymology ==\n* [[root]]").find_child(
                        NodeKind.LEVEL2
                    )
                )
                module = importlib.import_module(
                    f"wiktextract.extractor.{edition}.etymology"
                )
                module.extract_etymology_section(
                    wxr, [other_language, first, second], node
                )
                self.assertEqual(other_language.etymology_links, [])
                self.assertEqual(first.etymology_links, [("root", "root")])
                self.assertEqual(second.etymology_links, [("root", "root")])
                first.etymology_links.append(("extra", "extra"))
                self.assertEqual(second.etymology_links, [("root", "root")])

import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.gloss import extract_glosses
from wiktextract.extractor.de.page import parse_page
from wiktextract.extractor.es.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestDEGloss(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_nested_gloss(self):
        self.wxr.wtp.start_page("Keim")
        self.wxr.wtp.add_page("Vorlage:K", 10, "{{{1|}}}, {{{2|}}}:")
        root = self.wxr.wtp.parse(
            """===Bedeutungen===
:[2] das erste [[Entwicklungsstadium]]
::[a] {{K|Botanik}} erster [[Trieb]] einer Pflanze
::[b] {{K|Biologie|Medizin}} befruchtete [[Eizelle]], [[Embryo]]"""
        )
        word_entry = WordEntry(
            lang="Deutsch", lang_code="de", word="Keim", pos="noun"
        )
        extract_glosses(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in word_entry.senses],
            [
                {
                    "glosses": ["das erste Entwicklungsstadium"],
                    "sense_index": "2",
                },
                {
                    "glosses": [
                        "das erste Entwicklungsstadium",
                        "erster Trieb einer Pflanze",
                    ],
                    "topics": ["botany"],
                    "sense_index": "2a",
                },
                {
                    "glosses": [
                        "das erste Entwicklungsstadium",
                        "befruchtete Eizelle, Embryo",
                    ],
                    "topics": ["biology", "medicine"],
                    "sense_index": "2b",
                },
            ],
        )

    def test_nested_gloss_without_parent_gloss(self):
        self.wxr.wtp.add_page("Vorlage:K", 10, "{{{1}}}:")
        self.wxr.wtp.start_page("eingeben")
        root = self.wxr.wtp.parse(
            """===Bedeutungen===
*{{K|fachsprachlich}}
:[4] {{K|Technik}} etwas, was eine Maschine bearbeiten soll, an diese übergeben
:[5] {{K|EDV}} etwas in einen Computer übertragen"""
        )
        word_entry = WordEntry(
            lang="Deutsch", lang_code="de", word="eingeben", pos="verb"
        )
        extract_glosses(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in word_entry.senses],
            [
                {
                    "tags": ["jargon"],
                    "topics": ["technology"],
                    "glosses": [
                        "etwas, was eine Maschine bearbeiten soll, "
                        "an diese übergeben"
                    ],
                    "sense_index": "4",
                },
                {
                    "tags": ["jargon"],
                    "raw_tags": ["EDV"],
                    "glosses": ["etwas in einen Computer übertragen"],
                    "sense_index": "5",
                },
            ],
        )

    def test_k_template_ft_arg(self):
        self.wxr.wtp.add_page(
            "Vorlage:K",
            10,
            "<i>[[juristisch]],&#32;nur in der Wendung "
            "„auf etwas erkennen“&#58;</i>",
        )
        self.wxr.wtp.start_page("erkennen")
        root = self.wxr.wtp.parse(
            """===Bedeutungen===
:[5] {{K|juristisch|ft=nur in der Wendung „auf etwas erkennen“}} im Rahmen eines Urteils ein benanntes Verbrechen bestätigen"""  # noqa: E501
        )
        word_entry = WordEntry(
            lang="Deutsch", lang_code="de", word="erkennen", pos="verb"
        )
        extract_glosses(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in word_entry.senses],
            [
                {
                    "tags": ["law"],
                    "glosses": [
                        "nur in der Wendung „auf etwas erkennen“: im Rahmen "
                        "eines Urteils ein benanntes Verbrechen bestätigen"
                    ],
                    "sense_index": "5",
                },
            ],
        )

    def test_k_template_multiple_tags(self):
        self.wxr.wtp.add_page(
            "Vorlage:K",
            10,
            """<i>[[transitiv]]&#59;&#32;besonders&#32;[[bayrisch]],&#32;[[W:Österreichisches Deutsch|österreichisch]]&#58;</i>[[Kategorie:Verb transitiv&#32;(Deutsch)]][[Kategorie:Österreichisches Deutsch]]""",  # noqa: E501
        )
        self.wxr.wtp.start_page("almen")
        root = self.wxr.wtp.parse(
            """===Bedeutungen===
:[1] {{K|trans.|t1=;|besonders|t2=_|bayrisch|österr.}} [[Vieh]] auf der Alm halten"""  # noqa: E501
        )
        word_entry = WordEntry(
            lang="Deutsch", lang_code="de", word="almen", pos="verb"
        )
        extract_glosses(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in word_entry.senses],
            [
                {
                    "categories": [
                        "Verb transitiv (Deutsch)",
                        "Österreichisches Deutsch",
                    ],
                    "tags": ["transitive", "Austrian German"],
                    "raw_tags": ["besonders", "bayrisch"],
                    "glosses": ["Vieh auf der Alm halten"],
                    "sense_index": "1",
                },
            ],
        )

    def test_italic_sense_modifier(self):
        # https://de.wiktionary.org/wiki/habitare
        wikitext = """
* {{trans.}}
:[1] etwas [[oft]] [[haben]], zu haben [[pflegen]]
:[2] ''Stadt/Dorf:''
::[2.1] ''aktiv:'' [[bewohnen]], [[wohnen]]
::[2.2] ''passiv:'' bewohnt werden, zum [[Wohnsitz]] dienen
* {{intrans.}}
:[3] ''sich befinden:'' [[wohnen]]
:[4] ''übertragen:'' sich [[aufhalten]], [[heimisch]] sein, zu Hause sein
"""
        self.wxr.wtp.start_page("habitare")
        self.wxr.wtp.add_page("Vorlage:trans.", 10, "transitiv")
        self.wxr.wtp.add_page("Vorlage:intrans.", 10, "intransitiv")
        root = self.wxr.wtp.parse(wikitext)
        word_entry = WordEntry(
            lang="Latein", lang_code="la", word="habitare", pos="verb"
        )
        extract_glosses(self.wxr, word_entry, root)
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in word_entry.senses],
            [
                {
                    "tags": ["transitive"],
                    "glosses": ["etwas oft haben, zu haben pflegen"],
                    "sense_index": "1",
                },
                {
                    "tags": ["transitive"],
                    "raw_tags": ["Stadt/Dorf", "aktiv"],
                    "glosses": ["bewohnen, wohnen"],
                    "sense_index": "2.1",
                },
                {
                    "tags": ["transitive"],
                    "raw_tags": ["Stadt/Dorf", "passiv"],
                    "glosses": ["bewohnt werden, zum Wohnsitz dienen"],
                    "sense_index": "2.2",
                },
                {
                    "tags": ["intransitive"],
                    "raw_tags": ["sich befinden"],
                    "glosses": ["wohnen"],
                    "sense_index": "3",
                },
                {
                    "tags": ["intransitive", "figurative"],
                    "glosses": ["sich aufhalten, heimisch sein, zu Hause sein"],
                    "sense_index": "4",
                },
            ],
        )

    def test_italit_node_multiple_raw_tags(self):
        self.wxr.wtp.add_page(
            "Vorlage:K", 10, "<i>[[Deutschland]],&#32;[[Fernsehen]]&#58;</i>"
        )
        self.wxr.wtp.add_page("Vorlage:ugs.", 10, "''[[umgangssprachlich]]''")
        self.wxr.wtp.start_page("ARD")
        root = self.wxr.wtp.parse(
            """===Bedeutungen===
:[2] {{K|Deutschland|Fernsehen}} {{ugs.}}, ''[[Kurzwort]], [[Akronym]]:'' für das erste Fernsehprogramm der ARD"""  # noqa: E501
        )
        word_entry = WordEntry(
            lang="Deutsch", lang_code="de", word="ARD", pos="noun"
        )
        extract_glosses(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            [s.model_dump(exclude_defaults=True) for s in word_entry.senses],
            [
                {
                    "raw_tags": [
                        "Deutschland",
                        "Fernsehen",
                        "Kurzwort",
                        "Akronym",
                    ],
                    "glosses": ["für das erste Fernsehprogramm der ARD"],
                    "sense_index": "2",
                    "tags": ["colloquial"],
                },
            ],
        )

    def test_form_of(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "{{{1}}}")
        self.assertEqual(
            parse_page(
                self.wxr,
                "konjugierte",
                """== konjugierte ({{Sprache|Deutsch}}) ==
=== {{Wortart|Deklinierte Form|Deutsch}} ===
====Grammatische Merkmale====
*Nominativ Singular Femininum der starken Flexion des Positivs des Adjektivs '''[[konjugiert]]'''
*Akkusativ Singular Femininum der starken Flexion des Positivs des Adjektivs '''[[konjugiert]]'''""",  # noqa: E501
            ),
            [
                {
                    "lang": "Deutsch",
                    "lang_code": "de",
                    "pos": "adj",
                    "senses": [
                        {
                            "form_of": [{"word": "konjugiert"}],
                            "glosses": [
                                "Nominativ Singular Femininum der starken "
                                "Flexion des Positivs des Adjektivs konjugiert"
                            ],
                            "tags": ["nominative", "singular", "feminine"],
                        },
                        {
                            "form_of": [{"word": "konjugiert"}],
                            "glosses": [
                                "Akkusativ Singular Femininum der starken "
                                "Flexion des Positivs des Adjektivs konjugiert"
                            ],
                            "tags": ["accusative", "singular", "feminine"],
                        },
                    ],
                    "tags": ["form-of"],
                    "word": "konjugierte",
                }
            ],
        )

    def test_no_bedeutungen_section(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Vorlage:Ü", 10, "{{{2}}}")
        self.assertEqual(
            parse_page(
                self.wxr,
                "abakai",
                """== abakai ({{Sprache|Litauisch}}) ==
=== {{Wortart|Deklinierte Form|Litauisch}} ===
* Nominativ Plural von {{Ü|lt|abakas}}""",
            ),
            [
                {
                    "lang": "Litauisch",
                    "lang_code": "lt",
                    "pos": "unknown",
                    "senses": [
                        {
                            "form_of": [{"word": "abakas"}],
                            "glosses": ["Nominativ Plural von abakas"],
                            "tags": ["nominative", "plural"],
                        }
                    ],
                    "tags": ["form-of"],
                    "word": "abakai",
                }
            ],
        )

    def test_grammatische_merkmale_no_form_of_pos_title(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "{{{1}}}")
        self.assertEqual(
            parse_page(
                self.wxr,
                "abisse",
                """== abisse ({{Sprache|Latein}}) ==
=== {{Wortart|Infinitiv|Latein}} ===

==== Grammatische Merkmale ====
* Infinitiv Perfekt Aktiv des Verbs '''[[abire]]'''""",
            ),
            [
                {
                    "lang": "Latein",
                    "lang_code": "la",
                    "pos": "verb",
                    "senses": [
                        {
                            "form_of": [{"word": "abire"}],
                            "glosses": [
                                "Infinitiv Perfekt Aktiv des Verbs abire"
                            ],
                            "tags": ["perfect", "active"],
                        }
                    ],
                    "tags": ["form-of"],
                    "word": "abisse",
                }
            ],
        )

    def test_no_gloss_list(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "{{{1}}}")
        self.assertEqual(
            parse_page(
                self.wxr,
                "ama",
                """== ama ({{Sprache|Interlingua}}) ==
=== {{Wortart|Konjugierte Form|Interlingua}} ===

==== Grammatische Merkmale ====
Indikativ Präsens Aktiv des Verbs '''[[amar]]'''""",
            ),
            [
                {
                    "lang": "Interlingua",
                    "lang_code": "ia",
                    "pos": "unknown",
                    "senses": [
                        {"glosses": ["Indikativ Präsens Aktiv des Verbs amar"]}
                    ],
                    "tags": ["form-of"],
                    "word": "ama",
                }
            ],
        )

    def test_unordered_list(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "{{{1}}}")
        self.assertEqual(
            parse_page(
                self.wxr,
                "assa",
                """== assa ({{Sprache|Prußisch}}) ==
=== {{Wortart|Präposition |Prußisch}} ===

==== Bedeutungen ====
* Nebenform der Präposition '''[[esse]]'''""",
            ),
            [
                {
                    "lang": "Prußisch",
                    "lang_code": "prg",
                    "pos": "prep",
                    "senses": [{"glosses": ["Nebenform der Präposition esse"]}],
                    "word": "assa",
                }
            ],
        )

    def test_description_list_plus_unordered_list(self):
        self.wxr.wtp.add_page("Vorlage:Sprache", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Vorlage:Wortart", 10, "{{{1}}}")
        self.assertEqual(
            parse_page(
                self.wxr,
                "aut",
                """== aut ({{Sprache|Polnisch}}) ==
=== {{Wortart|Deklinierte Form|Polnisch}} ===
====Grammatische Merkmale====
:* Genitiv Plural des Substantivs '''[[auto#auto (Polnisch)|auto]]'''""",
            ),
            [
                {
                    "lang": "Polnisch",
                    "lang_code": "pl",
                    "pos": "noun",
                    "senses": [
                        {
                            "form_of": [{"word": "auto"}],
                            "glosses": ["Genitiv Plural des Substantivs auto"],
                            "tags": ["genitive", "plural"],
                        }
                    ],
                    "tags": ["form-of"],
                    "word": "aut",
                }
            ],
        )

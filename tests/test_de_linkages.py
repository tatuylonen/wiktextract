import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.linkage import extract_linkages
from wiktextract.extractor.de.models import Sense, WordEntry
from wiktextract.extractor.de.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestDELinkages(unittest.TestCase):
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

    def test_simple_link(self):
        # Extracts linkages and places them in the correct sense.
        self.wxr.wtp.start_page("Beispiel")
        root = self.wxr.wtp.parse("""==== Sinnverwandte Wörter ====
:[1] [[Beleg]], [[Exempel]]
:[2] [[Muster]], [[Vorbild]]""")
        word_entry = WordEntry(
            word="Beispiel",
            lang_code="de",
            lang="Deutsch",
            senses=[Sense(sense_index="1")],
        )
        extract_linkages(
            self.wxr, word_entry, root.children[0], "coordinate_terms"
        )
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in word_entry.coordinate_terms
            ],
            [
                {"word": "Beleg", "sense_index": "1"},
                {"word": "Exempel", "sense_index": "1"},
                {"word": "Muster", "sense_index": "2"},
                {"word": "Vorbild", "sense_index": "2"},
            ],
        )

    def test_explanatory_text_in_expressions(self):
        self.wxr.wtp.start_page("Beispiel")
        root = self.wxr.wtp.parse("""====Redewendungen====
:[[ein gutes Beispiel geben|ein gutes ''Beispiel'' geben]] – als [[Vorbild]] zur [[Nachahmung]] [[dienen]]/[[herausfordern]]""")
        word_entry = WordEntry(word="Beispiel", lang_code="de", lang="Deutsch")
        extract_linkages(self.wxr, word_entry, root.children[0], "expressions")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in word_entry.expressions
            ],
            [
                {
                    "note": "als Vorbild zur Nachahmung dienen/herausfordern",
                    "word": "ein gutes Beispiel geben",
                }
            ],
        )

    def test_italic_tag(self):
        self.wxr.wtp.start_page("Kokospalme")
        root = self.wxr.wtp.parse("""====Synonyme====
:[1] [[Kokosnusspalme]], ''wissenschaftlich:'' [[Cocos nucifera]]""")
        word_entry = WordEntry(
            word="Kokospalme",
            lang_code="de",
            lang="Deutsch",
            senses=[Sense(sense_index="1")],
        )
        extract_linkages(self.wxr, word_entry, root.children[0], "synonyms")
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in word_entry.synonyms],
            [
                {"word": "Kokosnusspalme", "sense_index": "1"},
                {
                    "word": "Cocos nucifera",
                    "sense_index": "1",
                    "raw_tags": ["wissenschaftlich"],
                },
            ],
        )

    def test_tag_template(self):
        self.wxr.wtp.start_page("Feber")
        self.wxr.wtp.add_page("Vorlage:va.", 10, "[[veraltet|''veraltet,'']]")
        self.wxr.wtp.add_page(
            "Vorlage:landsch.",
            10,
            "[[landschaftlich|''landschaftlich<nowiki>:</nowiki>'']]",
        )
        root = self.wxr.wtp.parse(
            ":[1] {{va.|,}} ''sonst noch'' {{landsch.|:}} [[Hornung]]"
        )
        word_entry = WordEntry(
            word="Feber",
            lang_code="de",
            lang="Deutsch",
            senses=[Sense(sense_index="1")],
        )
        extract_linkages(self.wxr, word_entry, root.children[0], "synonyms")
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in word_entry.synonyms],
            [
                {
                    "word": "Hornung",
                    "sense_index": "1",
                    "tags": ["archaic", "regional"],
                },
            ],
        )

    def test_link_in_italic_node(self):
        self.wxr.wtp.start_page("Abendland")
        root = self.wxr.wtp.parse("""====Redewendungen====
:[1] ''[[Morgenland und Abendland]]'' -""")
        word_entry = WordEntry(
            word="Abendland",
            lang_code="de",
            lang="Deutsch",
            senses=[Sense(sense_index="1")],
        )
        extract_linkages(self.wxr, word_entry, root.children[0], "expressions")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in word_entry.expressions
            ],
            [
                {"word": "Morgenland und Abendland", "sense_index": "1"},
            ],
        )

    def test_descendant(self):
        page_data = parse_page(
            self.wxr,
            "ordo",
            """== ōrdo ({{Sprache|Latein}}) ==
=== {{Wortart|Substantiv|Latein}}, {{m}} ===
====Bedeutungen====
:[1] ''gegenständlich:''
====Entlehnungen====
:[5b] ''deutsch:'' [[Ordination]]""",
        )
        self.assertEqual(
            page_data[0]["descendants"],
            [
                {
                    "lang": "deutsch",
                    "lang_code": "de",
                    "sense_index": "5b",
                    "word": "Ordination",
                }
            ],
        )

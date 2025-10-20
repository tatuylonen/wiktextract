from unittest import TestCase

from wikitextprocessor import WikiNode, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.linkages import process_linkage_section
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.parse_utils import Heading
from wiktextract.wxr_context import WiktextractContext


class TestElLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="el"),
            WiktionaryConfig(
                dump_file_lang_code="el", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def parse_related(self, word: str, text: str, type=Heading.Related) -> dict:
        data = WordEntry(word=word)
        self.wxr.wtp.start_page(word)
        parsed = self.wxr.wtp.parse(text)
        related_section = parsed.children[0]
        assert isinstance(related_section, WikiNode)
        process_linkage_section(self.wxr, data, related_section, type)

        return data.model_dump(exclude_defaults=True)

    def test_related1(self) -> None:
        data = self.parse_related(
            "κόκκινο",
            """==== <span style="cursor:help;" title="Λέξεις της ίδιας γλώσσας με ετυμολογική συγγένεια">Συγγενικά</span> ====

* [[κόκκινος]]
""",
        )
        self.assertEqual(
            data["related"],
            [
                {"word": "κόκκινος"},
            ],
        )

    def test_related1b(self) -> None:
        data = self.parse_related(
            "κόκκινο",
            """==== <span style="cursor:help;" title="Λέξεις της ίδιας γλώσσας με ετυμολογική συγγένεια">Συγγενικά</span> ====

* {{βλ|κόκκινος}}
""",
        )
        self.assertEqual(
            data["related"],
            [
                {"word": "κόκκινος"},
            ],
        )

    def test_related1c(self) -> None:
        data = self.parse_related(
            "κόκκινο",
            """==== <span style="cursor:help;" title="Λέξεις της ίδιας γλώσσας με ετυμολογική συγγένεια">Συγγενικά</span> ====

* {{βλ|κόκκινος|foo|bar}}
""",
        )
        self.assertEqual(
            data["related"],
            [
                {"word": "κόκκινος"},
                {"word": "foo"},
                {"word": "bar"},
            ],
        )

    def test_related2(self) -> None:
        data = self.parse_related(
            "papillon",
            """==== <span style="cursor:help;" title="Εκφράσεις που περιέχουν τη λέξη «κόκκινο»">Εκφράσεις</span> ====

* [[ντυμένος]] [[στα κόκκινα]]
""",
        )
        self.assertEqual(
            data["related"],
            [
                {"word": "ντυμένος στα κόκκινα"},
            ],
        )

    def test_transliterations(self) -> None:
        data = self.parse_related(
            "foo",
            """===={{μεταγραφές}}====
* ''αραβικό αλφάβητο'': [[arabfoo]]
* ''λατινικό αλφάβητο [[Yañalif]]'': [[yanalatinfoo]]
* ''λατινικό αλφάβητο'': [[latinfoo]]
""",
            type=Heading.Transliterations,
        )
        # print(f"{data=}")
        self.assertEqual(
            data["forms"],
            [
                {
                    "form": "arabfoo",
                    "tags": ["transliteration", "Arabic"],
                    "raw_tags": ["αραβικό αλφάβητο"],
                    "source": "linkage",
                },
                {
                    "form": "yanalatinfoo",
                    "tags": ["transliteration", "Latin", "Yañalif"],
                    "raw_tags": ["λατινικό αλφάβητο", "Yañalif"],
                    "source": "linkage",
                },
                {
                    "form": "latinfoo",
                    "tags": ["transliteration", "Latin"],
                    "raw_tags": ["λατινικό αλφάβητο"],
                    "source": "linkage",
                },
            ],
        )

    def test_transliterations_esperanto(self) -> None:
        data = self.parse_related(
            "foo",
            """===={{άλλη γραφή}}====
* {{eo-h|acidajho}}
* {{eo-x|acidajxo}}
""",
            type=Heading.Transliterations,
        )
        # print(f"{data=}")
        self.assertEqual(
            data["forms"],
            [
                {
                    "form": "acidajho",
                    "tags": ["transliteration"],
                    "raw_tags": ["H-sistemo"],
                    "source": "linkage",
                },
                {
                    "form": "acidajxo",
                    "tags": ["transliteration"],
                    "raw_tags": ["X-sistemo"],
                    "source": "linkage",
                },
            ],
        )

    def test_related_examples1(self) -> None:
        data = self.parse_related(
            "papillon",
            """==== <span style="cursor:help;" title="Εκφράσεις που περιέχουν τη λέξη «κόκκινο»">Εκφράσεις</span> ====

* [[ντυμένος]]
*: Foo
* [[στα κόκκινα]]
*: Baz
""",
        )
        self.assertEqual(
            data["related"],
            [
                {
                    "word": "ντυμένος",
                    "examples": ["Foo"],
                },
                {
                    "word": "στα κόκκινα",
                    "examples": ["Baz"],
                },
            ],
        )

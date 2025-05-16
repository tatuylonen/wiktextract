from typing import Any
from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.pos import process_pos
from wiktextract.wxr_context import WiktextractContext


def raw_trim(raw: str) -> str:
    return "\n".join(line.strip() for line in raw.strip().split("\n"))


class TestElGlosses(TestCase):
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

    def mktest_sense(self, raw: str, expected: list[dict[str, Any]]) -> None:
        """Compare only senses["tags"] and senses["form_of"].

        Do not compare senses["glosses"] but check that it exists. This
        way we don't need to expand templates, and we still (roughly) check
        that we didn't delete any glosses in the process.
        """
        self.wxr.wtp.start_page("start_filler")
        data = WordEntry(lang="Greek", lang_code="el", word="word_filler")
        # * Prefixing the header allows us to not have it everywhere in the tests.
        # * Adding the head just silences a warning.
        raw = "==={{ουσιαστικό|el}}===\n'''head'''\n" + raw_trim(raw)
        root = self.wxr.wtp.parse(raw)
        pos_node = root.children[0]
        process_pos(self.wxr, pos_node, data, None, "", "", pos_tags=[])  # type: ignore
        dumped = data.model_dump(exclude_defaults=True)

        # Check for the "glosses" key and remove it for comparison
        received = dumped["senses"]
        for sense in received:
            self.assertIsInstance(sense, dict)
            self.assertIn("glosses", sense)
            sense.pop("glosses")

        # print(f"{received=}")
        # print(f"{expected=}")
        self.assertEqual(received, expected)

    def test_inflection_noun1(self) -> None:
        # https://el.wiktionary.org/wiki/κόρφο
        raw = """* {{πτώσηΑεν|κόρφος}}"""
        expected = [
            {
                "form_of": [{"word": "κόρφος"}],
                "tags": ["accusative", "singular"],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_inflection_noun2(self) -> None:
        # https://el.wiktionary.org/wiki/κόρφο
        raw = """* {{πτώσηΑεν|κόρφος|el}}"""
        expected = [
            {
                "form_of": [{"word": "κόρφος"}],
                "tags": ["accusative", "singular"],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_inflection_noun_multiple(self) -> None:
        # https://el.wiktionary.org/wiki/κόρφο
        raw = """* {{πτώσειςΟΚπλ|κόρφος}}"""
        expected = [
            {
                "tags": ["nominative", "plural", "vocative"],
                "form_of": [{"word": "κόρφος"}],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_inflection_adj(self) -> None:
        # https://el.wiktionary.org/wiki/μικρή
        raw = """* {{θηλ_του-πτώσειςΟΑΚεν|μικρός}}"""
        expected = [
            {
                "tags": [
                    "accusative",
                    "feminine",
                    "nominative",
                    "singular",
                    "vocative",
                ],
                "form_of": [{"word": "μικρός"}],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_inflection_adj_multiple(self) -> None:
        # https://el.wiktionary.org/wiki/θαυμάσιο
        raw = """
            # {{πτώσηΑεν|θαυμάσιος}}
            # {{ουδ του-πτώσειςΟΑΚεν|θαυμάσιος}}
        """
        expected = [
            {
                "tags": ["accusative", "singular"],
                "form_of": [{"word": "θαυμάσιος"}],
            },
            {
                "tags": [
                    "accusative",
                    "neuter",
                    "nominative",
                    "singular",
                    "vocative",
                ],
                "form_of": [{"word": "θαυμάσιος"}],
            },
        ]
        self.mktest_sense(raw, expected)

    def test_form_of_verb_template1(self) -> None:
        # https://el.wiktionary.org/wiki/ξεκίνησα
        raw = """* {{ρημ τύπος|α' ενικό [[οριστική]]ς αορίστου|ξεκινώ}}"""
        expected = [{"form_of": [{"word": "ξεκινώ"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_verb_template1_with_noise1(self) -> None:
        # https://el.wiktionary.org/wiki/συμβουλέψω
        raw = """# (''ναα, νααα'') {{ρημ τύπος|α' ενικό [[Παράρτημα:Ρηματικοί τύποι (ελληνικά)#Υποτακτική|υποτακτικής]] αορίστου|συμβουλεύω}}"""
        expected = [
            {
                "raw_tags": ["ναα", "νααα"],  # does greek have native 'foo bar'?
                "form_of": [{"word": "συμβουλεύω"}],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_form_of_verb_template1_with_noise2(self) -> None:
        # https://el.wiktionary.org/wiki/συμβουλέψω
        raw = """# '''θα συμβουλέψω''': {{ρημ τύπος|α' ενικό οριστικής στιγμιαίου μέλλοντα|συμβουλεύω}}"""
        expected = [{"form_of": [{"word": "συμβουλεύω"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_generic_template_noun(self) -> None:
        # https://el.wiktionary.org/wiki/εδάφη
        raw = "* {{κλ||έδαφος|π=οακ|α=π}}"
        expected = [{"form_of": [{"word": "έδαφος"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_generic_template_verb(self) -> None:
        # https://el.wiktionary.org/wiki/πλανεύτηκα
        raw = "* {{κλ||πλανεύω|π=1ε|ε=ορ|χ=αορ|φ=π|φ+=πλανεύομαι}}"
        expected = [{"form_of": [{"word": "πλανεύω"}]}]
        self.mktest_sense(raw, expected)

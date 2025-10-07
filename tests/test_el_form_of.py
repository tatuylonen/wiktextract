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
                "raw_tags": [
                    "ναα",
                    "νααα",
                ],  # does greek have native 'foo bar'?
                "form_of": [{"word": "συμβουλεύω"}],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_form_of_verb_template1_with_noise2(self) -> None:
        # https://el.wiktionary.org/wiki/συμβουλέψω
        raw = """# '''θα συμβουλέψω''': {{ρημ τύπος|α' ενικό οριστικής στιγμιαίου μέλλοντα|συμβουλεύω}}"""
        expected = [{"form_of": [{"word": "συμβουλεύω"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_verb_participle1(self) -> None:
        # https://el.wiktionary.org/wiki/καταρτισμένος
        raw = """* {{μτχππ|καταρτίζω}}"""
        expected = [{"form_of": [{"word": "καταρτίζω"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_verb_participle2(self) -> None:
        # https://el.wiktionary.org/wiki/διαδεχθείς
        raw = """* {{μτχα|διαδέχομαι|παθ=1|χ+=διαδέχθηκα|00=-}}"""
        expected = [{"form_of": [{"word": "διαδέχομαι"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_empty_args1(self) -> None:
        # This should return nothing: no argument, no text after
        # NOTE for this test the name of the template is for debugging
        raw = """* {{μτχ3a}}"""
        expected: list[dict] = [{}]
        self.mktest_sense(raw, expected)

    def test_form_of_empty_args2(self) -> None:
        # This should return nothing: no argument, no text after
        # NOTE for this test the name of the template is for debugging
        raw = """* {{μτχ3b}} [[test]]"""
        expected = [{"form_of": [{"word": "test"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_empty_args3(self) -> None:
        # This should return nothing: no argument, no text after
        # NOTE for this test the name of the template is for debugging
        raw = """* {{μτχ3b}} [[test]] [[foo]]"""
        expected = [{"form_of": [{"word": "test foo"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_empty_args4(self) -> None:
        # This should return nothing: no argument, no text after
        # NOTE for this test the name of the template is for debugging
        raw = """* {{μτχ3b}} [[test]] [[foo]], [[bar]]"""
        expected = [{"form_of": [{"word": "test foo"}]}]
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

    def test_form_of_gr_base(self) -> None:
        # https://el.wiktionary.org/wiki/εσένανε
        raw = "* {{γρ|εσένα|μορφή}}"
        expected = [{"form_of": [{"word": "εσένα"}]}]
        self.mktest_sense(raw, expected)

    def test_form_of_gr_second_arg_wrong(self) -> None:
        # https://el.wiktionary.org/wiki/πιάνο_τοίχου
        # Should ignore expansion depending on the second argument
        raw = "* {{γρ|όρθιο πιάνο|συνων}}"
        expected = [{}]
        self.mktest_sense(raw, expected)

    def test_gr_linkage_second_arg_variant(self) -> None:
        # https://el.wiktionary.org/wiki/μαλακή_υπερώα
        raw = "* {{γρ|μαλθακή υπερώα|μορφ}}· ο μαλακός [[ιστός]]..."
        expected = [{"form_of": [{"word": "μαλθακή υπερώα"}]}]
        self.mktest_sense(raw, expected)

    def test_gr_linkage_second_arg_empty(self) -> None:
        # Seen via ripgrep
        raw = "* {{γρ|well-rounded||en}}"
        expected = [{}]
        self.mktest_sense(raw, expected)

    def test_gr_linkage_one_arg(self) -> None:
        # Seen via ripgrep
        raw = "* {{γρ|τάδε}}"
        expected = [{}]
        self.mktest_sense(raw, expected)

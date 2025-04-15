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
        for sense in dumped["senses"]:
            self.assertIsInstance(sense, dict)
            self.assertIn("glosses", sense)
            sense.pop("glosses")

            # The order of tags may change between runs
            # FIXME: this should not be the case?
            sense["raw_tags"].sort()

        received = dumped["senses"]
        # print(f"{received=}")
        # print(f"{expected=}")
        self.assertEqual(received, expected)

    def test_inflection_noun(self) -> None:
        # https://el.wiktionary.org/wiki/κόρφο
        raw = """* {{πτώσηΑεν|κόρφος}}"""
        expected = [
            {
                "raw_tags": ["αιτιατική", "ενικού"],
                "form_of": [{"word": "κόρφος"}],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_inflection_noun_multiple(self) -> None:
        # https://el.wiktionary.org/wiki/κόρφο
        raw = """* {{πτώσειςΟΚπλ|κόρφος}}"""
        expected = [
            {
                "raw_tags": ["κλητική", "ονομαστική", "πληθυντικού"],
                "form_of": [{"word": "κόρφος"}],
            }
        ]
        self.mktest_sense(raw, expected)

    def test_inflection_adj(self) -> None:
        # https://el.wiktionary.org/wiki/μικρή
        raw = """* {{θηλ_του-πτώσειςΟΑΚεν|μικρός}}"""
        expected = [
            {
                "tags": ["θηλυκό"],  # This is parsed somewhere else I guess
                "raw_tags": ["αιτιατική", "ενικού", "κλητική", "ονομαστική"],
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
                "raw_tags": ["αιτιατική", "ενικού"],
                "form_of": [{"word": "θαυμάσιος"}],
            },
            {
                "raw_tags": [
                    "αιτιατική",
                    "ενικού",
                    "κλητική",
                    "ονομαστική",
                    "ουδέτερο",
                ],
                "form_of": [{"word": "θαυμάσιος"}],
            },
        ]
        self.mktest_sense(raw, expected)

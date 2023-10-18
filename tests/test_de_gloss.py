import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.gloss import (
    extract_glosses,
    extract_tags_from_gloss_text,
    process_K_template,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestGlossList(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(dump_file_lang_code="de"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_de_extract_glosses(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(":[1] gloss1 \n:[2] gloss2")

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root)

        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "glosses": ["gloss1"],
                            "raw_glosses": ["[1] gloss1"],
                            "senseid": "1",
                        },
                        {
                            "glosses": ["gloss2"],
                            "raw_glosses": ["[2] gloss2"],
                            "senseid": "2",
                        },
                    ]
                }
            ],
        )

    def test_de_extract_glosses_with_subglosses(self):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            ":[1] gloss1\n::[a] subglossA\n::[b] subglossB"
        )

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root)

        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "glosses": ["gloss1"],
                            "raw_glosses": ["[1] gloss1"],
                            "senseid": "1",
                        },
                        {
                            "glosses": ["subglossA"],
                            "raw_glosses": ["[a] subglossA"],
                            "senseid": "1a",
                        },
                        {
                            "glosses": ["subglossB"],
                            "raw_glosses": ["[b] subglossB"],
                            "senseid": "1b",
                        },
                    ]
                }
            ],
        )

    def test_de_extract_glosses_with_only_subglosses(self):
        self.wxr.wtp.add_page("Vorlage:K", 10, "tag")
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse(
            ":[1] {{K|tag}}\n::[a] subglossA\n::[1b] subglossB"
        )

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root)
        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "tags": ["tag"],
                            "glosses": ["subglossA"],
                            "raw_glosses": ["[a] subglossA"],
                            "senseid": "1a",
                        },
                        {
                            "tags": ["tag"],
                            "glosses": ["subglossB"],
                            "raw_glosses": ["[1b] subglossB"],
                            "senseid": "1b",
                        },
                    ]
                }
            ],
        )

    def test_process_K_template_removes_K_template_nodes(self):
        self.wxr.wtp.add_page("Vorlage:K", 10, "tag1, tag2")
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse("{{K|tag1|tag2}} gloss1")

        gloss_data = defaultdict(list)

        self.assertEqual(len(root.children), 2)

        process_K_template(self.wxr, gloss_data, root)

        self.assertEqual(
            gloss_data,
            {
                "tags": ["tag1", "tag2"],
            },
        )

        self.assertEqual(len(root.children), 1)

    def get_mock(self, mock_return_value: str):
        def generic_mock(*args, **kwargs):
            return mock_return_value

        return generic_mock

    def test_process_K_template(self):
        # Test cases chosen from:
        # https://de.wiktionary.org/wiki/Vorlage:K/Doku
        test_cases = [
            # https://de.wiktionary.org/wiki/delektieren
            # One tag
            {
                "input": "{{K|refl.}}",
                "expected_tags": ["reflexiv"],
                "mock_return": "reflexiv:",
            },
            # https://de.wiktionary.org/wiki/abbreviare
            # With ft and spr args
            {
                "input": "{{K|trans.|ft=etwas in seinem [[räumlich]]en oder [[zeitlich]]en [[Ausmaß]] verringern|spr=it}}",
                "expected_tags": [
                    "transitiv",
                    "etwas in seinem räumlichen oder zeitlichen Ausmaß verringern",
                ],
                "mock_return": "transitiv, etwas in seinem räumlichen oder zeitlichen Ausmaß verringern:",
            },
            # https://de.wiktionary.org/wiki/abbreviare
            # With multiple tags
            {
                "input": "{{K|trans.|Linguistik|Wortbildung|spr=it}}",
                "expected_tags": [
                    "transitiv",
                    "Linguistik",
                    "Wortbildung",
                ],
                "mock_return": "transitiv, Linguistik, Wortbildung:",
            },
            # https://de.wiktionary.org/wiki/almen
            # Ideally we would filter out "besonders" but there doesn't seem
            # to be a general rule which tags are semmantially relevant
            # With multiple tags and t1, t2 args
            {
                "input": "{{K|trans.|t1=;|besonders|t2=_|bayrisch|österr.}}",
                "expected_tags": [
                    "transitiv",
                    "besonders bayrisch",
                    "österreichisch",
                ],
                "mock_return": "transitiv, besonders bayrisch, österreichisch",
            },
            # https://de.wiktionary.org/wiki/einlaufen
            # With two tags and t7 arg
            {
                "input": "{{K|intrans.|Nautik|t7=_|ft=(von Schiffen)}}",
                "expected_tags": ["intransitiv", "Nautik (von Schiffen)"],
                "mock_return": "intransitiv, Nautik (von Schiffen):",
            },
            # https://de.wiktionary.org/wiki/zählen
            # With Prä and Kas args
            {
                "input": "{{K|intrans.|Prä=auf|Kas=Akk.|ft=(auf jemanden/etwas zählen)}}",
                "expected_tags": [
                    "intransitiv",
                    "(auf jemanden/etwas zählen)",
                    "auf + Akk.",
                ],
                "mock_return": "intransitiv, (auf jemanden/etwas zählen):",
            },
            # https://de.wiktionary.org/wiki/bojovat
            # With Prä and Kas args and redundant ft arg
            {
                "input": "{{K|intrans.|Prä=proti|Kas=Dativ||ft=bojovat [[proti]] + [[Dativ]]|spr=cs}}",
                "expected_tags": [
                    "intransitiv",
                    "bojovat proti + Dativ",
                    "proti + Dativ",
                ],
                "mock_return": "intransitiv, bojovat proti + Dativ:",
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                gloss_data = defaultdict(list)

                self.wxr.wtp.start_page("")

                root = self.wxr.wtp.parse(case["input"])

                with patch(
                    "wiktextract.extractor.de.gloss.clean_node",
                    self.get_mock(case["mock_return"]),
                ):
                    process_K_template(self.wxr, gloss_data, root)
                    self.assertEqual(
                        gloss_data["tags"],
                        case["expected_tags"],
                    )

    def test_de_extract_tags_from_gloss_text(self):
        test_cases = [
            # https://de.wiktionary.org/wiki/Hengst
            {
                "input": "Zoologie: männliches Tier aus der Familie der Einhufer und Kamele",
                "expected_tags": ["Zoologie"],
                "expected_gloss": "männliches Tier aus der Familie der Einhufer und Kamele",
            },
            # https://de.wiktionary.org/wiki/ARD
            {
                "input": "umgangssprachlich, Kurzwort, Akronym: für das erste Fernsehprogramm der ARD",
                "expected_tags": ["umgangssprachlich", "Kurzwort", "Akronym"],
                "expected_gloss": "für das erste Fernsehprogramm der ARD",
            },
            # https://de.wiktionary.org/wiki/Endspiel
            {
                "input": "Drama von Samuel Beckett: Menschliche Existenz in der Endphase des Verfalls und der vergeblichen Suche nach einem Ausweg",
                "expected_tags": None,
                "expected_gloss": "Drama von Samuel Beckett: Menschliche Existenz in der Endphase des Verfalls und der vergeblichen Suche nach einem Ausweg",
            }
            # Add more test cases as needed
        ]
        for case in test_cases:
            with self.subTest(case=case):
                gloss_data = defaultdict(list)

                gloss_text = extract_tags_from_gloss_text(
                    gloss_data, case["input"]
                )

                if case["expected_tags"] is None:
                    self.assertEqual(gloss_data, {})
                else:
                    self.assertEqual(
                        gloss_data,
                        {
                            "tags": case["expected_tags"],
                        },
                    )
                self.assertEqual(gloss_text, case["expected_gloss"])

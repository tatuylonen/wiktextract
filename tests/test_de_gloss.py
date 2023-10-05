import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.gloss import (
    extract_glosses,
    extract_categories_from_gloss_node,
    extract_categories_from_gloss_text,
)
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestGlossList(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
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

        extract_glosses(self.wxr, page_data, root.children[0])

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

        extract_glosses(self.wxr, page_data, root.children[0])

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
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Vorlage:K", 10, "")
        root = self.wxr.wtp.parse(
            ":[1] {{K|category}}\n::[a] subglossA\n::[1b] subglossB"
        )

        page_data = [defaultdict(list)]

        extract_glosses(self.wxr, page_data, root.children[0])

        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "categories": ["category"],
                            "glosses": ["subglossA"],
                            "raw_glosses": ["[a] subglossA"],
                            "senseid": "1a",
                        },
                        {
                            "categories": ["category"],
                            "glosses": ["subglossB"],
                            "raw_glosses": ["[1b] subglossB"],
                            "senseid": "1b",
                        },
                    ]
                }
            ],
        )

    def test_de_extract_categories_from_gloss_node(self):
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Vorlage:K", 10, "")
        root = self.wxr.wtp.parse(":[1] {{K|category1|category2}} gloss1")

        list_item_node = root.children[0].children[0]

        gloss_data = defaultdict(list)

        extract_categories_from_gloss_node(self.wxr, gloss_data, list_item_node)

        self.assertEqual(
            gloss_data,
            {
                "categories": ["category1", "category2"],
            },
        )

    def test_de_extract_categories_from_gloss_text(self):
        test_cases = [
            {
                "input": "category1: gloss1",
                "expected_categories": ["category1"],
                "expected_gloss": "gloss1",
            },
            {
                "input": "category1, category2: gloss1",
                "expected_categories": ["category1", "category2"],
                "expected_gloss": "gloss1",
            },
            {
                "input": "category1 and category2: gloss1",
                "expected_categories": ["category1", "category2"],
                "expected_gloss": "gloss1",
            },
            {
                "input": "category1, category2 and category3: gloss1",
                "expected_categories": ["category1", "category2", "category3"],
                "expected_gloss": "gloss1",
            },
            {
                "input": "Beginning of gloss: second part of gloss",
                "expected_categories": None,
                "expected_gloss": "Beginning of gloss: second part of gloss",
            }
            # Add more test cases as needed
        ]
        for case in test_cases:
            with self.subTest(case=case):
                gloss_data = defaultdict(list)

                gloss_text = extract_categories_from_gloss_text(
                    gloss_data, case["input"]
                )

                if case["expected_categories"] is None:
                    self.assertEqual(gloss_data, {})
                else:
                    self.assertEqual(
                        gloss_data,
                        {
                            "categories": case["expected_categories"],
                        },
                    )
                self.assertEqual(gloss_text, case["expected_gloss"])

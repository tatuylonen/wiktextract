import unittest
from unittest.mock import patch

from wikitextprocessor import Page, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.simple.models import Form, WordEntry
from wiktextract.extractor.simple.pos import process_pos, remove_duplicate_forms
from wiktextract.wxr_context import WiktextractContext


class POSTests(unittest.TestCase):
    # maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="simple"),
            WiktionaryConfig(dump_file_lang_code="simple"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def process_test(self, text: str, should_be: dict) -> None:
        self.wxr.wtp.start_page("foo")
        entry = WordEntry(word="foo")
        root = self.wxr.wtp.parse(text)
        # print_tree(root)
        process_pos(self.wxr, root.children[0], entry, "noun")  # type: ignore
        # print(entry.model_dump(exclude_defaults=True))
        # print("==========")
        self.assertEqual(entry.model_dump(exclude_defaults=True), should_be)

    def test_glosses1(self) -> None:
        pos = """==Noun==
# Foo.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"glosses": ["Foo."]}],
        }
        self.process_test(pos, should_be)

    def test_glosses1b(self) -> None:
        pos = """==Noun==
Foo.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"glosses": ["Foo."]}],
        }
        self.process_test(pos, should_be)

    def test_glosses2(self) -> None:
        pos = """==Noun==
# Foo.
# Bar.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"glosses": ["Foo."]}, {"glosses": ["Bar."]}],
        }
        self.process_test(pos, should_be)

    def test_glosses3(self) -> None:
        pos = """==Noun==
# Foo.
## Baz.
# Bar.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"glosses": ["Foo.", "Baz."]}, {"glosses": ["Bar."]}],
        }
        self.process_test(pos, should_be)

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:verb",
            namespace_id=10,
            body="""{| border="0" width="100%25" class="inflection-table+inflection-noun-run-~-~-~-~-~-~"
|-
| bgcolor="%23e2e2ff" valign="top" width="49%25" style="padding-left%3A1em%3B" |
singular<br>
'''[[run]]'''
| width="0.5%25" |
| bgcolor="%23e2e2ff" valign="top" width="49%25" style="padding-left%3A1em%3B" |
plural<br>
<span class="form-of+plural-form-of-run">'''[[runs]]'''</span>
| width="0.5%25" |
|}
[[Category:Nouns]]""",
        ),
    )
    def test_template1(self, mock) -> None:
        pos = """==Noun==
{{noun}}
# Foo.
"""
        should_be = {
            "word": "foo",
            "forms": [
                {"form": "run", "tags": ["singular"]},
                {"form": "runs", "tags": ["plural"]},
            ],
            "pos": "noun",
            "senses": [{"glosses": ["Foo."]}],
            "head_templates": [{"name": "noun", "expansion": "[POS TABLE]"}],
        }
        self.process_test(pos, should_be)

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:verb",
            namespace_id=10,
            body="""{| border="0" width="100%25" class="inflection-table+inflection-noun-run-~-~-~-~-~-~"
|-
| bgcolor="%23e2e2ff" valign="top" width="49%25" style="padding-left%3A1em%3B" |
singular<br>
'''[[run]]'''
| width="0.5%25" |
| bgcolor="%23e2e2ff" valign="top" width="49%25" style="padding-left%3A1em%3B" |
plural<br>
<span class="form-of+plural-form-of-run">'''[[runs]]'''</span>
| width="0.5%25" |
|}
[[Category:Nouns]]""",
        ),
    )
    def test_template1b(self, mock) -> None:
        # No list ("#")
        pos = """==Noun==
{{noun}}
Foo.
"""
        should_be = {
            "word": "foo",
            "forms": [
                {"form": "run", "tags": ["singular"]},
                {"form": "runs", "tags": ["plural"]},
            ],
            "pos": "noun",
            "senses": [{"glosses": ["Foo."]}],
            "head_templates": [{"name": "noun", "expansion": "[POS TABLE]"}],
        }
        self.process_test(pos, should_be)

    def test_example1(self) -> None:
        pos = """==Noun==
# Foo.
#: Example bar.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "examples": [{"text": "Example bar."}],
                }
            ],
        }
        self.process_test(pos, should_be)

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:comparative",
            namespace_id=10,
            body="""(comparative)""",
        ),
    )
    def test_tags1(self, mock) -> None:
        pos = """==Noun==
# {{comparative}} Foo.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "tags": ["comparative"],
                }
            ],
        }
        self.process_test(pos, should_be)

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:comparative",
            namespace_id=10,
            body="""(comparative)""",
        ),
    )
    def test_tags1b(self, mock) -> None:
        pos = """==Noun==
{{comparative}} Foo.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "tags": ["comparative"],
                }
            ],
        }
        self.process_test(pos, should_be)

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:baz",
            namespace_id=10,
            body="""(baz)""",
        ),
    )
    def test_tags2(self, mock) -> None:
        pos = """==Noun==
# {{baz}} Foo.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "raw_tags": ["baz"],
                }
            ],
        }
        self.process_test(pos, should_be)

    def test_tags3(self) -> None:
        self.wxr.wtp.add_page("Template:baz", 10, "(baz)")
        self.wxr.wtp.add_page("Template:comparative", 10, "(comparative)")
        pos = """==Noun==
# {{baz}} {{comparative}} Foo.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "raw_tags": ["baz"],
                    "tags": ["comparative"],
                }
            ],
        }
        self.process_test(pos, should_be)

    def test_tags4(self) -> None:
        self.wxr.wtp.add_page(
            "Template:baz comparative", 10, "(baz, comparative)"
        )
        pos = """==Noun==
# {{baz comparative}} Foo.
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "raw_tags": ["baz"],
                    "tags": ["comparative"],
                }
            ],
        }
        self.process_test(pos, should_be)

    def test_synonyms1(self) -> None:
        self.wxr.wtp.add_page("Template:syn", 10, "")
        pos = """==Noun==
# Foo. {{syn|bar|baz}}
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "synonyms": [
                        {"word": "bar"},
                        {"word": "baz"},
                    ],
                }
            ],
        }
        self.process_test(pos, should_be)

    def test_synonyms2(self) -> None:
        self.wxr.wtp.add_page("Template:syn", 10, "")
        pos = """==Noun==
# Foo. {{syn||bar|baz|}}
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [
                {
                    "glosses": ["Foo."],
                    "synonyms": [
                        {"word": "bar"},
                        {"word": "baz"},
                    ],
                }
            ],
        }
        self.process_test(pos, should_be)

    def test_remove_duplicate_forms(self) -> None:
        input: list[Form] = [
            Form(form="foo"),
            Form(form="baz", tags=["comparative"]),
            Form(form="baz", tags=["comparative"]),
            Form(form="baz"),
            Form(form="baz"),
            Form(form="baz"),
        ]
        expected: list[Form] = [
            Form(form="foo"),
            Form(form="baz", tags=["comparative"]),
            Form(form="baz"),
        ]
        self.assertEqual(expected, remove_duplicate_forms(self.wxr, input))

    def test_empty_gloss1(self) -> None:
        pos = """==Noun==
#
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"tags": ["no-gloss"]}],
        }
        self.process_test(pos, should_be)

    def test_empty_gloss2(self) -> None:
        pos = """==Noun==
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"tags": ["no-gloss"]}],
        }
        self.process_test(pos, should_be)

    def test_empty_gloss3(self) -> None:
        pos = """==Noun==
{{exstub}}
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"tags": ["no-gloss"]}],
        }
        self.process_test(pos, should_be)

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:comparative",
            namespace_id=10,
            body="(comparative)",
        ),
    )
    def test_empty_gloss4(self, mock) -> None:
        pos = """==Noun==
{{comparative}}
"""
        should_be = {
            "word": "foo",
            "pos": "noun",
            "senses": [{"tags": ["comparative", "no-gloss"]}],
        }
        self.process_test(pos, should_be)

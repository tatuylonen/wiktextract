import unittest
from unittest.mock import patch

from wikitextprocessor import Page, WikiNode, Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.simple.models import WordEntry
from wiktextract.extractor.simple.pronunciation import process_pron
from wiktextract.wxr_context import WiktextractContext


class TestSIMPLEPronunciation(unittest.TestCase):
    # maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="simple"),
            WiktionaryConfig(dump_file_lang_code="simple"),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def extract_sound(self, text: str, target: dict) -> None:
        self.wxr.wtp.start_page("foo")
        root = self.wxr.wtp.parse(text)
        data: WordEntry = WordEntry(word="foo")
        if len(root.children) != 1 or not isinstance(
            root.children[0], WikiNode
        ):
            self.fail("Something went wrong with parsing the input text")
        process_pron(self.wxr, root.children[0], data)

        # from wikitextprocessor.parser import print_tree
        # print_tree(root)

        dumped = data.model_dump(exclude_defaults=True)
        self.assertEqual(dumped, target)

    def test_pron1(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* {{IPA|/foo/}}"""
        target = {
            "word": "foo",
            "sounds": [
                {
                    "ipa": "/foo/",
                }
            ],
        }
        self.extract_sound(text, target)

    def test_pron2(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* {{IPA|/foo/}}
* {{enPR|föö}}
"""
        target = {"word": "foo", "sounds": [{"ipa": "/foo/"}, {"enpr": "föö"}]}
        self.extract_sound(text, target)

    def test_pron3(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* {{IPA|/foo/}}, {{enPR|föö}}
"""
        target = {"word": "foo", "sounds": [{"ipa": "/foo/"}, {"enpr": "föö"}]}
        self.extract_sound(text, target)

    def test_pron4(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
; Verb
* {{IPA|/foo/}}
; Noun
* {{enPR|föö}}"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "pos": "verb"},
                {"enpr": "föö", "pos": "noun"},
            ],
        }
        self.extract_sound(text, target)

    def test_pron5(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
; Verb 1
* {{IPA|/foo/}}
; Verb 2
* {{enPR|föö}}"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "pos": "verb 1"},
                {"enpr": "föö", "pos": "verb 2"},
            ],
        }
        self.extract_sound(text, target)

    def test_pron6(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* Verb 1
* {{IPA|/foo/}}
* Verb 2
* {{enPR|föö}}"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "pos": "verb 1"},
                {"enpr": "föö", "pos": "verb 2"},
            ],
        }
        self.extract_sound(text, target)

    def test_pron7(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* Verb 1
** {{IPA|/foo/}}
** {{IPA|/bar/}}
* Verb 2
** {{enPR|föö}}"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "pos": "verb 1"},
                {"ipa": "/bar/", "pos": "verb 1"},
                {"enpr": "föö", "pos": "verb 2"},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_tags1(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* (UK) {{IPA|/foo/}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "tags": ["UK"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_tags2(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* (baz) {{IPA|/foo/}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "raw_tags": ["baz"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_tags3(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* (UK, baz) {{IPA|/foo/}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "raw_tags": ["baz"], "tags": ["UK"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_tags4(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* UK, baz {{IPA|/foo/}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "raw_tags": ["baz"], "tags": ["UK"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_tags5(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* UK, baz
**{{IPA|/foo/}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "raw_tags": ["baz"], "tags": ["UK"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_tags6(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* UK, baz {{IPA|/foo/}} {{enPR|baz}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "raw_tags": ["baz"], "tags": ["UK"]},
                {"enpr": "baz", "raw_tags": ["baz"], "tags": ["UK"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_tags7(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* UK {{ipachar|/foo/}} US {{enPR|baz}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"ipa": "/foo/", "tags": ["UK"]},
                {"enpr": "baz", "tags": ["US"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_audio1(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* {{audio|foo.wav|Audio (UK)}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"audio": "foo.wav", "tags": ["UK"], "raw_tags": ["Audio"]},
            ],
        }
        self.extract_sound(text, target)

    def test_pron_audio2(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* {{audio-ipa|foo.wav|/foo/}}
"""
        target = {
            "word": "foo",
            "sounds": [
                {"audio": "foo.wav", "ipa": "/foo/"},
            ],
        }
        self.extract_sound(text, target)

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:hyph",
            namespace_id=10,
            body="Hyphenation: foo.bar.baz",
        ),
    )
    def test_pron_hyphenation(self, mock_get_page) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* {{hyph|foo|bar|baz}}
"""
        target = {"word": "foo", "hyphenation": "foo.bar.baz"}
        self.extract_sound(text, target)

    def test_pron_homophones(self) -> None:
        self.wxr.wtp.start_page("foo")
        text = """=== Pronunciaton ===
* {{homophones|foo|bar|baz}}
"""
        target = {
            "word": "foo",
            "sounds": [{"homophones": ["foo", "bar", "baz"]}],
        }
        self.extract_sound(text, target)

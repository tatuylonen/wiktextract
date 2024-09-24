import unittest

from wikitextprocessor import WikiNode, Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.simple.models import Sound, WordEntry
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

        print(f"{data.model_dump(exclude_defaults=True)=}")

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
* {{IPA|/foo/}}
* {{enPR|föö}}"""
        target = {
            "word": "foo",
            "sounds": [
                {
                    "ipa": "/foo/",
                }
            ],
        }
        self.extract_sound(text, target)

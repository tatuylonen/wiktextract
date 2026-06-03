import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.models import Sense
from wiktextract.extractor.de.tags import translate_raw_tags
from wiktextract.wxr_context import WiktextractContext


class TestDEPage(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_de_recursive_topic(self) -> None:
        sense = Sense(raw_tags=["Soldatensprache"])
        translate_raw_tags(sense)  # type: ignore
        self.assertEqual(sense.tags, ["slang"])
        self.assertEqual(sense.topics, ["military"])

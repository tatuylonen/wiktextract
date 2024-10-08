from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ko.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKoSound(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="ko"),
            WiktionaryConfig(
                dump_file_lang_code="ko",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_common_sound_templates(self):
        self.wxr.wtp.start_page("answer")
        data = parse_page(
            self.wxr,
            "answer",
            """== 영어 ==
{{발음 듣기|en-uk-answer.ogg|영국|en-us-answer.ogg|미국}}
{{IPA|ˈɑːn.sə(ɹ)|영|ˈæn.sɚ|미}}

==== 타동사 ====
# [[대답하다]], [[대꾸하다]].""",
        )
        self.assertEqual(data[0]["sounds"][0]["audio"], "en-uk-answer.ogg")
        self.assertEqual(data[0]["sounds"][0]["raw_tags"], ["영국"])
        self.assertEqual(data[0]["sounds"][1]["audio"], "en-us-answer.ogg")
        self.assertEqual(data[0]["sounds"][1]["raw_tags"], ["미국"])
        self.assertEqual(
            data[0]["sounds"][2:],
            [
                {"ipa": "ˈɑːn.sə(ɹ)", "raw_tags": ["영"]},
                {"ipa": "ˈæn.sɚ", "raw_tags": ["미"]},
            ],
        )
        self.assertEqual(
            data[0]["senses"][0]["glosses"], ["대답하다, 대꾸하다."]
        )

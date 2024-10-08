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

    def test_ko_ipa_template(self):
        self.wxr.wtp.add_page(
            "틀:ko-IPA",
            10,
            """<ul><li>(<i>[[w:대한민국 표준어|표준어]]/[[w:경기 방언|서울]]</i>) [[w:국제 음성 기호|IPA]]<sup>([[위키낱말사전:국제 음성 기호|표기]])</sup>: <span class="IPA">[ka̠]</span></li><li class="ko-pron__ph">발음: <span class="Kore" lang="ko">[<span>가</span>]</span></li></ul><table><tr><th colspan="2">로마자 표기 목록</th></tr><tr><th>[[부록:로마자 표기법/국어|국어의 로마자 표기]]<br/><span>Revised Romanization</span></th><td class="IPA">ga</td></tr></table>[[분류:한국어 IPA 발음이 포함된 낱말]]""",
        )
        data = parse_page(
            self.wxr,
            "가",
            """== 한국어 ==
{{ko-IPA}}

=== 명사 ===
==== 명사 1 ====
# 어떤""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {"ipa": "[ka̠]", "raw_tags": ["표준어/서울"]},
                {"hangul": "[가]"},
                {"roman": "ga", "raw_tags": ["Revised Romanization"]},
            ],
        )
        self.assertEqual(
            data[0]["categories"], ["한국어 IPA 발음이 포함된 낱말"]
        )

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
                {"roman": "ga", "tags": ["revised", "romanization"]},
            ],
        )
        self.assertEqual(
            data[0]["categories"], ["한국어 IPA 발음이 포함된 낱말"]
        )

    def test_ja_pron(self):
        self.wxr.wtp.add_page(
            "틀:ja-pron",
            10,
            """<ul><li><span class="usage-label-accent"><span class="ib-brac">(</span><span class="ib-content">[[w:도쿄 방언|도쿄]]</span><span class="ib-brac">)</span></span> <span lang="ja" class="Jpan"><span>と<span></span></span>ーざい</span></span> <span class="Latn"><samp>[tóꜜòzàì]</samp></span> ([[頭高型|두고형]] – [1])</li><li>[[w:국제 음성 기호|IPA]]<sup>([[부록:일본어 발음|표기]])</sup>:&#32;<span class="IPA">[to̞ːza̠i]</span>[[Category:일본어 IPA 발음이 포함된 낱말|とうざい]][[Category:일본어 중복되지 않는 수동 정렬 키를 포함하는 낱말|東西]]</li></ul>""",
        )
        data = parse_page(
            self.wxr,
            "東西",
            """== 일본어 ==
=== 발음 ===
* {{ja-pron|とうざい|acc=1|acc_ref=DJR,NHK}}
=== 명사 ===
# [[동서]] ([[동쪽]]과 [[서쪽]])""",
        )
        self.assertEqual(
            data[0]["sounds"],
            [
                {
                    "roman": "[tóꜜòzàì]",
                    "other": "とーざい",
                    "raw_tags": ["도쿄"],
                },
                {"ipa": "[to̞ːza̠i]"},
            ],
        )
        self.assertEqual(
            data[0]["categories"],
            [
                "일본어 IPA 발음이 포함된 낱말",
                "일본어 중복되지 않는 수동 정렬 키를 포함하는 낱말",
            ],
        )

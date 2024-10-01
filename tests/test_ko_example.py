from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ko.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKoExample(TestCase):
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

    def test_ja_ruby(self):
        self.wxr.wtp.add_page(
            "틀:r", 10, "<ruby><rb>{{{1}}}</rb><rt>{{{2}}}</rt></ruby>"
        )
        data = parse_page(
            self.wxr,
            "犬",
            """== 일본어 ==
=== 명사 ===
* '''1.''' [[개]].
:* {{lang|ja|どの{{r|'''犬'''|いぬ}}が{{r|彼女|かのじょ}}のですか。—あの{{r|大|おお}}きい{{r|犬|いぬ}}です。}} 어느 쪽 개가 그 여자의 것입니까? — 저 큰 개입니다.""",
        )
        self.assertEqual(
            data[0]["senses"][0]["examples"][0],
            {
                "text": "どの犬が彼女のですか。—あの大きい犬です。",
                "ruby": [
                    ("犬", "いぬ"),
                    ("彼女", "かのじょ"),
                    ("大", "おお"),
                    ("犬", "いぬ"),
                ],
                "translation": "어느 쪽 개가 그 여자의 것입니까? — 저 큰 개입니다.",
            },
        )

    def test_zh(self):
        data = parse_page(
            self.wxr,
            "大家",
            """== 중국어 ==
* '''1.''' 모든 [[사람]], [[모두]], 사람들
: {{lang|zh|聖春問'''大家'''/聖春问'''大家'''  (Shèng chūn wèn dàjiā) }} 성춴은 모두에게 물었다.""",
        )
        self.assertEqual(
            data[0]["senses"][0]["examples"],
            [
                {
                    "text": "聖春問大家",
                    "roman": "Shèng chūn wèn dàjiā",
                    "tags": ["Traditional Chinese"],
                    "translation": "성춴은 모두에게 물었다.",
                },
                {
                    "text": "聖春问大家",
                    "roman": "Shèng chūn wèn dàjiā",
                    "tags": ["Simplified Chinese"],
                    "translation": "성춴은 모두에게 물었다.",
                },
            ],
        )

    def test_ref_quote_template(self):
        self.wxr.wtp.add_page(
            "틀:따옴삼국지",
            10,
            "3세기, 진수,《삼국지》, 〈권30 위서 오환선비동이전 (魏書 烏丸鮮卑東夷傳)〉",
        )
        data = parse_page(
            self.wxr,
            "犬",
            """== 한자 ==
=== 의미 ===
* '''1.''' (동물) [[개]].
:* 肥養犬 개를 살찌게 기르다. {{따옴삼국지|30|30 위서 오환선비동이전 (魏書 烏丸鮮卑東夷傳)}}""",
        )
        self.assertEqual(
            data[0]["senses"][0]["examples"][0],
            {
                "text": "肥養犬 개를 살찌게 기르다.",
                "ref": "3세기, 진수,《삼국지》, 〈권30 위서 오환선비동이전 (魏書 烏丸鮮卑東夷傳)〉",
            },
        )

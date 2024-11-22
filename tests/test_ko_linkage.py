from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.ko.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestKoLinkage(TestCase):
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

    def test_proverbs(self):
        data = parse_page(
            self.wxr,
            "개",
            """== 한국어 ==
=== 명사 ===
==== 명사 1 ====
# 가축으로

===== 속담 =====
* [[개 눈에는 똥만 보인다|'''개''' 눈에는 똥만 보인다]]: 어떤 일이나 물건이 자신에 마음에만 들도록 하는 사람의 태도를 비꼬아 하는 말.
* '''개'''가 벼룩 씹 듯 한다: 쓸데 없는 일에 잔소리를 되풀이하는 사람을 비꼬아 하는 말.""",
        )
        self.assertEqual(
            data[0]["proverbs"],
            [
                {
                    "word": "개 눈에는 똥만 보인다",
                    "sense": "어떤 일이나 물건이 자신에 마음에만 들도록 하는 사람의 태도를 비꼬아 하는 말.",
                },
                {
                    "word": "개가 벼룩 씹 듯 한다",
                    "sense": "쓸데 없는 일에 잔소리를 되풀이하는 사람을 비꼬아 하는 말.",
                },
            ],
        )

    def test_linkage_list_under_gloss_list(self):
        data = parse_page(
            self.wxr,
            "마르다",
            """== 한국어 ==
=== 명사 ===
# 젖은 것에 물기가 없어지다.
*반의어: [[젖다]]
{{합성어 상자|마른걸레}}""",
        )
        self.assertEqual(
            data[0]["antonyms"],
            [{"word": "젖다", "sense": "젖은 것에 물기가 없어지다."}],
        )
        self.assertEqual(
            data[0]["derived"],
            [{"word": "마른걸레", "sense": "젖은 것에 물기가 없어지다."}],
        )

    def test_colon_linkage_list(self):
        data = parse_page(
            self.wxr,
            "한글",
            """== 한국어 ==
=== 명사 ===
# 한국 고유의 글자이자 문자.
:* '''한글'''은 창제 당시 총 28개의 자모가 있었지만 지금은 24개만 사용한다.
:유의어: [[훈민정음]]""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [{"word": "훈민정음", "sense": "한국 고유의 글자이자 문자."}],
        )
        self.assertEqual(
            data[0]["senses"][0]["examples"],
            [
                {
                    "text": "한글은 창제 당시 총 28개의 자모가 있었지만 지금은 24개만 사용한다."
                }
            ],
        )

    def test_zh_pinyin(self):
        data = parse_page(
            self.wxr,
            "土",
            """== 중국어 ==
=== 명사 ===
* '''1.''' 흙, 땅
=== 합성어 ===
:*[[土產]]/[[土产 ]](tǔchǎn)""",
        )
        self.assertEqual(
            data[0]["derived"],
            [
                {"word": "土產", "roman": "tǔchǎn"},
                {"word": "土产", "roman": "tǔchǎn"},
            ],
        )

    def test_l_template(self):
        data = parse_page(
            self.wxr,
            "병신",
            """== 중국어 ==
=== 명사 ===
# 다쳐서
==== 관용구 ====
* {{l|ko|병신도 제 재미에 산다|t=사람은 각자 자기 잘 난 맛에 산다라는 뜻}}""",
        )
        self.assertEqual(
            data[0]["proverbs"],
            [
                {
                    "word": "병신도 제 재미에 산다",
                    "sense": "사람은 각자 자기 잘 난 맛에 산다라는 뜻",
                }
            ],
        )

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
        self.assertEqual(data[0]["antonyms"], [{"word": "젖다"}])
        self.assertEqual(data[0]["derived"], [{"word": "마른걸레"}])

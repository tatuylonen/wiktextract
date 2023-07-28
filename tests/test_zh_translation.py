import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Page, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.translation import extract_translation
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestTranslation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"), WiktionaryConfig(dump_file_lang_code="zh")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(title="", namespace_id=10, body=""),
    )
    def test_normal(self, mock_get_page) -> None:
        # test wikitext from page "你好" and "這裡"
        page_data = [defaultdict(list)]
        wikitext = """
{{trans-top|靠近說話者的地方}}
* 阿爾巴尼亞語：këtu (sq)
* 阿帕切語：
*: 西阿帕切語：kú
* 阿拉伯語：هُنَا‎ (hunā)
*: 埃及阿拉伯語：هنا‎ (henā)
*俄语：[[привет|приве́т]] ‎(privét) (非正式), [[здравствуйте|здра́вствуйте]] ‎(zdrávstvujte) (正式, 第一个"в"不发音)
{{trans-bottom}}
* 斯洛伐克語：pracovať impf
        """
        self.wxr.wtp.start_page("你好")
        node = self.wxr.wtp.parse(wikitext)
        extract_translation(self.wxr, page_data, node)
        self.assertEqual(
            page_data[0].get("translations"),
            [
                {
                    "code": "sq",
                    "lang": "阿爾巴尼亞語",
                    "sense": "靠近說話者的地方",
                    "word": "këtu",
                },
                {
                    "code": None,
                    "lang": "西阿帕切語",
                    "sense": "靠近說話者的地方",
                    "word": "kú",
                },
                {
                    "code": "ar",
                    "lang": "阿拉伯語",
                    "sense": "靠近說話者的地方",
                    "tags": ["hunā"],
                    "word": "هُنَا",
                },
                {
                    "code": "arz",
                    "lang": "埃及阿拉伯語",
                    "sense": "靠近說話者的地方",
                    "tags": ["henā"],
                    "word": "هنا",
                },
                {
                    "code": "ru",
                    "lang": "俄语",
                    "sense": "靠近說話者的地方",
                    "tags": ["privét", "非正式"],
                    "word": "приве́т",
                },
                {
                    "code": "ru",
                    "lang": "俄语",
                    "sense": "靠近說話者的地方",
                    "tags": ["zdrávstvujte", '正式, 第一个"в"不发音'],
                    "word": "здра́вствуйте",
                },
                {
                    "code": "sk",
                    "lang": "斯洛伐克語",
                    "sense": "靠近說話者的地方",
                    "tags": ["imperfective aspect"],
                    "word": "pracovať",
                },
            ],
        )

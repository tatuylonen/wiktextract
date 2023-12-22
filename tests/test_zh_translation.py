from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Page, Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.models import WordEntry
from wiktextract.extractor.zh.translation import extract_translation
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestZhTranslation(TestCase):
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
        page_data = [WordEntry(word="你好", lang_code="zh", lang_name="漢語")]
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
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[0].translations
            ],
            [
                {
                    "lang_code": "sq",
                    "lang_name": "阿爾巴尼亞語",
                    "sense": "靠近說話者的地方",
                    "word": "këtu",
                },
                {
                    "lang_name": "西阿帕切語",
                    "sense": "靠近說話者的地方",
                    "word": "kú",
                },
                {
                    "lang_code": "ar",
                    "lang_name": "阿拉伯語",
                    "sense": "靠近說話者的地方",
                    "roman": "hunā",
                    "word": "هُنَا",
                },
                {
                    "lang_code": "arz",
                    "lang_name": "埃及阿拉伯語",
                    "sense": "靠近說話者的地方",
                    "roman": "henā",
                    "word": "هنا",
                },
                {
                    "lang_code": "ru",
                    "lang_name": "俄语",
                    "sense": "靠近說話者的地方",
                    "roman": "privét",
                    "tags": ["非正式"],
                    "word": "приве́т",
                },
                {
                    "lang_code": "ru",
                    "lang_name": "俄语",
                    "sense": "靠近說話者的地方",
                    "roman": "zdrávstvujte",
                    "tags": ['正式, 第一个"в"不发音'],
                    "word": "здра́вствуйте",
                },
                {
                    "lang_code": "sk",
                    "lang_name": "斯洛伐克語",
                    "sense": "靠近說話者的地方",
                    "tags": ["imperfective aspect"],
                    "word": "pracovať",
                },
            ],
        )

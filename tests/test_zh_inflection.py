import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Page, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.inflection import extract_inflections
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestInflection(unittest.TestCase):
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
        return_value=Page(
            title="Template:ja-i",
            namespace_id=10,
            body="""{|
|-
! 基本形
|-
! 未然形
| 可笑しかろ
| おかしかろ
| okashikaro
|}
            """,
        ),
    )
    def test_ja_i_template(self, mock_get_page) -> None:
        page_data = [
            defaultdict(
                list,
                {
                    "lang": "日語",
                    "lang_code": "ja",
                    "word": "可笑しい",
                },
            )
        ]
        wikitext = "{{ja-i|可笑し|おかし|okashi}}"
        self.wxr.wtp.start_page("可笑しい")
        node = self.wxr.wtp.parse(wikitext)
        extract_inflections(self.wxr, page_data, node)
        self.assertEqual(
            page_data[0].get("forms"),
            [
                {
                    "form": "可笑しかろ",
                    "hiragana": "おかしかろ",
                    "roman": "okashikaro",
                    "source": "inflection",
                    "tags": ["基本形", "未然形"],
                },
            ],
        )

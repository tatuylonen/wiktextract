from unittest import TestCase
from unittest.mock import patch, Mock

from wikitextprocessor import Wtp
from wiktextract.extractor.zh.headword_line import extract_headword_line
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestHeadword(TestCase):
    @patch(
        "wiktextract.extractor.zh.headword_line.clean_node",
        return_value="manga (可數 & 不可數，複數 manga 或 mangas)",
    )
    def test_english_headword(self, mock_clean_node):
        node = Mock()
        node.args = [["en-noun"]]
        page_data = [{}]
        wtp = Wtp()
        wtp.title = "manga"
        wxr = WiktextractContext(wtp, Mock())
        extract_headword_line(wxr, page_data, node, "en")
        wtp.close_db_conn()
        close_thesaurus_db(wxr.thesaurus_db_path, wxr.thesaurus_db_conn)
        self.assertEqual(
            page_data,
            [
                {
                    "forms": [
                        {"form": "manga", "tags": ["plural"]},
                        {"form": "mangas", "tags": ["plural"]},
                    ],
                    "tags": ["countable", "uncountable"],
                }
            ],
        )

    @patch(
        "wiktextract.extractor.zh.headword_line.clean_node",
        return_value="manga m (複數 manga's，指小詞 mangaatje n)",
    )
    def test_headword_gender(self, mock_clean_node):
        node = Mock()
        node.args = [["nl-noun"]]
        page_data = [{}]
        wtp = Wtp()
        wtp.title = "manga"
        wxr = WiktextractContext(wtp, Mock())
        extract_headword_line(wxr, page_data, node, "nl")
        wtp.close_db_conn()
        close_thesaurus_db(wxr.thesaurus_db_path, wxr.thesaurus_db_conn)
        self.assertEqual(
            page_data,
            [
                {
                    "forms": [
                        {"form": "manga's", "tags": ["plural"]},
                        {"form": "mangaatje", "tags": ["diminutive", "neuter"]},
                    ],
                    "tags": ["masculine"],
                }
            ],
        )

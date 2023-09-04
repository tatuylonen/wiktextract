import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.form_line import extract_form_line
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestFormLine(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    @patch(
        "wiktextract.extractor.fr.form_line.clean_node",
        return_value="/lə nɔ̃/",
    )
    def test_pron_and_gender(self, mock_clean_node):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse("'''le nom''' {{pron|lə nɔ̃|fr}} {{m}}")
        page_data = [defaultdict(list)]
        extract_form_line(self.wxr, page_data, root.children)
        self.assertEqual(
            page_data,
            [{"sounds": [{"ipa": "/lə nɔ̃/"}], "tags": ["masculine"]}],
        )

from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.zh.example import extract_examples
from wiktextract.extractor.zh.models import Sense
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestExample(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="zh"), WiktionaryConfig(dump_file_lang_code="zh")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_example_list(self) -> None:
        sense_data = Sense()
        wikitext = """
#* ref text
#*: example text
        """
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, sense_data, node, [])
        self.assertEqual(
            sense_data.examples[0].model_dump(exclude_defaults=True),
            {
                "ref": "ref text",
                "texts": ["example text"],
            },
        )

    @patch(
        "wiktextract.extractor.zh.example.clean_node",
        return_value="""ref text
quote text
translation text""",
    )
    def test_quote_example(self, mock_clean_node) -> None:
        sense_data = Sense()
        wikitext = "#* {{RQ:Schuster Hepaticae}}"
        self.wxr.wtp.start_page("test")
        node = self.wxr.wtp.parse(wikitext)
        extract_examples(self.wxr, sense_data, node, [])
        self.assertEqual(
            sense_data.examples[0].model_dump(exclude_defaults=True),
            {
                "ref": "ref text",
                "texts": ["quote text"],
                "translation": "translation text",
            },
        )

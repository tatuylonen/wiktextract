import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.gloss import extract_gloss
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
        "wikitextprocessor.Wtp.node_to_html",
        return_value="<span class='term' id='fr-sportif'><i>(<span class='texte'>Sport</span>)</i></span>[[Catégorie:Sportifs en français]]",
    )
    def test_theme_templates(self, mock_node_to_html):
        self.wxr.wtp.start_page("")
        root = self.wxr.wtp.parse("# {{sportifs|fr}} gloss.\n#* example")
        page_data = [defaultdict(list)]
        extract_gloss(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data,
            [
                {
                    "senses": [
                        {
                            "glosses": ["(Sport)"],
                            "tags": ["Sport"],
                            "categories": ["Sportifs en français"],
                        }
                    ]
                }
            ],
        )

import unittest
from collections import defaultdict
from unittest.mock import patch

from wikitextprocessor import NodeKind, WikiNode, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.inflection import extract_inflection
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestInflection(unittest.TestCase):
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
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|
! Singulier !! Pluriel
|-
|'''<span><bdi>productrice</bdi></span>'''
| <bdi>[[productrices#fr|productrices]]</bdi>
|-
| colspan='2'
|[[Annexe:Prononciation/français|<span>\\pʁɔ.dyk.tʁis\\</span>]]
|}
        """,
    )
    def test_fr_reg(self, mock_node_to_wikitext):
        page_data = [defaultdict(list, {"word": "productrice"})]
        node = WikiNode(NodeKind.TEMPLATE, 0)
        self.wxr.wtp.start_page("productrice")
        extract_inflection(self.wxr, page_data, node, "fr-rég")
        self.assertEqual(
            page_data[-1].get("forms"),
            [{"form": "productrices", "tags": ["plural"]}],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|
|-
| class='invisible' |
! scope='col' ! Singulier !! Pluriel
|-
! scope='row' | Masculin
| [[producteur]]<br/>[[Annexe:Prononciation/français|<span>\\pʁɔ.dyk.tœʁ\\</span>]]
| [[producteurs]]<br/>[[Annexe:Prononciation/français|<span>\\pʁɔ.dyk.tœʁ\\</span>]]
|-
! scope='row' | Féminin
| [[productrice]]<br/>[[Annexe:Prononciation/français|<span>\\pʁɔ.dyk.tʁis\\</span>]]
| [[productrices]]<br/>[[Annexe:Prononciation/français|<span>\\pʁɔ.dyk.tʁis\\</span>]]
|}
        """,
    )
    def test_fr_accord(self, mock_node_to_wikitext):
        page_data = [defaultdict(list, {"word": "productrice"})]
        node = WikiNode(NodeKind.TEMPLATE, 0)
        self.wxr.wtp.start_page("productrice")
        extract_inflection(self.wxr, page_data, node, "fr-accord-eur")
        self.assertEqual(
            page_data[-1].get("forms"),
            [
                {
                    "form": "producteur",
                    "tags": ["singular", "masculine"],
                    "ipa": "\\pʁɔ.dyk.tœʁ\\",
                },
                {
                    "form": "producteurs",
                    "tags": ["plural", "masculine"],
                    "ipa": "\\pʁɔ.dyk.tœʁ\\",
                },
                {
                    "form": "productrices",
                    "tags": ["plural", "feminine"],
                    "ipa": "\\pʁɔ.dyk.tʁis\\",
                },
            ],
        )

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
        return_value="""
{|
! Singulier !! Pluriel
|-
|'''<span><bdi>productrice</bdi></span>'''
| <bdi>[[productrices#fr|productrices]]</bdi>
|-
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
            [{"form": "productrices", "tags": ["Pluriel"]}],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|
|-
|class='invisible'|
!scope='col'| Singulier
!scope='col'| Pluriel
|- class='flextable-fr-m'
!scope='row'| Masculin
|[[animal]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mal\\</span>]]
|[[animaux]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mo\\</span>]]
|- class='flextable-fr-f'
!scope='row'| Féminin
|[[animale]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mal\\</span>]]
|[[animales]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mal\\</span>]]
|}"""
    )
    def test_fr_accord_al(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/animal#Adjectif
        page_data = [defaultdict(list, {"word": "animal", "lang_code": "fr"})]
        node = WikiNode(NodeKind.TEMPLATE, 0)
        self.wxr.wtp.start_page("animal")
        extract_inflection(self.wxr, page_data, node, "fr-accord-al")
        self.assertEqual(
            page_data[-1].get("forms"),
            [
                {
                    "ipa": "\\a.ni.mo\\",
                    "tags": ["Pluriel", "Masculin"],
                    "form": "animaux"
                },
                {
                    "ipa": "\\a.ni.mal\\",
                    "tags": ["Singulier", "Féminin"],
                    "form": "animale"
                },
                {
                    "ipa": "\\a.ni.mal\\",
                    "tags": ["Pluriel", "Féminin"],
                    "form": "animales"
                }
            ]
        )

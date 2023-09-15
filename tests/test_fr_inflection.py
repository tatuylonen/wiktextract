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
|}""",
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
                    "form": "animaux",
                },
                {
                    "ipa": "\\a.ni.mal\\",
                    "tags": ["Singulier", "Féminin"],
                    "form": "animale",
                },
                {
                    "ipa": "\\a.ni.mal\\",
                    "tags": ["Pluriel", "Féminin"],
                    "form": "animales",
                },
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{| class='flextable flextable-en'
! Singulier !! Pluriel
|-
| '''<span lang='en' xml:lang='en' class='lang-en'><bdi>ration</bdi></span>'''<br />[[Annexe:Prononciation/anglais|<span>\\ˈɹæʃ.ən\\</span>]]<br /><small>ou</small> [[Annexe:Prononciation/anglais|<span>\\ˈɹeɪʃ.ən\\</span>]]
|  <bdi lang='en' xml:lang='en' class='lang-en'>[[rations#en-flex-nom|rations]]</bdi><br />[[Annexe:Prononciation/anglais|<span>\\ˈɹæʃ.ənz\\</span>]]<br /><small>ou</small> [[Annexe:Prononciation/anglais|<span>\\ˈɹeɪʃ.ənz\\</span>]]
|}""",
    )
    def test_multiple_lines_ipa(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/ration#Nom_commun_2
        page_data = [defaultdict(list, {"lang_code": "en", "word": "ration"})]
        node = WikiNode(NodeKind.TEMPLATE, 0)
        self.wxr.wtp.start_page("ration")
        extract_inflection(self.wxr, page_data, node, "en-nom-rég")
        self.assertEqual(
            page_data[-1].get("forms"),
            [
                {
                    "ipas": ["\\ˈɹæʃ.ənz\\", "\\ˈɹeɪʃ.ənz\\"],
                    "tags": ["Pluriel"],
                    "form": "rations",
                }
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|class='flextable'
! Temps
! Forme
|-
! Infinitif
| <span lang='en' xml:lang='en' class='lang-en'><bdi>to</bdi></span> '''<span lang='en' xml:lang='en' class='lang-en'><bdi>ration</bdi></span>'''<br />[[Annexe:Prononciation/anglais|<span>\\ˈɹæʃ.ən\\</span>]]<small> ou </small>[[Annexe:Prononciation/anglais|<span>\\ˈɹeɪʃ.ən\\</span>]]
|}""",
    )
    def test_single_line_multiple_ipa(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/ration#Verbe
        page_data = [defaultdict(list, {"lang_code": "en", "word": "ration"})]
        node = WikiNode(NodeKind.TEMPLATE, 0)
        self.wxr.wtp.start_page("ration")
        extract_inflection(self.wxr, page_data, node, "en-conj-rég")
        self.assertEqual(
            page_data[-1].get("forms"),
            [
                {
                    "ipas": ["\\ˈɹæʃ.ən\\", "\\ˈɹeɪʃ.ən\\"],
                    "tags": ["Infinitif"],
                    "form": "to ration",
                }
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|
! '''Singulier'''
! '''Pluriel'''
|-
| [[animal]]<span><br /><span>\\<small><span>[//fr.wiktionary.org/w/index.php?title=ration&action=edit Prononciation ?]</span></small>\\</span></span>
| [[animales]]<span><br /><span>\\<small><span>[//fr.wiktionary.org/w/index.php?title=ration&action=edit Prononciation ?]</span></small>\\</span></span>
|}""",
    )
    def test_invalid_ipa(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/animal#Nom_commun_3
        page_data = [defaultdict(list, {"lang_code": "en", "word": "animal"})]
        node = WikiNode(NodeKind.TEMPLATE, 0)
        self.wxr.wtp.start_page("animal")
        extract_inflection(self.wxr, page_data, node, "ast-accord-mf")
        self.assertEqual(
            page_data[-1].get("forms"),
            [{"tags": ["Pluriel"], "form": "animales"}],
        )

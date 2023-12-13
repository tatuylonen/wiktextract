from unittest import TestCase
from unittest.mock import patch

from wikitextprocessor import Wtp
from wikitextprocessor.parser import TemplateNode
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.inflection import extract_inflection
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestInflection(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

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
        page_data = [
            WordEntry(word="productrice", lang_code="fr", lang_name="Français")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("productrice")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"form": "productrices", "tags": ["Pluriel"]}],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|class="flextable flextable-fr-mfsp"
|-
!scope="col"| Singulier
!scope="col"| Pluriel
|- class="flextable-fr-m"
!scope="row"| Masculin
|[[animal]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mal\\</span>]]
|[[animaux]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mo\\</span>]]
|- class="flextable-fr-f"
!scope="row"| Féminin
|[[animale]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mal\\</span>]]
|[[animales]]<br>[[Annexe:Prononciation/français|<span>\\a.ni.mal\\</span>]]
|}""",
    )
    def test_fr_accord_al(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/animal#Adjectif
        page_data = [
            WordEntry(word="animal", lang_code="fr", lang_name="Français")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("animal")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "ipas": ["\\a.ni.mo\\"],
                    "tags": ["Pluriel", "Masculin"],
                    "form": "animaux",
                },
                {
                    "ipas": ["\\a.ni.mal\\"],
                    "tags": ["Singulier", "Féminin"],
                    "form": "animale",
                },
                {
                    "ipas": ["\\a.ni.mal\\"],
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
        # template "en-nom-rég"
        page_data = [
            WordEntry(word="ration", lang_code="en", lang_name="Anglais")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("ration")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
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
        # template "en-conj-rég"
        page_data = [
            WordEntry(word="ration", lang_code="en", lang_name="Anglais")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("ration")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
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
        # template "ast-accord-mf"
        page_data = [
            WordEntry(word="animal", lang_code="en", lang_name="Français")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("animal")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"tags": ["Pluriel"], "form": "animales"}],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{| class="flextable"
|-
! Simplifié
| <bdi lang="zh-Hans" xml:lang="zh-Hans" class="lang-zh-Hans">[[一万#zh|一万]]</bdi>
|-
! Traditionnel
| <bdi lang="zh-Hant" xml:lang="zh-Hant" class="lang-zh-Hant">[[一萬#zh|一萬]]</bdi>
|}""",
    )
    def test_no_column_headers(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/一万#Nom_commun
        # template "zh-formes"
        page_data = [WordEntry(word="一万", lang_code="zh", lang_name="Chinois")]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("一万")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"tags": ["Traditionnel"], "form": "一萬"}],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{| class="flextable"
!Cas
! Singulier
! Pluriel
|-
! Nominatif
|| <bdi lang="lt" xml:lang="lt" class="lang-lt">[[abadas#lt|abadas]]</bdi>
|| '''<span lang="lt" xml:lang="lt" class="lang-lt"><bdi>abadai</bdi></span>'''
|}""",
    )
    def test_lt_décl_as(self, mock_node_to_wikitext):
        # empty table cells should be ignored
        page_data = [
            WordEntry(word="abadai", lang_code="lt", lang_name="Lituanien")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("abadai")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"tags": ["Singulier", "Nominatif"], "form": "abadas"}],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|class="flextable flextable-fr-mfsp"

|-
| class="invisible" |
! scope="col" | Singulier
! scope="col" | Pluriel
|- class="flextable-fr-m"
! scope="row" | Masculin
|colspan="2"| [[aastais]]<br
/>[[Annexe:Prononciation/français|<span>\\a.a.stɛ\\</span>]]

|- class="flextable-fr-f"
! scope="row" | Féminin
| [[aastaise]]<br
/>[[Annexe:Prononciation/français|<span>\\a.a.stɛz\\</span>]]
| [[aastaises]]<br
/>[[Annexe:Prononciation/français|<span>\\a.a.stɛz\\</span>]]
|}""",
    )
    def test_fr_accord_s(self, mock_node_to_wikitext):
        page_data = [
            WordEntry(word="aastais", lang_code="fr", lang_name="Français")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("aastais")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "tags": ["Singulier", "Féminin"],
                    "form": "aastaise",
                    "ipas": ["\\a.a.stɛz\\"],
                },
                {
                    "tags": ["Pluriel", "Féminin"],
                    "form": "aastaises",
                    "ipas": ["\\a.a.stɛz\\"],
                },
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{| class="flextable"
| colspan="2" |
! Singulier !! Pluriel
|-
! rowspan="2" | 1<sup>e</sup> personne
! Masculin
| [[enculé de ma race]]<br/>[[Annexe:Prononciation/français|<span>\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\</span>]]
| [[enculés de notre race]]<br/>[[Annexe:Prononciation/français|<span>\\ɑ̃.ky.ˌle.də.nɔ.tʁə.ˈʁas\\</span>]]
|-
! Féminin
| [[enculée de ma race]]<br/>[[Annexe:Prononciation/français|<span>\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\</span>]]
| [[enculées de notre race]]<br/>[[Annexe:Prononciation/français|<span>\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\</span>]]
|}""",
    )
    def test_fr_accord_personne(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/enculé_de_ta_race
        page_data = [
            WordEntry(
                word="enculé de ta race", lang_code="fr", lang_name="Français"
            )
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("enculé de ta race")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "form": "enculé de ma race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\"],
                    "tags": ["Singulier", "1ᵉ personne", "Masculin"],
                },
                {
                    "form": "enculés de notre race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.nɔ.tʁə.ˈʁas\\"],
                    "tags": ["Pluriel", "1ᵉ personne", "Masculin"],
                },
                {
                    "form": "enculée de ma race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\"],
                    "tags": ["Singulier", "1ᵉ personne", "Féminin"],
                },
                {
                    "form": "enculées de notre race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\"],
                    "tags": ["Pluriel", "1ᵉ personne", "Féminin"],
                },
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{| class="flextable"
! <span class="ligne-de-forme"  ><i>masculin</i></span>
! colspan=2 | Singulier
! colspan=2 | Pluriel
|-
! cas || non articulé || articulé || non articulé || articulé
|-
! Nominatif<br />Accusatif
| <bdi lang="ro" xml:lang="ro" class="lang-ro">[[fenil#ro-nom|fenil]]</bdi>
| <bdi lang="ro" xml:lang="ro" class="lang-ro">[[fenilul#ro-nom|fenilul]]</bdi>
| <bdi lang="ro" xml:lang="ro" class="lang-ro">[[fenili#ro-nom|fenili]]</bdi>
| <bdi lang="ro" xml:lang="ro" class="lang-ro">[[fenilii#ro-nom|fenilii]]</bdi>
|-
! Vocatif
| colspan=2| <bdi lang="ro" xml:lang="ro" class="lang-ro">[[fenilule#ro-nom|fenilule]]</bdi>
| colspan=2| <bdi lang="ro" xml:lang="ro" class="lang-ro">[[fenililor#ro-nom|fenililor]]</bdi>
|}""",
    )
    def test_ro_nom_tab(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/fenil#Nom_commun_4
        page_data = [
            WordEntry(word="fenil", lang_code="fr", lang_name="Français")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("fenil")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "form": "fenilul",
                    "tags": ["Singulier", "articulé", "Nominatif Accusatif"],
                },
                {
                    "form": "fenili",
                    "tags": ["Pluriel", "non articulé", "Nominatif Accusatif"],
                },
                {
                    "form": "fenilii",
                    "tags": ["Pluriel", "articulé", "Nominatif Accusatif"],
                },
                {"form": "fenilule", "tags": ["Singulier", "Vocatif"]},
                {"form": "fenililor", "tags": ["Pluriel", "Vocatif"]},
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{| class="flextable flextable-sv"
! class="invisible" |
|-
! Commun
! Indéfini
! Défini
|-
! Singulier
| class="sing-indef" |<bdi lang="sv" xml:lang="sv" class="lang-sv">[[robot|robot]]</bdi>
| class="sing-def" |<bdi lang="sv" xml:lang="sv" class="lang-sv">[[roboten#sv|roboten]]</bdi>
|-
! Pluriel
| class="plur-indef" |<bdi lang="sv" xml:lang="sv" class="lang-sv">[[robotar#sv|robotar]]</bdi>
| class="plur-def" |<bdi lang="sv" xml:lang="sv" class="lang-sv">[[robotarna#sv|robotarna]]</bdi>
|}""",
    )
    def test_sv_nom_c_ar(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/robot#Nom_commun_7
        page_data = [
            WordEntry(word="robot", lang_code="fr", lang_name="Français")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("robot")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {"form": "roboten", "tags": ["Défini", "Singulier"]},
                {"form": "robotar", "tags": ["Indéfini", "Pluriel"]},
                {"form": "robotarna", "tags": ["Défini", "Pluriel"]},
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.node_to_wikitext",
        return_value="""{|class="flextable"
|-
!scope="col"| Cas<nowiki />
!scope="col"| Singulier<nowiki />
!scope="col"| Pluriel
|-
!scope="row"| Nominatif<nowiki />
| [[robot#cs-nom|robot''' ''']]<nowiki />
| [[roboti#cs-flex-nom|robot'''i ''']]<br /><small>''ou''</small> [[robotové#cs-flex-nom|robot'''ové ''']]<nowiki />
|}""",
    )
    def test_cs_decl_nom_ma_dur(self, mock_node_to_wikitext):
        # https://fr.wiktionary.org/wiki/robot#Nom_commun_1_2
        page_data = [
            WordEntry(word="robot", lang_code="fr", lang_name="Français")
        ]
        node = TemplateNode(0)
        self.wxr.wtp.start_page("robot")
        extract_inflection(self.wxr, page_data, node)
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {"form": "roboti", "tags": ["Pluriel", "Nominatif"]},
                {"form": "robotové", "tags": ["Pluriel", "Nominatif"]},
            ],
        )

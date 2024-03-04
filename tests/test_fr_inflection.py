from unittest import TestCase

from wikitextprocessor import Wtp
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

    def test_fr_reg(self):
        page_data = [
            WordEntry(word="productrice", lang_code="fr", lang="Français")
        ]
        self.wxr.wtp.add_page(
            "Modèle:fr-rég",
            10,
            """
{|
! Singulier !! Pluriel
|-
|'''<span><bdi>productrice</bdi></span>'''
| <bdi>[[productrices#fr|productrices]]</bdi>
|-
|[[Annexe:Prononciation/français|<span>\\pʁɔ.dyk.tʁis\\</span>]]
|}""",
        )
        self.wxr.wtp.start_page("productrice")
        root = self.wxr.wtp.parse("{{fr-rég|pʁɔ.dyk.tʁis}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"form": "productrices", "tags": ["plural"]}],
        )

    def test_fr_accord_al(self):
        # https://fr.wiktionary.org/wiki/animal#Adjectif
        page_data = [WordEntry(word="animal", lang_code="fr", lang="Français")]
        self.wxr.wtp.add_page(
            "Modèle:fr-accord-al",
            10,
            """{|class="flextable flextable-fr-mfsp"
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
        self.wxr.wtp.start_page("animal")
        root = self.wxr.wtp.parse("{{fr-accord-al|a.ni.m}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "ipas": ["\\a.ni.mo\\"],
                    "tags": ["plural", "masculine"],
                    "form": "animaux",
                },
                {
                    "ipas": ["\\a.ni.mal\\"],
                    "tags": ["singular", "feminine"],
                    "form": "animale",
                },
                {
                    "ipas": ["\\a.ni.mal\\"],
                    "tags": ["plural", "feminine"],
                    "form": "animales",
                },
            ],
        )

    def test_multiple_lines_ipa(self):
        # https://fr.wiktionary.org/wiki/ration#Nom_commun_2
        # template "en-nom-rég"
        page_data = [WordEntry(word="ration", lang_code="en", lang="Anglais")]
        self.wxr.wtp.add_page(
            "Modèle:en-nom-rég",
            10,
            """{| class='flextable flextable-en'
! Singulier !! Pluriel
|-
| '''<span lang='en' xml:lang='en' class='lang-en'><bdi>ration</bdi></span>'''<br />[[Annexe:Prononciation/anglais|<span>\\ˈɹæʃ.ən\\</span>]]<br /><small>ou</small> [[Annexe:Prononciation/anglais|<span>\\ˈɹeɪʃ.ən\\</span>]]
|  <bdi lang='en' xml:lang='en' class='lang-en'>[[rations#en-flex-nom|rations]]</bdi><br />[[Annexe:Prononciation/anglais|<span>\\ˈɹæʃ.ənz\\</span>]]<br /><small>ou</small> [[Annexe:Prononciation/anglais|<span>\\ˈɹeɪʃ.ənz\\</span>]]
|}""",
        )
        self.wxr.wtp.start_page("ration")
        root = self.wxr.wtp.parse("{{en-nom-rég|ˈɹæʃ.ən|ˈɹeɪʃ.ən}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "ipas": ["\\ˈɹæʃ.ənz\\", "\\ˈɹeɪʃ.ənz\\"],
                    "tags": ["plural"],
                    "form": "rations",
                }
            ],
        )

    def test_single_line_multiple_ipa(self):
        # https://fr.wiktionary.org/wiki/ration#Verbe
        # template "en-conj-rég"
        page_data = [WordEntry(word="ration", lang_code="en", lang="Anglais")]
        self.wxr.wtp.add_page(
            "Modèle:en-conj-rég",
            10,
            """{|class='flextable'
! Temps
! Forme
|-
! Infinitif
| <span lang='en' xml:lang='en' class='lang-en'><bdi>to</bdi></span> '''<span lang='en' xml:lang='en' class='lang-en'><bdi>ration</bdi></span>'''<br />[[Annexe:Prononciation/anglais|<span>\\ˈɹæʃ.ən\\</span>]]<small> ou </small>[[Annexe:Prononciation/anglais|<span>\\ˈɹeɪʃ.ən\\</span>]]
|}""",
        )
        self.wxr.wtp.start_page("ration")
        root = self.wxr.wtp.parse(
            "{{en-conj-rég|inf.pron=ˈɹæʃ.ən|inf.pron2=ˈɹeɪʃ.ən}}"
        )
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "ipas": ["\\ˈɹæʃ.ən\\", "\\ˈɹeɪʃ.ən\\"],
                    "tags": ["infinitive"],
                    "form": "to ration",
                }
            ],
        )

    def test_invalid_ipa(self):
        # https://fr.wiktionary.org/wiki/animal#Nom_commun_3
        page_data = [WordEntry(word="animal", lang_code="en", lang="Français")]
        self.wxr.wtp.add_page(
            "Modèle:ast-accord-mf",
            10,
            """{|
! '''Singulier'''
! '''Pluriel'''
|-
| [[animal]]<span><br /><span>\\<small><span>[//fr.wiktionary.org/w/index.php?title=ration&action=edit Prononciation ?]</span></small>\\</span></span>
| [[animales]]<span><br /><span>\\<small><span>[//fr.wiktionary.org/w/index.php?title=ration&action=edit Prononciation ?]</span></small>\\</span></span>
|}""",
        )
        self.wxr.wtp.start_page("animal")
        root = self.wxr.wtp.parse(
            "{{ast-accord-mf|s=animal|ps=|p=animales|pp=}}"
        )
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"tags": ["plural"], "form": "animales"}],
        )

    def test_no_column_headers(self):
        # https://fr.wiktionary.org/wiki/一万#Nom_commun
        # template "zh-formes"
        page_data = [WordEntry(word="一万", lang_code="zh", lang="Chinois")]
        self.wxr.wtp.add_page(
            "Modèle:zh-formes",
            10,
            """{| class="flextable"
|-
! Simplifié
| <bdi lang="zh-Hans" xml:lang="zh-Hans" class="lang-zh-Hans">[[一万#zh|一万]]</bdi>
|-
! Traditionnel
| <bdi lang="zh-Hant" xml:lang="zh-Hant" class="lang-zh-Hant">[[一萬#zh|一萬]]</bdi>
|}""",
        )
        self.wxr.wtp.start_page("一万")
        root = self.wxr.wtp.parse("{{zh-formes|一万|一萬}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"raw_tags": ["Traditionnel"], "form": "一萬"}],
        )

    def test_lt_décl_as(self):
        # empty table cells should be ignored
        page_data = [WordEntry(word="abadai", lang_code="lt", lang="Lituanien")]
        self.wxr.wtp.add_page(
            "Modèle:lt-décl-as",
            10,
            """{| class="flextable"
!Cas
! Singulier
! Pluriel
|-
! Nominatif
|| <bdi lang="lt" xml:lang="lt" class="lang-lt">[[abadas#lt|abadas]]</bdi>
|| '''<span lang="lt" xml:lang="lt" class="lang-lt"><bdi>abadai</bdi></span>'''
|}""",
        )
        self.wxr.wtp.start_page("abadai")
        root = self.wxr.wtp.parse("{{lt-décl-as|abad}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"tags": ["singular", "nominative"], "form": "abadas"}],
        )

    def test_fr_accord_s(self):
        page_data = [WordEntry(word="aastais", lang_code="fr", lang="Français")]
        self.wxr.wtp.add_page(
            "Modèle:fr-accord-s",
            10,
            """{|class="flextable flextable-fr-mfsp"

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
        self.wxr.wtp.start_page("aastais")
        root = self.wxr.wtp.parse("{{fr-accord-s|a.a.stɛ|ms=aastais}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "tags": ["singular", "feminine"],
                    "form": "aastaise",
                    "ipas": ["\\a.a.stɛz\\"],
                },
                {
                    "tags": ["plural", "feminine"],
                    "form": "aastaises",
                    "ipas": ["\\a.a.stɛz\\"],
                },
            ],
        )

    def test_fr_accord_personne(self):
        # https://fr.wiktionary.org/wiki/enculé_de_ta_race
        page_data = [
            WordEntry(word="enculé de ta race", lang_code="fr", lang="Français")
        ]
        self.wxr.wtp.add_page(
            "Modèle:fr-accord-personne",
            10,
            """{| class="flextable"
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
        self.wxr.wtp.start_page("enculé de ta race")
        root = self.wxr.wtp.parse(
            "{{fr-accord-personne|1ms = enculé de ma race}}"
        )
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "form": "enculé de ma race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\"],
                    "tags": ["singular", "first-person", "masculine"],
                },
                {
                    "form": "enculés de notre race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.nɔ.tʁə.ˈʁas\\"],
                    "tags": ["plural", "first-person", "masculine"],
                },
                {
                    "form": "enculée de ma race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\"],
                    "tags": ["singular", "first-person", "feminine"],
                },
                {
                    "form": "enculées de notre race",
                    "ipas": ["\\ɑ̃.ky.ˌle.də.ma.ˈʁas\\"],
                    "tags": ["plural", "first-person", "feminine"],
                },
            ],
        )

    def test_ro_nom_tab(self):
        # https://fr.wiktionary.org/wiki/fenil#Nom_commun_4
        page_data = [WordEntry(word="fenil", lang_code="fr", lang="Français")]
        self.wxr.wtp.add_page(
            "Modèle:ro-nom-tab",
            10,
            """{| class="flextable"
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
        self.wxr.wtp.start_page("fenil")
        root = self.wxr.wtp.parse(
            """{{ro-nom-tab|gen=masculin
|ns=fenil |np=fenili
|as=fenilul |ap=fenilii
|ds=fenilului |dp=fenililor
|vs=fenilule |vp=fenililor
}}""",
        )
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "form": "fenilul",
                    "tags": ["singular"],
                    "raw_tags": [
                        "articulé",
                        "Nominatif Accusatif",
                    ],
                },
                {
                    "form": "fenili",
                    "tags": ["plural"],
                    "raw_tags": [
                        "non articulé",
                        "Nominatif Accusatif",
                    ],
                },
                {
                    "form": "fenilii",
                    "tags": ["plural"],
                    "raw_tags": ["articulé", "Nominatif Accusatif"],
                },
                {"form": "fenilule", "tags": ["singular", "vocative"]},
                {"form": "fenililor", "tags": ["plural", "vocative"]},
            ],
        )

    def test_sv_nom_c_ar(self):
        # https://fr.wiktionary.org/wiki/robot#Nom_commun_7
        page_data = [WordEntry(word="robot", lang_code="fr", lang="Français")]
        self.wxr.wtp.add_page(
            "Modèle:sv-nom-c-ar",
            10,
            """{| class="flextable flextable-sv"
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
        self.wxr.wtp.start_page("robot")
        root = self.wxr.wtp.parse("{{sv-nom-c-ar}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {"form": "roboten", "tags": ["definite", "singular"]},
                {"form": "robotar", "tags": ["indefinite", "plural"]},
                {"form": "robotarna", "tags": ["definite", "plural"]},
            ],
        )

    def test_cs_decl_nom_ma_dur(self):
        # https://fr.wiktionary.org/wiki/robot#Nom_commun_1_2
        page_data = [WordEntry(word="robot", lang_code="fr", lang="Français")]
        self.wxr.wtp.add_page(
            "Modèle:cs-décl-nom-ma-dur",
            10,
            """{|class="flextable"
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
        self.wxr.wtp.start_page("robot")
        root = self.wxr.wtp.parse("{{cs-décl-nom-ma-dur|rad=robot}}")
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {"form": "roboti", "tags": ["plural", "nominative"]},
                {"form": "robotové", "tags": ["plural", "nominative"]},
            ],
        )

    def test_en_adj(self):
        # https://fr.wiktionary.org/wiki/new
        page_data = [WordEntry(word="new", lang_code="en", lang="Anglais")]
        self.wxr.wtp.start_page("new")
        root = self.wxr.wtp.parse("{{en-adj-er|pron=ˈnu|pronGB=ˈnjuː}}")
        self.wxr.wtp.add_page(
            "Modèle:en-adj-er",
            10,
            """{| class="flextable"
! Nature
! Forme
|-
| class="titre" | Positif
| '''<span lang="en" xml:lang="en" class="lang-en"><bdi>new</bdi></span>'''<br />[[Annexe:Prononciation/anglais|<span class="API" title="Prononciation API">\\ˈnu\\</span>]]<small> ou </small>[[Annexe:Prononciation/anglais|<span class="API" title="Prononciation API">\\ˈnjuː\\</span>]]
|-
| class="titre" | Comparatif
| <bdi lang="en" xml:lang="en" class="lang-en">[[newer#en|newer]]</bdi><br />[[Annexe:Prononciation/anglais|<span class="API" title="Prononciation API">\\ˈnu.ɚ\\</span>]]<small> ou </small>[[Annexe:Prononciation/anglais|<span class="API" title="Prononciation API">\\ˈnjuː.ə\\</span>]]
|-
| class="titre" | Superlatif
| <bdi lang="en" xml:lang="en" class="lang-en">[[newest#en|newest]]</bdi><br />[[Annexe:Prononciation/anglais|<span class="API" title="Prononciation API">\\ˈnu.ɪst\\</span>]]<small> ou </small>[[Annexe:Prononciation/anglais|<span class="API" title="Prononciation API">\\ˈnjuː.ɪst\\</span>]]
|}""",
        )
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "form": "newer",
                    "tags": ["comparative"],
                    "ipas": ["\\ˈnu.ɚ\\", "\\ˈnjuː.ə\\"],
                },
                {
                    "form": "newest",
                    "tags": ["superlative"],
                    "ipas": ["\\ˈnu.ɪst\\", "\\ˈnjuː.ɪst\\"],
                },
            ],
        )

    def test_fr_verbe_flexion(self):
        page_data = [WordEntry(word="dièse", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("dièse")
        root = self.wxr.wtp.parse("{{fr-verbe-flexion|diéser}}")
        self.wxr.wtp.add_page(
            "Modèle:fr-verbe-flexion",
            10,
            """{|
!colspan="3"|Voir la conjugaison du verbe ''diéser''
|-
|rowspan="2" | '''Indicatif'''
|rowspan="2" | '''Présent'''
| je <nowiki />dièse
|-
| il/elle/on dièse
|}""",
        )
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "form": "je dièse",
                    "tags": ["indicative", "present"],
                },
                {
                    "form": "il/elle/on dièse",
                    "tags": ["indicative", "present"],
                },
            ],
        )

    def test_it_enclise(self):
        page_data = [
            WordEntry(word="abbacarla", lang_code="it", lang="Italien")
        ]
        self.wxr.wtp.start_page("abbacarla")
        root = self.wxr.wtp.parse("{{it-enclise|abbacare|abbacar|abbacando}}")
        self.wxr.wtp.add_page(
            "Modèle:it-enclise",
            10,
            """{| class="flextable"
! Infinitif
| colspan=2| '''<bdi>[[abbacare#it|abbacare]]</bdi>'''
|-
! pronom<br />personnel || singulier || pluriel
|-
! masculin
| <bdi>[[abbacarlo#it|abbacarlo]]</bdi>
| <bdi>[[abbacargli#it|abbacargli]]</bdi>
|}""",
        )
        extract_inflection(self.wxr, page_data, root.children[0])
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [
                {
                    "form": "abbacare",
                    "tags": ["infinitive"],
                },
                {
                    "form": "abbacarlo",
                    "tags": ["singular", "masculine"],
                },
                {
                    "form": "abbacargli",
                    "tags": ["plural", "masculine"],
                },
            ],
        )

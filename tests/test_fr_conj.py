from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.conjugation import extract_conjugation
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestNotes(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_fr_conj_1(self):
        self.wxr.wtp.start_page("lancer")
        self.wxr.wtp.add_page(
            "Conjugaison:français/lancer", 116, "{{fr-conj-1-cer|lan|lɑ̃}}"
        )
        self.wxr.wtp.add_page(
            "Modèle:fr-conj-1-cer",
            10,
            """<h3> Modes impersonnels </h3>
<div>
{|
|-[[mode|Mode]]
!colspan=\"3\"|[[présent|Présent]]
!colspan=\"3\"|[[passé|Passé]]
|-
|'''[[infinitif|Infinitif]]'''
|&nbsp;&nbsp;
|[[lancer]]
|<span>\\lɑ̃.se\\</span>
|avoir
|[[lancé]]
|<span>\\a.vwaʁ lɑ̃.se\\</span>
|}
</div>

<h3> Indicatif </h3>
<div>
{|
|-
|width="50%"|
<table>
  <tr>
    <th colspan=\"4\">Présent</th>
  </tr>
  <tr>
    <td>je&nbsp;</td>
    <td>[[lance]]</td>
    <td>\\<span>ʒə&nbsp;</span></td>
    <td><span>lɑ̃s</span>\\</td>
  </tr>
</table>
|width="50%"|
{|
|-
!colspan=\"4\"|Passé composé
|-
|j’ai&nbsp;
|lancé&nbsp;
|<span>\\ʒ‿e lɑ̃.se\\</span>
|}
|}
</div>""",
        )
        entry = WordEntry(lang_code="fr", lang="Français", word="lancer")
        extract_conjugation(self.wxr, entry, "Conjugaison:français/lancer")
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in entry.forms],
            [
                {
                    "form": "lancer",
                    "ipas": ["\\lɑ̃.se\\"],
                    "source": "Conjugaison:français/lancer",
                    "tags": ["infinitive", "present"],
                },
                {
                    "form": "avoir lancé",
                    "ipas": ["\\a.vwaʁ lɑ̃.se\\"],
                    "source": "Conjugaison:français/lancer",
                    "tags": ["infinitive", "past"],
                },
                {
                    "form": "je lance",
                    "ipas": ["\\ʒə lɑ̃s\\"],
                    "source": "Conjugaison:français/lancer",
                    "tags": ["indicative", "present"],
                },
                {
                    "form": "j’ai lancé",
                    "ipas": ["\\ʒ‿e lɑ̃.se\\"],
                    "source": "Conjugaison:français/lancer",
                    "tags": ["indicative", "past", "multiword-construction"],
                },
            ],
        )

    def test_onglets_conjugaison(self):
        # https://fr.wiktionary.org/wiki/Conjugaison:français/s’abattre
        self.wxr.wtp.start_page("s’abattre")
        self.wxr.wtp.add_page(
            "Conjugaison:français/abattre",
            116,
            """{{Onglets conjugaison
| onglet1  =Conjugaison active
| contenu1 ={{fr-conj-3-attre|ab|a.b|'=oui}}
| onglet2  =Conjugaison pronominale
| contenu2 ={{fr-conj-3-attre|ab|a.b|'=oui|réfl=1}}
| sél ={{{sél|1}}}
}}""",
        )
        self.wxr.wtp.add_page(
            "Conjugaison:français/s’abattre",
            116,
            "{{:Conjugaison:français/abattre|sél=2}}",
        )
        self.wxr.wtp.add_page(
            "Modèle:fr-conj-3-attre",
            10,
            """<h3> Modes impersonnels </h3>
<div>
{|
|-[[mode|Mode]]
!colspan=\"3\"|[[présent|Présent]]
!colspan=\"3\"|[[passé|Passé]]
|-
|'''[[infinitif|Infinitif]]'''
|s’
|[[abattre]]
|<span>\\s‿a.batʁ\\</span>
|s’être
|[[abattu]]
|<span>\\s‿ɛtʁ‿a.ba.ty\\</span>
|}
</div>
<h3> Impératif </h3>
<div>
{|
|-
|width=\"50%\"|
{|
|-
!colspan=\"3\"|Présent<nowiki />
|-
|[[abats]]
|width=\"25%\"|-toi&nbsp;<nowiki />
|width=\"50%\"|[[Annexe:Prononciation/français|<span>\\a.ba.twa\\</span>]]
|}
|width=\"50%\"|
{|
|-
!Passé<nowiki />
|-
|align=\"center\"|—
|}
|}
</div>""",
        )
        entry = WordEntry(lang_code="fr", lang="Français", word="s’abattre")
        extract_conjugation(self.wxr, entry, "Conjugaison:français/s’abattre")
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in entry.forms],
            [
                {
                    "form": "s’abattre",
                    "ipas": ["\\s‿a.batʁ\\"],
                    "source": "Conjugaison:français/abattre",
                    "tags": ["infinitive", "present"],
                },
                {
                    "form": "s’être abattu",
                    "ipas": ["\\s‿ɛtʁ‿a.ba.ty\\"],
                    "source": "Conjugaison:français/abattre",
                    "tags": ["infinitive", "past"],
                },
                {
                    "form": "abats-toi",
                    "ipas": ["\\a.ba.twa\\"],
                    "source": "Conjugaison:français/abattre",
                    "tags": ["imperative", "present"],
                },
            ],
        )

    def test_ja_flx_adj(self):
        # https://fr.wiktionary.org/wiki/Conjugaison:japonais/格好だ
        self.wxr.wtp.start_page("格好")
        self.wxr.wtp.add_page(
            "Conjugaison:japonais/格好だ",
            116,
            "{{ja-flx-adj-な|格好|かっこう|kakkou}}",
        )
        self.wxr.wtp.add_page(
            "Modèle:ja-flx-adj-な",
            10,
            """<h4>Flexions</h4>
{|
|-
! colspan=\"4\" | '''Formes de base'''
|-
| '''Imperfectif''' (<span>未然形</span>) || <span>[[格好だろ]]</span>  || <span>[[かっこうだろ]]</span>  || ''kakkou daro''
|-
! colspan=\"4\" | '''Clefs de constructions'''
|-
| '''Neutre négatif''' || <span>[[格好ではない]]<br>[[格好じゃない]]</span> || <span>[[かっこうではない]]<br>[[かっこうじゃない]]</span> || ''kakkou dewa nai<br>kakkou ja nai''
|}""",  # noqa:E501
        )
        entry = WordEntry(lang_code="ja", lang="Japonais", word="格好")
        extract_conjugation(self.wxr, entry, "Conjugaison:japonais/格好だ")
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in entry.forms],
            [
                {
                    "form": "格好だろ",
                    "hiragana": "かっこうだろ",
                    "roman": "kakkou daro",
                    "source": "Conjugaison:japonais/格好だ",
                    "tags": ["base-form"],
                    "raw_tags": ["Imperfectif (未然形)"],
                },
                {
                    "form": "格好ではない",
                    "hiragana": "かっこうではない",
                    "roman": "kakkou dewa nai",
                    "source": "Conjugaison:japonais/格好だ",
                    "tags": ["neuter", "negative"],
                    "raw_tags": ["Clefs de constructions"],
                },
                {
                    "form": "格好じゃない",
                    "hiragana": "かっこうじゃない",
                    "roman": "kakkou ja nai",
                    "source": "Conjugaison:japonais/格好だ",
                    "tags": ["neuter", "negative"],
                    "raw_tags": ["Clefs de constructions"],
                },
            ],
        )

    def test_ja_conj(self):
        # https://fr.wiktionary.org/wiki/Conjugaison:japonais/在る
        self.wxr.wtp.start_page("在る")
        self.wxr.wtp.add_page("Conjugaison:japonais/在る", 116, "{{ja-在る}}")
        self.wxr.wtp.add_page(
            "Modèle:ja-在る",
            10,
            """{|
! colspan=\"7\" | '''Formes de base'''
|-
! colspan=\"4\" | '''L'inaccompli'''
| <bdi>[[在る#ja|在る]]</bdi>
| <bdi>[[ある#ja|ある]]</bdi>
| ''aru\n''
|-
! colspan=\"4\" | '''Imperfectif''' (<bdi>[[未然形#ja-nom|未然形]]</bdi>, <bdi>''mizen-kei''</bdi>)
| <bdi>[[無い#ja|無い]]</bdi>
| <bdi>[[ない#ja|ない]]</bdi>
| ''nai\n''
|-
! colspan=\"7\" | '''Clefs de constructions'''
|-
! colspan=\"2\" | Temps
! Forme
! Terme
! [[kanji|Kanji]]
! [[hiragana|Hiragana]]
! [[romaji|Rōmaji]]
|-
! rowspan=\"4\" colspan=\"2\" | Présent / Futur
! rowspan=\"2\" | poli
! affirmatif
| <bdi>[[在ります#ja|在ります]]</bdi>
| <bdi>[[あります#ja|あります]]</bdi>
| ''arimasu\n''
|-
! négatif
| <bdi>[[在りません#ja|在りません]]</bdi>
| <bdi>[[ありません#ja|ありません]]</bdi>
| ''arimasen\n''
|}""",  # noqa:E501
        )
        entry = WordEntry(lang_code="ja", lang="Japonais", word="在る")
        extract_conjugation(self.wxr, entry, "Conjugaison:japonais/在る")
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in entry.forms],
            [
                {
                    "form": "在る",
                    "hiragana": "ある",
                    "roman": "aru",
                    "source": "Conjugaison:japonais/在る",
                    "tags": ["base-form"],
                    "raw_tags": ["L'inaccompli"],
                },
                {
                    "form": "無い",
                    "hiragana": "ない",
                    "roman": "nai",
                    "source": "Conjugaison:japonais/在る",
                    "tags": ["base-form"],
                    "raw_tags": ["Imperfectif (未然形, mizen-kei)"],
                },
                {
                    "form": "在ります",
                    "hiragana": "あります",
                    "roman": "arimasu",
                    "source": "Conjugaison:japonais/在る",
                    "tags": ["present", "future", "polite", "affirmative"],
                    "raw_tags": ["Clefs de constructions"],
                },
                {
                    "form": "在りません",
                    "hiragana": "ありません",
                    "roman": "arimasen",
                    "source": "Conjugaison:japonais/在る",
                    "tags": ["present", "future", "polite", "negative"],
                    "raw_tags": ["Clefs de constructions"],
                },
            ],
        )

    def test_ku_conj_trans(self):
        self.wxr.wtp.start_page("gotin")
        self.wxr.wtp.add_page(
            "Conjugaison:kurde/gotin",
            116,
            "{{ku-conj-trans|gotin|bêj|got||pr=b|dr=c|prp=c|drp=c|incompl=oui}}",
        )
        self.wxr.wtp.add_page(
            "Modèle:ku-conj-trans",
            10,
            """{|
|-
! colspan="7" | Conjugaison du verbe gotin en kurmandji
|-
| &nbsp;
|-
! colspan="7"| TEMPS DU PRÉSENT ET DU FUTUR
|-
! colspan="3" | Présent
| &nbsp;
! colspan="3" | Présent progressif
| &nbsp;
|-
! Forme affirmative
| &nbsp;
! Forme négative
| &nbsp;
! Forme affirmative
| &nbsp;
! Forme négative
|-
| ez [[dibêjim]]
| &nbsp;
| ez [[nabêjim]]
| &nbsp;
| ez [[dibêjime]]
| &nbsp;
| ez [[nabêjime]]
|-
| colspan="7" | &nbsp;
|-
! Subjonctif
| &nbsp;
! Futur
| &nbsp;
|-
! Forme affirmative
| &nbsp;
! Forme négative
| &nbsp;
! Forme affirmative
| &nbsp;
! Forme négative
|-
| ez [[bibêjim]]
|}

{|
|-
! colspan="3" | TEMPS DU PASSÉ
|-
| colspan="3" | ignore this
|-
| &nbsp;
|-
! colspan="3" | Prétérit
| &nbsp;
|-
! Forme affirmative
| &nbsp;
! Forme négative
|-
| (''inusité'')
| &nbsp;
| (''inusité'')
|-
| <span style="color:green">min/ te/</span> <span style="color:lime">''wî''/ ''wê''/</span> <span style="color:green">me/ we/ wan</span> <span style="color:blue">ew/</span> <span style="color:teal">''xwe''</span> [[got]]
|}
[[Catégorie:Conjugaison en kurde]]""",
        )
        entry = WordEntry(lang_code="ku", lang="Kurde", word="gotin")
        extract_conjugation(self.wxr, entry, "Conjugaison:kurde/gotin")
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in entry.forms],
            [
                {
                    "form": "ez dibêjim",
                    "tags": ["present", "affirmative"],
                    "source": "Conjugaison:kurde/gotin",
                },
                {
                    "form": "ez nabêjim",
                    "tags": ["present", "negative"],
                    "source": "Conjugaison:kurde/gotin",
                },
                {
                    "form": "ez dibêjime",
                    "tags": ["present", "progressive", "affirmative"],
                    "source": "Conjugaison:kurde/gotin",
                },
                {
                    "form": "ez nabêjime",
                    "tags": ["present", "progressive", "negative"],
                    "source": "Conjugaison:kurde/gotin",
                },
                {
                    "form": "ez bibêjim",
                    "tags": ["subjunctive", "affirmative"],
                    "source": "Conjugaison:kurde/gotin",
                },
                {
                    "form": "min/ te/ wî/ wê/ me/ we/ wan ew/ xwe got",
                    "tags": ["preterite", "affirmative"],
                    "source": "Conjugaison:kurde/gotin",
                },
            ],
        )
        self.assertEqual(entry.categories, ["Conjugaison en kurde"])

    def test_ko_conj(self):
        self.wxr.wtp.start_page("오다")
        self.wxr.wtp.add_page(
            "Conjugaison:coréen/오다", 116, "{{ko-conj|rad3=court|classe=v}}"
        )
        self.wxr.wtp.add_page(
            "Modèle:ko-conj",
            10,
            """<h3><span>Verbe</span><span> </span>[[Catégorie:Wiktionnaire:Sections de type avec locution forcée]]</h3>
{|
|-
| ignore
|}
{|
|+ Formes finales
! rowspan="2" colspan="3" |
! colspan="2" | Registre formel
! colspan="2" | Registre informel
|-
! Non poli !! Poli !! Non poli !! Poli
|-
! rowspan="17" | Non passé
! rowspan="6" | Indicatif
! Déclaratif
| <span lang="ko" xml:lang="ko" class="lang-ko"><bdi>온다</bdi></span><br/>onda<br/>[[Annexe:Prononciation/coréen|<span class="API" title="Prononciation API">[on.da]</span>]]
| <span lang="ko" xml:lang="ko" class="lang-ko"><bdi>옵니다</bdi></span><br/>omnida<br/>[[Annexe:Prononciation/coréen|<span class="API" title="Prononciation API">[om.ni.da]</span>]]
| rowspan="2" | <span lang="ko" xml:lang="ko" class="lang-ko"><bdi>와</bdi></span><br/>wa<br/>[[Annexe:Prononciation/coréen|<span class="API" title="Prononciation API">[wa]</span>]]
| rowspan="2" | <span lang="ko" xml:lang="ko" class="lang-ko"><bdi>와요</bdi></span><br/>wayo<br/>[[Annexe:Prononciation/coréen|<span class="API" title="Prononciation API">[wa.jo̞]</span>]]
|-
! rowspan="3" | Interrogatif
| <span lang="ko" xml:lang="ko" class="lang-ko"><bdi>오느냐</bdi></span><br/>oneunya<br/>[[Annexe:Prononciation/coréen|<span class="API" title="Prononciation API">[o.nɯ.nja]</span>]]
| <span lang="ko" xml:lang="ko" class="lang-ko"><bdi>옵니까</bdi></span><br/>omnikka<br/>[[Annexe:Prononciation/coréen|<span class="API" title="Prononciation API">[om.ni.ˀka]</span>]]
|}
[[Catégorie:Conjugaison en coréen]]""",
        )
        entry = WordEntry(lang_code="ko", lang="Coréen", word="오다")
        extract_conjugation(self.wxr, entry, "Conjugaison:coréen/오다")
        self.assertEqual(
            entry.categories,
            [
                "Wiktionnaire:Sections de type avec locution forcée",
                "Conjugaison en coréen",
            ],
        )
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in entry.forms],
            [
                {
                    "form": "온다",
                    "tags": [
                        "final",
                        "formal",
                        "impolite",
                        "non-past",
                        "indicative",
                        "declarative",
                    ],
                    "roman": "onda",
                    "ipas": ["[on.da]"],
                    "source": "Conjugaison:coréen/오다",
                },
                {
                    "form": "옵니다",
                    "tags": [
                        "final",
                        "formal",
                        "polite",
                        "non-past",
                        "indicative",
                        "declarative",
                    ],
                    "roman": "omnida",
                    "ipas": ["[om.ni.da]"],
                    "source": "Conjugaison:coréen/오다",
                },
                {
                    "form": "와",
                    "tags": [
                        "final",
                        "informal",
                        "impolite",
                        "non-past",
                        "indicative",
                        "declarative",
                        "interrogative",
                    ],
                    "roman": "wa",
                    "ipas": ["[wa]"],
                    "source": "Conjugaison:coréen/오다",
                },
                {
                    "form": "와요",
                    "tags": [
                        "final",
                        "informal",
                        "polite",
                        "non-past",
                        "indicative",
                        "declarative",
                        "interrogative",
                    ],
                    "roman": "wayo",
                    "ipas": ["[wa.jo̞]"],
                    "source": "Conjugaison:coréen/오다",
                },
                {
                    "form": "오느냐",
                    "tags": [
                        "final",
                        "formal",
                        "impolite",
                        "non-past",
                        "indicative",
                        "interrogative",
                    ],
                    "roman": "oneunya",
                    "ipas": ["[o.nɯ.nja]"],
                    "source": "Conjugaison:coréen/오다",
                },
                {
                    "form": "옵니까",
                    "tags": [
                        "final",
                        "formal",
                        "polite",
                        "non-past",
                        "indicative",
                        "interrogative",
                    ],
                    "roman": "omnikka",
                    "ipas": ["[om.ni.ˀka]"],
                    "source": "Conjugaison:coréen/오다",
                },
            ],
        )

    def test_de_conj(self):
        self.wxr.wtp.start_page("trinken")
        self.wxr.wtp.add_page(
            "Conjugaison:allemand/trinken",
            116,
            "{{de-conj|trink|p2s=trink|prt=trank|part=getrunken|s2=tränk}}",
        )
        self.wxr.wtp.add_page(
            "Modèle:de-conj",
            10,
            """<h2>Verbe : [[trinken]] / Auxiliaire : [[haben]]</h2>
{|
|-
! colspan="7" | <strong>INFINITIF</strong>
|-
| &nbsp;
|-
! Présent
| rowspan="2" | &nbsp;
|-
| [[trinken]]
|}

{|
|-
! colspan="5" | <strong>IMPÉRATIF / PARTICIPE</strong>
|-
| &nbsp;
|-
! colspan="2" | Impératif
| rowspan="3" | &nbsp;
! colspan="2" | Participe
|-
| &nbsp;
| [[trink]](e)!
| &nbsp;
| présent : [[trinkend]]
|}

{|
|-
! colspan="8" | <strong>INDICATIF</strong>
|-
| &nbsp;
|-
! colspan="2" | Présent
| rowspan="7" | &nbsp;
! colspan="2" | Prétérit
| rowspan="7" | &nbsp;
! colspan="2" | Futur I
|-
| align="right" width="5%" | ich&nbsp;&nbsp;
| align="left" width="28%" | [[trinke ]]
|-
| &nbsp;
|-
! colspan="2" | Passé composé
| rowspan="7" | &nbsp;
|-
| align="right" width="5%" | ich&nbsp;&nbsp;
| align="left" width="28%" | habe getrunken
|}
[[Catégorie:Conjugaison en allemand|trinken]]""",
        )
        data = WordEntry(lang_code="de", lang="Allemand", word="trinken")
        extract_conjugation(self.wxr, data, "Conjugaison:allemand/trinken")
        self.assertEqual(
            [f.model_dump(exclude_defaults=True) for f in data.forms],
            [
                {
                    "form": "trink(e)!",
                    "tags": ["imperative"],
                    "raw_tags": ["IMPÉRATIF / PARTICIPE"],
                    "source": "Conjugaison:allemand/trinken",
                },
                {
                    "form": "trinkend",
                    "tags": ["present", "participle"],
                    "raw_tags": ["IMPÉRATIF / PARTICIPE"],
                    "source": "Conjugaison:allemand/trinken",
                },
                {
                    "form": "ich trinke",
                    "tags": ["indicative", "present"],
                    "source": "Conjugaison:allemand/trinken",
                },
                {
                    "form": "ich habe getrunken",
                    "tags": ["indicative", "past", "multiword-construction"],
                    "source": "Conjugaison:allemand/trinken",
                },
            ],
        )

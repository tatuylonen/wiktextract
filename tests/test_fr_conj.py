from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.conjugation import extract_conjugation
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestNotes(TestCase):
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
|<table>
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
|{|
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
                    "tags": ["Modes impersonnels", "Infinitif", "Présent"],
                },
                {
                    "form": "avoir lancé",
                    "ipas": ["\\a.vwaʁ lɑ̃.se\\"],
                    "source": "Conjugaison:français/lancer",
                    "tags": ["Modes impersonnels", "Infinitif", "Passé"],
                },
                {
                    "form": "je lance",
                    "ipas": ["\\ʒə lɑ̃s\\"],
                    "source": "Conjugaison:français/lancer",
                    "tags": ["Indicatif", "Présent"],
                },
                {
                    "form": "j’ai lancé",
                    "ipas": ["\\ʒ‿e lɑ̃.se\\"],
                    "source": "Conjugaison:français/lancer",
                    "tags": ["Indicatif", "Passé composé"],
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
                    "tags": ["Modes impersonnels", "Infinitif", "Présent"],
                },
                {
                    "form": "s’être abattu",
                    "ipas": ["\\s‿ɛtʁ‿a.ba.ty\\"],
                    "source": "Conjugaison:français/abattre",
                    "tags": ["Modes impersonnels", "Infinitif", "Passé"],
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
|}""",
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
                    "tags": ["Formes de base", "Imperfectif (未然形)"],
                },
                {
                    "form": "格好ではない",
                    "hiragana": "かっこうではない",
                    "roman": "kakkou dewa nai",
                    "source": "Conjugaison:japonais/格好だ",
                    "tags": ["Clefs de constructions", "Neutre négatif"],
                },
                {
                    "form": "格好じゃない",
                    "hiragana": "かっこうじゃない",
                    "roman": "kakkou ja nai",
                    "source": "Conjugaison:japonais/格好だ",
                    "tags": ["Clefs de constructions", "Neutre négatif"],
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
|}""",
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
                    "tags": ["Formes de base", "L'inaccompli"],
                },
                {
                    "form": "無い",
                    "hiragana": "ない",
                    "roman": "nai",
                    "source": "Conjugaison:japonais/在る",
                    "tags": [
                        "Formes de base",
                        "Imperfectif (未然形, mizen-kei)",
                    ],
                },
                {
                    "form": "在ります",
                    "hiragana": "あります",
                    "roman": "arimasu",
                    "source": "Conjugaison:japonais/在る",
                    "tags": [
                        "Clefs de constructions",
                        "Présent / Futur",
                        "poli",
                        "affirmatif",
                    ],
                },
                {
                    "form": "在りません",
                    "hiragana": "ありません",
                    "roman": "arimasen",
                    "source": "Conjugaison:japonais/在る",
                    "tags": [
                        "Clefs de constructions",
                        "Présent / Futur",
                        "poli",
                        "négatif",
                    ],
                },
            ],
        )

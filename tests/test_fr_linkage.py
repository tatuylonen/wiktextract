from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.linkage import extract_linkage
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.extractor.fr.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestFrLinkage(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"),
            WiktionaryConfig(
                dump_file_lang_code="fr",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_location_tags(self):
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:Canada", 10, body="(Canada)")
        self.wxr.wtp.add_page("Modèle:Louisiane", 10, body="(Louisiane)")
        root = self.wxr.wtp.parse(
            "* [[bon matin]] {{Canada|nocat=1}} {{Louisiane|nocat=1}}"
        )
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            page_data[-1].synonyms[0].model_dump(exclude_defaults=True),
            {"word": "bon matin", "raw_tags": ["Canada", "Louisiane"]},
        )

    def test_zh_synonyms(self):
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("你好")
        root = self.wxr.wtp.parse(
            "* {{zh-lien|你们好|nǐmen hǎo|你們好}} — Bonjour (au pluriel)."
        )
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            page_data[-1].synonyms[0].model_dump(exclude_defaults=True),
            {
                "word": "你们好",
                "roman": "nǐmen hǎo",
                "alt": "你們好",
                "translation": "Bonjour (au pluriel).",
            },
        )

    def test_template_as_partial_tag(self):
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:lien", 10, body="kwei")
        self.wxr.wtp.add_page("Modèle:Canada", 10, body="(Canada)")
        self.wxr.wtp.add_page("Modèle:L", 10, body="Atikamekw")
        root = self.wxr.wtp.parse(
            "* {{lien|kwei|fr}} {{Canada|nocat=1}} (mot {{L|atj}})"
        )
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            page_data[-1].synonyms[0].model_dump(exclude_defaults=True),
            {"word": "kwei", "raw_tags": ["Canada", "mot Atikamekw"]},
        )

    def test_list_item_has_two_words(self):
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("masse")
        root = self.wxr.wtp.parse(
            "* [[être à la masse]], [[mettre à la masse]]"
        )
        extract_linkage(self.wxr, page_data, root, "dérivés")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].derived
            ],
            [{"word": "être à la masse"}, {"word": "mettre à la masse"}],
        )

    def test_sub_list(self):
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("lézard ocellé")
        root = self.wxr.wtp.parse(
            """* [[saurien]]s (Sauria)
** [[lacertidé]]s (Lacertidae) (famille des lézards typiques)
"""
        )
        extract_linkage(self.wxr, page_data, root, "hyper")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].hypernyms
            ],
            [
                {"raw_tags": ["Sauria"], "word": "sauriens"},
                {
                    "raw_tags": [
                        "Lacertidae",
                        "famille des lézards typiques",
                    ],
                    "word": "lacertidés",
                },
            ],
        )

    def test_sense(self):
        # https://fr.wiktionary.org/wiki/autrice
        # https://fr.wiktionary.org/wiki/embouteillage
        page_data = [WordEntry(word="autrice", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("autrice")
        root = self.wxr.wtp.parse(
            """{{(|Celle qui est à l’origine de quelque chose|1}}
* [[artisane]]

; Mise en bouteille (sens 1)
* [[bouchonnerie]]
"""
        )
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].synonyms
            ],
            [
                {
                    "word": "artisane",
                    "sense": "Celle qui est à l’origine de quelque chose",
                    "sense_index": 1,
                },
                {
                    "word": "bouchonnerie",
                    "sense": "Mise en bouteille",
                    "sense_index": 1,
                },
            ],
        )

    def test_words_divided_by_slash(self):
        page_data = [WordEntry(word="test", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("eau")
        root = self.wxr.wtp.parse("* [[benoîte d’eau]] / [[benoite d’eau]]")
        extract_linkage(self.wxr, page_data, root, "dérivés")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].derived
            ],
            [{"word": "benoîte d’eau"}, {"word": "benoite d’eau"}],
        )

    def test_sense_index_str(self):
        page_data = [WordEntry(word="-er", lang_code="fr", lang="Néerlandais")]
        self.wxr.wtp.start_page("-er")
        root = self.wxr.wtp.parse("* [[-aar]] (1)")
        extract_linkage(self.wxr, page_data, root, "paronymes")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].paronyms
            ],
            [{"word": "-aar", "sense_index": 1}],
        )

    def test_italic_sense_node(self):
        self.wxr.wtp.add_page("Modèle:lien", 10, body="{{{1}}}")
        page_data = [WordEntry(word="-er", lang_code="en", lang="Anglais")]
        self.wxr.wtp.start_page("-er")
        root = self.wxr.wtp.parse(
            "* {{lien|more|en}} ''(selon les adjectifs)''"
        )
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].synonyms
            ],
            [{"word": "more", "sense": "selon les adjectifs"}],
        )

    def test_no_linkage_empty_tag(self):
        page_data = [WordEntry(word="gambo", lang_code="eo", lang="Espéranto")]
        self.wxr.wtp.start_page("gambo")
        root = self.wxr.wtp.parse("* [[korpo]] ( ''[[corps]]'' )")
        extract_linkage(self.wxr, page_data, root, "holonymes")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].holonyms
            ],
            [{"word": "korpo", "raw_tags": ["corps"]}],
        )

    def test_italic_number_sense(self):
        page_data = [WordEntry(word="gigabit", lang_code="en", lang="Anglais")]
        self.wxr.wtp.start_page("gigabit")
        root = self.wxr.wtp.parse("* (''10<sup>9</sup>'') [[Gb]]")
        extract_linkage(self.wxr, page_data, root, "variantes orthographiques")
        self.assertEqual(
            [d.model_dump(exclude_defaults=True) for d in page_data[-1].forms],
            [{"form": "Gb", "raw_tags": ["10⁹"]}],
        )

    def test_linkage_tags(self):
        page_data = [WordEntry(word="autrice", lang_code="fr", lang="Français")]
        self.wxr.wtp.add_page("Modèle:désuet", 10, body="(Désuet)")
        self.wxr.wtp.add_page("Modèle:anglicisme", 10, body="(Anglicisme)")
        self.wxr.wtp.start_page("autrice")
        root = self.wxr.wtp.parse(
            "* [[authoress]] {{désuet|nocat=1}} {{anglicisme|nocat=1}}"
        )
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].synonyms
            ],
            [
                {"word": "authoress", "tags": ["obsolete", "Anglicism"]},
            ],
        )

    def test_alcool(self):
        page_data = [WordEntry(word="alcool", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("alcool")
        root = self.wxr.wtp.parse(
            """* [[alcoolodépendance]] (ou [[alcoolo-dépendance]])
* [[syndrome alcoolo-fœtal]] ([[SAF]])"""
        )
        extract_linkage(self.wxr, page_data, root, "dérivés")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].derived
            ],
            [
                {"word": "alcoolodépendance"},
                {"word": "alcoolo-dépendance"},
                {"word": "syndrome alcoolo-fœtal", "raw_tags": ["SAF"]},
            ],
        )

    def test_italic_word(self):
        page_data = [
            WordEntry(
                word="Sus scrofa scrofa",
                lang_code="conv",
                lang="Conventions internationales",
            )
        ]
        self.wxr.wtp.start_page("Sus scrofa scrofa")
        root = self.wxr.wtp.parse("* ''[[Sus scrofa anglicus]]''")
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].synonyms
            ],
            [{"word": "Sus scrofa anglicus"}],
        )

    def test_réf_template(self):
        page_data = [WordEntry(word="chien", lang_code="fr", lang="Français")]
        self.wxr.wtp.start_page("chien")
        root = self.wxr.wtp.parse(
            "* [[battre le chien devant le lion]] : Châtier le faible devant le fort pour une faute que l’un ou l’autre a commise{{réf}}"
        )
        extract_linkage(self.wxr, page_data, root, "dérivés")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].derived
            ],
            [
                {
                    "word": "battre le chien devant le lion",
                    "sense": "Châtier le faible devant le fort pour une faute que l’un ou l’autre a commise",
                }
            ],
        )

    def test_zh_lien_link_tr(self):
        page_data = [WordEntry(word="狗", lang_code="zh", lang="Chinois")]
        self.wxr.wtp.start_page("狗")
        root = self.wxr.wtp.parse(
            "* {{zh-lien|饿狗|ègǒu}} — [[chien]] [[affamé]]"
        )
        extract_linkage(self.wxr, page_data, root, "dérivés")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].derived
            ],
            [{"word": "饿狗", "roman": "ègǒu", "translation": "chien affamé"}],
        )

    def test_voir_anagrammes(self):
        page_data = [
            WordEntry(
                word="chien",
                lang_code="fr",
                lang="Français",
            )
        ]
        self.wxr.wtp.add_page(
            "Modèle:voir anagrammes",
            10,
            """→ [[Spécial:EditPage|Modifier]]<div class="boite">
<div >
<div >
<div>
* [[niche#fr|niche]], [[niché#fr|niché]]
</div></div><div></div></div></div>""",
        )
        self.wxr.wtp.start_page("chien")
        root = self.wxr.wtp.parse("{{voir anagrammes|fr}}")
        extract_linkage(self.wxr, page_data, root, "anagrammes")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].anagrams
            ],
            [{"word": "niche"}, {"word": "niché"}],
        )

    def test_bold_sense(self):
        data = parse_page(
            self.wxr,
            "autochtone",
            """== {{langue|fr}} ==
=== {{S|adjectif|fr}} ===
# Qui
==== {{S|synonymes}} ====
'''se dit d’une espèce végétale ou animale'''
* [[endémique]]""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "word": "endémique",
                    "sense": "se dit d’une espèce végétale ou animale",
                }
            ],
        )

    def test_double_italic_tags(self):
        data = parse_page(
            self.wxr,
            "autochtone",
            """== {{langue|fr}} ==
=== {{S|nom|fr}} ===
# Personne
==== {{S|synonymes}} ====
* [[Peau-Rouge]] (''Désuet'') (''Injurieux'')""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [{"word": "Peau-Rouge", "tags": ["obsolete", "offensive"]}],
        )

    def test_italic_sense(self):
        data = parse_page(
            self.wxr,
            "car",
            """== {{langue|en}} ==
=== {{S|nom|en|num=1}} ===
# [[voiture|Voiture]].
==== {{S|synonymes}} ====
''Automobile'' :
* {{lien|automobile|en}}""",
        )
        self.assertEqual(
            data[0]["synonyms"], [{"word": "automobile", "sense": "Automobile"}]
        )

    def test_ignore_cf_template(self):
        data = parse_page(
            self.wxr,
            "throne",
            """== {{langue|en}} ==
=== {{S|nom|en}} ===
# [[trône|Trône]]
==== {{S|synonymes}} ====
''Siège de toilettes :''
* {{cf}} [[toilet#Synonymes|''toilet'' (synonymes)]]""",
        )
        self.assertTrue("synonyms" not in data[0])

    def test_zh_l(self):
        self.wxr.wtp.add_page("Modèle:L", 10, "Chinois")
        self.wxr.wtp.add_page(
            "Modèle:zh-l",
            10,
            """<span class="Hani" lang="zh">[[圖書#zh|圖書]]</span>／<span class="Hani" lang="zh">[[图书#zh|图书]]</span> (<i><span class="tr Latn">túshū</span></i>, « [[livre]]s, [[documents]] »)""",
        )
        data = parse_page(
            self.wxr,
            "書籍",
            """== {{langue|zh}} ==
=== {{S|nom|zh}} ===
# [[livre|Livre]], [[ouvrage]], [[documentation]].
==== {{S|synonymes}} ====
* {{zh-l|圖書|túshū|[[livre]]s, [[documents]]}}""",
        )
        self.assertEqual(
            data[0]["synonyms"],
            [
                {
                    "roman": "túshū",
                    "sense": "livres, documents",
                    "tags": ["Traditional-Chinese"],
                    "word": "圖書",
                },
                {
                    "roman": "túshū",
                    "sense": "livres, documents",
                    "tags": ["Simplified-Chinese"],
                    "word": "图书",
                },
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.linkage import extract_linkage
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.wxr_context import WiktextractContext


class TestLinkage(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_tags(self):
        page_data = [
            WordEntry(word="test", lang_code="fr", lang_name="Français")
        ]
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:Canada", 10, body="(Canada)")
        self.wxr.wtp.add_page("Modèle:Louisiane", 10, body="(Louisiane)")
        root = self.wxr.wtp.parse(
            "* [[bon matin]] {{Canada|nocat=1}} {{Louisiane|nocat=1}}"
        )
        extract_linkage(self.wxr, page_data, root, "synonymes")
        self.assertEqual(
            page_data[-1].synonyms[0].model_dump(exclude_defaults=True),
            {"word": "bon matin", "tags": ["Canada", "Louisiane"]},
        )

    def test_zh_synonyms(self):
        page_data = [
            WordEntry(word="test", lang_code="fr", lang_name="Français")
        ]
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
        page_data = [
            WordEntry(word="test", lang_code="fr", lang_name="Français")
        ]
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
            {"word": "kwei", "tags": ["Canada", "mot Atikamekw"]},
        )

    def test_list_item_has_two_words(self):
        page_data = [
            WordEntry(word="test", lang_code="fr", lang_name="Français")
        ]
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
            [
                {"word": "être à la masse"},
                {"word": "mettre à la masse"},
            ],
        )

    def test_sub_list(self):
        page_data = [
            WordEntry(word="test", lang_code="fr", lang_name="Français")
        ]
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
                {"tags": ["Sauria"], "word": "sauriens"},
                {
                    "tags": [
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
        page_data = [
            WordEntry(word="autrice", lang_code="fr", lang_name="Français")
        ]
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

    def test_derives_autres_langues_section(self):
        # https://fr.wiktionary.org/wiki/eau#Dérivés_dans_d’autres_langues
        # https://fr.wiktionary.org/wiki/caligineux#Dérivés_dans_d’autres_langues
        self.wxr.wtp.add_page("Modèle:lien", 10, body="{{{1}}}")
        self.wxr.wtp.add_page(
            "Modèle:L",
            10,
            body="""{{#switch: {{{1}}}
| kmv = Karipúna
| en = Anglais
}}""",
        )
        page_data = [
            WordEntry(word="test", lang_code="fr", lang_name="Français")
        ]
        self.wxr.wtp.start_page("eau")
        root = self.wxr.wtp.parse(
            """* {{L|kmv}} : {{lien|dlo|kmv}}, {{lien|djilo|kmv}}
* {{L|en}} : [[caliginous#en|caliginous]]"""
        )
        extract_linkage(self.wxr, page_data, root, "dérivés autres langues")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].derived
            ],
            [
                {
                    "word": "dlo",
                    "lang_code": "kmv",
                    "lang_name": "Karipúna",
                },
                {
                    "word": "djilo",
                    "lang_code": "kmv",
                    "lang_name": "Karipúna",
                },
                {
                    "word": "caliginous",
                    "lang_code": "en",
                    "lang_name": "Anglais",
                },
            ],
        )

    def test_words_divided_by_slash(self):
        page_data = [
            WordEntry(word="test", lang_code="fr", lang_name="Français")
        ]
        self.wxr.wtp.start_page("eau")
        root = self.wxr.wtp.parse("* [[benoîte d’eau]] / [[benoite d’eau]]")
        extract_linkage(self.wxr, page_data, root, "dérivés")
        self.assertEqual(
            [
                d.model_dump(exclude_defaults=True)
                for d in page_data[-1].derived
            ],
            [
                {"word": "benoîte d’eau"},
                {"word": "benoite d’eau"},
            ],
        )

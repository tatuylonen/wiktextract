from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.models import WordEntry
from wiktextract.extractor.fr.translation import extract_translation
from wiktextract.wxr_context import WiktextractContext


class TestTranslation(TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_italic_tag(self):
        # https://fr.wiktionary.org/wiki/bonjour
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Albanais")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{trad-début|Formule pour saluer}}\n* {{T|sq}} : {{trad+|sq|mirëdita}}, {{trad-|sq|mirë mëngjes}} ''(le matin)''"
        )
        base_data = WordEntry(word="bonjour", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(
            page_data[-1].model_dump(exclude_defaults=True),
            {
                "word": "bonjour",
                "lang_code": "fr",
                "lang": "Français",
                "translations": [
                    {
                        "lang_code": "sq",
                        "lang": "Albanais",
                        "word": "mirëdita",
                        "sense": "Formule pour saluer",
                    },
                    {
                        "lang_code": "sq",
                        "lang": "Albanais",
                        "word": "mirë mëngjes",
                        "sense": "Formule pour saluer",
                        "raw_tags": ["le matin"],
                    },
                ],
            },
        )

    def test_template_tag(self):
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Arabe")
        self.wxr.wtp.add_page("Modèle:transliterator", 10, body="mrḥbā")
        self.wxr.wtp.add_page("Modèle:informel", 10, body="(Informel)")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{T|ar}} : {{trad+|ar|مرحبا|dif=مرحبًا|tr={{transliterator|ar|مرحبا}}}} {{informel|nocat=1}}"
        )
        base_data = WordEntry(word="bonjour", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(
            page_data[-1].model_dump(exclude_defaults=True),
            {
                "word": "bonjour",
                "lang_code": "fr",
                "lang": "Français",
                "translations": [
                    {
                        "lang_code": "ar",
                        "lang": "Arabe",
                        "word": "مرحبًا",
                        "roman": "mrḥbā",
                        "raw_tags": ["Informel"],
                    },
                ],
            },
        )

    def test_traditional_writing(self):
        self.wxr.wtp.start_page("bonjour")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Mongol")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{T|mn}} : {{trad+|mn|сайн байна уу|tr=sain baina uu|tradi=ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨ᠎ᠠ ᠤᠤ}}"
        )
        base_data = WordEntry(word="bonjour", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(
            page_data[-1].model_dump(exclude_defaults=True),
            {
                "word": "bonjour",
                "lang_code": "fr",
                "lang": "Français",
                "translations": [
                    {
                        "lang_code": "mn",
                        "lang": "Mongol",
                        "word": "сайн байна уу",
                        "roman": "sain baina uu",
                        "traditional_writing": "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨ᠎ᠠ ᠤᠤ",
                    },
                ],
            },
        )

    def test_trad_template_gender_parameter(self):
        # https://fr.wiktionary.org/wiki/cambium
        self.wxr.wtp.start_page("cambium")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Allemand")
        self.wxr.wtp.add_page("Modèle:trad", 10, body="''neutre''")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{T|de}} : {{trad|de|Kambium|n}}"
        )
        base_data = WordEntry(word="cambium", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(
            page_data[-1].model_dump(exclude_defaults=True),
            {
                "word": "cambium",
                "lang_code": "fr",
                "lang": "Français",
                "translations": [
                    {
                        "lang_code": "de",
                        "lang": "Allemand",
                        "word": "Kambium",
                        "raw_tags": ["neutre"],
                    },
                ],
            },
        )

    def test_template_sense_parameter(self):
        self.wxr.wtp.start_page("masse")
        self.wxr.wtp.add_page("Modèle:S", 10, "{{{1}}}")
        self.wxr.wtp.add_page("Modèle:info lex", 10, "(Finance)")
        self.wxr.wtp.add_page(
            "Modèle:T",
            10,
            """{{#switch: {{{1}}}
| hr = Croate
| af = Afrikaans
}}""",
        )
        self.wxr.wtp.add_page("Modèle:trad+", 10, "masa")
        root = self.wxr.wtp.parse(
            """==== {{S|traductions}} ====
{{trad-début|{{info lex|finance}}|12}}
* {{T|hr}} : {{trad+|hr|masa}}
{{trad-fin}}

===== {{S|traductions à trier}} =====
* {{T|af|trier}} : {{trad+|af|massa}}"""
        )
        base_data = WordEntry(word="masse", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root.children[0])
        self.assertEqual(
            page_data[-1].model_dump(exclude_defaults=True),
            {
                "word": "masse",
                "lang_code": "fr",
                "lang": "Français",
                "translations": [
                    {
                        "lang_code": "hr",
                        "lang": "Croate",
                        "word": "masa",
                        "sense": "(Finance)",
                        "sense_index": 12,
                    },
                    {
                        "lang_code": "af",
                        "lang": "Afrikaans",
                        "word": "massa",
                    },
                ],
            },
        )

    def test_translation_list_without_t_template(self):
        self.wxr.wtp.start_page("medium")
        root = self.wxr.wtp.parse("* Anglais : {{trad+|en|MDF}}")
        base_data = WordEntry(word="medium", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root)
        self.assertEqual(
            [
                t.model_dump(exclude_defaults=True)
                for t in page_data[-1].translations
            ],
            [
                {
                    "lang_code": "en",
                    "lang": "Anglais",
                    "word": "MDF",
                }
            ],
        )

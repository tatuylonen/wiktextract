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
                        "tags": ["informal"],
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
                        "tags": ["neuter"],
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

    def test_ja_ruby(self):
        self.wxr.wtp.start_page("autrice")
        self.wxr.wtp.add_page("Modèle:T", 10, "Japonais")
        self.wxr.wtp.add_page(
            "Modèle:Lang",
            10,
            """<span lang="ja"><bdi><ruby>女作者<rp> (</rp><rt>おんな さくしゃ</rt><rp>) </rp></ruby></bdi></span>""",
        )
        root = self.wxr.wtp.parse(
            "* {{T|ja}} : {{trad-|ja|女作者|dif={{Lang|ja|{{ruby|女作者|おんな さくしゃ}}}}|tr=onna sakusha}}"
        )
        base_data = WordEntry(word="autrice", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root)
        self.assertEqual(
            [
                t.model_dump(exclude_defaults=True)
                for t in page_data[-1].translations
            ],
            [
                {
                    "lang": "Japonais",
                    "lang_code": "ja",
                    "roman": "onna sakusha",
                    "ruby": [("女作者", "おんな さくしゃ")],
                    "word": "女作者",
                }
            ],
        )

    def test_cf_template(self):
        # cf template shouldn't be added as tag to the previous tr data
        self.wxr.wtp.start_page("marron")
        self.wxr.wtp.add_page("Modèle:T", 10, "Norvégien (bokmål)")
        root = self.wxr.wtp.parse(
            """{{trad-début|Coup de poing|3}}
* {{T|nb}} : {{trad-|nb|knyttneveslag|n}}
{{trad-fin}}

{{trad-début|Marron d’Inde|4}}
* {{cf|marron d’Inde}}
{{trad-fin}}"""
        )
        base_data = WordEntry(word="marron", lang_code="fr", lang="Français")
        page_data = [base_data.model_copy(deep=True)]
        extract_translation(self.wxr, page_data, base_data, root)
        self.assertEqual(
            [
                t.model_dump(exclude_defaults=True)
                for t in page_data[-1].translations
            ],
            [
                {
                    "lang": "Norvégien (bokmål)",
                    "lang_code": "nb",
                    "sense": "Coup de poing",
                    "sense_index": 3,
                    "tags": ["neuter"],
                    "word": "knyttneveslag",
                }
            ],
        )

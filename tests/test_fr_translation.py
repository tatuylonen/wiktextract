import unittest
from collections import defaultdict

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.fr.translation import extract_translation
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class TestTranslation(unittest.TestCase):
    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="fr"), WiktionaryConfig(dump_file_lang_code="fr")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_italic_tag(self):
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Albanais")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{trad-début|Formule pour saluer}}\n* {{T|sq}} : {{trad+|sq|mirëdita}}, {{trad-|sq|mirë mëngjes}} ''(le matin)''"
        )
        page_data = [defaultdict(list)]
        extract_translation(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data,
            [
                {
                    "translations": [
                        {
                            "code": "sq",
                            "lang": "Albanais",
                            "word": "mirëdita",
                            "sense": "Formule pour saluer",
                        },
                        {
                            "code": "sq",
                            "lang": "Albanais",
                            "word": "mirë mëngjes",
                            "sense": "Formule pour saluer",
                            "tags": ["le matin"],
                        },
                    ]
                }
            ],
        )

    def test_template_tag(self):
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Arabe")
        self.wxr.wtp.add_page("Modèle:transliterator", 10, body="mrḥbā")
        self.wxr.wtp.add_page("Modèle:informel", 10, body="(Informel)")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{T|ar}} : {{trad+|ar|مرحبا|dif=مرحبًا|tr={{transliterator|ar|مرحبا}}}} {{informel|nocat=1}}"
        )
        page_data = [defaultdict(list)]
        extract_translation(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data,
            [
                {
                    "translations": [
                        {
                            "code": "ar",
                            "lang": "Arabe",
                            "word": "مرحبا",
                            "roman": "mrḥbā",
                            "tags": ["Informel"],
                        },
                    ]
                }
            ],
        )

    def test_traditional_writing(self):
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Mongol")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{T|mn}} : {{trad+|mn|сайн байна уу|tr=sain baina uu|tradi=ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨ᠎ᠠ ᠤᠤ}}"
        )
        page_data = [defaultdict(list)]
        extract_translation(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data,
            [
                {
                    "translations": [
                        {
                            "code": "mn",
                            "lang": "Mongol",
                            "word": "сайн байна уу",
                            "roman": "sain baina uu",
                            "traditional_writing": "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨ᠎ᠠ ᠤᠤ",
                        },
                    ]
                }
            ],
        )

    def test_trad_template_gender_parameter(self):
        self.wxr.wtp.start_page("")
        self.wxr.wtp.add_page("Modèle:T", 10, body="Allemand")
        self.wxr.wtp.add_page("Modèle:trad", 10, body="''neutre''")
        root = self.wxr.wtp.parse(
            "=== Traductions ===\n* {{T|de}} : {{trad|de|Kambium|n}}"
        )
        page_data = [defaultdict(list)]
        extract_translation(self.wxr, page_data, root.children[0])
        self.assertEqual(
            page_data,
            [
                {
                    "translations": [
                        {
                            "code": "de",
                            "lang": "Allemand",
                            "word": "Kambium",
                            "tags": ["neutre"],
                        },
                    ]
                }
            ],
        )

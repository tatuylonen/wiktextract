import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.models import WordEntry
from wiktextract.extractor.de.translation import extract_translation
from wiktextract.wxr_context import WiktextractContext


class TestDETranslation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"), WiktionaryConfig(dump_file_lang_code="de")
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_nest_list(self):
        self.wxr.wtp.add_page("Vorlage:zh-tw", 10, "Chinesisch (traditionell)")
        self.wxr.wtp.add_page("Vorlage:zh-cn", 10, "Chinesisch (vereinfacht)")
        self.wxr.wtp.start_page("Brot")
        root = self.wxr.wtp.parse("""{{Ü-Tabelle|1|G=kein Plural|Ü-Liste=
*{{zh}}:
**{{zh-tw}}: {{Üt|zh|麵包|miànbāo}}
**{{zh-cn}}: {{Üt|zh|面包|miànbāo}}
}}""")
        word_entry = WordEntry(lang="Deutsch", lang_code="de", word="Brot")
        extract_translation(self.wxr, word_entry, root)
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["translations"],
            [
                {
                    "lang_code": "zh-tw",
                    "lang": "Chinesisch (traditionell)",
                    "word": "麵包",
                    "roman": "miànbāo",
                    "sense": "kein Plural",
                    "sense_id": "1",
                },
                {
                    "lang_code": "zh-cn",
                    "lang": "Chinesisch (vereinfacht)",
                    "word": "面包",
                    "roman": "miànbāo",
                    "sense": "kein Plural",
                    "sense_id": "1",
                },
            ],
        )

    def test_tag(self):
        self.wxr.wtp.add_page("Vorlage:el", 10, "Griechisch (Neu-)")
        self.wxr.wtp.add_page("Vorlage:n", 10, "n")
        self.wxr.wtp.add_page("Vorlage:m", 10, "m")
        self.wxr.wtp.start_page("Brot")
        root = self.wxr.wtp.parse("""{{Ü-Tabelle|Ü-Liste=
*{{el}}: {{Üt|el|ψωμί|psomí}} {{n}}, ''antiquiert, kirchensprachlich:'' {{Üt|el|άρτος|ártos}} {{m}}
}}""")
        word_entry = WordEntry(lang="Deutsch", lang_code="de", word="Brot")
        extract_translation(self.wxr, word_entry, root)
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["translations"],
            [
                {
                    "lang_code": "el",
                    "lang": "Griechisch (Neu-)",
                    "word": "ψωμί",
                    "roman": "psomí",
                    "tags": ["neuter"],
                },
                {
                    "lang_code": "el",
                    "lang": "Griechisch (Neu-)",
                    "word": "άρτος",
                    "roman": "ártos",
                    "tags": ["masculine"],
                    "raw_tags": ["antiquiert", "kirchensprachlich"],
                },
            ],
        )

    def test_non_template_lang_name(self):
        self.wxr.wtp.add_page("Vorlage:el", 10, "Griechisch (Neu-)")
        self.wxr.wtp.add_page("Vorlage:n", 10, "n")
        self.wxr.wtp.add_page("Vorlage:m", 10, "m")
        self.wxr.wtp.start_page("Brot")
        root = self.wxr.wtp.parse("""{{Ü-Tabelle|Dialekttabelle=
*Kölsch: [?] {{Ü|ksh|Brut}}
*[[Niederpreußisch]]: [?] {{Ü|nds|Brot}}
}}""")
        word_entry = WordEntry(lang="Deutsch", lang_code="de", word="Brot")
        extract_translation(self.wxr, word_entry, root)
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["translations"],
            [
                {"lang_code": "ksh", "lang": "Kölsch", "word": "Brut"},
                {"lang_code": "nds", "lang": "Niederpreußisch", "word": "Brot"},
            ],
        )

    def test_ut_auto_roman(self):
        self.wxr.wtp.add_page("Vorlage:grc", 10, "Altgriechisch")
        self.wxr.wtp.add_page(
            "Vorlage:Üt",
            10,
            '<span lang="grc" xml:lang="grc">ἄρτος</span>&nbsp;(artos[[Wiktionary:Altgriechisch/Umschrift|<sup>☆</sup>]])&nbsp;<sup>→&nbsp;grc</sup>',
        )
        self.wxr.wtp.start_page("Brot")
        root = self.wxr.wtp.parse("""{{Ü-Tabelle|Dialekttabelle=
*{{grc}}: {{Üt|grc|ἄρτος}}
}}""")
        word_entry = WordEntry(lang="Deutsch", lang_code="de", word="Brot")
        extract_translation(self.wxr, word_entry, root)
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["translations"],
            [
                {
                    "lang_code": "grc",
                    "lang": "Altgriechisch",
                    "word": "ἄρτος",
                    "roman": "artos",
                }
            ],
        )

    # low quality or old format pages:
    # plain text tag: https://de.wiktionary.org/wiki/Bein
    # sense id before word: https://de.wiktionary.org/wiki/Beitrag

    def test_empty_translation(self):
        self.wxr.wtp.start_page("AM")
        word_entry = WordEntry(word="AM", lang="English", lang_code="en")
        root = self.wxr.wtp.parse(
            """==== {{Übersetzungen}} ====
{{Ü-Tabelle|Ü-Liste=
*{{fr}}: [1] {{Ü|fr|}}
}}"""
        )
        extract_translation(self.wxr, word_entry, root)
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True),
            {"word": "AM", "lang": "English", "lang_code": "en"},
        )

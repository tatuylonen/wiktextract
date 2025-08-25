import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.models import WordEntry
from wiktextract.extractor.de.page import parse_page
from wiktextract.extractor.de.translation import extract_translation
from wiktextract.wxr_context import WiktextractContext


class TestDETranslation(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de", capture_language_codes=None
            ),
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
                    "sense_index": "1",
                },
                {
                    "lang_code": "zh-cn",
                    "lang": "Chinesisch (vereinfacht)",
                    "word": "面包",
                    "roman": "miànbāo",
                    "sense": "kein Plural",
                    "sense_index": "1",
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
}}""")  # noqa: E501
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

    def test_wikinode_in_g_arguemnt(self):
        self.wxr.wtp.add_page("Vorlage:fr", 10, "Französisch")
        self.wxr.wtp.add_page(
            "Vorlage:Üt",
            10,
            '<span lang="grc" xml:lang="grc">ἄρτος</span>&nbsp;(artos[[Wiktionary:Altgriechisch/Umschrift|<sup>☆</sup>]])&nbsp;<sup>→&nbsp;grc</sup>',
        )
        self.wxr.wtp.start_page("Brot")
        root = self.wxr.wtp.parse("""{{Ü-Tabelle|1|G=[[Mitglied]] einer [[Gruppe]] von [[Person]]en sein|Ü-Liste=
*{{fr}}: {{Ü|fr|appartenir}}
}}""")  # noqa: E501
        word_entry = WordEntry(
            lang="Deutsch", lang_code="de", word="dazugehören"
        )
        extract_translation(self.wxr, word_entry, root)
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["translations"],
            [
                {
                    "lang_code": "fr",
                    "lang": "Französisch",
                    "word": "appartenir",
                    "sense": "Mitglied einer Gruppe von Personen sein",
                    "sense_index": "1",
                }
            ],
        )

    def test_semicolon(self):
        self.wxr.wtp.add_page("Vorlage:es", 10, "[[Spanisch]]")
        self.wxr.wtp.add_page(
            "Vorlage:Üt",
            10,
            '<span lang="es" xml:lang="es">{{{2}}}</span>&nbsp;[[:es:Special:Search/machete|<sup class="dewikttm">→&nbsp;es</sup>]][[Kategorie:Übersetzungen (Spanisch)]]',
        )
        data = parse_page(
            self.wxr,
            "Machete",
            """== Machete ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{fm}} ===
====Bedeutungen====
:[1] {{K|Waffe|Werkzeug}} [[Messer]] zur [[Ernte]]
==== Übersetzungen ====
{{Ü-Tabelle|1|G=Waffe, Werkzeug|Ü-Liste=
*{{es}}: {{Ü|es|machete}}; ''Nicaragua:'' {{Ü|es|paila}}
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "Spanisch",
                    "lang_code": "es",
                    "sense": "Waffe, Werkzeug",
                    "sense_index": "1",
                    "word": "machete",
                },
                {
                    "lang": "Spanisch",
                    "lang_code": "es",
                    "raw_tags": ["Nicaragua"],
                    "sense": "Waffe, Werkzeug",
                    "sense_index": "1",
                    "word": "paila",
                },
            ],
        )

    def test_hiragana(self):
        self.wxr.wtp.add_page("Vorlage:ja", 10, "[[Japanisch]]")
        data = parse_page(
            self.wxr,
            "Zeichen",
            """== Zeichen ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{n}} ===
====Bedeutungen====
:[1] etwas
==== Übersetzungen ====
{{Ü-Tabelle|1|G=etwas|Ü-Liste=
*{{ja}}: {{Üt|ja|合図|あいず, aizu}}
}}""",
        )
        self.assertEqual(
            data[0]["translations"],
            [
                {
                    "lang": "Japanisch",
                    "lang_code": "ja",
                    "word": "合図",
                    "other": "あいず",
                    "roman": "aizu",
                    "sense": "etwas",
                    "sense_index": "1",
                }
            ],
        )

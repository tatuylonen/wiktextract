from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.de.form import extracrt_form_section
from wiktextract.extractor.de.inflection import extract_inf_table_template
from wiktextract.extractor.de.models import WordEntry
from wiktextract.extractor.de.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestDeForms(TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="de"),
            WiktionaryConfig(
                dump_file_lang_code="de", capture_language_codes=None
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_noun_table(self):
        self.wxr.wtp.start_page("Wörterbuch")
        self.wxr.wtp.add_page(
            "Vorlage:Deutsch Substantiv Übersicht",
            10,
            """{|
! style="width: 65px;" |
! [[Hilfe:Singular|Singular]]
! [[Hilfe:Plural|Plural]]
|-
! style="text-align:left;" | [[Hilfe:Genitiv|Genitiv]]
| des [[Wörterbuches|Wörterbuches]]<br />des [[Wörterbuchs|Wörterbuchs]]
| der [[Wörterbücher|Wörterbücher]]
|}""",
        )
        root = self.wxr.wtp.parse("{{Deutsch Substantiv Übersicht}}")
        word_entry = WordEntry(
            word="Wörterbuch", lang="Deutsch", lang_code="de"
        )
        extract_inf_table_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "des Wörterbuches", "tags": ["genitive", "singular"]},
                {"form": "des Wörterbuchs", "tags": ["genitive", "singular"]},
                {"form": "der Wörterbücher", "tags": ["genitive", "plural"]},
            ],
        )

    def test_adj_flexion_page(self):
        self.wxr.wtp.start_page("arm")
        self.wxr.wtp.add_page(
            "Vorlage:Deutsch Adjektiv Übersicht",
            10,
            """{|
! [[Hilfe:Positiv|Positiv]]
! [[Hilfe:Komparativ|Komparativ]]
! [[Hilfe:Superlativ|Superlativ]]
|- align="center"
| arm
| [[ärmer|ärmer]]
| am&#32;[[ärmsten|ärmsten]]
|-
! colspan="5" | ''All other forms:'' [[Flexion:arm|Flexion:arm]]
|}""",
        )
        self.wxr.wtp.add_page(
            "Flexion:arm",
            108,
            """== arm (Deklination) ({{Adjektivdeklination|Deutsch}}) ==
{{Deklinationsseite Adjektiv
|Positiv-Stamm=arm
|Komparativ-Stamm=ärmer
|Superlativ-Stamm=ärmst
}}""",
        )
        self.wxr.wtp.add_page(
            "Vorlage:Deklinationsseite Adjektiv",
            10,
            """<h4>[[Hilfe:Positiv|Positiv]]</h4>
{|
! colspan="9" | [[Hilfe:Deklination|Schwache Deklination]]
|-
! rowspan="3" |
! colspan="6" | [[Hilfe:Singular|Singular]]
! colspan="2" | [[Hilfe:Plural|Plural]]
|-
! colspan="2" | [[Hilfe:Maskulinum|Maskulinum]]
! colspan="2" | [[Hilfe:Femininum|Femininum]]
! colspan="2" | [[Hilfe:Neutrum|Neutrum]]
! colspan="2" | —
|-
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
! [[Hilfe:Artikel|Artikel]]
! [[Hilfe:Wortform|Wortform]]
|-
! [[Hilfe:Nominativ|Nominativ]]
| der
| [[arme]]
| die
| [[arme]]
| das
| [[arme]]
| die
| [[armen]]
|-
! colspan="9" | [[Hilfe:Prädikativ|Prädikativ]]
|-
! rowspan="3" |
! colspan="6" | [[Hilfe:Singular|Singular]]
! colspan="2" | [[Hilfe:Plural|Plural]]
|-
! colspan="2" | [[Hilfe:Maskulinum|Maskulinum]]
! colspan="2" | [[Hilfe:Femininum|Femininum]]
! colspan="2" | [[Hilfe:Neutrum|Neutrum]]
! colspan="2" | —
|-
| colspan="2" | er ist [[arm]]
| colspan="2" | sie ist [[arm]]
| colspan="2" | es ist [[arm]]
| colspan="2" | sie sind [[arm]]
|}""",
        )
        root = self.wxr.wtp.parse("{{Deutsch Adjektiv Übersicht}}")
        word_entry = WordEntry(
            word="arm", lang="Deutsch", lang_code="de", pos="adj"
        )
        extract_inf_table_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "arm", "tags": ["positive"]},
                {"form": "ärmer", "tags": ["comparative"]},
                {"form": "am ärmsten", "tags": ["superlative"]},
                {
                    "form": "der arme",
                    "tags": [
                        "positive",
                        "nominative",
                        "weak",
                        "singular",
                        "masculine",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "die arme",
                    "tags": [
                        "positive",
                        "nominative",
                        "weak",
                        "singular",
                        "feminine",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "das arme",
                    "tags": [
                        "positive",
                        "nominative",
                        "weak",
                        "singular",
                        "neuter",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "die armen",
                    "tags": ["positive", "nominative", "weak", "plural"],
                    "source": "Flexion:arm",
                },
                {
                    "form": "er ist arm",
                    "tags": [
                        "positive",
                        "predicative",
                        "singular",
                        "masculine",
                    ],
                    "source": "Flexion:arm",
                },
                {
                    "form": "sie ist arm",
                    "tags": ["positive", "predicative", "singular", "feminine"],
                    "source": "Flexion:arm",
                },
                {
                    "form": "es ist arm",
                    "tags": ["positive", "predicative", "singular", "neuter"],
                    "source": "Flexion:arm",
                },
                {
                    "form": "sie sind arm",
                    "tags": ["positive", "predicative", "plural"],
                    "source": "Flexion:arm",
                },
            ],
        )

    def test_verb_table(self):
        self.wxr.wtp.start_page("sehen")
        self.wxr.wtp.add_page(
            "Vorlage:Deutsch Verb Übersicht",
            10,
            """{|
! style="width: 80px;" |
! style="width: 62px;" | [[Hilfe:Person|Person]]
! colspan="3" | Wortform
|-
! rowspan="3" | [[Hilfe:Präsens|Präsens]]
| style="text-align:right" | ich || colspan="3" | [[sehe|sehe]]
|-
|  style="text-align:right" |du || colspan="3" | [[siehst|siehst]]
|-
| style="text-align:right" | er, sie, es || colspan="3" | [[sieht|sieht]]
|-
! [[Hilfe:Präteritum|Präteritum]]
| style="text-align:right" | ich || colspan="3" | [[sah|sah]]
|-
! [[Hilfe:Konjunktiv|Konjunktiv&nbsp;II]]
| style="text-align:right" | ich || colspan="3" | [[sähe|sähe]]
|-
! rowspan="2" | [[Hilfe:Imperativ|Imperativ]]
| <small>Singular</small> || colspan="3" | [[siehe|siehe]]!<br />[[sieh|sieh]]!
|-
| <small>Plural</small> || colspan="3" | [[seht|seht]]!
|-
! rowspan="2" | [[Hilfe:Perfekt|Perfekt]] !! colspan="3" | [[Hilfe:Partizip|Partizip&nbsp;II]] ||  style="width: 90px;" | [[Hilfe:Hilfsverb|Hilfsverb]]
|-
| style="text-align:right" colspan="3" | [[gesehen|gesehen]]<br />sehen
| [[haben|haben]]
|-
! colspan="5" | <div>''All other forms:'' [[Flexion:sehen|Flexion:sehen]]</div>
|}""",  # noqa: E501
        )
        self.wxr.wtp.add_page(
            "Flexion:sehen",
            108,
            """== sehen (Konjugation) ({{Verbkonjugation|Deutsch}}) ==
{{Abgeleitete Verben|[[ansehen]], [[aufsehen]], [[umsehen]], [[versehen]]}}

{{Deutsch Verb unregelmäßig|2=seh|3=sah|4=säh|5=gesehen|6=sieh|8=i|vp=ja|zp=ja|gerund=ja
|Imperativ (du)=sieh!<br />siehe}}""",  # noqa: E501
        )
        self.wxr.wtp.add_page(
            "Vorlage:Deutsch Verb unregelmäßig",
            10,
            """==== Infinitive und Partizipien ====
{|
|-
!colspan="3" bgcolor=#CCCCFF|[[Hilfe:Infinitiv|(nichterweiterte) Infinitive]]
|-
|bgcolor=#F4F4F4|
|bgcolor=#F4F4F4 align=center|'''[[Hilfe:Präsens|Infinitiv Präsens]]'''
|bgcolor=#F4F4F4 align=center|'''[[Hilfe:Perfekt|Infinitiv Perfekt]]'''
|-
|bgcolor=#F4F4F4 align=center|'''[[Hilfe:Aktiv|Aktiv]]'''
| sehen
| gesehen haben
|-
!colspan="3" bgcolor=#CCCCFF|[[Hilfe:Partizip|Partizipien]]
|-
|bgcolor=#F4F4F4|'''[[Hilfe:Präsens|Präsens Aktiv]]'''
|bgcolor=#F4F4F4|'''[[Hilfe:Perfekt|Perfekt Passiv]]'''
|bgcolor=#F4F4F4|'''[[Hilfe:Gerundivum|Gerundivum]]'''<br><small>Nur attributive Verwendung</small>
|-
| sehend
| gesehen
| zu&#32;sehender,<br/>zu&#32;sehende&#32;…
|-
!colspan="3" bgcolor=#CCCCFF|[[Hilfe:Verbaladjektiv|Flexion der Verbaladjektive]]
|-
| [[Flexion:sehend|Flexion:sehend]]
| [[Flexion:gesehen#gesehen (Deklination) (Deutsch)|Flexion:gesehen]]
| [[Flexion:sehen/Gerundivum|Flexion:Gerundivum]]
|}""",  # noqa: E501
        )
        root = self.wxr.wtp.parse("{{Deutsch Verb Übersicht}}")
        word_entry = WordEntry(
            word="sehen", lang="Deutsch", lang_code="de", pos="verb"
        )
        extract_inf_table_template(self.wxr, word_entry, root.children[0])
        self.assertEqual(
            word_entry.model_dump(exclude_defaults=True)["forms"],
            [
                {"form": "sehe", "pronouns": ["ich"], "tags": ["present"]},
                {"form": "siehst", "pronouns": ["du"], "tags": ["present"]},
                {
                    "form": "sieht",
                    "pronouns": ["er", "sie", "es"],
                    "tags": ["present"],
                },
                {"form": "sah", "pronouns": ["ich"], "tags": ["past"]},
                {
                    "form": "sähe",
                    "pronouns": ["ich"],
                    "tags": ["subjunctive-ii"],
                },
                {"form": "siehe!", "tags": ["imperative", "singular"]},
                {"form": "sieh!", "tags": ["imperative", "singular"]},
                {"form": "seht!", "tags": ["imperative", "plural"]},
                {"form": "gesehen", "tags": ["participle-2", "perfect"]},
                {"form": "haben", "tags": ["auxiliary", "perfect"]},
                {
                    "form": "sehen",
                    "tags": ["active", "infinitive", "present"],
                    "source": "Flexion:sehen",
                    "raw_tags": ["Infinitive und Partizipien"],
                },
                {
                    "form": "gesehen haben",
                    "tags": ["active", "infinitive", "perfect"],
                    "source": "Flexion:sehen",
                    "raw_tags": ["Infinitive und Partizipien"],
                },
                {
                    "form": "sehend",
                    "tags": ["participle", "present", "active"],
                    "source": "Flexion:sehen",
                    "raw_tags": ["Infinitive und Partizipien"],
                },
                {
                    "form": "gesehen",
                    "tags": ["participle", "perfect", "passive"],
                    "source": "Flexion:sehen",
                    "raw_tags": ["Infinitive und Partizipien"],
                },
                {
                    "form": "zu sehender",
                    "tags": ["participle", "gerundive"],
                    "source": "Flexion:sehen",
                    "raw_tags": ["Infinitive und Partizipien"],
                },
                {
                    "form": "zu sehende …",
                    "tags": ["participle", "gerundive"],
                    "source": "Flexion:sehen",
                    "raw_tags": ["Infinitive und Partizipien"],
                },
            ],
        )

    def test_form_section_italic_tag(self):
        self.wxr.wtp.start_page("Hahn")
        base_data = WordEntry(lang="Deutsch", lang_code="de", word="Hahn")
        root = self.wxr.wtp.parse(":''Schweiz:'' [[Hahnen]]")
        extracrt_form_section(self.wxr, base_data, root, ["variant"])
        self.assertEqual(
            base_data.model_dump(exclude_defaults=True)["forms"],
            [
                {
                    "form": "Hahnen",
                    "tags": ["variant", "Swiss Standard German"],
                },
            ],
        )

    def test_transcription_section(self):
        self.wxr.wtp.add_page(
            "Vorlage:DIN 31634",
            10,
            "''[[Wiktionary:Altgriechisch/Umschrift|DIN 31634]]:''",
        )
        page_data = parse_page(
            self.wxr,
            "ἄνθρωπος",
            """== {{Polytonisch|ἄνθρωπος}} ({{Sprache|Altgriechisch}}) ==
=== {{Wortart|Substantiv|Altgriechisch}}, {{m}} ===
====Umschrift====
:{{DIN 31634}} anthrōpos
====Bedeutungen====
:[1] [[Mensch]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "anthrōpos",
                    "tags": ["transcription"],
                    "raw_tags": ["DIN 31634"],
                }
            ],
        )

        page_data = parse_page(
            self.wxr,
            "فه‌رهه‌نگ",
            """== فه‌رهه‌نگ ({{Sprache|Kurdisch}}) ==
=== {{Wortart|Substantiv|Kurdisch}} ===
====Umschrift====
:ferheng
====Bedeutungen====
:[1] [[Wörterbuch]], [[Lexikon]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [{"form": "ferheng", "tags": ["transcription"]}],
        )

        page_data = parse_page(
            self.wxr,
            "日本",
            """== 日本 ({{Sprache|Japanisch}}) ==
=== {{Wortart|Substantiv|Japanisch}}, {{Wortart|Eigenname|Japanisch}} ===
====Umschrift====
:[[Hilfe:Hepburn-shiki|Hepburn]]: [[nippon]], [[nihon]]
====Bedeutungen====
:[1] [[Japan]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "nippon",
                    "tags": ["transcription"],
                    "raw_tags": ["Hepburn"],
                },
                {
                    "form": "nihon",
                    "tags": ["transcription"],
                    "raw_tags": ["Hepburn"],
                },
            ],
        )

    def test_pron_table(self):
        self.wxr.wtp.add_page(
            "Vorlage:Deutsch Possessivpronomen",
            10,
            """{| class="wikitable float-right"
! style="background-color:#c6e2ff;" colspan="9" | attributiv (vor Substantiv)
|-
! rowspan="3" |
! colspan="6" | [[Hilfe:Singular|Singular]]
! colspan="2" | [[Hilfe:Plural|Plural]]
|-
! colspan="2" | [[Hilfe:Maskulinum|Maskulinum]]
! colspan="2" | [[Hilfe:Femininum|Femininum]]
! colspan="2" | [[Hilfe:Neutrum|Neutrum]]
! colspan="2" | —
|-
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
|-
! style="text-align:left" | [[Hilfe:Nominativ|Nominativ]]
| style="text-align:center" | —
| mein
| style="text-align:center" | —
| [[meine|meine]]
| style="text-align:center" | —
| mein
| style="text-align:center" | —
| [[meine|meine]]
|-
! style="background-color:#c6e2ff;" colspan="9" | nicht attributiv, mit Artikel
|-
! rowspan="3" |
! colspan="6" | [[Hilfe:Singular|Singular]]
! colspan="2" | [[Hilfe:Plural|Plural]]
|-
! colspan="2" | [[Hilfe:Maskulinum|Maskulinum]]
! colspan="2" | [[Hilfe:Femininum|Femininum]]
! colspan="2" | [[Hilfe:Neutrum|Neutrum]]
! colspan="2" | —
|-
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
! style="background:#F9F9F9" | [[Hilfe:Artikel|Artikel]]
! style="background:#F9F9F9" | [[Hilfe:Wortform|Wortform]]
|-
! style="text-align:left" | [[Hilfe:Nominativ|Nominativ]]
| der
| [[meine|meine]]
| die
| [[meine|meine]]
| das
| [[meine|meine]]
| die
| [[meinen|meinen]]
|}""",
        )
        page_data = parse_page(
            self.wxr,
            "mein",
            """== mein ({{Sprache|Deutsch}}) ==
=== {{Wortart|Possessivpronomen|Deutsch}}, ''1. Person Singular'' ===
{{Deutsch Possessivpronomen|mein}}
====Bedeutungen====
:[1] zeigt den Besitz""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "meine",
                    "tags": ["nominative", "singular", "feminine"],
                    "raw_tags": ["attributiv (vor Substantiv)"],
                },
                {
                    "form": "meine",
                    "tags": ["nominative", "plural"],
                    "raw_tags": ["attributiv (vor Substantiv)"],
                },
                {
                    "form": "der meine",
                    "tags": ["nominative", "singular", "masculine"],
                    "raw_tags": ["nicht attributiv, mit Artikel"],
                },
                {
                    "form": "die meine",
                    "tags": ["nominative", "singular", "feminine"],
                    "raw_tags": ["nicht attributiv, mit Artikel"],
                },
                {
                    "form": "das meine",
                    "tags": ["nominative", "singular", "neuter"],
                    "raw_tags": ["nicht attributiv, mit Artikel"],
                },
                {
                    "form": "die meinen",
                    "tags": ["nominative", "plural"],
                    "raw_tags": ["nicht attributiv, mit Artikel"],
                },
            ],
        )

    def test_plain_text_roman(self):
        page_data = parse_page(
            self.wxr,
            "mein",
            """== ولد ({{Sprache|Arabisch}}) ==
=== {{Wortart|Verb|Arabisch}} ===
====Umschrift====
:[[Hilfe:DMG|DMG]]: walada, Imperfekt: yalidu, Imperativ: lid
====Bedeutungen====
:[1] [[gebären]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {
                    "form": "walada",
                    "raw_tags": ["DMG"],
                    "tags": ["transcription"],
                },
                {"form": "yalidu", "tags": ["transcription", "imperfect"]},
                {"form": "lid", "tags": ["transcription", "imperative"]},
            ],
        )

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.table import process_inflection_section
from wiktextract.wxr_context import WiktextractContext


class TestElConjugation(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="el"),
            WiktionaryConfig(
                dump_file_lang_code="el",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def xinfl(self, word, pos, text):
        """Runs a single inflection table parsing test, and returns ``forms``.

        Adapted from the English xinfl used in inflection tests.
        """
        lang = "Greek"
        self.wxr.wtp.start_page(word)
        self.wxr.wtp.start_section(lang)
        self.wxr.wtp.start_subsection(pos)
        tree = self.wxr.wtp.parse(text)
        data = WordEntry(lang=lang, lang_code="el", word=word)
        process_inflection_section(self.wxr, data, tree)
        dumped = data.model_dump(exclude_defaults=True)
        forms = dumped["forms"]
        return forms

    def mktest_conjugation(self, received, expected):
        def sort_tags(lst):
            for form in lst:
                if "raw_tags" in form:
                    form["raw_tags"].sort()
                if "tags" in form:
                    form["tags"].sort()

        sort_tags(received)
        sort_tags(expected)

        self.assertEqual(received, expected)

    def test_el_conjugation_table(self):
        # Section of https://el.wiktionary.org/wiki/πίνω:
        # {{el-κλίσ-'μπαίνω'|θαορ=ήπι|θμελλ=πι}}
        # Expanded via 'wxr.wtp.node_to_text(node)' at the start of
        # 'process_inflection_section'
        raw = """
        {|
        |-
        ! colspan="7" style="background:#e2e4c0; text-align:center" | Εξακολουθητικοί χρόνοι
        |-
        ! πρόσωπα
        ! Ενεστώτας
        ! Παρατατικός
        ! Εξ. Μέλλ.
        ! Υποτακτική
        ! Προστακτική
        ! align=center | Μετοχή
        |-
        | style='background:#c0c0c0' | α' ενικ.
        | πίνω
        | έπινα
        | θα πίνω
        | να πίνω
        |
        | rowspan="6" align="center" |πίνοντας
        |-
        | style='background:#c0c0c0' | β' ενικ.
        | πίνεις
        | έπινες
        | θα πίνεις
        | να πίνεις
        | πίνε

        |}
        """.strip()
        received = self.xinfl("πίνω", "verb", raw)

        expected = [
            {"tags": ["inflection-template"]},
            {
                "form": "πίνω",
                "tags": ["first-person", "imperfective", "present", "singular"],
                "raw_tags": ["Εξακολουθητικοί χρόνοι", "Ενεστώτας", "α' ενικ."],
            },
            {
                "form": "έπινα",
                "tags": [
                    "first-person",
                    "imperfect",
                    "imperfective",
                    "singular",
                ],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "α' ενικ.",
                    "Παρατατικός",
                ],
            },
            {
                "form": "θα πίνω",
                "tags": [
                    "first-person",
                    "future",
                    "imperfect",
                    "imperfective",
                    "singular",
                ],
                "raw_tags": ["Εξ. Μέλλ.", "Εξακολουθητικοί χρόνοι", "α' ενικ."],
            },
            {
                "form": "να πίνω",
                "tags": [
                    "first-person",
                    "imperfective",
                    "singular",
                    "subjunctive",
                ],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "α' ενικ.",
                    "Υποτακτική",
                ],
            },
            {
                "form": "πίνοντας",
                "tags": ["imperfective", "participle"],
                "raw_tags": ["Μετοχή", "Εξακολουθητικοί χρόνοι"],
            },
            {
                "form": "πίνεις",
                "tags": [
                    "imperfective",
                    "present",
                    "second-person",
                    "singular",
                ],
                "raw_tags": ["Ενεστώτας", "Εξακολουθητικοί χρόνοι", "β' ενικ."],
            },
            {
                "form": "έπινες",
                "tags": [
                    "imperfect",
                    "imperfective",
                    "second-person",
                    "singular",
                ],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Παρατατικός",
                    "β' ενικ.",
                ],
            },
            {
                "form": "θα πίνεις",
                "tags": [
                    "future",
                    "imperfect",
                    "imperfective",
                    "second-person",
                    "singular",
                ],
                "raw_tags": ["Εξ. Μέλλ.", "Εξακολουθητικοί χρόνοι", "β' ενικ."],
            },
            {
                "form": "να πίνεις",
                "tags": [
                    "imperfective",
                    "second-person",
                    "singular",
                    "subjunctive",
                ],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Υποτακτική",
                    "β' ενικ.",
                ],
            },
            {
                "form": "πίνε",
                "tags": [
                    "imperative",
                    "imperfective",
                    "second-person",
                    "singular",
                ],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Προστακτική",
                    "β' ενικ.",
                ],
            },
        ]

        self.mktest_conjugation(received, expected)

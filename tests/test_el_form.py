from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import Form
from wiktextract.extractor.el.parse_utils import expand_suffix_forms
from wiktextract.extractor.el.table import postprocess_table_forms
from wiktextract.wxr_context import WiktextractContext


class TestElInflection(TestCase):
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

    def mktest_postprocess_table_forms(
        self, raw: str, expected: list[str]
    ) -> None:
        forms = [Form(form=entry.strip()) for entry in raw.splitlines()]
        new_forms = postprocess_table_forms(forms)
        new_forms_lemmas = [form.form for form in new_forms]
        self.assertEqual(new_forms_lemmas, expected)

    def test_postprocess_forms_separators1(self) -> None:
        # https://el.wiktionary.org/wiki/τρώω
        raw = "έτρωγαν / τρώγανε"
        expected = ["έτρωγαν", "τρώγανε"]
        self.mktest_postprocess_table_forms(raw, expected)

    def test_postprocess_forms_separators2(self) -> None:
        # https://el.wiktionary.org/wiki/ζητάω
        raw = "να ζητάν(ε) - ζητούν(ε)"
        expected = ["να ζητάν", "να ζητάνε", "να ζητούν", "να ζητούνε"]
        self.mktest_postprocess_table_forms(raw, expected)

    def test_postprocess_forms_separators3(self) -> None:
        # https://el.wiktionary.org/wiki/ζητάω
        raw = "ζητούσαν(ε) - ζήταγαν - ζητάγανε"
        expected = ["ζητούσαν", "ζητούσανε", "ζήταγαν", "ζητάγανε"]
        self.mktest_postprocess_table_forms(raw, expected)

    def test_postprocess_forms_declension(self) -> None:
        # https://el.wiktionary.org/wiki/λίθος
        # raw = "του/της λίθου" < This is never parsed by us
        # expected = ["λίθου"]  <
        raw = """
        ο/η
        του/της
        τον/τη
        τους/τις
        """.strip()
        self.mktest_postprocess_table_forms(raw, [])

    def test_postprocess_forms_suffix(self) -> None:
        # https://el.wiktionary.org/wiki/-ισμός
        raw = "ο -ισμός"
        expected = ["-ισμός"]
        self.mktest_postprocess_table_forms(raw, expected)

    def test_postprocess_forms_trailing_numbers(self) -> None:
        # https://el.wiktionary.org/wiki/Καπιτόπουλος
        raw = "Καπιτοπουλαίοι1"
        expected = ["Καπιτοπουλαίοι"]
        self.mktest_postprocess_table_forms(raw, expected)

    def mktest_expand_suffix_forms(self, raw: str, expected: list[str]) -> None:
        forms = [Form(form=entry.strip()) for entry in raw.split(",")]
        new_forms = expand_suffix_forms(forms)
        new_forms_lemmas = [form.form for form in new_forms]
        self.assertEqual(new_forms_lemmas, expected)

    def test_expand_suffix_forms_adj1(self) -> None:
        # https://el.wiktionary.org/wiki/άμεσος
        raw = "άμεσος, -η, -ο"
        expected = ["άμεσος", "άμεση", "άμεσο"]
        self.mktest_expand_suffix_forms(raw, expected)

    def test_expand_suffix_forms_adj2(self) -> None:
        # https://el.wiktionary.org/wiki/αρσενικός
        raw = "αρσενικός, -ή/-ιά, -ό"
        word = raw.split(",")[0]
        expected = ["αρσενικός", "αρσενική", "αρσενικιά", "αρσενικό"]
        self.mktest_expand_suffix_forms(raw, expected)

    def test_expand_suffix_forms_adj3(self) -> None:
        # https://el.wiktionary.org/wiki/σιδηρούς
        raw = "σιδηρούς, -ά, -ούν "
        word = raw.split(",")[0]
        expected = ["σιδηρούς", "σιδηρά", "σιδηρούν"]
        self.mktest_expand_suffix_forms(raw, expected)

    def test_expand_suffix_forms_adj4(self) -> None:
        # https://el.wiktionary.org/wiki/εξαμηνιαίος
        raw = "εξαμηνιαίος, -α, -ο"
        word = raw.split(",")[0]
        expected = ["εξαμηνιαίος", "εξαμηνιαία", "εξαμηνιαίο"]
        self.mktest_expand_suffix_forms(raw, expected)

    def test_expand_suffix_forms_participle(self) -> None:
        # https://el.wiktionary.org/wiki/αναμμένος
        raw = "αναμμένος, -η, -ο"
        word = raw.split(",")[0]
        expected = ["αναμμένος", "αναμμένη", "αναμμένο"]
        self.mktest_expand_suffix_forms(raw, expected)

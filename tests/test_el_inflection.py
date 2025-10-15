"""Inflection tests are made with:

   with open("inflection_table_dump.txt", "w") as f:
        text = wxr.wtp.node_to_wikitext(tnode)
        text = "\n".join(line.strip() for line in text.splitlines() if line)
        f.write(f"{text}\n")

at table.parse_table.py

The above trimming is done to compact tests.
"""

from unittest import TestCase

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.el.models import WordEntry
from wiktextract.extractor.el.table import process_inflection_section
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
        process_inflection_section(self.wxr, data, tree)  # note that source=""
        dumped = data.model_dump(exclude_defaults=True)
        forms = dumped["forms"]
        return forms

    def _remove_dontcares(self, received):
        dontcares = (
            {"tags": ["inflection-template"]},
            {"tags": ["inflection-template"], "source": "inflection"},
            {"source": "inflection", "tags": ["inflection-template"]},
        )
        for dontcare in dontcares:
            if dontcare in received:
                idx = received.index(dontcare)
                received.pop(idx)

    def mktest_form(self, raw, expected):
        received = self.xinfl("filler", "verb", raw.strip())

        self._remove_dontcares(received)

        def normalize_forms(lst):
            for form in lst:
                if "raw_tags" in form:
                    form["raw_tags"].sort()
                if "tags" in form:
                    form["tags"].sort()

        normalize_forms(received)
        normalize_forms(expected)

        self.assertEqual(received, expected)

    def mktest_form_no_raw_tags(self, raw, expected):
        received = self.xinfl("filler", "verb", raw.strip())

        self._remove_dontcares(received)

        def normalize_forms(lst):
            for form in lst:
                if "raw_tags" in form:
                    del form["raw_tags"]
                if "tags" in form:
                    form["tags"].sort()

        normalize_forms(received)
        normalize_forms(expected)

        self.assertEqual(received, expected)

    def test_noun_inflection_two_tables(self):
        # https://el.wiktionary.org/wiki/πλάγιος
        # The second table are the literary (usu. from Ancient Greek) versions
        raw = """
{| style="clear%3Aright%3B+float%3Aright%3B+margin-left%3A0.5em%3B+margin-bottom%3A0.5em%3Bbackground%3A%23ffffff%3B+color%3A%23000000%3B+border%3A1px+solid%23a1bdea%3B+text-align%3Aright%3B" rules="none" border="1" cellpadding="3" cellspacing="0"
|-
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B+text-align%3Acenter%3B+font-size%3A90%25%3B" align="center" | &darr;&nbsp;''πτώσεις''
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23a1bdea%3B+font-size%3A90%25%3B" align="center" colspan="6" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[ενικός|<span title="%CE%B5%CE%BD%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''ενικός'''''</span>]]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
|-
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+text-align%3Acenter%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" align="center" | ''γένη''&nbsp;&rarr;
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+font-size%3A70%25%3B+font-style%3Aitalic%3B+line-height%3A100%25%3B" colspan="2" align="center" | [[αρσενικό|<span style="color%3A%23000000%3B+font-weight%3Anormal%3B">αρσενικό</span>]]
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+font-size%3A70%25%3B+font-style%3Aitalic%3B+line-height%3A100%25%3B" colspan="2" align="center" | [[θηλυκό|<span style="color%3A%23000000%3B+font-weight%3Anormal%3B">θηλυκό</span>]]
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+font-size%3A70%25%3B+font-style%3Aitalic%3B+line-height%3A100%25%3B" colspan="2" align="center" | [[ουδέτερο|<span style="color%3A%23000000%3B+font-weight%3Anormal%3B">ουδέτερο</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | [[ονομαστική|<span title="%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''ονομαστική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[ο#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">ο</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιος#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ος</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[η#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">η</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγια#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">α</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγία#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">α</span>]]</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιο#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ο</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="%CE%B3%CE%B5%CE%BD%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''γενική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[του#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">του</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιου#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ου</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγίου#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ου</span>]]</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[της#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">της</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιας#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ας</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγίας#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ας</span>]]</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[του#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">του</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιου#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ου</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγίου#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ου</span>]]</span>
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''αιτιατική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τον#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τον</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιο#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ο</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[την#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">την</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγια#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">α</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγία#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">α</span>]]</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιο#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ο</span>]]
|-
| style="background%3A%23d5e2f6%3B+text-align%3Aright%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="%CE%BA%CE%BB%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B+font-size%3A90%25%3B">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιε#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ε</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγια#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">α</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλάγια#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">α</span>]]</span>
| align="center" |
| style="border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιο#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ο</span>]]
|-
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B+text-align%3Acenter%3B+font-size%3A90%25%3B" align="center" | &darr;&nbsp;''πτώσεις''
! style="background%3A%23a1bdea%3B+font-size%3A90%25%3B" align="center" colspan="6" | &nbsp;&nbsp;[[πληθυντικός|<span title="%CF%80%CE%BB%CE%B7%CE%B8%CF%85%CE%BD%CF%84%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''πληθυντικός'''''</span>]]&nbsp;&nbsp;
|-
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+text-align%3Acenter%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" align="center" | ''γένη''&nbsp;&rarr;
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+font-size%3A70%25%3B+font-style%3Aitalic%3B+line-height%3A100%25%3B" colspan="2" align="center" | [[αρσενικό|<span style="color%3A%23000000%3B+font-weight%3Anormal%3B">αρσενικό</span>]]
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+font-size%3A70%25%3B+font-style%3Aitalic%3B+line-height%3A100%25%3B" colspan="2" align="center" | [[θηλυκό|<span style="color%3A%23000000%3B+font-weight%3Anormal%3B">θηλυκό</span>]]
| style="background%3A%23c1d3f1%3B+border-right%3A1px+solid+%23a1bdea%3B+font-size%3A70%25%3B+font-style%3Aitalic%3B+line-height%3A100%25%3B" colspan="2" align="center" | [[ουδέτερο|<span style="color%3A%23000000%3B+font-weight%3Anormal%3B">ουδέτερο</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | [[ονομαστική|<span title="%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''ονομαστική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[οι#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">οι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιοι#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">οι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[οι#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">οι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιες#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ες</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγια#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">α</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="%CE%B3%CE%B5%CE%BD%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''γενική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[των#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">των</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιων#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ων</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγίων#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ων</span>]]</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[των#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">των</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιων#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ων</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγίων#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ων</span>]]</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[των#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">των</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιων#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ων</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγίων#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ων</span>]]</span>
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''αιτιατική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τους#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τους</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιους#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ους</span>]]<br><span style="white-space%3Anowrap%3B+font-size%3Asmall%3B">&&nbsp;[[πλαγίους#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλαγί</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ους</span>]]</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τις#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τις</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιες#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ες</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγια#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">α</span>]]
|-
| style="background%3A%23d5e2f6%3B+text-align%3Aright%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="%CE%BA%CE%BB%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B+font-size%3A90%25%3B">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιοι#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">οι</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγιες#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">ες</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[πλάγια#Νέα ελληνικά (el)|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">πλάγι</span><span style="color%3A%23eb0000%3B+font-weight%3Anormal%3B">α</span>]]
|-
| colspan="7" align="left" style="background%3A%23eaf0fa%3B+font-size%3A80%25%3B+line-height%3A100%25%3B" | Οι δεύτεροι τύποι, λόγιοι, από την αρχαία κλίση.
|-
| colspan="7" align="right" style="text-align%3Aright%3B+background%3A%23eaf0fa%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" | [[:Κατηγορία:Επίθετα που κλίνονται όπως το 'πλάγιος' (νέα ελληνικά)|Κατηγορία]] όπως «[[Παράρτημα:Επίθετα και μετοχές (νέα ελληνικά)#πλάγιος|πλάγιος]]» - [[Παράρτημα:Επίθετα και μετοχές (νέα ελληνικά)|<span title="%CE%A0%CE%B1%CF%81%CE%AC%CF%81%CF%84%CE%B7%CE%BC%CE%B1%3A%CE%95%CF%80%CE%AF%CE%B8%CE%B5%CF%84%CE%B1+%26+%CE%9C%CE%B5%CF%84%CE%BF%CF%87%CE%AD%CF%82">Παράρτημα:Επίθετα & Μετοχές</span>]]
|}
"""
        expected = [
            {
                "form": "πλάγιος",
                "tags": ["masculine", "nominative", "singular"],
            },
            {"form": "πλάγια", "tags": ["feminine", "nominative", "singular"]},
            {"form": "πλαγία", "tags": ["feminine", "nominative", "singular"]},
            {"form": "πλάγιο", "tags": ["neuter", "nominative", "singular"]},
            {"form": "πλάγιου", "tags": ["genitive", "masculine", "singular"]},
            {"form": "πλαγίου", "tags": ["genitive", "masculine", "singular"]},
            {"form": "πλάγιας", "tags": ["feminine", "genitive", "singular"]},
            {"form": "πλαγίας", "tags": ["feminine", "genitive", "singular"]},
            {"form": "πλάγιου", "tags": ["genitive", "neuter", "singular"]},
            {"form": "πλαγίου", "tags": ["genitive", "neuter", "singular"]},
            {"form": "πλάγιο", "tags": ["accusative", "masculine", "singular"]},
            {"form": "πλάγια", "tags": ["accusative", "feminine", "singular"]},
            {"form": "πλαγία", "tags": ["accusative", "feminine", "singular"]},
            {"form": "πλάγιο", "tags": ["accusative", "neuter", "singular"]},
            {"form": "πλάγιε", "tags": ["masculine", "singular", "vocative"]},
            {"form": "πλάγια", "tags": ["feminine", "singular", "vocative"]},
            {"form": "πλάγιο", "tags": ["neuter", "singular", "vocative"]},
            {"form": "πλάγιοι", "tags": ["masculine", "nominative", "plural"]},
            {"form": "πλάγιες", "tags": ["feminine", "nominative", "plural"]},
            {"form": "πλάγια", "tags": ["neuter", "nominative", "plural"]},
            {"form": "πλάγιων", "tags": ["genitive", "masculine", "plural"]},
            {"form": "πλαγίων", "tags": ["genitive", "masculine", "plural"]},
            {"form": "πλάγιων", "tags": ["feminine", "genitive", "plural"]},
            {"form": "πλαγίων", "tags": ["feminine", "genitive", "plural"]},
            {"form": "πλάγιων", "tags": ["genitive", "neuter", "plural"]},
            {"form": "πλαγίων", "tags": ["genitive", "neuter", "plural"]},
            {"form": "πλάγιους", "tags": ["accusative", "masculine", "plural"]},
            {"form": "πλαγίους", "tags": ["accusative", "masculine", "plural"]},
            {"form": "πλάγιες", "tags": ["accusative", "feminine", "plural"]},
            {"form": "πλάγια", "tags": ["accusative", "neuter", "plural"]},
            {"form": "πλάγιοι", "tags": ["masculine", "plural", "vocative"]},
            {"form": "πλάγιες", "tags": ["feminine", "plural", "vocative"]},
            {"form": "πλάγια", "tags": ["neuter", "plural", "vocative"]},
        ]
        self.mktest_form_no_raw_tags(raw, expected)

    def test_noun_inflection_only_singular(self):
        # https://el.wiktionary.org/wiki/αιδώς
        raw = """
{| style="clear%3Aright%3B+float%3Aright%3B+margin-left%3A0.5em%3B+margin-bottom%3A0.5em%3Bbackground%3A%23ffffff%3B+color%3A%23000000%3B+border%3A1px+solid%23a1bdea%3B+text-align%3Aright%3B" rules="none" border="1" cellpadding="3" cellspacing="0"
|-
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B+text-align%3Acenter%3B+font-size%3A90%25%3B" align="center" | &darr;&nbsp;''πτώσεις''
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23a1bdea%3B" colspan="2" align="center" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[ενικός|<span title="%CE%B5%CE%BD%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''ενικός'''''</span>]]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | [[ονομαστική|<span title="%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''ονομαστική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[η|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">η</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[αιδώς|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αιδ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ώς</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="%CE%B3%CE%B5%CE%BD%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''γενική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[της|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">της</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[αιδούς|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αιδ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ούς</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''αιτιατική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[την|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">την</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[αιδώ|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αιδ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ώ</span>]]
|-
| style="background%3A%23d5e2f6%3B+text-align%3Aright%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="%CE%BA%CE%BB%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B+font-size%3A90%25%3B">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23a1bdea%3B" align="left" | [[αιδώ|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αιδ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ώ</span>]]
|-
| colspan="5" align="right" style="text-align%3Aright%3B+background%3A%23eaf0fa%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" | [[:Κατηγορία:Ουσιαστικά που κλίνονται όπως το 'αιδώς' (νέα ελληνικά)|Κατηγορία]]  όπως «[[Παράρτημα:Ουσιαστικά (νέα ελληνικά)/θηλυκά#αιδώς|αιδώς]]» - [[Παράρτημα:Ουσιαστικά (νέα ελληνικά)|<span title="%CE%A0%CE%B1%CF%81%CE%AC%CF%81%CF%84%CE%B7%CE%BC%CE%B1%3A%CE%9F%CF%85%CF%83%CE%B9%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AC">Παράρτημα:Ουσιαστικά</span>]]
|}
"""
        expected = [
            {"form": "αιδώς", "tags": ["nominative", "singular"]},
            {"form": "αιδούς", "tags": ["genitive", "singular"]},
            {"form": "αιδώ", "tags": ["accusative", "singular"]},
            {"form": "αιδώ", "tags": ["vocative", "singular"]},
        ]
        self.mktest_form_no_raw_tags(raw, expected)

    def test_noun_inflection_no_genitive(self) -> None:
        # https://el.wiktionary.org/wiki/αβγούλι
        raw = """
{| style="clear%3Aright%3B+float%3Aright%3B+margin-left%3A0.5em%3B+margin-bottom%3A0.5em%3Bbackground%3A%23ffffff%3B+color%3A%23000000%3B+border%3A1px+solid%23a1bdea%3B+text-align%3Aright%3B" rules="none" border="1" cellpadding="3" cellspacing="0"
|-
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B+text-align%3Acenter%3B+font-size%3A90%25%3B" align="center" | &darr;&nbsp;''πτώσεις''
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B" colspan="2" align="center" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[ενικός|<span title="%CE%B5%CE%BD%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''ενικός'''''</span>]]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
! style="background%3A%23a1bdea%3B" colspan="2" align="center" | &nbsp;&nbsp;[[πληθυντικός|<span title="%CF%80%CE%BB%CE%B7%CE%B8%CF%85%CE%BD%CF%84%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''πληθυντικός'''''</span>]]&nbsp;&nbsp;
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | [[ονομαστική|<span title="%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''ονομαστική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[αβγούλι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αβγούλ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[αβγούλια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αβγούλ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="%CE%B3%CE%B5%CE%BD%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''γενική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" |
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | <span style="color%3A%23dddddd%3B">&mdash;</span>
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" |
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | <span style="color%3A%23dddddd%3B">&mdash;</span>
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''αιτιατική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[αβγούλι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αβγούλ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[αβγούλια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αβγούλ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| style="background%3A%23d5e2f6%3B+text-align%3Aright%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="%CE%BA%CE%BB%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B+font-size%3A90%25%3B">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[αβγούλι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αβγούλ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| align="center" |
| align="left" | [[αβγούλια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αβγούλ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| colspan="5" align="left" style="background%3A%23eaf0fa%3B+font-size%3A80%25%3B+line-height%3A100%25%3B" | Η κατάληξη του πληθυντικού -ια προφέρεται με [[συνίζηση]].
|-
| colspan="5" align="right" style="text-align%3Aright%3B+background%3A%23eaf0fa%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" | [[:Κατηγορία:Ουσιαστικά που κλίνονται όπως το 'παιδάκι' (νέα ελληνικά)|Κατηγορία]]  όπως «[[Παράρτημα:Ουσιαστικά (νέα ελληνικά)/ουδέτερα#παιδάκι|παιδάκι]]» - [[Παράρτημα:Ουσιαστικά (νέα ελληνικά)|<span title="%CE%A0%CE%B1%CF%81%CE%AC%CF%81%CF%84%CE%B7%CE%BC%CE%B1%3A%CE%9F%CF%85%CF%83%CE%B9%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AC">Παράρτημα:Ουσιαστικά</span>]]
|}
"""
        expected = [
            {"form": "αβγούλι", "tags": ["nominative", "singular"]},
            {"form": "αβγούλια", "tags": ["nominative", "plural"]},
            # There should be no genitive
            {"form": "αβγούλι", "tags": ["accusative", "singular"]},
            {"form": "αβγούλια", "tags": ["accusative", "plural"]},
            {"form": "αβγούλι", "tags": ["vocative", "singular"]},
            {"form": "αβγούλια", "tags": ["vocative", "plural"]},
        ]
        self.mktest_form_no_raw_tags(raw, expected)

    def test_noun_inflection_standard(self):
        raw = """
{| style="clear%3Aright%3B+float%3Aright%3B+margin-left%3A0.5em%3B+margin-bottom%3A0.5em%3Bbackground%3A%23ffffff%3B+color%3A%23000000%3B+border%3A1px+solid%23a1bdea%3B+text-align%3Aright%3B" rules="none" border="1" cellpadding="3" cellspacing="0"
|-
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B+text-align%3Acenter%3B+font-size%3A90%25%3B" align="center" | &darr;&nbsp;''πτώσεις''
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B" colspan="2" align="center" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[ενικός|<span title="%CE%B5%CE%BD%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''ενικός'''''</span>]]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
! style="background%3A%23a1bdea%3B" colspan="2" align="center" | &nbsp;&nbsp;[[πληθυντικός|<span title="%CF%80%CE%BB%CE%B7%CE%B8%CF%85%CE%BD%CF%84%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''πληθυντικός'''''</span>]]&nbsp;&nbsp;
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | [[ονομαστική|<span title="%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''ονομαστική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[μπόι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπό</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[μπόγια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπό</span><span style="color%3A%23002000%3B+font-weight%3Anormal%3B">γ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="%CE%B3%CE%B5%CE%BD%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''γενική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[του|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">του</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[μπογιού|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπο</span><span style="color%3A%23002000%3B+font-weight%3Anormal%3B">γ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ιού</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[των|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">των</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | ([[μπογιών|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπο</span><span style="color%3A%23002000%3B+font-weight%3Anormal%3B">γ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ιών</span>]])
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''αιτιατική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[μπόι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπό</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[μπόγια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπό</span><span style="color%3A%23002000%3B+font-weight%3Anormal%3B">γ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| style="background%3A%23d5e2f6%3B+text-align%3Aright%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="%CE%BA%CE%BB%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B+font-size%3A90%25%3B">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[μπόι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπό</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| align="center" |
| align="left" | [[μπόγια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">μπό</span><span style="color%3A%23002000%3B+font-weight%3Anormal%3B">γ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| colspan="5" align="left" style="background%3A%23eaf0fa%3B+font-size%3A80%25%3B+line-height%3A100%25%3B" | Οι καταλήξεις -ιού, -ια, -ιών προφέρονται με [[συνίζηση]].<br>Ο πληθυντικός δε συνηθίζεται.
|-
| colspan="5" align="right" style="text-align%3Aright%3B+background%3A%23eaf0fa%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" | [[:Κατηγορία:Ουσιαστικά που κλίνονται όπως το 'τσάι' (νέα ελληνικά)|Κατηγορία]]  όπως «[[Παράρτημα:Ουσιαστικά (νέα ελληνικά)/ουδέτερα#τσάι|τσάι]]» - [[Παράρτημα:Ουσιαστικά (νέα ελληνικά)|<span title="%CE%A0%CE%B1%CF%81%CE%AC%CF%81%CF%84%CE%B7%CE%BC%CE%B1%3A%CE%9F%CF%85%CF%83%CE%B9%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AC">Παράρτημα:Ουσιαστικά</span>]]
|}
"""
        expected = [
            {"form": "μπόι", "tags": ["nominative", "singular"]},
            {"form": "μπόγια", "tags": ["nominative", "plural"]},
            {"form": "μπογιού", "tags": ["genitive", "singular"]},
            # {"form": "(μπογιών)", "tags": ["genitive", "plural"]},
            # v Should treat parenthesized forms as rare
            {"form": "μπογιών", "tags": ["genitive", "plural", "rare"]},
            {"form": "μπόι", "tags": ["accusative", "singular"]},
            {"form": "μπόγια", "tags": ["accusative", "plural"]},
            {"form": "μπόι", "tags": ["vocative", "singular"]},
            {"form": "μπόγια", "tags": ["vocative", "plural"]},
        ]
        self.mktest_form_no_raw_tags(raw, expected)

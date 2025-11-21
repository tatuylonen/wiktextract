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
from wiktextract.extractor.el.page import parse_page
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

    def mktest_form(self, raw, expected) -> None:
        received = self.xinfl("filler", "verb", raw.strip())
        self.assertEqual(received, expected)

    def mktest_form_no_raw_tags(self, raw, expected) -> None:
        received = self.xinfl("filler", "verb", raw.strip())

        def normalize_forms(lst) -> None:
            for form in lst:
                if "raw_tags" in form:
                    del form["raw_tags"]

        normalize_forms(received)
        normalize_forms(expected)

        self.assertEqual(received, expected)

    def test_noun_inflection_two_tables(self) -> None:
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
            {"tags": ["inflection-template"]},
            {
                "form": "πλάγιος",
                "tags": ["masculine", "singular", "nominative"],
                "raw_tags": ["αρσενικό", "ενικός", "ονομαστική"],
            },
            {
                "form": "πλάγια",
                "tags": ["singular", "feminine", "nominative"],
                "raw_tags": ["ενικός", "θηλυκό", "ονομαστική"],
            },
            {
                "form": "πλαγία",
                "tags": ["singular", "feminine", "nominative"],
                "raw_tags": ["ενικός", "θηλυκό", "ονομαστική"],
            },
            {
                "form": "πλάγιο",
                "tags": ["singular", "nominative", "neuter"],
                "raw_tags": ["ενικός", "ονομαστική", "ουδέτερο"],
            },
            {
                "form": "πλάγιου",
                "tags": ["masculine", "genitive", "singular"],
                "raw_tags": ["αρσενικό", "γενική", "ενικός"],
            },
            {
                "form": "πλαγίου",
                "tags": ["masculine", "genitive", "singular"],
                "raw_tags": ["αρσενικό", "γενική", "ενικός"],
            },
            {
                "form": "πλάγιας",
                "tags": ["genitive", "singular", "feminine"],
                "raw_tags": ["γενική", "ενικός", "θηλυκό"],
            },
            {
                "form": "πλαγίας",
                "tags": ["genitive", "singular", "feminine"],
                "raw_tags": ["γενική", "ενικός", "θηλυκό"],
            },
            {
                "form": "πλάγιου",
                "tags": ["genitive", "singular", "neuter"],
                "raw_tags": ["γενική", "ενικός", "ουδέτερο"],
            },
            {
                "form": "πλαγίου",
                "tags": ["genitive", "singular", "neuter"],
                "raw_tags": ["γενική", "ενικός", "ουδέτερο"],
            },
            {
                "form": "πλάγιο",
                "tags": ["accusative", "masculine", "singular"],
                "raw_tags": ["αιτιατική", "αρσενικό", "ενικός"],
            },
            {
                "form": "πλάγια",
                "tags": ["accusative", "singular", "feminine"],
                "raw_tags": ["αιτιατική", "ενικός", "θηλυκό"],
            },
            {
                "form": "πλαγία",
                "tags": ["accusative", "singular", "feminine"],
                "raw_tags": ["αιτιατική", "ενικός", "θηλυκό"],
            },
            {
                "form": "πλάγιο",
                "tags": ["accusative", "singular", "neuter"],
                "raw_tags": ["αιτιατική", "ενικός", "ουδέτερο"],
            },
            {
                "form": "πλάγιε",
                "tags": ["masculine", "singular", "vocative"],
                "raw_tags": ["αρσενικό", "ενικός", "κλητική"],
            },
            {
                "form": "πλάγια",
                "tags": ["singular", "feminine", "vocative"],
                "raw_tags": ["ενικός", "θηλυκό", "κλητική"],
            },
            {
                "form": "πλάγιο",
                "tags": ["singular", "vocative", "neuter"],
                "raw_tags": ["ενικός", "κλητική", "ουδέτερο"],
            },
            {
                "form": "πλάγιοι",
                "tags": ["masculine", "nominative", "plural"],
                "raw_tags": ["αρσενικό", "ονομαστική", "πληθυντικός"],
            },
            {
                "form": "πλάγιες",
                "tags": ["feminine", "nominative", "plural"],
                "raw_tags": ["θηλυκό", "ονομαστική", "πληθυντικός"],
            },
            {
                "form": "πλάγια",
                "tags": ["nominative", "neuter", "plural"],
                "raw_tags": ["ονομαστική", "ουδέτερο", "πληθυντικός"],
            },
            {
                "form": "πλάγιων",
                "tags": ["masculine", "genitive", "plural"],
                "raw_tags": ["αρσενικό", "γενική", "πληθυντικός"],
            },
            {
                "form": "πλαγίων",
                "tags": ["masculine", "genitive", "plural"],
                "raw_tags": ["αρσενικό", "γενική", "πληθυντικός"],
            },
            {
                "form": "πλάγιων",
                "tags": ["genitive", "feminine", "plural"],
                "raw_tags": ["γενική", "θηλυκό", "πληθυντικός"],
            },
            {
                "form": "πλαγίων",
                "tags": ["genitive", "feminine", "plural"],
                "raw_tags": ["γενική", "θηλυκό", "πληθυντικός"],
            },
            {
                "form": "πλάγιων",
                "tags": ["genitive", "neuter", "plural"],
                "raw_tags": ["γενική", "ουδέτερο", "πληθυντικός"],
            },
            {
                "form": "πλαγίων",
                "tags": ["genitive", "neuter", "plural"],
                "raw_tags": ["γενική", "ουδέτερο", "πληθυντικός"],
            },
            {
                "form": "πλάγιους",
                "tags": ["accusative", "masculine", "plural"],
                "raw_tags": ["αιτιατική", "αρσενικό", "πληθυντικός"],
            },
            {
                "form": "πλαγίους",
                "tags": ["accusative", "masculine", "plural"],
                "raw_tags": ["αιτιατική", "αρσενικό", "πληθυντικός"],
            },
            {
                "form": "πλάγιες",
                "tags": ["accusative", "feminine", "plural"],
                "raw_tags": ["αιτιατική", "θηλυκό", "πληθυντικός"],
            },
            {
                "form": "πλάγια",
                "tags": ["accusative", "neuter", "plural"],
                "raw_tags": ["αιτιατική", "ουδέτερο", "πληθυντικός"],
            },
            {
                "form": "πλάγιοι",
                "tags": ["masculine", "vocative", "plural"],
                "raw_tags": ["αρσενικό", "κλητική", "πληθυντικός"],
            },
            {
                "form": "πλάγιες",
                "tags": ["feminine", "vocative", "plural"],
                "raw_tags": ["θηλυκό", "κλητική", "πληθυντικός"],
            },
            {
                "form": "πλάγια",
                "tags": ["vocative", "neuter", "plural"],
                "raw_tags": ["κλητική", "ουδέτερο", "πληθυντικός"],
            },
        ]
        self.mktest_form(raw, expected)

    def test_noun_inflection_only_singular(self) -> None:
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
            {"tags": ["inflection-template"]},
            {"form": "αιδώς", "tags": ["singular", "nominative"]},
            {"form": "αιδούς", "tags": ["genitive", "singular"]},
            {"form": "αιδώ", "tags": ["accusative", "singular"]},
            {"form": "αιδώ", "tags": ["singular", "vocative"]},
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
            {"tags": ["inflection-template"]},
            {"form": "αβγούλι", "tags": ["singular", "nominative"]},
            {"form": "αβγούλια", "tags": ["nominative", "plural"]},
            # There should be no genitive
            {"form": "αβγούλι", "tags": ["accusative", "singular"]},
            {"form": "αβγούλια", "tags": ["accusative", "plural"]},
            {"form": "αβγούλι", "tags": ["singular", "vocative"]},
            {"form": "αβγούλια", "tags": ["vocative", "plural"]},
        ]
        self.mktest_form_no_raw_tags(raw, expected)

    def test_two_inflection_sources(self) -> None:
        # https://el.wiktionary.org/wiki/αμάξι
        # Contains forms from both declension and header
        self.wxr.wtp.add_page("Πρότυπο:-el-", 10, "Νέα ελληνικά (el)")
        self.wxr.wtp.add_page("Πρότυπο:ουσιαστικό", 10, "Ουσιαστικό")
        self.wxr.wtp.add_page(
            "Πρότυπο:el-κλίση-'τραγούδι'",
            10,
            """{| style="clear%3Aright%3B+float%3Aright%3B+margin-left%3A0.5em%3B+margin-bottom%3A0.5em%3Bbackground%3A%23ffffff%3B+color%3A%23000000%3B+border%3A1px+solid%23a1bdea%3B+text-align%3Aright%3B" rules="none" border="1" cellpadding="3" cellspacing="0"
|-
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B+text-align%3Acenter%3B+font-size%3A90%25%3B" align="center" | &darr;&nbsp;''πτώσεις''
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B" colspan="2" align="center" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[ενικός|<span title="%CE%B5%CE%BD%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''ενικός'''''</span>]]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
! style="background%3A%23a1bdea%3B" colspan="2" align="center" | &nbsp;&nbsp;[[πληθυντικός|<span title="%CF%80%CE%BB%CE%B7%CE%B8%CF%85%CE%BD%CF%84%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''πληθυντικός'''''</span>]]&nbsp;&nbsp;
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | [[ονομαστική|<span title="%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''ονομαστική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[αμάξι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμάξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[αμάξια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμάξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="%CE%B3%CE%B5%CE%BD%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''γενική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[του|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">του</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[αμαξιού|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμαξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ιού</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[των|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">των</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[αμαξιών|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμαξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ιών</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''αιτιατική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[το|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">το</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[αμάξι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμάξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τα|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τα</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[αμάξια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμάξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| style="background%3A%23d5e2f6%3B+text-align%3Aright%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="%CE%BA%CE%BB%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B+font-size%3A90%25%3B">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[αμάξι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμάξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ι</span>]]
| align="center" |
| align="left" | [[αμάξια|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">αμάξ</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ια</span>]]
|-
| colspan="5" align="left" style="background%3A%23eaf0fa%3B+font-size%3A80%25%3B+line-height%3A100%25%3B" | Οι καταλήξεις -ιού, -ια, -ιών προφέρονται με [[συνίζηση]].
|-
| colspan="5" align="right" style="text-align%3Aright%3B+background%3A%23eaf0fa%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" | [[:Κατηγορία:Ουσιαστικά που κλίνονται όπως το 'τραγούδι' (νέα ελληνικά)|Κατηγορία]]  όπως «[[Παράρτημα:Ουσιαστικά (νέα ελληνικά)/ουδέτερα#τραγούδι|τραγούδι]]» - [[Παράρτημα:Ουσιαστικά (νέα ελληνικά)|<span title="%CE%A0%CE%B1%CF%81%CE%AC%CF%81%CF%84%CE%B7%CE%BC%CE%B1%3A%CE%9F%CF%85%CF%83%CE%B9%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AC">Παράρτημα:Ουσιαστικά</span>]]
|}""",
        )
        self.wxr.wtp.add_page(
            "Πρότυπο:ο",
            10,
            """<span style="background:#ffffff; color:#002000;">''ουδέτερο''</span>""",
        )

        raw = """
=={{-el-}}==
{{el-κλίση-'τραγούδι'}}
==={{ουσιαστικό|el}}===
'''{{PAGENAME}}''' {{ο}}
* foo
        """.strip()

        word = "αμάξι"
        page_datas = parse_page(self.wxr, word, raw)
        received = page_datas[0]["forms"]

        expected = [
            {
                "form": "el-κλίση-'τραγούδι'",
                "tags": ["inflection-template"],
                "source": "declension",
            },
            {
                "form": "αμάξι",
                "tags": ["nominative", "singular"],
                "raw_tags": ["ενικός", "ονομαστική"],
                "source": "declension",
            },
            {
                "form": "αμάξια",
                "tags": ["nominative", "plural"],
                "raw_tags": ["ονομαστική", "πληθυντικός"],
                "source": "declension",
            },
            {
                "form": "αμαξιού",
                "tags": ["genitive", "singular"],
                "raw_tags": ["ενικός", "γενική"],
                "source": "declension",
            },
            {
                "form": "αμαξιών",
                "tags": ["genitive", "plural"],
                "raw_tags": ["γενική", "πληθυντικός"],
                "source": "declension",
            },
            {
                "form": "αμάξι",
                "tags": ["accusative", "singular"],
                "raw_tags": ["ενικός", "αιτιατική"],
                "source": "declension",
            },
            {
                "form": "αμάξια",
                "tags": ["accusative", "plural"],
                "raw_tags": ["αιτιατική", "πληθυντικός"],
                "source": "declension",
            },
            {
                "form": "αμάξι",
                "tags": ["singular", "vocative"],
                "raw_tags": ["ενικός", "κλητική"],
                "source": "declension",
            },
            {
                "form": "αμάξια",
                "tags": ["plural", "vocative"],
                "raw_tags": ["κλητική", "πληθυντικός"],
                "source": "declension",
            },
            {
                "form": "αμάξι",
                "tags": ["neuter"],
                "raw_tags": ["ουδέτερο"],
                "source": "header",
            },
        ]

        def normalize_forms(lst) -> None:
            for form in lst:
                if "raw_tags" in form:
                    form["raw_tags"].sort()
                if "tags" in form:
                    form["tags"].sort()

        normalize_forms(received)
        normalize_forms(expected)

        self.assertEqual(received, expected)

    def test_suffix_inflection(self) -> None:
        # https://el.wiktionary.org/wiki/-ωνιά
        raw = """
{| style="clear%3Aright%3B+float%3Aright%3B+margin-left%3A0.5em%3B+margin-bottom%3A0.5em%3Bbackground%3A%23ffffff%3B+color%3A%23000000%3B+border%3A1px+solid%23a1bdea%3B+text-align%3Aright%3B" rules="none" border="1" cellpadding="3" cellspacing="0"
|-
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B+text-align%3Acenter%3B+font-size%3A90%25%3B" align="center" | &darr;&nbsp;''πτώσεις''
! style="background%3A%23a1bdea%3B+border-right%3A1px+solid+%23c1d3f1%3B" colspan="2" align="center" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[ενικός|<span title="%CE%B5%CE%BD%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''ενικός'''''</span>]]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
! style="background%3A%23a1bdea%3B" colspan="2" align="center" | &nbsp;&nbsp;[[πληθυντικός|<span title="%CF%80%CE%BB%CE%B7%CE%B8%CF%85%CE%BD%CF%84%CE%B9%CE%BA%CF%8C%CF%82+%CE%B1%CF%81%CE%B9%CE%B8%CE%BC%CF%8C%CF%82" style="color%3Ablack%3B">'''''πληθυντικός'''''</span>]]&nbsp;&nbsp;
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | [[ονομαστική|<span title="%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''ονομαστική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[η|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">η</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[-ωνιά|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ά</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[οι|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">οι</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[-ωνιές|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ές</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="%CE%B3%CE%B5%CE%BD%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''γενική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[της|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">της</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[-ωνιάς|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">άς</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[των|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">των</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[-ωνιών|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ών</span>]]
|-
| style="background%3A%23d5e2f6%3B+border-bottom%3A1px+solid+%23eaf0fa%3B+text-align%3Aright%3B+font-size%3A90%25%3B" | &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B">'''''αιτιατική'''''</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[την|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τη(ν)</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B+border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[-ωνιά|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ά</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="center" | [[τις|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">τις</span>]]
| style="border-bottom%3A1px+solid+%23eaf0fa%3B" align="left" | [[-ωνιές|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ές</span>]]
|-
| style="background%3A%23d5e2f6%3B+text-align%3Aright%3B" | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="%CE%BA%CE%BB%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%80%CF%84%CF%8E%CF%83%CE%B7" style="color%3Ablack%3B+font-size%3A90%25%3B">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right%3A1px+solid+%23eaf0fa%3B" align="left" | [[-ωνιά|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ά</span>]]
| align="center" |
| align="left" | [[-ωνιές|<span style="color%3A%23002000%3B+font-weight%3Anormal%3B">-ωνι</span><span style="color%3A%23EB0000%3B+font-weight%3Anormal%3B">ές</span>]]
|-
| colspan="5" align="left" style="background%3A%23eaf0fa%3B+font-size%3A80%25%3B+line-height%3A100%25%3B" | Οι καταλήξεις προφέρονται με [[συνίζηση]].
|-
| colspan="5" align="right" style="text-align%3Aright%3B+background%3A%23eaf0fa%3B+font-size%3A70%25%3B+line-height%3A100%25%3B" | [[:Κατηγορία:Ουσιαστικά που κλίνονται όπως το 'καρδιά' (νέα ελληνικά)|Κατηγορία]]  όπως «[[Παράρτημα:Ουσιαστικά (νέα ελληνικά)/θηλυκά#καρδιά|καρδιά]]» - [[Παράρτημα:Ουσιαστικά (νέα ελληνικά)|<span title="%CE%A0%CE%B1%CF%81%CE%AC%CF%81%CF%84%CE%B7%CE%BC%CE%B1%3A%CE%9F%CF%85%CF%83%CE%B9%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AC">Παράρτημα:Ουσιαστικά</span>]]
|}
"""
        expected = [
            {"tags": ["inflection-template"]},
            {"form": "-ωνιά", "tags": ["singular", "nominative"]},
            {"form": "-ωνιές", "tags": ["nominative", "plural"]},
            {"form": "-ωνιάς", "tags": ["genitive", "singular"]},
            {"form": "-ωνιών", "tags": ["genitive", "plural"]},
            {"form": "-ωνιά", "tags": ["accusative", "singular"]},
            {"form": "-ωνιές", "tags": ["accusative", "plural"]},
            {"form": "-ωνιά", "tags": ["singular", "vocative"]},
            {"form": "-ωνιές", "tags": ["vocative", "plural"]},
        ]
        self.mktest_form_no_raw_tags(raw, expected)

    def test_noun_inflection_standard(self) -> None:
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
            {"tags": ["inflection-template"]},
            {"form": "μπόι", "tags": ["singular", "nominative"]},
            {"form": "μπόγια", "tags": ["nominative", "plural"]},
            {"form": "μπογιού", "tags": ["genitive", "singular"]},
            # {"form": "(μπογιών)", "tags": ["genitive", "plural"]},
            # v Should treat parenthesized forms as rare
            {"form": "μπογιών", "tags": ["genitive", "plural", "rare"]},
            {"form": "μπόι", "tags": ["accusative", "singular"]},
            {"form": "μπόγια", "tags": ["accusative", "plural"]},
            {"form": "μπόι", "tags": ["singular", "vocative"]},
            {"form": "μπόγια", "tags": ["vocative", "plural"]},
        ]
        self.mktest_form_no_raw_tags(raw, expected)

    def test_prefix_inflection(self) -> None:
        # https://el.wiktionary.org/wiki/-γράφος
        raw = """{|
|-
! style="background:#a1bdea; border-right:1px solid #c1d3f1; text-align:center; font-size:90%;" align="center"| &darr;&nbsp;''πτώσεις''
! style="background:#a1bdea; border-right:1px solid #c1d3f1;" colspan="2" align="center"| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[ενικός|<span title="ενικός αριθμός" style="color:black;">'''''ενικός'''''</span>]]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
! style="background:#a1bdea;" colspan="2" align="center"| &nbsp;&nbsp;[[πληθυντικός|<span title="πληθυντικός αριθμός" style="color:black;">'''''πληθυντικός'''''</span>]]&nbsp;&nbsp;
|-
| style="background:#d5e2f6; border-bottom:1px solid #eaf0fa; text-align:right; font-size:90%;"| [[ονομαστική|<span title="ονομαστική πτώση" style="color:black;">'''''ονομαστική'''''</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="center" | [[ο|<span style="color:#002000; font-weight:normal;">ο</span>]]/[[η|<span style="color:#002000; font-weight:normal;">η</span>]]
| style="border-bottom:1px solid #eaf0fa; border-right:1px solid #eaf0fa;" align="left" | [[-γράφος|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">ος</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="center" | [[οι|<span style="color:#002000; font-weight:normal;">οι</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="left" | [[-γράφοι|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">οι</span>]]
|-
| style="background:#d5e2f6; border-bottom:1px solid #eaf0fa; text-align:right; font-size:90%;"| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[γενική|<span title="γενική πτώση" style="color:black;">'''''γενική'''''</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="center" | <span style="white-space:nowrap">[[του|<span style="color:#002000; font-weight:normal;">του</span>]]/[[της|<span style="color:#002000; font-weight:normal;">της</span>]]</span>
| style="border-bottom:1px solid #eaf0fa; border-right:1px solid #eaf0fa;" align="left" | [[-γράφου|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">ου</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="center" | [[των|<span style="color:#002000; font-weight:normal;">των</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="left" | [[-γράφων|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">ων</span>]]
|-
| style="background:#d5e2f6; border-bottom:1px solid #eaf0fa; text-align:right; font-size:90%;"| &nbsp;&nbsp;&nbsp;&nbsp;[[αιτιατική|<span title="αιτιατική πτώση" style="color:black;">'''''αιτιατική'''''</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="center" | <span style="white-space:nowrap">[[τον|<span style="color:#002000; font-weight:normal;">τον</span>]]/[[την|<span style="color:#002000; font-weight:normal;">τη(ν)</span>]]</span>
| style="border-bottom:1px solid #eaf0fa; border-right:1px solid #eaf0fa;" align="left" | [[-γράφο|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">ο</span>]]
| style="border-bottom:1px solid #eaf0fa;" align="center" | <span style="white-space:nowrap">[[τους|<span style="color:#002000; font-weight:normal;">τους</span>]]/[[τις|<span style="color:#002000; font-weight:normal;">τις</span>]]</span>
| style="border-bottom:1px solid #eaf0fa;" align="left" | [[-γράφους|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">ους</span>]]
|-
| style="background:#d5e2f6; text-align:right;"| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[[κλητική|<span title="κλητική πτώση" style="color:black; font-size:90%;">'''''κλητική'''''</span>]]
| align="center" |
| style="border-right:1px solid #eaf0fa;" align="left" | [[-γράφε|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">ε</span>]]
| align="center" |
| align="left" | [[-γράφοι|<span class="skin-nightmode-reset-color" style="color:#002000; font-weight:normal;">-γράφ</span><span class="skin-nightmode-reset-color" style="color:#EB0000; font-weight:normal;">οι</span>]]
|-
| colspan="5" align="right" style="text-align:right; background:#eaf0fa; font-size:70%; line-height:100%;" | [[:Κατηγορία:Ουσιαστικά που κλίνονται όπως το 'ζωγράφος' (νέα ελληνικά)|Κατηγορία]]  όπως «[[Παράρτημα:Ουσιαστικά (νέα ελληνικά)/κοινά#ζωγράφος|ζωγράφος]]» - [[Παράρτημα:Ουσιαστικά (νέα ελληνικά)|<span title="Παράρτημα:Ουσιαστικά">Παράρτημα:Ουσιαστικά</span>]]
|}"""
        expected = [
            {"tags": ["inflection-template"]},
            {
                "form": "-γράφος",
                "tags": ["singular", "nominative"],
                "raw_tags": ["ενικός", "ονομαστική"],
            },
            {
                "form": "-γράφοι",
                "tags": ["nominative", "plural"],
                "raw_tags": ["ονομαστική", "πληθυντικός"],
            },
            {
                "form": "-γράφου",
                "tags": ["genitive", "singular"],
                "raw_tags": ["γενική", "ενικός"],
            },
            {
                "form": "-γράφων",
                "tags": ["genitive", "plural"],
                "raw_tags": ["γενική", "πληθυντικός"],
            },
            {
                "form": "-γράφο",
                "tags": ["accusative", "singular"],
                "raw_tags": ["αιτιατική", "ενικός"],
            },
            {
                "form": "-γράφους",
                "tags": ["accusative", "plural"],
                "raw_tags": ["αιτιατική", "πληθυντικός"],
            },
            {
                "form": "-γράφε",
                "tags": ["singular", "vocative"],
                "raw_tags": ["ενικός", "κλητική"],
            },
            {
                "form": "-γράφοι",
                "tags": ["vocative", "plural"],
                "raw_tags": ["κλητική", "πληθυντικός"],
            },
        ]
        self.mktest_form_no_raw_tags(raw, expected)

    def test_el_conjugation_table(self) -> None:
        # Section of https://el.wiktionary.org/wiki/πίνω
        # {{el-κλίσ-'μπαίνω'|θαορ=ήπι|θμελλ=πι}}
        # Expanded via 'wxr.wtp.node_to_text(node)' at the start of
        # 'table.process_inflection_section'
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

        expected = [
            {"tags": ["inflection-template"]},
            {
                "form": "πίνω",
                "tags": ["present", "first-person", "singular"],
                "raw_tags": ["Ενεστώτας", "Εξακολουθητικοί χρόνοι", "α' ενικ."],
            },
            {
                "form": "έπινα",
                "tags": ["imperfect", "first-person", "singular"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Παρατατικός",
                    "α' ενικ.",
                ],
            },
            {
                "form": "θα πίνω",
                "tags": ["future", "imperfect", "first-person", "singular"],
                "raw_tags": ["Εξ. Μέλλ.", "Εξακολουθητικοί χρόνοι", "α' ενικ."],
            },
            {
                "form": "να πίνω",
                "tags": ["subjunctive", "first-person", "singular"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Υποτακτική",
                    "α' ενικ.",
                ],
            },
            {
                "form": "πίνοντας",
                "tags": ["participle"],
                "raw_tags": ["Εξακολουθητικοί χρόνοι", "Μετοχή"],
            },
            {
                "form": "πίνεις",
                "tags": ["present", "second-person", "singular"],
                "raw_tags": ["Ενεστώτας", "Εξακολουθητικοί χρόνοι", "β' ενικ."],
            },
            {
                "form": "έπινες",
                "tags": ["imperfect", "second-person", "singular"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Παρατατικός",
                    "β' ενικ.",
                ],
            },
            {
                "form": "θα πίνεις",
                "tags": ["future", "imperfect", "second-person", "singular"],
                "raw_tags": ["Εξ. Μέλλ.", "Εξακολουθητικοί χρόνοι", "β' ενικ."],
            },
            {
                "form": "να πίνεις",
                "tags": ["subjunctive", "second-person", "singular"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Υποτακτική",
                    "β' ενικ.",
                ],
            },
            {
                "form": "πίνε",
                "tags": ["imperative", "second-person", "singular"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Προστακτική",
                    "β' ενικ.",
                ],
            },
        ]

        self.mktest_form(raw, expected)

    def test_el_conjugation_table_non_standard(self) -> None:
        # https://el.wiktionary.org/wiki/τρώω
        raw = """
        {| style="background%3A%23F0F0F0"
        |-
        ! colspan="8" style="background%3A%23C0C0C0" | <center> προσωπικές εγκλίσεις </center>
        |-
        ! colspan="2" rowspan="2" style="background%3A%23C0C0C0" | πρόσωπο
        ! colspan="3" style="background%3A%23C0C0C0" | ενικός
        ! colspan="3" style="background%3A%23C0C0C0" | πληθυντικός
        |-
        ! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | πρώτο
        ! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | δεύτερο
        ! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | τρίτο
        ! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | πρώτο
        ! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | δεύτερο
        ! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | τρίτο
        |-
        ! style="background%3A%23c0cfe4" colspan="2" | οριστική
        ! style="background%3A%23c0cfe4" | εγώ
        ! style="background%3A%23c0cfe4" | εσύ
        ! style="background%3A%23c0cfe4" | αυτός
        ! style="background%3A%23c0cfe4" | εμείς
        ! style="background%3A%23c0cfe4" | εσείς
        ! style="background%3A%23c0cfe4" | αυτοί
        |-
        ! rowspan="3" style="background%3A%23c0cfe4" | μονολεκτικοί<br>χρόνοι
        ! style="height%3A3em%3Bbackground%3A%23c0cfe4" | ενεστώτας
        | τρώω
        | τρως
        | τρώει
        | τρώμε
        | τρώτε
        | τρώνε
        |-
        ! style="height%3A3em%3Bbackground%3A%23c0cfe4" | παρατατικός
        | έτρωγα
        | έτρωγες
        | έτρωγε
        | τρώγαμε
        | τρώγατε
        | έτρωγαν / τρώγανε
        |}
        """

        expected = [
            {"tags": ["inflection-template"]},
            {
                "form": "τρώω",
                "tags": ["first-person", "singular", "present"],
                "raw_tags": [
                    "εγώ",
                    "ενεστώτας",
                    "ενικός",
                    "μονολεκτικοί\nχρόνοι",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρως",
                "tags": ["present", "singular", "second-person"],
                "raw_tags": [
                    "ενεστώτας",
                    "ενικός",
                    "εσύ",
                    "μονολεκτικοί\nχρόνοι",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρώει",
                "tags": ["third-person", "singular", "present"],
                "raw_tags": [
                    "αυτός",
                    "ενεστώτας",
                    "ενικός",
                    "μονολεκτικοί\nχρόνοι",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρώμε",
                "tags": ["first-person", "plural", "present"],
                "raw_tags": [
                    "εμείς",
                    "ενεστώτας",
                    "μονολεκτικοί\nχρόνοι",
                    "πληθυντικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρώτε",
                "tags": ["present", "second-person", "plural"],
                "raw_tags": [
                    "ενεστώτας",
                    "εσείς",
                    "μονολεκτικοί\nχρόνοι",
                    "πληθυντικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρώνε",
                "tags": ["third-person", "plural", "present"],
                "raw_tags": [
                    "αυτοί",
                    "ενεστώτας",
                    "μονολεκτικοί\nχρόνοι",
                    "πληθυντικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "έτρωγα",
                "tags": ["first-person", "singular", "imperfect"],
                "raw_tags": [
                    "εγώ",
                    "ενικός",
                    "μονολεκτικοί\nχρόνοι",
                    "παρατατικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "έτρωγες",
                "tags": ["singular", "second-person", "imperfect"],
                "raw_tags": [
                    "ενικός",
                    "εσύ",
                    "μονολεκτικοί\nχρόνοι",
                    "παρατατικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "έτρωγε",
                "tags": ["third-person", "singular", "imperfect"],
                "raw_tags": [
                    "αυτός",
                    "ενικός",
                    "μονολεκτικοί\nχρόνοι",
                    "παρατατικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρώγαμε",
                "tags": ["first-person", "plural", "imperfect"],
                "raw_tags": [
                    "εμείς",
                    "μονολεκτικοί\nχρόνοι",
                    "παρατατικός",
                    "πληθυντικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρώγατε",
                "tags": ["second-person", "plural", "imperfect"],
                "raw_tags": [
                    "εσείς",
                    "μονολεκτικοί\nχρόνοι",
                    "παρατατικός",
                    "πληθυντικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "έτρωγαν",
                "tags": ["third-person", "plural", "imperfect"],
                "raw_tags": [
                    "αυτοί",
                    "μονολεκτικοί\nχρόνοι",
                    "παρατατικός",
                    "πληθυντικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
            {
                "form": "τρώγανε",
                "tags": ["third-person", "plural", "imperfect"],
                "raw_tags": [
                    "αυτοί",
                    "μονολεκτικοί\nχρόνοι",
                    "παρατατικός",
                    "πληθυντικός",
                    "προσωπικές εγκλίσεις",
                ],
            },
        ]

        self.mktest_form(raw, expected)

    def test_el_conjugation_table_variants(self) -> None:
        # Section of https://el.wiktionary.org/wiki/πίνω
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
        | style="background%3A%23c0c0c0" | γ' πληθ.
        | πίνουν(ε)
        | έπιναν<br>πίναν(ε)
        | θα πίνουν(ε)
        | να πίνουν(ε)
        |

        |}
        """.strip()

        expected = [
            {"tags": ["inflection-template"]},
            {
                "form": "πίνουν",
                "tags": ["present", "third-person", "plural"],
                "raw_tags": ["Ενεστώτας", "Εξακολουθητικοί χρόνοι", "γ' πληθ."],
            },
            {
                "form": "πίνουνε",
                "tags": ["present", "third-person", "plural"],
                "raw_tags": ["Ενεστώτας", "Εξακολουθητικοί χρόνοι", "γ' πληθ."],
            },
            {
                "form": "έπιναν",
                "tags": ["imperfect", "third-person", "plural"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Παρατατικός",
                    "γ' πληθ.",
                ],
            },
            {
                "form": "πίναν",
                "tags": ["imperfect", "third-person", "plural"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Παρατατικός",
                    "γ' πληθ.",
                ],
            },
            {
                "form": "πίνανε",
                "tags": ["imperfect", "third-person", "plural"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Παρατατικός",
                    "γ' πληθ.",
                ],
            },
            {
                "form": "θα πίνουν",
                "tags": ["future", "imperfect", "third-person", "plural"],
                "raw_tags": ["Εξ. Μέλλ.", "Εξακολουθητικοί χρόνοι", "γ' πληθ."],
            },
            {
                "form": "θα πίνουνε",
                "tags": ["future", "imperfect", "third-person", "plural"],
                "raw_tags": ["Εξ. Μέλλ.", "Εξακολουθητικοί χρόνοι", "γ' πληθ."],
            },
            {
                "form": "να πίνουν",
                "tags": ["subjunctive", "third-person", "plural"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Υποτακτική",
                    "γ' πληθ.",
                ],
            },
            {
                "form": "να πίνουνε",
                "tags": ["subjunctive", "third-person", "plural"],
                "raw_tags": [
                    "Εξακολουθητικοί χρόνοι",
                    "Υποτακτική",
                    "γ' πληθ.",
                ],
            },
        ]

        self.mktest_form(raw, expected)

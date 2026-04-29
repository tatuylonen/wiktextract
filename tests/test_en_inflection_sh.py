# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.inflection import parse_inflection_section
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class InflTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def xinfl(self, word, lang, pos, section, text):
        """Runs a single inflection table parsing test, and returns ``data``."""
        self.wxr.wtp.start_page(word)
        self.wxr.wtp.start_section(lang)
        self.wxr.wtp.start_subsection(pos)
        tree = self.wxr.wtp.parse(text)
        data = {}
        parse_inflection_section(self.wxr, data, word, lang, pos, section, tree)
        return data

    def test_SerboCroatian_adj1(self):
        ret = self.xinfl(
            "maorski",
            "Serbo-Croatian",
            "adj",
            "Declension",
            """
<div class="NavFrame" style>
<div class="NavHead" style="background%3A%23eff7ff">Declension of <i class="Latn+mention" lang="sh">maorski</i></div>
<div class="NavContent">

{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+font-size%3A12px%3B+width%3A100%25" class="inflection-table"

|-

! style="background%3A%23d9ebff%3B+width%3A25%25" colspan="2" |singular


! style="background%3A%23d9ebff" |masculine


! style="background%3A%23d9ebff" |feminine


! style="background%3A%23d9ebff" |neuter


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''nominative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorska</span>


|<span class="Latn" lang="sh">maorsko</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''genitive'''


|<span class="Latn" lang="sh">maorskog(a)</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorskog(a)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''dative'''


|<span class="Latn" lang="sh">maorskom(u/e)</span>


|<span class="Latn" lang="sh">maorskoj</span>


|<span class="Latn" lang="sh">maorskom(u/e)</span>


|-

! style="background-color%3A%23eff7ff" |'''accusative'''


! style="background%3A%23eff7ff" |<small>inanimate</small><br><small>animate</small>


|<span class="Latn" lang="sh">maorski<br>maorskog(a)</span>


|<span class="Latn" lang="sh">maorsku</span>


|<span class="Latn" lang="sh">maorsko</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''vocative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorska</span>


|<span class="Latn" lang="sh">maorsko</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''locative'''


|<span class="Latn" lang="sh">maorskom(e/u)</span>


|<span class="Latn" lang="sh">maorskoj</span>


|<span class="Latn" lang="sh">maorskom(e/u)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''instrumental'''


|<span class="Latn" lang="sh">maorskim</span>


|<span class="Latn" lang="sh">maorskom</span>


|<span class="Latn" lang="sh">maorskim</span>


|-

! style="background%3A%23d9ebff%3B+width%3A30%25" colspan="2" |plural


! style="background%3A%23d9ebff" |masculine


! style="background%3A%23d9ebff" |feminine


! style="background%3A%23d9ebff" |neuter


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''nominative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorska</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''genitive'''


|<span class="Latn" lang="sh">maorskih</span>


|<span class="Latn" lang="sh">maorskih</span>


|<span class="Latn" lang="sh">maorskih</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''dative'''


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''accusative'''


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorska</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''vocative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorska</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''locative'''


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''instrumental'''


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|}
</div></div>

[[Category:sh:Languages]]
""",
        )  # noqa: E501
        expected = {
            "forms": [
                {
                    "form": "no-table-tags",
                    "source": "Declension",
                    "tags": ["table-tags"],
                },
                {
                    "form": "maorski",
                    "source": "Declension",
                    "tags": ["masculine", "nominative", "singular"],
                },
                {
                    "form": "maorska",
                    "source": "Declension",
                    "tags": ["feminine", "nominative", "singular"],
                },
                {
                    "form": "maorsko",
                    "source": "Declension",
                    "tags": ["neuter", "nominative", "singular"],
                },
                {
                    "form": "maorskog",
                    "source": "Declension",
                    "tags": ["genitive", "masculine", "singular"],
                },
                {
                    "form": "maorskoga",
                    "source": "Declension",
                    "tags": ["genitive", "masculine", "singular"],
                },
                {
                    "form": "maorske",
                    "source": "Declension",
                    "tags": ["feminine", "genitive", "singular"],
                },
                {
                    "form": "maorskog",
                    "source": "Declension",
                    "tags": ["genitive", "neuter", "singular"],
                },
                {
                    "form": "maorskoga",
                    "source": "Declension",
                    "tags": ["genitive", "neuter", "singular"],
                },
                {
                    "form": "maorskomu",
                    "source": "Declension",
                    "tags": ["dative", "masculine", "singular"],
                },
                {
                    "form": "maorskome",
                    "source": "Declension",
                    "tags": ["dative", "masculine", "singular"],
                },
                {
                    "form": "maorskoj",
                    "source": "Declension",
                    "tags": ["dative", "feminine", "singular"],
                },
                {
                    "form": "maorskomu",
                    "source": "Declension",
                    "tags": ["dative", "neuter", "singular"],
                },
                {
                    "form": "maorskome",
                    "source": "Declension",
                    "tags": ["dative", "neuter", "singular"],
                },
                {
                    "form": "maorski",
                    "source": "Declension",
                    "tags": [
                        "accusative",
                        "inanimate",
                        "masculine",
                        "singular",
                    ],
                },
                {
                    "form": "maorsku",
                    "source": "Declension",
                    "tags": ["accusative", "feminine", "singular"],
                },
                {
                    "form": "maorsko",
                    "source": "Declension",
                    "tags": ["accusative", "neuter", "singular"],
                },
                {
                    "form": "maorskog",
                    "source": "Declension",
                    "tags": ["accusative", "animate", "masculine", "singular"],
                },
                {
                    "form": "maorskoga",
                    "source": "Declension",
                    "tags": ["accusative", "animate", "masculine", "singular"],
                },
                {
                    "form": "maorski",
                    "source": "Declension",
                    "tags": ["masculine", "singular", "vocative"],
                },
                {
                    "form": "maorska",
                    "source": "Declension",
                    "tags": ["feminine", "singular", "vocative"],
                },
                {
                    "form": "maorsko",
                    "source": "Declension",
                    "tags": ["neuter", "singular", "vocative"],
                },
                {
                    "form": "maorskome",
                    "source": "Declension",
                    "tags": ["locative", "masculine", "singular"],
                },
                {
                    "form": "maorskomu",
                    "source": "Declension",
                    "tags": ["locative", "masculine", "singular"],
                },
                {
                    "form": "maorskoj",
                    "source": "Declension",
                    "tags": ["feminine", "locative", "singular"],
                },
                {
                    "form": "maorskome",
                    "source": "Declension",
                    "tags": ["locative", "neuter", "singular"],
                },
                {
                    "form": "maorskomu",
                    "source": "Declension",
                    "tags": ["locative", "neuter", "singular"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["instrumental", "masculine", "singular"],
                },
                {
                    "form": "maorskom",
                    "source": "Declension",
                    "tags": ["feminine", "instrumental", "singular"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["instrumental", "neuter", "singular"],
                },
                {
                    "form": "maorski",
                    "source": "Declension",
                    "tags": ["masculine", "nominative", "plural"],
                },
                {
                    "form": "maorske",
                    "source": "Declension",
                    "tags": ["feminine", "nominative", "plural"],
                },
                {
                    "form": "maorska",
                    "source": "Declension",
                    "tags": ["neuter", "nominative", "plural"],
                },
                {
                    "form": "maorskih",
                    "source": "Declension",
                    "tags": ["genitive", "masculine", "plural"],
                },
                {
                    "form": "maorskih",
                    "source": "Declension",
                    "tags": ["feminine", "genitive", "plural"],
                },
                {
                    "form": "maorskih",
                    "source": "Declension",
                    "tags": ["genitive", "neuter", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["dative", "masculine", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["dative", "masculine", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["dative", "feminine", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["dative", "feminine", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["dative", "neuter", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["dative", "neuter", "plural"],
                },
                {
                    "form": "maorske",
                    "source": "Declension",
                    "tags": ["accusative", "masculine", "plural"],
                },
                {
                    "form": "maorske",
                    "source": "Declension",
                    "tags": ["accusative", "feminine", "plural"],
                },
                {
                    "form": "maorska",
                    "source": "Declension",
                    "tags": ["accusative", "neuter", "plural"],
                },
                {
                    "form": "maorski",
                    "source": "Declension",
                    "tags": ["masculine", "plural", "vocative"],
                },
                {
                    "form": "maorske",
                    "source": "Declension",
                    "tags": ["feminine", "plural", "vocative"],
                },
                {
                    "form": "maorska",
                    "source": "Declension",
                    "tags": ["neuter", "plural", "vocative"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["locative", "masculine", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["locative", "masculine", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["feminine", "locative", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["feminine", "locative", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["locative", "neuter", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["locative", "neuter", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["instrumental", "masculine", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["instrumental", "masculine", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["feminine", "instrumental", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["feminine", "instrumental", "plural"],
                },
                {
                    "form": "maorskim",
                    "source": "Declension",
                    "tags": ["instrumental", "neuter", "plural"],
                },
                {
                    "form": "maorskima",
                    "source": "Declension",
                    "tags": ["instrumental", "neuter", "plural"],
                },
            ],
        }
        self.assertEqual(expected, ret)

    def test_SerboCroatian_verb1(self):
        ret = self.xinfl(
            "nametati",
            "Serbo-Croatian",
            "verb",
            "Conjugation",
            """
<div class="NavFrame">
<div class="NavHead" style="background%3A%23d9ebff%3B">Conjugation of <i class="Latn+mention" lang="sh">nametati</i></div>
<div class="NavContent">

{| class="inflection-table" style="text-align%3Acenter%3B+width%3A+100%25%3B"

|-

! style="height%3A3em%3B+background-color%3A%23d9ebff%3B" colspan="2" | '''Infinitive: <span class="Latn" lang="sh">[[nametati#Serbo-Croatian|nametati]]</span>'''


! colspan="2" style="background-color%3A%23d9ebff%3B" | '''Present verbal adverb: <span class="Latn" lang="sh">[[namećući#Serbo-Croatian|nàmećūći]]</span>'''


! colspan="2" style="background-color%3A%23d9ebff%3B" | '''Past verbal adverb: &mdash;'''


! colspan="2" style="background-color%3A%23d9ebff%3B" | '''Verbal noun: <span class="Latn" lang="sh">[[nametanje#Serbo-Croatian|namètānje]]</span>'''


|- style="background-color%3A%23d5d5ff%3B"

! colspan="2" | '''Number'''


! colspan="3" | '''Singular'''


! colspan="3" | '''Plural'''


|- style="background-color%3A%23d5d5ff%3B"

! colspan="2" | '''Person'''


! style="width%3A+13.3%25%3B" | '''1st'''


! style="width%3A+13.3%25%3B" | '''2nd'''


! style="width%3A+13.3%25%3B" | '''3rd'''


! style="width%3A+13.3%25%3B" | '''1st'''


! style="width%3A+13.3%25%3B" | '''2nd'''


! style="width%3A+13.3%25%3B" | '''3rd'''


|- style="background-color%3A%23ccddff%3B"

! colspan="2" | '''Verbal forms'''


! '''<span class="Latn" lang="sh">[[ja#Serbo-Croatian|ja]]</span>'''


! '''<span class="Latn" lang="sh">[[ti#Serbo-Croatian|ti]]</span>'''


! '''<span class="Latn" lang="sh">[[on#Serbo-Croatian|on]]</span>''' / '''<span class="Latn" lang="sh">[[ona#Serbo-Croatian|ona]]</span>''' / '''<span class="Latn" lang="sh">[[ono#Serbo-Croatian|ono]]</span>'''


! '''<span class="Latn" lang="sh">[[mi#Serbo-Croatian|mi]]</span>'''


! '''<span class="Latn" lang="sh">[[vi#Serbo-Croatian|vi]]</span>'''


! '''<span class="Latn" lang="sh">[[oni#Serbo-Croatian|oni]]</span>''' / '''<span class="Latn" lang="sh">[[one#Serbo-Croatian|one]]</span>''' / '''<span class="Latn" lang="sh">[[ona#Serbo-Croatian|ona]]</span>'''


|-

! colspan="2" style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Present'''


| <span class="Latn" lang="sh">[[namećem#Serbo-Croatian|namećem]]</span>


| <span class="Latn" lang="sh">[[namećeš#Serbo-Croatian|namećeš]]</span>


| <span class="Latn" lang="sh">[[nameće#Serbo-Croatian|nameće]]</span>


| <span class="Latn" lang="sh">[[namećemo#Serbo-Croatian|namećemo]]</span>


| <span class="Latn" lang="sh">[[namećete#Serbo-Croatian|namećete]]</span>


| <span class="Latn" lang="sh">[[nameću#Serbo-Croatian|nameću]]</span>


|-

! rowspan="2" style="background-color%3A%23ccddff%3B" | '''Future'''


| style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Future I'''


| <span class="Latn" lang="sh">[[nametat#Serbo-Croatian|nametat]] [[ću#Serbo-Croatian|ću]]</span><sup>1</sup><br><span class="Latn" lang="sh">[[nametaću#Serbo-Croatian|nametaću]]</span>


| <span class="Latn" lang="sh">[[nametat#Serbo-Croatian|nametat]] [[ćeš#Serbo-Croatian|ćeš]]</span><sup>1</sup><br><span class="Latn" lang="sh">[[nametaćeš#Serbo-Croatian|nametaćeš]]</span>


| <span class="Latn" lang="sh">[[nametat#Serbo-Croatian|nametat]] [[će#Serbo-Croatian|će]]</span><sup>1</sup><br><span class="Latn" lang="sh">[[nametaće#Serbo-Croatian|nametaće]]</span>


| <span class="Latn" lang="sh">[[nametat#Serbo-Croatian|nametat]] [[ćemo#Serbo-Croatian|ćemo]]</span><sup>1</sup><br><span class="Latn" lang="sh">[[nametaćemo#Serbo-Croatian|nametaćemo]]</span>


| <span class="Latn" lang="sh">[[nametat#Serbo-Croatian|nametat]] [[ćete#Serbo-Croatian|ćete]]</span><sup>1</sup><br><span class="Latn" lang="sh">[[nametaćete#Serbo-Croatian|nametaćete]]</span>


| <span class="Latn" lang="sh">[[nametat#Serbo-Croatian|nametat]] [[će#Serbo-Croatian|će]]</span><sup>1</sup><br><span class="Latn" lang="sh">[[nametaće#Serbo-Croatian|nametaće]]</span>


|-

! style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Future II'''


| <span class="Latn" lang="sh">[[budem#Serbo-Croatian|bȕdēm]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[budeš#Serbo-Croatian|bȕdēš]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bude#Serbo-Croatian|bȕdē]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[budemo#Serbo-Croatian|bȕdēmo]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[budete#Serbo-Croatian|bȕdēte]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[budu#Serbo-Croatian|bȕdū]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


|-

! rowspan="3" style="background-color%3A%23ccddff%3B" | '''Past'''


! style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Perfect'''


| <span class="Latn" lang="sh">[[nametao#Serbo-Croatian|nametao]] [[sam#Serbo-Croatian|sam]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametao#Serbo-Croatian|nametao]] [[si#Serbo-Croatian|si]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametao#Serbo-Croatian|nametao]] [[je#Serbo-Croatian|je]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametali#Serbo-Croatian|nametali]] [[smo#Serbo-Croatian|smo]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametali#Serbo-Croatian|nametali]] [[ste#Serbo-Croatian|ste]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametali#Serbo-Croatian|nametali]] [[su#Serbo-Croatian|su]]</span><sup>2</sup>


|-

! style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Pluperfect'''<sup>3</sup>


| <span class="Latn" lang="sh">[[bio#Serbo-Croatian|bȉo]] [[sam#Serbo-Croatian|sam]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bio#Serbo-Croatian|bȉo]] [[si#Serbo-Croatian|si]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bio#Serbo-Croatian|bȉo]] [[je#Serbo-Croatian|je]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bili#Serbo-Croatian|bíli]] [[smo#Serbo-Croatian|smo]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bili#Serbo-Croatian|bíli]] [[ste#Serbo-Croatian|ste]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bili#Serbo-Croatian|bíli]] [[su#Serbo-Croatian|su]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


|-

| style="height%3A+3em%3B+background%3A+%23ccddff%3B" | '''Imperfect'''


| <span class="Latn" lang="sh">[[nametah#Serbo-Croatian|nametah]]</span>


| <span class="Latn" lang="sh">[[nametaše#Serbo-Croatian|nametaše]]</span>


| <span class="Latn" lang="sh">[[nametaše#Serbo-Croatian|nametaše]]</span>


| <span class="Latn" lang="sh">[[nametasmo#Serbo-Croatian|nametasmo]]</span>


| <span class="Latn" lang="sh">[[nametaste#Serbo-Croatian|nametaste]]</span>


| <span class="Latn" lang="sh">[[nametahu#Serbo-Croatian|nametahu]]</span>


|-

! colspan="2" style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Conditional I'''


| <span class="Latn" lang="sh">[[nametao#Serbo-Croatian|nametao]] [[bih#Serbo-Croatian|bih]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametao#Serbo-Croatian|nametao]] [[bi#Serbo-Croatian|bi]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametao#Serbo-Croatian|nametao]] [[bi#Serbo-Croatian|bi]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametali#Serbo-Croatian|nametali]] [[bismo#Serbo-Croatian|bismo]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametali#Serbo-Croatian|nametali]] [[biste#Serbo-Croatian|biste]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[nametali#Serbo-Croatian|nametali]] [[bi#Serbo-Croatian|bi]]</span><sup>2</sup>


|-

! colspan="2" style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Conditional II'''<sup>4</sup>


| <span class="Latn" lang="sh">[[bio#Serbo-Croatian|bȉo]] [[bih#Serbo-Croatian|bih]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bio#Serbo-Croatian|bȉo]] [[bi#Serbo-Croatian|bi]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bio#Serbo-Croatian|bȉo]] [[bi#Serbo-Croatian|bi]] [[nametao#Serbo-Croatian|nametao]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bili#Serbo-Croatian|bíli]] [[bismo#Serbo-Croatian|bismo]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bili#Serbo-Croatian|bíli]] [[biste#Serbo-Croatian|biste]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


| <span class="Latn" lang="sh">[[bili#Serbo-Croatian|bíli]] [[bi#Serbo-Croatian|bi]] [[nametali#Serbo-Croatian|nametali]]</span><sup>2</sup>


|-

! colspan="2" style="height%3A3em%3B+background-color%3A%23ccddff%3B" | '''Imperative'''


| &mdash;


| <span class="Latn" lang="sh">[[nameći#Serbo-Croatian|nameći]]</span>


| &mdash;


| <span class="Latn" lang="sh">[[namećimo#Serbo-Croatian|namećimo]]</span>


| <span class="Latn" lang="sh">[[namećite#Serbo-Croatian|namećite]]</span>


| &mdash;


|-

! colspan="2" style="height%3A3em%3B+background-color%3A%23d9ebff%3B" | '''Active past participle'''


| colspan="3" | <span class="Latn" lang="sh">[[nametao#Serbo-Croatian|nametao]]</span>&nbsp;<span class="gender"><abbr title="masculine+gender">m</abbr></span> / <span class="Latn" lang="sh">[[nametala#Serbo-Croatian|nametala]]</span>&nbsp;<span class="gender"><abbr title="feminine+gender">f</abbr></span> / <span class="Latn" lang="sh">[[nametalo#Serbo-Croatian|nametalo]]</span>&nbsp;<span class="gender"><abbr title="neuter+gender">n</abbr></span>


| colspan="3" | <span class="Latn" lang="sh">[[nametali#Serbo-Croatian|nametali]]</span>&nbsp;<span class="gender"><abbr title="masculine+gender">m</abbr></span> / <span class="Latn" lang="sh">[[nametale#Serbo-Croatian|nametale]]</span>&nbsp;<span class="gender"><abbr title="feminine+gender">f</abbr></span> / <span class="Latn" lang="sh">[[nametala#Serbo-Croatian|nametala]]</span>&nbsp;<span class="gender"><abbr title="neuter+gender">n</abbr></span>


|-

| colspan="2" style="height%3A+3em%3B+background%3A+%23d9ebff%3B" | '''Passive past participle'''


| colspan="3" | <span class="Latn" lang="sh">[[nametan#Serbo-Croatian|nametan]]</span>&nbsp;<span class="gender"><abbr title="masculine+gender">m</abbr></span> / <span class="Latn" lang="sh">[[nametana#Serbo-Croatian|nametana]]</span>&nbsp;<span class="gender"><abbr title="feminine+gender">f</abbr></span> / <span class="Latn" lang="sh">[[nametano#Serbo-Croatian|nametano]]</span>&nbsp;<span class="gender"><abbr title="neuter+gender">n</abbr></span>


| colspan="3" | <span class="Latn" lang="sh">[[nametani#Serbo-Croatian|nametani]]</span>&nbsp;<span class="gender"><abbr title="masculine+gender">m</abbr></span> / <span class="Latn" lang="sh">[[nametane#Serbo-Croatian|nametane]]</span>&nbsp;<span class="gender"><abbr title="feminine+gender">f</abbr></span> / <span class="Latn" lang="sh">[[nametana#Serbo-Croatian|nametana]]</span>&nbsp;<span class="gender"><abbr title="neuter+gender">n</abbr></span>


|-

| colspan="8" style="text-align%3Aleft%3B" | <sup>1</sup> &nbsp; Croatian spelling: others omit the infinitive suffix completely and bind the clitic.<br><sup>2</sup> &nbsp; For masculine nouns; a feminine or neuter agent would use the feminine and neuter gender forms of the active past participle and auxiliary verb, respectively.<br><sup>3</sup> &nbsp; Often replaced by the past perfect in colloquial speech, i.e. the auxiliary verb ''[[biti]]'' (to be) is routinely dropped.
<sup>4</sup> &nbsp; Often replaced by the conditional I in colloquial speech, i.e. the auxiliary verb ''[[biti]]'' (to be) is routinely dropped.
<br>&nbsp; * Note: The aorist and imperfect have nowadays fallen into disuse in many dialects and therefore they are routinely replaced by the past perfect in both formal and colloquial speech.


|}

</div></div>
""",
        )  # noqa: E501, W291
        expected = {
            "forms": [
                {
                    "form": "no-table-tags",
                    "source": "Conjugation",
                    "tags": ["table-tags"],
                },
                {
                    "form": "nametati",
                    "tags": ["infinitive"],
                    "source": "Conjugation",
                },
                {
                    "form": "nàmećūći",
                    "tags": ["adverbial", "present"],
                    "source": "Conjugation",
                    "links": [("nàmećūći", "namećući#Serbo-Croatian")],
                },
                {
                    "form": "-",
                    "tags": ["adverbial", "past"],
                    "source": "Conjugation",
                },
                {
                    "form": "namètānje",
                    "tags": ["noun-from-verb"],
                    "source": "Conjugation",
                    "links": [("namètānje", "nametanje#Serbo-Croatian")],
                },
                {
                    "form": "namećem",
                    "tags": ["first-person", "present", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "namećeš",
                    "tags": ["present", "second-person", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nameće",
                    "tags": ["present", "singular", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "namećemo",
                    "tags": ["first-person", "plural", "present"],
                    "source": "Conjugation",
                },
                {
                    "form": "namećete",
                    "tags": ["plural", "present", "second-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nameću",
                    "tags": ["plural", "present", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametat ću",
                    "tags": ["first-person", "future", "future-i", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaću",
                    "tags": ["first-person", "future", "future-i", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametat ćeš",
                    "tags": ["future", "future-i", "second-person", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaćeš",
                    "tags": ["future", "future-i", "second-person", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametat će",
                    "tags": ["future", "future-i", "singular", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaće",
                    "tags": ["future", "future-i", "singular", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametat ćemo",
                    "tags": ["first-person", "future", "future-i", "plural"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaćemo",
                    "tags": ["first-person", "future", "future-i", "plural"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametat ćete",
                    "tags": ["future", "future-i", "plural", "second-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaćete",
                    "tags": ["future", "future-i", "plural", "second-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametat će",
                    "tags": ["future", "future-i", "plural", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaće",
                    "tags": ["future", "future-i", "plural", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "bȕdēm nametao",
                    "tags": ["first-person", "future", "future-ii", "singular"],
                    "source": "Conjugation",
                    "links": [
                        ("bȕdēm", "budem#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȕdēš nametao",
                    "tags": [
                        "future",
                        "future-ii",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [
                        ("bȕdēš", "budeš#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȕdē nametao",
                    "tags": ["future", "future-ii", "singular", "third-person"],
                    "source": "Conjugation",
                    "links": [
                        ("bȕdē", "bude#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȕdēmo nametali",
                    "tags": ["first-person", "future", "future-ii", "plural"],
                    "source": "Conjugation",
                    "links": [
                        ("bȕdēmo", "budemo#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȕdēte nametali",
                    "tags": ["future", "future-ii", "plural", "second-person"],
                    "source": "Conjugation",
                    "links": [
                        ("bȕdēte", "budete#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȕdū nametali",
                    "tags": ["future", "future-ii", "plural", "third-person"],
                    "source": "Conjugation",
                    "links": [
                        ("bȕdū", "budu#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "nametao sam",
                    "tags": ["first-person", "past", "perfect", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametao si",
                    "tags": ["past", "perfect", "second-person", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametao je",
                    "tags": ["past", "perfect", "singular", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametali smo",
                    "tags": ["first-person", "past", "perfect", "plural"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametali ste",
                    "tags": ["past", "perfect", "plural", "second-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametali su",
                    "tags": ["past", "perfect", "plural", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "bȉo sam nametao",
                    "tags": ["first-person", "past", "pluperfect", "singular"],
                    "source": "Conjugation",
                    "links": [
                        ("bȉo", "bio#Serbo-Croatian"),
                        ("sam", "sam#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȉo si nametao",
                    "tags": ["past", "pluperfect", "second-person", "singular"],
                    "source": "Conjugation",
                    "links": [
                        ("bȉo", "bio#Serbo-Croatian"),
                        ("si", "si#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȉo je nametao",
                    "tags": ["past", "pluperfect", "singular", "third-person"],
                    "source": "Conjugation",
                    "links": [
                        ("bȉo", "bio#Serbo-Croatian"),
                        ("je", "je#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bíli smo nametali",
                    "tags": ["first-person", "past", "pluperfect", "plural"],
                    "source": "Conjugation",
                    "links": [
                        ("bíli", "bili#Serbo-Croatian"),
                        ("smo", "smo#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bíli ste nametali",
                    "tags": ["past", "pluperfect", "plural", "second-person"],
                    "source": "Conjugation",
                    "links": [
                        ("bíli", "bili#Serbo-Croatian"),
                        ("ste", "ste#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bíli su nametali",
                    "tags": ["past", "pluperfect", "plural", "third-person"],
                    "source": "Conjugation",
                    "links": [
                        ("bíli", "bili#Serbo-Croatian"),
                        ("su", "su#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "nametah",
                    "tags": ["first-person", "imperfect", "past", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaše",
                    "tags": ["imperfect", "past", "second-person", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaše",
                    "tags": ["imperfect", "past", "singular", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametasmo",
                    "tags": ["first-person", "imperfect", "past", "plural"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametaste",
                    "tags": ["imperfect", "past", "plural", "second-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametahu",
                    "tags": ["imperfect", "past", "plural", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametao bih",
                    "tags": [
                        "conditional",
                        "conditional-i",
                        "first-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametao bi",
                    "tags": [
                        "conditional",
                        "conditional-i",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametao bi",
                    "tags": [
                        "conditional",
                        "conditional-i",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametali bismo",
                    "tags": [
                        "conditional",
                        "conditional-i",
                        "first-person",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametali biste",
                    "tags": [
                        "conditional",
                        "conditional-i",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametali bi",
                    "tags": [
                        "conditional",
                        "conditional-i",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "bȉo bih nametao",
                    "tags": [
                        "conditional",
                        "conditional-ii",
                        "first-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [
                        ("bȉo", "bio#Serbo-Croatian"),
                        ("bih", "bih#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȉo bi nametao",
                    "tags": [
                        "conditional",
                        "conditional-ii",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [
                        ("bȉo", "bio#Serbo-Croatian"),
                        ("bi", "bi#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bȉo bi nametao",
                    "tags": [
                        "conditional",
                        "conditional-ii",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [
                        ("bȉo", "bio#Serbo-Croatian"),
                        ("bi", "bi#Serbo-Croatian"),
                        ("nametao", "nametao#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bíli bismo nametali",
                    "tags": [
                        "conditional",
                        "conditional-ii",
                        "first-person",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [
                        ("bíli", "bili#Serbo-Croatian"),
                        ("bismo", "bismo#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bíli biste nametali",
                    "tags": [
                        "conditional",
                        "conditional-ii",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [
                        ("bíli", "bili#Serbo-Croatian"),
                        ("biste", "biste#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "bíli bi nametali",
                    "tags": [
                        "conditional",
                        "conditional-ii",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [
                        ("bíli", "bili#Serbo-Croatian"),
                        ("bi", "bi#Serbo-Croatian"),
                        ("nametali", "nametali#Serbo-Croatian"),
                    ],
                },
                {
                    "form": "-",
                    "tags": ["first-person", "imperative", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "nameći",
                    "tags": ["imperative", "second-person", "singular"],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": ["imperative", "singular", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "namećimo",
                    "tags": ["first-person", "imperative", "plural"],
                    "source": "Conjugation",
                },
                {
                    "form": "namećite",
                    "tags": ["imperative", "plural", "second-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": ["imperative", "plural", "third-person"],
                    "source": "Conjugation",
                },
                {
                    "form": "nametao",
                    "tags": [
                        "active",
                        "masculine",
                        "participle",
                        "past",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametala",
                    "tags": [
                        "active",
                        "feminine",
                        "participle",
                        "past",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametalo",
                    "tags": [
                        "active",
                        "neuter",
                        "participle",
                        "past",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametali",
                    "tags": [
                        "active",
                        "masculine",
                        "participle",
                        "past",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametale",
                    "tags": [
                        "active",
                        "feminine",
                        "participle",
                        "past",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametala",
                    "tags": [
                        "active",
                        "neuter",
                        "participle",
                        "past",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametan",
                    "tags": [
                        "masculine",
                        "participle",
                        "passive",
                        "past",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametana",
                    "tags": [
                        "feminine",
                        "participle",
                        "passive",
                        "past",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametano",
                    "tags": [
                        "neuter",
                        "participle",
                        "passive",
                        "past",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametani",
                    "tags": [
                        "masculine",
                        "participle",
                        "passive",
                        "past",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametane",
                    "tags": [
                        "feminine",
                        "participle",
                        "passive",
                        "past",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "nametana",
                    "tags": [
                        "neuter",
                        "participle",
                        "passive",
                        "past",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
            ]
        }
        self.assertEqual(expected, ret)

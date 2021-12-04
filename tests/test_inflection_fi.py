# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.inflection import parse_inflection_section

class HeadTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 100000
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("testpage")
        self.ctx.start_section("English")

    def xinfl(self, word, lang, pos, section, text):
        """Runs a single inflection table parsing test, and returns ``data``."""
        self.ctx.start_page(word)
        self.ctx.start_section(lang)
        self.ctx.start_subsection(pos)
        tree = self.ctx.parse(text)
        data = {}
        parse_inflection_section(self.config, self.ctx, data, word, lang, pos,
                                 section, tree)
        return data

    def test_Finnish_verb1(self):
        ret = self.xinfl("armahtaa", "Finnish", "verb", "Conjugation", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="border%3A+solid+1px+%23CCCCFF%3B+text-align%3A+left%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23CCCCFF%3B"

! class="vsToggleElement" colspan="7" | [[Appendix:Finnish verbs|Inflection]] of <i class="Latn+mention" lang="fi">armahtaa</i> ([[Kotus]] type 53/[[Appendix:Finnish conjugation/muistaa|muistaa]], ''t-d'' gradation)


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="7" | [[indicative&nbsp;mood]]


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="4" | [[present&nbsp;tense]]


! colspan="3" | perfect


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

! style="min-width%3A+10em%3B+background%3A+%23CCCCFF%3B" colspan="2" | person


! style="min-width%3A+13em%3B" | positive


! style="min-width%3A+13em%3B" | negative


! style="min-width%3A+10em%3B+background%3A+%23CCCCFF%3B" | person


! style="min-width%3A+13em%3B" | positive


! style="min-width%3A+13em%3B" | negative


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fi">[[armahdan#Finnish|armahdan]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pres%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">en [[armahda#Finnish|armahda]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olen [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">en ole [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fi">[[armahdat#Finnish|armahdat]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pres%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">et [[armahda#Finnish|armahda]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olet [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">et ole [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fi">[[armahtaa#Finnish|armahtaa]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pres%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">ei [[armahda#Finnish|armahda]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">on [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei ole [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fi">[[armahdamme#Finnish|armahdamme]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pres%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">emme [[armahda#Finnish|armahda]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olemme [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">emme ole [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fi">[[armahdatte#Finnish|armahdatte]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pres%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">ette [[armahda#Finnish|armahda]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olette [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ette ole [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fi">[[armahtavat#Finnish|armahtavat]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pres%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">eivät [[armahda#Finnish|armahda]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">ovat [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">eivät ole [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | passive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+pasv%7Cpres%7Cindc-form-of+++++++" lang="fi">[[armahdetaan#Finnish|armahdetaan]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pres%7Cpasv%7Cindc%7Cconn-form-of+++++++" lang="fi">ei [[armahdeta#Finnish|armahdeta]]</span>


! style="background%3A+%23CCCCFF%3B" | passive


| data-accel-col="3" | <span class="Latn" lang="fi">on [[armahdettu#Finnish|armahdettu]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei ole [[armahdettu#Finnish|armahdettu]]</span>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="4" | [[past&nbsp;tense]]


! colspan="3" | pluperfect


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | person


! positive


! negative


! style="background%3A+%23CCCCFF%3B" | person


! positive


! negative


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cs%7Cpast%7Cindc-form-of+++++++" lang="fi">[[armahdin#Finnish|armahdin]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+past%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">en [[armahtanut#Finnish|armahtanut]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olin [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">en ollut [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cs%7Cpast%7Cindc-form-of+++++++" lang="fi">[[armahdit#Finnish|armahdit]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+past%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">et [[armahtanut#Finnish|armahtanut]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olit [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">et ollut [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cs%7Cpast%7Cindc-form-of+++++++" lang="fi">[[armahti#Finnish|armahti]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+past%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">ei [[armahtanut#Finnish|armahtanut]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">oli [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei ollut [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cp%7Cpast%7Cindc-form-of+++++++" lang="fi">[[armahdimme#Finnish|armahdimme]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+past%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">emme [[armahtaneet#Finnish|armahtaneet]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olimme [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">emme olleet [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cp%7Cpast%7Cindc-form-of+++++++" lang="fi">[[armahditte#Finnish|armahditte]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+past%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">ette [[armahtaneet#Finnish|armahtaneet]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olitte [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ette olleet [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cp%7Cpast%7Cindc-form-of+++++++" lang="fi">[[armahtivat#Finnish|armahtivat]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+past%7Cactv%7Cindc%7Cconn-form-of+++++++" lang="fi">eivät [[armahtaneet#Finnish|armahtaneet]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olivat [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">eivät olleet [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | passive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+pasv%7Cpast%7Cindc-form-of+++++++" lang="fi">[[armahdettiin#Finnish|armahdettiin]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+past%7Cpasv%7Cindc%7Cconn-form-of+++++++" lang="fi">ei [[armahdettu#Finnish|armahdettu]]</span>


! style="background%3A+%23CCCCFF%3B" | passive


| data-accel-col="3" | <span class="Latn" lang="fi">oli [[armahdettu#Finnish|armahdettu]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei ollut [[armahdettu#Finnish|armahdettu]]</span>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="7" | [[conditional&nbsp;mood]]


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="4" | present


! colspan="3" | perfect


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | person


! positive


! negative


! style="background%3A+%23CCCCFF%3B" | person


! positive


! negative


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cs%7Ccond-form-of+++++++" lang="fi">[[armahtaisin#Finnish|armahtaisin]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Ccond%7Cconn-form-of+++++++" lang="fi">en [[armahtaisi#Finnish|armahtaisi]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olisin [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">en olisi [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cs%7Ccond-form-of+++++++" lang="fi">[[armahtaisit#Finnish|armahtaisit]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Ccond%7Cconn-form-of+++++++" lang="fi">et [[armahtaisi#Finnish|armahtaisi]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olisit [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">et olisi [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cs%7Ccond-form-of+++++++" lang="fi">[[armahtaisi#Finnish|armahtaisi]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Ccond%7Cconn-form-of+++++++" lang="fi">ei [[armahtaisi#Finnish|armahtaisi]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olisi [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei olisi [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cp%7Ccond-form-of+++++++" lang="fi">[[armahtaisimme#Finnish|armahtaisimme]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Ccond%7Cconn-form-of+++++++" lang="fi">emme [[armahtaisi#Finnish|armahtaisi]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olisimme [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">emme olisi [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cp%7Ccond-form-of+++++++" lang="fi">[[armahtaisitte#Finnish|armahtaisitte]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Ccond%7Cconn-form-of+++++++" lang="fi">ette [[armahtaisi#Finnish|armahtaisi]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olisitte [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ette olisi [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cp%7Ccond-form-of+++++++" lang="fi">[[armahtaisivat#Finnish|armahtaisivat]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Ccond%7Cconn-form-of+++++++" lang="fi">eivät [[armahtaisi#Finnish|armahtaisi]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olisivat [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">eivät olisi [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | passive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+pasv%7Ccond-form-of+++++++" lang="fi">[[armahdettaisiin#Finnish|armahdettaisiin]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pasv%7Ccond%7Cconn-form-of+++++++" lang="fi">ei [[armahdettaisi#Finnish|armahdettaisi]]</span>


! style="background%3A+%23CCCCFF%3B" | passive


| data-accel-col="3" | <span class="Latn" lang="fi">olisi [[armahdettu#Finnish|armahdettu]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei olisi [[armahdettu#Finnish|armahdettu]]</span>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="7" | [[imperative&nbsp;mood]]


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="4" | present


! colspan="3" | perfect


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | person


! positive


! negative


! style="background%3A+%23CCCCFF%3B" | person


! positive


! negative


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;sing.


| &mdash;


| &mdash;


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;sing.


| &mdash;


| &mdash;


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cs%7Cimpr-form-of+++++++" lang="fi">[[armahda#Finnish|armahda]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+2%7Cs%7Cimpr%7Cconn-form-of+++++++" lang="fi">älä [[armahda#Finnish|armahda]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">ole [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">älä ole [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cs%7Cimpr-form-of+++++++" lang="fi">[[armahtakoon#Finnish|armahtakoon]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+3%7Cor%7Cp%7Cimpr%7Cconn-form-of+++++++" lang="fi">älköön [[armahtako#Finnish|armahtako]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">olkoon [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">älköön olko [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cp%7Cimpr-form-of+++++++" lang="fi">[[armahtakaamme#Finnish|armahtakaamme]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+3%7Cor%7Cp%7Cimpr%7Cconn-form-of+++++++" lang="fi">älkäämme [[armahtako#Finnish|armahtako]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olkaamme [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">älkäämme olko [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cp%7Cimpr-form-of+++++++" lang="fi">[[armahtakaa#Finnish|armahtakaa]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+3%7Cor%7Cp%7Cimpr%7Cconn-form-of+++++++" lang="fi">älkää [[armahtako#Finnish|armahtako]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olkaa [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">älkää olko [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cp%7Cimpr-form-of+++++++" lang="fi">[[armahtakoot#Finnish|armahtakoot]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+3%7Cor%7Cp%7Cimpr%7Cconn-form-of+++++++" lang="fi">älkööt [[armahtako#Finnish|armahtako]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">olkoot [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">älkööt olko [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | passive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+pasv%7Cimpr-form-of+++++++" lang="fi">[[armahdettakoon#Finnish|armahdettakoon]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pasv%7Cimpr%7Cconn-form-of+++++++" lang="fi">älköön [[armahdettako#Finnish|armahdettako]]</span>


! style="background%3A+%23CCCCFF%3B" | passive


| data-accel-col="3" | <span class="Latn" lang="fi">olkoon [[armahdettu#Finnish|armahdettu]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">älköön olko [[armahdettu#Finnish|armahdettu]]</span>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="7" | [[potential&nbsp;mood]]


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="4" | present


! colspan="3" | perfect


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | person


! positive


! negative


! style="background%3A+%23CCCCFF%3B" | person


! positive


! negative


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cs%7Cpotn-form-of+++++++" lang="fi">[[armahtanen#Finnish|armahtanen]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Cpotn%7Cconn-form-of+++++++" lang="fi">en [[armahtane#Finnish|armahtane]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">lienen [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">en liene [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cs%7Cpotn-form-of+++++++" lang="fi">[[armahtanet#Finnish|armahtanet]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Cpotn%7Cconn-form-of+++++++" lang="fi">et [[armahtane#Finnish|armahtane]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">lienet [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">et liene [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;sing.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cs%7Cpotn-form-of+++++++" lang="fi">[[armahtanee#Finnish|armahtanee]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Cpotn%7Cconn-form-of+++++++" lang="fi">ei [[armahtane#Finnish|armahtane]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;sing.


| data-accel-col="3" | <span class="Latn" lang="fi">lienee [[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei liene [[armahtanut#Finnish|armahtanut]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+1%7Cp%7Cpotn-form-of+++++++" lang="fi">[[armahtanemme#Finnish|armahtanemme]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Cpotn%7Cconn-form-of+++++++" lang="fi">emme [[armahtane#Finnish|armahtane]]</span>


! style="background%3A+%23CCCCFF%3B" | 1st&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">lienemme [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">emme liene [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 2nd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+2%7Cp%7Cpotn-form-of+++++++" lang="fi">[[armahtanette#Finnish|armahtanette]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Cpotn%7Cconn-form-of+++++++" lang="fi">ette [[armahtane#Finnish|armahtane]]</span>


! style="background%3A+%23CCCCFF%3B" | 2nd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">lienette [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ette liene [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 3rd&nbsp;plur.


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+3%7Cp%7Cpotn-form-of+++++++" lang="fi">[[armahtanevat#Finnish|armahtanevat]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+actv%7Cpotn%7Cconn-form-of+++++++" lang="fi">eivät [[armahtane#Finnish|armahtane]]</span>


! style="background%3A+%23CCCCFF%3B" | 3rd&nbsp;plur.


| data-accel-col="3" | <span class="Latn" lang="fi">lienevät [[armahtaneet#Finnish|armahtaneet]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">eivät liene [[armahtaneet#Finnish|armahtaneet]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | passive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+pasv%7Cpotn-form-of+++++++" lang="fi">[[armahdettaneen#Finnish|armahdettaneen]]</span>


| data-accel-col="2" | <span class="Latn+form-of+lang-fi+pasv%7Cpotn%7Cconn-form-of+++++++" lang="fi">ei [[armahdettane#Finnish|armahdettane]]</span>


! style="background%3A+%23CCCCFF%3B" | passive


| data-accel-col="3" | <span class="Latn" lang="fi">lienee [[armahdettu#Finnish|armahdettu]]</span>


| data-accel-col="4" | <span class="Latn" lang="fi">ei liene [[armahdettu#Finnish|armahdettu]]</span>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="7" | Nominal forms


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! colspan="4" | [[infinitive]]s


! colspan="3" | [[participle]]s


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

| style="background%3A+%23CCCCFF%3B" colspan="2" |


! active


! passive


| style="background%3A+%23CCCCFF%3B" |


! active


! passive


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 1st


| data-accel-col="1" colspan="2" | <span class="Latn" lang="fi">[[armahtaa#Finnish|armahtaa]]</span>


! style="background%3A+%23CCCCFF%3B" | present


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+participle-pres%7Cactv-form-of+++++++" lang="fi">[[armahtava#Finnish|armahtava]]</span>


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+participle-pres%7Cpasv-form-of+++++++" lang="fi">[[armahdettava#Finnish|armahdettava]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | long 1st<sup>2</sup>


| data-accel-col="1" colspan="2" | <span class="Latn+form-of+lang-fi+inf1l-a-form-of+++++++" lang="fi">[[armahtaakseen#Finnish|armahtaakseen]]</span>


! style="background%3A+%23CCCCFF%3B" | past


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+participle-past%7Cactv-form-of+++++++" lang="fi">[[armahtanut#Finnish|armahtanut]]</span>


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+participle-past%7Cpasv-form-of+++++++" lang="fi">[[armahdettu#Finnish|armahdettu]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" rowspan="2" | 2nd


! style="background%3A+%23E6E6FF%3B" | inessive<sup>1</sup>


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ine%7Cof%7Csecond%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtaessa#Finnish|armahtaessa]]</span>


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ine%7Cof%7Csecond%7Cpasv%7Cinf-form-of+++++++" lang="fi">[[armahdettaessa#Finnish|armahdettaessa]]</span>


! style="background%3A+%23CCCCFF%3B" | agent<sup>1,&nbsp;3</sup>


| data-accel-col="1" colspan="2" | <span class="Latn+form-of+lang-fi+participle-agent-form-of+++++++" lang="fi">[[armahtama#Finnish|armahtama]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | instructive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ist%7Cof%7Csecond%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtaen#Finnish|armahtaen]]</span>


| &mdash;


! style="background%3A+%23CCCCFF%3B" | negative


| data-accel-col="1" colspan="2" | <span class="Latn+form-of+lang-fi+participle-neg-form-of+++++++" lang="fi">[[armahtamaton#Finnish|armahtamaton]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" rowspan="6" | 3rd


! style="background%3A+%23E6E6FF%3B" | inessive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ine%7Cof%7Cthird%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtamassa#Finnish|armahtamassa]]</span>


| &mdash;


| colspan="3" rowspan="9" style="text-align%3Aleft%3Bvertical-align%3Atop%3Bfont-size%3Asmaller%3B" | <sup>1)</sup> Usually with a possessive suffix.<br>
<sup>2)</sup> Used only with a possessive suffix; this is the form for the third-person singular and third-person plural.<br>
<sup>3)</sup> Does not exist in the case of intransitive verbs. Do not confuse with nouns formed with the ''-ma'' suffix.


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | elative


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ela%7Cof%7Cthird%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtamasta#Finnish|armahtamasta]]</span>


| &mdash;


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | illative


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ill%7Cof%7Cthird%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtamaan#Finnish|armahtamaan]]</span>


| &mdash;


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | adessive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ade%7Cof%7Cthird%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtamalla#Finnish|armahtamalla]]</span>


| &mdash;


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | abessive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+abe%7Cof%7Cthird%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtamatta#Finnish|armahtamatta]]</span>


| &mdash;


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | instructive


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ist%7Cof%7Cthird%7Cactv%7Cinf-form-of+++++++" lang="fi">[[armahtaman#Finnish|armahtaman]]</span>


| data-accel-col="1" | <span class="Latn+form-of+lang-fi+ist%7Cof%7Cthird%7Cpasv%7Cinf-form-of+++++++" lang="fi">[[armahdettaman#Finnish|armahdettaman]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" rowspan="2" | 4th


! style="background%3A+%23E6E6FF%3B" | nominative


| colspan="2" data-accel-col="1" | <span class="Latn+form-of+lang-fi+nom%7Cof%7Cfourth%7Cinf-form-of+++++++" lang="fi">[[armahtaminen#Finnish|armahtaminen]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | partitive


| colspan="2" data-accel-col="1" | <span class="Latn+form-of+lang-fi+par%7Cof%7Cfourth%7Cinf-form-of+++++++" lang="fi">[[armahtamista#Finnish|armahtamista]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | 5th<sup>2</sup>


| colspan="2" data-accel-col="1" | <span class="Latn+form-of+lang-fi+inf5-a-form-of+++++++" lang="fi">[[armahtamaisillaan#Finnish|armahtamaisillaan]]</span>


|}
[[Category:Finnish muistaa-type verbs|ARMAHTAA]]
""")
        expected = {
            "forms": [
              {
                "form": "53/muistaa",
                "source": "Conjugation title",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "armahdan",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "positive",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "en armahda",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "olen armahtanut",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "perfect",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "en ole armahtanut",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "perfect",
                  "singular"
                ]
              },
              {
                "form": "armahdat",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "positive",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et armahda",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "olet armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "positive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et ole armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "armahtaa",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "positive",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei armahda",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "on armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "positive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei ole armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "armahdamme",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "positive",
                  "present"
                ]
              },
              {
                "form": "emme armahda",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "olemme armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "perfect",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "emme ole armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "perfect",
                  "plural"
                ]
              },
              {
                "form": "armahdatte",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "positive",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "ette armahda",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "olette armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "plural",
                  "positive",
                  "second-person"
                ]
              },
              {
                "form": "ette ole armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "armahtavat",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "positive",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "eivät armahda",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "ovat armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "plural",
                  "positive",
                  "third-person"
                ]
              },
              {
                "form": "eivät ole armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "armahdetaan",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "positive",
                  "present"
                ]
              },
              {
                "form": "ei armahdeta",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "on armahdettu",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "perfect",
                  "positive"
                ]
              },
              {
                "form": "ei ole armahdettu",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "armahdin",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "en armahtanut",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "olin armahtanut",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "en ollut armahtanut",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "pluperfect",
                  "singular"
                ]
              },
              {
                "form": "armahdit",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "positive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "olit armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "positive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et ollut armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "pluperfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "armahti",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "positive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "oli armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "positive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei ollut armahtanut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "pluperfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "armahdimme",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "emme armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "olimme armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "emme olleet armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "negative",
                  "pluperfect",
                  "plural"
                ]
              },
              {
                "form": "armahditte",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "positive",
                  "second-person"
                ]
              },
              {
                "form": "ette armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "olitte armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "plural",
                  "positive",
                  "second-person"
                ]
              },
              {
                "form": "ette olleet armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "pluperfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "armahtivat",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "positive",
                  "third-person"
                ]
              },
              {
                "form": "eivät armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "olivat armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "plural",
                  "positive",
                  "third-person"
                ]
              },
              {
                "form": "eivät olleet armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "pluperfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "armahdettiin",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "past",
                  "positive"
                ]
              },
              {
                "form": "ei armahdettu",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "past"
                ]
              },
              {
                "form": "oli armahdettu",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "pluperfect",
                  "positive"
                ]
              },
              {
                "form": "ei ollut armahdettu",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "pluperfect"
                ]
              },
              {
                "form": "armahtaisin",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "positive",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "en armahtaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "negative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "olisin armahtanut",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "en olisi armahtanut",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "negative",
                  "perfect",
                  "singular"
                ]
              },
              {
                "form": "armahtaisit",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "positive",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et armahtaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "olisit armahtanut",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "positive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et olisi armahtanut",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "armahtaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "positive",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei armahtaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "olisi armahtanut",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "positive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei olisi armahtanut",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "armahtaisimme",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural",
                  "positive",
                  "present"
                ]
              },
              {
                "form": "emme armahtaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "negative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "olisimme armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "emme olisi armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "negative",
                  "perfect",
                  "plural"
                ]
              },
              {
                "form": "armahtaisitte",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "positive",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "ette armahtaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "olisitte armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "plural",
                  "positive",
                  "second-person"
                ]
              },
              {
                "form": "ette olisi armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "armahtaisivat",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "positive",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "eivät armahtaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "olisivat armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "plural",
                  "positive",
                  "third-person"
                ]
              },
              {
                "form": "eivät olisi armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "armahdettaisiin",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "passive",
                  "positive",
                  "present"
                ]
              },
              {
                "form": "ei armahdettaisi",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "olisi armahdettu",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "passive",
                  "perfect",
                  "positive"
                ]
              },
              {
                "form": "ei olisi armahdettu",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "armahda",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "positive",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "älä armahda",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ole armahtanut",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "perfect",
                  "positive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "älä ole armahtanut",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "armahtakoon",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "positive",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "älköön armahtako",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "olkoon armahtanut",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "perfect",
                  "positive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "älköön olko armahtanut",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "armahtakaamme",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural",
                  "positive",
                  "present"
                ]
              },
              {
                "form": "älkäämme armahtako",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "negative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "olkaamme armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "perfect",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "älkäämme olko armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "negative",
                  "perfect",
                  "plural"
                ]
              },
              {
                "form": "armahtakaa",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "positive",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "älkää armahtako",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "olkaa armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "perfect",
                  "plural",
                  "positive",
                  "second-person"
                ]
              },
              {
                "form": "älkää olko armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "armahtakoot",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "positive",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "älkööt armahtako",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "olkoot armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "perfect",
                  "plural",
                  "positive",
                  "third-person"
                ]
              },
              {
                "form": "älkööt olko armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "armahdettakoon",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "passive",
                  "positive",
                  "present"
                ]
              },
              {
                "form": "älköön armahdettako",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "olkoon armahdettu",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "passive",
                  "perfect",
                  "positive"
                ]
              },
              {
                "form": "älköön olko armahdettu",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "armahtanen",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "positive",
                  "potential",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "en armahtane",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "negative",
                  "potential",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "lienen armahtanut",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "perfect",
                  "positive",
                  "potential",
                  "singular"
                ]
              },
              {
                "form": "en liene armahtanut",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "negative",
                  "perfect",
                  "potential",
                  "singular"
                ]
              },
              {
                "form": "armahtanet",
                "source": "Conjugation",
                "tags": [
                  "positive",
                  "potential",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et armahtane",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "potential",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "lienet armahtanut",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "positive",
                  "potential",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "et liene armahtanut",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "perfect",
                  "potential",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "armahtanee",
                "source": "Conjugation",
                "tags": [
                  "positive",
                  "potential",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei armahtane",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "potential",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "lienee armahtanut",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "positive",
                  "potential",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei liene armahtanut",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "perfect",
                  "potential",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "armahtanemme",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "positive",
                  "potential",
                  "present"
                ]
              },
              {
                "form": "emme armahtane",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "negative",
                  "plural",
                  "potential",
                  "present"
                ]
              },
              {
                "form": "lienemme armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "perfect",
                  "plural",
                  "positive",
                  "potential"
                ]
              },
              {
                "form": "emme liene armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "negative",
                  "perfect",
                  "plural",
                  "potential"
                ]
              },
              {
                "form": "armahtanette",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "positive",
                  "potential",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "ette armahtane",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "plural",
                  "potential",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "lienette armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "plural",
                  "positive",
                  "potential",
                  "second-person"
                ]
              },
              {
                "form": "ette liene armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "perfect",
                  "plural",
                  "potential",
                  "second-person"
                ]
              },
              {
                "form": "armahtanevat",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "positive",
                  "potential",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "eivät armahtane",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "plural",
                  "potential",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "lienevät armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "plural",
                  "positive",
                  "potential",
                  "third-person"
                ]
              },
              {
                "form": "eivät liene armahtaneet",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "perfect",
                  "plural",
                  "potential",
                  "third-person"
                ]
              },
              {
                "form": "armahdettaneen",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "positive",
                  "potential",
                  "present"
                ]
              },
              {
                "form": "ei armahdettane",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "passive",
                  "potential",
                  "present"
                ]
              },
              {
                "form": "lienee armahdettu",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "perfect",
                  "positive",
                  "potential"
                ]
              },
              {
                "form": "ei liene armahdettu",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "passive",
                  "perfect",
                  "potential"
                ]
              },
              {
                "form": "armahtaa",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-i"
                ]
              },
              {
                "form": "armahtava",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "armahdettava",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "armahtaakseen",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-i-long"
                ]
              },
              {
                "form": "armahtanut",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "armahdettu",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive",
                  "past"
                ]
              },
              {
                "form": "armahtaessa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "inessive",
                  "infinitive",
                  "infinitive-ii"
                ]
              },
              {
                "form": "armahdettaessa",
                "source": "Conjugation",
                "tags": [
                  "inessive",
                  "infinitive",
                  "infinitive-ii",
                  "passive"
                ]
              },
              {
                "form": "armahtama",
                "source": "Conjugation",
                "tags": [
                  "agent",
                  "participle"
                ]
              },
              {
                "form": "armahtaen",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "infinitive-ii",
                  "instructive"
                ]
              },
              {
                "form": "armahtamaton",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "participle"
                ]
              },
              {
                "form": "armahtamassa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "inessive",
                  "infinitive",
                  "infinitive-iii"
                ]
              },
              {
                "form": "armahtamasta",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "elative",
                  "infinitive",
                  "infinitive-iii"
                ]
              },
              {
                "form": "armahtamaan",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "illative",
                  "infinitive",
                  "infinitive-iii"
                ]
              },
              {
                "form": "armahtamalla",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adessive",
                  "infinitive",
                  "infinitive-iii"
                ]
              },
              {
                "form": "armahtamatta",
                "source": "Conjugation",
                "tags": [
                  "abessive",
                  "active",
                  "infinitive",
                  "infinitive-iii"
                ]
              },
              {
                "form": "armahtaman",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "infinitive-iii",
                  "instructive"
                ]
              },
              {
                "form": "armahdettaman",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-iii",
                  "instructive",
                  "passive"
                ]
              },
              {
                "form": "armahtaminen",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-iv",
                  "nominative"
                ]
              },
              {
                "form": "armahtamista",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-iv",
                  "partitive"
                ]
              },
              {
                "form": "armahtamaisillaan",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-v"
                ]
              },
              {
                "form": "gradation-t-d",
                "source": "Conjugation title",
                "tags": [
                  "word-tags"
                ]
              }
            ],
        }
        self.assertEqual(ret, expected)

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

    def test_Latin_verb1(self):
        ret = self.xinfl("accuso", "Latin", "verb", "Conjugation", """
{| style="width%3A+100%25%3B+background%3A+%23EEE%3B+border%3A+1px+solid+%23AAA%3B+font-size%3A+95%25%3B+text-align%3A+center%3B" class="inflection-table+vsSwitcher" data-toggle-category="inflection"

|-

! colspan="8" class="vsToggleElement" style="background%3A+%23CCC%3B+text-align%3A+left%3B" | &nbsp;&nbsp;&nbsp;Conjugation of <i class="Latn+mention" lang="la">accūsō</i> ([[Appendix:Latin first conjugation|first conjugation]])



|- class="vsHide"

! colspan="2" rowspan="2" style="background%3A%23c0cfe4" | indicative


! colspan="3" style="background%3A%23c0cfe4" | ''singular''


! colspan="3" style="background%3A%23c0cfe4" | ''plural''


|- class="vsHide"

! style="background%3A%23c0cfe4%3Bwidth%3A12.5%25" | [[first person|first]]


! style="background%3A%23c0cfe4%3Bwidth%3A12.5%25" | [[second person|second]]


! style="background%3A%23c0cfe4%3Bwidth%3A12.5%25" | [[third person|third]]


! style="background%3A%23c0cfe4%3Bwidth%3A12.5%25" | [[first person|first]]


! style="background%3A%23c0cfe4%3Bwidth%3A12.5%25" | [[second person|second]]


! style="background%3A%23c0cfe4%3Bwidth%3A12.5%25" | [[third person|third]]



|- class="vsHide"

! rowspan="6" style="background%3A%23c0cfe4" | active



! style="background%3A%23c0cfe4" | present


| <span class="Latn+form-of+lang-la+1%7Cs%7Cpres%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accuso#Latin|accūsō]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusas#Latin|accūsās]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cpres%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusat#Latin|accūsat]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cpres%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusamus#Latin|accūsāmus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cpres%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusatis#Latin|accūsātis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cpres%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusant#Latin|accūsant]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | imperfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cimpf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabam#Latin|accūsābam]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cimpf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabas#Latin|accūsābās]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cimpf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabat#Latin|accūsābat]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cimpf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabamus#Latin|accūsābāmus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cimpf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabatis#Latin|accūsābātis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cimpf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabant#Latin|accūsābant]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | future


| <span class="Latn+form-of+lang-la+1%7Cs%7Cfut%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabo#Latin|accūsābō]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cfut%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabis#Latin|accūsābis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cfut%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabit#Latin|accūsābit]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cfut%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabimus#Latin|accūsābimus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cfut%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabitis#Latin|accūsābitis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cfut%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabunt#Latin|accūsābunt]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | perfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavi#Latin|accūsāvī]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavisti#Latin|accūsāvistī]]</span>, <span class="Latn+form-of+lang-la+2%7Cs%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusasti#Latin|accūsāstī]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavit#Latin|accūsāvit]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavimus#Latin|accūsāvimus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavistis#Latin|accūsāvistis]]</span>, <span class="Latn+form-of+lang-la+2%7Cp%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusastis#Latin|accūsāstis]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverunt#Latin|accūsāvērunt]]</span>, <span class="Latn+form-of+lang-la+3%7Cp%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavere#Latin|accūsāvēre]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | pluperfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cplup%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveram#Latin|accūsāveram]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cplup%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveras#Latin|accūsāverās]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cplup%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverat#Latin|accūsāverat]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cplup%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveramus#Latin|accūsāverāmus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cplup%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveratis#Latin|accūsāverātis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cplup%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverant#Latin|accūsāverant]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | future&nbsp;perfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cfut%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavero#Latin|accūsāverō]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cfut%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveris#Latin|accūsāveris]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cfut%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverit#Latin|accūsāverit]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cfut%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverimus#Latin|accūsāverimus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cfut%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveritis#Latin|accūsāveritis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cfut%7Cperf%7Cact%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverint#Latin|accūsāverint]]</span>


|- class="vsHide"

! rowspan="6" style="background%3A%23c0cfe4" | passive



! style="background%3A%23c0cfe4" | present


| <span class="Latn+form-of+lang-la+1%7Cs%7Cpres%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusor#Latin|accūsor]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaris#Latin|accūsāris]]</span>, <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusare#Latin|accūsāre]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cpres%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusatur#Latin|accūsātur]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cpres%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusamur#Latin|accūsāmur]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cpres%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusamini#Latin|accūsāminī]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cpres%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusantur#Latin|accūsantur]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | imperfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cimpf%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabar#Latin|accūsābar]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cimpf%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabaris#Latin|accūsābāris]]</span>, <span class="Latn+form-of+lang-la+2%7Cs%7Cimpf%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabare#Latin|accūsābāre]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cimpf%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabatur#Latin|accūsābātur]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cimpf%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabamur#Latin|accūsābāmur]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cimpf%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabamini#Latin|accūsābāminī]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cimpf%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabantur#Latin|accūsābantur]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | future


| <span class="Latn+form-of+lang-la+1%7Cs%7Cfut%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabor#Latin|accūsābor]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cfut%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaberis#Latin|accūsāberis]]</span>, <span class="Latn+form-of+lang-la+2%7Cs%7Cfut%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabere#Latin|accūsābere]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cfut%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabitur#Latin|accūsābitur]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cfut%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabimur#Latin|accūsābimur]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cfut%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabimini#Latin|accūsābiminī]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cfut%7Cpass%7Cind-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusabuntur#Latin|accūsābuntur]]</span>


|- class="vsHide"

! style="background%3A%23c0cfe4" | perfect


! colspan="6" style="background%3A+%23CCC" |<i class="Latn+mention" lang="la">[[accusatus#Latin|accūsātus]]</i> + present active indicative of <i class="Latn+mention" lang="la">[[sum#Latin|sum]]</i>


|- class="vsHide"

! style="background%3A%23c0cfe4" | pluperfect


! colspan="6" style="background%3A+%23CCC" |<i class="Latn+mention" lang="la">[[accusatus#Latin|accūsātus]]</i> + imperfect active indicative of <i class="Latn+mention" lang="la">[[sum#Latin|sum]]</i>


|- class="vsHide"

! style="background%3A%23c0cfe4" | future&nbsp;perfect


! colspan="6" style="background%3A+%23CCC" |<i class="Latn+mention" lang="la">[[accusatus#Latin|accūsātus]]</i> + future active indicative of <i class="Latn+mention" lang="la">[[sum#Latin|sum]]</i>


|- class="vsHide"

! colspan="2" rowspan="2" style="background%3A%23c0e4c0" | subjunctive


! colspan="3" style="background%3A%23c0e4c0" | ''singular''


! colspan="3" style="background%3A%23c0e4c0" | ''plural''


|- class="vsHide"

! style="background%3A%23c0e4c0%3Bwidth%3A12.5%25" | [[first person|first]]


! style="background%3A%23c0e4c0%3Bwidth%3A12.5%25" | [[second person|second]]


! style="background%3A%23c0e4c0%3Bwidth%3A12.5%25" | [[third person|third]]


! style="background%3A%23c0e4c0%3Bwidth%3A12.5%25" | [[first person|first]]


! style="background%3A%23c0e4c0%3Bwidth%3A12.5%25" | [[second person|second]]


! style="background%3A%23c0e4c0%3Bwidth%3A12.5%25" | [[third person|third]]



|- class="vsHide"

! rowspan="4" style="background%3A%23c0e4c0" | active



! style="background%3A%23c0e4c0" | present


| <span class="Latn+form-of+lang-la+1%7Cs%7Cpres%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusem#Latin|accūsem]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accuses#Latin|accūsēs]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cpres%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accuset#Latin|accūset]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cpres%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusemus#Latin|accūsēmus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cpres%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusetis#Latin|accūsētis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cpres%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusent#Latin|accūsent]]</span>


|- class="vsHide"

! style="background%3A%23c0e4c0" | imperfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cimpf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusarem#Latin|accūsārem]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cimpf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusares#Latin|accūsārēs]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cimpf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaret#Latin|accūsāret]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cimpf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaremus#Latin|accūsārēmus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cimpf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaretis#Latin|accūsārētis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cimpf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusarent#Latin|accūsārent]]</span>


|- class="vsHide"

! style="background%3A%23c0e4c0" | perfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cperf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverim#Latin|accūsāverim]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cperf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveris#Latin|accūsāverīs]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cperf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverit#Latin|accūsāverit]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cperf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverimus#Latin|accūsāverīmus]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cperf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaveritis#Latin|accūsāverītis]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cperf%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaverint#Latin|accūsāverint]]</span>


|- class="vsHide"

! style="background%3A%23c0e4c0" | pluperfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavissem#Latin|accūsāvissem]]</span>, <span class="Latn+form-of+lang-la+1%7Cs%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusassem#Latin|accūsāssem]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavisses#Latin|accūsāvissēs]]</span>, <span class="Latn+form-of+lang-la+2%7Cs%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusasses#Latin|accūsāssēs]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavisset#Latin|accūsāvisset]]</span>, <span class="Latn+form-of+lang-la+3%7Cs%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusasset#Latin|accūsāsset]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavissemus#Latin|accūsāvissēmus]]</span>, <span class="Latn+form-of+lang-la+1%7Cp%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusassemus#Latin|accūsāssēmus]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavissetis#Latin|accūsāvissētis]]</span>, <span class="Latn+form-of+lang-la+2%7Cp%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusassetis#Latin|accūsāssētis]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavissent#Latin|accūsāvissent]]</span>, <span class="Latn+form-of+lang-la+3%7Cp%7Cplup%7Cact%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusassent#Latin|accūsāssent]]</span><sup style="color%3A+red">1</sup>


|- class="vsHide"

! rowspan="4" style="background%3A%23c0e4c0" | passive



! style="background%3A%23c0e4c0" | present


| <span class="Latn+form-of+lang-la+1%7Cs%7Cpres%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accuser#Latin|accūser]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accuseris#Latin|accūsēris]]</span>, <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusere#Latin|accūsēre]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cpres%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusetur#Latin|accūsētur]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cpres%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusemur#Latin|accūsēmur]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cpres%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusemini#Latin|accūsēminī]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cpres%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusentur#Latin|accūsentur]]</span>


|- class="vsHide"

! style="background%3A%23c0e4c0" | imperfect


| <span class="Latn+form-of+lang-la+1%7Cs%7Cimpf%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusarer#Latin|accūsārer]]</span>


| <span class="Latn+form-of+lang-la+2%7Cs%7Cimpf%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusareris#Latin|accūsārēris]]</span>, <span class="Latn+form-of+lang-la+2%7Cs%7Cimpf%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusarere#Latin|accūsārēre]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cimpf%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaretur#Latin|accūsārētur]]</span>


| <span class="Latn+form-of+lang-la+1%7Cp%7Cimpf%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaremur#Latin|accūsārēmur]]</span>


| <span class="Latn+form-of+lang-la+2%7Cp%7Cimpf%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaremini#Latin|accūsārēminī]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cimpf%7Cpass%7Csub-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusarentur#Latin|accūsārentur]]</span>


|- class="vsHide"

! style="background%3A%23c0e4c0" | perfect


! colspan="6" style="background%3A+%23CCC" |<i class="Latn+mention" lang="la">[[accusatus#Latin|accūsātus]]</i> + present active subjunctive of <i class="Latn+mention" lang="la">[[sum#Latin|sum]]</i>


|- class="vsHide"

! style="background%3A%23c0e4c0" | pluperfect


! colspan="6" style="background%3A+%23CCC" |<i class="Latn+mention" lang="la">[[accusatus#Latin|accūsātus]]</i> + imperfect active subjunctive of <i class="Latn+mention" lang="la">[[sum#Latin|sum]]</i>


|- class="vsHide"

! colspan="2" rowspan="2" style="background%3A%23e4d4c0" | imperative


! colspan="3" style="background%3A%23e4d4c0" | ''singular''


! colspan="3" style="background%3A%23e4d4c0" | ''plural''


|- class="vsHide"

! style="background%3A%23e4d4c0%3Bwidth%3A12.5%25" | [[first person|first]]


! style="background%3A%23e4d4c0%3Bwidth%3A12.5%25" | [[second person|second]]


! style="background%3A%23e4d4c0%3Bwidth%3A12.5%25" | [[third person|third]]


! style="background%3A%23e4d4c0%3Bwidth%3A12.5%25" | [[first person|first]]


! style="background%3A%23e4d4c0%3Bwidth%3A12.5%25" | [[second person|second]]


! style="background%3A%23e4d4c0%3Bwidth%3A12.5%25" | [[third person|third]]



|- class="vsHide"

! rowspan="2" style="background%3A%23e4d4c0" | active



! style="background%3A%23e4d4c0" | present


| &mdash;


| <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cact%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusa#Latin|accūsā]]</span>


| &mdash;


| &mdash;


| <span class="Latn+form-of+lang-la+2%7Cp%7Cpres%7Cact%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusate#Latin|accūsāte]]</span>


| &mdash;


|- class="vsHide"

! style="background%3A%23e4d4c0" | future


| &mdash;


| <span class="Latn+form-of+lang-la+2%7Cs%7Cfut%7Cact%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusato#Latin|accūsātō]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cfut%7Cact%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusato#Latin|accūsātō]]</span>


| &mdash;


| <span class="Latn+form-of+lang-la+2%7Cp%7Cfut%7Cact%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusatote#Latin|accūsātōte]]</span>


| <span class="Latn+form-of+lang-la+3%7Cp%7Cfut%7Cact%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusanto#Latin|accūsantō]]</span>


|- class="vsHide"

! rowspan="2" style="background%3A%23e4d4c0" | passive



! style="background%3A%23e4d4c0" | present


| &mdash;


| <span class="Latn+form-of+lang-la+2%7Cs%7Cpres%7Cpass%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusare#Latin|accūsāre]]</span>


| &mdash;


| &mdash;


| <span class="Latn+form-of+lang-la+2%7Cp%7Cpres%7Cpass%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusamini#Latin|accūsāminī]]</span>


| &mdash;


|- class="vsHide"

! style="background%3A%23e4d4c0" | future


| &mdash;


| <span class="Latn+form-of+lang-la+2%7Cs%7Cfut%7Cpass%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusator#Latin|accūsātor]]</span>


| <span class="Latn+form-of+lang-la+3%7Cs%7Cfut%7Cpass%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusator#Latin|accūsātor]]</span>


| &mdash;


| &mdash;


| <span class="Latn+form-of+lang-la+3%7Cp%7Cfut%7Cpass%7Cimp-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusantor#Latin|accūsantor]]</span>


|- class="vsHide"

! colspan="2" rowspan="2" style="background%3A%23e2e4c0" | non-finite forms


! colspan="3" style="background%3A%23e2e4c0" | active


! colspan="3" style="background%3A%23e2e4c0" | passive


|- class="vsHide"

! style="background%3A%23e2e4c0%3Bwidth%3A12.5%25" | present


! style="background%3A%23e2e4c0%3Bwidth%3A12.5%25" | perfect


! style="background%3A%23e2e4c0%3Bwidth%3A12.5%25" | future


! style="background%3A%23e2e4c0%3Bwidth%3A12.5%25" | present


! style="background%3A%23e2e4c0%3Bwidth%3A12.5%25" | perfect


! style="background%3A%23e2e4c0%3Bwidth%3A12.5%25" | future



|- class="vsHide"

! style="background%3A%23e2e4c0" colspan="2" | infinitives


| <span class="Latn+form-of+lang-la+pres%7Cact%7Cinf-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusare#Latin|accūsāre]]</span>


| <span class="Latn+form-of+lang-la+perf%7Cact%7Cinf-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusavisse#Latin|accūsāvisse]]</span>, <span class="Latn+form-of+lang-la+perf%7Cact%7Cinf-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusasse#Latin|accūsāsse]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn" lang="la">[[accusaturus#Latin|accūsātūrum]] [[esse#Latin|esse]]</span>


| <span class="Latn+form-of+lang-la+pres%7Cpass%7Cinf-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusari#Latin|accūsārī]]</span>


| <span class="Latn" lang="la">[[accusatus#Latin|accūsātum]] [[esse#Latin|esse]]</span>


| <span class="Latn" lang="la">[[accusatum#Latin|accūsātum]] [[iri#Latin|īrī]]</span>


|- class="vsHide"

! style="background%3A%23e2e4c0" colspan="2" | participles


| <span class="Latn+form-of+lang-la+pres%7Cact%7Cpart-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusans#Latin|accūsāns]]</span>


| &mdash;


| <span class="Latn+form-of+lang-la+fut%7Cact%7Cpart-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusaturus#Latin|accūsātūrus]]</span>


| &mdash;


| <span class="Latn+form-of+lang-la+perf%7Cpass%7Cpart-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusatus#Latin|accūsātus]]</span>


| <span class="Latn+form-of+lang-la+fut%7Cpass%7Cpart-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusandus#Latin|accūsandus]]</span>


|- class="vsHide"

! colspan="2" rowspan="3" style="background%3A%23e0e0b0" | verbal nouns


! colspan="4" style="background%3A%23e0e0b0" | gerund


! colspan="2" style="background%3A%23e0e0b0" | supine


|- class="vsHide"

! style="background%3A%23e0e0b0%3Bwidth%3A12.5%25" | genitive


! style="background%3A%23e0e0b0%3Bwidth%3A12.5%25" | dative


! style="background%3A%23e0e0b0%3Bwidth%3A12.5%25" | accusative


! style="background%3A%23e0e0b0%3Bwidth%3A12.5%25" | ablative


! style="background%3A%23e0e0b0%3Bwidth%3A12.5%25" | accusative


! style="background%3A%23e0e0b0%3Bwidth%3A12.5%25" | ablative


|- class="vsHide"

| <span class="Latn+form-of+lang-la+ger%7Cgen-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusandi#Latin|accūsandī]]</span>


| <span class="Latn+form-of+lang-la+ger%7Cdat-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusando#Latin|accūsandō]]</span>


| <span class="Latn+form-of+lang-la+ger%7Cacc-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusandum#Latin|accūsandum]]</span>


| <span class="Latn+form-of+lang-la+ger%7Cabl-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusando#Latin|accūsandō]]</span>


| <span class="Latn+form-of+lang-la+sup%7Cacc-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusatum#Latin|accūsātum]]</span>


| <span class="Latn+form-of+lang-la+sup%7Cabl-form-of++++origin-acc%C5%ABs%C5%8D+++" lang="la">[[accusatu#Latin|accūsātū]]</span>


|}
<sup style="color%3A+red">1</sup>At least one rare poetic syncopated perfect form is attested.<br>[[Category:Latin first conjugation verbs|ACCUSO]][[Category:Latin first conjugation verbs with perfect in -av-|ACCUSO]]
""")
        expected = {
            "forms": [
              {
                "form": "accūsō",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "accūsās",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsāmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "accūsātis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "accūsant",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "accūsābam",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "accūsābās",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsābat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsābāmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "accūsābātis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsābant",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsābō",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "accūsābis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsābit",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsābimus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "accūsābitis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsābunt",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsāvī",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "perfect",
                  "singular"
                ]
              },
              {
                "form": "accūsāvistī",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsāstī",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsāvit",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsāvimus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "perfect",
                  "plural"
                ]
              },
              {
                "form": "accūsāvistis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsāstis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsāvērunt",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsāvēre",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsāveram",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "singular"
                ]
              },
              {
                "form": "accūsāverās",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "pluperfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsāverat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "pluperfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsāverāmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "plural"
                ]
              },
              {
                "form": "accūsāverātis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "pluperfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsāverant",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "pluperfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsāverō",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "future",
                  "indicative",
                  "perfect",
                  "singular"
                ]
              },
              {
                "form": "accūsāveris",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsāverit",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsāverimus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "future",
                  "indicative",
                  "perfect",
                  "plural"
                ]
              },
              {
                "form": "accūsāveritis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsāverint",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "indicative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsor",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "passive",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "accūsāris",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsāre",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsātur",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsāmur",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "passive",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "accūsāminī",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "accūsantur",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "accūsābar",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "accūsābāris",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsābāre",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsābātur",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "passive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsābāmur",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "passive",
                  "plural"
                ]
              },
              {
                "form": "accūsābāminī",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "passive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsābantur",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "passive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsābor",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "accūsāberis",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsābere",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsābitur",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "passive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsābimur",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "passive",
                  "plural"
                ]
              },
              {
                "form": "accūsābiminī",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "passive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsābuntur",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "passive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsātus + present active indicative of sum",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "perfect",
                  "plural",
                  "singular"
                ]
              },
              {
                "form": "accūsātus + imperfect active indicative of sum",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "pluperfect",
                  "plural",
                  "singular"
                ]
              },
              {
                "form": "accūsātus + future active indicative of sum",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "passive",
                  "perfect",
                  "plural",
                  "singular"
                ]
              },
              {
                "form": "accūsem",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsēs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūset",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsēmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsētis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsent",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsārem",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārēs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāret",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsārēmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārētis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārent",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsāverim",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "perfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāverīs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "perfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāverit",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "perfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsāverīmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "perfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāverītis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "perfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāverint",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "perfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsāvissem",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "pluperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāssem",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "pluperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāvissēs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāssēs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāvisset",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsāsset",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsāvissēmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "pluperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāssēmus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "pluperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāvissētis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāssētis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsāvissent",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsāssent",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "pluperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūser",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "passive",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsēris",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsēre",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsētur",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsēmur",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "passive",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsēminī",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsentur",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsārer",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "passive",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārēris",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "passive",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārēre",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "passive",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārētur",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "passive",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsārēmur",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "passive",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārēminī",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "passive",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsārentur",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "passive",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "accūsātus + present active subjunctive of sum",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "perfect",
                  "plural",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsātus + imperfect active subjunctive of sum",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "pluperfect",
                  "plural",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "accūsā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsāte",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "accūsātō",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsātō",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsātōte",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "accūsantō",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsāre",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "passive",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsāminī",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "passive",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "accūsātor",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "imperative",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "accūsātor",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "imperative",
                  "passive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "accūsantor",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "imperative",
                  "passive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "accūsāre",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "present"
                ]
              },
              {
                "form": "accūsāvisse",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "perfect"
                ]
              },
              {
                "form": "accūsāsse",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "perfect"
                ]
              },
              {
                "form": "accūsātūrum esse",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "infinitive"
                ]
              },
              {
                "form": "accūsārī",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "accūsātum esse",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "accūsātum īrī",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "infinitive",
                  "passive"
                ]
              },
              {
                "form": "accūsāns",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "accūsātūrus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "future",
                  "participle"
                ]
              },
              {
                "form": "accūsātus",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "accūsandus",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "participle",
                  "passive"
                ]
              },
              {
                "form": "accūsandī",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "genitive",
                  "gerund",
                  "nominal-from-verb",
                  "nominalization"
                ]
              },
              {
                "form": "accūsandō",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dative",
                  "gerund",
                  "nominal-from-verb",
                  "nominalization"
                ]
              },
              {
                "form": "accūsandum",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "active",
                  "gerund",
                  "nominal-from-verb",
                  "nominalization"
                ]
              },
              {
                "form": "accūsandō",
                "source": "Conjugation",
                "tags": [
                  "ablative",
                  "gerund",
                  "nominal-from-verb",
                  "nominalization",
                  "passive"
                ]
              },
              {
                "form": "accūsātum",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "nominal-from-verb",
                  "nominalization",
                  "passive",
                  "supine"
                ]
              },
              {
                "form": "accūsātū",
                "source": "Conjugation",
                "tags": [
                  "ablative",
                  "nominal-from-verb",
                  "nominalization",
                  "passive",
                  "supine"
                ]
              },
              {
                "form": "conjugation-1",
                "source": "Conjugation title",
                "tags": [
                  "word-tags"
                ]
              }
            ],
        }
        self.assertEqual(ret, expected)

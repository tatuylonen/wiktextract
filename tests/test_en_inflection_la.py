# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org
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

    def test_Latin_verb1(self):
        ret = self.xinfl(
            "accuso",
            "Latin",
            "verb",
            "Conjugation",
            """
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
""",
        )  # noqa: E501
        expected = {
            "forms": [
                {
                    "form": "conjugation-1",
                    "source": "Conjugation",
                    "tags": ["table-tags"],
                },
                {
                    "form": "accūsō",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "present",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsō", "accuso#Latin")],
                },
                {
                    "form": "accūsās",
                    "tags": [
                        "active",
                        "indicative",
                        "present",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsās", "accusas#Latin")],
                },
                {
                    "form": "accūsat",
                    "tags": [
                        "active",
                        "indicative",
                        "present",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsat", "accusat#Latin")],
                },
                {
                    "form": "accūsāmus",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "plural",
                        "present",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāmus", "accusamus#Latin")],
                },
                {
                    "form": "accūsātis",
                    "tags": [
                        "active",
                        "indicative",
                        "plural",
                        "present",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsātis", "accusatis#Latin")],
                },
                {
                    "form": "accūsant",
                    "tags": [
                        "active",
                        "indicative",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsant", "accusant#Latin")],
                },
                {
                    "form": "accūsābam",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "indicative",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābam", "accusabam#Latin")],
                },
                {
                    "form": "accūsābās",
                    "tags": [
                        "active",
                        "imperfect",
                        "indicative",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābās", "accusabas#Latin")],
                },
                {
                    "form": "accūsābat",
                    "tags": [
                        "active",
                        "imperfect",
                        "indicative",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābat", "accusabat#Latin")],
                },
                {
                    "form": "accūsābāmus",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "indicative",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābāmus", "accusabamus#Latin")],
                },
                {
                    "form": "accūsābātis",
                    "tags": [
                        "active",
                        "imperfect",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābātis", "accusabatis#Latin")],
                },
                {
                    "form": "accūsābant",
                    "tags": [
                        "active",
                        "imperfect",
                        "indicative",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābant", "accusabant#Latin")],
                },
                {
                    "form": "accūsābō",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "indicative",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābō", "accusabo#Latin")],
                },
                {
                    "form": "accūsābis",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābis", "accusabis#Latin")],
                },
                {
                    "form": "accūsābit",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābit", "accusabit#Latin")],
                },
                {
                    "form": "accūsābimus",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "indicative",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābimus", "accusabimus#Latin")],
                },
                {
                    "form": "accūsābitis",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābitis", "accusabitis#Latin")],
                },
                {
                    "form": "accūsābunt",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābunt", "accusabunt#Latin")],
                },
                {
                    "form": "accūsāvī",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "perfect",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvī", "accusavi#Latin")],
                },
                {
                    "form": "accūsāvistī",
                    "tags": [
                        "active",
                        "indicative",
                        "perfect",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvistī", "accusavisti#Latin")],
                },
                {
                    "form": "accūsāstī",
                    "tags": [
                        "active",
                        "indicative",
                        "perfect",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāstī", "accusasti#Latin")],
                },
                {
                    "form": "accūsāvit",
                    "tags": [
                        "active",
                        "indicative",
                        "perfect",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvit", "accusavit#Latin")],
                },
                {
                    "form": "accūsāvimus",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "perfect",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvimus", "accusavimus#Latin")],
                },
                {
                    "form": "accūsāvistis",
                    "tags": [
                        "active",
                        "indicative",
                        "perfect",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvistis", "accusavistis#Latin")],
                },
                {
                    "form": "accūsāstis",
                    "tags": [
                        "active",
                        "indicative",
                        "perfect",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāstis", "accusastis#Latin")],
                },
                {
                    "form": "accūsāvērunt",
                    "tags": [
                        "active",
                        "indicative",
                        "perfect",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvērunt", "accusaverunt#Latin")],
                },
                {
                    "form": "accūsāvēre",
                    "tags": [
                        "active",
                        "indicative",
                        "perfect",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvēre", "accusavere#Latin")],
                },
                {
                    "form": "accūsāveram",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "pluperfect",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāveram", "accusaveram#Latin")],
                },
                {
                    "form": "accūsāverās",
                    "tags": [
                        "active",
                        "indicative",
                        "pluperfect",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverās", "accusaveras#Latin")],
                },
                {
                    "form": "accūsāverat",
                    "tags": [
                        "active",
                        "indicative",
                        "pluperfect",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverat", "accusaverat#Latin")],
                },
                {
                    "form": "accūsāverāmus",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "pluperfect",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverāmus", "accusaveramus#Latin")],
                },
                {
                    "form": "accūsāverātis",
                    "tags": [
                        "active",
                        "indicative",
                        "pluperfect",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverātis", "accusaveratis#Latin")],
                },
                {
                    "form": "accūsāverant",
                    "tags": [
                        "active",
                        "indicative",
                        "pluperfect",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverant", "accusaverant#Latin")],
                },
                {
                    "form": "accūsāverō",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "indicative",
                        "perfect",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverō", "accusavero#Latin")],
                },
                {
                    "form": "accūsāveris",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "perfect",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāveris", "accusaveris#Latin")],
                },
                {
                    "form": "accūsāverit",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "perfect",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverit", "accusaverit#Latin")],
                },
                {
                    "form": "accūsāverimus",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "indicative",
                        "perfect",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverimus", "accusaverimus#Latin")],
                },
                {
                    "form": "accūsāveritis",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "perfect",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāveritis", "accusaveritis#Latin")],
                },
                {
                    "form": "accūsāverint",
                    "tags": [
                        "active",
                        "future",
                        "indicative",
                        "perfect",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverint", "accusaverint#Latin")],
                },
                {
                    "form": "accūsor",
                    "tags": [
                        "first-person",
                        "indicative",
                        "passive",
                        "present",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsor", "accusor#Latin")],
                },
                {
                    "form": "accūsāris",
                    "tags": [
                        "indicative",
                        "passive",
                        "present",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāris", "accusaris#Latin")],
                },
                {
                    "form": "accūsāre",
                    "tags": [
                        "indicative",
                        "passive",
                        "present",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāre", "accusare#Latin")],
                },
                {
                    "form": "accūsātur",
                    "tags": [
                        "indicative",
                        "passive",
                        "present",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsātur", "accusatur#Latin")],
                },
                {
                    "form": "accūsāmur",
                    "tags": [
                        "first-person",
                        "indicative",
                        "passive",
                        "plural",
                        "present",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāmur", "accusamur#Latin")],
                },
                {
                    "form": "accūsāminī",
                    "tags": [
                        "indicative",
                        "passive",
                        "plural",
                        "present",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāminī", "accusamini#Latin")],
                },
                {
                    "form": "accūsantur",
                    "tags": [
                        "indicative",
                        "passive",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsantur", "accusantur#Latin")],
                },
                {
                    "form": "accūsābar",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "indicative",
                        "passive",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābar", "accusabar#Latin")],
                },
                {
                    "form": "accūsābāris",
                    "tags": [
                        "imperfect",
                        "indicative",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābāris", "accusabaris#Latin")],
                },
                {
                    "form": "accūsābāre",
                    "tags": [
                        "imperfect",
                        "indicative",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābāre", "accusabare#Latin")],
                },
                {
                    "form": "accūsābātur",
                    "tags": [
                        "imperfect",
                        "indicative",
                        "passive",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābātur", "accusabatur#Latin")],
                },
                {
                    "form": "accūsābāmur",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "indicative",
                        "passive",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābāmur", "accusabamur#Latin")],
                },
                {
                    "form": "accūsābāminī",
                    "tags": [
                        "imperfect",
                        "indicative",
                        "passive",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābāminī", "accusabamini#Latin")],
                },
                {
                    "form": "accūsābantur",
                    "tags": [
                        "imperfect",
                        "indicative",
                        "passive",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābantur", "accusabantur#Latin")],
                },
                {
                    "form": "accūsābor",
                    "tags": [
                        "first-person",
                        "future",
                        "indicative",
                        "passive",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābor", "accusabor#Latin")],
                },
                {
                    "form": "accūsāberis",
                    "tags": [
                        "future",
                        "indicative",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāberis", "accusaberis#Latin")],
                },
                {
                    "form": "accūsābere",
                    "tags": [
                        "future",
                        "indicative",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābere", "accusabere#Latin")],
                },
                {
                    "form": "accūsābitur",
                    "tags": [
                        "future",
                        "indicative",
                        "passive",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābitur", "accusabitur#Latin")],
                },
                {
                    "form": "accūsābimur",
                    "tags": [
                        "first-person",
                        "future",
                        "indicative",
                        "passive",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābimur", "accusabimur#Latin")],
                },
                {
                    "form": "accūsābiminī",
                    "tags": [
                        "future",
                        "indicative",
                        "passive",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābiminī", "accusabimini#Latin")],
                },
                {
                    "form": "accūsābuntur",
                    "tags": [
                        "future",
                        "indicative",
                        "passive",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsābuntur", "accusabuntur#Latin")],
                },
                {
                    "form": "accūsātus + present active indicative of sum",
                    "tags": ["indicative", "passive", "perfect"],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātus + imperfect active indicative of sum",
                    "tags": ["indicative", "passive", "pluperfect"],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātus + future active indicative of sum",
                    "tags": ["future", "indicative", "passive", "perfect"],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsem",
                    "tags": [
                        "active",
                        "first-person",
                        "present",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsem", "accusem#Latin")],
                },
                {
                    "form": "accūsēs",
                    "tags": [
                        "active",
                        "present",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsēs", "accuses#Latin")],
                },
                {
                    "form": "accūset",
                    "tags": [
                        "active",
                        "present",
                        "singular",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūset", "accuset#Latin")],
                },
                {
                    "form": "accūsēmus",
                    "tags": [
                        "active",
                        "first-person",
                        "plural",
                        "present",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsēmus", "accusemus#Latin")],
                },
                {
                    "form": "accūsētis",
                    "tags": [
                        "active",
                        "plural",
                        "present",
                        "second-person",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsētis", "accusetis#Latin")],
                },
                {
                    "form": "accūsent",
                    "tags": [
                        "active",
                        "plural",
                        "present",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsent", "accusent#Latin")],
                },
                {
                    "form": "accūsārem",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārem", "accusarem#Latin")],
                },
                {
                    "form": "accūsārēs",
                    "tags": [
                        "active",
                        "imperfect",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārēs", "accusares#Latin")],
                },
                {
                    "form": "accūsāret",
                    "tags": [
                        "active",
                        "imperfect",
                        "singular",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāret", "accusaret#Latin")],
                },
                {
                    "form": "accūsārēmus",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "plural",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārēmus", "accusaremus#Latin")],
                },
                {
                    "form": "accūsārētis",
                    "tags": [
                        "active",
                        "imperfect",
                        "plural",
                        "second-person",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārētis", "accusaretis#Latin")],
                },
                {
                    "form": "accūsārent",
                    "tags": [
                        "active",
                        "imperfect",
                        "plural",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārent", "accusarent#Latin")],
                },
                {
                    "form": "accūsāverim",
                    "tags": [
                        "active",
                        "first-person",
                        "perfect",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverim", "accusaverim#Latin")],
                },
                {
                    "form": "accūsāverīs",
                    "tags": [
                        "active",
                        "perfect",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverīs", "accusaveris#Latin")],
                },
                {
                    "form": "accūsāverit",
                    "tags": [
                        "active",
                        "perfect",
                        "singular",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverit", "accusaverit#Latin")],
                },
                {
                    "form": "accūsāverīmus",
                    "tags": [
                        "active",
                        "first-person",
                        "perfect",
                        "plural",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverīmus", "accusaverimus#Latin")],
                },
                {
                    "form": "accūsāverītis",
                    "tags": [
                        "active",
                        "perfect",
                        "plural",
                        "second-person",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverītis", "accusaveritis#Latin")],
                },
                {
                    "form": "accūsāverint",
                    "tags": [
                        "active",
                        "perfect",
                        "plural",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāverint", "accusaverint#Latin")],
                },
                {
                    "form": "accūsāvissem",
                    "tags": [
                        "active",
                        "first-person",
                        "pluperfect",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvissem", "accusavissem#Latin")],
                },
                {
                    "form": "accūsāssem",
                    "tags": [
                        "active",
                        "first-person",
                        "pluperfect",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāssem", "accusassem#Latin")],
                },
                {
                    "form": "accūsāvissēs",
                    "tags": [
                        "active",
                        "pluperfect",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvissēs", "accusavisses#Latin")],
                },
                {
                    "form": "accūsāssēs",
                    "tags": [
                        "active",
                        "pluperfect",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāssēs", "accusasses#Latin")],
                },
                {
                    "form": "accūsāvisset",
                    "tags": [
                        "active",
                        "pluperfect",
                        "singular",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvisset", "accusavisset#Latin")],
                },
                {
                    "form": "accūsāsset",
                    "tags": [
                        "active",
                        "pluperfect",
                        "singular",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāsset", "accusasset#Latin")],
                },
                {
                    "form": "accūsāvissēmus",
                    "tags": [
                        "active",
                        "first-person",
                        "pluperfect",
                        "plural",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvissēmus", "accusavissemus#Latin")],
                },
                {
                    "form": "accūsāssēmus",
                    "tags": [
                        "active",
                        "first-person",
                        "pluperfect",
                        "plural",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāssēmus", "accusassemus#Latin")],
                },
                {
                    "form": "accūsāvissētis",
                    "tags": [
                        "active",
                        "pluperfect",
                        "plural",
                        "second-person",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvissētis", "accusavissetis#Latin")],
                },
                {
                    "form": "accūsāssētis",
                    "tags": [
                        "active",
                        "pluperfect",
                        "plural",
                        "second-person",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāssētis", "accusassetis#Latin")],
                },
                {
                    "form": "accūsāvissent",
                    "tags": [
                        "active",
                        "pluperfect",
                        "plural",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāvissent", "accusavissent#Latin")],
                },
                {
                    "form": "accūsāssent",
                    "tags": [
                        "active",
                        "pluperfect",
                        "plural",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāssent", "accusassent#Latin")],
                },
                {
                    "form": "accūser",
                    "tags": [
                        "first-person",
                        "passive",
                        "present",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūser", "accuser#Latin")],
                },
                {
                    "form": "accūsēris",
                    "tags": [
                        "passive",
                        "present",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsēris", "accuseris#Latin")],
                },
                {
                    "form": "accūsēre",
                    "tags": [
                        "passive",
                        "present",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsēre", "accusere#Latin")],
                },
                {
                    "form": "accūsētur",
                    "tags": [
                        "passive",
                        "present",
                        "singular",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsētur", "accusetur#Latin")],
                },
                {
                    "form": "accūsēmur",
                    "tags": [
                        "first-person",
                        "passive",
                        "plural",
                        "present",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsēmur", "accusemur#Latin")],
                },
                {
                    "form": "accūsēminī",
                    "tags": [
                        "passive",
                        "plural",
                        "present",
                        "second-person",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsēminī", "accusemini#Latin")],
                },
                {
                    "form": "accūsentur",
                    "tags": [
                        "passive",
                        "plural",
                        "present",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsentur", "accusentur#Latin")],
                },
                {
                    "form": "accūsārer",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "passive",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārer", "accusarer#Latin")],
                },
                {
                    "form": "accūsārēris",
                    "tags": [
                        "imperfect",
                        "passive",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārēris", "accusareris#Latin")],
                },
                {
                    "form": "accūsārēre",
                    "tags": [
                        "imperfect",
                        "passive",
                        "second-person",
                        "singular",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārēre", "accusarere#Latin")],
                },
                {
                    "form": "accūsārētur",
                    "tags": [
                        "imperfect",
                        "passive",
                        "singular",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārētur", "accusaretur#Latin")],
                },
                {
                    "form": "accūsārēmur",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "passive",
                        "plural",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārēmur", "accusaremur#Latin")],
                },
                {
                    "form": "accūsārēminī",
                    "tags": [
                        "imperfect",
                        "passive",
                        "plural",
                        "second-person",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārēminī", "accusaremini#Latin")],
                },
                {
                    "form": "accūsārentur",
                    "tags": [
                        "imperfect",
                        "passive",
                        "plural",
                        "subjunctive",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsārentur", "accusarentur#Latin")],
                },
                {
                    "form": "accūsātus + present active subjunctive of sum",
                    "tags": ["passive", "perfect", "subjunctive"],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātus + imperfect active subjunctive of sum",
                    "tags": ["passive", "pluperfect", "subjunctive"],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": [
                        "active",
                        "first-person",
                        "imperative",
                        "present",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsā",
                    "tags": [
                        "active",
                        "imperative",
                        "present",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsā", "accusa#Latin")],
                },
                {
                    "form": "-",
                    "tags": [
                        "active",
                        "imperative",
                        "present",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": [
                        "active",
                        "first-person",
                        "imperative",
                        "plural",
                        "present",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsāte",
                    "tags": [
                        "active",
                        "imperative",
                        "plural",
                        "present",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāte", "accusate#Latin")],
                },
                {
                    "form": "-",
                    "tags": [
                        "active",
                        "imperative",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "imperative",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātō",
                    "tags": [
                        "active",
                        "future",
                        "imperative",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsātō", "accusato#Latin")],
                },
                {
                    "form": "accūsātō",
                    "tags": [
                        "active",
                        "future",
                        "imperative",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsātō", "accusato#Latin")],
                },
                {
                    "form": "-",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "imperative",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātōte",
                    "tags": [
                        "active",
                        "future",
                        "imperative",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsātōte", "accusatote#Latin")],
                },
                {
                    "form": "accūsantō",
                    "tags": [
                        "active",
                        "future",
                        "imperative",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsantō", "accusanto#Latin")],
                },
                {
                    "form": "-",
                    "tags": [
                        "first-person",
                        "imperative",
                        "passive",
                        "present",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsāre",
                    "tags": [
                        "imperative",
                        "passive",
                        "present",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāre", "accusare#Latin")],
                },
                {
                    "form": "-",
                    "tags": [
                        "imperative",
                        "passive",
                        "present",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": [
                        "first-person",
                        "imperative",
                        "passive",
                        "plural",
                        "present",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsāminī",
                    "tags": [
                        "imperative",
                        "passive",
                        "plural",
                        "present",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsāminī", "accusamini#Latin")],
                },
                {
                    "form": "-",
                    "tags": [
                        "imperative",
                        "passive",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": [
                        "first-person",
                        "future",
                        "imperative",
                        "passive",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātor",
                    "tags": [
                        "future",
                        "imperative",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsātor", "accusator#Latin")],
                },
                {
                    "form": "accūsātor",
                    "tags": [
                        "future",
                        "imperative",
                        "passive",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsātor", "accusator#Latin")],
                },
                {
                    "form": "-",
                    "tags": [
                        "first-person",
                        "future",
                        "imperative",
                        "passive",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": [
                        "future",
                        "imperative",
                        "passive",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsantor",
                    "tags": [
                        "future",
                        "imperative",
                        "passive",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("accūsantor", "accusantor#Latin")],
                },
                {
                    "form": "accūsāre",
                    "tags": ["active", "infinitive", "present"],
                    "source": "Conjugation",
                    "links": [("accūsāre", "accusare#Latin")],
                },
                {
                    "form": "accūsāvisse",
                    "tags": ["active", "infinitive", "perfect"],
                    "source": "Conjugation",
                    "links": [("accūsāvisse", "accusavisse#Latin")],
                },
                {
                    "form": "accūsāsse",
                    "tags": ["active", "infinitive", "perfect"],
                    "source": "Conjugation",
                    "links": [("accūsāsse", "accusasse#Latin")],
                },
                {
                    "form": "accūsātūrum esse",
                    "tags": ["active", "future", "infinitive"],
                    "source": "Conjugation",
                    "links": [
                        ("accūsātūrum", "accusaturus#Latin"),
                        ("esse", "esse#Latin"),
                    ],
                },
                {
                    "form": "accūsārī",
                    "tags": ["infinitive", "passive", "present"],
                    "source": "Conjugation",
                    "links": [("accūsārī", "accusari#Latin")],
                },
                {
                    "form": "accūsātum esse",
                    "tags": ["infinitive", "passive", "perfect"],
                    "source": "Conjugation",
                    "links": [
                        ("accūsātum", "accusatus#Latin"),
                        ("esse", "esse#Latin"),
                    ],
                },
                {
                    "form": "accūsātum īrī",
                    "tags": ["future", "infinitive", "passive"],
                    "source": "Conjugation",
                    "links": [
                        ("accūsātum", "accusatum#Latin"),
                        ("īrī", "iri#Latin"),
                    ],
                },
                {
                    "form": "accūsāns",
                    "tags": ["active", "participle", "present"],
                    "source": "Conjugation",
                    "links": [("accūsāns", "accusans#Latin")],
                },
                {
                    "form": "-",
                    "tags": ["active", "participle", "perfect"],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātūrus",
                    "tags": ["active", "future", "participle"],
                    "source": "Conjugation",
                    "links": [("accūsātūrus", "accusaturus#Latin")],
                },
                {
                    "form": "-",
                    "tags": ["participle", "passive", "present"],
                    "source": "Conjugation",
                },
                {
                    "form": "accūsātus",
                    "tags": ["participle", "passive", "perfect"],
                    "source": "Conjugation",
                    "links": [("accūsātus", "accusatus#Latin")],
                },
                {
                    "form": "accūsandus",
                    "tags": ["future", "participle", "passive"],
                    "source": "Conjugation",
                    "links": [("accūsandus", "accusandus#Latin")],
                },
                {
                    "form": "accūsandī",
                    "tags": ["genitive", "gerund", "noun-from-verb"],
                    "source": "Conjugation",
                    "links": [("accūsandī", "accusandi#Latin")],
                },
                {
                    "form": "accūsandō",
                    "tags": ["dative", "gerund", "noun-from-verb"],
                    "source": "Conjugation",
                    "links": [("accūsandō", "accusando#Latin")],
                },
                {
                    "form": "accūsandum",
                    "tags": ["accusative", "gerund", "noun-from-verb"],
                    "source": "Conjugation",
                    "links": [("accūsandum", "accusandum#Latin")],
                },
                {
                    "form": "accūsandō",
                    "tags": ["ablative", "gerund", "noun-from-verb"],
                    "source": "Conjugation",
                    "links": [("accūsandō", "accusando#Latin")],
                },
                {
                    "form": "accūsātum",
                    "tags": ["accusative", "noun-from-verb", "supine"],
                    "source": "Conjugation",
                    "links": [("accūsātum", "accusatum#Latin")],
                },
                {
                    "form": "accūsātū",
                    "tags": ["ablative", "noun-from-verb", "supine"],
                    "source": "Conjugation",
                    "links": [("accūsātū", "accusatu#Latin")],
                },
            ]
        }
        self.assertEqual(expected, ret)

    def test_Latin_noun1(self):
        # This also tests handling of a form starting with "*" (non-attested)
        ret = self.xinfl(
            "mare",
            "Latin",
            "noun",
            "Declension",
            """
[[Appendix:Latin third declension|Third-declension]] noun (neuter, “pure” i-stem).<templatestyles src="Template%3Ala-decl-1st%2Fstyle.css">

{| class="prettytable+inflection-table+inflection-table-la"

|-

! class="corner-header" | Case


! class="number-header" | Singular


! class="number-header" | Plural


|-

! class="case-header" | [[nominative case|Nominative]]


| class="form-cell" | <span class="Latn+form-of+lang-la+nom%7Cs-form-of++++origin-mare+++" lang="la">[[mare#Latin|mare]]</span>


| class="form-cell" | <span class="Latn+form-of+lang-la+nom%7Cp-form-of++++origin-mare+++" lang="la">[[maria#Latin|maria]]</span>


|-

! class="case-header" | [[genitive case|Genitive]]


| class="form-cell" | <span class="Latn+form-of+lang-la+gen%7Cs-form-of++++origin-mare+++" lang="la">[[maris#Latin|maris]]</span>


| class="form-cell" | <span class="Latn+form-of+lang-la+gen%7Cp-form-of++++origin-mare+++" lang="la">[[Reconstruction&#x3a;Latin/marium|*marium]]</span><br><span class="Latn+form-of+lang-la+gen%7Cp-form-of++++origin-mare+++" lang="la">[[marum#Latin|marum]]</span>


|-

! class="case-header" | [[dative case|Dative]]


| class="form-cell" | <span class="Latn+form-of+lang-la+dat%7Cs-form-of++++origin-mare+++" lang="la">[[mari#Latin|marī]]</span>


| class="form-cell" | <span class="Latn+form-of+lang-la+dat%7Cp-form-of++++origin-mare+++" lang="la">[[maribus#Latin|maribus]]</span>


|-

! class="case-header" | [[accusative case|Accusative]]


| class="form-cell" | <span class="Latn+form-of+lang-la+acc%7Cs-form-of++++origin-mare+++" lang="la">[[mare#Latin|mare]]</span>


| class="form-cell" | <span class="Latn+form-of+lang-la+acc%7Cp-form-of++++origin-mare+++" lang="la">[[maria#Latin|maria]]</span>


|-

! class="case-header" | [[ablative case|Ablative]]


| class="form-cell" | <span class="Latn+form-of+lang-la+abl%7Cs-form-of++++origin-mare+++" lang="la">[[mari#Latin|marī]]</span><br><span class="Latn+form-of+lang-la+abl%7Cs-form-of++++origin-mare+++" lang="la">[[mare#Latin|mare]]</span>


| class="form-cell" | <span class="Latn+form-of+lang-la+abl%7Cp-form-of++++origin-mare+++" lang="la">[[maribus#Latin|maribus]]</span>


|-

! class="case-header" | [[vocative case|Vocative]]


| class="form-cell" | <span class="Latn+form-of+lang-la+voc%7Cs-form-of++++origin-mare+++" lang="la">[[mare#Latin|mare]]</span>


| class="form-cell" | <span class="Latn+form-of+lang-la+voc%7Cp-form-of++++origin-mare+++" lang="la">[[maria#Latin|maria]]</span>


|-

|}

*The ablative singular can be ''marī'' or ''mare''.
*The genitive plural form *''marium'', although regularly formed for an i-stem noun, is not attested in the corpus of classical texts. ''Marum'' is found only once, in a line from Gnaeus Naevius.
*The 5th/6th-century grammarian [[w:Priscian|Priscian]] (''Institutiones'' 7) says it is rarely used in the genitive plural, noting Caesar's use of ''maribus'' too. Similarly, the 4th-century grammarian [[w:Flavius Sosipater Charisius|Charisius]] claims it lacks both a genitive plural *''marium'' and a *''maribus'' form (but see the quotation from Julius Caesar above): <blockquote>''"maria" tamen quamvis dicantur pluraliter, attamen nec "marium" nec "maribus" dicemus'' <br>— although ''maria'' can be said in the plural, nevertheless we won't say ''marium'' nor ''maribus'' (''Ars'' 1.11).</blockquote>
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
                    "form": "mare",
                    "tags": ["nominative", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "maria",
                    "tags": ["nominative", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "maris",
                    "tags": ["genitive", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "marium",
                    "tags": ["genitive", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "marum",
                    "tags": ["genitive", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "marī",
                    "tags": ["dative", "singular"],
                    "source": "Declension",
                    "links": [("marī", "mari#Latin")],
                },
                {
                    "form": "maribus",
                    "tags": ["dative", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "mare",
                    "tags": ["accusative", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "maria",
                    "tags": ["accusative", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "marī",
                    "tags": ["ablative", "singular"],
                    "source": "Declension",
                    "links": [("marī", "mari#Latin")],
                },
                {
                    "form": "mare",
                    "tags": ["ablative", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "maribus",
                    "tags": ["ablative", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "mare",
                    "tags": ["singular", "vocative"],
                    "source": "Declension",
                },
                {
                    "form": "maria",
                    "tags": ["plural", "vocative"],
                    "source": "Declension",
                },
            ]
        }

        self.assertEqual(expected, ret)

    def test_Latin_adj1(self):
        ret = self.xinfl(
            "magnificus",
            "Latin",
            "adj",
            "Declension",
            """
[[Appendix:Latin first declension|First]]/[[Appendix:Latin second declension|second-declension]] adjective.

{| class="prettytable+inflection-table+inflection-table-la"

|-

! style="background%3A%23549EA0%3B+font-style%3Aitalic%3B" | Number


! style="background%3A%23549EA0%3B+font-style%3Aitalic%3B" colspan="3" | Singular


| rowspan="2" |


! style="background%3A%23549EA0%3B+font-style%3Aitalic%3B" colspan="3" | Plural


|-

! style="background%3A%2340E0D0%3B+font-style%3Aitalic%3B" | Case / Gender


! style="background%3A%2340E0D0%3B" | Masculine


! style="background%3A%2340E0D0%3B" | Feminine


! style="background%3A%2340E0D0%3B" | Neuter


! style="background%3A%2340E0D0%3B" | Masculine


! style="background%3A%2340E0D0%3B" | Feminine


! style="background%3A%2340E0D0%3B" | Neuter


|-

! style="background%3A%2340E0D0%3B+font-style%3Aitalic%3B" | [[nominative case|Nominative]]


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+nom%7Cm%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnificus#Latin|magnificus]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+nom%7Cf%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifica#Latin|magnifica]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+nom%7Cn%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnificum#Latin|magnificum]]</span>


| rowspan="6" |


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+nom%7Cm%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnifici#Latin|magnificī]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+nom%7Cf%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificae#Latin|magnificae]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+nom%7Cn%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnifica#Latin|magnifica]]</span>


|-

! style="background%3A%2340E0D0%3B+font-style%3Aitalic%3B" | [[genitive case|Genitive]]


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+gen%7Cm%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifici#Latin|magnificī]]</span>


| style="background%3A%23F8F8FF%3B" align="center" rowspan="2" | <span class="Latn+form-of+lang-la+gen%7Cf%7Cs%7C%3B%7Cdat%7Cf%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnificae#Latin|magnificae]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+gen%7Cn%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifici#Latin|magnificī]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+gen%7Cm%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificorum#Latin|magnificōrum]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+gen%7Cf%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificarum#Latin|magnificārum]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+gen%7Cn%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificorum#Latin|magnificōrum]]</span>


|-

! style="background%3A%2340E0D0%3B+font-style%3Aitalic%3B" | [[dative case|Dative]]


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+dat%7Cm%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifico#Latin|magnificō]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+dat%7Cn%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifico#Latin|magnificō]]</span>


| style="background%3A%23F8F8FF%3B" align="center" colspan="3" | <span class="Latn+form-of+lang-la+dat%7Cm%7Cp%7C%3B%7Cdat%7Cf%7Cp%7C%3B%7Cdat%7Cn%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificis#Latin|magnificīs]]</span>


|-

! style="background%3A%2340E0D0%3B+font-style%3Aitalic%3B" | [[accusative case|Accusative]]


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+acc%7Cm%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnificum#Latin|magnificum]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+acc%7Cf%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnificam#Latin|magnificam]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+acc%7Cn%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnificum#Latin|magnificum]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+acc%7Cm%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificos#Latin|magnificōs]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+acc%7Cf%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificas#Latin|magnificās]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+acc%7Cn%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnifica#Latin|magnifica]]</span>


|-

! style="background%3A%2340E0D0%3B+font-style%3Aitalic%3B" | [[ablative case|Ablative]]


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+abl%7Cm%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifico#Latin|magnificō]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+abl%7Cf%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifica#Latin|magnificā]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+abl%7Cn%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifico#Latin|magnificō]]</span>


| style="background%3A%23F8F8FF%3B" align="center" colspan="3" | <span class="Latn+form-of+lang-la+abl%7Cm%7Cp%7C%3B%7Cabl%7Cf%7Cp%7C%3B%7Cabl%7Cn%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificis#Latin|magnificīs]]</span>


|-

! style="background%3A%2340E0D0%3B+font-style%3Aitalic%3B" | [[vocative case|Vocative]]


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+voc%7Cm%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifice#Latin|magnifice]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+voc%7Cf%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnifica#Latin|magnifica]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+voc%7Cn%7Cs-form-of++++origin-magnificus+++" lang="la">[[magnificum#Latin|magnificum]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+voc%7Cm%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnifici#Latin|magnificī]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+voc%7Cf%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnificae#Latin|magnificae]]</span>


| style="background%3A%23F8F8FF%3B" align="center" | <span class="Latn+form-of+lang-la+voc%7Cn%7Cp-form-of++++origin-magnificus+++" lang="la">[[magnifica#Latin|magnifica]]</span>


|}
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
                    "form": "magnificus",
                    "tags": ["masculine", "nominative", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnifica",
                    "tags": ["feminine", "nominative", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnificum",
                    "tags": ["neuter", "nominative", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnificī",
                    "tags": ["masculine", "nominative", "plural"],
                    "source": "Declension",
                    "links": [("magnificī", "magnifici#Latin")],
                },
                {
                    "form": "magnificae",
                    "tags": ["feminine", "nominative", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "magnifica",
                    "tags": ["neuter", "nominative", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "magnificī",
                    "tags": ["genitive", "masculine", "singular"],
                    "source": "Declension",
                    "links": [("magnificī", "magnifici#Latin")],
                },
                {
                    "form": "magnificae",
                    "tags": ["feminine", "genitive", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnificī",
                    "tags": ["genitive", "neuter", "singular"],
                    "source": "Declension",
                    "links": [("magnificī", "magnifici#Latin")],
                },
                {
                    "form": "magnificōrum",
                    "tags": ["genitive", "masculine", "plural"],
                    "source": "Declension",
                    "links": [("magnificōrum", "magnificorum#Latin")],
                },
                {
                    "form": "magnificārum",
                    "tags": ["feminine", "genitive", "plural"],
                    "source": "Declension",
                    "links": [("magnificārum", "magnificarum#Latin")],
                },
                {
                    "form": "magnificōrum",
                    "tags": ["genitive", "neuter", "plural"],
                    "source": "Declension",
                    "links": [("magnificōrum", "magnificorum#Latin")],
                },
                {
                    "form": "magnificō",
                    "tags": ["dative", "masculine", "singular"],
                    "source": "Declension",
                    "links": [("magnificō", "magnifico#Latin")],
                },
                {
                    "form": "magnificae",
                    "tags": ["dative", "feminine", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnificō",
                    "tags": ["dative", "neuter", "singular"],
                    "source": "Declension",
                    "links": [("magnificō", "magnifico#Latin")],
                },
                {
                    "form": "magnificīs",
                    "tags": [
                        "dative",
                        "feminine",
                        "masculine",
                        "neuter",
                        "plural",
                    ],
                    "source": "Declension",
                    "links": [("magnificīs", "magnificis#Latin")],
                },
                {
                    "form": "magnificum",
                    "tags": ["accusative", "masculine", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnificam",
                    "tags": ["accusative", "feminine", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnificum",
                    "tags": ["accusative", "neuter", "singular"],
                    "source": "Declension",
                },
                {
                    "form": "magnificōs",
                    "tags": ["accusative", "masculine", "plural"],
                    "source": "Declension",
                    "links": [("magnificōs", "magnificos#Latin")],
                },
                {
                    "form": "magnificās",
                    "tags": ["accusative", "feminine", "plural"],
                    "source": "Declension",
                    "links": [("magnificās", "magnificas#Latin")],
                },
                {
                    "form": "magnifica",
                    "tags": ["accusative", "neuter", "plural"],
                    "source": "Declension",
                },
                {
                    "form": "magnificō",
                    "tags": ["ablative", "masculine", "singular"],
                    "source": "Declension",
                    "links": [("magnificō", "magnifico#Latin")],
                },
                {
                    "form": "magnificā",
                    "tags": ["ablative", "feminine", "singular"],
                    "source": "Declension",
                    "links": [("magnificā", "magnifica#Latin")],
                },
                {
                    "form": "magnificō",
                    "tags": ["ablative", "neuter", "singular"],
                    "source": "Declension",
                    "links": [("magnificō", "magnifico#Latin")],
                },
                {
                    "form": "magnificīs",
                    "tags": [
                        "ablative",
                        "feminine",
                        "masculine",
                        "neuter",
                        "plural",
                    ],
                    "source": "Declension",
                    "links": [("magnificīs", "magnificis#Latin")],
                },
                {
                    "form": "magnifice",
                    "tags": ["masculine", "singular", "vocative"],
                    "source": "Declension",
                },
                {
                    "form": "magnifica",
                    "tags": ["feminine", "singular", "vocative"],
                    "source": "Declension",
                },
                {
                    "form": "magnificum",
                    "tags": ["neuter", "singular", "vocative"],
                    "source": "Declension",
                },
                {
                    "form": "magnificī",
                    "tags": ["masculine", "plural", "vocative"],
                    "source": "Declension",
                    "links": [("magnificī", "magnifici#Latin")],
                },
                {
                    "form": "magnificae",
                    "tags": ["feminine", "plural", "vocative"],
                    "source": "Declension",
                },
                {
                    "form": "magnifica",
                    "tags": ["neuter", "plural", "vocative"],
                    "source": "Declension",
                },
            ]
        }

        self.assertEqual(expected, ret)

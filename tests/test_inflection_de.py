# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.inflection import parse_inflection_section
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class InflTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 100000
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
        parse_inflection_section(self.wxr, data, word, lang, pos,
                                 section, tree)
        return data

    def test_German_verb1(self):
        ret = self.xinfl("aussteigen", "German", "verb", "Conjugation", """
<div class="NavFrame" style>
<div class="NavHead" style>Conjugation of <i class="Latn+mention" lang="de">[[aussteigen#German|aussteigen]]</i> (class 1 [[Appendix:Glossary#strong verb|strong]], auxiliary <i class="Latn+mention" lang="de">[[sein#German|sein]]</i>)</div>
<div class="NavContent">

{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23fafafa%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! colspan="2" style="background%3A%23d0d0d0" | <span title="Infinitiv">infinitive</span>


| colspan="4" | <span class="Latn+form-of+lang-de+inf-form-of++++origin-aussteigen+++" lang="de">[[aussteigen#German|aussteigen]]</span>


|-

! colspan="2" style="background%3A%23d0d0d0" | <span title="Partizip+I+%28Partizip+Pr%C3%A4sens%29">present participle</span>


| colspan="4" | <span class="Latn+form-of+lang-de+pres%7Cpart-form-of++++origin-aussteigen+++" lang="de">[[aussteigend#German|aussteigend]]</span>


|-

! colspan="2" style="background%3A%23d0d0d0" | <span title="Partizip+II+%28Partizip+Perfekt%29">past participle</span>


| colspan="4" | <span class="Latn+form-of+lang-de+perf%7Cpart-form-of++++origin-aussteigen+++" lang="de">[[ausgestiegen#German|ausgestiegen]]</span>


|-

! colspan="2" style="background%3A%23d0d0d0" | zu-infinitive


| colspan="4" | <span class="Latn+form-of+lang-de+zu-form-of++++origin-aussteigen+++" lang="de">[[auszusteigen#German|auszusteigen]]</span>


|-

! colspan="2" style="background%3A%23d0d0d0" | <span title="Hilfsverb">auxiliary</span>


| colspan="4" | <span class="Latn" lang="de">[[sein#German|sein]]</span>


|-

| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | <span title="Indikativ">indicative</span>


| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | <span title="Konjunktiv">subjunctive</span>


|-

! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | <span title="Pr%C3%A4sens">present</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[steige aus#German|steige aus]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[steigen aus#German|steigen aus]]</span>


! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | <span title="Konjunktiv+I+%28Konjunktiv+Pr%C3%A4sens%29">i</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[steige aus#German|steige aus]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[steigen aus#German|steigen aus]]</span>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[steigst aus#German|steigst aus]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[steigt aus#German|steigt aus]]</span>


| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[steigest aus#German|steigest aus]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[steiget aus#German|steiget aus]]</span>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[steigt aus#German|steigt aus]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[steigen aus#German|steigen aus]]</span>


| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[steige aus#German|steige aus]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[steigen aus#German|steigen aus]]</span>


|-

| colspan="6" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! rowspan="3" style="background%3A%23c0cfe4" | <span title="Pr%C3%A4teritum">preterite</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[stieg aus#German|stieg aus]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[stiegen aus#German|stiegen aus]]</span>


! rowspan="3" style="background%3A%23c0cfe4" | <span title="Konjunktiv+II+%28Konjunktiv+Pr%C3%A4teritum%29">ii</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stiege aus#German|stiege aus]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stiegen aus#German|stiegen aus]]</span><sup style="color%3A+red">1</sup>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[stiegst aus#German|stiegst aus]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[stiegt aus#German|stiegt aus]]</span>


| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stiegest aus#German|stiegest aus]]</span><sup style="color%3A+red">1</sup><br><span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stiegst aus#German|stiegst aus]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stieget aus#German|stieget aus]]</span><sup style="color%3A+red">1</sup><br><span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stiegt aus#German|stiegt aus]]</span><sup style="color%3A+red">1</sup>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[stieg aus#German|stieg aus]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[stiegen aus#German|stiegen aus]]</span>


| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stiege aus#German|stiege aus]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[stiegen aus#German|stiegen aus]]</span><sup style="color%3A+red">1</sup>


|-

| colspan="6" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! style="background%3A%23c0cfe4" | <span title="Imperativ">imperative</span>


| <span class="Latn+form-of+lang-de+s%7Cimp-form-of++++origin-aussteigen+++" lang="de">[[steig aus#German|steig aus]]</span> (<span class="Latn" lang="de">[[du#German|du]]</span>)<br><span class="Latn+form-of+lang-de+s%7Cimp-form-of++++origin-aussteigen+++" lang="de">[[steige aus#German|steige aus]]</span> (<span class="Latn" lang="de">[[du#German|du]]</span>)


| <span class="Latn+form-of+lang-de+p%7Cimp-form-of++++origin-aussteigen+++" lang="de">[[steigt aus#German|steigt aus]]</span> (<span class="Latn" lang="de">[[ihr#German|ihr]]</span>)


| colspan="3" style="background%3A%23e0e0e0" |


|}
<div style="width%3A100%25%3Btext-align%3Aleft%3Bbackground%3A%23d9ebff">
<div style="display%3Ainline-block%3Btext-align%3Aleft%3Bpadding-left%3A1em%3Bpadding-right%3A1em">
<sup style="color%3A+red">1</sup>Rare except in very formal contexts; alternative in <i class="Latn+mention" lang="de">[[würde#German|würde]]</i> normally preferred.
</div></div>
</div></div>
<div class="NavFrame" style>
<div class="NavHead" style>Subordinate-clause forms of <i class="Latn+mention" lang="de">[[aussteigen#German|aussteigen]]</i> (class 1 [[Appendix:Glossary#strong verb|strong]], auxiliary <i class="Latn+mention" lang="de">[[sein#German|sein]]</i>)</div>
<div class="NavContent">

{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23fafafa%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | <span title="Indikativ">indicative</span>


| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | <span title="Konjunktiv">subjunctive</span>


|-

! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | <span title="Pr%C3%A4sens">present</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Cdep%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[aussteige#German|aussteige]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Cdep%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[aussteigen#German|aussteigen]]</span>


! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | <span title="Konjunktiv+I+%28Konjunktiv+Pr%C3%A4sens%29">i</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Cdep%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[aussteige#German|aussteige]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Cdep%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[aussteigen#German|aussteigen]]</span>


|-

| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Cdep%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[aussteigst#German|aussteigst]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Cdep%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[aussteigt#German|aussteigt]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Cdep%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[aussteigest#German|aussteigest]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Cdep%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[aussteiget#German|aussteiget]]</span>


|-

| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Cdep%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[aussteigt#German|aussteigt]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Cdep%7Cpres-form-of++++origin-aussteigen+++" lang="de">[[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Cdep%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[aussteige#German|aussteige]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Cdep%7Csub%7CI-form-of++++origin-aussteigen+++" lang="de">[[aussteigen#German|aussteigen]]</span>


|-

| colspan="6" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! rowspan="3" style="background%3A%23c0cfe4" | <span title="Pr%C3%A4teritum">preterite</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Cdep%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[ausstieg#German|ausstieg]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Cdep%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[ausstiegen#German|ausstiegen]]</span>


! rowspan="3" style="background%3A%23c0cfe4" | <span title="Konjunktiv+II+%28Konjunktiv+Pr%C3%A4teritum%29">ii</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn+form-of+lang-de+1%7Cs%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstiege#German|ausstiege]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn+form-of+lang-de+1%7Cp%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstiegen#German|ausstiegen]]</span><sup style="color%3A+red">1</sup>


|-

| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Cdep%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[ausstiegst#German|ausstiegst]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Cdep%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[ausstiegt#German|ausstiegt]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstiegest#German|ausstiegest]]</span><sup style="color%3A+red">1</sup><br><span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn+form-of+lang-de+2%7Cs%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstiegst#German|ausstiegst]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstieget#German|ausstieget]]</span><sup style="color%3A+red">1</sup><br><span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn+form-of+lang-de+2%7Cp%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstiegt#German|ausstiegt]]</span><sup style="color%3A+red">1</sup>


|-

| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Cdep%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[ausstieg#German|ausstieg]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Cdep%7Cpret-form-of++++origin-aussteigen+++" lang="de">[[ausstiegen#German|ausstiegen]]</span>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn+form-of+lang-de+3%7Cs%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstiege#German|ausstiege]]</span><sup style="color%3A+red">1</sup>


| <span class="Latn" lang="de">[[dass#German|dass]]</span> <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn+form-of+lang-de+3%7Cp%7Cdep%7Csub%7CII-form-of++++origin-aussteigen+++" lang="de">[[ausstiegen#German|ausstiegen]]</span><sup style="color%3A+red">1</sup>


|}
<div style="width%3A100%25%3Btext-align%3Aleft%3Bbackground%3A%23d9ebff">
<div style="display%3Ainline-block%3Btext-align%3Aleft%3Bpadding-left%3A1em%3Bpadding-right%3A1em">
<sup style="color%3A+red">1</sup>Rare except in very formal contexts; alternative in <i class="Latn+mention" lang="de">[[würde#German|würde]]</i> normally preferred.
</div></div>
</div></div>
<div class="NavFrame" style>
<div class="NavHead" style>Composed forms of <i class="Latn+mention" lang="de">[[aussteigen#German|aussteigen]]</i> (class 1 [[Appendix:Glossary#strong verb|strong]], auxiliary <i class="Latn+mention" lang="de">[[sein#German|sein]]</i>)</div>
<div class="NavContent">

{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23fafafa%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! colspan="6" style="background%3A%2399cc99" | <span title="Perfekt">perfect</span>


|-

! rowspan="3" style="background%3A%23cfedcc%3B+width%3A7em" | <span title="Indikativ">indicative</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[bin#German|bin]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[sind#German|sind]] [[ausgestiegen#German|ausgestiegen]]</span>


! rowspan="3" style="background%3A%23cfedcc%3B+width%3A7em" | <span title="Konjunktiv">subjunctive</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[sei#German|sei]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[seien#German|seien]] [[ausgestiegen#German|ausgestiegen]]</span>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[bist#German|bist]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[seid#German|seid]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[seist#German|seist]] [[ausgestiegen#German|ausgestiegen]]</span><br><span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[seiest#German|seiest]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[seiet#German|seiet]] [[ausgestiegen#German|ausgestiegen]]</span>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[ist#German|ist]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[sind#German|sind]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[sei#German|sei]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[seien#German|seien]] [[ausgestiegen#German|ausgestiegen]]</span>


|-

! colspan="6" style="background%3A%2399CC99" | <span title="Plusquamperfekt">pluperfect</span>


|-

! rowspan="3" style="background%3A%23cfedcc" | <span title="Indikativ">indicative</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[war#German|war]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[waren#German|waren]] [[ausgestiegen#German|ausgestiegen]]</span>


! rowspan="3" style="background%3A%23cfedcc" | <span title="Konjunktiv">subjunctive</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[wäre#German|wäre]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[wären#German|wären]] [[ausgestiegen#German|ausgestiegen]]</span>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[warst#German|warst]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[wart#German|wart]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[wärst#German|wärst]] [[ausgestiegen#German|ausgestiegen]]</span><br><span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[wärest#German|wärest]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[wärt#German|wärt]] [[ausgestiegen#German|ausgestiegen]]</span><br><span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[wäret#German|wäret]] [[ausgestiegen#German|ausgestiegen]]</span>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[war#German|war]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[waren#German|waren]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[wäre#German|wäre]] [[ausgestiegen#German|ausgestiegen]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[wären#German|wären]] [[ausgestiegen#German|ausgestiegen]]</span>


|-

! colspan="6" style="background%3A%239999DF" | <span title="Futur+I">future i</span>


|-

! rowspan="3" style="background%3A%23ccccff" | <span title="Infinitiv">infinitive</span>


| rowspan="3" colspan="2" | <span class="Latn" lang="de">[[aussteigen#German|aussteigen]] [[werden#German|werden]]</span>


! rowspan="3" style="background%3A%23ccccff" | <span title="Konjunktiv+I+%28Konjunktiv+Pr%C3%A4sens%29">subjunctive i</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[werde#German|werde]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[aussteigen#German|aussteigen]]</span>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[werdest#German|werdest]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[werdet#German|werdet]] [[aussteigen#German|aussteigen]]</span>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[werde#German|werde]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[aussteigen#German|aussteigen]]</span>


|-

! colspan="6" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! rowspan="3" style="background%3A%23ccccff" | <span title="Indikativ">indicative</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[werde#German|werde]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[aussteigen#German|aussteigen]]</span>


! rowspan="3" style="background%3A%23ccccff" | <span title="Konjunktiv+II+%28Konjunktiv+Pr%C3%A4teritum%29">subjunctive ii</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[würde#German|würde]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[würden#German|würden]] [[aussteigen#German|aussteigen]]</span>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[wirst#German|wirst]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[werdet#German|werdet]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[würdest#German|würdest]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[würdet#German|würdet]] [[aussteigen#German|aussteigen]]</span>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[wird#German|wird]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[würde#German|würde]] [[aussteigen#German|aussteigen]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[würden#German|würden]] [[aussteigen#German|aussteigen]]</span>


|-

! colspan="6" style="background%3A%239999DF" | <span title="Futur+II">future ii</span>


|-

! rowspan="3" style="background%3A%23ccccff" | <span title="Infinitiv">infinitive</span>


| rowspan="3" colspan="2" | <span class="Latn" lang="de">[[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]] [[werden#German|werden]]</span>


! rowspan="3" style="background%3A%23ccccff" | <span title="Konjunktiv+I+%28Konjunktiv+Pr%C3%A4sens%29">subjunctive i</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[werde#German|werde]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[werdest#German|werdest]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[werdet#German|werdet]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[werde#German|werde]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


|-

! colspan="6" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! rowspan="3" style="background%3A%23ccccff" | <span title="Indikativ">indicative</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[werde#German|werde]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


! rowspan="3" style="background%3A%23ccccff" | <span title="Konjunktiv+II+%28Konjunktiv+Pr%C3%A4teritum%29">subjunctive ii</span>


| <span class="Latn" lang="de">[[ich#German|ich]]</span> <span class="Latn" lang="de">[[würde#German|würde]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[wir#German|wir]]</span> <span class="Latn" lang="de">[[würden#German|würden]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


|-

| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[wirst#German|wirst]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[werdet#German|werdet]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[du#German|du]]</span> <span class="Latn" lang="de">[[würdest#German|würdest]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[ihr#German|ihr]]</span> <span class="Latn" lang="de">[[würdet#German|würdet]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


|-

| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[wird#German|wird]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[werden#German|werden]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[er#German|er]]</span> <span class="Latn" lang="de">[[würde#German|würde]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


| <span class="Latn" lang="de">[[sie#German|sie]]</span> <span class="Latn" lang="de">[[würden#German|würden]] [[ausgestiegen#German|ausgestiegen]] [[sein#German|sein]]</span>


|}
</div></div>[[Category:German verbs with red links in their inflection tables|AUSSTEIGEN]]
""")  # noqa: E501
        expected = {
            "forms": [
                {
                    "form": "strong",
                    "source": "Conjugation",
                    "tags": [
                        "table-tags"
                    ]
                },
                {
                    "form": "1 strong",
                    "source": "Conjugation",
                    "tags": [
                        "class"
                    ]
                },
                {
                    "form": "sein",
                    "source": "Conjugation",
                    "tags": ["auxiliary"],
                },
                {
                    "form": "aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "infinitive"
                    ]
                },
                {
                    "form": "aussteigend",
                    "source": "Conjugation",
                    "tags": [
                        "participle",
                        "present"
                    ]
                },
                {
                    "form": "ausgestiegen",
                    "source": "Conjugation",
                    "tags": ["participle", "past"],
                },
                {
                    "form": "auszusteigen",
                    "source": "Conjugation",
                    "tags": [
                        "infinitive",
                        "infinitive-zu"
                    ]
                },
                {
                    "form": "steige aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "present",
                        "singular"
                    ]
                },
                {
                    "form": "steigen aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "plural",
                        "present"
                    ]
                },
                {
                    "form": "steige aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "steigen aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "plural",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "steigst aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "present",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "steigt aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "present",
                        "second-person"
                    ]
                },
                {
                    "form": "steigest aus",
                    "source": "Conjugation",
                    "tags": [
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "steiget aus",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "steigt aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "present",
                        "singular",
                        "third-person"
                    ]
                },
                {
                    "form": "steigen aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "present",
                        "third-person"
                    ]
                },
                {
                    "form": "steige aus",
                    "source": "Conjugation",
                    "tags": [
                        "singular",
                        "subjunctive",
                        "subjunctive-i",
                        "third-person"
                    ]
                },
                {
                    "form": "steigen aus",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "subjunctive",
                        "subjunctive-i",
                        "third-person"
                    ]
                },
                {
                    "form": "stieg aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "preterite",
                        "singular"
                    ]
                },
                {
                    "form": "stiegen aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "plural",
                        "preterite"
                    ]
                },
                {
                    "form": "stiege aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "stiegen aus",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "plural",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "stiegst aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "preterite",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "stiegt aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "preterite",
                        "second-person"
                    ]
                },
                {
                    "form": "stiegest aus",
                    "source": "Conjugation",
                    "tags": [
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "stiegst aus",
                    "source": "Conjugation",
                    "tags": [
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "stieget aus",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "stiegt aus",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "stieg aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "preterite",
                        "singular",
                        "third-person"
                    ]
                },
                {
                    "form": "stiegen aus",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "preterite",
                        "third-person"
                    ]
                },
                {
                    "form": "stiege aus",
                    "source": "Conjugation",
                    "tags": [
                        "singular",
                        "subjunctive",
                        "subjunctive-ii",
                        "third-person"
                    ]
                },
                {
                    "form": "stiegen aus",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "subjunctive",
                        "subjunctive-ii",
                        "third-person"
                    ]
                },
                {
                    "form": "steig aus",
                    "source": "Conjugation",
                    "tags": [
                        "imperative",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "steige aus",
                    "source": "Conjugation",
                    "tags": [
                        "imperative",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "steigt aus",
                    "source": "Conjugation",
                    "tags": [
                        "imperative",
                        "plural",
                        "second-person"
                    ]
                },
                {
                    "form": "strong",
                    "source": "Conjugation",
                    "tags": [
                        "table-tags"
                    ]
                },
                {
                    "form": "1 strong",
                    "source": "Conjugation",
                    "tags": [
                        "class"
                    ]
                },
                {
                    "form": "sein",
                    "source": "Conjugation",
                    "tags": [
                        "auxiliary"
                    ]
                },
                {
                    "form": "aussteige",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "present",
                        "singular",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "plural",
                        "present",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteige",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-i",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "plural",
                        "subjunctive",
                        "subjunctive-i",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteigst",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "present",
                        "second-person",
                        "singular",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteigt",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "present",
                        "second-person",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteigest",
                    "source": "Conjugation",
                    "tags": [
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-i",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteiget",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-i",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "aussteigt",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "present",
                        "singular",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "present",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "aussteige",
                    "source": "Conjugation",
                    "tags": [
                        "singular",
                        "subjunctive",
                        "subjunctive-i",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "subjunctive",
                        "subjunctive-i",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "ausstieg",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "preterite",
                        "singular",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "plural",
                        "preterite",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiege",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "plural",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiegst",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "preterite",
                        "second-person",
                        "singular",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiegt",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "preterite",
                        "second-person",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiegest",
                    "source": "Conjugation",
                    "tags": [
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiegst",
                    "source": "Conjugation",
                    "tags": [
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstieget",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstiegt",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause"
                    ]
                },
                {
                    "form": "ausstieg",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "preterite",
                        "singular",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "ausstiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "plural",
                        "preterite",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "ausstiege",
                    "source": "Conjugation",
                    "tags": [
                        "singular",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "ausstiegen",
                    "source": "Conjugation",
                    "tags": [
                        "plural",
                        "subjunctive",
                        "subjunctive-ii",
                        "subordinate-clause",
                        "third-person"
                    ]
                },
                {
                    "form": "strong",
                    "source": "Conjugation",
                    "tags": [
                        "table-tags"
                    ]
                },
                {
                    "form": "1 strong",
                    "source": "Conjugation",
                    "tags": [
                        "class"
                    ]
                },
                {
                    "form": "sein",
                    "source": "Conjugation",
                    "tags": [
                        "auxiliary"
                    ]
                },
                {
                    "form": "bin ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "multiword-construction",
                        "perfect",
                        "singular"
                    ]
                },
                {
                    "form": "sind ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "multiword-construction",
                        "perfect",
                        "plural"
                    ]
                },
                {
                    "form": "sei ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "multiword-construction",
                        "perfect",
                        "singular",
                        "subjunctive"
                    ]
                },
                {
                    "form": "seien ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "multiword-construction",
                        "perfect",
                        "plural",
                        "subjunctive"
                    ]
                },
                {
                    "form": "bist ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "perfect",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "seid ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "perfect",
                        "plural",
                        "second-person"
                    ]
                },
                {
                    "form": "seist ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "perfect",
                        "second-person",
                        "singular",
                        "subjunctive"
                    ]
                },
                {
                    "form": "seiest ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "perfect",
                        "second-person",
                        "singular",
                        "subjunctive"
                    ]
                },
                {
                    "form": "seiet ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "perfect",
                        "plural",
                        "second-person",
                        "subjunctive"
                    ]
                },
                {
                    "form": "ist ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "perfect",
                        "singular",
                        "third-person"
                    ]
                },
                {
                    "form": "sind ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "perfect",
                        "plural",
                        "third-person"
                    ]
                },
                {
                    "form": "sei ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "perfect",
                        "singular",
                        "subjunctive",
                        "third-person"
                    ]
                },
                {
                    "form": "seien ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "perfect",
                        "plural",
                        "subjunctive",
                        "third-person"
                    ]
                },
                {
                    "form": "war ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "multiword-construction",
                        "pluperfect",
                        "singular"
                    ]
                },
                {
                    "form": "waren ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "indicative",
                        "multiword-construction",
                        "pluperfect",
                        "plural"
                    ]
                },
                {
                    "form": "wäre ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "multiword-construction",
                        "pluperfect",
                        "singular",
                        "subjunctive"
                    ]
                },
                {
                    "form": "wären ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "multiword-construction",
                        "pluperfect",
                        "plural",
                        "subjunctive"
                    ]
                },
                {
                    "form": "warst ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "pluperfect",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "wart ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "pluperfect",
                        "plural",
                        "second-person"
                    ]
                },
                {
                    "form": "wärst ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "pluperfect",
                        "second-person",
                        "singular",
                        "subjunctive"
                    ]
                },
                {
                    "form": "wärest ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "pluperfect",
                        "second-person",
                        "singular",
                        "subjunctive"
                    ]
                },
                {
                    "form": "wärt ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "pluperfect",
                        "plural",
                        "second-person",
                        "subjunctive"
                    ]
                },
                {
                    "form": "wäret ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "pluperfect",
                        "plural",
                        "second-person",
                        "subjunctive"
                    ]
                },
                {
                    "form": "war ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "pluperfect",
                        "singular",
                        "third-person"
                    ]
                },
                {
                    "form": "waren ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "indicative",
                        "multiword-construction",
                        "pluperfect",
                        "plural",
                        "third-person"
                    ]
                },
                {
                    "form": "wäre ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "pluperfect",
                        "singular",
                        "subjunctive",
                        "third-person"
                    ]
                },
                {
                    "form": "wären ausgestiegen",
                    "source": "Conjugation",
                    "tags": [
                        "multiword-construction",
                        "pluperfect",
                        "plural",
                        "subjunctive",
                        "third-person"
                    ]
                },
                {
                    "form": "aussteigen werden",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "infinitive",
                        "multiword-construction"
                    ]
                },
                {
                    "form": "werde aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-i",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werden aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-i",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werdest aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werdet aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werde aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-i",
                        "third-person"
                    ]
                },
                {
                    "form": "werden aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-i",
                        "third-person"
                    ]
                },
                {
                    "form": "werde aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-i",
                        "indicative",
                        "multiword-construction",
                        "singular"
                    ]
                },
                {
                    "form": "werden aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-i",
                        "indicative",
                        "multiword-construction",
                        "plural"
                    ]
                },
                {
                    "form": "würde aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-i",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "würden aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-i",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "wirst aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "indicative",
                        "multiword-construction",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "werdet aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "indicative",
                        "multiword-construction",
                        "plural",
                        "second-person"
                    ]
                },
                {
                    "form": "würdest aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "würdet aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "wird aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "indicative",
                        "multiword-construction",
                        "singular",
                        "third-person"
                    ]
                },
                {
                    "form": "werden aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "indicative",
                        "multiword-construction",
                        "plural",
                        "third-person"
                    ]
                },
                {
                    "form": "würde aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii",
                        "third-person"
                    ]
                },
                {
                    "form": "würden aussteigen",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-i",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-ii",
                        "third-person"
                    ]
                },
                {
                    "form": "ausgestiegen sein werden",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "infinitive",
                        "multiword-construction"
                    ]
                },
                {
                    "form": "werde ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werden ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werdest ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werdet ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-i"
                    ]
                },
                {
                    "form": "werde ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-i",
                        "third-person"
                    ]
                },
                {
                    "form": "werden ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-i",
                        "third-person"
                    ]
                },
                {
                    "form": "werde ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-ii",
                        "indicative",
                        "multiword-construction",
                        "singular"
                    ]
                },
                {
                    "form": "werden ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-ii",
                        "indicative",
                        "multiword-construction",
                        "plural"
                    ]
                },
                {
                    "form": "würde ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "würden ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "first-person",
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "wirst ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "indicative",
                        "multiword-construction",
                        "second-person",
                        "singular"
                    ]
                },
                {
                    "form": "werdet ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "indicative",
                        "multiword-construction",
                        "plural",
                        "second-person"
                    ]
                },
                {
                    "form": "würdest ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "second-person",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "würdet ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "plural",
                        "second-person",
                        "subjunctive",
                        "subjunctive-ii"
                    ]
                },
                {
                    "form": "wird ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "indicative",
                        "multiword-construction",
                        "singular",
                        "third-person"
                    ]
                },
                {
                    "form": "werden ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "indicative",
                        "multiword-construction",
                        "plural",
                        "third-person"
                    ]
                },
                {
                    "form": "würde ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "singular",
                        "subjunctive",
                        "subjunctive-ii",
                        "third-person"
                    ]
                },
                {
                    "form": "würden ausgestiegen sein",
                    "source": "Conjugation",
                    "tags": [
                        "future",
                        "future-ii",
                        "multiword-construction",
                        "plural",
                        "subjunctive",
                        "subjunctive-ii",
                        "third-person"
                    ]
                }
            ],
        }
        self.assertEqual(expected, ret)

    def test_German_noun1(self):
        ret = self.xinfl("Bahnhof", "German", "noun", "Declension", """
<div class="NavFrame">
<div class="NavHead">Declension of <span class="Latn" lang="de">Bahnhof</span></div>
<div class="NavContent">

{| border="1px+solid+%23505050" style="border-collapse%3Acollapse%3B+background%3A%23FAFAFA%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table+inflection-table-de+inflection-table-de-m"

|-

! style="background%3A%23AAB8C0%3Bwidth%3A15%25" |


! colspan="3" style="background%3A%23AAB8C0%3Bwidth%3A46%25" | singular


! colspan="2" style="background%3A%23AAB8C0%3Bwidth%3A39%25" | plural


|-

! style="background%3A%23BBC9D0" |


! style="background%3A%23BBC9D0%3Bwidth%3A7%25" | [[indefinite article|indef.]]


! style="background%3A%23BBC9D0%3Bwidth%3A7%25" | [[definite article|def.]]


! style="background%3A%23BBC9D0%3Bwidth%3A32%25" | noun


! style="background%3A%23BBC9D0%3Bwidth%3A7%25" | [[definite article|def.]]


! style="background%3A%23BBC9D0%3Bwidth%3A32%25" | noun


|-

! style="background%3A%23BBC9D0" | nominative


| style="background%3A%23EEEEEE" | ein


| style="background%3A%23EEEEEE" | der


| <span class="Latn" lang="de">Bahnhof</span>


| style="background%3A%23EEEEEE" | die


| <span class="Latn" lang="de">[[Bahnhöfe#German|Bahnhöfe]]</span>


|-

! style="background%3A%23BBC9D0" | genitive


| style="background%3A%23EEEEEE" | eines


| style="background%3A%23EEEEEE" | des


| <span class="Latn" lang="de">[[Bahnhofes#German|Bahnhofes]]</span>,<br><span class="Latn" lang="de">[[Bahnhofs#German|Bahnhofs]]</span>


| style="background%3A%23EEEEEE" | der


| <span class="Latn" lang="de">Bahnhöfe</span>


|-

! style="background%3A%23BBC9D0" | dative


| style="background%3A%23EEEEEE" | einem


| style="background%3A%23EEEEEE" | dem


| <span class="Latn" lang="de">Bahnhof</span>,<br><span class="Latn" lang="de">[[Bahnhofe#German|Bahnhofe]]</span><sup>1</sup>


| style="background%3A%23EEEEEE" | den


| <span class="Latn" lang="de">[[Bahnhöfen#German|Bahnhöfen]]</span>


|-

! style="background%3A%23BBC9D0" | accusative


| style="background%3A%23EEEEEE" | einen


| style="background%3A%23EEEEEE" | den


| <span class="Latn" lang="de">Bahnhof</span>


| style="background%3A%23EEEEEE" | die


| <span class="Latn" lang="de">Bahnhöfe</span>


|}
<div style="text-align%3Aleft%3B+font-style%3A+italic%3B"><sup>1</sup>Now uncommon, [[Wiktionary:About German#Dative_singular_-e_in_noun_declension|see notes]]</div></div></div>
""")  # noqa: E501
        expected = {
            "forms": [
              {
                "form": "no-table-tags",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "Bahnhof",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "Bahnhöfe",
                "source": "Declension",
                "tags": [
                  "definite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "Bahnhofes",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "Bahnhofs",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "Bahnhöfe",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "Bahnhof",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "Bahnhofe",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "Bahnhöfen",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "plural"
                ]
              },
              {
                "form": "Bahnhof",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "singular"
                ]
              },
              {
                "form": "Bahnhöfe",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_German_adj1(self):
        ret = self.xinfl("eiskalt", "German", "adj", "Declension", """
<div class="NavFrame">
<div class="NavHead" style="text-align%3A+left">Declension of <i class="Latn+mention" lang="de">eiskalt</i></div>
<div class="NavContent">

{| border="1px+solid+%23cdcdcd" style="border-collapse%3Acollapse%3B+background%3A%23FEFEFE%3B+width%3A100%25" class="inflection-table"

|-

! colspan="2" rowspan="2" style="background%3A%23C0C0C0" | number & gender


! colspan="3" style="background%3A%23C0C0C0" | singular


! style="background%3A%23C0C0C0" | plural


|-

! style="background%3A%23C0C0C0" | masculine


! style="background%3A%23C0C0C0" | feminine


! style="background%3A%23C0C0C0" | neuter


! style="background%3A%23C0C0C0" | all genders


|-

! colspan="2" style="background%3A%23EEEEB0" | predicative


| <span class="Latn" lang="de">er ist [[eiskalt#German|eiskalt]]</span>


| <span class="Latn" lang="de">sie ist [[eiskalt#German|eiskalt]]</span>


| <span class="Latn" lang="de">es ist [[eiskalt#German|eiskalt]]</span>


| <span class="Latn" lang="de">sie sind [[eiskalt#German|eiskalt]]</span>


|-

! rowspan="4" style="background%3A%23c0cfe4" | strong declension <br> (without article)


! style="background%3A%23c0cfe4" | nominative


| <span class="Latn" lang="de">[[eiskalter#German|eiskalter]]</span>


| <span class="Latn" lang="de">[[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">[[eiskaltes#German|eiskaltes]]</span>


| <span class="Latn" lang="de">[[eiskalte#German|eiskalte]]</span>


|-

! style="background%3A%23c0cfe4" | genitive


| <span class="Latn" lang="de">[[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">[[eiskalter#German|eiskalter]]</span>


| <span class="Latn" lang="de">[[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">[[eiskalter#German|eiskalter]]</span>


|-

! style="background%3A%23c0cfe4" | dative


| <span class="Latn" lang="de">[[eiskaltem#German|eiskaltem]]</span>


| <span class="Latn" lang="de">[[eiskalter#German|eiskalter]]</span>


| <span class="Latn" lang="de">[[eiskaltem#German|eiskaltem]]</span>


| <span class="Latn" lang="de">[[eiskalten#German|eiskalten]]</span>


|-

! style="background%3A%23c0cfe4" | accusative


| <span class="Latn" lang="de">[[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">[[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">[[eiskaltes#German|eiskaltes]]</span>


| <span class="Latn" lang="de">[[eiskalte#German|eiskalte]]</span>


|-

! rowspan="4" style="background%3A%23c0e4c0" | weak declension <br> (with definite article)


! style="background%3A%23c0e4c0" | nominative


| <span class="Latn" lang="de">der [[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">die [[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">das [[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">die [[eiskalten#German|eiskalten]]</span>


|-

! style="background%3A%23c0e4c0" | genitive


| <span class="Latn" lang="de">des [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">der [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">des [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">der [[eiskalten#German|eiskalten]]</span>


|-

! style="background%3A%23c0e4c0" | dative


| <span class="Latn" lang="de">dem [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">der [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">dem [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">den [[eiskalten#German|eiskalten]]</span>


|-

! style="background%3A%23c0e4c0" | accusative


| <span class="Latn" lang="de">den [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">die [[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">das [[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">die [[eiskalten#German|eiskalten]]</span>


|-

! rowspan="4" style="background%3A%23e4d4c0" | mixed declension <br> (with indefinite article)


! style="background%3A%23e4d4c0" | nominative


| <span class="Latn" lang="de">ein [[eiskalter#German|eiskalter]]</span>


| <span class="Latn" lang="de">eine [[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">ein [[eiskaltes#German|eiskaltes]]</span>


| <span class="Latn" lang="de">(keine) [[eiskalten#German|eiskalten]]</span>


|-

! style="background%3A%23e4d4c0" | genitive


| <span class="Latn" lang="de">eines [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">einer [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">eines [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">(keiner) [[eiskalten#German|eiskalten]]</span>


|-

! style="background%3A%23e4d4c0" | dative


| <span class="Latn" lang="de">einem [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">einer [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">einem [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">(keinen) [[eiskalten#German|eiskalten]]</span>


|-

! style="background%3A%23e4d4c0" | accusative


| <span class="Latn" lang="de">einen [[eiskalten#German|eiskalten]]</span>


| <span class="Latn" lang="de">eine [[eiskalte#German|eiskalte]]</span>


| <span class="Latn" lang="de">ein [[eiskaltes#German|eiskaltes]]</span>


| <span class="Latn" lang="de">(keine) [[eiskalten#German|eiskalten]]</span>


|}
</div></div>
""")  # noqa: E501
        expected = {
            "forms": [
              {
                "form": "no-table-tags",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "eiskalt",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "predicative",
                  "singular"
                ]
              },
              {
                "form": "eiskalt",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "predicative",
                  "singular"
                ]
              },
              {
                "form": "eiskalt",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "predicative",
                  "singular"
                ]
              },
              {
                "form": "eiskalt",
                "source": "Declension",
                "tags": [
                  "plural",
                  "predicative"
                ]
              },
              {
                "form": "eiskalter",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "nominative",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalte",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskaltes",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "nominative",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalte",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalter",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "neuter",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalter",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskaltem",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalter",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskaltem",
                "source": "Declension",
                "tags": [
                  "dative",
                  "neuter",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "masculine",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalte",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskaltes",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "neuter",
                  "singular",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "eiskalte",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "strong",
                  "without-article"
                ]
              },
              {
                "form": "der eiskalte",
                "source": "Declension",
                "tags": [
                  "definite",
                  "includes-article",
                  "masculine",
                  "nominative",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "die eiskalte",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "includes-article",
                  "nominative",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "das eiskalte",
                "source": "Declension",
                "tags": [
                  "definite",
                  "includes-article",
                  "neuter",
                  "nominative",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "die eiskalten",
                "source": "Declension",
                "tags": [
                  "definite",
                  "includes-article",
                  "nominative",
                  "plural",
                  "weak"
                ]
              },
              {
                "form": "des eiskalten",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "includes-article",
                  "masculine",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "der eiskalten",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "genitive",
                  "includes-article",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "des eiskalten",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "includes-article",
                  "neuter",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "der eiskalten",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "includes-article",
                  "plural",
                  "weak"
                ]
              },
              {
                "form": "dem eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "includes-article",
                  "masculine",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "der eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "feminine",
                  "includes-article",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "dem eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "includes-article",
                  "neuter",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "den eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "includes-article",
                  "plural",
                  "weak"
                ]
              },
              {
                "form": "den eiskalten",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "includes-article",
                  "masculine",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "die eiskalte",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "feminine",
                  "includes-article",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "das eiskalte",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "includes-article",
                  "neuter",
                  "singular",
                  "weak"
                ]
              },
              {
                "form": "die eiskalten",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "includes-article",
                  "plural",
                  "weak"
                ]
              },
              {
                "form": "ein eiskalter",
                "source": "Declension",
                "tags": [
                  "includes-article",
                  "indefinite",
                  "masculine",
                  "mixed",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "eine eiskalte",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "ein eiskaltes",
                "source": "Declension",
                "tags": [
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "neuter",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "mixed",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "keine eiskalten",
                "source": "Declension",
                "tags": [
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "negative",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "eines eiskalten",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "includes-article",
                  "indefinite",
                  "masculine",
                  "mixed",
                  "singular"
                ]
              },
              {
                "form": "einer eiskalten",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "singular"
                ]
              },
              {
                "form": "eines eiskalten",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "mixed",
                  "plural"
                ]
              },
              {
                "form": "keiner eiskalten",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "negative",
                  "plural"
                ]
              },
              {
                "form": "einem eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "includes-article",
                  "indefinite",
                  "masculine",
                  "mixed",
                  "singular"
                ]
              },
              {
                "form": "einer eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "singular"
                ]
              },
              {
                "form": "einem eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "indefinite",
                  "mixed",
                  "plural"
                ]
              },
              {
                "form": "keinen eiskalten",
                "source": "Declension",
                "tags": [
                  "dative",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "negative",
                  "plural"
                ]
              },
              {
                "form": "einen eiskalten",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "includes-article",
                  "indefinite",
                  "masculine",
                  "mixed",
                  "singular"
                ]
              },
              {
                "form": "eine eiskalte",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "singular"
                ]
              },
              {
                "form": "ein eiskaltes",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "eiskalten",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "indefinite",
                  "mixed",
                  "plural"
                ]
              },
              {
                "form": "keine eiskalten",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "includes-article",
                  "indefinite",
                  "mixed",
                  "negative",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_German_noun2(self):
        # Language name inflection tables are slightly different
        ret = self.xinfl("Tatarisch", "German", "noun", "Declension", """
<div class="NavFrame" style="width%3A100%25">
<div class="NavHead">Declension of <span class="Latn" lang="de">[[Tatarisch#German|Tatarisch]]</span> (''language name'')</div>
<div class="NavContent">

{| border="1px+solid+%23505050" style="border-collapse%3Acollapse%3B+background%3A%23FAFAFA%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! style="background%3A%23AAB8C0%3Bwidth%3A15%25" |


! colspan="5" style="background%3A%23AAB8C0%3Bwidth%3A85%25" | singular &nbsp; ''([[Wiktionary:About German#Declension of language names|explanation of the use and meaning of the forms]])''


|-

! style="background%3A%23BBC9D0" |


! style="background%3A%23BBC9D0%3Bwidth%3A14%25" | (usually without article)


! style="background%3A%23BBC9D0%3Bwidth%3A32%25" | noun


! style="background%3A%23BBC9D0%3Bwidth%3A7%25" | [[definite article|def.]]


! style="background%3A%23BBC9D0%3Bwidth%3A32%25" | noun


|-

! style="background%3A%23BBC9D0" | nominative


| style="background%3A%23EEEEEE" | (<span class="Latn" lang="de">das</span>)


| <span class="Latn" lang="de">[[Tatarisch#German|Tatarisch]]</span>


| style="background%3A%23EEEEEE" | <span class="Latn" lang="de">das</span>


| <span class="Latn+form-of+lang-de+alternative-form-of+++++++" lang="de">[[Tatarische#German|Tatarische]]</span>


|-

! style="background%3A%23BBC9D0" | genitive


| style="background%3A%23EEEEEE" | (<span class="Latn" lang="de">des</span>)


| <span class="Latn" lang="de">[[Tatarisch#German|Tatarisch]]</span>, <span class="Latn+form-of+lang-de+gen%7Cs-form-of+++++++" lang="de">[[Tatarischs#German|Tatarischs]]</span>


| style="background%3A%23EEEEEE" | <span class="Latn" lang="de">des</span>


| <span class="Latn+form-of+lang-de+gen%7Cs-form-of+++++++" lang="de">[[Tatarischen#German|Tatarischen]]</span>


|-

! style="background%3A%23BBC9D0" | dative


| style="background%3A%23EEEEEE" | (<span class="Latn" lang="de">dem</span>)


| <span class="Latn" lang="de">[[Tatarisch#German|Tatarisch]]</span>


| style="background%3A%23EEEEEE" | <span class="Latn" lang="de">dem</span>


| <span class="Latn+form-of+lang-de+dat%7Cs-form-of+++++++" lang="de">[[Tatarischen#German|Tatarischen]]</span>


|-

! style="background%3A%23BBC9D0" | accusative


| style="background%3A%23EEEEEE" | (<span class="Latn" lang="de">das</span>)


| <span class="Latn" lang="de">[[Tatarisch#German|Tatarisch]]</span>


| style="background%3A%23EEEEEE" | <span class="Latn" lang="de">das</span>


| <span class="Latn+form-of+lang-de+acc%7Cs-form-of+++++++" lang="de">[[Tatarische#German|Tatarische]]</span>


|}
</div></div>
""")  # noqa: E501
        expected = {
          "forms": [
              {
                "form": "no-table-tags",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
            {
              "form": "Tatarisch",
              "source": "Declension",
              "tags": [
                "nominative",
                "singular",
                "usually-without-article"
              ]
            },
            {
              "form": "Tatarische",
              "source": "Declension",
              "tags": [
                "definite",
                "nominative",
                "singular"
              ]
            },
            {
              "form": "Tatarisch",
              "source": "Declension",
              "tags": [
                "genitive",
                "singular",
                "usually-without-article"
              ]
            },
            {
              "form": "Tatarischs",
              "source": "Declension",
              "tags": [
                "genitive",
                "singular",
                "usually-without-article"
              ]
            },
            {
              "form": "Tatarischen",
              "source": "Declension",
              "tags": [
                "definite",
                "genitive",
                "singular"
              ]
            },
            {
              "form": "Tatarisch",
              "source": "Declension",
              "tags": [
                "dative",
                "singular",
                "usually-without-article"
              ]
            },
            {
              "form": "Tatarischen",
              "source": "Declension",
              "tags": [
                "dative",
                "definite",
                "singular"
              ]
            },
            {
              "form": "Tatarisch",
              "source": "Declension",
              "tags": [
                "accusative",
                "singular",
                "usually-without-article"
              ]
            },
            {
              "form": "Tatarische",
              "source": "Declension",
              "tags": [
                "accusative",
                "definite",
                "singular"
              ]
            }
          ],
        }
        self.assertEqual(expected, ret)

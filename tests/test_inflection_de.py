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
""")
        expect = {
            "forms": [
                {
                    "form": "1 strong",
                    "source": "Conjugation title",
                    "tags": [
                        "class"
                    ]
                },
                {
                    "form": "sein",
                    "source": "Conjugation title",
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
                    "source": "Conjugation title",
                    "tags": [
                        "word-tags"
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
        self.assertEqual(ret, expect)

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
""")
        expected = {
            "forms": [
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
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(ret, expected)
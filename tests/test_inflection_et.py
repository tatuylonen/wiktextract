# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wiktextract.inflection import parse_inflection_section

class InflTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 100000
        self.wxr = WiktextractContext(WiktionaryConfig(), Wtp())
        
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

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

    def test_Estonian_noun1(self):
        ret = self.xinfl("kodu", "Estonian", "noun", "Declension", """
<div class="NavFrame" style>
<div class="NavHead" style>Declension of kodu</div>
<div class="NavContent">


{| border="1" color="%23cdcdcd" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3Btext-align%3Aleft%3B+cell-padding%3A1em%3B+width%3A100%25" class="inflection-table"

|-

! style="width%3A30%25%3Bbackground%3A%23c0cfe4" |


! style="width%3A35%25%3Btext-align%3Acenter%3Bbackground%3A%23c0cfe4" | singular <small>([[ainsus]])</small>


! style="width%3A35%25%3Btext-align%3Acenter%3Bbackground%3A%23c0cfe4" | plural <small>([[mitmus]])</small>


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | nominative <small>([[nimetav]])</small>


| [[kodu]]


| [[kodud]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | genitive <small>([[omastav]])</small>


| [[kodu]]


| [[kodude]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | partitive <small>([[osastav]])</small>


| [[kodu]]


| [[kodusid]]


|-

| colspan="3" style="background%3A%23c0cfe4" |


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | illative <small>([[sisseütlev]])</small>


| [[kodusse]], <br>[[koju]], <br>[[kottu]]


| [[kodudesse]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | inessive <small>([[seesütlev]])</small>


| [[kodus]]


| [[kodudes]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | elative <small>([[seestütlev]])</small>


| [[kodust]]


| [[kodudest]]


|-

| colspan="3" style="background%3A%23c0cfe4" |


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | allative <small>([[alaleütlev]])</small>


| [[kodule]]


| [[kodudele]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | adessive <small>([[alalütlev]])</small>


| [[kodul]]


| [[kodudel]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | ablative <small>([[alaltütlev]])</small>


| [[kodult]]


| [[kodudelt]]


|-

| colspan="3" style="background%3A%23c0cfe4" |


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | translative <small>([[saav]])</small>


| [[koduks]]


| [[kodudeks]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | terminative <small>([[rajav]])</small>


| [[koduni]]


| [[kodudeni]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | essive <small>([[olev]])</small>


| [[koduna]]


| [[kodudena]]


|-

| colspan="3" style="background%3A%23c0cfe4" |


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | abessive <small>([[ilmaütlev]])</small>


| [[koduta]]


| [[kodudeta]]


|-

! style="text-align%3Acenter%3Bbackground%3A%23EFEFEF" | comitative <small>([[kaasaütlev]])</small>


| [[koduga]]


| [[kodudega]]


|}
</div></div>
""")
        expected = {
            "forms": [
              {
                "form": "",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "kodu",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "kodud",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "kodu",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "kodude",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "kodu",
                "source": "Declension",
                "tags": [
                  "partitive",
                  "singular"
                ]
              },
              {
                "form": "kodusid",
                "source": "Declension",
                "tags": [
                  "partitive",
                  "plural"
                ]
              },
              {
                "form": "kodusse",
                "source": "Declension",
                "tags": [
                  "illative",
                  "singular"
                ]
              },
              {
                "form": "koju",
                "source": "Declension",
                "tags": [
                  "illative",
                  "singular"
                ]
              },
              {
                "form": "kottu",
                "source": "Declension",
                "tags": [
                  "illative",
                  "singular"
                ]
              },
              {
                "form": "kodudesse",
                "source": "Declension",
                "tags": [
                  "illative",
                  "plural"
                ]
              },
              {
                "form": "kodus",
                "source": "Declension",
                "tags": [
                  "inessive",
                  "singular"
                ]
              },
              {
                "form": "kodudes",
                "source": "Declension",
                "tags": [
                  "inessive",
                  "plural"
                ]
              },
              {
                "form": "kodust",
                "source": "Declension",
                "tags": [
                  "elative",
                  "singular"
                ]
              },
              {
                "form": "kodudest",
                "source": "Declension",
                "tags": [
                  "elative",
                  "plural"
                ]
              },
              {
                "form": "kodule",
                "source": "Declension",
                "tags": [
                  "allative",
                  "singular"
                ]
              },
              {
                "form": "kodudele",
                "source": "Declension",
                "tags": [
                  "allative",
                  "plural"
                ]
              },
              {
                "form": "kodul",
                "source": "Declension",
                "tags": [
                  "adessive",
                  "singular"
                ]
              },
              {
                "form": "kodudel",
                "source": "Declension",
                "tags": [
                  "adessive",
                  "plural"
                ]
              },
              {
                "form": "kodult",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "singular"
                ]
              },
              {
                "form": "kodudelt",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural"
                ]
              },
              {
                "form": "koduks",
                "source": "Declension",
                "tags": [
                  "singular",
                  "translative"
                ]
              },
              {
                "form": "kodudeks",
                "source": "Declension",
                "tags": [
                  "plural",
                  "translative"
                ]
              },
              {
                "form": "koduni",
                "source": "Declension",
                "tags": [
                  "singular",
                  "terminative"
                ]
              },
              {
                "form": "kodudeni",
                "source": "Declension",
                "tags": [
                  "plural",
                  "terminative"
                ]
              },
              {
                "form": "koduna",
                "source": "Declension",
                "tags": [
                  "essive",
                  "singular"
                ]
              },
              {
                "form": "kodudena",
                "source": "Declension",
                "tags": [
                  "essive",
                  "plural"
                ]
              },
              {
                "form": "koduta",
                "source": "Declension",
                "tags": [
                  "abessive",
                  "singular"
                ]
              },
              {
                "form": "kodudeta",
                "source": "Declension",
                "tags": [
                  "abessive",
                  "plural"
                ]
              },
              {
                "form": "koduga",
                "source": "Declension",
                "tags": [
                  "comitative",
                  "singular"
                ]
              },
              {
                "form": "kodudega",
                "source": "Declension",
                "tags": [
                  "comitative",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Estonian_verb1(self):
        ret = self.xinfl("tulema", "Estonian", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead" style="background%3Argb%2880%25%2C80%25%2C100%25%29">Inflection of <i class="Latn+mention" lang="et">tulema</i> (ÕS type [[Appendix:Estonian conjugation|36/tulema]], no gradation)</div>
<div class="NavContent">

{| class="inflection-table" style="width%3A100%25%3B+border%3A+solid+1px+rgb%2880%25%2C80%25%2C100%25%29%3B+margin-bottom%3A+0.5em%3B+text-align%3A+left%3B" cellspacing="1" cellpadding="2"

|-

! colspan="6" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | indicative


|-

! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | present


! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | perfect


|- style="background%3Argb%2890%25%2C90%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29%3B+width%3A+7%25" | person


! style="width%3A+18%25" | positive


! style="width%3A+21%25" | negative


! style="background%3Argb%2880%25%2C80%25%2C100%25%29%3B+width%3A+7%25" | person


! style="width%3A+21%25" | positive


! style="width%3A+24%25" | negative


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| <span class="Latn" lang="et">[[tulen#Estonian|tulen]]</span>


| rowspan="6" | <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tule#Estonian|tule]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| <span class="Latn" lang="et">[[olen#Estonian|olen]] [[tulnud#Estonian|tulnud]]</span>


| rowspan="6" | <span class="Latn" lang="et">[[ei#Estonian|ei]] [[ole#Estonian|ole]] [[tulnud#Estonian|tulnud]]</span><br><span class="Latn" lang="et">[[pole#Estonian|pole]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| <span class="Latn" lang="et">[[tuled#Estonian|tuled]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| <span class="Latn" lang="et">[[oled#Estonian|oled]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[tuleb#Estonian|tuleb]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[on#Estonian|on]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| <span class="Latn" lang="et">[[tuleme#Estonian|tuleme]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| <span class="Latn" lang="et">[[oleme#Estonian|oleme]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| <span class="Latn" lang="et">[[tulete#Estonian|tulete]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| <span class="Latn" lang="et">[[olete#Estonian|olete]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[tulevad#Estonian|tulevad]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[on#Estonian|on]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[tullakse#Estonian|tullakse]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tulda#Estonian|tulda]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[on#Estonian|on]] [[tuldud#Estonian|tuldud]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[ole#Estonian|ole]] [[tuldud#Estonian|tuldud]]</span><br><span class="Latn" lang="et">[[pole#Estonian|pole]] [[tuldud#Estonian|tuldud]]</span>


|-

! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | past


! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | pluperfect


|- style="background%3Argb%2890%25%2C90%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| <span class="Latn" lang="et">[[tulin#Estonian|tulin]]</span>


| rowspan="6" | <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tulnud#Estonian|tulnud]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| <span class="Latn" lang="et">[[olin#Estonian|olin]] [[tulnud#Estonian|tulnud]]</span>


| rowspan="6" | <span class="Latn" lang="et">[[ei#Estonian|ei]] [[olnud#Estonian|olnud]] [[tulnud#Estonian|tulnud]]</span><br><span class="Latn" lang="et">[[polnud#Estonian|polnud]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| <span class="Latn" lang="et">[[tulid#Estonian|tulid]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| <span class="Latn" lang="et">[[olid#Estonian|olid]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[tuli#Estonian|tuli]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[oli#Estonian|oli]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| <span class="Latn" lang="et">[[tulime#Estonian|tulime]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| <span class="Latn" lang="et">[[olime#Estonian|olime]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| <span class="Latn" lang="et">[[tulite#Estonian|tulite]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| <span class="Latn" lang="et">[[olite#Estonian|olite]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[tulid#Estonian|tulid]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[oli#Estonian|oli]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[tuldi#Estonian|tuldi]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tuldud#Estonian|tuldud]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[oli#Estonian|oli]] [[tuldud#Estonian|tuldud]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[olnud#Estonian|olnud]] [[tuldud#Estonian|tuldud]]</span><br><span class="Latn" lang="et">[[polnud#Estonian|polnud]] [[tuldud#Estonian|tuldud]]</span>


|-

! colspan="6" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | conditional


|-

! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | present


! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | perfect


|- style="background%3Argb%2890%25%2C90%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| <span class="Latn" lang="et">[[tuleksin#Estonian|tuleksin]]</span>


| rowspan="6" | <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tuleks#Estonian|tuleks]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| <span class="Latn" lang="et">[[oleksin#Estonian|oleksin]] [[tulnud#Estonian|tulnud]]</span>


| rowspan="6" | <span class="Latn" lang="et">[[ei#Estonian|ei]] [[oleks#Estonian|oleks]] [[tulnud#Estonian|tulnud]]</span><br><span class="Latn" lang="et">[[poleks#Estonian|poleks]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| <span class="Latn" lang="et">[[tuleksid#Estonian|tuleksid]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| <span class="Latn" lang="et">[[oleksid#Estonian|oleksid]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[tuleks#Estonian|tuleks]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[oleks#Estonian|oleks]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| <span class="Latn" lang="et">[[tuleksime#Estonian|tuleksime]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| <span class="Latn" lang="et">[[oleksime#Estonian|oleksime]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| <span class="Latn" lang="et">[[tuleksite#Estonian|tuleksite]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| <span class="Latn" lang="et">[[oleksite#Estonian|oleksite]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[tuleksid#Estonian|tuleksid]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[oleksid#Estonian|oleksid]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[tuldaks#Estonian|tuldaks]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tuldaks#Estonian|tuldaks]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[oleks#Estonian|oleks]] [[tuldud#Estonian|tuldud]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[oleks#Estonian|oleks]] [[tuldud#Estonian|tuldud]]</span><br><span class="Latn" lang="et">[[poleks#Estonian|poleks]] [[tuldud#Estonian|tuldud]]</span>


|-

! colspan="6" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | imperative


|-

! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | present


! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | perfect


|- style="background%3Argb%2890%25%2C90%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| &mdash;


| &mdash;


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;sing.


| &mdash;


| &mdash;


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| <span class="Latn" lang="et">[[tule#Estonian|tule]]</span>


| <span class="Latn" lang="et">[[ära#Estonian|ära]] [[tule#Estonian|tule]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;sing.


| &mdash;


| &mdash;


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[tulgu#Estonian|tulgu]]</span>


| <span class="Latn" lang="et">[[ärgu#Estonian|ärgu]] [[tulgu#Estonian|tulgu]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;sing.


| <span class="Latn" lang="et">[[olgu#Estonian|olgu]] [[tulnud#Estonian|tulnud]]</span>


| <span class="Latn" lang="et">[[ärgu#Estonian|ärgu]] [[olgu#Estonian|olgu]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| <span class="Latn" lang="et">[[tulgem#Estonian|tulgem]]</span>


| <span class="Latn" lang="et">[[ärgem#Estonian|ärgem]] [[tulgem#Estonian|tulgem]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 1st&nbsp;plur.


| &mdash;


| &mdash;


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| <span class="Latn" lang="et">[[tulge#Estonian|tulge]]</span>


| <span class="Latn" lang="et">[[ärge#Estonian|ärge]] [[tulge#Estonian|tulge]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 2nd&nbsp;plur.


| &mdash;


| &mdash;


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[tulgu#Estonian|tulgu]]</span>


| <span class="Latn" lang="et">[[ärgu#Estonian|ärgu]] [[tulgu#Estonian|tulgu]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | 3rd&nbsp;plur.


| <span class="Latn" lang="et">[[olgu#Estonian|olgu]] [[tulnud#Estonian|tulnud]]</span>


| <span class="Latn" lang="et">[[ärgu#Estonian|ärgu]] [[olgu#Estonian|olgu]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[tuldagu#Estonian|tuldagu]]</span>


| <span class="Latn" lang="et">[[ärgu#Estonian|ärgu]] [[tuldagu#Estonian|tuldagu]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[olgu#Estonian|olgu]] [[tuldud#Estonian|tuldud]]</span>


| <span class="Latn" lang="et">[[ärgu#Estonian|ärgu]] [[olgu#Estonian|olgu]] [[tuldud#Estonian|tuldud]]</span>


|-

! colspan="6" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | quotative


|-

! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | present


! colspan="3" style="background%3Argb%2880%25%2C80%25%2C100%25%29" | perfect


|- style="background%3Argb%2890%25%2C90%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | person


! positive


! negative


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | active


| <span class="Latn" lang="et">[[tulevat#Estonian|tulevat]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tulevat#Estonian|tulevat]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | active


| <span class="Latn" lang="et">[[olevat#Estonian|olevat]] [[tulnud#Estonian|tulnud]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[olevat#Estonian|olevat]] [[tulnud#Estonian|tulnud]]</span><br><span class="Latn" lang="et">[[polevat#Estonian|polevat]] [[tulnud#Estonian|tulnud]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[tuldavat#Estonian|tuldavat]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[tuldavat#Estonian|tuldavat]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | passive


| <span class="Latn" lang="et">[[olevat#Estonian|olevat]] [[tuldud#Estonian|tuldud]]</span>


| <span class="Latn" lang="et">[[ei#Estonian|ei]] [[olevat#Estonian|olevat]] [[tuldud#Estonian|tuldud]]</span><br><span class="Latn" lang="et">[[polevat#Estonian|polevat]] [[tuldud#Estonian|tuldud]]</span>


|-

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" colspan="10" | Nominal forms


|-

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | ma-infinitive


! style="background%3Argb%2890%25%2C90%25%2C100%25%29" | active


! style="background%3Argb%2890%25%2C90%25%2C100%25%29" | passive


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | da-infinitive


! style="background%3Argb%2890%25%2C90%25%2C100%25%29" | active


! style="background%3Argb%2890%25%2C90%25%2C100%25%29" | passive


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | nominative


| <span class="Latn" lang="et">[[tulema#Estonian|tulema]]</span>


| <span class="Latn" lang="et">[[tuldama#Estonian|tuldama]]</span>


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | da-form


| <span class="Latn" lang="et">[[tulla#Estonian|tulla]]</span>


| &mdash;


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | inessive


| <span class="Latn" lang="et">[[tulemas#Estonian|tulemas]]</span>


| &mdash;


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | des-form


| <span class="Latn" lang="et">[[tulles#Estonian|tulles]]</span>


| &mdash;


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | elative


| <span class="Latn" lang="et">[[tulemast#Estonian|tulemast]]</span>


| &mdash;


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | participle


! style="background%3Argb%2890%25%2C90%25%2C100%25%29" | active


! style="background%3Argb%2890%25%2C90%25%2C100%25%29" | passive


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | translative


| <span class="Latn" lang="et">[[tulemaks#Estonian|tulemaks]]</span>


| &mdash;


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | present


| <span class="Latn" lang="et">[[tulev#Estonian|tulev]]</span>


| <span class="Latn" lang="et">[[tuldav#Estonian|tuldav]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | abessive


| <span class="Latn" lang="et">[[tulemata#Estonian|tulemata]]</span>


| &mdash;


! style="background%3Argb%2880%25%2C80%25%2C100%25%29" | past


| <span class="Latn" lang="et">[[tulnud#Estonian|tulnud]]</span>


| <span class="Latn" lang="et">[[tuldud#Estonian|tuldud]]</span>


|}
</div></div>[[Category:Estonian tulema-type verbs|TULEMA]]
""")
        expected = {
            "forms": [
              {
                "form": "",
                "source": "Conjugation",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "no gradation",
                "source": "Conjugation",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "36/tulema",
                "source": "Conjugation",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "tulen",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "ei tule",
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
                "form": "olen tulnud",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "perfect",
                  "singular"
                ]
              },
              {
                "form": "ei ole tulnud",
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
                "form": "pole tulnud",
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
                "form": "tuled",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ei tule",
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
                "form": "oled tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ei ole tulnud",
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
                "form": "pole tulnud",
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
                "form": "tuleb",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei tule",
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
                "form": "on tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei ole tulnud",
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
                "form": "pole tulnud",
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
                "form": "tuleme",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "ei tule",
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
                "form": "oleme tulnud",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "perfect",
                  "plural"
                ]
              },
              {
                "form": "ei ole tulnud",
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
                "form": "pole tulnud",
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
                "form": "tulete",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "ei tule",
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
                "form": "olete tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "ei ole tulnud",
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
                "form": "pole tulnud",
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
                "form": "tulevad",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "ei tule",
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
                "form": "on tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "ei ole tulnud",
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
                "form": "pole tulnud",
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
                "form": "tullakse",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "ei tulda",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "on tuldud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "ei ole tuldud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "pole tuldud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "tulin",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "ei tulnud",
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
                "form": "olin tulnud",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "singular"
                ]
              },
              {
                "form": "ei olnud tulnud",
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
                "form": "polnud tulnud",
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
                "form": "tulid",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ei tulnud",
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
                "form": "olid tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ei olnud tulnud",
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
                "form": "polnud tulnud",
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
                "form": "tuli",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei tulnud",
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
                "form": "oli tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei olnud tulnud",
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
                "form": "polnud tulnud",
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
                "form": "tulime",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "ei tulnud",
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
                "form": "olime tulnud",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "plural"
                ]
              },
              {
                "form": "ei olnud tulnud",
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
                "form": "polnud tulnud",
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
                "form": "tulite",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "ei tulnud",
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
                "form": "olite tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "ei olnud tulnud",
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
                "form": "polnud tulnud",
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
                "form": "tulid",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "ei tulnud",
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
                "form": "oli tulnud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "ei olnud tulnud",
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
                "form": "polnud tulnud",
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
                "form": "tuldi",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "past"
                ]
              },
              {
                "form": "ei tuldud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "past"
                ]
              },
              {
                "form": "oli tuldud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "pluperfect"
                ]
              },
              {
                "form": "ei olnud tuldud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "pluperfect"
                ]
              },
              {
                "form": "polnud tuldud",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "negative",
                  "passive",
                  "pluperfect"
                ]
              },
              {
                "form": "tuleksin",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "ei tuleks",
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
                "form": "oleksin tulnud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "singular"
                ]
              },
              {
                "form": "ei oleks tulnud",
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
                "form": "poleks tulnud",
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
                "form": "tuleksid",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ei tuleks",
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
                "form": "oleksid tulnud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ei oleks tulnud",
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
                "form": "poleks tulnud",
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
                "form": "tuleks",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei tuleks",
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
                "form": "oleks tulnud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ei oleks tulnud",
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
                "form": "poleks tulnud",
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
                "form": "tuleksime",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "ei tuleks",
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
                "form": "oleksime tulnud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "plural"
                ]
              },
              {
                "form": "ei oleks tulnud",
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
                "form": "poleks tulnud",
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
                "form": "tuleksite",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "ei tuleks",
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
                "form": "oleksite tulnud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "ei oleks tulnud",
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
                "form": "poleks tulnud",
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
                "form": "tuleksid",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "ei tuleks",
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
                "form": "oleksid tulnud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "ei oleks tulnud",
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
                "form": "poleks tulnud",
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
                "form": "tuldaks",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "ei tuldaks",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "oleks tuldud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "ei oleks tuldud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "poleks tuldud",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                  'form': '-',
                  'source': 'Conjugation',
                  'tags': ['first-person', 'imperative', 'present', 'singular']
              },
              {
                  'form': '-',
                  'source': 'Conjugation',
                  'tags': ['first-person',
                           'imperative',
                           'negative',
                           'present',
                           'singular']
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person', 'imperative', 'perfect', 'singular']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person',
                        'imperative',
                        'negative',
                        'perfect',
                        'singular']},
              {
                "form": "tule",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ära tule",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['imperative', 'perfect', 'second-person', 'singular']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['imperative',
                        'negative',
                        'perfect',
                        'second-person',
                        'singular']},
              {
                "form": "tulgu",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ärgu tulgu",
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
                "form": "olgu tulnud",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "perfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "ärgu olgu tulnud",
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
                "form": "tulgem",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "ärgem tulgem",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "negative",
                  "plural",
                  "present"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person', 'imperative', 'perfect', 'plural']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person',
                        'imperative',
                        'negative',
                        'perfect',
                        'plural']},
              {
                "form": "tulge",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "ärge tulge",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['imperative', 'perfect', 'plural', 'second-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['imperative',
                        'negative',
                        'perfect',
                        'plural',
                        'second-person']},
              {
                "form": "tulgu",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "ärgu tulgu",
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
                "form": "olgu tulnud",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "perfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "ärgu olgu tulnud",
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
                "form": "tuldagu",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "ärgu tuldagu",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "olgu tuldud",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "ärgu olgu tuldud",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "passive",
                  "perfect"
                ]
              },
              {
                "form": "tulevat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "present",
                  "quotative"
                ]
              },
              {
                "form": "ei tulevat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "negative",
                  "present",
                  "quotative"
                ]
              },
              {
                "form": "olevat tulnud",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "perfect",
                  "quotative"
                ]
              },
              {
                "form": "ei olevat tulnud",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "negative",
                  "perfect",
                  "quotative"
                ]
              },
              {
                "form": "polevat tulnud",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "negative",
                  "perfect",
                  "quotative"
                ]
              },
              {
                "form": "tuldavat",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "present",
                  "quotative"
                ]
              },
              {
                "form": "ei tuldavat",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "passive",
                  "present",
                  "quotative"
                ]
              },
              {
                "form": "olevat tuldud",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "perfect",
                  "quotative"
                ]
              },
              {
                "form": "ei olevat tuldud",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "passive",
                  "perfect",
                  "quotative"
                ]
              },
              {
                "form": "polevat tuldud",
                "source": "Conjugation",
                "tags": [
                  "negative",
                  "passive",
                  "perfect",
                  "quotative"
                ]
              },
              {
                "form": "tulema",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "infinitive-ma",
                  "nominative"
                ]
              },
              {
                "form": "tuldama",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-ma",
                  "nominative",
                  "passive"
                ]
              },
              {
                "form": "tulla",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "infinitive-da",
                  "verb-form-da"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-da",
                  "passive",
                  "verb-form-da"
                ]
              },
              {
                "form": "tulemas",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "inessive",
                  "infinitive",
                  "infinitive-ma"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "inessive",
                  "infinitive",
                  "infinitive-ma",
                  "passive"
                ]
              },
              {
                "form": "tulles",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "infinitive-da",
                  "verb-form-des"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-da",
                  "passive",
                  "verb-form-des"
                ]
              },
              {
                "form": "tulemast",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "elative",
                  "infinitive",
                  "infinitive-ma"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "elative",
                  "infinitive",
                  "infinitive-ma",
                  "passive"
                ]
              },
              {
                "form": "tulemaks",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive",
                  "infinitive-ma",
                  "translative"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "infinitive-ma",
                  "passive",
                  "translative"
                ]
              },
              {
                "form": "tulev",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "tuldav",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "tulemata",
                "source": "Conjugation",
                "tags": [
                  "abessive",
                  "active",
                  "infinitive",
                  "infinitive-ma"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "abessive",
                  "infinitive",
                  "infinitive-ma",
                  "passive"
                ]
              },
              {
                "form": "tulnud",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "tuldud",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive",
                  "past"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

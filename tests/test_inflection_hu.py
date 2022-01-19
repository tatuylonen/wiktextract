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

class InflTests(unittest.TestCase):

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

    def test_Hungarian_verb1(self):
        ret = self.xinfl("fut", "Hungarian", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead" style="background%3A%23e2f6e2%3B">conjugation of ''fut''</div>
<div class="NavContent">


{| style="width%3A100%25" class="inflection-table" cellpadding="2" cellspacing="1"

|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background-color%3A%23c0e4c0" colspan="3" |


! style="background-color%3A%23c0e4c0" | 1st&nbsp;person&nbsp;<abbr title="singular">sg</abbr>


! style="background-color%3A%23c0e4c0" | 2nd&nbsp;person&nbsp;<abbr title="singular">sg</abbr><br>''informal''


! style="background-color%3A%23c0e4c0" | 3rd&nbsp;person&nbsp;<abbr title="singular">sg</abbr>,<br>2nd&nbsp;p.&nbsp;<abbr title="singular">sg</abbr>&nbsp;''formal''


! style="background-color%3A%23c0e4c0" | 1st&nbsp;person&nbsp;<abbr title="plural">pl</abbr>


! style="background-color%3A%23c0e4c0" | 2nd&nbsp;person&nbsp;<abbr title="plural">pl</abbr><br>''informal''


! style="background-color%3A%23c0e4c0" | 3rd&nbsp;person&nbsp;<abbr title="plural">pl</abbr>,<br>2nd&nbsp;p.&nbsp;<abbr title="plural">pl</abbr>&nbsp;''formal''



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! rowspan="6" style="background-color%3A%23c0e4c0" width="30px" | Indica&shy;tive<br>mood


! rowspan="3" style="background-color%3A%23c0e4c0" width="30px" | Pre&shy;sent


! style="background-color%3A%23c0e4c0" | <abbr title="Indefinite">Indef.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Cind%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futok#Hungarian|futok]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Cind%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futsz#Hungarian|futsz]]</span>


| <span class="Latn" lang="hu">[[fut#Hungarian|fut]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Cind%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futunk#Hungarian|futunk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Cind%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futtok#Hungarian|futtok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Cind%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futnak#Hungarian|futnak]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background-color%3A%23c0e4c0" | <abbr title="Definite">Def.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Cind%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futom#Hungarian|futom]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Cind%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futod#Hungarian|futod]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Cind%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futja#Hungarian|futja]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Cind%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futjuk#Hungarian|futjuk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Cind%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futjátok#Hungarian|futjátok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Cind%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futják#Hungarian|futják]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29%3B"

! style="background-color%3A%23c0e4c0%3B+line-height%3A+0.95%3B+white-space%3Anowrap%3B" | <small><abbr title="second-person+object">2nd-p. o.</abbr></small>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Cind%7Cpres%7C2o-form-of+++++++" lang="hu">[[futlak#Hungarian|futlak]]</span>


| colspan="5" style="background-color%3Argb%2895%25%2C95%25%2C100%25%29" | <small>―</small>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! rowspan="3" style="background-color%3A%23c0e4c0" | Past


! style="background-color%3A%23c0e4c0" | <abbr title="Indefinite">Indef.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Cind%7Cpast%7Cindef-form-of+++++++" lang="hu">[[futottam#Hungarian|futottam]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Cind%7Cpast%7Cindef-form-of+++++++" lang="hu">[[futottál#Hungarian|futottál]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Cind%7Cpast%7Cindef-form-of+++++++" lang="hu">[[futott#Hungarian|futott]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Cind%7Cpast%7Cindef-form-of+++++++" lang="hu">[[futottunk#Hungarian|futottunk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Cind%7Cpast%7Cindef-form-of+++++++" lang="hu">[[futottatok#Hungarian|futottatok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Cind%7Cpast%7Cindef-form-of+++++++" lang="hu">[[futottak#Hungarian|futottak]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background-color%3A%23c0e4c0" | <abbr title="Definite">Def.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Cind%7Cpast%7Cdef-form-of+++++++" lang="hu">[[futottam#Hungarian|futottam]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Cind%7Cpast%7Cdef-form-of+++++++" lang="hu">[[futottad#Hungarian|futottad]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Cind%7Cpast%7Cdef-form-of+++++++" lang="hu">[[futotta#Hungarian|futotta]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Cind%7Cpast%7Cdef-form-of+++++++" lang="hu">[[futottuk#Hungarian|futottuk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Cind%7Cpast%7Cdef-form-of+++++++" lang="hu">[[futottátok#Hungarian|futottátok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Cind%7Cpast%7Cdef-form-of+++++++" lang="hu">[[futották#Hungarian|futották]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29%3B"

! style="background-color%3A%23c0e4c0%3B+line-height%3A+0.95%3B+white-space%3Anowrap%3B" | <small><abbr title="second-person+object">2nd-p. o.</abbr></small>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Cind%7Cpast%7C2o-form-of+++++++" lang="hu">[[futottalak#Hungarian|futottalak]]</span>


| colspan="5" style="background-color%3Argb%2895%25%2C95%25%2C100%25%29" | <small>―</small>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! rowspan="3" style="background-color%3A%23d1f5d1" | Condi&shy;tional<br>mood


! rowspan="3" style="background-color%3A%23d1f5d1" | Pre&shy;sent


! style="background-color%3A%23d1f5d1" | <abbr title="Indefinite">Indef.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Ccond%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futnék#Hungarian|futnék]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Ccond%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futnál#Hungarian|futnál]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Ccond%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futna#Hungarian|futna]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Ccond%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futnánk#Hungarian|futnánk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Ccond%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futnátok#Hungarian|futnátok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Ccond%7Cpres%7Cindef-form-of+++++++" lang="hu">[[futnának#Hungarian|futnának]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background-color%3A%23d1f5d1" | <abbr title="Definite">Def.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Ccond%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futnám#Hungarian|futnám]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Ccond%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futnád#Hungarian|futnád]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Ccond%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futná#Hungarian|futná]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Ccond%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futnánk#Hungarian|futnánk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Ccond%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futnátok#Hungarian|futnátok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Ccond%7Cpres%7Cdef-form-of+++++++" lang="hu">[[futnák#Hungarian|futnák]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29%3B"

! style="background-color%3A%23d1f5d1%3B+line-height%3A+0.95%3B+white-space%3Anowrap%3B" | <small><abbr title="second-person+object">2nd-p. o.</abbr></small>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Ccond%7Cpres%7C2o-form-of+++++++" lang="hu">[[futnálak#Hungarian|futnálak]]</span>


| colspan="5" style="background-color%3Argb%2895%25%2C95%25%2C100%25%29" | <small>―</small>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! rowspan="3" style="background-color%3A%23e2f6e2" | Sub&shy;junc&shy;tive<br>mood


! rowspan="3" style="background-color%3A%23e2f6e2" | Pre&shy;sent


! style="background-color%3A%23e2f6e2" | <abbr title="Indefinite">Indef.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Csubj%7Cpres%7Cindef-form-of+++++++" lang="hu">[[fussak#Hungarian|fussak]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Csubj%7Cpres%7Cindef-form-of+++++++" lang="hu">[[fuss#Hungarian|fuss]]</span>&nbsp;''or''<br><span class="Latn+form-of+lang-hu+2%7Cs%7Csubj%7Cpres%7Cindef-form-of+++++++" lang="hu">[[fussál#Hungarian|fussál]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Csubj%7Cpres%7Cindef-form-of+++++++" lang="hu">[[fusson#Hungarian|fusson]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Csubj%7Cpres%7Cindef-form-of+++++++" lang="hu">[[fussunk#Hungarian|fussunk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Csubj%7Cpres%7Cindef-form-of+++++++" lang="hu">[[fussatok#Hungarian|fussatok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Csubj%7Cpres%7Cindef-form-of+++++++" lang="hu">[[fussanak#Hungarian|fussanak]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background-color%3A%23e2f6e2" | <abbr title="Definite">Def.</abbr>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Csubj%7Cpres%7Cdef-form-of+++++++" lang="hu">[[fussam#Hungarian|fussam]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Csubj%7Cpres%7Cdef-form-of+++++++" lang="hu">[[fusd#Hungarian|fusd]]</span>&nbsp;''or''<br><span class="Latn+form-of+lang-hu+2%7Cs%7Csubj%7Cpres%7Cdef-form-of+++++++" lang="hu">[[fussad#Hungarian|fussad]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Csubj%7Cpres%7Cdef-form-of+++++++" lang="hu">[[fussa#Hungarian|fussa]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Csubj%7Cpres%7Cdef-form-of+++++++" lang="hu">[[fussuk#Hungarian|fussuk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Csubj%7Cpres%7Cdef-form-of+++++++" lang="hu">[[fussátok#Hungarian|fussátok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Csubj%7Cpres%7Cdef-form-of+++++++" lang="hu">[[fussák#Hungarian|fussák]]</span>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29%3B"

! style="background-color%3A%23e2f6e2%3B+line-height%3A+0.95%3B+white-space%3Anowrap%3B" | <small><abbr title="second-person+object">2nd-p. o.</abbr></small>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Csubj%7Cpres%7C2o-form-of+++++++" lang="hu">[[fussalak#Hungarian|fussalak]]</span>


| colspan="5" style="background-color%3Argb%2895%25%2C95%25%2C100%25%29" | <small>―</small>



|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background-color%3A%23d1f5d1" colspan="1" | Infinitive


| colspan="2" | <span class="Latn+form-of+lang-hu+inf-form-of+++++++" lang="hu">[[futni#Hungarian|futni]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cs%7Cinf-form-of+++++++" lang="hu">[[futnom#Hungarian|futnom]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cs%7Cinf-form-of+++++++" lang="hu">[[futnod#Hungarian|futnod]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cs%7Cinf-form-of+++++++" lang="hu">[[futnia#Hungarian|futnia]]</span>


| <span class="Latn+form-of+lang-hu+1%7Cp%7Cinf-form-of+++++++" lang="hu">[[futnunk#Hungarian|futnunk]]</span>


| <span class="Latn+form-of+lang-hu+2%7Cp%7Cinf-form-of+++++++" lang="hu">[[futnotok#Hungarian|futnotok]]</span>


| <span class="Latn+form-of+lang-hu+3%7Cp%7Cinf-form-of+++++++" lang="hu">[[futniuk#Hungarian|futniuk]]</span>


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! colspan="3" rowspan="2" style="background-color%3A%23d1f5d1" | Other nonfinite<br>verb forms


! style="background-color%3A%23d1f5d1" colspan="1" | [[w:Verbal noun|Verbal noun]]


! style="background-color%3A%23d1f5d1" colspan="1" | Present&nbsp;participle


! style="background-color%3A%23d1f5d1" colspan="1" | Past&nbsp;participle


! style="background-color%3A%23d1f5d1" colspan="1" | Future&nbsp;part.


! style="background-color%3A%23d1f5d1" colspan="1" | [[w:Adverbial participle|Adverbial&nbsp;part.]]


! style="background-color%3A%23d1f5d1" colspan="1" | Potential


|- style="background%3Argb%2895%25%2C95%25%2C100%25%29"

| colspan="1" | <span class="Latn" lang="hu">[[futás#Hungarian|futás]]</span>


| colspan="1" | <span class="Latn+form-of+lang-hu+present_participle-form-of+++++++" lang="hu">[[futó#Hungarian|futó]]</span>


| colspan="1" | <span class="Latn+form-of+lang-hu+past_participle-form-of+++++++" lang="hu">[[futott#Hungarian|futott]]</span>


| colspan="1" | <span class="Latn+form-of+lang-hu+future_participle-form-of+++++++" lang="hu">[[futandó#Hungarian|futandó]]</span>


| colspan="1" |  <span class="Latn+form-of+lang-hu+adverbial_participle-form-of+++++++" lang="hu">[[futva#Hungarian|futva]]</span>


| colspan="1" | <span class="Latn+form-of+lang-hu+potential-form-of+++++++" lang="hu">[[futhat#Hungarian|futhat]]</span>


|}
</div></div>
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
                "form": "futok",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-indefinite",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "futsz",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-indefinite",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "fut",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-indefinite",
                  "present",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "fut",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-indefinite",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futunk",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-indefinite",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "futtok",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-indefinite",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "futnak",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-indefinite",
                  "plural",
                  "present",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "futnak",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-indefinite",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "futom",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-definite",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "futod",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-definite",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "futja",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-definite",
                  "present",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futja",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-definite",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futjuk",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-definite",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "futjátok",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-definite",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "futják",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-definite",
                  "plural",
                  "present",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "futják",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-definite",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "futlak",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-second-person",
                  "present",
                  "singular"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person',
                        'indicative',
                        'object-second-person',
                        'plural',
                        'present']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['formal',
                        'indicative',
                        'object-second-person',
                        'present',
                        'second-person-semantically',
                        'third-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['indicative',
                        'informal',
                        'object-second-person',
                        'present',
                        'second-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['indicative',
                        'object-second-person',
                        'present',
                        'third-person']},
              {
                "form": "futottam",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-indefinite",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "futottál",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-indefinite",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "futott",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-indefinite",
                  "past",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futott",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-indefinite",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futottunk",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-indefinite",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "futottatok",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-indefinite",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "futottak",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-indefinite",
                  "past",
                  "plural",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "futottak",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-indefinite",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "futottam",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-definite",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "futottad",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-definite",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "futotta",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-definite",
                  "past",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futotta",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-definite",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futottuk",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-definite",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "futottátok",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "object-definite",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "futották",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "indicative",
                  "object-definite",
                  "past",
                  "plural",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "futották",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "object-definite",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "futottalak",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "object-second-person",
                  "past",
                  "singular"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person',
                        'indicative',
                        'object-second-person',
                        'past',
                        'plural']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['formal',
                        'indicative',
                        'object-second-person',
                        'past',
                        'second-person-semantically',
                        'third-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['indicative',
                        'informal',
                        'object-second-person',
                        'past',
                        'second-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['indicative',
                        'object-second-person',
                        'past',
                        'third-person']},
              {
                "form": "futnék",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "object-indefinite",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "futnál",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "informal",
                  "object-indefinite",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "futna",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "formal",
                  "object-indefinite",
                  "present",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futna",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "object-indefinite",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futnánk",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "object-indefinite",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "futnátok",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "informal",
                  "object-indefinite",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "futnának",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "formal",
                  "object-indefinite",
                  "plural",
                  "present",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "futnának",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "object-indefinite",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "futnám",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "object-definite",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "futnád",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "informal",
                  "object-definite",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "futná",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "formal",
                  "object-definite",
                  "present",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futná",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "object-definite",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futnánk",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "object-definite",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "futnátok",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "informal",
                  "object-definite",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "futnák",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "formal",
                  "object-definite",
                  "plural",
                  "present",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "futnák",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "object-definite",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "futnálak",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "object-second-person",
                  "present",
                  "singular"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['conditional',
                        'first-person',
                        'object-second-person',
                        'plural',
                        'present']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['conditional',
                        'formal',
                        'object-second-person',
                        'present',
                        'second-person-semantically',
                        'third-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['conditional',
                        'informal',
                        'object-second-person',
                        'present',
                        'second-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['conditional',
                        'object-second-person',
                        'present',
                        'third-person']},
              {
                "form": "fussak",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "object-indefinite",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fuss or",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "object-indefinite",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fussál",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "object-indefinite",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fusson",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "object-indefinite",
                  "present",
                  "second-person-semantically",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fusson",
                "source": "Conjugation",
                "tags": [
                  "object-indefinite",
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussunk",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "object-indefinite",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "fussatok",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "object-indefinite",
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "fussanak",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "object-indefinite",
                  "plural",
                  "present",
                  "second-person-semantically",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussanak",
                "source": "Conjugation",
                "tags": [
                  "object-indefinite",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussam",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "object-definite",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fusd or",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "object-definite",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fussad",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "object-definite",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fussa",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "object-definite",
                  "present",
                  "second-person-semantically",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussa",
                "source": "Conjugation",
                "tags": [
                  "object-definite",
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussuk",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "object-definite",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "fussátok",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "object-definite",
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "fussák",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "object-definite",
                  "plural",
                  "present",
                  "second-person-semantically",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussák",
                "source": "Conjugation",
                "tags": [
                  "object-definite",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussalak",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "object-second-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person',
                        'object-second-person',
                        'plural',
                        'present',
                        'subjunctive']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['formal',
                        'object-second-person',
                        'present',
                        'second-person-semantically',
                        'subjunctive',
                        'third-person']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['informal',
                        'object-second-person',
                        'present',
                        'second-person',
                        'subjunctive']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['object-second-person',
                        'present',
                        'subjunctive',
                        'third-person']},
              {
                "form": "futni",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "futnom",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "infinitive",
                  "singular"
                ]
              },
              {
                "form": "futnod",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "informal",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "futnia",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "infinitive",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futnia",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "futnunk",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "infinitive",
                  "plural"
                ]
              },
              {
                "form": "futnotok",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "informal",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "futniuk",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "infinitive",
                  "plural",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "futniuk",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "futás",
                "source": "Conjugation",
                "tags": [
                  "noun-from-verb"
                ]
              },
              {
                "form": "futó",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "futott",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "futandó",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "participle"
                ]
              },
              {
                "form": "futva",
                "source": "Conjugation",
                "tags": [
                  "adverbial",
                  "participle"
                ]
              },
              {
                "form": "futhat",
                "source": "Conjugation",
                "tags": [
                  "potential"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Hungarian_noun1(self):
        ret = self.xinfl("hűtő", "Hungarian", "noun", "Declension", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="color%3A+rgb%280%25%2C0%25%2C30%25%29%3B+border%3A+solid+1px+rgb%2880%25%2C80%25%2C100%25%29%3B+text-align%3A+center%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23e2f6e2%3B"

! class="vsToggleElement" style="min-width%3A+30em%3B+text-align%3A+left%3B" colspan="3" | Inflection (stem in long/high vowel, front rounded harmony)


|- class="vsHide"

! style="min-width%3A+11em%3B+background%3A%23c0e4c0" |


! style="min-width%3A+10em%3B+background%3A%23c0e4c0" | singular


! style="min-width%3A+10em%3B+background%3A%23c0e4c0" | plural


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[nominative case|nominative]]


| <span class="Latn+form-of+lang-hu+nom%7Cs-form-of+++++++" lang="hu">[[hűtő#Hungarian|hűtő]]</span>


| <span class="Latn+form-of+lang-hu+nom%7Cp-form-of+++++++" lang="hu">[[hűtők#Hungarian|hűtők]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[accusative case|accusative]]


| <span class="Latn+form-of+lang-hu+acc%7Cs-form-of+++++++" lang="hu">[[hűtőt#Hungarian|hűtőt]]</span>


| <span class="Latn+form-of+lang-hu+acc%7Cp-form-of+++++++" lang="hu">[[hűtőket#Hungarian|hűtőket]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[dative case|dative]]


| <span class="Latn+form-of+lang-hu+dat%7Cs-form-of+++++++" lang="hu">[[hűtőnek#Hungarian|hűtőnek]]</span>


| <span class="Latn+form-of+lang-hu+dat%7Cp-form-of+++++++" lang="hu">[[hűtőknek#Hungarian|hűtőknek]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[instrumental case|instrumental]]


| <span class="Latn+form-of+lang-hu+ins%7Cs-form-of+++++++" lang="hu">[[hűtővel#Hungarian|hűtővel]]</span>


| <span class="Latn+form-of+lang-hu+ins%7Cp-form-of+++++++" lang="hu">[[hűtőkkel#Hungarian|hűtőkkel]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[causal-final]]


| <span class="Latn+form-of+lang-hu+cfi%7Cs-form-of+++++++" lang="hu">[[hűtőért#Hungarian|hűtőért]]</span>


| <span class="Latn+form-of+lang-hu+cfi%7Cp-form-of+++++++" lang="hu">[[hűtőkért#Hungarian|hűtőkért]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[translative case|translative]]


| <span class="Latn+form-of+lang-hu+tra%7Cs-form-of+++++++" lang="hu">[[hűtővé#Hungarian|hűtővé]]</span>


| <span class="Latn+form-of+lang-hu+tra%7Cp-form-of+++++++" lang="hu">[[hűtőkké#Hungarian|hűtőkké]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[terminative case|terminative]]


| <span class="Latn+form-of+lang-hu+ter%7Cs-form-of+++++++" lang="hu">[[hűtőig#Hungarian|hűtőig]]</span>


| <span class="Latn+form-of+lang-hu+ter%7Cp-form-of+++++++" lang="hu">[[hűtőkig#Hungarian|hűtőkig]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[essive-formal]]


| <span class="Latn+form-of+lang-hu+esf%7Cs-form-of+++++++" lang="hu">[[hűtőként#Hungarian|hűtőként]]</span>


| <span class="Latn+form-of+lang-hu+esf%7Cp-form-of+++++++" lang="hu">[[hűtőkként#Hungarian|hűtőkként]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[essive-modal]]


| &mdash;


| &mdash;


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[inessive case|inessive]]


| <span class="Latn+form-of+lang-hu+ine%7Cs-form-of+++++++" lang="hu">[[hűtőben#Hungarian|hűtőben]]</span>


| <span class="Latn+form-of+lang-hu+ine%7Cp-form-of+++++++" lang="hu">[[hűtőkben#Hungarian|hűtőkben]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[superessive case|superessive]]


| <span class="Latn+form-of+lang-hu+spe%7Cs-form-of+++++++" lang="hu">[[hűtőn#Hungarian|hűtőn]]</span>


| <span class="Latn+form-of+lang-hu+spe%7Cp-form-of+++++++" lang="hu">[[hűtőkön#Hungarian|hűtőkön]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[adessive case|adessive]]


| <span class="Latn+form-of+lang-hu+ade%7Cs-form-of+++++++" lang="hu">[[hűtőnél#Hungarian|hűtőnél]]</span>


| <span class="Latn+form-of+lang-hu+ade%7Cp-form-of+++++++" lang="hu">[[hűtőknél#Hungarian|hűtőknél]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[illative case|illative]]


| <span class="Latn+form-of+lang-hu+ill%7Cs-form-of+++++++" lang="hu">[[hűtőbe#Hungarian|hűtőbe]]</span>


| <span class="Latn+form-of+lang-hu+ill%7Cp-form-of+++++++" lang="hu">[[hűtőkbe#Hungarian|hűtőkbe]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[sublative]]


| <span class="Latn+form-of+lang-hu+sbl%7Cs-form-of+++++++" lang="hu">[[hűtőre#Hungarian|hűtőre]]</span>


| <span class="Latn+form-of+lang-hu+sbl%7Cp-form-of+++++++" lang="hu">[[hűtőkre#Hungarian|hűtőkre]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[allative case|allative]]


| <span class="Latn+form-of+lang-hu+all%7Cs-form-of+++++++" lang="hu">[[hűtőhöz#Hungarian|hűtőhöz]]</span>


| <span class="Latn+form-of+lang-hu+all%7Cp-form-of+++++++" lang="hu">[[hűtőkhöz#Hungarian|hűtőkhöz]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[elative case|elative]]


| <span class="Latn+form-of+lang-hu+ela%7Cs-form-of+++++++" lang="hu">[[hűtőből#Hungarian|hűtőből]]</span>


| <span class="Latn+form-of+lang-hu+ela%7Cp-form-of+++++++" lang="hu">[[hűtőkből#Hungarian|hűtőkből]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[delative case|delative]]


| <span class="Latn+form-of+lang-hu+del%7Cs-form-of+++++++" lang="hu">[[hűtőről#Hungarian|hűtőről]]</span>


| <span class="Latn+form-of+lang-hu+del%7Cp-form-of+++++++" lang="hu">[[hűtőkről#Hungarian|hűtőkről]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[ablative case|ablative]]


| <span class="Latn+form-of+lang-hu+abl%7Cs-form-of+++++++" lang="hu">[[hűtőtől#Hungarian|hűtőtől]]</span>


| <span class="Latn+form-of+lang-hu+abl%7Cp-form-of+++++++" lang="hu">[[hűtőktől#Hungarian|hűtőktől]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | <small>non-attributive<br>possessive - singular</small>


| <span class="Latn+form-of+lang-hu+np1%7Cs-form-of+++++++" lang="hu">[[hűtőé#Hungarian|hűtőé]]</span>


| <span class="Latn+form-of+lang-hu+np1%7Cp-form-of+++++++" lang="hu">[[hűtőké#Hungarian|hűtőké]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | <small>non-attributive<br>possessive - plural</small>


| <span class="Latn+form-of+lang-hu+np2%7Cs-form-of+++++++" lang="hu">[[hűtőéi#Hungarian|hűtőéi]]</span>


| <span class="Latn+form-of+lang-hu+np2%7Cp-form-of+++++++" lang="hu">[[hűtőkéi#Hungarian|hűtőkéi]]</span>


|}

{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="color%3A+rgb%280%25%2C0%25%2C30%25%29%3B+border%3A+solid+1px+rgb%2880%25%2C80%25%2C100%25%29%3B+text-align%3A+center%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23e2f6e2%3B"

! class="vsToggleElement" style="min-width%3A+30em%3B+text-align%3A+left%3B" colspan="3" | [[Appendix:Hungarian possessive suffixes|Possessive forms]] of <i class="Latn+mention" lang="hu">hűtő</i>


|- class="vsHide"

! style="min-width%3A+11em%3B+background%3A%23c0e4c0" | possessor


! style="min-width%3A+10em%3B+background%3A%23c0e4c0" | single possession


! style="min-width%3A+10em%3B+background%3A%23c0e4c0" | multiple possessions


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | 1st person sing.


| <span class="Latn" lang="hu">[[hűtőm#Hungarian|hűtőm]]</span>


| <span class="Latn" lang="hu">[[hűtőim#Hungarian|hűtőim]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | 2nd person sing.


| <span class="Latn" lang="hu">[[hűtőd#Hungarian|hűtőd]]</span>


| <span class="Latn" lang="hu">[[hűtőid#Hungarian|hűtőid]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | 3rd person sing.


| <span class="Latn" lang="hu">[[hűtője#Hungarian|hűtője]]</span>


| <span class="Latn" lang="hu">[[hűtői#Hungarian|hűtői]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | 1st person plural


| <span class="Latn" lang="hu">[[hűtőnk#Hungarian|hűtőnk]]</span>


| <span class="Latn" lang="hu">[[hűtőink#Hungarian|hűtőink]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | 2nd person plural


| <span class="Latn" lang="hu">[[hűtőtök#Hungarian|hűtőtök]]</span>


| <span class="Latn" lang="hu">[[hűtőitek#Hungarian|hűtőitek]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | 3rd person plural


| <span class="Latn" lang="hu">[[hűtőjük#Hungarian|hűtőjük]]</span>


| <span class="Latn" lang="hu">[[hűtőik#Hungarian|hűtőik]]</span>


|}
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
                "form": "front rounded harmony",
                "source": "Declension",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "long/high vowel",
                "source": "Declension",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "hűtő",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "hűtők",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "hűtőt",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "singular"
                ]
              },
              {
                "form": "hűtőket",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural"
                ]
              },
              {
                "form": "hűtőnek",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "hűtőknek",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "hűtővel",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "hűtőkkel",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "hűtőért",
                "source": "Declension",
                "tags": [
                  "causal-final",
                  "singular"
                ]
              },
              {
                "form": "hűtőkért",
                "source": "Declension",
                "tags": [
                  "causal-final",
                  "plural"
                ]
              },
              {
                "form": "hűtővé",
                "source": "Declension",
                "tags": [
                  "singular",
                  "translative"
                ]
              },
              {
                "form": "hűtőkké",
                "source": "Declension",
                "tags": [
                  "plural",
                  "translative"
                ]
              },
              {
                "form": "hűtőig",
                "source": "Declension",
                "tags": [
                  "singular",
                  "terminative"
                ]
              },
              {
                "form": "hűtőkig",
                "source": "Declension",
                "tags": [
                  "plural",
                  "terminative"
                ]
              },
              {
                "form": "hűtőként",
                "source": "Declension",
                "tags": [
                  "essive-formal",
                  "singular"
                ]
              },
              {
                "form": "hűtőkként",
                "source": "Declension",
                "tags": [
                  "essive-formal",
                  "plural"
                ]
              },
              {
                "form": "-",
                "source": "Declension",
                "tags": [
                  "essive-modal",
                  "singular"
                ]
              },
              {
                "form": "-",
                "source": "Declension",
                "tags": [
                  "essive-modal",
                  "plural"
                ]
              },
              {
                "form": "hűtőben",
                "source": "Declension",
                "tags": [
                  "inessive",
                  "singular"
                ]
              },
              {
                "form": "hűtőkben",
                "source": "Declension",
                "tags": [
                  "inessive",
                  "plural"
                ]
              },
              {
                "form": "hűtőn",
                "source": "Declension",
                "tags": [
                  "singular",
                  "superessive"
                ]
              },
              {
                "form": "hűtőkön",
                "source": "Declension",
                "tags": [
                  "plural",
                  "superessive"
                ]
              },
              {
                "form": "hűtőnél",
                "source": "Declension",
                "tags": [
                  "adessive",
                  "singular"
                ]
              },
              {
                "form": "hűtőknél",
                "source": "Declension",
                "tags": [
                  "adessive",
                  "plural"
                ]
              },
              {
                "form": "hűtőbe",
                "source": "Declension",
                "tags": [
                  "illative",
                  "singular"
                ]
              },
              {
                "form": "hűtőkbe",
                "source": "Declension",
                "tags": [
                  "illative",
                  "plural"
                ]
              },
              {
                "form": "hűtőre",
                "source": "Declension",
                "tags": [
                  "singular",
                  "sublative"
                ]
              },
              {
                "form": "hűtőkre",
                "source": "Declension",
                "tags": [
                  "plural",
                  "sublative"
                ]
              },
              {
                "form": "hűtőhöz",
                "source": "Declension",
                "tags": [
                  "allative",
                  "singular"
                ]
              },
              {
                "form": "hűtőkhöz",
                "source": "Declension",
                "tags": [
                  "allative",
                  "plural"
                ]
              },
              {
                "form": "hűtőből",
                "source": "Declension",
                "tags": [
                  "elative",
                  "singular"
                ]
              },
              {
                "form": "hűtőkből",
                "source": "Declension",
                "tags": [
                  "elative",
                  "plural"
                ]
              },
              {
                "form": "hűtőről",
                "source": "Declension",
                "tags": [
                  "delative",
                  "singular"
                ]
              },
              {
                "form": "hűtőkről",
                "source": "Declension",
                "tags": [
                  "delative",
                  "plural"
                ]
              },
              {
                "form": "hűtőtől",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "singular"
                ]
              },
              {
                "form": "hűtőktől",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural"
                ]
              },
              {
                "form": "hűtőé",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-single",
                  "predicative",
                  "singular"
                ]
              },
              {
                "form": "hűtőké",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-single",
                  "predicative"
                ]
              },
              {
                "form": "hűtőéi",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-single",
                  "predicative",
                  "singular"
                ]
              },
              {
                "form": "hűtőkéi",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-single",
                  "predicative"
                ]
              },
              {
                "form": "",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "hűtőm",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "possessive",
                  "possessive-single",
                  "singular"
                ]
              },
              {
                "form": "hűtőim",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "possessive",
                  "possessive-many",
                  "singular"
                ]
              },
              {
                "form": "hűtőd",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-single",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "hűtőid",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-many",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "hűtője",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-single",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "hűtői",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-many",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "hűtőnk",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-single"
                ]
              },
              {
                "form": "hűtőink",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-many"
                ]
              },
              {
                "form": "hűtőtök",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-single",
                  "second-person"
                ]
              },
              {
                "form": "hűtőitek",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-many",
                  "second-person"
                ]
              },
              {
                "form": "hűtőjük",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "hűtőik",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-many",
                  "third-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Hungarian_adj1(self):
        ret = self.xinfl("rövid", "Hungarian", "adj", "Declension", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="color%3A+rgb%280%25%2C0%25%2C30%25%29%3B+border%3A+solid+1px+rgb%2880%25%2C80%25%2C100%25%29%3B+text-align%3A+center%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23e2f6e2%3B"

! class="vsToggleElement" style="min-width%3A+30em%3B+text-align%3A+left%3B" colspan="3" | Inflection (stem in <i class="Latn+mention" lang="hu">-e-</i>, front unrounded harmony)


|- class="vsHide"

! style="min-width%3A+11em%3B+background%3A%23c0e4c0" |


! style="min-width%3A+10em%3B+background%3A%23c0e4c0" | singular


! style="min-width%3A+10em%3B+background%3A%23c0e4c0" | plural


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[nominative case|nominative]]


| <span class="Latn+form-of+lang-hu+nom%7Cs-form-of+++++++" lang="hu">[[rövid#Hungarian|rövid]]</span>


| <span class="Latn+form-of+lang-hu+nom%7Cp-form-of+++++++" lang="hu">[[rövidek#Hungarian|rövidek]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[accusative case|accusative]]


| <span class="Latn+form-of+lang-hu+acc%7Cs-form-of+++++++" lang="hu">[[rövidet#Hungarian|rövidet]]</span>


| <span class="Latn+form-of+lang-hu+acc%7Cp-form-of+++++++" lang="hu">[[rövideket#Hungarian|rövideket]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[dative case|dative]]


| <span class="Latn+form-of+lang-hu+dat%7Cs-form-of+++++++" lang="hu">[[rövidnek#Hungarian|rövidnek]]</span>


| <span class="Latn+form-of+lang-hu+dat%7Cp-form-of+++++++" lang="hu">[[rövideknek#Hungarian|rövideknek]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[instrumental case|instrumental]]


| <span class="Latn+form-of+lang-hu+ins%7Cs-form-of+++++++" lang="hu">[[röviddel#Hungarian|röviddel]]</span>


| <span class="Latn+form-of+lang-hu+ins%7Cp-form-of+++++++" lang="hu">[[rövidekkel#Hungarian|rövidekkel]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[causal-final]]


| <span class="Latn+form-of+lang-hu+cfi%7Cs-form-of+++++++" lang="hu">[[rövidért#Hungarian|rövidért]]</span>


| <span class="Latn+form-of+lang-hu+cfi%7Cp-form-of+++++++" lang="hu">[[rövidekért#Hungarian|rövidekért]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[translative case|translative]]


| <span class="Latn+form-of+lang-hu+tra%7Cs-form-of+++++++" lang="hu">[[röviddé#Hungarian|röviddé]]</span>


| <span class="Latn+form-of+lang-hu+tra%7Cp-form-of+++++++" lang="hu">[[rövidekké#Hungarian|rövidekké]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[terminative case|terminative]]


| <span class="Latn+form-of+lang-hu+ter%7Cs-form-of+++++++" lang="hu">[[rövidig#Hungarian|rövidig]]</span>


| <span class="Latn+form-of+lang-hu+ter%7Cp-form-of+++++++" lang="hu">[[rövidekig#Hungarian|rövidekig]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[essive-formal]]


| <span class="Latn+form-of+lang-hu+esf%7Cs-form-of+++++++" lang="hu">[[rövidként#Hungarian|rövidként]]</span>


| <span class="Latn+form-of+lang-hu+esf%7Cp-form-of+++++++" lang="hu">[[rövidekként#Hungarian|rövidekként]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[essive-modal]]


| &mdash;


| &mdash;


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[inessive case|inessive]]


| <span class="Latn+form-of+lang-hu+ine%7Cs-form-of+++++++" lang="hu">[[rövidben#Hungarian|rövidben]]</span>


| <span class="Latn+form-of+lang-hu+ine%7Cp-form-of+++++++" lang="hu">[[rövidekben#Hungarian|rövidekben]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[superessive case|superessive]]


| <span class="Latn+form-of+lang-hu+spe%7Cs-form-of+++++++" lang="hu">[[röviden#Hungarian|röviden]]</span>


| <span class="Latn+form-of+lang-hu+spe%7Cp-form-of+++++++" lang="hu">[[rövideken#Hungarian|rövideken]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[adessive case|adessive]]


| <span class="Latn+form-of+lang-hu+ade%7Cs-form-of+++++++" lang="hu">[[rövidnél#Hungarian|rövidnél]]</span>


| <span class="Latn+form-of+lang-hu+ade%7Cp-form-of+++++++" lang="hu">[[rövideknél#Hungarian|rövideknél]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[illative case|illative]]


| <span class="Latn+form-of+lang-hu+ill%7Cs-form-of+++++++" lang="hu">[[rövidbe#Hungarian|rövidbe]]</span>


| <span class="Latn+form-of+lang-hu+ill%7Cp-form-of+++++++" lang="hu">[[rövidekbe#Hungarian|rövidekbe]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[sublative]]


| <span class="Latn+form-of+lang-hu+sbl%7Cs-form-of+++++++" lang="hu">[[rövidre#Hungarian|rövidre]]</span>


| <span class="Latn+form-of+lang-hu+sbl%7Cp-form-of+++++++" lang="hu">[[rövidekre#Hungarian|rövidekre]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[allative case|allative]]


| <span class="Latn+form-of+lang-hu+all%7Cs-form-of+++++++" lang="hu">[[rövidhez#Hungarian|rövidhez]]</span>


| <span class="Latn+form-of+lang-hu+all%7Cp-form-of+++++++" lang="hu">[[rövidekhez#Hungarian|rövidekhez]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[elative case|elative]]


| <span class="Latn+form-of+lang-hu+ela%7Cs-form-of+++++++" lang="hu">[[rövidből#Hungarian|rövidből]]</span>


| <span class="Latn+form-of+lang-hu+ela%7Cp-form-of+++++++" lang="hu">[[rövidekből#Hungarian|rövidekből]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[delative case|delative]]


| <span class="Latn+form-of+lang-hu+del%7Cs-form-of+++++++" lang="hu">[[rövidről#Hungarian|rövidről]]</span>


| <span class="Latn+form-of+lang-hu+del%7Cp-form-of+++++++" lang="hu">[[rövidekről#Hungarian|rövidekről]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | [[ablative case|ablative]]


| <span class="Latn+form-of+lang-hu+abl%7Cs-form-of+++++++" lang="hu">[[rövidtől#Hungarian|rövidtől]]</span>


| <span class="Latn+form-of+lang-hu+abl%7Cp-form-of+++++++" lang="hu">[[rövidektől#Hungarian|rövidektől]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | <small>non-attributive<br>possessive - singular</small>


| <span class="Latn+form-of+lang-hu+np1%7Cs-form-of+++++++" lang="hu">[[rövidé#Hungarian|rövidé]]</span>


| <span class="Latn+form-of+lang-hu+np1%7Cp-form-of+++++++" lang="hu">[[rövideké#Hungarian|rövideké]]</span>


|- class="vsHide" style="background%3Argb%2895%25%2C95%25%2C100%25%29"

! style="background%3A%23e2f6e2" | <small>non-attributive<br>possessive - plural</small>


| <span class="Latn+form-of+lang-hu+np2%7Cs-form-of+++++++" lang="hu">[[rövidéi#Hungarian|rövidéi]]</span>


| <span class="Latn+form-of+lang-hu+np2%7Cp-form-of+++++++" lang="hu">[[rövidekéi#Hungarian|rövidekéi]]</span>


|}
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
                "form": "front unrounded harmony",
                "source": "Declension",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "-e-",
                "source": "Declension",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "rövid",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "rövidek",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "rövidet",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "singular"
                ]
              },
              {
                "form": "rövideket",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural"
                ]
              },
              {
                "form": "rövidnek",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "rövideknek",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "röviddel",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "rövidekkel",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "rövidért",
                "source": "Declension",
                "tags": [
                  "causal-final",
                  "singular"
                ]
              },
              {
                "form": "rövidekért",
                "source": "Declension",
                "tags": [
                  "causal-final",
                  "plural"
                ]
              },
              {
                "form": "röviddé",
                "source": "Declension",
                "tags": [
                  "singular",
                  "translative"
                ]
              },
              {
                "form": "rövidekké",
                "source": "Declension",
                "tags": [
                  "plural",
                  "translative"
                ]
              },
              {
                "form": "rövidig",
                "source": "Declension",
                "tags": [
                  "singular",
                  "terminative"
                ]
              },
              {
                "form": "rövidekig",
                "source": "Declension",
                "tags": [
                  "plural",
                  "terminative"
                ]
              },
              {
                "form": "rövidként",
                "source": "Declension",
                "tags": [
                  "essive-formal",
                  "singular"
                ]
              },
              {
                "form": "rövidekként",
                "source": "Declension",
                "tags": [
                  "essive-formal",
                  "plural"
                ]
              },
              {
                "form": "-",
                "source": "Declension",
                "tags": [
                  "essive-modal",
                  "singular"
                ]
              },
              {
                "form": "-",
                "source": "Declension",
                "tags": [
                  "essive-modal",
                  "plural"
                ]
              },
              {
                "form": "rövidben",
                "source": "Declension",
                "tags": [
                  "inessive",
                  "singular"
                ]
              },
              {
                "form": "rövidekben",
                "source": "Declension",
                "tags": [
                  "inessive",
                  "plural"
                ]
              },
              {
                "form": "röviden",
                "source": "Declension",
                "tags": [
                  "singular",
                  "superessive"
                ]
              },
              {
                "form": "rövideken",
                "source": "Declension",
                "tags": [
                  "plural",
                  "superessive"
                ]
              },
              {
                "form": "rövidnél",
                "source": "Declension",
                "tags": [
                  "adessive",
                  "singular"
                ]
              },
              {
                "form": "rövideknél",
                "source": "Declension",
                "tags": [
                  "adessive",
                  "plural"
                ]
              },
              {
                "form": "rövidbe",
                "source": "Declension",
                "tags": [
                  "illative",
                  "singular"
                ]
              },
              {
                "form": "rövidekbe",
                "source": "Declension",
                "tags": [
                  "illative",
                  "plural"
                ]
              },
              {
                "form": "rövidre",
                "source": "Declension",
                "tags": [
                  "singular",
                  "sublative"
                ]
              },
              {
                "form": "rövidekre",
                "source": "Declension",
                "tags": [
                  "plural",
                  "sublative"
                ]
              },
              {
                "form": "rövidhez",
                "source": "Declension",
                "tags": [
                  "allative",
                  "singular"
                ]
              },
              {
                "form": "rövidekhez",
                "source": "Declension",
                "tags": [
                  "allative",
                  "plural"
                ]
              },
              {
                "form": "rövidből",
                "source": "Declension",
                "tags": [
                  "elative",
                  "singular"
                ]
              },
              {
                "form": "rövidekből",
                "source": "Declension",
                "tags": [
                  "elative",
                  "plural"
                ]
              },
              {
                "form": "rövidről",
                "source": "Declension",
                "tags": [
                  "delative",
                  "singular"
                ]
              },
              {
                "form": "rövidekről",
                "source": "Declension",
                "tags": [
                  "delative",
                  "plural"
                ]
              },
              {
                "form": "rövidtől",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "singular"
                ]
              },
              {
                "form": "rövidektől",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural"
                ]
              },
              {
                "form": "rövidé",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-single",
                  "predicative",
                  "singular"
                ]
              },
              {
                "form": "rövideké",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-single",
                  "predicative"
                ]
              },
              {
                "form": "rövidéi",
                "source": "Declension",
                "tags": [
                  "possessive",
                  "possessive-single",
                  "predicative",
                  "singular"
                ]
              },
              {
                "form": "rövidekéi",
                "source": "Declension",
                "tags": [
                  "plural",
                  "possessive",
                  "possessive-single",
                  "predicative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

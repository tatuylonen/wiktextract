# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.inflection import parse_inflection_section

class InflTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 100000
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())

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

    def test_GermanLowGerman_verb1(self):
        ret = self.xinfl("kriegen", "German Low German", "verb",
                         "Conjugation", """
<div class="NavFrame" style="width%3A+42em">
<div class="NavHead" style="background%3A%23CCCCFF%3B">Conjugation of ''kriegen'' (class 1 strong verb)</div>
<div class="NavContent">

{| style="width%3A+100%25%3B+border%3A1px+solid+%23CCCCFF%3B+line-height%3A+125%25%3B+background-color%3A%23F9F9F9%3B+text-align%3Acenter%3B+border%3A+1px+solid+%23CCCCFF%3B" cellspacing="1" cellpadding="3" class="inflection-table"

|-
 style="background-color:#F2F2FF; "

|-

! style="background-color%3A%23dedeee%3B+font-weight%3Abold%3B" | [[infinitive]]


| colspan="2" style="background-color%3A%23EFEFEF%3B" | '''kriegen'''


|-

! style="background-color%3A%23CCCCFF%3B+font-weight%3Abold%3B" | [[indicative mood|indicative]]


! style="background-color%3A%23dedeee%3B+font-weight%3Abold%3B" | [[present tense|present]]


! style="background-color%3A%23dedeee%3B+font-weight%3Abold%3B" | [[preterite]]


|-

! style="background-color%3A%23eeeeee%3B+font-weight%3Abold%3B" |[[first-person|1st&nbsp;person]]&nbsp;[[singular]]


| style="background-color%3A%23efefff%3B" | krieg


| style="background-color%3A%23efefff%3B" | kreeg


|-

! style="background-color%3A%23eeeeee%3B+font-weight%3Abold%3B" |[[second-person|2nd&nbsp;person]]&nbsp;[[singular]]


| style="background-color%3A%23efefff%3B" | kriggs(t)


| style="background-color%3A%23efefff%3B" | kreegs(t)


|-

! style="background-color%3A%23eeeeee%3B+font-weight%3Abold%3B" |[[third-person|3rd&nbsp;person]]&nbsp;[[singular]]


| style="background-color%3A%23efefff%3B" | krigg(t)


| style="background-color%3A%23efefff%3B" | kreeg


|-

! style="background-color%3A%23eeeeee%3B+font-weight%3Abold%3B" |[[plural]]


| style="background-color%3A%23efefff%3B" | kriegt, kriegen


| style="background-color%3A%23efefff%3B" | kregen


|-

! style="background-color%3A%23CCCCFF%3B+font-weight%3Abold%3B" | [[imperative mood|imperative]]


! style="background-color%3A%23eedede%3B+font-weight%3Abold%3B" | [[present tense|present]]


! style="background-color%3A%23eedede%3B+font-weight%3Abold%3B" | —


|-

! style="background-color%3A%23eeeeee%3B+font-weight%3Abold%3B" |[[singular]]


| style="background-color%3A%23ffefef%3B" | krieg


| style="background-color%3A%23ffefef%3B" |


|-

! style="background-color%3A%23eeeeee%3B+font-weight%3Abold%3B" |[[plural]]


| style="background-color%3A%23ffefef%3B" | kriegt


| style="background-color%3A%23ffefef%3B" |


|-

! style="background-color%3A%23CCCCFF%3B+font-weight%3Abold%3B" | [[participle]]


! style="background-color%3A%23deeede%3B+font-weight%3Abold%3B" | [[present tense|present]]


! style="background-color%3A%23deeede%3B+font-weight%3Abold%3B" | [[past tense|past]]


|-

! style="background-color%3A%23eeeeee%3B+font-weight%3Abold%3B" |


| style="background-color%3A%23efffef%3B" | kriegen


| style="background-color%3A%23efffef%3B" | (e)kregen, gekregen


|-

! style="text+align%3Aleft%3B+font-weight%3A+normal" colspan="3" |Note: This conjugation is one of many; neither its grammar nor spelling apply to all dialects.


|}
</div></div>[[Category:Low German class 1 strong verbs]]
""")
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
                "form": "1 strong verb",
                "source": "Conjugation",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "kriegen",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "krieg",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "kreeg",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "preterite",
                  "singular"
                ]
              },
              {
                "form": "kriggs",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "kriggst",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "kreegs",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "kreegst",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "krigg",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "kriggt",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "kreeg",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "kriegt",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "kriegen",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "kregen",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite"
                ]
              },
              {
                "form": "krieg",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "kriegt",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "kriegen",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "kregen",
                "source": "Conjugation",
                "tags": ["participle", "past"],
              },
              {
                "form": "ekregen",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "gekregen",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

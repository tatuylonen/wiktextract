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

    def test_Danish_noun1(self):
        ret = self.xinfl("motorsav", "Danish", "noun", "Inflection", """
<div class="NavFrame">
<div class="NavHead">Declension of <i class="Latn+mention" lang="da">motorsav</i></div>
<div class="NavContent">

{| class="inflection-table" style="text-align%3Acenter%3Bwidth%3A100%25%3B"

|- style="background-color%3A%23eee%3B"

! rowspan="2" | common<br>gender


! colspan="2" | ''Singular''


! colspan="2" | ''Plural''


|- style="font-size%3A90%25%3Bbackground-color%3A%23eee%3B"

! style="width%3A25%25%3B" | ''indefinite''


! style="width%3A25%25%3B" | ''definite''


! style="width%3A25%25%3B" | ''indefinite''


! style="width%3A25%25%3B" | ''definite''


|-

! style="background-color%3A%23eee%3B" | ''[[nominative case|nominative]]''


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn" lang="da">[[motorsav#Danish|motorsav]]</span>


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn+form-of+lang-da+def%7Cs-form-of+++++++" lang="da">[[motorsaven#Danish|motorsaven]]</span>


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn+form-of+lang-da+indef%7Cp-form-of+++++++" lang="da">[[motorsave#Danish|motorsave]]</span>


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn+form-of+lang-da+def%7Cp-form-of+++++++" lang="da">[[motorsavene#Danish|motorsavene]]</span>


|-

! style="background-color%3A%23eee%3B" | ''[[genitive case|genitive]]''


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn+form-of+lang-da+indef%7Cgen%7Cs-form-of+++++++" lang="da">[[motorsavs#Danish|motorsavs]]</span>


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn+form-of+lang-da+def%7Cgen%7Cs-form-of+++++++" lang="da">[[motorsavens#Danish|motorsavens]]</span>


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn+form-of+lang-da+indef%7Cgen%7Cp-form-of+++++++" lang="da">[[motorsaves#Danish|motorsaves]]</span>


| style="background-color%3A%23f9f9f9%3B" | <span class="Latn+form-of+lang-da+def%7Cgen%7Cp-form-of+++++++" lang="da">[[motorsavenes#Danish|motorsavenes]]</span>


|}

</div></div>
""")
        expected = {
            "forms": [
              {
                "form": "motorsav",
                "source": "Inflection",
                "tags": [
                  "indefinite",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "motorsaven",
                "source": "Inflection",
                "tags": [
                  "definite",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "motorsave",
                "source": "Inflection",
                "tags": [
                  "indefinite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "motorsavene",
                "source": "Inflection",
                "tags": [
                  "definite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "motorsavs",
                "source": "Inflection",
                "tags": [
                  "genitive",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "motorsavens",
                "source": "Inflection",
                "tags": [
                  "definite",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "motorsaves",
                "source": "Inflection",
                "tags": [
                  "genitive",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "motorsavenes",
                "source": "Inflection",
                "tags": [
                  "definite",
                  "genitive",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Danish_verb1(self):
        ret = self.xinfl("patte", "Danish", "verb", "Inflection", """
<div class="NavFrame">
<div class="NavHead">Inflection of <i class="Latn+mention" lang="da">patte</i></div>
<div class="NavContent">

{| class="inflection-table" style="border-collapse%3Aseparate%3B+background%3A%23F0F0F0%3B+text-align%3Acenter%3B+width%3A100%25%3B+border-spacing%3A2px"

|-

!


! colspan="1" |present


! colspan="1" |past


|-

! colspan="1" style="background%3A%23c0cfe4" | simple


|<span class="Latn+form-of+lang-da+pres-form-of+++++++" lang="da">[[patter#Danish|patter]]</span>


|<span class="Latn+form-of+lang-da+past-form-of+++++++" lang="da">[[pattede#Danish|pattede]]</span>


|-

! colspan="1" style="background%3A%23c0cfe4" | perfect


|<span class="Latn" lang="da">[[har#Danish|har]]</span> pattet


|<span class="Latn" lang="da">[[havde#Danish|havde]]</span> pattet


|-

! colspan="1" style="background%3A%23c0cfe4" | passive


|<span class="Latn+form-of+lang-da+pasv-form-of+++++++" lang="da">[[pattes#Danish|pattes]]</span>


|&mdash;


|-

! colspan="1" style="background%3A%23c0cfe4" | participle


|<span class="Latn+form-of+lang-da+pres%7Cptcp-form-of+++++++" lang="da">[[pattende#Danish|pattende]]</span>


|<span class="Latn+form-of+lang-da+past%7Cptcp-form-of+++++++" lang="da">[[pattet#Danish|pattet]]</span>


|-

! colspan="1" style="background%3A%23e2e4c0" |imperative


|<span class="Latn+form-of+lang-da+impr-form-of+++++++" lang="da">[[pat#Danish|pat]]</span>


|—


|-

! colspan="1" style="background%3A%23e2e4c0" |infinitive


|<span class="Latn" lang="da">[[patte#Danish|patte]]</span>


|—


|-

! colspan="1" style="background%3A%23e2e4c0" |auxiliary verb


|<span class="Latn" lang="da">[[have#Danish|have]]</span>


|—


|-

! colspan="1" style="background%3A%23e2e4c0" |gerund


|<span class="Latn+form-of+lang-da+gerund-form-of+++++++" lang="da">[[patten#Danish|patten]]</span>


|—


|}


</div></div>



""")
        expected = {
           "forms": [
             {
               "form": "patter",
               "source": "Inflection",
               "tags": [
                 "present"
               ]
             },
             {
               "form": "pattede",
               "source": "Inflection",
               "tags": [
                 "past"
               ]
             },
             {
               "form": "har pattet",
               "source": "Inflection",
               "tags": [
                 "perfect",
                 "present"
               ]
             },
             {
               "form": "havde pattet",
               "source": "Inflection",
               "tags": [
                 "past",
                 "perfect"
               ]
             },
             {
               "form": "pattes",
               "source": "Inflection",
               "tags": [
                 "passive",
                 "present"
               ]
             },
             {
               "form": "pattende",
               "source": "Inflection",
               "tags": [
                 "participle",
                 "present"
               ]
             },
             {
               "form": "pattet",
               "source": "Inflection",
               "tags": [
                 "participle",
                 "past"
               ]
             },
             {
               "form": "pat",
               "source": "Inflection",
               "tags": [
                 "imperative",
                 "present"
               ]
             },
             {
               "form": "patte",
               "source": "Inflection",
               "tags": [
                 "infinitive",
                 "present"
               ]
             },
             {
               "form": "have",
               "source": "Inflection",
               "tags": [
                 "auxiliary",
                 "present"
               ]
             },
             {
               "form": "patten",
               "source": "Inflection",
               "tags": [
                 "gerund",
                 "present"
               ]
             }
           ],
        }
        self.assertEqual(expected, ret)

    def test_Danish_adj1(self):
        ret = self.xinfl("kedelig", "Danish", "adj", "Inflection", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="border%3A+solid+1px+%23CCCCFF%3B+text-align%3Aleft%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23CCCCFF%3B+vertical-align%3A+top%3B"

! class="vsToggleElement" colspan="4" | Inflection of <i class="Latn+mention" lang="da">kedelig</i>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! style="min-width%3A+12em%3B" |


! style="min-width%3A+12em%3B" | Positive


! style="min-width%3A+12em%3B" | Comparative


! style="min-width%3A+12em%3B" | Superlative


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Common singular


| <span class="Latn" lang="da">[[kedelig#Danish|kedelig]]</span>


| <span class="Latn" lang="da">[[kedeligere#Danish|kedeligere]]</span>


| <span class="Latn" lang="da">[[kedeligst#Danish|kedeligst]]</span><sup>2</sup>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Neuter singular


| <span class="Latn" lang="da">[[kedeligt#Danish|kedeligt]]</span>


| <span class="Latn" lang="da">[[kedeligere#Danish|kedeligere]]</span>


| <span class="Latn" lang="da">[[kedeligst#Danish|kedeligst]]</span><sup>2</sup>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Plural


| <span class="Latn" lang="da">[[kedelige#Danish|kedelige]]</span>


| <span class="Latn" lang="da">[[kedeligere#Danish|kedeligere]]</span>


| <span class="Latn" lang="da">[[kedeligst#Danish|kedeligst]]</span><sup>2</sup>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Definite attributive<sup>1</sup>


| <span class="Latn" lang="da">[[kedelige#Danish|kedelige]]</span>


| <span class="Latn" lang="da">[[kedeligere#Danish|kedeligere]]</span>


| <span class="Latn" lang="da">[[kedeligste#Danish|kedeligste]]</span>


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

| style="font-size%3A+smaller%3B" colspan="4" | 1) When an adjective is applied predicatively to something definite, the corresponding "indefinite" form is used.<br> 2) The "indefinite" superlatives may not be used attributively.


|}
""")
        expected = {
            "forms": [
              {
                "form": "kedelig",
                "source": "Inflection",
                "tags": [
                  "common-gender",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "kedeligere",
                "source": "Inflection",
                "tags": [
                  "common-gender",
                  "comparative",
                  "singular"
                ]
              },
              {
                "form": "kedeligst",
                "source": "Inflection",
                "tags": [
                  "common-gender",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "kedeligt",
                "source": "Inflection",
                "tags": [
                  "neuter",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "kedeligere",
                "source": "Inflection",
                "tags": [
                  "comparative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "kedeligst",
                "source": "Inflection",
                "tags": [
                  "neuter",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "kedelige",
                "source": "Inflection",
                "tags": [
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "kedeligere",
                "source": "Inflection",
                "tags": [
                  "comparative",
                  "plural"
                ]
              },
              {
                "form": "kedeligst",
                "source": "Inflection",
                "tags": [
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "kedelige",
                "source": "Inflection",
                "tags": [
                  "attributive",
                  "definite",
                  "positive"
                ]
              },
              {
                "form": "kedeligere",
                "source": "Inflection",
                "tags": [
                  "attributive",
                  "comparative",
                  "definite"
                ]
              },
              {
                "form": "kedeligste",
                "source": "Inflection",
                "tags": [
                  "attributive",
                  "definite",
                  "superlative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
import json
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.inflection import parse_inflection_section

class InflTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 100000
        self.wtpctx = Wtp()
        self.config = WiktionaryConfig()
        self.wtpctx.start_page("testpage")
        self.wtpctx.start_section("English")

    def xinfl(self, word, lang, pos, section, text):
        """Runs a single inflection table parsing test, and returns ``data``."""
        self.wtpctx.start_page(word)
        self.wtpctx.start_section(lang)
        self.wtpctx.start_subsection(pos)
        tree = self.wtpctx.parse(text)
        data = {}
        parse_inflection_section(self.config, self.wtpctx, data, word, lang, pos,
                                 section, tree)
        return data

    def test_Swedish_noun1(self):
        ret = self.xinfl("berg", "Swedish", "noun", "Declension", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="border%3A+solid+1px+%23CCCCFF%3B+text-align%3Aleft%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23CCCCFF%3B+vertical-align%3A+top%3B"

! class="vsToggleElement" colspan="5" | Declension of <i class="Latn+mention" lang="sv">berg</i>&nbsp;


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! rowspan="2" style="min-width%3A+12em%3B" |


! colspan="2" | Singular


! colspan="2" | Plural


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! style="min-width%3A+12em%3B" | Indefinite


! style="min-width%3A+12em%3B" | Definite


! style="min-width%3A+12em%3B" | Indefinite


! style="min-width%3A+12em%3B" | Definite


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Nominative


| <span class="Latn" lang="sv">[[berg#Swedish|berg]]</span>


| <span class="Latn" lang="sv">[[berget#Swedish|berget]]</span>


| <span class="Latn" lang="sv">[[berg#Swedish|berg]]</span>


| <span class="Latn" lang="sv">[[bergen#Swedish|bergen]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Genitive


| <span class="Latn" lang="sv">[[bergs#Swedish|bergs]]</span>


| <span class="Latn" lang="sv">[[bergets#Swedish|bergets]]</span>


| <span class="Latn" lang="sv">[[bergs#Swedish|bergs]]</span>


| <span class="Latn" lang="sv">[[bergens#Swedish|bergens]]</span>


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
                "form": "berg",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "berget",
                "source": "Declension",
                "tags": [
                  "definite",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "berg",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "bergen",
                "source": "Declension",
                "tags": [
                  "definite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "bergs",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "bergets",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "bergs",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "bergens",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Swedish_verb1(self):
        ret = self.xinfl("kunna", "Swedish", "verb", "Conjugation", """
<div class="NavFrame" style="width%3A+54em%3B" data-toggle-category="inflection">
<div class="NavHead">Conjugation of kunna (irregular)</div>
<div class="NavContent">

{| class="inflection-table" style="width%3A+100%25%3B+line-height%3A+125%25%3B+background-color%3A+%23F9F9F9%3B+text-align%3A+center%3B+border%3A+1px+solid+%23CCCCFF%3B" cellpadding="3" cellspacing="1"

|-

!


! colspan="2" style="width%3A+50%25%3B+background-color%3A%23EFEFEF%3B" | Active


! colspan="2" style="width%3A+50%25%3B+background-color%3A%23EFEFEF%3B" | Passive


|-

! style="background-color%3A%23EFEFEF%3B" | Infinitive


| colspan="2" | <span class="Latn" lang="sv">[[kunna#Swedish|kunna]]</span>


| colspan="2" | &mdash;


|-

! style="background-color%3A%23EFEFEF%3B" | Supine


| colspan="2" | <span class="Latn" lang="sv">[[kunnat#Swedish|kunnat]]</span>


| colspan="2" | &mdash;


|-

! style="background-color%3A%23EFEFEF%3B" | Imperative


| colspan="2" | &mdash;


| colspan="2" | &mdash;


|-

! style="background-color%3A%23EFEFEF%3B" | ''Imper. plural''<sup>1</sup>


| colspan="2" | &mdash;


| colspan="2" | &mdash;


|-

!


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Present


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Past


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Present


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Past


|-

! style="background-color%3A%23EFEFEF%3B" | Indicative


| <span class="Latn" lang="sv">[[kan#Swedish|kan]]</span>


| <span class="Latn" lang="sv">[[kunde#Swedish|kunde]]</span>


| &mdash;


| &mdash;


|-

! style="background-color%3A%23EFEFEF%3B" | ''Ind. plural''<sup>1</sup>


| <span class="Latn" lang="sv">[[kunna#Swedish|kunna]]</span>


| <span class="Latn" lang="sv">[[kunde#Swedish|kunde]]</span>


| &mdash;


| &mdash;


|-

! style="background-color%3A%23EFEFEF%3B" | ''Subjunctive''<sup>2</sup>


| <span class="Latn" lang="sv">[[kunne#Swedish|kunne]]</span>


| <span class="Latn" lang="sv">[[kunde#Swedish|kunde]]</span>


| &mdash;


| &mdash;


|-

!


! colspan="4" style="width%3A+100%25%3B+background-color%3A%23EFEFEF%3B" | Participles


|-

! style="background-color%3A%23EFEFEF%3B" | Present&nbsp;participle


| colspan="4" | <span class="Latn" lang="sv">[[kunnande#Swedish|kunnande]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | Past&nbsp;participle


| colspan="4" | &mdash;


|-

| colspan="5" style="text-align%3A+left%3B" | <small><sup>1</sup> Archaic. <sup>2</sup> Dated. See [[Appendix:Swedish verbs#Dated and archaic forms|the appendix on Swedish verbs]].</small>


|}
</div></div>[[Category:Swedish irregular verbs|KUNNA]]
""")
        expected = {
            "forms": [
              {
                "form": "irregular",
                "source": "Conjugation",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "kunna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['infinitive', 'passive']},
              {
                "form": "kunnat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "supine"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['passive', 'supine']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['active', 'imperative']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['imperative', 'passive']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['active', 'archaic', 'imperative', 'plural']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['archaic', 'imperative', 'passive', 'plural']},
              {
                "form": "kan",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "present"
                ]
              },
              {
                "form": "kunde",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "past"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['indicative', 'passive', 'present']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['indicative', 'passive', 'past']},
              {
                "form": "kunna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "archaic",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "kunde",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "archaic",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['archaic', 'indicative', 'passive', 'plural', 'present']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['archaic', 'indicative', 'passive', 'past', 'plural']},
              {
                "form": "kunne",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dated",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "kunde",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dated",
                  "past",
                  "subjunctive"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['dated', 'passive', 'present', 'subjunctive']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['dated', 'passive', 'past', 'subjunctive']},
              {
                "form": "kunnande",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['participle', 'past']}
            ],
        }
        self.assertEqual(expected, ret)

    def test_Swedish_verb2(self):
        ret = self.xinfl("simma", "Swedish", "verb", "Conjugation", """
<div class="NavFrame" style="width%3A+54em%3B" data-toggle-category="inflection">
<div class="NavHead">Conjugation of simma (weak)</div>
<div class="NavContent">

{| class="inflection-table" style="width%3A+100%25%3B+line-height%3A+125%25%3B+background-color%3A+%23F9F9F9%3B+text-align%3A+center%3B+border%3A+1px+solid+%23CCCCFF%3B" cellpadding="3" cellspacing="1"

|-

!


! colspan="2" style="width%3A+50%25%3B+background-color%3A%23EFEFEF%3B" | Active


! colspan="2" style="width%3A+50%25%3B+background-color%3A%23EFEFEF%3B" | Passive


|-

! style="background-color%3A%23EFEFEF%3B" | Infinitive


| colspan="2" | <span class="Latn" lang="sv">[[simma#Swedish|simma]]</span>


| colspan="2" | <span class="Latn" lang="sv">[[simmas#Swedish|simmas]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | Supine


| colspan="2" | <span class="Latn" lang="sv">[[simmat#Swedish|simmat]]</span>


| colspan="2" | <span class="Latn" lang="sv">[[simmats#Swedish|simmats]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | Imperative


| colspan="2" | <span class="Latn" lang="sv">[[simma#Swedish|simma]]</span>


| colspan="2" | &mdash;


|-

! style="background-color%3A%23EFEFEF%3B" | ''Imper. plural''<sup>1</sup>


| colspan="2" | <span class="Latn" lang="sv">[[simmen#Swedish|simmen]]</span>


| colspan="2" | &mdash;


|-

!


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Present


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Past


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Present


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Past


|-

! style="background-color%3A%23EFEFEF%3B" | Indicative


| <span class="Latn" lang="sv">[[simmar#Swedish|simmar]]</span>


| <span class="Latn" lang="sv">[[simmade#Swedish|simmade]]</span>


| <span class="Latn" lang="sv">[[simmas#Swedish|simmas]]</span>


| <span class="Latn" lang="sv">[[simmades#Swedish|simmades]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | ''Ind. plural''<sup>1</sup>


| <span class="Latn" lang="sv">[[simma#Swedish|simma]]</span>


| <span class="Latn" lang="sv">[[simmade#Swedish|simmade]]</span>


| <span class="Latn" lang="sv">[[simmas#Swedish|simmas]]</span>


| <span class="Latn" lang="sv">[[simmades#Swedish|simmades]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | ''Subjunctive''<sup>2</sup>


| <span class="Latn" lang="sv">[[simme#Swedish|simme]]</span>


| <span class="Latn" lang="sv">[[simmade#Swedish|simmade]]</span>


| <span class="Latn" lang="sv">[[simmes#Swedish|simmes]]</span>


| <span class="Latn" lang="sv">[[simmades#Swedish|simmades]]</span>


|-

!


! colspan="4" style="width%3A+100%25%3B+background-color%3A%23EFEFEF%3B" | Participles


|-

! style="background-color%3A%23EFEFEF%3B" | Present&nbsp;participle


| colspan="4" | <span class="Latn" lang="sv">[[simmande#Swedish|simmande]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | Past&nbsp;participle


| colspan="4" | <span class="Latn" lang="sv">[[simmad#Swedish|simmad]]</span>


|-

| colspan="5" style="text-align%3A+left%3B" | <small><sup>1</sup> Archaic. <sup>2</sup> Dated. See [[Appendix:Swedish verbs#Dated and archaic forms|the appendix on Swedish verbs]].</small>


|}
</div></div>[[Category:Swedish weak verbs|SIMMA]]
<div class="NavFrame" style="width%3A+54em%3B" data-toggle-category="inflection">
<div class="NavHead">Conjugation of simma (class 3 strong)</div>
<div class="NavContent">

{| class="inflection-table" style="width%3A+100%25%3B+line-height%3A+125%25%3B+background-color%3A+%23F9F9F9%3B+text-align%3A+center%3B+border%3A+1px+solid+%23CCCCFF%3B" cellpadding="3" cellspacing="1"

|-

!


! colspan="2" style="width%3A+50%25%3B+background-color%3A%23EFEFEF%3B" | Active


! colspan="2" style="width%3A+50%25%3B+background-color%3A%23EFEFEF%3B" | Passive


|-

! style="background-color%3A%23EFEFEF%3B" | Infinitive


| colspan="2" | <span class="Latn" lang="sv">[[simma#Swedish|simma]]</span>


| colspan="2" | <span class="Latn" lang="sv">[[simmas#Swedish|simmas]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | Supine


| colspan="2" | <span class="Latn" lang="sv">[[summit#Swedish|summit]]</span>


| colspan="2" | <span class="Latn" lang="sv">[[summits#Swedish|summits]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | Imperative


| colspan="2" | <span class="Latn" lang="sv">[[sim#Swedish|sim]]</span>


| colspan="2" | &mdash;


|-

! style="background-color%3A%23EFEFEF%3B" | ''Imper. plural''<sup>1</sup>


| colspan="2" | <span class="Latn" lang="sv">[[simmen#Swedish|simmen]]</span>


| colspan="2" | &mdash;


|-

!


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Present


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Past


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Present


! style="width%3A+25%25%3B+background-color%3A%23EFEFEF%3B" | Past


|-

! style="background-color%3A%23EFEFEF%3B" | Indicative


| <span class="Latn" lang="sv">[[simmer#Swedish|simmer]]</span>


| <span class="Latn" lang="sv">[[sam#Swedish|sam]]</span>


| <span class="Latn" lang="sv">[[sims#Swedish|sims]]</span>, <span class="Latn" lang="sv">[[simmes#Swedish|simmes]]</span>


| <span class="Latn" lang="sv">[[sams#Swedish|sams]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | ''Ind. plural''<sup>1</sup>


| <span class="Latn" lang="sv">[[simma#Swedish|simma]]</span>


| <span class="Latn" lang="sv">[[summo#Swedish|summo]]</span>


| <span class="Latn" lang="sv">[[simmas#Swedish|simmas]]</span>


| <span class="Latn" lang="sv">[[summos#Swedish|summos]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | ''Subjunctive''<sup>2</sup>


| <span class="Latn" lang="sv">[[simme#Swedish|simme]]</span>


| <span class="Latn" lang="sv">[[summe#Swedish|summe]]</span>


| <span class="Latn" lang="sv">[[simmes#Swedish|simmes]]</span>


| <span class="Latn" lang="sv">[[summes#Swedish|summes]]</span>


|-

!


! colspan="4" style="width%3A+100%25%3B+background-color%3A%23EFEFEF%3B" | Participles


|-

! style="background-color%3A%23EFEFEF%3B" | Present&nbsp;participle


| colspan="4" | <span class="Latn" lang="sv">[[simmande#Swedish|simmande]]</span>


|-

! style="background-color%3A%23EFEFEF%3B" | Past&nbsp;participle


| colspan="4" | <span class="Latn" lang="sv">[[summen#Swedish|summen]]</span>


|-

| colspan="5" style="text-align%3A+left%3B" | <small><sup>1</sup> Archaic. <sup>2</sup> Dated. See [[Appendix:Swedish verbs#Dated and archaic forms|the appendix on Swedish verbs]].</small>


|}
</div></div>[[Category:Swedish strong verbs|SIMMA]][[Category:Swedish class 3 strong verbs|SIMMA]]
""")
        expected = {
            "forms": [
              {
                "form": "weak",
                "source": "Conjugation",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "simma",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive"
                ]
              },
              {
                "form": "simmas",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "passive"
                ]
              },
              {
                "form": "simmat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "supine"
                ]
              },
              {
                "form": "simmats",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "supine"
                ]
              },
              {
                "form": "simma",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperative"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['imperative', 'passive']},
              {
                "form": "simmen",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "archaic",
                  "imperative",
                  "plural"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['archaic', 'imperative', 'passive', 'plural']},
              {
                "form": "simmar",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "present"
                ]
              },
              {
                "form": "simmade",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "past"
                ]
              },
              {
                "form": "simmas",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "simmades",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "past"
                ]
              },
              {
                "form": "simma",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "archaic",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "simmade",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "archaic",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "simmas",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "passive",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "simmades",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "passive",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "simme",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dated",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "simmade",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dated",
                  "past",
                  "subjunctive"
                ]
              },
              {
                "form": "simmes",
                "source": "Conjugation",
                "tags": [
                  "dated",
                  "passive",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "simmades",
                "source": "Conjugation",
                "tags": [
                  "dated",
                  "passive",
                  "past",
                  "subjunctive"
                ]
              },
              {
                "form": "simmande",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "simmad",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
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
                "form": "3 strong",
                "source": "Conjugation",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "simma",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "infinitive"
                ]
              },
              {
                "form": "simmas",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "passive"
                ]
              },
              {
                "form": "summit",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "supine"
                ]
              },
              {
                "form": "summits",
                "source": "Conjugation",
                "tags": [
                  "passive",
                  "supine"
                ]
              },
              {
                "form": "sim",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperative"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['imperative', 'passive']},
              {'form': 'simmen',
               'source': 'Conjugation',
               'tags': ['active', 'archaic', 'imperative', 'plural']},
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['archaic', 'imperative', 'passive', 'plural']},
              {
                "form": "simmer",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "present"
                ]
              },
              {
                "form": "sam",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "past"
                ]
              },
              {
                "form": "sims",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "simmes",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "sams",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "passive",
                  "past"
                ]
              },
              {'form': 'simma',
               'source': 'Conjugation',
               'tags': ['active', 'archaic', 'indicative', 'plural', 'present']},
              {
                "form": "summo",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "archaic",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {'form': 'simmas',
               'source': 'Conjugation',
               'tags': ['archaic', 'indicative', 'passive', 'plural', 'present']},
             {
                "form": "summos",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "passive",
                  "past",
                  "plural"
                ]
              },
              {'form': 'simme',
               'source': 'Conjugation',
               'tags': ['active', 'dated', 'present', 'subjunctive']},
              {
                "form": "summe",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dated",
                  "past",
                  "subjunctive"
                ]
              },
              {'form': 'simmes',
               'source': 'Conjugation',
               'tags': ['dated', 'passive', 'present', 'subjunctive']},
              {
                "form": "summes",
                "source": "Conjugation",
                "tags": [
                  "dated",
                  "passive",
                  "past",
                  "subjunctive"
                ]
              },
              {'form': 'simmande',
               'source': 'Conjugation',
               'tags': ['participle', 'present']},
              {
                "form": "summen",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Swedish_adj1(self):
        ret = self.xinfl("vacker", "Swedish", "adj", "Declension", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="border%3A+solid+1px+%23CCCCFF%3B+text-align%3Aleft%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23CCCCFF%3B+vertical-align%3A+top%3B"

! class="vsToggleElement" colspan="4" | Inflection of <i class="Latn+mention" lang="sv">vacker</i>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! style="min-width%3A+12em%3B" | Indefinite


! style="min-width%3A+12em%3B" | Positive


! style="min-width%3A+12em%3B" | Comparative


! style="min-width%3A+12em%3B" | Superlative<sup>2</sup>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Common singular


| <span class="Latn" lang="sv">[[vacker#Swedish|vacker]]</span>


| <span class="Latn" lang="sv">[[vackrare#Swedish|vackrare]]</span>


| <span class="Latn" lang="sv">[[vackrast#Swedish|vackrast]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Neuter singular


| <span class="Latn" lang="sv">[[vackert#Swedish|vackert]]</span>


| <span class="Latn" lang="sv">[[vackrare#Swedish|vackrare]]</span>


| <span class="Latn" lang="sv">[[vackrast#Swedish|vackrast]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Plural


| <span class="Latn" lang="sv">[[vackra#Swedish|vackra]]</span>


| <span class="Latn" lang="sv">[[vackrare#Swedish|vackrare]]</span>


| <span class="Latn" lang="sv">[[vackrast#Swedish|vackrast]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Masculine plural<sup>3</sup>


| <span class="Latn" lang="sv">[[vackre#Swedish|vackre]]</span>


| <span class="Latn" lang="sv">[[vackrare#Swedish|vackrare]]</span>


| <span class="Latn" lang="sv">[[vackrast#Swedish|vackrast]]</span>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! Definite


! Positive


! Comparative


! Superlative


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Masculine singular<sup>1</sup>


| <span class="Latn" lang="sv">[[vackre#Swedish|vackre]]</span>


| <span class="Latn" lang="sv">[[vackrare#Swedish|vackrare]]</span>


| <span class="Latn" lang="sv">[[vackraste#Swedish|vackraste]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | All


| <span class="Latn" lang="sv">[[vackra#Swedish|vackra]]</span>


| <span class="Latn" lang="sv">[[vackrare#Swedish|vackrare]]</span>


| <span class="Latn" lang="sv">[[vackraste#Swedish|vackraste]]</span>


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

| style="font-size%3A+smaller%3B" colspan="4" | 1) Only used, optionally, to refer to things whose natural gender is masculine.<br>2) The indefinite superlative forms are only used in the predicative.<br>3) Dated or archaic


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
                "form": "vacker",
                "source": "Declension",
                "tags": [
                  "common-gender",
                  "indefinite",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "vackrare",
                "source": "Declension",
                "tags": [
                  "common-gender",
                  "comparative",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "vackrast",
                "source": "Declension",
                "tags": [
                  "common-gender",
                  "indefinite",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "vackert",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "neuter",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "vackrare",
                "source": "Declension",
                "tags": [
                  "comparative",
                  "indefinite",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "vackrast",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "neuter",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "vackra",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "vackrare",
                "source": "Declension",
                "tags": [
                  "comparative",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "vackrast",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "vackre",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "masculine",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "vackrare",
                "source": "Declension",
                "tags": [
                  "comparative",
                  "indefinite",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "vackrast",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "masculine",
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "vackre",
                "source": "Declension",
                "tags": [
                  "definite",
                  "masculine",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "vackrare",
                "source": "Declension",
                "tags": [
                  "comparative",
                  "definite",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "vackraste",
                "source": "Declension",
                "tags": [
                  "definite",
                  "masculine",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "vackra",
                "source": "Declension",
                "tags": [
                  "definite",
                  "positive"
                ]
              },
              {
                "form": "vackrare",
                "source": "Declension",
                "tags": [
                  "comparative",
                  "definite"
                ]
              },
              {
                "form": "vackraste",
                "source": "Declension",
                "tags": [
                  "definite",
                  "superlative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Swedish_noun2(self):
        ret = self.xinfl("mos", "Swedish", "noun", "Declension", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="border%3A+solid+1px+%23CCCCFF%3B+text-align%3Aleft%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23CCCCFF%3B+vertical-align%3Atop%3B"

! class="vsToggleElement" colspan="5" | Declension of <i class="Latn+mention" lang="sv">[[mos#Swedish|mos]]</i>&nbsp;


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! rowspan="2" style="min-width%3A+12em%3B" |


! colspan="2" | Uncountable


! colspan="2" |


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! style="min-width%3A+12em%3B" | Indefinite


! style="min-width%3A+12em%3B" | Definite


! style="min-width%3A+12em%3B" |


! style="min-width%3A+12em%3B" |


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Nominative


| <span class="Latn+form-of+lang-sv+indef%7Cnom%7Cs-form-of+++++++" lang="sv">[[mos#Swedish|mos]]</span>


| <span class="Latn+form-of+lang-sv+def%7Cnom%7Cs-form-of+++++++" lang="sv">[[moset#Swedish|moset]]</span>


| &mdash;


| &mdash;


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Genitive


| <span class="Latn+form-of+lang-sv+indef%7Cgen%7Cs-form-of+++++++" lang="sv">[[mos#Swedish|mos]]</span>


| <span class="Latn+form-of+lang-sv+def%7Cgen%7Cs-form-of+++++++" lang="sv">[[mosets#Swedish|mosets]]</span>


| &mdash;


| &mdash;


|}
[[Category:Swedish nouns]]
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
                "form": "mos",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "nominative",
                  "uncountable"
                ]
              },
              {
                "form": "moset",
                "source": "Declension",
                "tags": [
                  "definite",
                  "nominative",
                  "uncountable"
                ]
              },
              {
                "form": "mos",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "uncountable"
                ]
              },
              {
                "form": "mosets",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "uncountable"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

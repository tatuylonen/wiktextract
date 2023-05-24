# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
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

    def test_Czech_verb1(self):
        ret = self.xinfl("myslet", "Czech", "verb", "Conjugation", """
<div style="width%3A+44em%3B">
<div class="NavFrame+inflection-table-verb">
<div class="NavHead">Conjugation</div>
<div class="NavContent" style="text-align%3A+left%3B">

{| class="wikitable" style="width%3A+43em%3B"

|- 

! '''Present forms'''

! colspan="2" |indicative 

! colspan="2" |imperative


|- 

! 

!singular

!plural

!singular

!plural


|- 

! style="width%3A+10em%3B" |1st person


| style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[myslím#Czech|myslím]]</span>

| style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[myslíme#Czech|myslíme]]</span> 

| style="width%3A+7em%3B" | &mdash; 

| style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[mysleme#Czech|mysleme]]</span>


|- 

!2nd person 


| <span class="Latn" lang="cs">[[myslíš#Czech|myslíš]]</span> 

| <span class="Latn" lang="cs">[[myslíte#Czech|myslíte]]</span> 

| <span class="Latn" lang="cs">[[mysli#Czech|mysli]]</span> 

| <span class="Latn" lang="cs">[[myslete#Czech|myslete]]</span>


|- 

!3rd person 


| <span class="Latn" lang="cs">[[myslí#Czech|myslí]]</span> 

| <span class="Latn" lang="cs">[[myslí#Czech|myslí]]</span>, <span class="Latn" lang="cs">[[myslejí#Czech|myslejí]]</span> 

| &mdash; 

| &mdash;


|}



{| 
 class="wikitable"
<td>The future tense: a combination of a future form of <i class="Latn+mention" lang="cs">[[být#Czech|být]]</i> + infinitive ''myslet''.</td>

|}



{| class="wikitable" style="width%3A+43em%3B"

|- 

! '''Participles'''

! colspan="2" |Past participles

! colspan="2" |Passive participles


|- 

! 

!singular 

!plural 

!singular 

!plural


|- 

! style="width%3A+10em%3B" |masculine animate 


| rowspan="2" style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[myslel#Czech|myslel]]</span>, <span class="Latn" lang="cs">[[myslil#Czech|myslil]]</span> 

| style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[mysleli#Czech|mysleli]]</span>, <span class="Latn" lang="cs">[[myslili#Czech|myslili]]</span>

| rowspan="2" style="width%3A+7em%3B" |  <span class="Latn" lang="cs">[[myšlen#Czech|myšlen]]</span>  

| style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[myšleni#Czech|myšleni]]</span>


|- 

!masculine inanimate 


| rowspan="2" style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[myslely#Czech|myslely]]</span>, <span class="Latn" lang="cs">[[myslily#Czech|myslily]]</span> 

| rowspan="2" style="width%3A+7em%3B" |<span class="Latn" lang="cs">[[myšleny#Czech|myšleny]]</span>


|- 

!feminine


|<span class="Latn" lang="cs">[[myslela#Czech|myslela]]</span>, <span class="Latn" lang="cs">[[myslila#Czech|myslila]]</span> 

|<span class="Latn" lang="cs">[[myšlena#Czech|myšlena]]</span>


|- 

!neuter


|<span class="Latn" lang="cs">[[myslelo#Czech|myslelo]]</span>, <span class="Latn" lang="cs">[[myslilo#Czech|myslilo]]</span> 

| <span class="Latn" lang="cs">[[myslela#Czech|myslela]]</span>, <span class="Latn" lang="cs">[[myslila#Czech|myslila]]</span> 

| <span class="Latn" lang="cs">[[myšleno#Czech|myšleno]]</span> 

|<span class="Latn" lang="cs">[[myšlena#Czech|myšlena]]</span>


|}



{| class="wikitable"

|- 

! '''Transgressives'''

!present 

!past


|- 

! masculine singular


| style="width%3A+7em%3B" | <span class="Latn" lang="cs">[[mysle#Czech|mysle]]</span>, <span class="Latn" lang="cs">[[mysleje#Czech|mysleje]]</span>  

| style="width%3A+7em%3B" | &mdash; 


|- 

!feminine + neuter singular


|<span class="Latn" lang="cs">[[myslíc#Czech|myslíc]]</span>, <span class="Latn" lang="cs">[[myslejíc#Czech|myslejíc]]</span>  

| &mdash;


|- 

!plural


| <span class="Latn" lang="cs">[[myslíce#Czech|myslíce]]</span>, <span class="Latn" lang="cs">[[myslejíce#Czech|myslejíce]]</span>  

| &mdash;


|}

</div></div></div>
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
              "form": "myslím",
              "source": "Conjugation",
              "tags": [
                "first-person",
                "indicative",
                "present",
                "singular"
              ]
            },
            {
              "form": "myslíme",
              "source": "Conjugation",
              "tags": [
                "first-person",
                "indicative",
                "plural",
                "present"
              ]
            },
            {
              "form": "-",
              "source": "Conjugation",
              "tags": [
                "first-person",
                "imperative",
                "present",
                "singular"
              ]
            },
            {
              "form": "mysleme",
              "source": "Conjugation",
              "tags": [
                "first-person",
                "imperative",
                "plural",
                "present"
              ]
            },
            {
              "form": "myslíš",
              "source": "Conjugation",
              "tags": [
                "indicative",
                "present",
                "second-person",
                "singular"
              ]
            },
            {
              "form": "myslíte",
              "source": "Conjugation",
              "tags": [
                "indicative",
                "plural",
                "present",
                "second-person"
              ]
            },
            {
              "form": "mysli",
              "source": "Conjugation",
              "tags": [
                "imperative",
                "present",
                "second-person",
                "singular"
              ]
            },
            {
              "form": "myslete",
              "source": "Conjugation",
              "tags": [
                "imperative",
                "plural",
                "present",
                "second-person"
              ]
            },
            {
              "form": "myslí",
              "source": "Conjugation",
              "tags": [
                "indicative",
                "present",
                "singular",
                "third-person"
              ]
            },
            {
              "form": "myslí",
              "source": "Conjugation",
              "tags": [
                "indicative",
                "plural",
                "present",
                "third-person"
              ]
            },
            {
              "form": "myslejí",
              "source": "Conjugation",
              "tags": [
                "indicative",
                "plural",
                "present",
                "third-person"
              ]
            },
            {
              "form": "-",
              "source": "Conjugation",
              "tags": [
                "imperative",
                "present",
                "singular",
                "third-person"
              ]
            },
            {
              "form": "-",
              "source": "Conjugation",
              "tags": [
                "imperative",
                "plural",
                "present",
                "third-person"
              ]
            },
            {
              "form": "",
              "source": "Conjugation",
              "tags": [
                "table-tags"
              ]
            },
            {
              "form": "myslel",
              "source": "Conjugation",
              "tags": [
                "animate",
                "masculine",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "myslil",
              "source": "Conjugation",
              "tags": [
                "animate",
                "masculine",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "mysleli",
              "source": "Conjugation",
              "tags": [
                "animate",
                "masculine",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myslili",
              "source": "Conjugation",
              "tags": [
                "animate",
                "masculine",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myšlen",
              "source": "Conjugation",
              "tags": [
                "animate",
                "masculine",
                "participle",
                "passive",
                "singular"
              ]
            },
            {
              "form": "myšleni",
              "source": "Conjugation",
              "tags": [
                "animate",
                "masculine",
                "participle",
                "passive",
                "plural"
              ]
            },
            {
              "form": "myslel",
              "source": "Conjugation",
              "tags": [
                "inanimate",
                "masculine",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "myslil",
              "source": "Conjugation",
              "tags": [
                "inanimate",
                "masculine",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "myslely",
              "source": "Conjugation",
              "tags": [
                "inanimate",
                "masculine",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myslily",
              "source": "Conjugation",
              "tags": [
                "inanimate",
                "masculine",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myšlen",
              "source": "Conjugation",
              "tags": [
                "inanimate",
                "masculine",
                "participle",
                "passive",
                "singular"
              ]
            },
            {
              "form": "myšleny",
              "source": "Conjugation",
              "tags": [
                "inanimate",
                "masculine",
                "participle",
                "passive",
                "plural"
              ]
            },
            {
              "form": "myslela",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "myslila",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "myslely",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myslily",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myšlena",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "participle",
                "passive",
                "singular"
              ]
            },
            {
              "form": "myšleny",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "participle",
                "passive",
                "plural"
              ]
            },
            {
              "form": "myslelo",
              "source": "Conjugation",
              "tags": [
                "neuter",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "myslilo",
              "source": "Conjugation",
              "tags": [
                "neuter",
                "participle",
                "past",
                "singular"
              ]
            },
            {
              "form": "myslela",
              "source": "Conjugation",
              "tags": [
                "neuter",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myslila",
              "source": "Conjugation",
              "tags": [
                "neuter",
                "participle",
                "past",
                "plural"
              ]
            },
            {
              "form": "myšleno",
              "source": "Conjugation",
              "tags": [
                "neuter",
                "participle",
                "passive",
                "singular"
              ]
            },
            {
              "form": "myšlena",
              "source": "Conjugation",
              "tags": [
                "neuter",
                "participle",
                "passive",
                "plural"
              ]
            },
            {
              "form": "",
              "source": "Conjugation",
              "tags": [
                "table-tags"
              ]
            },
            {
              "form": "mysle",
              "source": "Conjugation",
              "tags": [
                "masculine",
                "present",
                "singular",
                "transgressive"
              ]
            },
            {
              "form": "mysleje",
              "source": "Conjugation",
              "tags": [
                "masculine",
                "present",
                "singular",
                "transgressive"
              ]
            },
            {
              "form": "-",
              "source": "Conjugation",
              "tags": [
                "masculine",
                "past",
                "singular",
                "transgressive"
              ]
            },
            {
              "form": "myslíc",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "neuter",
                "present",
                "singular",
                "transgressive"
              ]
            },
            {
              "form": "myslejíc",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "neuter",
                "present",
                "singular",
                "transgressive"
              ]
            },
            {
              "form": "-",
              "source": "Conjugation",
              "tags": [
                "feminine",
                "neuter",
                "past",
                "singular",
                "transgressive"
              ]
            },
            {
              "form": "myslíce",
              "source": "Conjugation",
              "tags": [
                "plural",
                "present",
                "transgressive"
              ]
            },
            {
              "form": "myslejíce",
              "source": "Conjugation",
              "tags": [
                "plural",
                "present",
                "transgressive"
              ]
            },
            {
              "form": "-",
              "source": "Conjugation",
              "tags": [
                "past",
                "plural",
                "transgressive"
              ],
            },
          ],
        }
        self.assertEqual(expected, ret)

    def test_Czech_noun1(self):
        ret = self.xinfl("týden", "Czech", "noun", "Declension", """
<div class="NavFrame" style="width%3A30em">
<div class="NavHead">Declension</div>
<div class="NavContent">

{| style="width%3A30em%3B+margin%3A+0%3B" class="wikitable+inflection-table"

|-

! style="width%3A+7em" |


! singular


! plural


|-

! nominative


| <span class="Latn" lang="cs">[[týden#Czech|týden]]</span>


| <span class="Latn" lang="cs">[[týdny#Czech|týdny]]</span>


|-

! genitive


| <span class="Latn" lang="cs">[[týdne#Czech|týdne]]</span>


| <span class="Latn" lang="cs">[[týdnů#Czech|týdnů]]</span>


|-

! dative


| <span class="Latn" lang="cs">[[týdnu#Czech|týdnu]], [[týdni#Czech|týdni]]</span>


| <span class="Latn" lang="cs">[[týdnům#Czech|týdnům]]</span>


|-

! accusative


| <span class="Latn" lang="cs">[[týden#Czech|týden]]</span>


| <span class="Latn" lang="cs">[[týdny#Czech|týdny]]</span>


|-

! vocative


| <span class="Latn" lang="cs">[[týdne#Czech|týdne]], [[týdni#Czech|týdni]]</span>


| <span class="Latn" lang="cs">[[týdny#Czech|týdny]]</span>


|-

! locative


| <span class="Latn" lang="cs">[[týdnu#Czech|týdnu]], [[týdni#Czech|týdni]]</span>


| <span class="Latn" lang="cs">[[týdnech#Czech|týdnech]]</span>


|-

! instrumental


| <span class="Latn" lang="cs">[[týdnem#Czech|týdnem]]</span>


| <span class="Latn" lang="cs">[[týdny#Czech|týdny]]</span>


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
                "form": "týden",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "týdny",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "týdne",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "týdnů",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "týdnu",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "týdni",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "týdnům",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "týden",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "singular"
                ]
              },
              {
                "form": "týdny",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural"
                ]
              },
              {
                "form": "týdne",
                "source": "Declension",
                "tags": [
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "týdni",
                "source": "Declension",
                "tags": [
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "týdny",
                "source": "Declension",
                "tags": [
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "týdnu",
                "source": "Declension",
                "tags": [
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "týdni",
                "source": "Declension",
                "tags": [
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "týdnech",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "týdnem",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "týdny",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Czech_adj1(self):
        ret = self.xinfl("dobrý", "Czech", "adj", "Declension", """
<div class="NavFrame" style="clear%3Aboth%3B+width%3A50em">
<div class="NavHead" align="center">Declension</div>
<div class="NavContent">

{| style="width%3A50em%3B+background%3A%23FFFFFF%3B" class="prettytable+inflection-table"

|-

! style="background%3A%23DEDEDE" colspan="5" |singular


|-

!&nbsp;


!masculine animate


!masculine inanimate


!feminine


!neuter


|-

!nominative


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobrý#Czech|dobrý]]</span>


|<span class="Latn" lang="cs">[[dobrá#Czech|dobrá]]</span>


|<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|-

!genitive


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobrého#Czech|dobrého]]</span>


|<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|<span class="Latn" lang="cs">[[dobrého#Czech|dobrého]]</span>


|-

!dative


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobrému#Czech|dobrému]]</span>


|<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|<span class="Latn" lang="cs">[[dobrému#Czech|dobrému]]</span>


|-

!accusative


|<span class="Latn" lang="cs">[[dobrého#Czech|dobrého]]</span>


|<span class="Latn" lang="cs">[[dobrý#Czech|dobrý]]</span>


|<span class="Latn" lang="cs">[[dobrou#Czech|dobrou]]</span>


|<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|-

!vocative


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobrý#Czech|dobrý]]</span>


|<span class="Latn" lang="cs">[[dobrá#Czech|dobrá]]</span>


|<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|-

!locative


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobrém#Czech|dobrém]]</span>


|<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|<span class="Latn" lang="cs">[[dobrém#Czech|dobrém]]</span>


|-

!instrumental


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobrým#Czech|dobrým]]</span>


|<span class="Latn" lang="cs">[[dobrou#Czech|dobrou]]</span>


|<span class="Latn" lang="cs">[[dobrým#Czech|dobrým]]</span>


|-

! style="background%3A%23DEDEDE" colspan="5" |plural


|-

!&nbsp;


!masculine animate


!masculine inanimate


!feminine


!neuter


|-

!nominative


|<span class="Latn" lang="cs">[[dobří#Czech|dobří]]</span>


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|<span class="Latn" lang="cs">[[dobrá#Czech|dobrá]]</span>


|-

!genitive


| colspan="4" align="center" |<span class="Latn" lang="cs">[[dobrých#Czech|dobrých]]</span>


|-

!dative


| colspan="4" align="center" |<span class="Latn" lang="cs">[[dobrým#Czech|dobrým]]</span>


|-

!accusative


| colspan="3" align="center" |<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|<span class="Latn" lang="cs">[[dobrá#Czech|dobrá]]</span>


|-

!vocative


|<span class="Latn" lang="cs">[[dobří#Czech|dobří]]</span>


| colspan="2" align="center" |<span class="Latn" lang="cs">[[dobré#Czech|dobré]]</span>


|<span class="Latn" lang="cs">[[dobrá#Czech|dobrá]]</span>


|-

!locative


| colspan="4" align="center" |<span class="Latn" lang="cs">[[dobrých#Czech|dobrých]]</span>


|-

!instrumental


| colspan="4" align="center" |<span class="Latn" lang="cs">[[dobrými#Czech|dobrými]]</span>


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
                "form": "dobrý",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "dobrá",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "dobrého",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "dobrého",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "dobrému",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "dobrému",
                "source": "Declension",
                "tags": [
                  "dative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "dobrého",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "animate",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "dobrý",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "inanimate",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "dobrou",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "dobrý",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "dobrá",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "dobrém",
                "source": "Declension",
                "tags": [
                  "locative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "dobrém",
                "source": "Declension",
                "tags": [
                  "locative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "dobrým",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "dobrou",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "dobrým",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "dobří",
                "source": "Declension",
                "tags": [
                  "animate",
                  "masculine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "inanimate",
                  "masculine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "dobrá",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "dobrých",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "dobrým",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "dobrá",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "dobří",
                "source": "Declension",
                "tags": [
                  "animate",
                  "masculine",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "dobré",
                "source": "Declension",
                "tags": [
                  "inanimate",
                  "masculine",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "dobrá",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "dobrých",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "dobrými",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

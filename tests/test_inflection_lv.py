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

    def test_Latvian_verb1(self):
        ret = self.xinfl("saprast", "Latvian", "verb", "Conjugation", """
<div class="NavFrame" style="width%3A470px">
<div class="NavHead" style>conjugation of ''saprast''</div>
<div class="NavContent">


{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! style="background%3A%23BCB2B0" |


! colspan="4" style="background%3A%23BCB2B0" | INDICATIVE <small>([[īstenības]] [[izteiksme]])</small>


! rowspan="2" style="background%3A%23BCB2B0" | IMPERATIVE<br><small>([[pavēles]] [[izteiksme]])</small>


|-

! style="background%3A%23BCB2B0" |


! style="background%3A%23BCB2B0" |


! style="background%3A%23BCB2B0" | Present<br><small>([[tagadne]])</small>


! style="background%3A%23BCB2B0" | Past<br><small>([[pagātne]])</small>


! style="background%3A%23BCB2B0" | Future<br><small>([[nākotne]])</small>


|-

! style="background%3A%23DEDEDE%3B+width%3A60px" | [[first person|1st pers.]] [[singular|sg.]]


! style="background%3A%23DEDEDE%3B+width%3A70px" | <span class="Latn" lang="lv">[[es#Latvian|es]]</span>


| <span class="Latn" lang="lv">[[saprotu#Latvian|saprotu]]</span>


| <span class="Latn" lang="lv">[[sapratu#Latvian|sapratu]]</span>


| <span class="Latn" lang="lv">[[sapratīšu#Latvian|sapratīšu]]</span>


| —


|-

! style="background%3A%23DEDEDE" | [[second person|2nd pers.]] [[singular|sg.]]


! style="background%3A%23DEDEDE" | <span class="Latn" lang="lv">[[tu#Latvian|tu]]</span>


| <span class="Latn" lang="lv">[[saproti#Latvian|saproti]]</span>


| <span class="Latn" lang="lv">[[saprati#Latvian|saprati]]</span>


| <span class="Latn" lang="lv">[[sapratīsi#Latvian|sapratīsi]]</span>


| <span class="Latn" lang="lv">[[saproti#Latvian|saproti]]</span>


|-

! style="background%3A%23DEDEDE" | [[third person|3rd pers.]] [[singular|sg.]]


! style="background%3A%23DEDEDE" | <span class="Latn" lang="lv">[[viņš#Latvian|viņš]]</span>, <span class="Latn" lang="lv">[[viņa#Latvian|viņa]]</span>


| <span class="Latn" lang="lv">[[saprot#Latvian|saprot]]</span>


| <span class="Latn" lang="lv">[[saprata#Latvian|saprata]]</span>


| <span class="Latn" lang="lv">[[sapratīs#Latvian|sapratīs]]</span>


| <span class="Latn" lang="lv">[[lai#Latvian|lai]]</span> <span class="Latn" lang="lv">[[saprot#Latvian|saprot]]</span>


|-

! style="background%3A%23DEDEDE" | [[first person|1st pers.]] [[plural|pl.]]


! style="background%3A%23DEDEDE" | <span class="Latn" lang="lv">[[mēs#Latvian|mēs]]</span>


| <span class="Latn" lang="lv">[[saprotam#Latvian|saprotam]]</span>


| <span class="Latn" lang="lv">[[sapratām#Latvian|sapratām]]</span>


| <span class="Latn" lang="lv">[[sapratīsim#Latvian|sapratīsim]]</span>


| <span class="Latn" lang="lv">[[sapratīsim#Latvian|sapratīsim]]</span>


|-

! style="background%3A%23DEDEDE" | [[second person|2nd pers.]] [[plural|pl.]]


! style="background%3A%23DEDEDE" | <span class="Latn" lang="lv">[[jūs#Latvian|jūs]]</span>


| <span class="Latn" lang="lv">[[saprotat#Latvian|saprotat]]</span>


| <span class="Latn" lang="lv">[[sapratāt#Latvian|sapratāt]]</span>


| <span class="Latn" lang="lv">[[sapratīsiet#Latvian|sapratīsiet]]</span>,<br><span class="Latn" lang="lv">[[sapratīsit#Latvian|sapratīsit]]</span>


| <span class="Latn" lang="lv">[[saprotiet#Latvian|saprotiet]]</span>


|-

! style="background%3A%23DEDEDE" | [[third person|3rd pers.]] [[plural|pl.]]


! style="background%3A%23DEDEDE" | <span class="Latn" lang="lv">[[viņi#Latvian|viņi]]</span>, <span class="Latn" lang="lv">[[viņas#Latvian|viņas]]</span>


| <span class="Latn" lang="lv">[[saprot#Latvian|saprot]]</span>


| <span class="Latn" lang="lv">[[saprata#Latvian|saprata]]</span>


| <span class="Latn" lang="lv">[[sapratīs#Latvian|sapratīs]]</span>


| <span class="Latn" lang="lv">[[lai#Latvian|lai]]</span> <span class="Latn" lang="lv">[[saprot#Latvian|saprot]]</span>


|-

! colspan="6" style="background%3A%23CDCDCD%3Bheight%3A.75em" |


|-

! colspan="3" style="background%3A%23DEDEDE" | RENARRATIVE <small>([[atstāstījuma]] [[izteiksme]])</small>


! colspan="3" style="background%3A%23DEDEDE" | PARTICIPLES <small>([[divdabji]])</small>


|-

! style="background%3A%23DEDEDE" | Present


| colspan="2" | <span class="Latn" lang="lv">[[saprotot#Latvian|saprotot]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Present Active 1 <small>(Adj.)</small>


| <span class="Latn" lang="lv">[[saprotošs#Latvian|saprotošs]]</span>


|-

! style="background%3A%23DEDEDE" | Past


| colspan="2" | <span class="Latn" lang="lv">[[esot#Latvian|esot]]</span> <span class="Latn" lang="lv">[[sapratis#Latvian|sapratis]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Present Active 2 <small>(Adv.)</small>


| <span class="Latn" lang="lv">[[saprazdams#Latvian|saprazdams]]</span>


|-

! style="background%3A%23DEDEDE" | Future


| colspan="2" | <span class="Latn" lang="lv">[[sapratīšot#Latvian|sapratīšot]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Present Active 3 <small>(Adv.)</small>


| <span class="Latn" lang="lv">[[saprotot#Latvian|saprotot]]</span>


|-

! style="background%3A%23DEDEDE" | Imperative


| colspan="2" | <span class="Latn" lang="lv">[[lai#Latvian|lai]]</span> <span class="Latn" lang="lv">[[saprotot#Latvian|saprotot]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Present Active 4 <small>(Obj.)</small>


| <span class="Latn" lang="lv">[[saprotam#Latvian|saprotam]]</span>


|-

! colspan="3" style="background%3A%23DEDEDE" | CONDITIONAL <small>([[vēlējuma]] [[izteiksme]])</small>


! colspan="2" style="background%3A%23DEDEDE" | Past Active


| <span class="Latn" lang="lv">[[sapratis#Latvian|sapratis]]</span>


|-

! style="background%3A%23DEDEDE" | Present


| colspan="2" | <span class="Latn" lang="lv">[[saprastu#Latvian|saprastu]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Present Passive


| <span class="Latn" lang="lv">[[saprotams#Latvian|saprotams]]</span>


|-

! style="background%3A%23DEDEDE" | Past


| colspan="2" | <span class="Latn" lang="lv">[[būtu#Latvian|būtu]]</span> <span class="Latn" lang="lv">[[sapratis#Latvian|sapratis]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Past Passive


| <span class="Latn" lang="lv">[[saprasts#Latvian|saprasts]]</span>


|-

! colspan="3" style="background%3A%23DEDEDE" | DEBITIVE <small>([[vajadzības]] [[izteiksme]])</small>


! colspan="3" style="background%3A%23DEDEDE" | NOMINAL FORMS


|-

! style="background%3A%23DEDEDE" | Indicative


| colspan="2" | (<span class="Latn" lang="lv">[[būt#Latvian|būt]]</span>) <span class="Latn" lang="lv">[[jāsaprot#Latvian|jāsaprot]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Infinitive <small>(nenoteiksme)</small>


| <span class="Latn" lang="lv">[[saprast#Latvian|saprast]]</span>


|-

! style="background%3A%23DEDEDE" | Conjunctive&nbsp;1


| colspan="2" | <span class="Latn" lang="lv">[[esot#Latvian|esot]]</span> <span class="Latn" lang="lv">[[jāsaprot#Latvian|jāsaprot]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Negative Infinitive


| <span class="Latn" lang="lv">[[nesaprast#Latvian|nesaprast]]</span>


|-

! style="background%3A%23DEDEDE" | Conjunctive&nbsp;2


| colspan="2" | <span class="Latn" lang="lv">[[jāsaprotot#Latvian|jāsaprotot]]</span>


! colspan="2" style="background%3A%23DEDEDE" | Verbal noun


| <span class="Latn" lang="lv">[[saprašana#Latvian|saprašana]]</span>


|}
</div></div>[[Category:Latvian first conjugation verbs]][[Category:Latvian first conjugation verbs in -t]][[Category:Latvian a/o/a-s/t type first conjugation verbs]][[Category:Latvian first conjugation verbs in -zt or -st]]
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
                "form": "saprotu",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "sapratu",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "sapratīšu",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person', 'imperative', 'singular']},
              {
                "form": "saproti",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saprati",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sapratīsi",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saproti",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saprot",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saprata",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sapratīs",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "lai saprot",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saprotam",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "sapratām",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "sapratīsim",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "sapratīsim",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "saprotat",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "sapratāt",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "sapratīsiet",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "sapratīsit",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "saprotiet",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "saprot",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "saprata",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "sapratīs",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "lai saprot",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "saprotot",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "renarrative"
                ]
              },
              {
                "form": "saprotošs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "participle",
                  "participle-1",
                  "present"
                ]
              },
              {
                "form": "esot sapratis",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "renarrative"
                ]
              },
              {
                "form": "saprazdams",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "participle",
                  "participle-2",
                  "present"
                ]
              },
              {
                "form": "sapratīšot",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "renarrative"
                ]
              },
              {
                "form": "saprotot",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "participle",
                  "participle-3",
                  "present"
                ]
              },
              {
                "form": "lai saprotot",
                "source": "Conjugation",
                "tags": [
                  "imperative"
                ]
              },
              {
                "form": "saprotam",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle",
                  "participle-4",
                  "present"
                ]
              },
              {
                "form": "sapratis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "saprastu",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "present"
                ]
              },
              {
                "form": "saprotams",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "būtu sapratis",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "past"
                ]
              },
              {
                "form": "saprasts",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive",
                  "past"
                ]
              },
              {
                "form": "jāsaprot",
                "source": "Conjugation",
                "tags": [
                  "debitive",
                  "indicative"
                ]
              },
              {
                "form": "būt jāsaprot",
                "source": "Conjugation",
                "tags": [
                  "debitive",
                  "indicative"
                ]
              },
              {
                "form": "saprast",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "esot jāsaprot",
                "source": "Conjugation",
                "tags": [
                  "conjunctive",
                  "conjunctive-1",
                  "debitive"
                ]
              },
              {
                "form": "nesaprast",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "negative"
                ]
              },
              {
                "form": "jāsaprotot",
                "source": "Conjugation",
                "tags": [
                  "conjunctive",
                  "conjunctive-2",
                  "debitive"
                ]
              },
              {
                "form": "saprašana",
                "source": "Conjugation",
                "tags": [
                  "noun-from-verb"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Latvian_noun1(self):
        ret = self.xinfl("auss", "Latvian", "noun", "Declension", """
<div class="NavFrame" style="width%3A410px">
<div class="NavHead" style>Declension of ''auss''<nowiki /> (6th declension)</div>
<div class="NavContent">

{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! style="width%3A178px%3Bbackground%3A%23DEDEDE" |


! style="background%3A%23DEDEDE" | singular <small>([[vienskaitlis]])</small>


! style="background%3A%23DEDEDE" | plural <small>([[daudzskaitlis]])</small>


|-

! style="background%3A%23EFEFEF" | nominative <small>([[nominatīvs]])</small>


| <span class="Latn+form-of+lang-lv+nom%7Cs-form-of+++++++" lang="lv">[[auss#Latvian|auss]]</span>


| <span class="Latn+form-of+lang-lv+nom%7Cp-form-of+++++++" lang="lv">[[ausis#Latvian|ausis]]</span>


|-

! style="background%3A%23EFEFEF" | accusative <small>([[akuzatīvs]])</small>


| <span class="Latn+form-of+lang-lv+acc%7Cs-form-of+++++++" lang="lv">[[ausi#Latvian|ausi]]</span>


| <span class="Latn+form-of+lang-lv+acc%7Cp-form-of+++++++" lang="lv">[[ausis#Latvian|ausis]]</span>


|-

! style="background%3A%23EFEFEF" | genitive <small>([[ģenitīvs]])</small>


| <span class="Latn+form-of+lang-lv+gen%7Cs-form-of+++++++" lang="lv">[[auss#Latvian|auss]]</span>


| <span class="Latn+form-of+lang-lv+gen%7Cp-form-of+++++++" lang="lv">[[ausu#Latvian|ausu]]</span>


|-

! style="background%3A%23EFEFEF" | dative <small>([[datīvs]])</small>


| <span class="Latn+form-of+lang-lv+dat%7Cs-form-of+++++++" lang="lv">[[ausij#Latvian|ausij]]</span>


| <span class="Latn+form-of+lang-lv+dat%7Cp-form-of+++++++" lang="lv">[[ausīm#Latvian|ausīm]]</span>


|-

! style="background%3A%23EFEFEF" | instrumental <small>([[instrumentālis]])</small>


| <span class="Latn+form-of+lang-lv+ins%7Cs-form-of+++++++" lang="lv">[[ausi#Latvian|ausi]]</span>


| <span class="Latn+form-of+lang-lv+ins%7Cp-form-of+++++++" lang="lv">[[ausīm#Latvian|ausīm]]</span>


|-

! style="background%3A%23EFEFEF" | locative <small>([[lokatīvs]])</small>


| <span class="Latn+form-of+lang-lv+loc%7Cs-form-of+++++++" lang="lv">[[ausī#Latvian|ausī]]</span>


| <span class="Latn+form-of+lang-lv+loc%7Cp-form-of+++++++" lang="lv">[[ausīs#Latvian|ausīs]]</span>


|-

! style="background%3A%23EFEFEF" | vocative <small>([[vokatīvs]])</small>


| <span class="Latn+form-of+lang-lv+voc%7Cs-form-of+++++++" lang="lv">[[auss#Latvian|auss]]</span>


| <span class="Latn+form-of+lang-lv+voc%7Cp-form-of+++++++" lang="lv">[[ausis#Latvian|ausis]]</span>


|}
</div></div>[[Category:Latvian sixth declension&#32;&#32;nouns]][[Category:Latvian&#32;&#32;noun forms]][[Category:Latvian non-alternating sixth declension&#32;&#32;nouns]]
""")
        expected = {
            "forms": [
              {
                "form": "declension-6",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "6th declension",
                "source": "Declension",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "auss",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "ausis",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "ausi",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "singular"
                ]
              },
              {
                "form": "ausis",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural"
                ]
              },
              {
                "form": "auss",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "ausu",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "ausij",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "ausīm",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "ausi",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "ausīm",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "ausī",
                "source": "Declension",
                "tags": [
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "ausīs",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "auss",
                "source": "Declension",
                "tags": [
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "ausis",
                "source": "Declension",
                "tags": [
                  "plural",
                  "vocative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Latvian_adj1(self):
        ret = self.xinfl("zils", "Latvian", "adj", "Declension", """
<div class="NavFrame" style="width%3A508px">
<div class="NavHead" style>indefinite declension <small>([[nenoteiktā]] [[galotne]])</small> of ''zils''</div>
<div class="NavContent">


{| border="1" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! rowspan="2" style="background%3A%23DEDEDE%3Bwidth%3A195px" |


! colspan="2" style="background%3A%23DEDEDE%3Bwidth%3A156px" | masculine <small>([[vīriešu]] [[dzimte]])</small>


! rowspan="9" style="background%3A%23DEDEDE%3Bwidth%3A1px" |


! colspan="2" style="background%3A%23DEDEDE%3Bwidth%3A156px" | feminine <small>([[sieviešu]] [[dzimte]])</small>


|-

! style="background%3A%23DEDEDE%3Bwidth%3A77px" | singular <br><small>([[vienskaitlis]])</small>


! style="background%3A%23DEDEDE%3Bwidth%3A79px" | plural <br><small>([[daudzskaitlis]])</small>


! style="background%3A%23DEDEDE%3Bwidth%3A77px" | singular <br><small>([[vienskaitlis]])</small>


! style="background%3A%23DEDEDE%3Bwidth%3A79px" | plural <br><small>([[daudzskaitlis]])</small>


|-

! style="background%3A%23EFEFEF" | nominative <small>([[nominatīvs]])</small>


| <span class="Latn" lang="lv">[[zils#Latvian|zils]]</span>


| <span class="Latn" lang="lv">[[zili#Latvian|zili]]</span>


| <span class="Latn" lang="lv">[[zila#Latvian|zila]]</span>


| <span class="Latn" lang="lv">[[zilas#Latvian|zilas]]</span>


|-

! style="background%3A%23EFEFEF" | accusative <small>([[akuzatīvs]])</small>


| <span class="Latn" lang="lv">[[zilu#Latvian|zilu]]</span>


| <span class="Latn" lang="lv">[[zilus#Latvian|zilus]]</span>


| <span class="Latn" lang="lv">[[zilu#Latvian|zilu]]</span>


| <span class="Latn" lang="lv">[[zilas#Latvian|zilas]]</span>


|-

! style="background%3A%23EFEFEF" | genitive <small>([[ģenitīvs]])</small>


| <span class="Latn" lang="lv">[[zila#Latvian|zila]]</span>


| <span class="Latn" lang="lv">[[zilu#Latvian|zilu]]</span>


| <span class="Latn" lang="lv">[[zilas#Latvian|zilas]]</span>


| <span class="Latn" lang="lv">[[zilu#Latvian|zilu]]</span>


|-

! style="background%3A%23EFEFEF" | dative <small>([[datīvs]])</small>


| <span class="Latn" lang="lv">[[zilam#Latvian|zilam]]</span>


| <span class="Latn" lang="lv">[[ziliem#Latvian|ziliem]]</span>


| <span class="Latn" lang="lv">[[zilai#Latvian|zilai]]</span>


| <span class="Latn" lang="lv">[[zilām#Latvian|zilām]]</span>


|-

! style="background%3A%23EFEFEF" | instrumental <small>([[instrumentālis]])</small>


| <span class="Latn" lang="lv">[[zilu#Latvian|zilu]]</span>


| <span class="Latn" lang="lv">[[ziliem#Latvian|ziliem]]</span>


| <span class="Latn" lang="lv">[[zilu#Latvian|zilu]]</span>


| <span class="Latn" lang="lv">[[zilām#Latvian|zilām]]</span>


|-

! style="background%3A%23EFEFEF" | locative <small>([[lokatīvs]])</small>


| <span class="Latn" lang="lv">[[zilā#Latvian|zilā]]</span>


| <span class="Latn" lang="lv">[[zilos#Latvian|zilos]]</span>


| <span class="Latn" lang="lv">[[zilā#Latvian|zilā]]</span>


| <span class="Latn" lang="lv">[[zilās#Latvian|zilās]]</span>


|-

! style="background%3A%23EFEFEF" | vocative <small>([[vokatīvs]])</small>


| —


| —


| —


| —


|-

! colspan="10" style="background%3A%23DEDEDE%3Bheight%3A1em" |


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
                "form": "zils",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "masculine",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "zili",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "masculine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "zila",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "zilas",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "zilu",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "indefinite",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "zilus",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "indefinite",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "zilu",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "zilas",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "zila",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "zilu",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "zilas",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "zilu",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "zilam",
                "source": "Declension",
                "tags": [
                  "dative",
                  "indefinite",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "ziliem",
                "source": "Declension",
                "tags": [
                  "dative",
                  "indefinite",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "zilai",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "zilām",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "zilu",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "instrumental",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "ziliem",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "instrumental",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "zilu",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "zilām",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "zilā",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "locative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "zilos",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "locative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "zilā",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "zilās",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "locative",
                  "plural"
                ]
              },
              {'form': '-',
               'source': 'Declension',
               'tags': ['indefinite', 'masculine', 'singular', 'vocative']},
              {'form': '-',
               'source': 'Declension',
               'tags': ['indefinite', 'masculine', 'plural', 'vocative']},
              {'form': '-',
               'source': 'Declension',
               'tags': ['feminine', 'indefinite', 'singular', 'vocative']},
              {'form': '-',
               'source': 'Declension',
               'tags': ['feminine', 'indefinite', 'plural', 'vocative']}
              ],
        }
        self.assertEqual(expected, ret)

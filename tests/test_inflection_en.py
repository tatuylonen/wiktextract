# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

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

    def test_English_verb1(self):
        ret = self.xinfl("wander", "English", "verb", "Conjugation", """
<div class="NavFrame" style="width%3A+42em%3B">
<div class="NavHead">Conjugation of ''wander''</div>
<div class="NavContent">

{| style="width%3A100%25%3B+margin%3A+0px%3B" class="wikitable+inflection-table"

|-

! [[Appendix:Glossary#infinitive|infinitive]]


| colspan="3" | (to) wander


|-

|


! style="width%3A+50%25%3B+white-space%3A+nowrap%3B" | [[Appendix:Glossary#present tense|present tense]]


! style="width%3A+50%25%3B+white-space%3A+nowrap%3B" | [[Appendix:Glossary#past tense|past tense]]


|-

! style="white-space%3A+nowrap%3B" | [[Appendix:Glossary#first-person|1st-person]] [[Appendix:Glossary#singular|singular]]


| wander


| <span class="Latn+form-of+lang-en+past%7Cand%7Cpast%7Cptcp-form-of+++++++" lang="en">[[wandered#English|wandered]]</span>


|-

! style="white-space%3A+nowrap%3B" | [[Appendix:Glossary#second-person|2nd-person]] [[Appendix:Glossary#singular|singular]]


| wander, <span class="Latn+form-of+lang-en+archaic%7C2%7Cs%7Cpres-form-of+++++++" lang="en">[[wanderest#English|wanderest]]</span><sup font-size:large>*</sup>


| <span class="Latn+form-of+lang-en+past%7Cand%7Cpast%7Cptcp-form-of+++++++" lang="en">[[wandered#English|wandered]]</span>, <span class="Latn+form-of+lang-en+archaic%7C2%7Cs%7Cpast-form-of+++++++" lang="en">[[wanderedst#English|wanderedst]]</span><sup font-size:large>*</sup>


|-

! style="white-space%3A+nowrap%3B" | [[Appendix:Glossary#third-person|3rd-person]] [[Appendix:Glossary#singular|singular]]


| <span class="Latn+form-of+lang-en+3%7Cs%7Cpres-form-of+++++++" lang="en">[[wanders#English|wanders]]</span>, <span class="Latn+form-of+lang-en+archaic%7C3%7Cs%7Cpres-form-of+++++++" lang="en">[[wandereth#English|wandereth]]</span><sup font-size:large>*</sup>


| rowspan="4" | <span class="Latn+form-of+lang-en+past%7Cand%7Cpast%7Cptcp-form-of+++++++" lang="en">[[wandered#English|wandered]]</span>


|-

! [[Appendix:Glossary#plural|plural]]


| wander


|-

|


|-

! [[Appendix:Glossary#subjunctive|subjunctive]]


| wander


|-

| colspan="3" |


|-

! [[Appendix:Glossary#imperative|imperative]]


| wander


| —


|-

| colspan="3" |


|-

! [[Appendix:Glossary#participle|participle]]s


| <span class="Latn+form-of+lang-en+pres%7Cptcp-form-of+++++++" lang="en">[[wandering#English|wandering]]</span>


| <span class="Latn+form-of+lang-en+past%7Cand%7Cpast%7Cptcp-form-of+++++++" lang="en">[[wandered#English|wandered]]</span>


|}

<div style="width%3A100%25%3Btext-align%3Aleft%3Bbackground%3A%23f7f8fa">
<div style="display%3Ainline-block%3Btext-align%3Aleft%3Bpadding-left%3A1em%3Bpadding-right%3A1em">
<strong><sup font-size:large>*</sup></strong>[[Wiktionary:Glossary#archaic|Archaic]] or [[Wiktionary:Glossary#obsolete|obsolete]].
</div></div></div></div>
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
                "form": "wander",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "wander",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "wandered",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "wander",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wanderest",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wandered",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wanderedst",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wanders",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "wandereth",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "wandered",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "wander",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present"
                ]
              },
              {
                "form": "wandered",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural"
                ]
              },
              {
                "form": "wander",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "wandered",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "subjunctive"
                ]
              },
              {
                "form": "wander",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "past"
                ]
              },
              {
                "form": "wandering",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "wandered",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
            ],
        }
        self.assertEqual(expected, ret)

    def test_English_verb2(self):
        ret = self.xinfl("affect", "English", "verb", "Conjugation", """
<div class="NavFrame" style>
<div class="NavHead" style>conjugation of ''affect''</div>
<div class="NavContent">

{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23fafafa%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! colspan="4" style="background%3A%23d0d0d0" | infinitive


| colspan="8" | [[affect]]


|-

! colspan="4" style="background%3A%23d0d0d0" | present participle


| colspan="8" | [[affecting]]


|-

! colspan="4" style="background%3A%23d0d0d0" | past participle


| colspan="8" | [[affected]]


|-

| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | simple


| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | progressive


| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | perfect


| style="background%3A%23a0ade3" |


! colspan="2" style="background%3A%23a0ade3" | perfect progressive


|-

! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | present


| I affect


| we affect


! rowspan="3" style="background%3A%23d5d5d5" |


| I am affecting


| we are affecting


! rowspan="3" style="background%3A%23d5d5d5" |


| I have affected


| we have affected


! rowspan="3" style="background%3A%23d5d5d5" |


| I have been affecting


| we have been affecting


|-

| you affect


| you affect


| you are affecting


| you are affecting


| you have affected


| you have affected


| you have been affecting


| you have been affecting


|-

| he affects


| they affect


| he is affecting


| they are affecting


| he has affected


| they have affected


| he has been affecting


| they have been affecting


|-

| colspan="12" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | past


| I affected


| we affected


! rowspan="3" style="background%3A%23d5d5d5" |


| I was affecting


| we were affecting


! rowspan="3" style="background%3A%23d5d5d5" |


| I had affected


| we had affected


! rowspan="3" style="background%3A%23d5d5d5" |


| I had been affecting


| we had been affecting


|-

| you affected


| you affected


| you were affecting


| you were affecting


| you had affected


| you had affected


| you had been affecting


| you had been affecting


|-

| he affected


| they affected


| he was affecting


| they were affecting


| he had affected


| they had affected


| he had been affecting


| they had been affecting


|-

| colspan="12" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | future


| I will affect


| we will affect


! rowspan="3" style="background%3A%23d5d5d5" |


| I will be affecting


| we will be affecting


! rowspan="3" style="background%3A%23d5d5d5" |


| I will have affected


| we will have affected


! rowspan="3" style="background%3A%23d5d5d5" |


| I will have been affecting


| we will have been affecting


|-

| you will affect


| you will affect


| you will be affecting


| you will be affecting


| you will have affected


| you will have affected


| you will have been affecting


| you will have been affecting


|-

| he will affect


| they will affect


| he will be affecting


| they will be affecting


| he will have affected


| they will have affected


| he will have been affecting


| they will have been affecting


|-

| colspan="12" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! rowspan="3" style="background%3A%23c0cfe4%3B+width%3A7em" | conditional


| I would affect


| we would affect


! rowspan="3" style="background%3A%23d5d5d5" |


| I would be affecting


| we would be affecting


! rowspan="3" style="background%3A%23d5d5d5" |


| I would have affected


| we would have affected


! rowspan="3" style="background%3A%23d5d5d5" |


| I would have been affecting


| we would have been affecting


|-

| you would affect


| you would affect


| you would be affecting


| you would be affecting


| you would have affected


| you would have affected


| you would have been affecting


| you would have been affecting


|-

| he would affect


| they would affect


| he would be affecting


| they would be affecting


| he would have affected


| they would have affected


| he would have been affecting


| they would have been affecting


|-

| colspan="12" style="background%3A%23d5d5d5%3B+height%3A+.25em" |


|-

! style="background%3A%23c0cfe4" | imperative


| colspan="2" | affect


| colspan="9" style="background%3A%23e0e0e0" |


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
                "form": "affect",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "affecting",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "affected",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "affect",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "affect",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "am affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "are affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "have affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "perfect",
                  "present",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "have affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "perfect",
                  "plural",
                  "present",
                  "multiword-construction"
                ]
              },
              {
                "form": "have been affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "perfect",
                  "present",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "have been affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "perfect",
                  "plural",
                  "present",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "affect",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "are affecting",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "have affected",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "present",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "have been affecting",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "present",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "affects",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "affect",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "is affecting",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "are affecting",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "has affected",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "present",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "have affected",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "plural",
                  "present",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "has been affecting",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "present",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "have been affecting",
                "source": "Conjugation",
                "tags": [
                  "perfect",
                  "plural",
                  "present",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "was affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "were affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "plural",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "had affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "perfect",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "had affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "perfect",
                  "plural",
                  "multiword-construction"
                ]
              },
              {
                "form": "had been affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "perfect",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "had been affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "perfect",
                  "plural",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "affected",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "second-person"
                ]
              },
              {
                "form": "were affecting",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "had affected",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "perfect",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "had been affecting",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "perfect",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "affected",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "affected",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "was affecting",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "were affecting",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "had affected",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "perfect",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "had affected",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "perfect",
                  "plural",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "had been affecting",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "perfect",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "had been affecting",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "perfect",
                  "plural",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will affect",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "will affect",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "plural",
                  "multiword-construction"
                ]
              },
              {
                "form": "will be affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "will be affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "plural",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "perfect",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have affected",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "perfect",
                  "plural",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have been affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "perfect",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have been affecting",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "perfect",
                  "plural",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "will affect",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will be affecting",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have affected",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "perfect",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have been affecting",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "perfect",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will affect",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will affect",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will be affecting",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will be affecting",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have affected",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "perfect",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have affected",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "perfect",
                  "plural",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have been affecting",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "perfect",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "will have been affecting",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "perfect",
                  "plural",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would affect",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "would affect",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural",
                  "multiword-construction"
                ]
              },
              {
                "form": "would be affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "would be affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have affected",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have affected",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "plural",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have been affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "progressive",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have been affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "perfect",
                  "plural",
                  "progressive",
                  "multiword-construction"
                ]
              },
              {
                "form": "would affect",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would be affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have affected",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have been affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "progressive",
                  "second-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would affect",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would affect",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would be affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would be affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have affected",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have affected",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "plural",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have been affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "progressive",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "would have been affecting",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "perfect",
                  "plural",
                  "progressive",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "affect",
                "source": "Conjugation",
                "tags": [
                  "imperative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_English_verb3(self):
        ret = self.xinfl("be", "English", "verb", "Conjugation", """
{| class="wikitable%2Bcollapsible%2Bcollapsed" style="text-align%253Acenter"

|-

! colspan="7" | Modern conjugations




|-

! colspan="2" | infinitive




| colspan="5" | <span class="Latn" lang="en">[[to#English|to]]</span> be




|-

! colspan="2" | present participle/gerund




| colspan="5" | <span class="Latn" lang="en">[[being#English|being]]</span>




|-

! colspan="2" | past participle




| colspan="5" | <span class="Latn" lang="en">[[been#English|been]]</span>




|-

! rowspan="2" |




! colspan="2" | indicative




! colspan="2" | subjunctive




! colspan="2" | imperative




|-

! singular




! plural




! singular




! plural




! singular




! plural




|-

! rowspan="3" | present




| I <span class="Latn" lang="en">[[am#English|am]]</span> (<span class="Latn" lang="en">[['m#English|’m]]</span>)




| we <span class="Latn" lang="en">[[are#English|are]]</span> (<span class="Latn" lang="en">[['re#English|’re]]</span>)




| I be




| we be




| let me be




| <span class="Latn" lang="en">[[let us#English|let us]]</span> be, <span class="Latn" lang="en">[[let's#English|let’s]]</span> be




|-

| you <span class="Latn" lang="en">[[are#English|are]]</span> (<span class="Latn" lang="en">[['re#English|’re]]</span>)




| you <span class="Latn" lang="en">[[are#English|are]]</span> (<span class="Latn" lang="en">[['re#English|’re]]</span>)




| you be




| you be




| be




| be




|-

| he/she/it <span class="Latn" lang="en">[[is#English|is]]</span> (<span class="Latn" lang="en">[['s#English|’s]]</span>) <br>they <span class="Latn" lang="en">[[are#English|are]]</span>*** (<span class="Latn" lang="en">[['re#English|’re]]</span>)




| they <span class="Latn" lang="en">[[are#English|are]]</span> (<span class="Latn" lang="en">[['re#English|’re]]</span>)




| he/she/it/they be




| they be




| let him/her/it/them be




| let them be




|-

! rowspan="3" | preterite




| I <span class="Latn" lang="en">[[was#English|was]]</span>*




| we <span class="Latn" lang="en">[[were#English|were]]</span>****




| I <span class="Latn" lang="en">[[were#English|were]]</span>




| we <span class="Latn" lang="en">[[were#English|were]]</span>




| rowspan="3" colspan="2" bgcolor="lightgray" |




|-

| you <span class="Latn" lang="en">[[were#English|were]]</span>**




| you <span class="Latn" lang="en">[[were#English|were]]</span>****




| you <span class="Latn" lang="en">[[were#English|were]]</span>




| you <span class="Latn" lang="en">[[were#English|were]]</span>




|-

| he/she/it <span class="Latn" lang="en">[[was#English|was]]</span>* <br>they <span class="Latn" lang="en">[[were#English|were]]</span>**




| they <span class="Latn" lang="en">[[were#English|were]]</span>****




| he/she/it/they <span class="Latn" lang="en">[[were#English|were]]</span>




| they <span class="Latn" lang="en">[[were#English|were]]</span>




|}


<small>*Some non-standard dialects use <i class="Latn+mention" lang="en">[[were#English|were]]</i> in these instances.</small><br>
<small>**Some non-standard dialects use <i class="Latn+mention" lang="en">[[was#English|was]]</i> in these instances.</small><br>
<small>***Some non-standard forms use <i class="Latn+mention" lang="en">[[is#English|is]]</i> in these instances.</small><br>
<small>****Some non-standard dialects use <i class="Latn+mention" lang="en">[[was#English|was]]</i> in these instances.</small><br>


{| class="wikitable%2Bcollapsible%2Bcollapsed" style="text-align%253Acenter"

|-

! colspan="7" | Archaic conjugations




|-

! colspan="2" | infinitive




| colspan="5" | <span class="Latn" lang="en">[[to#English|to]]</span> be




|-

! colspan="2" | present participle/gerund




| colspan="5" | <span class="Latn" lang="en">[[being#English|being]]</span>




|-

! colspan="2" | past participle




| colspan="5" | <span class="Latn" lang="en">[[been#English|been]]</span>




|-

! rowspan="2" |




! colspan="2" | indicative




! colspan="2" | subjunctive




! colspan="2" | imperative




|-

! singular




! plural




! singular




! plural




! singular




! plural




|-

! rowspan="3" | present




| I <span class="Latn" lang="en">[[am#English|am]]</span> (<span class="Latn" lang="en">[['m#English|’m]]</span>)/<span class="Latn" lang="en">[[be#English|be]]</span>




| we <span class="Latn" lang="en">[[are#English|are]]</span> (<span class="Latn" lang="en">[['re#English|’re]]</span>)/<span class="Latn" lang="en">[[be#English|be]]</span>/<span class="Latn" lang="en">[[been#English|been]]</span>




| I be




| we be




| —




| <span class="Latn" lang="en">[[let's#English|let’s]]</span> be




|-

| thou <span class="Latn" lang="en">[[art#English|art]]</span> (<span class="Latn" lang="en">[[thou'rt#English|’rt]]</span>)/<span class="Latn" lang="en">[[beest#English|beest]]</span>




| ye <span class="Latn" lang="en">[[are#English|are]]</span> (<span class="Latn" lang="en">[[ye're#English|’re]]</span>)/<span class="Latn" lang="en">[[be#English|be]]</span>/<span class="Latn" lang="en">[[been#English|been]]</span>




| thou <span class="Latn" lang="en">[[be#English|be]]</span>/<span class="Latn" lang="en">[[beest#English|beest]]</span>




| ye be




| be (thou)***




| be (ye)***




|-

| he/she/it <span class="Latn" lang="en">[[is#English|is]]</span> (<span class="Latn" lang="en">[['s#English|’s]]</span>)/<span class="Latn" lang="en">[[beeth#English|beeth]]</span>/<span class="Latn" lang="en">[[bes#English|bes]]</span>




| they <span class="Latn" lang="en">[[are#English|are]]</span> (<span class="Latn" lang="en">[['re#English|’re]]</span>)/<span class="Latn" lang="en">[[be#English|be]]</span>/<span class="Latn" lang="en">[[been#English|been]]</span>




| he/she/it be




| they be




| —




| —




|-

! rowspan="3" | preterite




| I <span class="Latn" lang="en">[[was#English|was]]</span>*




| we <span class="Latn" lang="en">[[were#English|were]]</span>**




| I <span class="Latn" lang="en">[[were#English|were]]</span>




| we <span class="Latn" lang="en">[[were#English|were]]</span>**




| rowspan="3" colspan="2" bgcolor="lightgray" |




|-

| thou <span class="Latn" lang="en">[[wert#English|wert]]</span>/<span class="Latn" lang="en">[[wast#English|wast]]</span>




| ye <span class="Latn" lang="en">[[were#English|were]]</span>**




| thou <span class="Latn" lang="en">[[were#English|were]]</span>/<span class="Latn" lang="en">[[wert#English|wert]]</span>




| ye <span class="Latn" lang="en">[[were#English|were]]</span>**




|-

| he/she/it <span class="Latn" lang="en">[[was#English|was]]</span>*




| they <span class="Latn" lang="en">[[were#English|were]]</span>**




| he/she/it <span class="Latn" lang="en">[[were#English|were]]</span>




| they <span class="Latn" lang="en">[[were#English|were]]</span>**




|}


<small>*Some non-standard dialects will have <span class="Latn" lang="en">[[were#English|were]]</span> in these instances.</small><br><small>**Some non-standard dialects will have <span class="Latn" lang="en">[[was#English|was]]</span> in these instances.</small><br><small>***Subject pronoun is optional.</small>

* The verb <i class="Latn+mention" lang="en">be</i> is the most irregular non-defective verb in Standard English. Unlike other verbs, which distinguish at most five forms (as in <i class="Latn+mention" lang="en">do</i>–<i class="Latn+mention" lang="en">does</i>–<i class="Latn+mention" lang="en">doing</i>–<i class="Latn+mention" lang="en">did</i>–<i class="Latn+mention" lang="en">done</i>), <i class="Latn+mention" lang="en">be</i> distinguishes many more:
** <i class="Latn+mention" lang="en">Be</i> itself is the plain form, used as the infinitive, as the imperative, and as the present subjunctive (though many speakers do not distinguish the present indicative and present subjunctive, using the indicative forms for both).
**:: ''I want to '''be''' a father someday.'' (infinitive)
**:: ''If that '''be''' true...'' (present subjunctive; ''is'' is common in this position)
**:: ''Allow the truth to '''be''' heard!'' (infinitive)
**:: ''Please '''be''' here by eight o’clock.'' (imperative)
**:: ''The librarian asked that the rare books not '''be''' touched.'' (present subjunctive; speakers that do not distinguish the subjunctive and indicative would use an [[auxiliary verb]] construction here)
**: <li class="senseid" id="English%3A_dynamic_conjugation"><i class="Latn+mention" lang="en">Be</i> is also used as the present tense indicative form in the alternative, dynamic / lexical conjugation of ''be'':
**:: ''What do we do? We '''be''' ourselves.'' (first-person plural present indicative, lexical be)
**:: but: ''Who '''are''' we? We '''are''' human beings.'' (first-person plural present indicative, copula be)
**: It is also an archaic alternative form of the indicative, especially in the plural:<ref>[[w:Goold Brown|Goold Brown]]&#32;(1851),&#32;&#32;“Of Verbs”, in&#32;<cite>The Grammar of English Grammars,<span class="q-hellip-sp"> </span><span class="q-hellip-b"><span style="font-style%3A+normal%3B">[</span></span><span title="with+an+Introduction%2C+Historical+and+Critical%3B+the+Whole+Methodically+Arranged+and+Amply+Illustrated%3B+with+Forms+of+Correcting+and+of+Parsing%2C+Improprieties+for+Correction%2C+Examples+for+Parsing%2C+Questions+for+Examination%2C+Exercises+for+Writing%2C+Observations+for+the+Advanced+Student%2C+Decisions+and+Proofs+for+the+Settlement+of+Disputed+Points%2C+Occasional+Strictures+and+Defences%2C+an+Exhibition+of+the+Several+Methods+of+Analysis%2C+and+a+Key+to+the+Oral+Exercises%3A+to+Which+Are+Added+Four+Appendixes%2C+Pertaining+Separately+to+the+Four+Parts+of+Grammar">…</span><span class="q-hellip-b"><span style="font-style%3A+normal%3B">]</span></span><span class="q-hellip-b" /></cite>, New York, N.Y.&#58; <span class="q-hellip-sp">&#32;</span><span class="q-hellip-b">[</span><span title="Published+by">…</span><span class="q-hellip-b">]</span><span class="q-hellip-b">&#32;</span>Samuel S. & William Wood,<span class="q-hellip-sp">&nbsp;</span><span class="q-hellip-b">[</span><span title="No.+261+Pearl+Street">…</span><span class="q-hellip-b">]</span><span class="q-hellip-b" />, [[https://archive.org/details/grammarofenglish00browrich/page/357/mode/1up] page 357].</ref>
**:: ''The [[powers that be|powers that '''be''']], are ordained of God.'' (Romans 13:1, Tyndale Bible, 1526)<ref>&#91;[[w:William Tyndale|William Tyndale]], transl.&#93;&#32;(1526)&#32;<cite>[[w:New Testament|The Newe Testamẽt<span class="q-hellip-sp"> </span><span class="q-hellip-b"><span style="font-style%3A+normal%3B">[</span></span><span title="as+it+was+Written+and+Caused+to+be+Writt%E1%BA%BD+by+Them+which+Herde+Yt.+To+whom+also+Oure+Saveoure+Christ+Jesus+Commaunded+that+They+Shulde+Preache+it+vnto+Al+Creatures.">…</span><span class="q-hellip-b"><span style="font-style%3A+normal%3B">]</span></span><span class="q-hellip-b" />]]</cite>&#32;([[w:Tyndale Bible|Tyndale Bible]]), [Worms, Germany
&vert;publisher  = [[w:Peter Schöffer|Peter Schöffer]]], <small>[[w:OCLC|OCLC]] [https://worldcat.org/oclc/762018299 762018299]</small>, [[w:Epistle to the Romans|Romans]]&#32;xiij&#58;[1], [https://archive.org/stream/1526-tyndale-nt#page/n215/mode/1up folio ccxiij, recto]&#58; “The powers that be / are ordeyned off God.”</ref>
**:: ''We are true men; we are no spies: We '''be''' twelve brethren...'' (Genesis 42:31-2, King James Version, 1611)<ref>&#32;<cite>[[w:Bible|The Holy Bible,<span class="q-hellip-sp"> </span><span class="q-hellip-b"><span style="font-style%3A+normal%3B">[</span></span><span title="Conteyning+the+Old+Testament%2C+and+the+New.+Newly+Translated+out+of+the+Originall+Tongues%3A+%26+with+the+Former+Translations+Diligently+Compared+and+Reuised%2C+by+His+Maiesties+Speciall+Comandement.+Appointed+to+be+Read+in+Churches.">…</span><span class="q-hellip-b"><span style="font-style%3A+normal%3B">]</span></span><span class="q-hellip-b" />]]</cite>&#32;([[w:King James Version|King James Version]]), London&#58; <span class="q-hellip-sp">&#32;</span><span class="q-hellip-b">[</span><span title="Imprinted+at+London+by">…</span><span class="q-hellip-b">]</span><span class="q-hellip-b">&#32;</span> [[w:Robert Barker (printer)|Robert Barker]],<span class="q-hellip-sp">&nbsp;</span><span class="q-hellip-b">[</span><span title="printer+to+the+Kings+Most+Excellent+Maiestie.">…</span><span class="q-hellip-b">]</span><span class="q-hellip-b" />, 1611, <small>[[w:OCLC|OCLC]] [https://worldcat.org/oclc/964384981 964384981]</small>, [[w:Book of Genesis|Genesis]] [https://archive.org/stream/Bible1611/Binder1#page/n125/mode/1up 42:31–32], column 2&#58; “We are true men; we are no ſpies. We be twelue brethren<span class="q-hellip-sp">&nbsp;</span><span class="q-hellip-b">[</span>…<span class="q-hellip-b">]</span><span class="q-hellip-b" />”.</ref>
**:: ''I think it '''be''' thine indeed, for thou liest in it.'' (Hamlet, Act V, Scene 1, circa 1600 — though this may be viewed as the subjunctive instead)<ref>[[w:William Shakespeare|William Shakespeare]]&#32;(''[[Appendix:Glossary#c.|c.]]'' 1599–1602),&#32;&#32;“[[w:Hamlet|The Tragedie of Hamlet, Prince of Denmarke]]”, in&#32;<cite>Mr. William Shakespeares Comedies, Histories, & Tragedies: Published According to the True Originall Copies</cite>&#32;([[w:First Folio|First Folio]]), London&#58; <span class="q-hellip-sp">&#32;</span><span class="q-hellip-b">[</span><span title="Printed+by">…</span><span class="q-hellip-b">]</span><span class="q-hellip-b">&#32;</span> [[w:William Jaggard|Isaac Iaggard]], and [[w:Edward Blount|Ed[ward] Blount]], published 1623, <small>[[w:OCLC|OCLC]] [https://worldcat.org/oclc/606515358 606515358]</small>, [Act V, scene i], [[https://archive.org/details/mrvvilliamshakes00shak/page/277/mode/1up] page 277], column 2&#58; “I thinke it be thine indeed: for thou lieſt in’t.”</ref>
** <i class="Latn+mention" lang="en">[[am#English|Am]]</i>, <i class="Latn+mention" lang="en">[[are#English|are]]</i>, and <i class="Latn+mention" lang="en">[[is#English|is]]</i> are the forms of the present indicative. <i class="Latn+mention" lang="en">Am</i> is the first-person singular (used with <i class="Latn+mention" lang="en">I</i>); <i class="Latn+mention" lang="en">is</i> is the third-person singular (used with <i class="Latn+mention" lang="en">he</i>, <i class="Latn+mention" lang="en">she</i>, <i class="Latn+mention" lang="en">it</i> and other subjects that would be used with <i class="Latn+mention" lang="en">does</i> rather than <i class="Latn+mention" lang="en">do</i>); and <i class="Latn+mention" lang="en">are</i> is both the second-person singular and the plural (used with <i class="Latn+mention" lang="en">we</i>, <i class="Latn+mention" lang="en">you</i>, <i class="Latn+mention" lang="en">they</i>, and any other plural subjects).
**: '''''Am''' I in the right place?'' (first-person singular present indicative)
**: ''You '''are''' even taller than your brother!'' (second-person singular present indicative)
**: ''Where '''is''' the library?'' (third-person singular present indicative)
**: ''These '''are''' the biggest shoes we have.'' (plural present indicative)
** <i class="Latn+mention" lang="en">[[was#English|Was]]</i> and <i class="Latn+mention" lang="en">[[were#English|were]]</i> are the forms of the past indicative and past subjunctive (like <i class="Latn+mention" lang="en">did</i>). In the past indicative, <i class="Latn+mention" lang="en">was</i> is the first- and third-person singular (used with <i class="Latn+mention" lang="en">I</i>, as well as with <i class="Latn+mention" lang="en">he</i>, <i class="Latn+mention" lang="en">she</i>, <i class="Latn+mention" lang="en">it</i> and other subjects that would be used with <i class="Latn+mention" lang="en">does</i> rather than <i class="Latn+mention" lang="en">do</i>), and <i class="Latn+mention" lang="en">were</i> is both the second-person singular and the plural (used with <i class="Latn+mention" lang="en">we</i>, <i class="Latn+mention" lang="en">you</i>, <i class="Latn+mention" lang="en">they</i>, and any other plural subjects). In the traditional past subjunctive, <i class="Latn+mention" lang="en">were</i> is used with all subjects, though many speakers do not actually distinguish the past subjunctive from the past indicative, and therefore use <i class="Latn+mention" lang="en">was</i> with first- and third-person singular subjects even in cases where other speakers would use <i class="Latn+mention" lang="en">were</i>.
**: ''I '''was''' out of town.'' (first-person singular past indicative)
**: ''You '''were''' the first person here.'' (second-person singular past indicative)
**: ''The room '''was''' dirty.'' (third-person singular past indicative)
**: ''We '''were''' angry at each other.'' (plural past indicative)
**: ''I wish I '''were''' more sure.'' (first-person singular past subjunctive; ''was'' is also common, though considered less correct by some)
**: ''If she '''were''' here, she would know what to do.'' (third-person singular past subjunctive; ''was'' is also common, though considered less correct by some)
** <i class="Latn+mention" lang="en">[[being#English|Being]]</i> is the gerund and present participle, used in progressive aspectual forms, after various [[Appendix:English catenative verbs|catenative]] verbs, and in other constructions that function like nouns, adjectivally or adverbially. (It’s also used as a deverbal noun and as a conjunction; see those senses in the entry for <i class="Latn+mention" lang="en">[[being#English|being]]</i> itself.)
**: '''''Being''' in London and '''being''' in Tokyo have similar rewards but in different languages.'' (gerund in grammatical subject)
**: ''All of a sudden, he’s '''being''' nice to everyone.'' (present participle in progressive aspect)
**:''His mood '''being''' good increased his productivity noticeably.'' (present participle in adjectival phrase)
**: ''It won’t stop '''being''' a problem until someone does something about it.'' (gerund after catenative verb)
** <i class="Latn+mention" lang="en">[[been#English|Been]]</i> is the past participle, used in the perfect aspect. In Middle English, it was also the infinitive.
**: ''It’s '''been''' that way for a week and a half.''
* In archaic or obsolete forms of English, with the pronoun <i class="Latn+mention" lang="en">[[thou#English|thou]]</i>, the verb <i class="Latn+mention" lang="en">be</i> has a few additional forms:
** When the pronoun <i class="Latn+mention" lang="en">thou</i> was in regular use, the forms <i class="Latn+mention" lang="en">[[art#English|art]]</i>, <i class="Latn+mention" lang="en">[[wast#English|wast]]</i>, and <i class="Latn+mention" lang="en">[[wert#English|wert]]</i> were the corresponding present indicative, past indicative, and past subjunctive, respectively.
** As <i class="Latn+mention" lang="en">thou</i> became less common and more highly marked, a special present-subjunctive form <i class="Latn+mention" lang="en">[[beest#English|beest]]</i> developed (replacing the regular present subjunctive form <i class="Latn+mention" lang="en">be</i>, still used with all other subjects). Additionally, the form <i class="Latn+mention" lang="en">wert</i>, previously a past subjunctive form, came to be used as a past indicative as well.
* The forms <i class="Latn+mention" lang="en">am</i>, <i class="Latn+mention" lang="en">is</i>, and <i class="Latn+mention" lang="en">are</i> can contract with preceding subjects: <i class="Latn+mention" lang="en">[[I'm#English|I’m]]</i> <span class="mention-gloss-paren+annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">I am</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren+annotation-paren">)</span>, <i class="Latn+mention" lang="en">[['s#English|’s]]</i> <span class="mention-gloss-paren+annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">is</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren+annotation-paren">)</span>, <i class="Latn+mention" lang="en">[['re#English|’re]]</i> <span class="mention-gloss-paren+annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">are</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren+annotation-paren">)</span>. The form <i class="Latn+mention" lang="en">are</i> most commonly contracts with personal pronouns (<i class="Latn+mention" lang="en">[[we're#English|we’re]]</i> <span class="mention-gloss-paren+annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">we are</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren+annotation-paren">)</span>, <i class="Latn+mention" lang="en">[[you're#English|you’re]]</i> <span class="mention-gloss-paren+annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">you are</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren+annotation-paren">)</span>, <i class="Latn+mention" lang="en">[[they're#English|they’re]]</i> <span class="mention-gloss-paren+annotation-paren">(</span><span class="mention-gloss-double-quote">“</span><span class="mention-gloss">they are</span><span class="mention-gloss-double-quote">”</span><span class="mention-gloss-paren+annotation-paren">)</span>), but contractions with other subjects are possible; the form <i class="Latn+mention" lang="en">is</i> contracts quite freely with a variety of subjects. These contracted forms, however, are possible only when there is an explicit, non-preposed complement, and they cannot be stressed; therefore, contraction does not occur in sentences such as the following:
*: ''Who’s here? —I '''am'''.''
*: ''I wonder what it '''is'''.''
*: ''I don’t want to be involved. —But you '''''are''''' involved, regardless.''
* Several of the finite forms of <i class="Latn+mention" lang="en">be</i> have special negative forms, containing the suffix <i class="Latn+mention" lang="en">[[-n't#English|-n’t]]</i>, that can be used instead of adding the adverb <i class="Latn+mention" lang="en">[[not#English|not]]</i>. Specifically, the forms <i class="Latn+mention" lang="en">is</i>, <i class="Latn+mention" lang="en">are</i>, <i class="Latn+mention" lang="en">was</i>, and <i class="Latn+mention" lang="en">were</i> have the negative forms <i class="Latn+mention" lang="en">[[isn't#English|isn’t]]</i>, <i class="Latn+mention" lang="en">[[aren't#English|aren’t]]</i>, <i class="Latn+mention" lang="en">[[wasn't#English|wasn’t]]</i>, and <i class="Latn+mention" lang="en">[[weren't#English|weren’t]]</i>. The form <i class="Latn+mention" lang="en">be</i> itself does not, even in finite uses, with “not be” being used in the present subjunctive and “do not be” or “don’t be” (or, in dated use, “be not”) being used in the imperative. The form <i class="Latn+mention" lang="en">am</i> has the negative forms <i class="Latn+mention" lang="en">[[aren't#English|aren’t]]</i>, <i class="Latn+mention" lang="en">[[amn't#English|amn’t]]</i>, and <i class="Latn+mention" lang="en">[[ain't#English|ain’t]]</i>, but all of these are in restricted use; see their entries for details.
* Outside of Standard English, there is some variation in usage of some forms; some dialects, for example, use <i class="Latn+mention" lang="en">is</i> or <i class="Latn+mention" lang="en">’s</i> throughout the present indicative (supplanting, in whole or in part, <i class="Latn+mention" lang="en">am</i> and <i class="Latn+mention" lang="en">are</i>), and/or <i class="Latn+mention" lang="en">was</i> throughout the past indicative and past subjunctive (supplanting <i class="Latn+mention" lang="en">were</i>).

</li>
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
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "being",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "been",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "am",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "’m",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular",
                  "clitic"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present",
                  "clitic"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "let be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "present",
                  "singular",
                  "multiword-construction"
                ]
              },
              {
                "form": "let be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural",
                  "present",
                  "multiword-construction"
                ]
              },
              {
                "form": "let's be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural",
                  "present",
                  "pronoun-included",
                  "multiword-construction"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular",
                  "clitic"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person",
                  "clitic"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "is",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "’s",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person",
                  "clitic"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "singular",
                  "third-person",
                  "clitic"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person",
                  "clitic"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "let be",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present",
                  "singular",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "let be",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "present",
                  "third-person",
                  "multiword-construction"
                ]
              },
              {
                "form": "was",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "preterite",
                  "singular"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "preterite"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "preterite",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "preterite",
                  "subjunctive"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "second-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "preterite",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "preterite",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "was",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "third-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "preterite",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "preterite",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "archaic",
                "source": "Conjugation",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "being",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "been",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "am",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "’m",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular",
                  "clitic"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present",
                  "clitic"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "been",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "let's be",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural",
                  "present",
                  "pronoun-included",
                  "multiword-construction"
                ]
              },
              {
                "form": "art",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "’rt",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular",
                  "clitic"
                ]
              },
              {
                "form": "beest",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person",
                  "clitic"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "been",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "beest",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "is",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "’s",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person",
                  "clitic"
                ]
              },
              {
                "form": "beeth",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "bes",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "are",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "’re",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person",
                  "clitic"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "been",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "be",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "-",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "was",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "preterite",
                  "singular"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "preterite"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "preterite",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "preterite",
                  "subjunctive"
                ]
              },
              {
                "form": "wert",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wast",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "second-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "preterite",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "wert",
                "source": "Conjugation",
                "tags": [
                  "preterite",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "preterite",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "was",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "third-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "preterite",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "were",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "preterite",
                  "subjunctive",
                  "third-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_English_verb4(self):
        ret = self.xinfl("wit", "English", "verb", "Conjugation", """
{|

|-

| valign="top" |


{| class="wikitable"

|-

! Infinitive




| to wit




|-

! Imperative




| wit




|-

! Present participle




| [[witting]]




|-

! Past participle




| [[wist]]




|}






| valign="top" |


{| class="wikitable"

|-

!




! Present indicative




! Past indicative




|-

! First-person singular




| I [[wot]]




| I wist




|-

! Second-person singular




| thou [[wost]], [[wottest|wot(test)]] <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span>




| thou [[wistest|wist(est)]] <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span>




|-

! Third-person singular




| he/she/it wot




| he/she/it wist




|-

! First-person plural




| we wit(e)




| we wist




|-

! Second-person plural




| ye wit(e) <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span>




| ye wist <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span>




|-

! Third-person plural




| they wit(e)




| they wist




|}






|}
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
                "form": "wit",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "wit",
                "source": "Conjugation",
                "tags": [
                  "imperative"
                ]
              },
              {
                "form": "witting",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "wist",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
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
                "form": "wot",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "wist",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "wost",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wot",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wottest",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wist",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wistest",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "wot",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "wist",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "wit",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "wite",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "wist",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "wit",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "wite",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "wist",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "wit",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "wite",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "wist",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              }
            ],
}
        self.assertEqual(expected, ret)

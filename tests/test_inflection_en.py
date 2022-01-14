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

    def test_Finnish_verb2(self):
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

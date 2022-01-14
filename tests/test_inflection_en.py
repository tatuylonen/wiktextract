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

    def test_Finnish_verb1(self):
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

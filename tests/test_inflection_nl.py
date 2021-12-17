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

    def test_Dutch_verb1(self):
        ret = self.xinfl("slapen", "Dutch", "verb", "Inflection", """
{| style="border%3A1px+solid+%23CCCCFF%3B+text-align%3Acenter%3B+line-height%3A125%25" class="inflection-table+vsSwitcher" data-toggle-category="inflection" cellspacing="1" cellpadding="3"

|- style="background%3A+%23CCCCFF%3B"

! colspan="5" class="vsToggleElement" style="text-align%3A+left" | Inflection of <i class="Latn+mention" lang="nl">slapen</i> (strong class 7)


|- class="vsShow" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[infinitive]]


| style="min-width%3A+12em%3B" | <span class="Latn" lang="nl">[[slapen#Dutch|slapen]]</span>


|- class="vsShow" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[past tense|past]]&nbsp;[[singular]]


| <span class="Latn" lang="nl">[[sliep#Dutch|sliep]]</span>


|- class="vsShow" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[past tense|past]]&nbsp;[[participle]]


| <span class="Latn" lang="nl">[[geslapen#Dutch|geslapen]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[infinitive]]


| colspan="4" | <span class="Latn" lang="nl">[[slapen#Dutch|slapen]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[gerund]]


| colspan="4" | <span class="Latn" lang="nl">[[slapen#Dutch|slapen]]</span> <span class="gender"><abbr title="neuter+gender">n</abbr></span>


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

|


| style="min-width%3A+12em%3B+font-weight%3A+bold" | [[present&nbsp;tense]]


| style="min-width%3A+12em%3B+font-weight%3A+bold" | [[past&nbsp;tense]]


|-


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[first-person|1st&nbsp;person]]&nbsp;[[singular]]


| <span class="Latn" lang="nl">[[slaap#Dutch|slaap]]</span>

| <span class="Latn" lang="nl">[[sliep#Dutch|sliep]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[second-person|2nd&nbsp;person]]&nbsp;[[singular|sing.]]&nbsp;(<span lang="nl">[[jij#Dutch|jij]]</span>)


| <span class="Latn" lang="nl">[[slaapt#Dutch|slaapt]]</span>

| <span class="Latn" lang="nl">[[sliep#Dutch|sliep]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[second-person|2nd&nbsp;person]]&nbsp;[[singular|sing.]]&nbsp;(<span lang="nl">[[u#Dutch|u]]</span>)


| <span class="Latn" lang="nl">[[slaapt#Dutch|slaapt]]</span>

| <span class="Latn" lang="nl">[[sliep#Dutch|sliep]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[second-person|2nd&nbsp;person]]&nbsp;[[singular|sing.]]&nbsp;(<span lang="nl">[[gij#Dutch|gij]]</span>)


| <span class="Latn" lang="nl">[[slaapt#Dutch|slaapt]]</span>

| <span class="Latn" lang="nl">[[sliept#Dutch|sliept]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[third-person|3rd&nbsp;person]]&nbsp;[[singular]]


| <span class="Latn" lang="nl">[[slaapt#Dutch|slaapt]]</span>

| <span class="Latn" lang="nl">[[sliep#Dutch|sliep]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[plural]]


| <span class="Latn" lang="nl">[[slapen#Dutch|slapen]]</span>

| <span class="Latn" lang="nl">[[sliepen#Dutch|sliepen]]</span>


|- class="vsHide" style="background%3A+%23E6E6FF%3B+height%3A+0.5em"

|


| colspan="2" |


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[subjunctive]]&nbsp;[[singular|sing.]]<sup>1</sup>


| <span class="Latn" lang="nl">[[slape#Dutch|slape]]</span>

| <span class="Latn" lang="nl">[[sliepe#Dutch|sliepe]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[subjunctive]]&nbsp;[[plural|plur.]]<sup>1</sup>


| <span class="Latn" lang="nl">[[slapen#Dutch|slapen]]</span>

| <span class="Latn" lang="nl">[[sliepen#Dutch|sliepen]]</span>


|- class="vsHide" style="background%3A+%23E6E6FF%3B+height%3A+0.5em"

|


| colspan="2" |


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[imperative]]&nbsp;[[singular|sing.]]


| <span class="Latn" lang="nl">[[slaap#Dutch|slaap]]</span>


| rowspan="2" style="background%3A+%23E6E6FF%3B" |


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[imperative]]&nbsp;[[plural|plur.]]<sup>1</sup>


| <span class="Latn" lang="nl">[[slaapt#Dutch|slaapt]]</span>


|- class="vsHide" style="background%3A+%23E6E6FF%3B+height%3A+0.5em"

|


| colspan="2" |


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[participles]]


| <span class="Latn" lang="nl">[[slapend#Dutch|slapend]]</span>

| <span class="Latn" lang="nl">[[geslapen#Dutch|geslapen]]</span>


|- class="vsHide" style="background%3A+%23E6E6FF%3B"

| colspan="5" style="text-align%3Aleft%3B+vertical-align%3Atop%3B+font-size%3A+smaller%3B+line-height%3A+1em" | <sup>1)</sup> [[Wiktionary:Glossary#archaic|Archaic]].


|}
[[Category:Dutch class 7 strong verbs|SLAPEN]][[Category:Dutch basic verbs|SLAPEN]]
""")
        expected = {
            "forms": [
              {
                "form": "7",
                "source": "Inflection title",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "slapen",
                "source": "Inflection",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "slapen",
                "source": "Inflection",
                "tags": [
                  "gerund",
                  "neuter"
                ]
              },
              {
                "form": "slaap",
                "source": "Inflection",
                "tags": [
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "sliep",
                "source": "Inflection",
                "tags": [
                  "first-person",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "slaapt",
                "source": "Inflection",
                "tags": [
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sliep",
                "source": "Inflection",
                "tags": [
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "slaapt",
                "source": "Inflection",
                "tags": [
                  "formal",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sliep",
                "source": "Inflection",
                "tags": [
                  "formal",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "slaapt",
                "source": "Inflection",
                "tags": [
                  "Flanders",
                  "colloquial",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "slaapt",
                "source": "Inflection",
                "tags": [
                  "archaic",
                  "formal",
                  "majestic",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sliept",
                "source": "Inflection",
                "tags": [
                  "Flanders",
                  "colloquial",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sliept",
                "source": "Inflection",
                "tags": [
                  "archaic",
                  "formal",
                  "majestic",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "slaapt",
                "source": "Inflection",
                "tags": [
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sliep",
                "source": "Inflection",
                "tags": [
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "slapen",
                "source": "Inflection",
                "tags": [
                  "plural",
                  "present"
                ]
              },
              {
                "form": "sliepen",
                "source": "Inflection",
                "tags": [
                  "past",
                  "plural"
                ]
              },
              {
                "form": "slape",
                "source": "Inflection",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "sliepe",
                "source": "Inflection",
                "tags": [
                  "past",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "slapen",
                "source": "Inflection",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "sliepen",
                "source": "Inflection",
                "tags": [
                  "past",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "slaap",
                "source": "Inflection",
                "tags": [
                  "imperative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "slaapt",
                "source": "Inflection",
                "tags": [
                  "imperative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "slapend",
                "source": "Inflection",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "geslapen",
                "source": "Inflection",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "strong",
                "source": "Inflection title",
                "tags": [
                  "word-tags"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Dutch_adj1(self):
        ret = self.xinfl("mooi", "Dutch", "adj", "Inflection", """
{| style="border%3A+1px+solid+%23CCCCFF%3B+text-align%3A+center%3B+line-height%3A+125%25%3B" class="inflection-table+vsSwitcher" data-toggle-category="inflection" cellspacing="1" cellpadding="3"

|- style="background%3A+%23CCCCFF%3B"

! colspan="5" class="vsToggleElement" style="text-align%3A+left" | Inflection of <i class="Latn+mention" lang="nl">mooi</i>


|- class="vsShow" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | uninflected


| style="min-width%3A+12em%3B" | <span class="Latn+form-of+lang-nl+indef%7Cn%7Cs-form-of++++++form-of-nostore+" lang="nl">[[mooi#Dutch|mooi]]</span>


|- class="vsShow" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | inflected


| <span class="Latn+form-of+lang-nl+indef%7Cm%7Cand%7Cf%7Cs-form-of++++++form-of-nostore+" lang="nl">[[mooie#Dutch|mooie]]</span>


|- class="vsShow" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | comparative


| <span class="Latn+form-of+lang-nl+indef%7Cn%7Cs%7Ccomd-form-of++++++form-of-nostore+" lang="nl">[[mooier#Dutch|mooier]]</span>


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

| colspan="2" style="background%3A+%23E6E6FF%3B" |


! style="min-width%3A+12em%3B" | [[positive degree|positive]]


! style="min-width%3A+12em%3B" | [[comparative degree|comparative]]


! style="min-width%3A+12em%3B" | [[superlative degree|superlative]]


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | [[predicative]]/[[adverbial]]


| <span class="Latn+form-of+lang-nl+pred-form-of+++++++" lang="nl">[[mooi#Dutch|mooi]]</span>

| <span class="Latn+form-of+lang-nl+pred%7Ccomd-form-of+++++++" lang="nl">[[mooier#Dutch|mooier]]</span>

| <span class="Latn+form-of+lang-nl+pred%7Csupd-form-of+++++++" lang="nl">het [[mooist#Dutch|mooist]]</span><br><span class="Latn+form-of+lang-nl+pred%7Csupd-form-of+++++++" lang="nl">het [[mooiste#Dutch|mooiste]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" rowspan="3" | [[indefinite]]


! style="background%3A+%23CCCCFF%3B" | [[masculine|m.]]/[[feminine|f.]]&nbsp;[[singular|sing.]]


| <span class="Latn+form-of+lang-nl+indef%7Cm%7Cand%7Cf%7Cs-form-of+++++++" lang="nl">[[mooie#Dutch|mooie]]</span>

| <span class="Latn+form-of+lang-nl+indef%7Cm%7Cand%7Cf%7Cs%7Ccomd-form-of+++++++" lang="nl">[[mooiere#Dutch|mooiere]]</span>

| <span class="Latn+form-of+lang-nl+indef%7Cm%7Cand%7Cf%7Cs%7Csupd-form-of+++++++" lang="nl">[[mooiste#Dutch|mooiste]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" | [[neuter|n.]]&nbsp;[[singular|sing.]]


| <span class="Latn+form-of+lang-nl+indef%7Cn%7Cs-form-of+++++++" lang="nl">[[mooi#Dutch|mooi]]</span>

| <span class="Latn+form-of+lang-nl+indef%7Cn%7Cs%7Ccomd-form-of+++++++" lang="nl">[[mooier#Dutch|mooier]]</span>

| <span class="Latn+form-of+lang-nl+indef%7Cn%7Cs%7Csupd-form-of+++++++" lang="nl">[[mooiste#Dutch|mooiste]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A%23CCCCFF%3B" | [[plural]]


| <span class="Latn+form-of+lang-nl+indef%7Cp-form-of+++++++" lang="nl">[[mooie#Dutch|mooie]]</span>

| <span class="Latn+form-of+lang-nl+indef%7Cp%7Ccomd-form-of+++++++" lang="nl">[[mooiere#Dutch|mooiere]]</span>

| <span class="Latn+form-of+lang-nl+indef%7Cp%7Csupd-form-of+++++++" lang="nl">[[mooiste#Dutch|mooiste]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | [[definite]]


| <span class="Latn+form-of+lang-nl+def-form-of+++++++" lang="nl">[[mooie#Dutch|mooie]]</span>

| <span class="Latn+form-of+lang-nl+def%7Ccomd-form-of+++++++" lang="nl">[[mooiere#Dutch|mooiere]]</span>

| <span class="Latn+form-of+lang-nl+def%7Csupd-form-of+++++++" lang="nl">[[mooiste#Dutch|mooiste]]</span>


|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23CCCCFF%3B" colspan="2" | [[partitive]]


| <span class="Latn+form-of+lang-nl+par-form-of+++++++" lang="nl">[[moois#Dutch|moois]]</span>

| <span class="Latn+form-of+lang-nl+par%7Ccomd-form-of+++++++" lang="nl">[[mooiers#Dutch|mooiers]]</span>

| &mdash;


|}
""")
        expected = {
            "forms": [
              {
                "form": "mooi",
                "source": "Inflection",
                "tags": [
                  "adverbial",
                  "positive",
                  "predicative"
                ]
              },
              {
                "form": "mooier",
                "source": "Inflection",
                "tags": [
                  "adverbial",
                  "comparative",
                  "predicative"
                ]
              },
              {
                "form": "het mooist",
                "source": "Inflection",
                "tags": [
                  "adverbial",
                  "predicative",
                  "superlative"
                ]
              },
              {
                "form": "het mooiste",
                "source": "Inflection",
                "tags": [
                  "adverbial",
                  "predicative",
                  "superlative"
                ]
              },
              {
                "form": "mooie",
                "source": "Inflection",
                "tags": [
                  "feminine",
                  "indefinite",
                  "masculine",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "mooiere",
                "source": "Inflection",
                "tags": [
                  "comparative",
                  "feminine",
                  "indefinite",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "mooiste",
                "source": "Inflection",
                "tags": [
                  "feminine",
                  "indefinite",
                  "masculine",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "mooi",
                "source": "Inflection",
                "tags": [
                  "indefinite",
                  "neuter",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "mooier",
                "source": "Inflection",
                "tags": [
                  "comparative",
                  "indefinite",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "mooiste",
                "source": "Inflection",
                "tags": [
                  "indefinite",
                  "neuter",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "mooie",
                "source": "Inflection",
                "tags": [
                  "indefinite",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "mooiere",
                "source": "Inflection",
                "tags": [
                  "comparative",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "mooiste",
                "source": "Inflection",
                "tags": [
                  "indefinite",
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "mooie",
                "source": "Inflection",
                "tags": [
                  "definite",
                  "positive"
                ]
              },
              {
                "form": "mooiere",
                "source": "Inflection",
                "tags": [
                  "comparative",
                  "definite"
                ]
              },
              {
                "form": "mooiste",
                "source": "Inflection",
                "tags": [
                  "definite",
                  "superlative"
                ]
              },
              {
                "form": "moois",
                "source": "Inflection",
                "tags": [
                  "partitive",
                  "positive"
                ]
              },
              {
                "form": "mooiers",
                "source": "Inflection",
                "tags": [
                  "comparative",
                  "partitive"
                ]
              },
              {
                "form": "-",
                "source": "Inflection",
                "tags": [
                  "partitive",
                  "superlative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

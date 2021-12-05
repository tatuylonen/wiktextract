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
                "form": "sliept",
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

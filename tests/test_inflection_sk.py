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

    def test_Slovak_verb1(self):
        ret = self.xinfl("darovať", "Slovak", "verb", "conjugation", """
<div class="NavFrame" style>
<div class="NavHead" style>conjugation of ''darovať''</div>
<div class="NavContent">
<table style="text-align%3Acenter%3B+width%3A100%25" class="inflection-table">
<tr>
<th colspan="2" style="background%3A%23d0d0d0">infinitive</th>
<td colspan="5">[[darovať]]</td>
</tr>
<tr>
<th colspan="2" style="background%3A%23d0d0d0">present active participle</th>
<td colspan="5">darujúci</td>
</tr>

<tr>
<th colspan="2" style="background%3A%23d0d0d0">passive participle</th>
<td colspan="5">darovaný</td>
</tr>
<tr>
<th colspan="2" style="background%3A%23d0d0d0">l-participle</th>
<td colspan="5">daroval</td>
</tr>
<tr>
<th colspan="2" style="background%3A%23d0d0d0">transgressive</th>
<td colspan="5">darujúc</td>
</tr>
<tr>
<th colspan="2" style="background%3A%23d0d0d0">gerund</th>
<td colspan="5">darovanie</td>
</tr>
<tr>
<th rowspan="2" style="background%3A%23a0ade3">indicative</th>
<th colspan="3" style="background%3A%23a0ade3">''singular''</th>
<th colspan="3" style="background%3A%23a0ade3">''plural''</th>
</tr>
<tr>
<th style="background%3A%23a0ade3">[[first person|first]]</th>
<th style="background%3A%23a0ade3">[[second person|second]]</th>
<th style="background%3A%23a0ade3">[[third person|third]]</th>
<th style="background%3A%23a0ade3">[[first person|first]]</th>
<th style="background%3A%23a0ade3">[[second person|second]]</th>
<th style="background%3A%23a0ade3">[[third person|third]]</th>
</tr>
<tr>
<th style="background%3A%23c0cfe4%3B+width%3A7em">present</th>
<td>darujem</td>
<td>daruješ</td>
<td>daruje</td>
<td>darujeme</td>
<td>darujete</td>
<td>darujú</td>
</tr>
<tr>
<th style="background%3A%23c0cfe4%3B+width%3A7em">past <small>(m./f./n.)</small></th>
<td>daroval som<br>darovala som<br>darovalo som</td>
<td>daroval si<br>darovala si<br>darovalo si</td>
<td>daroval<br>darovala<br>darovalo</td>
<td>darovali sme</td>
<td>darovali ste</td>
<td>darovali</td>
</tr>
<tr>
<th style="background%3A%23c0cfe4%3B+width%3A7em">past perfect <small>(m./f./n.)</small></th>
<td>bol som daroval<br>bola som darovala<br>bolo som darovalo</td>
<td>bol si daroval<br>bola si darovala<br>bolo si darovalo</td>
<td>bol daroval<br>bola darovala<br>bolo darovalo</td>
<td>boli sme darovali</td>
<td>boli ste darovali</td>
<td>boli darovali</td>
</tr>
<tr>
<th style="background%3A%23c0cfe4%3B+width%3A7em">future</th>
<td>budem darovať</td>
<td>budeš darovať</td>
<td>bude darovať</td>
<td>budeme darovať</td>
<td>budete darovať</td>
<td>budú darovať</td>
</tr>
<tr>
<th rowspan="2" style="background%3A%2301DF74">conditional</th>
<th colspan="3" style="background%3A%2301DF74">''singular''</th>
<th colspan="3" style="background%3A%2301DF74">''plural''</th>
</tr>
<tr>
<th style="background%3A%2301DF74">[[first person|first]]</th>
<th style="background%3A%2301DF74">[[second person|second]]</th>
<th style="background%3A%2301DF74">[[third person|third]]</th>
<th style="background%3A%2301DF74">[[first person|first]]</th>
<th style="background%3A%2301DF74">[[second person|second]]</th>
<th style="background%3A%2301DF74">[[third person|third]]</th>
</tr>
<tr>
<th style="background%3A%2300FF80%3B+width%3A7em">present <small>(m./f./n.)</small></th>
<td>daroval by som<br>darovala by som<br>darovalo by som</td>
<td>daroval by si<br>darovala by si<br>darovalo by si</td>
<td>daroval by<br>darovala by<br>darovalo by</td>
<td>darovali by sme</td>
<td>darovali by ste</td>
<td>darovali by</td>
</tr>
<tr>
<th style="background%3A%2300FF80%3B+width%3A7em">past <small>(m./f./n.)</small></th>
<td>bol by som daroval<br>bola by som darovala<br>bolo by som darovalo</td>
<td>bol by si daroval<br>bola by si darovala<br>bolo by si darovalo</td>
<td>bol by daroval<br>bola by darovala<br>bolo by darovalo</td>
<td>boli by sme darovali</td>
<td>boli by ste darovali</td>
<td>boli by darovali</td>
</tr>
<tr>
<th rowspan="2" style="background%3A%23F3F781">imperative</th>
<th colspan="3" style="background%3A%23F3F781">''singular''</th>
<th colspan="3" style="background%3A%23F3F781">''plural''</th>
</tr>
<tr>
<th style="background%3A%23F3F781">[[first person|first]]</th>
<th style="background%3A%23F3F781">[[second person|second]]</th>
<th style="background%3A%23F3F781">[[third person|third]]</th>
<th style="background%3A%23F3F781">[[first person|first]]</th>
<th style="background%3A%23F3F781">[[second person|second]]</th>
<th style="background%3A%23F3F781">[[third person|third]]</th>
</tr>
<tr>
<th style="background%3A%23F2F5A9%3B+width%3A7em">present</th>
<td>—</td>
<td>daruj</td>
<td>—</td>
<td>darujme</td>
<td>darujte</td>
<td>—</td>
</tr>
</table></div></div>
""")
        expected = {
            "forms": [
                {
                  "form": "",
                  "source": "conjugation",
                  "tags": [
                    "table-tags"
                  ]
                },
                {
                  "form": "darovať",
                  "source": "conjugation",
                  "tags": [
                    "infinitive"
                  ]
                },
                {
                  "form": "darujúci",
                  "source": "conjugation",
                  "tags": [
                    "active",
                    "participle",
                    "present"
                  ]
                },
                {
                  "form": "darovaný",
                  "source": "conjugation",
                  "tags": [
                    "participle",
                    "passive"
                  ]
                },
                {
                  "form": "daroval",
                  "source": "conjugation",
                  "tags": [
                    "l-participle"
                  ]
                },
                {
                  "form": "darujúc",
                  "source": "conjugation",
                  "tags": [
                    "transgressive"
                  ]
                },
                {
                  "form": "darovanie",
                  "source": "conjugation",
                  "tags": [
                    "gerund"
                  ]
                },
                {
                  "form": "darujem",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "present",
                    "singular"
                  ]
                },
                {
                  "form": "daruješ",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "present",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "daruje",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "present",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darujeme",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "plural",
                    "present"
                  ]
                },
                {
                  "form": "darujete",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "plural",
                    "present",
                    "second-person"
                  ]
                },
                {
                  "form": "darujú",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "plural",
                    "present",
                    "third-person"
                  ]
                },
                {
                  "form": "daroval som",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "singular"
                  ]
                },
                {
                  "form": "darovala som",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "singular"
                  ]
                },
                {
                  "form": "darovalo som",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "singular"
                  ]
                },
                {
                  "form": "daroval si",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "darovala si",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "darovalo si",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "daroval",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darovala",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darovalo",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darovali sme",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "plural"
                  ]
                },
                {
                  "form": "darovali ste",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "plural",
                    "second-person"
                  ]
                },
                {
                  "form": "darovali",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "plural",
                    "third-person"
                  ]
                },
                {
                  "form": "bol som daroval",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "perfect",
                    "singular"
                  ]
                },
                {
                  "form": "bola som darovala",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "perfect",
                    "singular"
                  ]
                },
                {
                  "form": "bolo som darovalo",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "perfect",
                    "singular"
                  ]
                },
                {
                  "form": "bol si daroval",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "bola si darovala",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "bolo si darovalo",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "bol daroval",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "bola darovala",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "bolo darovalo",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "boli sme darovali",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "indicative",
                    "past",
                    "perfect",
                    "plural"
                  ]
                },
                {
                  "form": "boli ste darovali",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "plural",
                    "second-person"
                  ]
                },
                {
                  "form": "boli darovali",
                  "source": "conjugation",
                  "tags": [
                    "indicative",
                    "past",
                    "perfect",
                    "plural",
                    "third-person"
                  ]
                },
                {
                  "form": "budem darovať",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "future",
                    "indicative",
                    "singular"
                  ]
                },
                {
                  "form": "budeš darovať",
                  "source": "conjugation",
                  "tags": [
                    "future",
                    "indicative",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "bude darovať",
                  "source": "conjugation",
                  "tags": [
                    "future",
                    "indicative",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "budeme darovať",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "future",
                    "indicative",
                    "plural"
                  ]
                },
                {
                  "form": "budete darovať",
                  "source": "conjugation",
                  "tags": [
                    "future",
                    "indicative",
                    "plural",
                    "second-person"
                  ]
                },
                {
                  "form": "budú darovať",
                  "source": "conjugation",
                  "tags": [
                    "future",
                    "indicative",
                    "plural",
                    "third-person"
                  ]
                },
                {
                  "form": "daroval by som",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "present",
                    "singular"
                  ]
                },
                {
                  "form": "darovala by som",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "present",
                    "singular"
                  ]
                },
                {
                  "form": "darovalo by som",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "present",
                    "singular"
                  ]
                },
                {
                  "form": "daroval by si",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "present",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "darovala by si",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "present",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "darovalo by si",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "present",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "daroval by",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "present",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darovala by",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "present",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darovalo by",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "present",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darovali by sme",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "plural",
                    "present"
                  ]
                },
                {
                  "form": "darovali by ste",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "plural",
                    "present",
                    "second-person"
                  ]
                },
                {
                  "form": "darovali by",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "plural",
                    "present",
                    "third-person"
                  ]
                },
                {
                  "form": "bol by som daroval",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "past",
                    "singular"
                  ]
                },
                {
                  "form": "bola by som darovala",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "past",
                    "singular"
                  ]
                },
                {
                  "form": "bolo by som darovalo",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "past",
                    "singular"
                  ]
                },
                {
                  "form": "bol by si daroval",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "bola by si darovala",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "bolo by si darovalo",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "bol by daroval",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "bola by darovala",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "bolo by darovalo",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "boli by sme darovali",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "first-person",
                    "past",
                    "plural"
                  ]
                },
                {
                  "form": "boli by ste darovali",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "plural",
                    "second-person"
                  ]
                },
                {
                  "form": "boli by darovali",
                  "source": "conjugation",
                  "tags": [
                    "conditional",
                    "past",
                    "plural",
                    "third-person"
                  ]
                },
                {
                  "form": "-",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "imperative",
                    "present",
                    "singular"
                  ]
                },
                {
                  "form": "daruj",
                  "source": "conjugation",
                  "tags": [
                    "imperative",
                    "present",
                    "second-person",
                    "singular"
                  ]
                },
                {
                  "form": "-",
                  "source": "conjugation",
                  "tags": [
                    "imperative",
                    "present",
                    "singular",
                    "third-person"
                  ]
                },
                {
                  "form": "darujme",
                  "source": "conjugation",
                  "tags": [
                    "first-person",
                    "imperative",
                    "plural",
                    "present"
                  ]
                },
                {
                  "form": "darujte",
                  "source": "conjugation",
                  "tags": [
                    "imperative",
                    "plural",
                    "present",
                    "second-person"
                  ]
                },
                {
                  "form": "-",
                  "source": "conjugation",
                  "tags": [
                    "imperative",
                    "plural",
                    "present",
                    "third-person"
                  ]
                }
                ]
                  }
        self.assertEqual(expected, ret)

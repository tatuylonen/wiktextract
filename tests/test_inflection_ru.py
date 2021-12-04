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

class HeadTests(unittest.TestCase):

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

    def test_Russian_adj1(self):
        ret = self.xinfl("следующий", "Russian", "adj", "Declension", """
<div>
<div class="NavFrame" style="display%3A+inline-block%3B+min-width%3A+70em">
<div class="NavHead" style="background%3A%23eff7ff">Declension of <b lang="ru" class="Cyrl"><span class="Cyrl" lang="ru">сле́дующий</span></b> (unknown short forms)</div>
<div class="NavContent">

{| style="background%3A%23F9F9F9%3Btext-align%3Acenter%3B+min-width%3A70em" class="inflection-table"

|-

! style="width%3A20%25%3Bbackground%3A%23d9ebff" colspan="2" |


! style="background%3A%23d9ebff" | masculine


! style="background%3A%23d9ebff" | neuter


! style="background%3A%23d9ebff" | feminine


! style="background%3A%23d9ebff" | plural


|-

! style="background%3A%23eff7ff" colspan="2" | nominative


| <span class="Cyrl+form-of+lang-ru+nom%7Cm%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующий#Russian|сле́дующий]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščij</span>


| <span class="Cyrl+form-of+lang-ru+nom%7Cn%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующее#Russian|сле́дующее]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščeje</span>


| <span class="Cyrl+form-of+lang-ru+nom%7Cf%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующая#Russian|сле́дующая]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščaja</span>


| <span class="Cyrl+form-of+lang-ru+nom%7Cp-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующие#Russian|сле́дующие]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščije</span>


|-

! style="background%3A%23eff7ff" colspan="2" | genitive


| colspan="2" | <span class="Cyrl+form-of+lang-ru+gen%7Cm%2F%2Fn%7Cs-form-of+++transliteration-sl%C3%A9duju%C5%A1%C4%8Devo+origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующего#Russian|сле́дующего]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščevo</span>


| <span class="Cyrl+form-of+lang-ru+gen%7Cf%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующей#Russian|сле́дующей]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščej</span>


| <span class="Cyrl+form-of+lang-ru+gen%7Cp-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующих#Russian|сле́дующих]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščix</span>


|-

! style="background%3A%23eff7ff" colspan="2" | dative


| colspan="2" | <span class="Cyrl+form-of+lang-ru+dat%7Cm%2F%2Fn%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующему#Russian|сле́дующему]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščemu</span>


| <span class="Cyrl+form-of+lang-ru+dat%7Cf%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующей#Russian|сле́дующей]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščej</span>


| <span class="Cyrl+form-of+lang-ru+dat%7Cp-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующим#Russian|сле́дующим]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščim</span>


|-

! style="background%3A%23eff7ff" rowspan="2" | accusative


! style="background%3A%23eff7ff" | animate


| <span class="Cyrl+form-of+lang-ru+an%7Cacc%7Cm%7Cs-form-of+++transliteration-sl%C3%A9duju%C5%A1%C4%8Devo+origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующего#Russian|сле́дующего]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščevo</span>


| rowspan="2" | <span class="Cyrl+form-of+lang-ru+acc%7Cn%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующее#Russian|сле́дующее]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščeje</span>


| rowspan="2" | <span class="Cyrl+form-of+lang-ru+acc%7Cf%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующую#Russian|сле́дующую]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščuju</span>


| <span class="Cyrl+form-of+lang-ru+an%7Cacc%7Cp-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующих#Russian|сле́дующих]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščix</span>


|-

! style="background%3A%23eff7ff" | inanimate


| <span class="Cyrl+form-of+lang-ru+in%7Cacc%7Cm%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующий#Russian|сле́дующий]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščij</span>


| <span class="Cyrl+form-of+lang-ru+in%7Cacc%7Cp-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующие#Russian|сле́дующие]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščije</span>


|-

! style="background%3A%23eff7ff" colspan="2" | instrumental


| colspan="2" | <span class="Cyrl+form-of+lang-ru+ins%7Cm%2F%2Fn%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующим#Russian|сле́дующим]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščim</span>


| <span class="Cyrl+form-of+lang-ru+ins%7Cf%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующей#Russian|сле́дующей]]</span>, <span class="Cyrl+form-of+lang-ru+ins%7Cf%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующею#Russian|сле́дующею]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščej</span>, <span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščeju</span>


| <span class="Cyrl+form-of+lang-ru+ins%7Cp-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующими#Russian|сле́дующими]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščimi</span>


|-

! style="background%3A%23eff7ff" colspan="2" | prepositional


| colspan="2" | <span class="Cyrl+form-of+lang-ru+pre%7Cm%2F%2Fn%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующем#Russian|сле́дующем]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščem</span>


| <span class="Cyrl+form-of+lang-ru+pre%7Cf%7Cs-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующей#Russian|сле́дующей]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščej</span>


| <span class="Cyrl+form-of+lang-ru+pre%7Cp-form-of++++origin-%D1%81%D0%BB%D0%B5%CC%81%D0%B4%D1%83%D1%8E%D1%89%D0%B8%D0%B9+++" lang="ru">[[следующих#Russian|сле́дующих]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888%3B">slédujuščix</span>


|-

|}
</div></div></div>[[Category:Russian sibilant-stem stem-stressed adjectives|СЛЕДУЮЩИЙ]]
""")
        expected = {
            "forms": [
              {
                "form": "сле́дующий",
                "roman": "slédujuščij",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "nominative"
                ]
              },
              {
                "form": "сле́дующее",
                "roman": "slédujuščeje",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "nominative"
                ]
              },
              {
                "form": "сле́дующая",
                "roman": "slédujuščaja",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative"
                ]
              },
              {
                "form": "сле́дующие",
                "roman": "slédujuščije",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "сле́дующего",
                "roman": "slédujuščevo",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "neuter"
                ]
              },
              {
                "form": "сле́дующей",
                "roman": "slédujuščej",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive"
                ]
              },
              {
                "form": "сле́дующих",
                "roman": "slédujuščix",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "сле́дующему",
                "roman": "slédujuščemu",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "neuter"
                ]
              },
              {
                "form": "сле́дующей",
                "roman": "slédujuščej",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine"
                ]
              },
              {
                "form": "сле́дующим",
                "roman": "slédujuščim",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "сле́дующего",
                "roman": "slédujuščevo",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "animate",
                  "masculine"
                ]
              },
              {
                "form": "сле́дующее",
                "roman": "slédujuščeje",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "neuter"
                ]
              },
              {
                "form": "сле́дующую",
                "roman": "slédujuščuju",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine"
                ]
              },
              {
                "form": "сле́дующих",
                "roman": "slédujuščix",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "animate",
                  "plural"
                ]
              },
              {
                "form": "сле́дующий",
                "roman": "slédujuščij",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "inanimate",
                  "masculine"
                ]
              },
              {
                "form": "сле́дующие",
                "roman": "slédujuščije",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "inanimate",
                  "plural"
                ]
              },
              {
                "form": "сле́дующим",
                "roman": "slédujuščim",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "masculine",
                  "neuter"
                ]
              },
              {
                "form": "сле́дующей",
                "roman": "slédujuščej",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "instrumental"
                ]
              },
              {
                "form": "сле́дующею",
                "roman": "slédujuščeju",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "instrumental"
                ]
              },
              {
                "form": "сле́дующими",
                "roman": "slédujuščimi",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "сле́дующем",
                "roman": "slédujuščem",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "neuter",
                  "prepositional"
                ]
              },
              {
                "form": "сле́дующей",
                "roman": "slédujuščej",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "prepositional"
                ]
              },
              {
                "form": "сле́дующих",
                "roman": "slédujuščix",
                "source": "Declension",
                "tags": [
                  "plural",
                  "prepositional"
                ]
              }
            ],
        }
        self.assertEqual(ret, expected)

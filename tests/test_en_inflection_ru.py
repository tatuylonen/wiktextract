# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.inflection import parse_inflection_section
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class InflTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def xinfl(self, word, lang, pos, section, text):
        """Runs a single inflection table parsing test, and returns ``data``."""
        self.wxr.wtp.start_page(word)
        self.wxr.wtp.start_section(lang)
        self.wxr.wtp.start_subsection(pos)
        tree = self.wxr.wtp.parse(text)
        data = {}
        parse_inflection_section(self.wxr, data, word, lang, pos, section, tree)
        return data

    def test_Russian_adj1(self):
        ret = self.xinfl(
            "следующий",
            "Russian",
            "adj",
            "Declension",
            """
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
""",
        )  # noqa: E501
        expected = {
            "forms": [
                {
                    "form": "no-table-tags",
                    "source": "Declension",
                    "tags": ["table-tags"],
                },
                {
                    "form": "сле́дующий",
                    "tags": ["masculine", "nominative"],
                    "source": "Declension",
                    "roman": "slédujuščij",
                    "links": [("сле́дующий", "следующий#Russian")],
                },
                {
                    "form": "сле́дующее",
                    "tags": ["neuter", "nominative"],
                    "source": "Declension",
                    "roman": "slédujuščeje",
                    "links": [("сле́дующее", "следующее#Russian")],
                },
                {
                    "form": "сле́дующая",
                    "tags": ["feminine", "nominative"],
                    "source": "Declension",
                    "roman": "slédujuščaja",
                    "links": [("сле́дующая", "следующая#Russian")],
                },
                {
                    "form": "сле́дующие",
                    "tags": ["nominative", "plural"],
                    "source": "Declension",
                    "roman": "slédujuščije",
                    "links": [("сле́дующие", "следующие#Russian")],
                },
                {
                    "form": "сле́дующего",
                    "tags": ["genitive", "masculine", "neuter"],
                    "source": "Declension",
                    "roman": "slédujuščevo",
                    "links": [("сле́дующего", "следующего#Russian")],
                },
                {
                    "form": "сле́дующей",
                    "tags": ["feminine", "genitive"],
                    "source": "Declension",
                    "roman": "slédujuščej",
                    "links": [("сле́дующей", "следующей#Russian")],
                },
                {
                    "form": "сле́дующих",
                    "tags": ["genitive", "plural"],
                    "source": "Declension",
                    "roman": "slédujuščix",
                    "links": [("сле́дующих", "следующих#Russian")],
                },
                {
                    "form": "сле́дующему",
                    "tags": ["dative", "masculine", "neuter"],
                    "source": "Declension",
                    "roman": "slédujuščemu",
                    "links": [("сле́дующему", "следующему#Russian")],
                },
                {
                    "form": "сле́дующей",
                    "tags": ["dative", "feminine"],
                    "source": "Declension",
                    "roman": "slédujuščej",
                    "links": [("сле́дующей", "следующей#Russian")],
                },
                {
                    "form": "сле́дующим",
                    "tags": ["dative", "plural"],
                    "source": "Declension",
                    "roman": "slédujuščim",
                    "links": [("сле́дующим", "следующим#Russian")],
                },
                {
                    "form": "сле́дующего",
                    "tags": ["accusative", "animate", "masculine"],
                    "source": "Declension",
                    "roman": "slédujuščevo",
                    "links": [("сле́дующего", "следующего#Russian")],
                },
                {
                    "form": "сле́дующее",
                    "tags": ["accusative", "neuter"],
                    "source": "Declension",
                    "roman": "slédujuščeje",
                    "links": [("сле́дующее", "следующее#Russian")],
                },
                {
                    "form": "сле́дующую",
                    "tags": ["accusative", "feminine"],
                    "source": "Declension",
                    "roman": "slédujuščuju",
                    "links": [("сле́дующую", "следующую#Russian")],
                },
                {
                    "form": "сле́дующих",
                    "tags": ["accusative", "animate", "plural"],
                    "source": "Declension",
                    "roman": "slédujuščix",
                    "links": [("сле́дующих", "следующих#Russian")],
                },
                {
                    "form": "сле́дующий",
                    "tags": ["accusative", "inanimate", "masculine"],
                    "source": "Declension",
                    "roman": "slédujuščij",
                    "links": [("сле́дующий", "следующий#Russian")],
                },
                {
                    "form": "сле́дующие",
                    "tags": ["accusative", "inanimate", "plural"],
                    "source": "Declension",
                    "roman": "slédujuščije",
                    "links": [("сле́дующие", "следующие#Russian")],
                },
                {
                    "form": "сле́дующим",
                    "tags": ["instrumental", "masculine", "neuter"],
                    "source": "Declension",
                    "roman": "slédujuščim",
                    "links": [("сле́дующим", "следующим#Russian")],
                },
                {
                    "form": "сле́дующей",
                    "tags": ["feminine", "instrumental"],
                    "source": "Declension",
                    "roman": "slédujuščej",
                    "links": [("сле́дующей", "следующей#Russian")],
                },
                {
                    "form": "сле́дующею",
                    "tags": ["feminine", "instrumental"],
                    "source": "Declension",
                    "roman": "slédujuščeju",
                    "links": [("сле́дующею", "следующею#Russian")],
                },
                {
                    "form": "сле́дующими",
                    "tags": ["instrumental", "plural"],
                    "source": "Declension",
                    "roman": "slédujuščimi",
                    "links": [("сле́дующими", "следующими#Russian")],
                },
                {
                    "form": "сле́дующем",
                    "tags": ["masculine", "neuter", "prepositional"],
                    "source": "Declension",
                    "roman": "slédujuščem",
                    "links": [("сле́дующем", "следующем#Russian")],
                },
                {
                    "form": "сле́дующей",
                    "tags": ["feminine", "prepositional"],
                    "source": "Declension",
                    "roman": "slédujuščej",
                    "links": [("сле́дующей", "следующей#Russian")],
                },
                {
                    "form": "сле́дующих",
                    "tags": ["plural", "prepositional"],
                    "source": "Declension",
                    "roman": "slédujuščix",
                    "links": [("сле́дующих", "следующих#Russian")],
                },
            ]
        }

        self.assertEqual(expected, ret)

    def test_Russian_verb1(self):
        ret = self.xinfl(
            "произносить",
            "Russian",
            "verb",
            "Conjugation",
            """
<templatestyles src="Module%3Aru-verb%2Fstyle.css"><div class="NavFrame" style="width%3A49.6em%3B">
<div class="NavHead" style="text-align%3Aleft%3B+background%3A%23e0e0ff%3B">Conjugation of <span lang="ru" class="Cyrl">''произноси́ть''</span> (class 4c imperfective transitive)</div>
<div class="NavContent">

{| class="inflection+inflection-ru+inflection-verb+inflection-table"

|+
 Note: For declension of participles, see their entries. Adverbial participles are indeclinable.

|- class="rowgroup"

! colspan="3" | [[несовершенный вид|imperfective aspect]]


|-

! [[неопределённая форма|infinitive]]


| colspan="2" | <span class="Cyrl+form-of+lang-ru+inf-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносить#Russian|произноси́ть]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosítʹ</span>


|- class="rowgroup"

! style="width%3A15em" | [[причастие|participles]]


! [[настоящее время|present tense]]


! [[прошедшее время|past tense]]


|-

! [[действительный залог|active]]


| <span class="Cyrl+form-of+lang-ru+pres%7Cact%7Cpart-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносящий#Russian|произнося́щий]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosjáščij</span>

| <span class="Cyrl+form-of+lang-ru+past%7Cact%7Cpart-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносивший#Russian|произноси́вший]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosívšij</span>


|-

! [[страдательный залог|passive]]


| <span class="Cyrl+form-of+lang-ru+pres%7Cpass%7Cpart-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносимый#Russian|произноси́мый]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosímyj</span>

| &mdash;


|-

! [[деепричастие|adverbial]]


| <span class="Cyrl+form-of+lang-ru+pres%7Cadv%7Cpart-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произнося#Russian|произнося́]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosjá</span>

| <span class="Cyrl+form-of+lang-ru+past%7Cadv%7Cpart-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносив#Russian|произноси́в]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosív</span>,<br><span class="Cyrl+form-of+lang-ru+past%7Cadv%7Cpart-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносивши#Russian|произноси́вши]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosívši</span>


|- class="rowgroup"

!


! [[настоящее время|present tense]]


! [[будущее время|future tense]]


|-

! [[первое лицо|1st]] [[единственное число|singular]] (<span lang="ru" class="Cyrl">я</span>)


| <span class="Cyrl+form-of+lang-ru+1%7Cs%7Cpres%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произношу#Russian|произношу́]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznošú</span>

| <span class="Cyrl" lang="ru">[[буду#Russian|бу́ду]]</span><span lang="ru" class="Cyrl"> произноси́ть</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">búdu proiznosítʹ</span>


|-

! [[второе лицо|2nd]] [[единственное число|singular]] (<span lang="ru" class="Cyrl">ты</span>)


| <span class="Cyrl+form-of+lang-ru+2%7Cs%7Cpres%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносишь#Russian|произно́сишь]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznósišʹ</span>

| <span class="Cyrl" lang="ru">[[будешь#Russian|бу́дешь]]</span><span lang="ru" class="Cyrl"> произноси́ть</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">búdešʹ proiznosítʹ</span>


|-

! [[третье лицо|3rd]] [[единственное число|singular]] (<span lang="ru" class="Cyrl">он/она́/оно́</span>)


| <span class="Cyrl+form-of+lang-ru+3%7Cs%7Cpres%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносит#Russian|произно́сит]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznósit</span>

| <span class="Cyrl" lang="ru">[[будет#Russian|бу́дет]]</span><span lang="ru" class="Cyrl"> произноси́ть</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">búdet proiznosítʹ</span>


|-

! [[первое лицо|1st]] [[множественное число|plural]] (<span lang="ru" class="Cyrl">мы</span>)


| <span class="Cyrl+form-of+lang-ru+1%7Cp%7Cpres%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносим#Russian|произно́сим]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznósim</span>

| <span class="Cyrl" lang="ru">[[будем#Russian|бу́дем]]</span><span lang="ru" class="Cyrl"> произноси́ть</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">búdem proiznosítʹ</span>


|-

! [[второе лицо|2nd]] [[множественное число|plural]] (<span lang="ru" class="Cyrl">вы</span>)


| <span class="Cyrl+form-of+lang-ru+2%7Cp%7Cpres%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносите#Russian|произно́сите]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznósite</span>

| <span class="Cyrl" lang="ru">[[будете#Russian|бу́дете]]</span><span lang="ru" class="Cyrl"> произноси́ть</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">búdete proiznosítʹ</span>


|-

! [[третье лицо|3rd]] [[множественное число|plural]] (<span lang="ru" class="Cyrl">они́</span>)


| <span class="Cyrl+form-of+lang-ru+3%7Cp%7Cpres%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносят#Russian|произно́сят]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznósjat</span>

| <span class="Cyrl" lang="ru">[[будут#Russian|бу́дут]]</span><span lang="ru" class="Cyrl"> произноси́ть</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">búdut proiznosítʹ</span>


|- class="rowgroup"

! [[повелительное наклонение|imperative]]


! [[единственное число|singular]]


! [[множественное число|plural]]


|-

!


| <span class="Cyrl+form-of+lang-ru+2%7Cs%7Cimp-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произноси#Russian|произноси́]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosí</span>

| <span class="Cyrl+form-of+lang-ru+2%7Cp%7Cimp-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносите#Russian|произноси́те]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosíte</span>


|- class="rowgroup"

! [[прошедшее время|past tense]]


! [[единственное число|singular]]


! [[множественное число|plural]]<br>(<span lang="ru" class="Cyrl">мы/вы/они́</span>)


|-

! [[мужской род|masculine]] (<span lang="ru" class="Cyrl">я/ты/он</span>)


| <span class="Cyrl+form-of+lang-ru+m%7Cs%7Cpast%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносил#Russian|произноси́л]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosíl</span>

| rowspan="3" | <span class="Cyrl+form-of+lang-ru+p%7Cpast%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносили#Russian|произноси́ли]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosíli</span>


|-

! [[женский род|feminine]] (<span lang="ru" class="Cyrl">я/ты/она́</span>)


| <span class="Cyrl+form-of+lang-ru+f%7Cs%7Cpast%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносила#Russian|произноси́ла]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosíla</span>


|-

! style="background-color%3A+%23ffffe0%3B" | [[средний род|neuter]] (<span lang="ru" class="Cyrl">оно́</span>)


| <span class="Cyrl+form-of+lang-ru+n%7Cs%7Cpast%7Cind-form-of++++origin-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%BD%D0%BE%D1%81%D0%B8%CC%81%D1%82%D1%8C+++" lang="ru">[[произносило#Russian|произноси́ло]]</span><br><span lang="ru-Latn" class="tr+Latn" style="color%3A+%23888">proiznosílo</span>


|}

</div>
</div>[[Category:Russian class 4 verbs|ПРОИЗНОСИТЬ]][[Category:Russian class 4c verbs|ПРОИЗНОСИТЬ]][[Category:Russian imperfective verbs|ПРОИЗНОСИТЬ]][[Category:Russian transitive verbs|ПРОИЗНОСИТЬ]]
""",
        )  # noqa: E501
        expected = {
            "forms": [
                {
                    "form": "imperfective transitive",
                    "source": "Conjugation",
                    "tags": ["table-tags"],
                },
                {
                    "form": "4c imperfective transitive",
                    "source": "Conjugation",
                    "tags": ["class"],
                },
                {
                    "form": "произноси́ть",
                    "tags": ["imperfective", "infinitive"],
                    "source": "Conjugation",
                    "roman": "proiznosítʹ",
                    "links": [("произноси́ть", "произносить#Russian")],
                },
                {
                    "form": "произнося́щий",
                    "tags": ["active", "participle", "present"],
                    "source": "Conjugation",
                    "roman": "proiznosjáščij",
                    "links": [("произнося́щий", "произносящий#Russian")],
                },
                {
                    "form": "произноси́вший",
                    "tags": ["active", "participle", "past"],
                    "source": "Conjugation",
                    "roman": "proiznosívšij",
                    "links": [("произноси́вший", "произносивший#Russian")],
                },
                {
                    "form": "произноси́мый",
                    "tags": ["participle", "passive", "present"],
                    "source": "Conjugation",
                    "roman": "proiznosímyj",
                    "links": [("произноси́мый", "произносимый#Russian")],
                },
                {
                    "form": "-",
                    "tags": ["participle", "passive", "past"],
                    "source": "Conjugation",
                },
                {
                    "form": "произнося́",
                    "tags": ["adverbial", "participle", "present"],
                    "source": "Conjugation",
                    "roman": "proiznosjá",
                    "links": [("произнося́", "произнося#Russian")],
                },
                {
                    "form": "произноси́в",
                    "tags": ["adverbial", "participle", "past"],
                    "source": "Conjugation",
                    "roman": "proiznosív",
                    "links": [("произноси́в", "произносив#Russian")],
                },
                {
                    "form": "произноси́вши",
                    "tags": ["adverbial", "participle", "past"],
                    "source": "Conjugation",
                    "roman": "proiznosívši",
                    "links": [("произноси́вши", "произносивши#Russian")],
                },
                {
                    "form": "произношу́",
                    "tags": ["first-person", "present", "singular"],
                    "source": "Conjugation",
                    "roman": "proiznošú",
                    "links": [("произношу́", "произношу#Russian")],
                },
                {
                    "form": "бу́ду произноси́ть",
                    "tags": ["first-person", "future", "singular"],
                    "source": "Conjugation",
                    "roman": "búdu proiznosítʹ",
                },
                {
                    "form": "произно́сишь",
                    "tags": ["present", "second-person", "singular"],
                    "source": "Conjugation",
                    "roman": "proiznósišʹ",
                    "links": [("произно́сишь", "произносишь#Russian")],
                },
                {
                    "form": "бу́дешь произноси́ть",
                    "tags": ["future", "second-person", "singular"],
                    "source": "Conjugation",
                    "roman": "búdešʹ proiznosítʹ",
                },
                {
                    "form": "произно́сит",
                    "tags": ["present", "singular", "third-person"],
                    "source": "Conjugation",
                    "roman": "proiznósit",
                    "links": [("произно́сит", "произносит#Russian")],
                },
                {
                    "form": "бу́дет произноси́ть",
                    "tags": ["future", "singular", "third-person"],
                    "source": "Conjugation",
                    "roman": "búdet proiznosítʹ",
                },
                {
                    "form": "произно́сим",
                    "tags": ["first-person", "plural", "present"],
                    "source": "Conjugation",
                    "roman": "proiznósim",
                    "links": [("произно́сим", "произносим#Russian")],
                },
                {
                    "form": "бу́дем произноси́ть",
                    "tags": ["first-person", "future", "plural"],
                    "source": "Conjugation",
                    "roman": "búdem proiznosítʹ",
                },
                {
                    "form": "произно́сите",
                    "tags": ["plural", "present", "second-person"],
                    "source": "Conjugation",
                    "roman": "proiznósite",
                    "links": [("произно́сите", "произносите#Russian")],
                },
                {
                    "form": "бу́дете произноси́ть",
                    "tags": ["future", "plural", "second-person"],
                    "source": "Conjugation",
                    "roman": "búdete proiznosítʹ",
                },
                {
                    "form": "произно́сят",
                    "tags": ["plural", "present", "third-person"],
                    "source": "Conjugation",
                    "roman": "proiznósjat",
                    "links": [("произно́сят", "произносят#Russian")],
                },
                {
                    "form": "бу́дут произноси́ть",
                    "tags": ["future", "plural", "third-person"],
                    "source": "Conjugation",
                    "roman": "búdut proiznosítʹ",
                },
                {
                    "form": "произноси́",
                    "tags": ["imperative", "singular"],
                    "source": "Conjugation",
                    "roman": "proiznosí",
                    "links": [("произноси́", "произноси#Russian")],
                },
                {
                    "form": "произноси́те",
                    "tags": ["imperative", "plural"],
                    "source": "Conjugation",
                    "roman": "proiznosíte",
                    "links": [("произноси́те", "произносите#Russian")],
                },
                {
                    "form": "произноси́л",
                    "tags": ["masculine", "past", "singular"],
                    "source": "Conjugation",
                    "roman": "proiznosíl",
                    "links": [("произноси́л", "произносил#Russian")],
                },
                {
                    "form": "произноси́ли",
                    "tags": ["masculine", "past", "plural"],
                    "source": "Conjugation",
                    "roman": "proiznosíli",
                    "links": [("произноси́ли", "произносили#Russian")],
                },
                {
                    "form": "произноси́ла",
                    "tags": ["feminine", "past", "singular"],
                    "source": "Conjugation",
                    "roman": "proiznosíla",
                    "links": [("произноси́ла", "произносила#Russian")],
                },
                {
                    "form": "произноси́ли",
                    "tags": ["feminine", "past", "plural"],
                    "source": "Conjugation",
                    "roman": "proiznosíli",
                    "links": [("произноси́ли", "произносили#Russian")],
                },
                {
                    "form": "произноси́ло",
                    "tags": ["neuter", "past", "singular"],
                    "source": "Conjugation",
                    "roman": "proiznosílo",
                    "links": [("произноси́ло", "произносило#Russian")],
                },
                {
                    "form": "произноси́ли",
                    "tags": ["neuter", "past", "plural"],
                    "source": "Conjugation",
                    "roman": "proiznosíli",
                    "links": [("произноси́ли", "произносили#Russian")],
                },
            ]
        }
        self.assertEqual(expected, ret)

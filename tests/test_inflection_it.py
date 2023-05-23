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

    def test_Italian_verb1(self):
        ret = self.xinfl("essere", "Italian", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead">&nbsp; &nbsp; Conjugation of <i class="Latn+mention" lang="it">[[essere]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[esser]]</i></div>
<div class="NavContent">

{| style="background%3A%23F0F0F0%3Bborder-collapse%3Aseparate%3Bborder-spacing%3A2px%3Bwidth%3A100%25" class="inflection-table"

|-

! colspan="1" style="background%3A%23e2e4c0" | <span title="infinito">infinitive</span>


| colspan="1" | <span class="Latn" lang="it">[[essere#Italian|essere]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[esser#Italian|esser]]</span>


|-

! colspan="2" style="background%3A%23e2e4c0" | <span title="verbo+ausiliare">auxiliary verb</span>


| colspan="1" | <span class="Latn" lang="it">[[essere#Italian|essere]]</span>


! colspan="2" style="background%3A%23e2e4c0" | <span title="gerundio">gerund</span>


| colspan="2" | <span class="Latn" lang="it">[[essendo#Italian|essendo]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[sendo#Italian|sendo]]</span>


|-

! colspan="2" style="background%3A%23e2e4c0" |  <span title="participio+presente">present participle</span>


| colspan="1" | <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">rare, partially supplied</span><span class="ib-brac+qualifier-brac">)</span> [[essente#Italian|essente]]</span>


! colspan="2" style="background%3A%23e2e4c0" | <span title="participio+passato">past participle</span>


| colspan="2" | <span class="Latn" lang="it">[[stato#Italian|stato]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic, supplied by ''<span class="Latn" lang="it">[[stato#Italian|stato]]</span>''</span><span class="ib-brac+qualifier-brac">)</span> [[essuto#Italian|essuto]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[suto#Italian|suto]]</span>


|-

! colspan="1" rowspan="2" style="background%3A%23C0C0C0" | person


! colspan="3" style="background%3A%23C0C0C0" | singular


! colspan="3" style="background%3A%23C0C0C0" | plural


|-

! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | first


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | second


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | third


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | first


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | second


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | third


|-

! style="background%3A%23c0cfe4" colspan="1" | <span title="indicativo">indicative</span>


! style="background%3A%23c0cfe4" | io


! style="background%3A%23c0cfe4" | tu


! style="background%3A%23c0cfe4" | lui/lei, esso/essa


! style="background%3A%23c0cfe4" | noi


! style="background%3A%23c0cfe4" | voi


! style="background%3A%23c0cfe4" | loro, essi/esse


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="presente">present</span>


| <span class="Latn" lang="it">[[sono#Italian|sono]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[son#Italian|son]]</span>


| <span class="Latn" lang="it">[[sei#Italian|sei]]</span>


| <span class="Latn" lang="it">[[è#Italian|è]]</span>


| <span class="Latn" lang="it">[[siamo#Italian|siamo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[siam#Italian|siam]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic or regional</span><span class="ib-brac+qualifier-brac">)</span> [[semo#Italian|semo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic or regional, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[sem#Italian|sem]]</span>


| <span class="Latn" lang="it">[[siete#Italian|siete]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[sete#Italian|sete]]</span>


| <span class="Latn" lang="it">[[sono#Italian|sono]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[son#Italian|son]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic or regional</span><span class="ib-brac+qualifier-brac">)</span> [[enno#Italian|enno]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic or regional, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[en#Italian|en]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="imperfetto">imperfect</span>


| <span class="Latn" lang="it">[[ero#Italian|ero]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic or literary</span><span class="ib-brac+qualifier-brac">)</span> [[era#Italian|era]]</span>


| <span class="Latn" lang="it">[[eri#Italian|eri]]</span>


| <span class="Latn" lang="it">[[era#Italian|era]]</span>


| <span class="Latn" lang="it">[[eravamo#Italian|eravamo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[eravam#Italian|eravam]]</span>


| <span class="Latn" lang="it">[[eravate#Italian|eravate]]</span>


| <span class="Latn" lang="it">[[erano#Italian|erano]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[eran#Italian|eran]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="passato+remoto">past historic</span>


| <span class="Latn" lang="it">[[fui#Italian|fui]]</span>


| <span class="Latn" lang="it">[[fosti#Italian|fosti]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fusti#Italian|fusti]]</span>


| <span class="Latn" lang="it">[[fu#Italian|fu]]</span>


| <span class="Latn" lang="it">[[fummo#Italian|fummo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[fum#Italian|fum]]</span>


| <span class="Latn" lang="it">[[foste#Italian|foste]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fuste#Italian|fuste]]</span>


| <span class="Latn" lang="it">[[furono#Italian|furono]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[furon#Italian|furon]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[furo#Italian|furo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[fur#Italian|fur]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[foro#Italian|foro]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[for#Italian|for]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fuoro#Italian|fuoro]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[fuor#Italian|fuor]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="futuro+semplice">future</span>


| <span class="Latn" lang="it">[[sarò#Italian|sarò]]</span>


| <span class="Latn" lang="it">[[sarai#Italian|sarai]]</span>


| <span class="Latn" lang="it">[[sarà#Italian|sarà]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fia#Italian|fia]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fie#Italian|fie]]</span>


| <span class="Latn" lang="it">[[saremo#Italian|saremo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[sarem#Italian|sarem]]</span>


| <span class="Latn" lang="it">[[sarete#Italian|sarete]]</span>


| <span class="Latn" lang="it">[[saranno#Italian|saranno]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[saran#Italian|saran]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fiano#Italian|fiano]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[fian#Italian|fian]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fieno#Italian|fieno]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[fien#Italian|fien]]</span>


|-

! style="background%3A%23c0d8e4" colspan="1" | <span title="condizionale">conditional</span>


! style="background%3A%23c0d8e4" | io


! style="background%3A%23c0d8e4" | tu


! style="background%3A%23c0d8e4" | lui/lei, esso/essa


! style="background%3A%23c0d8e4" | noi


! style="background%3A%23c0d8e4" | voi


! style="background%3A%23c0d8e4" | loro, essi/esse


|-

! style="height%3A3em%3Bbackground%3A%23c0d8e4" colspan="1" | <span title="condizionale+presente">present</span>


| <span class="Latn" lang="it">[[sarei#Italian|sarei]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[saria#Italian|saria]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fora#Italian|fora]]</span>


| <span class="Latn" lang="it">[[saresti#Italian|saresti]]</span>


| <span class="Latn" lang="it">[[sarebbe#Italian|sarebbe]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[saria#Italian|saria]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fora#Italian|fora]]</span>


| <span class="Latn" lang="it">[[saremmo#Italian|saremmo]]</span>


| <span class="Latn" lang="it">[[sareste#Italian|sareste]]</span>


| <span class="Latn" lang="it">[[sarebbero#Italian|sarebbero]]</span>


|-

! style="background%3A%23c0e4c0" colspan="1" | <span title="congiuntivo">subjunctive</span>


! style="background%3A%23c0e4c0" | che io


! style="background%3A%23c0e4c0" | che tu


! style="background%3A%23c0e4c0" | che lui/che lei, che esso/che essa


! style="background%3A%23c0e4c0" | che noi


! style="background%3A%23c0e4c0" | che voi


! style="background%3A%23c0e4c0" | che loro, che essi/che esse


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="congiuntivo+presente">present</span>


| <span class="Latn" lang="it">[[sia#Italian|sia]]</span>


| <span class="Latn" lang="it">[[sia#Italian|sia]]</span>


| <span class="Latn" lang="it">[[sia#Italian|sia]]</span>


| <span class="Latn" lang="it">[[siamo#Italian|siamo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[siam#Italian|siam]]</span>


| <span class="Latn" lang="it">[[siate#Italian|siate]]</span>


| <span class="Latn" lang="it">[[siano#Italian|siano]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[sian#Italian|sian]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[sieno#Italian|sieno]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic, truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[sien#Italian|sien]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" rowspan="1" | <span title="congiuntivo+imperfetto">imperfect</span>


| <span class="Latn" lang="it">[[fossi#Italian|fossi]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fussi#Italian|fussi]]</span>


| <span class="Latn" lang="it">[[fossi#Italian|fossi]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fussi#Italian|fussi]]</span>


| <span class="Latn" lang="it">[[fosse#Italian|fosse]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fusse#Italian|fusse]]</span>


| <span class="Latn" lang="it">[[fossimo#Italian|fossimo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[fossim#Italian|fossim]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fussimo#Italian|fussimo]]</span>


| <span class="Latn" lang="it">[[foste#Italian|foste]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fuste#Italian|fuste]]</span>


| <span class="Latn" lang="it">[[fossero#Italian|fossero]]</span>, <span class="Latn" lang="it"><span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">archaic</span><span class="ib-brac+qualifier-brac">)</span> [[fussero#Italian|fussero]]</span>


|-

! colspan="1" rowspan="2" style="height%3A3em%3Bbackground%3A%23e4d4c0" | <span title="imperativo">imperative</span>


! style="background%3A%23e4d4c0" | &mdash;


! style="background%3A%23e4d4c0" | tu


! style="background%3A%23e4d4c0" | Lei


! style="background%3A%23e4d4c0" | noi


! style="background%3A%23e4d4c0" | voi


! style="background%3A%23e4d4c0" | Loro


|-

|


| <span class="Latn" lang="it">[[sii#Italian|sii]]</span>, <span class="Latn" lang="it">non [[essere#Italian|essere]]/[[esser#Italian|esser]]</span>


| <span class="Latn" lang="it">[[sia#Italian|sia]]</span>


| <span class="Latn" lang="it">[[siamo#Italian|siamo]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[siam#Italian|siam]]</span>


| <span class="Latn" lang="it">[[siate#Italian|siate]]</span>


| <span class="Latn" lang="it">[[siano#Italian|siano]], <span class="ib-brac+qualifier-brac">(</span><span class="ib-content+qualifier-content">truncated apocopic form</span><span class="ib-brac+qualifier-brac">)</span> [[sian#Italian|sian]]</span>


|-

|}
</div></div>[[Category:Italian irregular verbs|ESSERE]][[Category:Italian verbs with irregular past participles|ESSERE]]<ref name="essere1" />
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
                "form": "essere",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "esser",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "infinitive"
                ]
              },
              {
                "form": "essere",
                "source": "Conjugation",
                "tags": [
                  "auxiliary"
                ]
              },
              {
                "form": "essendo",
                "source": "Conjugation",
                "tags": [
                  "gerund"
                ]
              },
              {
                "form": "sendo",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "gerund"
                ]
              },
              {
                "form": "essente",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present",
                  "rare"
                ]
              },
              {
                "form": "stato",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "essuto",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "suto",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "sono",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "son",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "sei",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "è",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "siamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "siam",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "semo",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "dialectal",
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "sem",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "dialectal",
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "siete",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "sete",
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
                "form": "sono",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "son",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "enno",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "dialectal",
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "en",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "dialectal",
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "ero",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "era",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "literary",
                  "singular"
                ]
              },
              {
                "form": "eri",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "era",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "eravamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "eravam",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "eravate",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "erano",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "eran",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fui",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "historic",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "fosti",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "fusti",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "fu",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "fummo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "historic",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "fum",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "historic",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "foste",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "fuste",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "furono",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "furon",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "furo",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fur",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "foro",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "for",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fuoro",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fuor",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "sarò",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "sarai",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sarà",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "fia",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "fie",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saremo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "sarem",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "sarete",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "saranno",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "saran",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fiano",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fian",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fieno",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "fien",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "sarei",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "saria",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "fora",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "saresti",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sarebbe",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saria",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "fora",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saremmo",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "sareste",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "sarebbero",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {

                "form": "sia",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "sia",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "sia",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "siamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "siam",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "siate",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "siano",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "sian",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "sieno",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "sien",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "archaic",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fossi",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fussi",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fossi",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fussi",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "fosse",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fusse",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fossimo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "fossim",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "fussimo",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "foste",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "fuste",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "fossero",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "fussero",
                "source": "Conjugation",
                "tags": [
                  "archaic",
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "sii",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "essere",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "esser",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sia",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "siamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "siam",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "siate",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "siano",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "plural",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "sian",
                "source": "Conjugation",
                "tags": [
                  "apocopic",
                  "formal",
                  "imperative",
                  "plural",
                  "second-person-semantically",
                  "third-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Italian_verb2(self):
        ret = self.xinfl("torneare", "Italian", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead">&nbsp; &nbsp; Conjugation of <i class="Latn+mention" lang="it">torneare</i></div>
<div class="NavContent">

{| style="background%3A%23F0F0F0%3Bborder-collapse%3Aseparate%3Bborder-spacing%3A2px%3Bwidth%3A100%25" class="inflection-table"

|-

! colspan="1" style="background%3A%23e2e4c0" | <span title="infinito">infinitive</span>


| colspan="1" | <span class="Latn" lang="it">[[torneare#Italian|torneare]]</span>


|-

! colspan="2" style="background%3A%23e2e4c0" | <span title="verbo+ausiliare">auxiliary verb</span>


| colspan="1" | <span class="Latn" lang="it">[[avere#Italian|avere]]</span>


! colspan="2" style="background%3A%23e2e4c0" | <span title="gerundio">gerund</span>


| colspan="2" | <span class="Latn" lang="it">[[torneando#Italian|torneando]]</span>


|-

! colspan="2" style="background%3A%23e2e4c0" |  <span title="participio+presente">present participle</span>


| colspan="1" | <span class="Latn" lang="it">[[torneante#Italian|torneante]]</span>


! colspan="2" style="background%3A%23e2e4c0" | <span title="participio+passato">past participle</span>


| colspan="2" | <span class="Latn" lang="it">[[torneato#Italian|torneato]]</span>


|-

! colspan="1" rowspan="2" style="background%3A%23C0C0C0" | person


! colspan="3" style="background%3A%23C0C0C0" | singular


! colspan="3" style="background%3A%23C0C0C0" | plural


|-

! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | first


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | second


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | third


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | first


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | second


! style="background%3A%23C0C0C0%3Bwidth%3A12.5%25" | third


|-

! style="background%3A%23c0cfe4" colspan="1" | <span title="indicativo">indicative</span>


! style="background%3A%23c0cfe4" | io


! style="background%3A%23c0cfe4" | tu


! style="background%3A%23c0cfe4" | lui/lei, esso/essa


! style="background%3A%23c0cfe4" | noi


! style="background%3A%23c0cfe4" | voi


! style="background%3A%23c0cfe4" | loro, essi/esse


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="presente">present</span>


| <span class="Latn" lang="it">[[torneo#Italian|torneo]]</span>


| <span class="Latn" lang="it">[[tornei#Italian|tornei]]</span>


| <span class="Latn" lang="it">[[tornea#Italian|tornea]]</span>


| <span class="Latn" lang="it">[[torneiamo#Italian|torneiamo]]</span>


| <span class="Latn" lang="it">[[torneate#Italian|torneate]]</span>


| <span class="Latn" lang="it">[[torneano#Italian|torneano]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="imperfetto">imperfect</span>


| <span class="Latn" lang="it">[[torneavo#Italian|torneavo]]</span>


| <span class="Latn" lang="it">[[torneavi#Italian|torneavi]]</span>


| <span class="Latn" lang="it">[[torneava#Italian|torneava]]</span>


| <span class="Latn" lang="it">[[torneavamo#Italian|torneavamo]]</span>


| <span class="Latn" lang="it">[[torneavate#Italian|torneavate]]</span>


| <span class="Latn" lang="it">[[torneavano#Italian|torneavano]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="passato+remoto">past historic</span>


| <span class="Latn" lang="it">[[torneai#Italian|torneai]]</span>


| <span class="Latn" lang="it">[[torneasti#Italian|torneasti]]</span>


| <span class="Latn" lang="it">[[torneò#Italian|torneò]]</span>


| <span class="Latn" lang="it">[[torneammo#Italian|torneammo]]</span>


| <span class="Latn" lang="it">[[torneaste#Italian|torneaste]]</span>


| <span class="Latn" lang="it">[[tornearono#Italian|tornearono]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" colspan="1" | <span title="futuro+semplice">future</span>


| <span class="Latn" lang="it">[[torneerò#Italian|torneerò]]</span>


| <span class="Latn" lang="it">[[torneerai#Italian|torneerai]]</span>


| <span class="Latn" lang="it">[[torneerà#Italian|torneerà]]</span>


| <span class="Latn" lang="it">[[torneeremo#Italian|torneeremo]]</span>


| <span class="Latn" lang="it">[[torneerete#Italian|torneerete]]</span>


| <span class="Latn" lang="it">[[torneeranno#Italian|torneeranno]]</span>


|-

! style="background%3A%23c0d8e4" colspan="1" | <span title="condizionale">conditional</span>


! style="background%3A%23c0d8e4" | io


! style="background%3A%23c0d8e4" | tu


! style="background%3A%23c0d8e4" | lui/lei, esso/essa


! style="background%3A%23c0d8e4" | noi


! style="background%3A%23c0d8e4" | voi


! style="background%3A%23c0d8e4" | loro, essi/esse


|-

! style="height%3A3em%3Bbackground%3A%23c0d8e4" colspan="1" | <span title="condizionale+presente">present</span>


| <span class="Latn" lang="it">[[torneerei#Italian|torneerei]]</span>


| <span class="Latn" lang="it">[[torneeresti#Italian|torneeresti]]</span>


| <span class="Latn" lang="it">[[torneerebbe#Italian|torneerebbe]]</span>


| <span class="Latn" lang="it">[[torneeremmo#Italian|torneeremmo]]</span>


| <span class="Latn" lang="it">[[torneereste#Italian|torneereste]]</span>


| <span class="Latn" lang="it">[[torneerebbero#Italian|torneerebbero]]</span>


|-

! style="background%3A%23c0e4c0" colspan="1" | <span title="congiuntivo">subjunctive</span>


! style="background%3A%23c0e4c0" | che io


! style="background%3A%23c0e4c0" | che tu


! style="background%3A%23c0e4c0" | che lui/che lei, che esso/che essa


! style="background%3A%23c0e4c0" | che noi


! style="background%3A%23c0e4c0" | che voi


! style="background%3A%23c0e4c0" | che loro, che essi/che esse


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="congiuntivo+presente">present</span>


| <span class="Latn" lang="it">[[tornei#Italian|tornei]]</span>


| <span class="Latn" lang="it">[[tornei#Italian|tornei]]</span>


| <span class="Latn" lang="it">[[tornei#Italian|tornei]]</span>


| <span class="Latn" lang="it">[[torneiamo#Italian|torneiamo]]</span>


| <span class="Latn" lang="it">[[torneiate#Italian|torneiate]]</span>


| <span class="Latn" lang="it">[[torneino#Italian|torneino]]</span>


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" rowspan="1" | <span title="congiuntivo+imperfetto">imperfect</span>


| <span class="Latn" lang="it">[[torneassi#Italian|torneassi]]</span>


| <span class="Latn" lang="it">[[torneassi#Italian|torneassi]]</span>


| <span class="Latn" lang="it">[[torneasse#Italian|torneasse]]</span>


| <span class="Latn" lang="it">[[torneassimo#Italian|torneassimo]]</span>


| <span class="Latn" lang="it">[[torneaste#Italian|torneaste]]</span>


| <span class="Latn" lang="it">[[torneassero#Italian|torneassero]]</span>


|-

! colspan="1" rowspan="2" style="height%3A3em%3Bbackground%3A%23e4d4c0" | <span title="imperativo">imperative</span>


! style="background%3A%23e4d4c0" | &mdash;


! style="background%3A%23e4d4c0" | tu


! style="background%3A%23e4d4c0" | Lei


! style="background%3A%23e4d4c0" | noi


! style="background%3A%23e4d4c0" | voi


! style="background%3A%23e4d4c0" | Loro


|-

|


| <span class="Latn" lang="it">[[tornea#Italian|tornea]]</span>, <span class="Latn" lang="it">non [[torneare#Italian|torneare]]</span>


| <span class="Latn" lang="it">[[tornei#Italian|tornei]]</span>


| <span class="Latn" lang="it">[[torneiamo#Italian|torneiamo]]</span>


| <span class="Latn" lang="it">[[torneate#Italian|torneate]]</span>


| <span class="Latn" lang="it">[[torneino#Italian|torneino]]</span>


|-

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
                "form": "torneare",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "avere",
                "source": "Conjugation",
                "tags": [
                  "auxiliary"
                ]
              },
              {
                "form": "torneando",
                "source": "Conjugation",
                "tags": [
                  "gerund"
                ]
              },
              {
                "form": "torneante",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "present"
                ]
              },
              {
                "form": "torneato",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "torneo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "tornei",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "tornea",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "torneiamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "torneate",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "torneano",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "torneavo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "torneavi",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "torneava",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "torneavamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "torneavate",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "torneavano",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "torneai",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "historic",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "torneasti",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "torneò",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "torneammo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "historic",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "torneaste",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "tornearono",
                "source": "Conjugation",
                "tags": [
                  "historic",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "torneerò",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "torneerai",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "torneerà",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "torneeremo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "torneerete",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "torneeranno",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "torneerei",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "torneeresti",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "torneerebbe",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "torneeremmo",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "torneereste",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "torneerebbero",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "tornei",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "tornei",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "tornei",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "torneiamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "torneiate",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "torneino",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "torneassi",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "torneassi",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "torneasse",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "torneassimo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "torneaste",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "torneassero",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "tornea",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "torneare",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "tornei",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "second-person-semantically",
                  "singular",
                  "third-person",
                ]
              },
              {
                "form": "torneiamo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "torneate",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "torneino",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "plural",
                  "second-person-semantically",
                  "third-person",
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)
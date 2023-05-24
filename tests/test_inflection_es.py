# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021, 2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
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

    def test_Spanish_verb1(self):
        ret = self.xinfl("interdecir", "Spanish", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead" align="center">&nbsp; &nbsp; Conjugation of <i class="Latn+mention" lang="es">[[interdecir#Spanish|interdecir]]</i> (irregular; e-i alternation) (See [[Appendix:Spanish verbs]])</div>
<div class="NavContent">

{| style="background%3A%23F9F9F9%3Btext-align%3Acenter%3Bwidth%3A100%25"

|-

! colspan="3" style="background%3A%23e2e4c0" | <span title="infinitivo">infinitive</span>


| colspan="5" | <span class="Latn+form-of+lang-es+inf-form-of++++origin-interdecir+++" lang="es">[[interdecir#Spanish|interdecir]]</span>



|-

! colspan="3" style="background%3A%23e2e4c0" | <span title="gerundio">gerund</span>


| colspan="5" | <span class="Latn+form-of+lang-es+ger-form-of++++origin-interdecir+++" lang="es">[[interdiciendo#Spanish|interdiciendo]]</span>



|-

! rowspan="3" colspan="2" style="background%3A%23e2e4c0" | <span title="participio+%28pasado%29">past participle</span>


| colspan="2" style="background%3A%23e2e4c0" |


! colspan="2" style="background%3A%23e2e4c0" | <span title="masculino">masculine</span>


! colspan="2" style="background%3A%23e2e4c0" | <span title="femenino">feminine</span>


|-

! colspan="2" style="background%3A%23e2e4c0" | singular


| colspan="2" | <span class="Latn+form-of+lang-es+m%7Cs%7Cpast%7Cpart-form-of++++origin-interdecir+++" lang="es">[[interdicho#Spanish|interdicho]]</span>


| colspan="2" | <span class="Latn+form-of+lang-es+f%7Cs%7Cpast%7Cpart-form-of++++origin-interdecir+++" lang="es">[[interdicha#Spanish|interdicha]]</span>


|-

! colspan="2" style="background%3A%23e2e4c0" | plural


| colspan="2" | <span class="Latn+form-of+lang-es+m%7Cp%7Cpast%7Cpart-form-of++++origin-interdecir+++" lang="es">[[interdichos#Spanish|interdichos]]</span>


| colspan="2" | <span class="Latn+form-of+lang-es+f%7Cp%7Cpast%7Cpart-form-of++++origin-interdecir+++" lang="es">[[interdichas#Spanish|interdichas]]</span>



|-

! colspan="2" rowspan="2" style="background%3A%23DEDEDE" |


! colspan="3" style="background%3A%23DEDEDE" | singular


! colspan="3" style="background%3A%23DEDEDE" | plural



|-

! style="background%3A%23DEDEDE" | 1st person


! style="background%3A%23DEDEDE" | 2nd person


! style="background%3A%23DEDEDE" | 3rd person


! style="background%3A%23DEDEDE" | 1st person


! style="background%3A%23DEDEDE" | 2nd person


! style="background%3A%23DEDEDE" | 3rd person



|-

! rowspan="6" style="background%3A%23c0cfe4" | <span title="indicativo">indicative</span>



! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" |


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | yo


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | tú<br>vos


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | él/ella/ello<br>usted


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | nosotros<br>nosotras


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | vosotros<br>vosotras


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | ellos/ellas<br>ustedes



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="presente+de+indicativo">present</span>


| <span class="Latn+form-of+lang-es+1%7Cs%7Cpres%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdigo#Spanish|interdigo]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cpres%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdices#Spanish|interdices]]</span><sup><sup>tú</sup></sup><br><span class="Latn+form-of+lang-es+2%7Cs%7Cvoseo%7Cpres%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecís#Spanish|interdecís]]</span><sup><sup>vos</sup></sup>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cpres%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdice#Spanish|interdice]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cpres%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecimos#Spanish|interdecimos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cpres%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecís#Spanish|interdecís]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cpres%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdicen#Spanish|interdicen]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+imperfecto+%28copr%C3%A9terito%29">imperfect</span>


| <span class="Latn+form-of+lang-es+1%7Cs%7Cimpf%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecía#Spanish|interdecía]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cimpf%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecías#Spanish|interdecías]]</span>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cimpf%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecía#Spanish|interdecía]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cimpf%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecíamos#Spanish|interdecíamos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cimpf%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecíais#Spanish|interdecíais]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cimpf%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdecían#Spanish|interdecían]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+perfecto+simple+%28pret%C3%A9rito+indefinido%29">preterite</span>


| <span class="Latn+form-of+lang-es+1%7Cs%7Cpret%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdije#Spanish|interdije]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cpret%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdijiste#Spanish|interdijiste]]</span>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cpret%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdijo#Spanish|interdijo]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cpret%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdijimos#Spanish|interdijimos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cpret%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdijisteis#Spanish|interdijisteis]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cpret%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdijeron#Spanish|interdijeron]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="futuro+simple+%28futuro+imperfecto%29">future</span>


| <span class="Latn+form-of+lang-es+1%7Cs%7Cfut%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdiré#Spanish|interdiré]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cfut%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdirás#Spanish|interdirás]]</span>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cfut%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdirá#Spanish|interdirá]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cfut%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdiremos#Spanish|interdiremos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cfut%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdiréis#Spanish|interdiréis]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cfut%7Cind-form-of++++origin-interdecir+++" lang="es">[[interdirán#Spanish|interdirán]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="condicional+simple+%28pospret%C3%A9rito+de+modo+indicativo%29">conditional</span>


| <span class="Latn+form-of+lang-es+1%7Cs%7Ccond-form-of++++origin-interdecir+++" lang="es">[[interdiría#Spanish|interdiría]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Ccond-form-of++++origin-interdecir+++" lang="es">[[interdirías#Spanish|interdirías]]</span>


| <span class="Latn+form-of+lang-es+3%7Cs%7Ccond-form-of++++origin-interdecir+++" lang="es">[[interdiría#Spanish|interdiría]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Ccond-form-of++++origin-interdecir+++" lang="es">[[interdiríamos#Spanish|interdiríamos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Ccond-form-of++++origin-interdecir+++" lang="es">[[interdiríais#Spanish|interdiríais]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Ccond-form-of++++origin-interdecir+++" lang="es">[[interdirían#Spanish|interdirían]]</span>



|-

! style="background%3A%23DEDEDE%3Bheight%3A.75em" colspan="8" |


|-

! rowspan="5" style="background%3A%23c0e4c0" | <span title="subjuntivo">subjunctive</span>


! style="background%3A%23ECECEC" |


! style="background%3A%23ECECEC" | yo


! style="background%3A%23ECECEC" | tú<br>vos


! style="background%3A%23ECECEC" | él/ella/ello<br>usted


! style="background%3A%23ECECEC" | nosotros<br>nosotras


! style="background%3A%23ECECEC" | vosotros<br>vosotras


! style="background%3A%23ECECEC" | ellos/ellas<br>ustedes



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="presente+de+subjuntivo">present</span>


| <span class="Latn+form-of+lang-es+1%7Cs%7Cpres%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdiga#Spanish|interdiga]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cpres%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdigas#Spanish|interdigas]]</span><sup><sup>tú</sup></sup><br><span class="Latn+form-of+lang-es+2%7Cs%7Cvoseo%7Cpres%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdigás#Spanish|interdigás]]</span><sup><sup>vos<sup style="color%3Ared">2</sup></sup></sup>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cpres%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdiga#Spanish|interdiga]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cpres%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdigamos#Spanish|interdigamos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cpres%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdigáis#Spanish|interdigáis]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cpres%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdigan#Spanish|interdigan]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+imperfecto+de+subjuntivo">imperfect</span><br>(ra)


| <span class="Latn+form-of+lang-es+1%7Cs%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijera#Spanish|interdijera]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijeras#Spanish|interdijeras]]</span>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijera#Spanish|interdijera]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijéramos#Spanish|interdijéramos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijerais#Spanish|interdijerais]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijeran#Spanish|interdijeran]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+imperfecto+de+subjuntivo">imperfect</span><br>(se)


| <span class="Latn+form-of+lang-es+1%7Cs%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijese#Spanish|interdijese]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijeses#Spanish|interdijeses]]</span>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijese#Spanish|interdijese]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijésemos#Spanish|interdijésemos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijeseis#Spanish|interdijeseis]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cimpf%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijesen#Spanish|interdijesen]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="futuro+simple+de+subjuntivo+%28futuro+de+subjuntivo%29">future</span><sup style="color%3Ared">1</sup>


| <span class="Latn+form-of+lang-es+1%7Cs%7Cfut%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijere#Spanish|interdijere]]</span>


| <span class="Latn+form-of+lang-es+2%7Cs%7Cfut%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijeres#Spanish|interdijeres]]</span>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cfut%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijere#Spanish|interdijere]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cfut%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijéremos#Spanish|interdijéremos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cfut%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijereis#Spanish|interdijereis]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cfut%7Csub-form-of++++origin-interdecir+++" lang="es">[[interdijeren#Spanish|interdijeren]]</span>



|-

! style="background%3A%23DEDEDE%3Bheight%3A.75em" colspan="8" |


|-

! rowspan="6" style="background%3A%23e4d4c0" | <span title="imperativo">imperative</span>


! style="background%3A%23ECECEC" |


! style="background%3A%23ECECEC" | —


! style="background%3A%23ECECEC" | tú<br>vos


! style="background%3A%23ECECEC" | usted


! style="background%3A%23ECECEC" | nosotros<br>nosotras


! style="background%3A%23ECECEC" | vosotros<br>vosotras


! style="background%3A%23ECECEC" | ustedes



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="imperativo+afirmativo">affirmative</span>


|


| <span class="Latn+form-of+lang-es+2%7Cs%7Cimp-form-of++++origin-interdecir+++" lang="es">[[interdice#Spanish|interdice]]</span><sup><sup>tú</sup></sup><br><span class="Latn+form-of+lang-es+2%7Cs%7Cvoseo%7Cimp-form-of++++origin-interdecir+++" lang="es">[[interdecí#Spanish|interdecí]]</span><sup><sup>vos</sup></sup>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cimp-form-of++++origin-interdecir+++" lang="es">[[interdiga#Spanish|interdiga]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cimp-form-of++++origin-interdecir+++" lang="es">[[interdigamos#Spanish|interdigamos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cimp-form-of++++origin-interdecir+++" lang="es">[[interdecid#Spanish|interdecid]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cimp-form-of++++origin-interdecir+++" lang="es">[[interdigan#Spanish|interdigan]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="imperativo+negativo">negative</span>


|


| <span class="Latn" lang="es">[[no#Spanish|no]] [[interdigas#Spanish|interdigas]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[interdiga#Spanish|interdiga]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[interdigamos#Spanish|interdigamos]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[interdigáis#Spanish|interdigáis]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[interdigan#Spanish|interdigan]]</span>


|}
<div style="width%3A100%25%3Btext-align%3Aleft%3Bbackground%3A%23d9ebff">
<div style="display%3Ainline-block%3Btext-align%3Aleft%3Bpadding-left%3A1em%3Bpadding-right%3A1em">
<sup style="color%3A+red">1</sup>Mostly obsolete form, now mainly used in legal jargon.<br><sup style="color%3A+red">2</sup>Argentine and Uruguayan <i class="Latn+mention" lang="es">[[voseo#Spanish|voseo]]</i> prefers the <i class="Latn+mention" lang="es">[[tú#Spanish|tú]]</i> form for the present subjunctive.
</div></div>
</div></div>
[[Category:Spanish verbs ending in -ir|INTERDECIR]][[Category:Spanish irregular verbs|INTERDECIR]][[Category:Spanish verbs with e-i alternation|INTERDECIR]]
""")
        expected = {
            "forms": [
              {
                  "form": "irregular",
                  "source": "Conjugation",
                  "tags": ["table-tags"],
              },
              {
                  "form": "e-i alternation",
                  "source": "Conjugation",
                  "tags": ["class"],
              },
              {
                "form": "interdecir",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "interdiciendo",
                "source": "Conjugation",
                "tags": [
                  "gerund"
                ]
              },
              {
                "form": "interdicho",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "participle",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "interdicha",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "participle",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "interdichos",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "participle",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "interdichas",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "participle",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "interdigo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "interdices",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "interdecís",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "present",
                  "second-person",
                  "singular",
                  "vos-form"
                ]
              },
              {
                "form": "interdice",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdecimos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "interdecís",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "interdicen",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "interdecía",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "interdecías",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "interdecía",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdecíamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "interdecíais",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "interdecían",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "interdije",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "preterite",
                  "singular"
                ]
              },
              {
                "form": "interdijiste",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "interdijo",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdijimos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "preterite"
                ]
              },
              {
                "form": "interdijisteis",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "second-person"
                ]
              },
              {
                "form": "interdijeron",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "third-person"
                ]
              },
              {
                "form": "interdiré",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "interdirás",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "interdirá",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdiremos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "interdiréis",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "interdirán",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "interdiría",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "interdirías",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "interdiría",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdiríamos",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "interdiríais",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "interdirían",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "interdiga",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdigas",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdigás",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive",
                  "vos-form"
                ]
              },
              {
                "form": "interdiga",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdigamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "interdigáis",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "interdigan",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdijera",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijeras",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijera",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdijéramos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijerais",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijeran",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdijese",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "imperfect-se",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijeses",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijese",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdijésemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "imperfect-se",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijeseis",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijesen",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdijere",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijeres",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijere",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdijéremos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijereis",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "interdijeren",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "interdice",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "informal",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "interdecí",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "informal",
                  "second-person",
                  "singular",
                  "vos-form"
                ]
              },
              {
                "form": "interdiga",
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
                "form": "interdiga",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdigamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "interdecid",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "interdigan",
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
                "form": "interdigan",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "interdigas",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "interdiga",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "negative",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdiga",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "interdigamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "negative",
                  "plural"
                ]
              },
              {
                "form": "interdigáis",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "interdigan",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "negative",
                  "plural",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "interdigan",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "third-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Spanish_verb2(self):
        # This has ^vos^2 in second-person singular subjunctive
        ret = self.xinfl("apoltronarse", "Spanish", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead" align="center">&nbsp; &nbsp; Conjugation of <i class="Latn+mention" lang="es">[[apoltronarse#Spanish|apoltronarse]]</i> (See [[Appendix:Spanish verbs]])</div>
<div class="NavContent">

{| style="background%3A%23F9F9F9%3Btext-align%3Acenter%3Bwidth%3A100%25"

|-

! colspan="3" style="background%3A%23e2e4c0" | <span title="infinitivo">infinitive</span>


| colspan="5" | <span class="Latn+form-of+lang-es+inf-form-of++++origin-apoltronarse+++" lang="es">[[apoltronarse#Spanish|apoltronarse]]</span>



|-

! colspan="3" style="background%3A%23e2e4c0" | <span title="gerundio">gerund</span>


| colspan="5" | <span class="Latn+form-of+lang-es+ger-form-of++++origin-apoltronarse+++" lang="es">[[apoltronándose#Spanish|apoltronándose]]</span>



|-

! rowspan="3" colspan="2" style="background%3A%23e2e4c0" | <span title="participio+%28pasado%29">past participle</span>


| colspan="2" style="background%3A%23e2e4c0" |


! colspan="2" style="background%3A%23e2e4c0" | <span title="masculino">masculine</span>


! colspan="2" style="background%3A%23e2e4c0" | <span title="femenino">feminine</span>


|-

! colspan="2" style="background%3A%23e2e4c0" | singular


| colspan="2" | <span class="Latn+form-of+lang-es+m%7Cs%7Cpast%7Cpart-form-of++++origin-apoltronarse+++" lang="es">[[apoltronado#Spanish|apoltronado]]</span>


| colspan="2" | <span class="Latn+form-of+lang-es+f%7Cs%7Cpast%7Cpart-form-of++++origin-apoltronarse+++" lang="es">[[apoltronada#Spanish|apoltronada]]</span>


|-

! colspan="2" style="background%3A%23e2e4c0" | plural


| colspan="2" | <span class="Latn+form-of+lang-es+m%7Cp%7Cpast%7Cpart-form-of++++origin-apoltronarse+++" lang="es">[[apoltronados#Spanish|apoltronados]]</span>


| colspan="2" | <span class="Latn+form-of+lang-es+f%7Cp%7Cpast%7Cpart-form-of++++origin-apoltronarse+++" lang="es">[[apoltronadas#Spanish|apoltronadas]]</span>



|-

! colspan="2" rowspan="2" style="background%3A%23DEDEDE" |


! colspan="3" style="background%3A%23DEDEDE" | singular


! colspan="3" style="background%3A%23DEDEDE" | plural



|-

! style="background%3A%23DEDEDE" | 1st person


! style="background%3A%23DEDEDE" | 2nd person


! style="background%3A%23DEDEDE" | 3rd person


! style="background%3A%23DEDEDE" | 1st person


! style="background%3A%23DEDEDE" | 2nd person


! style="background%3A%23DEDEDE" | 3rd person



|-

! rowspan="6" style="background%3A%23c0cfe4" | <span title="indicativo">indicative</span>



! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" |


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | yo


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | tú<br>vos


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | él/ella/ello<br>usted


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | nosotros<br>nosotras


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | vosotros<br>vosotras


! style="background%3A%23ECECEC%3Bwidth%3A12.5%25" | ellos/ellas<br>ustedes



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="presente+de+indicativo">present</span>


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltrono#Spanish|apoltrono]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronas#Spanish|apoltronas]]</span><sup><sup>tú</sup></sup><br><span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronás#Spanish|apoltronás]]</span><sup><sup>vos</sup></sup>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltrona#Spanish|apoltrona]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronamos#Spanish|apoltronamos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronáis#Spanish|apoltronáis]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronan#Spanish|apoltronan]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+imperfecto+%28copr%C3%A9terito%29">imperfect</span>


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltronaba#Spanish|apoltronaba]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronabas#Spanish|apoltronabas]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronaba#Spanish|apoltronaba]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronábamos#Spanish|apoltronábamos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronabais#Spanish|apoltronabais]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronaban#Spanish|apoltronaban]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+perfecto+simple+%28pret%C3%A9rito+indefinido%29">preterite</span>


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltroné#Spanish|apoltroné]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronaste#Spanish|apoltronaste]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronó#Spanish|apoltronó]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronamos#Spanish|apoltronamos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronasteis#Spanish|apoltronasteis]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronaron#Spanish|apoltronaron]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="futuro+simple+%28futuro+imperfecto%29">future</span>


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltronaré#Spanish|apoltronaré]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronarás#Spanish|apoltronarás]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronará#Spanish|apoltronará]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronaremos#Spanish|apoltronaremos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronaréis#Spanish|apoltronaréis]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronarán#Spanish|apoltronarán]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="condicional+simple+%28pospret%C3%A9rito+de+modo+indicativo%29">conditional</span>


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltronaría#Spanish|apoltronaría]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronarías#Spanish|apoltronarías]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronaría#Spanish|apoltronaría]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronaríamos#Spanish|apoltronaríamos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronaríais#Spanish|apoltronaríais]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronarían#Spanish|apoltronarían]]</span>



|-

! style="background%3A%23DEDEDE%3Bheight%3A.75em" colspan="8" |


|-

! rowspan="5" style="background%3A%23c0e4c0" | <span title="subjuntivo">subjunctive</span>


! style="background%3A%23ECECEC" |


! style="background%3A%23ECECEC" | yo


! style="background%3A%23ECECEC" | tú<br>vos


! style="background%3A%23ECECEC" | él/ella/ello<br>usted


! style="background%3A%23ECECEC" | nosotros<br>nosotras


! style="background%3A%23ECECEC" | vosotros<br>vosotras


! style="background%3A%23ECECEC" | ellos/ellas<br>ustedes



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="presente+de+subjuntivo">present</span>


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltrone#Spanish|apoltrone]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltrones#Spanish|apoltrones]]</span><sup><sup>tú</sup></sup><br><span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronés#Spanish|apoltronés]]</span><sup><sup>vos<sup style="color%3Ared">2</sup></sup></sup>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltrone#Spanish|apoltrone]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronemos#Spanish|apoltronemos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronéis#Spanish|apoltronéis]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronen#Spanish|apoltronen]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+imperfecto+de+subjuntivo">imperfect</span><br>(ra)


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltronara#Spanish|apoltronara]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronaras#Spanish|apoltronaras]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronara#Spanish|apoltronara]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronáramos#Spanish|apoltronáramos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronarais#Spanish|apoltronarais]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronaran#Spanish|apoltronaran]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="pret%C3%A9rito+imperfecto+de+subjuntivo">imperfect</span><br>(se)


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltronase#Spanish|apoltronase]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronases#Spanish|apoltronases]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronase#Spanish|apoltronase]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronásemos#Spanish|apoltronásemos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronaseis#Spanish|apoltronaseis]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronasen#Spanish|apoltronasen]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="futuro+simple+de+subjuntivo+%28futuro+de+subjuntivo%29">future</span><sup style="color%3Ared">1</sup>


| <span class="Latn" lang="es">[[me#Spanish|me]] [[apoltronare#Spanish|apoltronare]]</span>


| <span class="Latn" lang="es">[[te#Spanish|te]] [[apoltronares#Spanish|apoltronares]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronare#Spanish|apoltronare]]</span>


| <span class="Latn" lang="es">[[nos#Spanish|nos]] [[apoltronáremos#Spanish|apoltronáremos]]</span>


| <span class="Latn" lang="es">[[os#Spanish|os]] [[apoltronareis#Spanish|apoltronareis]]</span>


| <span class="Latn" lang="es">[[se#Spanish|se]] [[apoltronaren#Spanish|apoltronaren]]</span>



|-

! style="background%3A%23DEDEDE%3Bheight%3A.75em" colspan="8" |


|-

! rowspan="6" style="background%3A%23e4d4c0" | <span title="imperativo">imperative</span>


! style="background%3A%23ECECEC" |


! style="background%3A%23ECECEC" | —


! style="background%3A%23ECECEC" | tú<br>vos


! style="background%3A%23ECECEC" | usted


! style="background%3A%23ECECEC" | nosotros<br>nosotras


! style="background%3A%23ECECEC" | vosotros<br>vosotras


! style="background%3A%23ECECEC" | ustedes



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="imperativo+afirmativo">affirmative</span>


|


| <span class="Latn+form-of+lang-es+2%7Cs%7Cimp-form-of++++origin-apoltronarse+++" lang="es">[[apoltrónate#Spanish|apoltrónate]]</span><sup><sup>tú</sup></sup><br><span class="Latn+form-of+lang-es+2%7Cs%7Cvoseo%7Cimp-form-of++++origin-apoltronarse+++" lang="es">[[apoltronate#Spanish|apoltronate]]</span><sup><sup>vos</sup></sup>


| <span class="Latn+form-of+lang-es+3%7Cs%7Cimp-form-of++++origin-apoltronarse+++" lang="es">[[apoltrónese#Spanish|apoltrónese]]</span>


| <span class="Latn+form-of+lang-es+1%7Cp%7Cimp-form-of++++origin-apoltronarse+++" lang="es">[[apoltronémonos#Spanish|apoltronémonos]]</span>


| <span class="Latn+form-of+lang-es+2%7Cp%7Cimp-form-of++++origin-apoltronarse+++" lang="es">[[apoltronaos#Spanish|apoltronaos]]</span>


| <span class="Latn+form-of+lang-es+3%7Cp%7Cimp-form-of++++origin-apoltronarse+++" lang="es">[[apoltrónense#Spanish|apoltrónense]]</span>



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | <span title="imperativo+negativo">negative</span>


|


| <span class="Latn" lang="es">[[no#Spanish|no]] [[te#Spanish|te]] [[apoltrones#Spanish|apoltrones]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[se#Spanish|se]] [[apoltrone#Spanish|apoltrone]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[nos#Spanish|nos]] [[apoltronemos#Spanish|apoltronemos]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[os#Spanish|os]] [[apoltronéis#Spanish|apoltronéis]]</span>


| <span class="Latn" lang="es">[[no#Spanish|no]] [[se#Spanish|se]] [[apoltronen#Spanish|apoltronen]]</span>


|}
<div style="width%3A100%25%3Btext-align%3Aleft%3Bbackground%3A%23d9ebff">
<div style="display%3Ainline-block%3Btext-align%3Aleft%3Bpadding-left%3A1em%3Bpadding-right%3A1em">
<sup style="color%3A+red">1</sup>Mostly obsolete form, now mainly used in legal jargon.<br><sup style="color%3A+red">2</sup>Argentine and Uruguayan <i class="Latn+mention" lang="es">[[voseo#Spanish|voseo]]</i> prefers the <i class="Latn+mention" lang="es">[[tú#Spanish|tú]]</i> form for the present subjunctive.
</div></div>
</div></div>
<div class="NavFrame">
<div class="NavHead" align="center">&nbsp; &nbsp; Selected combined forms of <i class="Latn+mention" lang="es">[[apoltronarse#Spanish|apoltronarse]]</i></div>
<div class="NavContent">

{| class="inflection-table" style="background%3A%23F9F9F9%3Btext-align%3Acenter%3Bwidth%3A100%25"

|-

! colspan="2" rowspan="2" style="background%3A%23DEDEDE" |


! colspan="3" style="background%3A%23DEDEDE" | singular


! colspan="3" style="background%3A%23DEDEDE" | plural



|-

! style="background%3A%23DEDEDE" | 1st person


! style="background%3A%23DEDEDE" | 2nd person


! style="background%3A%23DEDEDE" | 3rd person


! style="background%3A%23DEDEDE" | 1st person


! style="background%3A%23DEDEDE" | 2nd person


! style="background%3A%23DEDEDE" | 3rd person



|-

! rowspan="2" style="background%3A%23c0cfe4" | Infinitives



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | accusative


| <span class="Latn+form-of+lang-es+me%7Cinf%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronarme#Spanish|apoltronarme]]</span>


| <span class="Latn+form-of+lang-es+te%7Cinf%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronarte#Spanish|apoltronarte]]</span>


| <span class="Latn+form-of+lang-es+se%7Cinf%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronarse#Spanish|apoltronarse]]</span>


| <span class="Latn+form-of+lang-es+nos%7Cinf%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronarnos#Spanish|apoltronarnos]]</span>


| <span class="Latn+form-of+lang-es+os%7Cinf%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronaros#Spanish|apoltronaros]]</span>


| <span class="Latn+form-of+lang-es+se%7Cinf%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronarse#Spanish|apoltronarse]]</span>



|-

! style="background%3A%23DEDEDE%3Bheight%3A.35em" colspan="8" |


|-

! rowspan="2" style="background%3A%23d0cfa4" | gerunds



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | accusative


| <span class="Latn+form-of+lang-es+me%7Cgerund%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronándome#Spanish|apoltronándome]]</span>


| <span class="Latn+form-of+lang-es+te%7Cgerund%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronándote#Spanish|apoltronándote]]</span>


| <span class="Latn+form-of+lang-es+se%7Cgerund%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronándose#Spanish|apoltronándose]]</span>


| <span class="Latn+form-of+lang-es+nos%7Cgerund%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronándonos#Spanish|apoltronándonos]]</span>


| <span class="Latn+form-of+lang-es+os%7Cgerund%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronándoos#Spanish|apoltronándoos]]</span>


| <span class="Latn+form-of+lang-es+se%7Cgerund%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronándose#Spanish|apoltronándose]]</span>



|-

! style="background%3A%23DEDEDE%3Bheight%3A.35em" colspan="8" |


|-

! rowspan="2" style="background%3A%23f2caa4" | with positive imperatives



|-

! style="height%3A3em%3Bbackground%3A%23ECECEC" | accusative


| ''not used''


| <span class="Latn+form-of+lang-es+te%7Cimp%7C2s%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltrónate#Spanish|apoltrónate]]</span>


| <span class="Latn+form-of+lang-es+se%7Cimp%7C3s%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltrónese#Spanish|apoltrónese]]</span>


| <span class="Latn+form-of+lang-es+nos%7Cimp%7C1p%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronémonos#Spanish|apoltronémonos]]</span>


| <span class="Latn+form-of+lang-es+os%7Cimp%7C2p%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltronaos#Spanish|apoltronaos]]</span>


| <span class="Latn+form-of+lang-es+se%7Cimp%7C3p%7Ccombined-form-of++++origin-apoltronarse+++" lang="es">[[apoltrónense#Spanish|apoltrónense]]</span>


|}
</div></div>
[[Category:Spanish verbs ending in -ar|APOLTRONARSE]][[Category:Spanish reflexive verbs|APOLTRONARSE]]
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
                "form": "apoltronarse",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "apoltronándose",
                "source": "Conjugation",
                "tags": [
                  "gerund"
                ]
              },
              {
                "form": "apoltronado",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "participle",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "apoltronada",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "participle",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "apoltronados",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "participle",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "apoltronadas",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "participle",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "me apoltrono",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "te apoltronas",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "te apoltronás",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "informal",
                  "present",
                  "second-person",
                  "singular",
                  "vos-form"
                ]
              },
              {
                "form": "se apoltrona",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "os apoltronáis",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "se apoltronan",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "me apoltronaba",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "te apoltronabas",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "se apoltronaba",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronábamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "os apoltronabais",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "se apoltronaban",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "me apoltroné",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "preterite",
                  "singular"
                ]
              },
              {
                "form": "te apoltronaste",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "se apoltronó",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "preterite"
                ]
              },
              {
                "form": "os apoltronasteis",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "second-person"
                ]
              },
              {
                "form": "se apoltronaron",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "third-person"
                ]
              },
              {
                "form": "me apoltronaré",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "te apoltronarás",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "se apoltronará",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronaremos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "os apoltronaréis",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "se apoltronarán",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "me apoltronaría",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "te apoltronarías",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "se apoltronaría",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronaríamos",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "os apoltronaríais",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "se apoltronarían",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "me apoltrone",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "te apoltrones",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "te apoltronés",
                "source": "Conjugation",
                "tags": [
                  "informal",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive",
                  "vos-form"
                ]
              },
              {
                "form": "se apoltrone",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "os apoltronéis",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "se apoltronen",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "me apoltronara",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "te apoltronaras",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "se apoltronara",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronáramos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "os apoltronarais",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "se apoltronaran",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "me apoltronase",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "imperfect-se",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "te apoltronases",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "se apoltronase",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronásemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "imperfect-se",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "os apoltronaseis",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "se apoltronasen",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "imperfect-se",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "me apoltronare",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "te apoltronares",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "se apoltronare",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronáremos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "os apoltronareis",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "se apoltronaren",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "apoltrónate",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "informal",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "apoltronate",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "informal",
                  "second-person",
                  "singular",
                  "vos-form"
                ]
              },
              {
                "form": "apoltrónese",
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
                "form": "apoltrónese",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "apoltronémonos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "apoltronaos",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "apoltrónense",
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
                "form": "apoltrónense",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "te apoltrones",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "se apoltrone",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "negative",
                  "second-person-semantically",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "se apoltrone",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nos apoltronemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "negative",
                  "plural"
                ]
              },
              {
                "form": "os apoltronéis",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "se apoltronen",
                "source": "Conjugation",
                "tags": [
                  "formal",
                  "imperative",
                  "negative",
                  "plural",
                  "second-person-semantically",
                  "third-person"
                ]
              },
              {
                "form": "se apoltronen",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "third-person"
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
                "form": "apoltronarme",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "infinitive",
                  "object-first-person",
                  "object-singular"
                ]
              },
              {
                "form": "apoltronarte",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "infinitive",
                  "object-second-person",
                  "object-singular"
                ]
              },
              {
                "form": "apoltronarse",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "infinitive",
                  "object-singular",
                  "object-third-person"
                ]
              },
              {
                "form": "apoltronarnos",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "infinitive",
                  "object-first-person",
                  "object-plural"
                ]
              },
              {
                "form": "apoltronaros",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "infinitive",
                  "object-plural",
                  "object-second-person"
                ]
              },
              {
                "form": "apoltronarse",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "infinitive",
                  "object-plural",
                  "object-third-person"
                ]
              },
              {
                "form": "apoltronándome",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "gerund",
                  "object-first-person",
                  "object-singular"
                ]
              },
              {
                "form": "apoltronándote",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "gerund",
                  "object-second-person",
                  "object-singular"
                ]
              },
              {
                "form": "apoltronándose",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "gerund",
                  "object-singular",
                  "object-third-person"
                ]
              },
              {
                "form": "apoltronándonos",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "gerund",
                  "object-first-person",
                  "object-plural"
                ]
              },
              {
                "form": "apoltronándoos",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "gerund",
                  "object-plural",
                  "object-second-person"
                ]
              },
              {
                "form": "apoltronándose",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "gerund",
                  "object-plural",
                  "object-third-person"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['accusative',
                        'combined-form',
                        'object-first-person',
                        'object-singular',
                        'with-positive-imperative']},
              {
                "form": "apoltrónate",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "object-second-person",
                  "object-singular",
                  "with-positive-imperative"
                ]
              },
              {
                "form": "apoltrónese",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "object-singular",
                  "object-third-person",
                  "with-positive-imperative"
                ]
              },
              {
                "form": "apoltronémonos",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "object-first-person",
                  "object-plural",
                  "with-positive-imperative"
                ]
              },
              {
                "form": "apoltronaos",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "object-plural",
                  "object-second-person",
                  "with-positive-imperative"
                ]
              },
              {
                "form": "apoltrónense",
                "source": "Conjugation",
                "tags": [
                  "accusative",
                  "combined-form",
                  "object-plural",
                  "object-third-person",
                  "with-positive-imperative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

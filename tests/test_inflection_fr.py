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

    def test_French_verb1(self):
        ret = self.xinfl("avoir", "French", "verb", "Conjugation", """
<div class="NavFrame" style="clear%3Aboth">
<div class="NavHead" align="left">Conjugation of ''avoir'' <span style="font-size%3A90%25%3B">(see also [[Appendix:French verbs]])</span></div>
<div class="NavContent" align="center">

{| style="background%3A%23F0F0F0%3Bwidth%3A100%25%3Bborder-collapse%3Aseparate%3Bborder-spacing%3A2px" class="inflection-table"

|-

! colspan="1" rowspan="2" style="background%3A%23e2e4c0" | <span title="infinitif">infinitive</span>


! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>simple</small>


| avoir


|-

! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>compound</small>


! colspan="6" style="background%3A%23DEDEDE" | <i>[[avoir]]</i> + past participle


|-

! colspan="1" rowspan="2" style="background%3A%23e2e4c0" | <span title="participe+pr%C3%A9sent">present participle</span> or <span title>gerund</span><sup>1</sup>


! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>simple</small>


| <span class="Latn+form-of+lang-fr+ppr-form-of+++++++" lang="fr">[[ayant#French|ayant]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ.jɑ̃/</span></span>


|-

! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>compound</small>


! colspan="6" style="background%3A%23DEDEDE" | <i>[[ayant]]</i> + past participle


|-

! colspan="2" style="background%3A%23e2e4c0" | <span title="participe+pass%C3%A9">past participle</span>


| <span class="Latn+form-of+lang-fr+pp-form-of+++++++" lang="fr">[[eu#French|eu]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/y/</span></span>


|-

! colspan="2" rowspan="2" |


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

! style="background%3A%23c0cfe4" colspan="2" | <span title="indicatif">indicative</span>


! style="background%3A%23c0cfe4" | je (j’)


! style="background%3A%23c0cfe4" | tu


! style="background%3A%23c0cfe4" | il, elle


! style="background%3A%23c0cfe4" | nous


! style="background%3A%23c0cfe4" | vous


! style="background%3A%23c0cfe4" | ils, elles


|-

! rowspan="5" style="background%3A%23c0cfe4" | <small>(simple<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pr%C3%A9sent">present</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[ai#French|ai]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/e/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[as#French|as]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[a#French|a]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[avons#French|avons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.vɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[avez#French|avez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.ve/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[ont#French|ont]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɔ̃/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="imparfait">imperfect</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[avais#French|avais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.vɛ/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[avais#French|avais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.vɛ/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[avait#French|avait]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.vɛ/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[avions#French|avions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.vjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[aviez#French|aviez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.vje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[avaient#French|avaient]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/a.vɛ/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+simple">past historic</span><sup>2</sup>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cphis-form-of+++++++" lang="fr">[[eus#French|eus]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/y/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cphis-form-of+++++++" lang="fr">[[eus#French|eus]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/y/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cphis-form-of+++++++" lang="fr">[[eut#French|eut]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/y/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cphis-form-of+++++++" lang="fr">[[eûmes#French|eûmes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ym/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cphis-form-of+++++++" lang="fr">[[eûtes#French|eûtes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/yt/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cphis-form-of+++++++" lang="fr">[[eurent#French|eurent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/yʁ/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="futur+simple">future</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cfutr-form-of+++++++" lang="fr">[[aurai#French|aurai]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁe/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cfutr-form-of+++++++" lang="fr">[[auras#French|auras]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁa/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cfutr-form-of+++++++" lang="fr">[[aura#French|aura]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁa/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cfutr-form-of+++++++" lang="fr">[[aurons#French|aurons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cfutr-form-of+++++++" lang="fr">[[aurez#French|aurez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁe/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cfutr-form-of+++++++" lang="fr">[[auront#French|auront]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁɔ̃/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="conditionnel+pr%C3%A9sent">conditional</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Ccond-form-of+++++++" lang="fr">[[aurais#French|aurais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Ccond-form-of+++++++" lang="fr">[[aurais#French|aurais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Ccond-form-of+++++++" lang="fr">[[aurait#French|aurait]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Ccond-form-of+++++++" lang="fr">[[aurions#French|aurions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Ccond-form-of+++++++" lang="fr">[[auriez#French|auriez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Ccond-form-of+++++++" lang="fr">[[auraient#French|auraient]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/o.ʁɛ/</span></span>


|-

! rowspan="5" style="background%3A%23c0cfe4" | <small>(compound<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+compos%C3%A9">present perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | present indicative of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="plus-que-parfait">pluperfect</span>


! colspan="6" style="background%3A%23DEDEDE" | imperfect indicative of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+ant%C3%A9rieur">past anterior</span><sup>2</sup>


! colspan="6" style="background%3A%23DEDEDE" | past historic of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="futur+ant%C3%A9rieur">future perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | future of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="conditionnel+pass%C3%A9">conditional perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | conditional of <i>[[avoir]]</i> + past participle


|-

! style="background%3A%23c0e4c0" colspan="2" | <span title="subjonctif">subjunctive</span>


! style="background%3A%23c0e4c0" | que je (j’)


! style="background%3A%23c0e4c0" | que tu


! style="background%3A%23c0e4c0" | qu’il, qu’elle


! style="background%3A%23c0e4c0" | que nous


! style="background%3A%23c0e4c0" | que vous


! style="background%3A%23c0e4c0" | qu’ils, qu’elles


|-

! rowspan="2" style="background%3A%23c0e4c0" | <small>(simple<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+pr%C3%A9sent">present</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[aie#French|aie]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[aies#French|aies]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[ait#French|ait]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[ayons#French|ayons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ.jɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[ayez#French|ayez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ.je/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[aient#French|aient]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" rowspan="1" | <span title="subjonctif+imparfait">imperfect</span><sup>2</sup>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[eusse#French|eusse]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ys/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[eusses#French|eusses]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ys/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[eût#French|eût]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/y/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[eussions#French|eussions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/y.sjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[eussiez#French|eussiez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/y.sje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[eussent#French|eussent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ys/</span></span>


|-

! rowspan="2" style="background%3A%23c0e4c0" | <small>(compound<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+pass%C3%A9">past</span>


! colspan="6" style="background%3A%23DEDEDE" | present subjunctive of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+plus-que-parfait">pluperfect</span><sup>2</sup>


! colspan="6" style="background%3A%23DEDEDE" | imperfect subjunctive of <i>[[avoir]]</i> + past participle


|-

! colspan="2" style="background%3A%23e4d4c0" | <span title="imp%C3%A9ratif">imperative</span>


! style="background%3A%23e4d4c0" | –


! style="background%3A%23e4d4c0" | <s>tu</s>


! style="background%3A%23e4d4c0" | –


! style="background%3A%23e4d4c0" | <s>nous</s>


! style="background%3A%23e4d4c0" | <s>vous</s>


! style="background%3A%23e4d4c0" | –


|-

! style="height%3A3em%3Bbackground%3A%23e4d4c0" colspan="2" | <span title>simple</span>


| —


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpr-form-of+++++++" lang="fr">[[aie#French|aie]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ/</span></span>


| —


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpr-form-of+++++++" lang="fr">[[ayons#French|ayons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ.jɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpr-form-of+++++++" lang="fr">[[ayez#French|ayez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/ɛ.je/</span></span>


| —


|-

! style="height%3A3em%3Bbackground%3A%23e4d4c0" colspan="2" | <span title>compound</span>


| —


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


| —


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


| —


|-

| colspan="8" |<sup>1</sup> The French gerund is only usable with the preposition <i>[[en]]</i>.


|-

| colspan="8" |<sup>2</sup> In less formal writing or speech, the past historic, past anterior, imperfect subjunctive and pluperfect subjunctive tenses may be found to have been replaced with the indicative present perfect, indicative pluperfect, present subjunctive and past subjunctive tenses respectively (Christopher Kendris [1995], <i>Master the Basics: French</i>, pp. [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA77 77], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA78 78], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA79 79], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA81 81]).


|}

</div>
</div>
[[Category:French third group verbs|AVOIR]][[Category:French irregular verbs|AVOIR]]
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
                "form": "avoir",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "multiword-construction"
                ]
              },
              {
                "form": "ayant",
                "ipa": "/ɛ.jɑ̃/",
                "source": "Conjugation",
                "tags": [
                  "gerund",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "ayant + past participle",
                "source": "Conjugation",
                "tags": [
                  "gerund",
                  "multiword-construction",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "eu",
                "ipa": "/y/",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "ai",
                "ipa": "/e/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "as",
                "ipa": "/a/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "a",
                "ipa": "/a/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "avons",
                "ipa": "/a.vɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "avez",
                "ipa": "/a.ve/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "ont",
                "ipa": "/ɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "avais",
                "ipa": "/a.vɛ/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "avais",
                "ipa": "/a.vɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "avait",
                "ipa": "/a.vɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "avions",
                "ipa": "/a.vjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "aviez",
                "ipa": "/a.vje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "avaient",
                "ipa": "/a.vɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "eus",
                "ipa": "/y/",
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
                "form": "eus",
                "ipa": "/y/",
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
                "form": "eut",
                "ipa": "/y/",
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
                "form": "eûmes",
                "ipa": "/ym/",
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
                "form": "eûtes",
                "ipa": "/yt/",
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
                "form": "eurent",
                "ipa": "/yʁ/",
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
                "form": "aurai",
                "ipa": "/o.ʁe/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "auras",
                "ipa": "/o.ʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "aura",
                "ipa": "/o.ʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "aurons",
                "ipa": "/o.ʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "aurez",
                "ipa": "/o.ʁe/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "auront",
                "ipa": "/o.ʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "aurais",
                "ipa": "/o.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "aurais",
                "ipa": "/o.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "aurait",
                "ipa": "/o.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "aurions",
                "ipa": "/o.ʁjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "auriez",
                "ipa": "/o.ʁje/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "auraient",
                "ipa": "/o.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "present indicative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "multiword-construction",
                  "perfect",
                  "present"
                ]
              },
              {
                "form": "imperfect indicative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "multiword-construction",
                  "pluperfect"
                ]
              },
              {
                "form": "past historic of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "anterior",
                  "indicative",
                  "multiword-construction",
                  "past"
                ]
              },
              {
                "form": "future of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "multiword-construction",
                  "perfect"
                ]
              },
              {
                "form": "conditional of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "multiword-construction",
                  "perfect"
                ]
              },
              {
                "form": "aie",
                "ipa": "/ɛ/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "aies",
                "ipa": "/ɛ/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "ait",
                "ipa": "/ɛ/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "ayons",
                "ipa": "/ɛ.jɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "ayez",
                "ipa": "/ɛ.je/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "aient",
                "ipa": "/ɛ/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "eusse",
                "ipa": "/ys/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "eusses",
                "ipa": "/ys/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "eût",
                "ipa": "/y/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "eussions",
                "ipa": "/y.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "eussiez",
                "ipa": "/y.sje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "eussent",
                "ipa": "/ys/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "present subjunctive of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "multiword-construction",
                  "past",
                  "subjunctive"
                ]
              },
              {
                "form": "imperfect subjunctive of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "multiword-construction",
                  "pluperfect",
                  "subjunctive"
                ]
              },
              {
                "form": "aie",
                "ipa": "/ɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "ayons",
                "ipa": "/ɛ.jɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "ayez",
                "ipa": "/ɛ.je/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "multiword-construction",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "multiword-construction",
                  "plural"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "multiword-construction",
                  "plural",
                  "second-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_French_verb2(self):
        ret = self.xinfl("budgéter", "French", "verb", "Conjugation", """
This verb is conjugated like <i class="Latn+mention" lang="fr">[[céder#French|céder]]</i>. It is a regular <i class="Latn+mention" lang="fr">[[-er#French|-er]]</i> verb, except that its last stem vowel alternates between <span class="IPA">/e/</span> (written ‘é’) and <span class="IPA">/ɛ/</span> (written ‘è’), with the latter being used before mute ‘e’.
One special case is the future stem, used in the future and the conditional. Before 1990, the future stem of such verbs was written ''budgéter-'', reflecting the historic pronunciation <span class="IPA">/e/</span>. In 1990, the French Academy recommended that it be written ''budgèter-'', reflecting the now common pronunciation <span class="IPA">/ɛ/</span>, thereby making this distinction consistent throughout the conjugation (and also matching in this regard the conjugations of verbs like <i class="Latn+mention" lang="fr">[[lever#French|lever]]</i> and <i class="Latn+mention" lang="fr">[[jeter#French|jeter]]</i>). Both spellings are in use today, and both are therefore given here.
<div class="NavFrame" style="clear%3Aboth">
<div class="NavHead" align="left">Conjugation of ''budgéter'' <span style="font-size%3A90%25%3B">(see also [[Appendix:French verbs]])</span></div>
<div class="NavContent" align="center">

{| style="background%3A%23F0F0F0%3Bwidth%3A100%25%3Bborder-collapse%3Aseparate%3Bborder-spacing%3A2px" class="inflection-table"

|-

! colspan="1" rowspan="2" style="background%3A%23e2e4c0" | <span title="infinitif">infinitive</span>


! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>simple</small>


| budgéter


|-

! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>compound</small>


! colspan="6" style="background%3A%23DEDEDE" | <i>[[avoir]]</i> + past participle


|-

! colspan="1" rowspan="2" style="background%3A%23e2e4c0" | <span title="participe+pr%C3%A9sent">present participle</span> or <span title>gerund</span><sup>1</sup>


! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>simple</small>


| <span class="Latn+form-of+lang-fr+ppr-form-of+++++++" lang="fr">[[budgétant#French|budgétant]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɑ̃/</span></span>


|-

! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>compound</small>


! colspan="6" style="background%3A%23DEDEDE" | <i>[[ayant]]</i> + past participle


|-

! colspan="2" style="background%3A%23e2e4c0" | <span title="participe+pass%C3%A9">past participle</span>


| <span class="Latn+form-of+lang-fr+pp-form-of+++++++" lang="fr">[[budgété#French|budgété]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.te/</span></span>


|-

! colspan="2" rowspan="2" |


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

! style="background%3A%23c0cfe4" colspan="2" | <span title="indicatif">indicative</span>


! style="background%3A%23c0cfe4" | je (j’)


! style="background%3A%23c0cfe4" | tu


! style="background%3A%23c0cfe4" | il, elle


! style="background%3A%23c0cfe4" | nous


! style="background%3A%23c0cfe4" | vous


! style="background%3A%23c0cfe4" | ils, elles


|-

! rowspan="5" style="background%3A%23c0cfe4" | <small>(simple<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pr%C3%A9sent">present</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[budgète#French|budgète]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[budgètes#French|budgètes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[budgète#French|budgète]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[budgétons#French|budgétons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[budgétez#French|budgétez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.te/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[budgètent#French|budgètent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="imparfait">imperfect</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[budgétais#French|budgétais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɛ/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[budgétais#French|budgétais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɛ/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[budgétait#French|budgétait]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɛ/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[budgétions#French|budgétions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[budgétiez#French|budgétiez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[budgétaient#French|budgétaient]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɛ/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+simple">past historic</span><sup>2</sup>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cphis-form-of+++++++" lang="fr">[[budgétai#French|budgétai]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.te/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cphis-form-of+++++++" lang="fr">[[budgétas#French|budgétas]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.ta/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cphis-form-of+++++++" lang="fr">[[budgéta#French|budgéta]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.ta/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cphis-form-of+++++++" lang="fr">[[budgétâmes#French|budgétâmes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tam/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cphis-form-of+++++++" lang="fr">[[budgétâtes#French|budgétâtes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tat/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cphis-form-of+++++++" lang="fr">[[budgétèrent#French|budgétèrent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɛʁ/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="futur+simple">future</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cfutr-form-of+++++++" lang="fr">[[budgèterai#French|budgèterai]]</span> or <span class="Latn+form-of+lang-fr+1%7Cs%7Cfutr-form-of+++++++" lang="fr">[[budgéterai#French|budgéterai]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁe/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cfutr-form-of+++++++" lang="fr">[[budgèteras#French|budgèteras]]</span> or <span class="Latn+form-of+lang-fr+2%7Cs%7Cfutr-form-of+++++++" lang="fr">[[budgéteras#French|budgéteras]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁa/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cfutr-form-of+++++++" lang="fr">[[budgètera#French|budgètera]]</span> or <span class="Latn+form-of+lang-fr+3%7Cs%7Cfutr-form-of+++++++" lang="fr">[[budgétera#French|budgétera]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁa/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cfutr-form-of+++++++" lang="fr">[[budgèterons#French|budgèterons]]</span> or <span class="Latn+form-of+lang-fr+1%7Cp%7Cfutr-form-of+++++++" lang="fr">[[budgéterons#French|budgéterons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cfutr-form-of+++++++" lang="fr">[[budgèterez#French|budgèterez]]</span> or <span class="Latn+form-of+lang-fr+2%7Cp%7Cfutr-form-of+++++++" lang="fr">[[budgéterez#French|budgéterez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁe/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cfutr-form-of+++++++" lang="fr">[[budgèteront#French|budgèteront]]</span> or <span class="Latn+form-of+lang-fr+3%7Cp%7Cfutr-form-of+++++++" lang="fr">[[budgéteront#French|budgéteront]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁɔ̃/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="conditionnel+pr%C3%A9sent">conditional</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Ccond-form-of+++++++" lang="fr">[[budgèterais#French|budgèterais]]</span> or <span class="Latn+form-of+lang-fr+1%7Cs%7Ccond-form-of+++++++" lang="fr">[[budgéterais#French|budgéterais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Ccond-form-of+++++++" lang="fr">[[budgèterais#French|budgèterais]]</span> or <span class="Latn+form-of+lang-fr+2%7Cs%7Ccond-form-of+++++++" lang="fr">[[budgéterais#French|budgéterais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Ccond-form-of+++++++" lang="fr">[[budgèterait#French|budgèterait]]</span> or <span class="Latn+form-of+lang-fr+3%7Cs%7Ccond-form-of+++++++" lang="fr">[[budgéterait#French|budgéterait]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Ccond-form-of+++++++" lang="fr">[[budgèterions#French|budgèterions]]</span> or <span class="Latn+form-of+lang-fr+1%7Cp%7Ccond-form-of+++++++" lang="fr">[[budgéterions#French|budgéterions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tə.ʁjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Ccond-form-of+++++++" lang="fr">[[budgèteriez#French|budgèteriez]]</span> or <span class="Latn+form-of+lang-fr+2%7Cp%7Ccond-form-of+++++++" lang="fr">[[budgéteriez#French|budgéteriez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tə.ʁje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Ccond-form-of+++++++" lang="fr">[[budgèteraient#French|budgèteraient]]</span> or <span class="Latn+form-of+lang-fr+3%7Cp%7Ccond-form-of+++++++" lang="fr">[[budgéteraient#French|budgéteraient]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛ.tʁɛ/</span></span>


|-

! rowspan="5" style="background%3A%23c0cfe4" | <small>(compound<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+compos%C3%A9">present perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | present indicative of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="plus-que-parfait">pluperfect</span>


! colspan="6" style="background%3A%23DEDEDE" | imperfect indicative of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+ant%C3%A9rieur">past anterior</span><sup>2</sup>


! colspan="6" style="background%3A%23DEDEDE" | past historic of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="futur+ant%C3%A9rieur">future perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | future of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="conditionnel+pass%C3%A9">conditional perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | conditional of <i>[[avoir]]</i> + past participle


|-

! style="background%3A%23c0e4c0" colspan="2" | <span title="subjonctif">subjunctive</span>


! style="background%3A%23c0e4c0" | que je (j’)


! style="background%3A%23c0e4c0" | que tu


! style="background%3A%23c0e4c0" | qu’il, qu’elle


! style="background%3A%23c0e4c0" | que nous


! style="background%3A%23c0e4c0" | que vous


! style="background%3A%23c0e4c0" | qu’ils, qu’elles


|-

! rowspan="2" style="background%3A%23c0e4c0" | <small>(simple<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+pr%C3%A9sent">present</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[budgète#French|budgète]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[budgètes#French|budgètes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[budgète#French|budgète]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[budgétions#French|budgétions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[budgétiez#French|budgétiez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[budgètent#French|budgètent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" rowspan="1" | <span title="subjonctif+imparfait">imperfect</span><sup>2</sup>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[budgétasse#French|budgétasse]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tas/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[budgétasses#French|budgétasses]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tas/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[budgétât#French|budgétât]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.ta/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[budgétassions#French|budgétassions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.ta.sjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[budgétassiez#French|budgétassiez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.ta.sje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[budgétassent#French|budgétassent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tas/</span></span>


|-

! rowspan="2" style="background%3A%23c0e4c0" | <small>(compound<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+pass%C3%A9">past</span>


! colspan="6" style="background%3A%23DEDEDE" | present subjunctive of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+plus-que-parfait">pluperfect</span><sup>2</sup>


! colspan="6" style="background%3A%23DEDEDE" | imperfect subjunctive of <i>[[avoir]]</i> + past participle


|-

! colspan="2" style="background%3A%23e4d4c0" | <span title="imp%C3%A9ratif">imperative</span>


! style="background%3A%23e4d4c0" | –


! style="background%3A%23e4d4c0" | <s>tu</s>


! style="background%3A%23e4d4c0" | –


! style="background%3A%23e4d4c0" | <s>nous</s>


! style="background%3A%23e4d4c0" | <s>vous</s>


! style="background%3A%23e4d4c0" | –


|-

! style="height%3A3em%3Bbackground%3A%23e4d4c0" colspan="2" | <span title>simple</span>


| —


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpr-form-of+++++++" lang="fr">[[budgète#French|budgète]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒɛt/</span></span>


| —


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpr-form-of+++++++" lang="fr">[[budgétons#French|budgétons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.tɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpr-form-of+++++++" lang="fr">[[budgétez#French|budgétez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/by.dʒe.te/</span></span>


| —


|-

! style="height%3A3em%3Bbackground%3A%23e4d4c0" colspan="2" | <span title>compound</span>


| —


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


| —


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


| —


|-

| colspan="8" |<sup>1</sup> The French gerund is only usable with the preposition <i>[[en]]</i>.


|-

| colspan="8" |<sup>2</sup> In less formal writing or speech, the past historic, past anterior, imperfect subjunctive and pluperfect subjunctive tenses may be found to have been replaced with the indicative present perfect, indicative pluperfect, present subjunctive and past subjunctive tenses respectively (Christopher Kendris [1995], <i>Master the Basics: French</i>, pp. [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA77 77], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA78 78], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA79 79], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA81 81]).


|}

</div>
</div>
[[Category:French verbs with conjugation -é-er|BUDGETER]][[Category:French first group verbs|BUDGETER]]
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
                "form": "budgéter",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "multiword-construction"
                ]
              },
              {
                "form": "budgétant",
                "ipa": "/by.dʒe.tɑ̃/",
                "source": "Conjugation",
                "tags": [
                  "gerund",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "ayant + past participle",
                "source": "Conjugation",
                "tags": [
                  "gerund",
                  "multiword-construction",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "budgété",
                "ipa": "/by.dʒe.te/",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "budgète",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "budgètes",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "budgète",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "budgétons",
                "ipa": "/by.dʒe.tɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "budgétez",
                "ipa": "/by.dʒe.te/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "budgètent",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "budgétais",
                "ipa": "/by.dʒe.tɛ/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "budgétais",
                "ipa": "/by.dʒe.tɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "budgétait",
                "ipa": "/by.dʒe.tɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "budgétions",
                "ipa": "/by.dʒe.tjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "budgétiez",
                "ipa": "/by.dʒe.tje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "budgétaient",
                "ipa": "/by.dʒe.tɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "budgétai",
                "ipa": "/by.dʒe.te/",
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
                "form": "budgétas",
                "ipa": "/by.dʒe.ta/",
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
                "form": "budgéta",
                "ipa": "/by.dʒe.ta/",
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
                "form": "budgétâmes",
                "ipa": "/by.dʒe.tam/",
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
                "form": "budgétâtes",
                "ipa": "/by.dʒe.tat/",
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
                "form": "budgétèrent",
                "ipa": "/by.dʒe.tɛʁ/",
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
                "form": "budgèterai",
                "ipa": "/by.dʒɛ.tʁe/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "budgéterai",
                "ipa": "/by.dʒɛ.tʁe/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "budgèteras",
                "ipa": "/by.dʒɛ.tʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "budgéteras",
                "ipa": "/by.dʒɛ.tʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "budgètera",
                "ipa": "/by.dʒɛ.tʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "budgétera",
                "ipa": "/by.dʒɛ.tʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "budgèterons",
                "ipa": "/by.dʒɛ.tʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "budgéterons",
                "ipa": "/by.dʒɛ.tʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "budgèterez",
                "ipa": "/by.dʒɛ.tʁe/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "budgéterez",
                "ipa": "/by.dʒɛ.tʁe/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "budgèteront",
                "ipa": "/by.dʒɛ.tʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "budgéteront",
                "ipa": "/by.dʒɛ.tʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "budgèterais",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "budgéterais",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "budgèterais",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "budgéterais",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "budgèterait",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "budgéterait",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "budgèterions",
                "ipa": "/by.dʒɛ.tə.ʁjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "budgéterions",
                "ipa": "/by.dʒɛ.tə.ʁjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "budgèteriez",
                "ipa": "/by.dʒɛ.tə.ʁje/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "budgéteriez",
                "ipa": "/by.dʒɛ.tə.ʁje/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "budgèteraient",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "budgéteraient",
                "ipa": "/by.dʒɛ.tʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "present indicative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "multiword-construction",
                  "perfect",
                  "present"
                ]
              },
              {
                "form": "imperfect indicative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "multiword-construction",
                  "pluperfect"
                ]
              },
              {
                "form": "past historic of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "anterior",
                  "indicative",
                  "multiword-construction",
                  "past"
                ]
              },
              {
                "form": "future of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "multiword-construction",
                  "perfect"
                ]
              },
              {
                "form": "conditional of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "multiword-construction",
                  "perfect"
                ]
              },
              {
                "form": "budgète",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "budgètes",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "budgète",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "budgétions",
                "ipa": "/by.dʒe.tjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "budgétiez",
                "ipa": "/by.dʒe.tje/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "budgètent",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "budgétasse",
                "ipa": "/by.dʒe.tas/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "budgétasses",
                "ipa": "/by.dʒe.tas/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "budgétât",
                "ipa": "/by.dʒe.ta/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "budgétassions",
                "ipa": "/by.dʒe.ta.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "budgétassiez",
                "ipa": "/by.dʒe.ta.sje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "budgétassent",
                "ipa": "/by.dʒe.tas/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "present subjunctive of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "multiword-construction",
                  "past",
                  "subjunctive"
                ]
              },
              {
                "form": "imperfect subjunctive of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "multiword-construction",
                  "pluperfect",
                  "subjunctive"
                ]
              },
              {
                "form": "budgète",
                "ipa": "/by.dʒɛt/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "budgétons",
                "ipa": "/by.dʒe.tɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "budgétez",
                "ipa": "/by.dʒe.te/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "multiword-construction",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "multiword-construction",
                  "plural"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "multiword-construction",
                  "plural",
                  "second-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_French_verb3(self):
        ret = self.xinfl("saurir", "French", "verb", "Conjugation", """
This is a regular verb of the second conjugation, like finir, choisir, and most other verbs with infinitives ending in <i class="Latn+mention" lang="fr">[[-ir#French|-ir]]</i>. One salient feature of this conjugation is the repeated appearance of the infix <i class="Latn+mention" lang="fr">[[-iss-#French|-iss-]]</i>.
<div class="NavFrame" style="clear%3Aboth">
<div class="NavHead" align="left">Conjugation of ''saurir'' <span style="font-size%3A90%25%3B">(see also [[Appendix:French verbs]])</span></div>
<div class="NavContent" align="center">

{| style="background%3A%23F0F0F0%3Bwidth%3A100%25%3Bborder-collapse%3Aseparate%3Bborder-spacing%3A2px" class="inflection-table"

|-

! colspan="1" rowspan="2" style="background%3A%23e2e4c0" | <span title="infinitif">infinitive</span>


! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>simple</small>


| saurir


|-

! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>compound</small>


! colspan="6" style="background%3A%23DEDEDE" | <i>[[avoir]]</i> + past participle


|-

! colspan="1" rowspan="2" style="background%3A%23e2e4c0" | <span title="participe+pr%C3%A9sent">present participle</span> or <span title>gerund</span><sup>1</sup>


! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>simple</small>


| <span class="Latn+form-of+lang-fr+ppr-form-of+++++++" lang="fr">[[saurissant#French|saurissant]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sɑ̃/</span> or <span class="IPA">/so.ʁi.sɑ̃/</span></span>


|-

! colspan="1" style="height%3A3em%3Bbackground%3A%23e2e4c0" | <small>compound</small>


! colspan="6" style="background%3A%23DEDEDE" | <i>[[ayant]]</i> + past participle


|-

! colspan="2" style="background%3A%23e2e4c0" | <span title="participe+pass%C3%A9">past participle</span>


| <span class="Latn+form-of+lang-fr+pp-form-of+++++++" lang="fr">[[sauri#French|sauri]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


|-

! colspan="2" rowspan="2" |


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

! style="background%3A%23c0cfe4" colspan="2" | <span title="indicatif">indicative</span>


! style="background%3A%23c0cfe4" | je (j’)


! style="background%3A%23c0cfe4" | tu


! style="background%3A%23c0cfe4" | il, elle


! style="background%3A%23c0cfe4" | nous


! style="background%3A%23c0cfe4" | vous


! style="background%3A%23c0cfe4" | ils, elles


|-

! rowspan="5" style="background%3A%23c0cfe4" | <small>(simple<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pr%C3%A9sent">present</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[sauris#French|sauris]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[sauris#French|sauris]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cpres%7Cindc-form-of+++++++" lang="fr">[[saurit#French|saurit]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[saurissons#French|saurissons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sɔ̃/</span> or <span class="IPA">/so.ʁi.sɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[saurissez#French|saurissez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.se/</span> or <span class="IPA">/so.ʁi.se/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cpres%7Cindc-form-of+++++++" lang="fr">[[saurissent#French|saurissent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="imparfait">imperfect</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[saurissais#French|saurissais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sɛ/</span> or <span class="IPA">/so.ʁi.sɛ/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[saurissais#French|saurissais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sɛ/</span> or <span class="IPA">/so.ʁi.sɛ/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[saurissait#French|saurissait]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sɛ/</span> or <span class="IPA">/so.ʁi.sɛ/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[saurissions#French|saurissions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sjɔ̃/</span> or <span class="IPA">/so.ʁi.sjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[saurissiez#French|saurissiez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sje/</span> or <span class="IPA">/so.ʁi.sje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cimpf%7Cindc-form-of+++++++" lang="fr">[[saurissaient#French|saurissaient]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sɛ/</span> or <span class="IPA">/so.ʁi.sɛ/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+simple">past historic</span><sup>2</sup>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cphis-form-of+++++++" lang="fr">[[sauris#French|sauris]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cphis-form-of+++++++" lang="fr">[[sauris#French|sauris]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cphis-form-of+++++++" lang="fr">[[saurit#French|saurit]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cphis-form-of+++++++" lang="fr">[[saurîmes#French|saurîmes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁim/</span> or <span class="IPA">/so.ʁim/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cphis-form-of+++++++" lang="fr">[[saurîtes#French|saurîtes]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁit/</span> or <span class="IPA">/so.ʁit/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cphis-form-of+++++++" lang="fr">[[saurirent#French|saurirent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁiʁ/</span> or <span class="IPA">/so.ʁiʁ/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="futur+simple">future</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cfutr-form-of+++++++" lang="fr">[[saurirai#French|saurirai]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁe/</span> or <span class="IPA">/so.ʁi.ʁe/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cfutr-form-of+++++++" lang="fr">[[sauriras#French|sauriras]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁa/</span> or <span class="IPA">/so.ʁi.ʁa/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cfutr-form-of+++++++" lang="fr">[[saurira#French|saurira]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁa/</span> or <span class="IPA">/so.ʁi.ʁa/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cfutr-form-of+++++++" lang="fr">[[saurirons#French|saurirons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁɔ̃/</span> or <span class="IPA">/so.ʁi.ʁɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cfutr-form-of+++++++" lang="fr">[[saurirez#French|saurirez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁe/</span> or <span class="IPA">/so.ʁi.ʁe/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cfutr-form-of+++++++" lang="fr">[[sauriront#French|sauriront]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁɔ̃/</span> or <span class="IPA">/so.ʁi.ʁɔ̃/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="conditionnel+pr%C3%A9sent">conditional</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Ccond-form-of+++++++" lang="fr">[[saurirais#French|saurirais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁɛ/</span> or <span class="IPA">/so.ʁi.ʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Ccond-form-of+++++++" lang="fr">[[saurirais#French|saurirais]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁɛ/</span> or <span class="IPA">/so.ʁi.ʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Ccond-form-of+++++++" lang="fr">[[saurirait#French|saurirait]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁɛ/</span> or <span class="IPA">/so.ʁi.ʁɛ/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Ccond-form-of+++++++" lang="fr">[[sauririons#French|sauririons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁjɔ̃/</span> or <span class="IPA">/so.ʁi.ʁjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Ccond-form-of+++++++" lang="fr">[[sauririez#French|sauririez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁje/</span> or <span class="IPA">/so.ʁi.ʁje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Ccond-form-of+++++++" lang="fr">[[sauriraient#French|sauriraient]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.ʁɛ/</span> or <span class="IPA">/so.ʁi.ʁɛ/</span></span>


|-

! rowspan="5" style="background%3A%23c0cfe4" | <small>(compound<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+compos%C3%A9">present perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | present indicative of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="plus-que-parfait">pluperfect</span>


! colspan="6" style="background%3A%23DEDEDE" | imperfect indicative of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="pass%C3%A9+ant%C3%A9rieur">past anterior</span><sup>2</sup>


! colspan="6" style="background%3A%23DEDEDE" | past historic of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="futur+ant%C3%A9rieur">future perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | future of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0cfe4" | <span title="conditionnel+pass%C3%A9">conditional perfect</span>


! colspan="6" style="background%3A%23DEDEDE" | conditional of <i>[[avoir]]</i> + past participle


|-

! style="background%3A%23c0e4c0" colspan="2" | <span title="subjonctif">subjunctive</span>


! style="background%3A%23c0e4c0" | que je (j’)


! style="background%3A%23c0e4c0" | que tu


! style="background%3A%23c0e4c0" | qu’il, qu’elle


! style="background%3A%23c0e4c0" | que nous


! style="background%3A%23c0e4c0" | que vous


! style="background%3A%23c0e4c0" | qu’ils, qu’elles


|-

! rowspan="2" style="background%3A%23c0e4c0" | <small>(simple<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+pr%C3%A9sent">present</span>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[saurisse#French|saurisse]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[saurisses#French|saurisses]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cpres%7Csubj-form-of+++++++" lang="fr">[[saurisse#French|saurisse]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[saurissions#French|saurissions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sjɔ̃/</span> or <span class="IPA">/so.ʁi.sjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[saurissiez#French|saurissiez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sje/</span> or <span class="IPA">/so.ʁi.sje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cpres%7Csubj-form-of+++++++" lang="fr">[[saurissent#French|saurissent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" rowspan="1" | <span title="subjonctif+imparfait">imperfect</span><sup>2</sup>


| <span class="Latn+form-of+lang-fr+1%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[saurisse#French|saurisse]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[saurisses#French|saurisses]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cs%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[saurît#French|saurît]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[saurissions#French|saurissions]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sjɔ̃/</span> or <span class="IPA">/so.ʁi.sjɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[saurissiez#French|saurissiez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sje/</span> or <span class="IPA">/so.ʁi.sje/</span></span>


| <span class="Latn+form-of+lang-fr+3%7Cp%7Cimpf%7Csubj-form-of+++++++" lang="fr">[[saurissent#French|saurissent]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁis/</span> or <span class="IPA">/so.ʁis/</span></span>


|-

! rowspan="2" style="background%3A%23c0e4c0" | <small>(compound<br>tenses)</small>


! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+pass%C3%A9">past</span>


! colspan="6" style="background%3A%23DEDEDE" | present subjunctive of <i>[[avoir]]</i> + past participle


|-

! style="height%3A3em%3Bbackground%3A%23c0e4c0" | <span title="subjonctif+plus-que-parfait">pluperfect</span><sup>2</sup>


! colspan="6" style="background%3A%23DEDEDE" | imperfect subjunctive of <i>[[avoir]]</i> + past participle


|-

! colspan="2" style="background%3A%23e4d4c0" | <span title="imp%C3%A9ratif">imperative</span>


! style="background%3A%23e4d4c0" | –


! style="background%3A%23e4d4c0" | <s>tu</s>


! style="background%3A%23e4d4c0" | –


! style="background%3A%23e4d4c0" | <s>nous</s>


! style="background%3A%23e4d4c0" | <s>vous</s>


! style="background%3A%23e4d4c0" | –


|-

! style="height%3A3em%3Bbackground%3A%23e4d4c0" colspan="2" | <span title>simple</span>


| —


| <span class="Latn+form-of+lang-fr+2%7Cs%7Cimpr-form-of+++++++" lang="fr">[[sauris#French|sauris]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi/</span> or <span class="IPA">/so.ʁi/</span></span>


| —


| <span class="Latn+form-of+lang-fr+1%7Cp%7Cimpr-form-of+++++++" lang="fr">[[saurissons#French|saurissons]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.sɔ̃/</span> or <span class="IPA">/so.ʁi.sɔ̃/</span></span>


| <span class="Latn+form-of+lang-fr+2%7Cp%7Cimpr-form-of+++++++" lang="fr">[[saurissez#French|saurissez]]</span><br><span style="color%3A%237F7F7F"><span class="IPA">/sɔ.ʁi.se/</span> or <span class="IPA">/so.ʁi.se/</span></span>


| —


|-

! style="height%3A3em%3Bbackground%3A%23e4d4c0" colspan="2" | <span title>compound</span>


| —


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


| —


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


! style="background%3A%23DEDEDE" | simple imperative of <i>[[avoir]]</i> + past participle


| —


|-

| colspan="8" |<sup>1</sup> The French gerund is only usable with the preposition <i>[[en]]</i>.


|-

| colspan="8" |<sup>2</sup> In less formal writing or speech, the past historic, past anterior, imperfect subjunctive and pluperfect subjunctive tenses may be found to have been replaced with the indicative present perfect, indicative pluperfect, present subjunctive and past subjunctive tenses respectively (Christopher Kendris [1995], <i>Master the Basics: French</i>, pp. [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA77 77], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA78 78], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA79 79], [https://books.google.fr/books?id=g4G4jg5GWMwC&pg=PA81 81]).


|}

</div>
</div>
[[Category:French verbs with conjugation -ir|SAURIR]][[Category:French second group verbs|SAURIR]]
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
                "form": "saurir",
                "source": "Conjugation",
                "tags": [
                  "infinitive"
                ]
              },
              {
                "form": "avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "multiword-construction"
                ]
              },
              {
                "form": "saurissant",
                "ipa": "/sɔ.ʁi.sɑ̃/",
                "source": "Conjugation",
                "tags": [
                  "gerund",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "saurissant",
                "ipa": "/so.ʁi.sɑ̃/",
                "source": "Conjugation",
                "tags": [
                  "gerund",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "ayant + past participle",
                "source": "Conjugation",
                "tags": [
                  "gerund",
                  "multiword-construction",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "sauri",
                "ipa": "/sɔ.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "sauri",
                "ipa": "/so.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past"
                ]
              },
              {
                "form": "sauris",
                "ipa": "/sɔ.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "sauris",
                "ipa": "/so.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "sauris",
                "ipa": "/sɔ.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sauris",
                "ipa": "/so.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saurit",
                "ipa": "/sɔ.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saurit",
                "ipa": "/so.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saurissons",
                "ipa": "/sɔ.ʁi.sɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "saurissons",
                "ipa": "/so.ʁi.sɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "saurissez",
                "ipa": "/sɔ.ʁi.se/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "saurissez",
                "ipa": "/so.ʁi.se/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "saurissent",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "saurissent",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "saurissais",
                "ipa": "/sɔ.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "saurissais",
                "ipa": "/so.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "saurissais",
                "ipa": "/sɔ.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saurissais",
                "ipa": "/so.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saurissait",
                "ipa": "/sɔ.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saurissait",
                "ipa": "/so.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saurissions",
                "ipa": "/sɔ.ʁi.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "saurissions",
                "ipa": "/so.ʁi.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "saurissiez",
                "ipa": "/sɔ.ʁi.sje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "saurissiez",
                "ipa": "/so.ʁi.sje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "saurissaient",
                "ipa": "/sɔ.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "saurissaient",
                "ipa": "/so.ʁi.sɛ/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "sauris",
                "ipa": "/sɔ.ʁi/",
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
                "form": "sauris",
                "ipa": "/so.ʁi/",
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
                "form": "sauris",
                "ipa": "/sɔ.ʁi/",
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
                "form": "sauris",
                "ipa": "/so.ʁi/",
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
                "form": "saurit",
                "ipa": "/sɔ.ʁi/",
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
                "form": "saurit",
                "ipa": "/so.ʁi/",
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
                "form": "saurîmes",
                "ipa": "/sɔ.ʁim/",
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
                "form": "saurîmes",
                "ipa": "/so.ʁim/",
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
                "form": "saurîtes",
                "ipa": "/sɔ.ʁit/",
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
                "form": "saurîtes",
                "ipa": "/so.ʁit/",
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
                "form": "saurirent",
                "ipa": "/sɔ.ʁiʁ/",
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
                "form": "saurirent",
                "ipa": "/so.ʁiʁ/",
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
                "form": "saurirai",
                "ipa": "/sɔ.ʁi.ʁe/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "saurirai",
                "ipa": "/so.ʁi.ʁe/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "sauriras",
                "ipa": "/sɔ.ʁi.ʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sauriras",
                "ipa": "/so.ʁi.ʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saurira",
                "ipa": "/sɔ.ʁi.ʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saurira",
                "ipa": "/so.ʁi.ʁa/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saurirons",
                "ipa": "/sɔ.ʁi.ʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "saurirons",
                "ipa": "/so.ʁi.ʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "saurirez",
                "ipa": "/sɔ.ʁi.ʁe/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "saurirez",
                "ipa": "/so.ʁi.ʁe/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "sauriront",
                "ipa": "/sɔ.ʁi.ʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "sauriront",
                "ipa": "/so.ʁi.ʁɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "saurirais",
                "ipa": "/sɔ.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "saurirais",
                "ipa": "/so.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "saurirais",
                "ipa": "/sɔ.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saurirais",
                "ipa": "/so.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saurirait",
                "ipa": "/sɔ.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "saurirait",
                "ipa": "/so.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sauririons",
                "ipa": "/sɔ.ʁi.ʁjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "sauririons",
                "ipa": "/so.ʁi.ʁjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "sauririez",
                "ipa": "/sɔ.ʁi.ʁje/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "sauririez",
                "ipa": "/so.ʁi.ʁje/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "sauriraient",
                "ipa": "/sɔ.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "sauriraient",
                "ipa": "/so.ʁi.ʁɛ/",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "present indicative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "multiword-construction",
                  "perfect",
                  "present"
                ]
              },
              {
                "form": "imperfect indicative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "multiword-construction",
                  "pluperfect"
                ]
              },
              {
                "form": "past historic of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "anterior",
                  "indicative",
                  "multiword-construction",
                  "past"
                ]
              },
              {
                "form": "future of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "multiword-construction",
                  "perfect"
                ]
              },
              {
                "form": "conditional of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "multiword-construction",
                  "perfect"
                ]
              },
              {
                "form": "saurisse",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurisse",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurisses",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurisses",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurisse",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "saurisse",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "saurissions",
                "ipa": "/sɔ.ʁi.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissions",
                "ipa": "/so.ʁi.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissiez",
                "ipa": "/sɔ.ʁi.sje/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissiez",
                "ipa": "/so.ʁi.sje/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissent",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "saurissent",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "saurisse",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurisse",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurisses",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurisses",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "saurît",
                "ipa": "/sɔ.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "saurît",
                "ipa": "/so.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "saurissions",
                "ipa": "/sɔ.ʁi.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissions",
                "ipa": "/so.ʁi.sjɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissiez",
                "ipa": "/sɔ.ʁi.sje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissiez",
                "ipa": "/so.ʁi.sje/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "saurissent",
                "ipa": "/sɔ.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "saurissent",
                "ipa": "/so.ʁis/",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "present subjunctive of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "multiword-construction",
                  "past",
                  "subjunctive"
                ]
              },
              {
                "form": "imperfect subjunctive of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "multiword-construction",
                  "pluperfect",
                  "subjunctive"
                ]
              },
              {
                "form": "sauris",
                "ipa": "/sɔ.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "sauris",
                "ipa": "/so.ʁi/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "saurissons",
                "ipa": "/sɔ.ʁi.sɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "saurissons",
                "ipa": "/so.ʁi.sɔ̃/",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "saurissez",
                "ipa": "/sɔ.ʁi.se/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "saurissez",
                "ipa": "/so.ʁi.se/",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "multiword-construction",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "multiword-construction",
                  "plural"
                ]
              },
              {
                "form": "simple imperative of avoir + past participle",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "multiword-construction",
                  "plural",
                  "second-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

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

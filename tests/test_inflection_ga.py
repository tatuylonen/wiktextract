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

    def test_Irish_verb1(self):
        ret = self.xinfl("nigh", "Irish", "verb", "Conjugation", """
<div class="NavFrame">
<div class="NavHead" align="left">[[Appendix:Irish verbs|First Conjugation]] (C)</div>
<div class="NavContent" align="center">
<div class="inflection-table">


{| style="background-color%3A%23f0f0f0%3Bborder-collapse%3Aseparate%3Bborder-spacing%3A2px%3B+margin%3A0+auto+0+auto%3B"

|-

! colspan="2" rowspan="2" style="background-color%3A%23c0cfe4%3B" |


! colspan="3" style="background-color%3A%23c0cfe4%3B" scope="col" | ''singular''


! colspan="3" style="background-color%3A%23c0cfe4%3B" scope="col" | ''plural''


! rowspan="2" style="background-color%3A%23c0cfe4%3B" scope="col" | [[relative]]


! rowspan="2" style="background-color%3A%23c0cfe4%3B" scope="col" | [[autonomous]]


|-

! style="background-color%3A%23c0cfe4%3Bwidth%3A10%25" scope="col" | [[first person|first]]


! style="background-color%3A%23c0cfe4%3Bwidth%3A10%25" scope="col" | [[second person|second]]


! style="background-color%3A%23c0cfe4%3Bwidth%3A10%25" scope="col" | [[third person|third]]


! style="background-color%3A%23c0cfe4%3Bwidth%3A10%25" scope="col" | [[first person|first]]


! style="background-color%3A%23c0cfe4%3Bwidth%3A10%25" scope="col" | [[second person|second]]


! style="background-color%3A%23c0cfe4%3Bwidth%3A10%25" scope="col" | [[third person|third]]


|- style="background-color%3A%23e0e0e0%3B"

! rowspan="4" style="background-color%3A%23c0cfe4%3B" scope="row" | indicative


! style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | present


| <span class="Latn" lang="ga">[[ním#Irish|ním]]</span>


| <span class="Latn" lang="ga">[[níonn#Irish|níonn]]</span> tú; <br> <span class="Latn" lang="ga">[[nír#Irish|nír]]</span><sup>†</sup>


| <span class="Latn" lang="ga">[[níonn#Irish|níonn]]</span> sé, sí


| <span class="Latn" lang="ga">[[nímid#Irish|nímid]]</span>


| <span class="Latn" lang="ga">[[níonn#Irish|níonn]]</span> sibh


| <span class="Latn" lang="ga">[[níonn#Irish|níonn]]</span> siad; <br> <span class="Latn" lang="ga">[[níd#Irish|níd]]</span><sup>†</sup>


| a <span class="Latn" lang="ga">[[níonn#Irish|níonn]]</span>; a <span class="Latn" lang="ga">[[níos#Irish|níos]]</span>


| <span class="Latn" lang="ga">[[nitear#Irish|nitear]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | past


| <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span> mé; <span class="Latn" lang="ga">[[níos#Irish|níos]]</span>


| <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span> tú; <br> <span class="Latn" lang="ga">[[nís#Irish|nís]]</span>


| <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span> sé, sí


| <span class="Latn" lang="ga">[[níomar#Irish|níomar]]</span>; <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span> muid


| <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span> sibh; <span class="Latn" lang="ga">[[níobhair#Irish|níobhair]]</span>


| <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span> siad; <span class="Latn" lang="ga">[[níodar#Irish|níodar]]</span>


| a <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span>&nbsp;/<br>ar <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span>*


| <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | past habitual


| <span class="Latn" lang="ga">[[nínn#Irish|nínn]]</span>


| <span class="Latn" lang="ga">[[niteá#Irish|niteá]]</span>


| <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> sé, sí


| <span class="Latn" lang="ga">[[nimis#Irish|nimis]]</span>; <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> muid


| <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> sibh


| <span class="Latn" lang="ga">[[nidís#Irish|nidís]]</span>; <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> siad


| a <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span>&nbsp;/<br>a <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span>*


| <span class="Latn" lang="ga">[[nití#Irish|nití]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | future


| <span class="Latn" lang="ga">[[nífidh#Irish|nífidh]]</span> mé; <br> <span class="Latn" lang="ga">[[nífead#Irish|nífead]]</span>


| <span class="Latn" lang="ga">[[nífidh#Irish|nífidh]]</span> tú; <br> <span class="Latn" lang="ga">[[nífir#Irish|nífir]]</span><sup>†</sup>


| <span class="Latn" lang="ga">[[nífidh#Irish|nífidh]]</span> sé, sí


| <span class="Latn" lang="ga">[[nífimid#Irish|nífimid]]</span>; <br> <span class="Latn" lang="ga">[[nífidh#Irish|nífidh]]</span> muid


| <span class="Latn" lang="ga">[[nífidh#Irish|nífidh]]</span> sibh


| <span class="Latn" lang="ga">[[nífidh#Irish|nífidh]]</span> siad; <br> <span class="Latn" lang="ga">[[nífid#Irish|nífid]]</span><sup>†</sup>


| a <span class="Latn" lang="ga">[[nífidh#Irish|nífidh]]</span>; a <span class="Latn" lang="ga">[[nífeas#Irish|nífeas]]</span>


| <span class="Latn" lang="ga">[[nífear#Irish|nífear]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! colspan="2" style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | conditional


| <span class="Latn" lang="ga">[[nífinn#Irish|nífinn]]</span>


| <span class="Latn" lang="ga">[[nífeá#Irish|nífeá]]</span>


| <span class="Latn" lang="ga">[[nífeadh#Irish|nífeadh]]</span> sé, sí


| <span class="Latn" lang="ga">[[nífimis#Irish|nífimis]]</span>; <span class="Latn" lang="ga">[[nífeadh#Irish|nífeadh]]</span> muid


| <span class="Latn" lang="ga">[[nífeadh#Irish|nífeadh]]</span> sibh


| <span class="Latn" lang="ga">[[nífidís#Irish|nífidís]]</span>; <span class="Latn" lang="ga">[[nífeadh#Irish|nífeadh]]</span> siad


| a <span class="Latn" lang="ga">[[nífeadh#Irish|nífeadh]]</span>&nbsp;/<br>a <span class="Latn" lang="ga">[[nífeadh#Irish|nífeadh]]</span>*


| <span class="Latn" lang="ga">[[nífí#Irish|nífí]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! rowspan="2" style="background-color%3A%23c0cfe4%3B" scope="row" | subjunctive


! style="background-color%3A%23c0cfe4%3B" scope="row" | present


| go <span class="Latn" lang="ga">[[ní#Irish|ní]]</span> mé; <br> go <span class="Latn" lang="ga">[[níod#Irish|níod]]</span><sup>†</sup>


| go <span class="Latn" lang="ga">[[ní#Irish|ní]]</span> tú; <br> go <span class="Latn" lang="ga">[[nír#Irish|nír]]</span><sup>†</sup>


| go <span class="Latn" lang="ga">[[ní#Irish|ní]]</span> sé, sí


| go <span class="Latn" lang="ga">[[nímid#Irish|nímid]]</span>; <br> go <span class="Latn" lang="ga">[[ní#Irish|ní]]</span> muid


| go <span class="Latn" lang="ga">[[ní#Irish|ní]]</span> sibh


| go <span class="Latn" lang="ga">[[ní#Irish|ní]]</span> siad; <br> go <span class="Latn" lang="ga">[[níd#Irish|níd]]</span><sup>†</sup>


| style="text-align%3Acenter%3B" | —


| go <span class="Latn" lang="ga">[[nitear#Irish|nitear]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | past


| dá <span class="Latn" lang="ga">[[nínn#Irish|nínn]]</span>


| dá <span class="Latn" lang="ga">[[niteá#Irish|niteá]]</span>


| dá <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> sé, sí


| dá <span class="Latn" lang="ga">[[nimis#Irish|nimis]]</span>; <br> dá <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> muid


| dá <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> sibh


| dá <span class="Latn" lang="ga">[[nidís#Irish|nidís]]</span>; <br> dá <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> siad


| style="text-align%3Acenter%3B" | —


| dá <span class="Latn" lang="ga">[[nití#Irish|nití]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! colspan="2" style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | imperative


| <span class="Latn" lang="ga">[[ním#Irish|ním]]</span>


| <span class="Latn" lang="ga">[[nigh#Irish|nigh]]</span>


| <span class="Latn" lang="ga">[[níodh#Irish|níodh]]</span> sé, sí


| <span class="Latn" lang="ga">[[nímis#Irish|nímis]]</span>


| <span class="Latn" lang="ga">[[nígí#Irish|nígí]]</span>; <br> <span class="Latn" lang="ga">[[nídh#Irish|nídh]]</span><sup>†</sup>


| <span class="Latn" lang="ga">[[nídís#Irish|nídís]]</span>


| style="text-align%3Acenter%3B" | —


| <span class="Latn" lang="ga">[[nitear#Irish|nitear]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! colspan="2" style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | verbal noun


| colspan="8" | <span class="Latn" lang="ga">[[ní#Irish|ní]]</span>


|- style="background-color%3A%23e0e0e0%3B"

! colspan="2" style="height%3A2em%3Bbackground%3A%23c0cfe4" scope="row" | past participle


| colspan="8" | <span class="Latn" lang="ga">[[nite#Irish|nite]]</span>


|}

&#42; Indirect relative<br>† Archaic or dialect form
</div></div></div>[[Category:Irish first-conjugation contract verbs|NIGH]]
""")
        expected = {
            "forms": [
              {
                "form": "First Conjugation",
                "source": "Conjugation title",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "ním",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "níonn tú",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "nír",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "níonn sé",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nímid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "níonn sibh",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "níonn siad",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "níd",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "a níonn",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "relative"
                ]
              },
              {
                "form": "a níos",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "relative"
                ]
              },
              {
                "form": "nitear",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "indicative",
                  "present"
                ]
              },
              {
                "form": "nigh mé",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "níos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "nigh tú",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "nís",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "nigh sé",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "níomar",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "nigh muid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "nigh sibh",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "níobhair",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "nigh siad",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "níodar",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "a nigh",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "relative"
                ]
              },
              {
                "form": "ar nigh",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "relative"
                ]
              },
              {
                "form": "níodh",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "indicative",
                  "past"
                ]
              },
              {
                "form": "nínn",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "habitual",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "niteá",
                "source": "Conjugation",
                "tags": [
                  "habitual",
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "níodh sé",
                "source": "Conjugation",
                "tags": [
                  "habitual",
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "habitual",
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nimis",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "habitual",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "níodh muid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "habitual",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "níodh sibh",
                "source": "Conjugation",
                "tags": [
                  "habitual",
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "nidís",
                "source": "Conjugation",
                "tags": [
                  "habitual",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "níodh siad",
                "source": "Conjugation",
                "tags": [
                  "habitual",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "a níodh",
                "source": "Conjugation",
                "tags": [
                  "habitual",
                  "indicative",
                  "past",
                  "relative"
                ]
              },
              {
                "form": "nití",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "habitual",
                  "indicative",
                  "past"
                ]
              },
              {
                "form": "nífidh mé",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "nífead",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "nífidh tú",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "nífir",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "nífidh sé",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nífimid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "nífidh muid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "nífidh sibh",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "nífidh siad",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "nífid",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "a nífidh",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "relative"
                ]
              },
              {
                "form": "a nífeas",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "relative"
                ]
              },
              {
                "form": "nífear",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "future",
                  "indicative"
                ]
              },
              {
                "form": "nífinn",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "nífeá",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "nífeadh sé",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nífimis",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "nífeadh muid",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "nífeadh sibh",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "nífidís",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "nífeadh siad",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "a nífeadh",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "relative"
                ]
              },
              {
                "form": "nífí",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "conditional"
                ]
              },
              {
                "form": "go ní mé",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "go níod",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "go ní tú",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "go nír",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "go ní sé",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "go nímid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "go ní muid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "go ní sibh",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "go ní siad",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "go níd",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "go nitear",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "dá nínn",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "dá niteá",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "dá níodh sé",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "dá nimis",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "dá níodh muid",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "past",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "dá níodh sibh",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "dá nidís",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "dá níodh siad",
                "source": "Conjugation",
                "tags": [
                  "past",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "dá nití",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "past",
                  "subjunctive"
                ]
              },
              {
                "form": "ním",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "singular"
                ]
              },
              {
                "form": "nigh",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "níodh sé",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "sí",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "nímis",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "nígí",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "nídh",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "nídís",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "nitear",
                "source": "Conjugation",
                "tags": [
                  "autonomous",
                  "imperative"
                ]
              },
              {
                "form": "ní",
                "source": "Conjugation",
                "tags": [
                  "nominal-from-verb",
                  "nominalization",
                ]
              },
              {
                "form": "nite",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "past",
                ]
              },
              {
                "form": "conjugation-1",
                "source": "Conjugation title",
                "tags": [
                  "word-tags"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Irish_mutation1(self):
        ret = self.xinfl("cois", "Irish", "prep", "Mutation", """
{| border="1" cellpadding="4" cellspacing="0" class="inflection-table" style="align%3A+left%3B+margin%3A+0.5em+0+0+0%3B+border-style%3A+solid%3B+border%3A+1px+solid+%237f7f7f%3B+border-right-width%3A+2px%3B+border-bottom-width%3A+2px%3B+border-collapse%3A+collapse%3B+background-color%3A+%23F8F8F8%3B+font-size%3A+95%25%3B"

|-

! colspan="3" | [[Appendix:Irish mutations|Irish mutation]]


|-

! Radical


! Lenition


! Eclipsis


|-

| <span class="Latn" lang="ga">[[cois#Irish|cois]]</span>


| <span class="Latn" lang="ga">[[chois#Irish|chois]]</span>


| <span class="Latn" lang="ga">[[gcois#Irish|gcois]]</span>


|-

| colspan="3" | <small style="font-size%3A85%25%3B">''Note:'' Some of these forms may be hypothetical. Not every possible mutated form of every word actually occurs.</small>


|}
""")
        expected = {
            "forms": [
              {
                "form": "cois",
                "source": "Mutation",
                "tags": [
                  "mutation",
                  "mutation-radical"
                ]
              },
              {
                "form": "chois",
                "source": "Mutation",
                "tags": [
                  "lenition",
                  "mutation"
                ]
              },
              {
                "form": "gcois",
                "source": "Mutation",
                "tags": [
                  "eclipsis",
                  "mutation"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Irish_noun1(self):
        ret = self.xinfl("cois", "Irish", "noun", "Declension", """
<div class="NavFrame" style>
<div class="NavHead" style>Declension of ''cois''</div>
<div class="NavContent">

'''[[Appendix:Irish second-declension nouns|Second declension]]'''

{| cellspacing="0" cellpadding="0" style="background-color%3A+transparent%3B+width%3A+95%25" class="inflection-table"

|-

| width="50%25" style="text-align%3Aleft%3Bvertical-align%3Atop%3B" |
Bare forms

{| border="1" cellpadding="4" cellspacing="0" class="toccolours" style="align%3A+left%3B+margin%3A+0.5em+0+0+0%3B+border-style%3A+solid%3B+border%3A+1px+solid+%237f7f7f%3B+border-right-width%3A+2px%3B+border-bottom-width%3A+2px%3B+border-collapse%3A+collapse%3B+font-size%3A+95%25%3B"

|-

!Case


!Singular


!Plural


|-

| [[nominative|Nominative]]


| <span class="Latn" lang="ga">[[cois#Irish|cois]]</span>


| <span class="Latn" lang="ga">[[cosa#Irish|cosa]]</span>


|-

| [[vocative|Vocative]]


| a <span class="Latn" lang="ga">[[chois#Irish|chois]]</span>


| a <span class="Latn" lang="ga">[[chosa#Irish|chosa]]</span>


|-

| [[genitive|Genitive]]


| <span class="Latn" lang="ga">[[coise#Irish|coise]]</span>


| <span class="Latn" lang="ga">[[cos#Irish|cos]]</span>


|-

| [[dative|Dative]]


| <span class="Latn" lang="ga">[[cois#Irish|cois]]</span>


| <span class="Latn" lang="ga">[[cosa#Irish|cosa]]</span>


|}



| width="50%25" style="text-align%3Aleft%3Bvertical-align%3Atop%3B" |
Forms with the [[definite article]]

{| border="1" cellpadding="4" cellspacing="0" class="toccolours" style="align%3A+left%3B+margin%3A+0.5em+0+0+0%3B+border-style%3A+solid%3B+border%3A+1px+solid+%237f7f7f%3B+border-right-width%3A+2px%3B+border-bottom-width%3A+2px%3B+border-collapse%3A+collapse%3B+font-size%3A+95%25%3B"

|-

!Case


!Singular


!Plural


|-

| [[nominative|Nominative]]


| an <span class="Latn" lang="ga">[[chois#Irish|chois]]</span>


| na <span class="Latn" lang="ga">[[cosa#Irish|cosa]]</span>


|-

| [[genitive|Genitive]]


| na <span class="Latn" lang="ga">[[coise#Irish|coise]]</span>


| na <span class="Latn" lang="ga">[[gcos#Irish|gcos]]</span>


|-

| [[dative|Dative]]


| leis an <span class="Latn" lang="ga">[[gcois#Irish|gcois]]</span><br>
don <span class="Latn" lang="ga">[[chois#Irish|chois]]</span>


| leis na <span class="Latn" lang="ga">[[cosa#Irish|cosa]]</span>


|}



|}
</div></div>[[Category:Irish second-declension nouns|COIS]]
""")
        expected = {
            "forms": [
              {
                "form": "cois",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "cosa",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "a chois",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "a chosa",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "coise",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "cos",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "cois",
                "source": "Declension",
                "tags": [
                  "dative",
                  "indefinite",
                  "singular"
                ]
              },
              {
                "form": "cosa",
                "source": "Declension",
                "tags": [
                  "dative",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "an chois",
                "source": "Declension",
                "tags": [
                  "definite",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "na cosa",
                "source": "Declension",
                "tags": [
                  "definite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "na coise",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "na gcos",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "leis an gcois",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "singular"
                ]
              },
              {
                "form": "don chois",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "singular"
                ]
              },
              {
                "form": "leis na cosa",
                "source": "Declension",
                "tags": [
                  "dative",
                  "definite",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Irish_adj1(self):
        ret = self.xinfl("sona", "Irish", "adj", "Declension", """
<div class="NavFrame" style="width%3A+50em">
<div class="NavHead" align="left">[[Appendix:Irish adjectives|Declension]] of <i class="Latn+mention" lang="ga">sona</i></div>
<div class="NavContent" align="center">
<div class="inflection-table">

{| style="background-color%3A%23f0f0f0%3Bborder-collapse%3Aseparate%3Bborder-spacing%3A2px"

|-

| style="width%3A20%25" |


! colspan="2" | Singular


! colspan="2" | Plural (''m/f'')


|-

! Positive


! style="width%3A20%25" | Masculine


! style="width%3A20%25" | Feminine


! style="width%3A20%25" | (''strong noun'')


! style="width%3A20%25" | (''weak noun'')


|-

| Nominative


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" rowspan="2" | <span class="Latn" lang="ga">[[shona#Irish|shona]]</span>


| colspan="2" style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>&#59;<br><span class="Latn" lang="ga">[[shona#Irish|shona]]</span>²


|-

| Vocative


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" rowspan="2" | <span class="Latn" lang="ga">[[shona#Irish|shona]]</span>


| colspan="2" style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>


|-

| Genitive


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>


|-

| Dative


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>&#59;<br><span class="Latn" lang="ga">[[shona#Irish|shona]]</span>¹


| style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[shona#Irish|shona]]</span>


| colspan="2" style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>&#59;<br><span class="Latn" lang="ga">[[shona#Irish|shona]]</span>²


|-

! Comparative


| colspan="4" style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | níos <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>


|-

! Superlative


| colspan="4" style="text-align%3Acenter%3Bbackground-color%3A%23ffffff%3B" | is <span class="Latn" lang="ga">[[sona#Irish|sona]]</span>


|}
</div>
¹ When the preceding noun is lenited and governed by the definite article.<br>
² When the preceding noun ends in a slender consonant.
</div></div>
""")
        expected = {
            "forms": [
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "masculine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "masculine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "masculine",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "masculine",
                  "plural",
                  "strong"
                ]
              },
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "masculine",
                  "plural",
                  "weak"
                ]
              },
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "sona",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "shona",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "níos sona",
                "source": "Declension",
                "tags": [
                  "comparative"
                ]
              },
              {
                "form": "is sona",
                "source": "Declension",
                "tags": [
                  "superlative"
                ]
              },
            ],
        }
        self.assertEqual(expected, ret)

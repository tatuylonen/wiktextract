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

    def test_Finnish_verb1(self):
        # The main point is to test global annotations from table header
        # going into the forms
        ret = self.xinfl("baià", "Lombard", "verb", "Conjugation", """
<div class="NavFrame" style="text-align%3Acenter"><div class="NavHead">[[File:Flag of Milan.svg|20px]]&nbsp;&nbsp;Western Lombard conjugation of baià

([[:Category:Lombard transitive verbs|transitive]])</div><div class="NavContent">

{| style="text-align%3Acenter%3Bbackground%3A%23F9F9F9"

|-

! colspan="3" style="background%3A%23e2e4c0" |infinitive


| colspan="7" |<span class="Latn" lang="lmo">[[baià#Lombard|baià]]</span>


|-

! colspan="3" style="background%3A%23e2e4c0" |gerund


| colspan="7" |<span class="Latn" lang="lmo">[[baiànd#Lombard|baiànd]], [[baiàndo#Lombard|baiàndo]]</span>


|-

! colspan="3" style="background%3A%23e2e4c0" |past participle


| colspan="7" |<span class="Latn" lang="lmo">[[baiàa#Lombard|baiàa]]</span>


|-

! colspan="3" style="background%3A%23e2e4c0" |auxiliary verb


| colspan="7" |<span class="Latn" lang="lmo">[[avè#Lombard|avè]]</span>


|-

! rowspan="2" colspan="2" style="background%3A%23DEDEDE" |


! colspan="3" style="background%3A%23DEDEDE" |singular


! colspan="3" style="background%3A%23DEDEDE" |plural


|-

! style="background%3A%23DEDEDE" |first


! style="background%3A%23DEDEDE" |second


! style="background%3A%23DEDEDE" |third


! style="background%3A%23DEDEDE" |first


! style="background%3A%23DEDEDE" |second


! style="background%3A%23DEDEDE" |third


|-

! rowspan="4" style="background%3A%23c0cfe4" |indicative


! style="background%3A%23c0cfe4" |


! style="background%3A%23c0cfe4" |mì


! style="background%3A%23c0cfe4" |tì te


! style="background%3A%23c0cfe4" |lù el / lee la


! style="background%3A%23c0cfe4" |nun


! style="background%3A%23c0cfe4" |violter / vialter


! style="background%3A%23c0cfe4" |lor


|-

! style="background%3A%23c0cfe4%3Bheight%3A3em" |present


|<span class="Latn" lang="lmo">[[bàii#Lombard|bàii]]</span>


|<span class="Latn" lang="lmo">[[bàiet#Lombard|bàiet]]</span>


|<span class="Latn" lang="lmo">[[bàia#Lombard|bàia]]</span>


|<span class="Latn" lang="lmo">[[bàiom#Lombard|bàiom]]</span>


|<span class="Latn" lang="lmo">[[bàiov#Lombard|bàiov]], [[baiee#Lombard|baiee]]</span>


|<span class="Latn" lang="lmo">[[bàien#Lombard|bàien]]</span>


|-

! style="background%3A%23c0cfe4%3Bheight%3A3em" |imperfect


|<span class="Latn" lang="lmo">[[baiàvi#Lombard|baiàvi]]</span>


|<span class="Latn" lang="lmo">[[baiàvet#Lombard|baiàvet]]</span>


|<span class="Latn" lang="lmo">[[baiàva#Lombard|baiàva]]</span>


|<span class="Latn" lang="lmo">[[baiàvom#Lombard|baiàvom]]</span>


|<span class="Latn" lang="lmo">[[baiàvov#Lombard|baiàvov]]</span>


|<span class="Latn" lang="lmo">[[baiàven#Lombard|baiàven]]</span>


|-

! style="background%3A%23c0cfe4%3Bheight%3A3em" |future


|<span class="Latn" lang="lmo">[[baiaróo#Lombard|baiaróo]]</span>


|<span class="Latn" lang="lmo">[[baiaré#Lombard|baiaré]], [[baiarét#Lombard|baiarét]]</span>


|<span class="Latn" lang="lmo">[[baiarà#Lombard|baiarà]]</span>


|<span class="Latn" lang="lmo">[[baiarèmm#Lombard|baiarèmm]]</span>


|<span class="Latn" lang="lmo">[[baiarii#Lombard|baiarii]]</span>


|<span class="Latn" lang="lmo">[[baiarànn#Lombard|baiarànn]]</span>


|-

! rowspan="2" style="background%3A%23c0d8e4" |conditional


! style="background%3A%23c0d8e4" |


! style="background%3A%23c0d8e4" |mì


! style="background%3A%23c0d8e4" |tì te


! style="background%3A%23c0d8e4" |lù el / lee la


! style="background%3A%23c0d8e4" |nun


! style="background%3A%23c0d8e4" |violter / vialter


! style="background%3A%23c0d8e4" |lor


|-

! style="background%3A%23c0d8e4%3Bheight%3A3em" |present


|<span class="Latn" lang="lmo">[[baiarìa#Lombard|baiarìa]], [[baiarìss#Lombard|baiarìss]], [[baiarìssi#Lombard|baiarìssi]]</span>


|<span class="Latn" lang="lmo">[[baiarìet#Lombard|baiarìet]], [[baiarìsset#Lombard|baiarìsset]]</span>


|<span class="Latn" lang="lmo">[[baiarìa#Lombard|baiarìa]], [[baiarìss#Lombard|baiarìss]]</span>


|<span class="Latn" lang="lmo">[[baiarìom#Lombard|baiarìom]], [[baiarìssom#Lombard|baiarìssom]]</span>


|<span class="Latn" lang="lmo">[[baiarìov#Lombard|baiarìov]], [[baiarìssov#Lombard|baiarìssov]]</span>


|<span class="Latn" lang="lmo">[[baiarìen#Lombard|baiarìen]], [[baiarìssen#Lombard|baiarìssen]]</span>


|-

! rowspan="3" style="background%3A%23c0e4c0" |subjunctive


! style="background%3A%23c0e4c0" |


! style="background%3A%23c0e4c0" |(che) mì


! style="background%3A%23c0e4c0" |(che) tì te


! style="background%3A%23c0e4c0" |(che) lù el / lee la


! style="background%3A%23c0e4c0" |(che) nun


! style="background%3A%23c0e4c0" |(che) violter / vialter


! style="background%3A%23c0e4c0" |(che) lor


|-

! style="background%3A%23c0e4c0%3Bheight%3A3em" |present


|<span class="Latn" lang="lmo">[[bàii#Lombard|bàii]]</span>


|<span class="Latn" lang="lmo">[[bàiet#Lombard|bàiet]]</span>


|<span class="Latn" lang="lmo">[[bàia#Lombard|bàia]]</span>


|<span class="Latn" lang="lmo">[[bàiom#Lombard|bàiom]]</span>


|<span class="Latn" lang="lmo">[[bàiov#Lombard|bàiov]], [[baiii#Lombard|baiii]]</span>


|<span class="Latn" lang="lmo">[[bàien#Lombard|bàien]]</span>


|-

! style="background%3A%23c0e4c0%3Bheight%3A3em" |past


|<span class="Latn" lang="lmo">[[baiàssi#Lombard|baiàssi]]</span>


|<span class="Latn" lang="lmo">[[baiàsset#Lombard|baiàsset]]</span>


|<span class="Latn" lang="lmo">[[baiàss#Lombard|baiàss]]</span>


|<span class="Latn" lang="lmo">[[baiàssom#Lombard|baiàssom]]</span>


|<span class="Latn" lang="lmo">[[baiàssov#Lombard|baiàssov]]</span>


|<span class="Latn" lang="lmo">[[baiàssen#Lombard|baiàssen]]</span>


|-

! colspan="2" rowspan="2" style="background%3A%23e4d4c0" |imperative


! style="background%3A%23e4d4c0" |–


! style="background%3A%23e4d4c0" |<del>tì</del>


! style="background%3A%23e4d4c0" |<del>lù / lee</del><br>che el


! style="background%3A%23e4d4c0" |<del>nun</del>


! style="background%3A%23e4d4c0" |<del>violter / vialter</del>


! style="background%3A%23e4d4c0" |<del>lor</del><br>che el


|-

|–


|<span class="Latn" lang="lmo">[[bàia#Lombard|bàia]]</span>


|<span class="Latn" lang="lmo">[[bàia#Lombard|bàia]]</span>


|<span class="Latn" lang="lmo">[[baièmm#Lombard|baièmm]]</span>


|<span class="Latn" lang="lmo">[[baiee#Lombard|baiee]]</span>


|<span class="Latn" lang="lmo">[[bàien#Lombard|bàien]]</span>


|}
</div></div><div class="NavFrame" style="text-align%3Acenter"><div class="NavHead">[[File:Flag of Bergamo.svg|20px]]&nbsp;&nbsp;Eastern Lombard conjugation of baià
 ([[:Category:Lombard transitive verbs|transitive]])</div><div class="NavContent">

{| style="text-align%3Acenter%3Bbackground%3A%23F9F9F9"

|-

! colspan="3" style="background%3A%23e2e4c0" |infinitive


| colspan="7" |<span class="Latn" lang="lmo">[[baià#Lombard|baià]]</span>


|-

! colspan="3" style="background%3A%23e2e4c0" |past participle


| colspan="7" |<span class="Latn" lang="lmo">[[baiàt#Lombard|baiàt]]</span>


|-

! colspan="3" style="background%3A%23e2e4c0" |auxiliary verb


| colspan="7" |<span class="Latn" lang="lmo">[[ìga#Lombard|ìga]]</span>


|-

! rowspan="2" colspan="2" style="background%3A%23DEDEDE" |


! colspan="3" style="background%3A%23DEDEDE" |singular


! colspan="3" style="background%3A%23DEDEDE" |plural


|-

! style="background%3A%23DEDEDE" |first


! style="background%3A%23DEDEDE" |second


! style="background%3A%23DEDEDE" |third


! style="background%3A%23DEDEDE" |first


! style="background%3A%23DEDEDE" |second


! style="background%3A%23DEDEDE" |third


|-

! rowspan="4" style="background%3A%23c0cfe4" |indicative


! style="background%3A%23c0cfe4" |


! style="background%3A%23c0cfe4" |mé


! style="background%3A%23c0cfe4" |té


! style="background%3A%23c0cfe4" |lü / le


! style="background%3A%23c0cfe4" |nóter


! style="background%3A%23c0cfe4" |vóter


! style="background%3A%23c0cfe4" |lur / lùre


|-

! style="background%3A%23c0cfe4%3Bheight%3A3em" |present


|<span class="Latn" lang="lmo">[[bàie#Lombard|bàie]]</span>


|<span class="Latn" lang="lmo">[[bàiet#Lombard|bàiet]]</span>


|<span class="Latn" lang="lmo">[[bàia#Lombard|bàia]]</span>


|<span class="Latn" lang="lmo">[[baióm#Lombard|baióm]]</span>


|<span class="Latn" lang="lmo">[[baiìf#Lombard|baiìf]]</span>


|<span class="Latn" lang="lmo">[[bàia#Lombard|bàia]]</span>


|-

! style="background%3A%23c0cfe4%3Bheight%3A3em" |imperfect


|<span class="Latn" lang="lmo">[[baiàe#Lombard|baiàe]]</span>


|<span class="Latn" lang="lmo">[[baiàet#Lombard|baiàet]]</span>


|<span class="Latn" lang="lmo">[[baiàa#Lombard|baiàa]]</span>


|<span class="Latn" lang="lmo">[[baiàem#Lombard|baiàem]]</span>


|<span class="Latn" lang="lmo">[[baiàef#Lombard|baiàef]]</span>


|<span class="Latn" lang="lmo">[[baiàa#Lombard|baiàa]]</span>


|-

! style="background%3A%23c0cfe4%3Bheight%3A3em" |future


|<span class="Latn" lang="lmo">[[baiaró#Lombard|baiaró]]</span>


|<span class="Latn" lang="lmo">[[baiarét#Lombard|baiarét]]</span>


|<span class="Latn" lang="lmo">[[baiarà#Lombard|baiarà]]</span>


|<span class="Latn" lang="lmo">[[baiaróm#Lombard|baiaróm]]</span>


|<span class="Latn" lang="lmo">[[baiarìf#Lombard|baiarìf]]</span>


|<span class="Latn" lang="lmo">[[baiarà#Lombard|baiarà]]</span>


|-

! rowspan="2" style="background%3A%23c0d8e4" |conditional


! style="background%3A%23c0d8e4" |


! style="background%3A%23c0d8e4" |mé


! style="background%3A%23c0d8e4" |té


! style="background%3A%23c0d8e4" |lü / lé


! style="background%3A%23c0d8e4" |nóter


! style="background%3A%23c0d8e4" |vóter


! style="background%3A%23c0d8e4" |lur / lúre


|-

! style="background%3A%23c0d8e4%3Bheight%3A3em" |present


|<span class="Latn" lang="lmo">[[baiarèse#Lombard|baiarèse]]</span>


|<span class="Latn" lang="lmo">[[baiarèset#Lombard|baiarèset]]</span>


|<span class="Latn" lang="lmo">[[baiarès#Lombard|baiarès]]</span>


|<span class="Latn" lang="lmo">[[baiarèsem#Lombard|baiarèsem]]</span>


|<span class="Latn" lang="lmo">[[baiarèsef#Lombard|baiarèsef]]</span>


|<span class="Latn" lang="lmo">[[baiarès#Lombard|baiarès]]</span>


|-

! rowspan="3" style="background%3A%23c0e4c0" |subjunctive


! style="background%3A%23c0e4c0" |


! style="background%3A%23c0e4c0" |(che) mé


! style="background%3A%23c0e4c0" |(che) té


! style="background%3A%23c0e4c0" |(che) lü / lé


! style="background%3A%23c0e4c0" |(che) nóter


! style="background%3A%23c0e4c0" |(che) vóter


! style="background%3A%23c0e4c0" |(che) lur / lùre


|-

! style="background%3A%23c0e4c0%3Bheight%3A3em" |present


|<span class="Latn" lang="lmo">[[bàies#Lombard|bàies]]</span>


|<span class="Latn" lang="lmo">[[bàies#Lombard|bàies]]</span>


|<span class="Latn" lang="lmo">[[bàie#Lombard|bàie]]</span>


|<span class="Latn" lang="lmo">[[baiómes#Lombard|baiómes]]</span>


|<span class="Latn" lang="lmo">[[baiìghes#Lombard|baiìghes]]</span>


|<span class="Latn" lang="lmo">[[bàie#Lombard|bàie]]</span>


|-

! style="background%3A%23c0e4c0%3Bheight%3A3em" |past


|<span class="Latn" lang="lmo">[[baièse#Lombard|baièse]]</span>


|<span class="Latn" lang="lmo">[[baièset#Lombard|baièset]]</span>


|<span class="Latn" lang="lmo">[[baiès#Lombard|baiès]]</span>


|<span class="Latn" lang="lmo">[[baièsem#Lombard|baièsem]]</span>


|<span class="Latn" lang="lmo">[[baièsef#Lombard|baièsef]]</span>


|<span class="Latn" lang="lmo">[[baiès#Lombard|baiès]]</span>


|-

! colspan="2" style="background%3A%23e4d4c0" |imperative


! style="background%3A%23e4d4c0" |–


! style="background%3A%23e4d4c0" |<del>té</del>


! style="background%3A%23e4d4c0" |–


! style="background%3A%23e4d4c0" |<del>nóter</del>


! style="background%3A%23e4d4c0" |<del>vóter</del>


! style="background%3A%23e4d4c0" |–


|-

| colspan="2" style="background%3A%23e4d4c0" |


|–


|<span class="Latn" lang="lmo">[[bàia#Lombard|bàia]]</span>


|–


|<span class="Latn" lang="lmo">[[baiómm#Lombard|baiómm]]</span>


|<span class="Latn" lang="lmo">[[baiì#Lombard|baiì]]</span>


|–


|}
</div></div>
""")
        expected = {
            "forms": [
              {
                "form": "baià",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "infinitive"
                ]
              },
              {
                "form": "baiànd",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "gerund"
                ]
              },
              {
                "form": "baiàndo",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "gerund"
                ]
              },
              {
                "form": "baiàa",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "avè",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "auxiliary"
                ]
              },
              {
                "form": "bàii",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "bàiet",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "bàia",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "bàiom",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "bàiov",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "baiee",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "bàien",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "baiàvi",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "baiàvet",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiàva",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baiàvom",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "baiàvov",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "baiàven",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "baiaróo",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "baiaré",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiarét",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiarà",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baiarèmm",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "baiarii",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "baiarànn",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "baiarìa",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "baiarìss",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "baiarìssi",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "baiarìet",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiarìsset",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiarìa",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baiarìss",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baiarìom",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "baiarìssom",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "baiarìov",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "baiarìssov",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "baiarìen",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "baiarìssen",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "conditional",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "bàii",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "bàiet",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "bàia",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "bàiom",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "bàiov",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "baiii",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "bàien",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "baiàssi",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "past",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "baiàsset",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "past",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "baiàss",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "past",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "baiàssom",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "past",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "baiàssov",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "past",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "baiàssen",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "past",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "bàia",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "bàia",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baièmm",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "baiee",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "bàien",
                "source": "Conjugation",
                "tags": [
                  "Western-Lombard",
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "transitive",
                "source": "Conjugation title",
                "tags": [
                  "word-tags"
                ]
              },
              {
                "form": "baià",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "infinitive"
                ]
              },
              {
                "form": "baiàt",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "ìga",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "auxiliary"
                ]
              },
              {
                "form": "bàie",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "bàiet",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "bàia",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baióm",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "baiìf",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "bàia",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "baiàe",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "baiàet",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiàa",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baiàem",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "baiàef",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "baiàa",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "baiaró",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "baiarét",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiarà",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baiaróm",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "baiarìf",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "baiarà",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "baiarèse",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "conditional",
                  "first-person",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "baiarèset",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "conditional",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiarès",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "conditional",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "baiarèsem",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "conditional",
                  "first-person",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "baiarèsef",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "conditional",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "baiarès",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "conditional",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "bàies",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "bàies",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "bàie",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "baiómes",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "baiìghes",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "bàie",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "baièse",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "past",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "baièset",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "past",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "baiès",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "past",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "baièsem",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "past",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "baièsef",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "past",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "baiès",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "past",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "bàia",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "baiómm",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "baiì",
                "source": "Conjugation",
                "tags": [
                  "Eastern-Lombard",
                  "imperative",
                  "plural",
                  "second-person"
                ]
              }
            ],
        }
        self.assertEqual(ret, expected)

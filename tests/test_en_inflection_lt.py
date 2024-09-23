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
        parse_inflection_section(self.wxr, data, word, lang, pos,
                                 section, tree)
        return data

    def test_Lithuanian_verb1(self):
        ret = self.xinfl("važiuoti", "Lithuanian", "verb", "Conjugation", """
<div class="NavFrame" style>
<div class="NavHead" style>Conjugation of <i class="Latn+mention" lang="lt">[[važiuoti#Lithuanian|važiuoti]]</i></div>
<div class="NavContent">


{| border="1" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! colspan="2" rowspan="2" style="background%3A%23DEDEDE" |


! colspan="3" style="background%3A%23DEDEDE" | singular <br><small>([[vienaskaita]])</small>


! rowspan="9" style="background%3A%23DEDEDE%3Bwidth%3A1em" |


! colspan="3" style="background%3A%23DEDEDE" | plural <br><small>([[daugiskaita]])</small>


|-

! style="background%3A%23DEDEDE" | 1<sup>st</sup> person <br><small>([[pirmasis]] [[asmuo]])</small>


! style="background%3A%23DEDEDE" | 2<sup>nd</sup> person <br><small>([[antrasis]] [[asmuo]])</small>


! style="background%3A%23DEDEDE" | 3<sup>rd</sup> person <br><small>([[trečiasis]] [[asmuo]])</small>


! style="background%3A%23DEDEDE" | 1<sup>st</sup> person <br><small>([[pirmasis]] [[asmuo]])</small>


! style="background%3A%23DEDEDE" | 2<sup>nd</sup> person <br><small>([[antrasis]] [[asmuo]])</small>


! style="background%3A%23DEDEDE" | 3<sup>rd</sup> person <br><small>([[trečiasis]] [[asmuo]])</small>


|-

! colspan="2" style="background%3A%23EFEFEF" |


! style="background%3A%23EFEFEF" | aš


! style="background%3A%23EFEFEF" | tu


! style="background%3A%23EFEFEF" | jis/ji


! style="background%3A%23EFEFEF" | mes


! style="background%3A%23EFEFEF" | jūs


! style="background%3A%23EFEFEF" | jie/jos


|-

! rowspan="4" style="background%3A%23EFEFEF" | indicative <br><small>([[tiesioginė nuosaka|tiesioginė <br>nuosaka]])</small>


! style="background%3A%23EFEFEF" | present <br><small>([[esamasis laikas]])</small>


| <span class="Latn" lang="lt">[[važiuoju#Lithuanian|važiuoju]]</span>


| <span class="Latn" lang="lt">[[važiuoji#Lithuanian|važiuoji]]</span>


| <span class="Latn" lang="lt">[[važiuoja#Lithuanian|važiuoja]]</span>


| <span class="Latn" lang="lt">[[važiuojame#Lithuanian|važiuojame]]</span>, <br><small>važiuojam</small>


| <span class="Latn" lang="lt">[[važiuojate#Lithuanian|važiuojate]]</span>, <br><small>važiuojat</small>


| <span class="Latn" lang="lt">[[važiuoja#Lithuanian|važiuoja]]</span>


|-

! style="background%3A%23EFEFEF" | past <br><small>([[būtasis kartinis laikas|būtasis kartinis <br>laikas]])</small>


| <span class="Latn" lang="lt">[[važiavau#Lithuanian|važiavau]]</span>


| <span class="Latn" lang="lt">[[važiavai#Lithuanian|važiavai]]</span>


| <span class="Latn" lang="lt">[[važiavo#Lithuanian|važiavo]]</span>


| <span class="Latn" lang="lt">[[važiavome#Lithuanian|važiavome]]</span>, <br><small>važiavom</small>


| <span class="Latn" lang="lt">[[važiavote#Lithuanian|važiavote]]</span>, <br><small>važiavot</small>


| <span class="Latn" lang="lt">[[važiavo#Lithuanian|važiavo]]</span>


|-

! style="background%3A%23EFEFEF" | past frequentative <br><small>([[būtasis dažninis laikas|būtasis dažninis <br>laikas]])</small>


| <span class="Latn" lang="lt">[[važiuodavau#Lithuanian|važiuodavau]]</span>


| <span class="Latn" lang="lt">[[važiuodavai#Lithuanian|važiuodavai]]</span>


| <span class="Latn" lang="lt">[[važiuodavo#Lithuanian|važiuodavo]]</span>


| <span class="Latn" lang="lt">[[važiuodavome#Lithuanian|važiuodavome]]</span>, <br><small>važiuodavom</small>


| <span class="Latn" lang="lt">[[važiuodavote#Lithuanian|važiuodavote]]</span>, <br><small>važiuodavot</small>


| <span class="Latn" lang="lt">[[važiuodavo#Lithuanian|važiuodavo]]</span>


|-

! style="background%3A%23EFEFEF" | future <br><small>([[būsimasis laikas]])</small>


| <span class="Latn" lang="lt">[[važiuosiu#Lithuanian|važiuosiu]]</span>


| <span class="Latn" lang="lt">[[važiuosi#Lithuanian|važiuosi]]</span>


| <span class="Latn" lang="lt">[[važiuos#Lithuanian|važiuos]]</span>


| <span class="Latn" lang="lt">[[važiuosime#Lithuanian|važiuosime]]</span>, <br><small>važiuosim</small>


| <span class="Latn" lang="lt">[[važiuosite#Lithuanian|važiuosite]]</span>, <br><small>važiuosit</small>


| <span class="Latn" lang="lt">[[važiuos#Lithuanian|važiuos]]</span>


|-

! colspan="2" style="background%3A%23EFEFEF" | subjunctive <br><small>([[tariamoji nuosaka]])</small>


| <span class="Latn" lang="lt">[[važiuočiau#Lithuanian|važiuočiau]]</span>


| <span class="Latn" lang="lt">[[važiuotum#Lithuanian|važiuotum]]</span>, <br><small>važiuotumei</small>


| <span class="Latn" lang="lt">[[važiuotų#Lithuanian|važiuotų]]</span>


| <span class="Latn" lang="lt">[[važiuotumėme#Lithuanian|važiuotumėme]]</span>, <br><small>važiuotumėm, <br>važiuotume</small>


| <span class="Latn" lang="lt">[[važiuotumėte#Lithuanian|važiuotumėte]]</span>, <br><small>važiuotumėt</small>


| <span class="Latn" lang="lt">[[važiuotų#Lithuanian|važiuotų]]</span>


|-

! colspan="2" style="background%3A%23EFEFEF" | imperative <br><small>([[liepiamoji nuosaka]])</small>


| —


| <span class="Latn" lang="lt">[[važiuok#Lithuanian|važiuok]]</span>, <br><small>važiuoki</small>


| <span class="Latn" lang="lt">[[tevažiuoja#Lithuanian|tevažiuoja]]</span>, <br><small>tevažiuojie</small>


| <span class="Latn" lang="lt">[[važiuokime#Lithuanian|važiuokime]]</span>, <br><small>važiuokim</small>


| <span class="Latn" lang="lt">[[važiuokite#Lithuanian|važiuokite]]</span>, <br><small>važiuokit</small>


| <span class="Latn" lang="lt">[[tevažiuoja#Lithuanian|tevažiuoja]]</span>, <br><small>tevažiuojie</small>


|}
</div></div>

<div class="NavFrame" style="width%3A75%25">
<div class="NavHead" style>Participles of <i class="Latn+mention" lang="lt">[[važiuoti#Lithuanian|važiuoti]]</i></div>
<div class="NavContent">


{| border="1" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! colspan="4" style="background%3A%23DEDEDE" |Adjectival <small>([[dalyviai]])</small>


|-

! colspan="2" style="background%3A%23DEDEDE%3Bwidth%3A33%25" |


! style="background%3A%23DEDEDE" | active


! style="background%3A%23DEDEDE" | passive


|-

! colspan="2" style="background%3A%23EFEFEF" | present


| <span class="Latn" lang="lt">[[važiuojąs#Lithuanian|važiuojąs]]</span>, <span class="Latn" lang="lt">[[važiuojantis#Lithuanian|važiuojantis]]</span>


| <span class="Latn" lang="lt">[[važiuojamas#Lithuanian|važiuojamas]]</span>



|-

! colspan="2" style="background%3A%23EFEFEF" | past


| <span class="Latn" lang="lt">[[važiavęs#Lithuanian|važiavęs]]</span>


| <span class="Latn" lang="lt">[[važiuotas#Lithuanian|važiuotas]]</span>


|-

! colspan="2" style="background%3A%23EFEFEF" | past frequentative


| <span class="Latn" lang="lt">[[važiuodavęs#Lithuanian|važiuodavęs]]</span>


| —


|-

! colspan="2" style="background%3A%23EFEFEF" | future


| <span class="Latn" lang="lt">[[važiuosiąs#Lithuanian|važiuosiąs]]</span>, <span class="Latn" lang="lt">[[važiuosiantis#Lithuanian|važiuosiantis]]</span>


| <span class="Latn" lang="lt">[[važiuosimas#Lithuanian|važiuosimas]]</span>


|-

! colspan="2" style="background%3A%23EFEFEF" | participle of necessity


| —


| <span class="Latn" lang="lt">[[važiuotinas#Lithuanian|važiuotinas]]</span>


|-

! colspan="4" style="background%3A%23DEDEDE%3Bheight%3A.5em" | Adverbial


|-

! colspan="2" style="background%3A%23EFEFEF" |special <small>([[pusdalyvis]])</small>


|<span class="Latn" lang="lt">[[važiuodamas#Lithuanian|važiuodamas]]</span>


!


|-

! rowspan="4" style="background%3A%23EFEFEF" |half-participle <br><small>([[padalyvis|padalyviai]])</small>


! style="background%3A%23EFEFEF" | present


|<span class="Latn" lang="lt">[[važiuojant#Lithuanian|važiuojant]]</span>


!


|-

! style="background%3A%23EFEFEF" | past


|<span class="Latn" lang="lt">[[važiavus#Lithuanian|važiavus]]</span>


!


|-

! style="background%3A%23EFEFEF" | past frequentative


|<span class="Latn" lang="lt">[[važiuodavus#Lithuanian|važiuodavus]]</span>


!


|-

! style="background%3A%23EFEFEF" | future


|<span class="Latn" lang="lt">[[važiuosiant#Lithuanian|važiuosiant]]</span>


!


|-

! colspan="2" style="background%3A%23EFEFEF" |manner of action <small>([[būdinys]])</small>


|<span class="Latn" lang="lt">[[važiuote#Lithuanian|važiuote]]</span>, <span class="Latn" lang="lt">[[važiuotinai#Lithuanian|važiuotinai]]</span>


!


|}
</div></div>
""")  # noqa: E501
        expected = {
            "forms": [
              {
                "form": "no-table-tags",
                "source": "Conjugation",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "važiuoju",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "važiuoji",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "važiuoja",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "važiuojame",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "važiuojam",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "važiuojate",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "važiuojat",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "važiuoja",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "važiavau",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "važiavai",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "važiavo",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "važiavome",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "važiavom",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "važiavote",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "važiavot",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "važiavo",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "važiuodavau",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "frequentative",
                  "indicative",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "važiuodavai",
                "source": "Conjugation",
                "tags": [
                  "frequentative",
                  "indicative",
                  "past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "važiuodavo",
                "source": "Conjugation",
                "tags": [
                  "frequentative",
                  "indicative",
                  "past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "važiuodavome",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "frequentative",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "važiuodavom",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "frequentative",
                  "indicative",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "važiuodavote",
                "source": "Conjugation",
                "tags": [
                  "frequentative",
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "važiuodavot",
                "source": "Conjugation",
                "tags": [
                  "frequentative",
                  "indicative",
                  "past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "važiuodavo",
                "source": "Conjugation",
                "tags": [
                  "frequentative",
                  "indicative",
                  "past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "važiuosiu",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "važiuosi",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "važiuos",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "važiuosime",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "važiuosim",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "važiuosite",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "važiuosit",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "važiuos",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "važiuočiau",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotum",
                "source": "Conjugation",
                "tags": [
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotumei",
                "source": "Conjugation",
                "tags": [
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotų",
                "source": "Conjugation",
                "tags": [
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "važiuotumėme",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotumėm",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotume",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotumėte",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotumėt",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "važiuotų",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person', 'imperative', 'singular']},
              {
                "form": "važiuok",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "važiuoki",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "tevažiuoja",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "tevažiuojie",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "važiuokime",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "važiuokim",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "važiuokite",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "važiuokit",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "tevažiuoja",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "tevažiuojie",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "no-table-tags",
                "source": "Conjugation",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "važiuojąs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "važiuojantis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "važiuojamas",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "participle",
                  "passive",
                  "present"
                ]
              },
              {
                "form": "važiavęs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "važiuotas",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "participle",
                  "passive",
                  "past"
                ]
              },
              {
                "form": "važiuodavęs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "frequentative",
                  "participle",
                  "past"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['adjectival',
                        'frequentative',
                        'participle',
                        'passive',
                        'past']},
              {
                "form": "važiuosiąs",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "future",
                  "participle"
                ]
              },
              {
                "form": "važiuosiantis",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adjectival",
                  "future",
                  "participle"
                ]
              },
              {
                "form": "važiuosimas",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "future",
                  "participle",
                  "passive"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['active', 'adjectival', 'necessitative', 'participle']},
              {
                "form": "važiuotinas",
                "source": "Conjugation",
                "tags": [
                  "adjectival",
                  "necessitative",
                  "participle",
                  "passive"
                ]
              },
              {
                "form": "važiuodamas",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "participle",
                  "special"
                ]
              },
              {
                "form": "važiuojant",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "half-participle",
                  "participle",
                  "present"
                ]
              },
              {
                "form": "važiavus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "half-participle",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "važiuodavus",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "frequentative",
                  "half-participle",
                  "participle",
                  "past"
                ]
              },
              {
                "form": "važiuosiant",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "future",
                  "half-participle",
                  "participle"
                ]
              },
              {
                "form": "važiuote",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "adverbial-manner",
                  "participle"
                ]
              },
              {
                "form": "važiuotinai",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "adverbial",
                  "adverbial-manner",
                  "participle"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_Lithuanian_noun1(self):
        ret = self.xinfl("akis", "Lithuanian", "noun", "Declension", """
<div class="NavFrame" style>
<div class="NavHead" style>declension of akis</div>
<div class="NavContent">


{| border="1" color="%23cdcdcd" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25" class="inflection-table"

|-

! style="width%3A30%25%3Bbackground%3A%23DEDEDE" |


! style="width%3A35%25%3Bbackground%3A%23DEDEDE" | singular <small>([[vienaskaita]])</small>


! style="width%3A35%25%3Bbackground%3A%23DEDEDE" | plural <small>([[daugiskaita]])</small>


|-

! style="background%3A%23EFEFEF" | nominative <small>([[vardininkas]])</small>


| <span class="Latn" lang="lt">[[akis#Lithuanian|akìs]]</span>


| <span class="Latn" lang="lt">[[akys#Lithuanian|ãkys]]</span>


|-

! style="background%3A%23EFEFEF" | genitive <small>([[kilmininkas]])</small>


| <span class="Latn" lang="lt">[[akies#Lithuanian|akiẽs]]</span>


| <span class="Latn" lang="lt">[[akių#Lithuanian|akių̃]]</span>


|-

! style="background%3A%23EFEFEF" | dative <small>([[naudininkas]])</small>


| <span class="Latn" lang="lt">[[akiai#Lithuanian|ãkiai]]</span>


| <span class="Latn" lang="lt">[[akims#Lithuanian|akìms]]</span>


|-

! style="background%3A%23EFEFEF" | accusative <small>([[galininkas]])</small>


| <span class="Latn" lang="lt">[[akį#Lithuanian|ãkį]]</span>


| <span class="Latn" lang="lt">[[akis#Lithuanian|akìs]]</span>


|-

! style="background%3A%23EFEFEF" | instrumental <small>([[įnagininkas]])</small>


| <span class="Latn" lang="lt">[[akimi#Lithuanian|akimì]]</span>


| <span class="Latn" lang="lt">[[akimis#Lithuanian|akimìs]]</span>


|-

! style="background%3A%23EFEFEF" | locative <small>([[vietininkas]])</small>


| <span class="Latn" lang="lt">[[akyje#Lithuanian|akyjè]]</span>


| <span class="Latn" lang="lt">[[akyse#Lithuanian|akysè]]</span>


|-

! style="background%3A%23EFEFEF" | vocative <small>([[šauksmininkas]])</small>


| <span class="Latn" lang="lt">[[akie#Lithuanian|akiẽ]]</span>


| <span class="Latn" lang="lt">[[akys#Lithuanian|ãkys]]</span>


|}
</div></div>
""")  # noqa: E501
        expected = {
            "forms": [
              {
                "form": "no-table-tags",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "akìs",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "ãkys",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "akiẽs",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "akių̃",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "ãkiai",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "akìms",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "ãkį",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "singular"
                ]
              },
              {
                "form": "akìs",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural"
                ]
              },
              {
                "form": "akimì",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "akimìs",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "akyjè",
                "source": "Declension",
                "tags": [
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "akysè",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "akiẽ",
                "source": "Declension",
                "tags": [
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "ãkys",
                "source": "Declension",
                "tags": [
                  "plural",
                  "vocative"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

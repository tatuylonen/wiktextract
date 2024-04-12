# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.inflection import parse_inflection_section
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class InflTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 100000
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

    def test_Portuguese_verb1(self):
        ret = self.xinfl("viajar", "Portuguese", "verb", "Conjugation", """
<div class="NavFrame" style="clear%3Aboth%3B+white-space%3A+nowrap">
<div class="NavHead">&nbsp;&nbsp;Conjugation of the [[Appendix:Portuguese verbs|Portuguese ''-ar'' verb]] ''viajar''</div>
<div class="NavContent" align="left">

{| class="inflection-table" style="background%3A%23F6F6F6%3B+text-align%3A+left%3B+border%3A+1px+solid+%23999999%3B" cellpadding="3" cellspacing="0"

|-

| style="border%3A+1px+solid+%23999999%3B" colspan="7" | '''Notes''':<sup class="plainlinks">[//wiki.local/w/index.php?action=edit&title=Module%3Apt-conj%2Fdata%2F-ar [edit]]</sup>
* This is a regular verb of the '''-ar''' group.
*
* Verbs with this conjugation include: <i class="Latn+mention" lang="pt">[[amar#Portuguese|amar]]</i>, <i class="Latn+mention" lang="pt">[[cantar#Portuguese|cantar]]</i>, <i class="Latn+mention" lang="pt">[[gritar#Portuguese|gritar]]</i>, <i class="Latn+mention" lang="pt">[[marchar#Portuguese|marchar]]</i>, <i class="Latn+mention" lang="pt">[[mostrar#Portuguese|mostrar]]</i>, <i class="Latn+mention" lang="pt">[[nadar#Portuguese|nadar]]</i>, <i class="Latn+mention" lang="pt">[[parar#Portuguese|parar]]</i>, <i class="Latn+mention" lang="pt">[[participar#Portuguese|participar]]</i>, <i class="Latn+mention" lang="pt">[[retirar#Portuguese|retirar]]</i>, <i class="Latn+mention" lang="pt">[[separar#Portuguese|separar]]</i>, <i class="Latn+mention" lang="pt">[[viajar#Portuguese|viajar]]</i>.


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23B0B0B0" rowspan="2" |


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0" colspan="3" | Singular


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0" colspan="3" | Plural


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A12.5%25" | First-person<br>([[eu#Portuguese|eu]])


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A12.5%25" | Second-person<br>([[tu#Portuguese|tu]])


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A12.5%25" | Third-person<br>([[ele#Portuguese|ele]] / [[ela#Portuguese|ela]] / [[você#Portuguese|você]])


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A12.5%25" | First-person<br>([[nós#Portuguese|nós]])


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A12.5%25" | Second-person<br>([[vós#Portuguese|vós]])


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A12.5%25" | Third-person<br>([[eles#Portuguese|eles]] / [[elas#Portuguese|elas]] / [[vocês#Portuguese|vocês]])


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23c498ff" colspan="7" | ''<span title="infinitivo">Infinitive</span>''


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23a478df" | '''<span title="infinitivo+impessoal">Impersonal</span>'''


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" colspan="6" | <span class="Latn" lang="pt">[[viajar#Portuguese|viajar]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23a478df" | '''<span title="infinitivo+pessoal">Personal</span>'''


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajar#Portuguese|viajar]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajares#Portuguese|viajares]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajar#Portuguese|viajar]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarmos#Portuguese|viajarmos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajardes#Portuguese|viajardes]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarem#Portuguese|viajarem]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%2398ffc4" colspan="7" | ''<span title="ger%C3%BAndio">Gerund</span>''


|-

| style="border%3A+1px+solid+%23999999%3B+background%3A%2378dfa4" |


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" colspan="6" | <span class="Latn" lang="pt">[[viajando#Portuguese|viajando]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23ffc498" colspan="7" | ''<span title="partic%C3%ADpio+passado">Past participle</span>''


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23dfa478" | Masculine


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" colspan="3" | <span class="Latn" lang="pt">[[viajado#Portuguese|viajado]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" colspan="3" | <span class="Latn" lang="pt">[[viajados#Portuguese|viajados]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23dfa478" | Feminine


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" colspan="3" | <span class="Latn" lang="pt">[[viajada#Portuguese|viajada]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" colspan="3" | <span class="Latn" lang="pt">[[viajadas#Portuguese|viajadas]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23d0dff4" colspan="7" | ''<span title="indicativo">Indicative</span>''


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | <span title="presente">Present</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajo#Portuguese|viajo]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajas#Portuguese|viajas]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viaja#Portuguese|viaja]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajamos#Portuguese|viajamos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajais#Portuguese|viajais]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajam#Portuguese|viajam]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | <span title="pret%C3%A9rito+imperfeito">Imperfect</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajava#Portuguese|viajava]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajavas#Portuguese|viajavas]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajava#Portuguese|viajava]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajávamos#Portuguese|viajávamos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajáveis#Portuguese|viajáveis]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajavam#Portuguese|viajavam]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | <span title="pret%C3%A9rito+perfeito">Preterite</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajei#Portuguese|viajei]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaste#Portuguese|viajaste]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajou#Portuguese|viajou]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajamos#Portuguese|viajamos]]</span><br><span class="Latn" lang="pt">[[viajámos#Portuguese|viajámos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajastes#Portuguese|viajastes]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaram#Portuguese|viajaram]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | <span title="pret%C3%A9rito+mais-que-perfeito+simples">Pluperfect</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajara#Portuguese|viajara]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaras#Portuguese|viajaras]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajara#Portuguese|viajara]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajáramos#Portuguese|viajáramos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajáreis#Portuguese|viajáreis]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaram#Portuguese|viajaram]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | <span title="futuro+do+presente">Future</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarei#Portuguese|viajarei]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarás#Portuguese|viajarás]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajará#Portuguese|viajará]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaremos#Portuguese|viajaremos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajareis#Portuguese|viajareis]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarão#Portuguese|viajarão]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23ffffaa" colspan="7" | ''<span title="condicional+%2F+futuro+do+pret%C3%A9rito">Conditional</span>''


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23ddddaa" |


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaria#Portuguese|viajaria]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarias#Portuguese|viajarias]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaria#Portuguese|viajaria]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaríamos#Portuguese|viajaríamos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajaríeis#Portuguese|viajaríeis]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajariam#Portuguese|viajariam]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23d0f4d0" colspan="7" | ''<span title="conjuntivo+%28pt%29+%2F+subjuntivo+%28br%29">Subjunctive</span>''


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0d4b0" | <span title="+presente+do+conjuntivo+%28pt%29+%2F+subjuntivo+%28br%29">Present</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viaje#Portuguese|viaje]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajes#Portuguese|viajes]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viaje#Portuguese|viaje]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajemos#Portuguese|viajemos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajeis#Portuguese|viajeis]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajem#Portuguese|viajem]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0d4b0" | <span title="pret%C3%A9rito+imperfeito+do+conjuntivo+%28pt%29+%2F+subjuntivo+%28br%29">Imperfect</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajasse#Portuguese|viajasse]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajasses#Portuguese|viajasses]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajasse#Portuguese|viajasse]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajássemos#Portuguese|viajássemos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajásseis#Portuguese|viajásseis]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajassem#Portuguese|viajassem]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0d4b0" | <span title="futuro+do+conjuntivo+%28pt%29+%2F+subjuntivo+%28br%29">Future</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajar#Portuguese|viajar]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajares#Portuguese|viajares]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajar#Portuguese|viajar]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarmos#Portuguese|viajarmos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajardes#Portuguese|viajardes]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajarem#Portuguese|viajarem]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23f4e4d0" colspan="7" | ''<span title="imperativo">Imperative</span>''


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23d4c4b0" | <span title="imperativo+afirmativo">Affirmative</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | -


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viaja#Portuguese|viaja]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viaje#Portuguese|viaje]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajemos#Portuguese|viajemos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajai#Portuguese|viajai]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajem#Portuguese|viajem]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23d4c4b0" | <span title="imperativo+negativo">Negative</span> ([[não#Portuguese|não]])


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | -


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajes#Portuguese|viajes]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viaje#Portuguese|viaje]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajemos#Portuguese|viajemos]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajeis#Portuguese|viajeis]]</span>


| style="border%3A+1px+solid+%23999999%3B+vertical-align%3A+top%3B" | <span class="Latn" lang="pt">[[viajem#Portuguese|viajem]]</span>


|}

            </div>
            </div>
""")
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
                "form": "-ar verb",
                "source": "Conjugation",
                "tags": [
                  "class"
                ]
              },
              {
                "form": "viajar",
                "source": "Conjugation",
                "tags": [
                  "impersonal",
                  "infinitive"
                ]
              },
              {
                "form": "viajar",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "infinitive",
                  "singular"
                ]
              },
              {
                "form": "viajares",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viajar",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajarmos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "infinitive",
                  "plural"
                ]
              },
              {
                "form": "viajardes",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "viajarem",
                "source": "Conjugation",
                "tags": [
                  "infinitive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "viajando",
                "source": "Conjugation",
                "tags": [
                  "gerund"
                ]
              },
              {
                "form": "viajado",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "participle",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "viajados",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "participle",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "viajada",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "participle",
                  "past",
                  "singular"
                ]
              },
              {
                "form": "viajadas",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "participle",
                  "past",
                  "plural"
                ]
              },
              {
                "form": "viajo",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "present",
                  "singular"
                ]
              },
              {
                "form": "viajas",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viaja",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "present",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "present"
                ]
              },
              {
                "form": "viajais",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "second-person"
                ]
              },
              {
                "form": "viajam",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "present",
                  "third-person"
                ]
              },
              {
                "form": "viajava",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "viajavas",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viajava",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajávamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "viajáveis",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "viajavam",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "viajei",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "preterite",
                  "singular"
                ]
              },
              {
                "form": "viajaste",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viajou",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "preterite",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajamos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "preterite"
                ]
              },
              {
                "form": "viajámos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "plural",
                  "preterite"
                ]
              },
              {
                "form": "viajastes",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "second-person"
                ]
              },
              {
                "form": "viajaram",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "plural",
                  "preterite",
                  "third-person"
                ]
              },
              {
                "form": "viajara",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "singular"
                ]
              },
              {
                "form": "viajaras",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viajara",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajáramos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "pluperfect",
                  "plural"
                ]
              },
              {
                "form": "viajáreis",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "viajaram",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "pluperfect",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "viajarei",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "singular"
                ]
              },
              {
                "form": "viajarás",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viajará",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajaremos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "indicative",
                  "plural"
                ]
              },
              {
                "form": "viajareis",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "viajarão",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "indicative",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "viajaria",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "singular"
                ]
              },
              {
                "form": "viajarias",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viajaria",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajaríamos",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "first-person",
                  "plural"
                ]
              },
              {
                "form": "viajaríeis",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "viajariam",
                "source": "Conjugation",
                "tags": [
                  "conditional",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "viaje",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "present",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "viajes",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "viaje",
                "source": "Conjugation",
                "tags": [
                  "present",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "viajemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "plural",
                  "present",
                  "subjunctive"
                ]
              },
              {
                "form": "viajeis",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "viajem",
                "source": "Conjugation",
                "tags": [
                  "plural",
                  "present",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "viajasse",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "viajasses",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "viajasse",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "viajássemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfect",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "viajásseis",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "viajassem",
                "source": "Conjugation",
                "tags": [
                  "imperfect",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "viajar",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "viajares",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "viajar",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "viajarmos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "future",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "viajardes",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "viajarem",
                "source": "Conjugation",
                "tags": [
                  "future",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person', 'imperative', 'singular']},
              {
                "form": "viaja",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viaje",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "plural"
                ]
              },
              {
                "form": "viajai",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "viajem",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "plural",
                  "third-person"
                ]
              },
              {'form': '-',
               'source': 'Conjugation',
               'tags': ['first-person', 'imperative', 'negative', 'singular']},
              {
                "form": "viajes",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "viaje",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "viajemos",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperative",
                  "negative",
                  "plural"
                ]
              },
              {
                "form": "viajeis",
                "source": "Conjugation",
                "tags": [
                  "imperative",
                  "negative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "viajem",
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

    def test_Portuguese_adj1(self):
        ret = self.xinfl("lindo", "Portuguese", "adj", "Conjugation", """
<div class="NavFrame" style="clear%3Aboth%3B+white-space%3A+nowrap%3B+max-width%3A+50em">
<div class="NavHead">Inflection of <i class="Latn+mention" lang="pt">lindo</i></div>
<div class="NavContent">

{| style="border%3A+1px+solid+%23999999%3B+width%3A+100%25%3B+background%3A%23F6F6F6%3B" cellpadding="3" cellspacing="0" class="inflection-table"

|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23B0B0B0" rowspan="2" |


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0" colspan="2" | singular


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0" colspan="2" | plural


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A21%25" | masculine


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A21%25" | feminine


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A21%25" | masculine


! style="border%3A+1px+solid+%23999999%3B+background%3A%23D0D0D0%3B+width%3A21%25" | feminine


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | [[Appendix:Glossary#positive|positive]]


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindo#Portuguese|lindo]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[linda#Portuguese|linda]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindos#Portuguese|lindos]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindas#Portuguese|lindas]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | [[Appendix:Glossary#comparative|comparative]]


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[mais#Portuguese|mais]] lindo</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[mais#Portuguese|mais]] linda</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[mais#Portuguese|mais]] lindos</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[mais#Portuguese|mais]] lindas</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | [[Appendix:Glossary#superlative|superlative]]


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[o#Portuguese|o]] [[mais#Portuguese|mais]] lindo</span><br><span class="Latn" lang="pt">[[lindíssimo#Portuguese|lindíssimo]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[a#Portuguese|a]] [[mais#Portuguese|mais]] linda</span><br><span class="Latn" lang="pt">[[lindíssima#Portuguese|lindíssima]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[os#Portuguese|os]] [[mais#Portuguese|mais]] lindos</span><br><span class="Latn" lang="pt">[[lindíssimos#Portuguese|lindíssimos]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[as#Portuguese|as]] [[mais#Portuguese|mais]] lindas</span><br><span class="Latn" lang="pt">[[lindíssimas#Portuguese|lindíssimas]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | [[Appendix:Glossary#augmentative|augmentative]]


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindão#Portuguese|lindão]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindona#Portuguese|lindona]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindões#Portuguese|lindões]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindonas#Portuguese|lindonas]]</span>


|-

! style="border%3A+1px+solid+%23999999%3B+background%3A%23b0bfd4" | [[Appendix:Glossary#diminutive|diminutive]]


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindinho#Portuguese|lindinho]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindinha#Portuguese|lindinha]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindinhos#Portuguese|lindinhos]]</span>


| style="border%3A+1px+solid+%23999999%3B" valign="top" | <span class="Latn" lang="pt">[[lindinhas#Portuguese|lindinhas]]</span>


|}
</div></div>
""")
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
                "form": "lindo",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "linda",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "positive",
                  "singular"
                ]
              },
              {
                "form": "lindos",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "lindas",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "plural",
                  "positive"
                ]
              },
              {
                "form": "mais lindo",
                "source": "Conjugation",
                "tags": [
                  "comparative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "mais linda",
                "source": "Conjugation",
                "tags": [
                  "comparative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "mais lindos",
                "source": "Conjugation",
                "tags": [
                  "comparative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "mais lindas",
                "source": "Conjugation",
                "tags": [
                  "comparative",
                  "feminine",
                  "plural"
                ]
              },
              {
                "form": "o mais lindo",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "lindíssimo",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "a mais linda",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "lindíssima",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "singular",
                  "superlative"
                ]
              },
              {
                "form": "os mais lindos",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "lindíssimos",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "as mais lindas",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "lindíssimas",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "plural",
                  "superlative"
                ]
              },
              {
                "form": "lindão",
                "source": "Conjugation",
                "tags": [
                  "augmentative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "lindona",
                "source": "Conjugation",
                "tags": [
                  "augmentative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "lindões",
                "source": "Conjugation",
                "tags": [
                  "augmentative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "lindonas",
                "source": "Conjugation",
                "tags": [
                  "augmentative",
                  "feminine",
                  "plural"
                ]
              },
              {
                "form": "lindinho",
                "source": "Conjugation",
                "tags": [
                  "diminutive",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "lindinha",
                "source": "Conjugation",
                "tags": [
                  "diminutive",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "lindinhos",
                "source": "Conjugation",
                "tags": [
                  "diminutive",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "lindinhas",
                "source": "Conjugation",
                "tags": [
                  "diminutive",
                  "feminine",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

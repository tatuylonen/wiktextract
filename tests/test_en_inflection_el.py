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

    def test_Greek_verb1(self):
        ret = self.xinfl(
            "είμαι",
            "Greek",
            "verb",
            "Conjugation",
            """
<div class="NavFrame">
<div class="NavHead" style="background%3A%239FBFFF%3B+text-align%3Aleft">είμαι</div>
<div class="NavContent">

{| style="border%3A+1px+solid+%23A9A9A9%3B+background%3A%23FFFFFF%3B+border-collapse%3Acollapse%3B+margin%3A+0%3B" class="inflection-table" rules="cols" width="100%25"

|- style="background-color%3A%23b5d7fe%3B+text-align%3Acenter%3B"

|


| colspan="3" style="text-align%3Acenter%3B" |'''[[Appendix:Glossary#active|Active voice]]''' <span style="cursor%3Ahelp%3B" title="%CE%B5%CE%BD%CE%B5%CF%81%CE%B3%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%86%CF%89%CE%BD%CE%AE">&#10148;</span> &nbsp; — &nbsp; '''[[Appendix:Glossary#imperfective|Imperfective aspect]]''' <span style="cursor%3Ahelp%3B" title="%CE%B5%CE%BE%CE%B1%CE%BA%CE%BF%CE%BB%CE%BF%CF%85%CE%B8%CE%B7%CF%84%CE%B9%CE%BA%CE%BF%CE%AF+%CF%87%CF%81%CF%8C%CE%BD%CE%BF%CE%B9%2C+%CE%B1%CF%84%CE%B5%CE%BB%CE%AD%CF%82+%CF%80%CE%BF%CE%B9%CF%8C%CE%BD">&#10148;</span>



|- style="background-color%3A%23CCE4FC%3B"

| style="background-color%3A%239FBFFF%3B" |'''[[Appendix:Glossary#indicative|Indicative mood]]''' <span style="cursor%3Ahelp%3B" title="%CE%BF%CF%81%CE%B9%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CE%AD%CE%B3%CE%BA%CE%BB%CE%B9%CF%83%CE%B7">&#10148;</span>


|[[Appendix:Glossary#present|Present]] <span style="cursor%3Ahelp%3B" title="%CE%B5%CE%BD%CE%B5%CF%83%CF%84%CF%8E%CF%84%CE%B1%CF%82">&#10148;</span>


|[[Appendix:Glossary#imperfect|Imperfect]] <span style="cursor%3Ahelp%3B" title="imperfective+past%2C+preterimperfect+%28%CF%80%CE%B1%CF%81%CE%B1%CF%84%CE%B1%CF%84%CE%B9%CE%BA%CF%8C%CF%82%29">&#10148;</span>


|Future <span style="cursor%3Ahelp%3B" title="%28%CE%BC%CE%AD%CE%BB%CE%BB%CE%BF%CE%BD%CF%84%CE%B1%CF%82%29">&#10148;</span>



|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |1 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[είμαι]]


|[[ήμουν]]([[ήμουνα|α]])<sup>1</sup>


|θα είμαι


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |2 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[είσαι]]


|[[ήσουν]]([[ήσουνα|α]])<sup>1</sup>


|θα είσαι


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3Bvertical-align%3Atop%3B" |3 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[είναι]]


|[[ήταν]]([[ήτανε|ε]])<sup>1</sup>


|θα είναι


|-

| height="1" style="background-color%3A%23CFDFFF%3B" colspan="4" |


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |1 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[είμαστε]], &#0123;&#0091;[[είμεθα]]&#0093;&#0125;<sup>3</sup>


|[[ήμαστε]], [[ήμασταν]]<sup>2</sup>


|θα είμαστε


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |2 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[είστε]], [[είσαστε]]


|[[ήσαστε]], [[ήσασταν]]<sup>2</sup>


|θα είστε, θα είσαστε


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |3 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[είναι]]


|[[ήταν]]([[ήτανε|ε]])<sup>1</sup>, &#0123;[[ήσαν]]&#0125;<sup>3</sup>, &#0091;[[ήσανε]]&#0093;<sup>1</sup>


|θα είναι


|-

| height="1" style="background-color%3A%239FBFFF%3B" colspan="4" |


|-

| height="1" style="background-color%3A%239FBFFF%3B" colspan="4" |



|-

| style="background-color%3A%239FBFFF%3B" |'''[[Appendix:Glossary#subjunctive|Subjunctive mood]]'''&nbsp;<span style="cursor%3Ahelp%3B" title="%CF%85%CF%80%CE%BF%CF%84%CE%B1%CE%BA%CF%84%CE%B9%CE%BA%CE%AE+%CE%AD%CE%B3%CE%BA%CE%BB%CE%B9%CF%83%CE%B7">&#10148;</span>


| colspan="3" |Formed using ''present tense'' from above with a particle ([[να]], [[ας]]).


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="4" |



|- style="background-color%3A%23CCE4FC%3B"

| style="background-color%3A%239FBFFF%3B" |'''[[Appendix:Glossary#imperative|Imperative mood]]''' <span style="cursor%3Ahelp%3B" title="%CF%80%CF%81%CE%BF%CF%83%CF%84%CE%B1%CE%BA%CF%84%CE%B9%CE%BA%CE%AE+%CE%AD%CE%B3%CE%BA%CE%BB%CE%B9%CF%83%CE%B7">&#10148;</span>


|2 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|2 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" | Imperfective aspect


|να είσαι, &#0123;&#0091;[[έσο]]&#0093;&#0125;<sup>3</sup>


|να είστε, να είσαστε, &#0123;&#0091;[[έστε]]&#0093;&#0125;<sup>3</sup>


|


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="4" |



|- style="background-color%3A%23CCE4FC%3B"

| style="background-color%3A%239FBFFF%3B" | '''Other forms'''


|Present participle <span style="cursor%3Ahelp%3B" title="%CE%BC%CE%B5%CF%84%CE%BF%CF%87%CE%AE+%CE%B5%CE%BD%CE%B5%CF%83%CF%84%CF%8E%CF%84%CE%B1">&#10148;</span>


| colspan="2" |


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3Btext-align%3Aright%3B" |


|[[όντας]]<sup>4</sup>&nbsp;<span style="cursor%3Ahelp%3B" title="gerund%2C+indeclinable+%28%CE%BC%CE%B5%CF%84%CE%BF%CF%87%CE%AE+%CE%B5%CE%BD%CE%B5%CF%81%CE%B3%CE%B7%CF%84%CE%B9%CE%BA%CE%BF%CF%8D+%CE%B5%CE%BD%CE%B5%CF%83%CF%84%CF%8E%CF%84%CE%B1%2C+%CE%AC%CE%BA%CE%BB%CE%B9%CF%84%CE%B7%29">&#10148;</span>


| colspan="2" |


|-

| height="1" style="background-color%3A%239FBFFF%3B" colspan="4" |



|-

| height="1" style="background-color%3A%23FFDAEA%3B" colspan="4" |


|-

| style="background-color%3A%23FFDAEA%3Bvertical-align%3Atop%3B" |'''Notes''' &nbsp;<br>&nbsp;<br>'''[[Appendix:Greek verbs]]'''


| style="text-align%3Aleft%3B" colspan="4" |&nbsp;• <sup>1</sup> informal alternatives &nbsp; &nbsp; <sup>2</sup> orally differentiated alternatives &nbsp; &nbsp; <sup>3</sup> formal<br>&nbsp;&bull; <sup>4</sup> Also, archaic '''active present participle''': ο&nbsp;&#0123;[[ων]]&#0125;, η&nbsp;&#0123;[[ούσα]]&#0125;, το&nbsp;&#0123;[[ον]]&#0125;<br>&nbsp;• (…) optional or informal.  &nbsp;  […] rare.   &nbsp;  {…} learned, archaic.<br>&nbsp;• Multiple forms are shown in order of reducing frequency.<br>&nbsp;• Periphrastic imperative forms may be produced using the subjunctive.


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="4" |


|}
</div></div>[[Category:Greek irregular verbs]]
* <small><templatestyles src="audio%2Fstyles.css"></small><table class="audiotable" style="vertical-align%3A+bottom%3B+display%3Ainline-block%3B+list-style%3Anone%3Bline-height%3A+1em%3B+border-collapse%3Acollapse%3B"><tr><td class="unicode+audiolink" style="padding-right%3A5px%3B+padding-left%3A+0%3B">Audio: present indicative</td><td class="audiofile">[[File:El-είμαι conjugation-present indicative.ogg|noicon|175px]]</td><td class="audiometa" style="font-size%3A+80%25%3B">([[:File:El-είμαι conjugation-present indicative.ogg|file]])</td></tr></table>[[Category:Greek terms with audio links|ΕΙΜΑΙ]] <templatestyles src="audio%2Fstyles.css"><table class="audiotable" style="vertical-align%3A+bottom%3B+display%3Ainline-block%3B+list-style%3Anone%3Bline-height%3A+1em%3B+border-collapse%3Acollapse%3B"><tr><td class="unicode+audiolink" style="padding-right%3A5px%3B+padding-left%3A+0%3B">imperfect</td><td class="audiofile">[[File:El-είμαι-conjugation-imperfect-ήμουν.ogg|noicon|175px]]</td><td class="audiometa" style="font-size%3A+80%25%3B">([[:File:El-είμαι-conjugation-imperfect-ήμουν.ogg|file]])</td></tr></table>[[Category:Greek terms with audio links|ΕΙΜΑΙ]]</small>
""",
        )  # noqa: E501
        expected = {
            "forms": [
                {
                    "form": "no-table-tags",
                    "source": "Conjugation",
                    "tags": ["table-tags"],
                },
                {
                    "form": "είμαι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfective",
                        "indicative",
                        "present",
                        "singular",
                    ],
                },
                {
                    "form": "ήμουν",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "singular",
                    ],
                },
                {
                    "form": "ήμουνα",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "singular",
                    ],
                },
                {
                    "form": "θα είμαι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "imperfective",
                        "indicative",
                        "singular",
                    ],
                },
                {
                    "form": "είσαι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "present",
                        "second-person",
                        "singular",
                    ],
                },
                {
                    "form": "ήσουν",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "second-person",
                        "singular",
                    ],
                },
                {
                    "form": "ήσουνα",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "second-person",
                        "singular",
                    ],
                },
                {
                    "form": "θα είσαι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "future",
                        "imperfective",
                        "indicative",
                        "second-person",
                        "singular",
                    ],
                },
                {
                    "form": "είναι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "present",
                        "singular",
                        "third-person",
                    ],
                },
                {
                    "form": "ήταν",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "singular",
                        "third-person",
                    ],
                },
                {
                    "form": "ήτανε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "singular",
                        "third-person",
                    ],
                },
                {
                    "form": "θα είναι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "future",
                        "imperfective",
                        "indicative",
                        "singular",
                        "third-person",
                    ],
                },
                {
                    "form": "είμαστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                    ],
                },
                {
                    "form": "είμεθα",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "archaic",
                        "first-person",
                        "formal",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "rare",
                    ],
                },
                {
                    "form": "ήμαστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                    ],
                },
                {
                    "form": "ήμασταν",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                    ],
                },
                {
                    "form": "θα είμαστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "imperfective",
                        "indicative",
                        "plural",
                    ],
                },
                {
                    "form": "είστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "second-person",
                    ],
                },
                {
                    "form": "είσαστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "second-person",
                    ],
                },
                {
                    "form": "ήσαστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                },
                {
                    "form": "ήσασταν",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                },
                {
                    "form": "θα είστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "future",
                        "imperfective",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                },
                {
                    "form": "θα είσαστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "future",
                        "imperfective",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                },
                {
                    "form": "είναι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "third-person",
                    ],
                },
                {
                    "form": "ήταν",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "plural",
                        "third-person",
                    ],
                },
                {
                    "form": "ήτανε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "plural",
                        "third-person",
                    ],
                },
                {
                    "form": "ήσαν",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "archaic",
                        "formal",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "third-person",
                    ],
                },
                {
                    "form": "ήσανε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "plural",
                        "rare",
                        "third-person",
                    ],
                },
                {
                    "form": "θα είναι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "future",
                        "imperfective",
                        "indicative",
                        "plural",
                        "third-person",
                    ],
                },
                {
                    "form": "Formed using present tense from above "
                    "with a particle (να, ας).",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "future",
                        "imperfect",
                        "imperfective",
                        "present",
                        "subjunctive",
                    ],
                },
                {
                    "form": "να είσαι",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperative",
                        "imperfective",
                        "second-person",
                        "singular",
                    ],
                },
                {
                    "form": "έσο",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "archaic",
                        "formal",
                        "imperative",
                        "imperfective",
                        "rare",
                        "second-person",
                        "singular",
                    ],
                },
                {
                    "form": "να είστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperative",
                        "imperfective",
                        "plural",
                        "second-person",
                    ],
                },
                {
                    "form": "να είσαστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "imperative",
                        "imperfective",
                        "plural",
                        "second-person",
                    ],
                },
                {
                    "form": "έστε",
                    "source": "Conjugation",
                    "tags": [
                        "active",
                        "archaic",
                        "formal",
                        "imperative",
                        "imperfective",
                        "plural",
                        "rare",
                        "second-person",
                    ],
                },
                {
                    "form": "όντας",
                    "source": "Conjugation",
                    "tags": ["participle", "present"],
                },
            ],
        }
        self.assertEqual(expected, ret)

    def test_Greek_verb2(self):
        ret = self.xinfl(
            "περπατάω",
            "Greek",
            "verb",
            "Conjugation",
            """
<div class="NavFrame">
<div class="NavHead" style="background%3A%239FBFFF%3B+text-align%3Aleft">'''περπατάω / περπατώ, περπατιέμαι''' </div>
<div class="NavContent">

{| style="border%3A+1px+solid+%23A9A9A9%3B+background%3A%23FFFFFF%3B+border-collapse%3Acollapse%3B+margin%3A+0%3B" class="inflection-table" rules="cols" width="100%25"

|- style="background-color%3A%239FBFFF%3B"

|


| colspan="2" style="text-align%3Acenter%3B" |'''[[Appendix:Glossary#active|Active voice]]''' <span style="cursor%3Ahelp%3B" title="%CE%B5%CE%BD%CE%B5%CF%81%CE%B3%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%86%CF%89%CE%BD%CE%AE">&#10148;</span>


| colspan="2" style="text-align%3Acenter%3B" |'''[[Appendix:Glossary#passive|Passive voice]]''' <span style="cursor%3Ahelp%3B" title="%CF%80%CE%B1%CE%B8%CE%B7%CF%84%CE%B9%CE%BA%CE%AE+%CF%86%CF%89%CE%BD%CE%AE">&#10148;</span>


|- style="background-color%3A%23b5d7fe%3B+text-align%3Acenter%3B"

| style="background-color%3A%239FBFFF%3B" |<b>[[Appendix:Glossary#indicative|Indicative mood]]</b> <span style="cursor%3Ahelp%3B" title="%CE%BF%CF%81%CE%B9%CF%83%CF%84%CE%B9%CE%BA%CE%AE+%CE%AD%CE%B3%CE%BA%CE%BB%CE%B9%CF%83%CE%B7">&#10148;</span>


|[[Appendix:Glossary#imperfective|Imperfective aspect]] <span style="cursor%3Ahelp%3B" title="%CE%B5%CE%BE%CE%B1%CE%BA%CE%BF%CE%BB%CE%BF%CF%85%CE%B8%CE%B7%CF%84%CE%B9%CE%BA%CE%BF%CE%AF+%CF%87%CF%81%CF%8C%CE%BD%CE%BF%CE%B9%2C+%CE%B1%CF%84%CE%B5%CE%BB%CE%AD%CF%82+%CF%80%CE%BF%CE%B9%CF%8C%CE%BD">&#10148;</span>


|[[Appendix:Glossary#perfective|Perfective aspect]] <span style="cursor%3Ahelp%3B" title="%CF%83%CF%85%CE%BD%CE%BF%CF%80%CF%84%CE%B9%CE%BA%CE%BF%CE%AF%2F%CF%83%CF%84%CE%B9%CE%B3%CE%BC%CE%B9%CE%B1%CE%AF%CE%BF%CE%B9+%CF%87%CF%81%CF%8C%CE%BD%CE%BF%CE%B9%2C+%CF%84%CE%AD%CE%BB%CE%B5%CE%B9%CE%BF+%CF%80%CE%BF%CE%B9%CF%8C%CE%BD">&#10148;</span>


|Imperfective aspect


|Perfective aspect



|- style="background-color%3A%23CCE4FC%3B"

|Non-past tenses <span style="cursor%3Ahelp%3B" title="%CF%80%CE%B1%CF%81%CE%BF%CE%BD%CF%84%CE%B9%CE%BA%CE%BF%CE%AF+%CF%87%CF%81%CF%8C%CE%BD%CE%BF%CE%B9">&#10148;</span>


|[[Appendix:Glossary#present|Present]] <span style="cursor%3Ahelp%3B" title="%CE%B5%CE%BD%CE%B5%CF%83%CF%84%CF%8E%CF%84%CE%B1%CF%82">&#10148;</span>


|[[Appendix:Glossary#dependent|''Dependent'']] <span style="cursor%3Ahelp%3B" title="dependent+%28%CE%B5%CE%BE%CE%B1%CF%81%CF%84%CE%B7%CE%BC%CE%B5%CE%BD%CE%BF%CF%82+%CF%84%CF%8D%CF%80%CE%BF%CF%82%29+is+only+used+with+other+forms+or+particles.">&#10148;</span>


|Present


|''Dependent''



|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |1 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[περπατάω]], [[περπατώ]]


|[[περπατήσω]]


|[[περπατιέμαι]]


|[[περπατηθώ]]


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |2 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[περπατάς]]


|[[περπατήσεις]]


|[[περπατιέσαι]]


|[[περπατηθείς]]


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3Bvertical-align%3Atop%3B" |3 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[περπατάει]], [[περπατά]]


|[[περπατήσει]]


|[[περπατιέται]]


|[[περπατηθεί]]


|-

| height="1" style="background-color%3A%23CFDFFF%3B" colspan="5" |



|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |1 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[περπατάμε]], [[περπατούμε]]


|[[περπατήσουμε]], &#0091;[[περπατήσομε|&#8209;ομε]]&#0093;


|[[περπατιόμαστε]]


|[[περπατηθούμε]]


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |2 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[περπατάτε]]


|[[περπατήσετε]]


|[[περπατιέστε]], ([[περπατιόσαστε|&#8209;ιόσαστε]])


|[[περπατηθείτε]]


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |3 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[περπατάνε]], [[περπατάν]], [[περπατούν]]([[περπατούνε|ε]])


|[[περπατήσουν]]([[περπατήσουνε|ε]])


|[[περπατιούνται]], ([[περπατιόνται|&#8209;ιόνται]])


|[[περπατηθούν]]([[περπατηθούνε|ε]])


|-

| height="1" style="background-color%3A%239FBFFF%3B" colspan="5" |



|- style="background-color%3A%23CCE4FC%3B"

|Past tenses <span style="cursor%3Ahelp%3B" title="%CF%80%CE%B1%CF%81%CE%B5%CE%BB%CE%B8%CE%BF%CE%BD%CF%84%CE%B9%CE%BA%CE%BF%CE%AF+%CF%87%CF%81%CF%8C%CE%BD%CE%BF%CE%B9">&#10148;</span>


|[[Appendix:Glossary#imperfect|Imperfect]] <span style="cursor%3Ahelp%3B" title="imperfective+past%2C+preterimperfect+%28%CF%80%CE%B1%CF%81%CE%B1%CF%84%CE%B1%CF%84%CE%B9%CE%BA%CF%8C%CF%82%29">&#10148;</span>


|[[simple past|Simple past]] <span style="cursor%3Ahelp%3B" title="aorist%2C+perfective+past%2C+preterite+%28%CE%B1%CF%8C%CF%81%CE%B9%CF%83%CF%84%CE%BF%CF%82%29">&#10148;</span>


|Imperfect


|Simple past



|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |1 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[περπατούσα]], [[περπάταγα]]


|[[περπάτησα]]


|[[περπατιόμουν]]([[περπατιόμουνα|α]])


|[[περπατήθηκα]]


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |2 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[περπατούσες]], [[περπάταγες]]


|[[περπάτησες]]


|[[περπατιόσουν]]([[περπατιόσουνα|α]])


|[[περπατήθηκες]]


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |3 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[περπατούσε]], [[περπάταγε]]


|[[περπάτησε]]


|[[περπατιόταν]]([[περπατιότανε|ε]])


|[[περπατήθηκε]]


|-

| height="1" style="background-color%3A%23CFDFFF%3B" colspan="5" |



|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |1 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[περπατούσαμε]], [[περπατάγαμε]]


|[[περπατήσαμε]]


|[[περπατιόμασταν]], ([[περπατιόμαστε|&#8209;ιόμαστε]])


|[[περπατηθήκαμε]]


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |2 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[περπατούσατε]], [[περπατάγατε]]


|[[περπατήσατε]]


|[[περπατιόσασταν]], ([[περπατιόσαστε|&#8209;ιόσαστε]])


|[[περπατηθήκατε]]


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |3 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[περπατούσαν]]([[περπατούσανε|ε]]), [[περπάταγαν]], ([[περπατάγανε]])


|[[περπάτησαν]], [[περπατήσαν]]([[περπατήσανε|ε]])


|[[περπατιόνταν]]([[περπατιόντανε|ε]]), [[περπατιόντουσαν]], [[περπατιούνταν]]


|[[περπατήθηκαν]], [[περπατηθήκαν]]([[περπατηθήκανε|ε]])


|-

| height="1" style="background-color%3A%239FBFFF%3B" colspan="5" |



|- style="background-color%3A%23CCE4FC%3B"

|Future tenses <span style="cursor%3Ahelp%3B" title="%CE%BC%CE%B5%CE%BB%CE%BB%CE%BF%CE%BD%CF%84%CE%B9%CE%BA%CE%BF%CE%AF+%CF%87%CF%81%CF%8C%CE%BD%CE%BF%CE%B9">&#10148;</span>


|Continuous <span style="cursor%3Ahelp%3B" title="imperfective%2C+progressive+%28%CE%B5%CE%BE%CE%B1%CE%BA%CE%BF%CE%BB%CE%BF%CF%85%CE%B8%CE%B7%CF%84%CE%B9%CE%BA%CF%8C%CF%82+%CE%BC%CE%AD%CE%BB%CE%BB%CE%BF%CE%BD%CF%84%CE%B1%CF%82%29">&#10148;</span>


|Simple <span style="cursor%3Ahelp%3B" title="perfective+%28%CF%83%CF%85%CE%BD%CE%BF%CF%80%CF%84%CE%B9%CE%BA%CF%8C%CF%82%2F%CF%83%CF%84%CE%B9%CE%B3%CE%BC%CE%B9%CE%B1%CE%AF%CE%BF%CF%82+%CE%BC%CE%AD%CE%BB%CE%BB%CE%BF%CE%BD%CF%84%CE%B1%CF%82%29">&#10148;</span>


|Continuous


|Simple


|-

| style="background-color%3A%23EFF7FF%3B" |1 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[θα]] [[περπατάω]], θα&nbsp;[[περπατώ]] <span style="cursor%3Ahelp%3B" title="%CE%B8%CE%B1+%2B+present+forms+above">&#10148;</span>


|θα [[περπατήσω]] <span style="cursor%3Ahelp%3B" title="%CE%B8%CE%B1+%2B+dependent+forms+above">&#10148;</span>


|θα [[περπατιέμαι]] <span style="cursor%3Ahelp%3B" title="%CE%B8%CE%B1+%2B+present+forms+above">&#10148;</span>


|θα [[περπατηθώ]] <span style="cursor%3Ahelp%3B" title="%CE%B8%CE%B1+%2B+dependent+forms+above">&#10148;</span>


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |2,3 <span class="gender"><abbr title="singular+number">sg</abbr></span>, 1,2,3 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|θα [[περπατάς]], …


|θα [[περπατήσεις]], …


|θα [[περπατιέσαι]], …


|θα [[περπατηθείς]], …



|-

| height="1" style="background-color%3A%239FBFFF%3B" colspan="5" |


|- style="background-color%3A%23b5d7fe%3B+text-align%3Acenter%3B"

|


| colspan="2" |Perfect aspect <span style="cursor%3Ahelp%3B" title="%CF%83%CF%85%CE%BD%CF%84%CE%B5%CE%BB%CE%B5%CF%83%CE%BC%CE%AD%CE%BD%CE%BF+%CF%80%CE%BF%CE%B9%CF%8C%CE%BD">&#10148;</span>


| colspan="2" |Perfect aspect


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |Present&nbsp;perfect&nbsp;<span style="cursor%3Ahelp%3B" title="perfect+%28%CF%80%CE%B1%CF%81%CE%B1%CE%BA%CE%B5%CE%AF%CE%BC%CE%B5%CE%BD%CE%BF%CF%82%29">&#10148;</span>


| colspan="2" style="text-align%3Aleft%3B" |&nbsp; [[έχω]], [[έχεις]], … [[περπατήσει]]<br>&nbsp; έχω, έχεις, … [[περπατημένο]], &#8209;η, &#8209;ο&ensp;<span style="cursor%3Ahelp%3B" title="accusative+%28%CE%B1%CE%B9%CF%84%CE%B9%CE%B1%CF%84%CE%B9%CE%BA%CE%AE%29">&#10148;</span>


| colspan="2" style="text-align%3Aleft%3B" |&nbsp; έχω, έχεις, … [[περπατηθεί]]<br>&nbsp; [[είμαι]], [[είσαι]], … [[περπατημένος]], &#8209;η, &#8209;ο&ensp;<span style="cursor%3Ahelp%3B" title="nominative+%28%CE%BF%CE%BD%CE%BF%CE%BC%CE%B1%CF%83%CF%84%CE%B9%CE%BA%CE%AE%29">&#10148;</span>


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |Past perfect <span style="cursor%3Ahelp%3B" title="pluperfect+%28%CF%85%CF%80%CE%B5%CF%81%CF%83%CF%85%CE%BD%CF%84%CE%AD%CE%BB%CE%B9%CE%BA%CE%BF%CF%82%29">&#10148;</span>


| colspan="2" style="text-align%3Aleft%3B" |&nbsp; [[είχα]], [[είχες]], … [[περπατήσει]]<br>&nbsp; είχα, είχες, … [[περπατημένο]], &#8209;η, &#8209;ο


| colspan="2" style="text-align%3Aleft%3B" |&nbsp; είχα, είχες, … [[περπατηθεί]]<br>&nbsp; [[ήμουν]], [[ήσουν]], … [[περπατημένος]], &#8209;η, &#8209;ο


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |Future perfect <span style="cursor%3Ahelp%3B" title="%CF%83%CF%85%CE%BD%CF%84%CE%B5%CE%BB%CE%B5%CF%83%CE%BC%CE%AD%CE%BD%CE%BF%CF%82+%CE%BC%CE%AD%CE%BB%CE%BB%CE%BF%CE%BD%CF%84%CE%B1%CF%82">&#10148;</span>


| colspan="2" style="text-align%3Aleft%3B" |&nbsp; [[θα]] έχω, θα έχεις, … [[περπατήσει]]<br>&nbsp; θα έχω, θα έχεις, … [[περπατημένο]], &#8209;η, &#8209;ο


| colspan="2" style="text-align%3Aleft%3B" |&nbsp; θα έχω, θα έχεις, … [[περπατηθεί]]<br>&nbsp; θα είμαι, θα είσαι, … [[περπατημένος]], &#8209;η, &#8209;ο


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="5" |



|-

| style="background-color%3A%239FBFFF%3B" |<span style="white-space%3Anowrap"><b>[[Appendix:Glossary#subjunctive|Subjunctive mood]]</b> <span style="cursor%3Ahelp%3B" title="%CF%85%CF%80%CE%BF%CF%84%CE%B1%CE%BA%CF%84%CE%B9%CE%BA%CE%AE+%CE%AD%CE%B3%CE%BA%CE%BB%CE%B9%CF%83%CE%B7">&#10148;</span> </span>


| colspan="4" |Formed using ''present'', ''dependent'' (for ''simple past'') or ''present perfect'' from above with a particle ([[να]], [[ας]]).


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="5" |



|- style="background-color%3A%23CCE4FC%3B"

| style="background-color%3A%239FBFFF%3B" |<b>[[Appendix:Glossary#imperative|Imperative mood]]</b> <span style="cursor%3Ahelp%3B" title="%CF%80%CF%81%CE%BF%CF%83%CF%84%CE%B1%CE%BA%CF%84%CE%B9%CE%BA%CE%AE+%CE%AD%CE%B3%CE%BA%CE%BB%CE%B9%CF%83%CE%B7">&#10148;</span>


|Imperfective aspect


|Perfective aspect


|Imperfective aspect


|Perfective aspect


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3B" |2 <span class="gender"><abbr title="singular+number">sg</abbr></span>


|[[περπάτα]], [[περπάταγε]]


|[[περπάτησε]], [[περπάτα]]


|—


|[[περπατήσου]]


|- style="background-color%3A%23eeeeee%3Bvertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3B" |2 <span class="gender"><abbr title="plural+number">pl</abbr></span>


|[[περπατάτε]]


|[[περπατήστε]]


|[[περπατιέστε]]


|[[περπατηθείτε]]


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="5" |



|- style="background-color%3A%239FBFFF%3B"

|<b>Other forms</b>


| colspan="2" style="text-align%3Acenter%3B" |'''Active voice'''


| colspan="2" style="text-align%3Acenter%3B" |'''Passive voice'''


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23EFF7FF%3Btext-align%3Aright%3B" |Present participle<span style="cursor%3Ahelp%3B" title="%CE%BC%CE%B5%CF%84%CE%BF%CF%87%CE%AE+%CE%B5%CE%BD%CE%B5%CF%83%CF%84%CF%8E%CF%84%CE%B1">&#10148;</span>


| colspan="2" |[[περπατώντας]]&nbsp;<span style="cursor%3Ahelp%3B" title="gerund%2C+indeclinable+%28%CE%BC%CE%B5%CF%84%CE%BF%CF%87%CE%AE+%CE%B5%CE%BD%CE%B5%CF%81%CE%B3%CE%B7%CF%84%CE%B9%CE%BA%CE%BF%CF%8D+%CE%B5%CE%BD%CE%B5%CF%83%CF%84%CF%8E%CF%84%CE%B1%2C+%CE%AC%CE%BA%CE%BB%CE%B9%CF%84%CE%B7%29">&#10148;</span>


| colspan="2" |—


|- style="vertical-align%3Atop%3B"

| style="background-color%3A%23CCE4FC%3Btext-align%3Aright%3B" |Perfect participle<span style="cursor%3Ahelp%3B" title="%CE%BC%CE%B5%CF%84%CE%BF%CF%87%CE%AE+%CF%80%CE%B1%CF%81%CE%B1%CE%BA%CE%B5%CE%B9%CE%BC%CE%AD%CE%BD%CE%BF%CF%85">&#10148;</span>


| colspan="2" style="background-color%3A%23eeeeee%3B" |[[έχοντας]] [[περπατήσει]]&nbsp;<span style="cursor%3Ahelp%3B" title="indeclinable+%28%CE%BC%CE%B5%CF%84%CE%BF%CF%87%CE%AE+%CE%B5%CE%BD%CE%B5%CF%81%CE%B3%CE%B7%CF%84%CE%B9%CE%BA%CE%BF%CF%8D+%CF%80%CE%B1%CF%81%CE%B1%CE%BA%CE%B5%CE%B9%CE%BC%CE%AD%CE%BD%CE%BF%CF%85%2C+%CE%AC%CE%BA%CE%BB%CE%B9%CF%84%CE%B7%29">&#10148;</span>


| colspan="2" style="background-color%3A%23eeeeee%3B" |[[περπατημένος]],&nbsp;&#8209;η,&nbsp;&#8209;ο&nbsp;<span style="cursor%3Ahelp%3B" title="declinable+%28%CE%BC%CE%B5%CF%84%CE%BF%CF%87%CE%AE+%CF%80%CE%B1%CE%B8%CE%B7%CF%84%CE%B9%CE%BA%CE%BF%CF%8D+%CF%80%CE%B1%CF%81%CE%B1%CE%BA%CE%B5%CE%B9%CE%BC%CE%AD%CE%BD%CE%BF%CF%85%2C+%CE%BA%CE%BB%CE%B9%CF%84%CE%AE%29">&#10148;</span>


|-

| height="1" style="background-color%3A%239FBFFF%3B" colspan="5" |


|-

| style="background-color%3A%23EFF7FF%3Btext-align%3Aright%3B" |Nonfinite form<span style="cursor%3Ahelp%3B" title="indeclinable+%28%CE%AC%CE%BA%CE%BB%CE%B9%CF%84%CE%BF%CF%82+%CF%84%CF%8D%CF%80%CE%BF%CF%82%2C+%CE%B1%CF%80%CE%B1%CF%81%CE%AD%CE%BC%CF%86%CE%B1%CF%84%CE%BF%29">&#10148;</span>


| colspan="2" |[[περπατήσει]]


| colspan="2" |[[περπατηθεί]]


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="5" |



|-

| height="1" style="background-color%3A%23FFDAEA%3B" colspan="5" |


|-

| style="background-color%3A%23FFDAEA%3Bvertical-align%3Atop%3B" |<b>Notes</b> &nbsp;<br>&nbsp;<br>'''[[Appendix:Greek verbs]]'''


| style="text-align%3Aleft%3B" colspan="4" |&nbsp;• (…) optional or informal.  &nbsp;  […] rare.   &nbsp;  {…} learned, archaic.<br>&nbsp;• Multiple forms are shown in order of reducing frequency.<br>&nbsp;• Periphrastic imperative forms may be produced using the subjunctive.


|-

| height="2" style="background-color%3A%23A9A9A9%3B" colspan="5" |


|}
</div></div>[[Category:Greek verbs conjugating like 'αγαπάω-αγαπώ']]
""",
        )  # noqa: E501
        expected = {
            "forms": [
                {
                    "form": "no-table-tags",
                    "source": "Conjugation",
                    "tags": ["table-tags"],
                },
                {
                    "form": "περπατάω",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfective",
                        "indicative",
                        "present",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατώ",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfective",
                        "indicative",
                        "present",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσω",
                    "tags": [
                        "active",
                        "dependent",
                        "first-person",
                        "indicative",
                        "perfective",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιέμαι",
                    "tags": [
                        "first-person",
                        "imperfective",
                        "indicative",
                        "passive",
                        "present",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθώ",
                    "tags": [
                        "dependent",
                        "first-person",
                        "indicative",
                        "passive",
                        "perfective",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάς",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "present",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσεις",
                    "tags": [
                        "active",
                        "dependent",
                        "indicative",
                        "perfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιέσαι",
                    "tags": [
                        "imperfective",
                        "indicative",
                        "passive",
                        "present",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθείς",
                    "tags": [
                        "dependent",
                        "indicative",
                        "passive",
                        "perfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάει",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "present",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατά",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "present",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσει",
                    "tags": [
                        "active",
                        "dependent",
                        "indicative",
                        "perfective",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιέται",
                    "tags": [
                        "imperfective",
                        "indicative",
                        "passive",
                        "present",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθεί",
                    "tags": [
                        "dependent",
                        "indicative",
                        "passive",
                        "perfective",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάμε",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούμε",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσουμε",
                    "tags": [
                        "active",
                        "dependent",
                        "first-person",
                        "indicative",
                        "perfective",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "‑ομε",
                    "tags": [
                        "active",
                        "dependent",
                        "first-person",
                        "indicative",
                        "perfective",
                        "plural",
                        "rare",
                    ],
                    "source": "Conjugation",
                    "links": [("‑ομε", "περπατήσομε")],
                },
                {
                    "form": "περπατιόμαστε",
                    "tags": [
                        "first-person",
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "present",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθούμε",
                    "tags": [
                        "dependent",
                        "first-person",
                        "indicative",
                        "passive",
                        "perfective",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάτε",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσετε",
                    "tags": [
                        "active",
                        "dependent",
                        "indicative",
                        "perfective",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιέστε",
                    "tags": [
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "present",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "‑ιόσαστε",
                    "tags": [
                        "imperfective",
                        "indicative",
                        "informal",
                        "passive",
                        "plural",
                        "present",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("‑ιόσαστε", "περπατιόσαστε")],
                },
                {
                    "form": "περπατηθείτε",
                    "tags": [
                        "dependent",
                        "indicative",
                        "passive",
                        "perfective",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάνε",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάν",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούν",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούνε",
                    "tags": [
                        "active",
                        "imperfective",
                        "indicative",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσουν",
                    "tags": [
                        "active",
                        "dependent",
                        "indicative",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσουνε",
                    "tags": [
                        "active",
                        "dependent",
                        "indicative",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιούνται",
                    "tags": [
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "‑ιόνται",
                    "tags": [
                        "imperfective",
                        "indicative",
                        "informal",
                        "passive",
                        "plural",
                        "present",
                        "third-person",
                    ],
                    "source": "Conjugation",
                    "links": [("‑ιόνται", "περπατιόνται")],
                },
                {
                    "form": "περπατηθούν",
                    "tags": [
                        "dependent",
                        "indicative",
                        "passive",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθούνε",
                    "tags": [
                        "dependent",
                        "indicative",
                        "passive",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούσα",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάταγα",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάτησα",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "past",
                        "perfective",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόμουν",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόμουνα",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήθηκα",
                    "tags": [
                        "first-person",
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούσες",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάταγες",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάτησες",
                    "tags": [
                        "active",
                        "indicative",
                        "past",
                        "perfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόσουν",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόσουνα",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήθηκες",
                    "tags": [
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούσε",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάταγε",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάτησε",
                    "tags": [
                        "active",
                        "indicative",
                        "past",
                        "perfective",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόταν",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιότανε",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήθηκε",
                    "tags": [
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "singular",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούσαμε",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάγαμε",
                    "tags": [
                        "active",
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσαμε",
                    "tags": [
                        "active",
                        "first-person",
                        "indicative",
                        "past",
                        "perfective",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόμασταν",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "‑ιόμαστε",
                    "tags": [
                        "first-person",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "passive",
                        "plural",
                    ],
                    "source": "Conjugation",
                    "links": [("‑ιόμαστε", "περπατιόμαστε")],
                },
                {
                    "form": "περπατηθήκαμε",
                    "tags": [
                        "first-person",
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "plural",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούσατε",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάγατε",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσατε",
                    "tags": [
                        "active",
                        "indicative",
                        "past",
                        "perfective",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόσασταν",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "‑ιόσαστε",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "passive",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                    "links": [("‑ιόσαστε", "περπατιόσαστε")],
                },
                {
                    "form": "περπατηθήκατε",
                    "tags": [
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούσαν",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατούσανε",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάταγαν",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάγανε",
                    "tags": [
                        "active",
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "informal",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάτησαν",
                    "tags": [
                        "active",
                        "indicative",
                        "past",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσαν",
                    "tags": [
                        "active",
                        "indicative",
                        "past",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσανε",
                    "tags": [
                        "active",
                        "indicative",
                        "past",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόνταν",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόντανε",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιόντουσαν",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιούνταν",
                    "tags": [
                        "imperfect",
                        "imperfective",
                        "indicative",
                        "passive",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήθηκαν",
                    "tags": [
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθήκαν",
                    "tags": [
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθήκανε",
                    "tags": [
                        "indicative",
                        "passive",
                        "past",
                        "perfective",
                        "plural",
                        "third-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "θα περπατάω",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "imperfective",
                        "indicative",
                        "progressive",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "θα περπατώ",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "imperfective",
                        "indicative",
                        "progressive",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "θα περπατήσω",
                    "tags": [
                        "active",
                        "first-person",
                        "future",
                        "indicative",
                        "perfective",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "θα περπατιέμαι",
                    "tags": [
                        "continuative",
                        "first-person",
                        "future",
                        "imperfective",
                        "indicative",
                        "passive",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "θα περπατηθώ",
                    "tags": [
                        "first-person",
                        "future",
                        "indicative",
                        "passive",
                        "perfective",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "Formed using present",
                    "tags": [
                        "continuative",
                        "future",
                        "imperfective",
                        "perfective",
                        "progressive",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "dependent (for simple past)",
                    "tags": [
                        "continuative",
                        "future",
                        "imperfective",
                        "perfective",
                        "progressive",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "present perfect from above with a particle (να, ας).",
                    "tags": [
                        "continuative",
                        "future",
                        "imperfective",
                        "perfective",
                        "progressive",
                        "subjunctive",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάτα",
                    "tags": [
                        "active",
                        "imperative",
                        "imperfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάταγε",
                    "tags": [
                        "active",
                        "imperative",
                        "imperfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάτησε",
                    "tags": [
                        "active",
                        "imperative",
                        "perfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπάτα",
                    "tags": [
                        "active",
                        "imperative",
                        "perfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": [
                        "imperative",
                        "imperfective",
                        "passive",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσου",
                    "tags": [
                        "imperative",
                        "passive",
                        "perfective",
                        "second-person",
                        "singular",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατάτε",
                    "tags": [
                        "active",
                        "imperative",
                        "imperfective",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήστε",
                    "tags": [
                        "active",
                        "imperative",
                        "perfective",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατιέστε",
                    "tags": [
                        "imperative",
                        "imperfective",
                        "passive",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθείτε",
                    "tags": [
                        "imperative",
                        "passive",
                        "perfective",
                        "plural",
                        "second-person",
                    ],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατώντας",
                    "tags": ["active", "participle", "present"],
                    "source": "Conjugation",
                },
                {
                    "form": "-",
                    "tags": ["participle", "passive", "present"],
                    "source": "Conjugation",
                },
                {
                    "form": "έχοντας περπατήσει",
                    "tags": ["active", "participle", "past"],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατημένος",
                    "tags": ["participle", "passive", "past"],
                    "source": "Conjugation",
                },
                {
                    "form": "‑η",
                    "tags": ["participle", "passive", "past"],
                    "source": "Conjugation",
                },
                {
                    "form": "‑ο",
                    "tags": ["participle", "passive", "past"],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατήσει",
                    "tags": ["active", "infinitive-aorist"],
                    "source": "Conjugation",
                },
                {
                    "form": "περπατηθεί",
                    "tags": ["infinitive-aorist", "passive"],
                    "source": "Conjugation",
                },
            ]
        }

        self.assertEqual(expected, ret)

    def test_Greek_noun1(self):
        ret = self.xinfl(
            "νοσοκόμος",
            "Greek",
            "noun",
            "Declension",
            """
<div class="NavFrame" style="max-width%3A50em">
<div class="NavHead" style="background%3A%23cce4fc%3B+text-align%3Aleft">declension of νοσοκόμος</div>
<div class="NavContent">

{| style="background%3A%23fdfdfd%3B+text-align%3Acenter%3B+width%3A100%25%3B+border-collapse%3Aseparate%3B+border-spacing%3A1px"

|-

! style="width%3A33%25%3Bbackground%3A%23cce4fc" |


! style="background%3A%23cce4fc" | singular


! style="background%3A%23cce4fc" | plural


|-

! style="background%3A%23e0f0ff" |nominative


|<span class="Grek" lang="el">[[νοσοκόμος#Greek|νοσοκόμος]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3mos">•</span>


|<span class="Grek" lang="el">[[νοσοκόμοι#Greek|νοσοκόμοι]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3moi">•</span>


|-

! style="background%3A%23e0f0ff" |genitive


|<span class="Grek" lang="el">[[νοσοκόμου#Greek|νοσοκόμου]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3mou">•</span>


|<span class="Grek" lang="el">[[νοσοκόμων#Greek|νοσοκόμων]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3mon">•</span>


|-

! style="background%3A%23e0f0ff" |accusative


|<span class="Grek" lang="el">[[νοσοκόμο#Greek|νοσοκόμο]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3mo">•</span>


|<span class="Grek" lang="el">[[νοσοκόμους#Greek|νοσοκόμους]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3mous">•</span>


|-

! style="background%3A%23e0f0ff" |vocative


|<span class="Grek" lang="el">[[νοσοκόμε#Greek|νοσοκόμε]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3me">•</span>


|<span class="Grek" lang="el">[[νοσοκόμοι#Greek|νοσοκόμοι]]</span>&nbsp;<span style="cursor%3Ahelp%3B" title="nosok%C3%B3moi">•</span>


|-

|}
</div></div>[[Category:Greek nouns declining like 'δρόμος']]
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
                    "form": "νοσοκόμος",
                    "source": "Declension",
                    "tags": ["nominative", "singular"],
                },
                {
                    "form": "νοσοκόμοι",
                    "source": "Declension",
                    "tags": ["nominative", "plural"],
                },
                {
                    "form": "νοσοκόμου",
                    "source": "Declension",
                    "tags": ["genitive", "singular"],
                },
                {
                    "form": "νοσοκόμων",
                    "source": "Declension",
                    "tags": ["genitive", "plural"],
                },
                {
                    "form": "νοσοκόμο",
                    "source": "Declension",
                    "tags": ["accusative", "singular"],
                },
                {
                    "form": "νοσοκόμους",
                    "source": "Declension",
                    "tags": ["accusative", "plural"],
                },
                {
                    "form": "νοσοκόμε",
                    "source": "Declension",
                    "tags": ["singular", "vocative"],
                },
                {
                    "form": "νοσοκόμοι",
                    "source": "Declension",
                    "tags": ["plural", "vocative"],
                },
            ],
        }
        self.assertEqual(expected, ret)

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

    def test_Azerbaijani_noun1(self):
        ret = self.xinfl("yardım", "Azerbaijani", "verb", "Declension", """
<div class="NavFrame" style>
<div class="NavHead" style>Declension of ''yardım''</div>
<div class="NavContent">

{| style="background%3A%23F9F9F9%3Bwidth%3A100%25%3Btext-align%3Acenter" class="inflection-table"

|-

! colspan="1" rowspan="1" style |


! colspan="1" rowspan="1" style="background%3A%23DEDEDE" |singular


| colspan="1" style="background%3A%23DEDEDE" |'''plural'''



|-

! style="background%3A%23EFEFEF" | nominative


| yardım


|[[yardımlar]]



|-

! style="background%3A%23EFEFEF" | definite accusative


|[[yardımı]]


|[[yardımları]]



|-

! style="background%3A%23EFEFEF" | dative


|[[yardıma]]


|[[yardımlara]]



|-

! style="background%3A%23EFEFEF" | locative


|[[yardımda]]


|[[yardımlarda]]



|-

! style="background%3A%23EFEFEF" | ablative


|[[yardımdan]]


|[[yardımlardan]]



|-

! style="background%3A%23EFEFEF" | definite genitive


|[[yardımın]]


|[[yardımların]]



|}
</div></div>
<div class="NavFrame" style>
<div class="NavHead" style>Possessive forms of ''yardım''</div>
<div class="NavContent">

{| style="background%3A%23F9F9F9%3Bwidth%3A100%25%3Btext-align%3Acenter" class="inflection-table"

|-

! colspan="1" style |


! colspan="2" style="background%3A%23DEDEDE" |nominative


|-

! colspan="1" rowspan="1" style |


! colspan="1" rowspan="1" style="background%3A%23DEDEDE" |singular


| colspan="1" style="background%3A%23DEDEDE" |'''plural'''



|-

! style="background%3A%23EFEFEF" | [[mənim]] (“my”)


|[[yardımım]]


|[[yardımlarım]]



|-

! style="background%3A%23EFEFEF" | [[sənin]] (“your”)


|[[yardımın]]


|[[yardımların]]



|-

! style="background%3A%23EFEFEF" | [[onun]] (“his/her/its”)


|[[yardımı]]


|[[yardımları]]



|-

! style="background%3A%23EFEFEF" | [[bizim]] (“our”)


|[[yardımımız]]


|[[yardımlarımız]]



|-

! style="background%3A%23EFEFEF" | [[sizin]] (“your”)


|[[yardımınız]]


|[[yardımlarınız]]



|-

! style="background%3A%23EFEFEF" | [[onların]] (“their”)


|[[yardımı]]&nbsp;''or'' [[yardımları]]


|[[yardımları]]



|-

! colspan="1" style |


! colspan="2" style="background%3A%23DEDEDE" |accusative


|-

! colspan="1" rowspan="1" style |


! colspan="1" rowspan="1" style="background%3A%23DEDEDE" |singular


| colspan="1" style="background%3A%23DEDEDE" |'''plural'''



|-

! style="background%3A%23EFEFEF" | [[mənim]] (“my”)


|[[yardımımı]]


|[[yardımlarımı]]



|-

! style="background%3A%23EFEFEF" | [[sənin]] (“your”)


|[[yardımını]]


|[[yardımlarını]]



|-

! style="background%3A%23EFEFEF" | [[onun]] (“his/her/its”)


|[[yardımını]]


|[[yardımlarını]]



|-

! style="background%3A%23EFEFEF" | [[bizim]] (“our”)


|[[yardımımızı]]


|[[yardımlarımızı]]



|-

! style="background%3A%23EFEFEF" | [[sizin]] (“your”)


|[[yardımınızı]]


|[[yardımlarınızı]]



|-

! style="background%3A%23EFEFEF" | [[onların]] (“their”)


|[[yardımını]]&nbsp;''or'' [[yardımlarını]]


|[[yardımlarını]]



|-

! colspan="1" style |


! colspan="2" style="background%3A%23DEDEDE" |dative


|-

! colspan="1" rowspan="1" style |


! colspan="1" rowspan="1" style="background%3A%23DEDEDE" |singular


| colspan="1" style="background%3A%23DEDEDE" |'''plural'''



|-

! style="background%3A%23EFEFEF" | [[mənim]] (“my”)


|[[yardımıma]]


|[[yardımlarıma]]



|-

! style="background%3A%23EFEFEF" | [[sənin]] (“your”)


|[[yardımına]]


|[[yardımlarına]]



|-

! style="background%3A%23EFEFEF" | [[onun]] (“his/her/its”)


|[[yardımına]]


|[[yardımlarına]]



|-

! style="background%3A%23EFEFEF" | [[bizim]] (“our”)


|[[yardımımıza]]


|[[yardımlarımıza]]



|-

! style="background%3A%23EFEFEF" | [[sizin]] (“your”)


|[[yardımınıza]]


|[[yardımlarınıza]]



|-

! style="background%3A%23EFEFEF" | [[onların]] (“their”)


|[[yardımına]]&nbsp;''or'' [[yardımlarına]]


|[[yardımlarına]]



|-

! colspan="1" style |


! colspan="2" style="background%3A%23DEDEDE" |locative


|-

! colspan="1" rowspan="1" style |


! colspan="1" rowspan="1" style="background%3A%23DEDEDE" |singular


| colspan="1" style="background%3A%23DEDEDE" |'''plural'''



|-

! style="background%3A%23EFEFEF" | [[mənim]] (“my”)


|[[yardımımda]]


|[[yardımlarımda]]



|-

! style="background%3A%23EFEFEF" | [[sənin]] (“your”)


|[[yardımında]]


|[[yardımlarında]]



|-

! style="background%3A%23EFEFEF" | [[onun]] (“his/her/its”)


|[[yardımında]]


|[[yardımlarında]]



|-

! style="background%3A%23EFEFEF" | [[bizim]] (“our”)


|[[yardımımızda]]


|[[yardımlarımızda]]



|-

! style="background%3A%23EFEFEF" | [[sizin]] (“your”)


|[[yardımınızda]]


|[[yardımlarınızda]]



|-

! style="background%3A%23EFEFEF" | [[onların]] (“their”)


|[[yardımında]]&nbsp;''or'' [[yardımlarında]]


|[[yardımlarında]]



|-

! colspan="1" style |


! colspan="2" style="background%3A%23DEDEDE" |ablative


|-

! colspan="1" rowspan="1" style |


! colspan="1" rowspan="1" style="background%3A%23DEDEDE" |singular


| colspan="1" style="background%3A%23DEDEDE" |'''plural'''



|-

! style="background%3A%23EFEFEF" | [[mənim]] (“my”)


|[[yardımımdan]]


|[[yardımlarımdan]]



|-

! style="background%3A%23EFEFEF" | [[sənin]] (“your”)


|[[yardımından]]


|[[yardımlarından]]



|-

! style="background%3A%23EFEFEF" | [[onun]] (“his/her/its”)


|[[yardımından]]


|[[yardımlarından]]



|-

! style="background%3A%23EFEFEF" | [[bizim]] (“our”)


|[[yardımımızdan]]


|[[yardımlarımızdan]]



|-

! style="background%3A%23EFEFEF" | [[sizin]] (“your”)


|[[yardımınızdan]]


|[[yardımlarınızdan]]



|-

! style="background%3A%23EFEFEF" | [[onların]] (“their”)


|[[yardımından]]&nbsp;''or'' [[yardımlarından]]


|[[yardımlarından]]



|-

! colspan="1" style |


! colspan="2" style="background%3A%23DEDEDE" |genitive


|-

! colspan="1" rowspan="1" style |


! colspan="1" rowspan="1" style="background%3A%23DEDEDE" |singular


| colspan="1" style="background%3A%23DEDEDE" |'''plural'''



|-

! style="background%3A%23EFEFEF" | [[mənim]] (“my”)


|[[yardımımın]]


|[[yardımlarımın]]



|-

! style="background%3A%23EFEFEF" | [[sənin]] (“your”)


|[[yardımının]]


|[[yardımlarının]]



|-

! style="background%3A%23EFEFEF" | [[onun]] (“his/her/its”)


|[[yardımının]]


|[[yardımlarının]]



|-

! style="background%3A%23EFEFEF" | [[bizim]] (“our”)


|[[yardımımızın]]


|[[yardımlarımızın]]



|-

! style="background%3A%23EFEFEF" | [[sizin]] (“your”)


|[[yardımınızın]]


|[[yardımlarınızın]]



|-

! style="background%3A%23EFEFEF" | [[onların]] (“their”)


|[[yardımının]]&nbsp;''or'' [[yardımlarının]]


|[[yardımlarının]]



|}
</div></div>
""")
        expected = {
            "forms": [
              {
                "form": "",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "yardım",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "yardımlar",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "yardımı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "singular"
                ]
              },
              {
                "form": "yardımları",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "plural"
                ]
              },
              {
                "form": "yardıma",
                "source": "Declension",
                "tags": [
                  "dative",
                  "singular"
                ]
              },
              {
                "form": "yardımlara",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural"
                ]
              },
              {
                "form": "yardımda",
                "source": "Declension",
                "tags": [
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "yardımlarda",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "yardımdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "singular"
                ]
              },
              {
                "form": "yardımlardan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural"
                ]
              },
              {
                "form": "yardımın",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "yardımların",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "",
                "source": "Declension",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "yardımım",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "nominative",
                  "possessive",
                  "possessive-single",
                  "singular"
                ]
              },
              {
                "form": "yardımlarım",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "nominative",
                  "possessive",
                  "possessive-many",
                  "singular"
                ]
              },
              {
                "form": "yardımın",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessive",
                  "possessive-single",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımların",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessive",
                  "possessive-many",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımı",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessive",
                  "possessive-single",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımları",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessive",
                  "possessive-many",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımımız",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "nominative",
                  "plural",
                  "possessive",
                  "possessive-single"
                ]
              },
              {
                "form": "yardımlarımız",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "nominative",
                  "plural",
                  "possessive",
                  "possessive-many"
                ]
              },
              {
                "form": "yardımınız",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınız",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "second-person"
                ]
              },
              {
                "form": "yardımı",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımları",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımları",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "third-person"
                ]
              },
              {
                "form": "yardımımı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "first-person",
                  "possessive",
                  "possessive-single",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "first-person",
                  "possessive",
                  "possessive-many",
                  "singular"
                ]
              },
              {
                "form": "yardımını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessive",
                  "possessive-single",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessive",
                  "possessive-many",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessive",
                  "possessive-single",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessive",
                  "possessive-many",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımımızı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-single"
                ]
              },
              {
                "form": "yardımlarımızı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-many"
                ]
              },
              {
                "form": "yardımınızı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "second-person"
                ]
              },
              {
                "form": "yardımını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "third-person"
                ]
              },
              {
                "form": "yardımıma",
                "source": "Declension",
                "tags": [
                  "dative",
                  "first-person",
                  "possessive",
                  "possessive-single",
                  "singular"
                ]
              },
              {
                "form": "yardımlarıma",
                "source": "Declension",
                "tags": [
                  "dative",
                  "first-person",
                  "possessive",
                  "possessive-many",
                  "singular"
                ]
              },
              {
                "form": "yardımına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessive",
                  "possessive-single",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessive",
                  "possessive-many",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessive",
                  "possessive-single",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessive",
                  "possessive-many",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımımıza",
                "source": "Declension",
                "tags": [
                  "dative",
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-single"
                ]
              },
              {
                "form": "yardımlarımıza",
                "source": "Declension",
                "tags": [
                  "dative",
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-many"
                ]
              },
              {
                "form": "yardımınıza",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınıza",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "second-person"
                ]
              },
              {
                "form": "yardımına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "third-person"
                ]
              },
              {
                "form": "yardımımda",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "locative",
                  "possessive",
                  "possessive-single",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımda",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "locative",
                  "possessive",
                  "possessive-many",
                  "singular"
                ]
              },
              {
                "form": "yardımında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessive",
                  "possessive-single",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessive",
                  "possessive-many",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessive",
                  "possessive-single",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessive",
                  "possessive-many",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımımızda",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "locative",
                  "plural",
                  "possessive",
                  "possessive-single"
                ]
              },
              {
                "form": "yardımlarımızda",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "locative",
                  "plural",
                  "possessive",
                  "possessive-many"
                ]
              },
              {
                "form": "yardımınızda",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızda",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "second-person"
                ]
              },
              {
                "form": "yardımında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "third-person"
                ]
              },
              {
                "form": "yardımımdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "first-person",
                  "possessive",
                  "possessive-single",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "first-person",
                  "possessive",
                  "possessive-many",
                  "singular"
                ]
              },
              {
                "form": "yardımından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessive",
                  "possessive-single",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessive",
                  "possessive-many",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessive",
                  "possessive-single",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessive",
                  "possessive-many",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımımızdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-single"
                ]
              },
              {
                "form": "yardımlarımızdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "first-person",
                  "plural",
                  "possessive",
                  "possessive-many"
                ]
              },
              {
                "form": "yardımınızdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "second-person"
                ]
              },
              {
                "form": "yardımından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "third-person"
                ]
              },
              {
                "form": "yardımımın",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "genitive",
                  "possessive",
                  "possessive-single",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımın",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "genitive",
                  "possessive",
                  "possessive-many",
                  "singular"
                ]
              },
              {
                "form": "yardımının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessive",
                  "possessive-single",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessive",
                  "possessive-many",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessive",
                  "possessive-single",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessive",
                  "possessive-many",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımımızın",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "genitive",
                  "plural",
                  "possessive",
                  "possessive-single"
                ]
              },
              {
                "form": "yardımlarımızın",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "genitive",
                  "plural",
                  "possessive",
                  "possessive-many"
                ]
              },
              {
                "form": "yardımınızın",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızın",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "second-person"
                ]
              },
              {
                "form": "yardımının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessive",
                  "possessive-single",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessive",
                  "possessive-many",
                  "third-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

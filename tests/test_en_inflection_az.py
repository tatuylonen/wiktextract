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


class EnAzInflTests(unittest.TestCase):
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
                "form": "no-table-tags",
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
                  "possessed-single",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımlarım",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "nominative",
                  "possessed-many",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımın",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessed-single",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımların",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessed-many",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımı",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessed-single",
                  "possessive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımları",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "possessed-many",
                  "possessive",
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
                  "possessed-single",
                  "possessive",
                ]
              },
              {
                "form": "yardımlarımız",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "nominative",
                  "plural",
                  "possessed-many",
                  "possessive",
                ]
              },
              {
                "form": "yardımınız",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınız",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımı",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımları",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımları",
                "source": "Declension",
                "tags": [
                  "nominative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımımı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "first-person",
                  "possessed-single",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "first-person",
                  "possessed-many",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessed-single",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessed-many",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessed-single",
                  "possessive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "possessed-many",
                  "possessive",
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
                  "possessed-single",
                  "possessive",
                ]
              },
              {
                "form": "yardımlarımızı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "first-person",
                  "plural",
                  "possessed-many",
                  "possessive",
                ]
              },
              {
                "form": "yardımınızı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızı",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarını",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımıma",
                "source": "Declension",
                "tags": [
                  "dative",
                  "first-person",
                  "possessed-single",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımlarıma",
                "source": "Declension",
                "tags": [
                  "dative",
                  "first-person",
                  "possessed-many",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessed-single",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessed-many",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessed-single",
                  "possessive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "possessed-many",
                  "possessive",
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
                  "possessed-single",
                  "possessive",
                ]
              },
              {
                "form": "yardımlarımıza",
                "source": "Declension",
                "tags": [
                  "dative",
                  "first-person",
                  "plural",
                  "possessed-many",
                  "possessive",
                ]
              },
              {
                "form": "yardımınıza",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınıza",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarına",
                "source": "Declension",
                "tags": [
                  "dative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımımda",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "locative",
                  "possessed-single",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımda",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "locative",
                  "possessed-many",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessed-single",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessed-many",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessed-single",
                  "possessive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "possessed-many",
                  "possessive",
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
                  "possessed-single",
                  "possessive",
                ]
              },
              {
                "form": "yardımlarımızda",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "locative",
                  "plural",
                  "possessed-many",
                  "possessive",
                ]
              },
              {
                "form": "yardımınızda",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızda",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarında",
                "source": "Declension",
                "tags": [
                  "locative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımımdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "first-person",
                  "possessed-single",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "first-person",
                  "possessed-many",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessed-single",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessed-many",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessed-single",
                  "possessive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "possessed-many",
                  "possessive",
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
                  "possessed-single",
                  "possessive",
                ]
              },
              {
                "form": "yardımlarımızdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "first-person",
                  "plural",
                  "possessed-many",
                  "possessive",
                ]
              },
              {
                "form": "yardımınızdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızdan",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarından",
                "source": "Declension",
                "tags": [
                  "ablative",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımımın",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "genitive",
                  "possessed-single",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımlarımın",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "genitive",
                  "possessed-many",
                  "possessive",
                  "singular"
                ]
              },
              {
                "form": "yardımının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessed-single",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessed-many",
                  "possessive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "yardımının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessed-single",
                  "possessive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "possessed-many",
                  "possessive",
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
                  "possessed-single",
                  "possessive",
                ]
              },
              {
                "form": "yardımlarımızın",
                "source": "Declension",
                "tags": [
                  "first-person",
                  "genitive",
                  "plural",
                  "possessed-many",
                  "possessive",
                ]
              },
              {
                "form": "yardımınızın",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımlarınızın",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "second-person"
                ]
              },
              {
                "form": "yardımının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessed-single",
                  "possessive",
                  "third-person"
                ]
              },
              {
                "form": "yardımlarının",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "plural",
                  "possessed-many",
                  "possessive",
                  "third-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

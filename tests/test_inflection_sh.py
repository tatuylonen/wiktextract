# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

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

    def test_SerboCroatian_adj1(self):
        ret = self.xinfl("maorski", "Serbo-Croatian", "adj", "Declension", """
<div class="NavFrame" style>
<div class="NavHead" style="background%3A%23eff7ff">Declension of <i class="Latn+mention" lang="sh">maorski</i></div>
<div class="NavContent">

{| border="1px+solid+%23000000" style="border-collapse%3Acollapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+font-size%3A12px%3B+width%3A100%25" class="inflection-table"

|-

! style="background%3A%23d9ebff%3B+width%3A25%25" colspan="2" |singular


! style="background%3A%23d9ebff" |masculine


! style="background%3A%23d9ebff" |feminine


! style="background%3A%23d9ebff" |neuter


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''nominative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorska</span>


|<span class="Latn" lang="sh">maorsko</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''genitive'''


|<span class="Latn" lang="sh">maorskog(a)</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorskog(a)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''dative'''


|<span class="Latn" lang="sh">maorskom(u/e)</span>


|<span class="Latn" lang="sh">maorskoj</span>


|<span class="Latn" lang="sh">maorskom(u/e)</span>


|-

! style="background-color%3A%23eff7ff" |'''accusative'''


! style="background%3A%23eff7ff" |<small>inanimate</small><br><small>animate</small>


|<span class="Latn" lang="sh">maorski<br>maorskog(a)</span>


|<span class="Latn" lang="sh">maorsku</span>


|<span class="Latn" lang="sh">maorsko</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''vocative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorska</span>


|<span class="Latn" lang="sh">maorsko</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''locative'''


|<span class="Latn" lang="sh">maorskom(e/u)</span>


|<span class="Latn" lang="sh">maorskoj</span>


|<span class="Latn" lang="sh">maorskom(e/u)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''instrumental'''


|<span class="Latn" lang="sh">maorskim</span>


|<span class="Latn" lang="sh">maorskom</span>


|<span class="Latn" lang="sh">maorskim</span>


|-

! style="background%3A%23d9ebff%3B+width%3A30%25" colspan="2" |plural


! style="background%3A%23d9ebff" |masculine


! style="background%3A%23d9ebff" |feminine


! style="background%3A%23d9ebff" |neuter


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''nominative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorska</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''genitive'''


|<span class="Latn" lang="sh">maorskih</span>


|<span class="Latn" lang="sh">maorskih</span>


|<span class="Latn" lang="sh">maorskih</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''dative'''


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''accusative'''


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorska</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''vocative'''


|<span class="Latn" lang="sh">maorski</span>


|<span class="Latn" lang="sh">maorske</span>


|<span class="Latn" lang="sh">maorska</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''locative'''


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|-

! style="background-color%3A%23eff7ff" colspan="2" |'''instrumental'''


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|<span class="Latn" lang="sh">maorskim(a)</span>


|}
</div></div>

[[Category:sh:Languages]]
""")
        expected = {
            "forms": [
              {
                "form": "maorski",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "maorska",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "maorsko",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "nominative",
                  "singular"
                ]
              },
              {
                "form": "maorskog",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorskoga",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorske",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "singular"
                ]
              },
              {
                "form": "maorskog",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorskoga",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorskomu",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorskome",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorskoj",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "maorskomu",
                "source": "Declension",
                "tags": [
                  "dative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorskome",
                "source": "Declension",
                "tags": [
                  "dative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorski",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "inanimate",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorsku",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "singular"
                ]
              },
              {
                "form": "maorsko",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorskog",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "animate",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorskoga",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "animate",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorski",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "maorska",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "maorsko",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "singular",
                  "vocative"
                ]
              },
              {
                "form": "maorskome",
                "source": "Declension",
                "tags": [
                  "locative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorskomu",
                "source": "Declension",
                "tags": [
                  "locative",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorskoj",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "locative",
                  "singular"
                ]
              },
              {
                "form": "maorskome",
                "source": "Declension",
                "tags": [
                  "locative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorskomu",
                "source": "Declension",
                "tags": [
                  "locative",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "maorskom",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "instrumental",
                  "singular"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "neuter",
                  "singular"
                ]
              },
              {
                "form": "maorski",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "maorske",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "maorska",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "maorskih",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorskih",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "plural"
                ]
              },
              {
                "form": "maorskih",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "dative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "dative",
                  "feminine",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "dative",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "dative",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "maorske",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorske",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "plural"
                ]
              },
              {
                "form": "maorska",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "maorski",
                "source": "Declension",
                "tags": [
                  "masculine",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "maorske",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "maorska",
                "source": "Declension",
                "tags": [
                  "neuter",
                  "plural",
                  "vocative"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "locative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "locative",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "locative",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "locative",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "locative",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "instrumental",
                  "plural"
                ]
              },
              {
                "form": "maorskim",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "neuter",
                  "plural"
                ]
              },
              {
                "form": "maorskima",
                "source": "Declension",
                "tags": [
                  "instrumental",
                  "neuter",
                  "plural"
                ]
              }
            ],
                  }
        self.assertEqual(expected, ret)

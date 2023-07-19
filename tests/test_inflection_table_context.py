# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org
import unittest

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.inflection import parse_inflection_section, TableContext
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
        tablecontext = TableContext("test-template-name")
        parse_inflection_section(self.wxr, data, word, lang, pos,
                                 section, tree, tablecontext=tablecontext)
        return data

    def test_Swedish_noun1(self):
        ret = self.xinfl("berg", "Swedish", "noun", "Declension", """
{| class="inflection-table+vsSwitcher" data-toggle-category="inflection" style="border%3A+solid+1px+%23CCCCFF%3B+text-align%3Aleft%3B" cellspacing="1" cellpadding="2"

|- style="background%3A+%23CCCCFF%3B+vertical-align%3A+top%3B"

! class="vsToggleElement" colspan="5" | Declension of <i class="Latn+mention" lang="sv">berg</i>&nbsp;


|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! rowspan="2" style="min-width%3A+12em%3B" |


! colspan="2" | Singular

|- class="vsHide" style="background%3A+%23CCCCFF%3B"

! style="min-width%3A+12em%3B" | Indefinite

|- class="vsHide" style="background%3A+%23F2F2FF%3B"

! style="background%3A+%23E6E6FF%3B" | Nominative


| <span class="Latn" lang="sv">[[berg#Swedish|berg]]</span>


|}
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
                "form": "test-template-name",
                "source": "Declension",
                "tags": [
                  "inflection-template"
                ]
              },
              {
                "form": "berg",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "nominative",
                  "singular"
                ]
              },
            ],
        }
        self.assertEqual(expected, ret)

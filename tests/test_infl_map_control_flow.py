# -*- fundamental -*-
#
# Tests for infl_map control flow
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest

from unittest.mock import patch

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.inflection import expand_header, TableContext
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class InflTests(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")
        self.tablecontext = TableContext("barfoo")

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def xexpand_header(self, text, i_map, lang="English", pos="verb",
                       base_tags=[],):
        with patch('wiktextract.inflection.infl_map', i_map):
            ret = expand_header(self.wxr, self.tablecontext,
                                "foobar", lang,
                                pos, "foo", base_tags)
        return ret

    def test_basic(self):
        ret = self.xexpand_header("foo", { "foo": "counterfactual" })
        expected = [("counterfactual",)]
        self.assertEqual(expected, ret)

    def test_basic_b(self):
        ret = self.xexpand_header("foo", { "bar": "counterfactual" })
        expected = [("error-unrecognized-form",)]
        self.assertEqual(expected, ret)


    def test_if1(self):
        infl_map = {
            "foo": {
                # if this tag was previously present
                "if": "indicative",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("positive",)] # then
        self.assertEqual(expected, ret)

    def test_if2(self):
        infl_map = {
            "foo": {
                # if any of these tags previously present
                "if": "any: indicative counterfactual",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("positive",)] # then
        self.assertEqual(expected, ret)

    def test_if3(self):
        infl_map = {
            "foo": {
                # if all tags are previously present
                "if": "indicative counterfactual",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("negative",)] # else
        self.assertEqual(expected, ret)

    def test_if4(self):
        infl_map = {
            "foo": {
                # negative test
                "if": "counterfactual",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("negative",)] # else
        self.assertEqual(expected, ret)

    def test_if5(self):
        infl_map = {
            "foo": {
                # no if test
                "if": "",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("positive",)] # then
        self.assertEqual(expected, ret)

    def test_if6(self):
        infl_map = {
            "foo": {
                # no if test
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("positive",)] # then
        self.assertEqual(expected, ret)

    def test_if7(self):
        infl_map = {
            "foo": {
                "if": "indicative",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [()] # "then"
        self.assertEqual(expected, ret)

    def test_if8(self):
        infl_map = {
            "foo": {
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [()] # then
        self.assertEqual(expected, ret)

    def test_if9(self):
        infl_map = {
            "foo": {
                "if": "counterfactual",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("negative",)] # then
        self.assertEqual(expected, ret)

    def test_if10(self):
        infl_map = {
            "foo": {
                "if": "counterfactual",
                "then": {
                    "if": "indicative",
                    "then": "positive",
                },
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["counterfactual",
                                             "indicative"],)
        expected = [("positive",)] # then
        self.assertEqual(expected, ret)

    def test_if11(self):
        infl_map = {
            "foo": {
                "if": "counterfactual",
                "then": {
                    "if": "indicative",
                    "then": "positive",
                },
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["counterfactual"],)
        expected = [("error-unrecognized-form",)] # then
        self.assertEqual(expected, ret)

    def test_default1(self):
        infl_map = {
            "foo": {
                "default": "negative",
                "if": "counterfactual",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("negative",)] # default
        self.assertEqual(expected, ret)

    def test_default2(self):
        infl_map = {
            "foo": {
                "default": "negative",
                "if": "indicative",
                "then": {
                    "if": "counterfactual",
                    "then": "positive"
                },

            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("negative",)] # default
        self.assertEqual(expected, ret)

    def test_default3(self):
        infl_map = {
            "foo": {
                "default": "positive",
                "if": "indicative",
                "then": {
                    "default": "negative",
                    "if": "counterfactual",
                    "then": "positive"
                },

            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  base_tags=["indicative"],)
        expected = [("negative",)] # deeper default
        self.assertEqual(expected, ret)

    def test_lang1(self):
        infl_map = {
            "foo": {
                "lang": "Finnish",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  base_tags=["indicative"],)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

    def test_lang2(self):
        infl_map = {
            "foo": {
                "lang": "English",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_pos1(self):
        infl_map = {
            "foo": {
                "pos": "noun",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

    def test_pos2(self):
        infl_map = {
            "foo": {
                "pos": "verb",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_tmplt_name1(self):
        infl_map = {
            "foo": {
                "inflection-template": "barfoo",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  pos="noun",)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

    def test_tmplt_name2(self):
        infl_map = {
            "foo": {
                "inflection-template": "foofoo",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  pos="noun",)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions1(self):
        infl_map = {
            "foo": {
                "lang": "Finnish",
                "pos": "noun",
                "if": "indicative",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions2(self):
        infl_map = {
            "foo": {
                "lang": "Finnish",
                "pos": "noun",
                "if": "counterfactual",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions3(self):
        infl_map = {
            "foo": {
                "lang": "Finnish",
                "pos": "verb",
                "if": "indicative",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions4(self):
        infl_map = {
            "foo": {
                "lang": "Finnish",
                "pos": "verb",
                "if": "counterfactual",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions5(self):
        infl_map = {
            "foo": {
                "lang": "English",
                "pos": "noun",
                "if": "indicative",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions6(self):
        infl_map = {
            "foo": {
                "lang": "English",
                "pos": "noun",
                "if": "counterfactual",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions7(self):
        infl_map = {
            "foo": {
                "lang": "English",
                "pos": "verb",
                "if": "indicative",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions8(self):
        infl_map = {
            "foo": {
                "lang": "English",
                "pos": "verb",
                "if": "counterfactual",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("negative",)]
        self.assertEqual(expected, ret)

    def test_combined_conditions9(self):
        infl_map = {
            "foo": {
                "lang": "English",
                "pos": "verb",
                "inflection-template": "barfoo",
                "if": "indicative",
                "then": "positive",
                "else": "negative",
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="English",
                                  pos="verb",
                                  base_tags=["indicative"],)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

    def test_mixed1(self):
        infl_map = {
            "foo": {
                "default": "negative",
                "lang": "Finnish",
                "then": {
                    "if": "indicative",
                    "then": "positive",
                },
                "else": {
                    "pos": "noun",
                    "then": "negative",
                    "else": {
                        "lang": "English",
                        "then": "negative",
                    },
                },
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="Finnish",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

    def test_mixed2(self):
        infl_map = {
            "foo": {
                "default": "positive",
                "lang": "Finnish",
                "then": {
                    "if": "indicative",
                    "then": "negative",
                },
                "else": {
                    "pos": "verb",
                    "then": {
                        "lang": "English",
                        "then": "negative",
                    "else": "negative",
                    },
                },
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="English",
                                  pos="noun",
                                  base_tags=["indicative"],)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

    def test_mixed3(self):
        infl_map = {
            "foo": {
                "default": "negative",
                "lang": "Finnish",
                "then": {
                    "if": "indicative",
                    "then": "negative",
                },
                "else": {
                    "pos": "noun",
                    "then": "negative",
                    "else": {
                        "lang": "English",
                        "then": "positive",
                    },
                },
            },
        }
        ret = self.xexpand_header("foo", infl_map,
                                  lang="English",
                                  pos="verb",
                                  base_tags=["indicative"],)
        expected = [("positive",)]
        self.assertEqual(expected, ret)

# Tests for parse_translation_desc()
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
from wikitextprocessor import Wtp
from wiktextract import WiktionaryConfig
from wiktextract.form_descriptions import parse_translation_desc
from wiktextract.translations import parse_translation_item_text

class TrTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 20000
        self.ctx = Wtp()
        self.config = WiktionaryConfig()
        self.ctx.start_page("abolitionism")  # Note: some tests use last char
        self.ctx.start_section("English")

    def runtr(self, item, sense=None, pos_datas=[],
              lang=None, langcode=None, translations_from_template=[]):
        """Simple test runner.  Returns data."""
        data = {}
        parse_translation_item_text(self.ctx, self.ctx.title, data,
                                    item, sense, pos_datas, lang, langcode,
                                    translations_from_template)
        return data

    def test_trdesc1(self):
        tr = {}
        # Note: this test uses last char of title
        parse_translation_desc(self.ctx, "French", "abolitionnisme m", tr)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(tr, {"word": "abolitionnisme",
                              "tags": ["masculine"]})

    def test_trdesc2(self):
        tr = {}
        parse_translation_desc(self.ctx, "French", "abolitionnisme f", tr)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(tr, {"word": "abolitionnisme",
                              "tags": ["feminine"]})

    def test_trdesc3(self):
        tr = {}
        # m is in page title, should not interpret as tag
        self.ctx.start_page("m m m")
        parse_translation_desc(self.ctx, "French", "m m m", tr)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(tr, {"word": "m m m"})

    def test_trdesc4(self):
        tr = {}
        self.ctx.start_page("assessment")
        parse_translation_desc(self.ctx, "German", "Schätzung f", tr)
        self.assertEqual(self.ctx.errors, [])
        self.assertEqual(self.ctx.warnings, [])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(tr, {"word": "Schätzung",
                              "tags": ["feminine"]})

    def test_tr1(self):
        data = self.runtr("Finnish: foo")
        self.assertEqual(data, {"translations": [
            {"word": "foo", "lang": "Finnish", "code": "fi"},
            ]})

    def test_tr2(self):
        data = self.runtr("Swedish: foo f")
        self.assertEqual(data, {"translations": [
            {"word": "foo", "lang": "Swedish", "code": "sv",
             "tags": ["feminine"]},
            ]})

    def test_tr3(self):
        data = self.runtr("Swedish: foo f or m")
        self.assertEqual(data, {"translations": [
            {"word": "foo", "lang": "Swedish", "code": "sv",
             "tags": ["feminine", "masculine"]},
            ]})

    def test_tr4(self):
        data = self.runtr("Swedish: foo ?")
        self.assertEqual(data, {"translations": [
            {"word": "foo", "lang": "Swedish", "code": "sv"},
            ]})

    def test_tr5(self):
        data = self.runtr("Swedish: foo f, bar m")
        self.assertEqual(data, {"translations": [
            {"word": "foo", "lang": "Swedish", "code": "sv",
             "tags": ["feminine"]},
            {"word": "bar", "lang": "Swedish", "code": "sv",
             "tags": ["masculine"]},
            ]})

    def test_tr6(self):
        data = self.runtr("Swedish: foo f sg or f pl")
        self.assertEqual(data, {"translations": [
            {"word": "foo", "lang": "Swedish", "code": "sv",
             "tags": ["feminine", "plural", "singular"]},
            ]})

    def test_tr7(self):
        # Dual should not be processed for Swedish
        data = self.runtr("Swedish: foo du")
        self.assertNotEqual(self.ctx.debugs, [])  # Should be suspicious tr
        self.assertEqual(data, {"translations": [
            {"word": "foo du", "lang": "Swedish", "code": "sv"},
            ]})

    def test_tr8(self):
        data = self.runtr("Mandarin: 是 (rrr)", lang="Chinese")
        self.assertEqual(data, {"translations": [
            {"word": "是", "roman": "rrr", "lang": "Chinese", "code": "zh",
             "tags": ["Mandarin"]},
            ]})

    def test_tr9(self):
        data = self.runtr("Mandarin: 寺 (zh) (sì) (Buddhist)",
                          langcode="zh")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "寺", "roman": "sì", "lang": "Mandarin", "code": "zh",
             "english": "Buddhist"},
            ]})

    def test_tr10(self):
        data = self.runtr("Arabic: مَعْبَد‎ m (maʿbad), هَيْكَل‎ m (haykal)",
                          langcode="ar")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "مَعْبَد‎", "roman": "maʿbad", "lang": "Arabic", "code": "ar",
             "tags": ["masculine"]},
            {"word": "هَيْكَل‎", "roman": "haykal", "lang": "Arabic",
             "code": "ar", "tags": ["masculine"]},
            ]})

    def test_tr11(self):
        data = self.runtr("Oriya: please add this translation if you can")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {})

    def test_tr12(self):
        data = self.runtr("Burmese: လျှောက် (my) (hlyauk), လမ်းလျှောက် (my) (lam:hlyauk)")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "လျှောက်", "roman": "hlyauk", "lang": "Burmese",
             "code": "my"},
            {"word": "လမ်းလျှောက်", "roman": "lam:hlyauk", "lang": "Burmese",
             "code": "my"},
            ]})

    def test_tr13(self):
        data = self.runtr("Finnish: tämä, testi",
                          translations_from_template=["tämä, testi"])
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "tämä, testi", "lang": "Finnish", "code": "fi"},
            ]})

    def test_tr14(self):
        data = self.runtr("Finnish: kävellä (fi), käydä (fi) "
                          "(poetic or archaic)")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "kävellä", "lang": "Finnish", "code": "fi"},
            {"word": "käydä", "lang": "Finnish", "code": "fi",
             "tags": ["archaic", "poetic"]},
            ]})

    def test_tr15(self):
        data = self.runtr("Macedonian: шета (šeta) (to go for a walk), "
                          "иде (ide)")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "шета", "roman": "šeta", "lang": "Macedonian",
             "english": "to go for a walk",
             "code": "mk"},
            {"word": "иде", "roman": "ide", "lang": "Macedonian", "code": "mk"},
            ]})

    def test_tr16(self):
        data = self.runtr("Russian: испари́ться (ru) (isparítʹsja) "
                          "(colloquial), бы́ли вы́несенны pl or pf "
                          "(býli výnesenny) (past tense)")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "испари́ться", "roman": "isparítʹsja",
             "lang": "Russian", "code": "ru", "tags": ["colloquial"]},
            {"word": "бы́ли вы́несенны", "roman": "býli výnesenny",
             "lang": "Russian", "code": "ru", "tags": ["past"]},
            ]})

    def test_tr16(self):
        # Test second-level "language" being script name
        data = self.runtr("Burmese: ပဏ္ဏ n (paṇṇa)",
                          lang="Pali")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "ပဏ္ဏ", "roman": "paṇṇa",
             "lang": "Pali", "code": "pi", "tags": ["Burmese", "neuter"]},
            ]})

    def test_tr17(self):
        data = self.runtr("Finnish: foo 11")
        self.assertNotEqual(self.ctx.debugs, [])  # should get warning
        self.assertEqual(data, {"translations": [
            {"word": "foo 11", "lang": "Finnish", "code": "fi"},
            ]})

    def test_tr18(self):
        data = self.runtr("Maore Comorian: wani 11 or 6")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "wani", "lang": "Maore Comorian", "code": "swb",
             "tags": ["class-11", "class-6"]},
            ]})

    def test_tr19(self):
        data = self.runtr("Lingala: nkásá 9 or 10, lokásá 11 or 10")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "nkásá", "lang": "Lingala", "code": "ln",
             "tags": ["class-10", "class-9"]},
            {"word": "lokásá", "lang": "Lingala", "code": "ln",
             "tags": ["class-10", "class-11"]},
            ]})

    def test_tr20(self):
        data = self.runtr("Swahili: jani (sw) 5 or 6, msahafu (sw) 3 or 4")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "jani", "lang": "Swahili", "code": "sw",
             "tags": ["class-5", "class-6"]},
            {"word": "msahafu", "lang": "Swahili", "code": "sw",
             "tags": ["class-3", "class-4"]},
            ]})

    def test_tr21(self):
        data = self.runtr("Xhosa: igqabi 5 or 6")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "igqabi", "lang": "Xhosa", "code": "xh",
             "tags": ["class-5", "class-6"]},
            ]})

    def test_tr22(self):
        data = self.runtr("Zulu: ikhasi (zu) 5 or 6, iqabi (zu) 5 or 6")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "ikhasi", "lang": "Zulu", "code": "zu",
             "tags": ["class-5", "class-6"]},
            {"word": "iqabi", "lang": "Zulu", "code": "zu",
             "tags": ["class-5", "class-6"]},
            ]})

    def test_tr23(self):
        data = self.runtr("Belarusian: ліст m (list)")
        self.assertEqual(self.ctx.debugs, [])
        self.assertEqual(data, {"translations": [
            {"word": "ліст", "lang": "Belarusian", "code": "be",
             "roman": "list", "tags": ["masculine"]},
            ]})




    # XXX for now this kind of or splitting is broken
    # def test_tr7(self):
    #     data = self.runtr("Swedish: foo f or bar m")
    #     self.assertEqual(data, {"translations": [
    #         {"word": "foo", "lang": "Swedish", "code": "sv",
    #          "tags": ["feminine"]},
    #         {"word": "bar", "lang": "Swedish", "code": "sv",
    #          "tags": ["masculine"]},
    #         ]})

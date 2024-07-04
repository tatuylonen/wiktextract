# Tests for classify_desc()
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest

from wiktextract.form_descriptions import classify_desc


class ClassifyTests(unittest.TestCase):

    def test_empty(self):
        ret = classify_desc("")
        self.assertEqual(ret, "other")

    def test_classify1(self):
        cls = classify_desc("predicative particle")
        self.assertEqual(cls, "tags")

    def test_classify2(self):
        cls = classify_desc("predicative, particle")
        self.assertEqual(cls, "tags")

    def test_classify3(self):
        cls = classify_desc("Lat. Amer.")
        self.assertEqual(cls, "tags")

    def test_classify4(self):
        cls = classify_desc("Lynx lynx")
        self.assertEqual(cls, "taxonomic")

    def test_classify5(self):
        # Defined in taxondata.py
        cls = classify_desc("Eudyptes unknowniensis")
        self.assertEqual(cls, "taxonomic")

    def test_classify6(self):
        # Defined in form_description.py as additional genus
        cls = classify_desc("Monetaria unknowniensis")
        self.assertEqual(cls, "taxonomic")

    def test_classify7(self):
        # Currently, only the first word of a taxonomic name can be capitalized.
        # This should perhaps be reviewed.
        cls = classify_desc("Monetaria Unknowniensis")
        self.assertEqual(cls, "english")

    def test_classify8(self):
        cls = classify_desc("Monetaria unknowniensis IV")
        self.assertEqual(cls, "taxonomic")

    def test_classify9(self):
        cls = classify_desc("winter")
        self.assertEqual(cls, "english")

    def test_classify10(self):
        cls = classify_desc("winter")
        self.assertEqual(cls, "english")

    def test_classify11(self):
        cls = classify_desc("winter weather")
        self.assertEqual(cls, "english")

    def test_classify12(self):
        cls = classify_desc("Winter Weather")
        self.assertEqual(cls, "english")

    def test_classify13(self):
        cls = classify_desc("winter's")
        self.assertEqual(cls, "english")

    def test_classify13a(self):
        cls = classify_desc("winters'")
        self.assertEqual(cls, "english")

    def test_classify14(self):
        # Compound not in words, both words are
        cls = classify_desc("winter-bringing")
        self.assertEqual(cls, "english")

    def test_classify15(self):
        # Compound not in words, both words are
        cls = classify_desc("winter-bringing")
        self.assertEqual(cls, "english")

    def test_classify16(self):
        # Word in english_words.py but not brown corpus
        cls = classify_desc("lily")
        self.assertEqual(cls, "english")

    def test_classify17(self):
        # Word in english_words.py but plural not defined
        cls = classify_desc("plurals")
        self.assertEqual(cls, "english")

    def test_classify18(self):
        # Word in brown but -ing not
        cls = classify_desc("atoning")
        self.assertEqual(cls, "english")

    def test_classify19(self):
        # Word in brown but -ed not
        cls = classify_desc("atoned")
        self.assertEqual(cls, "english")

    def test_classify20(self):
        # Word in brown but -ed not
        cls = classify_desc('he said "run"!')
        self.assertEqual(cls, "english")

    def test_classify21(self):
        cls = classify_desc('!')
        self.assertEqual(cls, "other")

    def test_classify22(self):
        cls = classify_desc("'")
        self.assertEqual(cls, "other")

    def test_classify23(self):
        cls = classify_desc("/foo/")
        self.assertEqual(cls, "romanization")

    def test_classify24(self):
        cls = classify_desc("fo/o")
        self.assertEqual(cls, "romanization")  # Or should this be "other"?

    def test_classify25(self):
        cls = classify_desc("kälbə")
        self.assertEqual(cls, "romanization")

    def test_classify26(self):
        cls = classify_desc("kalb")
        self.assertEqual(cls, "romanization")

    def test_classify27(self):
        cls = classify_desc("čalb")
        self.assertEqual(cls, "romanization")

    def test_classify28(self):
        cls = classify_desc("al-wilāyātu l-muttaḥida")
        self.assertEqual(cls, "romanization")

    def test_classify29(self):
        cls = classify_desc("Spolúčeni Štáty")
        self.assertEqual(cls, "romanization")

    def test_classify30(self):
        cls = classify_desc("Spolúčeni Štáty")
        self.assertEqual(cls, "romanization")

    def test_classify31(self):
        cls = classify_desc("ZŠA")
        self.assertEqual(cls, "romanization")

    def test_classify32(self):
        cls = classify_desc("sà-hà-rát-à-mee-rí-gaa")
        self.assertEqual(cls, "romanization")

    def test_classify33(self):
        cls = classify_desc("saṃyuktarājyāni")
        self.assertEqual(cls, "romanization")

    def test_classify34(self):
        cls = classify_desc("ʼā mē li kā")
        self.assertEqual(cls, "romanization")

    def test_classify35(self):
        cls = classify_desc("Mihapjungguk")
        self.assertEqual(cls, "romanization")

    def test_classify36(self):
        cls = classify_desc("Amerika Gasshūkoku")
        self.assertEqual(cls, "romanization")

    def test_classify37(self):
        cls = classify_desc("artsot ha-brit")
        self.assertEqual(cls, "romanization")

    def test_classify38(self):
        cls = classify_desc("šeertebuli šṭaṭebi")
        self.assertEqual(cls, "romanization")

    def test_classify39(self):
        cls = classify_desc("zạn'")
        self.assertEqual(cls, "romanization")

    def test_classify40(self):
        cls = classify_desc("ʾakādīmiyy")
        self.assertEqual(cls, "romanization")

    def test_classify41(self):
        cls = classify_desc("xuéshù de")
        self.assertEqual(cls, "romanization")

    def test_classify42(self):
        cls = classify_desc("akadimaïkós")
        self.assertEqual(cls, "romanization")

    def test_classify43(self):
        cls = classify_desc("jāmiʿiyy")
        self.assertEqual(cls, "romanization")

    def test_classify44(self):
        cls = classify_desc("nák-sʉ̀k-sǎa")
        self.assertEqual(cls, "romanization")

    def test_classify45(self):
        cls = classify_desc("ʾustaḏ")
        self.assertEqual(cls, "romanization")

    def test_classify46(self):
        cls = classify_desc("faat³ long⁴ si⁶")
        self.assertEqual(cls, "romanization")

    def test_classify47(self):
        cls = classify_desc("arbitraryascii junk testoonotenglish")
        self.assertEqual(cls, "romanization")

    def test_classify48(self):
        cls = classify_desc("中華文明")
        self.assertEqual(cls, "other")

    def test_classify48b(self):
        cls = classify_desc("중국문명")
        self.assertEqual(cls, "other")

    def test_classify49(self):
        cls = classify_desc("ចិន")
        self.assertEqual(cls, "other")

    def test_classify50(self):
        cls = classify_desc("Кина")
        self.assertEqual(cls, "other")

    def test_classify51(self):
        cls = classify_desc("چین‎")
        self.assertEqual(cls, "other")

    def test_classify52(self):
        cls = classify_desc("华夏")
        self.assertEqual(cls, "other")

    def test_classify53(self):
        cls = classify_desc("चीन")
        self.assertEqual(cls, "other")

    def test_classify54(self):
        cls = classify_desc("中华文明")
        self.assertEqual(cls, "other")

    def test_classify55(self):
        cls = classify_desc("中國")
        self.assertEqual(cls, "other")

    def test_classify56(self):
        cls = classify_desc("ᱪᱤᱱ")
        self.assertEqual(cls, "other")

    def test_classify57(self):
        cls = classify_desc("ちゅうごく")
        self.assertEqual(cls, "other")

    def test_classify58(self):
        cls = classify_desc("中国")
        self.assertEqual(cls, "other")

    def test_classify59(self):
        cls = classify_desc("Κίνα")
        self.assertEqual(cls, "other")

    def test_classify60(self):
        cls = classify_desc("ჩინეთი")
        self.assertEqual(cls, "other")

    def test_classify61(self):
        cls = classify_desc("ސީނުކަރަ‎")
        self.assertEqual(cls, "other")

    def test_classify62(self):
        cls = classify_desc("རྒྱ་ནག")
        self.assertEqual(cls, "other")

    def test_classify63(self):
        cls = classify_desc("1")
        self.assertEqual(cls, "other")

    def test_classify64(self):
        cls = classify_desc("-")
        self.assertEqual(cls, "other")

    def test_classify65(self):
        cls = classify_desc("nabórnyj disk")
        self.assertEqual(cls, "romanization")

    def test_classify66(self):
        cls = classify_desc("choko chippu")
        self.assertEqual(cls, "romanization")

    def test_classify67(self):
        cls = classify_desc("chika tankō")
        self.assertEqual(cls, "romanization")

    def test_classify68(self):
        cls = classify_desc("Kongo")
        self.assertEqual(cls, "romanization")

    def test_classify69(self):
        cls = classify_desc("band karnā")
        self.assertEqual(cls, "romanization")

    def test_classify70(self):
        cls = classify_desc("hindu kuś")
        self.assertEqual(cls, "romanization")

    def test_classify71(self):
        cls = classify_desc("film waṯāʾiqiyy")
        self.assertEqual(cls, "romanization")

    def test_classify72(self):
        cls = classify_desc("bārid ad-dam")
        self.assertEqual(cls, "romanization")

    def test_classify73(self):
        # This really tests that disabling unknown starts works in classify_desc
        cls = classify_desc("symbol, for boron")
        self.assertEqual(cls, "tags")

    def test_classify74(self):
        # This really tests that disabling unknown starts works in classify_desc
        cls = classify_desc("symbol, for boron", no_unknown_starts=True)
        self.assertEqual(cls, "english")

    def test_classify75(self):
        # This really tests that disabling unknown starts works in classify_desc
        cls = classify_desc("7 a.m.", no_unknown_starts=True)
        self.assertEqual(cls, "english")

    def test_classify76(self):
        # This really tests that disabling unknown starts works in classify_desc
        cls = classify_desc("11 PM", no_unknown_starts=True)
        self.assertEqual(cls, "english")

    def test_classify77(self):
        # This really tests that disabling unknown starts works in classify_desc
        cls = classify_desc("11 to 19", no_unknown_starts=True)
        self.assertEqual(cls, "english")

    def test_classify78(self):
        cls = classify_desc("The cat goes \"meow\".")
        self.assertEqual(cls, "english")

    def test_classify79(self):
        cls = classify_desc('merely announcing that the elimination of news '
                            'programming [on tv channel TQS] will allow it to '
                            'focus on "the production of quality entertainment '
                            'and cultural programming"')
        self.assertEqual(cls, "english")

    def test_classify80(self):
        cls = classify_desc("I was living with him.")
        self.assertEqual(cls, "english")

    def test_classify81(self):
        cls = classify_desc("J'habitais avec lui.")
        self.assertEqual(cls, "romanization")

    def test_classify82(self):
        cls = classify_desc("Police resort to DNA analysis in order to "
                            "identify criminals.")
        self.assertEqual(cls, "english")

    def test_classify83(self):
        cls = classify_desc('"She will not be there tomorrow." ―"Oh, too bad, '
                            'it\'s not important, we\'ll go on without her."')
        self.assertEqual(cls, "english")

    def test_classify84(self):
        cls = classify_desc('Hardcore pictures.')
        self.assertEqual(cls, "english")

    def test_classify85(self):
        cls = classify_desc('denʹgám')
        self.assertEqual(cls, "romanization")

    def test_classify86(self):
        cls = classify_desc('dénʹgam')
        self.assertEqual(cls, "romanization")

    def test_classify87(self):
        cls = classify_desc('proiznosív')
        self.assertEqual(cls, "romanization")

    def test_classify88(self):
        cls = classify_desc('proiznosívši')
        self.assertEqual(cls, "romanization")

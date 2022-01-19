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

    def test_arabic_noun1(self):
        ret = self.xinfl("دمقس", "Arabic", "noun", "Declension", """
<div class="NavFrame">
<div class="NavHead">Declension of noun <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْس]]</span>&lrm; (<span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqs</span>)</div>
<div class="NavContent">

{| class="inflection-table" style="border-width%3A+1px%3B+border-collapse%3A+collapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25%3B"

|-

! style="background%3A+%23CDCDCD%3B" rowspan="2" | Singular


! style="background%3A+%23CDCDCD%3B" colspan="3" | basic singular triptote


|-

! style="background%3A+%23CDCDCD%3B" | Indefinite


! style="background%3A+%23CDCDCD%3B" | Definite


! style="background%3A+%23CDCDCD%3B" | Construct


|-

! style="background%3A+%23EFEFEF%3B" | Informal


| <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْس]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqs</span>


| <span class="Arab" lang="ar">[[الدمقس#Arabic|الدِّمَقْس]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">ad-dimaqs</span>


| <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْس]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqs</span>


|-

! style="background%3A+%23EFEFEF%3B" | Nominative


| <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْسٌ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqsun</span>


| <span class="Arab" lang="ar">[[الدمقس#Arabic|الدِّمَقْسُ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">ad-dimaqsu</span>


| <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْسُ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqsu</span>


|-

! style="background%3A+%23EFEFEF%3B" | Accusative


| <span class="Arab" lang="ar">[[دمقسا#Arabic|دِمَقْسًا]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqsan</span>


| <span class="Arab" lang="ar">[[الدمقس#Arabic|الدِّمَقْسَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">ad-dimaqsa</span>


| <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْسَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqsa</span>


|-

! style="background%3A+%23EFEFEF%3B" | Genitive


| <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْسٍ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqsin</span>


| <span class="Arab" lang="ar">[[الدمقس#Arabic|الدِّمَقْسِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">ad-dimaqsi</span>


| <span class="Arab" lang="ar">[[دمقس#Arabic|دِمَقْسِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">dimaqsi</span>


|}

</div>
</div>[[Category:Arabic nouns with basic triptote singular|دمقس]]
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
                "form": "دِمَقْس‎",
                "roman": "dimaqs",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "informal",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الدِّمَقْس‎",
                "roman": "ad-dimaqs",
                "source": "Declension",
                "tags": [
                  "definite",
                  "informal",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "دِمَقْس‎",
                "roman": "dimaqs",
                "source": "Declension",
                "tags": [
                  "construct",
                  "informal",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "دِمَقْسٌ‎",
                "roman": "dimaqsun",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "nominative",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الدِّمَقْسُ‎",
                "roman": "ad-dimaqsu",
                "source": "Declension",
                "tags": [
                  "definite",
                  "nominative",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "دِمَقْسُ‎",
                "roman": "dimaqsu",
                "source": "Declension",
                "tags": [
                  "construct",
                  "nominative",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "دِمَقْسًا‎",
                "roman": "dimaqsan",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "indefinite",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الدِّمَقْسَ‎",
                "roman": "ad-dimaqsa",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "دِمَقْسَ‎",
                "roman": "dimaqsa",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "construct",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "دِمَقْسٍ‎",
                "roman": "dimaqsin",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الدِّمَقْسِ‎",
                "roman": "ad-dimaqsi",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "دِمَقْسِ‎",
                "roman": "dimaqsi",
                "source": "Declension",
                "tags": [
                  "construct",
                  "genitive",
                  "singular",
                  "triptote"
                ]
              },
            ],
        }
        self.assertEqual(expected, ret)

    def test_arabic_verb1(self):
        ret = self.xinfl("أبلع", "Arabic", "verb", "Conjugation", """
<div class="NavFrame+ar-conj">
<div class="NavHead" style="height%3A2.5em">Conjugation of <div style="display%3A+inline-block"><b lang="ar" class="Arab">أَبْلَعَ</b></div> (form-IV sound)</div>
<div class="NavContent">


{| class="inflection-table"

|-

! colspan="6" class="nonfinite-header" | verbal noun<br><span class="Arab" lang="ar">الْمَصْدَر</span>


| colspan="7" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[إبلاع#Arabic|إِبْلَاع]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾiblāʿ</span></span>


|-

! colspan="6" class="nonfinite-header" | active participle<br><span class="Arab" lang="ar">اِسْم الْفَاعِل</span>


| colspan="7" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[مبلع#Arabic|مُبْلِع]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">mubliʿ</span></span>


|-

! colspan="6" class="nonfinite-header" | passive participle<br><span class="Arab" lang="ar">اِسْم الْمَفْعُول</span>


| colspan="7" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[مبلع#Arabic|مُبْلَع]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">mublaʿ</span></span>


|-

! colspan="12" class="voice-header" | active voice<br><span class="Arab" lang="ar">الْفِعْل الْمَعْلُوم</span>


|-

! colspan="2" class="empty-header" |


! colspan="3" class="number-header" | singular<br><span class="Arab" lang="ar">الْمُفْرَد</span>


! rowspan="12" class="divider" |


! colspan="2" class="number-header" | dual<br><span class="Arab" lang="ar">الْمُثَنَّى</span>


! rowspan="12" class="divider" |


! colspan="3" class="number-header" | plural<br><span class="Arab" lang="ar">الْجَمْع</span>


|-

! colspan="2" class="empty-header" |


! class="person-header" | 1<sup>st</sup> person<br><span class="Arab" lang="ar">الْمُتَكَلِّم</span>


! class="person-header" | 2<sup>nd</sup> person<br><span class="Arab" lang="ar">الْمُخَاطَب</span>


! class="person-header" | 3<sup>rd</sup> person<br><span class="Arab" lang="ar">الْغَائِب</span>


! class="person-header" | 2<sup>nd</sup> person<br><span class="Arab" lang="ar">الْمُخَاطَب</span>


! class="person-header" | 3<sup>rd</sup> person<br><span class="Arab" lang="ar">الْغَائِب</span>


! class="person-header" | 1<sup>st</sup> person<br><span class="Arab" lang="ar">الْمُتَكَلِّم</span>


! class="person-header" | 2<sup>nd</sup> person<br><span class="Arab" lang="ar">الْمُخَاطَب</span>


! class="person-header" | 3<sup>rd</sup> person<br><span class="Arab" lang="ar">الْغَائِب</span>


|-

! rowspan="2" class="tam-header" | past (perfect) indicative<br><span class="Arab" lang="ar">الْمَاضِي</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أَبْلَعْتُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿtu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أَبْلَعْتَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿta</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أَبْلَعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿa</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتما#Arabic|أَبْلَعْتُمَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿtumā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعا#Arabic|أَبْلَعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿā</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعنا#Arabic|أَبْلَعْنَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿnā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتم#Arabic|أَبْلَعْتُمْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿtum</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعوا#Arabic|أَبْلَعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿū</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أَبْلَعْتِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿti</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أَبْلَعَتْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿat</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتا#Arabic|أَبْلَعَتَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿatā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتن#Arabic|أَبْلَعْتُنَّ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿtunna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعن#Arabic|أَبْلَعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾablaʿna</span></span>


|-

! rowspan="2" class="tam-header" | non-past (imperfect) indicative<br><span class="Arab" lang="ar">الْمُضَارِع</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أُبْلِعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلِعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلع#Arabic|يُبْلِعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿu</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعان#Arabic|تُبْلِعَانِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿāni</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعان#Arabic|يُبْلِعَانِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿāni</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[نبلع#Arabic|نُبْلِعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">nubliʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعون#Arabic|تُبْلِعُونَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿūna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعون#Arabic|يُبْلِعُونَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿūna</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعين#Arabic|تُبْلِعِينَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿīna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلِعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعان#Arabic|تُبْلِعَانِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿāni</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعن#Arabic|تُبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعن#Arabic|يُبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿna</span></span>


|-

! rowspan="2" class="tam-header" | subjunctive<br><span class="Arab" lang="ar">الْمُضَارِع الْمَنْصُوب</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أُبْلِعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلِعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلع#Arabic|يُبْلِعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿa</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعا#Arabic|يُبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿā</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[نبلع#Arabic|نُبْلِعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">nubliʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعوا#Arabic|تُبْلِعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿū</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعوا#Arabic|يُبْلِعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿū</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعي#Arabic|تُبْلِعِي]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿī</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلِعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعن#Arabic|تُبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعن#Arabic|يُبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿna</span></span>


|-

! rowspan="2" class="tam-header" | jussive<br><span class="Arab" lang="ar">الْمُضَارِع الْمَجْزُوم</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أُبْلِعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلِعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلع#Arabic|يُبْلِعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿ</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعا#Arabic|يُبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿā</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[نبلع#Arabic|نُبْلِعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">nubliʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعوا#Arabic|تُبْلِعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿū</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعوا#Arabic|يُبْلِعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿū</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعي#Arabic|تُبْلِعِي]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿī</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلِعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعن#Arabic|تُبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tubliʿna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعن#Arabic|يُبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yubliʿna</span></span>


|-

! rowspan="2" class="tam-header" | imperative<br><span class="Arab" lang="ar">الْأَمْر</span>


! class="gender-header" | m


| rowspan="2" |


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أَبْلِعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾabliʿ</span></span>


| rowspan="2" |


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعا#Arabic|أَبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾabliʿā</span></span>


| rowspan="2" |


| rowspan="2" |


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعوا#Arabic|أَبْلِعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾabliʿū</span></span>


| rowspan="2" |


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعي#Arabic|أَبْلِعِي]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾabliʿī</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعن#Arabic|أَبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾabliʿna</span></span>


|-

! colspan="12" class="voice-header" | passive voice<br><span class="Arab" lang="ar">الْفِعْل الْمَجْهُول</span>


|-

| colspan="2" class="empty-header" |


! colspan="3" class="number-header" | singular<br><span class="Arab" lang="ar">الْمُفْرَد</span>


| rowspan="10" class="divider" |


! colspan="2" class="number-header" | dual<br><span class="Arab" lang="ar">الْمُثَنَّى</span>


| rowspan="10" class="divider" |


! colspan="3" class="number-header" | plural<br><span class="Arab" lang="ar">الْجَمْع</span>


|-

| colspan="2" class="empty-header" |


! class="person-header" | 1<sup>st</sup> person<br><span class="Arab" lang="ar">الْمُتَكَلِّم</span>


! class="person-header" | 2<sup>nd</sup> person<br><span class="Arab" lang="ar">الْمُخَاطَب</span>


! class="person-header" | 3<sup>rd</sup> person<br><span class="Arab" lang="ar">الْغَائِب</span>


! class="person-header" | 2<sup>nd</sup> person<br><span class="Arab" lang="ar">الْمُخَاطَب</span>


! class="person-header" | 3<sup>rd</sup> person<br><span class="Arab" lang="ar">الْغَائِب</span>


! class="person-header" | 1<sup>st</sup> person<br><span class="Arab" lang="ar">الْمُتَكَلِّم</span>


! class="person-header" | 2<sup>nd</sup> person<br><span class="Arab" lang="ar">الْمُخَاطَب</span>


! class="person-header" | 3<sup>rd</sup> person<br><span class="Arab" lang="ar">الْغَائِب</span>


|-

! rowspan="2" class="tam-header" | past (perfect) indicative<br><span class="Arab" lang="ar">الْمَاضِي</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أُبْلِعْتُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿtu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أُبْلِعْتَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿta</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أُبْلِعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿa</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتما#Arabic|أُبْلِعْتُمَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿtumā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعا#Arabic|أُبْلِعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿā</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعنا#Arabic|أُبْلِعْنَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿnā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتم#Arabic|أُبْلِعْتُمْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿtum</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعوا#Arabic|أُبْلِعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿū</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أُبْلِعْتِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿti</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعت#Arabic|أُبْلِعَتْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿat</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتا#Arabic|أُبْلِعَتَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿatā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعتن#Arabic|أُبْلِعْتُنَّ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿtunna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلعن#Arabic|أُبْلِعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾubliʿna</span></span>


|-

! rowspan="2" class="tam-header" | non-past (imperfect) indicative<br><span class="Arab" lang="ar">الْمُضَارِع</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أُبْلَعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾublaʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلَعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلع#Arabic|يُبْلَعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿu</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعان#Arabic|تُبْلَعَانِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿāni</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعان#Arabic|يُبْلَعَانِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿāni</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[نبلع#Arabic|نُبْلَعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">nublaʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعون#Arabic|تُبْلَعُونَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿūna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعون#Arabic|يُبْلَعُونَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿūna</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعين#Arabic|تُبْلَعِينَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿīna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلَعُ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿu</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعان#Arabic|تُبْلَعَانِ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿāni</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعن#Arabic|تُبْلَعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعن#Arabic|يُبْلَعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿna</span></span>


|-

! rowspan="2" class="tam-header" | subjunctive<br><span class="Arab" lang="ar">الْمُضَارِع الْمَنْصُوب</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أُبْلَعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾublaʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلَعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلع#Arabic|يُبْلَعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿa</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلَعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعا#Arabic|يُبْلَعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿā</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[نبلع#Arabic|نُبْلَعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">nublaʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعوا#Arabic|تُبْلَعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿū</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعوا#Arabic|يُبْلَعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿū</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعي#Arabic|تُبْلَعِي]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿī</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلَعَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿa</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلَعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعن#Arabic|تُبْلَعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعن#Arabic|يُبْلَعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿna</span></span>


|-

! rowspan="2" class="tam-header" | jussive<br><span class="Arab" lang="ar">الْمُضَارِع الْمَجْزُوم</span>


! class="gender-header" | m


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[أبلع#Arabic|أُبْلَعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">ʾublaʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلَعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلع#Arabic|يُبْلَعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿ</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلَعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعا#Arabic|يُبْلَعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿā</span></span>


| rowspan="2" | <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[نبلع#Arabic|نُبْلَعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">nublaʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعوا#Arabic|تُبْلَعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿū</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعوا#Arabic|يُبْلَعُوا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿū</span></span>


|-

! class="gender-header" | f


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعي#Arabic|تُبْلَعِي]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿī</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلع#Arabic|تُبْلَعْ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿ</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعا#Arabic|تُبْلَعَا]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿā</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[تبلعن#Arabic|تُبْلَعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">tublaʿna</span></span>


| <div style="display%3A+inline-block"><span class="Arab" lang="ar">[[يبلعن#Arabic|يُبْلَعْنَ]]</span>&lrm;</div><br><span style="color%3A+%23888"><span lang="ar-Latn" class="tr+Latn">yublaʿna</span></span>


|}

</div>
</div><templatestyles src="Template%3Aar-conj%2Fstyle.css">[[Category:Arabic form-IV verbs|أبلع]][[Category:Arabic sound verbs by conjugation|أبلع]][[Category:Arabic sound form-IV verbs|أبلع]][[Category:Arabic sound verbs|أبلع]][[Category:Arabic verbs with full passive|أبلع]][[Category:Arabic transitive verbs|أبلع]]
""")
        expected = {
            "forms": [
              {
                "form": "",
                "source": "Conjugation",
                "tags": [
                  "table-tags"
                ]
              },
              {
                "form": "إِبْلَاع‎",
                "roman": "ʾiblāʿ",
                "source": "Conjugation",
                "tags": [
                  "noun-from-verb"
                ]
              },
              {
                "form": "مُبْلِع‎",
                "roman": "mubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "participle"
                ]
              },
              {
                "form": "مُبْلَع‎",
                "roman": "mublaʿ",
                "source": "Conjugation",
                "tags": [
                  "participle",
                  "passive"
                ]
              },
              {
                "form": "أَبْلَعْتُ‎",
                "roman": "ʾablaʿtu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "singular"
                ]
              },
              {
                "form": "أَبْلَعْتَ‎",
                "roman": "ʾablaʿta",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "أَبْلَعَ‎",
                "roman": "ʾablaʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "أَبْلَعْتُمَا‎",
                "roman": "ʾablaʿtumā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "second-person"
                ]
              },
              {
                "form": "أَبْلَعَا‎",
                "roman": "ʾablaʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "third-person"
                ]
              },
              {
                "form": "أَبْلَعْنَا‎",
                "roman": "ʾablaʿnā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "plural"
                ]
              },
              {
                "form": "أَبْلَعْتُمْ‎",
                "roman": "ʾablaʿtum",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "أَبْلَعُوا‎",
                "roman": "ʾablaʿū",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "indicative",
                  "masculine",
                  "past",
                  "perfective",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أَبْلَعْتُ‎",
                "roman": "ʾablaʿtu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "indicative",
                  "past",
                  "perfective",
                  "singular"
                ]
              },
              {
                "form": "أَبْلَعْتِ‎",
                "roman": "ʾablaʿti",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "indicative",
                  "past",
                  "perfective",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "أَبْلَعَتْ‎",
                "roman": "ʾablaʿat",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "indicative",
                  "past",
                  "perfective",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "أَبْلَعْتُمَا‎",
                "roman": "ʾablaʿtumā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "indicative",
                  "past",
                  "perfective",
                  "second-person"
                ]
              },
              {
                "form": "أَبْلَعَتَا‎",
                "roman": "ʾablaʿatā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "indicative",
                  "past",
                  "perfective",
                  "third-person"
                ]
              },
              {
                "form": "أَبْلَعْنَا‎",
                "roman": "ʾablaʿnā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "indicative",
                  "past",
                  "perfective",
                  "plural"
                ]
              },
              {
                "form": "أَبْلَعْتُنَّ‎",
                "roman": "ʾablaʿtunna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "indicative",
                  "past",
                  "perfective",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "أَبْلَعْنَ‎",
                "roman": "ʾablaʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "indicative",
                  "past",
                  "perfective",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعُ‎",
                "roman": "ʾubliʿu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "singular"
                ]
              },
              {
                "form": "تُبْلِعُ‎",
                "roman": "tubliʿu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "يُبْلِعُ‎",
                "roman": "yubliʿu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلِعَانِ‎",
                "roman": "tubliʿāni",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلِعَانِ‎",
                "roman": "yubliʿāni",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلِعُ‎",
                "roman": "nubliʿu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "plural"
                ]
              },
              {
                "form": "تُبْلِعُونَ‎",
                "roman": "tubliʿūna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلِعُونَ‎",
                "roman": "yubliʿūna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعُ‎",
                "roman": "ʾubliʿu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "singular"
                ]
              },
              {
                "form": "تُبْلِعِينَ‎",
                "roman": "tubliʿīna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "تُبْلِعُ‎",
                "roman": "tubliʿu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلِعَانِ‎",
                "roman": "tubliʿāni",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "second-person"
                ]
              },
              {
                "form": "تُبْلِعَانِ‎",
                "roman": "tubliʿāni",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلِعُ‎",
                "roman": "nubliʿu",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "plural"
                ]
              },
              {
                "form": "تُبْلِعْنَ‎",
                "roman": "tubliʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلِعْنَ‎",
                "roman": "yubliʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعَ‎",
                "roman": "ʾubliʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "masculine",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلِعَ‎",
                "roman": "tubliʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "masculine",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلِعَ‎",
                "roman": "yubliʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "masculine",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلِعَا‎",
                "roman": "tubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "masculine",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلِعَا‎",
                "roman": "yubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "masculine",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلِعَ‎",
                "roman": "nubliʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "masculine",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلِعُوا‎",
                "roman": "tubliʿū",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "masculine",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلِعُوا‎",
                "roman": "yubliʿū",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "masculine",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعَ‎",
                "roman": "ʾubliʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلِعِي‎",
                "roman": "tubliʿī",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلِعَ‎",
                "roman": "tubliʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلِعَا‎",
                "roman": "tubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلِعَا‎",
                "roman": "tubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلِعَ‎",
                "roman": "nubliʿa",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلِعْنَ‎",
                "roman": "tubliʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلِعْنَ‎",
                "roman": "yubliʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعْ‎",
                "roman": "ʾubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "jussive",
                  "masculine",
                  "singular"
                ]
              },
              {
                "form": "تُبْلِعْ‎",
                "roman": "tubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "jussive",
                  "masculine",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "يُبْلِعْ‎",
                "roman": "yubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "jussive",
                  "masculine",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلِعَا‎",
                "roman": "tubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "jussive",
                  "masculine",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلِعَا‎",
                "roman": "yubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "jussive",
                  "masculine",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلِعْ‎",
                "roman": "nubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "first-person",
                  "jussive",
                  "masculine",
                  "plural"
                ]
              },
              {
                "form": "تُبْلِعُوا‎",
                "roman": "tubliʿū",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "jussive",
                  "masculine",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلِعُوا‎",
                "roman": "yubliʿū",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "jussive",
                  "masculine",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعْ‎",
                "roman": "ʾubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "jussive",
                  "singular"
                ]
              },
              {
                "form": "تُبْلِعِي‎",
                "roman": "tubliʿī",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "jussive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "تُبْلِعْ‎",
                "roman": "tubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "jussive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلِعَا‎",
                "roman": "tubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "jussive",
                  "second-person"
                ]
              },
              {
                "form": "تُبْلِعَا‎",
                "roman": "tubliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "jussive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلِعْ‎",
                "roman": "nubliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "first-person",
                  "jussive",
                  "plural"
                ]
              },
              {
                "form": "تُبْلِعْنَ‎",
                "roman": "tubliʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "jussive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلِعْنَ‎",
                "roman": "yubliʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "jussive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أَبْلِعْ‎",
                "roman": "ʾabliʿ",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperative",
                  "masculine",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "أَبْلِعَا‎",
                "roman": "ʾabliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "imperative",
                  "masculine",
                  "second-person"
                ]
              },
              {
                "form": "أَبْلِعُوا‎",
                "roman": "ʾabliʿū",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "imperative",
                  "masculine",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "أَبْلِعِي‎",
                "roman": "ʾabliʿī",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "imperative",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "أَبْلِعَا‎",
                "roman": "ʾabliʿā",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "dual",
                  "feminine",
                  "imperative",
                  "second-person"
                ]
              },
              {
                "form": "أَبْلِعْنَ‎",
                "roman": "ʾabliʿna",
                "source": "Conjugation",
                "tags": [
                  "active",
                  "feminine",
                  "imperative",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "أُبْلِعْتُ‎",
                "roman": "ʾubliʿtu",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "singular"
                ]
              },
              {
                "form": "أُبْلِعْتَ‎",
                "roman": "ʾubliʿta",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "أُبْلِعَ‎",
                "roman": "ʾubliʿa",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعْتُمَا‎",
                "roman": "ʾubliʿtumā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "second-person"
                ]
              },
              {
                "form": "أُبْلِعَا‎",
                "roman": "ʾubliʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعْنَا‎",
                "roman": "ʾubliʿnā",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "plural"
                ]
              },
              {
                "form": "أُبْلِعْتُمْ‎",
                "roman": "ʾubliʿtum",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "أُبْلِعُوا‎",
                "roman": "ʾubliʿū",
                "source": "Conjugation",
                "tags": [
                  "indicative",
                  "masculine",
                  "passive",
                  "past",
                  "perfective",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعْتُ‎",
                "roman": "ʾubliʿtu",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "singular"
                ]
              },
              {
                "form": "أُبْلِعْتِ‎",
                "roman": "ʾubliʿti",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "أُبْلِعَتْ‎",
                "roman": "ʾubliʿat",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعْتُمَا‎",
                "roman": "ʾubliʿtumā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "second-person"
                ]
              },
              {
                "form": "أُبْلِعَتَا‎",
                "roman": "ʾubliʿatā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلِعْنَا‎",
                "roman": "ʾubliʿnā",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "plural"
                ]
              },
              {
                "form": "أُبْلِعْتُنَّ‎",
                "roman": "ʾubliʿtunna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "أُبْلِعْنَ‎",
                "roman": "ʾubliʿna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "indicative",
                  "passive",
                  "past",
                  "perfective",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلَعُ‎",
                "roman": "ʾublaʿu",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "تُبْلَعُ‎",
                "roman": "tublaʿu",
                "source": "Conjugation",
                "tags": [
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "يُبْلَعُ‎",
                "roman": "yublaʿu",
                "source": "Conjugation",
                "tags": [
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلَعَانِ‎",
                "roman": "tublaʿāni",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلَعَانِ‎",
                "roman": "yublaʿāni",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلَعُ‎",
                "roman": "nublaʿu",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "plural"
                ]
              },
              {
                "form": "تُبْلَعُونَ‎",
                "roman": "tublaʿūna",
                "source": "Conjugation",
                "tags": [
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلَعُونَ‎",
                "roman": "yublaʿūna",
                "source": "Conjugation",
                "tags": [
                  "imperfective",
                  "indicative",
                  "masculine",
                  "non-past",
                  "passive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلَعُ‎",
                "roman": "ʾublaʿu",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "تُبْلَعِينَ‎",
                "roman": "tublaʿīna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "تُبْلَعُ‎",
                "roman": "tublaʿu",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلَعَانِ‎",
                "roman": "tublaʿāni",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "second-person"
                ]
              },
              {
                "form": "تُبْلَعَانِ‎",
                "roman": "tublaʿāni",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلَعُ‎",
                "roman": "nublaʿu",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "plural"
                ]
              },
              {
                "form": "تُبْلَعْنَ‎",
                "roman": "tublaʿna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلَعْنَ‎",
                "roman": "yublaʿna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "imperfective",
                  "indicative",
                  "non-past",
                  "passive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلَعَ‎",
                "roman": "ʾublaʿa",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "masculine",
                  "passive",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلَعَ‎",
                "roman": "tublaʿa",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "passive",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلَعَ‎",
                "roman": "yublaʿa",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "passive",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلَعَا‎",
                "roman": "tublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "masculine",
                  "passive",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلَعَا‎",
                "roman": "yublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "masculine",
                  "passive",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلَعَ‎",
                "roman": "nublaʿa",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "masculine",
                  "passive",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلَعُوا‎",
                "roman": "tublaʿū",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "passive",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلَعُوا‎",
                "roman": "yublaʿū",
                "source": "Conjugation",
                "tags": [
                  "masculine",
                  "passive",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلَعَ‎",
                "roman": "ʾublaʿa",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "passive",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلَعِي‎",
                "roman": "tublaʿī",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "passive",
                  "second-person",
                  "singular",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلَعَ‎",
                "roman": "tublaʿa",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "passive",
                  "singular",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلَعَا‎",
                "roman": "tublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "passive",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلَعَا‎",
                "roman": "tublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "passive",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلَعَ‎",
                "roman": "nublaʿa",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "passive",
                  "plural",
                  "subjunctive"
                ]
              },
              {
                "form": "تُبْلَعْنَ‎",
                "roman": "tublaʿna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "passive",
                  "plural",
                  "second-person",
                  "subjunctive"
                ]
              },
              {
                "form": "يُبْلَعْنَ‎",
                "roman": "yublaʿna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "passive",
                  "plural",
                  "subjunctive",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلَعْ‎",
                "roman": "ʾublaʿ",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "jussive",
                  "masculine",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "تُبْلَعْ‎",
                "roman": "tublaʿ",
                "source": "Conjugation",
                "tags": [
                  "jussive",
                  "masculine",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "يُبْلَعْ‎",
                "roman": "yublaʿ",
                "source": "Conjugation",
                "tags": [
                  "jussive",
                  "masculine",
                  "passive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلَعَا‎",
                "roman": "tublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "jussive",
                  "masculine",
                  "passive",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلَعَا‎",
                "roman": "yublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "jussive",
                  "masculine",
                  "passive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلَعْ‎",
                "roman": "nublaʿ",
                "source": "Conjugation",
                "tags": [
                  "first-person",
                  "jussive",
                  "masculine",
                  "passive",
                  "plural"
                ]
              },
              {
                "form": "تُبْلَعُوا‎",
                "roman": "tublaʿū",
                "source": "Conjugation",
                "tags": [
                  "jussive",
                  "masculine",
                  "passive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلَعُوا‎",
                "roman": "yublaʿū",
                "source": "Conjugation",
                "tags": [
                  "jussive",
                  "masculine",
                  "passive",
                  "plural",
                  "third-person"
                ]
              },
              {
                "form": "أُبْلَعْ‎",
                "roman": "ʾublaʿ",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "jussive",
                  "passive",
                  "singular"
                ]
              },
              {
                "form": "تُبْلَعِي‎",
                "roman": "tublaʿī",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "jussive",
                  "passive",
                  "second-person",
                  "singular"
                ]
              },
              {
                "form": "تُبْلَعْ‎",
                "roman": "tublaʿ",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "jussive",
                  "passive",
                  "singular",
                  "third-person"
                ]
              },
              {
                "form": "تُبْلَعَا‎",
                "roman": "tublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "jussive",
                  "passive",
                  "second-person"
                ]
              },
              {
                "form": "تُبْلَعَا‎",
                "roman": "tublaʿā",
                "source": "Conjugation",
                "tags": [
                  "dual",
                  "feminine",
                  "jussive",
                  "passive",
                  "third-person"
                ]
              },
              {
                "form": "نُبْلَعْ‎",
                "roman": "nublaʿ",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "first-person",
                  "jussive",
                  "passive",
                  "plural"
                ]
              },
              {
                "form": "تُبْلَعْنَ‎",
                "roman": "tublaʿna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "jussive",
                  "passive",
                  "plural",
                  "second-person"
                ]
              },
              {
                "form": "يُبْلَعْنَ‎",
                "roman": "yublaʿna",
                "source": "Conjugation",
                "tags": [
                  "feminine",
                  "jussive",
                  "passive",
                  "plural",
                  "third-person"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

    def test_arabic_adj1(self):
        ret = self.xinfl("جاذب", "Arabic", "adj", "Declension", """
<div class="NavFrame">
<div class="NavHead">Declension of adjective <span class="Arab" lang="ar">[[جاذب#Arabic|جَاذِب]]</span>&lrm; (<span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏib</span>)</div>
<div class="NavContent">

{| class="inflection-table" style="border-width%3A+1px%3B+border-collapse%3A+collapse%3B+background%3A%23F9F9F9%3B+text-align%3Acenter%3B+width%3A100%25%3B"

|-

! style="background%3A+%23CDCDCD%3B" rowspan="3" | Singular


! style="background%3A+%23CDCDCD%3B" colspan="2" | Masculine


! style="background%3A+%23CDCDCD%3B" colspan="2" | Feminine


|-

! style="background%3A+%23CDCDCD%3B" colspan="2" | basic singular triptote


! style="background%3A+%23CDCDCD%3B" colspan="2" | singular triptote in <i class="Arab+mention" lang="ar">ـَة</i> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="ar-Latn" class="mention-tr+tr+Latn">-a</span><span class="mention-gloss-paren+annotation-paren">)</span>


|-

! style="background%3A+%23CDCDCD%3B" | Indefinite


! style="background%3A+%23CDCDCD%3B" | Definite


! style="background%3A+%23CDCDCD%3B" | Indefinite


! style="background%3A+%23CDCDCD%3B" | Definite


|-

! style="background%3A+%23EFEFEF%3B" | Informal


| <span class="Arab" lang="ar">[[جاذب#Arabic|جَاذِب]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏib</span>


| <span class="Arab" lang="ar">[[الجاذب#Arabic|الْجَاذِب]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏib</span>


| <span class="Arab" lang="ar">[[جاذبة#Arabic|جَاذِبَة]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏiba</span>


| <span class="Arab" lang="ar">[[الجاذبة#Arabic|الْجَاذِبَة]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏiba</span>


|-

! style="background%3A+%23EFEFEF%3B" | Nominative


| <span class="Arab" lang="ar">[[جاذب#Arabic|جَاذِبٌ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibun</span>


| <span class="Arab" lang="ar">[[الجاذب#Arabic|الْجَاذِبُ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibu</span>


| <span class="Arab" lang="ar">[[جاذبة#Arabic|جَاذِبَةٌ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibatun</span>


| <span class="Arab" lang="ar">[[الجاذبة#Arabic|الْجَاذِبَةُ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibatu</span>


|-

! style="background%3A+%23EFEFEF%3B" | Accusative


| <span class="Arab" lang="ar">[[جاذبا#Arabic|جَاذِبًا]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏiban</span>


| <span class="Arab" lang="ar">[[الجاذب#Arabic|الْجَاذِبَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏiba</span>


| <span class="Arab" lang="ar">[[جاذبة#Arabic|جَاذِبَةً]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibatan</span>


| <span class="Arab" lang="ar">[[الجاذبة#Arabic|الْجَاذِبَةَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibata</span>


|-

! style="background%3A+%23EFEFEF%3B" | Genitive


| <span class="Arab" lang="ar">[[جاذب#Arabic|جَاذِبٍ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibin</span>


| <span class="Arab" lang="ar">[[الجاذب#Arabic|الْجَاذِبِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibi</span>


| <span class="Arab" lang="ar">[[جاذبة#Arabic|جَاذِبَةٍ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibatin</span>


| <span class="Arab" lang="ar">[[الجاذبة#Arabic|الْجَاذِبَةِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibati</span>


|-

! style="background%3A+%23CDCDCD%3B" rowspan="2" | Dual


! style="background%3A+%23CDCDCD%3B" colspan="2" | Masculine


! style="background%3A+%23CDCDCD%3B" colspan="2" | Feminine


|-

! style="background%3A+%23CDCDCD%3B" | Indefinite


! style="background%3A+%23CDCDCD%3B" | Definite


! style="background%3A+%23CDCDCD%3B" | Indefinite


! style="background%3A+%23CDCDCD%3B" | Definite


|-

! style="background%3A+%23EFEFEF%3B" | Informal


| <span class="Arab" lang="ar">[[جاذبين#Arabic|جَاذِبَيْن]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibayn</span>


| <span class="Arab" lang="ar">[[الجاذبين#Arabic|الْجَاذِبَيْن]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibayn</span>


| <span class="Arab" lang="ar">[[جاذبتين#Arabic|جَاذِبَتَيْن]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibatayn</span>


| <span class="Arab" lang="ar">[[الجاذبتين#Arabic|الْجَاذِبَتَيْن]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibatayn</span>


|-

! style="background%3A+%23EFEFEF%3B" | Nominative


| <span class="Arab" lang="ar">[[جاذبان#Arabic|جَاذِبَانِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibāni</span>


| <span class="Arab" lang="ar">[[الجاذبان#Arabic|الْجَاذِبَانِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibāni</span>


| <span class="Arab" lang="ar">[[جاذبتان#Arabic|جَاذِبَتَانِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibatāni</span>


| <span class="Arab" lang="ar">[[الجاذبتان#Arabic|الْجَاذِبَتَانِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibatāni</span>


|-

! style="background%3A+%23EFEFEF%3B" | Accusative


| <span class="Arab" lang="ar">[[جاذبين#Arabic|جَاذِبَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibayni</span>


| <span class="Arab" lang="ar">[[الجاذبين#Arabic|الْجَاذِبَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibayni</span>


| <span class="Arab" lang="ar">[[جاذبتين#Arabic|جَاذِبَتَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibatayni</span>


| <span class="Arab" lang="ar">[[الجاذبتين#Arabic|الْجَاذِبَتَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibatayni</span>


|-

! style="background%3A+%23EFEFEF%3B" | Genitive


| <span class="Arab" lang="ar">[[جاذبين#Arabic|جَاذِبَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibayni</span>


| <span class="Arab" lang="ar">[[الجاذبين#Arabic|الْجَاذِبَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibayni</span>


| <span class="Arab" lang="ar">[[جاذبتين#Arabic|جَاذِبَتَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibatayni</span>


| <span class="Arab" lang="ar">[[الجاذبتين#Arabic|الْجَاذِبَتَيْنِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibatayni</span>


|-

! style="background%3A+%23CDCDCD%3B" rowspan="3" | Plural


! style="background%3A+%23CDCDCD%3B" colspan="2" | Masculine


! style="background%3A+%23CDCDCD%3B" colspan="2" | Feminine


|-

! style="background%3A+%23CDCDCD%3B" colspan="2" | sound masculine plural


! style="background%3A+%23CDCDCD%3B" colspan="2" | sound feminine plural‎; basic broken plural diptote


|-

! style="background%3A+%23CDCDCD%3B" | Indefinite


! style="background%3A+%23CDCDCD%3B" | Definite


! style="background%3A+%23CDCDCD%3B" | Indefinite


! style="background%3A+%23CDCDCD%3B" | Definite


|-

! style="background%3A+%23EFEFEF%3B" | Informal


| <span class="Arab" lang="ar">[[جاذبين#Arabic|جَاذِبِين]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibīn</span>


| <span class="Arab" lang="ar">[[الجاذبين#Arabic|الْجَاذِبِين]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibīn</span>


| <span class="Arab" lang="ar">[[جاذبات#Arabic|جَاذِبَات]]</span>&lrm;‎; <span class="Arab" lang="ar">[[جواذب#Arabic|جَوَاذِب]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibāt</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jawāḏib</span>


| <span class="Arab" lang="ar">[[الجاذبات#Arabic|الْجَاذِبَات]]</span>&lrm;‎; <span class="Arab" lang="ar">[[الجواذب#Arabic|الْجَوَاذِب]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibāt</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jawāḏib</span>


|-

! style="background%3A+%23EFEFEF%3B" | Nominative


| <span class="Arab" lang="ar">[[جاذبون#Arabic|جَاذِبُونَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibūna</span>


| <span class="Arab" lang="ar">[[الجاذبون#Arabic|الْجَاذِبُونَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibūna</span>


| <span class="Arab" lang="ar">[[جاذبات#Arabic|جَاذِبَاتٌ]]</span>&lrm;‎; <span class="Arab" lang="ar">[[جواذب#Arabic|جَوَاذِبُ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibātun</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jawāḏibu</span>


| <span class="Arab" lang="ar">[[الجاذبات#Arabic|الْجَاذِبَاتُ]]</span>&lrm;‎; <span class="Arab" lang="ar">[[الجواذب#Arabic|الْجَوَاذِبُ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibātu</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jawāḏibu</span>


|-

! style="background%3A+%23EFEFEF%3B" | Accusative


| <span class="Arab" lang="ar">[[جاذبين#Arabic|جَاذِبِينَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibīna</span>


| <span class="Arab" lang="ar">[[الجاذبين#Arabic|الْجَاذِبِينَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibīna</span>


| <span class="Arab" lang="ar">[[جاذبات#Arabic|جَاذِبَاتٍ]]</span>&lrm;‎; <span class="Arab" lang="ar">[[جواذب#Arabic|جَوَاذِبَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibātin</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jawāḏiba</span>


| <span class="Arab" lang="ar">[[الجاذبات#Arabic|الْجَاذِبَاتِ]]</span>&lrm;‎; <span class="Arab" lang="ar">[[الجواذب#Arabic|الْجَوَاذِبَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibāti</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jawāḏiba</span>


|-

! style="background%3A+%23EFEFEF%3B" | Genitive


| <span class="Arab" lang="ar">[[جاذبين#Arabic|جَاذِبِينَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibīna</span>


| <span class="Arab" lang="ar">[[الجاذبين#Arabic|الْجَاذِبِينَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibīna</span>


| <span class="Arab" lang="ar">[[جاذبات#Arabic|جَاذِبَاتٍ]]</span>&lrm;‎; <span class="Arab" lang="ar">[[جواذب#Arabic|جَوَاذِبَ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jāḏibātin</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">jawāḏiba</span>


| <span class="Arab" lang="ar">[[الجاذبات#Arabic|الْجَاذِبَاتِ]]</span>&lrm;‎; <span class="Arab" lang="ar">[[الجواذب#Arabic|الْجَوَاذِبِ]]</span>&lrm;<br><span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jāḏibāti</span>‎; <span lang="ar-Latn" class="tr+Latn" style="color%3A+%23888%3B">al-jawāḏibi</span>


|}

</div>
</div>[[Category:Arabic adjectives with basic triptote singular|جاذب]][[Category:Arabic adjectives with triptote singular in -a|جاذب]][[Category:Arabic adjectives with sound masculine plural|جاذب]][[Category:Arabic adjectives with sound feminine plural|جاذب]][[Category:Arabic adjectives with broken plural|جاذب]][[Category:Arabic adjectives with basic diptote broken plural|جاذب]]
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
                "form": "جَاذِب‎",
                "roman": "jāḏib",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "informal",
                  "masculine",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِب‎",
                "roman": "al-jāḏib",
                "source": "Declension",
                "tags": [
                  "definite",
                  "informal",
                  "masculine",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَة‎",
                "roman": "jāḏiba",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "informal",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَة‎",
                "roman": "al-jāḏiba",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "informal",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبٌ‎",
                "roman": "jāḏibun",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "masculine",
                  "nominative",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِبُ‎",
                "roman": "al-jāḏibu",
                "source": "Declension",
                "tags": [
                  "definite",
                  "masculine",
                  "nominative",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَةٌ‎",
                "roman": "jāḏibatun",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "nominative",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَةُ‎",
                "roman": "al-jāḏibatu",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "nominative",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبًا‎",
                "roman": "jāḏiban",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "indefinite",
                  "masculine",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِبَ‎",
                "roman": "al-jāḏiba",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "masculine",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَةً‎",
                "roman": "jāḏibatan",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "indefinite",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَةَ‎",
                "roman": "al-jāḏibata",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "feminine",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبٍ‎",
                "roman": "jāḏibin",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "masculine",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِبِ‎",
                "roman": "al-jāḏibi",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "masculine",
                  "singular",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَةٍ‎",
                "roman": "jāḏibatin",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "indefinite",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَةِ‎",
                "roman": "al-jāḏibati",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "genitive",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبَيْن‎",
                "roman": "jāḏibayn",
                "source": "Declension",
                "tags": [
                  "dual",
                  "indefinite",
                  "informal",
                  "masculine",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِبَيْن‎",
                "roman": "al-jāḏibayn",
                "source": "Declension",
                "tags": [
                  "definite",
                  "dual",
                  "informal",
                  "masculine",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَتَيْن‎",
                "roman": "jāḏibatayn",
                "source": "Declension",
                "tags": [
                  "dual",
                  "feminine",
                  "indefinite",
                  "informal",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَتَيْن‎",
                "roman": "al-jāḏibatayn",
                "source": "Declension",
                "tags": [
                  "definite",
                  "dual",
                  "feminine",
                  "informal",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبَانِ‎",
                "roman": "jāḏibāni",
                "source": "Declension",
                "tags": [
                  "dual",
                  "indefinite",
                  "masculine",
                  "nominative",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِبَانِ‎",
                "roman": "al-jāḏibāni",
                "source": "Declension",
                "tags": [
                  "definite",
                  "dual",
                  "masculine",
                  "nominative",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَتَانِ‎",
                "roman": "jāḏibatāni",
                "source": "Declension",
                "tags": [
                  "dual",
                  "feminine",
                  "indefinite",
                  "nominative",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَتَانِ‎",
                "roman": "al-jāḏibatāni",
                "source": "Declension",
                "tags": [
                  "definite",
                  "dual",
                  "feminine",
                  "nominative",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبَيْنِ‎",
                "roman": "jāḏibayni",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "dual",
                  "indefinite",
                  "masculine",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِبَيْنِ‎",
                "roman": "al-jāḏibayni",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "dual",
                  "masculine",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَتَيْنِ‎",
                "roman": "jāḏibatayni",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "dual",
                  "feminine",
                  "indefinite",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَتَيْنِ‎",
                "roman": "al-jāḏibatayni",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "dual",
                  "feminine",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبَيْنِ‎",
                "roman": "jāḏibayni",
                "source": "Declension",
                "tags": [
                  "dual",
                  "genitive",
                  "indefinite",
                  "masculine",
                  "triptote"
                ]
              },
              {
                "form": "الْجَاذِبَيْنِ‎",
                "roman": "al-jāḏibayni",
                "source": "Declension",
                "tags": [
                  "definite",
                  "dual",
                  "genitive",
                  "masculine",
                  "triptote"
                ]
              },
              {
                "form": "جَاذِبَتَيْنِ‎",
                "roman": "jāḏibatayni",
                "source": "Declension",
                "tags": [
                  "dual",
                  "feminine",
                  "genitive",
                  "indefinite",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "الْجَاذِبَتَيْنِ‎",
                "roman": "al-jāḏibatayni",
                "source": "Declension",
                "tags": [
                  "definite",
                  "dual",
                  "feminine",
                  "genitive",
                  "singular",
                  "triptote-a"
                ]
              },
              {
                "form": "جَاذِبِين‎",
                "roman": "jāḏibīn",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "informal",
                  "masculine",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "الْجَاذِبِين‎",
                "roman": "al-jāḏibīn",
                "source": "Declension",
                "tags": [
                  "definite",
                  "informal",
                  "masculine",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "جَاذِبَات‎‎",
                "roman": "jāḏibāt‎",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "informal",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "جَوَاذِب‎",
                "roman": "jawāḏib",
                "source": "Declension",
                "tags": [
                  "broken-plural",
                  "diptote",
                  "feminine",
                  "indefinite",
                  "informal",
                  "plural"
                ]
              },
              {
                "form": "الْجَاذِبَات‎‎",
                "roman": "al-jāḏibāt‎",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "informal",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "الْجَوَاذِب‎",
                "roman": "al-jawāḏib",
                "source": "Declension",
                "tags": [
                  "broken-plural",
                  "definite",
                  "diptote",
                  "feminine",
                  "informal",
                  "plural"
                ]
              },
              {
                "form": "جَاذِبُونَ‎",
                "roman": "jāḏibūna",
                "source": "Declension",
                "tags": [
                  "indefinite",
                  "masculine",
                  "nominative",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "الْجَاذِبُونَ‎",
                "roman": "al-jāḏibūna",
                "source": "Declension",
                "tags": [
                  "definite",
                  "masculine",
                  "nominative",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "جَاذِبَاتٌ‎‎",
                "roman": "jāḏibātun‎",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "indefinite",
                  "nominative",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "جَوَاذِبُ‎",
                "roman": "jawāḏibu",
                "source": "Declension",
                "tags": [
                  "broken-plural",
                  "diptote",
                  "feminine",
                  "indefinite",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "الْجَاذِبَاتُ‎‎",
                "roman": "al-jāḏibātu‎",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "nominative",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "الْجَوَاذِبُ‎",
                "roman": "al-jawāḏibu",
                "source": "Declension",
                "tags": [
                  "broken-plural",
                  "definite",
                  "diptote",
                  "feminine",
                  "nominative",
                  "plural"
                ]
              },
              {
                "form": "جَاذِبِينَ‎",
                "roman": "jāḏibīna",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "indefinite",
                  "masculine",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "الْجَاذِبِينَ‎",
                "roman": "al-jāḏibīna",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "masculine",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "جَاذِبَاتٍ‎‎",
                "roman": "jāḏibātin‎",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "feminine",
                  "indefinite",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "جَوَاذِبَ‎",
                "roman": "jawāḏiba",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "broken-plural",
                  "diptote",
                  "feminine",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "الْجَاذِبَاتِ‎‎",
                "roman": "al-jāḏibāti‎",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "definite",
                  "feminine",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "الْجَوَاذِبَ‎",
                "roman": "al-jawāḏiba",
                "source": "Declension",
                "tags": [
                  "accusative",
                  "broken-plural",
                  "definite",
                  "diptote",
                  "feminine",
                  "plural"
                ]
              },
              {
                "form": "جَاذِبِينَ‎",
                "roman": "jāḏibīna",
                "source": "Declension",
                "tags": [
                  "genitive",
                  "indefinite",
                  "masculine",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "الْجَاذِبِينَ‎",
                "roman": "al-jāḏibīna",
                "source": "Declension",
                "tags": [
                  "definite",
                  "genitive",
                  "masculine",
                  "plural",
                  "sound-masculine-plural"
                ]
              },
              {
                "form": "جَاذِبَاتٍ‎‎",
                "roman": "jāḏibātin‎",
                "source": "Declension",
                "tags": [
                  "feminine",
                  "genitive",
                  "indefinite",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "جَوَاذِبَ‎",
                "roman": "jawāḏiba",
                "source": "Declension",
                "tags": [
                  "broken-plural",
                  "diptote",
                  "feminine",
                  "genitive",
                  "indefinite",
                  "plural"
                ]
              },
              {
                "form": "الْجَاذِبَاتِ‎‎",
                "roman": "al-jāḏibāti‎",
                "source": "Declension",
                "tags": [
                  "definite",
                  "feminine",
                  "genitive",
                  "plural",
                  "sound-feminine-plural"
                ]
              },
              {
                "form": "الْجَوَاذِبِ‎",
                "roman": "al-jawāḏibi",
                "source": "Declension",
                "tags": [
                  "broken-plural",
                  "definite",
                  "diptote",
                  "feminine",
                  "genitive",
                  "plural"
                ]
              }
            ],
        }
        self.assertEqual(expected, ret)

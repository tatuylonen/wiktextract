# -*- fundamental -*-
#
# Tests for parsing inflection tables
#
# Copyright (c) 2021, 2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org
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
        self.wxr.wtp.start_section("Assyrian Neo-Aramaic")

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

    def test_aii_table(self):
        ret = self.xinfl(
            "ܛܠܐ",
            "Assyrian Neo-Aramaic",
            "prep",
            "Conjugation",
            """
<div class="inflection-table-wrapper%2Binflection-table-narrow%2Binflection-table-red%2B%2Binflection-table-collapsible%2Binflection-table-collapsed%2Bno-vc%2B" style="width%253A%2Bfit-content" data-toggle-category="inflection"><templatestyles src="Template%253Ainflection-table-top%252Fstyle.css">


{| class="inflection-table%2B"

|+ 
 class="inflection-table-title"
 Inflection of <i class="Syrc%2Bmention" lang="aii">ܛܠܵܐ</i>


|- 

! colspan="3" class="outer" | base form




| <span class="Syrc" lang="aii">[[ܛܠܐ#Assyrian&#95;Neo-Aramaic|ܛܠܵܐ]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlā</span><span class="mention-gloss-paren+annotation-paren">)</span>




|- 

! colspan="999" class="separator" |




|- 

! colspan="4" class="outer" | Personal-pronoun including forms




|- 

! rowspan="2" class="outer" |




! colspan="2" | singular




! rowspan="2" | plural




|- 

! class="secondary" | <span class="gender"><abbr title="masculine+gender">m</abbr></span>




! class="secondary" | <span class="gender"><abbr title="feminine+gender">f</abbr></span>




|- 

! class="outer" |1<sup>st</sup> person




| colspan="2" | <span class="Syrc" lang="aii">[[ܛܠܬܝ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܝܼ]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯī</span><span class="mention-gloss-paren+annotation-paren">)</span>




| <span class="Syrc" lang="aii">[[ܛܠܬܢ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܲܢ]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯan</span><span class="mention-gloss-paren+annotation-paren">)</span>




|- class="vsHide"

! class="outer" | 2<sup>nd</sup> person




| <span class="Syrc" lang="aii">[[ܛܠܬܘܟ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܘܼܟ݂]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯūḵ</span><span class="mention-gloss-paren+annotation-paren">)</span>




| <span class="Syrc" lang="aii">[[ܛܠܬܟܝ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܵܟ݂ܝ]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯāḵ</span><span class="mention-gloss-paren+annotation-paren">)</span>




| <span class="Syrc" lang="aii">[[ܛܠܬܘܟܘܢ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܵܘܟ݂ܘܿܢ]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯāwḵōn</span><span class="mention-gloss-paren+annotation-paren">)</span>




|- 

! class="outer" | 3<sup>rd</sup> person




| <span class="Syrc" lang="aii">[[ܛܠܬܗ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܹܗ]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯēh</span><span class="mention-gloss-paren+annotation-paren">)</span>




| <span class="Syrc" lang="aii">[[ܛܠܬܗ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܵܗ̇]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯāh</span><span class="mention-gloss-paren+annotation-paren">)</span>




| <span class="Syrc" lang="aii">[[ܛܠܬܗܘܢ#Assyrian&#95;Neo-Aramaic|ܛܠܵܬ݂ܗܘܿܢ]]</span> <span class="mention-gloss-paren+annotation-paren">(</span><span lang="aii-Latn" class="tr+Latn">ṭlāṯhōn</span><span class="mention-gloss-paren+annotation-paren">)</span>




|}



</div>
""",  # noqa: E501 W291
        )
        expected = {
            "forms": [
                {
                    "form": "no-table-tags",
                    "tags": ["table-tags"],
                    "source": "Conjugation",
                },
                {
                    "form": "ܛܠܵܐ",
                    "roman": "ṭlā",
                    "source": "Conjugation",
                    "tags": ["stem"],
                },
                {
                    "form": "ܛܠܵܬ݂ܝܼ",
                    "roman": "ṭlāṯī",
                    "source": "Conjugation",
                    "tags": ["first-person", "singular", "stem"],
                },
                {
                    "form": "ܛܠܵܬ݂ܲܢ",
                    "roman": "ṭlāṯan",
                    "source": "Conjugation",
                    "tags": ["first-person", "plural"],
                },
                {
                    "form": "ܛܠܵܬ݂ܘܼܟ݂",
                    "roman": "ṭlāṯūḵ",
                    "source": "Conjugation",
                    "tags": ["masculine", "second-person", "singular", "stem"],
                },
                {
                    "form": "ܛܠܵܬ݂ܵܟ݂ܝ",
                    "roman": "ṭlāṯāḵ",
                    "source": "Conjugation",
                    "tags": ["feminine", "second-person", "singular", "stem"],
                },
                {
                    "form": "ܛܠܵܬ݂ܵܘܟ݂ܘܿܢ",
                    "roman": "ṭlāṯāwḵōn",
                    "source": "Conjugation",
                    "tags": ["plural", "second-person"],
                },
                {
                    "form": "ܛܠܵܬ݂ܹܗ",
                    "roman": "ṭlāṯēh",
                    "source": "Conjugation",
                    "tags": ["masculine", "singular", "stem", "third-person"],
                },
                {
                    "form": "ܛܠܵܬ݂ܵܗ̇",
                    "roman": "ṭlāṯāh",
                    "source": "Conjugation",
                    "tags": ["feminine", "singular", "stem", "third-person"],
                },
                {
                    "form": "ܛܠܵܬ݂ܗܘܿܢ",
                    "roman": "ṭlāṯhōn",
                    "source": "Conjugation",
                    "tags": ["plural", "third-person"],
                },
            ]
        }
        self.assertEqual(expected, ret)

# Tests for parse_alt_or_inflection_of()
#
# Copyright (c) 2021-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest

from wikitextprocessor import Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.en.form_descriptions import (
    parse_alt_or_inflection_of,
)
from wiktextract.extractor.en.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class FormOfTests(unittest.TestCase):
    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(
                dump_file_lang_code="en", capture_language_codes=None
            ),
        )
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_non_of1(self):
        ret = parse_alt_or_inflection_of(self.wxr, "inalienable", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertIs(ret, None)

    def test_non_of2(self):
        ret = parse_alt_or_inflection_of(self.wxr, "inflection of", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, None)

    def test_non_of3(self):
        ret = parse_alt_or_inflection_of(self.wxr, "genitive", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, (["genitive"], None))

    def test_simple1(self):
        ret = parse_alt_or_inflection_of(self.wxr, "abbreviation of foo", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, (["abbreviation", "alt-of"], [{"word": "foo"}]))

    def test_simple2(self):
        ret = parse_alt_or_inflection_of(
            self.wxr,
            "abbreviation of New York, a city in the United States",
            set(),
        )
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(
            ret,
            (
                ["abbreviation", "alt-of"],
                [{"word": "New York", "extra": "a city in the United States"}],
            ),
        )

    def test_simple3(self):
        ret = parse_alt_or_inflection_of(self.wxr, "inflection of foo", set())
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, (["form-of"], [{"word": "foo"}]))

    def test_simple4(self):
        ret = parse_alt_or_inflection_of(
            self.wxr, "plural of instrumental", set()
        )
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(
            ret, (["form-of", "plural"], [{"word": "instrumental"}])
        )

    def test_simple5(self):
        ret = parse_alt_or_inflection_of(
            self.wxr, "plural of corgi or corgy", set()
        )
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(
            ret, (["form-of", "plural"], [{"word": "corgi"}, {"word": "corgy"}])
        )

    def test_simple6(self):
        ret = parse_alt_or_inflection_of(
            self.wxr, "plural of fish or chips", set()
        )
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(
            ret, (["form-of", "plural"], [{"word": "fish or chips"}])
        )

    def test_simple7(self):
        ret = parse_alt_or_inflection_of(
            self.wxr, "abbreviation of OK.", set(["OK."])
        )
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, (["abbreviation", "alt-of"], [{"word": "OK."}]))

    def test_simple8(self):
        ret = parse_alt_or_inflection_of(
            self.wxr, "abbreviation of OK.", set(["OK"])
        )
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(ret, (["abbreviation", "alt-of"], [{"word": "OK"}]))

    def test_dialect1(self):
        ret = parse_alt_or_inflection_of(
            self.wxr, "Western-Armenian form of OK.", set(["OK"])
        )
        self.assertEqual(self.wxr.wtp.errors, [])
        self.assertEqual(self.wxr.wtp.warnings, [])
        self.assertEqual(self.wxr.wtp.debugs, [])
        self.assertEqual(
            ret, (["Western-Armenian", "alt-of"], [{"word": "OK"}])
        )

    def test_alt_form_section(self):
        self.wxr.wtp.add_page(
            "Template:alter",
            10,
            """<span class="Latn" lang="scn">[[zùccuru#Sicilian|zùccuru]]</span>, <span class="Latn" lang="scn">[[zùcchiru#Sicilian|zùcchiru]]</span>""",
        )
        page_data = parse_page(
            self.wxr,
            "zùccaru",
            """==Sicilian==
===Alternative forms===
* {{alter|scn|zùccuru|zùcchiru}}
===Noun===
# [[sugar]]""",
        )
        self.assertEqual(
            page_data[0]["forms"],
            [
                {"form": "zùccuru", "tags": ["alternative"]},
                {"form": "zùcchiru", "tags": ["alternative"]},
            ],
        )

    def test_ja_kt_tables_under_pos(self):
        self.wxr.wtp.add_page(
            "Template:ja-kanjitab",
            10,
            """{| class="wikitable kanji-table floatright"
! colspan="2" | [[Appendix:Japanese_glossary#kanji|Kanji]] in this term
|- lang="ja" class="Jpan"
| [[元#Japanese|元]]
| [[気#Japanese|気]]
|-
| <span class="Jpan" lang="ja">げん</span><br/><small>[[Appendix:Japanese_glossary#kyōiku_kanji|Grade: 2]]</small>
| <span class="Jpan" lang="ja">き</span><br/><small>[[Appendix:Japanese_glossary#kyōiku_kanji|Grade: 1]]</small>
|-
| colspan="2" |[[Appendix:Japanese_glossary#kan'on|kan'on]]
|}
{| class="wikitable floatright"
! style="font-weight:normal" | Alternative spelling
|-
| <span class="Jpan" lang="ja">[[元氣#Japanese|元氣]]</span> <small><span class="usage-label-sense"><span class="ib-brac label-brac">(</span><span class="ib-content label-content">kyūjitai</span><span class="ib-brac label-brac">)</span></span></small>
|}[[Category:Japanese terms spelled with 元 read as げん|けんき']]""",
        )
        data = parse_page(
            self.wxr,
            "元気",
            """==Japanese==
{{ja-kanjitab|yomi=kanon|げん|き}}
====Adjective====
# [[healthy]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {
                    "form": "元氣",
                    "tags": ["alternative", "kanji", "kyūjitai"],
                }
            ],
        )
        self.assertEqual(
            data[0]["categories"],
            ["Japanese terms spelled with 元 read as げん"],
        )

    def test_ja_kt_table_under_pos(self):
        self.wxr.wtp.add_page(
            "Template:ja-kanjitab",
            10,
            """{| class="wikitable floatright"
! style="font-weight:normal" | Alternative spellings
|-
| <span class="Jpan" lang="ja">[[親子#Japanese|親子]]</span><br><span class="Jpan" lang="ja">[[母子#Japanese|母子]]</span>
|}""",
        )
        data = parse_page(
            self.wxr,
            "おやこ",
            """==Japanese==
{{ja-kanjitab|alt=親子,母子}}
===Noun===
# [[parent]] and [[child]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [
                {"form": "親子", "tags": ["alternative", "kanji"]},
                {"form": "母子", "tags": ["alternative", "kanji"]},
            ],
        )

    def test_ja_kt_under_etymology(self):
        self.wxr.wtp.add_page(
            "Template:ja-kanjitab",
            10,
            """{| class="wikitable floatright"
! style="font-weight:normal" | Alternative spelling
|-
| <span class="Jpan" lang="ja">[[今日#Japanese|今日]]</span>
|}""",
        )
        data = parse_page(
            self.wxr,
            "きょう",
            """==Japanese==
===Etymology 1===
{{ja-kanjitab|alt=今日}}
====Noun====
# [[today]]""",
        )
        self.assertEqual(
            data[0]["forms"],
            [{"form": "今日", "tags": ["alternative", "kanji"]}],
        )

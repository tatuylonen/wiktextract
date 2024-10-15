# Tests for parsing a page
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import unittest
from unittest.mock import patch

from wikitextprocessor import Page, Wtp

from wiktextract.config import WiktionaryConfig
from wiktextract.page import parse_page
from wiktextract.thesaurus import close_thesaurus_db
from wiktextract.wxr_context import WiktextractContext


class EnPageTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.wxr = WiktextractContext(
            Wtp(lang_code="en"),
            WiktionaryConfig(
                capture_language_codes=None,
                capture_translations=True,
                capture_pronunciation=True,
                capture_linkages=True,
                capture_compounds=True,
                capture_redirects=True,
                capture_examples=True,
            )
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()
        close_thesaurus_db(
            self.wxr.thesaurus_db_path, self.wxr.thesaurus_db_conn
        )

    def test_page1(self):
        lst = parse_page(
            self.wxr,
            "testpage",
            """
==Swedish==
===Noun===
foo f

# sense 1
# sense 2
""",
        )
        # XXX should also capture examples
        self.assertEqual(
            lst,
            [
                {
                    "forms": [
                        {"form": "foo", "tags": ["canonical", "feminine"]}
                    ],
                    "lang": "Swedish",
                    "lang_code": "sv",
                    "pos": "noun",
                    "senses": [
                        {
                            "glosses": ["sense 1"],
                        },
                        {
                            "glosses": ["sense 2"],
                        },
                    ],
                    "word": "testpage",
                }
            ],
        )

    def test_page2(self):
        lst = parse_page(
            self.wxr,
            "testpage",
            """
==Swedish==
===Noun===
testpage f

# sense 1
""",
        )
        self.assertEqual(
            lst,
            [
                {
                    "lang": "Swedish",
                    "lang_code": "sv",
                    "pos": "noun",
                    "senses": [
                        {
                            "glosses": ["sense 1"],
                            "tags": ["feminine"],
                        },
                    ],
                    "word": "testpage",
                }
            ],
        )

    def test_page3(self):
        lst = parse_page(
            self.wxr,
            "Unsupported titles/C sharp",
            """
==Swedish==
===Noun===
foo

# sense 1
""",
        )
        self.assertEqual(
            lst,
            [
                {
                    "forms": [
                        {"form": "foo", "tags": ["canonical"]},
                    ],
                    "lang": "Swedish",
                    "lang_code": "sv",
                    "original_title": "Unsupported titles/C sharp",
                    "pos": "noun",
                    "senses": [
                        {
                            "glosses": ["sense 1"],
                        },
                    ],
                    "word": "C#",
                }
            ],
        )

    def test_page4(self):
        lst = parse_page(
            self.wxr,
            "foo",
            """
==English==

===Noun===
foo

# sense 1
# sense 2
# (mycology) mushroom
# (person) one who foos

====Translations====
* Finnish: fuu
* Swedish: bar m, hop f

====Related terms====
* (sense abc) zap
* verbs: zip, zump

""",
        )
        # print("RETURNED:", json.dumps(lst, indent=2, sort_keys=True))
        self.assertEqual(
            lst,
            [
                {
                    "lang": "English",
                    "lang_code": "en",
                    "pos": "noun",
                    "related": [
                        {"sense": "sense abc", "word": "zap"},
                        {"word": "zip", "tags": ["verb"]},
                        {"word": "zump", "tags": ["verb"]},
                    ],
                    "senses": [
                        {
                            "glosses": ["sense 1"],
                        },
                        {
                            "glosses": ["sense 2"],
                        },
                        {
                            "glosses": ["mushroom"],
                            "raw_glosses": ["(mycology) mushroom"],
                            "topics": [
                                "biology",
                                "mycology",
                                "natural-sciences",
                            ],
                        },
                        {
                            "glosses": ["one who foos"],
                            "raw_glosses": ["(person) one who foos"],
                            "tags": ["person"],
                        },
                    ],
                    "translations": [
                        {"word": "fuu", "lang": "Finnish", "code": "fi"},
                        {
                            "word": "bar",
                            "lang": "Swedish",
                            "code": "sv",
                            "tags": ["masculine"],
                        },
                        {
                            "word": "hop",
                            "lang": "Swedish",
                            "code": "sv",
                            "tags": ["feminine"],
                        },
                    ],
                    "word": "foo",
                }
            ],
        )

    def test_page5(self):
        lst = parse_page(
            self.wxr,
            "foo",
            """
==English==

===Noun===
foo

# sense 1
#: example 1 causes sense 1 to get pushed
## subsense 1
##: subexample 1
## subsense 2
# sense 2
# (mycology) mushroom
#: example 2
#: example 3
# (person) one who foos
## one who foos more specifically
## another one who foos

====Translations====
* Finnish: fuu
* Swedish: bar m, hop f

====Related terms====
* (sense abc) zap
* verbs: zip, zump

""",
        )
        # print("RETURNED:", json.dumps(lst, indent=2, sort_keys=True))
        self.assertEqual(
            lst,
            [
                {
                    "lang": "English",
                    "lang_code": "en",
                    "pos": "noun",
                    "related": [
                        {"sense": "sense abc", "word": "zap"},
                        {"word": "zip", "tags": ["verb"]},
                        {"word": "zump", "tags": ["verb"]},
                    ],
                    "senses": [
                        {
                            "glosses": ["sense 1", "subsense 1"],
                            "examples": [{"text": "subexample 1"}],
                        },
                        {
                            "glosses": ["sense 1", "subsense 2"],
                        },
                        {
                            "glosses": ["sense 1"],
                            "examples": [
                                {
                                    "text": "example 1 causes sense "
                                    "1 to get pushed"
                                }
                            ],
                        },
                        {
                            "glosses": ["sense 2"],
                        },
                        {
                            "glosses": ["mushroom"],
                            "raw_glosses": ["(mycology) mushroom"],
                            "topics": [
                                "biology",
                                "mycology",
                                "natural-sciences",
                            ],
                            "examples": [
                                {"text": "example 2"},
                                {"text": "example 3"},
                            ],
                        },
                        {
                            "glosses": [
                                "one who foos",
                                "one who foos more specifically",
                            ],
                            "raw_glosses": [
                                "(person) one who foos",
                                "one who foos more specifically",
                            ],
                            "tags": ["person"],
                        },
                        {
                            "glosses": ["one who foos", "another one who foos"],
                            "raw_glosses": [
                                "(person) one who foos",
                                "another one who foos",
                            ],
                            "tags": ["person"],
                        },
                    ],
                    "translations": [
                        {"word": "fuu", "lang": "Finnish", "code": "fi"},
                        {
                            "word": "bar",
                            "lang": "Swedish",
                            "code": "sv",
                            "tags": ["masculine"],
                        },
                        {
                            "word": "hop",
                            "lang": "Swedish",
                            "code": "sv",
                            "tags": ["feminine"],
                        },
                    ],
                    "word": "foo",
                }
            ],
        )

    def test_page6(self):
        lst = parse_page(
            self.wxr,
            "testpage",
            """
==Japanese==
===Verb===
foo

# sense 1
#: <dl><dd><span class="Jpan" lang="ja"><a href="/wiki/%E3%81%94%E9%A3%AF#Japanese" title="ご飯">ご<ruby>飯<rp>(</rp><rt>はん</rt><rp>)</rp></ruby></a>を<b><ruby>食<rp>(</rp><rt>た</rt><rp>)</rp></ruby>べる</b></span><dl><dd><i>go-han o <b>taberu</b></i></dd><dd>to <b>eat</b> a meal</dd></dl></dd></dl>
""",  # noqa: E501
        )
        self.assertEqual(
            lst,
            [
                {
                    "forms": [
                        {
                            "form": "foo",
                            "tags": [
                                "canonical",
                            ],
                        }
                    ],
                    "lang": "Japanese",
                    "lang_code": "ja",
                    "pos": "verb",
                    "senses": [
                        {
                            "glosses": ["sense 1"],
                            "examples": [
                                {
                                    "english": "to eat a meal",
                                    "roman": "go-han o taberu",
                                    "ruby": [("飯", "はん"), ("食", "た")],
                                    "text": "ご飯を食べる",
                                }
                            ],
                        },
                    ],
                    "word": "testpage",
                }
            ],
        )

    def test_page7(self):
        """When inside a list, an HTML element should not interrupt the
        list"""
        # unfortunately, I've only figured out a simple way to do this
        # if the closing tag is exactly at the start of the next line, and
        # there's nothing else in-between breaking the list... But it's
        # better than nothing and fixes a few issues.
        lst = parse_page(
            self.wxr,
            "foo",
            """
==English==

===Noun===
foo

# sense 1
# sense 2
## (mycology) mushroom<div>
</div>
## (person) one who foos
""",
        )
        # print("RETURNED:", json.dumps(lst, indent=2, sort_keys=True))
        self.assertEqual(
            lst,
            [
                {
                    "lang": "English",
                    "lang_code": "en",
                    "pos": "noun",
                    "senses": [
                        {
                            "glosses": ["sense 1"],
                        },
                        {
                            "glosses": ["sense 2", "mushroom"],
                            "raw_glosses": ["sense 2", "(mycology) mushroom"],
                            "topics": [
                                "biology",
                                "mycology",
                                "natural-sciences",
                            ],
                        },
                        {
                            "glosses": ["sense 2", "one who foos"],
                            "raw_glosses": ["sense 2", "(person) one who foos"],
                            "tags": ["person"],
                        },
                    ],
                    "word": "foo",
                }
            ],
        )

    def test_page8(self):
        """Capture category links and normal links in glosses"""
        lst = parse_page(
            self.wxr,
            "foo",
            """
==English==

===Noun===
foo

# sense 1 [[Category:bar]], [[bazlink|baz]]
""",
        )
        # print("RETURNED:", json.dumps(lst, indent=2, sort_keys=True))
        self.assertEqual(
            lst,
            [
                {
                    "lang": "English",
                    "lang_code": "en",
                    "pos": "noun",
                    "senses": [
                        {
                            "categories": ["bar"],
                            "glosses": ["sense 1, baz"],
                            "links": [("baz", "bazlink")],
                        },
                    ],
                    "word": "foo",
                }
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(title="Template:zh-see", namespace_id=10, body=""),
    )
    def test_zh_see(self, mock_get_page):
        # https://en.wiktionary.org/wiki/你们
        # GitHub issue #287
        data = parse_page(
            self.wxr,
            "你们",
            """
==Chinese==
{{zh-see|你們}}
{{zh-see|妳們}}
            """,
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "Chinese",
                    "lang_code": "zh",
                    "pos": "soft-redirect",
                    "redirects": ["你們", "妳們"],
                    "senses": [{"tags": ["no-gloss"]}],
                    "word": "你们",
                }
            ],
        )
        data = parse_page(
            self.wxr,
            "车",
            """
==Chinese==
===Glyph origin===
From cursive script of 車.

===Definitions===
{{zh-see|車|s}}
{{zh-see|龺|ss}}
            """,
        )
        self.assertEqual(
            data,
            [
                {
                    "etymology_text": "From cursive script of 車.",
                    "lang": "Chinese",
                    "lang_code": "zh",
                    "redirects": ["車", "龺"],
                    "word": "车",
                    "pos": "character",
                    "senses": [{"tags": ["no-gloss"]}],
                }
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(title="Template:test", namespace_id=10, body=""),
    )
    def test_catlangname_template_in_headword_line(self, mock_get_page) -> None:
        """
        gloss data should be extracted when template catlangname is in the
        headword line, GitHub issue #285
        test wikitext from page https://en.wiktionary.org/wiki/ox
        """
        data = parse_page(
            self.wxr,
            "",
            """
==English==

===Noun===
{{en-noun|oxen|oxes|pl2qual=nonstandard}} {{catlangname|en|nouns with irregular plurals|two-letter words}}

# An adult castrated male of cattle.""",  # noqa: E501
        )
        self.assertEqual(
            data[0].get("senses"),
            [{"glosses": ["An adult castrated male of cattle."]}],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(title="test", namespace_id=10, body=""),
    )
    def test_ARF_page(self, mock_get_page) -> None:
        """
        test wikitext copied from page https://en.wiktionary.org/wiki/ARF
        """
        data = parse_page(
            self.wxr,
            "",
            """
==English==

===Phrase===
{{head|en|phrase}}

# {{lb|en|computing}} "[[abort|Abort]], [[retry|Retry]], [[fail|Fail]]?"
            """,
        )
        self.assertEqual(
            data[0].get("senses", [{}])[0].get("glosses"),
            ['"Abort, Retry, Fail?"'],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:ux",
            namespace_id=10,
            body="Name given to a number of one-piece attires",
        ),
    )
    def test_ux_template_in_gloss(self, mock_get_page) -> None:
        """
        test wikitext copied from page https://en.wiktionary.org/wiki/onesie
        """
        data = parse_page(
            self.wxr,
            "",
            """
==English==

===Noun===

# {{ux|en|Name given to a number of one-piece attires}}
            """,
        )
        self.assertEqual(
            data[0].get("senses", [{}])[0].get("glosses"),
            ["Name given to a number of one-piece attires"],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:head",
            namespace_id=10,
            body='<strong class="Latn headword" lang="ga">shail</strong>[[Category:Irish non-lemma forms|SHAIL]][[Category:Irish mutated nouns|SHAIL]]',
        ),
    )
    def test_gloss_not_inside_list(self, mock_get_page):
        # https://en.wiktionary.org/wiki/shail
        data = parse_page(
            self.wxr,
            "shail",
            """
==Irish==

===Noun===
{{head|ga|mutated noun}}

1. Celtic

====Translations====

foo
            """,
        )
        # from pprint import pp
        # pp(data)
        self.assertEqual(
            data,
            [
                {
                    "head_templates": [
                        {
                            "args": {"1": "ga", "2": "mutated noun"},
                            "expansion": "shail",
                            "name": "head",
                        }
                    ],
                    "lang": "Irish",
                    "lang_code": "ga",
                    "pos": "noun",
                    "senses": [
                        {
                            "categories": [
                                "Irish mutated nouns",
                                "Irish non-lemma forms",
                            ],
                            "glosses": ["Celtic"],
                        }
                    ],
                    "word": "shail",
                }
            ],
        )

    def test_ja_see(self):
        # https://en.wiktionary.org/wiki/ひとり
        self.wxr.wtp.start_page("ひとり")
        data = parse_page(
            self.wxr,
            "ひとり",
            "==Japanese==\n{{ja-see|一人|独り}}",
        )
        self.assertEqual(
            data,
            [
                {
                    "lang": "Japanese",
                    "lang_code": "ja",
                    "pos": "soft-redirect",
                    "redirects": ["一人", "独り"],
                    "senses": [{"tags": ["no-gloss"]}],
                    "word": "ひとり",
                }
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:+obj",
            namespace_id=10,
            body="[with accusative blu or ergative = MEANING]",
        ),
    )
    def test_plusobj_template(self, mock_get_page):
        """Testing info_templates, specifically Template:+obj. If +obj is ever
        changed, this test won't be able to catch it; it would be handy to have
        tests that check for this, but it's not feasible to require up-to-date
        databases for testing.

        GitHub issue #667
        GitHub issue #760
        """
        data = parse_page(
            self.wxr,
            "foo",
            """
==Czech==

===Noun===
foo {{+obj|cs|accusative|blu|or|ergative|means=MEANING}}

# foobar {{+obj|cs|accusative|blu|or|ergative|means=MEANING}}
""",
        )
        # from pprint import pp
        # pp(data)
        self.assertEqual(
            data,
            [
                {
                    "info_templates": [
                        {
                            "args": {
                                "1": "cs",
                                "2": "accusative",
                                "3": "blu",
                                "4": "or",
                                "5": "ergative",
                                "means": "MEANING",
                            },
                            "expansion": "[with accusative blu or "
                            "ergative = MEANING]",
                            "extra_data": {
                                "meaning": "MEANING",
                                "tags": ["ergative"],
                                "words": ["accusative", "blu"],
                            },
                            "name": "+obj",
                        }
                    ],
                    "lang": "Czech",
                    "lang_code": "cs",
                    "pos": "noun",
                    "senses": [
                        {
                            "glosses": [
                                "foobar",
                            ],
                            "info_templates": [
                                {
                                    "args": {
                                        "1": "cs",
                                        "2": "accusative",
                                        "3": "blu",
                                        "4": "or",
                                        "5": "ergative",
                                        "means": "MEANING",
                                    },
                                    "expansion": "[with accusative blu or "
                                    "ergative = "
                                    "MEANING]",
                                    "extra_data": {
                                        "meaning": "MEANING",
                                        "tags": ["ergative"],
                                        "words": ["accusative", "blu"],
                                    },
                                    "name": "+obj",
                                }
                            ],
                            "raw_glosses": [
                                "foobar [with accusative blu or ergative = "
                                "MEANING]"
                            ],
                        }
                    ],
                    "word": "foo",
                }
            ],
        )

    def test_zh_see_under_pos_title(self):
        # GH issue #730
        self.assertEqual(
            parse_page(
                self.wxr,
                "马",
                """==Chinese==
===Definitions===
{{zh-see|馬}}""",
            ),
            [
                {
                    "lang": "Chinese",
                    "lang_code": "zh",
                    "pos": "character",
                    "redirects": ["馬"],
                    "senses": [{"tags": ["no-gloss"]}],
                    "word": "马",
                }
            ],
        )

    def test_supergloss_clean(self):
        # PR #764
        self.assertEqual(
            parse_page(
                self.wxr,
                "test",
                """==English==
===Noun===

test
# † supergloss [removed text]
## subgloss
## subgloss2""",
            ),
            [
                {
                    "lang": "English",
                    "lang_code": "en",
                    "pos": "noun",
                    "senses": [
                        {
                            "glosses": ["supergloss", "subgloss"],
                            "raw_glosses": [
                                "† supergloss [removed text]",
                                "subgloss",
                            ],
                            "tags": ["obsolete"],
                        },
                        {
                            "glosses": ["supergloss", "subgloss2"],
                            "raw_glosses": [
                                "† supergloss [removed text]",
                                "subgloss2",
                            ],
                            "tags": ["obsolete"],
                        },
                    ],
                    "word": "test",
                }
            ],
        )

    @patch(
        "wikitextprocessor.Wtp.get_page",
        return_value=Page(
            title="Template:test-alcance",
            namespace_id=10,
            body="""inflection of alcanfoo
## first/third-person singular present subjunctive
## third-person singular imperative""",
        ),
    )
    def test_templates_with_subglosses(self, mock_get_page):
        # PR #771
        self.assertEqual(
            parse_page(
                self.wxr,
                "alcance",
                """==Spanish==
===Verb===

alcance
# {{test-alcance}}
""",
            ),
            [
                {
                    "lang": "Spanish",
                    "lang_code": "es",
                    "pos": "verb",
                    "senses": [
                        {
                            "form_of": [{"word": "alcanfoo"}],
                            "glosses": [
                                "inflection of alcanfoo",
                                "first/third-person singular present subjunctive",
                            ],
                            "tags": [
                                "first-person",
                                "form-of",
                                "present",
                                "singular",
                                "subjunctive",
                                "third-person",
                            ],
                        },
                        {
                            "form_of": [{"word": "alcanfoo"}],
                            "glosses": [
                                "inflection of alcanfoo",
                                "third-person singular imperative",
                            ],
                            "tags": [
                                "form-of",
                                "imperative",
                                "singular",
                                "third-person",
                            ],
                        },
                    ],
                    "word": "alcance",
                }
            ],
        )

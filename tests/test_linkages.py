# Tests for parsing linkages (synonyms, hypernyms, related terms, etc)
#
# Copyright (c) 2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import json
import unittest
from wiktextract.linkages import parse_linkage_item_text
from wiktextract.config import WiktionaryConfig
from wiktextract.wxr_context import WiktextractContext
from wikitextprocessor import Wtp


class LinkageTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 20000
        self.wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        self.wxr.wtp.start_page("testpage")
        self.wxr.wtp.start_section("English")

    def run_data(self, item, word="testpage", lang="English",
                 field="related", ruby=[], sense=None, senses=[],
                 wxr=None, is_reconstruction=False):
        """Runs a test where we expect the parsing to return None.  This
        function returns ``data``."""
        assert isinstance(item, str)
        assert isinstance(word, str)
        assert isinstance(lang, str)
        assert isinstance(field, str)
        assert isinstance(ruby, list)
        assert sense is None or isinstance(sense, str)
        assert isinstance(senses, list)
        assert wxr is None or isinstance(wxr, WiktextractContext)
        wxr1 = wxr if wxr is not None else WiktextractContext(
                                                        Wtp(),
                                                        WiktionaryConfig())
        self.wxr = wxr1
        self.wxr.wtp.start_page(word)
        self.wxr.wtp.start_section(lang)
        data = {}
        ret = parse_linkage_item_text(self.wxr, word, data, field, item,
                                      sense, ruby, senses, is_reconstruction)
        self.assertIs(ret, None)
        if wxr is None:
            self.assertEqual(self.wxr.wtp.errors, [])
            self.assertEqual(self.wxr.wtp.warnings, [])
            self.assertEqual(self.wxr.wtp.debugs, [])
        return data

    def run_empty(self, item):
        data = self.run_data(item)
        self.assertEqual(data, {})

    def test_simple1(self):
        data = self.run_data("plan B")
        self.assertEqual(data, {"related": [{"word": "plan B"}]})

    def test_simple2(self):
        data = self.run_data("f")
        self.assertEqual(data, {"related": [{"word": "f"}]})

    def test_simple3(self):
        data = self.run_data("3")
        self.assertEqual(data, {"related": [{"word": "3"}]})

    def test_simple4(self):
        data = self.run_data("3", lang="Zulu")
        self.assertEqual(data, {"related": [{"word": "3"}]})

    def test_simple5(self):
        data = self.run_data("u", lang="Swahili")
        self.assertEqual(data, {"related": [{"word": "u"}]})

    def test_simple6(self):
        data = self.run_data("uu", lang="Swahili")
        self.assertEqual(data, {"related": [{"word": "uu"}]})

    def test_simple7(self):
        data = self.run_data("f.")
        self.assertEqual(data, {"related": [{"word": "f."}]})

    def test_simple8(self):
        data = self.run_data("f.")
        self.assertEqual(data, {"related": [{"word": "f."}]})

    def test_simple9(self):
        data = self.run_data("&c.")
        self.assertEqual(data, {"related": [{"word": "&c."}]})

    def test_simple10(self):
        data = self.run_data("& cetera")
        self.assertEqual(data, {"related": [{"word": "& cetera"}]})

    def test_simple11(self):
        data = self.run_data("et cétéra")
        self.assertEqual(data, {"related": [{"word": "et cétéra"}]})

    def test_simple12(self):
        data = self.run_data("et cætera, et caetera")
        self.assertEqual(data, {"related": [
            {"word": "et cætera"},
            {"word": "et caetera"},
        ]})

    def test_simple13(self):
        data = self.run_data("a, b, ..., z")
        self.assertEqual(data, {"related": [
            {"word": "a"},
            {"word": "b"},
            {"word": "z"},
        ]})

    def test_simple14(self):
        data = self.run_data("a, b, …, z")
        self.assertEqual(data, {"related": [
            {"word": "a"},
            {"word": "b"},
            {"word": "z"},
        ]})

    def test_simple15(self):
        data = self.run_data(",")
        self.assertEqual(data, {"related": [
            {"word": ","},
        ]})

    def test_simple16(self):
        data = self.run_data(";")
        self.assertEqual(data, {"related": [
            {"word": ";"},
        ]})

    def test_simple17(self):
        data = self.run_data("or")
        self.assertEqual(data, {"related": [
            {"word": "or"},
        ]})

    def test_simple18(self):
        data = self.run_data("and")
        self.assertEqual(data, {"related": [
            {"word": "and"},
        ]})

    def test_simple19(self):
        data = self.run_data("a or b")
        self.assertEqual(data, {"related": [
            {"word": "a"},
            {"word": "b"},
        ]})

    def test_simple20(self):
        data = self.run_data("a (verb)")
        self.assertEqual(data, {"related": [
            {"word": "a", "tags": ["verb"]}]})

    def test_simple21(self):
        data = self.run_data("a (b)")
        self.assertEqual(data, {"related": [
            {"word": "a", "alt": "b"}]})

    def test_simple22(self):
        data = self.run_data("human (Homo sapiens)")
        self.assertEqual(data, {"related": [
            {"word": "human", "taxonomic": "Homo sapiens"}]})

    def test_simple23(self):
        data = self.run_data("neanderthalin ihminen (×Homo neanderthalis)")
        self.assertEqual(data, {"related": [
            {"word": "neanderthalin ihminen",
             "tags": ["extinct"],
             "taxonomic": "Homo neanderthalis"}]})

    def test_simple24(self):
        data = self.run_data("×Dinosauria")
        self.assertEqual(data, {"related": [
            {"word": "Dinosauria",
             "tags": ["extinct"]}]})

    def test_simple25(self):
        data = self.run_data("foo (×Dummy)")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "alt": "Dummy",
             "tags": ["extinct"]}]})

    def test_simple26(self):
        data = self.run_data('foo "a horse"')
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "english": "a horse"}]})

    def test_simple27(self):
        data = self.run_data("起徛 (Zhangzhou Hokkien)")
        self.assertEqual(data, {"related": [
            {"word": "起徛",
             "tags": ["Zhangzhou-Hokkien"]}]})

    def test_simple28(self):
        data = self.run_data("全部 (quánbù) (attributive)")
        self.assertEqual(data, {"related": [
            {"word": "全部",
             "roman": "quánbù",
             "tags": ["attributive"]}]})

    def test_simple29(self):
        data = self.run_data("整齊／整齐 (zhěngqí)")
        self.assertEqual(data, {"related": [
            {"word": "整齊",
             "roman": "zhěngqí"},
            {"word": "整齐",
             "roman": "zhěngqí"},
        ]})

    def test_simple30(self):
        data = self.run_data("甘心 (gānxīn) (usually in the negative)")
        self.assertEqual(data, {"related": [
            {"word": "甘心",
             "tags": ["usually", "with-negation"],
             "roman": "gānxīn"},
        ]})

    def test_reconstruction1(self):
        data = self.run_data("*foo", is_reconstruction=True)
        self.assertEqual(data, {"related": [{"word": "foo"}]})

    def test_reconstruction2(self):
        data = self.run_data("*foo", is_reconstruction=False)
        self.assertEqual(data, {"related": [{"word": "*foo"}]})

    def test_dup1(self):
        # Duplicates should get eliminated
        data = self.run_data("foo, bar, foo")
        self.assertEqual(data, {"related": [
            {"word": "foo"},
            {"word": "bar"},
        ]})

    def test_senseonly1(self):
        # In this case, parse_linkage_item_text should return the sense
        # for follow-on linkages
        self.wxr.wtp.start_page("滿")
        self.wxr.wtp.start_section("Chinese")
        data = {}
        ret = parse_linkage_item_text(self.wxr, "滿", data, "synonyms",
                                      "(arrogant):", None, [], [], False)
        self.assertEqual(ret, "arrogant")

    def test_sensearg1(self):
        data = self.run_data("foo", sense="test sense")
        self.assertEqual(data, {"related": [{"word": "foo",
                                             "sense": "test sense"}]})

    def test_sensearg2(self):
        data = self.run_data("foo", sense="intransitive verbs")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "tags": ["intransitive", "verb"]}]})

    def test_ignore1(self):
        self.run_empty("Historical and regional synonyms of foo")

    def test_ignore2(self):
        self.run_empty("edit data")

    def test_ignore3(self):
        self.run_empty("or these other third-person pronouns")

    def test_ignore4(self):
        self.run_empty("Signal flag: foobar")

    def test_ignore5(self):
        self.run_empty("Semaphore: foobar")

    def test_ignore6(self):
        self.run_empty("introduced in Unicode 1.2.3")

    def test_ignore7(self):
        self.run_empty("Any of Thesaurus:foobar")

    def test_ignore8(self):
        self.run_empty("See contents of Category:foobar")

    def test_ignore9(self):
        self.run_empty("domesticated animal: ,,,")

    def test_ignore10(self):
        self.run_empty("intransitive: ,, ")

    def test_ignore11(self):
        self.run_empty("(intransitive)")

    def test_ignore12(self):
        self.run_empty("(intransitive) ,,")

    def test_ignore13(self):
        # self-links should be ignored
        self.run_empty("testpage")

    def test_ignore_paren1(self):
        data = self.run_data("foo (foobar used as whatever)")
        self.assertEqual(data, {"related": [{"word": "foo"}]})

    def test_ignore_paren2(self):
        data = self.run_data("foo (foobar from Etymology 1)")
        self.assertEqual(data, {"related": [{"word": "foo"}]})

    def test_taxonomic1(self):
        data = self.run_data("Hominidae - family")
        self.assertEqual(data, {"related": [{"english": "family",
                                             "word": "Hominidae"}]})
    def test_taxonomic2(self):
        data = self.run_data("Aotidae, Atelidae - families")
        self.assertEqual(data, {"related": [{"english": "family",
                                             "word": "Aotidae"},
                                            {"english": "family",
                                             "word": "Atelidae"}]})
    def test_taxonomic3(self):
        # Currently no special handling for taxonomic terms in linkages.
        # This might change in the future.
        data = self.run_data("Homo sapiens")
        self.assertEqual(data, {"related": [{"word": "Homo sapiens"}]})

    def test_taxonomic4(self):
        data = self.run_data("(order): Eukaryota - superkingdom; "
                             "Animalia - kingdom")
        self.assertEqual(data, {"related": [
            {"sense": "order", "english": "superkingdom", "word": "Eukaryota"},
            {"sense": "order", "english": "kingdom", "word": "Animalia"}]})

    def test_truncate1(self):
        data = self.run_data("(blood type): from antigen B")
        self.assertEqual(data, {"related": [
            {"word": "antigen B", "sense": "blood type"}]})

    def test_truncate2(self):
        data = self.run_data("(symbol for boron): abbreviation of boron")
        self.assertEqual(data, {"related": [
            {"word": "boron",
             "tags": ["abbreviation"],
             "sense": "symbol for boron"}]})

    def test_truncate3(self):
        data = self.run_data("(cricket, balls): abbreviation of balls")
        self.assertEqual(data, {"related": [
            {"word": "balls",
             "tags": ["abbreviation"],
             "topics": ["cricket", "ball-games", "games", "sports",
                        "hobbies", "lifestyle"],
             "sense": "balls",
            }]})

    def test_truncate4(self):
        data = self.run_data("(billion): abbreviation of billion")
        self.assertEqual(data, {"related": [
            {"word": "billion",
             "tags": ["abbreviation"],
             "sense": "billion",
            }]})

    def test_truncate5(self):
        data = self.run_data("Homo sapiens on Wikispecies")
        self.assertEqual(data, {"related": [
            {"word": "Homo sapiens"}
        ]})

    def test_truncate6(self):
        data = self.run_data("dog on English Wiktionary.")
        self.assertEqual(data, {"related": [
            {"word": "dog"}
        ]})

    def test_prefix1(self):
        data = self.run_data("animal: pet, companion")
        self.assertEqual(data, {"related": [
            {"sense": "animal", "word": "pet"},
            {"sense": "animal", "word": "companion"}]})

    def test_prefix2(self):
        data = self.run_data("nouns: pet, companion")
        self.assertEqual(data, {"related": [
            {"tags": ["noun"], "word": "pet"},
            {"tags": ["noun"], "word": "companion"}]})

    def test_prefix3(self):
        data = self.run_data("finance: stock, trading")
        self.assertEqual(data, {"related": [
            {"topics": ["finance", "business"], "word": "stock"},
            {"topics": ["finance", "business"], "word": "trading"}]})

    def test_prefix4(self):
        data = self.run_data("(animal): pet, companion")
        self.assertEqual(data, {"related": [
            {"sense": "animal", "word": "pet"},
            {"sense": "animal", "word": "companion"}]})

    def test_prefix5(self):
        data = self.run_data("(nouns): pet, companion")
        self.assertEqual(data, {"related": [
            {"tags": ["noun"], "word": "pet"},
            {"tags": ["noun"], "word": "companion"}]})

    def test_prefix6(self):
        data = self.run_data("(finance): stock, trading")
        self.assertEqual(data, {"related": [
            {"topics": ["finance", "business"], "word": "stock"},
            {"topics": ["finance", "business"], "word": "trading"}]})

    def test_prefix7(self):
        # XXX should this affect first linkage only or all of them?
        data = self.run_data("(animal) pet, companion")
        self.assertEqual(data, {"related": [
            {"sense": "animal", "word": "pet"},
            {"word": "companion"}]})

    def test_prefix8(self):
        # XXX should this affect first linkage only or all of them?
        data = self.run_data("(nouns) pet, companion")
        self.assertEqual(data, {"related": [
            {"tags": ["noun"], "word": "pet"},
            {"word": "companion"}]})

    def test_prefix9(self):
        # XXX should this affect first linkage only or all of them?
        data = self.run_data("(finance) stock, trading")
        self.assertEqual(data, {"related": [
            {"topics": ["finance", "business"], "word": "stock"},
            {"word": "trading"}]})

    def test_prefix10(self):
        data = self.run_data("(intransitive, formal, to wander about) meander")
        self.assertEqual(data, {"related": [
            {"sense": "to wander about",
             "tags": ["formal", "intransitive"],
             "word": "meander"}]})

    def test_prefix11(self):
        data = self.run_data("(to wander about, intransitive, formal) meander")
        self.assertEqual(data, {"related": [
            {"sense": "to wander about",
             "tags": ["formal", "intransitive"],
             "word": "meander"}]})

    def test_prefix12(self):
        data = self.run_data("chemistry (slang): foo")
        self.assertEqual(data, {"related": [
            {"tags": ["slang"],
             "topics": ["chemistry", "physical-sciences", "natural-sciences"],
             "word": "foo"}]})

    def test_prefix13(self):
        data = self.run_data("foo: chemistry (slang)")
        self.assertEqual(data, {"related": [
            {"tags": ["slang"],
             "topics": ["chemistry", "physical-sciences", "natural-sciences"],
             "word": "foo"}]})

    def test_prefix14(self):
        data = self.run_data("(2): foo", senses=[
            {"glosses": ["sense1"]},
            {"glosses": ["sense2", "sense2b"]},
            {"glosses": ["sense3"]}])
        self.assertEqual(data, {"related": [
            {"sense": "sense2; sense2b",
             "word": "foo"}]})

    def test_prefix15(self):
        data = self.run_data("(3): foo", senses=[
            {"glosses": ["sense1"]},
            {"glosses": ["sense2", "sense2b"]},
            {"glosses": ["sense3"]}])
        self.assertEqual(data, {"related": [
            {"sense": "sense3",
             "word": "foo"}]})

    def test_prefix16(self):
        # Triggers an error due to invalid gloss reference
        wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        data = self.run_data("(4): foo", wxr=wxr, senses=[
            {"glosses": ["sense1"]},
            {"glosses": ["sense2", "sense2b"]},
            {"glosses": ["sense3"]}])
        self.assertEqual(data, {"related": [
            {"word": "foo"}]})
        self.assertNotEqual(wxr.wtp.debugs, [])

    def test_prefix17(self):
        data = self.run_data("(3): foo",
                             sense="initial sense",
                             senses=[
            {"glosses": ["sense1"]},
            {"glosses": ["sense2", "sense2b"]},
            {"glosses": ["sense3"]}])
        self.assertEqual(data, {"related": [
            {"sense": "initial sense; sense3",
             "word": "foo"}]})

    def test_prefix18(self):
        # Triggers error due to invalid prefix
        wxr = WiktextractContext(Wtp(), WiktionaryConfig())
        data = self.run_data("dsafjdasfkldjas: foo", wxr=wxr)
        self.assertEqual(data, {"related": [{"word": "foo"}]})
        self.assertNotEqual(wxr.wtp.debugs, [])

    def test_prefix19(self):
        data = self.run_data("NATO phonetic: Bravo")
        self.assertEqual(data, {"related": [
            {"word": "Bravo", "english": "NATO phonetic"}]})

    def test_prefix20(self):
        data = self.run_data("Morse code: –···")
        self.assertEqual(data, {"related": [
            {"word": "–···", "english": "Morse code"}]})

    def test_prefix21(self):
        data = self.run_data("Braille: ⠃")
        self.assertEqual(data, {"related": [
            {"word": "⠃", "english": "Braille"}]})

    def test_prefix22(self):
        data = self.run_data("something else in English: foo")
        self.assertEqual(data, {"related": [
            {"word": "foo", "sense": "something else in English"}]})

    def test_prefix23(self):
        data = self.run_data("(intransitive, transitive, verb, frequentative): "
                             "foo")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "tags": ["frequentative", "intransitive", "transitive", "verb"]}]})

    def test_prefix24(self):
        data = self.run_data("foo: verb")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "tags": ["verb"]}]})

    def test_prefix25(self):
        data = self.run_data("(intransitive, to run, transitive, "
                             "ditransitive): foo")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "sense": "to run",
             "tags": ["ditransitive", "intransitive", "transitive"]}]})

    def test_prefix26(self):
        data = self.run_data("(to run, transitive): foo")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "sense": "to run",
             "tags": ["transitive"]}]})

    def test_prefix27(self):
        data = self.run_data("alternative (B): foo")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "sense": "alternative (B)"}]})

    def test_prefix28(self):
        data = self.run_data("(human, Homo sapiens): foo")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "sense": "human, Homo sapiens"}]})

    def test_prefix29(self):
        data = self.run_data("Homo sapiens: foo (human)")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "english": "human",
             "sense": "Homo sapiens"}]})

    def test_prefix30(self):
        data = self.run_data("^() foo")
        self.assertEqual(data, {"related": [
            {"word": "foo"},
        ]})

    def test_prefix31(self):
        data = self.run_data("^( ) foo")
        self.assertEqual(data, {"related": [
            {"word": "foo"},
        ]})

    def test_prefix32(self):
        data = self.run_data("^ foo")
        self.assertEqual(data, {"related": [
            {"word": "foo"},
        ]})

    def test_prefix33(self):
        data = self.run_data('(any member of the suborder (sometimes superfamily) Feliformia or Feloidea): feliform ("cat-like" carnivoran), feloid (compare Caniformia, Canoidea)')
        self.assertEqual(data, {"related": [
            {"sense": "any member of the suborder (sometimes superfamily) Feliformia or Feloidea",
             "word": "feliform",
             "english": 'cat-like; carnivoran'},
            {"sense": "any member of the suborder (sometimes superfamily) Feliformia or Feloidea",
             "word": "feloid",
             "english": "compare Caniformia, Canoidea"},
        ]})

    def test_suffix1(self):
        data = self.run_data("pet (animal), companion")
        self.assertEqual(data, {"related": [
            {"english": "animal", "word": "pet"},
            {"word": "companion"}]})

    def test_suffix2(self):
        data = self.run_data("pet, companion (animal)")
        self.assertEqual(data, {"related": [
            {"word": "pet"},
            {"english": "animal", "word": "companion"}]})

    def test_suffix3(self):
        data = self.run_data("pet, companion (animal) (female)")
        self.assertEqual(data, {"related": [
            {"word": "pet"},
            {"english": "animal", "tags": ["feminine"], "word": "companion"}]})

    def test_suffix4(self):
        data = self.run_data("pet, companion (female, animal)")
        self.assertEqual(data, {"related": [
            {"word": "pet"},
            {"english": "animal", "tags": ["feminine"], "word": "companion"}]})

    def test_suffix5(self):
        data = self.run_data("pet (verb), companion (female, animal)")
        self.assertEqual(data, {"related": [
            {"tags": ["verb"], "word": "pet"},
            {"english": "animal", "tags": ["feminine"], "word": "companion"}]})

    def test_suffix6(self):
        data = self.run_data("foo, bar - verbs")
        self.assertEqual(data, {"related": [
            {"tags": ["verb"], "word": "foo"},
            {"tags": ["verb"], "word": "bar"},
        ]})

    def test_suffix7(self):
        data = self.run_data("a - b")
        self.assertEqual(data, {"related": [
            {"word": "a - b"},
        ]})

    def test_suffix8(self):
        data = self.run_data("(no superlative): foo, bar - adjectives")
        self.assertEqual(data, {"related": [
            {"tags": ["adjective", "no-superlative"], "word": "foo"},
            {"tags": ["adjective", "no-superlative"], "word": "bar"},
        ]})

    def test_eq1(self):
        data = self.run_data("luoda = to create")
        self.assertEqual(data, {"related": [
            {"word": "luoda", "english": "to create"}]})

    def test_eq2(self):
        # This should also work in the opposite order (and it is used both ways)
        data = self.run_data("to create = luoda")
        self.assertEqual(data, {"related": [
            {"word": "luoda", "english": "to create"}]})

    def test_gender1(self):
        data = self.run_data("foo f", lang="Swedish")
        self.assertEqual(data, {"related": [
            {"tags": ["feminine"], "word": "foo"}]})

    def test_gender2(self):
        data = self.run_data("foo m", lang="Swedish")
        self.assertEqual(data, {"related": [
            {"tags": ["masculine"], "word": "foo"}]})

    def test_gender3(self):
        data = self.run_data("foo n", lang="Swedish")
        self.assertEqual(data, {"related": [
            {"tags": ["neuter"], "word": "foo"}]})

    def test_gender4(self):
        # XXX "common" should distinguish gender vs. frequent meanings
        data = self.run_data("foo c", lang="Swedish")
        self.assertEqual(data, {"related": [
            {"tags": ["common-gender"], "word": "foo"}]})

    def test_gender5(self):
        # Numeric inflection classes should only be interpreted for certain
        # languages (e.g., Bantu languages)
        wxr = WiktextractContext(Wtp(), WiktionaryConfig())  # To allow debug messages
        data = self.run_data("foo 1", lang="Swedish", wxr=wxr)
        self.assertEqual(data, {"related": [
            {"word": "foo 1"}]})

    def test_gender6(self):
        data = self.run_data("foo 1", lang="Zulu")
        self.assertEqual(data, {"related": [
            {"tags": ["class-1"], "word": "foo"}]})

    def test_gender7(self):
        data = self.run_data("foo 5/6", lang="Zulu")
        self.assertEqual(data, {"related": [
            {"tags": ["class-5", "class-6"], "word": "foo"}]})

    def test_gender8(self):
        data = self.run_data("foo 1a", lang="Zulu")
        self.assertEqual(data, {"related": [
            {"tags": ["class-1a"], "word": "foo"}]})

    def test_gender9(self):
        # These special inflection class markers should only be recognized
        # for certain languages
        data = self.run_data("foo mu", lang="Swahili")
        self.assertEqual(data, {"related": [
            {"tags": ["class-18"], "word": "foo"}]})

    def test_gender10(self):
        # Make sure the marker with "or" is handled properly
        data = self.run_data("foo ki or vi", lang="Swahili")
        self.assertEqual(data, {"related": [
            {"tags": ["class-7", "class-8"], "word": "foo"}]})

    def test_gender11(self):
        # For languages that don't recognize these markers, the "or" should
        # split linkage into two
        data = self.run_data("foo ki or vi", lang="English")
        self.assertEqual(data, {"related": [
            {"word": "foo ki"},
            {"word": "vi"}]})

    def test_gender12(self):
        data = self.run_data("foo 1 or 2", lang="Ngazidja Comorian")
        self.assertEqual(data, {"related": [
            {"word": "foo",
             "tags": ["class-1", "class-2"]},
        ]})

    def test_gender13(self):
        # They should not be interpreted for other languages
        wxr = WiktextractContext(Wtp(), WiktionaryConfig())  # To allow debug messages
        data = self.run_data("foo 1 or 2", lang="English", wxr=wxr)
        self.assertEqual(data, {"related": [
            {"word": "foo 1"},
            {"word": "2"},
        ]})

    def test_gender14(self):
        # pants/English/Translations
        data = self.run_data("kelnės f or n", lang="Lithuanian")
        self.assertEqual(data, {"related": [
            {"word": "kelnės", "tags": ["feminine", "neuter"]},
        ]})

    def test_gender15(self):
        # inclusive or/English/Translations
        wxr = WiktextractContext(Wtp(), WiktionaryConfig())  # To allow debug messages
        data = self.run_data("μη αποκλειστικό or n (mi apokleistikó or)",
                             lang="Greek", word="inclusive or", wxr=wxr)
        self.assertEqual(data, {"related": [
            {"word": "μη αποκλειστικό or", "tags": ["neuter"],
             "roman": "mi apokleistikó or"},
        ]})

    def test_gender16(self):
        # simplified from wife/English/Translations
        data = self.run_data("ווײַב‎ n or f, פֿרוי‎ f (froy)",
                             lang="Yiddish")
        print(json.dumps(data, indent=2, sort_keys=True))
        self.assertEqual(data, {"related": [
            {"word": "ווײַב‎", "tags": ["feminine", "neuter"]},
            {"word": "פֿרוי‎", "tags": ["feminine"], "roman": "froy"},
        ]})

    def test_gender16orig(self):
        # wife/English/Translations
        data = self.run_data("ווײַב‎ n (vayb) or f, פֿרוי‎ f (froy)",
                             lang="Yiddish")
        self.assertEqual(data, {"related": [
            {"word": "ווײַב‎", "tags": ["feminine", "neuter"],
             "roman": "vayb"},
            {"word": "פֿרוי‎", "tags": ["feminine"], "roman": "froy"},
        ]})

    def test_gender17(self):
        # homonym/English/Translations/French
        data = self.run_data("homonyme m or n",
                             lang="French")
        self.assertEqual(data, {"related": [
            {"word": "homonyme", "tags": ["masculine", "neuter"]},
        ]})

    def test_gender18(self):
        # dragonfly/Eng/Tr/Zulu
        data = self.run_data("uzekamanzi 1a or 2a",
                             lang="Zulu")
        self.assertEqual(data, {"related": [
            {"word": "uzekamanzi", "tags": ["class-1a", "class-2a"]},
        ]})

    def test_gender19(self):
        # Spanish Netherlands/Tr/French
        data = self.run_data("Pays-Bas espagnois pl or m",
                             lang="French")
        self.assertEqual(data, {"related": [
            {"word": "Pays-Bas espagnois",
             "tags": ["masculine", "plural", "singular"]},
        ]})

    def test_begining_tags1(self):
        data = self.run_data("frequentative juoksennella, cohortative juostaan",
                             lang="Finnish")
        self.assertEqual(data, {"related": [
            {"tags": ["frequentative"], "word": "juoksennella"},
            {"tags": ["cohortative"], "word": "juostaan"}]})

    def test_begining_tags2(self):
        data = self.run_data("frequentative", lang="Finnish")
        self.assertEqual(data, {"related": [
            {"word": "frequentative"}]})

    def test_jp1(self):
        data = self.run_data("一犬 (ikken): one dog", lang="Japanese",
                             field="compounds", ruby=[("一犬", "いっけん")])
        self.assertEqual(data, {"compounds": [
            {"word": "一犬",
             "roman": "ikken",
             "ruby": [("一犬", "いっけん")],
             "english": "one dog"}]})

    def test_jp2(self):
        # This twisted test just tries to cover a rare code path
        data = self.run_data("一犬 (ikken): one dog - family")
        self.assertEqual(data, {"related": [
            {"word": "一犬",
             "roman": "ikken",
             "english": "family; one dog"}]})

    def test_jp3(self):
        # This synthetic test tries to cover a case where there is also
        # an "alt" in the parentheses
        data = self.run_data("一犬 (滿洲, ikken): one dog")
        self.assertEqual(data, {"related": [
            {"word": "一犬",
             "alt": "滿洲",
             "roman": "ikken",
             "english": "one dog"}]})

    def test_ko1(self):
        data = self.run_data("만주 (滿洲, Manju, “Manchuria”)",
                             lang="Korean")
        self.assertEqual(data, {"related": [
            {"word": "만주",
             "alt": "滿洲",
             "roman": "Manju",
             "english": "Manchuria"}]})

    def test_zh1(self):
        data = self.run_data("(to be brimming with): 充滿／充满 (chōngmǎn), "
                             "充盈 (chōngyíng), 洋溢 (yángyì)",
                             field="synonyms")
        self.assertEqual(data, {"synonyms": [
            {"sense": "to be brimming with",
             "word": "充滿",
             "roman": "chōngmǎn"},
            {"sense": "to be brimming with",
             "word": "充满",
             "roman": "chōngmǎn"},
            {"sense": "to be brimming with",
             "word": "充盈",
             "roman": "chōngyíng"},
            {"sense": "to be brimming with",
             "word": "洋溢",
             "roman": "yángyì"}]})

    def test_papersizes1(self):
        data = self.run_data("(A paper sizes): 2A0   A0   A1   A2   A3   A4   "
                             "A5   A6   A7   A8   A9   A10")
        self.assertEqual(data, {"related": [
            {"sense": "A paper sizes", "word": "2A0"},
            {"sense": "A paper sizes", "word": "A0"},
            {"sense": "A paper sizes", "word": "A1"},
            {"sense": "A paper sizes", "word": "A2"},
            {"sense": "A paper sizes", "word": "A3"},
            {"sense": "A paper sizes", "word": "A4"},
            {"sense": "A paper sizes", "word": "A5"},
            {"sense": "A paper sizes", "word": "A6"},
            {"sense": "A paper sizes", "word": "A7"},
            {"sense": "A paper sizes", "word": "A8"},
            {"sense": "A paper sizes", "word": "A9"},
            {"sense": "A paper sizes", "word": "A10"}]})

    def test_papersizes2(self):
        data = self.run_data("  (B paper sizes): B0   B1   B2   B3   B4   "
                             "B5   B6   B7   B8   B9   B10        ")
        self.assertEqual(data, {"related": [
            {"sense": "B paper sizes", "word": "B0"},
            {"sense": "B paper sizes", "word": "B1"},
            {"sense": "B paper sizes", "word": "B2"},
            {"sense": "B paper sizes", "word": "B3"},
            {"sense": "B paper sizes", "word": "B4"},
            {"sense": "B paper sizes", "word": "B5"},
            {"sense": "B paper sizes", "word": "B6"},
            {"sense": "B paper sizes", "word": "B7"},
            {"sense": "B paper sizes", "word": "B8"},
            {"sense": "B paper sizes", "word": "B9"},
            {"sense": "B paper sizes", "word": "B10"}]})

    def test_script1(self):
        data = self.run_data("(Arabic digits): 0 1 2 3 4 5 6 7 8 9")
        self.assertEqual(data, {"related": [
            {"tags": ["Arabic", "digit"], "word": "0"},
            {"tags": ["Arabic", "digit"], "word": "1"},
            {"tags": ["Arabic", "digit"], "word": "2"},
            {"tags": ["Arabic", "digit"], "word": "3"},
            {"tags": ["Arabic", "digit"], "word": "4"},
            {"tags": ["Arabic", "digit"], "word": "5"},
            {"tags": ["Arabic", "digit"], "word": "6"},
            {"tags": ["Arabic", "digit"], "word": "7"},
            {"tags": ["Arabic", "digit"], "word": "8"},
            {"tags": ["Arabic", "digit"], "word": "9"}]})

    def test_script2(self):
        data = self.run_data("(Latin script):  Aa  Bb  Cc  Dd  Ee  Ff  Gg  Hh  "
                             "Ii  Jj  Kk  Ll  Mm  Nn  Oo  Pp  Qq  Rr  Sſs  Tt  "
                             "Uu  Vv  Ww  Xx  Yy  Zz")
        self.assertEqual(data, {"related": [
            {"tags": ["Latin", "character"], "word": "A"},
            {"tags": ["Latin", "character"], "word": "a"},
            {"tags": ["Latin", "character"], "word": "B"},
            {"tags": ["Latin", "character"], "word": "b"},
            {"tags": ["Latin", "character"], "word": "C"},
            {"tags": ["Latin", "character"], "word": "c"},
            {"tags": ["Latin", "character"], "word": "D"},
            {"tags": ["Latin", "character"], "word": "d"},
            {"tags": ["Latin", "character"], "word": "E"},
            {"tags": ["Latin", "character"], "word": "e"},
            {"tags": ["Latin", "character"], "word": "F"},
            {"tags": ["Latin", "character"], "word": "f"},
            {"tags": ["Latin", "character"], "word": "G"},
            {"tags": ["Latin", "character"], "word": "g"},
            {"tags": ["Latin", "character"], "word": "H"},
            {"tags": ["Latin", "character"], "word": "h"},
            {"tags": ["Latin", "character"], "word": "I"},
            {"tags": ["Latin", "character"], "word": "i"},
            {"tags": ["Latin", "character"], "word": "J"},
            {"tags": ["Latin", "character"], "word": "j"},
            {"tags": ["Latin", "character"], "word": "K"},
            {"tags": ["Latin", "character"], "word": "k"},
            {"tags": ["Latin", "character"], "word": "L"},
            {"tags": ["Latin", "character"], "word": "l"},
            {"tags": ["Latin", "character"], "word": "M"},
            {"tags": ["Latin", "character"], "word": "m"},
            {"tags": ["Latin", "character"], "word": "N"},
            {"tags": ["Latin", "character"], "word": "n"},
            {"tags": ["Latin", "character"], "word": "O"},
            {"tags": ["Latin", "character"], "word": "o"},
            {"tags": ["Latin", "character"], "word": "P"},
            {"tags": ["Latin", "character"], "word": "p"},
            {"tags": ["Latin", "character"], "word": "Q"},
            {"tags": ["Latin", "character"], "word": "q"},
            {"tags": ["Latin", "character"], "word": "R"},
            {"tags": ["Latin", "character"], "word": "r"},
            {"tags": ["Latin", "character"], "word": "S"},
            {"tags": ["Latin", "character"], "word": "ſ"},
            {"tags": ["Latin", "character"], "word": "s"},
            {"tags": ["Latin", "character"], "word": "T"},
            {"tags": ["Latin", "character"], "word": "t"},
            {"tags": ["Latin", "character"], "word": "U"},
            {"tags": ["Latin", "character"], "word": "u"},
            {"tags": ["Latin", "character"], "word": "V"},
            {"tags": ["Latin", "character"], "word": "v"},
            {"tags": ["Latin", "character"], "word": "W"},
            {"tags": ["Latin", "character"], "word": "w"},
            {"tags": ["Latin", "character"], "word": "X"},
            {"tags": ["Latin", "character"], "word": "x"},
            {"tags": ["Latin", "character"], "word": "Y"},
            {"tags": ["Latin", "character"], "word": "y"},
            {"tags": ["Latin", "character"], "word": "Z"},
            {"tags": ["Latin", "character"], "word": "z"},
        ]})

    def test_script3(self):
        data = self.run_data("(Variations of letter B):  Ḃḃ  Ḅḅ  Ḇḇ  Ƀƀ  Ɓɓ  Ƃƃ  ᵬ  ᶀ  ʙ  Ｂｂ  ȸ  ℔  Ꞗꞗ")
        self.assertEqual(data, {"related": [
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ḃ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ḃ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ḅ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ḅ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ḇ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ḇ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ƀ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ƀ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ɓ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ɓ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ƃ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ƃ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ᵬ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ᶀ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ʙ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ｂ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ｂ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ȸ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "℔"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "Ꞗ"},
            {"sense": "Variations of letter B",
             "tags": ["letter"],
             "word": "ꞗ"},
        ]})

    def test_script4(self):
        # This should get ignored
        data = self.run_data('For more variations, see Appendix:Variations of "b".')
        self.assertEqual(data, {})

    def test_script5(self):
        data = self.run_data('(other scripts) Β (B, “Beta”), Б (B, “Be”), '
                             'В (V, “Ve”), ב‎ (b, “beth”)')
        self.assertEqual(data, {"related": [
            {"word": "Β", "roman": "B", "english": "Beta",
             "sense": "other scripts"},
            {"word": "Б", "roman": "B", "english": "Be"},
            {"word": "В", "roman": "V", "english": "Ve"},
            # XXX what should happen with the left-to-right mark here?
            {"word": "ב\u200e", "roman": "b", "english": "beth"},
        ]})

    def test_script6(self):
        data = self.run_data("(Latin-script letters) letter; A a, B b, C c, "
                             "D d, E e, F f, G g, H h, I i, J j, K k, L l, "
                             "M m, N n, O o, P p, Q q, R r, S s, T t, U u, "
                             "V v, W w, X x, Y y, Z z", lang="English")
        self.assertEqual(data, {"related": [
            {"tags": ["Latin", "letter"], "word": "letter"},
            {"tags": ["Latin", "letter"], "word": "A"},
            {"tags": ["Latin", "letter"], "word": "a"},
            {"tags": ["Latin", "letter"], "word": "B"},
            {"tags": ["Latin", "letter"], "word": "b"},
            {"tags": ["Latin", "letter"], "word": "C"},
            {"tags": ["Latin", "letter"], "word": "c"},
            {"tags": ["Latin", "letter"], "word": "D"},
            {"tags": ["Latin", "letter"], "word": "d"},
            {"tags": ["Latin", "letter"], "word": "E"},
            {"tags": ["Latin", "letter"], "word": "e"},
            {"tags": ["Latin", "letter"], "word": "F"},
            {"tags": ["Latin", "letter"], "word": "f"},
            {"tags": ["Latin", "letter"], "word": "G"},
            {"tags": ["Latin", "letter"], "word": "g"},
            {"tags": ["Latin", "letter"], "word": "H"},
            {"tags": ["Latin", "letter"], "word": "h"},
            {"tags": ["Latin", "letter"], "word": "I"},
            {"tags": ["Latin", "letter"], "word": "i"},
            {"tags": ["Latin", "letter"], "word": "J"},
            {"tags": ["Latin", "letter"], "word": "j"},
            {"tags": ["Latin", "letter"], "word": "K"},
            {"tags": ["Latin", "letter"], "word": "k"},
            {"tags": ["Latin", "letter"], "word": "L"},
            {"tags": ["Latin", "letter"], "word": "l"},
            {"tags": ["Latin", "letter"], "word": "M"},
            {"tags": ["Latin", "letter"], "word": "m"},
            {"tags": ["Latin", "letter"], "word": "N"},
            {"tags": ["Latin", "letter"], "word": "n"},
            {"tags": ["Latin", "letter"], "word": "O"},
            {"tags": ["Latin", "letter"], "word": "o"},
            {"tags": ["Latin", "letter"], "word": "P"},
            {"tags": ["Latin", "letter"], "word": "p"},
            {"tags": ["Latin", "letter"], "word": "Q"},
            {"tags": ["Latin", "letter"], "word": "q"},
            {"tags": ["Latin", "letter"], "word": "R"},
            {"tags": ["Latin", "letter"], "word": "r"},
            {"tags": ["Latin", "letter"], "word": "S"},
            {"tags": ["Latin", "letter"], "word": "s"},
            {"tags": ["Latin", "letter"], "word": "T"},
            {"tags": ["Latin", "letter"], "word": "t"},
            {"tags": ["Latin", "letter"], "word": "U"},
            {"tags": ["Latin", "letter"], "word": "u"},
            {"tags": ["Latin", "letter"], "word": "V"},
            {"tags": ["Latin", "letter"], "word": "v"},
            {"tags": ["Latin", "letter"], "word": "W"},
            {"tags": ["Latin", "letter"], "word": "w"},
            {"tags": ["Latin", "letter"], "word": "X"},
            {"tags": ["Latin", "letter"], "word": "x"},
            {"tags": ["Latin", "letter"], "word": "Y"},
            {"tags": ["Latin", "letter"], "word": "y"},
            {"tags": ["Latin", "letter"], "word": "Z"},
            {"tags": ["Latin", "letter"], "word": "z"},
        ]})

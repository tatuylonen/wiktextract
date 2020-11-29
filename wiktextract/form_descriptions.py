# Code for parsing linguistic form descriptions and tags for word senses
# (both the word entry head - initial part and parenthesized parts -
# and tags at the beginning of word senses)
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import Levenshtein
from wikitextprocessor import Wtp
from .datautils import data_append, data_extend, split_at_comma_semi


# Mappings for tags in template head line ends outside parentheses
xlat_head_map = {
    "m": "masculine",
    "f": "feminine",
    "n": "neuter",
    "c": "common",  # common gender in at least West Frisian
    "sg": "singular",
    "pl": "plural",
    "du": "dual",
    "inan": "inanimate",
    "anim": "animate",
    "pers": "person",  # XXX check what this really is used for? personal?
    "npers": "impersonal",
    "vir": "virile",
    "nvir": "nonvirile",
    "anml": "animal",
    "impf": "imperfect",
    "pf": "perfective",
    "?": "",
}

# General mapping for linguistic tags.  Value is a string of space-separated
# tags, or list of alternative sets of tags.  Alternative forms in the same
# category can all be listed in the same string (e.g., multiple genders).
xlat_tags_map = {
    "m.": "masculine",
    "male": "masculine",
    "f.": "feminine",
    "fem.": "feminine",
    "female": "feminine",
    "indef.": "indefinite",
    "gen.": "genitive",
    "impf.": "imperfect",
    "unc": "uncountable",
    "trans.": "transitive",
    "abbreviated": "abbreviation",
    "diminutives": "diminutive",
    "†-tari": "-tari",
    "†-nari": "-nari",
    "countable and uncountable": "countable uncountable",
    "masculine and feminine plural": "masculine feminine plural",
    "definite singular and plural": "definite singular plural",
    "plural and definite singular attributive":
    ["plural attributive", "definite singular attributive"],
    "oblique and nominative feminine singular":
    "oblique nominative feminine singular",
    "feminine and neuter plural": "feminine neuter plural",
    "feminine and neuter": "feminine neuter",
    "feminine and neuter plural": "feminine neuter plural",
    "masculine and feminine": "masculine feminine",
    "masculine and neuter": "masculine neuter",
    "masculine and plural": "masculine plural",
    "female and neuter": "feminine neuter",
    "singular and plural": "singular plural",
    "plural and weak singular": ["plural", "weak singular"],
    "dative-directional": "dative",
    "preterite and supine": "preterite supine",
    "genitive and dative": "genitive dative",
    "genitive and plural": "genitive plural",
    "dative and accusative": "dative accusative",
    "accusative/illative": "accusative illative",
    "dative and accusative singular": "dative accusative singular",
    "simple past and past participle": ["simple past", "past participle"],
    "simple past": "simple past",
    "simple present": "simple present",
    "genitive/dative": "genitive dative",
    "dative/locative": "dative locative",
    "dative/instrumental": "dative instrumental",
    "genitive/dative/locative": "genitive dative locative",
    "genitive/dative/ablative": "genitive dative ablative",
    "dative/ablative/locative": "dative ablative locative",
    "ablative/vocative": "ablative vocative",
    "ablative/locative": "ablative locative",
    "ablative/instrumental": "ablative instrumental",
    "dative/ablative": "dative ablative",
    "genitive/instrumental/locative": "genitive instrumental locative",
    "genitive/dative/locative/vocative": "genitive dative locative vocative",
    "genitive/dative/instrumental/prepositional":
    "genitive dative instrumental prepositional",
    "accusative/instrumental": "accusative instrumental",
    "dative/adverbial case": "dative adverbial",
    "dative/genitive": "dative genitive",
    "dative/genitive/instrumental": "dative genitive instrumental",
    "dative/accusative": "dative accusative",
    "dative/accusative/locative": "dative accusative locative",
    "genitive/accusative/prepositional":
    "genitive accusative prepositional",
    "genitive/dative/accusative": "genitive dative accusative",
    "genitive/animate accusative": ["genitive", "animate accusative"],
    "accusative plural and genitive plural": "accusative genitive plural",
    "first/second-declension adjective":
    "first-declension second-declension adjective",
    "class 9/10": "class-9 class-10",
    "class 5/6": "class-5 class-6",
    "class 3/4": "class-3 class-4",
    "class 7/8": "class-7 class-8",
    "class 1/2": "class-1 class-2",
    "class 11/10": "class-11 class-10",
    "first/second declension": "first-declension second-declension",
    "first/second-declension suffix":
    "first-declension second-declension suffix",
    "first/second-declension numeral plural only":
    "first-declension second-declension numeral plural-only",
    "possessive (with noun)": "possessive with-noun",
    "possessive (without noun)": "possessive without-noun",
    "informal 1st possessive": "informal first-person possessive",
    "impolite 2nd possessive": "informal second-person possessive",
    "strong personal": "strong personal pronoun",
    "weak personal": "weak personal pronoun",
    "with accusative or dative": "with-accusative with-dative",
    "with accusative or genitive": "with-accusative with-genitive",
    "with accusative or ablative": "with-accusative with-ablative",
    "nominative and accusative definite singular":
    "nominative accusative definite singular",
    "+ genitive or possessive suffix": "with-genitive with-possessive-suffix",
    "+ genitive possessive suffix or elative":
    "with-genitive with-possessive-suffix with-elative",
    "+ partitive or (less common) possessive suffix":
    "with-partitive with-possessive-suffix",
    "no perfect or supine stem": "no-perfect no-supine",
    "adverbial locative noun in the pa, ku, or mu locative classes":
    "adverbial locative",
    "comparative -": "no-comparative",
    "superlative -": "no-superlative",
    "1 declension": "first-declension",
    "4 declension": "fourth-declension",
    "5th declension": "fifth-declension",
    "feminine ? declension": "feminine",
    "masculine ? declension": "masculine",
    "1st declension": "first-declension",
    "2nd declension": "second-declension",
    "3rd declension": "third-declension",
    "4th declension": "fourth-declension",
    "2nd-person": "second-person",
    "1st-person": "first-person",
    "3rd-person": "third-person",
    "plural inv": "plural invariable",
    "plural not attested": "no-plural",
    "no plural forms": "no-plural",
    "used only predicatively": "not-attributive",
    "predicatively": "predicative",
    "present tense": "present",
    "past tense": "past",
    "feminine counterpart": "feminine",
    "masculine counterpart": "masculine",
    "passive counterpart": "passive",
    "active counterpart": "active",
    "basic stem form": "stem",
    "no supine stem": "no-supine",
    "no perfect stem": "no-perfect",
    "construct state": "construct",
    "construct form": "construct",
    "uppercase": "upper-case",
    "lowercase": "lower-case",
    "phonemic reduplicative": "reduplicated",
    "objective case": "objective",
    "first person": "first-person",
    "second person": "second-person",
    "third person": "third-person",
    "genitive case": "genitive",
    "dative case": "dative",
    "ergative cases": "ergative",
    "absolutive case": "absolutive",
    "genitive unattested": "no-genitive",
    "genitive -": "no-genitive",
    "nominative plural -": "no-nominative-plural",
    "rare/awkward": "rare",
    "found only in the imperfective tenses": "no-perfect",
    "third plural indicative": "third-person plural indicative",
    "defective verb": "defective",
    "3rd possessive": "third-person possessive",
    "active voice": "active",
    "plus genitive": "with-genitive",
    "+ genitive": "with-genitive",
    "+genitive": "with-genitive",
    "+ genitive case": "with-genitive",
    "genitive +": "with-genitive",
    "with genitive case": "with-genitive",
    "with genitive": "with-genitive",
    "+dative": "with-dative",
    "+ dative case": "with-dative",
    "+ dative": "with-dative",
    "plus dative": "with-dative",
    "with dative": "with-dative",
    "+ accusative": "with-accusative",
    "+ accusative case": "with-accusative",
    "+accusative": "with-accusative",
    "with accusative case": "with-accusative",
    "with accusative": "with-accusative",
    "plus accusative": "with-accusative",
    "governs the accusative": "with-accusative",
    "+ partitive": "with-partitive",
    "+ partitive + vastaan": "with-partitive",
    "+partitive": "with-partitive",
    "with partitive case": "with-partitive",
    "plus partitive": "with-partitive",
    "with partitive": "with-partitive",
    "+ablative": "with-ablative",
    "+ ablative": "with-ablative",
    "with ablative case": "with-ablative",
    "plus ablative": "with-ablative",
    "with ablative": "with-ablative",
    "+ subjunctive": "with-subjunctive",
    "+subjunctive": "with-subjunctive",
    "plus subjunctive": "with-subjunctive",
    "with subjunctive": "with-subjunctive",
    "+ instrumental": "with-instrumental",
    "+instrumental": "with-instrumental",
    "+ instrumental case": "with-instrumental",
    "with instrumental case": "with-instrumental",
    "with instrumental": "with-instrumental",
    "plus instrumental": "with-instrumental",
    "+ locative": "with-locative",
    "+ locative case": "with-locative",
    "with locative": "with-locative",
    "+absolutive": "with-absolutive",
    "+ absolutive": "with-absolutive",
    "with absolutive case": "with-absolutive",
    "with absolutive": "with-absolutive",
    "+ absolutive case": "with-absolutive",
    "plus absolutive": "with-absolutive",
    "+elative": "with-elative",
    "+ elative": "with-elative",
    "with elative case": "with-elative",
    "with elative": "with-elative",
    "plus elative": "with-elative",
    "+objective": "with-objective",
    "+ objective": "with-objective",
    "with objective case": "with-objective",
    "with objective": "with-objective",
    "plus objective": "with-objective",
    "+ present form": "with-present",
    "+ noun phrase] + subjunctive (verb)":
    "with-noun-phrase with-subjunctive",
    "with noun phrase": "with-noun-phrase",
    "+ [nounphrase] + subjunctive":
    "with-noun-phrase with-subjunctive",
    "+ number": "with-number",
    "with number": "with-number",
    "optative mood +": "with-optative",
    "p-past": "passive past",
    "ppp": "passive perfect participle",
    "not used in plural form": "no-plural",
    "not declined": "indeclinable",
    "interrogative adverb": "interrogative",
    "perfect tense": "perfect",
    "intensive": "emphatic",
    "changed conjunct form": "conjunct",
    "biblical hebrew pausal form": "pausal",
    "emphatic form": "emphatic",
    "emphatically": "emphatic",
    "emphatical": "emphatic",
    "standard form": "standard",
    "augmented form": "augmented",
    "active form": "active",
    "passive form": "passive",
    "mutated form": "mutated",
    "auxiliary verb": "auxiliary",
    "modal auxiliary verb": "auxiliary modal",
    "transitive verb": "transitive",
    "intransitive verb": "intransitive",
    "male equivalent": "masculine",
    "in compounds": "in-compounds",
    "in combination": "in-compounds",
    "attribute": "attributive",
    "in the past subjunctive": "past subjunctive",
    "use the subjunctive tense of the verb that follows": "with-subjunctive",
    "kyūjitai form": "kyūjitai",
    "shinjitai kanji": "shinjitai",
    "dialectical": "dialectal",
    "dialect": "dialectal",
    "possibly obsolete": "archaic",
    "19th century": "archaic",
    "dated or regional": "archaic regional",
    "archaic ortography": "archaic",
    "in the plural": "plural-only",
    "derogative": "derogatory",
    "collective sense": "collectively",
    "relatively rare": "rare",
    "very informal": "informal",
    "with a + inf.": "with-a with-infinitive",
    "with di + inf.": "with-di with-infinitive",
    "with che + subj.": "with-che with-subjunctive",
    "with inf.": "with-infinitive",
    # XXX re-enable "~ се": "with-ce",
    "strong/mixed": "strong mixed",
    "auxiliary sein": "with-sein",
    "nominative/accusative": "nominative accusative",
    "masculine/feminine": "masculine feminine",
    "masculine/neuter": "masculine neuter",
    "present/future": "present future",
    "future/present": "present future",
    "present/aoriest": "present aorist",
    "superlative degree": "superlative",
    "comparative degree": "comparative",
    "positive degree": "positive",
    "equative degree": "equative",
    "indicative and subjunctive": "indicative subjunctive",
    "indicative/subjunctive": "indicative subjunctive",
    "second/third-person": "second-person third-person",
    "singular/plural": "singular plural",
    "dual/plural": "dual plural",
    "(with savrtsobi)": "with-savrtsobi",
    "plural and definite singular": ["plural", "definite singular"],
    "feminine singular & neuter plural": ["feminine singular", "neuter plural"],
    "partitive/illative": "partitive illative",
    "oblique/nominative": "oblique nominative",
    "nominative/vocative/dative/strong genitive":
    ["nominative vocative dative", "strong genitive"],
    "non-attributive": "not-attributive",
    "nominative/vocative/instrumental":
    "nominative vocative instrumental",
    "nominative/vocative/strong genitive/dative":
    ["nominative vocative dative", "strong genitive"],
    "nominative/vocative/dative": "nominative vocative dative",
    "accusative/genitive/partitive/illative":
    "accusative genitive partitive illative",
    "nominative/vocative/accusative/genitive":
    "nominative vocative accusative genitive",
    "accusative/genitive/locative": "accusative locative genitive",
    "accusative/genitive/dative/instrumental":
    "accusative genitive dative instrumental",
    "accusative/genitive/dative": "accusative genitive dative",
    "accusative/genitive": "accusative genitive",
    "masculine/feminine/neuter": "masculine feminine neuter",
    "feminine/neuter/masculine": "masculine feminine neuter",
    "feminine/neuter": "feminine neuter",
    "present participle and present tense": ["present participle", "present"],
    "present participle and gerund": ["present participle", "gerund"],
    "all-gender": [],
    "all-case": [],
    "accusative/dative": "accusative dative",
    "accusative-singular": "accusative singular",
    "accusative-genitive": "accusative genitive",
    "dative/locative/instrumental": "dative locative instrumental",
    "dative/vocative/locative": "dative vocative locative",
    "dative/prepositional": "dative prepositional",
    "dative and ablative": "dative ablative",
    "nominative/vocative/dative and strong genitive":
    ["nominative vocative dative", "strong genitive"],
    "nominative/vocative/accusative":
    "nominative vocative accusative",
    "nominative/vocative": "nominative vocative",
    "nominative/oblique": "nominative oblique",
    "nominative/locative": "nominative locative",
    "nominative/instrumental": "nominative instrumental",
    "nominative/genitive/dative/accusative":
    "nominative genitive dative accusative",
    "nominative/genitive/dative": "nominative genitive dative",
    "nominative/genitive/accusative/vocative":
    "nominative genitive accusative vocative",
    "nominative/genitive/accusative":
    "nominative genitive accusative",
    "nominative/dative": "nominative dative",
    "nominative/accusative/vocative/instrumental":
    "nominative accusative vocative instrumental",
    "nominative/accusative/vocative": "nominative accusative vocative",
    "nominative/accusative/nominative/accusative":
    "nominative accusative",
    "nominative/accusative/nominative": "nominative accusative",
    "nominative/accusative/locative": "nominative accusative locative",
    "nominative/accusative/genitive/dative":
    "nominative accusative genitive dative",
    "nominative/accusative/genitive": "nominative accusative genitive",
    "nominative/accusative/genitive": "nominative accusative genitive",
    "nominative/accusative/dative": "nominative accusative dative",
    "nominative/accusative": "nominative accusative",
    "perfective/imperfective": "perfective imperfective",
    "animate/inanimate": "animate inanimate",
    "locative/vocative": "locative vocative",
    "prospective/agentive": "prospective agentive",
    "genitive/accusative": "genitive accusative",
    "singular/duoplural": "singular duoplural",
    "first/second/third-person":
    "first-person second-person third-person",
    "first/third/third-person": "first-person third-person",
    "first/second/second-person": "first-person second-person",
    "first/third-person": "first-person third-person",
    "first-person/second-person": "first-person second-person",
    "first-person/third-person": "first-person third-person",
    "first-person singular/third-person singular":
    "first-person third-person singular",
    "first-person singular/third-person plural":
    ["first-person singular", "third-person plural"],
    "affirmative/negative": "affirmative negative",
    "first-, second-, third-person singular subjunctive present":
    "first-person second-person third-person singular subjunctive present",
    "first-, second- and third-person singular present indicative":
    "first-person second-person third-person singular present indicative",
    "first- and third-person": "first-person third-person",
    "female equivalent": "feminine",
    "direct/oblique/vocative": "direct oblique vocative",
    "definite/plural": "definite plural",
    "agent noun": "agent",
    "third active infinitive": "third-infinitive active",
    "third passive infinitive": "third-infinitive passive",
    "British spelling": "UK",
    "eye dialect": "pronunciation-spelling",
    "enclitic and proclitic": "enclitic proclitic",
    "(hence past tense)": "past",
    "(suffix conjugation)": "suffix",
    "(suffix conjugation)": "prefix",
    "(nós)": "with-nos",
    "(eu)": "with-eu",
    "(vós)": "with-vós",
    "(tu)": "with-tu",
    "(eles)": "with-eles",
    "(elas)": "with-elas",
    "(vocês)": "with-vocês",
    "(ele, ela, also used with tu and você?)":
    "with-ele with-ela with-tu with-você",
    "(eles and elas, also used with vocês and others)":
    "with-eles with-elas with-vocês with-others",
    "(você)": "with-você",
    "(hiri)": "with-hiri",
    "(hura)": "with-hura",
    "(zuek)": "with-zuek",
    "(vós, sometimes used with vocês)": "with-vós with-vocês",
    "(gij)": "with-gij",
    "(tu, sometimes used with você)": "with-tu with-você",
    "(ele and ela, also used with você and others)":
    "with-ele with-ela with-você with-others",
    "former reform[s] only": [],
    "no construct forms": "no-construct-forms",
    "no nominative plural": "no-nominative-plural",
    "no supine": "no-supine",
    "no perfect": "no-perfect",
    "no genitive": "no-genitive",
    "no superlative": "no-superlative",
    "no comparative": "no-comparative",
    "no plural": "no-plural",
    "no singular": "plural-only",
    "not comparable": "not-comparable",
    "plurale tantum": "plurale-tantum",
    "possessive suffix": "possessive-suffix",
    "possessive determiner": "possessive-determiner",
    "pronominal state": "pronominal-state",
    "nominal state": "nominal-state",
    "form i": "form-i",
    "form ii": "form-ii",
    "form iii": "form-iii",
    "form iv": "form-iv",
    "form v": "form-v",
    "form vi": "form-vi",
    "form vii": "form-vii",
    "form viii": "form-viii",
    "form ix": "form-ix",
    "form x": "form-x",
    "form xi": "form-xi",
    "form xii": "form-xii",
    "form xiii": "form-xiii",
    "form iq": "form-iq",
    "form iiq": "form-iiq",
    "form iiiq": "form-iiiq",
    "form ivq": "form-ivq",
    "class 1": "class-1",
    "class 1a": "class-1a",
    "class 2": "class-2",
    "class 2a": "class-2a",
    "class 3": "class-3",
    "class 4": "class-4",
    "class 5": "class-5",
    "class 6": "class-6",
    "class 7": "class-7",
    "class 8": "class-8",
    "class 9": "class-9",
    "class 10": "class-10",
    "class 11": "class-11",
    "class 12": "class-12",
    "class 13": "class-13",
    "class 14": "class-14",
    "class 15": "class-15",
    "m-wa class": "m-wa-class",
    "m-mi class": "m-mi-class",
    "u class": "u-class",
    "ki-vi class": "ki-vi-class",
    "first declension": "first-declension",
    "second declension": "second-declension",
    "third declension": "third-declension",
    "fourth declension": "fourth-declension",
    "fifth declension": "fifth-declension",
    "first conjugation": "first-conjugation",
    "second conjugation": "second-conjugation",
    "third conjugation": "third-conjugation",
    "fourth conjugation": "fourth-conjugation",
    "fifth conjugation": "fifth-conjugation",
    "sixth conjugation": "sixth-conjugation",
    "seventh conjugation": "seventh-conjugation",
    "stress pattern 1": "stress-pattern-1",
    "stress pattern 2": "stress-pattern-2",
    "stress pattern 3": "stress-pattern-3",
    "stress pattern 3a": "stress-pattern-3a",
    "stress pattern 3b": "stress-pattern-3b",
    "stress pattern 4": "stress-pattern-4",
    "type p": "type-p",
    "type u": "type-u",
    "type up": "type-up",
    "type a": "type-a",
    "ordinal form of": "ordinal form-of",
    "the ordinal form of the number": "ordinal form-of",
    "the ordinal form of": "ordinal form-of",
    "the ordinal of": "ordinal form-of",
    "the ordinal number corresponding to the cardinal number":
    "ordinal form-of",
    "the ordinal form of the cardinal number": "ordinal form-of",
    "the ordinal number": "ordinal form-of",
    "used in the form": "used-in-the-form",
    "upper case": "upper-case",
    "lower case": "lower-case",
    "mixed case": "mixed-case",
    "verb form i": "verb-form-i",
    "verb form ii": "verb-form-ii",
    "pi'el construction": "pi'el-construction",
    "pa'el construction": "pa'el-construction",
    "hif'il construction": "hif'il-construction",
    "hitpa'el construction": "hitpa'el-construction",
    "pu'al construction": "pu'al-construction",
    "nif'al construction": "nif'al-construction",
    "huf'al construction": "huf'al-construction",
    "verbal noun": "verbal-noun",
    "abstract noun": "abstract-noun",
    "genitive as verbal noun": "genitive verbal-noun",
    "genitive singular as substantive": "genitive singular substantive",
    "female names": "feminine proper-noun",
    "proper name": "proper-noun",
    "proper noun": "proper-noun",
    "proper nouns": "proper-noun",
    "usually in the": "usually",
    "non-scientific usage": "non-scientific",
    "krama inggil": "krama-inggil",
    "McCune-Reischauer chŏn": "McCune-Reischauer-chŏn",
    "gender indeterminate": "gender-indeterminate",
    "singular only": "singular-only",
    "plural only": "plural-only",
    "imperative only": "imperative-only",
    "in general sense": "broadly",
    "by extension": "broadly",
    "by metonymy": "metonymically",
    "by semantic narrowing": "narrowly",
    "by semantic widening": "broadly",
    "strict sense": "strict-sense",
    "baby talk": "baby-talk",
    "middle infinitive": "middle-infinitive",
    "first infinitive": "first-infinitive",
    "second infinitive": "second-infinitive",
    "third infinitive": "third-infinitive",
    "fourth infinitive": "fourth-infinitive",
    "subjunctive I": "subjunctive-I",
    "subjunctive II": "subjunctive-II",
    "morse code": "morse-code",
    "with odd-syllable stems": "with-odd-syllable-stems",
    "old ortography": "archaic",
    "Brazilian ortography": "Brazilian",
    "European ortography": "European",
    "with noun phrase": "with-noun-phrase",
    "contracted dem-form": "contracted-dem-form",
    "Yale cen": "Yale-cen",
    "subjective pronoun": "subjective-pronoun",
    "revised jeon": "revised-jeon",
    "form used before": "archaic",
    "front vowel harmony variant": "front-vowel",
    "romanization of": "alt-of romanization",
    "romanisation of": "alt-of romanization",
    "archaic spelling of": "alt-of archaic",
    "obsolete typography of": "alt-of obsolete",
    "obsolete spelling of": "alt-of obsolete",
    "rare spelling of": "alt-of rare",
    "superseded spelling of": "alt-of archaic",
    "pronunciation spelling of": "alt-of pronunciation-spelling",
    "eye dialect spelling of": "alt-of pronunciation-spelling",
    "alternative or obsolete spelling of":
    "alt-of obsolete alternative",
    "alternative name of": "alt-of alternative",
    "nonstandard spelling of": "alt-of nonstandard",
    "US standard spelling of": "alt-of US standard",
    "US spelling of": "alt-of US",
    "alternative typography of": "alt-of alternative",
    "polytonic spelling of": "alt-of polytonic",
    "variant of": "alt-of alternative",
    "uncommon spelling of": "alt-of uncommon",
    "alternative typographic spelling of": "alt-of alternative",
    "alternative spelling of": "alt-of alternative",
    "alternative form of": "alt-of alternative",
    "alternative term for": "alt-of alternative",
    "alternative stem of": "alt-of stem alternative",
    "medieval spelling of": "alt-of obsolete",
    "post-1930s Cyrillic spelling of": "alt-of standard",
    "pre-1918 spelling of": "alt-of obsolete",
    "Switzerland and Liechtenstein standard spelling of":
    "alt-of Switzerland Liechtenstein standard",
    "form removed with the spelling reform of 2012; superseded by":
    "alt-of dated",
    "excessive spelling of": "alt-of excessive",
    "exaggerated degree of": "alt-of exaggerated",
    "defective spelling of": "alt-of misspelling",
    "alternative verbal noun of": "alt-of verbal-noun",
    "alternative conjugation of": "alt-of alternative",
    "abbreviation of": "alt-of abbreviation",
    "acronym of": "alt-of abbreviation",
    "initialism of": "alt-of abbreviation initialism",
    "contraction of": "alt-of abbreviation contraction",
    "IUPAC 3-letter abbreviation of": "alt-of abbreviation",
    "praenominal abbreviation of": "alt-of abbreviation praenominal",
    "ellipsis of": "alt-of ellipsis abbreviation",
    "clipping of": "alt-of clipping abbreviation",
    "X-system spelling of": "alt-of X-system",
    "H-system spelling of": "alt-of H-system",
    "Pinyin transcription of": "alt-of pinyin",
    "Rōmaji transcription of": "alt-of romaji",
    "visual rendering of Morse code for":
    "alt-of visual-rendering morse-code",
    "soft mutation of": "alt-of soft",
    "Non-Oxford British English standard spelling of":
    "alt-of nonstandard UK",
    "Nil standard spelling of": "alt-of UK standard",
    "nasal mutation of": "alt-of nasal mutation",
    "mixed mutation of": "alt-of mixed mutation",
    "aspirate mutation of": "alt-of aspirate mutation",
    "misspelling of": "alt-of misspelling",
    "deliberate misspelling of": "alt-of misspelling deliberate",
    "common misspelling of": "alt-of misspelling",
    "misconstruction of": "alt-of misconstruction",
    "Latin spelling of": "alt-of latin",
    "Late Anglo-Norman spelling of": "alt-of Anglo-Norman",
    "Jawi spelling of": "alt-of Jawi",
    "Hanja form of": "alt-of Hanja",
    "Hanja form? of": "alt-of Hanja",
    "Glagolitic spelling of": "alt-of Glagolitic",
    "front vowel variant of": "alt-of front-vowel",
    "front-vowel variant of": "alt-of front-vowel",
    "euphemistic spelling of": "alt-of euphemistic",
    "euphemistic reading of": "alt-of euphemistic",
    "Cyrillic spelling of": "alt-of Cyrillic",
    "British standard spellingh of": "alt-of UK standard",
    "British and Canada standard spelling of":
    "alt-of UK Canada standard",
    "Britain and Ireland standard spelling of":
    "alt-of UK Ireland standard",
    "Britain and New Zealand standard spelling of":
    "alt-of UK New-Zealand standard",
    "Britain and Canada spelling of": "alt-of UK Canada",
    "Baybayin spelling of": "alt-of Baybayin",
    "Arabic spelling of": "alt-of Arabic",
    "Formerly standard spelling of": "alt-of archaic",
    "informal spelling of": "alt-of informal",
    "Yañalif spelling of": "alt-of Yañalif",
    "traditional orthography spelling of": "alt-of traditional",
    "Taraškievica spelling of": "alt-of Taraškievica",
    "Baybayin spelling of": "alt-of Baybayin",
    "Post-1930s Cyrillic spelling of": "alt-of Cyrillic",
    "Britain spelling of": "alt-of UK",
    "linguistically informed spelling of": "alt-of literary",
    "Chinese spelling of": "alt-of China",
    "Mongolian spelling of": "alt-of Mongolia",
    "Leet spelling of": "alt-of Leet",
    "plural of": "form-of plural",
    "combining form of": "in-compounds form-of",
    "compound of": "compound-of",
    "compound of gerund of": "compound-of",
    "compound of imperative (noi form) of": "compound-of",
    "compound of imperative (tu form) of": "compound-of",
    "compound of imperative (vo form) of": "compound-of",
    "compound of imperative (voi form) of": "compound-of",
    "compound of imperative of": "compound-of",
    "compound of indicative present of": "compound-of",
    "compound of masculine plural past participle of": "compound-of",
    "compound of past participle of": "compound-of",
    "compound of present indicative of": "compound-of",
    "compound of plural past participle of": "compound-of",
    "compound of second-person singular imperative of": "compound-of",
    "compound of the gerund of": "compound-of",
    "compound of the imperfect": "compound-of",
    "compound of the infinitive": "compound-of",
    "synonym of": "synonym-of",
    "topicalized form of": "topic form-of",
    "form of": "form-of",
    "humurous": "humorous",
    "ironic": "humorous",
    "figuratively or literally": "figuratively literally",
    "figuative": "figuratively",
    "humorously": "humorous",
    "jocular": "humorous",
    "northern dialects": "dialectal",
    "archaic or loosely": "archaic broadly",
    "used attributively": "attributive",
    "used predicatively": "predicative",
    "used substatively": "substantive",
    "unofficial spelling": "nonstandard",
    "capitalised": "capitalized",
    "rhetorical question": "rhetoric",
    "old-fashioned": "dated",
    "rarely used": "rare",
    "rarely": "rare",
    "now rare": "archaic",
    "fossil word": "archaic",
    "brusque": "impolite",
    "verbs": "verb",
    "local use": "regional",
    "more generally": "broadly",
    "loosely": "broadly",
    "broad sense": "broadly",
    "hypocoristic": "familiar",
    "hyperbolic": "excessive",
    "18th century": "obsolete",
    "9th century": "obsolete",
    "17th century": "obsolete",
    "10th century": "obsolete",
    "16th century": "obsolete",
    "14th century": "obsolete",
    "12th century": "obsolete",
    "post-classical": "obsolete",
    "early 20th century": "archaic",
    "20th century": "dated",
    "mid-20th century": "dated",
    "mid-19th century": "obsolete",
    "before 20th century": "obsolete",
    "19th to 20th century": "archaic",
    "15th century": "obsolete",
    "11th century": "obsolete",
    "until early 20th century": "obsolete",
    "since the 16th century": "dated",
    "late 16th century": "obsolete",
    "late 14th century": "obsolete",
    "in usage until 20th century": "obsolete",
    "in the 17th century": "obsolete",
    "in the 16 th century": "obsolete",
    "in Scots until the seventeenth century": "obsolete",
    "in 10th century": "obsolete",
    "early 17th century": "obsolete",
    "chiefly 18th century": "obsolete",
    "chiefly 12th century": "obsolete",
    "before 16th century": "obsolete",
    "attested in the 16th century": "obsolete",
    "5th century": "obsolete",
    "19th to early 20th century": "obsolete",
    "19th-mid 20th century": "obsolete",
    "19 the century": "obsolete",
    "19th-early 20th century": "obsolete",
    "19th century": "obsolete",
    "1776-19th century": "obsolete",
    "15th-16th century": "obsolete",
    "collective": "collectively",
    "used formally in Spain": "Spain",
    "nouns": "noun",
    "with the particle lai": "with-lai",
    "adjectives": "adjective",
    "non-standard since 2012": "nonstandard",
    "colloquialism": "colloquial",
    "non-standard since 1917": "nonstandard",
    "conditional mood": "conditional",
    "figurative": "figuratively",
    "reciprocal": "reflexive",
    "compound words": "compound",
    "girl": "person feminine",
    "woman": "person feminine",
    "form of address": "term-of-address",
    "term of address": "term-of-address",
    "as a term of address": "term-of-address",
    "direct address": "term-of-address",
    "face-to-face address term": "term-of-address",
    "address": "term-of-address",
    "endearingly": "endearing",
    "elliptically": "ellipsis",
    "elegant": "formal",  # Elegant or Formal Thai
    "nonce word": "neologism",
    "attributively": "attributive",
    "poetic term": "poetic",
    "poetic meter": "poetic",
    "in certain phrases": "in-certain-phrases",
    "deprecated template usage": "deprecated-template",
    "diacritical mark": "diacritic",
}

# Translation map for topics.
# XXX revisit this mapping.  Create more fine-tuned hierarchy
topic_generalize_map = {
    "(sport)": "sports",
    "card games": "games",
    "board games": "games",
    "ball games": "games",
    "rock paper scissors": "games",
    '"manner of action"': "manner",
    "manner of action": "manner",
    "planets of the Solar system": "planets",
    "planets": "astronomy region",
    "continents": "geography region",
    "countries of Africa": "countries",
    "countries of Europe": "countries",
    "countries of Asia": "countries",
    "countries of South America": "countries",
    "countries of North America": "countries",
    "countries of Central America": "countries",
    "countries of Oceania": "countries",
    "countries": "region",
    "country": "countries",
    "the country": "countries",
    "regions of Armenia": "region",
    "region around the Ruppel river": "region",
    "geographical region": "region",
    "winegrowing region": "region",
    "the historical region": "region",
    "region": "geography location",
    "geography": "natural-sciences",
    "natural-sciences": "sciences",
    "states of India": "states",
    "states of Australia": "states",
    "states": "region",
    "city": "cities",
    "cities": "region",
    "prefectures of Japan": "prefectures",
    "prefecture": "region",
    "software": "computing",
    "text messaging": "communications telephone",
    "billiards": "games",
    "blackjack": "games",
    "backgammon": "games",
    "bridge": "games",
    "darts": "games",
    "human-sciences": "sciences",
    "anthropology": "human-sciences",
    "anthropodology": "anthropology",
    "ornithology": "biology",
    "ornitology": "ornithology",
    "entomology": "biology",
    "medicine": "sciences",
    "anatomy": "medicine",
    "bone": "anatomy",
    "body": "anatomy",
    "scientific": "sciences",
    "scholarly": "sciences",
    "neuroanatomy": "anatomy neurology",
    "neurotoxicology": "neurology toxicology",
    "neurobiology": "neurology",
    "neurophysiology": "physiology neurology",
    "nephrology": "medicine",
    "hepatology": "medicine",
    "endocrinology": "medicine",
    "gynaecology": "medicine",
    "mammology": "medicine",
    "urology": "medicine",
    "neurology": "medicine neuroscience",
    "neuroscience": "human-sciences",
    "gerontology": "medicine",
    "andrology": "medicine",
    "phycology": "botany",
    "planktology": "botany",
    "oncology": "medicine",
    "hematology": "medicine",
    "physiology": "medicine",
    "gastroenterology": "medicine",
    "surgery": "medicine",
    "pharmacology": "medicine",
    "drugs": "pharmacology",
    "cytology": "biology medicine",
    "healthcare": "government",
    "cardiology": "medicine",
    "dentistry": "medicine",
    "odontology": "dentistry",
    "pathology": "medicine",
    "toxicology": "medicine",
    "dermatology": "medicine",
    "epidemiology": "medicine",
    "psychiatry": "medicine psychology",
    "psychoanalysis": "medicine psychology",
    "phrenology": "medicine psychology",
    "psychology": "medicine human-sciences",
    "sociology": "social-science",
    "social science": "social-science",
    "social sciences": "social-science",
    "social-science": "human-sciences",
    "demographics": "demography",
    "immunology": "medicine",
    "immunologic sense": "medicine",
    "anesthesiology": "medicine",
    "xenobiology": "biology",
    "sinology": "geography",
    "psychopathology": "psychiatry",
    "histopathology": "pathology histology",
    "histology": "biology",
    "patology": "pathology",
    "virology": "medicine",
    "bacteriology": "medicine",
    "parapsychology": "psychology pseudoscience",
    "psyschology": "psychology error",
    "printing technology": "printing",
    "litography": "printing",
    "iconography": "history",
    "geomorphology": "geology",
    "phytopathology": "botany pathology",
    "bryology": "botany",
    "opthalmology": "medicine",
    "embryology": "medicine",
    "illness": "medicine",
    "parasitology": "medicine",
    "teratology": "medicine",
    "speech therapy": "medicine",
    "speech pathology": "medicine",
    "radiology": "medicine",
    "radiography": "radiology",
    "vaccinology": "medicine",
    "traumatology": "medicine",
    "microbiology": "biology medicine",
    "pulmonology": "medicine",
    "pneumology": "pulmonology",
    "biology": "natural-sciences",
    "strong topology": "topology",
    "sociobiology": "social-science biology",
    "radio technology": "electrical-engineering radio",
    "authorship": "legal",
    "volcanology": "geology",
    "gemmology": "gemology",
    "gemology": "geology",
    "conchology": "zoology",
    "comics": "literature",
    "codicology": "history",
    "zoology": "biology",
    "botany": "biology",
    "malacology": "biology",
    "geology": "geography",
    "mineralogy": "geology chemistry",
    "mineralology": "mineralogy",
    "biochemistry": "microbiology chemistry",
    "language": "linguistics",
    "grammar": "linguistics",
    "syntax": "linguistics",
    "semantics": "linguistics",
    "epistemology": "philosophy",
    "ontology": "epistemology",
    "etymology": "linguistics",
    "ethnology": "anthropology",
    "ethnography": "anthropology",
    "historical ethnography": "ethnography history",
    "entertainment industry": "economics",
    "electrochemistry": "chemistry",
    "classical studies": "history",
    "textual criticism": "linguistics",
    "nanotechnology": "engineering",
    "electromagnetism": "physics",
    "biotechnology": "engineering medicine",
    "systems theory": "mathematics",
    "computer games": "games",
    "graphic design": "arts",
    "criminology": "legal human-sciences",
    "penology": "criminology",
    "pragmatics": "linguistics",
    "morphology": "linguistics",
    "phonology": "linguistics",
    "phonetics": "phonology",
    "prosody": "phonology",
    "lexicography": "linguistics",
    "lexicology": "linguistics",
    "narratology": "linguistics",
    "linguistic": "linguistics",
    "translation studies": "linguistics",
    "semiotics": "linguistics",
    "dialectology": "linguistics",
    "ortography": "linguistics",
    "beekeeping": "agriculture",
    "officialese": "government",
    "textiles": "manufacturing",
    "weaving": "textiles",
    "quilting": "textiles",
    "knitting": "textiles",
    "sewing": "textiles",
    "cutting": "textiles",
    "furniture": "manufacturing lifestyle",
    "caving": "sports",
    "country dancing": "dancing",
    "dancing": "sports",
    "hip-hop": "dancing",
    "cheerleading": "sports",
    "bowling": "sports",
    "athletics": "sports",
    "acrobatics": "sports",
    "martial arts": "martial-arts",
    "martial-arts": "sports military",
    "meterology": "meteorology",
    "meteorology": "geography",
    "weather": "meteorology",
    "climate": "meteorology",
    "cryptozoology": "zoology",
    "lepidopterology": "zoology",
    "nematology": "zoology",
    "campanology": "history",
    "vexillology": "history",
    "phenomenology": "philosophy",
    "seismology": "geology",
    "cosmology": "astronomy",
    "astrogeology": "astronomy geology",
    "areology": "astrology geology",
    "stratigraphy": "geology",
    "orography": "geology",
    "stenography": "writing",
    "palynology": "chemistry microbiology",
    "lichenology": "botany",
    "seasons": "weather",
    "information technology": "computing",
    "algebra": "mathematics",
    "calculus": "mathematics",
    "arithmetics": "mathematics",
    "statistics": "mathematics",
    "geometry": "mathematics",
    "logic": "mathematics philosophy",
    "trigonometry": "mathematics",
    "mathematical analysis": "mathematics",
    "ethics": "philosophy",
    "existentialism": "philosophy",
    "religion": "philosophy lifestyle",
    "philosophy": "human-sciences",
    "transport": "economics",
    "shipping": "economics",
    "railways": "vehicles",
    "automotive": "vehicles",
    "automobile": "vehicles",
    "vehicles": "transport",
    "tourism": "economics",
    "travel": "tourism lifestyle",
    "travel industry": "tourism",
    "parliamentary procedure": "government",
    "food": "lifestyle",
    "vegetable": "food",
    "beer": "food",
    "brewing": "food manufacturing",
    "cooking": "food",
    "sexuality": "lifestyle",
    "seduction community": "sexuality",
    "BDSM": "sexuality",
    "LGBT": "sexuality",
    "sexual orientations": "sexuality",
    "romantic orientations": "sexuality",
    "prostitution": "sexuality",
    "sexology": "sexuality",
    "biblical": "religion",
    "ecclesiastical": "religion",
    "genetics": "biology medicine",
    "medical terminology": "medicine",
    "mycology": "biology",
    "paganism": "religion",
    "mechanical-engineering": "engineering",
    "mechanics": "mechanical-engineering",
    "lubricants": "mechanical-engineering",
    "measurement": "engineering",
    "thermodynamics": "physics",
    "signal processing": "computing mathematics",
    "topology": "mathematics",
    "algebraic topology": "topology",
    "norm topology": "topology",
    "linear algebra": "mathematics",
    "number theory": "mathematics",
    "insurance": "economics",
    "taxation": "economics government",
    "sugar-making": "manufacturing",
    "glassmaking": "manufacturing",
    "food manufacture": "manufacturing",
    "manufacturing": "economics",
    "optics": "physics engineering",
    "physical-sciences": "sciences",
    "chemistry": "physical-sciences",
    "ceramics": "chemistry engineering",
    "chess": "games",
    "checkers": "games",
    "mahjong": "games",
    "crystallography": "chemistry",
    "fluids": "chemistry physics engineering",
    "science": "sciences",
    "physics": "physical-sciences",
    "electrical-engineering": "engineering",
    "electricity": "electrical-engineering physics",
    "electronics": "electrical-engineering",
    "programming": "computing",
    "databases": "computing",
    "visual art": "arts",
    "crafts": "arts hobbies",
    "papercraft": "crafts",
    "bowmaking": "crafts",
    "lutherie": "crafts",
    "history": "human-sciences",
    "heraldry": "hobbies nobility",
    "philately": "hobbies",
    "hobbies": "lifestyle",
    "numismatics": "hobbies",
    "chronology": "horology",
    "horology": "hobbies",
    "cryptography": "computing",
    "finance": "economics",
    "finances": "finance",
    "accounting": "finance",
    "business": "economics",
    "politics": "government",
    "communism": "ideology",
    "socialism": "ideology",
    "capitalism": "ideology",
    "feudalism": "politics",
    "fascism": "ideology",
    "white supremacist ideology": "ideology",
    "pedology": "geography",
    "biogeography": "geography biology",
    "cryptocurrency": "finance",
    "nobility": "monarchy",
    "monarchy": "politics",
    "demography": "social-science statistics government",
    "historical demography": "demography",
    "chromatography": "chemistry",
    "anarchism": "politics",
    "diplomacy": "politics",
    "regionalism": "politics",
    "economic liberalism": "politics",
    "agri.": "agriculture",
    "agriculture": "lifestyle",
    "horticulture": "agriculture",
    "fashion": "lifestyle textiles",
    "cosmetics": "lifestyle",
    "design": "arts lifestyle",
    "money": "finance",
    "oceanography": "geography",
    "geological oceanography": "geology oceanography",
    "angelology": "theology",
    "woodworking": "carpentry",
    "art": "arts",
    "television": "broadcasting",
    "broadcasting": "media",
    "radio": "broadcasting",
    "radio communications": "radio",
    "journalism": "media",
    "writing": "journalism literature",
    "editing": "writing",
    "film": "television",
    "cinematography": "film",
    "drama": "film theater",
    "printing": "publishing",
    "publishing": "media",
    "science-fiction": "literature",
    "science fiction": "science-fiction",
    "fiction": "literature",
    "pornography": "media sexuality",
    "naturism": "lifestyle",
    "veganism": "lifestyle",
    "urbanism": "lifestyle",
    "Kantianism": "philosophy",
    "newspapers": "journalism",
    "telegraphy": "telecommunications",
    "wireless telegraphy": "telegraphy",
    "telegram": "telegraphy",
    "audio": "radio television electrical-engineering",
    "literature": "publishing",
    "folklore": "arts history",
    "music": "publishing arts",
    "guitar": "music",
    "musicology": "music human-sciences",
    "talking": "communications",
    "militaryu": "military",
    "army": "military",
    "navy": "military",
    "naval": "navy",
    "weaponry": "military tools",
    "weapon": "weaponry",
    "firearms": "weaponry",
    "fortifications": "military",
    "fortification": "fortifications",
    "law enforcement": "government",
    "archaeology": "history",
    "epigraphy": "history",
    "paleontology": "history natural-sciences",
    "palæontology": "paleontology",
    "paleobiology": "paleontology biology",
    "paleoanthropology": "paleontology anthropology",
    "paleogeography": "paleontology geography",
    "palentology": "paleontology error",
    "papyrology": "history",
    "hagiography": "history religion",
    "palaeography": "history",
    "historical geography": "geography history",
    "historiography": "history",
    "calligraphy": "arts",
    "ichthyology": "zoology",
    "herpetology": "zoology",
    "glaciology": "geography",
    "arachnology": "zoology",
    "veterinary pathology": "zoology pathology",
    "acarology": "arachnology",
    "mythology": "human-sciences",
    "ufology": "mythology",
    "fundamental interactions": "physics",
    "quantum field theory": "physics",
    "extragalactic medium": "cosmology",
    "extra-cluster medium": "cosmology",
    "uranography": "cartography astronomy",
    "astrocartography": "cartography astronomy",
    "mining": "manufacturing",
    "forestry": "manufacturing",
    "metalworking": "crafts",
    "metallurgy": "engineering",
    "communication": "communications",
    "telecommunications": "electrical-engineering communications",
    "telephony": "telecommunications communications",
    "bookbinding": "crafts publishing",
    "petrology": "geology",
    "petroleum": "petrology energy",
    "petrography": "petrology",
    "energy": "engineering physics",
    "shipbuilding": "manufacturing",
    "plumbing": "construction",
    "roofing": "construction",
    "carpentry": "construction",
    "construction": "manufacturing",
    "piledriving": "construction",
    "masonry": "construction",
    "tools": "engineering",
    "cranes": "tools",
    "colleges": "education",
    "higher education": "education",
    "clothing": "textiles fashion",
    "alchemy": "pseudoscience",
    "photography": "hobbies arts",
    "videography": "photography film",
    "horses": "sports lifestyle",
    "equestrianism": "horses",
    "demoscene": "computing",
    "golf": "sports lifestyle",
    "tennis": "sports",
    "hunting": "lifestyle agriculture",
    "fishing": "lifestyle agriculture",
    "birdwashing": "hobbies",
    "fisheries": "ecology",
    "climatology": "geography ecology",
    "limnology": "ecology",
    "informatics": "computing",
    "marketing": "business",
    "advertising": "marketing",
    "electrotechnology": "electrical-engineering",
    "electromagnetic radiation": "electromagnetism",
    "electronics manufacturing": "manufacturing electrical-engineering",
    "electric power": "energy electrical-engineering",
    "electronic communication": "telecommunications",
    "electrical device": "electrical-engineering",
    "enology": "oenology",
    "oenology": "food",
    "wine": "oenology lifestyle",
    "cigars": "lifestyle",
    "smoking": "lifestyle",
    "gambling": "games",
    "exercise": "sports",
    "acting": "drama",
    "theater": "arts",
    "comedy": "theater film",
    "dominoes": "games",
    "pocket billiards": "games",
    "pool": "games",
    "graphical user interface": "computing",
    "mysticism": "philosophy",
    "philology": "philosophy",
    "enthnology": "human-sciences",
    "feminism": "ideology",
    "creationism": "ideology religion",
    "shamanism": "religion",
    "ideology": "politics philosophy",
    "politology": "political-science",
    "political-science": "human-sciences",
    "political science": "political-science",
    "cartomancy": "mysticism",
    "tarot": "mysticism",
    "tasseography": "mysticism",
    "theology": "religion",
    "religionists": "religion",
    "spiritualism": "religion",
    "horse racing": "horses",
    "horse-racing": "horses",
    "equitation": "horses",
    "farriery": "horses",
    "motor racing": "sports",
    "racing": "sports",
    "spinning": "sports",
    "gymnastics": "sports",
    "cricket": "sports",
    "volleyball": "sports",
    "lacrosse": "sports",
    "rugby": "sports",
    "bodybuilding": "sports",
    "falconry": "hunting",
    "parachuting": "sports",
    "squash": "sports",
    "curling": "sports",
    "motorcycling": "sports",
    "swimming": "sports",
    "diving": "sports",
    "underwater diving": "diving",
    "basketball": "sports",
    "baseball": "sports",
    "soccer": "sports",
    "snooker": "sports",
    "snowboarding": "sports",
    "skateboarding": "sports",
    "weightlifting": "sports",
    "skiing": "sports",
    "mountaineering": "sports",
    "skating": "sports",
    "cycling": "sports",
    "rowing": "sports",
    "boxing": "martial-arts",
    "bullfighting": "sports",
    "archery": "martial-arts",
    "fencing": "martial-arts",
    "climbing": "sports",
    "surfing": "sports",
    "ballooning": "sports",
    "sailmaking": "manufacturing nautical",
    "sailing": "nautical",
    "maritime": "nautical",
    "ropemaking": "manufacturing nautical",
    "retail": "commerce",
    "commercial": "commerce",
    "retailing": "commerce",
    "electrical": "electricity",
    "category theory": "mathematics computing",
    "in technical contexts": "engineering physics chemistry",
    "technology": "engineering",
    "technical": "engineering",
    "stock exchange": "finance",
    "surveying": "geography",
    "networking": "computing",
    "computer sciences": "computing",
    "computer software": "computing",
    "software compilation": "computing",
    "computer languages": "computing",
    "computer hardware": "computing",
    "computer graphics": "computing",
    "meats": "food",
    "meat": "meats",
    "web design": "computing",
    "aviation": "aeronautics",
    "aerospace": "aeronautics",
    "investment": "finance",
    "computing theory": "computing mathematics",
    "information theory": "mathematics computing",
    "probability": "mathematics",
    "probability theory": "mathematics",
    "set theory": "mathematics",
    "order theory": "mathematics",
    "graph theory": "mathematics",
    "mathematical analysis": "mathematics",
    "cellular automata": "computing mathematics",
    "game theory": "mathematics computing",
    "computational": "computing",
    "behavioral sciences": "psychology",
    "space sciences": "astronomy",
    "applied sciences": "sciences engineering",
    "(sport)": "sports",
    "stock ticker symbol": "finance",
    "banking": "economics",
    "commerce": "economics",
    "cryptocurrency": "finance",
    "cartography": "geography",
    "ecology": "biology",
    "hydrology": "geography",
    "hydrography": "hydrology oceanography",
    "topography": "geography",
    "bibliography": "history literature",
    "polygraphy": "legal",
    "planetology": "astronomy",
    "astrology": "mysticism",
    "astrology signs": "astrology",
    "linguistic morphology": "morphology",
    "science": "sciences",
    "video games": "games",
    "role-playing games": "games",
    "poker": "games",
    "wrestling": "martial-arts",
    "professional wrestling": "wrestling",
    "sumo": "wrestling",
    "law": "legal",
    "court": "legal government",
    "rail transport": "railways",
    "colour": "color",
    "color": "property",
    "time": "property",
    "days of the week": "weekdays",
    "weekdays": "time",
    "temporal location": "time",
    "location": "property",
    "time": "property",
    "heading": "property",
    "manner": "property",
    "monotheism": "religion",
    "Catholicism": "Christianity",
    "Protestantism": "Christianity",
    "occultism": "religion",
    "buddhism": "religion",
    "hinduism": "religion",
    "Roman Catholicism": "Catholicism",
}

blocked = set(["të", "a", "e", "al", "þou", "?", "lui", "auf", "op", "ein",
               "af", "uit", "aus", "ab", "zu", "on", "off", "um", "faço",
               "dou", "†yodan", "at", "feito", "mná", "peces", "har",
               "an", "u", "ce", "for"])

valid_tags = set([
    "masculine",
    "feminine",
    "neuter",
    "common",
    "epicene",
    "ionic",
    "gender-indeterminate",
    "singular",
    "singulative",  # Individuation of a collective or mass noun
    "plural",     # depending on language, two or more / three or more
    "no-plural",
    "no-nominative-plural",
    "duoplural",  # two or more in number
    "dual",       # two in number
    "exclusive",
    "inclusive",
    "paucal",
    "also",
    "singular-only",
    "plural-only",
    "plurale-tantum",
    "uncountable",
    "countable",
    "comparative",
    "superlative",
    "comparable",
    "not-comparable",
    "no-comparative",
    "no-superlative",
    "excessive",
    "inanimate",
    "animate",
    "person",
    "partner",
    "personal",
    "impersonal",
    "abstract",
    "physical",
    "material",
    "natural",
    "demonstrative",
    "subjective-pronoun",
    "subject",
    "nominative",
    "genitive",
    "no-genitive",
    "possessive",
    "possessive-suffix",
    "possessive-determiner",
    "single-possession",
    "multiple-possession",
    "accusative",
    "objective",
    "subjective",
    "prospective",
    "agentive",
    "causative",
    "causal-final",
    "partitive",
    "dative",
    "oblique",
    "locative",
    "lative",
    "ablative",
    "comitative",
    "essive",
    "superessive",
    "delative",
    "essive-modal",
    "essive-instructive",
    "essive-formal",
    "sublative",
    "inessive",
    "adessive",
    "abessive",
    "translative",
    "prolative",
    "elative",
    "illative",
    "allative",
    "instrumental",
    "vocative",
    "relative",
    "ergative",
    "direct",
    "absolutive",
    "absolute",   # XXX Swedish at least ???
    "definitive",  # XXX is this used same as "definite", opposite indefinite?
    "definite",
    "indefinite",
    "collectively",
    "diminutive",
    "endearing",
    "emphatic",
    "prepositional",
    "augmentative",
    "augmented",
    "unaugmented",
    "mutated",
    "contracted",
    "pejorative",
    "infinitive",
    "middle",
    "middle-infinitive",
    "first-infinitive",
    "second-infinitive",
    "third-infinitive",
    "fourth-infinitive",
    "da-infinitive",
    "participle",
    "first-person",
    "second-person",
    "third-person",
    "fourth-person",
    "virile",
    "nonvirile",
    "present",
    "future",
    "simple",
    "past",
    "non-past",
    "preterite",
    "supine",
    "aorist",
    "active",
    "epic",
    "affirmative",
    "transgressive",
    "quotative",
    "analytic",
    "jussive",
    "passive",
    "mediopassive",
    "interrogative",
    "contemplative",
    "subjunctive",
    "subjunctive-I",
    "subjunctive-II",
    "conjunctive",
    "no-supine",
    "no-perfect",
    "suffix",
    "prefix",
    "enclitic",
    "proclitic",
    "clitic",
    "strong",
    "weak",
    "mixed",
    "short",
    "dependent",
    "independent",
    "autonomous",
    "attributive",
    "not-attributive",
    "predicative",
    "not-predicative",
    "irregular",
    "defective",
    "indicative",
    "progressive",
    "gerund",
    "complete",
    "perfect",
    "perfective",
    "si-perfective",
    "imperfect",
    "imperfective",
    "vav-consecutive",
    "imperative",
    "imperative-only",
    "pluperfect",
    "historic",
    "potential",
    "hypothetic",
    "sequential",
    "conditional",
    "volitive",
    "negative",
    "copulative",
    "connegative",
    "positive",
    "equative",
    "causative",
    "frequentative",
    "cohortative",
    "optative",
    "terminative",
    "durative",
    "transitive",
    "intransitive",
    "ditransitive",
    "ambitransitive",
    "stative",
    "pronoun",
    "pronominal-state",
    "nominal-state",
    "invariable",
    "invariant",  # XXX is this same as invariable?
    "indeclinable",
    "inalienable",
    "form-i",
    "form-ii",
    "form-iii",
    "form-iv",
    "form-v",
    "form-vi",
    "form-vii",
    "form-viii",
    "form-ix",
    "form-x",
    "form-xi",
    "form-xii",
    "form-xiii",
    "form-iq",
    "form-iiq",
    "form-iiiq",
    "form-ivq",
    "class-1",
    "class-1a",
    "class-2",
    "class-2a",
    "class-3",
    "class-4",
    "class-5",
    "class-6",
    "class-7",
    "class-8",
    "class-9",
    "class-10",
    "class-11",
    "class-12",
    "class-13",
    "class-14",
    "class-15",
    "m-wa-class",
    "m-mi-class",
    "u-class",
    "ki-vi-class",
    "first-declension",
    "second-declension",
    "third-declension",
    "fourth-declension",
    "fifth-declension",
    "first-conjugation",
    "second-conjugation",
    "third-conjugation",
    "fourth-conjugation",
    "fifth-conjugation",
    "sixth-conjugation",
    "seventh-conjugation",
    "one-termination",
    "two-termination",
    "stress-pattern-1",
    "stress-pattern-2",
    "stress-pattern-3",
    "stress-pattern-3a",
    "stress-pattern-3b",
    "stress-pattern-4",
    "stressed",
    "type-p",
    "type-u",
    "type-up",
    "type-a",
    "root",
    "stem",
    "possessed",
    "ordinal",
    "cardinal",
    "conjunct",
    "used-in-the-form",
    "construct",
    "no-construct-forms",
    "reduplicated",
    "pausal",
    "upper-case",
    "lower-case",
    "mixed-case",
    "verb-form-i",
    "verb-form-ii",
    "pi'el-construction",
    "pa'el-construction",
    "hif'il-construction",
    "hitpa'el-construction",
    "pu'al-construction",
    "nif'al-construction",
    "huf'al-construction",
    "adnominal",
    "nominal",
    "nominalization",
    "agent",
    "adverbial",
    "adverb",
    "term-of-address",
    "pronominal",
    "reflexive",
    "adjective",
    "adjectival",
    "verbal-noun",
    "substantive",
    "article",
    "verb",
    "noun",
    "abstract-noun",
    "auxiliary",
    "modal",
    "numeral",
    "classifier",
    "kyūjitai",
    "shinjitai",
    "pinyin",
    "romanization",
    "romaji",
    "X-system",
    "visual-rendering",
    "morse-code",
    "hangeul",
    "zhuyin",
    "revised-jeon",
    "McCune-Reischauer-chŏn",
    "Yale-cen",
    "prototonic",
    "deuterotonic",
    "polytonic",
    "dialectal",
    "baby-talk",
    "childish",
    "obsolete",
    "archaic",
    "regional",
    "historical",
    "hellenism",
    "literary",
    "neologism",
    "rhetoric",
    "informal",
    "polite",
    "impolite",
    "familiar",
    "humble",
    "poetic",
    "formal",
    "honorific",
    "standard",
    "nonstandard",
    "misspelling",
    "misconstruction",
    "mutation",
    "pronunciation-spelling",
    "reconstruction",
    "alternative",
    "colloquial",
    "with-infinitive",
    "with-odd-syllable-stems",
    "with-genitive",
    "with-dative",
    "with-objective",
    "with-accusative",
    "with-ablative",
    "with-instrumental",
    "with-elative",
    "with-absolutive",
    "with-partitive",
    "with-locative",
    "with-possessive-suffix",
    "with-present",
    "with-noun-phrase",
    "with-noun",
    "without-noun",
    "with-subjunctive",
    "with-optative",
    "with-number",
    "with-che",
    "with-lai",
    "with-meel",
    "with-kala",
    "with-järgi",
    "with-välja",
    "with-a",
    "with-avec",
    "with-ce",
    "with-con",
    "with-da",
    "with-de",
    "with-di",
    "with-en",
    "with-eu",
    "with-for",
    "with-gij",
    "with-in",
    "with-per",
    "with-pour",
    "with-savrtsobi",
    "with-sein",
    "with-su",
    "with-sur",
    "with-você",
    "with-ele",
    "with-ela",
    "with-tu",
    "with-eles",
    "with-elas",
    "with-vocês",
    "with-vós",
    "with-nos",
    "with-zuek",
    "with-hura",
    "with-hiri",
    "with-others",
    "with-à",
    "krama",
    "ngoko",
    "krama-ngoko",
    "krama-inggil",
    "next",
    "previous",
    "abbreviation",
    "prothesis",
    "lenition",
    "soft",
    "eclipsis",
    "contracted-dem-form",
    "accent/glottal",
    "transcription",
    "medial",
    "error",
    "canonical",  # Used to mark the canonical word from from the head tag
    "figuratively",
    "metonymically",
    "broadly",
    "narrowly",
    "strict-sense",
    "literally",
    "deictically",
    "anaphorically",
    "-na",  # Japanese inflection type
    "-i",   # Japanese inflection type
    "-tari",  # Japanese inflection type
    "-nari",  # Japanese inflection type
    "suru",  # Japanese verb inflection type
    "compound",
    "in-compounds",
    "in-certain-phrases",
    "slang",
    "derogatory",
    "proscribed",
    "humorous",
    "sarcastic",
    "rare",
    "proper-noun",
    "surnames",
    "sometimes",
    "possibly",
    "somewhat",
    "especially",
    "specifically",
    "chiefly",
    "often",
    "usually",
    "vulgar",
    "offensive",
    "euphemism",
    "idiomatic",
    "ethnic",
    "non-scientific",
    "capitalized",
    "typography",
    "definition",
    "economics",
    "slur",
    "diacritic",
    "capitalized",
    "onomatopoeia",
    "expressively",
    "ideophonic",
    "dated",
    "exaggerated",
    "initialism",
    "contraction",
    "praenominal",
    "ellipsis",
    "clipping",
    "nasal",
    "aspirate",
    "deliberate",
    "latin",
    "euphemistic",
    "traditional",
    "uncommon",
    "būdinys",
    "front-vowel",
    "form-of",
    "alt-of",
    "compound-of",
    "synonym-of",
    "US",
    "relational",
    "sequence",
    "topic",
    "deprecated-template",
])

valid_topics = set([
    "Catholicism",
    "Christianity",
    "Internet",
    "Internet",
    "aeronautics",
    "agriculture",
    "anatomy",
    "animal",
    "anthropology",
    "arachnology",
    "architecture",
    "arithmetic",
    "arts",
    "astrology",
    "astronomy",
    "astrophysics",
    "ball-games",
    "biology",
    "board-games",
    "botany",
    "broadcasting",
    "business",
    "card-games",
    "carpentry",
    "cartography",
    "chemistry",
    "cities",
    "color",
    "commerce",
    "communications",
    "computing",
    "construction",
    "cosmology",
    "countries",
    "court",
    "crafts",
    "criminology",
    "demography",
    "dancing",
    "dentistry",
    "diving",
    "drama",
    "drugs",
    "ecology",
    "economics",
    "education",
    "electrical-engineering",
    "electricity",
    "electromagnetism",
    "energy",
    "engineering",
    "epistemology",
    "error",
    "ethnography",
    "fantasy",
    "fashion",
    "film",
    "finance",
    "food",
    "fortifications",
    "games",
    "gemology",
    "geography",
    "geology",
    "government",
    "heading",
    "healthcare",
    "histology",
    "history",
    "hobbies",
    "horology",
    "horses",
    "human-sciences",
    "hunting",
    "hydrology",
    "ideology",
    "journalism",
    "legal",
    "lifestyle",
    "linguistics",
    "literature",
    "location",
    "management",
    "manner",
    "manufacturing",
    "marketing",
    "martial-arts",
    "mathematics",
    "meats",
    "mechanical-engineering",
    "media",
    "medicine",
    "meteorology",
    "metrology",
    "microbiology",
    "military",
    "mineralogy",
    "mining",
    "monarchy",
    "morphology",
    "music",
    "mysticism",
    "mythology",
    "natural-sciences",
    "nautical",
    "navy",
    "neurology",
    "neuroscience",
    "nobility",
    "oceanography",
    "oenology",
    "organization",
    "ornithology",
    "paleontology",
    "pathology",
    "petrology",
    "pharmacology",
    "philosophy",
    "phonology",
    "photography",
    "physical-sciences",
    "physics",
    "physiology",
    "planets",
    "political-science",
    "politics",
    "publishing",
    "pulmonology",
    "prefectures",
    "printing",
    "property",
    "pseudoscience",
    "psychiatry",
    "psychology",
    "radio",
    "radiology",
    "railways",
    "region",
    "religion",
    "science-fiction",
    "sciences",
    "sexuality",
    "social-science",
    "socialism",
    "sports",
    "states",
    "statistics",
    "telecommunications",
    "telegraphy",
    "telephone",
    "television",
    "temperature",
    "textiles",
    "theater",
    "theology",
    "time",
    "tools",
    "topology",
    "tourism",
    "toxicology",
    "transport",
    "vehicles",
    "weaponry",
    "weather",
    "weekdays",
    "wrestling",
    "writing",
    "zoology",
])


ignored_parens = set([
    "please verify",
    "in words with back vowel harmony",
    "in words with front vowel harmony",
])


# Words that can be part of form description
valid_words = set(["or", "and"])
for x in valid_tags:
    valid_words.update(x.split(" "))
for x in xlat_tags_map.keys():
    valid_words.update(x.split(" "))


def add_to_valid_tree(tree, field, tag, v):
    """Helper function for building trees of valid tags/sequences during
    initialization."""
    assert isinstance(tree, dict)
    assert field in ("tags", "topics")
    assert isinstance(tag, str)
    assert v is None or isinstance(v, str)
    node = tree
    for w in tag.split(" "):
        if w in node:
            node = node[w]
        else:
            new_node = {}
            node[w] = new_node
            node = new_node
    if "$" not in node:
        node["$"] = {}
    node = node["$"]
    if field not in node:
        node[field] = ()
    if v is not None and v not in node[field]:
        node[field] += (v,)


def add_to_valid_tree1(tree, field, k, v, valid_values):
    assert isinstance(tree, dict)
    assert isinstance(field, str)
    assert isinstance(k, str)
    assert v is None or isinstance(v, (list, tuple, str))
    assert isinstance(valid_values, set)
    if not v:
        add_to_valid_tree(valid_sequences, field, k, None)
        return
    elif isinstance(v, str):
        v = [v]
    q = []
    for vv in v:
        assert isinstance(vv, str)
        add_to_valid_tree(valid_sequences, field, k, vv)
        add_to_valid_tree(valid_sequences, field, k.lower(), vv)
        vvs = vv.split(" ")
        q.extend(vvs)
        for x in vvs:
            if x not in valid_values and x[0].islower():
                print("WARNING: {} in mapping {!r} but not in valid_values"
                      .format(x, k))
    return q


def add_to_valid_tree_mapping(tree, field, mapping, valid_values, recurse):
    for k, v in mapping.items():
        assert isinstance(k, str)
        assert isinstance(v, (list, str))
        if isinstance(v, str):
            v = [v]
        q = []
        for vv in v:
            vv = vv.split(" ")
            q.extend(add_to_valid_tree1(tree, field, k, vv, valid_values))
        if recurse:
            visited = set()
            while q:
                v = q.pop()
                if v in visited:
                    continue
                visited.add(v)
                if v not in mapping:
                    continue
                for vv in mapping[v].split(" "):
                    qq = add_to_valid_tree1(tree, field, k, vv, valid_values)
                    q.extend(qq)


# Tree of sequences considered to be tags (includes sequences that are
# mapped to something that becomes one or more valid tags)
valid_sequences = {}
for tag in valid_tags:
    add_to_valid_tree(valid_sequences, "tags", tag, tag)
add_to_valid_tree_mapping(valid_sequences, "tags", xlat_tags_map,
                          valid_tags, False)
# Add topics to the same table, with all generalized topics also added
for topic in valid_topics:
    add_to_valid_tree(valid_sequences, "topics", topic, topic)
# Let each original topic value stand alone.  These are not generally on
# valid_topics.
for topic in topic_generalize_map:
    add_to_valid_tree(valid_sequences, "topics", topic, topic)
# Add canonicalized/generalized topic values
add_to_valid_tree_mapping(valid_sequences, "topics", topic_generalize_map,
                          valid_topics, True)

# Regexp used to find "words" from word heads and linguistic descriptions
word_re = re.compile(r"[^ ,;()\u200e]+|\(([^()]|\([^)]*\))*\)")


def distw(titleparts, word):
    """Computes how distinct ``word`` is from the most similar word in
    ``titleparts``.  Returns 1 if words completely distinct, 0 if
    identical, or otherwise something in between."""
    w = min(Levenshtein.distance(word, tw) / max(len(tw), len(word)) for
            tw in titleparts)
    return w


def map_with(ht, lst):
    assert isinstance(ht, dict)
    assert isinstance(lst, (list, tuple))
    ret = []
    for x in lst:
        x = x.strip()
        x = ht.get(x, x)
        if isinstance(x, str):
            ret.append(x)
        elif isinstance(x, (list, tuple)):
            ret.extend(x)
        else:
            raise RuntimeError("map_with unexpected value: {!r}".format(x))
    return ret


def decode_tags(lst, allow_any=False):
    """Decodes tags, doing some canonicalizations.  This returns a list of
    lists of tags and a list of topics."""
    assert isinstance(lst, (list, tuple))
    lsts = [[]]
    for x in lst:
        assert isinstance(x, str)
        for alt in map_with(xlat_tags_map, [x]):
            lsts = list(lst1 + [alt] for lst1 in lsts)
    lsts = map_with(xlat_tags_map, list(map(lambda x: " ".join(x), lsts)))
    lsts = list(map(lambda x: x.split(" "), lsts))
    topics = []
    tagsets = set()
    for lst in lsts:
        tags = []
        nodes = [(valid_sequences, 0)]
        for i, w in enumerate(lst):
            if not w:
                continue
            new_nodes = []

            def add_new(node, next_i):
                for node2, next_i2 in new_nodes:
                    if node2 is node and next_i2 == next_i:
                        break
                else:
                    new_nodes.append((node, next_i))

            max_next_i = max(x[1] for x in nodes)
            for node, next_i in nodes:
                if w in node:
                    add_new(node[w], next_i)
                if "$" in node:
                    tags.extend(node["$"].get("tags", ()))
                    topics.extend(node["$"].get("topics", ()))
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i)
                if w not in node and "$" not in node:
                    if allow_any:
                        tag = " ".join(lst[next_i:i + 1])
                        next_i = i + 1
                        if w in valid_sequences:
                            add_new(valid_sequences[w], i)
                    else:
                        rest = tags[max_next_i:]
                        tag = " ".join(rest)
                        tags.append("error-unknown-tag")
                        if w in valid_sequences:
                            add_new(valid_sequences[w], next_i)
            if not new_nodes:
                add_new(valid_sequences, max_next_i)
            nodes = new_nodes

        valid_end = False
        for node, next_i in nodes:
            if "$" in node:
                tags.extend(node["$"].get("tags", ()))
                topics.extend(node["$"].get("topics", ()))
                valid_end = True
        max_next_i = max(x[1] for x in nodes)
        if not valid_end and any(lst[max_next_i:]):
            rest = lst[max_next_i:]
            tag = " ".join(rest)
            if tag and allow_any:
                if tag not in tags:
                    tags.append(tag)
            elif tag and not tag[0].isupper():
                tags.append("error-unknown-tag")
        tagsets.add(tuple(sorted(set(tags))))
    ret = list(tagsets)
    return ret, topics


def add_tags(ctx, data, lst, allow_any=False):
    assert isinstance(ctx, Wtp)
    assert isinstance(data, dict)
    assert isinstance(lst, (list, tuple))
    for x in lst:
        assert isinstance(x, str)
    tagsets, topics = decode_tags(lst, allow_any=allow_any)
    data_extend(ctx, data, "topics", topics)
    for tags in tagsets:
        data_extend(ctx, data, "tags", tags)


def add_related(ctx, data, lst, related):
    assert isinstance(ctx, Wtp)
    assert isinstance(lst, (list, tuple))
    for x in lst:
        assert isinstance(x, str)
    assert isinstance(related, (list, tuple))
    related = " ".join(related)
    if related == "[please provide]":
        return
    if related == "-":
        ctx.warning("add_related: unhandled {} related form {}"
                    .format(lst, related))
        return
    for related in related.split(" or "):
        if related:
            m = re.match(r"\(([^()]|\([^)]*\))*\)\s*", related)
            if m:
                paren = m.group(1)
                related = related[m.end():]
                tagsets1, topics1 = decode_tags(split_at_comma_semi(paren))
            else:
                tagsets1 = [[]]
                topics1 = []
            tagsets2, topics2 = decode_tags(lst)
            for tags1 in tagsets1:
                assert isinstance(tags1, (list, tuple))
                for tags2 in tagsets2:
                    assert isinstance(tags1, (list, tuple))
                    if "alt-of" in tags2:
                        data_extend(ctx, data, "tags", tags1)
                        data_extend(ctx, data, "tags", tags2)
                        data_extend(ctx, data, "topics", topics1)
                        data_extend(ctx, data, "topics", topics2)
                        data_append(ctx, data, "alt_of", related)
                    elif "form-of" in tags2:
                        data_extend(ctx, data, "tags", tags1)
                        data_extend(ctx, data, "tags", tags2)
                        data_extend(ctx, data, "topics", topics1)
                        data_extend(ctx, data, "topics", topics2)
                        data_append(ctx, data, "inflection_of", related)
                    elif "compound-of" in tags2:
                        data_extend(ctx, data, "tags", tags1)
                        data_extend(ctx, data, "tags", tags2)
                        data_extend(ctx, data, "topics", topics1)
                        data_extend(ctx, data, "topics", topics2)
                        data_append(ctx, data, "compound", related)
                    else:
                        form = {"form": related}
                        data_extend(ctx, form, "tags", tags1)
                        data_extend(ctx, form, "tags", tags2)
                        data_extend(ctx, form, "topics", topics1)
                        data_extend(ctx, form, "topics", topics2)
                        data_append(ctx, data, "forms", form)


def parse_word_head(ctx, pos, text, data):
    """Parses the head line for a word for in a particular language and
    part-of-speech, extracting tags and related forms."""
    assert isinstance(ctx, Wtp)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_word_head:", text)

    if text.find("Lua execution error") >= 0:
        return
    if text.find("Lua timeout error") >= 0:
        return

    title = ctx.title
    titleparts = list(m.group(0) for m in re.finditer(word_re, title))

    # Handle the part of the head that is not in parentheses
    base = re.sub(r"\(([^()]|\([^(]*\))*\)", " ", text)
    base = re.sub(r"\?", " ", base)  # Removes uncertain articles etc
    base = re.sub(r"\s+", " ", base).strip()
    descs = map_with(xlat_tags_map, split_at_comma_semi(base))
    for desc_i, desc in enumerate(descs):
        desc = desc.strip()
        for alt in map_with(xlat_tags_map, desc.split(" or ")):
            baseparts = list(m.group(0) for m in re.finditer(word_re, alt))
            if " ".join(baseparts) in valid_tags and desc_i > 0:
                lst = []  # Word form
                rest = baseparts  # Tags
            else:
                rest = []
                lst = []
                for i in range(len(baseparts) - 1, -1, -1):
                    part = baseparts[i]
                    if part not in xlat_head_map:
                        lst = baseparts[:i + 1]
                        break
                    rest.append(xlat_head_map[part])
                rest = list(reversed(rest))
            # lst is canonical form of the word
            # rest is additional tags (often gender m/f/n/c/...)
            if lst and title != " ".join(lst):
                add_related(ctx, data, ["canonical"], lst)
            # XXX here we should only look at a subset of tags allowed
            # in the base
            add_tags(ctx, data, rest)

    # Handle parenthesized descriptors for the word form and links to
    # related words
    parens = list(m.group(1) for m in
                  re.finditer(r"\((([^()]|\([^)]*\))*)\)", text))
    for paren in parens:
        paren = paren.strip()
        descriptors = map_with(xlat_tags_map, [paren])
        new_desc = []
        for desc in descriptors:
            new_desc.extend(map_with(xlat_tags_map, split_at_comma_semi(desc)))
        for desc in new_desc:
            parts = list(m.group(0) for m in re.finditer(word_re, desc))
            lst = []
            node = valid_sequences
            last_valid = 0
            i = 0
            while i < len(parts):
                part = parts[i]
                w = distw(titleparts, part)  # 0=identical .. 1=very different
                if (part != title and part not in titleparts and
                    (w >= 0.6 or len(part) < 4) and
                    (part in node or
                     ("$" in node and part in valid_sequences))):
                    # Consider it part of a descriptor
                    if part in node:
                        if "$" in node:
                            lst.extend(node["$"].get("tags", ()))
                            last_valid = i + 1
                        node = node[part]
                    else:
                        assert "$" in node
                        lst.extend(node["$"].get("tags", ()))
                        last_valid = i
                        node = valid_sequences[part]
                elif w == "of" and lst and "of" not in node:
                    lst.append("form-of")
                    last_valid = i + 1
                    node = valid_sequences
                    break
                else:
                    # Consider the rest as a related term
                    break
                i += 1
                # Stop if we have completed parsing something that is always
                # followed by a word form
                if ("alt-of" in lst or
                    "form-of" in lst or
                    "compound-of" in lst or
                    "synonym-of" in lst):
                    break
            if "$" in node:
                lst.extend(node["$"].get("tags", ()))
                last_valid = i
            related = parts[last_valid:]
            # XXX check if related contains valid tag sequences and warn if
            # so
            for tagspec in " ".join(lst).split(" or "):
                lst = tagspec.split(" ")
                if related:
                    add_related(ctx, data, lst, related)
                else:
                    add_tags(ctx, data, lst)

def parse_sense_tags(ctx, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_sense_tags:", text)
    for semi in split_at_comma_semi(text):
        tags = map_with(xlat_tags_map, [semi])
        tagsets, topics = decode_tags(tags, allow_any=True)
        data_extend(ctx, data, "topics", topics)
        # XXX should think how to handle distinct options better,
        # e.g., "singular and plural genitive"; that can't really be
        # done with changing the calling convention of this function.
        # XXX should handle cases where it is actually form-of or alt-of
        for tags in tagsets:
            data_extend(ctx, data, "tags", tags)


def parse_pronunciation_tags(ctx, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    tags = map_with(xlat_tags_map, split_at_comma_semi(text))
    # XXX should think how to handle distinct options better,
    # e.g., "singular and plural genitive"; that can't really be
    # done with changing the calling convention of this function.

    # XXX remove this?
    #tagsets = decode_tags(tags, allow_any=True)
    #for tags in tagsets:
    #    data_extend(ctx, data, "tags", tags)
    data_extend(ctx, data, "tags", tags)


def parse_translation_desc(ctx, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_translation_desc:", text)

    # Handle the part of the head that is not in parentheses
    base = re.sub(r"\(([^()]|\([^)]*\))*\):?", "", text)
    base = re.sub(r"\s+", " ", base).strip()
    baseparts = list(m.group(0) for m in re.finditer(word_re, base))
    rest = []  # Tags
    i = len(baseparts) - 1
    while i > 0:
        word = baseparts[i]
        if word == "•":
            pass
        elif word in xlat_head_map:
            rest.append(xlat_head_map[word])
        elif word in ("or", "and"):
            rest.append(word)
        else:
            break
        i -= 1
    lst = baseparts[: i + 1]  # word form
    rest = list(reversed(rest))
    # lst is canonical form of the word
    # rest is additional tags (often gender m/f/n/c/...)
    data["word"] = " ".join(lst)
    # XXX here we should only look at a subset of tags allowed
    # in the translation
    for tagdesc in map_with(xlat_tags_map, [" ".join(rest)]):
        for tagpart in tagdesc.split(" or "):
            lst = []
            for part in tagpart.split(" "):
                if not part or part == "or":
                    continue
                if part in xlat_head_map:
                    lst.append(xlat_head_map[part])
                elif part in valid_tags:
                    lst.append(part)
                elif part.startswith("("):
                    continue
                elif part.startswith('"') or part.startswith('“'):
                    continue
                elif part not in valid_tags:
                    ctx.warning("unexpected part in translation: {!r} in "
                                "{!r}".format(part, text))
            add_tags(ctx, data, lst)

    # Handle parenthesized descriptors for the word form and links to
    # related words
    parens = list(m.group(1) for m in
                  re.finditer(r"\((([^()]|\([^)]*\))*)\)", text))
    for paren in parens:
        paren = paren.strip()
        if paren.endswith(":"):
            paren = paren[:-1]  # Probably mistakes
        if paren in ignored_parens:
            continue
        if paren.startswith("(Can we clean up"):
            continue
        if paren.startswith("(Can we verify"):
            continue
        if paren.startswith("numeral:"):
            data["numeral"] = paren[8:].strip()
            continue
        descriptors = map_with(xlat_tags_map, [paren])
        for desc in descriptors:
            for new_desc in map_with(xlat_tags_map, split_at_comma_semi(desc)):
                new_desc = new_desc.strip()
                if new_desc.startswith("e.g."):
                    continue
                if new_desc.startswith("cf."):
                    continue
                if new_desc.startswith("use with "):
                    # See e.g., "ten", Finnish translation; the intention is
                    # to ignore this and all later comma-separated components
                    # of this parenthesized part.
                    break
                if new_desc.startswith("literally "):
                    continue
                if new_desc.startswith("also expressed with"):
                    continue
                if new_desc in valid_tags:
                    add_tags(ctx, data, [new_desc], allow_any=True)
                elif new_desc[0].isupper() and not ctx.title[0].isupper():
                    data_append(ctx, data, "tags", new_desc)
                elif "alt" not in data:
                    data["roman"] = new_desc
                else:
                    ctx.warning("maybe more than one romanization: {!r}"
                                .format(text))
                    data_append(ctx, data, "tags", "error-multiple-paren")

def parse_alt_or_inflection_of(ctx, gloss):
    """Tries to parse an inflection-of or alt-of description."""
    tags = set()
    nodes = [(valid_sequences, 0)]
    gloss = re.sub(r"\s+", " ", gloss)
    lst = gloss.strip().split(" ")
    last = 0
    for i, w in enumerate(lst):
        if not w:
            continue
        new_nodes = []

        def add_new(node, next_i):
            for node2, next_i2 in new_nodes:
                if node2 is node and next_i2 == next_i:
                    break
            else:
                new_nodes.append((node, next_i))

        max_next_i = max(x[1] for x in nodes)
        for node, next_i in nodes:
            if w in node:
                add_new(node[w], next_i)
            elif w.lower() in node:
                add_new(node[w.lower()], next_i)
            if "$" in node:
                for x in node["$"].get("tags", ()):
                    tags.add(x)
                if w in valid_sequences:
                    add_new(valid_sequences[w], i)
                elif w.lower() in valid_sequences:
                    add_new(valid_sequences[w.lower()], i)
                last = i
        if not new_nodes:
            add_new(valid_sequences, max_next_i)
        nodes = new_nodes

    if last == 0:
        return [], gloss

    # It is fairly common for form_of glosses to end with something like
    # "ablative case".  Parse that ending.
    lst = lst[last:]
    if len(lst) >= 3 and lst[-1] == "case":
        node = valid_sequences.get(lst[-2])
        if node and "$" in node:
            tags.extend(node["$"].get("tags", ()))
            lst = lst[:-2]

    tags = list(sorted(tags))
    base = " ".join(lst).strip()
    # Clean up some common additional stuff
    base = re.sub(r"(?s)(:|;| - ).*", "", base)
    base = re.sub(r"\s+(with an added emphasis on the person.)", "", base)
    base = re.sub(r"\s+with -ra/-re$", "", base)
    base = re.sub(r"\s+\([^)]*\)", "", base)  # Remove all (...) groups
    # Note: base might still contain comma-separated values and values
    # separated by "and"
    base = base.strip()
    if base.endswith("."):
        base = base[:-1]
    if base.find(".") >= 0:
        ctx.debug(". remains in alt_of/inflection_of: {}".format(base))
    return tags, base

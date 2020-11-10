# Code for parsing linguistic form descriptions and tags for word senses
# (both the word entry head - initial part and parenthesized parts -
# and tags at the beginning of word senses)
#
# Copyright (c) 2020 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import Levenshtein
from wikitextprocessor import Wtp
from .config import WiktionaryConfig
from .datautils import (data_append, data_extend, data_inflection_of,
                        data_alt_of, split_at_comma_semi)

# Maps strings into one or more other strings.  This is applied at multiple
# levels of partitioning the description.

xlat_tags_map = {
    "m": "masculine",
    "m.": "masculine",
    "male": "masculine",
    "f": "feminine",
    "f.": "feminine",
    "fem.": "feminine",
    "female": "feminine",
    "sg": "singular",
    "pl": "plural",
    "indef.": "indefinite",
    "gen.": "genitive",
    "n": "neuter",
    "pl": "plural",
    "inan": "inanimate",
    "anim": "animate",
    "pers": "person",  # XXX check what this really is used for? personal?
    "impf.": "imperfect",
    "impf": "imperfect",
    "pf": "perfective",
    "unc": "uncountable",
    "trans.": "transitive",
    "npers": "impersonal",
    "agri.": "agriculture",
    "c": "common",  # common gender in at least West Frisian
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
    "masculine and plural": ["masculine", "plural"],
    "female and neuter": "feminine neuter",
    "singular and plural": "singular plural",
    "plural and weak singular": ["plural", "weak singular"],
    "dative-directional": "dative",
    "preterite and supine": "preterite supine",
    "genitive and dative": "genitive dative",
    "genitive and plural": ["genitive", "plural"],
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
    ["with-genitive with-possessive-suffix", "with-elative"],
    "+ partitive or (less common) possessive suffix":
    ["with-partitive", "with-possessive-suffix"],
    "no perfect or supine stem": ["no-perfect no-supine"],
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
    "+dative": "with-dative",
    "+ dative case": "with-dative",
    "+ dative": "with-dative",
    "plus dative": "with-dative",
    "+ accusative": "with-accusative",
    "+ accusative case": "with-accusative",
    "+accusative": "with-accusative",
    "with accusative case": "with-accusative",
    "plus accusative": "with-accusative",
    "governs the accusative": "with-accusative",
    "+ partitive": "with-partitive",
    "+ partitive + vastaan": "with-partitive",
    "+partitive": "with-partitive",
    "with partitive case": "with-partitive",
    "plus partitive": "with-partitive",
    "+ablative": "with-ablative",
    "+ ablative": "with-ablative",
    "with ablative case": "with-ablative",
    "plus ablative": "with-ablative",
    "+ subjunctive": "with-subjunctive",
    "+subjunctive": "with-subjunctive",
    "plus subjunctive": "with-subjunctive",
    "+ instrumental": "with-instrumental",
    "+instrumental": "with-instrumental",
    "+ instrumental case": "with-instrumental",
    "with instrumental case": "with-instrumental",
    "plus instrumental": "with-instrumental",
    "+ locative case": "with-locative",
    "+absolutive": "with-absolutive",
    "+ absolutive": "with-absolutive",
    "with absolutive case": "with-absolutive",
    "+ absolutive case": "with-absolutive",
    "plus absolutive": "with-absolutive",
    "+elative": "with-elative",
    "+ elative": "with-elative",
    "with elative case": "with-elative",
    "plus elative": "with-elative",
    "+objective": "with-objective",
    "+ objective": "with-objective",
    "with objective case": "with-objective",
    "plus objective": "with-objective",
    "+ present form": "with-present",
    "+ noun phrase] + subjunctive (verb)":
    "with-noun-phrase with-subjunctive",
    "+ [nounphrase] + subjunctive":
    "with-noun-phrase with-subjunctive",
    "+ number": "with-number",
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
    "militaryu slang": "military slang",
    "dialectical": "dialectal",
    "dialect": "dialectal",
    "possibly obsolete": "archaic",
    "19th century": "archaic",
    "dated or regional": "archaic regional",
    "archaic ortography": "archaic",
    '"manner of action"': "manner-of-action",
    "in the plural": "plural-only",
    "derogative": "derogatory",
    "collective sense": "collective",
    "law": "legal",
    "rail transport": "transport",
    "relatively rare": "rare",
    "very informal": "informal",
    "with a + inf.": "with-a with-infinitive",
    "with di + inf.": "with-di with-infinitive",
    "with che + subj.": "with-che with-subjunctive",
    "with inf.": "with-infinitive",
    "~ се": "with-ce",
    "strong/mixed": "strong mixed",
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
    "not comparable": "no-comparative no-superlative",
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
    "ordinal form of": "ordinal",
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
    "proper name": "proper-name",
    "usually in the": "usually",
    "non-scientific usage": "non-scientific",
    "card games": "card-games",
    "manner of action": "manner-of-action",
    "krama inggil": "krama-inggil",
    "McCune-Reischauer chŏn": "McCune-Reischauer-chŏn",
    "gender indeterminate": "gender-indeterminate",
    "singular only": "singular-only",
    "plural only": "plural-only",
    "imperative only": "imperative-only",
    "by extension": "by-extension",
    "by metonymy": "by-metonymy",
    "by semantic narrowing": "by-semantic-narrowing",
    "by semantic widening": "by-semantic-widening",
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
    "compound of": "compound-of",
    "form of": "form-of",
    "humurous": "humorous",
}

# These mappings suggest the word form should go in alt_of
# XXX these include final of/by
alt_of_map = {
}

blocked = set(["të", "a", "e", "al", "þou", "?", "lui", "auf", "op", "ein",
               "af", "uit", "aus", "ab", "zu", "on", "off", "um", "faço",
               "dou", "†yodan", "at", "feito", "mná", "peces", "har",
               "an", "u"])

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
    "no-comparative",
    "no-superlative",
    "excessive",
    "inanimate",
    "animate",
    "person",
    "personal",
    "impersonal",
    "abstract",
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
    "collective",
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
    "pronominal",
    "reflexive",
    "adjective",
    "adjectival",
    "verbal-noun",
    "substantive",
    "verb",
    "abstract-noun",
    "auxiliary",
    "modal",
    "numeral",
    "roman",
    "classifier",
    "kyūjitai",
    "shinjitai",
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
    "obsolete",
    "archaic",
    "regional",
    "historical",
    "hellenism",
    "literary",
    "neologism",
    "rhetoric",
    "informal",
    "familiar",
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
    "figurative",
    "by-extension",
    "by-metonymy",
    "by-semantic-narrowing",
    "by-semantic-widening",
    "-na",  # Japanese inflection type
    "-i",   # Japanese inflection type
    "-tari",  # Japanese inflection type
    "-nari",  # Japanese inflection type
    "suru",  # Japanese verb inflection type
    "compound",
    "in-compounds",
    "slang",
    "derogatory",
    "humorous",
    "sarcastic",
    "rare",
    "proper-name",
    "sometimes",
    "chiefly",
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
    "Internet",
    "military",
    "agriculture",
    "aviation",
    "baseball",
    "biology",
    "medicine",
    "botany",
    "zoology",
    "computing",
    "science",
    "economics",
    "psychology",
    "clothing",
    "slur",
    "geology",
    "mineralogy",
    "Internet",
    "physics",
    "chemistry",
    "legal",
    "linguistics",
    "grammar",
    "meteorology",
    "astronomy",
    "astrology",
    "arithmetic",
    "metrology",
    "astrophysics",
    "mythology",
    "card-games",
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
    "communism",
    "business",
    "finance",
    "architecture",
    "cryptography",
    "anatomy",
    "mathematics",
    "geometry",
    "programming",
    "engineering",
    "biochemistry",
    "automotive",
    "chess",
    "writing",
    "paganism",
    "genetics",
    "music",
    "sports",
    "cooking",
    "transport",
    "sexuality",
    "pharmacology",
    "vegetable",
    "uncommon",
    "beer",
    "būdinys",
    "manner-of-action",
    "front-vowel",
    "form-of",
    "alt-of",
    "compound-of",
])
for t in valid_tags:
    if t.find(" ") >= 0:
        print("WARNING: TAG CONTAINS SPACE:", t)

ignored_parens = set([
    "please verify",
])


# Words that can be part of form description
valid_words = set(["or", "and"])
for x in valid_tags:
    valid_words.update(x.split(" "))
for x in xlat_tags_map.keys():
    valid_words.update(x.split(" "))


def add_to_valid_tree(tree, tag, v):
    """Helper function for building trees of valid tags/sequences during
    initialization."""
    assert isinstance(tree, dict)
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
        node["$"] = ()
    if v is not None and v not in node["$"]:
        node["$"] += (v,)

# Tree of valid final tags
valid_tree = {}
for tag in valid_tags:
    add_to_valid_tree(valid_tree, tag, tag)

# Tree of sequences considered to be tags (includes sequences that are
# mapped to something that becomes one or more valid tags)
valid_sequences = {}
for tag in valid_tags:
    add_to_valid_tree(valid_sequences, tag, tag)
for k, v in xlat_tags_map.items():
    assert isinstance(k, str)
    assert isinstance(v, (list, str))
    if not v:
        add_to_valid_tree(valid_sequences, k, None)
    elif isinstance(v, str):
        v = [v]
    for vv in v:
        assert isinstance(vv, str)
        add_to_valid_tree(valid_sequences, k, vv)
        add_to_valid_tree(valid_sequences, k.lower(), vv)
        for x in vv.split(" "):
            if x not in valid_tags and x[0].islower():
                print("WARNING: {} in {!r} xlat map but not in valid_tags"
                      .format(x, k))

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


def decode_tags(config, lst, allow_any=False):
    """Decodes tags, doing some canonicalizations.  This returns a list of
    lists of tags."""
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(lst, (list, tuple))
    lsts = [[]]
    for x in lst:
        assert isinstance(x, str)
        for alt in map_with(xlat_tags_map, [x]):
            lsts = list(lst1 + [alt] for lst1 in lsts)
    lsts = map_with(xlat_tags_map, list(map(lambda x: " ".join(x), lsts)))
    lsts = list(map(lambda x: x.split(" "), lsts))
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
                    tags.extend(node["$"])
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i)
                if w not in node and "$" not in node:
                    if allow_any:
                        tag = " ".join(lst[next_i:i + 1])
                        next_i = i + 1
                        if tag not in tags:
                            tags.append(tag)
                        if w in valid_sequences:
                            add_new(valid_sequences[w], i)
                    else:
                        config.warning("unsupported tag at {!r} in {}"
                                       .format(w, lst))
                        tags.append("error")
                        if w in valid_sequences:
                            add_new(valid_sequences[w], next_i)
            if not new_nodes:
                add_new(valid_sequences, max_next_i)
            nodes = new_nodes

        valid_end = False
        for node, next_i in nodes:
            if "$" in node:
                tags.extend(node["$"])
                valid_end = True
        max_next_i = max(x[1] for x in nodes)
        if not valid_end and any(lst[max_next_i]):
            rest = lst[max_next_i:]
            tag = " ".join(rest)
            if tag and not tag[0].isupper():
                config.warning("incomplete tag ending in {}"
                               .format(lst[max_next_i:]))
                tags.append("error")
        tagsets.add(tuple(sorted(tags)))
    ret = list(tagsets)
    return ret


def add_tags(ctx, config, data, lst, allow_any=False):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(lst, (list, tuple))
    for x in lst:
        assert isinstance(x, str)
    tagsets = decode_tags(config, lst, allow_any=allow_any)
    for tags in tagsets:
        data_extend(config, data, "tags", tags)


def add_related(ctx, config, data, lst, related):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(lst, (list, tuple))
    for x in lst:
        assert isinstance(x, str)
    assert isinstance(related, (list, tuple))
    related = " ".join(related)
    if related == "-":
        config.warning("add_related: unhandled {} related form {}"
                       .format(lst), related)
        return
    for related in related.split(" or "):
        if related:
            m = re.match(r"\(([^()]|\([^)]*\))*\)\s*", related)
            if m:
                paren = m.group(1)
                related = related[m.end():]
                tagsets1 = decode_tags(config,
                                       split_at_comma_semi(paren))
            else:
                tagsets1 = [[]]
            tagsets2 = decode_tags(config, lst)
            for tags1 in tagsets1:
                for tags2 in tagsets2:
                    if "alt-of" in tags2:
                        data_extend(config, data, "tags", tags1)
                        data_extend(config, data, "tags", tags2)
                        data_append(config, data, "alt_of", related)
                    elif "form-of" in tags2:
                        data_append(config, data, "tags", tags1)
                        data_append(config, data, "tags", tags2)
                        data_append(config, data, "inflection_of", related)
                    elif "compound-of" in tags2:
                        data_append(config, data, "tags", tags1)
                        data_append(config, data, "tags", tags2)
                        data_append(config, data, "compound", related)
                    else:
                        form = {"form": related}
                        data_extend(config, form, "tags", tags1)
                        data_extend(config, form, "tags", tags2)
                        data_append(config, data, "forms", form)


def parse_word_head(ctx, config, pos, text, data):
    """Parses the head line for a word for in a particular language and
    part-of-speech, extracting tags and related forms."""
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    #print("parse_word_head:", text)
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
            # XXX change this to parse the part after the word form using
            # valid_sequences
            baseparts = list(m.group(0) for m in re.finditer(word_re, alt))
            if " ".join(baseparts) in valid_tags and desc_i > 0:
                lst = []  # Word form
                rest = baseparts  # Tags
            else:
                lst = []  # Word form (NOT tags)
                i = 0
                while i < len(baseparts):
                    word = baseparts[i]
                    w = distw(titleparts, word)  # 0=identical..1=very different
                    if (word == title or word in blocked or
                        word in titleparts or
                        ((w <= 0.7 or len(word) <= 4) and
                         word not in valid_tags and word not in xlat_tags_map)):
                        lst.append(word)
                    else:
                        break
                    i += 1
                rest = baseparts[i:]
            # lst is canonical form of the word
            # rest is additional tags (often gender m/f/n/c/...)
            if lst and title != " ".join(lst):
                add_related(ctx, config, data, ["canonical"], lst)
            # XXX here we should only look at a subset of tags allowed
            # in the base
            add_tags(ctx, config, data, rest)

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
                    (w >= 0.7 or len(word) < 4) and
                    (part in node or
                     ("$" in node and part in valid_sequences))):
                    # Consider it part of a descriptor
                    if part in node:
                        if "$" in node:
                            lst.extend(parts[last_valid:i])
                            last_valid = i
                        node = node[part]
                    else:
                        assert "$" in node
                        lst.extend(parts[last_valid:i])
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
                # Stop if we have completed parsing something that is always
                # followed by a word form
                if "alt-of" in lst or "form-of" in lst or "compound-of" in lst:
                    break
                i += 1
            if "$" in node:
                lst.extend(parts[last_valid:i])
                last_valid = i
            related = parts[last_valid:]
            # XXX check if related contains valid tag sequences and warn if
            # so
            for tagspec in " ".join(lst).split(" or "):
                lst = tagspec.split(" ")
                if related:
                    add_related(ctx, config, data, lst, related)
                else:
                    add_tags(ctx, config, data, lst)


def parse_sense_tags(ctx, config, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_sense_tags:", text)
    for semi in split_at_comma_semi(text):
        tags = map_with(xlat_tags_map, [semi])
        tagsets = decode_tags(config, tags, allow_any=True)
        # XXX should think how to handle distinct options better,
        # e.g., "singular and plural genitive"; that can't really be
        # done with changing the calling convention of this function.
        # XXX should handle cases where it is actually form-of or alt-of
        for tags in tagsets:
            data_extend(config, data, "tags", tags)


def parse_pronunciation_tags(ctx, config, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    tags = map_with(xlat_tags_map, split_at_comma_semi(text))
    # XXX should think how to handle distinct options better,
    # e.g., "singular and plural genitive"; that can't really be
    # done with changing the calling convention of this function.

    # XXX remove this?
    #tagsets = decode_tags(config, tags, allow_any=True)
    #for tags in tagsets:
    #    data_extend(config, data, "tags", tags)
    data_extend(config, data, "tags", tags)


def parse_translation_desc(ctx, config, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_translation_desc:", text)

    # Handle the part of the head that is not in parentheses
    base = re.sub(r"\(([^()]|\([^)]*\))*\):?", "", text)
    base = re.sub(r"\s+", " ", base).strip()
    baseparts = list(m.group(0) for m in re.finditer(word_re, base))
    lst = []  # Word form (NOT tags)
    i = 0
    while i < len(baseparts):
        word = baseparts[i]
        if word == "•":
            continue
        if word in blocked or not lst or word not in valid_words:
            lst.append(word)
        else:
            break
        i += 1
    rest = baseparts[i:]
    # lst is canonical form of the word
    # rest is additional tags (often gender m/f/n/c/...)
    data["word"] = " ".join(lst)
    # XXX here we should only look at a subset of tags allowed
    # in the translation
    for tagdesc in map_with(xlat_tags_map, [" ".join(rest)]):
        for tagpart in tagdesc.split(" or "):
            add_tags(ctx, config, data, tagpart.split(" "))

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
                    add_tags(ctx, config, data, [new_desc],
                             allow_any=True)
                elif new_desc[0].isupper() and not ctx.title[0].isupper():
                    data_append(config, data, "tags", new_desc)
                elif "alt" not in data:
                    data["roman"] = new_desc
                else:
                    config.warning("maybe more than one romanization: {!r}"
                                   .format(text))
                    data_append(config, data, "tags", "error")

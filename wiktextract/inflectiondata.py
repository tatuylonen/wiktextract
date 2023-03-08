# -*- fundamental -*-
#
# Data for parsing inflection tables
#
# Copyright (c) 2021, 2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
from .tags import valid_tags, head_final_numeric_langs
from wiktextract.parts_of_speech import PARTS_OF_SPEECH

# Languages where possessive forms (e.g. pronouns) inflect according to the
# gender/number of the possessed object(s)
POSSESSIVE_POSSESSED_LANGS = set([
    "Azerbaijani",
    "Danish",
    "Faroese",
    "Icelandic",
    "Kumyk",
    "Norwegian Bokmål",
    "Norwegian Nynorsk",
    "Quechua",
    "Swedish",
    "Uyghur",
    "Turkish",
])

# Languages that have numbered infinitives (infinitive-i etc)
LANGS_WITH_NUMBERED_INFINITIVES = set([
    "Finnish",
    "Ingrian",
    "Veps",
    "Northern Sami",
    "Proto-Samic",
    "Skolt Sami",
    "Lule Sami",
    "Inari Sami",
    "Pite Sami",
])


# Inflection map for parsing headers in tables.

# When the parser encounters a header in a table, it checks here for a key, like
# "plural". Then if that key leads to a string, or a list or tuple of strings,
# it uses those tag strings as the tags for that header. If it encounters a
# dict, it recursively uses entries in the dict to perform simple if-then-else
# control flow.
# "default": default tag string or list; propagates to lower levels
# "then": follow this if "if", "lang" and "pos" are all true
# "if": if the current header already has some tags, check if it has these ones
# "lang": is the current language equal to string or in a list of strings
# "pos": is the current PART OF SPEECH equal to string or in a list of strings
# "nested-table-depth": is the current depth of nested tables, and only tables.
# Only in scope from handle_wikitext_table() onwards and not stored for anything
# else.
 
infl_map = {
    "plural": {
        "default": "plural",
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-many",
        "else": {
            "if": "combined-form",
            "then": "object-plural",
        },
    },
    "singular": {
        "default": "singular",
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-single",
        "else": {
            "if": "combined-form",
            "then": "object-singular",
            "else": "singular",
        },
    },
    "accusative": "accusative",
    "dative": "dative",
    "instrumental": "instrumental",
    "ablative": "ablative",
    "illative": "illative",
    "elative": "elative",
    "adessive": "adessive",
    "allative": "allative",
    "possessor": "possessive",
    "vocative": "vocative",
    "Singular": "singular",
    "instructive": "instructive",
    "Plural": "plural",
    "1st person": {
        "if": "combined-form",
        "then": "object-first-person",
        "else": "first-person",
    },
    "2nd person": {
        "if": "combined-form",
        "then": "object-second-person",
        "else": "second-person",
    },
    "3rd person": {
        "if": "combined-form",
        "then": "object-third-person",
        "else": "third-person",
    },
    "1st - Singular": "first-person singular",
    "2nd - Singular": "second-person singular",
    "3rd - Singular Masculine": "third-person singular masculine",
    "3rd - Singular Feminine": "third-person singular feminine",
    "3rd - Singular Neuter": "third-person singular neuter",
    "1st - Plural": "first-person plural",
    "2nd - Plural": "second-person plural",
    "3rd - Plural": "third-person plural",
    "2nd - Polite": "second-person polite",
    "1st infinitive": "infinitive infinitive-i",
    "2nd infinitive": "infinitive infinitive-ii",
    "3rd infinitive": "infinitive infinitive-iii",
    "1 sg": "first-person singular",
    "2 sg": "second-person singular",
    "3 sg": "third-person singular",
    "1 pl": "first-person plural",
    "2 pl": "second-person plural",
    "3 pl": "third-person plural",
    "nom.": "nominative",
    "gen.": "genitive",
    "Nominative": "nominative",
    "Genitive": "genitive",
    "Dative": "dative",
    "Vocative": "vocative",
    "Accusative": "accusative",
    "feminine": {
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-feminine",
        "else": "feminine",
    },
    "neuter": {
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-neuter",
        "else": "neuter",
    },
    "Ablative": "ablative",
    "imperative": "imperative",
    "causal-final": "causal-final",
    "essive-formal": "essive-formal",
    "essive-modal": "essive-modal",
    "superessive": "superessive",
    "sublative": "sublative",
    "delative": "delative",
    "non-attributive possessive - singular":
    "predicative possessive possessed-single",  # XXX check hűtő/Hungarian/Noun
    "non-attributive possessive - plural":
    "predicative possessive possessed-single",
    "infinitive": "infinitive",
    "prepositional": "prepositional",
    "masculine": {
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-masculine",
        "else": "masculine",
    },
    "error-unrecognized-form": "error-unrecognized-form",  # internal use
    "active": "active",
    "passive": "passive",
    "Case": "*",  # Interpret the column as headers (e.g., anglais/Irish)
    "participles": "participle",
    "Participles": "participle",
    "PARTICIPLES (divdabji)": "participle",
    "Present forms": "present",
    "Transgressives": "transgressive",
    "past tense": "past",
    "Positive participial": "positive participle",
    "Negative participial": "negative participle",
    "present tense": "present",
    "future tense": "future",
    "Neuter": "neuter",
    # "Masculine": "masculine",
    "Feminine": "feminine",
    "adverbial": "adverbial",
    "1st singular (я)": "first-person singular",
    "2nd singular (ты)": "second-person singular",
    "3rd singular (он/она́/оно́)": "third-person singular",
    "1st plural (мы)": "first-person plural",
    "2nd plural (вы)": "second-person plural",
    "3rd plural (они́)": "third-person plural",
    "plural (мы/вы/они́)": "plural",
    "masculine (я/ты/он)": "masculine",
    "feminine (я/ты/она́)": "feminine",
    "neuter (оно́)": "neuter",
    "feminine + neuter singular": "feminine neuter singular",
    "1st person plural": "first-person plural",
    "2nd person plural": "second-person plural",
    "3rd person plural": "third-person plural",
    "single possession": "possessive possessed-single",
    "multiple possessions": "possessive possessed-many",
    "1st person sing.": "first-person singular",
    "2nd person sing.": "second-person singular",
    "2nd person sing. (u)": "second-person singular formal",
    "2nd person sing. (gij)": ["second-person singular archaic "
                               "formal majestic",
                               "second-person singular colloquial Flanders"],
    "3rd person sing.": "third-person singular",
    "2d person sing.": "second-person singular",
    "3d sing. masc.": "third-person singular masculine",
    "3d sing. fem.": "third-person singular feminine",
    "1st person pl.": "first-person plural",
    "2d person pl.": "second-person plural",
    "3d person pl.": "third-person plural",
    "First": "first-person",
    "Second": "second-person",
    "Third": "third-person",
    "Case / Gender": "",
    "masculine inanimate": "masculine inanimate",
    "Infinitive": "infinitive",
    "Past indicative": "past indicative",
    "Past participle": "past participle",
    "Past participles": "past participle",
    "past participle plural": "past participle plural",
    "Passive participles": "passive participle",
    "Present participle": "present participle",
    "present participle/gerund": "present participle",
    "1st person sg": "first-person singular",
    "2nd person sg informal": "second-person singular informal",
    "3rd person sg 2nd p. sg formal":
    ["third-person singular",
     "third-person singular formal second-person-semantically"],
    "1st person pl": "first-person plural",
    "3rd person pl 2nd p. pl formal":
    ["third-person plural",
     "third-person plural formal second-person-semantically"],
    "Indica­tive mood": "indicative",
    "Pre­sent": "present",
    "Indef.": {
        "lang": "Hungarian",
        "then": "object-indefinite",
        "else": "indefinite",
    },
    "Def.": {
        "lang": "Hungarian",
        "then": "object-definite",
        "else": "definite",
    },
    "2nd-p. o.": "object-second-person",
    "m verbs conjugated according to third person sg. er":
    "third-person singular",
    "m verbs conjugated according to 3nd person sg. er":
    "third-person singular",
    "verbs conjugated according to 2nd person pl. ihr":
    "second-person plural",
    "verbs conjugated according to 3rd person pl. sie":
    "second-person plural",
    "2nd person plural (familiar)": "second-person plural familiar",
    "2nd person sg. or pl. (polite)": "second-person singular plural polite",
    "2nd person sg. or pl. (elevated²)":
    "second-person singular plural polite archaic",
    "Condi­tional mood": "conditional",
    "Sub­junc­tive mood": "subjunctive",
    "Other nonfinite verb forms": {
        "lang": "Hungarian",
        "then": "",
        "else": "dummy-mood",
    },
    "Verbal noun": "noun-from-verb",
    "Future part.": "future participle",
    "Future I": "future future-i",
    "Future II": "future future-ii",
    "Adverbial part.": "adverbial participle",
    "Potential": "potential",
    "potential": "potential",
    "present": "present",
    "virile": "virile",
    "nonvirile": "nonvirile",
    "case": "",
    "nominative, vocative": "nominative vocative",
    "indefinite": "indefinite",
    "masculine personal/animate": {
        "lang": "Polish",
        "then": "masculine animate",
        "else": "masculine personal animate",
    },
    "perfective aspect": "perfective",
    "definite": "definite",
    "animate": "animate",
    "inanimate": "inanimate",
    "Dual": "dual",
    "indicative": "indicative",
    "subjunctive": "subjunctive",
    "person": {
        "lang": "Polish",
        "then": "",  # Needs to be empty for mówić/Polish
    },
    "Forms with the definite article": "definite",
    "Forms with the definite article:": "definite",
    "indefinite articulation": "indefinite",
    "definite articulation": "definite",
    "nominative/accusative": "nominative accusative",
    "genitive/dative": "genitive dative",
    "imperfective aspect": "imperfective",
    "future": "future",
    "Immediate future": "future future-near",
    "Remote future": "future future-remote",
    "Comparative": "comparative",
    "Superlative": "superlative",
    "perfect": "perfect",
    "gerund": "gerund",
    "first": "first-person",
    "second": "second-person",
    "third": "third-person",
    "imperfect": "imperfect",
    "infinitives": "infinitive",
    "conditional": "conditional",
    "pluperfect": "pluperfect",

    # XXX These need to be better structured, but I don't know where these
    # are from (see e.g. cois/Irish)
    "Bare forms": "indefinite",
    "Bare forms:": "",

    "past": "past",
    "1st": {
        "default": "first-person",
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-i",
        "else": {
            "lang": "Swahili",
            "then": "first-person"
        },
    },
    "2nd":  {
        "default": "second-person",
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-ii",
        "else": {
            "lang": "Swahili",
            "then": "second-person"
        },
    },
    "3rd":  {
        "default": "third-person",
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-iii",
    },
    "4th": {
        "default": "fourth-person",
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-iv",
    },
    "5th": {
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-v",
    },
    "Case / #": "",
    # XXX needs special handling ['-льник', '-овка', '-ник']
    "accusative animate inanimate": "accusative animate inanimate",
    "negative": "negative",
    "past participle": "past participle",
    "indicative mood": "indicative",
    "nominative/ accusative": "nominative accusative",
    "genitive/ dative": "genitive dative",
    "Positive": "positive",
    "short form": "short-form",
    "Short past participle": "past participle short-form",
    "Long past participle": "past participle long-form",
    "positive": "positive",
    "1st sing.": "first-person singular",
    "2nd sing.": "second-person singular",
    "3rd sing.": "third-person singular",
    "1st plur.": "first-person plural",
    "2nd plur.": "second-person plural",
    "3rd plur.": "third-person plural",
    "conditional mood": "conditional",
    "imperative mood": "imperative",
    "potential mood": "potential",
    "Nominal forms": "dummy-reset-headers",  # Reset column inheritance
    "long 1st": "infinitive-i-long",
    "I": {
         "lang": LANGS_WITH_NUMBERED_INFINITIVES,
         "if": "infinitive",
         "then": "infinitive-i",
         "else": {
            "lang": "Czech",  # podnikat/Czech
            "then": "first-person singular",
            "else": {
                "lang": "Komi-Zyrian",  # ань/Komi-Zyrian
                "if": "accusative",
                "then": "accusative-i",
                "else": {
                    "lang": "Komi-Zyrian",
                    "if": "prolative",
                    "then": "prolative-i",
                    "else": {
                        "lang": "Avar",
                        "if": "locative",
                        "then": "locative-i",
                        "else": {
                            "lang": "Avar",
                            "if": "allative",
                            "then": "allative-i",
                            "else": {
                                "lang": "Avar",
                                "if": "ablative",
                                "then": "ablative-i",
                                "else": {
                                    "lang": "Avar",
                                    "if": "translative",
                                    "then": "translative-i",
                                },
                            },
                        },
                    },
                },
            },
                
          },
    },
    "long I": {
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-i-long",
    },
    "II": {
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-ii",
        "else": {
            "lang": "Komi-Zyrian",  # ань/Komi-Zyrian
            "if": "accusative",
            "then": "accusative-ii",
            "else": {
                "lang": "Komi-Zyrian",
                "if": "prolative",
                "then": "prolative-ii",
                "else": {
                    "lang": "Avar",
                    "if": "locative",
                    "then": "locative-ii",
                    "else": {
                        "lang": "Avar",
                        "if": "allative",
                        "then": "allative-ii",
                        "else": {
                            "lang": "Avar",
                            "if": "ablative",
                            "then": "ablative-ii",
                            "else": {
                                "lang": "Avar",
                                "if": "translative",
                                "then": "translative-ii",
                            },
                        },
                    },
                },
            },
        },
    },
    "III": {
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-iii",
        "else": {
            "lang": "Avar",
            "if": "locative",
            "then": "locative-iii",
            "else": {
                "lang": "Avar",
                "if": "allative",
                "then": "allative-iii",
                "else": {
                    "lang": "Avar",
                    "if": "ablative",
                    "then": "ablative-iii",
                    "else": {
                        "lang": "Avar",
                        "if": "translative",
                        "then": "translative-iii",
                    },
                },
            },
        },
    },
    "IV": {
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-iv",
        "else": {
            "lang": "Avar",
            "if": "locative",
            "then": "locative-iv",
            "else": {
                "lang": "Avar",
                "if": "allative",
                "then": "allative-iv",
                "else": {
                    "lang": "Avar",
                    "if": "ablative",
                    "then": "ablative-iv",
                    "else": {
                        "lang": "Avar",
                        "if": "translative",
                        "then": "translative-iv",
                    },
                },
            },
        },
    },
    "V": {
        "lang": LANGS_WITH_NUMBERED_INFINITIVES,
        "if": "infinitive",
        "then": "infinitive-v",
        "else": {
            "lang": "Avar",
            "if": "locative",
            "then": "locative-v",
            "else": {
                "lang": "Avar",
                "if": "allative",
                "then": "allative-v",
                "else": {
                    "lang": "Avar",
                    "if": "ablative",
                    "then": "ablative-v",
                    "else": {
                        "lang": "Avar",
                        "if": "translative",
                        "then": "translative-v",
                    },
                },
            },
        },
    },
    "agent": "agent",
    "Plural (m/f)": "plural masculine feminine",
    "(strong noun)": "strong",
    "(weak noun)": "weak",
    "Weak conjugation": "weak",
    "Strong conjugation": "strong",
    "Masc./Fem.": "masculine feminine",
    "present participle": "present participle",
    "number case / gender": "",
    "Case/Gender": "",
    "Derived forms": "",
    "Adverb": "adverbial",
    "augmentative": "augmentative",
    "diminutive": "diminutive",
    "singular (vienaskaita)": "singular",
    "plural (daugiskaita)": "plural",
    "nominative (vardininkas)": "nominative",
    "genitive (kilmininkas)": "genitive",
    "dative (naudininkas)": "dative",
    "accusative (galininkas)": "accusative",
    "instrumental (įnagininkas)": "instrumental",
    "locative (vietininkas)": "locative",
    "vocative (šauksmininkas)": "vocative",
    "ie": {
        "lang": "Dutch",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
        "else": {
            "lang": ["Middle French", "Old Occitan", "Ladin",],
            "pos": "verb",
            "if": "first-person singular",
            "then": "first-person singular",
        },
    },
    "io": {
        "lang": ["Aromanian", "Interlingua", "Istro-Romanian",
                 "Italian", "Neapolitan"],
        "pos":  ["verb", "suffix"],  # -urre/Italian; Added Italian entries
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "tu": {
        "lang": ["Aromanian", "Asturian", "Catalan", "French", "Friulian",
                 "Gallurese",
                 "Gaulish", "Ido", "Interlingua", "Italian", "Kalasha",
                 "Kalo Finnish Romani", "Ladino", "Latgalian", "Latin",
                 "Latvian", "Lithuanian", "Middle French",
                 "Mirandese", "Neapolitan",
                 "Northern Kurdish", "Old French",
                 "Occitan", "Old Irish", "Old Portuguese",
                 "Phalura", "Portuguese", "Romani", "Romanian",
                 "Sassarese", "Savi",
                 "Scottish Gaelic", "Sicilian", "Sinte Romani",
                 "Sudovian", "Tarantino", "Tocharian A", "Welsh Romani"],
        "pos":  ["verb", "suffix"],
        "then": "second-person",
        "else": {
            "lang": "Ladin",
            "then": "second-person singular",
        },
    },
    "lui/lei, esso/essa": {
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "lui/lei": {  # calere/Italian
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "noi": {
        "lang": ["Aromanian", "Corsican", "Gallurese",
                 "Italian", "Piedmontese", "Romanian", "Sassarese"],
        "pos":  ["verb", "suffix"],
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "voi": {
        "lang": ["Aromanian", "Corsican", "Gallurese",
                 "Italian", "Piedmontese", "Romanian", "Sassarese"],
        "pos":  ["verb", "suffix"],
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "loro, essi/esse": {
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "loro": {  # calere/Italian
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "che io": {
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "che tu": {
        "lang": ["Italian", "Ladin"],
        "pos":  ["verb", "suffix"],
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "che lui/che lei, che esso/che essa": {
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "che lui/che lei": {  # calere/Italian
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "che noi": {
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "che voi": {
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "che loro, che essi/che esse": {
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "che loro": {  # calere/Italian
        "lang": "Italian",
        "pos":  ["verb", "suffix"],
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "io/mini/mine": {
        "lang": "Aromanian",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "mini / mine": {  # escu/Aromanian
        "lang": "Aromanian",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "tu/tini/tine": {
        "lang": "Aromanian",
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "tini / tine": {  # escu/Aromanian
        "lang": "Aromanian",
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "nãsh/nãshi, nãsi/nãse, elj, eali/eale": {
        "lang": "Aromanian",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "nãsh, nãse / nãsi, elj, eali": {
        "lang": "Aromanian",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "nãs, nãsã / nãsa, el, ea": {
        "lang": "Aromanian",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "eiu": {
        "lang": "Corsican",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "tù": {
        "lang": "Corsican",
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "ellu/ella": {
        "lang": "Corsican",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "elli/elle": {
        "lang": "Corsican",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "eu": {
        "lang": ["Galician", "Gallurese",
                 "Old Occitan", "Old Portuguese", "Portuguese",
                 "Romanian", "Romansch"],
        "pos": "verb",
        # ~ "if": "first-person singular",
        "then": "first-person singular",
    },
    "el/ea": {
        "lang": "Romanian",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "ei/ele": {
        "lang": "Romanian",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "aš": {
        "lang": "Lithuanian",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person",
    },
    "jis/ji": {
        "lang": "Lithuanian",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person",
    },
    "mes": {
        "lang": ["Latgalian", "Latvian", "Lithuanian", "Old Prussian"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person",
    },
    "mēs": {
        "lang": "Latvian",
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "es": {
        "lang": ["Alemannic German", "Cimbrian", "German", "Hunsrik",
                 "Pennsylvania German", "Sudovian"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
        "else": {
            "lang": ["Bavarian"],
            "pos": "verb",
            "if": "second-person plural familiar",
            "then": "second-person plural familiar",
            "else": {
                "lang": "Kabuverdianu",
                "pos": "verb",
                "if": "third-person plural",
                "then": "third-person plural",
                "else": {
                    "lang": ["Latgalian", "Latvian"],
                    "pos": "verb",
                    "if": "first-person singular",
                    "then": "first-person singular",
                },
            },
        },
    },
    "jūs": {
        "lang": ["Latvian", "Lithuanian", "Old Prussian"],
        "pos": "verb",
        "if": "singular",
        "then": "second-person singular",
        "else": {
            "lang": ["Latvian", "Lithuanian", "Old Prussian"],
            "pos": "verb",
            "if": "plural",
            "then": "second-person plural",
            "else": "second-person plural",
        },
    },
    "jie/jos": {
        "lang": "Lithuanian",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "jie": {
        "lang": "Saterland Frisian",
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
        "else": {
            "lang": "Saterland Frisian",
            "pos": "verb",
            "if": "second-person plural",
            "then": "second-person plural",
        },
    },
    "ije": {
        "lang": ["Neapolitan", "Tarantino"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "jidde / jèdde": {
        "lang": "Tarantino",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "nuje": {
        "lang": ["Neapolitan", "Tarantino"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "vuje": {
        "lang": ["Neapolitan", "Tarantino"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "lóre": {
        "lang": "Tarantino",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "lloro": {
        "lang": "Neapolitan",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "isso/essa": {
        "lang": "Neapolitan",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "cu ije": {
        "lang": "Tarantino",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "cu tu": {
        "lang": ["Neapolitan", "Tarantino",],
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "cu jidde / cu jèdde": {
        "lang": "Tarantino",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "cu nuje": {
        "lang": ["Neapolitan", "Tarantino",],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "cu vuje": {
        "lang": "Tarantino",
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "cu lóre": {
        "lang": "Tarantino",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "ca io": {
        "lang": "Neapolitan",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "ca isso/ca essa": {
        "lang": "Neapolitan",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "ca vuje": {
        "lang": "Neapolitan",
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "ca lloro": {
        "lang": "Neapolitan",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "ja": {
        "lang": ["Assan", "Guerrero Amuzgo", "Gutnish", "Lower Sorbian",
                 "Polish", "Serbo-Croatian", "Slovak", "Upper Sorbian"],
        "pos": ["verb", "suffix"],
        "if": "first-person singular",
        "then": "first-person singular",
        "else": {
            "lang": "North Frisian",
            "pos": "verb",
            "if": "third-person plural",
            "then": "third-person plural",
        },
    },
    "ti": {
        "lang": ["Albanian", "Galician", "Istriot", "Ligurian", "Piedmontese",
                 "Romansch", "Serbo-Croatian", "Slovene", "Welsh", "Cumprar",],
        "pos": ["verb", "suffix"],
        # ~ "if": "second-person singular",
        "then": "second-person singular",
        "else": {
            "lang": "Czech",
            "pos": "verb",
            # ~ "if": "third-person plural",
            "then": "third-person plural",
            "else": {
                "lang": "Hungarian",
                "pos": "verb",
                # ~ "if": "second-person plural",
                "then": "second-person plural",
            },
        },
    },
    "on / ona / ono": {
        "lang": ["Czech", "Old Czech", "Polish", "Serbo-Croatian", "Slovak",
                 "Slovene"],
        "pos": ["verb", "suffix"],
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "mi": {
        "lang": ["Bislama", "Esperanto", "Fula", "Ga", "Gaulish",
                 "Guinea-Bissau Creole", "Jamaican Creole",
                 "Kabuverdianu", "Ligurian", "Nigerian Pidgin", "Nzadi",
                 "Önge", "Papiamentu", "Piedmontese", "Pijin",
                 "Scottish Gaelic", "Sranan Tongo", "Tok Pisin",
                 "Welsh"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
        "else": {
            "lang": ["Hungarian", "Serbo-Croatian", "Slovene"],
            "pos": ["verb", "suffix"],
            "if": "first-person plural",
            "then": "first-person plural",
            "else": {
                "lang": ["Ewe", "Laboya"],
                "pos": "verb",
                "if": "second-person plural",
                "then": "second-person plural",
                "else": {
                    "lang": "Jarawa",
                    "pos": "verb",
                    "if": "first-person singular",  # both plural and singular
                    "then": "first-person singular",
                    "else": {
                        "lang": "Jarawa",
                        "pos": "verb",
                        "if": "first-person plural",
                        "then": "first-person plural",
                    },
                },
            },
        },
    },
    "vi": {
        "lang": ["Danish", "Norwegian Bokmål", "Norwegian Nynorsk",
                 "Swedish"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
        "else": {
            "lang": ["Esperanto", "Ido", "Serbo-Croatian"],
            "pos": ["verb", "suffix"],
            "if": "second-person plural",
            "then": "second-person plural",
            "else": {
                "lang": "Slovene",
                "pos": "verb",
                "if": "second-person",  # plural or (formal) singular
                "then": "second-person",
            },
        }
    },
    "oni / one / ona": {
        "lang": ["Czech", "Old Czech", "Polish", "Serbo-Croatian", "Slovak",
                 "Slovene"],
        "pos": ["verb", "suffix"],
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "ono": {
        "lang": "Hadza",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "me": {
        "lang": "Romani",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "amen": {
        "lang": "Romani",
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "tumen": {
        "lang": "Romani",
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "on": {
        "lang": "Romani",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "Lei": {
        "lang": "Italian",
        "if": "third-person",
        "then": "third-person singular formal second-person-semantically",
    },
    "Loro": {
        "lang": "Italian",
        "if": "third-person",
        "then": "third-person plural formal second-person-semantically",
    },
    "yo": {
        "lang": ["Afar", "Aragonese", "Asturian", "Chavacano", "Kristang",
                 "Ladino", "Spanish"],
        "pos": ["verb", "suffix"],
        "if": "first-person singular",
        "then": "first-person singular",
        "else": {
            "lang": "Haitian Creole",
            "pos": "verb",
            "if" :"third-person plural",
            "then": "third-person plural",
        },
    },
    "vos": {
        "lang": ["Interlingua", "Ladino", "Latin", "Old French",
                 "Old Occitan", "Sardinian", "Lorrain",],
        "pos": "verb",
        "then": "second-person",
        "else": {
            "lang": ["Ladin", "Walloon",],
            "then": "second-person plural",
        },
    },
    "tú": {
        "lang": ["Aragonese", "Faroese", "Irish", "Ladino", "Old Irish"],
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "jo": {
        "lang": ["Catalan", "Friulian", "Occitan", "Old French", "Silesian"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
        "else": {
            "lang": ["North Frisian", "Saterland Frisian"],
            "pos": "verb",
            "if": "third-person singular",
            "then": "third-person singular",
        },
    },
    "ell/ella vostè": {
        "lang": "Catalan",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "nosaltres nós": {
        "lang": "Catalan",
        "pos": "verb",
        "if": "first-person plural",
         "then": "first-person plural",
    },
    "vosaltres vós": {
        "lang":  "Catalan",
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "ells/elles vostès": {
        "lang": "Catalan",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "vostè": {
        "lang": "Catalan",
        "pos": "verb",
        "if": "third-person singular",
        "then": "formal second-person-semantically",
    },
    "nosaltres": {
        "lang": "Catalan",
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "vostès": {
        "lang": "Catalan",
        "pos": "verb",
        "if": "third-person plural",
        "then": "formal second-person-semantically",
    },
    "tú vos": {
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "él/ella/ello usted": {
        "lang": "Spanish",
        "pos": ["verb", "suffix"],
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "nosotros nosotras": {
        "lang": ["Asturian", "Spanish"],
        "pos": ["verb", "suffix"],
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "vosotros vosotras": {
        "lang": ["Spanish"],
        "pos": ["verb", "suffix"],
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "ellos/ellas ustedes": {
        "lang": "Spanish",
        "pos": ["verb", "suffix"],
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "usted": {
        "lang": "Spanish",
        "pos": ["verb", "suffix"],
        "if": "imperative",
        "then": ["third-person singular formal second-person-semantically",
                 "third-person singular"],
    },
    "ustedes": {
        "lang": "Spanish",
        "pos": ["verb", "suffix"],
        "if": "imperative",
        "then": ["third-person plural formal second-person-semantically",
                 "third-person plural"],
    },

    "je (j’)": {
        "lang": "French",
        "pos": ["verb", "suffix",],
        "then": "first-person singular",
    },
    "il, elle, on": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "third-person singular",
    },
    "il, elle": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "third-person singular",
    },
    "nous": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "first-person plural",
    },
    "vous": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "second-person plural",
    },
    "ils, elles": {
        "lang": "French",
        "pos": ["verb", "suffix",],
        "then": "third-person plural",
    },
    "que je (j’)": {
        "lang": "French",
        "pos": ["verb", "suffix",],
        "then": "first-person singular",
    },
    "que tu": {
        "lang": ["French", "Middle French", "Old French",
                 "Lorrain",],
        "pos": ["verb", "suffix",],
        "then": "second-person singular",
    },
    "qu’il, qu’elle": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "third-person singular",
    },
    "que nous": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "first-person plural",
    },
    "que vous": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "second-person plural",
    },
    "qu’ils, qu’elles": {
        "lang": ["French", "Middle French"],
        "pos": ["verb", "suffix",],
        "then": "third-person plural",
    },
    "ie (i’)": {
        "lang": "Middle French",
        "pos": "verb",
        "then": "first-person singular",
    },
    "ilz, elles": {
        "lang": "Middle French",
        "pos": "verb",
        "then": "third-person plural",
    },
    "que ie (i’)": {
       "lang": "Middle French",
       "pos": "verb",
       "then": "first-person singular",
    },
    "qu’ilz, qu’elles": {
        "lang": "Middle French",
        "pos": "verb",
        "then": "third-person plural",
    },
    "il": {
        "lang": ["Old French"],
        "pos": "verb",
        "then": "third-person",
    },
    "nos": {
        "lang": ["Lorrain", "Old French", "Ladin",],
        "pos": "verb",
        "then": "first-person plural",
    },
    "que jo": {
        "lang": ["Old French"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "qu’il": {
        "lang": "Old French",
        "pos": "verb",
        "if": "third-person",
        "then": "third-person",
    },
    "que nos": {
        "lang": "Old French",
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "que vos": {
        "lang": ["Old French", "Lorrain",],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "lui/jê": {
        "lang": "Friulian",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "nô": {
        "lang": "Friulian",
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "vô": {
        "lang": "Friulian",
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "lôr": {
        "lang": "Friulian",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "ես": {
        "lang": ["Armenian", "Old Armenian"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "դու": {
        "lang": ["Armenian", "Old Armenian"],
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "նա": {
        "lang": ["Armenian", "Old Armenian"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "դուք": {
        "lang": ["Armenian", "Old Armenian"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "(դու)": {
        "lang": ["Armenian", "Old Armenian"],
        "pos": "verb",
        "if": "second-person singular",
        "then": "rare",
    },
    "(դուք)": {
        "lang": ["Armenian", "Old Armenian"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "rare",
    },
    "nós": {
        "lang": ["Asturian", "Galician", "Indo-Portuguese", "Mirandese",
                 "Portuguese"],
        "pos": "verb",
        # ~ "if": "first-person plural",
        "then": "first-person plural",
    },
    "el/ela/Vde.": {
        "lang": "Galician",
        "pos": "verb",
        # ~ "if": "third-person singular",
        "then": "third-person singular",
    },
    "eles/elas/Vdes.": {
        "lang": "Galician",
        "pos": "verb",
        # ~ "if": "third-person plural",
        "then": "third-person plural",
    },
    "mì": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "tì te": {
       "lang": ["Lombard", "Western Lombard"],
       "pos": "verb",
       "if": "second-person singular",
       "then": "second-person singular",
    },
    "lù el / lee la": {
       "lang": ["Lombard", "Western Lombard"],
       "pos": "verb",
       "if": "third-person singular",
       "then": "third-person singular",
    },
    "nun": {
        "lang": ["Lombard", "Western Lombard", "Wolof"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "violter / vialter": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "lor": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "iu": {
        "lang": "Sicilian",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "iddu/idda": {
        "lang": ["Gallurese", "Sicilian"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "éiu, eu":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "eddu/edda":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "eddi":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "che éiu, chi eu":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "chi eddu/edda":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "chi noi":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "chi voi":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "chi eddi":  {
        "lang": "Sassarese",
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "nuàutri": {
        "lang": "Sicilian",
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "vuàutri": {
        "lang": "Sicilian",
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "iddi": {
        "lang": ["Gallurese", "Sicilian"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "(che) mì": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "(che) tì te": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "(che) lù el / lee la": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "(che) nun": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "(che) violter / vialter": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "(che) lor": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "tì": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "lù / lee che el": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "lor che el": {
        "lang": ["Lombard", "Western Lombard"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "mé": {
        "lang": ["Eastern Lombard", "Irish", "Lombard", "Old Irish"],
        "pos": "verb",
        "if": "first-person singular",
         "then": "first-person singular",
    },
    "té": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "lü / le": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "lü / lé": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "nóter": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "vóter": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "lur / lùre": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "lur / lúre": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "(che) mé": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "(che) té": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "second-person singular",
        "then": "second-person singular",
    },
    "(che) lü / le": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "(che) lü / lé": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
    },
    "(che) nóter": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "(che) vóter": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "(che) lur / lùre": {
        "lang": ["Eastern Lombard", "Lombard"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "non-finite forms": {
        "lang": "Latin",
        "pos": "verb",
        "then": "dummy-reset-headers",  # Reset column inheritance
        "else": "",
    },
    "ben": {
        "lang": "Turkish",
        "pos": ["verb", "adj"],
        "if": "first-person singular",
        "then": "first-person singular",
    },
    "sen": {
        "lang": ["Crimean Tatar", "Turkish", "Turkmen"],
        "pos": "verb",
        # ~ "if": "second-person singular",
        "then": "second-person singular",
    },
    "o": {
        "lang": ["Azerbaijani", "Crimean Tatar", "Fula", "Igbo", "Turkish",
                 "Welsh", "Zazaki"],
        "pos": "verb",
        "if": "third-person singular",
        "then": "third-person singular",
        "else": {
            "lang": "Kikuyu",
            "pos": "verb",
            "if": "third-person plural",
            "then": "third-person plural",
            "else": {
               "lang": "Pnar",
               "pos": "verb",
               "if": "first-person singular",
               "then": "first-person singular",
               "else": {
                   "lang": "Yoruba",
                   "pos": "verb",
                   "if": "second-person third-person singular",
                   "then": "second-person third-person singular",
               },
            },
        },
    },
    "biz": {
        "lang": ["Azerbaijani", "Crimean Tatar", "Turkish","Turkmen"],
        "pos": "verb",
        "if": "first-person plural",
        "then": "first-person plural",
    },
    "siz": {
        "lang": ["Azerbaijani", "Crimean Tatar", "Turkish", "Turkmen"],
        "pos": "verb",
        "if": "second-person plural",
        "then": "second-person plural",
    },
    "onlar": {
        "lang": ["Azerbaijani", "Turkish"],
        "pos": "verb",
        "if": "third-person plural",
        "then": "third-person plural",
    },
    "vossìa": {
        "lang": "Sicilian",
        "if": "third-person singular",
        "then": ""},

    "deo eo": {
        "lang": "Sardinian",
        "if": "first-person singular",
        "then": ""},
    "tue": {
        "lang": "Sardinian",
        "if": "second-person singular",
        "then": ""},
    "issu/issa/isse": {
        "lang": "Sardinian",
        "if": "third-person singular",
        "then": ""},
    "nois": {
        "lang": "Sardinian",
        "if": "first-person plural",
        "then": ""},
    "bois": {
        "lang": "Sardinian",
        "if": "second-person plural",
        "then": ""},
    "issos/issas": {
        "lang": "Sardinian",
        "if": "third-person plural",
        "then": ""},
    "chi deo chi eo": {
        "lang": "Sardinian",
        "if": "first-person singular",
        "then": ""},
    "chi tue": {
        "lang": "Sardinian",
        "if": "second-person singular",
        "then": ""},
    "chi issu/issa/isse": {
        "lang": "Sardinian",
        "if": "third-person singular",
        "then": ""},
    "chi nois": {
        "lang": "Sardinian",
        "if": "first-person plural",
        "then": ""},
    "chi bois": {
        "lang": "Sardinian",
        "if": "second-person plural",
        "then": ""},
    "chi issos/issas": {
        "lang": "Sardinian",
        "if": "third-person plural",
        "then": ""},
    "dego deo": {
        "lang": "Sardinian",
        "if": "first-person singular",
        "then": ""},
    "issu/issa": {
        "lang": "Sardinian",
        "if": "third-person singular",
        "then": ""},
    "chi dego chi deo": {
        "lang": "Sardinian",
        "if": "first-person singular",
        "then": ""},
    "chi issu/issa": {
        "lang": "Sardinian",
        "if": "third-person singular",
        "then": ""},

    "ieu": {
        "lang": "Occitan",
        "if": "first-person singular",
        "then": ""},
    "el": {
        "lang": "Occitan",
        "if": "third-person singular",
        "then": ""},
    "nosautres": {
        "lang": "Occitan",
        "if": "first-person plural",
        "then": ""},
    "vosautres": {
        "lang": "Occitan",
        "if": "second-person plural",
        "then": ""},
    "eles": {
        "lang": "Occitan",
        "if": "third-person plural",
        "then": ""},
    "que ieu": {
        "lang": "Occitan",
        "if": "first-person singular",
        "then": ""},
    "que el": {
        "lang": "Occitan",
        "if": "third-person singular",
        "then": ""},
    "que nosautres": {
        "lang": "Occitan",
        "if": "first-person plural",
        "then": ""},
    "que vosautres": {
        "lang": "Occitan",
        "if": "second-person plural",
        "then": ""},
    "que eles": {
        "lang": "Occitan",
        "if": "third-person plural",
        "then": ""},

    "аз": {
        "lang": "Bulgarian",
        "if": "first-person singular",
        "then": ""},
    "ти": {
        "lang": ["Bulgarian", "Serbo-Croatian"],
        "if": "second-person singular",
        "then": ""},
    "той/тя/то": {
        "lang": "Bulgarian",
        "if": "third-person singular",
        "then": ""},
    "ние": {
        "lang": "Bulgarian",
        "if": "first-person plural",
        "then": ""},
    "вие": {
        "lang": "Bulgarian",
        "if": "second-person plural",
        "then": ""},
    "те": {
        "lang": "Bulgarian",
        "if": "third-person plural",
        "then": ""},

    "viņš, viņa": {
        "lang": "Latvian",
        "if": "third-person singular",
        "then": ""},
    "viņi, viņas": {
        "lang": "Latvian",
        "if": "third-person plural",
        "then": ""},

    "el / ela / Vde.": {
        "lang": "Galician",
        # ~ "if": "singular third-person",
        "then": "third-person singular",
        },
    "vós": {
        "lang": "Galician",
        # ~ "if": "plural second-person",
        "then": "second-person plural",
        },
    "eles / elas / Vdes.": {
        "lang": "Galician",
        # ~ "if": "plural third-person",
        "then": "third-person plural",
        },
    "Vde.": {
        "lang": "Galician",
        # ~ "if": "singular third-person",
        "then": "third-person singular formal"
        },
    "Vdes.": {
        "lang": "Galician",
        # ~ "if": "plural third-person",
        "then": "third-person plural formal"},

    "ⲛ̄ⲧⲟⲕ": {
        "lang": "Coptic",
        "if": "second-person singular masculine",
        "then": ""},
    "ⲛ̄ⲧⲟ": {
        "lang": "Coptic",
        "if": "second-person singular feminine",
        "then": ""},
    "ⲛ̄ⲧⲟϥ": {
    "lang": "Coptic",
        "if": "third-person singular masculine",
        "then": ""},
    "ⲛ̄ⲧⲟⲥ": {
        "lang": "Coptic",
        "if": "third-person singular feminine",
        "then": ""},
    "ⲛ̄ⲧⲱⲧⲛ̄": {
        "lang": "Coptic",
        "if": "second-person plural",
        "then": ""},
    "ⲛ̄ⲧⲟⲟⲩ": {
        "lang": "Coptic",
        "if": "third-person plural",
        "then": ""},
    "ⲛ̀ⲑⲟⲕ": {
        "lang": "Coptic",
        "if": "second-person singular masculine",
        "then": ""},
    "ⲛ̀ⲑⲟ": {
        "lang": "Coptic",
        "if": "second-person singular feminine",
        "then": ""},
    "ⲛ̀ⲑⲟϥ": {
        "lang": "Coptic",
        "if": "third-person singular masculine",
        "then": ""},
    "ⲛ̀ⲑⲟⲥ": {
        "lang": "Coptic",
        "if": "third-person singular feminine",
        "then": ""},
    "ⲛ̀ⲑⲱⲧⲉⲛ": {
        "lang": "Coptic",
        "if": "second-person plural",
        "then": ""},
    "ⲛ̀ⲑⲱⲟⲩ": {
        "lang": "Coptic",
        "if": "third-person plural",
        "then": ""},
    "ñuqa": {
        "lang": "Quechua",
        "if": "first-person singular",
        "then": ""},
    "qam": {
        "lang": "Quechua",
        "if": "second-person singular",
        "then": ""},
    "pay": {
        "lang": "Quechua",
        "if": "third-person singular",
        "then": ""},
    "ñuqanchik": {
        "lang": "Quechua",
        "if": "first-person plural inclusive",
        "then": ""},
    "ñuqayku": {
        "lang": "Quechua",
        "if": "first-person plural exclusive",
        "then": ""},
    "qamkuna": {
        "lang": "Quechua",
        "if": "second-person plural",
        "then": ""},
    "paykuna": {
        "lang": "Quechua",
        "if": "third-person plural",
        "then": ""},

    "unë": {
        "lang": "Albanian",
        "then": "first-person singular",
        },
    "ai/ajo": {
        "lang": "Albanian",
        "then": "third-person singular",
        },
    "ne": {
        "lang": "Albanian",
        "then": "first-person plural",
        "else": {
            "lang": "Livonian",
            "then": "third-person plural",
            },
        },
    "ju": {
        "lang": "Albanian",
        "then": "second-person plural",
        },
    "ata/ato": {
        "lang": "Albanian",
        "then": "third-person plural",
        },

    "մենք": {
        "lang": "Armenian",
        "if": "first-person plural",
        "then": ""},
    "նրանք": {
        "lang": "Armenian",
        "if": "third-person plural",
        "then": ""},

    "verbal nouns": "noun-from-verb",
    "supine": "supine",
    "past historic": "past historic",
    "passato remoto": "past historic",
    "future perfect": "future perfect",
    "impersonal": "impersonal",
    "verbal noun": "noun-from-verb",
    "auxiliary verb": "auxiliary",
    "active adjectival participle": "active adjectival participle",
    "contemporary adverbial participle": "contemporary adjectival participle",
    "passive adjectival participle": "passive adjectival participle",
    "Instrumental": "instrumental",
    "exessive": "exessive",
    "indef.": "indefinite",  # XXX see -heit, may need special handling
    "def.": "definite",
    "noun": "noun",  # XXX see ['-heit', '-schaft', '-tum']
    "absolutive": "absolutive",
    "definite accusative": "definite accusative",
    "definite genitive": "definite genitive",
    "possessive": "possessive",
    "Possessive": "possessive",
    "2nd person formal": "second-person formal",
    "3rd person masculine": "third-person masculine",
    "3rd person feminine": "third-person feminine",
    "3rd person neuter": "third-person neuter",
    "mənim (“my”)": "first-person singular possessive",
    "sənin (“your”)": "second-person singular possessive",
    "onun (“his/her/its”)": "third-person singular possessive",
    "bizim (“our”)": "first-person plural possessive",
    "sizin (“your”)": "second-person plural possessive",
    "onların (“their”)": "third-person plural possessive",
    "mən (“I am”)": "first-person predicative",
    "sən (“you are”)": "second-person predicative",
    "o (“he/she is”)": "third-person predicative",
    "predicative": "predicative",
    "subjective": "subjective",
    "preterite": "preterite",
    "strong/subject": "strong subjective",
    "weak (direct object)": "weak objective direct-object",
    "weak (indirect object)": "weak objective indirect-object",
    "proclitic": "proclitic",
    "Proclitic": "proclitic",
    "enclitic": "enclitic",
    "Enclitic": "enclitic",
    "1st person majestic": "first-person majestic formal",
    "2nd person very formal": "second-person formal",
    "3rd person reflexive": "third-person reflexive",
    "ablative/genitive": "ablative genitive",
    "Masculine / Feminine": "masculine feminine",
    "Imperative": "imperative",
    "imperfect (ra)": "imperfect",
    "imperfect (se)": "imperfect imperfect-se",
    "affirmative": {
        "if": "imperative",
        "then": "positive",
        "else": "affirmative",
    },
    "Affirmative": {
        "if": "imperative",
        "then": "positive",
        "else": "affirmative",
    },
    "Affirmative (+)": {
        "if": "imperative",
        "then": "positive",
        "else": "affirmative",
    },
    "participle": "participle",
    "Bare forms (no plural for this noun):": "no-plural",
    "old dative": "dative archaic",  # XXX archaic or dated?
    "Bare forms (no plural of this noun)": "no-plural",
    "Conditional": "conditional",
    "Inflection": "",
    "Definite accusative": "definite accusative",
    "present perfect": "present perfect",
    "optative": "optative",
    "positive degree": "positive",
    "comparative degree": "comparative",
    "superlative degree": "superlative",
    "prolative": "prolative",
    "comparative": {
        "lang": ["Chechen","Mari", "Nivkh",],
        "pos": "noun",
        "then": "comparative-case",
        "else": "comparative",
    },
    "causative": "causative",
    "Indicative": "indicative",
    "Class": "",
    "11": "class-11",
    "14": "class-14",
    "15": "class-15",
    "–": {
        "lang": "Nepalese",
        "then": "negative",
        "else": "dummy-ignore-skipped"},
    "m": "masculine",
    "f": "feminine",
    "compound": "multiword-construction",
    "reflexive": "reflexive",
    "Reflexive": "reflexive",
    "unstr.": "unstressed",
    "First-person singular": "first-person singular",
    "Second-person singular": "second-person singular",
    "Third-person singular": "third-person singular",
    "First-person plural": "first-person plural",
    "Second-person plural": "second-person plural",
    "Third-person plural": "third-person plural",
    "First-person (eu)": "first-person singular",
    "Second-person (tu)": "second-person singular",
    "Third-person (ele / ela / você)": "third-person singular",
    "First-person (nós)": "first-person plural",
    "Second-person (vós)": "second-person plural",
    "Third-person (eles / elas / vocês)": "third-person plural",
    "Impersonal": "impersonal",
    "Personal": "personal",
    "Gerund": "gerund",
    "Preterite": "preterite",
    "Pluperfect": "pluperfect",
    "Negative (-)": "negative",
    "Negative (não)": "negative",
    "definite (subject form)": "definite subjective",
    "definite (object form)": "definite objective",
    "extended (vocative form)": "extended vocative",
    "number": "",
    "dual": "dual",
    "middle/ passive": "middle passive",
    "Active": "active",
    "Passive": "passive",
    "first person": "first-person",
    "second person": "second-person",
    "third person": "third-person",
    "first person singular": "first-person singular",
    "second person singular": "second-person singular",
    "third person singular": "third-person singular",
    "1ˢᵗ person": "first-person",
    "2ⁿᵈ person": "second-person",
    "3ʳᵈ person": "third-person",
    "middle/passive": "middle passive",
    "present participle or gerund": "present participle gerund",
    "(simple tenses)": "",
    "(compound tenses)": "multiword-construction",
    "past anterior": "past anterior",
    "conditional perfect": "conditional perfect",
    "middle": "middle",
    "Indefinite": "indefinite",
    "Definite": "definite",
    "1st-person singular": "first-person singular",
    "2nd-person singular": "second-person singular",
    "3rd-person singular": "third-person singular",
    "1st-person plural": "first-person plural",
    "2nd-person plural": "second-person plural",
    "3rd-person plural": "third-person plural",
    "derivations": "",
    "subject": "subjective",
    "object": "objective",
    "full": "stressed",
    "pred.": "predicative",
    "2nd person archaic or regiolectal": "second-person archaic dialectal",
    "m-s1": "",  # Icelandic ['-lingur', '-hlaðningur']
    "Tense \ Voice": "",
    "Strong declension": "strong",
    "gender": "",
    "Weak declension": "weak",
    "Bare forms (no plural form of this noun)": "indefinite no-plural",
    "Positive declarative": "",
    "imperfective participle": "imperfective participle",
    "personal": "personal",
    "future participle": "future participle",
    "personal participle": "personal participle",
    "way of doing": "adverbial",
    "aorist": "aorist",
    "imperfective": "imperfective",
    "perfective": "perfective",
    "inferential": "inferential",
    "progressive": "progressive",
    "necessitative": "necessitative",
    "Positive interrogative": "interrogative",
    "Negative declarative": "negative",
    "Negative interrogative": "negative interrogative",
    "m6": "",  # Faroese ['-gustur', '-lingur']
    "indefinite forms, (trajta të pashquara)": "indefinite",
    "definite forms, (trajta të shquara)": "definite",
    "singular (numri njëjës)": "singular",
    "plural (numri shumës)": "plural",
    "nominative (emërore)": "nominative",
    "accusative (kallëzore)": "accusative",
    "genitive (gjinore), (i/e/të/së)": "genitive",
    "dative (dhanore)": "dative",
    "ablative (rrjedhore)": "ablative",
    "notes": "",
    "m-w1": "",  # Icelandic ['-isti', '-ismi']
    "masculine animate": "masculine animate",
    "Masculine singular": "masculine singular",
    "Neuter singular": "neuter singular",
    "n-s": "",  # Icelandic ['-leysi']
    "singular (vienskaitlis)": "singular",
    "nominative (nominatīvs)": "nominative",
    "accusative (akuzatīvs)": "accusative",
    "genitive (ģenitīvs)": "genitive",
    "dative (datīvs)": "dative",
    "instrumental (instrumentālis)": "instrumental",
    "locative (lokatīvs)": "locative",
    "vocative (vokatīvs)": "vocative",
    "past perfect": "past perfect",
    "plural only": "plural-only",
    "m pers": "masculine personal",
    "other": "",
    "f-w1": "",  # Icelandic ['-ína']
    "Supine": "supine",
    "Imper. plural": "imperative plural",
    "Ind. plural": "indicative plural",
    "-skur a24": "",  # Faroese ['-skur']
    "Singular (eintal)": "singular",
    "Nominative (hvørfall)": "nominative",
    "Accusative (hvønnfall)": "accusative",
    "Dative (hvørjumfall)": "dative",
    "Genitive (hvørsfall)": "genitive",
    "Plural (fleirtal)": "plural",
    "Original form": "",  # XXX Latin ['-bo']
    "Derived form": "",  # XXX Latin ['-bo']
    "Present active indicative (third conjugation)":
    "present active indicative conjugation-3",
    "Present active subjunctive": "present active subjunctive",
    "Present passive indicative": "present passive indicative",
    "Present passive subjunctive": "present passive subjunctive",
    "f1": "",  # Faroese ['-isma']
    "anterior adverbial participle": "anterior adverbial participle",
    "Plural only": "plural-only",
    "m1": "",  # Faroese ['-ari']
    "f2": "",  # Faroese ['-d']
    "m. plural": "masculine plural",
    "n./f. plural": "neuter feminine plural",
    "1ˢᵗ person inclusive": "first-person inclusive",
    "1ˢᵗ person exclusive": "first-person exclusive",
    "hortative": "hortative",
    "reciprocal": "reciprocal",
    "Reciprocal": "reciprocal",
    "Preesens": "present",
    "coactive": "coactive",
    "objective": "objective",
    "subsuntive": "subsuntive",
    "relative": "relative",
    "autonomous": "autonomous",
    "past habitual": "past habitual",
    "Habituals": "habitual",
    "n gender": "neuter",
    "Feminine singular": "feminine singular",
    "Root word": "root",
    "Aspect": "",
    "Complete": "completive",
    "Progressive": "progressive",
    "Contemplative": "contemplative",
    "Masculine o-stem": "masculine stem",
    "ergative": "ergative",
    "Ergative": "ergative",
    "prosecutive": "prosecutive",
    "equative": "equative",
    "Verbal forms": "",
    "Conditional I": "conditional conditional-i",
    "conditional I": "conditional conditional-i",
    "Conditional II": "conditional conditional-ii",
    "conditional II": "conditional conditional-ii",
    "Active past participle": "active past participle",
    "Objective": "objective",
    "Objective Genitive": "objective genitive",
    "often only in the singular": "often singular-only",
    "Common singular": "common-gender singular",
    "common(noun)": "common-gender",
    "neuter(noun)": "neuter",
    "masculine (person)": "masculine person",
    "feminine (person)": "feminine person",
    "Masculine plural": "masculine plural",
    "modern": "",
    "archaic / formal": "archaic formal",
    "All": "",
    "str.": "stressed",
    "1st person singular": "first-person singular",
    "2nd person singular (informal)": "second-person singular informal",
    "2nd person singular (familiar)": "second-person singular familiar",
    "2nd person singular (polite)": "second-person singular polite",
    "2nd person singular (formal)": "second-person singular formal",
    "3rd person singular": "third-person singular",
    "3rd person singular (m.)": "third-person singular masculine",
    "3rd person singular (f.)": "third-person singular feminine",
    "3rd person singular (n.)": "third-person singular neuter",
    "Present verbal adverb": "present adverbial",
    "Past verbal adverb": "past adverbial",
    "disused": "",
    "all genders": "",
    "number & gender": "",
    "strong declension (without article)": "strong without-article",
    "weak declension (with definite article)":
    "weak definite includes-article",
    "mixed declension (with indefinite article)":
    "mixed indefinite includes-article",
    "inanimate animate": "animate inanimate",
    "Informal": "informal",
    "modern / informal": "informal",
    "i": {"lang": ["German", "Cimbrian",],
          "then": "subjunctive subjunctive-i",
          "else": {
              "if": "subjunctive",
              "then": "subjunctive-i",
              "else": {
                "lang": ["Tagalog", "Assamese"],
                "then": "",
              },
          },
    },
    "ii": {"lang": ["German", "Cimbrian",],
           "then": "subjunctive subjunctive-ii",
           "else": {
               "if": "subjunctive",
               "then": "subjunctive-ii",
           },
    },
    "definite forms": "definite",
    "1ˢᵗ person possessive forms (my)": "possessive first-person",
    "2ⁿᵈ person possessive forms (your)": "possessive second-person",
    "oblique": "oblique",
    "direct": "direct",
    "Construct": "construct",
    "Negative": "negative",
    "auxiliary": "auxiliary",
    "Conjunctive": "conjunctive",
    "Perfective": "perfective",
    "Stem forms": "stem",
    "Continuative": "continuative",
    "Continuative (連用形)": "continuative",
    "Terminal (終止形)": "terminative",
    "Attributive (連体形)": "attributive",
    "Imperative (命令形)": "imperative",
    "Imperfective (未然形)": "imperfective",
    "Hypothetical (仮定形)": "hypothetical",
    "Terminal": "terminative",
    "Attributive": "attributive",
    "Volitional": "volitional",
    "Imperfective": "imperfective",
    "Hypothetical": "hypothetical",
    "Negative continuative": "negative continuative",
    "Formal": "formal",
    "Hypothetical conditional": "hypothetical conditional",
    "1st singular": "first-person singular",
    "2nd singular": "second-person singular",
    "3rd singular": "third-person singular",
    "1st plural": "first-person plural",
    "2nd plural": "second-person plural",
    "3rd plural": "third-person plural",
    "benefactive": "benefactive",
    "future in the past": "past-future",
    "Passive past participle": "passive past participle",
    "associative": "associative",
    "distributive": "distributive",
    "exclusive": "exclusive",
    "future i": "future future-i",
    "subjunctive i": "subjunctive subjunctive-i",
    "subjunctive ii": "subjunctive subjunctive-ii",
    "future ii": "future future-ii",
    "л-participles": "participle",
    "verbal adjective m.sg.": "masculine singular adjectival",
    "verbal adverb": "adverbial",
    "Compound tenses": "multiword-construction",
    "има-perfect": "има perfect",
    "има-pluperfect": "има pluperfect",
    "има-perfect reported": "има perfect reported",
    "има-future": "има future",
    "има-future in the past": "има future past",
    "future reported": "future reported",
    "има-future reported": "има future reported",
    "има-conditional": "има conditional",
    "uninflected": "uninflected",
    "inflected": "inflected",
    # XXX pending removal; the participle marking is in sense
    # "predicative/adverbial": {
    #     "lang": "Dutch",
    #     "pos": "verb",
    #     "then": ["participle predicative", "participle adverbial"],
    #     "else": "predicative adverbial",
    # },
    "predicative/adverbial": "predicative adverbial",
    "m./f. sing.": "masculine feminine singular",
    "n. sing.": "neuter singular",
    "masculine (vīriešu dzimte)": "masculine",
    "feminine (sieviešu dzimte)": "feminine",
    "plural (daudzskaitlis)": "plural",
    "archaic plural": "archaic plural",
    "Non-past": "non-past",
    "Interrogative": "interrogative",
    "Assertive": "assertive",
    "Cause/Reason": "causative",
    "Contrast": "contrastive",
    "Conjunction": "conjunctive",
    "Condition": "conditional",
    "Verbal nouns": "noun-from-verb",
    "Past-tense verbal nouns": "past noun-from-verb",
    "Determiners": "determiner",
    "simple perfect": "perfect",
    "Notes": {
        "lang": "Assamese",
        "then": "dummy-remove-this-cell",
        "else": "dummy-skip-this",
    },
    # ~ "Notes": "dummy-ignore-skipped",
    "postpositions taking a dative case": "postpositional with-dative",
    "postpositions taking a genitive case": "postpositional with-genitive",
    "postpositions taking an instrumental case":
    "postpositional with-instrumental",
    "postpositions taking an adverbial case": "postpositional with-adverb",
    "Motive": "motive-form",
    "zu-infinitive": "infinitive infinitive-zu",
    "active participle": "active participle",
    "active voice": "active",
    "Active voice ➤ — Imperfective aspect": "active imperfective",
    "Active voice ➤ — Imperfective aspect ➤": "active imperfective",
    "Active voice ➤": "active",
    "Passive voice ➤": "passive",
    "Active voice": "active",
    "Passive voice": "passive",
    "Imperfective aspect ➤": "imperfective",
    "Perfective aspect ➤": "perfective",
    "Imperfective aspect": "imperfective",
    "Perfective aspect": "perfective",
    "Perfect aspect ➤": "perfective",
    "Perfect aspect": "perfective",
    "Present perfect ➤": {
        "lang": "Greek",
        "then": "dummy-skip-this",  # e.g περπατάω/Greek
    },
    "Past perfect ➤": {
        "lang": "Greek",
        "then": "dummy-skip-this",  # e.g περπατάω/Greek
    },
    "Future perfect ➤": {
        "lang": "Greek",
        "then": "dummy-skip-this",  # e.g περπατάω/Greek
    },
    "Indicative mood ➤": "indicative",
    "Past tenses ➤": {
        "lang": "Greek",
        "then": "",  # tense column follows
    },
    "Non-past tenses ➤": "",
    "Dependent ➤": "dependent",
    "Dependent": "dependent",
    "dependent": "dependent",  # immee/Manx
    "Present participle➤": "present participle",
    "Perfect participle➤": "past participle",
    "Nonfinite form➤": {
        "lang": "Greek",
        "then": "infinitive-aorist",
    },
    "Subjunctive mood ➤": {
        "lang": "Greek",
        "then": "subjunctive dummy-tense",
        "else": "subjunctive",
    },
    "Imperative mood ➤": {
        "lang": "Greek",
        "then": "imperative dummy-tense",
        "else": "imperative",
    },
    "Imperative mood": {
        "lang": "Greek",
        "then": "imperative dummy-tense",
        "else": "imperative",
    },
    "Subjunctive mood": {
        "lang": "Greek",
        "then": "subjunctive dummy-tense",
        "else": "subjunctive",
    },
    "Present ➤": "present",
    "Imperfect ➤": "imperfect",
    "Simple past ➤": "past",
    "Future ➤": "future",
    "Future tenses ➤": "future",
    "Continuous ➤": "progressive",
    "Simple ➤": "",
    "Present participle ➤": "present participle",
    "Simple past": "past",
    "Habitual": "habitual",
    "passive participle": "passive participle",
    "passive voice": "passive",
    "singular (жекеше)": "singular",
    "plural (көпше)": "plural",
    "nominative (атау септік)": "nominative",
    "genitive (ілік септік)": "genitive",
    "dative (барыс септік)": "dative",
    "accusative (табыс септік)": "accusative",
    "locative (жатыс септік)": "locative",
    "ablative (шығыс септік)": "ablative",
    "instrumental (көмектес септік)": "instrumental",
    "compound tenses": "multiword-construction",
    "Sentence-final forms": "sentence-final",
    "Connective forms": "connective",
    "Noun and determiner forms": "",
    "Verbal Noun": "noun-from-verb",
    "count form": "count-form",
    "infinitive (nafnháttur)": "infinitive",
    "supine (sagnbót)": "supine",
    "present participle (lýsingarháttur nútíðar)": "present participle",
    "indicative (framsöguháttur)": "indicative",
    "subjunctive (viðtengingarháttur)": "subjunctive",
    "present (nútíð)": "present",
    "past (þátíð)": "past",
    "imperative (boðháttur)": "past",
    "Forms with appended personal pronoun": "pronoun-included",
    "Sentence-final forms with honorific": "sentence-final honorific",
    "Connective forms with honorific": "connective honorific",
    "Noun and determiner forms with honorific": "honorific",
    "Hortative": "hortative",
    "singular (uncountable)": "singular uncountable",
    "absolute": "absolute",
    "Positive absolute": "positive absolute",
    "Negative absolute": "negative absolute",
    "singular (singulare tantum)": "singular singular-only",
    "Nom. sg.": "nominative singular",
    "Gen. sg.": "genitive singular",
    "nom. sing.": "nominative singular",
    "gen. sing.": "genitive singular",
    "Non-finite forms": "dummy-mood",
    "1st singular я": "first-person singular",
    "second-person": "second-person",
    "4th person": "fourth-person",
    "invertive": "invertive",
    "Simple finite forms": "finite-form",
    "Positive form": "positive",
    "Complex finite forms": "dummy-reset-headers",  # Reset
    "2nd singular ти": "second-person singular",
    "3rd singular він / вона / воно": "third-person singular",
    "1st plural ми": "first-person plural",
    "2nd plural ви": "second-person plural",
    "3rd plural вони": "third-person plural",
    "first-person": "first-person",
    "plural ми / ви / вони": "plural",
    "masculine я / ти / він": "masculine",
    "feminine я / ти / вона": "feminine",
    "neuter воно": "neuter",
    "vocative form": "vocative",
    "Uncountable": "uncountable",
    "definite unspecified": "definite unspecified",
    "definite proximal": "definite proximal",
    "definite distal": "definite distal",
    "informal": "informal",
    "f gender": "feminine",
    "simple tenses": "",
    "present indicative": "present indicative",
    "ñuqap (my)": "first-person singular",
    "qampa (your)": "second-person singular",
    "paypa (his/her/its)": "third-person singular",
    "ñuqanchikpa (our(incl))": "first-person plural inclusive",
    "ñuqaykup (our(excl))": "first-person plural exclusive",
    "qamkunap (your(pl))": "second-person plural",
    "paykunap (their)": "third-person plural",
    "tense": "",
    "m.": "masculine",
    "f.": "feminine",
    "Stem": "stem",
    "aorist stem": "stem",
    "pos.": "positive",
    "neg.": "negative",
    "future perfect in the past": "future perfect past",
    "renarrative": "renarrative",
    "present and imperfect": ["present", "imperfect"],
    "future and future in the past": ["future", "future past"],
    "present and past perfect": ["present", "past perfect"],
    "future perfect and future perfect in the past":
    ["future perfect", "future past perfect"],
    "dubitative": "dubitative",
    "conclusive": "conclusive",
    "f-s2": "",  # Icelandic ['bölvun', 'létteind', 'dvöl']
    "Indicative mood": "indicative",
    "2,3 sg, 1,2,3 pl": {
        "lang": "Greek",
        "then": "dummy-skip-this",  # used in περπατάω/Greek
    },
    "Present perfect": "present perfect",
    "Past perfect": "past perfect",
    "Future perfect": "future perfect",
    "Inflected colloquial forms": "colloquial",
    "adjective active participle": "adjective active participle",
    "adverbial active participle": "adverbial active participle",
    "nominal active participle": "noun-from-verb active participle",
    "plural unknown": "plural unknown",
    "Contrafactual": "counterfactual",
    "finite forms": "finite-form",
    "Indefinite forms": "indefinite",
    "Definite forms": "definite",
    "numeral": "numeral",
    "non-numeral (plural)": "non-numeral plural",
    "Strong (indefinite) inflection": "strong indefinite",
    "Weak (definite) inflection": "weak definite",
    "directive": "directive",
    "destinative": "destinative",
    "Regular": "",
    "PERFECTIVE": "perfective",
    "Present passive": "present passive",
    "1st dual": "first-person dual",
    "2nd dual": "second-person dual",
    "Undeclined": "",
    "Oblique Infinitive": "oblique infinitive",
    "Prospective Agentive": "prospective agentive",
    "prospective": "prospective",
    "non-prospective": "non-prospective",
    "Adjectival": "adjectival",
    "մեք": "first-person plural",
    "նոքա": "third-person plural",
    "imperatives": "imperative",
    "cohortative": "cohortative",
    "prohibitive": "prohibitive",
    "A-stem": "",
    "continuous": "continuative",
    "f-s1": "",  # Icelandic ['blæðing', 'Sigríður', 'líkamsræktarstöð']
    "+": "positive",
    "Unknown": "unknown",
    "Simple": "",
    "simple": {
        "lang": ["English"],
        "then": "dummy-mood",
        "else": "",
    },
    "formal": "formal",
    "INDICATIVE (īstenības izteiksme)": "indicative",
    "IMPERATIVE (pavēles izteiksme)": "imperative",
    "Present (tagadne)": "present",
    "Past (pagātne)": "past",
    "Future (nākotne)": "future",
    "1st pers. sg.": "first-person singular",
    "2nd pers. sg.": "second-person singular",
    "3rd pers. sg.": "third-person singular",
    "1st pers. pl.": "first-person plural",
    "2nd pers. pl.": "second-person plural",
    "3rd pers. pl.": "third-person plural",
    "RENARRATIVE (atstāstījuma izteiksme)": "renarrative",
    "Present Active 1 (Adj.)":
    "participle participle-1 present active adjectival",
    "Present Active 2 (Adv.)":
    "participle participle-2 present active adverbial",
    "Present Active 3 (Adv.)":
    "participle participle-3 present active adverbial",
    "Present Active 4 (Obj.)":
    "participle participle-4 present active",
    "CONDITIONAL (vēlējuma izteiksme)": "conditional",
    "Past Active": {
        "if": "participle",
        "then": "participle past active",  # saprast/Latvian/Verb
        "else": "past active",
    },
    "Present Passive": {
        "if": "participle",
        "then": "participle present passive",  # saprast/Latvian/Verb
        "else": "present passive",
    },
    "Past Passive": {
        "if": "participle",
        "then": "participle past passive",
        "else": "past passive",
    },
    "DEBITIVE (vajadzības izteiksme)": "debitive",
    "NOMINAL FORMS": "dummy-mood",
    "Infinitive (nenoteiksme)": "infinitive",
    "Conjunctive 1": "conjunctive conjunctive-1",
    "Conjunctive 2": "conjunctive conjunctive-2",
    "Nonfinite form": "dummy-mood",
    "Perfect participle": "perfect participle",
    "perfect progressive": "perfect progressive",
    "Recently Completive": "completive past past-recent",
    "subject non-past participle": "subjective non-past participle",
    "subject past participle": "subjective past participle",
    "subject future definite participle":
    "subjective future definite participle",
    "non-subject participle": "non-subject participle",
    "general temporal participle": "general temporal participle",
    "participle of intensification": "intensifier participle",
    "specific temporal participle": "specific temporal participle",
    "modal participle": "modal participle",
    "perfect 1": "perfect perfect-i",
    "perfect 2": "perfect perfect-ii",
    "future-in-the-past": "past-future",
    "obligational": "obligative",
    "evidential": "evidential",
    "converb": "converb",
    "negative potential": "negative potential",
    "adjective passive participle": "adjectival passive participle",
    "adverbial passive participle": "adverbial passive participle",
    "nominal passive participle": "noun-from-verb passive participle",
    "IMPERFECTIVE": "imperfective",
    "Non-Aspectual": "non-aspectual",
    "PERF": "perfect",
    "FUT": "future",
    "PST": "past",
    "PRS": "present",
    "Presumptive": "presumptive",
    "PRS PST": "present past",
    "PRS PST FUT": "present past future",
    "agentive": "agentive",
    "FUTURE": "future",
    "Jussive": "jussive",
    "Root": {
        "lang": "Limburgish",  # beer/Limburgish
        "then": "",
        "else": "root",
    },
    "Involuntary": "involuntary",  # Verb form, e.g., khitan/Indonesian
    "part participle": "past participle",
    "direct present": "direct present",
    "indirect present": "indirect present",
    "singular/plural": "singular plural",
    "personal infinitive": "personal infinitive",
    "Class 1": "class-1",
    "Class 2": "class-2",
    "Class 3": "class-3",
    "Class 4": "class-4",
    "Class 5": "class-5",
    "Class 6": "class-6",
    "Class 7": "class-7",
    "Class 8": "class-8",
    "Class 9": "class-9",
    "Class 10": "class-10",
    "Class 11": "class-11",
    "Class 12": "class-12",
    "Class 13": "class-13",
    "Class 14": "class-14",
    "Class 15": "class-15",
    "Class 16": "class-16",
    "Class 17": "class-17",
    "Class 18": "class-18",
    "Class 2 strong": "class-2 strong",
    "Class 4 strong": "class-4 strong",
    "Class 6 strong": "class-6 strong",
    "Class 7 strong": "class-7 strong",
    "imperfect subjunctive": "imperfect subjunctive",
    "dative-locative": "dative locative",
    "directional": "directional",
    "possessive pronoun": "possessive pronoun",
    "possessive determiner": "possessive determiner",
    "genderless, nonspecific (formal)": "gender-neutral formal",
    "genderless": "gender-neutral",
    "standard formal": "formal",
    "archaic informal": "archaic informal",
    "Gen/Dat": "genitive dative",
    "Nom/Acc": "nominative accusative",
    "uncountable": "uncountable",
    "gender f": "feminine",
    "Present subjunctive": "present subjunctive",
    "Future progressive presumptive": "future progressive presumptive",
    "Past progressive": "past progressive",
    "Negative present progressive": "negative present progressive",
    "1.": "first-person",
    "2.": "second-person",
    "3. m": "third-person masculine",
    "3. f": "third-person feminine",
    "3. n": "third-person neuter",
    "1st person plural inclusive": "first-person plural inclusive",
    "1st person plural exclusive": "first-person plural exclusive",
    "3rd person plural participle": "third-person plural participle",
    "Indefinite subject (passive)": "passive",
    "3rd person pl": "third-person plural",
    "2nd person pl": "second-person plural",
    "3rd person dual": "third-person dual",
    "2nd person dual": "second-person dual",
    "1st person dual": "first-person dual",
    "2nd person sg": "second-person singular",
    "3rd-person sg": "third-person singular",
    "perfective aorist": "perfective aorist",
    "f-w2": "",  # málfræði/Icelandic
    "f-s3": "",  # kvaðratrót/Icelandic
    "m-s2": "",
    "m-s3": "",
    "3rd person plural (3p) Wiinawaa": "third-person plural",
    "2nd-person plural (2p) Giinawaa": "second-person plural",
    "1st person plural inclusive (21) Giinawind":
    "first-person plural inclusive",
    "1st person plural exclusive (1p) Niinawind":
    "first-person plural exclusive",
    "Indefinite (X)": "indefinite",
    "Obviative (3')": "third-person obviative",
    "1st person (1s) Niin": "first-person singular",
    "2nd person (2s) Giin": "second-person singular",
    "3rd person (3s) Wiin": "third-person singular",
    "1st sg": "first-person singular",
    "2nd sg": "second-person singular",
    "3rd sg": "third-person singular",
    "1st pl": "first-person plural",
    "2nd pl": "second-person plural",
    "3rd pl": "third-person plural",
    "2nd sg neuter": "second-person singular neuter",
    "2nd sg for": "second-person singular formal",
    "Mood / Tense": "",
    "hypothetic": "hypothetical",
    "Indefinite feminine and masculine gender":
    "indefinite feminine masculine",
    "contrafactual": "counterfactual",
    "presumptive": "presumptive",
    "habitual": "habitual",
    "2ⁿᵈ person*": "second-person",
    "мынем (“my”)": "first-person singular possessive",
    "Primary stem": "stem stem-primary",
    "Secondary stem": "stem stem-secondary",
    "intentive": "intentive",
    "serial": "habitual",
    "characteristic": "adverbial",  # patjaṉi/Pitjantjatjara
    "imperative continuous": "imperative continuative",
    "precursive": "precursive",
    "limitative": "limitative",
    "circumstantial focalising": "circumstantial focalising",
    "focalising precursive": "focalising precursive",
    "focalising": "focalising",
    "expectative": "expectative",
    "nominative (ప్రథమా విభక్తి)": "nominative",
    "genitive": "genitive",
    "locative": "locative",
    "1st मैं": "first-person",
    "basic": "",
    "Preterite I": "preterite preterite-i",
    "Preterite II": "preterite preterite-ii",
    "Pluperfect I": "pluperfect pluperfect-i",
    "Pluperfect II": "pluperfect pluperfect-ii",
    "Durative preterite": "durative preterite",
    "Frequentative preterite": "frequentative preterite",
    "Auxiliary": "auxiliary",
    "Nominative Accusative": "nominative accusative",
    "obviative singular (0')": "obviative singular",
    "singular (0')": "singular",
    "Indefinite masculine gender": "indefinite masculine",
    "Definite masculine gender": "definite masculine",
    "SUBJECT": "subjective",
    "Singular OBJECT": {
        "lang": "Pashto",
        "then": "object-singular object-concord",
        "else": "singular objective",
    },
    "Plural OBJECT": {
        "lang": "Pashto",
        "then": "object-plural object-concord",
        "else": "plural objective",
    },
    "indefinite forms": "indefinite",
    "2ⁿᵈ person singular": "second-person singular",
    "2ⁿᵈ person plural": "second-person plural",
    "3ʳᵈ person [sing. and plural]": "third-person singular plural",
    "Actor": {"lang": "Tagalog", "then": "trigger-actor"},
    "Object": {"lang": "Tagalog", "then": "trigger-object"},
    "Locative": {"lang": "Tagalog", "then": "trigger-locative",
                 "else": "locative"},
    "Instrument": {"lang": "Tagalog", "then": "trigger-instrument",
                   "else": "instrumental"},
    "Causative": {"lang": "Tagalog", "then": "trigger-causative",
                  "else": "causative"},
    "Referential": {"lang": "Tagalog", "then": "trigger-referential"},
    "1ˢᵗ person m": "first-person masculine",
    "1ˢᵗ person f": "first-person feminine",
    "2ⁿᵈ person m": "second-person masculine",
    "2ⁿᵈ person f": "second-person feminine",
    "Tense/Mood": "",
    "masculine object": "masculine objective",
    "feminine object": "feminine objective",
    "neuter object": "neuter objective",
    "singular subject": "singular subjective",
    "plural subject": "plural subjective",
    "Allative I": "allative allative-i",
    "Allative II": "allative allative-ii",
    "conditional active": "conditional active",
    "subjunctive active": "subjunctive active",
    "Concessive": "concessive",
    "Preparative": "preparative",
    "Durative": "durative",
    "Subordinative (Past gerund)": "past gerund",
    "Coordinative (Infinitive)": "infinitive",
    "Converbs": "converb",
    "Optative": "optative",
    "Polite": "polite",
    "Strong": "emphatic",
    "Normal": "",
    "Present-future": "future",
    "habitual/conditional past": "habitual conditional past",
    "simple past": "past",
    "present continuous": "present continuative",
    "simple present": "present",
    "polite": "polite",
    "familiar": "familiar",
    "very familiar": "familiar",
    "PAST TENSE": "past",
    "3rd person m": "third-person masculine",
    "3rd person f": "third-person feminine",
    "3rd m": "third-person masculine",
    "3rd m.": "third-person masculine",  # hug/Manx
    "gender m": "masculine",
    "dative form": "dative",
    "continuative": "continuative",
    "circumposition": "circumposition",
    "singular and plural": "singular plural",
    "accusative indefinite-dative": "accusative indefinite dative",
    "Literary forms": "literary",
    "Case \\ Number": "",
    "masc./fem.": "masculine feminine",
    "gender n": "neuter",
    "m or n": "masculine neuter",
    "actor I": "actor-i",
    "Sociative": "sociative",
    "Present negative": "present negative",
    "Possessive determiner": "possessive determiner",
    "Proximal": "proximal",
    "ergative-instrumental": "ergative instrumental",
    "Plural/Distributive": "plural distributive",
    "stressed": "stressed",
    "vir pl": "virile plural",
    "poss. adj.": "possessive adjective",
    "Gender": "",
    "All numbers": "",
    "m obl, pl": "masculine oblique plural",
    "m & n": "masculine neuter",
    "dative-lative-locative": "dative lative locative",
    "aspect": "",
    "Third person m": "third-person masculine",
    "Dual virile": "dual virile",
    "Accusative /Genitive": "accusative genitive",
    "1st c. sg. (me)": "first-person singular",
    "Future tense": "future",
    "👤 singular": "singular",
    "👥 dual": "dual",
    "👤👥👥 plural": "plural",
    "Feminine i/ō-stem": "feminine stem",
    "past indicative": "past indicative",
    "Irregular with past tense": "irregular",
    "Abs.": "absolute",
    "Conj.": "conjunct",
    "Rel.": "relative",
    "Positive relative": "positive relative",
    "Negative relative": "negative relative",
    "intentional": "intentive",
    "oblig": "obligative",
    "indef": "indefinite",
    "def": "definite",
    "perf": "perfective",
    "cont": "continuative",
    "comp": "completive",
    "simpl": "",
    "nominal non-finites": "noun-from-verb dummy-mood",
    "comitative": "comitative",
    "abessive": "abessive",
    "essive": "essive",
    "terminative": "terminative",
    "translative": "translative",
    "inessive": "inessive",
    "partitive": "partitive",
    "nominative": "nominative",
    "singulare tantum": "singular-only",
    "Absolutive": "absolutive",
    "Infinitival": "infinitive",
    "negatival complement": "negative",
    "complementary infinitive": "infinitive",  # XXX what add gp/Egyptian
    "stative stem": "stative",
    "periphrastic imperfective": "imperfective",
    "periphrastic prospective": "prospective",
    "‘pseudoverbal’ forms": "",
    "suffix conjugation": "",
    "contingent": "contingent",
    "obligative": "obligative",
    "potentialis": "potential",
    "normal": "",
    "1ˢᵗ Perfect": "perfect-i",
    "2ⁿᵈ Perfect": "perfect-ii",
    "m. sing.": "masculine singular",
    "f. sing.": "feminine singular",
    "c. sing.": "common-gender singular",
    "pl.": "plural",
    "high-resp.": "formal deferential",
    "Conjugation type": "conjugation-type",
    "Injunctive": "injunctive",
    "Habitual participle": "habitual participle",
    "Future conditional": "future conditional",
    "condizionale passato": "past conditional",  # ripromettersi/Italian
    "futuro anteriore": "future perfect",  # ripromettersi/Italian
    "passato prossimo": "perfect",  # ripromettersi/Italian
    "trapassato remoto": "preterite-perfect",  # ripromettersi/Italian
    "trapassato prossimo": "past perfect",  # ripromettersi/Italian
    "(♂)": "masculine",
    "Contingent": "contingent",
    "Reason": "reason",
    "Goal": "goal",
    "Agentive (emphatic)": "agentive emphatic",
    "Genitive infinitive": "genitive infinitive",
    "Conjugative": "conjugative",
    "Gerund Past participle Agentive": "gerund past participle agentive",
    "construct": "construct",
    "Form": "",
    "form": "",
    "Isolated forms": "",
    "isolated forms": "",  #a ܡܘܙܐ/Assyrian Neo-Aramaic
    "Possessed": "possessed-form",
    "Unpossessed": "unpossessed-form",
    "past imperfective": "past imperfective",
    "past perfective": "past perfective",
    "Conjunct": "conjunct",
    "dir m s": "direct masculine singular",
    "m p obl m s": ["masculine plural", "oblique masculine singular"],
    "f s": "feminine singular",
    "f p": "feminine plural",
    "gerunds": "gerund",
    "perfect subjunctive": "perfect subjunctive",
    "future subjunctive": "future subjunctive",
    "screeves": "",  # კვეთს/Georgian
    "second-person singular formal": "second-person singular formal",
    "second-person singular informal": "second-person singular informal",
    "first-person singular": "first-person singular",
    "possessive forms": "possessive",
    "Indirect": "indirect",
    "Direct": "direct",
    "Soft": "soft",
    "Hard": "hard",
    "Nasalization": "mutation-nasal",
    "soft": {
        "if": "mutation",
        "then": "mutation-soft",
        "else": {
            "lang": "Breton",
            "then": "mutation-soft",
            "else": "soft",
        },
    },
    "nasal": {
        "if": "mutation",
        "then": "mutation-nasal",
    },
    "aspirate": {
        "if": "mutation",
        "then": "mutation-aspirate",
        "else": {
            "lang": "Breton",
            "then": "mutation-aspirate",
        },
    },
    "mixed": {
        "if": "mutation",
        "then": "mutation-mixed",
        "else": "mixed",
    },
    "radical": {
        "if": "mutation",
        "then": "mutation-radical",
    },
    "Radical": {
        "if": "mutation",
        "then": "mutation-radical",
    },
    "with h-prothesis": {
        "if": "mutation",
        "then": "prothesis-h",
    },
    "with t-prothesis": {
        "if": "mutation",
        "then": "prothesis-t",
    },
    "Lenition": "lenition",
    "Eclipsis": "eclipsis",
    "+ object concord": "object-concord",
    "lative": "lative",
    "post./nom.": "postpositional",  # XXX what is nom. ?
    "Measurement": {"lang": "Tagalog", "then": "trigger-measurement"},
    "past continuous": "past continuative",
    "with definite article": "definite includes-article",
    "with indefinite article": "indefinite includes-article",
    "(usually without article)": "usually-without-article",
    "Completive": "completive",
    "dative definite": "dative definite",
    "nominative definite": "nominative definite",
    "long nominative": "nominative",
    "Past subjunctive": "past subjunctive",
    "Prot.": "prototonic",
    "Deut.": "deuterotonic",
    "Imperfect": "imperfect",
    "Present indicative": "present indicative",
    "Passive pl.": "passive plural",
    "Passive sg.": "passive singular",
    "1st sg.": "first-person singular",
    "2nd sg.": "second-person singular",
    "3rd sg.": "third-person singular",
    "1st pl.": "first-person plural",
    "2nd pl.": "second-person plural",
    "3rd pl.": "third-person plural",
    "Indefinite feminine gender": "indefinite feminine",
    "Definite feminine gender": "definite feminine",
    "present participle¹ or gerund": "present participle gerund",
    "short forms": "short-form",
    "long forms": "long-form",
    "Negative adjective (un-…-able)": "negative participle",
    "Positive adjective (-able)": "participle",
    "Infinitive (archaic)": "infinitive archaic",
    "Subjunctive Mood": "subjunctive",
    "Conditional Mood": "conditional",
    "Indicative Mood": "indicative",
    "3rd person pl, 2nd p. pl formal":
    ["third-person plural",
     "third-person plural formal second-person-semantically"],
    "2nd person pl informal": "second-person plural informal",
    "3rd person sg, 2nd p. sg formal":
     ["third-person singular",
      "third-person singular formal second-person-semantically"],
    "Participle": "participle",
    "Past tense": "past",
    "Present tense": "present",
    "oblique/vocative": "oblique vocative",
    "3ʳᵈ person f": "third-person feminine",
    "3ʳᵈ person m": "third-person masculine",
    "Case/Form": "",
    "Positive Infinitive": "positive infinitive",
    "future converb I": "future converb converb-i",
    "future converb II": "future converb converb-ii",
    "perfective converb": "perfective converb",
    "simultaneous converb": "simultaneous converb",
    "imperfective converb": "imperfective converb",
    "dative and adverbial": ["dative", "adverbial"],
    "nominative genitive and instrumental": "nominative genitive instrumental",
    "singular unknown": "singular",
    "Plural of variety": "plural plural-of-variety",
    "dir. pl.": "direct plural",
    "dir. sg.": "direct singular",
    "Terminative": "terminative",
    "Desiderative": "desiderative",
    "mediopassive voice": "mediopassive",
    "past frequentative": "past frequentative",
    "Infinitives": {
        "default": "infinitive",
        "lang": "Swahili",
        "then": "dummy-section-header infinitive",
    },
    "Pronon": "",
    "म SING.": {"if": "first-person", "then": "singular"},
    "हामी PL.": {"if": "first-person", "then": "plural"},
    "तँ LOW-RESP. SING.": {"if": "second-person", "then": "singular impolite"},
    "तिमी MID-RESP.": {"if": "second-person", "then": "polite"},
    "ऊ LOW-RESP. SING.": {"if": "third-person", "then": "singular impolite"},
    "उनी MID-RESP.": {"if": "third-person", "then": "polite"},
    "तपाईं / ऊहाँ HIGH-RESP.": "formal deferential",
    "2ⁿᵈ & 3ʳᵈ": "second-person third-person",
    "plural only (plurale tantum)": "plural-only",
    "approximative": "approximative",
    "consecutive": "consecutive",
    "post-classical": "",
    "Active present participle": "active present participle",
    "Active perfect participle": "active perfect participle",
    "Passive perfect participle": "passive perfect participle",
    "active participle اِسْم الْفَاعِل": "active participle",
    "active voice الْفِعْل الْمَعْلُوم": "active",
    "singular الْمُفْرَد": "singular",
    "dual الْمُثَنَّى": "dual",
    "plural الْجَمْع": "plural",
    "1ˢᵗ person الْمُتَكَلِّم": "first-person",
    "2ⁿᵈ person الْمُخَاطَب": "second-person",
    "3ʳᵈ person الْغَائِب": "third-person",
    "past (perfect) indicative الْمَاضِي": "past perfective indicative",
    "non-past (imperfect) indicative الْمُضَارِع": # XXX remove me to check if I'm relevant
    "non-past imperfective indicative",
    # ^ This might have been changed in the wiktionary template:
    "non-past (imperfect) indicative الْمُضَارِع الْمَرْفُوع": #x تراجع/Arabic
    "non-past imperfective indicative",
    "subjunctive الْمُضَارِع الْمَنْصُوب": "subjunctive",
    "jussive الْمُضَارِع الْمَجْزُوم": "jussive",
    "imperative الْأَمْر": "imperative",
    "passive participle اِسْم الْمَفْعُول": "passive participle",
    "passive voice الْفِعْل الْمَجْهُول": "passive",
    "verbal noun الْمَصْدَر": "noun-from-verb",
    "verbal nouns الْمَصَادِر": "noun-from-verb",
    "strong declension": "strong",
    "weak declension": "weak",
    "Recently Complete": "completive past past-recent",
    "Recent past": "past past-recent",
    "Remote past": "past past-remote",
    "first singular": "first-person singular",
    "second singular": "second-person singular",
    "third singular": "third-person singular",
    "quotative": "quotative",
    "ma-infinitive": "infinitive infinitive-ma",
    "ma- infinitive": "infinitive infinitive-ma",
    "da-infinitive": "infinitive infinitive-da",
    "da- infinitive": "infinitive infinitive-da",
    "da-form": "verb-form-da",
    "des-form": "verb-form-des",
    "m gender": "masculine",
    "long": "long-form",
    "short": "short-form",
    "1st pers.": "first-person",
    "2nd pers.": "second-person",
    "3rd pers.": "third-person",
    "aorist (simple past)": "aorist",
    "aorist II (past perfect II)": "aorist aorist-ii",
    "admirative": "admirative",
    "Adverbial": "adverbial",
    "adjective": "adjectival",
    "neuter gender": "neuter",
    "number and gender": "",
    "attributive and/or after a declined word": "attributive",
    "independent as first declined word": "",
    "after a declined word": "attributive",
    "as first declined word": "",
    "singular only": "singular-only",
    "absolute superlative": "absolute superlative",
    "present subjunctive": "present subjunctive",
    "my": "possessive singular first-person",
    "your": "possessive singular plural second-person",
    "her/his/its": "possessive singular third-person",
    "our": "possessive plural first-person",
    "their": "possessive plural third-person",
    "nominal": "noun",  # XXX or noun-from-something?
    "circumstantial": "circumstantial",
    "jussive": "jussive",
    "Singulative": "singulative",
    "singulative": "singulative",
    "Collective": "collective",
    "Paucal": "paucal",
    "stem": "stem",
    "resultative participle": "resultative participle",
    "subject participle": "subjective participle",
    "connegative converb": "connegative converb",
    "subjunctive singular": "subjunctive singular",
    "imperative singular": "imperative singular",
    "imperative sing.": "imperative singular",
    "imperative plural": "imperative plural",
    "imperative plur.": "imperative plural",
    "participle of necessity": "participle necessitative",
    "special": "special",
    "half-participle": "half-participle",
    "manner of action": "adverbial-manner",
    "mixed declension": "mixed",
    "Habitual Aspect": "habitual",
    "Perfective Aspect": "perfective",
    "Progressive Aspect": "progressive",
    "1ˢᵗ": "first-person",
    "2ⁿᵈ": "second-person",
    "3ʳᵈ": "third-person",
    "Negative Infinitive": "negative infinitive",
    "2nd person singular": "second-person singular",
    "present active participle": "present active participle",
    "past active aorist participle": "past active aorist participle",
    "past active imperfect participle": "past active imperfect participle",
    "past passive participle": "past passive participle",
    "adverbial participle": "adverbial participle",
    "adjectival participle": "adjectival participle",
    "perfect participle": "perfect participle",
    "definite subject form": "definite subjective",
    "definite object form": "definite objective",
    "durative sentence": "durative",
    "negated with": "negated-with",
    "non-durative sentence": "non-durative",
    "main clause": "main-clause",
    "subordinate clause": "subordinate-clause",
    "conjunctive": "conjunctive",
    "future conjunctive": "future conjunctive",
    "egressive": "egressive",
    "first singular yo": "first-person singular",
    "second singular tu": "second-person singular",
    "third singular él/elli": "third-person singular",
    "first plural nosotros/nós": "first-person plural",
    "second plural vosotros/vós": "second-person plural",
    "third plural ellos": "third-person plural",
    "First person": "first-person",
    "Second person": "second-person",
    "Third person": "third-person",
    "Very faml. & Inferior": "familiar impolite",
    "Familiar": "familiar",
    "Honorific": "honorific",
    "Non honorific": "",
    "Continuous": "continuative",
    "Others": "",
    "Other forms": "dummy-reset-headers",  # Reset (είμαι/Greek/Verb)
    "Oblique": "oblique",
    "Demonstrative oblique": "demonstrative oblique",
    "♀": "feminine",
    "Class 1 weak": "class-1 weak",
    "Benefactive": "benefactive",
    "1sg": "first-person singular",
    "1pl": "first-person plural",
    "2sg": "second-person singular",
    "2pl": "second-person plural",
    "Irrealis": "irrealis",
    "Realis": "realis",
    "Contrasting conjunction": "contrastive",
    "Causal conjunction": "causative",
    "Conditional conjunction": "conditional",
    "Perfect tense": "perfect",
    "Perfect-continuative tense": "perfect continuative",
    "present indicative/future": "present future indicative",
    "imperfect (indicative/subjunctive)/ conditional":
    ["imperfect indicative subjunctive", "conditional"],
    "verbal adjectives": "participle",
    "relative (incl. nominal / emphatic) forms": "relative",
    "Passive perfect particple": "passive perfect participle",
    "caritive": "caritive",
    "Caritive": "caritive",
    "Gerund & Past participle": ["gerund", "past participle"],
    "Pronoun": "",
    "nominative genitive instrumental": "nominative genitive instrumental",
    "dative adverbial": "dative adverbial",
    "♂": "masculine",
    "2nd singular ты": "second-person singular",
    "3rd singular ён / яна́ / яно́": "third-person singular",
    "1st plural мы": "first-person plural",
    "2nd plural вы": "second-person plural",
    "3rd plural яны́": "third-person plural",
    "plural мы / вы / яны́": "plural",
    "masculine я / ты / ён": "masculine",
    "feminine я / ты / яна́": "feminine",
    "neuter яно́": "neuter",
    "Imperfect indicative": "imperfect indicative",
    "Verbal of necessity": "necessitative",
    "without article": "without-article",
    "participle (a26)": "participle",
    "participle (a6)": "participle",
    "participle (a5)": "participle",
    "participle (a39)": "participle",
    "Definite feminine and masculine gender": "definite feminine masculine",
    "Neuter s-stem": "neuter",
    "2nd sg informal": "second-person singular informal",
    "2nd person plural (2p) Giinawaa": "second-person plural",
    "3rd person sg": "third-person singular",
    "Causative / Applicative": "causative applicative",
    "Lengadocian (Standard Occitan)": "Lengadocian",
    "Auvernhàs": "Auvernhàs",  # Dialect of Occitan
    "Gascon": "Gascon",  # Occitan
    "Lemosin": "Lemosin",  # Occitan
    "Provençau": "Provençau",  # Occitan
    "Old Saxon personal pronouns": "personal pronoun",
    "nominative / accusative": "nominative accusative",
    "situative": "situative",
    "oppositive": "oppositive",
    "multiplicative": "multiplicative",
    "temporal": "temporal",
    "Aorist": "aorist",
    "Illative": "illative",
    "superlative": "superlative",
    "aspect / mood": "",
    "impersonal participle": "impersonal participle",
    "action noun": "noun-from-verb",
    "Future passive participle": "future passive participle",
    "essive-instructive": "essive-instructive",
    "accusative-ablative": "accusative ablative",
    "plurale tantum": "plural-only",
    "Emphatic": "emphatic",
    "non-past": "non-past",
    "2nd person m": "second-person masculine",
    "2nd person pl formal": "second-person plural formal",
    "3rd singular m": "third-person singular masculine",
    "3rd dual": "third-person dual",
    "First-person": "first-person",
    "Second-person": "second-person",  # sibi/Latin
    "Simple present / conditional": "present conditional",
    "Future progressive, presumptive": "future progressive presumptive",
    "Prolative I": "prolative",
    "infinitive I": "infinitive infinitive-i",
    "general accusative": "accusative",
    "nonpast": "non-past",
    "masculine/neuter": "masculine neuter",
    "Past Stem": "past stem",
    "Genitive-Dative": "genitive dative",
    "Present / future": "present future",
    "indefinite singular": "indefinite singular",
    "indirect": "indirect",
    "locative-qualitative": "locative-qualitative",
    "separative": "separative",
    "paucal": "paucal",
    "Tense": "",
    "Voice": "",
    "Plain infinitive": "infinitive",
    "Weak inflection": "weak",
    "common gender": {
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-common",
        "else": "common-gender",
    },
    "Common gender": {
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-common",
        "else": "common-gender",
    },
    "common": {
        "if": "possessive",
        "lang": POSSESSIVE_POSSESSED_LANGS,
        "then": "possessed-common",
        "else": "common-gender",
    },
    "archaic": "archaic",
    "either gender": "masculine feminine",
    "present stem": "present",
    "inclusive": "inclusive",
    "NORI (dative)": "dative",
    "DURATIVE": "durative",
    "nom./acc.": "nominative accusative",
    "acc.": "accusative",
    "FUTURE TENSE": "future",
    "OPTATIVE": "optative",
    "possessive m": "possessive masculine",
    "past progressive": "past progressive",
    "long infinitive": "infinitive infinitive-i-long",
    "l-participles": "l-participle",
    "L-participle": "l-participle",
    "l-participle": "l-participle",
    "Informal negative": "informal negative",
    "infinitival forms": "infinitive",
    "subjunctive sing.": "subjunctive singular",
    "subjunctive plur.": "subjunctive plural",
    "Type": "",
    "type": "",
    "gender-neutral": "gender-neutral",
    "gender-neutral (person)": "gender-neutral",
    "sing. conneg.": "singular connegative",
    "plur. conneg.": "plural connegative",
    "Definite attributive": "definite attributive",
    "present conditional": "present conditional",
    "past conditional": "past conditional",
    "connegative": "connegative",
    "present active": "present active",
    "past active": "past active",
    "past passive": "past passive",
    "→○": "",  # e.g. sikkaralla/Finnish
    "○": "",  # e.g. sikkaralla/Finnish
    "○→": "",  # e.g. sikkaralla/Finnish
    "with positive imperatives": "with-positive-imperative",
    "no possessor": "no-possessor",
    # "+ object concord": XXX,
    # "state": XXX,
    # "free state": XXX,
    # "Free state": XXX,
    # "Full form": XXX,
    # "Noun": XXX,
    # "stative stem": XXX,
    # "unmutated": XXX,
    # "unmodified": XXX,
    # "Genitive infin.": XXX,
    # "ilz, elles": XXX,
    # "el / ela": XXX,
    # "il/elli": XXX,
    # "el / ela / Vde": XXX,
    # "benim (my)": XXX,
    # "Declarative": XXX,
    # "substantive genitive": XXX,
    # "preposition": XXX,
    # "specific": XXX,
    # "adverb": XXX,
    # "adverbial participles": XXX,
    # "In genitive": XXX,
    # "Low": XXX,
    # "Low/Mid": XXX,
    # "Tense particles (See particles)": XXX,
    # "past stem": XXX,
    # "transitory past": XXX,
    # "determiners": XXX,
    # "determiners and pronouns": XXX,
    # "past particle": XXX,
    # "class I": XXX,
    # "adelative": XXX,
    # "oblique I": XXX,
    # "NORK (ergative)": "",  # XXX see irakatsi/Basque
    # "NOR (absolutive)": "",  # XXX see irakatsi/Basque


    # These are headers for columns that contain titles even if not header style
    "noun case": {
        "lang": "Finnish",
        "then": "*",  # e.g., kolme/Finnish
        "else": "",
    },
    "adverbial form": {
        "lang": "Finnish",
        "then": "*",  # e.g., kolme/Finnish
        "else": "adverbial",
    },
    "m verbs conjugated according to 3rd person sg. er": {
        "lang": "German",
        "if": "polite",  # du/German
        "then": "masculine third-person second-person-semantically"
    },
    # This didn't work to replace "second-person": -KJ
    # ~ "2nd person": {
        # ~ "lang": "German",
        # ~ "if": "second-person-semantically",  # du/German
        # ~ "then": ""
    # ~ },
    "(without article)": {
        "lang": "German",  # jeglicher/German
        "then": "without-article",
    },
    "(with indefinite article)": {
        "lang": "German",  # jeglicher/German
        "then": "indefinite with-article",
    },
    "Strong plural": {
        "lang": "German",  # mehrere/German
        "then": "strong plural",
    },
    "Weak and mixed plural": {
        "lang": "German",
        "then": "weak mixed plural",  # mehrere/German
    },
    "Second-person formal": { # Ihr/German
        "lang": "German",
        "then": "second-person formal",
    },
    "Singular (neuter, pronoun only)": {
        "lang": "German",
        "then": "singular neuter pronoun",
    },
    "Plural, strong forms": {
        "lang": "German",
        "then": "plural strong",
    },
    "Plural, weak and mixed forms (e.g. with definite article)": {
        "lang": "German",
        "then": "plural weak mixed with-article",
    },
    "strong (without article)": { # selber/German
        "lang": "German",
        "then": "strong without-article",
    },
    "weak (with definite article)": { # selber/German
        "lang": "German",
        "then": "weak definite with-article",
    },
    "m./n. plural": { # оба/Russian
        "lang": "Russian",
        "then": "masculine neuter plural",
    },
    "f. plural": { # оба/Russian
        "lang": "Russian",
        "then": "feminine plural"
    },
    "sigmatic future": "sigmatic future",  # adiuvo/Latin
    "sigmatic aorist": "sigmatic aorist",  # adiuvo/Latin
    "Key constructions": {
        "lang": "Japanese",
        "then": "dummy-reset-headers",  # Break column inheritance, 伶俐/Japanese
    },
    "Informal past": { # 伶俐/Japanese
        "lang": "Japanese",
        "then": "informal past",
    },

    "Informal negative past": { # 伶俐/Japanese
        "lang": "Japanese",
        "then": "informal negative past",
    },

    "Formal negative": { # 伶俐/Japanese
        "lang": "Japanese",
        "then": "formal negative",
    },

    "Formal past": { # 伶俐/Japanese
        "lang": "Japanese",
        "then": "formal past",
    },
    "Formal negative past": { # 伶俐/Japanese
        "lang": "Japanese",
        "then": "formal negative past",
    },
    "Provisional": { # 伶俐/Japanese
        "lang": "Japanese",
        "then": "past conditional",
    },
    "Degree": { # 伶俐/Japanese
        "lang": "Japanese",
        "then": "noun-from-adj",  # equivalent to English -ness, needs more
    },
    # in חתול/Hebrew:
    "With possessive pronouns": "possessed-form",

    "Person": {
        "default": "person",
        "lang": ["Hebrew", "Scottish Gaelic", "Old Irish",],
        # umpa/Scottish Gaelic, la/Old Irish
        "then": "*",
    },
    "masculine singular": {
        "lang": "Hebrew",
        "if": "possessed-form",
        "then": "possessed-masculine possessed-single",  # doesn't work
        "else": "masculine singular",
    },
    # could there be a third control character besides "*" and "dummy-reset-headers"
    # that lets you override bleeding rules for a column so that it
    # takes over the whole row, like here?
    "masculine plural": {
        "lang": "Hebrew",
        "if": "possessed-form",
        "then": "possessed-masculine possessed-many",
        "else": "masculine plural",
    },
    "feminine singular": {
        "lang": "Hebrew",
        "if": "possessed-form",
        "then": "possessed-feminine possessed-single",
        "else": "feminine singular"
    },
    "feminine plural": {
        "lang": "Hebrew",
        "if": "possessed-form",
        "then": "possessed-feminine possessed-many",
        "else": "feminine plural",
    },

    "masculine and neuter": "masculine neuter",  # hannars/Westrobothnian
    "singular masculine": "masculine singular",
    "plural masculine": "masculine plural",
    "singular feminine": "feminine singular",
    "plural feminine": "feminine plural",
    "singular neuter": "neuter singular",
    "plural neuter": "neuter plural",

    "quantitative": { # vienas/Lithuanian
        "lang": "Lithuanian",
        "pos": "num",
        "then": "cardinal",
    },
    "ordinal": {
        "lang": "Lithuanian",
        "pos": "num",
        "then": "ordinal",
    },
    "plain": {
        "lang": "Lithuanian",
        "then": "",
    },
    "prefixed with be-": {
        "lang": "Lithuanian",
        "then": "be-prefix",
    },
    "special adverbial participle": {
        "lang": "Lithuanian",
        "then": "adverbial participle",
    },
    "present adverbial": {
        "lang": "Lithuanian",
        "then": "present adverbial",
    },
    "past adverbial": {
        "lang": "Lithuanian",
        "then": "past adverbial",
    },
    "past frequentative adverbial": {
        "lang": "Lithuanian",
        "then": "past frequentative adverbial",
    },
    "future adverbial": {
        "lang": "Lithuanian",
        "then": "future adverbial",
    },


    "1st person (pirmasis asmuo)" : { # -uoti/Lithuanian
        "lang": "Lithuanian",
        "then": "first-person",
    },

    "2nd person(antrasis asmuo)" : {
        "lang": "Lithuanian",
        "then": "second-person",
    },

    "3rd person(trečiasis asmuo)" : {
        "lang": "Lithuanian",
        "then": "third-person",
    },

    "present dependent": { # abair/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "present dependent",
    },
    "past habitual dependent": { # abair/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "past habitual dependent",
    },
    "future dependent": { # abair/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "future dependent",
    },
    "conditional dependent": { # abair/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "conditional dependent",
    },
    "conditional independent": { # abair/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "conditional independent",
    },
    "future independent": { # faigh/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "future independent",
    },
    "past independent": { # faigh/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "past independent",
    },
    "past dependent": { # faigh/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "past dependent",
    },
    "present independent": { # faigh/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "present independent",
    },
    "past habitual independent": { # faigh/Irish, table for archaic verb paradigm
        "lang": "Irish",
        "then": "past habitual independent",
    },

    "definite singular": "definite singular",
    "indefinite plural": "indefinite plural",
    "definite plural": "definite plural",

    "masc." : "masculine",  # ща/Bulgarian
    "fem.": "feminine",
    "neut.": "neuter",

    "genitive form": "genitive",  # глава/Bulgarian
    "feminine/ neuter": "feminine neuter",  # два/Bulgarian

    "future indicative": "future indicative",  # mdlić/Polish

    "dummy-ignored-text-cell": "dummy-ignored-text-cell",  # Kludge

    "s": {
        "lang": "Finnish",  # erata/Finnish
        "then": "singular",
    },
    "pl": {
        "lang": "Finnish",  # erata/Finnish
        "then": "plural",
    },
    "pos": "positive",  # erata/Finnish
    "neg": "negative",  # erata/Finnish

    "evidential participle": "evidential participle",  # տալ/Armenian
    "future converb 1": "future converb converb-i",  # տալ/Armenian
    "future converb 2": "future converb converb-ii",  # տալ/Armenian
    "past imperfect": "past imperfect",  # տալ/Armenian
    "դուն": {  # տալ/Armenian
        "lang": "Armenian",
        "then": "second-person singular",
    },
    "ան": {  # տալ/Armenian
        "lang": "Armenian",
        "then": "third-person singular",
    },
    "անանք": { # տալ/Armenian
        "lang": "Armenian",
        "then": "third-person plural",
    },
    "(դուն)": { # տալ/Armenian
        "lang": "Armenian",
        "then": "second-person singular",
    },

    "1 sg." : "first-person singular",  # féin/Old Irish
    "2 sg." : "second-person singular",  # féin/Old Irish
    "3 sg." : "third-person singular",  # féin/Old Irish
    "1 pl." : "first-person plural",  # féin/Old Irish
    "2 pl." : "second-person plural",  # féin/Old Irish
    "3 pl." : "third-person plural",  # féin/Old Irish
    "m./n." : "masculine neuter",  # féin/Old Irish
    "Stressed": "stressed",  # suide/Old irish
    "Unstressed": "unstressed",  # suide/Old Irish
    "Masculine": { # suide/Old Irish
        "default": "masculine",
        "lang": "Old Irish",
        "then": "dummy-reset-headers masculine",
    },
    "Feminine/neuter": {
        "default": "feminine neuter",
        "lang": "Old Irish",
        "then": "dummy-reset-headers feminine neuter",
    },
    "2d sing.": "second-person singular",  # attá/Old Irish
    "3d sing.": "third-person singular",  # attá/Old Irish
    "3d sg. masc.": "third-person singular masculine",  # attá/Old Irish
    "3d sg. fem.": "third-person singular feminine",  # attá/Old Irish
    "2d sg.": "second-person singular",  # attá/Old Irish BOTH OF THESE in the same template!
    "3d sg.": "third-person singular",  # attá/Old Irish
    "2d pl.": "second-person plural",  # attá/Old Irish
    "3d pl.": "third-person plural",  # attá/Old Irish
    "Pres.​indic.​prog.": "present indicative progressive",  # attá/Old Irish
    "Pres.​indic.​hab.": "present indicative habitual",  # attá/Old Irish
    # ~ "Pres.ind.": "present indicative",  # attá/Old Irish
    # Original data has a zero-width space, causing problems
    "Pres.​subj.": "present subjunctive",  # attá/Old Irish

    "Active present participle ➤": {  # στρατοπεδεύω/Greek (modern)
        "lang": "Greek",
        "then": "active present participle indeclinable",
    },
    "Active perfect participle ➤": {
        "lang": "Greek",
        "then": "active perfect participle indeclinable",
    },
    "Passive perfect participle ➤": {
        "lang": "Greek",
        "then": "passive perfect participle indeclinable",
    },
    "Perfect participle ➤": {  # χαίρομαι/Greek
        "lang": "Greek",
        "then": "perfect participle indeclinable",
    },
    #https://en.wikipedia.org/wiki/Nonfinite_verb#Modern_Greek
    "Nonfinite form ➤": {
        "lang": "Greek",
        "then": "infinitive-aorist",
    },

    "m·s": "masculine singular",  # καθείς/Greek
    "f·s": "feminine singular",
    "n·s": "neuter singular",
    "m·p": "masculine plural",  # αυτός/Greek
    "f·p": "feminine plural",
    "n·p": "neuter plural",

    "Masc./Fem./Neut.": "masculine feminine neuter",  # mille/Latin
    "Reflexive third": "third-person reflexive",  # se/Latin

    "masculine dual": "masculine dual",  #a סוס/Hebrew

    "his": "third-person singular masculine possessive",  # moj/Serbo-Croatian
    "her": "third-person singular feminine possessive",  # moj/Serbo-Croatian

    "1st singular (я (ja))": "first-person singular",  # быць/Serbo-Croatian
    "2nd singular (ты (ty))": "second-person singular",
    "3rd singular (ён (jon)/яна́ (janá)/яно́ (janó))": "third-person singular",
    "1st plural (мы (my))": "first-person plural",
    "2nd plural (вы (vy))": "second-person plural",
    "3rd plural (яны́ (janý))": "third-person plural",
    "plural (мы (my), вы (vy), яны́ (janý))": "plural",
    "masculine (я (ja), ты (ty), ён (jon))": "masculine",
    "feminine (я (ja), ты (ty), яна́ (janá))": "feminine",
    "neuter (яно́ (janó))": "neuter",

    "adjectival partc.": "adjectival participle",  # доврне/Macedonian
    "adverbial partc.": "adverbial participle",
    # ~ "non-finite forms": {  # доврне/Macedonian  didn't work out
        # ~ "lang": "Macedonian",
        # ~ "then": "",
    # ~ },
    # ~ "l-participle": "l-participle",
    # ~ "Compound tenses": {
        # ~ "lang": "Macedonian",
        # ~ "pos": "verb",
        # ~ "then": "dummy-reset-headers",
    # ~ },

    "collective": {  # ремен/Macedonian
        "lang": ["Lithuanian", "Macedonian", "Proto-Indo-European",],
        "pos": ["num", "noun"],
        "then": "collective",
    },

    "Nominative/Accusative (Unarticulated)": "nominative accusative indefinite",  # acid caboxilic/Romanian
    "Nominative/Accusative (Definite articulation)": "nominative accusative definite",
    "Genitive/Dative (Definite articulation)": "genitive dative definite",

    "present infinitive": "present infinitive",  # фи/Romanian
    "past infinitive": "past infinitive",

    # ~ This doesn't want to work - why?
    # ~ "rare but acceptable": "standard",  # soler/Spanish

    "genitive (gjinore) (i/e/të/së)": "genitive",  # mjez/Albanian

    "participle — present": "present participle",  # afrohet/Albanian
    "participle — perfect": "perfect participle",
    "gerund — present": "present gerund",
    "gerund — perfect": "perfect gerund",
    "infinitive — present": "present infinitive",
    "infinitive — perfect": "perfect infinitive",
    "privative": "privative",
    "absolutive — perfect": "perfect absolutive",
    "continuous present": "present progressive",
    "continuous imperfect": "imperfect progressive",
    "2nd future": "future future-ii",
    "2nd future perfect": "future future-ii perfect",
    "imperative — negatory": "negative imperative",
    "genitive/dative/ablative": "genitive dative ablative",  # tij/Albanian
    "male forms": "masculine",  # Dit/Albanian
    "female forms": "feminine",
    "Base form": {
        "lang": ["Arabic", "Moroccan Arabic","Maltese","Gulf Arabic",],
        # "pos": ["noun", "verb", "particle", "prep"],
        "then": "stem",
    },
    "Personal-pronoun- including forms": {
        "lang": ["Arabic", "Moroccan Arabic","Maltese","Gulf Arabic",],
        # "pos": ["noun", "verb", "particle", "prep"],
        "then": "dummy-reset-headers",
    },
    # ~ "singular": {
        # ~ "lang": ["Arabic", "Moroccan Arabic",],
        # ~ "pos": "prep",
        # ~ "if": "stem",
        # ~ "then": "dummy-reset-headers",
    # ~ },

    "common, neuter": {  # kaj/Serbo-Croatian
        "lang": "Serbo-Croatian",
        "then": "common-gender neuter",
    },

    "pres.​indep.​aff.": "present independent affirmative",  # bí/Irish
    "pres.​dep.": "present dependent",
    "pres.​neg.‡": "present negative",  # after ‡ starts working as a footnote
                                       # character, remove it from here.
    "pres.​hab.": "present habitual",
    "past hab.": "past habitual",
    "past ind.": "past independent",
    "past dep.": "past dependent",

    "accusative form": "accusative",  # отец/Bulgarian
    "basic suffix": "suffix",
    "direct object suffix": "direct-object suffix",
    "indirect object suffix": "indirect-object suffix",

    "Xemxin": "xemxin-assimilation",  # lil/Maltese
    "Qamrin": "qamrin-unassimilation",

    "State": {
        "lang": ["Aramaic", "Hebrew", "Assyrian Neo-Aramaic",], 
        "pos": "noun",
        "then": "*",
        "else": "",
    },
    "state": {
        "lang": "Assyrian Neo-Aramaic", 
        "pos": "noun",
        "then": "*",
        "else": "",
    },

    "Absolute": {  #x חקלא/Aramaic
        "lang": "Aramaic",
        "pos": "noun",
        "then": "absolute",
    },
    "Determined": {
        "lang": "Aramaic",
        "pos": "noun",
        "then": "emphatic",
    },
    "emphatic": "emphatic",  #v דלתא/Aramaic

    "3rd f": "third-person feminine",  #umpa/Scottish Gaelic
    "Number": {
        "default": "",
        #umpa/Scottish Gaelic
        "lang": ["Hebrew", "Scottish Gaelic",],
        "then": "*",
    },

    "Third person f": "third-person feminine",  # an/Scottish Gaelic
    "First sg": "first-person singular",  # an/Scottish Gaelic
    "Second sg": "second-person singular",
    "Third sg m": "third-person singular masculine",
    "Third sg f": "third-person singular feminine",
    "First pl": "first-person plural",
    "Second pl": "second-person plural",
    "Third pl": "third-person plural",
    "Independent": "independent",
    "independent": "independent",  # immee/Manx
    "Affirmative Interrogative": "affirmative interrogative",
    "Negative Interrogative": "negative interrogative",

    "Affirmative interrogative": "affirmative interrogative",  # thathar/Scottish Gaelic
    "Relative future": ["with-pronoun future", "with-conjunction future",],

    "agent1, 3": "agent participle",  # puhkaa/Finnish

    "Unabbreviated form": "unabbreviation alt-of",  # jku/Finnish
    "Abbreviation": "abbreviation",

    "nãs/nãsu, nãsã/nãsa, el/elu, ea": {
        "lang": "Aromanian",
        "if": "third-person singular",
        "then": "third-person singular",
    },

    "Masculine,Feminine, Neuter": "masculine feminine neuter",
    # tři/Czech, copy-pasted manual table without template...
    "Present Sg": "present singular",  # skrýt/Czech
    "Present Pl": "present plural",
    "Future Sg": "future singular",
    "Future Pl": "future plural",
    "Past Sg": "past singular",
    "Past Pl": "past plural",

    "neuter singular": "neuter singular",  # ony/Czech

    # dar éisi/Old Irish, la/Old Irish
    "3d sing. masc./neut., accusative":
        "third-person singular masculine neuter accusative",
    "3d sing. masc./neut., dative":
        "third-person singular masculine neuter dative",
    "3d sing. fem., accusative":
        "third-person singular feminine accusative",
    "3d sing. fem., dative":
        "third-person singular feminine dative",
    "3d person pl., dative":
        "third-person plural dative",
    "3d person pl., accusative":
        "third-person plural accusative",

    "nominative-accusative": "nominative accusative", #stand/Nynorsk
    "compound-genitive": "in-compounds genitive",

    "Common": {
        "lang": "Arabic",
        "then": "common-gender",
    },

    "Affix": "affix",

    # podnikat/Czech
    "you (singular)": "second-person singular",
    "you (polite)": "second-person singular formal",
    "he/she/it": "third-person singular",
    "we": {
        "lang": "Czech",
        "then": "first-person plural",
    },
    "you (plural)": "second-person plural",
    "they": {
        "lang": "Czech",
        "then": "third-person plural",
    },
    "Active (Perfect)": "active participle",
    "Masculine, feminine, neuter": "masculine feminine neuter",  # čtyři/Czech

    "participle (a7)": "participle",  # hylja/Faroese
    "participle (a8)": "participle",  # lagt/Faroese
    "participle (a34)": "participle",  # falla/Faroese
    "participle (a27)": "participle",  # kvøða/Faroese
    "participle (a18/a6)": "participle",  # skreiða/Faroese
    "participle (a18)": "participle",  # ýa/Faroese
    "participle (a5 (a39))": "participle",  # skráseta/Faroese


    # síggjast/Faroese
    "eg": {
        "lang": "Faroese",
        "then": "first-person singular",
    },
    "hann/hon/tað": "third-person singular",
    "vit, tit, teir/tær/tey": "plural",
    "mediopassive": "mediopassive",

    "imperfect (indicative/subjunctive)/conditional": {  #de-glicio/Welsh
        "lang": "Welsh",
        "then": ["imperfect indicative", "conditional"],
    },
    "imperfect indicative/conditional": {  #gwneud/Welsh
        "lang": "Welsh",
        "then": ["imperfect indicative", "conditional"],
    },
    "present/future": {  # darganfod/Welsh
        "lang": "Welsh",
        "then": ["present indicative", "future indicative"],
    },
    "imperfect/conditional": {  # darganfod/Welsh
        "lang": "Welsh",
        "then": ["imperfect indicative", "conditional"],
    },
    "future/present habitual": {  # adnabod/Welsh
        "lang": "Welsh",
        "then": ["future habitual", "present habitual"],
    },

    # ϧⲉⲣϧⲉⲣ/Coptic
    # Bohairic
    "ⲁⲛⲟⲕ": "first-person singular",
    # Removed duplicates
    "ⲁⲛⲟⲛ": "first-person plural",
    "-": {
        "lang": "Coptic",
        "then": "nominal",
        "else": {
            "lang": "Assamese",
            "pos": "verb",
            "then": "negative",
            "else": {
                "lang": "Old Saxon",
                "pos": "pron",
                "then": ""
                },
        },
    },
    "focalising, precursive": "focalising",

    # ⲃⲱⲗ/Coptic, different pronouns in different dialects
    # Sahidic
    # Removed duplicates
    # Akhmimic
    "ⲁⲛⲁⲕ": "first-person singular",
    "ⲛ̄ⲧⲁⲕ": "second-person singular masculine",
    "ⲛ̄ⲧⲁϥ": "third-person singular masculine",
    "ⲛ̄ⲧⲁⲥ": "third-person singular feminine",
    "ⲁⲛⲁⲛ": "first-person plural",
    "ⲛ̄ⲧⲱⲧⲛⲉ": "second-person plural",
    "ⲛ̄ⲧⲁⲩ": "third-person plural",
    # Lycopolitan has a mixture of different forms
    # Fayyumic
    "ⲛⲧⲁⲕ": "second-person singular masculine",
    "ⲛⲧⲁ": "second-person singular feminine",
    "ⲛⲧⲁϥ": "third-person singular masculine",
    "ⲛⲧⲁⲥ": "third-person singular feminine",
    "ⲛⲧⲁⲧⲉⲛ": "second-person plural",
    "ⲛⲧⲁⲩ": "third-person plural",
    "circumstantial, focalising": "focalising",

    # ignore Tagalog Affix column affixes
    # manghalik/Tagalog
    "Actor-secondary": "actor-secondary",
    "mang-": {"lang": "Tagalog", "then": "",},
    "-an": {"lang": "Tagalog", "then": "",},
    "pang- -an": {"lang": "Tagalog", "then": "",},
    "ikapang-": {"lang": "Tagalog", "then": "",},
    "magpa-": {"lang": "Tagalog", "then": "",},
    "papang- -in": {"lang": "Tagalog", "then": "",},
    "⁠ pa- -an": {"lang": "Tagalog", "then": "",},
    "ipagpa-": {"lang": "Tagalog", "then": "",},
    "ipapang-": {"lang": "Tagalog", "then": "",},
    "ikapagpapang-": {"lang": "Tagalog", "then": "",},
    "papang- -an": {"lang": "Tagalog", "then": "",},
    "makapang-": {"lang": "Tagalog", "then": "",},
    "ma -an": {"lang": "Tagalog", "then": "",},
    "maipang-": {"lang": "Tagalog", "then": "",},
    "maikapang-": {"lang": "Tagalog", "then": "",},
    "mapang- -an": {"lang": "Tagalog", "then": "",},
    "makapagpa-": {"lang": "Tagalog", "then": "",},
    "mapapang-": {"lang": "Tagalog", "then": "",},
    "mapa- -an": {"lang": "Tagalog", "then": "",},
    "maipagpa-": {"lang": "Tagalog", "then": "",},
    "maipapang-": {"lang": "Tagalog", "then": "",},
    "maikapagpapang-": {"lang": "Tagalog", "then": "",},
    "mapapang- -an": {"lang": "Tagalog", "then": "",},
    "makipang-": {"lang": "Tagalog", "then": "",},
    "makipagpa-": {"lang": "Tagalog", "then": "",},
    # ipalinis/Tagalog
    "mag-": {"lang": "Tagalog", "then": "",},
    "-in": {"lang": "Tagalog", "then": "",},
    "\u2060pag- -an": {"lang": "Tagalog", "then": "",},
    "ipag-": {"lang": "Tagalog", "then": "",},
    "ipang-": {"lang": "Tagalog", "then": "",},
    "ikapag-": {"lang": "Tagalog", "then": "",},
    "pag- -an": {"lang": "Tagalog", "then": "",},
    "papag- -in": {"lang": "Tagalog", "then": "",},
    "ipa-": {"lang": "Tagalog", "then": "",},
    "ikapagpa-": {"lang": "Tagalog", "then": "",},
    "\u2060pagpa- -an": {"lang": "Tagalog", "then": "",},
    "\u2060papag- -an": {"lang": "Tagalog", "then": "",},
    "makapag-": {"lang": "Tagalog", "then": "",},
    "ma-": {"lang": "Tagalog", "then": "",},
    "maipag-": {"lang": "Tagalog", "then": "",},
    "maikapag-": {"lang": "Tagalog", "then": "",},
    "mapag- -an": {"lang": "Tagalog", "then": "",},
    "mapapag-": {"lang": "Tagalog", "then": "",},
    "maipa-": {"lang": "Tagalog", "then": "",},
    "maikapagpa-": {"lang": "Tagalog", "then": "",},
    "mapagpa- -an": {"lang": "Tagalog", "then": "",},
    "mapapag- -an": {"lang": "Tagalog", "then": "",},
    "makipag-": {"lang": "Tagalog", "then": "",},
    "maki-": {"lang": "Tagalog", "then": "",},
    # batikusin/Tagalog
    "-um-": {"lang": "Tagalog", "then": "",},
    "i-": {"lang": "Tagalog", "then": "",},
    "ika-": {"lang": "Tagalog", "then": "",},
    "pa- -in": {"lang": "Tagalog", "then": "",},
    # umagnas/Tagalog
    "um-": {"lang": "Tagalog", "then": "",},
    # baybayin/Tagalog
    "Directional": "directional",
    # madali/Tagalog
    "root": "root",
    "superiority": {"lang": "Tagalog", "then": "superior",},
    "inferiority": {"lang": "Tagalog", "then": "inferior",},
    "equality": {"lang": "Tagalog", "then": "equal",},
    # sumisid/Tagalog
    "maka-": {"lang": "Tagalog", "then": "",},
    "mapa-": {"lang": "Tagalog", "then": "",},
    "mai-": {"lang": "Tagalog", "then": "",},
    "maika-": {"lang": "Tagalog", "then": "",},
    "mapag- -an": {"lang": "Tagalog", "then": "",},
    "mapagpa- -an": {"lang": "Tagalog", "then": "",},
    "mapapag- -an": {"lang": "Tagalog", "then": "",},
    # ipasagot/Tagalog
    "ma- -an": {"lang": "Tagalog", "then": "",},
    "mapa- -an": {"lang": "Tagalog", "then": "",},
    # ayusin/Tagalog
    "mapag-": {"lang": "Tagalog", "then": "",},


    "resultative": "resultative",  # sloniti/Proto-Slavic
    "imperfective aorist": "aorist imperfective",  # byti/Proto-Slavic

    "Masculine and feminine": "masculine feminine",  # hwa/Old English

    # ufuy/Afar
    "Postpositioned forms": {
        "lang": "Afar",
        "then": "with-postposition",
    },
    "l-case": "l-case",
    "k-case": "k-case",
    "t-case": "t-case",
    "h-case": "h-case",
    # icfide/Afar
    "present progressive": "present progressive",
    "future progressive": "future progressive",
    "immediate future": "immediate-future",
    "imperfect potential I": "imperfect potential potential-i",
    "imperfect potential II": "imperfect potential potential-ii",
    "perfect potential": "perfect potential",
    "present conditional II": "present conditional conditional-ii",
    "present conditional I": "present conditional conditional-i",
    "irrealis": "irrealis",
    "perfect conditional": "perfect conditional",
    "V-affirmative": "v-affirmative",
    "N-affirmative": "n-affirmative",
    "conjunctive I": "conjunctive conjunctive-i",
    "conjunctive II": "conjunctive conjunctive-ii",
    "consultative": "consultative",
    "-h converb": "h-converb converb",
    "-i form": "i-form converb",
    "-k converb": "k-converb converb",
    "-in(n)uh converb": "innuh-converb converb",
    "-innuk converb": "innuk-converb converb",
    "V-focus": "v-focus participle indefinite",
    "N-focus": "n-focus participle indefinite",
    "indefinite participle": "indefinite participle",
    # qunxa/Afar
    "present indicative I": "present indicative indicative-i",
    "present indicative II": "present indicative indicative-ii",
    "past indicative I": "past indicative indicative-i",
    "past indicative II": "past indicative indicative-ii",
    "present potential": "present potential",

    "dist. plural": "distributive plural",  # nástro/Navajo
    "duoplural": "duoplural",
    # this separate duoplural number can't simply be broken into dual and plural
    # because of tag-merging issues, like here: if Navajo has the default numbers
    # ["singular", "plural"], then singular + duoplural has "dual" left over,
    # if it has ["singular", "plural", "dual",] then all of them are merged BUT
    # that implies that the non-duoplural "plural" could also be part of the merge.
    "Unspecified": {
        "lang": "Navajo",
        "then": "indefinite-person",
    },
    "Unspecified person": {
        "lang": "Navajo",
        "then": "indefinite-person",
    },
    "Passive A": {
        "lang": "Navajo",
        "then": "passive",
    },

    "Passive B": {
        "lang": "Navajo",
        "then": "passive agentive",
    },
    "Spatial": {
        "lang": "Navajo",
        "then": "spatial-person",
    },
    "Spatial person": {
        "lang": "Navajo",
        "then": "spatial-person",
    },
    "ITERATIVE": "iterative",  # náhádleeh/Navajo
    "early": "archaic",  #soule/Middle English
    "nominative, accusative": "nominative accusative",  #dale/Middle English
    "subjunctive plural": "subjunctive plural",  #been/Middle English
    "Middle": {
        "lang": ["Hittite", "Sanskrit",],
        "then": "middle-voice",  # अवति/Sanskrit
    },
    "Active Voice": "active",
    "Passive Voice": "passive",
    "Middle Voice": "middle-voice",  #शृणोति/Sanskrit

    "Potential mood / Optative mood": "potential",
    # ვენეციური/Georgian
    "nominative, genitive, instrumental": "nominative genitive instrumental",
    "dative, adverbial": "dative adverbial",
    "negative imperative": "negative imperative",  # აბეზღებს/Georgian
    #მათ/Georgian
    "third-person": "third-person",
    "personal pronouns": {
        "lang": "Georgian",
        "then": "",
    },
    "relative pronouns": {
        "lang": "Georgian",
        "then": "",
    },
    "this": "proximal pronoun singular",
    "that": "distal pronoun singular",
    "these": "proximal pronoun plural",
    "those": "distal pronoun plural",
    # დაწერს/Georgian
    "masdar": "noun-from-verb",  #also in Arabic
    "transitive screeves": "transitive",
    "intransitive screeves": "intransitive",
    "privative participle": "privative participle",
    "მე": {
        "lang": "Georgian",
        "then": "first-person singular",
        },
    "შენ": {
        "lang": "Georgian",
        "then": "second-person singular",
        },
    "ის": {
        "lang": "Georgian",
        "then": "third-person singular",
        },
    "ჩვენ": {
        "lang": "Georgian",
        "then": "first-person plural",
        },
    "თქვენ": {
        "lang": "Georgian",
        "then": "second-person plural",
        },
    "ისინი": {
        "lang": "Georgian",
        "then": "third-person plural",
        },
    "მან": {
        "lang": "Georgian",
        "then": "third-person singular",
        },
    "მათ": {
        "lang": "Georgian",
        "then": "third-person plural",
        },
    "მას": {
        "lang": "Georgian",
        "then": "third-person singular",
        },
    # ~ "": {
        # ~ "lang": "Georgian",
        # ~ "then": "",
        # ~ },
    "inversion": "inversion",

    # maanaadad/Ojibwe
    "singular (0s)": "singular inanimate",
    "obviative singular (0's)": "obviative inanimate singular",
    "plural (0p)": "plural inanimate",
    "obviative plural (0'p)": "obviative plural inanimate",
    "singular or plural (0)": "singular plural inanimate",
    "obviative singular or plural (0')": "obviative singular plural inanimate",

    #a ܒܢܓܐ/Classical_Syriac
    "1st c. sg. (my)": "first-person singular common-gender possessive",
    "2nd m. sg. (your)": "second-person singular masculine possessive",
    "2nd f. sg. (your)": "second-person singular feminine possessive",
    "3rd m. sg. (his)": "third-person singular masculine possessive",
    "3rd f. sg. (her)": "third-person singular feminine possessive",
    "1st c. pl. (our)": "first-person common-gender plural possessive",
    "2nd m. pl. (your)": "second-person plural masculine possessive",
    "2nd f. pl. (your)": "second-person plural feminine possessive",
    "3rd m. pl. (their)": "third-person plural masculine possessive",
    "3rd f. pl. (their)": "third-person plural feminine possessive",

    # vágyhat/Hungarian
    "3rd person sg, 2nd person sg formal":
        ["third-person singular",
         "second-person singular formal",],
    "3rd person pl, 2nd person pl formal":
        ["third-person plural",
         "second-person plural formal",],
    # ichwane/Zulu
    "Possessive forms": "possessive",
    "Full form": "full-form",
    "Simple form": "basic-form",
    "Substantive": {
        "lang": "Zulu",
        "if": "possessive",
        "then": "possessive-substantive",
    },
    "Modifier": {
        "lang": ["Zulu", "Swazi",],
        # ~ "if": "possessive",
        "then": "",
        "else": {
            "lang": "Xhosa",  #magqagala
            "then": "attributive",
        },
    },
    "Copulative": "copulative",

    "present negative": "present negative",  # hoteti/Slovene

    "Construct state": "construct",  # ziqqurratum/Akkadian
    # marāṣum/Akkadian
    "Adjective": "adjective",
    "1.sg":"first-person singular",
    "2.sg": "second-person singular",
    "3.sg": "third-person singular",
    "1.pl": "first-person plural",
    "2.pl": "second-person plural",
    "3.pl": "third-person plural",

    # pats/Latvian
    "Masculine Singular": "masculine singular",
    "Feminine Singular": "feminine singular",
    "Masculine Plural": "masculine plural",
    "Feminine Plural": "feminine plural",

    "⁠ ka- -an": {"lang": "Tagalog", "then": "",},  # maligaw/Tagalog

    # AFAICT the following is just the idiosyncracy of a singular editor.
    # No real idea of what "analytical" means in this context. It's not
    # standard terminology for specific forms, but I guess it could
    # stand for some kind of free-standing form...
    "analytical": {  # immee/Manx
        "lang": "Manx",
        "then": "analytic",
    },

    # alcun/Old French
    "Subject": "subjective",

    # styri/Lower Sorbian
    "Masculine inanimate/ feminine/neuter":
        ["masculine inanimate",
         "feminine neuter",
        ],
    "Masculine animate": "masculine animate",

    # glab/Breton
    "unmutated": "unmutated",
    "hard": {
        "lang": "Breton",
        "then": "mutation-hard",
    },
    "0": {  # gwildronañ/Breton
        "lang": "Breton",
        "pos": "verb",
        "then": "impersonal",
    },
    "Impersonal forms": {
        "lang": "Breton",
        "pos": "verb",
        "then": "*",
    },
    "Mutated forms": {
        "lang": "Breton",
        "pos": "verb",
        "then": "dummy-reset-headers",
    },

    # дөрвөл/Mongolian
    "substantive genitive":
        "possessive-substantive genitive",
    "attributive locative":
        "attributive locative",

    # сэрээх/Mongolian
    "Future participle": "future participle",
    "Confirmative": "confirmative",
    "Resultative": "resultative",
    "Imperfective converb": "imperfective converb",
    "possessive particle": "possessive particle",  #чи/Mongolian

    # কোবোৱা/Assamese
    "Gerund, Past participle, Agentive":
        ["gerund",
         "past participle",
         "agentive",
        ],
    "Progressive participle": "progressive participle",
    "t": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "",
    },
    "মই moi": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "first-person",
        },
    "তই toi": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "familiar impolite second-person",
        },
    "তুমি tumi": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "familiar second-person",
        },
    "আপুনি apuni": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "honorific second-person",
        },
    "তেওঁ etc teü͂": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "honorific third-person",
        },
    "সি ♂, তাই ♀ etc xi ♂, tai ♀": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "third-person",
        },
    "আমি ami": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "first-person",
        },
    "তহঁত tohõt": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "familiar impolite second-person",
        },
    "তোমালোক tümalük": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "familiar second-person",
        },
    "আপোনালোক apünalük": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "honorific second-person",
        },
    "তেওঁলোক teü͂lük": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "honorific third-person",
        },
    "সিহঁত etc xihõt": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "third-person",
        },
    "তহঁতে tohõte": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "familiar impolite second-person",
        },
    "তোমালোকে tümalüke": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "familiar second-person",
        },
    "আপোনালোকে apünalüke": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "honorific second-person",
        },
    "তেওঁলোকে teü͂lüke": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "honorific third-person",
        },
    "সিহঁতে etc xihõte": {
        "lang": "Assamese",
        "pos": "verb",
        "then": "third-person",
        },

    # gözde/Turkish predicative adjective table
    "ben (I am)": "first-person singular",
    "sen (you are)": "second-person singular",
    "o (he/she/it is)": "third-person singular",
    "biz (we are)": "first-person plural",
    "siz (you are)": "second-person plural",
    "onlar (they are)": "third-person plural",
    "ben (I was)": "first-person singular",
    "sen (you were)": "second-person singular",
    "o (he/she/it was)": "third-person singular",
    "biz (we were)": "first-person plural",
    "siz (you were)": "second-person plural",
    "onlar (they were)": "third-person plural",
    "ben (if I)": "first-person singular",
    "sen (if you)": "second-person singular",
    "o (if he/she/it)": "third-person singular",
    "biz (if we)": "first-person plural",
    "siz (if you)": "second-person plural",
    "onlar (if they)": "third-person plural",
    "positive, declarative": "",
    "positive, interrogative": "interrogative",
    "negative, declarative": "negative",
    "negative, interrogative": "negative interrogative",

    #a راتلل/Pashto
    "زۀ": "first-person singular",
    "تۀ": {
        "if": "second-person singular masculine",
        "then": "second-person singular masculine",
        "else": {
            "if": "second-person singular feminine",
            "then": "second-person singular feminine",
            "else": "second-person singular",
            },
        },

    "دی / هغه": "third-person singular masculine",
    "دا / هغه": "third-person singular feminine",
    "موږ": "first-person plural",
    "تاسې": "second-person plural",
    "دوی / هغوی": "third-person plural",
    "present imperfective": "present imperfective",
    "present perfective": "present perfective",
    "تاسو": "second-person plural",
    # This specific form seems like the addition of someone later in a
    # new part of the table, it's a Northern Pashto variant, so someone
    # might change it later, unless تاسو is part of the "command"
    # paradigm in general.

    #a ہاوُن/Kashmiri
    "Feminine plural": "feminine plural",
    "Completed": "completive",
    "بہٕ": "first-person singular",
    'ژٕ': "second-person singular",
    "سُہ, سۄ": "third-person singular",
    'أسؠ': "first-person plural",
    "تۄہؠ, تۆہؠ": "second-person plural",
    "تِم, تِمہٕ": "third-person plural",
    "Nominative subject": "with-nominative",
    "Ergative subject": "with-ergative",
    "Simple present": "present",
    "Past continuous": "past continuative",
    "Future continuous": "future continuative",
    "m or f": "masculine feminine",
    "Simple future": "future",
    # Ergatives
    'مےٚ': "first-person singular",
    'ژےٚ': "second-person singular",
    'تٔمؠ, تَمہِ': "third-person singular",
    'اَسہِ': "first-person plural",
    'تۄہہِ': "second-person plural",
    'تِمَو': "third-person plural",
    "m sg": "masculine singular",
    "m pl": "masculine plural",
    "f sg": "feminine singular",
    "f pl": "feminine plural",
    "Obligatory": "obligative",
    "Simple Conditional": "conditional",
    "Conditional past continuous": "past continuative conditional",
    "Conditional past perfect": "past perfect conditional",
    # XXX return to Kashmiri after next wiktionary dump

    # дрьзнѫти/Old Church Slavonic
    "азъ (azŭ)": "first-person singular",
    "тꙑ (ty)": "second-person singular",
    "тъ (tŭ)": "third-person singular",
    "вѣ (vě)": "first-person dual",
    "ва (va)": "second-person dual",
    "та (ta)": "third-person dual",
    "мꙑ (my)": "first-person plural",
    "вꙑ (vy)": "second-person plural",
    "ти (ti)": "third-person plural",

    # əhli-həsəd/Azerbaijani
    "broken plural": "broken-form plural",
    # bədən/Azerbaijani
    "broken": {
        "lang": "Azerbaijani",
        # ~ "if": "plural",  # doesn't work
        "then": "broken-form plural",
        },
    "sound": {
        "lang": "Azerbaijani",
        "then": "",
    },

    # 𒉿𒀠𒄴𒍣/Hittite
    "Noun": {
        "lang": "Hittite",
        "pos": "verb",
        "then": "noun-from-verb",
    },

    # ampesar/Ladino
    "io / yo": {
        "lang": "Ladino",
        "then": "first-person singular",
    },
    "él / ella": {
        "lang": "Ladino",
        "then": "third-person singular",
    },
    "mosotros mosós": {
        "lang": "Ladino",
        "then": "first-person plural",
    },
    "vosotros vosós / vós": {
        "lang": "Ladino",
        "then": "second-person plural",
    },
    "ellos / ellas": {
        "lang": "Ladino",
        "then": "third-person plural",
    },

    # চাওয়া/Bengali
    "progressive participle": "progressive participle",
    "habitual participle": "habitual participle",
    "conditional participle": "conditional participle",
    "আমি (ami)": "first-person",
    "আমরা (amra)": "first-person",
    "তুই (tui)": "second-person impolite",
    "তোরা (tora)": "second-person impolite",
    "তুমি (tumi)": "second-person",
    "তোমরা (tomra)": "second-person",
    "এ (e), ও (o), সে (she)": "third-person",
    "এরা (era), ওরা (ora), তারা (tara)": "third-person",
    "আপনি (apni)": "second-person formal",
    "আপনারা (apnara)": "second-person formal",
    "ইনি (ini), উনি (uni), তিনি (tini)":
        "third-person formal",
    "এঁরা (ẽra), ওঁরা (õra), তাঁরা (tãra)":
        "third-person formal",

    # schlaa/Alemannic German
    "1ˢᵗ person ich, i": "first-person singular",
    "3ʳᵈ person er/si/es": "third-person singular",
    "2ⁿᵈ person ir": "second-person plural",
    # remove duplicates
    
    # natüürlic/Alemannic German
    "Strong inflection": "strong",
    # d/Alemannic German
    "Nominative/Accusative": "nominative accusative",
    # ik/German Low German
    "(Genitive)": "genitive rare",
    "m f": "masculine feminine",  # etwer/German
    # фи/Romanian
    "еу": {
        "lang": "Romanian",
        "pos": "verb",
        "then": "first-person singular",
    },
    "ту": {
        "lang": ["Tajik", "Romanian",],
        "pos": "verb",
        "then":  "second-person singular",
    },
    "ел/я": {
        "lang": "Romanian",
        "pos": "verb",
        "then": "third-person singular",
    },
    "нои": {
        "lang": "Romanian",
        "pos": "verb",
        "then": "first-person plural",
    },
    "вои": {
        "lang": "Romanian",
        "pos": "verb",
        "then": "second-person plural",
    },
    "еи/еле":  {
        "lang": "Romanian",
        "pos": "verb",
        "then": "third-person plural",
    },
    "compound perfect": {  # has mostly replaced the simple perfect
        "lang": "Romanian",
        "then": "perfect",
    },

    # idealistesch/Luxembourgish
    "attributive and/or after determiner": "attributive with-determiner",
    "independent without determiner": "without-determiner",
    "after any declined word": "with-head",
    # hunn/Luxembourgish
    "1ˢᵗ person ech": "first-person singular",
    "2ⁿᵈ person du": "second-person singular",
    "3ʳᵈ person hien/si/hatt": "third-person singular",
    "1ˢᵗ person mir": "first-person plural",
    "2ⁿᵈ person dir": "second-person plural",
    "3ʳᵈ person si": "third-person plural",
    "present simple": "present",
    "future simple": "future",

    # чӧсмасьны/Komi-Zyrian
    "Direct past tense": "direct past",
    "Reported past tense": "reported past",
    "Imperfect participle": "imperfect participle",
    "Caritive participle": "caritive participle",
    # ~ "^(*)) The impersonal reported past is"\
     # ~ "expressed using the third singular form."\
     # ~ " ^(**)) The first person imperative is"\
     # ~ " expressed using the first person future"\
     # ~ " form. ^(***)) Any form ending in -ӧй"\
     # ~ " has an alternative form ending in -ӧ."\
     # ~ " ^(****)) The imperfect and perfect"\
     # ~ " participles have alternative forms"\
     # ~ " with a paragogic -а.":
    "^(*)) The impersonal reported past is expressed using the third singular form. ^(**)) The first person imperative is expressed using the first person future form. ^(***)) Any form ending in -ӧй has an alternative form ending in -ӧ. ^(****)) The imperfect and perfect participles have alternative forms with a paragogic -а.":
        "",  #<th> with footnotes that don't refer to anything?
    # ми/Komi-Zyrian
    "long dative": "dative",
    "short dative": "dative",
    # сы/Komi-zyrian
    "short nominative": "nominative",
    # ehun/Basque
    "anim.": "animate",
    "inanim.": "inanimate",

    # erakutsi/Basque
    "NORK": {"lang": "Basque", "then": "ergative",},
    "NOR": {"lang": "Basque", "then": "absolutive",},
    "NORI": {"lang": "Basque", "then": "dative",},
    "nik": {"lang": "Basque", "then": "first-person singular",},
    "hik": {"lang": "Basque", "then": "second-person singular informal",},
    "hark": {"lang": "Basque", "then": "third-person singular",},
    "guk": {"lang": "Basque", "then": "first-person plural",},
    "zuk": {"lang": "Basque", "then": "second-person singular",},
    "zuek": {"lang": "Basque", "then": "second-person plural",},
    "haiek": {"lang": "Basque", "then": "third-person plural",},
    "hura": {"lang": "Basque", "then": "third-person singular",},
    "niri": {"lang": "Basque", "then": "first-person singular",},
    "hiri": {"lang": "Basque", "then": "second-person singular informal",},
    "hari": {"lang": "Basque", "then": "third-person singular",},
    "guri": {"lang": "Basque", "then": "first-person plural",},
    "zuri": {"lang": "Basque", "then": "second-person singular",},
    "zuei": {"lang": "Basque", "then": "second-person plural",},
    "haiei": {"lang": "Basque", "then": "third-person plural",},
    "future cons.": "future consequential",
    "past cons.": "past consequential",
    "2nd sg inf": "second-person singular informal",
    # ISP/Norwegian
    "Bokmål m": {
        "lang": "Norwegian Bokmål",
        "then": "masculine",
        "else": "masculine Bokmål",
    },
    "Bokmål f": {
        "lang": "Norwegian Bokmål",
        "then": "feminine",
        "else": "feminine Bokmål",
    },
    "Bokmål c": {
        "lang": "Norwegian Bokmål",
        "then": "common-gender",
        "else": "common-gender Bokmål",
    },
    "Bokmål n": {
        "lang": "Norwegian Bokmål",
        "then": "neuter",
        "else": "neuter Bokmål",
    },
    "Bokmål": {
        "lang": "Norwegian Bokmål",
        "then": "",
        "else": "Bokmål",
    },

    "Nynorsk f": {
        "lang": "Norwegian Nynorsk",
        "then": "feminine",
        "else": "feminine Nynorsk",
    },

    "Nynorsk m": {
        "lang": "Norwegian Nynorsk",
        "then": "masculine",
        "else": "masculine Nynorsk",
    },

    "Nynorsk n": {
        "lang": "Norwegian Nynorsk",
        "then": "neuter",
        "else": "neuter Nynorsk",
    },
    "Nynorsk c": {
        "lang": "Norwegian Nynorsk",
        "then": "common-gender",
        "else": "common-gender Nynorsk",
    },
    "Nynorsk": {
        "lang": "Norwegian Nynorsk",
        "then": "",
        "else": "Nynorsk",
    },


    # του/Greek
    "weak": "weak",
    "strong": "strong",

    "infinitive — present)": "present infinitive",  #eh/Albanian
    "infinitive — perfect)": "perfect infinitive",
    "past perfect I": "past past-i perfect",
    "past perfect II": "past past-ii perfect",
    "future I": "future future-i",
    "future II": "future future-ii",
    "future perfect I": "future future-i perfect",
    "future perfect II": "future future-ii perfect",
    "ato (3rd person feminine plural)": "third-person feminine plural",  #ato/Albanian
    "ai (3rd person masculine singular)": "third-person masculine singular",  #ai
    "ti (2nd person singular)": "second-person singular",  #ti
    "ata (3rd person masculine plural)": "third-person masculine plural",  #ata
    "ajo (3rd person feminine singular)":" third-person feminine singular",  #ajo

    # Tagalog small verb tables, like magwahil/Tagalog
    # need something to tag a td-cell with stuff like
    # "actor" or "object" in it, or else it'll cause
    # NO-TAGS. Unfortunately, only "actor" is tagged
    # because "object" and others are parsed as headers.
    # At least this way, there is no error message, but
    # it is inconsistently applied.
    # Using "focus": "detail", in valid_tags seems to
    # do the trick and stop 'focus' from bleeding as it
    # doesn't with "misc".
    "Trigger": {
        "lang": "Tagalog",
        "then": "focus",
    },

    # Arabic number paradigm markers decomposed after changes in the parser:
    #a  ـًى (-an) => ar-infl-an-maksura
    #a  ـًا (-an) => ar-infl-an-alef
    "basic broken plural diptote": "broken-form plural diptote",
    "basic broken plural triptote": "broken-form plural triptote",  #a حجرة/Arabic
    "basic collective triptote": "collective triptote",
    "basic singular diptote": "singular diptote",
    "basic singular triptote": "singular triptote",
    "broken plural diptote in ـٍ (-in)":  "broken-form plural diptote ar-infl-in",  #a سحلية/Arabic
    "broken plural in ـًى (-an)": "broken-form plural ar-infl-an-maksura",  #a بلوة/Arabic
    "broken plural invariable": "broken-form plural invariable",  #a ضحية/Arabic
    "broken plural triptote in ـَة (-a)": "broken-form plural triptote ar-infl-a",  #a رصيد/Arabic
    "collective invariable": "collective invariable",
    "diptote triptote": ["diptote", "triptote",],
    "singular diptote in ـٍ (-in)": "singular diptote ar-infl-in",
    "singular diptote in ـَاة (-āh)": "singular diptote ar-infl-ah",  #a حماة/Arabic
    "singular diptote in ـَة (-a)": "singular diptote ar-infl-a",  #a أرمية/Arabic
    "singular in ـًا (-an)": "singular ar-infl-an-alef",
    "singular in ـًى (-an)": "singular ar-infl-an-maksura",  #a مدى/Arabic
    "singular invariable": "singular invariable",
    "singular long construct": "singular long-construct",  #a ذو الحجة/Arabic
    "singular of irregular noun": "singular irregular",
    "singular triptote in ـٍ (-in)": "singular triptote ar-infl-in",
    "singular triptote in ـَاة (-āh)": "singular triptote ar-infl-ah", #a قناة السويس/Arabic
    "singular triptote in ـَة (-a)": "singular triptote ar-infl-a",  #a حاجة/Arabic
    "singulative triptote in ـَة (-a)": "singulative triptote ar-infl-a",  #a جثجاث/Arabic
    "sound feminine paucal": "sound-form feminine paucal",
    "sound feminine plural": "sound-form feminine plural",
    "sound masculine plural": "sound-form masculine plural",
    "sound masculine paucal": "sound-form masculine paucal",
    "basic broken paucal triptote": "broken-form paucal triptote",
    "sound plural in ـَوْنَ (-awna)": "sound-form plural ar-infl-awna",
    "broken plural triptote in ـَاة (-āh)": "broken-form plural triptote ar-infl-ah",
    "basic collective diptote": "collective diptote",
    "basic singulative triptote": "singulative triptote",
    "basic singulative diptote": "singulative diptote",
    "singulative triptote in ـَاة (-āh)": "singulative triptote ar-infl-ah",
    "collective triptote in ـَة (-a)": "collective triptote ar-infl-a",
    "collective in ـًا (-an)": "collective ar-infl-an-alef",
    "broken plural triptote in ـٍ (-in)": "broken-form plural triptote ar-infl-in",
    "broken plural in ـًا (-an)": "broken-form plural ar-infl-an-alef",
    "broken plural in ـًى (-an)‎": "broken-form plural ar-infl-an-maksura",
    "plural of irregular noun": "plural irregular",
    "collective in ـًى (-an)": "collective ar-infl-an-maksura",
    "broken paucal triptote in ـَة (-a)": "broken-form paucal triptote ar-infl-a",
    "singular of irregular pronoun": "singular irregular pronoun",
    "basic broken paucal diptote": "broken-form paucal diptote",
    
    
    
    # teie/Estonian
    "Partitive": "partitive",
    "Inessive": "inessive",
    "Elative": "elative",
    "Allative": "allative",
    "Adessive": "adessive",
    "Translative": "translative",
    "Essive": "essive",
    "Abessive": "abessive",
    "Comitative": "comitative",

    # ащема/Moksha
    "one possession": "possessive possessed-single",
    "one or multiple possessions": "possessive possessed-single possessed-many",
    # XXX the big headers don't express

    "Participles➤": "participle",  # άρχω/Greek
    "Active Present ➤": "present",
    "Passive Present ➤": "passive present",

    # 알리다/Korean
    "Formal non-polite": "formal",
    "Informal non-polite": "informal",
    "Informal polite": "informal polite",
    "Formal polite": "formal polite",

    "Middle/Passive": "middle-voice passive",  # पिबति/Sanskrit

    "Singular base form": "singular base-form",  #a ܒܪܘܢܐ/Assyrian Neo-Aramaic
    "Plural base form": "plural base-form",

    "substantive": {
        "lang": ["Chechen", "Ingush",],
        "pos": "noun",
        "then": "substantive-case",
    },

    "similitude": "similitude",  # a ئانا/Uyghur
    "equivalence": "equal",
    "Declension of locative-qualitative form": "locative-qualitative",
    "representative": "representative",
    "Declension of representative form": "representative",

    # When copy-pasting headers from Wiktionary with a browser,
    # remember to replace the "downgraded"-superscripts into
    # unicode superscript characters here, if the copy-pasted
    # content doesn't have super-scripts. Things with <sup></sup>
    # get automatically translated into those in clean.py, and
    # these entries have to match them. If copy-pasting from
    # error messages in the shell, you get the 'correct' characters.

    "2ⁿᵈperson singular ordinary": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "second-person singular possessive",
    },
    "2ⁿᵈperson plural ordinary": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "second-person plural possessive",
    },
    "2ⁿᵈperson singular refined": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "second-person singular formal possessive",
    },
    "2ⁿᵈperson plural refined": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "second-person plural formal possessive",
    },
    "2ⁿᵈperson singular & plural respectful (your)": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "second-person polite possessive",
    },
    "1ˢᵗ person plural": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "first-person plural possessive",
        "else": "first-person plural",
    },
    "3ʳᵈ person (his, her, its, their)": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "third-person singular possessive",
    },
    "1ˢᵗ person singular": {
        "lang": "Uyghur",
        "pos": "noun",
        "then": "first-person singular possessive",
        "else": "first-person singular",
    },

    # -raihu/Kikuyu
    # Class [singular class], Class [plural class]
    "Class 1, Class 2": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-1",
        "else": "class-2",
    },
    "Class 3, Class 4": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-3",
        "else": "class-4",
    },
    "Class 5, Class 6": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-5",
        "else": "class-6",
    },
    "Class 7, Class 8": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-7",
        "else": "class-8",
    },
    "Class 9, Class 10": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-9",
        "else": "class-10",
    },
    "Class 11, Class 10": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-11",
        "else": "class-10",
    },
    "Class 12, Class 13": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-12",
        "else": "class-13",
    },
    "Class 14, Class 6": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-14",
        "else": "class-6",
    },
    "Class 15, Class 6": {
        "lang": "Kikuyu",
        "if": "singular",
        "then": "class-15",
        "else": "class-6",
    },

    "2nd person f": "second-person feminine",
    
    "ја": {  # THIS IS CYRILLIC!! Not Latin! подразумевати/Serbo-Croatian
        "lang": "Serbo-Croatian",
        "then": "first-person singular",
    },
    "он / она / оно": {
        "lang": "Serbo-Croatian",
        "then": "third-person singular",
    },
    "ми": {
        "lang": "Serbo-Croatian",
        "then": "first-person plural",
    },
    "ви": {
        "lang": "Serbo-Croatian",
        "then": "second-person plural",
    },
    "они / оне / она": {
        "lang": "Serbo-Croatian",
        "then": "third-person plural",
    },
    "conditional¹^, (kushtore)": {  # kushtoj/Albanian
        "lang": "Albanian",
        "then": "conditional",
    },
    "personal non-finite": {  # prosternarse/Spanish
        "lang": "Spanish",
        "then": "",
    },
    "1ˢᵗ person singular (“my”)": "first-person singular possessive",  #a احساس/Persian
    "3ʳᵈ person singular (“his, her, its”)": "third-person singular possessive",
    "1ˢᵗ plural (“our”)": "first-person plural possessive",
    "2ⁿᵈ plural (“your”)": "second-person plural possessive",
    "3ʳᵈ plural (“their”)": "third-person plural possessive",

    "with possessive pronouns": "possessed-form",  #a ܡܘܙܐ/Assyrian Neo-Aramaic

    # Talat/Turkish, possessive tables for names
    "benim (my)": "first-person singular",
    "senin (your)": "second-person singular",
    "onun (his/her/its)": "third-person singular",
    "bizim (our)": "first-person plural",
    "sizin (your)": "second-person plural",
    "onların (their)": "third-person plural",

    # Alpler/Turkish
    "singular, uncountable (tekil, sayılamaz)": "singular uncountable",

    # अकड़ना/Hindi
    "1ˢᵗ मैं": "first-person singular",
    "2ⁿᵈ तू": "second-person singular",
    "3ʳᵈ यह/वह, ये/वो": "third-person singular",
    "2ⁿᵈ तुम": "second-person plural",
    "1ˢᵗ हम": "first-person plural",
    "3ʳᵈ, 2ⁿᵈ ये/वो/वे, आप":
        ["third-person plural",
         "second-person formal"],
    
    # -ra/Basque
    "proximal plural": "proximal plural",

    #a שלאָפֿן/Yiddish
    # These tables are unparseable due to lack of headers, really
    # ~ "Composed forms": "",

    # kalium/Limburgish
    "Root singular": "singular",
    "Root plural": "plural",
    "Diminutive singular": "diminutive singular",
    "Diminutive plural": "diminutive plural",

    # tèlle/Limburgish
    "adverb": "adverb",
    "number & tense": "*",
    "verb-second order": "v2",
    "verb-first order": "v1",
    "first person plural": "first-person plural",
    "second person plural": "second-person plural",
    "third person plural": "third-person plural",
    "other forms": "",
    "imperative singular impolite": "imperative singular impolite",
    "imperative singular polite": "imperative singular polite",
    "imperative dual": "imperative dual",

    # beer/Limburgish
    "Diminutive": "diminutive",
    "Mutation": "mutation",
    "Diminutive Mutation": "diminutive mutation",

    # сядоце/Moksha
    "мон (mon)": "first-person singular",
    "минь (minʹ)": "first-person plural",
    "тон (ton)": "second-person singular",
    "тинь (tinʹ)": "second-person plural",
    "сон (son)": "third-person singular",
    "синь (sinʹ)": "third-person plural",

    # улемс/Moksha
    "1ˢᵗ singular — мон (mon)": "first-person singular",
    "2ⁿᵈ singular — тон (ton)": "second-person singular",
    "3ʳᵈ singular — сон (son)": "third-person singular",
    "1ˢᵗ plural — минь (minʹ)": "first-person plural",
    "2ⁿᵈ plural — тинь (tinʹ)": "second-person plural",
    "3ʳᵈ plural — синь (sinʹ)": "third-person plural",
    "Past I": "past-i past",
    "Compound future": "multiword-construction future",
    "agentive / pres. act. part.": "present active participle agentive",
    "present passive participle": "present passive participle",

    # содамс/Moksha
    "Past II / subjunctive": "past-ii past subjunctive",
    "Subjunctive of conditional": "subjunctive conditional",
    "ma-infinitive / verbal noun": "noun-from-verb infinitive infinitive-ma",
    "mda-infinitive": "infinitive infinitive-mda",
    "gerund negative": "negative gerund",
    "1ˢᵗ person singular object — монь (monʹ)":
        "object-first-person object-singular",
    "2ⁿᵈ person singular object — тонь (tonʹ)":
        "object-second-person object-singular",
    "3ʳᵈ person singular object — сонь (sonʹ)":
        "object-third-person object-singular",
    "1ˢᵗ person plural object — минь (minʹ)":
        "object-first-person object-plural",
    "2ⁿᵈ person plural object — тинь (tinʹ)":
        "object-second-person object-plural",
    "3ʳᵈ person plural object — синь (sinʹ)":
        "object-third-person object-plural",

    # ਪਾਉਣਾ/(Punjabi
    "Singular/Plural": "singular plural",
    "Plural/Formal": "",
    "1ˢᵗ ਮੈਂ": "first-person singular",
    "2ⁿᵈ intimate ਤੂੰ": "second-person singular intimate",
    "3ʳᵈ ਇਹ/ਉਹ": "third-person singular",
    "2ⁿᵈ familiar ਤੁਸੀਂ": "second-person familiar",
    "1ˢᵗ ਅਸੀਂ": "third-person plural",
    "2ⁿᵈ formal, 3ʳᵈ ਇਹ/ਉਹ/ਆਪ":
        ["second-person formal",
         "third-person plural",
         ],
    "REG": "",
    "POL": "polite",

    # оз/Komi-Zyrian
    "Non-Past tense": "non-past",

    # hāi7Namuyi
    "Habitual/Future": "habitual future",
    "Prospective": "prospective",
    "Ingressive": "ingressive",
    "Experiential": "experiential",
    "Premeditated": "premeditated",

    # nyanyi/Warlpiri
    "andative": "andative",
    "nomic": "nomic",

    # être/Lorrain
    "je (j')": {
        "lang": "Lorrain",
        "then": "first-person singular",
    },
    "el, elle": {
        "lang": "Lorrain",
        "then": "third-person singular",
    },
    "el, elles": {
        "lang": "Lorrain",
        "then": "third-person plural",
    },
    "distant imperfect (from Latin er-)": "imperfect distant-imperfect-er",
    "distant imperfect (from Latin stab-)": "imperfect distant-imperfect-stab",
    "near imperfect": "imperfect near-imperfect",
    "que je / qu'i": "first-person singular",
    "qu'â (al), qu'ale": "third-person singular",
    "qu'âs, qu'ales": "third-person plural",

    
    "ham": {
        "lang": "Fiji Hindi",
        "then": "first-person singular",
    },
    "ham log": {
        "lang": "Fiji Hindi",
        "then": "first-person plural",
    },
    "tum": {
        "lang": "Fiji Hindi",
        "then": "second-person singular",
    },
    "tum log": {
        "lang": "Fiji Hindi",
        "then": "second-person plural",
    },
    "uu": {
        "lang": "Fiji Hindi",
        "then": "third-person singular",
    },
    "uu log": {
        "lang": "Fiji Hindi",
        "then": "third-person plural",
    },

    # ndu/South Slavey
    "areal": {
        "lang": "South Slavey",
        "then": "locative",
    },

    # ave/Tolai
    "1st person exclusive": "first-person exclusive",
    "1st person inclusive": "first-person inclusive",

    # mahkwa/Fox
    "Singular Noun": "singular",
    "Plural Noun": "plural",
    "Proximate": "proximative",
    "Obviative": "obviative",
    "Local": "locative",
    "Singular Possessive": "possessed-single",
    "Plural Possessive": "possessed-many",
    "First and second person": "first-person second-person",

    "perlative": "perlative",  # arnaq/Yup'ik

    
    # tōku/Maori
    "singular object": {
        "lang": "Maori",
        "then": "possessed-single",
    },
    "dual/plural object": {
        "lang": "Maori",
        "then": "possessed-many",
    },
    "A category":  {
        "lang": "Maori",
        "then": "alienable",
    },
    "O category":  {
        "lang": "Maori",
        "then": "inalienable",
    },
    "Neutral":  {
        "lang": "Maori",
        "then": "",
    },
    "dual subject": "dual",
    "1st person, inclusive": "first-person inclusive",
    "1st person, exclusive": "first-person exclusive",

    "comitative-instrumental": "comitative instrumental",  #тан/Mansi
    # пыг/Mansi
    "double possession": "possessed-two",
    "multiple possession": "possessed-many",
    "3d person dual": "third-person dual",
    "3d person plural": "third-person plural",

    # Tibetan romanizations
    "Wylie": "romanization",

    "Basic": {
        "lang": "Udmurt",
        "then": "",
    },
    "Temporal": {
        "lang": "Udmurt",
        "then":"gerund-temporal gerund",
    },
    "Fourth": {
        "lang":"Udmurt",
        "then": "gerund-iv gerund",
    },
    "Deverbal": {
        "lang":"Udmurt",
        "then": "noun-from-verb",
    },

    # тос/Mariupol Greek
    "3rd n": "third-person neuter",
    "clitic": "clitic",

    # likkõ/Livonian
    "sa": {
        "lang": "Livonian",
        "then":"second-person singular",
    },
    "ta": "third-person singular",
    "mēg": "first-person plural",
    "tēg": "second-person plural",
    "indicative negative": "negative indicative",
    "(sa)": "second-person singular",
    "(mēg)": "first-person plural",
    "(tēg)": "second-person plural",
    "imperative negative": "negative imperative",
    "conditional negative": "negative conditional",
    "jussive negative": "negative jussive",
    "debitive": "debitive",
    "minnõn": "first-person singular",
    "sinnõn": "second-person singular",
    "tämmõn": "third-person singular",
    "mäddõn": "first-person plural",
    "täddõn": "second-person plural",
    "näntõn": "third-person plural",
    "supine abessive": "supine abessive",

    # நத்தை/Tamil
    "Genitive 1": "genitive-i genitive",
    "Genitive 2": "genitive-ii genitive",
    "Locative 1": "locative-i locative",
    "Locative 2": "locative-ii locative",
    "Sociative 1": "sociative-i sociative",
    "Sociative 2": "sociative-ii sociative",

    # பிடி/Tamil
    "singular affective": "affective singular",
    "third masculine": "third-person masculine",
    "third feminine": "third-person feminine",
    "third honorific": "third-person honorific",
    "third neuter": "third-person neuter",
    "நான்": "first-person singular",
    "நீ": "second-person singular",
    "அவன்": "third-person singular masculine",
    "அவள்": "third-person singular feminine",
    "அவர்": "third-person singular honorific",
    "அது": "third-person singular neuter",
    "future negative": "negative future",
    "plural affective": "affective plural",
    "third epicene": "third-person epicene",
    "நாம் (inclusive) நாங்கள் (exclusive)":
                ["first-person plural inclusive",
                 "first-person plural exclusive",],
    "நீங்கள்": "second-person plural",
    "அவர்கள்": "third-person plural epicene",
    "அவை": "third-person plural neuter",
    "effective": "effective",
    "casual conditional": "conditional informal",
    "honorific": "honorific",
    "epicene": "epicene",
    "Form I": {
        "lang": "Tamil",
        "then": "gerund-i gerund",
        },
    "Form II": {
        "lang": "Tamil",
        "then": "gerund-ii gerund",
        },
    "Form III": {
        "lang": "Tamil",
        "then": "gerund-iii gerund",
        },

    # bolmak/Turkmen
    "men": "first-person singular",
    "ol": "third-person singular",
    "olar": "third-person plural",
    "proximal": "proximal",
    "distal": "distal",
    "unwitnessed": "unwitnessed",
    "obligatory": "obligative",

    # kanákta/Mohawk
    "Sing.": "singular",
    "Plur.": "plural",

    # እግር/Amharic
    "Definite subject": "definite nominative",
    "Definite object": "definite accusative",
    "General object": "accusative",

    # sugu/Veps
    "approximative I": "approximative-i approximative",
    "approximative II": "approximative-ii approximative",
    "terminative I": "terminative-i terminative",
    "terminative II": "terminative-ii terminative",
    "terminative III": "terminative-iii terminative",
    "additive I": "additive-i additive",
    "additive II": "additive-ii additive",

        # duhtadit/Northern Sami
    "action inessive": "noun-from-verb inessive",
    "action elative": "noun-from-verb elative",
    "agent participle": "agent participle",
    "action comitative": "noun-from-verb comitative",
    "conditional 1": "conditional-i conditional",
    "conditional 2": "conditional-ii conditional",

    # 능숙하다/Korean
    "Plain": {
        "lang": "Korean",
        "then": "",
    },

    # stupid Interlingua hand-crafted minimal tables, deber/Interlingua
    "Present:": "present",
    "Past:": "past",
    "Future:": "future",
    "Conditional:": "conditional",
    "Present participle:": "present participle",
    "Past participle:": "past participle",
    "Imperative:": "imperative",

    # уө/Southern Yukaghir
    "short plural": "plural short-form",
    "long plural": "plural long-form",

    # aganchaka/Garo
    "Declarative": "",
    '"not yet"': "not-yet-form",
    '"probably"': "potential",
    "Intentional": "intentive",
    "Change of state": "perfect",
    "Formal imperative": "imperative formal",

    # ಹುಟ್ಟು/Kannada
    "adverbial participles": "adverbial participle",
    "adjectival participles": "adjectival participle",
    "other nonfinite forms": "",
    "volitive forms": "volitive",
    "present adverbial participle": "present adverbial participle",
    "nonpast adjectival participle": "non-past adjectival participle",
    "suihortative form": "suihortative",
    "past adverbial participle": "past adverbial participle",
    "past adjectival participle": "past adjectival participle",
    "dative infinitive": "infinitive dative",
    "cohortative form I": "cohortative-i cohortative",
    "negative adverbial participle": "negative adverbial participle",
    "negative adjectival participle": "negative adjectival participle",
    "conditional form": "conditional",
    "cohortative form II": "cohortative-ii cohortative",
    "tense/modality": "",
    "ನಾನು": "first-person singular",
    "ನೀನು": "second-person singular",
    "ಅವನು": "third-person masculine singular",
    "ಅವಳು": "third-person feminine singular",
    "ಅದು": "third-person neuter singular",
    "ನಾವು": "first-person plural",
    "ನೀವು": "second-person plural",
    "ಅವರು": "third-person epicene plural",
    "ಅವು": "third-person neuter plural",
    # ಅದು/Kannada
    '"Objective Singular"': "singular objective",
    "Epicene Plural": "epicene plural",

    # цӏехуьл/Lezgi
    "adelative": "adelative",
    "addirective": "addirective",
    "postessive": "postessive",
    "postelative": "postelative",
    "postdirective": "postdirective",
    "subessive": "subessive",
    "subelative": "subelative",
    "subdirective": "subdirective",
    "inelative": "inelative",
    "superelative": "superelative",
    "superdirective": "superdirective",

    # देर/Konkani
    "accusative/dative": "accusative dative",
    # भेड्डो/Konkani
    "masc. singular": "masculine singular",
    "fem. singular": "feminine singular",
    "masc. plural": "masculine plural",
    "fem. plural": "feminine plural",

    # zeuen burua/Basque
    "elkar": "reciprocal",
    "noren burua": "reflexive",
    # ezer/Basque
    "nor": "interrogative pronoun personal",
    "zer": "interrogative pronoun",
    "zein": "interrogative pronoun",
    "zenbat": "interrogative quantitative",
    # batzuk/Basque
    "bat": "pronoun",
    "bakoitz": "pronoun",

    # veda/Scanian
    "jağ": "first-person singular",
    "dú": "second-person singular",
    "hanð": "third-person singular",
    "ví": "first-person plural",
    "í": "second-person plural",
    "dé":  "third-person plural",
    "present imperative": "present imperative",
    
    #a ګړندی/Pashto
    "oblique I": "oblique oblique-i",
    "oblique II (dialectal)": "oblique oblique-ii dialectal",
    #a پخول/Pashto
    "Present Imperfective Subject Agreement": "present imperfective",
    "Past Imperfective Object Agreement":
        "past imperfective object-concord dummy-object-concord",
    "OBJECT": "",
    "Past Perfective": {
        "default": "past perfective",
        "lang": "Pashto",
        "then": "past perfective object-concord dummy-object-concord",
    },
    # ní/Old Irish
    "Animate": "animate",
    # just in case
    "Inanimate": "inanimate",

    # τα/Greek
    "1-s": "first-person singular",
    "2-s": "second-person singular",
    "3-ms": "third-person masculine singular",
    "3-fs": "third-person feminine singular",
    "3-ns": "third-person neuter singular",
    "1-p": "first-person plural",
    "2-p": "second-person plural",
    "3-mp": "third-person masculine plural",
    "3-fp": "third-person feminine plural",
    "3-np": "third-person neuter plural",

    # angu/Swahili
    "Noun class": {
        "lang": "Swahili",
        "then": "",
        },
    "M-wa class": {
        "lang": "Swahili",
        "then": "class-1 class-2",
    },
    "M-mi class": {
        "lang": "Swahili",
        "then": "class-3 class-4",
    },
    "Ma class": {
        "lang": "Swahili",
        "then": "class-5 class-6",
    },
    "Ki-vi class": {
        "lang": "Swahili",
        "then": "class-7 class-8",
    },
    "N class": {
        "lang": "Swahili",
        "then": "class-9 class-10",
    },
    "U class": {
        "lang": "Swahili",
        "then": "class-11 class-12",
    },
    "Pa class": {
        "lang": "Swahili",
        "then": "class-16",
    },
    "Ku class": {
        "lang": "Swahili",
        "then": "class-15",
    },
    "Mu class": {
        "lang": "Swahili",
        "then": "class-18",
    },
    "m-wa": {
        "lang": "Swahili",
        "then": "class-1 class-2",
    },
    "m-mi": {
        "lang": "Swahili",
        "then": "class-3 class-4",
    },
    "ma": {
        "lang": "Swahili",
        "then": "class-5 class-6",
        "else": {
            "lang": "Livonian",
            "then": "first-person singular",
        }
    },
    "ki-vi": {
        "lang": "Swahili",
        "then": "class-7 class-8",
    },
    "n": {
        "default": "neuter",
        "lang": "Swahili",
        "then": "class-9 class-10",
    },
    "u": {
        "lang": "Swahili",
        "then": "class-11 class-12",
    },
    "pa": {
        "lang": "Swahili",
        "then": "class-16",
    },
    "ku": {
        "lang": "Swahili",
        "then": "class-15",
    },
    "mu": {
        "lang": "Swahili",
        "then": "class-18",
    },
    "other classes": "",
    "Consecutive subjunctive": "consecutive subjunctive",

    # taka/Swahili sw-conj
    "Polarity": "",
    "Persons": "",
    "Persons / Classes": "",
    "Classes": "",
    "3rd / M-wa": {
        "lang": "Swahili",
        "then": "third-person",
    },
    "M-mi": "",
    "Ma": "",
    "Ki-vi": "",
    "N": "",
    "U": "",
    "Ku": "",
    "Pa": "",
    "Mu": "",
    "Sg.": {
        "default": "singular",
        "lang": "Swahili",
        "then": "singular",
    },
    "Pl.": {
        "default": "plural",
        "lang": "Swahili",
        "then": "plural",
    },
    "Sg. / 1": {
        "default": "singular class-1",
        "lang": "Swahili",
        "then": "singular class-1",
    },
    "Pl. / 2":  {
        "default": "plural class-2",
        "lang": "Swahili",
        "then": "plural class-2",
    },
    "3": {
        "default": "third-person",
        "lang": "Swahili",
        "then": "class-3",
        "else": {
            "lang": head_final_numeric_langs,
            "then": "class-3",
        },
    },
    "4": {
        "default": "class-4",
        "lang": "Swahili",
        "then": "class-4",
    },
    "5": {
        "default": "class-5",
        "lang": "Swahili",
        "then": "class-5",
    },
    "6": {
        "default": "class-6",
        "lang": "Swahili",
        "then": "class-6",
    },
    "7": {
        "default": "class-7",
        "lang": "Swahili",
        "then": "class-7",
    },
    "8": {
        "default": "class-8",
        "lang": "Swahili",
        "then": "class-8",
    },
    "9": {
        "default": "class-9",
        "lang": "Swahili",
        "then": "class-9",
    },
    "10": {
        "default": "class-10",
        "lang": "Swahili",
        "then": "class-10",
    },
    "11 / 14": {
        "default": "class-11 class-14",
        "lang": "Swahili",
        "then": "class-11 class-14",
    },
    "15 / 17": {
        "default": "class-15 class-17",
        "lang": "Swahili",
        "then": "class-15 class-17",
    },
    "16": {
        "default": "class-16",
        "lang": "Swahili",
        "then": "class-16",
    },
    "18": {
        "default": "class-18",
        "lang": "Swahili",
        "then": "class-18",
    },

    "1s": {
        "default": "first-person singular",
        "if": "object-concord",
        "then": "object-first-person object-singular",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags first-person singular",
                     "dummy-use-as-rowtags object-first-person object-singular",
                    ],
            },
        },
    "2s": {
        "default": "second-person singular",
        "if": "object-concord",
        "then": "object-second-person object-singular",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags second-person singular",
                    "dummy-use-as-rowtags object-second-person object-singular",
                    ],
            },
        },
    "3s": {
        "default": "third-person singular",
        "if": "object-concord",
        "then": "object-third-person object-singular",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags third-person singular",
                     "dummy-use-as-rowtags object-third-person object-singular",
                    ],
            },
        },
    "1p": {
        "default": "first-person plural",
        "if": "object-concord",
        "then": "object-first-person object-plural",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags first-person plural",
                     "dummy-use-as-rowtags object-first-person object-plural",
                    ],
            },
        },
    "2p": {
        "default": "second-person plural",
        "if": "object-concord",
        "then": "object-second-person object-plural",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags second-person plural",
                    "dummy-use-as-rowtags object-second-person object-plural",
                    ],
            },
        },
    "3p": {
        "default": "third-person plural",
        "if": "object-concord",
        "then": "object-third-person object-plural",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags third-person plural",
                     "dummy-use-as-rowtags object-third-person object-plural",
                    ],
            },
        },
    "c1": {
        "default": "class-1",
        "if": "object-concord",
        "then": "object-class-1",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-1",
                     "dummy-use-as-rowtags object-class-1",]
        },
    },
    "c2": {
        "default": "class-2",
        "if": "object-concord",
        "then": "object-class-2",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-2",
                     "dummy-use-as-rowtags object-class-2",],
        },
    },
    "c3": {
        "default": "class-3",
        "if": "object-concord",
        "then": "object-class-3",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-3",
                     "dummy-use-as-rowtags object-class-3",],
        },
    },
    "c4": {
        "default": "class-4",
        "if": "object-concord",
        "then": "object-class-4",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-4",
                     "dummy-use-as-rowtags object-class-4",],
        },
    },
    "c5": {
        "default": "class-5",
        "if": "object-concord",
        "then": "object-class-5",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-5",
                     "dummy-use-as-rowtags object-class-5",],
        },
    },
    "c6": {
        "default": "class-6",
        "if": "object-concord",
        "then": "object-class-6",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-6",
                     "dummy-use-as-rowtags object-class-6",],
        },
    },
    "c7": {
        "default": "class-7",
        "if": "object-concord",
        "then": "object-class-7",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-7",
                     "dummy-use-as-rowtags object-class-7",],
        },
    },
    "c8": {
        "default": "class-8",
        "if": "object-concord",
        "then": "object-class-8",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-8",
                     "dummy-use-as-rowtags object-class-8",],
        },
    },
    "c9": {
        "default": "class-9",
        "if": "object-concord",
        "then": "object-class-9",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-9",
                     "dummy-use-as-rowtags object-class-9",],
        },
    },
    "c10": {
        "default": "class-10",
        "if": "object-concord",
        "then": "object-class-10",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-10",
                     "dummy-use-as-rowtags object-class-10",],
        },
    },
    "c11": {
        "default": "class-11",
        "if": "object-concord",
        "then": "object-class-11",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-11",
                     "dummy-use-as-rowtags object-class-11",],
        },
    },
    "c12": {
        "default": "class-12",
        "if": "object-concord",
        "then": "object-class-12",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-12",
                     "dummy-use-as-rowtags object-class-12",],
        },
    },
    "c13": {
        "default": "class-13",
        "if": "object-concord",
        "then": "object-class-13",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-13",
                     "dummy-use-as-rowtags object-class-13",],
        },
    },
    "c14": {
        "default": "class-14",
        "if": "object-concord",
        "then": "object-class-14",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-14",
                     "dummy-use-as-rowtags object-class-14",],
        },
    },
    "c15": {
        "default": "class-15",
        "if": "object-concord",
        "then": "object-class-15",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-15",
                     "dummy-use-as-rowtags object-class-15",],
        },
    },
    "c16": {
        "default": "class-16",
        "if": "object-concord",
        "then": "object-class-16",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-16",
                     "dummy-use-as-rowtags object-class-16",],
        },
    },
    "c17": {
        "default": "class-17",
        "if": "object-concord",
        "then": "object-class-17",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-17",
                     "dummy-use-as-rowtags object-class-17",],
        },
    },
    "c18": {
        "default": "class-18",
        "if": "object-concord",
        "then": "object-class-18",
        "else": {
            "lang": "Swahili",
            "then": ["dummy-use-as-coltags class-18",
                     "dummy-use-as-rowtags object-class-18",],
        },
    },
        
    "1s/2s/3s/c1": ["object-first-person object-second-person "
                    "object-third-person object-singular",
                    "object-class-1"],
    "*p/2/3/11/14": ["object-plural object-first-person "
                     "object-second-person object-third-person",
                     "object-class-2 object-class-3 object-class-11 "
                     "object-class-14"],
    "c4/c6/c9": "object-class-4 object-class-6 object-class-9",
    "2s/2p/15/17": ["object-second-person object-singular object-plural",
                    "object-class-15 object-class-17"],
    "2p/3p/c2": ["object-second-person object-third-person object-plural",
                 "object-class-2"],
    "c3/c11/c14": "object-class-3 object-class-11 object-class-14",
    "c4/c9": "object-class-4 object-class-9",
    "Forms with object concords": "object-concord",

    "Past": {
        "default": "past",
        "lang": "Swahili",
        "then": "past",
    },
    "Present": {
        "default": "present",
        "lang": "Swahili",
        "then": "present",
    },
    "Future": {
        "default": "future",
        "lang": "Swahili",
        "then": "future"
     },
    "Subjunctive": {
        "default": "subjunctive",
        "lang": "Swahili",
        "then": "subjunctive"
     },
    "Present conditional": {
        "default": "present irrealis",
        "lang": "Swahili",
        "then": "present irrealis"
     },
    "Past conditional": {
        "default": "past irrealis",
        "lang": "Swahili",
        "then": "past irrealis"
     },
    "Conditional contrary to fact": {
        "default": "conditional counterfactual",
        "lang": "Swahili",
        "then": "conditional counterfactual"
     },
    "Gnomic": {
        "default": "gnomic",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "gnomic"
     },
    "Perfect": {
        "default": "perfect",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "perfect"
     },
    '"Already"': {
        "default": "already-form",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "already-form"
     },
    '"Not yet"': {
        "default": "not-yet-form",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "not-yet-form"
     },
    '"If/When"': {
        "default": "if-when-form",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "if-when-form"
     },
    '"If not"': {
        "default": "if-not-form",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "if-not-form"
     },
    "Consecutive": {
        "default": "consecutive",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "consecutive"
     },
    "General positive": {
        "default": "general-mood positive",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "general-mood positive"
     },
    "General negative": {
        "default": "general-mood negative",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "general-mood negative"
     },
    "Positive past": {
        "default": "positive past",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "positive past"
     },
    "Negative past": {
        "default": "negative past",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "negative past"
     },
    "Positive present": {
        "default": "positive present",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "positive present"
     },
    "Negative present": {
        "default": "negative present",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "negative present"
     },
    "Positive future": {
        "default": "positive future",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "positive future"
     },
    "Negative future": {
        "default": "negative future",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "negative future"
     },
    "Positive subjunctive": {
        "default": "positive subjunctive",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "positive subjunctive"
     },
    "Negative subjunctive": {
        "default": "negative subjunctive",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "negative subjunctive"
     },
    "Positive present conditional": {
        "default": "positive present irrealis",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "positive present irrealis"
     },
    "Negative present conditional": {
        "default": "negative present irrealis",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "negative present irrealis"
     },
    "Positive past conditional": {
        "default": "positive past irrealis",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "positive past irrealis"
     },
    "Negative past conditional": {
        "default": "negative past irrealis",
        "lang": "Swahili",
        "nested-table-depth": [1, 2],
        "then": "negative past irrealis"
     },

    "transgressive": "transgressive",  # darovať/Slovak
    # conocer/Asturian
    "gerundive": "gerund",

    "case \ number": "",  #δίκυκλο/Greek
    "number case \ gender": "",  #απύρωτος/Greek
    "conditional 2nd form": "conditional conditional-ii",  #costosir/Occitan

    #konyugön/Volapük
    "2nd person polite singular": "second-person singular polite",
    "3rd person male singular": "third-person masculine singular",
    "3rd person female singular": "third-person singular feminine",
    "reflexive singular": "reflexive singular",
    "reciprocative singular": "reciprocal singular",
    "2nd person polite plural": "second-person polite plural",
    "3rd person male plural": "third-person masculine plural",
    "3rd person female plural": "third-person feminine plural",
    "reflexive plural": "reflexive plural",
    "reciprocative plural": "reciprocal plural",
    "future in the past perfect": "past perfect future",

    #райҳон/Tajik
    "bare": "",  
    "definite object": "definite direct-object",

    #brestan/Proto-West Germanic
    "Genitive infin.": "genitive infinitive",
    "Dative infin.": "dative infinitive",
    "Instrum. infin.": "instrumental infinitive",

    #sberegar/Venetian
    "eło / eła": "third-person singular",
    "noialtri / noialtre": "first-person plural",
    "voialtri / voialtre": "second-person plural",
    "łuri / łore": "third-person plural",
    "che mi": "first-person singular subjunctive",
    "che eło / eła": "third-person singular subjunctive",
    "che noialtri / noialtre": "first-person plural subjunctive",
    "che voialtri / voialtre": "second-person plural subjunctive",
    "che łuri / łore": "third-person plural subjunctive",

    #qolmoq/Uzbek
    "1": {
        "default": "first-person",
    },
    "2": {
        "default": "second-person",
    },
    "cont A": "continuative",
    "cont B": "continuative formal imperfective",
    "cont C": "continuative habitual",
    
    #taanduma/Estonian
    "voice": "",

    "singular / indefinite": "singular indefinite",  #Өгэдэй/Mongolian/668

    # Proto-Finnic/munidak
    "passive connegative": "passive connegative",
    "infinitives/nouns": "",
    "infinitive 1": "infinitive infinitive-i",
    "infinitive 2": "infinitive infinitive-ii",
    "gerund/supine": "gerund supine",
    
    # glæþia/Old Swedish
    "þū": {
        "lang": "Old Swedish",
        "then": "second-person singular",
    },
    "vīr": {
        "lang": "Old Swedish",
        "then": "first-person plural",
    },
    "īr": {
        "lang": "Old Swedish",
        "then": "second-person plural",
    },
    "iæk": {
        "lang": "Old Swedish",
        "then": "first-person singular",
    },
    "han": {
        "lang": "Old Swedish",
        "then": "third-person singular",
    },
    "þēr": {
        "lang": "Old Swedish",
        "then": "third-person plural",
    },

    "Absolute superlative": "absolute superlative",  #τρανός/Greek

    # kolfino/Ternate
    "Inclusive": "inclusive plural",
    "Exclusive": "exclusive plural",
    "Human m": "human-person masculine",
    "Human f": "human-person feminine",
    "Non-human": "non-human",

    # ntw/Eqyptian
    "suffix pronouns": "suffix pronoun",
    "stative (‘pseudoparticiple’) endings": "stative",
    "enclitic (‘dependent’) pronouns": "enclitic pronoun", 
    "stressed (‘independent’) pronouns": "stressed pronoun",
    "proclitic (‘subject form’) pronouns": "proclitic pronoun",

    #райҳон/Tajik
    "indefinite, definite relative": "indefinite definite relative",

    "mixed after th": "after-th mutation-mixed",  #wenyn/Cornish
    
    "feminine gender": "feminine",  #heiße Zitrone/German
    "masculine gender": "masculine",  #alter Drache/German
    "specific": "specific",  #পূঁজ/Assamese
    "not specific": "unspecified",  #পূঁজ/Assamese/163

    
    #навохтан/Tajik
    "ман": "first-person singular",
    "ӯ": "third-person singular",
    "мо": "first-person plural",
    "шумо": ["second-person plural",
             "second-person singular polite"],
    "онҳо": "third-person plural",
    
    "минем (“my”)": "first-person singular possessive",  #сез/Tatar
    "синең (“your”)": "second-person singular possessive",
    "аның (“his/her/it”)": "third-person singular possessive",
    "безнең (“our”)": "first-person plural possessive",
    "сезнең (“your”)": "second-person plural possessive",
    "аларның (“their”)": "third-person plural possessive",

    "Realis mood": "realis",  #weyetun/Mapudungun
    "singular or plural": ["singular", "plural",],  #aبڑھنا/Urdu
    "iek": {  #ongelje/Saterland Frisian
        "lang": "Saterland Frisian",
        "then": "first-person singular",
    },
    
    #wenschen/Middle Dutch
    "In genitive": { "lang": "Middle Dutch", "then": "infinitive genitive", },
    "In dative": { "lang": "Middle Dutch", "then": "infinitive dative", },
    # ongelje/Saterland Frisian
    "hie/ju/dät": "third-person singular",
    "wie": { "lang": "Saterland Frisian", "then": "first-person plural", },
    "du": { "lang": "Saterland Frisian", "then": "second-person singular", },

    # यहाँका/Nepali
    "Low": {
        "lang": "Nepali",
        "then": "impolite",
    },
    "Mid": {
        "lang": "Nepali",
        "then": "polite",
    },
    "Low/Mid": {
        "lang": "Nepali",
        "then": "impolite polite",
    },
    "High": {
        "lang": "Nepali",
        "then": "deferential",
    },
    "izofa": "ezafe",  # райҳон/Tajik
    "ezâfe": "ezafe",  #a دریچه/Persian

    "adverbs": "adverb",  # tꜣj/Egyptian
    "Equative": "equative",  # erk/Proto-Turkic
    "Pres. subjunctive": "present subjunctive",  # adkʷiseti/Proto-Celtic
    "Inclusive Tri-Plural": "inclusive tri-plural",  #aaombiniili'/Chickasaw
    "1st-person dual": "first-person dual",  #ferkuupe/North Frisian
    "2nd-person dual": "second-person dual",  #ferkuupe/North Frisian

    #coymaq/Crimean Tatar
    "repeated gerund": "gerund repeated",  
    "temporal gerund": "temporal gerund",
    "non-future participle": "present past participle",

    # tussenin/Dutch
    "postpositional adv.": "adverb postpositional",

    #védde/Ligurian
    "lê o/a": "third-person singular",  
    "noî, niâtri": "first-person plural", 
    "voî, viâtri": "second-person plural", 
    "lô, liâtri": "third-person plural",
    "che ti": "second-person singular subjunctive",  
    "che lê o/a": "third-person singular subjunctive",  
    "che noî, che niâtri": "first-person plural subjunctive", 
    "che voî, che viâtri": "second-person plural subjunctive", 
    "che lô, che liâtri": "second-person plural subjunctive",

    "હું": "first-person singular",  #અવતરવું/Gujarati/92
    "અમે, આપણે": "first-person plural",  #અવતરવું/Gujarati/184
    "તું": "second-person singular",  #અવતરવું/Gujarati/184
    "તમે": "second-person plural",  #અવતરવું/Gujarati/184
    "તું, આ, આઓ, તે, તેઓ": "third-person",  #અવતરવું/Gujarati/92
    
    "marked indefinite or relative definite": [   #a دریچه/Persian
        "stressed indefinite",
        "relative definite",
    ],

    #delegher/Ladin
    "el / ela": "third-person singular",  
    "ei / eles": "third-person plural",
    "che ie": "first-person singular subjunctive",  
    "che el / ela": "third-person singular subjunctive",
    "che nos": "first-person plural subjunctive", 
    "che vos": "second-person plural subjunctive", 
    "che ei / eles": "third-person plural subjunctive",

    "preposition": "prepositional",  #daarmede/Dutch
    
    "Prolative II": "prolative prolative-ii",  #килең/Tuvan

    # pawjō/Proto-Italic
    "Perfect indicative": "perfect indicative",
    "Present imperative": "present imperative",  
    "Future imperative": "future imperative",  
    "tu-derivative": "tu-derivative",  
    "s-derivative": "s-derivative",

    #weyetun/Mapudungun
    "Tense particles (See particles)": "particle", 
    "iñce": "first-person singular",
    "eymi": "second-person singular",
    "fey": "third-person singular", 
    "iñciw": "first-person dual",
    "eymu": "second-person dual", 
    "feygu": "third-person dual",
    "iñciñ": "first-person plural",
    "eymvn": "second-person plural",
    "feygvn": "third-person plural",

    "attributive": "attributive",  #Өгэдэй/Mongolian/167
    
    "Active indicative": "indicative active",  #konyugön/Volapük/166
    "Active subjunctive": "subjunctive active",  #konyugön/Volapük/166
    "Active optative": "optative active",  #konyugön/Volapük/166
    "Active interrogative": "interrogative active",  #konyugön/Volapük/166
    "Active jussive": "jussive active",  #konyugön/Volapük/166
    
    "definitive direct object": "direct-object definite",  #دریچه/Persian/154

    "preceding noun": "before-noun",  #jenöfik/Volapük/151
    "separated": "without-noun",  #jenöfik/Volapük/151
    
    "temp. dist.": "temporal distributive",  #sisässä/Finnish/145
    "oblique/vocative/instrumental": "oblique vocative instrumental",  #કેટલું/Gujarati
    "I-stem (Passive)": "passive",  #सोहोर्नु/Nepali/144
    
    "Passive indicative": "passive indicative",  #konyugön/Volapük
    "Passive subjunctive": "passive subjunctive",
    "Passive optative": "passive optative",
    "Passive interrogative": "passive interrogative",  
    "Passive jussive": "passive jussive",
    
    "unmodified": "without-modifier",  #birciqqo/Sidamo
    "modified": "with-modifier",  #birciqqo/Sidamo

    "Past/present inchoative": "past present inchoative",  #ganansiya/Cebuano
    "Future/habitual inchoative": "future habitual inchoative",
    
    "el / ela / Vde": "third-person singular",  #aterecer/Galician
    "eles / elas / Vdes": "third-person plural",  #aterecer/Galician
    
    "busatros busatras": "second-person plural",  #foratar/Aragonese
    "agentive / prospective": "agentive prospective",  #a بڑھنا/Urdu

    "мен": "first-person singular",  #чылгаар/Tuvan
    "бис": "first-person plural",
    "силер": "second-person plural",
    "ол": "third-person singular",
    "олар": "third-person plural",
    "-лар": "third-person plural", 
    "Past II": "past past-ii",
    "Evidential": "evidential", 
    "-тар": "third-person plural",
    "-нар": "third-person plural",
    "-лер": "third-person plural",  #дээр/Tuvan
    "-тер": "third-person plural",
    "-нер": "third-person plural",

    "Grúundfoarme": "",  #ongelje/Saterland Frisian

    #oh-/Choctaw/124
    "+V": { "lang": "Choctaw",
            "then": "before-vowel", },
    "+C": { "lang": "Choctaw",
            "then": "before-consonant", },
    "+s": { "lang": "Choctaw",
            "then": "before-s", },
    "+C/i": { "lang": "Choctaw",
            "then": "before-consonant before-front-vowel", },
    "+a/o": { "lang": "Choctaw",
            "then": "before-back-vowel", },
    # +s 	+C 	+V 	+C/i 	+a/o 	+C 	+V 	+C 	+V 	+C 	+V
            
    "past subjunctive": "past subjunctive",  #شباهت داشتن/Persian/120

    "vus": "second-person plural",  #cumprar/Romansch/117
    "nus": "first-person plural",  
    "jeu": "first-person singular",
    "el/ella": "third-person singular",
    "els/ellas": "third-person plural",
    "che nus": "first-person plural subjunctive", 
    "che vus": "second-person plural subjunctive", 
    "ch'els/ch'ellas": "third-person plural subjunctive",
    "che jeu": "first-person singular subjunctive",
    "ch'el/ch'ella": "third-person singular subjunctive",
    "direct future": "direct future",  
    "indirect future": "indirect future",

    "unmarked": "",  #tꜣj/Egyptian/114

    "Conditional mood": "conditional",  #weyetun/Mapudungun/112
    "Volitive mood": "volitive",  #weyetun/Mapudungun/112

    "distant": "distal",  #тұту/Kazakh/110
    
    "affirmative commands": "imperative",  #ፈተለ/Tigrinya/110
    "negative commands": "negative imperative",
    
    '1st-person ("my, our")': "first-person possessive",  #aaombiniili'/Chickasaw/106
    '2nd-person ("thy, your")': "second-person possessive",
    '3rd-person ("his, her, its, their")': "third-person possessive", 
    "je (nos)": "first-person",  #cogier/Norman/104
    "Agentive": "agentive",  #হাঁঠ/Assamese/102
    "Middle voice": "middle-voice",  #ḱléwseti/Proto-Indo-European/100
    "1st-person (I, we)": "first-person",  #chaaha̱ taloowa/Chickasaw/99
    "2nd-person (you, you all)": "second-person", 
    "3rd-person (he, she, it, they)": "third-person", 
    "ils": "third-person plural",  #ovrar/Franco-Provençal/98
    "que je (j')": "first-person singular subjunctive", 
    "que te (t')": "second-person singular subjunctive",
    "qu'il/el": "third-person singular subjunctive",
    "qu'ils/els": "third-person plural subjunctive",
    "il/elli": "third-person singular",
    "Nasal": "mutation-nasal",  #arglwyt/Middle Welsh/98
    "Present progressive": "present progressive",  #અવતરવું/Gujarati/92
    "Negative conditional": "negative conditional",

    "pronoun": "pronoun",  #küm-/Maquiritari/88
    "noun possessor/ series II verb argument":
        ["possessive",
         "series-ii-verb-argument",],
    "series I verb argument":
         "series-ii-verb-argument",
    "postposition object": "direct-object postpositional",
    "transitive patient": "transitive patient",
    "intransitive patient-like": "intransitive patient-like",
    "intransitive agent-like": "intransitive agent-like",
    "transitive agent": "transitive agent",
    "first person dual inclusive": "first-person dual inclusive",
    "first person dual exclusive": "first-person dual exclusive",
    "distant past third person": "distant-past past",
    "coreferential/reflexive": "reflexive",
    "series I verb argument: transitive agent and transitive patient":
        "transitive agent patient",
    "first person > second person": "first-person object-second-person",
    "first person dual exclusive > second person":
        "first-person dual exclusive object-second-person",
    "second person > first person": "second-person object-first-person",
    "second person > first person dual exclusive":
        "second-person object-first-person object-dual object-exclusive",
    "third person > any person X …or… any person X > third person":
        ["third-person", "object-third-person"],
    
    "2nd Person Singular": "second-person singular",  #spigen/Middle Low German
    "él": "third-person singular",  #foratar/Aragonese
    "nusatros nusatras": "first-person plural",
    "ellos/els ellas": "third-person plural", 
    "Conjectural": "",  #노타/Middle Korean/85
    "transgressive present": "present transgressive",  #naposlouchat/Czech
    "transgressive past": "past transgressive",
    "Verbal adjective": "adjective-from-verb", 
    "je (j’) / i": "first-person singular",  #gizai/Bourguignon/81
    "je (j') / i": "first-person singular",  #antreprarre/Bourguignon/79
    "que je (j') / qu'i": "first-person singular subjunctive",
    "que je (j’) / qu'i": "first-person singular subjunctive",
    "ai (el), ale": "third-person singular",  #gizai/Bourguignon/58
    "ai (el), ales": "third-person plural", 
    "qu'ai (el), qu'ale": "third-person singular subjunctive",
    "qu'ai (el), qu'ales": "third-person plural subjunctive",

    "determiners and pronouns": "determiner pronoun",  #tꜣj/Egyptian/76
    "anaphoric": "anaphoric",
    
    "regular": "",  #এৱা গাখীৰ/Assamese/74
    "very formal": "deferential",
    
    "infinitive II": "infinitive-ii infinitive",  #ferkuupe/North Frisian
    "PROGRESSIVE": "progressive",  #yitih/Navajo
    "past stem": "stem past",  #a شباهت داشتن/Persian
    "nominative, genitive and instrumental":
        "nominative genitive instrumental",   #ხმოვანი/Georgian

    "ej (j')": "first-person singular",  #vouloér/Picard
    "tu (t')": "second-person singular",
    "i (il)/ale": "third-person singular",  #vouloér/Picard
    "i (il)/a (al)": "third-person singular",  #ète/Picard/1
    "(n)os": "first-person plural",  #vouloér/Picard/60
    "os": "second-person plural",  #vouloér/Picard
    "is": "third-person plural",  #vouloér/Picard/31
    "qu'ej (j')": "first-person singular subjunctive",  #vouloér/Picard/31
    "qu'tu (t')": "second-person singular subjunctive",
    "eq tu (t')": "second-person singular subjunctive",  #ète/Picard/1
    "qu'i (il)/ale": "third-person singular subjunctive",  #connoéte/Picard/29
    "qu'i (il)/a (al)": "third-person singular subjunctive",  #vouloér/Picard/2
    "qu'(n)os": "first-person plural subjunctive",  #connoéte/Picard/29
    "qu'os": "first-person second-person plural subjunctive",  #vouloér/Picard/33
    "qu'is": "third-person plural subjunctive",  #vouloér/Picard/31

    "inanimate pronoun": "inanimate pronoun",  #mönsemjo/Maquiritari
    "medial": "medial",

    "unmarked (later)": "",  #ntw/Egyptian singular/plural/unmarked
    "H-prothesis": "prothesis-h",  #arglwyt/Middle Welsh/61
    "h-prothesis": "prothesis-h",  # moved here, uncommented

    "distant past": "distant-past past",  #weyetun/Mapudungun/56

    # XXX Tatar has a ton of soft hyphens
    "Futu\xadre": "future",  #!! soft hyphen! тыңларга/Tatar
    "Nonfinite verb forms": "",
    
    "transitory past": "past transitional-past",  #тұту/Kazakh
    "сен": {
        "lang": "Kazakh",
        "then": "second-person singular informal",
        "else": {
            "lang": "Tuvan",
            "then": "second-person singular",
        },
    },
    "сіз": "second-person singular formal",
    "біз": "first-person plural",
    "сендер": "second-person plural informal",
    "сіздер": "second-person plural formal",
    "imperative/hortative": "imperative hortative",

    "gend/num": "",  #vascuenciu/Asturian/54

    "inf": "infinitive",  #হাঁঠ/Assamese/54

    "ca je/i'": "first-person singular subjunctive",  #spantacà/Neapolitan
    "ca tu": "second-person singular subjunctive",
    "ca nuje": "first-person plural subjunctive",
    
    "il, alle, nos": "third-person singular",  #cogier/Norman/52
    "il, alles": "third-person plural", 
    "qu'il, qu'alle, que nos": "third-person singular subjunctive",
    "que je (que nos)": "first-person plural subjunctive",
    "qu'il, qu'alles": "third-person plural subjunctive",

    # Get yourself together, Sardinian
    "deo": "",  #nochere/Sardinian/52
    "deo, eo": "",  #tzappare/Sardinian/51
    "dego, deo": "",  #tzappare/Sardinian/33
    "isse/issa": "",  #nochere/Sardinian/27
    "chi deo, chi eo": "",  #tzappare/Sardinian/17
    "chi deo": "",  #impreare/Sardinian/12
    "chi dego, chi deo": "",  #tzappare/Sardinian/11
    "che deo": "",  #nochere/Sardinian/8
    "che tue": "",  #nochere/Sardinian/8
    "che isse/issa": "",  #nochere/Sardinian/8
    "che nois": "",  #nochere/Sardinian/8
    "che bois": "",  #nochere/Sardinian/8
    "che issos/issas": "",  #nochere/Sardinian/8
    "issos/ issas": "",  #finire/Sardinian/4
    "eo, deo": "",  #finire/Sardinian/3
    "deu": "",  #essi/Sardinian/3
    "tui": "",  #essi/Sardinian/3
    "nosu": "",  #essi/Sardinian/3
    "bosatrus/bosatras": "",  #essi/Sardinian/3
    "issus/issas": "",  #essi/Sardinian/3
    "past/ imperfect": "",  #finire/Sardinian/2
    "+ past participle": "",  #pòdere/Sardinian/2
    "isse/ issa": "",  #finire/Sardinian/1
    "chi deu": "",  #essi/Sardinian/1
    "chi tui": "",  #essi/Sardinian/1
    "chi nosu": "",  #essi/Sardinian/1
    "chi bosatrus/bosatras": "",  #essi/Sardinian/1
    "chi issus/issas": "",  #essi/Sardinian/1

    
    "Verbs beginning with a consonant.": "",  #chaaha̱ taloowa/Chickasaw/52

    "te": "second-person singular",  #ovrar/Franco-Provençal
    "nu": "first-person plural",  #legro/Dalmatian
    "vu": "second-person plural",
    "Perfekta": "perfect",  #sannoa/Ingrian/50
    "Nouns in vowel-, b-, or p-": "",  #aaombiniili'/Chickasaw/50
    "subjunctive present": "present subjunctive",  #a متشکر بودن/Persian/48

    "1st Person Singular": "first-person singular",  #spigen/Middle Low German
    "3rd Person Singular": "third-person singular",

    "Rewş": "",  # "case", kerguh/Northern Kurdish
    "Vde": "third-person singular",  #aterecer/Galician
    "Vdes": "third-person plural",  
    "IMPF": "imperfect",  #डिलीट होना/Hindi
    "frm": "",  # ??? "form"? হাঁঠ/Assamese
    "focus": "focus",  #issito/Choctaw
    "singular 1ˢᵗ person": "first-person singular",  #гъэкӏодын/Adyghe
    "singular 2ˢᵗ person": "second-person singular",
    "singular 3ˢᵗ person": "third-person singular",
    "plural 1ˢᵗ person": "first-person plural",
    "plural 2ˢᵗ person": "second-person plural",
    "plural 3ˢᵗ person": "third-person plural",
    "Neuter gender": "neuter",  #𒄭𒅔𒃷/Hittite

    "Plain Infinitive": "infinitive",  #spigen/Middle Low German
    "Full Infinitive (Gerund)": "gerund infinitive", 
    "Imperatives": {
        "default": "imperative",
        "lang": "Swahili",
        "then": "dummy-section-header imperative",
    },
    "Tensed forms": {
        "default": "",
        "lang": "Swahili",
        "then": "dummy-reset-section-header",
    },
    "Object concord (indicative positive)": {
        "default": "object-concord indicative positive",
        "lang": "Swahili",
        "then": "dummy-section-header object-concord indicative positive",
    },
    "Relative forms": {
        "default": "",
        "lang": "Swahili",
        "then": "dummy-section-header relative object-concord",
    },
    "2nd Person Plural": "second-person plural",
    "free state": "free-state",  #aɣemmar/Tarifit
    "construct state": "construct",
    "dative/instr": "dative instrumental",  #unseraz/Proto-Germanic/39

    "infinitive III": "infinitive infinitive-iii",  #stärwe/North Frisian
    "determiners": "determiner",  #nꜣyw/Egyptian/38
    "pronouns": "pronoun",  
    "proximal to speaker": "proximal-to-speaker",
    "proximal to spoken of": "proximal-to-topic",
    "‘copula’": "copulative",
    "possessive determiners (used with suffix pronouns)":
            "possessive determiner",
    "relational pronouns (‘possessive prefixes’)": "possessive pronoun",
    "definite articles": "definite article",
    "indefinite articles": "indefinite article",

    "Aspirate": "mutation-aspirate",  #vynet/Middle Welsh/37
    "dji (dj')": "first-person singular",  #atchter/Walloon/37
    "preterit": "preterite",  
    "dji / nos": "first-person plural", 
    "nós nós outros nós outras": "first-person plural",  #prazer/Old Portuguese
    "vós vós outros vós outras": "second-person plural",
    
    "contrastive": "contrastive",  #issito/Choctaw/36

    #espurrire/Leonese
    "you": { "lang": "Leonese", "then": "first-person singular", },
    "él / eilla / eillu / vusté": "third-person singular", 
    "nosoutros / nosoutras": "first-person plural", 
    "vosoutros / vosoutras": "second-person plural",
    "eillos / eillas / vustedes": "third-person plural",

    "Personal-pronoun including forms": "",  #ܓܘ/Assyrian Neo-Aramaic/36
    "Non-personal-pronoun-including form": "",  #במו/Hebrew/35

    #pårler/Walloon
    "i (il) / ele": "third-person singular",
    "dji (dj') / nos": "first-person plural", 
    "ki dj'": "first-person singular subjunctive",
    "ki t'": "second-person singular subjunctive",
    "k' i (il) / k' ele": "third-person singular subjunctive",
    "ki dj' / ki nos": "first-person plural subjunctive",
    "ki vos": "second-person plural subjunctive",
    "k' i (il)": "third-person plural subjunctive",

    # sannoa/Ingrian, rest of these
    "Imperfekta": "imperfect",
    "Pluskvamperfekta": "pluperfect",
    "Infinitivat": "infinitive",
    "Partisipat": "participle",
    
    # f/Slovene
    "nominative imenovȃlnik": "nominative",
    "genitive rodȋlnik": "genitive",
    "dative dajȃlnik": "dative",
    "accusative tožȋlnik": "accusative",
    "locative mẹ̑stnik": "locative",
    "instrumental orọ̑dnik": "instrumental",
    "(vocative) (ogȏvorni imenovȃlnik)": "vocative",

    # akaka/Choctaw
    "Possession": "possessed-form",
    '("my, our")': "first-person possessive",
    '("thy, your")': "second-person possessive",
    '("his, her, its, their")': "third-person possessive",

    # humingi/Tagalog
    # Why is there \u2060 in so many differen tagalog templates like these???
    "\u2060 ma- -an": "",
    "\u2060mapag- -an": "",
    "\u2060 mapa- -an": "",
    "\u2060mapagpa- -an": "",
    "\u2060mapapag- -an": "",
    # katayin/Tagalog
    "\u2060mapapag-": "",


    # -nən/Azerbaijani floating div! Got it to work!
    "preceding vowel": "",
    "A / I / O / U": "back-vowel-harmony",
    "E / Ə / İ / Ö / Ü": "front-vowel-harmony",
    "postconsonantal": "after-consonant",
    "postvocalic": "after-vowel",
    # -ül/Azerbaijani
    "A / I": "back-vowel-harmony unrounded-harmony",
    "E / Ə / İ": "front-vowel-harmony unrounded-harmony",
    "O / U": "back-vowel-harmony rounded-harmony",
    "Ö / Ü": "front-vowel-harmony rounded-harmony",
    "postconsonantal except after L": "after-consonant-except-l",
    "after L": "after-l-consonant",
    # kk-suffix-forms Kazakh
    "А / Ы / О / Ұ": "back-vowel-harmony",
    "Ә / Е / І / Ө / Ү": "front-vowel-harmony",
    # ky-suffix-forms Kyrgyz
    "А / Ы": "back-vowel-harmony unrounded-harmony",
    "Е / И": "front-vowel-harmony unrounded-harmony",
    "О / У": "back-vowel-harmony rounded-harmony",
    "Ө / Ү": "front-vowel-harmony unrounded-harmony",
    # tr-inf-p Turkish
    "E / İ": "front-vowel-harmony unrounded-harmony",
    # tt-suffix-forms Tatar
    "А / Ы / О / У": "back-vowel-harmony",
    "Ә/ Е / Э / Ө / Ү": "front-vowel-harmony",

}


def check_tags(k, v):
    assert isinstance(k, str)
    assert isinstance(v, str)
    for tag in v.split():
        if tag not in valid_tags and tag not in ("*",):
            print("infl_map[{!r}] contains invalid tag {!r}"
                  .format(k, tag))


def check_v(k, v):
    assert isinstance(k, str)
    if v is None: # or v in ("dummy-reset-headers",):
        return
    if isinstance(v, str):
        check_tags(k, v)
    elif isinstance(v, list):
        for item in v:
            check_v(k, item)
    elif isinstance(v, dict):
        for kk in v.keys():
            if kk in ("if", "then", "else",):
                check_v(k, v[kk])
            elif kk == "default":
                if not isinstance(v[kk], (str, list, tuple)):
                    print("infl_map[{!r}] contains invalid default value "
                                  "{!r}".format(k, v[kk]))
            elif kk == "pos":
                vv = v[kk]
                if isinstance(vv, str):
                    vv = [vv]
                for vvv in vv:
                    if vvv not in PARTS_OF_SPEECH:
                        print("infl_map[{!r}] contains invalid part-of-speech "
                              "{!r}".format(k, kk, v[kk]))
            elif kk in ("lang",):
                pass
            elif kk == "nested-table-depth":
                if not isinstance(v[kk], (int, list, tuple)):
                    print("infl_map[{!r}] contains invalid depth-value "
                                "{!r}".format(k, v[kk]))
            elif kk == "inflection-template":
                if not isinstance(v[kk], (str, list, tuple)):
                    print("infl_map[{!r}] contains invalid"
                          "inflection-template value "
                                "{!r}".format(k, v[kk]))
            else:
                print("infl_map[{!r}] contains invalid key {!r}"
                      .format(k, kk))
    else:
        print("infl_map[{!r}] contains invalid value {!r}"
              .format(k, v))


for k, v in infl_map.items():
    check_v(k, v)


# Mapping from start of header to tags for inflection tables.  The start must
# be followed by a space (automatically added, do not enter here).
infl_start_map = {
    "with infinitive": "infinitive",
    "with gerund": "gerund",
    "with informal second-person singular imperative":
    "informal second-person singular imperative",
    "with informal second-person singular tú imperative":  # cedular/Spanish
    "informal second-person singular imperative with-tú",
    "with informal second-person singular vos imperative":
    "informal second-person singular imperative with-vos",
    "with formal second-person singular imperative":
    "formal second-person singular imperative",
    "with first-person plural imperative":
    "first-person plural imperative",
    "with informal second-person plural imperative":
    "informal second-person plural imperative",
    "with formal second-person plural imperative":
    "formal second-person plural imperative",
    # kaozeal/Breton
    "Soft mutation after": "mutation-soft",
    "Mixed mutation after": "mutation-mixed",
    # gláedach/Old Irish
    "Initial mutations of a following adjective:": "dummy-skip-this",
}
for k, v in infl_start_map.items():
    check_v(k, v)

infl_start_re = re.compile(
    r"^({}) ".format("|".join(re.escape(x) for x in infl_start_map.keys())))

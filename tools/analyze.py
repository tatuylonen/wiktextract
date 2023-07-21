# XXX temporary tool for evaluating contents of database dumps

import re
import sys
import json
import collections

known_data_keys = {
    "abbreviations",
    "alternate",
    "antonyms",
    "categories",
    "compounds",
    "conjugation",
    "derived",
    "enum",
    "heads",
    "hiragana",
    "hypernyms",
    "hypernym",  # XXX remove this, or check zh-div
    "hyphenation",
    "hyponyms",
    "isbn",
    "lang",
    "pos",
    "pronunciations",
    "related",
    "senses",
    "synonyms",
    "topics",
    "translations",
    "word",
}

known_sense_keys = {
    "agent_of",
    "alt_of",
    "classifier",
    "color",
    "complex_inflection_of",
    "derived_from",
    "examples",
    "form_of",
    "glosses",
    "holonyms",
    "hypernyms",
    "inflection_of",
    "kyujitai_spelling",
    "morse_code",
    "nonglosses",
    "object_preposition",
    "only_in",
    "origin",
    "pron1",
    "pron2",
    "sort",
    "suffix",
    "tags",
    "taxon",
    "topics",
    "unit",
    "wikidata",
    "wikipedia",
}

lingform_tags = {
    "1",
    "2",
    "3",
    "plural",
    "singular",
    "present",
    "past",
    "perfect",
    "perfective",  # XXX
    "imperfect",
    "imperfective",  # XXX canonicalize to imperfect?
    "pluperfect",
    "negative",
    "connegative",
    "future",
    "modal",
    "auxiliary",
    "modal auxiliary verb",  # XXX
    "augmentative",
    "imperative",
    "imperative only",  # XX
    "conditional",
    "indicative",
    "preterite",
    "affirmative",
    "subjective",
    "objective",
    "aorist",
    "semelfactive",
    "iterative",
    "copulative",
    "causative",
    "optative",
    "hortative",
    "desirative",
    "evaluative",
    "depreciative",
    "expletive",
    "catenative",
    "passive",
    "passive form",  # XXX
    "passive voice",  #XXX
    "passive sense",  #XXX
    "in a passive sense",  # XXX
    "mediopassive",
    "in mediopassive",  # XXX
    "active",
    "active verb",  # XXX
    "active voice",  # XXX
    "in active",  # XXX
    "active sense",  # XXX
    "middle",
    "middle voice",
    "in middle",
    "in the middle voice",
    "potential",
    "participle",
    "participle-past",  # XXX canonicalize to ["participle", "past"]
    "participle-pres",  # XXX canonicalize to ["participle", "present"]
    "participle-agnt",  # XXX canonicalize to something
    "participle-nega",  # XXX canonicalize to something
    "participle-past_pasv",  # XXX canonicalize
    "participle-pres_pasv",  # XXX canonicalize
    "infinitive",
    "infinitive-2a",
    "infinitive-2p",
    "infinitive-3a",
    "infinitive-3p",
    "infinitive-4",
    "stative",
    "absolute",
    "nominative",
    "nominative form",
    "genitive",
    "possessive",
    "accusative",
    "accusative (partitive-accusative)",  # XXX
    "dative",
    "essive",
    "partitive",
    "translative",
    "inessive",
    "elative",
    "illative",
    "adessive",
    "ablative",
    "allative",
    "abessive",
    "comitative",
    "instructive",
    "locative",
    "vocative",
    "instrumental",
    "feminine",
    "masculine",
    "neuter",
    "formal",
    "formally",  # XXX canonicalize?
    "informal",
    "polite",
    "humble",
    "definite",
    "indefinite",
    "hypercorrect",
    "comparative",
    "superlative",
    "attributive",
    "attributively",  # XXX canonicalize
    "attributive usage",  # XXX
    "predicative",
    "used only predicatively",  # XXX canonicalize
    "predicative only",  # XXX canonicalize
    "non-attributive",  # XXX
    "used as a predicative noun",   # XXX canonicalize
    "derogatory",
    "diminutive",
    "endearing",  # XXX should this be combined with diminutive?
    "affectionate",  # XXX canonicalize?
    "hypocoristic",
    "pejorative",  # XXX canonicalize to "offensive"?
    "pejoratively",  # XXX
    "derogative",  # XXX
    "offensive",
    "racial slur",  # XXX canonicalize to "offensive"?
    "ethnic slur",  # XXX canonicalize
    "impolite",  # XXX canonicalize to offensive
    "offensive slang",  # XXX canonicalize to both offensive and slang
    "dismissive",  # XXX canonicalize to offensive?  XXX check
    "subjunctive",
    "subordinate",
    "supine",
    "humorous",
    "satirical",  # XXX canonicalize
    "jocular",  # XXX canonicalize
    "sarcastic",  # XXX canonicalize?
    "ironic",  # XXX canonicalize?
    "archaic",
    "archaic form",
    "obsolete",
    "obsolete form",  # XXX canonicalize to obsolete
    "obsolescent",  # XXX canonicalize to obsolete?
    "dialectical",
    "dialect",   # XXX canonicalize to dialectical
    "dialectal",  # XXX canonicalize to dialectical
    "dialectal form",  # XXX canoncialize
    "eye dialect",
    "slang",
    "misconstructed",
    "colloquial",
    "colloquialism",  # XXX canonicalize
    "synonym",
    "alternative_spelling",
    "standard_spelling",
    "nonstandard",  # XXX Should this be normalize to "alternative_spelling"
    "non-standard",  # XXX Should this be normalized to "alternative_spelling"?
    "misspelling",
    "erroneous",  # XXX normalize to misspelling, but check what these are
    "misconstruction",  # XXX normalize
    "misconstructed",  # XXX normalize
    "abbreviation",
    "initialism",  # XXX normalize to abbreviation?
    "vulgar",
    "coarse",
    "spoken",
    "literal",  # XXX normalize to something?
    "literally",  # XXX seems to indicate literal translations
    "literary",
    "academic",  # XXX normalize to literary?
    "countable",
    "uncountable",
    "comparable",  # XXX check which words have this, cf. comparative
    "uncomparable",
    "not comparable",  # XXX canonicalize to uncomparable
    "ergative",
    "transitive",
    "intransitive",
    "ditransitive",
    "ambitransitive",
    "poetic",
    "euphemistic",
    "euphemism",  # XXX normalize to euphemistic
    "uncommon",
    "rare",
    "rare form",  # XXX canonicalize to rare
    "obscure",  # XXX canonicalize to rare
    "neologism",
    "onomatopoeia",
    "ideophonic",  # XXX canonicalize to onomatopoeia?
    "irregular",
    "regional",  # XXX check
    "proscribed",
    "historical",  # XXX normalize to archaic
    "historic",  # XXX normalize to archaic
    "pseudo-archaic",  # XXX normalize to archaic
    "reflexive",
    "reflexive pronoun",  # normalize to reflexive
    "plural only",
    "in plural",  # XXX normalize to plural only
    "pluralonly",  # XXX normalize to plural only
    "singulare tantum",  # XXX normalize to singular only?
    "plurale tantum",  # XXX normalize to plural only?
    "pluralized",  # XXX normalize to plural only
    "always plural",  # XXX normalize
    "plural noun",  # XXX canonicalize
    "translation_hub",
    "postpositive",
    "hyperbole",  # XXX check where this is used
    "figurative",
    "figuratively",  # XXX canonicalize
    "by extension",  # XXX
    "metaphorical",  # XXX canonicalize with figurative?
    "metaphoric",  # XXX canonicalize to figurative?
    "metaphor",  # XXX canonicalize
    "by analogy",  # XXX canonicalize to figurative?
    "by ellipsis",
    "metonym",
    "metonymy",  # XXX camonicalize to metonym?
    "by metonymy",  # XXX canonicalize
    "metonymic",  # XXX canonicalize
    "emphatic",
    "collective",  # XXX check where this is used
    "collectively",   #XXX
    "collective noun",  #XXX
    "frequentative",
    "distributive",
    "capitalized",  # XXX seems to be "often capitalized"
    "childish",
    "impersonal",
    "physical",  # XXX where used?
    "social",  # XXX where used?
    "abstract",
    "abstract noun",
    "honorific",
    "idiomatic",
    "idiom",  # XXX canonicalize to idiomatic
    "provincial",
    "hyphenated",
    "hyphenated when used attributively",  # XXX normalize
    "surname",
    "given_name",
    # XXX broad categories of things
    "person",
    "place",
    "organism",
    "unit-of-measurement",
    "inanimate",
    "animate",
    "in combination",  # XXX check
    "especially in combination",  # XXX check, canonicalize?
    "in combinations",  # XXX check, canonicalize?
    "pron-compound",
    "rhetoric",   # XXX check, this might be a topic or a mix
    "rhetorical question",  # XXX check, is this same as rhetoric???
    "conjunctive",  # XXX this largely needs to be determined from topics
    "disjunctive",  # XXX
    "substantive",  # XXX should really change part-of-speech?
    "noun",   # XXX canonicalize to substantive?
    "as a noun",  # XXX canonicalize
    "used as a noun",  # XXX canonicalize?
    "verbal noun",
    "locative noun",  # XXX check
    "proper noun",  # XXX check
    "mass noun",  # XXX canonicalize (uncountable)
    "adjective",  # XXX should really change part-of-speech?
    "adjectival",  # XXX canonicalize to adjective?
    "as an adjective",  # XXX canonicalize to adjective?
    "adjectival usage",  # XXX canonicalize to adjective?
    "pronoun",   # XXX should affect part-of-speech?
    "demonstrative",
    "demonstrative pronoun",  # XXX canonicalize
    "relative",
    "possessive pronoun",  # XXX canonicalize to possessive?  part-of-speech?
    "personal pronoun",  #  XXX how to canonicalize?
    "reciprocal pronoun",  # XXX how to canonicalize?
    "interrogative",
    "interrogative pronoun",  # XXX canonicalize
    "indefinite pronoun",
    "definite pronoun",
    "indefinite personal pronoun",
    "first-person singular pronoun",  # XXX canonicalize
    "third-person feminine singular pronoun",  #XXX
    "first person singular pronoun",  #XXX
    "second-person singular pronoun",  #XXX
    "first person singular personal pronoun",
    "third-person feminine plural pronoun",
    "third-person masculine plural pronoun",
    "third-person masculine singular pronoun",
    "third-person plural pronoun",
    "third person masculine singular pronoun",
    "indefinite third-person singular pronoun",
    "first-person plural pronoun",
    "object pronoun",
    "bound object pronoun",
    "relative and indefinite pronoun",
    "personal pronouns",
    "reflexive-possessive pronoun",
    "substantive interrogative pronoun",
    "pronominal",  # XXX means: "takes reflexive pronoun"
    "adverbial",  # XXX check, pronominal means "takes reflexive pronoun"
    "adverb",  # XXX
    "as an adverb",  # XXX
    "ordinal adverbial",  # XXX
    "cardinal adverbial",  # XXX
    "adverbially",  # XXX
    "adverbial form",  # XXX
    "used adverbially",  # XXX
    "as adverb",  # XXX
    "demonstrative adverb",  # XXX canonicalize
    "sentential adverb",
    "verb",  # XXX part-of-speech?
    "verbal",  # XXX
    "impersonal verb",  # XXX
    "reflexive verb",   # XXX
    "false verb",  # XXX
    "classifier",
    "definite article",
    "indefinite article",
    "modal particle",
    "interrogative particle",
    "agent",
    "patient",
    "focus",
    "active/agent-focus",  # XXX
    "patient-focus",
    "relative/goal-focus",  # XXX
    "agent focus",
    "external/agent focus",
    "object_accusative",
    "object_dative",
    "object_genitive",
    "object_nominative",
    "object_instructive",
    "object_elative",
    "object_ablative",
    "defective",
    "eclipsis",
    "lenition",
    "prothesis",
    "singulative",
    "relational",
}

lingform_end_re = re.compile(r" (" + "|".join(lingform_tags) + ")$")

data_keys = collections.defaultdict(int)
sense_keys = collections.defaultdict(int)
topic_ht = collections.defaultdict(int)
tag_ht = collections.defaultdict(int)
color_ht = collections.defaultdict(int)

def add_sense(word, data, sense):
    for k in data.keys():
        data_keys[k] += 1
        if k not in known_data_keys:
            print("{} UNRECOGNIZED DATA KEY: {}".format(word, k))
    for k in sense.keys():
        sense_keys[k] += 1
        if k not in known_sense_keys:
            print("{} UNRECOGNIZED SENSE KEY: {}".format(word, k))
    pos = data.get("pos", "")
    lang = data.get("lang", "")
    heads = data.get("heads", ())
    translations = data.get("translations", ())
    pronunciations = data.get("pronunciations", ())
    categories = data.get("categories", ())
    derived = data.get("derived", ())
    synonyms = data.get("synonyms", ())
    related = data.get("related", ())
    antonyms = data.get("antonyms", ())
    hyphenation = data.get("hyphenation", ())
    isbn = data.get("isbn", ())
    hyponyms = data.get("hyponyms", ())
    hypernyms = data.get("hypernyms", [])
    alternate = data.get("alternate", ())
    conjugation = data.get("conjugation", ())
    abbreviations = data.get("abbreviations", ())
    enum = data.get("enum", ())
    compounds = data.get("compounds", ())
    topics = data.get("topics", [])

    glosses = sense.get("glosses", ())
    tags = sense.get("tags", ())
    inflection_of = sense.get("inflection_of", ())
    alt_of = sense.get("alt_of", ())
    sense_hypernyms = sense.get("hypernyms", [])  # XXX from {{place|...}
    hypernyms += sense_hypernyms
    holonyms = sense.get("holonyms", [])  # XXX from {{place|...}}
    sense_antonyms = sense.get("antonyms", [])
    antonyms += sense_antonyms
    sense_hyponyms = sense.get("hyponyms", [])
    hyponyms += sense_hyponyms
    coordinate_terms = sense.get("coordinate_terms", [])
    taxon = sense.get("taxon", ())
    wikipedia = sense.get("wikipedia", ())
    origin = sense.get("origin", ())
    nonglosses = sense.get("nonglosses", ())
    senseid = sense.get("senseid", ())
    sense_topics = sense.get("topics", [])
    topics += sense_topics
    complex_inflection_of = sense.get("complex_inflection_of", ())
    unit = sense.get("unit", ())
    only_in = sense.get("only_in", ())
    color = sense.get("color", ())
    object_preposition = sense.get("object_preposition", ())
    examples = sense.get("examples", ())
    #if len(glosses) > 1:
    #    print("{}: MORE THAN ONE GLOSS: {}".format(word, glosses))
    #if only_in:
    #    print("{}: ONLY IN: {}: {}".format(word, only_in, glosses))
    #if topics:
    #    print("{}: TOPICS {}: {}".format(word, topics, glosses))
    #    for t in topics:
    #        topic_ht[t] += 1
    #if object_preposition:
    #    print("{}: OBJECT PREPOSITION: {}: {}"
    #          "".format(word, object_preposition, glosses))
    #for tag in tags:
    #    tag_ht[tag] += 1
    for color in color:
        print(color)
        color_ht[color] += 1

#with open("temp.tmp") as f:
cnt = 0
for line in sys.stdin:
    data = json.loads(line)
    word = data.get("word")
    if word is None:
        continue
    if re.match(r"^(Wiktionary|Help):", word):
        continue
    if "lang" not in data:
        # XXX look into these
        #print("SKIPPING", word)
        continue
    senses = data.get("senses", [])
    if not senses:
        #print("{:<15s} {}".format(word, "NO SENSES"))
        continue
    for sense in senses:
        for gloss in (sense.get("glosses", [""]) or [""]):
            #print("{:<15s} {}".format(word, gloss))
            add_sense(word, data, sense)
            cnt += 1
            if cnt % 100000 == 0:
              print("...", cnt)

print("DATA KEYS")
for k, v in sorted(data_keys.items(), key=lambda x: x[1]):
    print("{:<20s} {}".format(k, v))
print("")
print("SENSE KEYS")
for k, v in sorted(sense_keys.items(), key=lambda x: x[1]):
    print("{:<20s} {}".format(k, v))
print("")

if False:
    print("TOPICS")
    for k, v in sorted(topic_ht.items(), key=lambda x: x[1]):
        print("{:<40s} {}".format(k, v))
    print("{} different topics, {} instances"
          "".format(len(topic_ht), sum(topic_ht.values())))

if False:
    print("TAGS")
    of_cnt = 0
    with_cnt = 0
    lingform_cnt = 0
    for k, v in sorted(tag_ht.items(), key=lambda x: x[1]):
        if k in lingform_tags or re.search(lingform_end_re, k):
            lingform_cnt += 1
            continue
        if k.startswith("of "):
            of_cnt += 1
            continue
        if k.startswith("with "):
            with_cnt += 1
            continue
        print("{:<40s} {}".format(k, v))
    print("{} different tags, {} instances, {} of, {} with, {} lingform"
          "".format(len(tag_ht), sum(tag_ht.values()),
                    of_cnt, with_cnt, lingform_cnt))

if True:
    print("COLORS")
    for k, v in sorted(color_ht.items(), key=lambda x: x[1]):
        print("{:<20s} {}".format(k, v))
    print("{} different colors, {} instances"
          "".format(len(color_ht), sum(color_ht.values())))

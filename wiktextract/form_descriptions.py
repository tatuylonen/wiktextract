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
                        data_alt_of)

# Maps individual words from form descriptions.  This is primarily used for
# expanding abbreviations and some canonicalization.
form_map = {
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
    "inan": "inanimate",
    "anim": "animate",
    "pers": "person",
    "impf.": "imperfect",
    "impf": "imperfect",
    "pf": "perfective",
    "unc": "uncountable",
    "trans.": "transitive",
    "npers": "impersonal",
    "c": "common",  # common gender in at least West Frisian
    "&": "and",
    "abbreviated": "abbreviation",
}

# Maps strings into one or more other strings.  This is applied at multiple
# levels of partitioning the description.

paren_map = {
    "countable and uncountable": ["countable", "uncountable"],
    "masculine and feminine plural": ["masculine plural", "feminine plural"],
    "definite singular and plural": ["definite singular", "definite plural"],
    "plural and definite singular attributive":
    ["plural attributive", "definite singular attributive"],
    "oblique and nominative feminine singular":
    ["oblique feminine singular", "nominative feminine singular"],
    "feminine and neuter plural": ["feminine plural", "neuter plural"],
    "feminine and neuter": ["feminine", "neuter"],
    "feminine and neuter plural": ["feminine plural", "neuter plural"],
    "masculine and feminine": ["masculine", "feminine"],
    "masculine and neuter": ["masculine", "neuter"],
    "masculine and plural": ["masculine", "plural"],
    "female and neuter": ["feminine", "neuter"],
    "singular and plural": ["singular", "plural"],
    "plural and weak singular": ["plural", "weak singular"],
    "preterite and supine": ["preterite", "supine"],
    "genitive and dative": ["genitive", "dative"],
    "genitive and plural": ["genitive", "plural"],
    "dative and accusative": ["dative", "accusative"],
    "dative and accusative singular":
    ["dative singular", "accusative singular"],
    "simple past and past participle": ["simple past", "past participle"],
    "genitive/dative": ["genitive", "dative"],
    "first/second-declension adjective":
    ["first-declension adjective", "second-declension adjective"],
    "class 9/10": ["class 9", "class 10"],
    "class 5/6": ["class 5", "class 6"],
    "class 3/4": ["class 3", "class 4"],
    "class 7/8": ["class 7", "class 8"],
    "class 1/2": ["class 1", "class 2"],
    "first/second declension": ["first declension", "second declension"],
    "genitive/dative": ["genitive", "dative"],
    "first/second-declension suffix":
    ["first-declension suffix", "second-declension suffix"],
    "first/second-declension numeral plural only":
    ["first-declension numeral plural only",
     "second-declension numeral plural only"],
    "third-declension two-termination adjective":
    ["third-declension adjective",
     "third-declension two-termination adjective"],
    "third-declension one-termination adjective":
    ["third-declension adjective",
     "third-declension one-termination adjective"],
    "possessive (with noun)": ["possessive", "with noun"],
    "possessive (without noun)": ["possessive", "without noun"],
    "informal 1st possessive": ["informal", "first-person possessive"],
    "impolite 2nd possessive": ["informal", "second-person possessive"],
    "strong personal pronoun": ["strong", "personal pronoun"],
    "weak personal pronoun": ["weak", "personal pronoun"],
    "strong personal": ["strong", "personal pronoun"],
    "weak personal": ["weak", "personal pronoun"],
    "upper case roman numeral": ["upper case", "numeral"],
    "usually uncountable": ["uncountable", "usually uncountable"],
    "with accusative or dative": ["with accusative", "with dative"],
    "with accusative or genitive": ["with accusative", "with genitive"],
    "with accusative or ablative": ["with accusative", "with ablative"],
    "nominative and accusative definite singular":
    ["nominative definite singular", "accusative definite singular"],
    "+ genitive or possessive suffix":
    ["with genitive", "with possessive suffix"],
    "+ genitive possessive suffix or elative":
    ["with genitive", "with possessive suffix", "with elative"],
    "+ partitive or (less common) possessive suffix":
    ["with partitive", "with possessive suffix"],
    "no perfect or supine stem": ["no perfect", "no supine"],
    "adverbial locative noun in the pa, ku, or mu locative classes":
    ["adverbial locative noun"],
    "comparative -": ["no comparative"],
    "superlative -": ["no superlative"],
    "1 declension": ["first declension"],
    "4 declension": ["fourth declension"],
    "5th declension": ["fifth declension"],
    "feminine ? declension": ["feminine"],
    "masculine ? declension": ["masculine"],
    "1st declension": ["first declension"],
    "2nd declension": ["second declension"],
    "3rd declension": ["third declension"],
    "4th declension": ["fourth declension"],
    "plural inv": ["plural invariable"],
    "plural not attested": ["no plural"],
    "no plural forms": ["no plural"],
    "used only predicatively": ["not attributive"],
    "present tense": ["present"],
    "past tense": ["past"],
    "feminine counterpart": ["feminine"],
    "masculine counterpart": ["masculine"],
    "passive counterpart": ["passive"],
    "active counterpart": ["active"],
    "basic stem form": ["stem"],
    "no supine stem": ["no supine"],
    "no perfect stem": ["no perfect"],
    "construct state": ["construct"],
    "construct form": ["construct"],
    "uppercase": ["upper case"],
    "lowercase": ["lower case"],
    "phonemic reduplicative": ["reduplicated"],
    "objective case": ["objective"],
    "genitive case": ["genitive"],
    "dative case": ["dative"],
    "ergative cases": ["ergative"],
    "absolutive case": ["absolutive"],
    "genitive unattested": ["no genitive"],
    "genitive -": ["no genitive"],
    "nominative plural -": ["no nominative plural"],
    "rare comparative": ["comparative"],
    "rare/awkward comparative": ["comparative"],
    "found only in the imperfective tenses": ["no perfect"],
    "third plural indicative": ["third-person plural indicative"],
    "defective verb": ["defective"],
    "3rd possessive": ["third-person possessive"],
    "active voice": ["active"],
    "plural rare": ["plural"],
    "plus genitive": ["with genitive"],
    "+ genitive": ["with genitive"],
    "+genitive": ["with genitive"],
    "+ genitive case": ["with genitive"],
    "genitive +": ["with genitive"],
    "with genitive case": ["with genitive"],
    "+dative": ["with dative"],
    "+ dative case": ["with dative"],
    "+ dative": ["with dative"],
    "plus dative": ["with dative"],
    "+ accusative": ["with accusative"],
    "+accusative": ["with accusative"],
    "with accusative case": ["with accusative"],
    "plus accusative": ["with accusative"],
    "+ partitive": ["with partitive"],
    "+partitive": ["with partitive"],
    "with partitive case": ["with partitive"],
    "plus partitive": ["with partitive"],
    "+ablative": ["with ablative"],
    "+ ablative": ["with ablative"],
    "with ablative case": ["with ablative"],
    "plus ablative": ["with ablative"],
    "+ subjunctive": ["with subjunctive"],
    "+subjunctive": ["with subjunctive"],
    "plus subjunctive": ["with subjunctive"],
    "+ instrumental": ["with instrumental"],
    "+instrumental": ["with instrumental"],
    "with instrumental case": ["with instrumental"],
    "plus instrumental": ["with instrumental"],
    "+absolutive": ["with absolutive"],
    "+ absolutive": ["with absolutive"],
    "with absolutive case": ["with absolutive"],
    "+ absolutive case": ["with absolutive"],
    "plus absolutive": ["with absolutive"],
    "+elative": ["with elative"],
    "+ elative": ["with elative"],
    "with elative case": ["with elative"],
    "plus elative": ["with elative"],
    "+objective": ["with objective"],
    "+ objective": ["with objective"],
    "with objective case": ["with objective"],
    "plus objective": ["with objective"],
    "p-past": ["passive past"],
    "ppp": ["passive perfect participle"],
    "not used in plural form": ["no plural"],
    "not declined": ["indeclinable"],
    "interrogative adverb": ["interrogative"],
    "perfect tense": ["perfect"],
    "intensive": ["emphatic"],
    "changed conjunct form": ["conjunct"],
    "biblical hebrew pausal form": ["pausal"],
    "emphatic form": ["emphatic"],
    "standard form": ["standard"],
    "augmented form": ["augmented"],
    "active form": ["active"],
    "passive form": ["passive"],
    "mutated form": ["mutated"],
    "auxiliary verb": ["auxiliary"],
    "male equivalent": ["masculine"],
}

blocked = set(["të", "a", "e", "al", "þou", "?", "lui", "auf", "op", "ein",
               "af", "uit", "aus", "ab", "zu", "on", "off", "um", "faço",
               "dou", "†yodan", "at", "feito", "mná", "peces", "har",
               "an", "u"])

valid_tags = [
    "masculine",
    "feminine",
    "neuter",
    "common",
    "gender indeterminate",
    "singular",
    "singulative",
    "plural",
    "paucal",
    "alternative plural",
    "also",
    "plural only",
    "plurale tantum",
    "uncountable",
    "countable",
    "comparative",
    "superlative",
    "comparable",
    "not comparable",
    "no comparative",
    "no superlative",
    "predicative superlative",
    "excessive",
    "inanimate",
    "animate",
    "person",
    "impersonal",
    "abstract",
    "demonstrative",
    "personal pronoun",
    "subjective pronoun",
    "nominative",
    "genitive",
    "no genitive",
    "possessive",
    "first-person possessive",
    "second-person possessive",
    "third-person possessive",
    "possessive suffix",
    "possessive determiner",
    "accusative",
    "objective",
    "subjective",
    "partitive",
    "dative",
    "oblique",
    "locative",
    "ablative",
    "elative",
    "illative",
    "allative",
    "instrumental",
    "equative",
    "relative",
    "ergative",
    "absolutive",
    "definitive",
    "indefinite",
    "collective",
    "diminutive",
    "pejorative",
    "diminutive of",
    "infinitive"
    "da-infinitive",
    "first-person",
    "second-person",
    "third-person",
    "present",
    "future",
    "past",
    "non-past",
    "perfect",
    "imperfect",
    "preterite",
    "supine",
    "aorist",
    "active",
    "passive",
    "interrogative",
    "contemplative",
    "subjunctive",
    "conjunctive",
    "future independent",
    "no supine",
    "no perfect",
    "attributive",
    "not attributive",
    "predicative",
    "not predicative",
    "irregular",
    "defective",
    "present participle",
    "past participle",
    "active participle",
    "passive participle",
    "indicative",
    "progressive",
    "complete",
    "perfective",
    "imperfective",
    "imperative",
    "imperative only",
    "negative",
    "positive",
    "causative",
    "frequentative",
    "transitive",
    "intransitive",
    "ambitransitive",
    "stative",
    "pronominal state",
    "nominal state",
    "invariable",
    "invariant",  # XXX is this same as invariable?
    "indeclinable",
    "inalienable",
    "form i",
    "form ii",
    "form iii",
    "form iv",
    "form v",
    "form vi",
    "form vii",
    "form viii",
    "form ix",
    "form x",
    "form xi",
    "form xii",
    "form xiii",
    "form iq",
    "form iiq",
    "form iiiq",
    "form ivq",
    "class 1",
    "class 1a",
    "class 2",
    "class 2a",
    "class 3",
    "class 4",
    "class 5",
    "class 6",
    "class 7",
    "class 8",
    "class 9",
    "class 10",
    "class 11",
    "class 12",
    "class 13",
    "class 14",
    "class 15",
    "m-wa class",
    "m-mi class",
    "u class",
    "ki-vi class",
    "first-declension adjective",
    "second-declension adjective",
    "third-declension adjective",
    "first declension",
    "second declension",
    "third declension",
    "fourth declension",
    "fifth declension",
    "first conjugation",
    "second conjugation",
    "third conjugation",
    "fourth conjugation",
    "fifth conjugation",
    "sixth conjugation",
    "seventh conjugation",
    "stress pattern 1",
    "stress pattern 2",
    "stress pattern 3",
    "stress pattern 3a",
    "stress pattern 3b",
    "stress pattern 4",
    "type p",
    "type u",
    "type up",
    "type a",
    "root",
    "stem",
    "present stem",
    "past stem",
    "possessed",
    "ordinal",
    "ordinal form of",
    "conjunct participle",
    "conjunct",
    "used in the form",
    "construct",
    "no construct forms",
    "reduplicated",
    "pausal",
    "upper case",
    "lower case",
    "mixed case",
    "verb form i",
    "dual",
    "form used before",
    "pi'el construction",
    "pa'el construction",
    "hif'il construction",
    "hitpa'el construction",
    "pu'al construction",
    "nif'al construction",
    "huf'al construction",
    "sequential",
    "conditional",
    "volitive",
    "adnominal",
    "nominal",
    "adverbial",
    "adverb",
    "adjective",
    "adjectival",
    "verbal noun",
    "auxiliary",
    "numeral",
    "classifier",
    "kyūjitai",
    "shinjitai",
    "brazilian orthography",
    "european orthography",
    "classical milanese orthography",
    "old orthography",
    "traditional orthography spelling",
    "northern dialect",
    "dialectal",
    "obsolete",
    "archaic",
    "historical",
    "literary",
    "informal",
    "formal",
    "colloquial",
    "with odd-syllable stems",
    "with genitive",
    "with dative",
    "with objective",
    "with accusative",
    "with ablative",
    "with instrumental",
    "with elative",
    "with absolutive",
    "with subjunctive",
    "with partitive",
    "with possessive suffix",
    "krama",
    "ngoko",
    "krama-ngoko",
    "krama inggil",
    "next",
    "previous",
    "past participle of",
    "plural of",
    "compound of",
    "abbreviation",
    "contracted dem-form",
    "accent/glottal",
    "transcription",
    "medial",
    "future analytic",
    "present analytic",
    "genitive as verbal noun",
    "genitive singular as substantive",
    "prototonic",
    "error",
    "canonical",  # Used to mark the canonical word from from head
    "figurative",
]

valid_tree = {}
for tag in valid_tags:
    node = valid_tree
    for w in tag.split(" "):
        if w in node:
            node = node[w]
        else:
            new_node = {}
            node[w] = new_node
            node = new_node
    node["$"] = tag

# Regexp used to find "words" from word heads and linguistic descriptions
word_re = re.compile(r"[^ ,;()\u200e]+|\([^)]*\)")

def distw(titleparts, word):
    # Returns 1 if words completely distinct, 0 if identical, or otherwise
    # something in between
    w = min(Levenshtein.distance(word, tw) / max(len(tw), len(word))
            for tw in titleparts)
    return w


def map_with(ht, lst):
    assert isinstance(ht, dict)
    assert isinstance(lst, list)
    ret = []
    for x in lst:
        x = x.strip()
        x = ht.get(x, x)
        if isinstance(x, str):
            ret.append(x)
        elif isinstance(x, list):
            ret.extend(x)
        else:
            raise RuntimeError("map_with unexpected value: {!r}".format(x))
    return ret


def decode_tags(config, lst):
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(lst, list)
    tags = []
    node = valid_tree
    for w in lst:
        while True:
            if w in node:
                node = node[w]
                break
            elif "$" in node:
                tag = node["$"]
                tags.append(tag)
                node = valid_tree
            else:
                config.warning("unsupported tag component {!r} in {}"
                               .format(w, lst))
                if "error" not in tags:
                    tags.append("error")
                node = valid_tree
                break
    if node is not valid_tree:
        if "$" in node:
            tag = node["$"]
            tags.append(tag)
        else:
            config.warning("unsupported tag component {!r} in {}"
                           .format(w, lst))
    return tags


def add_tags(ctx, config, data, lst):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(data, dict)
    assert isinstance(lst, list)
    tags = decode_tags(config, lst)
    if tags:
        data_extend(config, data, "tags", tags)


def add_related(ctx, config, data, lst, related):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(lst, list)
    assert isinstance(related, list)
    related = " ".join(related)
    if related:
        tags = decode_tags(config, lst)
        data_append(config, data, "forms", {"tags": tags, "form": related})


def parse_word_head(ctx, config, pos, text, data):
    """Parses the head line for a word for in a particular language and
    part-of-speech, extracting tags and related forms."""
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    print("parse_word_head:", ctx.title, text)
    title = ctx.title
    titleparts = list(m.group(0) for m in re.finditer(word_re, title))

    # Handle the part of the head that is not in parentheses
    base = re.sub(r"\([^)]*\)", "", text)
    base = re.sub(r"\s+", " ", base).strip()
    for desc in map_with(paren_map, base.split(";")):
        for alt in map_with(paren_map, base.split(" or ")):
            baseparts = list(m.group(0) for m in re.finditer(word_re, alt))
            baseparts = list(map(lambda x: form_map.get(x, x), baseparts))
            lst = []
            i = 0
            while i < len(baseparts):
                word = baseparts[i]
                w = distw(titleparts, word)
                if word == title or (w <= 0.5 and word not in blocked and
                                     word not in valid_tags):
                    lst.append(word)
                else:
                    break
                i += 1
            rest = baseparts[i:]
            # lst is canonical form of the word
            # rest is additional tags (often gender m/f/n/c/...)
            #print("word (lst)", lst)
            #print("rest", rest)
            if title != " ".join(lst):
                add_related(ctx, config, data, ["canonical"], lst)
            # XXX here we should only look at a subset of tags allowed
            # in the base
            add_tags(ctx, config, data, rest)

    # Handle parenthesized descriptors for the word form and links to
    # related words
    parens = list(m.group(1) for m in re.finditer(r"\(([^)]*)\)", text))
    for paren in parens:
        descriptors = map_with(paren_map, [paren])
        new_desc = []
        for desc in descriptors:
            for semi in map_with(paren_map, desc.split(";")):
                for alt in map_with(paren_map, semi.split(",")):
                    new_desc.extend(map_with(paren_map, alt.split(" or ")))
        for desc in new_desc:
            parts = list(m.group(0) for m in re.finditer(word_re, desc))
            parts = list(map(lambda x: form_map.get(x, x), parts))
            lst = []
            i = 0
            while i < len(parts):
                part = parts[i]
                w = distw(titleparts, part)
                if (part != title and
                    (part in valid_tags or
                     (w > 0.5 and
                      (not lst or lst[-1] not in (
                          "comparative", "superlative", "classifier")) and
                     part not in blocked))):
                    # Consider it part of a descriptor
                    lst.append(part)
                else:
                    # Consider the rest as a related term
                    break
                i = i + 1
            related = parts[i:]
            if related:
                add_related(ctx, config, data, lst, related)
            else:
                add_tags(ctx, config, data, lst)


def parse_sense_tags(ctx, config, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    print("parse_sense_tags", text)
    tags = map_with(paren_map, text.split(","))
    # XXX should check which tags are valid XXX do we want to warn about
    # unknown ones here
    data_extend(config, data, "tags", tags)


def parse_pronunciation_tags(ctx, config, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(config, WiktionaryConfig)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    print("parse_pronunciation_tags", text)
    tags = map_with(paren_map, text.split(","))
    # XXX should check which tags are valid for pronunciations
    # XXX do we want to warn about unknown ones here?
    data_extend(config, data, "tags", tags)

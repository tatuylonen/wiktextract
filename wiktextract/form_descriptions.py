# Code for parsing linguistic form descriptions and tags for word senses
# (both the word entry head - initial part and parenthesized parts -
# and tags at the beginning of word senses)
#
# Copyright (c) 2020-2021 Tatu Ylonen.  See file LICENSE and https://ylonen.org

import re
import functools
import unicodedata
import Levenshtein
from nltk import TweetTokenizer
from wikitextprocessor import Wtp
from .datautils import data_append, data_extend, split_at_comma_semi
from .taxondata import known_species, known_firsts
from .topics import valid_topics, topic_generalize_map
from .tags import (xlat_head_map, valid_tags,
                   uppercase_tags, xlat_tags_map, xlat_descs_map,
                   head_final_numeric_langs,
                   head_final_bantu_langs, head_final_bantu_map,
                   head_final_other_langs, head_final_other_map)
from .english_words import english_words, not_english_words

# Tokenizer for classify_desc()
tokenizer = TweetTokenizer()

# Add some additional known taxonomic species names.  Adding the family name
# here may be the answer if a taxonomic name goes in "alt".
known_firsts.update([
    "Aglaope",
    "Albulidae",
    "Alphonsus",
    "Artipus",
    "Bubo",
    "Callistosporium",
    "Caprobrotus",
    "Chaetodontinae",
    "Chalchicuautla",
    "Citriobatus",
    "Citrofortunella",
    "Coriandum",
    "Eriophyes",
    "Lagerstomia",
    "Lyssavirus",
    "Maulisa",
    "Megamimivirinae",
    "Mercenaria",
    "Monetaria",
    "Mugillidae",
    "Ogcocephalus",
    "Onchorhynchus",
    "Plebidonax",
    "Poncirus",
    "Rugosomyces",
    "Tanagra",
])

# First words of unicodedata.name() that indicate scripts that cannot be
# accepted in romanizations or english (i.e., should be considered "other"
# in classify_desc()).
non_latin_scripts = [
    "ADLAM",
    "ARABIC",
    "ARABIC-INDIC",
    "ARMENIAN",
    "BALINESE",
    "BENGALI",
    "BRAHMI",
    "BRAILLE",
    "CANADIAN",
    "CHAKMA",
    "CHAM",
    "CHEROKEE",
    "CJK",
    "COPTIC",
    "COUNTING ROD",
    "CUNEIFORM",
    "CYRILLIC",
    "DOUBLE-STRUCK",
    "EGYPTIAN",
    "ETHIOPIC",
    "EXTENDED ARABIC-INDIC",
    "GEORGIAN",
    "GLAGOLITIC",
    "GOTHIC",
    "GREEK",
    "GUJARATI",
    "GURMUKHI",
    "HANGUL",
    "HANIFI ROHINGYA",
    "HEBREW",
    "HIRAGANA",
    "JAVANESE",
    "KANNADA",
    "KATAKANA",
    "KAYAH LI",
    "KHMER",
    "KHUDAWADI",
    "LAO",
    "LEPCHA",
    "LIMBU",
    "MALAYALAM",
    "MEETEI",
    "MYANMAR",
    "NEW TAI LUE",
    "NKO",
    "OL CHIKI",
    "OLD PERSIAN",
    "OLD SOUTH ARABIAN",
    "ORIYA",
    "OSMANYA",
    "PHOENICIAN",
    "SAURASHTRA",
    "SHARADA",
    "SINHALA",
    "SUNDANESE",
    "SYLOTI",
    "TAI THAM",
    "TAKRI",
    "TAMIL",
    "TELUGU",
    "THAANA",
    "THAI",
    "TIBETAN",
    "TIFINAGH",
    "TIRHUTA",
    "UGARITIC",
    "WARANG CITI",
    "YI",
]
non_latin_scripts_re = re.compile(
    r"(" +
    r"|".join(re.escape(x) for x in non_latin_scripts) +
    r")\b")

# Regexp for finding nested translations from translation items (these are
# used in, e.g., year/English/Translations/Arabic).  This is actually used
# in page.py.
nested_translations_re = re.compile(
    r"\s+\((({}): ([^()]|\([^()]+\))+)\)"
    .format("|".join(x for x in xlat_head_map.values()
                     if x and not x.startswith("class-"))))

# Regexp that matches head tag specifiers.  Used to match tags from end of
# translations and linkages
head_final_re = re.compile(
    r"( -)?( ({}))+$".format(
        "|".join(re.escape(x) for x in
                 # The sort is to put longer ones first, preferring them in
                 # the regexp match
                 sorted(xlat_head_map.keys(), key=lambda x: len(x),
                        reverse=True))))

# Regexp used to match head tag specifiers at end of a form for certain
# Bantu languages (particularly Swahili and similar languages).
head_final_bantu_re = re.compile(
    r" ({})$".format(
        "|".join(re.escape(x) for x in head_final_bantu_map.keys())))

# Regexp used to match head tag specifiers at end of a form for certain
# other languages (e.g., Lithuanian, Finnish, French).
head_final_other_re = re.compile(
    r" ({})$".format(
        "|".join(re.escape(x) for x in head_final_other_map.keys())))

# Parenthesized parts that are ignored in translations
ignored_parens = set([
    "please verify",
    "(please verify)",
    "transliteration needed",
    "(transliteration needed)",
    "in words with back vowel harmony",
    "(in words with back vowel harmony)",
    "in words with front vowel harmony",
    "(in words with front vowel harmony)",
])

# Translations that are ignored
ignored_translations = set([
    "[script needed]",
    "please add this translation if you can",
])

# Put english text into the "note" field in a translation if it contains one
# of these words
tr_note_re = re.compile(
    r"(\b(article|definite|indefinite|superlative|comparative|pattern|"
    "adjective|adjectives|clause|clauses|pronoun|pronouns|preposition|prep|"
    "postposition|postp|action|actions|articles|"
    "adverb|adverbs|noun|nouns|verb|verbs|before|"
    "after|placed|prefix|suffix|used with|translated|"
    "nominative|genitive|dative|infinitive|participle|past|perfect|imperfect|"
    "perfective|imperfective|auxiliary|negative|future|present|tense|aspect|"
    "conjugation|declension|class|category|plural|singular|positive|"
    "seldom used|formal|informal|familiar|unspoken|spoken|written|"
    "indicative|progressive|conditional|potential|"
    "accusative|adessive|inessive|superessive|elative|allative|"
    "dialect|dialects|object|subject|predicate|movies|recommended|language|"
    "locative|continuous|simple|continuousness|gerund|subjunctive|"
    "periphrastically|no equivalent|not used|not always used|"
    "used only with|not applicable|use the|signifying|wordplay|pronounced|"
    "preconsonantal|spelled|spelling|respelling|respellings|phonetic|"
    "may be replaced|stricter sense|for nonhumans|"
    "sense:|used:|in full:|informally used|followed by|"
    "not restricted to|pertaining to|or optionally with|are optional|"
    "in conjunction with|in compounds|depending on the relationship|"
    "person addressed|one person|multiple persons|may be replaced with|"
    "optionally completed with|in the phrase|in response to|"
    "before a|before an|preceded by|verbs ending|very common|after a verb|"
    "with verb|with uncountable|with the objects|with stative|"
    "can be replaced by|often after|used before|used after|"
    "used in|clipping of|spoken|somewhat|capitalized|"
    "short form|shortening of|shortened form|initialism of|"
    "said to|rare:|rarer also|is rarer|negatively connoted|"
    "previously mentioned|uncountable noun|countable noun|"
    "countable nouns|uncountable nouns|"
    "with predicative|with -|with imperfect|with a negated|"
    "colloquial|misspelling|holophrastic|frequently|esp\.|especially|"
    '"|'
    "form|regular|irregular|alternative)"
    ")($|[) ])|^("
    # Following are only matched at the beginning of the string
    "pl|pl\.|see:|pl:|sg:|plurals:|e\.g\.|e\.g\.:|e\.g\.,|cf\.|compare|such as|"
    "see|only|often|usually|used|usage:|of|not|in|compare|usu\.|"
    "as|about|abbrv\.|abbreviation|abbr\.|that:|optionally|"
    "mainly|from|for|also|also:|acronym|"
    "with) ")
# \b does not work at the end???

# If an unknown sequence starts with one of these, it will continue as an
# unknown sequence until the end, unless it turns out to have a replacement.
allowed_unknown_starts = set([
    "Relating",
    "accompanied",
    "added",
    "after",
    "answering",
    "as",
    "based",
    "before",
    "conjugated",
    "conjunction",
    "construed",
    "e.g.",
    "especially",
    "expression:",
    "figurative:",
    "followed",
    "for",
    "forms",
    "from",
    "governs",
    "in",
    "indicating",
    "modifying",
    "normally",
    "not",
    "of",
    "originally",
    "preceding",
    "prefixed",
    "referring",
    "relating",
    "revived",
    "said",
    "since",
    "takes",
    "used",
    "with",
    "With",
    "without",
])

# Words that can be part of form description
valid_words = set(["or", "and"])
for x in valid_tags:
    valid_words.update(x.split(" "))
for x in xlat_tags_map.keys():
    valid_words.update(x.split(" "))


def add_to_valid_tree(tree, desc, v):
    """Helper function for building trees of valid tags/sequences during
    initialization."""
    assert isinstance(tree, dict)
    assert isinstance(desc, str)
    assert v is None or isinstance(v, str)
    node = tree
    for w in desc.split(" "):
        if w in node:
            node = node[w]
        else:
            new_node = {}
            node[w] = new_node
            node = new_node
    if "$" not in node:
        node["$"] = {}
    if not v:
        return

    node = node["$"]
    tags = []
    topics = []
    for vv in v.split():
        if vv in valid_tags:
            tags.append(vv)
        elif vv in valid_topics:
            topics.append(vv)
        else:
            print("WARNING: tag/topic {!r} maps to unknown {!r}"
                  .format(desc, vv))
    topics = " ".join(topics)
    tags = " ".join(tags)
    if topics:
        if "topics" not in node:
            node["topics"] = ()
        node["topics"] += (topics,)
    if tags:
        if "tags" not in node:
            node["tags"] = ()
        node["tags"] += (tags,)


def add_to_valid_tree1(tree, k, v, valid_values):
    assert isinstance(tree, dict)
    assert isinstance(k, str)
    assert v is None or isinstance(v, (list, tuple, str))
    assert isinstance(valid_values, set)
    if not v:
        add_to_valid_tree(valid_sequences, k, None)
        return
    elif isinstance(v, str):
        v = [v]
    q = []
    for vv in v:
        assert isinstance(vv, str)
        add_to_valid_tree(valid_sequences, k, vv)
        vvs = vv.split()
        for x in vvs:
            q.append(x)
    return q


def add_to_valid_tree_mapping(tree, mapping, valid_values, recurse):
    assert isinstance(tree, dict)
    assert isinstance(mapping, dict)
    assert isinstance(valid_values, set)
    assert recurse in (True, False)
    for k, v in mapping.items():
        assert isinstance(k, str)
        assert isinstance(v, (list, str))
        if isinstance(v, str):
            v = [v]
        q = add_to_valid_tree1(tree, k, v, valid_values)
        if recurse:
            visited = set()
            while q:
                v = q.pop()
                if v in visited:
                    continue
                visited.add(v)
                if v not in mapping:
                    continue
                vv = mapping[v]
                qq = add_to_valid_tree1(tree, k, vv, valid_values)
                q.extend(qq)


# Tree of sequences considered to be tags (includes sequences that are
# mapped to something that becomes one or more valid tags)
valid_sequences = {}
for tag in valid_tags:
    add_to_valid_tree(valid_sequences, tag, tag)
for tag in uppercase_tags:
    hyphenated = re.sub(r"\s+", "-", tag)
    valid_tags.add(hyphenated)
    add_to_valid_tree(valid_sequences, hyphenated, hyphenated)
for tag in uppercase_tags:
    hyphenated = re.sub(r"\s+", "-", tag)
    add_to_valid_tree(valid_sequences, tag, hyphenated)
add_to_valid_tree_mapping(valid_sequences, xlat_tags_map, valid_tags, False)
# Add topics to the same table, with all generalized topics also added
for topic in valid_topics:
    assert " " not in topic
    add_to_valid_tree(valid_sequences, topic, topic)
# Let each original topic value stand alone.  These are not generally on
# valid_topics.  We add the original topics with spaces replaced by hyphens.
for topic in topic_generalize_map.keys():
    hyphenated = re.sub(r" ", "-", topic)
    valid_topics.add(hyphenated)
    add_to_valid_tree(valid_sequences, topic, hyphenated)
# Add canonicalized/generalized topic values
add_to_valid_tree_mapping(valid_sequences, topic_generalize_map,
                          valid_topics, True)

# Regexp used to find "words" from word heads and linguistic descriptions
word_re = re.compile(r"[^ ,;()\u200e]+|\(([^()]|\([^()]*\))*\)")

# Maps from segments in gloss to tags that will be added.  These are matched
# case-insensitive.
gloss_tags = {
    # Note: these are surrounded by \b in regexp
    # XXX should really dividide this by part-of-speech
    "of a": "",  # Intended to block various uses of words in irrelevant context
    "of an": "",
    "as a": "",
    "as an": "",
    "in a": "",
    "in an": "",
    "with a": "",
    "with an": "",
    "without a": "",
    "without an": "",
    "used substantively, with an implied noun.": "without-noun",
    "used without a following noun": "without-noun",
    "possessive case of": "possessive",
    "that with belongs to": "possessive",
    "Belonging to": "possessive",
    "belonging to": "possessive",
    "used predicatively": "predicative not-attributive",
    "used attributively": "attributive not-predicative",
    "usually attributive": "usually attributive",
    "usually predicative": "usually predicative",
    "attributive": "attributive",
    "predicative": "predicative",
    "attributively": "attributive",
    "predicatively": "predicative",
    "female": "g-feminine",
    "feminine": "g-feminine",
    "masculine": "g-masculine",
    "male": "g-masculine",
    "woman": "g-feminine g-person",
    "women": "g-feminine g-person g-plural",
    "man": "g-masculine g-person",
    "men": "g-masculine g-person g-plural",
    "captain": "g-person",
    "officer": "g-person",
    "person": "g-person",
    "child": "g-person",
    "a baby": "g-person",
    "an infant": "g-person",
    "attractive young": "g-person",
    "young human": "g-person",
    "people": "g-person g-plural",
    "audience": "g-person",
    "girl": "g-person g-feminine",
    "boy": "g-person g-masculine",
    "cavalry soldiers": "g-person",
    "foot soldier": "g-person",
    "male soldier": "g-person g-masculine",
    "a soldier": "g-person",
    "a private in": "g-person",
    "a guardsman": "g-person",
    "a low-rangking member of": "g-person",
    "impersonal": "impersonal",
    "personal pronoun": "g-person personal",
    "first-person": "first-person g-person",
    "second-person": "second-person g-person",
    "group spoken to": "second-person g-person",
    "individual or group spoken to": "second-person g-person",
    "person being addressed": "second-person g-person",
    "people spoken, or written to": "second-person g-person",
    "third-person": "third-person",
    "singular": "g-singular",
    "plural": "g-plural",
    "inanimate": "inanimate",
    "animate": "animate",
    "neither female nor male": "",
    "who": "g-person",
    "whom": "g-person",
    "whoever": "g-person",
    "whomever": "g-person",
    "whose": "g-person",
    "someone": "g-person",
    "somebody": "g-person",
    "anyone": "g-person",
    "anybody": "g-person",
    "nobody": "g-person",
    "campaigner": "g-person",
    "activist": "g-person",
    "sales assistant": "g-person",
    "an assistant": "g-person",
    "a relief pitcher": "g-person",
    "inspector": "g-person",
    "sergeant": "g-person",
    "captain": "g-person",
    "lieutnant": "g-person",
    "colonist": "g-person",
    "settler": "g-person",
    "pilgrim": "g-person",
    "colonialist": "g-person",
    "founder": "g-person",
    "doer": "g-person",
    "executioner": "g-person",
    "facilitator": "g-person",
    "maidservant": "g-person g-feminine",
    "operator of": "g-person",
    "dealer": "g-person",
    "trader": "g-person",
    "one given to": "g-person",
    "layman": "g-person",
    "cleric": "g-person",
    "head coach": "g-person",
    "head cook": "g-person",
    "administrator": "g-person",
    "clergyman": "g-person",
    "scholar": "g-person",
    "a pilot": "g-person",
    "a guide or escort": "g-person",
    "a follower of": "g-person",
    "a senior member of": "g-person",
    "student": "g-person",
    "lover": "g-person",
    "girlfriend": "g-person g-feminine",
    "boyfriend": "g-person g-feminine",
    "a partner": "g-person",
    "an associate": "g-person",
    "the head of a": "g-person",
    "a managerial or leading position": "g-person",
    "the head of state": "g-person",
    "male monarch": "g-person g-masculine",
    "female monarch": "g-person g-feminine",
    "the monarch with": "g-person",
    "Queen of England": "g-person g-feminine",
    "a female member of": "g-person g-feminine",
    "a male member of": "g-person g-masculine",
    "a female ruler": "g-person g-feminine",
    "a male ruler": "g-person g-masculine",
    "wife": "g-person g-feminine",
    "husband": "g-person g-masculine",
    "sister": "g-person g-feminine",
    "brother": "g-person g-masculine",
    "procuress": "g-person g-feminine",
    "artist": "g-person",
    "singer": "g-person",
    "cousin": "g-person",
    "a relative": "g-person",
    "the husband of": "g-person",
    "mother of": "g-person g-feminine",
    "father of": "g-person g-masculine",
    "grandmother": "g-person g-feminine",
    "grandfather": "g-person g-masculine",
    "worker unit": "g-person",
    "heir": "g-person",
    "forefather": "g-person",
    "pacifist": "g-person",
    "prisoner": "g-person",
    "coward": "g-person",
    "shepherd": "g-person",
    "a minister": "g-person",
    "priest": "g-person",
    "actor": "g-person",
    "a virgin": "g-person",
    "actress": "g-person",
    "policeman": "g-person",
    "politician": "g-person",
    "gamer": "g-person",
    "gambler": "g-person",
    "prostitute": "g-person",
    "prostitute's client": "g-person",
    "rapist": "g-person",
    "a thug": "g-person",
    "henchman": "g-person",
    "a fool": "g-person",
    "enforcer": "g-person",
    "a participant": "g-person",
    "a German guard": "g-person",
    "darling": "g-person",
    "sweetheart": "g-person",
    "one engaged in": "g-person",
    "a hippie": "g-person",
    "easy victim": "g-person",
    "sibling": "g-person",
    "a judge": "g-person",
    "an attorney": "g-person",
    "a lawyer": "g-person",
    "that also appears as the subject": "reflexive",
    "when that group also is the subject": "reflexive g-plural",
    "dummy pronoun": "g-placeholder",
    "used without referent": "g-placeholder",
    "in various short idioms": "idiomatic",
    "in idioms": "idiomatic",
    "in various idioms": "idiomatic",
    "reflexive": "reflexive",
    "including the speaker": "inclusive",
    "excluding the speaker": "exclusive",
    "not including the speaker": "exclusive",
    "speaker or writer": "first-person",
    "intensifies": "emphatic",
    "for emphasis": "emphatic",
    "object of a verb or preposition": "objective",
    "object of a verb": "objective",
    "object of a preposition": "objective",
    "delayed subject": "subjective",
    "as an object": "objective",
    "as a subject": "subjective",
    "mark of respect": "formal deferential",
    "as subject or object": "objective subjective",
    "as the grammatical subject": "subjective",
    "as the grammatical object": "objective",
    "this letter": "",
    "letter": "letter",
    "digit": "digit",
    "ordinal number": "ordinal",
    "ordinal form": "ordinal",
    "written in the Latin script": "Latin",
    "written in the Cyrillic script": "Cyrillic",
    "letter of several Cyrillic alphabets": "Cyrillic letter",
    "letter of the Bashkir alphabet": "Bashkir letter",
    "letter of the Kazakh alphabet": "Kazakh letter",
    "letter of the Kyrgyz alphabet": "Kyrgyz letter",
    "letter of the Mongolian alphabet": "Mongolian letter",
    "letter of the Serbo-Croatian alphabet": "Serbo-Croatian letter",
    "letter of the Tajik alphabet": "Tajik letter",
    "SI unit of": "g-unit",
    "the base unit of": "g-unit",
    "in the International System of Units": "g-unit",
    "unit of measurement": "g-unit",
    "the unit of": "g-unit",
    "a unit of": "g-unit",
    "a measure of": "g-unit",
    "the metric unit of": "g-unit",
    "any of various units of": "g-unit",
    "ounce, weighing": "g-unit",
    "fluid ounce": "g-unit",
    "a living being": "g-organism",
    "one of the asexual": "g-organism",
    "feline": "g-organism",
    "canine": "g-organism",
    "bovine": "g-organism",
    "lemur": "g-organism",
    "male sheep": "g-organism g-masculine",
    "female sheep": "g-organism g-feminine",
    "a sheep": "g-organism",
    "ewe": "g-organism g-feminine",
    "woody plant": "g-organism",
    "any plant": "g-organism",
    "plant itself": "g-organism",
    "a shrub": "g-organism",
    "monocot tree": "g-organism",
    "coniferous tree": "g-organism",
    "a tree": "g-organism",
    "any tree": "g-organism",
    "a yucca": "g-organism",
    "domesticated species": "g-organism",
    "ground-dwelling rodents": "g-organism",
    "burrowing rodents": "g-organism",
    "any small rodent": "g-organism",
    "any of several": "g-organism",
    "any of various": "g-organism",
    "any of very many animals": "g-organism",
    "any animal": "g-organism",
    "young animal": "g-organism",
    "unhatched vertebrate": "g-organism",
    "unborn vertebrate": "g-organism",
    "unborn young": "g-organism",
    "a human embryo": "g-organism",
    "vertebrate animal": "g-organism",
    "invertebrate animal": "g-organism",
    "an aquatic invertebrate": "g-organism",
    "aquatic animal": "g-organism",
    "a mammal": "g-organism",
    "mammalian species": "g-organism",
    "large mammal": "g-organism",
    "young swine": "g-organism",
    "adult swine": "g-organism",
    "reptile": "g-organism",
    "any bovines": "g-organism",
    "any bird": "g-organism",
    "weaverbird": "g-organism",
    "a bird, the": "g-organism",
    "any of the birds": "g-organism",
    "one of several birds": "g-organism",
    "domestic pigeon": "g-organism",
    "owl pigeon": "g-organism",
    "pet pig": "g-organism",
    "a dog used in": "g-organism",
    "a horse used in": "g-organism",
    "a kind of spider": "g-organism",
    "domestic fowl": "g-organism",
    "young of any bird": "g-organism",
    "surf scoter duck": "g-organism",
    "an insect": "g-organism",
    "social insect": "g-organism",
    "female ant": "g-organism g-feminine",
    "dragonfly": "g-organism",
    "a flying insect": "g-organism",
    "nocturnal insect": "g-organism",
    "a worm": "g-organism",
    "vertebrate": "g-organism",
    "eukaryote": "g-organism",
    "aquatic beetle": "g-organism",
    "a fish, the": "g-organism",
    "sea fish": "g-organism",
    "certain fish": "g-organism",
    "fesh-water fish": "g-organism",
    "fruit bat": "g-organism",
    "voracious fish": "g-organism",
    "other unrelated fish": "g-organism",
    "a species of": "g-organism",
    "a parasite": "g-organism",
    "large wasp": "g-organism",
    "various plants not in family": "g-organism",
    "any plant of": "g-organism",
    "a flowering plant": "g-organism",
    "fungus": "g-organism",
    "single-celled fungus": "g-organism",
    "bacterium": "g-organism",
    "archaebacterium": "g-organism",
    "algae": "g-organism",
    "mushroom species": "g-organism",
    "of the genus": "g-organism",
    "in the genus": "g-organism",
    "of the infraorder": "g-organism",
    "of the family": "g-organism",
    "of the suborder": "g-organism",
    "organism": "g-organism",
    "photosynthetic organisms": "g-organism",
    "photosynthetic protist": "g-organism",
    "photosynthetic protists": "g-organism",
    "microorganism": "g-organism",
    "any member of the family": "g-organism",
    "the activity of": "g-activity",
    "the action of": "g-action",
    "the process of": "g-process",
    "uppercase": "uppercase",
    "lowercase": "lowercase",
    "upper-case": "uppercase",
    "lower-case": "lowercase",
    "a building": "place",
    "a place": "place",
    "term of endearment": "endearing",
    "familiar term of endearment": "endearing familiar",
    "form of address": "term-of-address",
    "metaphor for": "metaphoric",
    "especially one who is male": "usually g-masculine",
    "originally a man": "usually g-masculine",
    "now female": "now g-feminine",
}
for k, v in gloss_tags.items():
    for t in v.split():
        if t not in valid_tags:
            print("gloss_tags contains {!r} -> {!r} with unrecognized tag {!r}"
                  .format(k, v, t))

# Convert gloss-tags to lowercase keys (needed due to case-insensitive match)
gloss_tags = {k.lower(): v for k, v in list(gloss_tags.items())}

# Regexp for finding recognized mappings from a gloss.
# Currently, key to gloss_tags is taken from m.groups(2)
gloss_tags_re = re.compile(
    r"(^|[ (])(" +
    "|".join(re.escape(x) for x in
             sorted(set(gloss_tags.keys()),
                    key=lambda x: (len(x), x),
                    reverse=True)) +
    r")($|[ ,;:).])")


def distw(titleparts, word):
    """Computes how distinct ``word`` is from the most similar word in
    ``titleparts``.  Returns 1 if words completely distinct, 0 if
    identical, or otherwise something in between."""
    assert isinstance(titleparts, (list, tuple))
    assert isinstance(word, str)
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


@functools.lru_cache(maxsize=65536)
def decode_tags(src, allow_any=False, no_unknown_starts=False):
    """Decodes tags, doing some canonicalizations.  This returns a list of
    lists of tags and a list of topics."""
    assert isinstance(src, str)

    # print("decode_tags: src={!r}".format(src))

    pos_paths = [[[]]]

    def check_unknown(to_i, from_i, i):
        assert isinstance(to_i, int)
        assert isinstance(from_i, int)
        assert isinstance(i, int)
        # Adds unknown tag if needed.  Returns new last_i
        # print("check_unknown to_i={} from_i={} i={}"
        #       .format(to_i, from_i, i))
        if from_i >= to_i:
            return []
        words = lst[from_i: to_i]
        # print("unknown words:", words)
        tag = " ".join(words)
        if not tag:
            return from_i
        if tag in ("and", "or"):
            return []

        if (not allow_any and
            not words[0].startswith("~") and
            (no_unknown_starts or
             words[0] not in allowed_unknown_starts or
             len(words) <= 1)):
            # print("ERR allow_any={} words={}"
            #       .format(allow_any, words))
            return [(from_i, "UNKNOWN",
                     ["error-unknown-tag", tag])]
        else:
            return [(from_i, "UNKNOWN", [tag])]

    # First split the tags at commas and semicolons.  Their significance is that
    # a multi-word sequence cannot continue across them.
    lst = []
    for part in split_at_comma_semi(src, extra=[";", ":"]):
        max_last_i = len(lst)
        lst1 = part.split()
        if not lst1:
            continue
        lst.extend(lst1)
        nodes = []
        for w in lst1:
            i = len(pos_paths) - 1
            new_nodes = []

            def add_new(node, start_i, last_i, new_paths):
                assert isinstance(new_paths, list)
                # print("add_new: start_i={} last_i={}".format(start_i, last_i))
                nonlocal max_last_i
                # print("$ {} last_i={} start_i={}"
                #       .format(w, last_i, start_i))
                max_last_i = max(max_last_i, last_i)
                for node2, start_i2, last_i2 in new_nodes:
                    if (node2 is node and start_i2 == start_i and
                        last_i2 == last_i):
                        break
                else:
                    new_nodes.append((node, start_i, last_i))
                if "$" in node:
                    u = check_unknown(start_i, last_i, i)
                    new_paths.extend([(last_i,
                                       node["$"].get("tags"),
                                       node["$"].get("topics"))] + u + x
                                     for x in pos_paths[last_i])
                    max_last_i = i + 1

            new_paths = []
            # print("ITER i={} w={} max_last_i={} lst={}"
            #       .format(i, w, max_last_i, lst))
            for node, start_i, last_i in nodes:
                if w in node:
                    # print("INC", w)
                    add_new(node[w], start_i, last_i, new_paths)
                if "$" in node:
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i, i, new_paths)
                if w not in node and "$" not in node:
                    # print("w not in node and $: i={} last_i={} lst={}"
                    #       .format(i, last_i, lst))
                    if (i == last_i or
                        no_unknown_starts or
                        lst[last_i] not in allowed_unknown_starts):
                        # print("NEW", w)
                        if w in valid_sequences:
                            add_new(valid_sequences[w], i, last_i, new_paths)
            if not new_nodes:
                # Some initial words cause the rest to be interpreted as unknown
                # print("not new nodes: i={} last_i={} lst={}"
                #       .format(i, max_last_i, lst))
                if (i == max_last_i or
                    no_unknown_starts or
                    lst[max_last_i] not in allowed_unknown_starts):
                    # print("RECOVER w={} i={} max_last_i={} lst={}"
                    #       .format(w, i, max_last_i, lst))
                    if w in valid_sequences:
                        add_new(valid_sequences[w], i, max_last_i, new_paths)
            nodes = new_nodes
            pos_paths.append(new_paths)

        # print("END max_last_i={} len(lst)={} len(pos_paths)={}"
        #       .format(max_last_i, len(lst), len(pos_paths)))

        if nodes:
            # print("END HAVE_NODES")
            for node, start_i, last_i in nodes:
                if "$" in node:
                    # print("$ END start_i={} last_i={}"
                    #       .format(start_i, last_i))
                    for path in pos_paths[start_i]:
                        pos_paths[-1].append([(last_i,
                                               node["$"].get("tags"),
                                               node["$"].get("topics"))] +
                                             path)
                else:
                    # print("UNK END start_i={} last_i={} lst={}"
                    #       .format(start_i, last_i, lst))
                    u = check_unknown(len(lst), last_i, len(lst))
                    for path in pos_paths[start_i]:
                        pos_paths[-1].append(u + path)
        else:
            # Check for a final unknown tag
            # print("NO END NODES max_last_i={}".format(max_last_i))
            paths = pos_paths[max_last_i] or [[]]
            u = check_unknown(len(lst), max_last_i, len(lst))
            if u:
                # print("end max_last_i={}".format(max_last_i))
                last_paths = pos_paths[-1]
                for path in list(paths):  # Copy in case it is the last pos
                    pos_paths[-1].append(u + path)

    # import json
    # print("POS_PATHS:", json.dumps(pos_paths, indent=2, sort_keys=True))

    if not pos_paths[-1]:
        # print("decode_tags: {}: EMPTY POS_PATHS[-1]".format(src))
        return [], []

    # Find the best path
    pw = []
    for path in pos_paths[-1]:
        weight = len(path)
        if any(x[1] == "UNKNOWN" for x in path):
            weight += 100  # Penalize unknown paths
        pw.append((weight, path))
    path = min(pw)[1]

    # Convert the best path to tagsets and topics
    tagsets = [[]]
    topics = []
    for i, tagspec, topicspec in path:
        if tagspec == "UNKNOWN":
            new_tagsets = []
            for x in tagsets:
                new_tagsets.append(x + topicspec)
            tagsets = new_tagsets
            continue
        if tagspec:
            new_tagsets = []
            for x in tagsets:
                for t in tagspec:
                    if t:
                        new_tags = list(x)
                        for tag in t.split():
                            if tag not in new_tags:
                                new_tags.append(tag)
                        new_tagsets.append(new_tags)
                    else:
                        new_tagsets.append(x)
            tagsets = new_tagsets
        if topicspec:
            for t in topicspec:
                for topic in t.split():
                    if topic not in topics:
                        topics.append(topic)

    # print("unsorted tagsets:", tagsets)
    tagsets = list(sorted(set(tuple(sorted(set(tags))) for tags in tagsets)))
    # topics = list(sorted(set(topics)))   XXX tests expect not sorted
    # print("decode_tags: {} -> {} topics {}".format(src, tagsets, topics))
    return tagsets, topics


def parse_head_final_tags(ctx, lang, form):
    """Parses tags that are allowed at the end of a form head from the end
    of the form.  This can also be used for parsing the final gender etc tags
    from translations and linkages."""
    assert isinstance(ctx, Wtp)
    assert isinstance(lang, str)  # Should be language that "form" is for
    assert isinstance(form, str)

    # print("parse_head_final_tags: lang={} form={!r}".format(lang, form))

    # Make sure there are no double spaces in the form as this code does not
    # handle them otherwise.
    form = re.sub(r"\s+", " ", form.strip())

    tags = []

    # If parsing for certain Bantu languages (e.g., Swahili), handle
    # some extra head-final tags first
    if lang in head_final_bantu_langs:
        m = re.search(head_final_bantu_re, form)
        if m is not None:
            tagkeys = m.group(1)
            if not ctx.title.endswith(tagkeys):
                form = form[:m.start()]
                tags.extend(head_final_bantu_map[tagkeys].split(" "))

    # If parsing for certain other languages (e.g., Lithuanian,
    # French, Finnish), handle some extra head-final tags first
    if lang in head_final_other_langs:
        m = re.search(head_final_other_re, form)
        if m is not None:
            tagkeys = m.group(1)
            if not ctx.title.endswith(tagkeys):
                form = form[:m.start()]
                tags.extend(head_final_other_map[tagkeys].split(" "))

    # Handle normal head-final tags
    m = re.search(head_final_re, form)
    if m is not None:
        tagkeys = m.group(2)  # Note: intentionally not stripped
        # print("tagkeys={}".format(tagkeys))
        # Only replace tags ending with numbers in languages that have
        # head-final numeric tags (e.g., Bantu classes); also, don't replace
        # tags if the main title ends with them (then presume they are part
        # of the word)
        # print("head_final_tags form={!r} tagkeys={!r} lang={}"
        #       .format(form, tagkeys, lang))
        if ((not tagkeys[-1].isdigit() or
             lang in head_final_numeric_langs) and
            not ctx.title.endswith(tagkeys)):
            if not tagkeys[-1].isdigit() or lang in head_final_numeric_langs:
                form = form[:m.start()]
                for t in tagkeys.split():  # Note: effectively strips
                    if t == "or":
                        continue
                    tags.extend(xlat_head_map[t].split(" "))

    # print("parse_head_final_tags: form={!r} tags={}".format(form, tags))
    return form, tags


def add_related(ctx, data, tags_lst, related):
    """Internal helper function for some post-processing entries for related
    forms (e.g., in word head)."""
    assert isinstance(ctx, Wtp)
    assert isinstance(tags_lst, (list, tuple))
    for x in tags_lst:
        assert isinstance(x, str)
    assert isinstance(related, (list, tuple))
    # print("add_related: tags_lst={} related={}".format(tags_lst, related))
    related = " ".join(related)
    if related == "[please provide]":
        return
    if related == "-":
        return

    # Split to altenratives by "or".  However, if the right side of the "or"
    # is all words that are head tags, then merge with previous alternative.
    related_alts = []
    for x in related.split(" or "):
        if not related:
            continue
        if related_alts and all(y in xlat_head_map for y in x.split(" ")):
            related_alts[-1] += " or " + x
        else:
            related_alts.append(x)

    for related in related_alts:
        m = re.match(r"\((([^()]|\([^()]*\))*)\)\s*", related)
        if m:
            paren = m.group(1)
            related = related[m.end():]
            tagsets1, topics1 = decode_tags(paren)
        else:
            tagsets1 = [[]]
            topics1 = []
        if related and related.startswith("{{"):
            ctx.debug("{{ in word head form - possible Wiktionary error: {!r}"
                      .format(related))
            continue  # Likely Wiktionary coding error
        tagsets2, topics2 = decode_tags(" ".join(tags_lst))
        for tags1 in tagsets1:
            assert isinstance(tags1, (list, tuple))
            for tags2 in tagsets2:
                assert isinstance(tags1, (list, tuple))
                if "alt-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "alt_of", {"word": related})
                elif "form-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "form_of", {"word": related})
                elif "compound-of" in tags2:
                    data_extend(ctx, data, "tags", tags1)
                    data_extend(ctx, data, "tags", tags2)
                    data_extend(ctx, data, "topics", topics1)
                    data_extend(ctx, data, "topics", topics2)
                    data_append(ctx, data, "compound", related)
                else:
                    lang = ctx.section
                    related, final_tags = parse_head_final_tags(ctx, lang,
                                                                related)
                    tags = list(tags1) + list(tags2) + list(final_tags)
                    form = {"form": related}
                    # Add tags from canonical form into the main entry
                    if "canonical" in tags:
                        for x in tags:
                            if x != "canonical":
                                data_append(ctx, data, "tags", x)
                        data_append(ctx, form, "tags", "canonical")
                        if ctx.title != related or topics1 or topics2:
                            data_append(ctx, data, "forms", form)
                    else:
                        data_extend(ctx, form, "tags", list(sorted(set(tags))))
                        data_append(ctx, data, "forms", form)
                    data_extend(ctx, form, "topics", topics1)
                    data_extend(ctx, form, "topics", topics2)
                    if topics1 or topics2:
                        ctx.debug("word head form has topics: {}".format(form))


def parse_word_head(ctx, pos, text, data):
    """Parses the head line for a word for in a particular language and
    part-of-speech, extracting tags and related forms."""
    assert isinstance(ctx, Wtp)
    assert isinstance(pos, str)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("PARSE_WORD_HEAD: {}: {}".format(ctx.section, text))

    if text.find("Lua execution error") >= 0:
        return
    if text.find("Lua timeout error") >= 0:
        return

    language = ctx.section
    title = ctx.title
    titleparts = list(m.group(0) for m in re.finditer(word_re, title))
    if not titleparts:
        return

    # Handle the part of the head that is not in parentheses
    base = re.sub(r"(\s?)\(([^()]|\([^(]*\))*\)", r"\1", text)
    base = re.sub(r"\?", " ", base)  # Removes uncertain articles etc
    base = re.sub(r"\s+", " ", base).strip()
    # print("parse_word_head: base={!r}".format(base))
    descs = split_at_comma_semi(base)
    for desc_i, desc in enumerate(descs):
        desc = desc.strip()
        if desc_i > 0 and desc.startswith("also "):
            break  # There seems to be exactly one of these, "Benen"
        for alt in desc.split(" or "):
            baseparts = list(m.group(0) for m in re.finditer(word_re, alt))
            # For non-first parts, see if it an be treated as tags-only
            if desc_i > 0:
                tagsets, topics = decode_tags(" ".join(baseparts))
                if (not any("error-unknown-tag" in x for x in tagsets) and
                    not topics):
                    for tags in tagsets:
                        data_extend(ctx, data, "tags", tags)
                    continue
            add_related(ctx, data, ["canonical"], baseparts)

    # Handle parenthesized descriptors for the word form and links to
    # related words
    parens = list(m.group(1) for m in
                  re.finditer(r"\((([^()]|\([^()]*\))*)\)", text))
    have_ruby = False
    hiragana = ""
    katakana = ""
    for paren in parens:
        paren = paren.strip()
        if not paren:
            continue

        # If it starts with hiragana or katakana, treat as such form.  Note
        # that each hiragana/katakana character is in separate parentheses,
        # so we must concatenate them.
        try:
            un = unicodedata.name(paren[0]).split()[0]
        except ValueError:
            un = "INVALID"
        if (un == "KATAKANA"):
            katakana += paren
            have_ruby = True
            continue
        if (un == "HIRAGANA"):
            hiragana += paren
            have_ruby = True
            continue

        descriptors = map_with(xlat_descs_map, [paren])
        new_desc = []
        for desc in descriptors:
            new_desc.extend(map_with(xlat_tags_map, split_at_comma_semi(desc)))
        prev_tags = None
        for desc in new_desc:
            # print("head desc: {!r}".format(desc))

            # If only one word, assume it is comma-separated alternative
            # to the previous one
            if (desc.find(" ") < 0 and
                classify_desc(desc) != "tags"):
                if prev_tags:
                    # Assume comma-separated alternative to previous one
                    add_related(ctx, data, prev_tags, [desc])
                    continue
                elif distw(titleparts, desc) <= 0.5:
                    # Similar to head word, assume a dialectal variation to
                    # the base form.  Cf. go/Alemannic German/Verb
                    add_related(ctx, data, ["alternative"], [desc])
                    continue

            m = re.match(r"^(\d+) strokes?$", desc)
            if m:
                # Special case, used to give #strokes for Han characters
                add_related(ctx, data, ["strokes"], [m.group(1)])
                continue
            m = re.match(r"^[\u2F00-\u2FDF\u2E80-\u2EFF\U00018800-\U00018AFF"
                         r"\uA490-\uA4CF\u4E00-\u9FFF]\+\d+$", desc)
            if m:
                # Special case, used to give radical + strokes for Han
                # characters
                add_related(ctx, data, ["radical+strokes"], [desc])
                prev_tags = None
                continue
            parts = list(m.group(0) for m in re.finditer(word_re, desc))
            if not parts:
                prev_tags = None
                continue

            alt_related = None
            alt_tagsets = None
            tagsets = None
            for i in range(len(parts), 0, -1):
                related = parts[i:]
                tagparts = parts[:i]
                # print("  i={} related={} tagparts={}"
                #       .format(i, related, tagparts))
                tagsets, topics = decode_tags(" ".join(tagparts),
                                              no_unknown_starts=True)
                # print("tagparts={!r} tagsets={} topics={} related={} "
                #       "alt_related={}"
                #       .format(tagparts, tagsets, topics, related,
                #               alt_related))
                if (topics or
                    any("error-unknown-tag" in x for x in tagsets)):
                    if alt_related is not None:
                        break
                    prev_tags = None
                    continue
                if (i > 1 and
                    len(parts[i - 1]) >= 4 and
                    distw(titleparts, parts[i - 1]) <= 0.4):
                    alt_related = related
                    alt_tagsets = tagsets
                    continue
                alt_related = None
                alt_tagsets = None
                break
            else:
                if alt_related is None:
                    # Check if the parenthesized part is likely a romanization
                    if ((have_ruby or classify_desc(base) == "other") and
                        classify_desc(paren) == "romanization"):
                        add_related(ctx, data, ["romanization"], [paren])
                        continue
                    tagsets = [["error-unrecognized-form"]]
                    ctx.debug("unrecognized head form: {}".format(desc))
                    continue

            if alt_related is not None:
                related = alt_related
                tagsets = alt_tagsets

            # print("FORM END: tagsets={} related={}".format(tagsets, related))
            if tagsets:
                for tags in tagsets:
                    if related:
                        add_related(ctx, data, tags, related)
                        if len(tagsets) == 1:
                            prev_tags = tags
                        else:
                            prev_tags = None
                    else:
                        data_extend(ctx, data, "tags", tags)

    # Finally, if we collected hirakana/katakana, add them now
    if hiragana:
        add_related(ctx, data, ["hiragana"], [hiragana])
    if katakana:
        add_related(ctx, data, ["katagana"], [katakana])


def parse_sense_qualifier(ctx, text, data):
    """Parses tags or topics for a sense or some other data.  The values are
    added into the dictionary ``data``."""
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    # print("parse_sense_qualifier:", text)
    lst = map_with(xlat_descs_map, [text])
    for text in lst:
        for semi in split_at_comma_semi(text):
            if not semi:
                continue
            orig_semi = semi
            idx = semi.find(":")
            if idx >= 0:
                semi = semi[:idx]
            cls = classify_desc(semi, allow_unknown_tags=True)
            # print("parse_sense_qualifier: classify_desc: {} -> {}"
            #       .format(semi, cls))
            if cls == "tags":
                tagsets, topics = decode_tags(semi)
                data_extend(ctx, data, "topics", topics)
                # XXX should think how to handle distinct options better,
                # e.g., "singular and plural genitive"; that can't really be
                # done with changing the calling convention of this function.
                for tags in tagsets:
                    data_extend(ctx, data, "tags", tags)
            elif cls == "taxonomic":
                if re.match(r"×[A-Z]", semi):
                    data_append(ctx, dt, "tags", "extinct")
                    semi = semi[1:]
                data["taxonomic"] = semi
            elif cls == "english":
                if "english" in data:
                    data["english"] += "; " + orig_semi
                else:
                    data["english"] = orig_semi
            else:
                ctx.debug("parse_sense_qualifier unrecognized qualifier: {}"
                          .format(text))


def parse_pronunciation_tags(ctx, text, data):
    assert isinstance(ctx, Wtp)
    assert isinstance(text, str)
    assert isinstance(data, dict)
    text = text.strip()
    if not text:
        return
    cls = classify_desc(text)
    notes = []
    if cls == "tags":
        tagsets, topics = decode_tags(text)
        data_extend(ctx, data, "topics", topics)
        for tagset in tagsets:
            for t in tagset:
                if t.find(" ") >= 0:
                    notes.append(t)
                else:
                    data_append(ctx, data, "tags", t)
    else:
        notes.append(text)
    if notes:
        data["note"] = "; ".join(notes)

def parse_translation_desc(ctx, lang, text, tr):
    assert isinstance(ctx, Wtp)
    assert isinstance(lang, str)  # The language of ``text``
    assert isinstance(text, str)
    assert isinstance(tr, dict)
    # print("parse_translation_desc:", text)

    # Process all parenthesized parts from the translation item
    note = None
    restore_beginning = ""
    restore_end = ""
    while True:
        beginning = False
        # See if we can find a parenthesized expression at the end
        m = re.search(r"\s*\((([^()]|\([^()]+\))+)\)\.?$", text)
        if m:
            par = m.group(1)
            text = text[:m.start()]
            if par.startswith("literally ") or par.startswith("lit."):
                continue  # Not useful for disambiguation in many idioms
        else:
            # See if we can find a parenthesized expression at the start
            m = re.match(r"^\^?\((([^()]|\([^()]+\))+)\):?(\s+|$)", text)
            if m:
                par = m.group(1)
                text = text[m.end():]
                beginning = True
                if re.match(r"^(\d|\s|,| or | and )+$", par):
                    # Looks like this beginning parenthesized expression only
                    # contains digits or their combinations.  We assume such
                    # to be sense descriptions if no sense has been selected,
                    # or otherwise just ignore them.
                    if not tr.get("sense"):
                        tr["sense"] = par
                    continue
            else:
                # No more parenthesized expressions - break out of the loop
                break

        # Some cleanup of artifacts that may result from skipping some templates
        # in earlier stages
        if par.startswith(": "):
            par = par[2:]
        if par.endswith(","):
            par = par[:-1]
        if re.match(r'^[“"]([^“”"]*)[“”"]$', par):
            par = par[1:-1]
        par = par.strip()

        # Check for special script pronunciation followed by romanization,
        # used in many Asian languages.
        lst = par.split(", ")
        if len(lst) == 2:
            a, r = lst
            if classify_desc(a) == "other":
                cls = classify_desc(r)
                # print("parse_translation_desc: r={} cls={}".format(r, cls))
                if (cls == "romanization" or
                    (cls == "english" and len(r.split()) == 1 and
                     r[0].islower())):
                    if tr.get("alt") and tr.get("alt") != a:
                        ctx.debug("more than one value in \"alt\": {} vs. {}"
                                  .format(tr["alt"], a))
                    tr["alt"] = a
                    if tr.get("roman") and tr.get("roman") != r:
                        ctx.debug("more than one value in \"roman\": "
                                  "{} vs. {}"
                                  .format(tr["roman"], r))
                    tr["roman"] = r
                    continue

        # Check for certain comma-separated tags combined with English text
        # at the beginning or end of a comma-separated parenthesized list
        while len(lst) > 1:
            cls = classify_desc(lst[0])
            if cls == "tags":
                tagsets, topics = decode_tags(lst[0])
                for t in tagsets:
                    data_extend(ctx, tr, "tags", t)
                data_extend(ctx, tr, "topics", topics)
                lst = lst[1:]
                continue
            cls = classify_desc(lst[-1])
            if cls == "tags":
                tagsets, topics = decode_tags(lst[-1])
                for t in tagsets:
                    data_extend(ctx, tr, "tags", t)
                data_extend(ctx, tr, "topics", topics)
                lst = lst[:-1]
                continue
            break
        par = ", ".join(lst)

        if not par:
            continue
        if par in ignored_parens:
            continue
        if par.startswith("Can we clean up"):
            continue
        if par.startswith("Can we verify"):
            continue
        if par.startswith("numeral:"):
            par = par[8:].strip()

        # Classify the part in parenthesis and process accordingly
        cls = classify_desc(par)
        # print("parse_translation_desc classify: {!r} -> {}"
        #       .format(par, cls))
        if par == text:
            pass
        if par == "f":
            data_append(ctx, tr, "tags", "feminine")
        elif par == "m":
            data_append(ctx, tr, "tags", "masculine")
        elif cls == "tags":
            tagsets, topics = decode_tags(par)
            for tags in tagsets:
                data_extend(ctx, tr, "tags", tags)
            data_extend(ctx, tr, "topics", topics)
        elif cls == "english":
            # If the text contains any of certain grammatical words, treat it
            # as a "note" instead of "english"
            if re.search(tr_note_re, par):
                if par.endswith(":"):
                    par = par[:-1]
                if par not in ("see entry for forms",):
                    if note:
                        note = note + ";" + par
                    else:
                        note = par
            else:
                # There can be more than one parenthesized english item, see
                # e.g. Aunt/English/Translations/Tamil
                if tr.get("english"):
                    tr["english"] += "; " + par
                else:
                    tr["english"] = par
        elif cls == "romanization":
            # print("roman text={!r} text cls={}"
            #       .format(text, classify_desc(text)))
            if (classify_desc(text) in ("english", "romanization") and
                lang not in ("Egyptian",)):
                if beginning:
                    restore_beginning += "({}) ".format(par)
                else:
                    restore_end = " ({})".format(par) + restore_end
            else:
                if tr.get("roman"):
                    ctx.debug("more than one value in \"roman\": {} vs. {}"
                              .format(tr["roman"], par))
                tr["roman"] = par
        elif cls == "taxonomic":
            if tr.get("taxonomic"):
                ctx.debug("more than one value in \"taxonomic\": {} vs. {}"
                          .format(tr["taxonomic"], par))
            if re.match(r"×[A-Z]", par):
                data_append(ctx, dt, "tags", "extinct")
                par = par[1:]
            tr["taxonomic"] = par
        elif cls == "other":
            if tr.get("alt"):
                ctx.debug("more than one value in \"alt\": {} vs. {}"
                          .format(tr["alt"], par))
            tr["alt"] = par
        else:
            ctx.debug("parse_translation_desc unimplemented cls {}: {}"
                        .format(cls, par))

    # Check for gender indications in suffix
    text, final_tags = parse_head_final_tags(ctx, lang, text)
    data_extend(ctx, tr, "tags", final_tags)

    # Restore those parts that we did not want to remove (they are often
    # optional words or words that are always used with the given translation)
    text = restore_beginning + text + restore_end

    if note:
        tr["note"] = note.strip()
    if text and text not in ignored_translations:
        tr["word"] = text.strip()

    # Sometimes gender seems to be at the end of "roman" field, see e.g.
    # fire/English/Noun/Translations/Egyptian (for "oxidation reaction")
    roman = tr.get("roman")
    if roman:
        if roman.endswith(" f"):
            data_append(ctx, tr, "tags", "feminine")
            tr["roman"] = roman[:-2].strip()
        elif roman.endswith(" m"):
            data_append(ctx, tr, "tags", "masculine")
            tr["roman"] = roman[:-2].strip()

    # If the word now has "english" field but no "roman" field, and
    # the word would be classified "other" (generally non-latin
    # characters), and the value in "english" is only one lowercase
    # word, move it to "roman".  This happens semi-frequently when the
    # translation is transliterated the same as some English word.
    roman = tr.get("roman")
    english = tr.get("english")
    if english and not roman and "word" in tr:
        cls = classify_desc(tr["word"])
        if (cls == "other" and
            english.find(" ") < 0 and
            english[0].islower()):
            del tr["english"]
            tr["roman"] = english

    # If the entry now has both tr["roman"] and tr["word"] and they have
    # the same value, delete tr["roman"] (e.g., man/English/Translations
    # Evenki)
    if tr.get("word") and tr.get("roman") == tr.get("word"):
        del tr["roman"]

    # import json
    # print("TR:", json.dumps(tr, sort_keys=True))

# Regular expression used to strip additional stuff from the end of alt_of and
# form_of.
alt_of_form_of_clean_re = re.compile(
    r"(?s)(" +
    "|".join([
        r":",
        r";",
        r" \(",
        r" - ",
        r" \(with ",
        r" with -ra/-re",
        r"\. Used ",
        r"\. Also ",
        r"\. Since ",
        r", a ",
        r", an ",
        r", the ",
        r", obsolete ",
        r", possessed",  # 'd/English
        r", imitating",  # 1/English
        r", derived from",
        r", called ",
        r", especially ",
        r", slang for ",
        ]) +
    r").*$")

def parse_alt_or_inflection_of(ctx, gloss):
    """Tries to parse an inflection-of or alt-of description.  If successful,
    this returns (tags, alt-of/inflection-of-dict).  If the description cannot
    be parsed, this returns None.  This may also return (tags, None) when the
    gloss describes a form (or some other tags were extracted from it), but
    there was no alt-of/form-of/synonym-of word."""
    # Occasionally inflection_of/alt_of have "A(n) " etc. at the beginning.
    gloss1 = gloss
    m = re.match(r"(A\(n\)|A|a|an|An|The|the) ", gloss1)
    if m:
        gloss1 = gloss1[m.end():]
    # First try parsing it as-is
    parsed = parse_alt_or_inflection_of1(ctx, gloss1)
    if parsed is not None:
        return parsed
    # Next try parsing it with the first character converted to lowercase if
    # it was previously uppercase.
    if gloss1 != gloss:
        gloss1 = gloss
    if gloss1 and gloss1[0].isupper():
        gloss1 = gloss1[0].lower() + gloss1[1:]
        parsed = parse_alt_or_inflection_of1(ctx, gloss1)
        if parsed is not None:
            return parsed
    # Cannot parse it as an alt-of/form-of/synonym-of.
    # See if we can extract something else from the gloss.
    tags = []
    for m in re.finditer(gloss_tags_re, gloss.lower()):
        k = m.group(2)
        t = gloss_tags[k]
        tags.extend(t.split())
    # Search for species names.  Can't add to gloss_tags_re, because huge
    # regexps become very slow in Python.  This does almost the same but
    # way faster.
    for m in re.finditer(r"(^|[ (])(([A-Z][a-z]+) [a-z]+)", gloss):
        k = m.group(2)
        first = m.group(3)
        if first in known_firsts or k in known_species:
            tags.append("g-organism")
    # Search for taxonomic categories
    for m in re.finditer(r"(subspecies|species|genus|genera|subfamily|"
                         "family|suborder|infraorder|phylum|"
                         r"order|clade|kingdom|taxonomic domain) [A-Z][a-z]+",
                         gloss):
        tags.append("g-organism")
    if tags:
        return tags, None
    return None

# These tags are not allowed in alt-or-inflection-of parsing
alt_infl_disallowed = set([
    "error-unknown-tag",
    "place",  # Not in inflected forms and causes problems e.g. house/English
])

def parse_alt_or_inflection_of1(ctx, gloss):
    """Helper function for parse_alt_or_inflection_of.  This handles a single
    capitalization."""
    if not gloss or not gloss.strip():
        return None

    # Prevent some common errors where we would parse something we shouldn't
    if re.match(r"(?i)form of address ", gloss):
        return None

    # First try all formats ending with "of" (or other known last words that
    # can end a form description)
    for m in reversed(list(m for m in
                           re.finditer(r" (of|for|by|as|letter|number) ",
                                       gloss))):
        desc = gloss[:m.end()]
        base = gloss[m.end():]
        tagsets, topics = decode_tags(desc, no_unknown_starts=True)
        if not topics and any(not (alt_infl_disallowed & set(ts))
                              for ts in tagsets):
            # Successfully parsed, including "of" etc.
            tags = []
            for ts in tagsets:
                if not (alt_infl_disallowed & set(ts)):
                    tags.extend(ts)
            if ("alt-of" in tags or
                "form-of" in tags or
                "synonym-of" in tags or
                "compound-of" in tags):
                break
        elif m.group(1) == "of":
            # Try parsing without the final "of".  This is commonly used in
            # various form-of expressions.
            desc = gloss[:m.start()]
            base = gloss[m.end():]
            tagsets, topics = decode_tags(desc, no_unknown_starts=True)
            if (not topics and
                any(not (alt_infl_disallowed & set(t)) for t in tagsets)):
                tags = ["form-of"]
                for t in tagsets:
                    if not (alt_infl_disallowed & set(t)):
                        tags.extend(t)
                break

    else:
        # Did not find a form description based on last word; see if the
        # whole description is tags
        tagsets, topics = decode_tags(gloss, no_unknown_starts=True)
        if (not topics and
            any("error-unknown-tag" not in t for t in tagsets)):
            tags = []
            for t in tagsets:
                if "error-unknown-tag" not in t:
                    tags.extend(t)
            base = ""
        else:
            return None

    # It is fairly common for form_of glosses to end with something like
    # "ablative case" or "in instructive case".  Parse that ending.
    # print("parse_alt_or_inflection_of: lst={}".format(lst))
    base = base.strip()
    lst = base.split()
    if len(lst) >= 3 and lst[-1] in ("case", "case."):
        node = valid_sequences.get(lst[-2])
        if node and "$" in node:
            for t in node["$"].get("tags", ()):
                tags.extend(t.split(" "))
            lst = lst[:-2]
            if lst[-1] == "in" and len(lst) > 1:
                lst = lst[:-1]

    tags = list(sorted(set(t for t in tags if t)))
    # Clean up some extra stuff from the linked word
    orig_base = base
    base = re.sub(alt_of_form_of_clean_re, "", orig_base)
    base = re.sub(r" [(⟨][^()]*[)⟩]", "", base)  # Remove all (...) groups
    extra = orig_base[len(base):]
    extra = re.sub(r"^[- :;.,，—]+", "", extra)
    if extra.endswith(".") and extra.count(".") == 1:
        extra = extra[:-1].strip()
    m = re.match(r"^\(([^()]*)\)$", extra)
    if m:
        extra = m.group(1)
    else:
        # These weird backets used in "slash mark"
        m = re.match(r"^⟨([^()]*)⟩$", extra)
        if m:
            extra = m.group(1)
    m = re.match(r'^[“"]([^"“”]*)["”]$', extra)
    if m:
        extra = m.group(1)
    # Note: base might still contain comma-separated values and values
    # separated by "and"
    base = base.strip()
    if base.endswith("."):
        base = base[:-1]
    if base.endswith("(\u201cconjecture\")"):
        base = base[:-14].strip()
        tags.append("conjecture")
    if base.endswith("."):
        base = base[:-1].strip()
    base = base.strip()
    if not base:
        return tags, None
    parts = split_at_comma_semi(base, extra=[" / ",  "／"])
    if (len(parts) <= 1 or base.startswith("/") or
        base.endswith("/") or
        ctx.title.find("/") >= 0):
        parts = [base]
    lst = []
    for p in parts:
        # Check for some suspicious base forms
        m = re.find(r"[.,{}()]", p)
        if m and not ctx.page_exists(p):
            ctx.debug("suspicious alt_of/form_of with {!r}: {}"
                      .format(m.group(0), p))

        dt = { "word": p }
        if extra:
            dt["extra"] = extra
        lst.append(dt)
    # print("alt_or_infl_of returning tags={} lst={} base={!r}"
    #       .format(tags, lst, base))
    return tags, lst


@functools.lru_cache(maxsize=65536)
def classify_desc(desc, allow_unknown_tags=False, no_unknown_starts=False):
    """Determines whether the given description is most likely tags, english,
    a romanization, or something else.  Returns one of: "tags", "english",
    "romanization", or "other".  If ``allow_unknown_tags`` is True, then
    allow "tags" classification even when the only tags are those starting
    with a word in allowed_unknown_starts. """
    assert isinstance(desc, str)
    # Empty and whitespace-only strings are treated as "other"
    desc = desc.strip()
    if not desc:
        return "other"

    # If it can be fully decoded as tags without errors, treat as tags
    tagsets, topics = decode_tags(desc, no_unknown_starts=no_unknown_starts)
    for tagset in tagsets:
        assert isinstance(tagset, (list, tuple, set))
        if ("error-unknown-tag" not in tagset and
            (topics or allow_unknown_tags or
             any(x.find(" ") < 0 for x in tagset))):
            return "tags"

    # Check if it looks like the taxonomic name of a species
    if desc in known_species:
        return "taxonomic"
    desc1 = re.sub(r"^×([A-Z])", r"\1", desc)
    desc1 = re.sub(r"\s*×.*", "", desc1)
    lst = desc1.split()
    if len(lst) > 1 and len(lst) <= 5 and lst[0] in known_firsts:
        have_non_english = lst[0].lower() not in english_words
        for x in lst[1:]:
            if x in ("A", "B", "C", "D", "E", "F", "I", "II", "III", "IV", "V"):
                continue
            if x[0].isupper():
                break
            if x not in english_words:
                have_non_english = True
        else:
            # Starts with known taxonomic term, does not contain uppercase
            # words (except allowed letters) and at least one word is not
            # English
            if have_non_english:
                return "taxonomic"

    # If all words are in our English dictionary, interpret as English
    if desc.isascii() and len(desc) > 1:
        if desc in english_words and desc[0].isalpha():
            return "english"   # Handles ones containing whitespace
        tokens = tokenizer.tokenize(desc)
        if not tokens:
            return "other"
        lst = list(x not in not_english_words and
                   not x.isdigit() and
                   (x in english_words or x.lower() in english_words or
                    x in known_firsts or
                    x[0].isdigit() or
                    # (x[0].isupper() and x.find("-") < 0 and x.isascii()) or
                   (x.endswith("s") and len(x) >= 4 and
                    x[:-1] in english_words) or  # Plural
                    (x.endswith("ies") and len(x) >= 5 and
                     x[:-3] + "y" in english_words) or  # E.g. lily - lilies
                    (x.endswith("ing") and len(x) >= 5 and
                     x[:-3] in english_words) or  # E.g. bring - bringing
                    (x.endswith("ing") and len(x) >= 5 and
                     x[:-3] + "e" in english_words) or  # E.g., tone - toning
                    (x.endswith("ed") and len(x) >= 5 and
                     x[:-2] in english_words) or   # E.g. hang - hanged
                    (x.endswith("ed") and len(x) >= 5 and
                     x[:-2] + "e" in english_words) or  # E.g. atone - atoned
                    (x.endswith("'s") and x[:-2] in english_words) or
                    (x.endswith("s'") and x[:-2] in english_words) or
                    (x.endswith("ise") and len(x) >= 5 and
                     x[:-3] + "ize" in english_words) or
                    (x.endswith("ised") and len(x) >= 6 and
                     x[:-4] + "ized" in english_words) or
                    (x.endswith("ising") and len(x) >= 7 and
                     x[:-5] + "izing" in english_words) or
                    (x.find("-") >= 0 and all((y in english_words or not y)
                                             for y in x.split("-"))))
                   for x in tokens)
        cnt = lst.count(True)
        if (any(lst[i] and x[0].isalpha() and len(x) > 1
                for i, x in enumerate(tokens)) and
            not desc.startswith("-") and
            not desc.endswith("-") and
            re.search(r"\w+", desc) and
            (cnt == len(lst) or
             (any(lst[i] and len(x) > 3 for i, x in enumerate(tokens)) and
              cnt >= len(lst) - 1) or
             cnt / len(lst) >= 0.8)):
            return "english"
    # Some translations have apparent pronunciation descriptions in /.../
    # which we'll put in the romanization field (even though they probably are
    # not exactly romanizations).
    if desc.startswith("/") and desc.endswith("/"):
        return "romanization"
    # If all characters are in classes that could occur in romanizations,
    # treat as romanization
    classes = list(unicodedata.category(x)
                   if x not in ("-", ",", ":", "/", '"') else "OK"
                   for x in unicodedata.normalize("NFKD", desc))
    classes1 = []
    num_latin = 0
    num_greek = 0
    for ch, cl in zip(desc, classes):
        if ch in ("'",  # ' in Arabic, / in IPA-like parenthesized forms
                  ".",  # e.g., "..." in translations
                  ";",
                  ":",
                  "!",
                  "‘",
                  "’",
                  '"',
                  '“',
                  '”',
                  "/",
                  "…",  # alternative to "..."
                  "⁻",  # superscript -, used in some Cantonese roman, e.g. "we"
                  "ʹ"):  # ʹ e.g. in understand/English/verb Russian transl
            classes1.append("OK")
            continue
        if cl not in ("Ll", "Lu"):
            classes1.append(cl)
            continue
        try:
            name = unicodedata.name(ch)
            first = name.split()[0]
            if first == "LATIN":
                num_latin += 1
            elif first == "GREEK":
                num_greek += 1
            elif first == "COMBINING":  # Combining diacritic
                cl = "OK"
            elif re.match(non_latin_scripts_re, name):
                cl = "NO"  # Not acceptable in romanizations
        except ValueError:
            cl = "NO"  # Not acceptable in romanizations
        classes1.append(cl)
    # print("classify_desc: {!r} classes1: {}".format(desc, classes1))
    if all(x in ("Ll", "Lu", "Lt", "Lm", "Mn", "Mc", "Zs", "Nd", "OK")
           for x in classes1):
        if ((num_latin >= num_greek + 2 or num_greek == 0) and
            classes1.count("OK") < len(classes1) and
            classes1.count("Nd") < len(classes1)):
            return "romanization"
    # Otherwise it is something else, such as hanji version of the word
    return "other"

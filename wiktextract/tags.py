# -*- fundamental -*-
#
# Lists of valid tags and mappings for tags canonicalization.
#
# Copyright (c) 2020-2022 Tatu Ylonen.  See file LICENSE and https://ylonen.org

# Mappings for tags in template head line ends outside parentheses.  These are
# also used to parse final tags from translations.
xlat_head_map = {
    "m": "masculine",
    "f": "feminine",
    "m/f": "masculine feminine",
    "m./f.": "masculine feminine",
    "m or f": "masculine feminine",
    "m or n": "masculine neuter",
    "m or c": "masculine common-gender",
    "f or m": "feminine masculine",
    "f or n": "feminine neuter",
    "f or n.": "feminine neuter",  # fimmtíu/Icelandig
    "f or c": "feminine common-gender",  # sustainability/Tr/Norwegian
    "n or f": "neuter feminine",
    "n or m": "neuter masculine",
    "n or c": "neuter common-gender",
    "c or m": "common-gender masculine",
    "c or f": "common-gender feminine",  # picture book/Tr/Norwegian
    "c or n": "common-gender neuter",  # ethylene/Eng/Tr/Danish
    "m or f or n": "masculine feminine neuter",
    "f or m or n": "feminine masculine neuter",
    "m or f or c": "masculine feminine common-gender",
    "f or m or c": "feminine masculine common-gender",
    "m or c or n": "masculine common-gender neuter",
    "f or c or n": "feminine common-gender neuter",
    "m or n or c": "masculine neuter common-gender",
    "f or n or c": "feminine neuter common-gender",
    "c or f or n": "common-gender feminine neuter",
    "c or m or n": "common-gender masculine neuter",
    "n or f or c": "neuter feminine common-gender",
    "n or m or c": "neuter masculine common-gender",
    "n or m or f": "neuter masculine feminine",
    "n or f or m": "neuter feminine masculine",
    "c or m or f": "common-gender masculine feminine",
    "c or f or m": "common-gender masculine feminine",
    "m or c or n": "masculine common-gender neuter",
    "f or n or m": "feminine neuter masculine",
    "m or n or f": "masculine neuter feminine",
    "f or c or m": "feminine common-gender masculine",
    "m or c or f": "masculine common-gender feminine",
    "m or f or m": "?masculine feminine",  # fantasma,soldado/Portuguese
    "m pl": "masculine plural",
    "f pl": "feminine plural",
    "n pl": "neuter plural",
    "m sg": "masculine singular",
    "f sg": "feminine singular",
    "n sg": "neuter singular",
    "f or pl": "feminine singular plural",  # XXX information/Eng/Tr/Latgalian
    "m or pl": "masculine singular plural",  # XXX information/Eng/Tr/Latgalian
    "n or pl": "neuter singular plural",  # XXX table scrap/Tr/Greek
    "c or pl": "common-gender singular plural",
    "pl or f": "feminine singular plural",  # XXX grit/Eng/Tr(husked...)/German
    "pl or m": "masculine singular plural",
    "pl or n": "neuter singular plural",  # ordnance/Tr/German
    "pl or c": "common-gender singular plural",  # "you don't say"/Tr/Romanian
    "sg or f": "singular feminine",
    "sg or m": "singular masculine",
    "sg or n": "singular neuter",
    "sg or c": "singular common-gender",
    "m or sg": "masculine singular",
    "f or sg": "feminine singular",
    "m or sg": "neuter singular",
    "c or sg": "common-gender singular",
    "m or pl": "masculine plural",
    "f or pl": "feminine plural",
    "n or pl": "neuter plural",
    "c or pl": "common-gender plural",
    "m or f pl": "masculine feminine plural",
    "c or n or n pl": "common-gender neuter singular plural",  # XXX augmentation/Tr
    "pl or m or f": "masculine feminine singular plural",  # XXX suc* my co*/Tr
    "m or f or sg or pl": "masculine feminine singular plural",  # Ainu/Russian
    "m or f or pl": "masculine feminine plural",  # that/Tr/Dutch
    "m or f sg": "masculine feminine singular",
    "pl or f or m or n": "",  # Sindhi/Tr(language)/Spanish
    "pl or f or n": "masculine feminine neuter plural singular singular",  # XXX
    # crush/Portuguese head
    "m or m f": "?masculine feminine",
    # beginner/Eng/Tr/Polish
    "m or m pl": "masculine singular plural",
    "f or f pl": "feminine singular plural",
    "n or n pl": "neuter singular plural",
    "c or c pl": "common-gender singular plural",
    "f pl or n pl": "feminine neuter plural",  # diurnal/Eng/Tr/Polish
    "f pl or n or n pl": "feminine neuter singular plural",  # veneral/Tr/Polish
    "m or m pl or f or f pl or n or n pl": "",  # "a lot"/Tr/Latin
    "pl or n or n pl": "neuter singular plural",  # salt/Tr/Greek
    "f or f": "feminine",
    "topo.": "toponymic",  # E.g., p/Egyptian
    "n": "neuter",
    "m or n or f": "masculine neuter feminine",  # cataract/Tr/Dutch
    "c": "common-gender",  # common gender in at least West Frisian
    "sg": "singular",
    "pl": "plural",
    "pl or sg": "plural singular",
    "sg or pl": "singular plural",
    "m sg or m pl": "masculine singular plural",  # valenki/Tr/German
    "f sg or f pl": "feminine singular plural",
    "n sg or n pl": "neuter singular plural",
    "c sg or c pl": "common-gender singular plural",
    "m pl or f pl": "masculine feminine plural",  # comedian/English/Tr/Welsh
    "m pl or n pl": "masculine neuter plural",  # whose/Tr/Latin
    "m pl or n": "?masculine neuter plural singular",  # pimpernel/Tr/Bulgarian
    "m sg or f sg": "masculine singular feminine",  # your/Eng/Tr/Walloon
    "f sg or m sg": "masculine singular feminine",  # your/Eng/Tr/Walloon
    "n sg or n sg": "masculine singular feminine",  # your/Eng/Tr/Walloon
    # copacetic/English/Tr/Hebrew:
    "m or m pl or f or f pl": "masculine feminine singular plural",
    # your/Eng/Tr/Norwegian:
    "m pl or f pl or n pl": "masculine feminine neuter plural",
    "m sg or f sg or n sg": "masculine feminine neuter singular",
    "m pl or f or f pl": "masculine feminine singular plural",
    "c or c pl": "common-gender singular plural",
    "c pl or n pl": "common-gender neuter plural",  # which/Tr/Danish
    "inan": "inanimate",
    "Inanimate": "inanimate",  # e.g., "James Bay"/English/Tr/Northern East Cree
    "inan or anim": "inanimate animate",
    "anim or inan": "animate inanimate",
    "anim": "animate",
    "f anim": "feminine animate",
    "m anim": "masculine animate",
    "n anim": "neuter animate",
    "f inan": "feminine inanimate",
    "m inan": "masculine inanimate",
    "n inan": "neuter inanimate",
    "f anim sg": "feminine animate singular",
    "m anim sg": "masculine animate singular",
    "n anim sg": "neuter animate singular",
    "f inan sg": "feminine inanimate singular",
    "m inan sg": "masculine inanimate singular",
    "n inan sg": "neuter inanimate singular",
    "f anim pl": "feminine animate plural",
    "m anim pl": "masculine animate plural",
    "n anim pl": "neuter animate plural",
    "f inan pl": "feminine inanimate plural",
    "m inan pl": "masculine inanimate plural",
    "n inan pl": "neuter inanimate plural",
    "f anim or f inan": "feminine animate inanimate",
    "f inan or f anim": "feminine inanimate animate",
    "m anim or m inan": "masculine animate inanimate",
    "m inan or m anim": "masculine inanimate animate",
    "m anim or f anim": "masculine animate feminine",
    "f anim or m anum": "feminine animate masculine",
    "f inan or f inan pl": "feminine inanimate singular plural",
    "m inan or m inan pl": "masculine inanimate singular plural",
    "n inan or n inan pl": "neuter inanimate singular plural",
    "n inan or m inan": "neuter masculine inanimate",
    "f anim or f anim pl": "feminine animate singular plural",
    "m anim or m anim pl": "masculine animate singular plural",
    "n anim or n anim pl": "neuter animate singular plural",
    "f anim or m anim": "feminine animate masculine",
    "f inan or n inan": "feminine inanimate neuter",
    "m inan pl or m anim pl": "masculine inanimate animate plural",
    "f inan or m inan": "feminine masculine inanimate",
    "f inan or m inan or f inan pl":
    "feminine masculine inanimate singular plural",
    "f inan or m inan or f inan pl or m inan pl":
    "feminine masculine inanimate singular plural",
    "m inan pl or m anim pl or f anim pl":
    "masculine feminine inanimate animate plural",
    "f anim or f inan or f anim pl":
    "feminine animate inanimate singular plural",
    "f anim or f inan or f anim pl or f inan pl":
    "feminine animate inanimate singular plural",
    "f anim pl or f inan or f inan pl":
    "feminine animate inanimate singular plural",  # XXX
    "f inan pl or f anim or f anim pl":
    "feminine inanimate animate singular plural",  # XXX
    "f anim or f anim pl or f inan":
    "feminine animate inanimate singular plural",
    "f anim or f anim pl or f inan or f inan pl":
    "feminine animate inanimate singular plural",
    "m anim pl or f anim pl": "masculine feminine animate plural",
    "m anim pl or f anim pl or f inan or f inan pl":
    "masculine animate plural feminine inanimate",
    "m anim pl or f anim pl or f inan":
    "masculine animate feminine plural inanimate singular",  # XXX
    "f anim pl or f inan pl": "feminine animate inanimate plural",
    "f anim pl or f inan pl or m anim pl":
    "feminine masculine animate inanimate plural",
    "m anim pl or f anim pl or f inan pl":
    "masculine animate feminine plural inanimate",  # XXX
    "f inan pl or m anim pl": "feminine masculine animate inanimate plural",
    "f inan pl or m anim pl or f anim pl":
    "masculine animate feminine plural inanimate",  # XXX
    "m anim or f anim or m anim pl":
    "masculine animate feminine singular plural",
    "m anim or f anim or m anim pl or f anim pl":
    "masculine animate feminine singular plural",
    "n inan or n anim or m inan or m anim":
    "neuter inanimate animate masculine",
    "m anim pl or f anim pl or m anim or f anim":
    "masculine animate plural feminine singular",
    "m anim pl or f inan or f inan pl":
    "masculine animate plural feminine inanimate singular",  # XXX
    "m anim or n inan": "masculine animate neuter inanimate",  # XXX
    "n inan pl or m inan or m inan pl":
    "neuter inanimate plural masculine singular plural",  # XXX
    "n inan pl or f inan or f inan pl":
    "neuter inanimate plural feminine singular",  # XXX
    "f inan pl or m anim or m anim pl":
    "feminine inanimate plural masculine animate singular",  # XXX
    "f inan pl or m inan or m inan pl":
    "feminine inanimate plural masculine singular",  # XXX
    "n anim": "neuter animate",
    "n anim pl or n inan or n inan pl":
    "neuter animate plural inanimate singular",  # XXX
    "n inan or n inan pl or f inan or f inan pl":
    "neuter inanimate singular plural feminine",
    "n inan pl or n anim or n anim pl":
    "neuter inanimate plural animate singular",  # XXX
    "n anim or n inan": "neuter animate inanimate",
    "pers": "person",  # XXX check what this really is used for? personal?
    "npers": "impersonal",
    "f pers": "feminine person",
    "m pers": "masculine person",
    "f pers or f pers pl": "feminine person singular plural",
    "m pers or m pers pl": "masculine person singular plural",
    "m pers or f pers": "masculine person feminine",
    "f pers or m pers": "feminine person masculine",
    "m pers or n pers": "masculine person neuter",
    "f pers or n pers": "feminine person neuter",
    "m pers or m anim": "masculine person animate",
    "m pers or m inan": "masculine person inanimate",
    "f pers or f anim": "feminine person animate",
    "f pers or f inan": "feminine person inanimate",
    "m pers or f": "masculine person feminine",
    "m inan or m pers": "masculine inanimate person",
    "m or m pers or f": "masculine inanimate animate person feminine",  # XXX
    "m anim or m pers": "masculine animate person",
    "f anim or f pers": "feminine animate person",
    "n anim or n pers": "neuter animate person",
    "m pers or n": "masculine person neuter animate inanimate",  # XXX
    "m pers or f": "masculine person feminine animate inanimate",  # XXX
    "vir": "virile",
    "nvir": "nonvirile",
    "anml": "animal-not-person",
    "f anml": "feminine animal-not-person",
    "m anml": "masculine animal-not-person",
    "f animal": "feminine animal-not-person",
    "m animal": "masculine animal-not-person",
    "m animal or f animal": "masculine animal-not-person feminine",
    "f animal or m animal": "feminine animal-not-person masculine",
    "m anim or f": "masculine animate feminine inanimate",
    "impf": "imperfective",
    "impf.": "imperfective",
    "pf": "perfective",
    "pf.": "perfective",
    "impf or impf": "imperfective",
    "impf or pf": "imperfective perfective",  # ought/Eng/Tr/Serbo-Croatian
    "pf or impf": "perfective imperfective",  # start/Tr(of an activity)/Russian
    "invariable": "invariable",
    "n.": "noun",
    "v.": "verb",
    "adj.": "adjective",
    "adv.": "adverb",
    "adversative": "",
    "?": "",
    "1.": "first-person",
    "2.": "second-person",
    "3.": "third-person",
    "1": "class-1",
    "1a": "class-1a",
    "2": "class-2",
    "2a": "class-2a",
    "3": "class-3",
    "4": "class-4",
    "5": "class-5",
    "6": "class-6",
    "7": "class-7",
    "8": "class-8",
    "9": "class-9",
    "9a": "class-9a",
    "10": "class-10",
    "10a": "class-10a",
    "11": "class-11",
    "12": "class-12",
    "13": "class-13",
    "14": "class-14",
    "15": "class-15",
    "16": "class-16",
    "17": "class-17",
    "18": "class-18",
    "1/2": "class-1 class-2",
    "3/4": "class-3 class-4",
    "5/6": "class-5 class-6",
    "7/8": "class-7 class-8",
    "9/10": "class-9 class-10",
    "15/17": "class-15 class-17",
    "1 or 2": "class-1 class-2",
    "1a or 2a": "class-1a class-2a",
    "1a or 2": "class-1a class-2",
    "3 or 4": "class-3 class-4",
    "5 or 6": "class-5 class-6",
    "7 or 8": "class-7 class-8",
    "9 or 10": "class-9 class-10",
    "9a or 10a": "class-9a class-10a",
    "15 or 17": "class-15 class-17",
    "9/10 or 1/2": "class-9 class-10 class-1 class-2",
    # two/Tr/Kikuyu
    "2 or 4 or 6 or 13": "class-2 class-4 class-6 class-13",
    "8 or 10": "class-8 class-10",  # two/Tr/Kikuyu
    "11 or 10": "class-11 class-10",  # sea/Eng/Tr/Zulu
    "11 or 10a": "class-11 class-10a",  # half/Ngazidja Comorian
    "10 or 11": "class-10 class-11",  # mushroom/Tr/Swahili
    "11 or 14": "class-11 class-14",  # country/Tr/Swahili
    "11 or 12": "class-11 class-12",  # theater/Tr/Swahili
    "11 or 6": "class-11 class-6",   # leaf/'Maore Comorian
    "9 or 6": "class-9 class-6",  # birthday,carrot/Tr/Rwanda-Rundi
    "1 or 6": "class-2 class-6",  # Zulu/Tr/Zulu
    "6 or 7": "class-6 class-7",  # spider/Eng/Tr/Lingala ???
    "15 or 6": "class-15 class-6",  # leg/Tr/Rwanda-Rundi
    "14 or 6": "class-14 class-6",  # rainbow/Tr/Chichewa
    "9 or 9": "?class-9",  # XXX bedsheet/Tr/Sotho
    "m1": "masculine declension-1",
    "f2": "feminine declension-2",
    "m2": "masculine declension-2",
    "f3": "feminine declension-3",
    "m3": "masculine declension-3",
    "f4": "feminine declension-4",
    "m4": "masculine declension-4",
    "f5": "feminine declension-5",
    "m5": "masculine declension-5",
    "[uncountable]": "uncountable",
    "is more colloquial": "colloquial",
    "(plural f)": "singular plural feminine",  # XXX chromicas/Galician
    "(plural m)": "singular plural masculine",  # XXX Genseric/Galician
    "2 or 3": "?class-2 class-3",  # XXX branch/Tr/Swahili
    "m or impf": "masculine imperfective",  # pour/Tr/Ukrainian
    "f or impf": "feminine imperfective",  # fuc* around/Tr/(s with many)/Czech
    "n or impf": "neuter imperfective",  # glom/Russian
    "f or pf": "feminine perfective",
    "m or pf": "masculine perfective",
    "n or pf": "neuter perfective",
    "m or m": "?masculine",  # Paul/Tr(male given name)/Urdu
    "f or c pl": "?feminine common-gender singular plural",  # mulberry/Tr/Zazaki
    "c pl or n": "?common-gender neuter singular plural",  # mouthpiece/Tr/Swedish
    "impf or impf": "imperfective",
    "pf or pf": "?perfective",
    "sg or sg": "?singular",
    "pl or pl": "?plural",
    "c or impf": "?common-gender imperfective",
    "m inan or n": "masculine inanimate neuter",
    "m inan or f": "masculine inanimate feminine",
    "pl or pf": "?plural perfective",
    "m pl or pf": "masculine plural perfective",
    "f pl or pf": "feminine plural perfective",
    "n pl or pf": "neuter plural perfective",
    "f pl or impf": "feminine plural imperfective",
    "m pl or impf": "masculine plural imperfective",
    "n pl or impf": "neuter plural imperfective",
    "m or f or impf": "?masculine feminine imperfective",
    "pl or m or f or n": "?plural masculine feminine neuter",
    "no perfect or supine stem": "no-perfect no-supine",
}

# Languages that can have head-final numeric class indicators.  They are mostly
# used in Bantu languages.  We do not want to interpret them at the ends of
# words like "Number 11"/English.  Also, some languages have something like
# "stress pattern 1" at the end of word head, which we also do not want to
# interpret as class-1.
head_final_numeric_langs = set([
    "Bende",
    "Chichewa",
    "Chimwiini",
    "Dyirbal",  # Australian aboriginal, uses class-4 etc
    "Kamba",
    "Kikuyu",
    "Lingala",
    "Luganda",
    "Maore Comorian",
    "Masaba",
    "Mwali Comorian",
    "Mwani",
    "Ngazidja Comorian",
    "Northern Ndebele",
    "Nyankole",
    "Phuthi",
    "Rwanda-Rundi",
    "Sotho",
    "Shona",
    "Southern Ndebele",
    "Swahili",
    "Swazi",
    "Tsonga",
    "Tswana",
    "Tumbuka",
    "Xhosa",
    "Zulu",
    "ǃXóõ",
])

# Languages for which to consider head_final_extra_map
head_final_bantu_langs = set([
    # XXX should other Bantu languages be included here?  Which ones use
    # suffixes such as "m or wa"?
    "Swahili",
])

head_final_bantu_map = {
    # These are only handled in parse_head_final_tags
    # and will generally be ignored elsewhere.  These may contain spaces.

    # Swahili class indications.
    "m or wa": "class-1 class-2",
    "m or mi": "class-3 class-4",
    "ma": "class-5 class-6",
    "ki or vi": "class-7 class-8",
    "n": "class-9 class-10",
    "u": "class-11 class-12 class-14",
    "ku": "class-15",
    "pa": "class-16",
    "mu": "class-18",

    # XXX these are probably errors in Wiktionary, currently ignored
    "n or n": "?",  # Andromeda/Eng/Tr/Swahili etc
    "m or ma": "?",  # environment/Eng/Tr/Swahili etc
    "u or u": "?",  # wife/Eng/Tr/Swahili
}

head_final_semitic_langs = set([
    "Akkadian",
    "Amharic",
    "Arabic",
    "Aramaic",
    "Eblaite",
    "Hebrew",
    "Hijazi Arabic",
    "Maltese",
    "Moroccan Arabic",
    "Phoenician",
    "South Levantine Arabic",
    "Tigre",
    "Tigrinya",
    "Ugaritic",
])

head_final_semitic_map = {
    "I": "form-i",
    "II": "form-ii",
    "III": "form-iii",
    "IV": "form-iv",
    "V": "form-v",
    "VI": "form-vi",
    "VII": "form-vii",
    "VIII": "form-viii",
    "IX": "form-ix",
    "X": "form-x",
    "XI": "form-xi",
    "XII": "form-xii",
    "XIII": "form-xiii",
    "Iq": "form-iq",
    "IIq": "form-iiq",
    "IIIq": "form-iiiq",
    "IVq": "form-ivq",
}

head_final_other_langs = set([
    "Finnish",
    "French",
    "Lithuanian",
    "Arabic",
    "Armenian",
    "Zazaki",
    "Hebrew",
    "Hijazi Arabic",
    "Moroccan Arabic",
    "Nama",
    "Old Church Slavonic",
    "Gothic",
    "Old Irish",
    "Latin",
    "Scottish Gaelic",
    "Slovene",
    "Sorbian",
    "South Levantine Arabic",
    "Kajkavian",
    "Chakavian",
    "Croatian",  # Kajkavian and Chakavian are forms of Croatian
    "Sanskrit",
    "Ancient Greek",
    # XXX For dual??? see e.g. route/Tr(course or way)/Polish
    "Dyirbal",
    "Egyptian",
    "Maltese",
    "Maori",
    "Polish",
    "Portuguese",
    "Romanian",  # cache,acquaintance/Tr/Romanian
    "Ukrainian",
    "Ugaritic",
])

head_final_other_map = {
    # This is used in Finnish at the end of some word forms (in translations?)
    "in indicative or conditional mood": "in-indicative in-conditional",

    # marine/French Derived terms
    "f colloquial form of a feminine marin": "feminine colloquial",

    # These stress pattern indicators occur in Lithuanian
    "stress pattern 1": "stress-pattern-1",
    "stress pattern 2": "stress-pattern-2",
    "stress pattern 3": "stress-pattern-3",
    "stress pattern 3a": "stress-pattern-3a",
    "stress pattern 3b": "stress-pattern-3b",
    "stress pattern 4": "stress-pattern-4",
    "stress pattern: 1": "stress-pattern-1",
    "stress pattern: 2": "stress-pattern-2",
    "stress pattern: 3": "stress-pattern-3",
    "stress pattern: 3a": "stress-pattern-3a",
    "stress pattern: 3b": "stress-pattern-3b",
    "stress pattern: 4": "stress-pattern-4",

    # These are specific to Arabic, Armenian, Zazaki, Hebrew, Nama,
    # Old Church Slavonic, Gothic, Old Irish, Latin, Scotish Gaelic,
    # Slovene, Sorbian, Kajkavian, Chakavian, (Croatian), Sanskrit,
    # Ancient Greek
    # (generally languages with a dual number)
    "du": "dual",
    "du or pl": "dual plural",  # aka duoplural
    "m du": "masculine dual",
    "f du": "feminine dual",
    "n du": "neuter dual",
    "m du or f du": "masculine feminine dual",  # yellow/Tr/Zazaki
    "f du or m du": "feminine masculine dual",
    "n du or n pl": "neuter dual plural",
    "f du or f pl": "feminine dual plural",
    "m du or m pl": "masculine dual plural",
    "du or f du or n": "?",  # XXX guest/Tr/Zazaki
    "du or n or pf": "?",  # XXX how would this be expressed
    "du or n du": "neuter dual",  # bilberry/Tr/Zazaki
    "du or f du or n": "",  # XXX guest/Tr(patron)/Zazaki
    "pl or pf": "?plural perfective",  # walk/Tr(to steal)/Russian
    "m or pf": "?masculine perfective",  # boom/Tr(make book)/Russian
    "n or n du": "neuter singular dual",
    # XXX clump/Tr/Portuguese
    "sg or m du": "singular feminine neuter masculine dual",
    "m du or f du or n du": "masculine dual feminine neuter",
    "du or m": "?dual masculine",
}

# Accepted uppercase tag values.  As tags these are represented with words
# connected by hyphens.  These are classified as dialect tags; if an uppercase
# is not a dialect tag, then it should be listed separately in valid_tags.
uppercase_tags = set([
    "A Estierna",
    "AF",  # ??? what does this mean
    "ALUPEC",
    "ASL gloss",  # Used with sign language heads
    "Aargau",
    "Abagatan",
    "Absheron",
    "Abung/Kotabumi",
    "Abung/Sukadana",
    "Abzakh",
    "Acadian",
    "Achaemenid",
    "Achterhooks",
    "Adana",
    "Adyghe",
    "Aeolic",
    "Affectation",
    "Afi-Amanda",
    "Africa",
    "African-American Vernacular English",
    "Afrikaans",
    "Afyonkarahisar",
    "Agdam",
    "Ağrı",
    "Akhmimic",
    "Aknada",
    "Al-Andalus",
    "Ala-Laukaa",
    "Alak",
    "Alemannic",  # Variant of German
    "Alemannic German",  # Variant of German
    "Algherese",
    "Alles",
    "Alliancelles",
    "Alsace",
    "Alsatian",
    "Alviri",  # Variant of Alviri-Vidari
    "Amecameca",
    "American continent",
    "Americanization",
    "Amerindish",
    "Amianan",
    "Amira",
    "Amrum",
    "Amur",
    "Anbarani",  # Variant of Talysh
    "Ancient",
    "Ancient China",
    "Ancient Egyptian",
    "Ancient Greek",
    "Ancient Rome",
    "Ancient Roman",
    "Andalucia",
    "Andalusia",
    "Andalusian",
    "Anglian",
    "Anglicised",
    "Anglicism",
    "Anglism",
    "Anglo-Latin",
    "Anglo-Norman",
    "Angola",
    "Aniwa",
    "Anpezan",  # Variant of Ladin
    "Antalya",
    "Antanosy",
    "Antilles",
    "Appalachia",
    "Appalachian",
    "Aragon",
    "Aragón",
    "Aramaic",
    "Aran",
    "Aranese",
    "Arango",
    "Arawak",
    "Arbëresh",
    "Ardennes",
    "Argentina",
    "Arkhangelsk",
    "Armenia",
    "Aromanian",
    "Aruba",
    "Asalem",
    "Asalemi",  # Variant of Talysh
    "Asante",
    "Ashkenazi Hebrew",
    "Asturias",
    "Atlantic Canada",
    "Atlapexco",
    "Attic",  # Ancient greek
    "Aukštaitian",
    "Australia",
    "Australian",
    "Austria",
    "Austrian",
    "Auve",
    "Auvernhàs",  # Dialect of Occitan
    "Avignon",
    "Ayer",
    "Ayt Ndhir",
    "Azerbaijani",
    "Azores",
    "Baan Nong Duu",
    "Babia",
    "Bacheve",
    "Badiot",  # Variant of Ladin
    "Badiu",
    "Baghdad",
    "Bahamas",
    "Bahasa Baku",
    "Baku",
    "Balearic",
    "Balkar",
    "Baltic-Finnic",
    "Bamu",
    "Banatiski Gurbet",
    "Banawá",
    "Bangkok",
    "Barbados",
    "Barda",
    "Bardez Catholic",
    "Barlavento",
    "Basel",
    "Bashkir",
    "Basque",
    "Batang",
    "Batangas",
    "Bavaria",
    "Bavarian",
    "Baxter Sagart",  # a reconstruction of Old Chinese pronunciation
    "Beijing",
    "Belalau",
    "Belarusian",
    "Belgium",
    "Belize",
    "Bentheim",
    "Bering Straits",  # Inupiaq language
    "Berlin",
    "Berlin-Brandenburg",
    "Bern",
    "Beru",
    "Bezhta",
    "Bharati braille",
    "Biblical Hebrew",
    "Biblical",
    "Bikol Legazpi",
    "Bikol Naga",
    "Bikol Tabaco",
    "Bilasuvar",
    "Bimenes",
    "Biscayan",
    "Bla-Brang",
    "Bo Sa-ngae",
    "Bodega",
    "Bogota",
    "Boharic",  # XXX is this typo of Bohairic?  fruit/Tr/part of plant/Coptic
    "Bohairic",
    "Bohemia",
    "Boholano",
    "Bokmål",  # Variant of Norwegian
    "Bolivia",
    "Bologna",
    "Bolognese",
    "Bombay",
    "Borneo",
    "Boro",
    "Bosnia Croatia",
    "Bosnia",
    "Bosnian",
    "Bosnian Croatian",
    "Bosnian Serbian",
    "Boston",
    "Botswana",
    "Brabant",
    "Brabantian",
    "Brazil",
    "Brazilian",
    "Bressan",
    "Brest",
    "Britain",
    "British",
    "British airforce",
    "British Army",
    "British Columbia",
    "British Isles",
    "British Royal Navy",
    "Brunei",
    "Bugey",
    "Bugurdži",
    "Bukovina",
    "Bulgaria",
    "Bulgarian",
    "Busan",
    "Bushehr",
    "Burdur",
    "Burgenland",
    "Bygdeå",
    "Byzantine",
    "Bzyb",
    "Béarn",
    "cabo Verde",
    "CJK tally marks",
    "Cabrales",
    "Caipira",
    "Caithness",
    "California",
    "Campello Monti",
    "Campidanese",  # Variant of Sardinian
    "Canada",
    "Canadian",
    "Canadian English",
    "Canadian French",
    "Canadian Prairies",
    "Canado-American",
    "Canary Islands",
    "Cangas del Narcea",
    "Cantonese",  # Chinese dialect/language
    "Cape Afrikaans",
    "Carakan",
    "Carcoforo",
    "Caribbean",
    "Carioca",
    "Carpi",
    "Castilian Spanish",
    "Castilian",
    "Catalan",
    "Catalan-speaking bilingual areas mostly",
    "Catalonia",
    "Catholic",
    "Cebu",
    "Cebuano",
    "Central America",
    "Central Apulia",
    "Central Asia",
    "Central Scots",
    "Central Sweden",
    "Central and Southern Italy",
    "Central",
    "Chakavian",
    "Changuena",
    "Changsha",
    "Changtai",
    "Chanthaburi",
    "Chazal",  # Jewish historical sages
    "Chengdu",
    "Chiconamel",
    "Chicontepec",
    "Child US",
    "Chile",
    "China",
    "Chinese Character classification",
    "Cholula",
    "Chongqing",
    "Christian",
    "Chugoku",
    "Chūgoku",
    "Chumulu",
    "Church of England",
    "Cieszyn Silesia",
    "Cincinnati",
    "Cismontane",  # Corsican dialect
    "Classical",  # Variant of several languages, e.g., Greek, Nahuatl
    "Classical Attic",
    "Classical Chinese",
    "Classical Edessan",
    "Classical Indonesian",
    "Classical K'Iche",
    "Classical Latin",
    "Classical Persian",
    "Classical Sanskrit",
    "Classical Syriac",
    "Classical studies",
    "Clay",
    "Closed ultima",
    "Coastal Min",
    "Cockney",
    "Cois Fharraige",
    "Cois Fharraige",
    "Colombia",
    "Colunga",
    "Common accent",
    "Commonwealth",
    "Congo",
    "Congo-Kinshasa",
    "Connacht",
    "Connemara",
    "Contentin",
    "Continent",
    "Copenhagen",
    "Cork",
    "Cornish",
    "Cornwall",
    "Counting rod",
    "Costa Rica",
    "Cotentin",
    "Crimea",
    "Croatia",
    "Croatian",
    "Cu'up",  # Region in Indonesia (Rejang language)
    "Cuarto de los Valles",
    "Cuba",
    "Cuisnahuat",
    "Cumbria",
    "Cuoq",
    "Cusco",
    "Cypriot",
    "Cyprus",
    "Czech",
    "Czech Republic",
    "Čakavian",
    "DR Congo",
    "Dalmatia",
    "Dalinpu",
    "Dananshan Miao",
    "Dankyira",
    "Dari",
    "Dashtestan",
    "Dauphinois",
    "Daya",
    "Daytshmerish",
    "De'kwana",
    "Debri",
    "Deh Sarv",
    "Deirate",
    "Delhi",
    "Delhi Hindi",
    "Demotic",  # Greek/Ancient Greek
    "Denizli",
    "Derbyshire",
    "Devon",
    "Digor",  # Variant of Ossetian
    "Dingzhou",
    "Dissenter",
    "Dithmarsisch",
    "Diyarbakır",
    "Dominican Republic",
    "Dominican Republic",
    "Dongmen",
    "Doric",  # Ancient Greek
    "Drasi",  # Region in India
    "Draweno-Polabian",
    "Drents",
    "Dundee",
    "Dungan",
    "Durham",
    "Dutch",
    "Dêgê",
    "Džáva",
    "EU",
    "Early Middle English",
    "Early Modern Greek",
    "Early",
    "East Anglia",
    "East Armenian",
    "East Bengal",
    "East Coast",
    "East Frisian",
    "East Midland",
    "East Slovakia",
    "East",
    "Eastern Armenian",
    "Eastern Lombard",
    "Eastern New England",
    "Eastern Punjabi",
    "Eastern Syriac",
    "Eastern",
    "Ecclesiastical",
    "Ectasian",
    "Ecuador",
    "Ecuadorian Kichwa",
    "Edirne",
    "Egypt",
    "Egyptian Arabic",  # Variant of Arabic
    "Egyptiot",
    "Ekagongo",
    "Ekavian",
    "El Salvador",
    "Elazığ",
    "Elberfelder Bibel",
    "England",
    "English Midlands",
    "English",
    "Eonavian",
    "Epic",
    "Epigraphic Gandhari",
    "Erhua",  # Northern Chinese dialectal feature
    "Erzgebirgisch",
    "Esham",
    "Esperantized",
    "Esperanto",
    "Estonian",
    "Estuary English",
    "Europe",
    "European",
    "European Union",
    "European ortography",
    "Eurozone",
    "Fante",
    "Faroese",
    "Fars",
    "Fascian",  # Variant of Ladin
    "Fayyumic",
    "Fengkai",
    "Finglish",  # Finnish word taken from English / American Finnish dialect
    "Finland",
    "Fjolde",
    "Flanders",
    "Flemish",
    "Florida",
    "Fluminense",
    "Fodom",  # Variant of Ladin
    "For transcription only",
    "Formazza",
    "Fountain",
    "Fragoria vesca",
    "France Quebec",
    "France",
    "Fredrikstad",
    "French",
    "Frenchified",
    "Fribourg",
    "Friulian",
    "From Old Northern French",
    "Föhr",
    "Föhr-Amrum",
    "Fuzhou",
    "Gadabay",
    "Gaellic",
    "Galgolitic",
    "Galicia",
    "Galician",
    "Galitzish",
    "Galway",
    "Gan",  # Variant of Chinese
    "Gangwon",  # Dialect/region for Korean
    "Gascon",  # DIalect of Occitan
    "Gascony",
    "Gaspésie",
    "Gaúcho",
    "Gelders",
    "General American",
    "General Australian",
    "General Brazilian",
    "General Cebuano",
    "General New Zealand",
    "General South African",
    "Genoese",
    "Genovese",
    "Geordie",
    "Georgia",
    "German",
    "German Low German",
    "Germanic",
    "Germany",
    "Gheg",
    "Gherdëina",  # Variant of Ladin
    "Gipuzkoan",
    "Glarus",
    "Goan Konkani",
    "Goerdie",
    "Goeree-Overflakkee",
    "Gope",
    "Gorj",
    "Goth",
    "Gothenburg",
    "Gotland",
    "Goud Saraswat",
    "Grecian",
    "Greco-Bohairic",
    "Greco-Roman",
    "Greek Catholic",
    "Greek-type",  # Used to characterize some Latin words e.g. nematodes/Latin)
    "Gressoney",
    "Grischun",
    "Grisons",
    "Groningen",
    "Gronings",
    "Guadeloupean",
    "Gualaca",
    "Guatemala",
    "Guangdong",
    "Guangzhou",
    "Guernsey",
    "Gufin",
    "Guichicovi",
    "Guinea-Bissau",
    "Guinée Conakry",
    "Gulf Arabic",  # Variant of Arabic Language
    "Gurbet",
    "Gurvari",
    "Guyana",
    "Gwichya",
    "Gyeongsang",
    "H-system",
    "Ha",
    "Hachijō",
    "Hainanese",
    "Haketia",
    "Hakka",  # Chinese dialect/language
    "Halchighol",
    "Hallig",
    "Halligen",
    "Hamburg",
    "Hangaza",
    "Hanoi",
    "Hanyuan",
    "Harak",
    "Harat",
    "Harry Potter",
    "Hawaii",
    "Hawick",
    "Hán tự",
    "Hebei",  # China
    "Hejazi Arabic",  # Variant of Arabic Language
    "Hejazi",
    "Helgoland",  # Variant of North Frisian
    "Heligoland",
    "Heligolandic",
    "Hellenizing School",
    "Hevaha",
    "Hianacoto",
    "Hiberno-English",
    "Hijazi",  # Variant of Arabic
    "Hijazi Arabic",  # Variant of Arabic
    "Hinduism",
    "Hokkien",  # Chinese dialect/language
    "Honduras",
    "Hong Kong",
    "Hongmaogang",
    "Hong'an",
    "Hoanya",
    "Hometwoli",
    "Hongfeng",
    "Hosso",
    "Hsinchu Hokkien",  # Chinese dialect/language
    "Hua",
    "Huizhou",
    "Hui'an",
    "Hungarian Vend",
    "Huế",
    "Hyōgai",  # Uncommon type of Kanji character
    "Hà Nội",  # Vietnamese dialect
    "Hà Tĩnh",  # Vietnamese dialect
    "Hössjö",
    "Hồ Chí Minh City",
    "I Ching hexagram",
    "I-I",  # Used in some Dungan nouns; I have no idea what this means
    "Ionic",  # Ancient Greek
    "IUPAC name",
    "Iberian",
    "Ibero-Romance",
    "Iceland",
    "İçel",
    "Ikavian",
    "Ijekavian",
    "Ijekavian/Ekavian",
    "Ilir",
    "In conjunct consonants",
    "Inari",  # Variant of Sami
    "India",
    "Indian English",
    "Indo-Aryan linguistics",
    "Indo-European studies",
    "Indonesia",
    "Inkhokwari",
    "Inland Min",
    "Inland Northern American",
    "Inner Mongolia",
    "Insular Scots",
    "Insular",
    "Interlingua",
    "Internet",
    "Inuvialuktun",
    "Iran",
    "Iranian",
    "Iranian Persian",
    "Iraq",
    "Iraqi Hebrew",
    "Ireland",
    "Irish",
    "Iron",  # Variant of Ossetian
    "Isfahan",
    "Isparta",
    "Israel",
    "Issime",
    "Istanbul",
    "Italian Hebrew",
    "Italy",
    "Iyaric",
    "Izalco",
    "İzmit",
    "Jabung",
    "Jainism",
    "Jakarta",
    "Jalalabad",
    "Jalilabad",
    "Jalnguy",
    "Jamaica",
    "Jamaican",
    "Jamaican creole",
    "Japan",
    "Japurá",
    "Jarawara",
    "Jazan",
    "Jáva",
    "Jehovah's Witnesses",
    "Jèrriais",
    "Jersey",
    "Jewish Aramaic",
    "Jewish Babylonian Aramaic",
    "Jewish Palestinian Aramaic",
    "Jewish",
    "Jianghuai Mandarin",  # Chinese dialect/language
    "Jian'ou",  # Chinese dialect
    "Jicalapa",
    "Jicarilla",  # Variant of the Apache Language?
    "Jilu Mandarin",  # Dialect/Language in Chinese
    "Jin",
    "Jin Mandarin",  # Chinese dialect/language
    "Jinjiang Hokkien",  # Chinese dialect/language
    "Jinjiang",
    "Johannesburg",
    "Johor-Selangor",
    "Johore",
    "Judaism",
    "Judeo-French",
    "Kabul",
    "Kabuli",
    "Kadaru",
    "Kagoshima",
    "Kaipi",
    "Kaiwaligau Ya",
    "Kajkavian",
    "Kalaw Kawaw Ya",
    "Kalaw Lagaw Ya",
    "Kalbajar",
    "Kalderaš",
    "Kalianda",
    "Kaliarda",
    "Kalix",
    "Kaluga",
    "Kamino",
    "Kampong Ayer",
    "Kamrupi",
    "Kamviri",
    "Kanchanaburi",
    "Kandahar",
    "Kansai",
    "Kanto",
    "Kaohsiung",
    "Kaohsiung Hokkien",  # Chinese dialect/language
    "Karabakh",
    "Karachay",
    "Karanga",
    "Karwari",
    "Kasuweri",
    "Katharevousa",
    "Kautokeino",
    "Kayseri",
    "Kayu Agung",
    "Kayu Agung Asli",
    "Kayu Agung Pendatang",
    "Kaw Kyaik",
    "Kazakh",
    "Kazerun",
    "Kazym",
    "Kedayan",
    "Kent",
    "Kentish",
    "Kenya",
    "Kernewek Kemmyn",
    "Kernowek Standard",
    "Kerry",
    "Kfar Kama",  # Region in Israel
    "Khesht",
    "Khojavend",
    "Khorasan",
    "Khoshar-Khota",
    "Khun villages",
    "Kiambu",
    "Kidero",
    "Kinmen Hokkien",
    "Kinmen",
    "Kinshasa",
    "Kinyarwanda",
    "Kirundi",
    "Klang",
    "Kobuk",  # Inupiaq
    "Koine",  # Ancient Greek
    "Konartakhteh",
    "Kong Loi village",
    "Kong Loi villages",
    "Konya",
    "Koryo-mar",
    "Kosovo",
    "Kosovo Arli",
    "Kota Agung",
    "Krui",
    "Kulkalgau Ya",
    "Kurdamir",
    "Kuritiba",
    "Kursk",
    "Kuwait",
    "Kuwaiti Gulf Arabic",  # Variant of Arabic Language
    "Kuzarg",
    "Kyoto",
    "Kyrgyz",
    "Kyūshū",
    "Kwantlada",
    "Kölsch",
    "LÚ",
    "La Up village",
    "Lamphun Province",
    "Languedoc",
    "Late Bohairic",
    "Late Egyptian",
    "Late Latin",
    "Late Middle English",
    "Late Old French",
    "Late Old Frisian",
    "Late West Saxon",
    "Late",
    "Latin America",
    "Latinate",
    "Latinism",
    "Latvian",
    "Laval",
    "Lavarone",
    "Lebanese Arabic",  # Variant of Arabic language
    "Lebong",  # Region in Indonesia/Sumatra?  (Rejang language)
    "Leet",  # Leetspeak, an internet "slang"
    "Legazpi",
    "Leizhou Min",  # Chinese dialect/language
    "Lemosin",  # Dialect of Occitan
    "Lengadocian",  # Dialect of Occitan
    "Lesotho",
    "Levantine Arabic",  # Variant of Arabic language
    "Lewis",
    "Leyte",
    "Lhasa",
    "Liechtenstein",
    "Limba Sarda Comuna",
    "Limburg",
    "Limburgish",
    "Limousin",
    "Limuru",
    "Linnaeus",
    "Lippisch",
    "Lisan ud-Dawat",
    "Listuguj",
    "Literary affectation",
    "Lithuania",
    "Lithuanian",
    "Litvish",
    "Liverpudlian",
    "Llanos",
    "Logudorese",  # Variant of Sardinian
    "Lojban",
    "Loli",
    "Lombardy",
    "London",
    "Lorraine",
    "Louisiana",
    "Lovara",
    "Low Prussian",
    "Low Sorbian",
    "Lower Sorbian",
    "Lubunyaca",
    "Lukang Hokkien",
    "Lukang",
    "Luleå",
    "Lunfardo",
    "Luserna",
    "Luxembourg",
    "Luxembourgish",
    "Lycopolitan",
    "Lyon",
    "Lyons",
    "Lviv",
    "Lövånger",
    "Ḷḷena",
    "Łowicz",
    "M.O.D.",  # Used as head form in Marshallese
    "Maastrichtian",
    "Macau",
    "Macedonia",
    "Macedonian",
    "Macedonian Arli",
    "Macedonian Džambazi",
    "Mackem",
    "Madeira",
    "Maharashtra",
    "Mahuizalco",
    "Maiak",
    "Maine",
    "Mainland China",
    "Malacatepec",
    "Malak",
    "Malayalam",
    "Malaysia",
    "Malaysia Hokkien",
    "Malaysian English",
    "Mallorca",
    "Malta",
    "Malyangapa",
    "Mamluk-Kipchak",
    "Mandalay Taishanese",
    "Mandarin",  # Dialect/Language in Chinese
    "Mandi",
    "Manglish",
    "Manichaean",
    "Manicoré",
    "Manitoba Saulteux",
    "Mantua",
    "Manyika",
    "Marathi",
    "Martinican",
    "Martinican Creole",
    "Marwari",
    "Mary-marry-merry distinction",
    "Mary-marry-merry merger",
    "Marxism",
    "Masarm",
    "Maharastri Prakrit",
    "Mauritania",
    "Mawakwa",
    "Mayo",
    "Mecayapan",  # Variant of Nathuatl
    "Mecklenburg-Vorpommern",
    "Mecklenburgisch",
    "Mecklenburgisch-Vorpommersch",
    "Medan",
    "Mediaeval",
    "Medieval",
    "Medieval Greek",
    "Medieval Latin",
    "Medio-Late Egyptian",
    "Mehedinți",
    "Meinong",
    "Meixian",
    "Melanesian",
    "Melinting",
    "Menggala/Tulang Bawang",
    "Mercian",
    "Merseyside",
    "Mescaleiro",
    "Mexica",
    "Mexico",
    "Mfom",
    "Miaoli",
    "Microsoft Azure",
    "Mid Northern Scots",
    "Mid Northern",
    "Mid",
    "Mid-Atlantic",
    "Middle Ages",
    "Middle Chinese",  # Historical variant of Chinese
    "Middle Cornish",
    "Middle Egyptian",
    "Middle",
    "Midland American English",
    "Midlands",
    "Midlandsnormalen",
    "Midwestern US",
    "Milan",
    "Milanese",
    "Milpa Alta",
    "Min",
    "Min Bei",
    "Min Dong",  # Chinese dialect/language
    "Min Nan",  # Chinese dialect/language
    "Minas Gerais",
    "Mineiro",
    "Mirandola",
    "Mirandolese",
    "Mistralian",
    "Mizrahi Hebrew",
    "Modena",
    "Modern",
    "Modern Armenian",
    "Modern Israeli Hebrew",
    "Modern Israeli",
    "Modern Latin",
    "Modern Polabian",
    "Modern Turkish",
    "Modi",  # Variant/language based on Sanskrit
    "Moghamo",
    "Moldavia",
    "Molet Kasu",
    "Molet Mur",
    "Monegasque",
    "Mongo-Turkic",
    "Montenegro",
    "Montreal",
    "Mooring",  # Variant of North Frisian
    "Moravia",
    "Mormonism",
    "Moroccan",  # Variant of Arabic
    "Moroccan Arabic",  # Variant of Arabic
    "Morocco",
    "Moscow",
    "Moselle Franconian",
    "Mosetén",
    "Mount Currie",
    "Mozambique",
    "Moçambique",
    "Mpakwithi",
    "Muğla",
    "Multicultural London English",
    "Munster",
    "Muping",
    "Murang'a",
    "Mushuau Innu",
    "Muslim",
    "Münsterland",
    "Münsterländisch",
    "Mycenaean",  # Variant of Greek
    "Nahua",
    "Nahuatl",
    "Nakhchivan",
    "Namibia",
    "Nanchuan",
    "Nanchang",
    "Nan'an",
    "Nao Klao",  # dialect
    "Naples",
    "Navajo",
    "Navarre",
    "Navarrese",
    "Navarro-Lapurdian",
    "Navy",
    "Nazism",
    "Ndia",
    "Neo-Latin",
    "Nepal",
    "Netherlands",
    "Nevada",
    "New Age",
    "New England",
    "New Jersey",
    "New Latin",
    "New Sanskrit",
    "New York City",
    "New York",
    "New Zealand",
    "Newfoundland",
    "Nicaragua",
    "Niçard",
    "Nidwalden",
    "Nigeria",
    "Niğde",
    "Ningbo",
    "Nizhegorod",
    "Nomen sacrum",  # Used in Gothic form names
    "Non-Oxford",
    "Nordestino",
    "Nordic",
    "Norfolk",
    "Normandy",
    "Norse",
    "North Afar",
    "North America",
    "North American",
    "North Brazil",
    "North East England",
    "North Eastern US",
    "North German",
    "North Korea",
    "North Levantine",
    "North Levantine Arabic",  # Variant of Arabic
    "North Northern Scots",
    "North Northern",
    "North Northern",
    "North Wales",
    "North and East of the Netherlands",
    "North",
    "Northeast Brazil",
    "Northeastern Brazil",
    "Northeastern",
    "Northern California",
    "Northern Catalan",
    "Northern Crimea",
    "Northern England",
    "Northern English",
    "Northern Germany",
    "Northern Ireland",
    "Northern Italy",
    "Northern Mandarin",  # Chinese dialect/language
    "Northern Manx",
    "Northern Middle English",
    "Northern Puebla",
    "Northern Scots",
    "Northern UK",
    "Northern US",
    "Northern Yiddish",
    "Northern Zazaki",
    "Northern",
    "Northamptonshire",
    "Northumbria",
    "Northwestern",
    "Novgorod",
    "Nde",
    "Nembe",
    "Nfom",
    "Ngan'gimerri",
    "Ngan'gikurunggurr",
    "Ngie",
    "Ngoko",
    "Nghệ An",  # Vietnamese dialect
    "Nkim",
    "Nkojo",
    "Nkum",
    "Norse",
    "Nselle",
    "Nsimbwa",
    "Nta",
    "Ntuzu",
    "Nuorese",
    "Nyeri",
    "Nynorak",
    "Nynorsk",  # Variant of Norwegian
    "Nyungkal",
    "Nürnbergisch",
    "Occitania",
    "Old Bohairic",
    "Old Chamorro",
    "Old Chinese",  # Historical variant of Chinese
    "Old Coptic",
    "Old East Church Slavonic",
    "Old Egyptian",
    "Old English",
    "Old Latin",
    "Old Lithuanian",
    "Old Norse",
    "Old Northern French",
    "Old Polabian",
    "Old Tagalog",
    "Oliti",
    "Olles",
    "Ombos",
    "Ontario",
    "Ooldea",
    "Orcadian",
    "Ordubad",
    "Orkney",
    "Ormulum",
    "Oryol",
    "Oslo",
    "Ottomans",
    "Oxford",  # Variant of British English
    "Pa Pae village",
    "Paderbornish",
    "Paderbornisch",
    "Pahang",
    "Pak Kret District",
    "Pakistan",
    "Palacios de Sil",
    "Palatine",
    "Palestinian",
    "Pali",  # Sanskrit
    "Panama",
    "Pangin",
    "Papua New Guinea",
    "Paraguay",
    "Paris",
    "Parisian",
    "Parres",
    "Parts of south Jeolla",
    "Paulistano",
    "Payang",  # Region in Indonesia (Rejang language)
    "Pays de Bray",
    "Pays de Caux",
    "Paḷḷuezu",
    "Peking",
    "Pembrokeshire",
    "Penang Hokkien",
    "Penang",
    "Peng'im",
    "Penghu Hokkien",
    "Pennsylvania",
    "Periphrastic conjugations",
    "Perm",
    "Persian Gulf",
    "Persianized",
    "Perso-Arabic",
    "Peru",
    "Peshawar",
    "Phnom Penh",
    "Philadelphia",
    "Philippine",
    "Philippines",
    "Piacenza",
    "Picardy",
    "Pinghua",  # Chinese dialect/language
    "Pinyin",
    "Pirupiru",
    "Pite",  # Variant of Sami
    "Piteå",
    "Plautdietsch",
    "Polari",
    "Polish",
    "Portugal",
    "Portugal",
    "Possesse",
    "Poylish",
    "Poznań",
    "Praenominal",  # Type of abbreviation
    "Pre-Hebrew",
    "Prokem",
    "Protestant",
    "Proto-Slavic",
    "Provençal",
    "Provençau",  # Dialect of Occitan
    "Pskov",
    "Pu No",  # dialect
    "Pubian",
    "Puebla",
    "Puerto Rico",
    "Pulaar",
    "Pular",
    "Puter",
    "Puxian Min",  # Chinese language/dialect
    "Valdés",
    "Vallander",
    "Varendra",
    "Vegliot",
    "Vest Recklinghausen",
    "Villacidayo",
    "Qazakh",
    "Quakerism",
    "Quanzhou",
    "Quebec",
    "Quebec City",
    "Quetta",
    "Quirós",
    "Quốc ngữ",
    "Raguileo Alphabet",
    "Ragusan",
    "Rai Kaili",
    "Ranau",
    "Rastafari",
    "Rastafarian",
    "Ratak",
    "Received Pronunciation",
    "Recueil scientifique ou littéraire",
    "Reggio Emilia",
    "Reina-Valera version",
    "Renshou",
    "Revived Late Cornish",
    "Revived Middle Cornish",
    "Revived",
    "Rhine Franconian",  # Variant of German
    "Rhineland",
    "Rhodesia",
    "Riau",
    "Riau-Lingga",
    "Rigveda",
    "Riksmål",
    "Rimella",
    "Ring",
    "Rio Grande De Sul",
    "Rio de Janeiro",
    "Rioplatense",
    "Ripuarian",
    "Ritsu",
    "Rogaland",
    "Roman Catholic",
    "Roman Empire",
    "Romanian",
    "Romungro",
    "Rouen",
    "Rubī-Safaia",
    "Ruhrgebiet",
    "Rumantsch Grischun",
    "Rumy",
    "Rundi",
    "Rungu",
    "Russia",
    "Russian",
    "Russianism",
    "Rwanda",
    "Rwanda-Rundi",
    "Rālik",
    "Rāṛha",
    "SK Standard",
    "SW England",
    "Saarve",
    "Sagada",
    "Sahidic",
    "Saint Ouën",
    "Saint Petersburg",
    "Sakayamuni",
    "Sakhalin",
    "Salaca",
    "Salas",
    "Sallans",
    "Salyan",
    "Sami",
    "San Juan Quiahije",
    "Sanskrit",
    "Sanskritized",
    "Santiago",
    "Sanxia Hokkien",
    "São Vicente",
    "Sappada",
    "Sapper-Ricke",
    "Sark",
    "Sauerland",
    "Sauerländisch",
    "Sauris",
    "Savoie",
    "Savoyard",
    "Sawndip",
    "Sayisi",  # Variant of Chipewyan language?
    "Schleswig-Holstein",
    "Schwyz",
    "Scientific Latin",
    "Scotland",
    "Scottish",
    "Scouse",
    "Seoul",
    "Sepečides",
    "Sepoe",
    "Serbia",
    "Serbian",
    "Serbo-Croatian",
    "Servia",
    "Sesivi",
    "Sette Comuni",
    "Seville",
    "Shandong",
    "Shanghai",
    "Shanghainese Wu",
    "Shapsug",
    "Shavian",
    "Sheffield",
    "Sheng",
    "Shephardi Hebrew",
    "Sheshatshiu Innu",
    "Shetland",
    "Shetlandic",
    "Shia",
    "Shidong",
    "Shikoku",
    "Shin",
    "Shiraz",
    "Shropshire",
    "Shubi",
    "Shuri-Naha",
    "Shuryshkar",
    "Siba",
    "Sibe",
    "Sichuan",
    "Sichuanese",
    "Sikh",
    "Sikhism",
    "Silesian",
    "Simplified",
    "Singapore English",
    "Singapore",
    "Singlish",
    "Sino-Korean",
    "Sino-Japanese",
    "Sisiame",
    "Sistani",
    "Sixian",
    "Skellefteå",
    "Skiri",
    "Skolt",  # Variant of Sami
    "Slovak",
    "Slovene",
    "Slovincian",
    "Smolensk",
    "Sobrescobiu",
    "Sofia Erli",
    "Soikkola",
    "Solothurn",
    "Somiedu",
    "Sori",
    "Sotavento",
    "Souletin",
    "South Afar",
    "South Africa",
    "South African",
    "South America",
    "South American English",
    "South Asia",
    "South Azerbaijani",
    "South Brazil",
    "South German",
    "South Korea",
    "South Levantine",
    "South Levantine Arabic",
    "South Northern Scots",
    "South Scots",
    "South Wales",
    "South",
    "Southeastern",
    "Southern Africa",
    "Southern American English",
    "Southern Brazil",
    "Southern England",
    "Southern Italy",
    "Southern Manx",
    "Southern Middle English",
    "Southern Quechua",
    "Southern Scotland",
    "Southern Scots",
    "Southern Spain",
    "Southern US",
    "Southern Yiddish",
    "Southern Zazaki",
    "Southern",
    "Southwestern",
    "Southwestern Mandarin",  # Chinese dialect/language
    "Space Force",
    "Spain",
    "Spanish",
    "Sremski Gurbet",
    "Sri Lanka",
    "St. Gallen",
    "Standard Cornish",
    "Standard Chinese",  # Standard spoken Chinese, Standard Northern Mandarin in linguistics
    "Standard East Norwegian",
    "Standard German of Switzerland",
    "Standard German",
    "Standard Hlai",
    "Standard Sicilian",
    "Standard Tagalog",
    "Standard Zhuang",
    "Stavanger",
    "Stellingwerfs",
    "Stokoe",  # Used in sign language letter entries to indicate Latin letter
    "Suizhou",
    "Sukai",
    "Sukau",
    "Sundanese",
    "Sungkai",
    "Sunni",
    "Surgut",
    "Surigaonon",
    "Surinam",
    "Suriname",
    "Surmiran",
    "Sursilvan",
    "Suðuroy",
    "Sutsilvan",
    "Suzhou",
    "Sweden",
    "Swiss German",
    "Swiss",
    "Switzerland",
    "Syllabics",  # Used in word head with Plains Cree, e.g. tânisi/Plains Cree
    "Sylt",  # Variant of North Frisian
    "Syrian Hebrew",
    "São Paulo",
    "São Vicente",
    "TV",
    "Taberga",
    "Tabriz",
    "Taicheng",
    "Tai Xuan Jing",
    "Taichung Hokkien",
    "Tainan",
    "Taipei",
    "Taishanese",
    "Taishan",
    "Taiwan",
    "Taiwanese Min Nan",
    "Taiwanese Hokkien",
    "Taiwanese Mandarin",  # Chinese dialect/language
    "Taixuanjing tetragram",
    "Taiyuan",
    "Tajik",
    "Talang Padang",
    "Tally-marks",
    "Talur",
    "Tang-e Eram",
    "Tankarana",
    "Tantoyuca",
    "Tao",
    "Taraškievica",
    "Tashelhit",  # Variant of Berber
    "Tasmania",
    "Tasmanian",
    "Tavastia",
    "Tebera",
    "Teesside",
    "Tehran",
    "Tehrani",
    "Telugu-Kui",
    "Temapache",
    "Tenerife",
    "Teochew",
    "Teotepeque",
    "Tepetzintla",
    "Terre-Neuve-et-Labrador",
    "Tessin",
    "Texas",
    "Texcoco",
    "Textbibel",
    "Tgdaya",
    "Thailand",
    "Thanh Chương",
    "The Hague",
    "Thung Luang village",
    "Thung Luang",
    "Thurgau",
    "Thuringian-Upper Saxon",
    "Tianjin",
    "Tiberian Hebrew",
    "Timau",
    "Timor-Leste",
    "Tlaxcala",
    "Tlyadal",
    "Toaripi",
    "Tokat",
    "Tokyo",
    "Tongyang",
    "Tongzi",
    "Torlakian",
    "Tosk",
    "Toulouse",
    "Traditional",
    "Trakai-Vilnius",
    "Translingual",
    "Transoxianan",
    "Transylvania",
    "Trat",
    "Tredici Comuni",
    "Trentino",
    "Trinidad and Tobago",
    "Truku",
    "Tsimihety",
    "Tulamni",
    "Turkmen",
    "Tuscany",
    "Twente",
    "Twents",
    "Twi",  # Dialect of the Akan language
    "Tyneside",
    "Uganda",
    "UK with /ʊ/",
    "UK",
    "Ulu",
    "UPA",
    "Upper Silesia",
    "Upper Sorbian",
    "Urama",
    "Urdu",
    "US with /u/",
    "US",
    "US-Inland North",
    "US-merged",
    "Ukraine",
    "Ukrainish",
    "Ukraynish",
    "Ulaanbaatar",
    "Ulster Scots",
    "Ulster",
    "Ultramontane",  # Corsican dialect
    "Umeå",
    "Unified",
    "Unix",
    "Unquachog",  # Dialect of Quiripi
    "Upper RP Triphthong Smoothing",
    "Uri",
    "Urkers",
    "Ursari",
    "Urtijëi",
    "Uruguay",
    "Utara",  # Region in Indonesia (Rejang language)
    "Uutände",
    "Uyghurjin",
    "Vaiśeṣika",
    "Valais",
    "Valencia",
    "Valencian",
    "Vallander",
    "Vancouver",
    "Vancouver Island",
    "Vaṅga",
    "Vedic",
    "Veluws",
    "Venezuela",
    "Verona",
    "Vidari",  # Variant of Alviri-Vidari
    "Vietnam",
    "Vinh",
    "Vinza",
    "Virginia",
    "Vivaro-Alpin",
    "Vivaro-Alpine",
    "Volapük Nulik",
    "Volapük Rigik",
    "Vosges",
    "Vulgata",
    "Västergötland",
    "WW2 air pilots' usage",
    "Wade-Giles",
    "Wadikali",
    "Walapai",
    "Wales",
    "Wallonia",
    "Wamwan",
    "Wardak",
    "Waterford",
    "Way Lima",
    "Wazirwola",
    "Wearside",
    "Weirate",
    "Welche",
    "Welsh English",
    "Wenzhou",  # Chinese dialect/language
    "Wenzhou Wu",  # Chinese dialect/language
    "West Armenian",
    "West Bengal",
    "West Cork",
    "West Country",
    "West Kerry",
    "West Midlands",
    "West Muskerry",
    "West Pomeranian",
    "West Saxon",
    "West",
    "Western Armenian",
    "Western Lombard",
    "Western Punjabi",
    "Western Quebec",
    "Western Rumelia",
    "Western Syriac",
    "Western",
    "Westminster system",
    "Westmünsterland",
    "Westphalia",
    "Westphalian",
    "Westpfälzisch",
    "Westwestphalian",
    "Wiedingharde",
    "Windesi",
    "Witzapan",
    "Wood",
    "World War I",
    "Wrangelsholm",
    "Written Form",
    "Wu",  # Chinese dialect/language
    "Wuhan",
    "Wuvulu",
    "X-system",
    "Xiamen",
    "Xiang",
    "Xilitla",
    "YIVO",
    "Yagaria",
    "Yahualica",
    "Yajurveda chanting",
    "Yaman",
    "Yanbian",
    "Yanhe",
    "Yao'an",
    "Yardliyawara",
    "Yardymli",
    "Yaut",
    "Yawelmani",
    "Yañalif",
    "Ye'kwana",
    "Yemen",
    "Yemenite Hebrew",
    "Yichang",
    "Yiddish-influenced",
    "Yilan",
    "Yilan Hokkien",
    "Yindjilandji",
    "Yintyingka",
    "Ylä-Laukaa",
    "Yongshan",
    "Yorkshire",
    "Yozgat",
    "Yukjin",
    "Yukon",
    "Yulparija",
    "Yunnan",
    "Zacatianguis",
    "Zamboanga",
    "Zangilan",
    "Zaqatala",
    "Zezuru",
    "Zhengzhang",
    "Zhangzhou",
    "Zhangzhou Hokkien",
    "Zhangpu",
    "Zimbabwe",
    "Zinacantán",
    "Zurich",
    "Zêkog",
    "Överkalix",
    "al-Andalus",  # historically Muslim ruled area of the Iberian Penisula
    "bureaucratese",
    "central and northeastern Switzerland",
    "continental Normandy",
    "feudal Britain",
    "parts of South Africa",
    "outside Northumbria",
    "post-Augustan",
    "post-Classical",
    "post-Homeric",
    "pre-Classical",
    "regionally African American Vernacular",
    "southern Moselle Franconian",
    "northernmost Moselle Franconian",
    "west Sweden",
    "most of Moselle Franconian",
    "Southern Germany",
    "southern Germany",
    "Northwest German",  # anfangen/German
    "Ruhrdeutsch",  # Haus/German
    "Berlinisch",  # Haus/German
    "18th ct.",  # Haus/German
    "south-western German",  # Maus/German
    "Upper German",  # schneien/German
    # paste from placenames relating to Chinese dialectal synonyms
    "Tianmen",
    "Gaoming",
    "Xining",
    "Dali",
    "Huicheng-Bendihua",
    "Ganzhou",
    "Luoyang",
    "Lingui",
    "Changting",
    "Lütian",
    "Jiamusi",
    "Heshan",
    "Neipu",
    "Sanjia",
    "Fuyang",
    "Baihe",
    "Changchun",
    "Linfen",
    "Jinzhou",
    "Chongming",
    "Dandong",
    "Qingxi",
    "Shexian",
    "Mengzi",
    "Tonghua",
    "Zhengzhou",
    "Qingping",
    "Haikou",
    "Zunyi",
    "Zhangjiakou",
    "Yangchun",
    "Guiyang",
    "Southern-Pinghua",
    "Ninghua",
    "Dazhou",
    "Zhuhai",
    "Shuangfeng",
    "Tangkou",
    "Hailar",
    "Nanchong",
    "Lianyungang",
    "Kuala-Lumpur",
    "Wengyuan",
    "Hsinchu-County",
    "Ningdu",
    "Lunbei",
    "Wuping",
    "Tingzi",
    "Zhaotong",
    "Liuzhou",
    "Yantai",
    "Shenzhen",
    "Doumen",
    "Leizhou",
    "Zhongshan",
    "Changzhi",
    "Lianjiang",
    "Xinhui",
    "Lishi",
    "Baisha",
    "Xihe",
    "Hangzhou",
    "Tong'an",
    "Baoji",
    "Hanzhong",
    "Yanqian",
    "Xi'an",
    "Cangzhou",
    "Zhao'an",
    "Xinyang",
    "Jieyang",
    "Xiangyang",
    "Huazhou",
    "Niujiang",
    "Xichang",
    "Sabah",
    "Danyang",
    "Lianshui",
    "Qianshan",
    "Jining",
    "Zhudong",
    "Conghua",
    "Huiyang",
    "Chikan",
    "Yangxi",
    "Pingshan",
    "Anqing",
    "Xiuzhuan",
    "Qingdao",
    "Erenhot",
    "Pingtung",
    "Hefei",
    "Manila",
    "Chifeng",
    "Qionglin",
    "Nantong",
    "Yangyuan",
    "Zengcheng",
    "Lijin",
    "Dunhuang",
    "Kam-Tin-Weitou",
    "Nanlang-Heshui",
    "Lichuan",
    "Jiexi",
    "Dongshi",
    "Xindong",
    "Linzhou",
    "Qionghai",
    "Shangqiu",
    "Wuhu",
    "Shijiao",
    "Linhe",
    "Shunde",
    "Wenchang",
    "Kaiping",
    "Shijiazhuang",
    "Yinchuan",
    "Mingcheng",
    "Xinyi",
    "Dongguan",
    "Tonggu",
    "Tianshui",
    "Guangfu",
    "Jixi",
    "Yangjiang",
    "Shatou",
    "Suide",
    "Nanjing",
    "Foshan",
    "Dalian",
    "Liannan",
    "Baicheng",
    "Datong",
    "Yunlin",
    "Shenyang",
    "Nanhai",
    "Dabu",
    "Shajing",
    "Chaozhou",
    "Hami",
    "Pingxiang",
    "Shiqi",
    "Sanshui",
    "Baoding",
    "Johor-Bahru",
    "Tangshan",
    "Harbin",
    "Yudu",
    "Dianbai",
    "Gaozhou",
    "Heihe",
    "Hulunbuir",
    "Jinan",
    "Kunming",
    "Changde",
    "Enping",
    "Shatoujiao",
    "Hailu",
    "Chengde",
    "Zigong",
    "Zhucheng",
    "Guilin",
    "Panlong",
    "Wanrong",
    "Huadu",
    "Bao'an",
    "Qiqihar",
    "Jinhua",
    "Xinzhou",
    "Lanzhou",
    "Huashan",
    "Loudi",
    "Shalang",
    "Yayao",
    "Dayu",
    "Senai",
    "Hohhot",
    "Nanning",
    "Raoping",
    "Sandu",
    "Yuanyang",
    "Handan",
    "Jiangmen",
    "Panyu",
    "Xin'an",
    "Sihe",
    "Xuzhou",
    "Lingbao",
    "Luchuan",
    "Mengshan",
    "Taichung",
    "Qianpai",
    "Yangzhou",
    "Liping",
    "Ürümqi",
    "Bijie",
])


# General mapping for linguistic tags.  Value is a string of space-separated
# tags, or list of alternative sets of tags.  Alternative forms in the same
# category can all be listed in the same string (e.g., multiple genders).
# XXX should analyze imperfect vs. imperfective - are they just used in
# different languages, or is there an actual difference in meaning?
xlat_tags_map = {
    "sg": "singular",
    "pl": "plural",
    "sg.": "singular",
    "pl.": "plural",
    "sg. and pl.": "singular plural",
    "sg and pl": "singular plural",
    "m/f": "masculine feminine",
    "no pl": "no-plural",
    "pl. only": "plural-only plural",
    "pl ordinaux": "usually plural",
    "m.": "masculine",
    "male": "masculine",
    "f.": "feminine",
    "fem.": "feminine",
    "female": "feminine",
    "indef.": "indefinite",
    "gen.": "genitive",
    "pres.": "present",
    "subj.": "subjunctive",
    "impf.": "imperfective",
    "pf.": "perfective",
    "trans.": "transitive",
    "unc": "uncountable",
    "abbreviated": "abbreviation",
    "abbreviation as": "abbreviation",
    "diminutives": "diminutive",
    "Diminutive": "diminutive",
    "Diminutives": "diminutive",
    "†-tari": "-tari",
    "†-nari": "-nari",
    "♂♀": "masculine feminine",
    "♂": "masculine",
    "♀": "feminine",
    "cangjie input": "cangjie-input",
    "RP": "Received-Pronunciation",
    "BR": "Brazil",
    "Brasil": "Brazil",
    "Brazilian Portuguese": "Brazil",
    "FR": "France",
    "IT": "Italy",
    "CAN": "Canada",
    "AU": "Australia",
    "AUS": "Australia",
    "Austr.": "Australian",
    "AusE": "Australia",
    "Aus": "Australia",
    "LKA": "Sri-Lanka",
    "RU": "Russia",
    "SA": "South-Africa",
    "[AU]": "Australia",
    "NYC": "New-York-City",
    "CA": "Canada",
    "AT": "Austria",
    "GA": "General-American",
    "NV": "Navajo",
    "UK male": "UK",
    "UK female": "UK",
    "GB": "UK",
    "EN": "UK",
    "IN": "India",
    "PRC": "China",
    "BG": "Bulgaria",
    "DE": "Germany",
    "IE": "Ireland",
    "NL": "Netherlands",
    "NZ": "New-Zealand",
    "PT": "Portugal",
    "BOL": "Bolivia",
    "U.S.A.": "US",
    "U.S.": "US",
    "[US]": "US",
    "Americanisation": "Americanization",
    "Saint Ouen": "Saint-Ouën",
    "Déné syllabary": "Déné-syllabary",
    "Kayah Li": "Kayah-Li",
    "Hanifi Rohingya": "Hanifi-Rohingya",
    "Ol Chiki": "Ol-Chiki",
    "Old Persian": "Old-Persian",
    "Tai Tham": "Tai-Tham",
    "Warang Citi": "Warang-Citi",
    "UK & Aus": "UK Australia",
    "Britian": "Britain",
    "coastal Min": "Coastal-Min",
    "Telugu-Kui language": "Telugu-Kui",
    "SK Standard/Seoul": "SK-Standard Seoul",
    "Devanagri": "Devanagari error-misspelling",
    "Standard Seoul": "SK-Standard Seoul",
    "Association canadienne de normalisation": "Canada",
    "esp.": "especially",
    "northwestern": "Northwestern",
    "northeastern": "Northeastern",
    "southwestern": "Southwestern",
    "southeastern": "Southeastern",
    "northern": "Northern",
    "southern": "Southern",
    "western": "Western",
    "eastern": "Eastern",
    "westernmost": "Western",
    "west": "West",
    "Mecayapán": "Mecayapan",
    "Mooring and Föhr-Amrum": "Mooring Föhr-Amrum",
    "Föhr-Amrum & Mooring": "Föhr-Amrum Mooring",
    "Nazi slur against Churchill": "Nazism slur",
    "religious slur": "slur",
    "euphemistic Nazi term": "Nazism euphemistic",
    "United States": "US",
    "Québec": "Quebec",
    "Classic Persian": "Classical-Persian",
    "Sette Communi": "Sette-Comuni",
    "Vivaro-alpine": "Vivaro-Alpine",
    "Mooring and Hallig": "Mooring Hallig",
    "Zürich": "Zurich",
    "Somiedo": "Somiedu",
    "Uk": "UK",
    "US/UK": "US UK",  # XXX leave separate
    "USA": "US",
    "México": "Mexico",
    "Latinamerica": "Latin-America",
    "Lat. Amer.": "Latin-America",
    "LAm": "Latin-America",
    "Monégasque": "Monegasque",
    "Audio": "",
    "orig. US": "",
    "poetical": "poetic",
    "Noun": "noun",
    "Adjective": "adjective",
    "Verb": "verb",
    "Poetic": "poetic",
    "Poetic.": "poetic",
    "Informal.": "informal",
    "slightly more formal": "formal",
    "Colloquial.": "colloquial",
    "Antiquated.": "dated",
    "Archaic": "archaic",
    "religious/archaic": "archaic",
    "Causative": "causative",
    "Passive": "passive",
    "Stative": "stative",
    "Applicative": "applicative",
    "Colloquial": "colloquial",
    "Epic verse": "poetic",
    "Nominative plural - rare": "nominative plural rare",
    "Nonstandard but common": "nonstandard common",
    "Slang": "slang",
    "Slang-Latin America": "slang Latin-America",
    "slangy": "slang",
    "backslang": "slang",
    "butcher's slang": "slang jargon",
    "archiac": "archaic error-misspelling",
    "archaic except in fixed expressions": "archaic",
    "nonstandard form": "nonstandard",
    "singular form": "singular",
    "plural form": "plural",
    "nonstandard form of": "nonstandard alt-of",
    "main verb": "base-form",
    "standard form of": "standard alt-of",
    "nonstandard stylistic suffix": "nonstandard dialectal suffix",
    "honorific form": "honorific",
    "possessed form": "possessed-form",
    "obligatorily possessed": "possessed-form",
    "obligatory possessive": "possessed-form",
    "obligatory possession": "possessed-form",
    "possessive only": "possessive",
    "obligational": "obligative",
    "indicated possession by preceding noun": "possessed-form",
    "unpossessed form": "unpossessed-form",
    "Dialectal": "dialectal",
    "Dialect": "",
    "dialectal form": "dialectal",
    "dialectal term": "dialectal",
    "dialectal Mandarin": "dialectal Mandarin",
    "Dialect:": "",
    "regiolectal": "dialectal",
    "archaic or regiolectal": "archaic dialectal",
    "archaic or regional": "archaic dialectal",
    "Archaic or obsolete": "archaic",
    "Canada: Ontario": "Ontario",
    "Canada: British Columbia": "British-Columbia",
    "GenAm": "General-American",
    "Greco-Bohairic Pronunciation": "Greco-Bohairic",
    "Greco-Bohairic pronunciation": "Greco-Bohairic",
    "Vallader": "Vallander",
    "Conservative RP": "Received-Pronunciation",
    "Received Prononunciation": "Received-Pronunciation",
    "North American also": "North-American",
    "Cois Fharraige also": "Cois-Fharraige",
    "Sawndip forms": "Sawndip",
    "Sawndip form": "Sawndip",
    "old orthography": "archaic",
    "Maine accent": "Maine",
    "Bosnia Serbia": "Bosnian-Serbian",
    "MLE": "Multicultural-London-English",
    "AAVE": "African-American-Vernacular-English",
    "Early ME": "Early-Middle-English",
    "Northern ME": "Northern-Middle-English",
    "Southern ME": "Southern-Middle-English",
    "Late ME": "Late-Middle-English",
    "Spanish given name": "Spanish proper-noun",
    "Taichung & Tainan Hokkien": "Taichung-Hokkien Tainan",
    "St. Petersburg or dated": "Saint-Petersburg dated",
    "Irregular reading": "irregular-pronunciation",
    "irreg. adv.": "irregular adverbial",
    "Argentina and Uruguay": "Argentina Uruguay",
    "Argentina Uruguay": "Argentina Uruguay",
    "Southern US folk speech": "Southern-US dialectal",
    "Main dialectal variations": "dialectal",
    "Many eastern and northern dialects": "dialectal",
    "many dialects": "dialectal",
    "some dialects of": "dialectal",
    "now sometimes by conflation with etymology 1 under standard German influence":
    "sometimes",
    "see below": "",
    "unstressed form": "unstressed",
    "mute of": "unstressed form-of",
    "for some speakers": "uncommon",
    'when "do" is unstressed and the next word starts with /j/':
    "unstressed-before-j",
    "before a vowel": "before-vowel",
    "before vowel": "before-vowel",
    "before vowels": "before-vowel",
    "pre-vocalic": "before-vowel",
    "used before vowels and lenited fh-": "before-vowel before-lenited-fh",
    "used before vowels": "before-vowel",
    "used before the past tense": "before-past",
    "used a verb in imperfect subjunctive": "with-imperfect with-subjunctive",
    "the Eurozone": "Eurozone",
    "Phoneme": "phoneme",
    "Vowel": "phoneme",
    "Consonant": "phoneme",
    "Name of letter": "name",
    "nation's name": "name",
    "proprietary name": "name",
    "Vulgar": "vulgar",
    "strong language": "vulgar",
    "Very Strong Swear word": "vulgar",
    "Spoken": "colloquial",
    "spoken": "colloquial",
    "written": "literary",
    "Syllable initial": "syllable-initial",
    "Syllable final": "syllable-final",
    "internet": "Internet",
    "online": "Internet",
    "instant messaging": "Internet",
    "text messaging": "Internet",
    "cot-caught merged": "cot-caught-merger",
    "cot–caught merged": "cot-caught-merger",
    "cot-caught merger": "cot-caught-merger",
    "cot–caught merger": "cot-caught-merger",
    "pin-pen merger": "pin-pen-merger",
    "pin–pen merger": "pin-pen-merger",
    "prefix before comparative forms": "prefix with-comparative",
    "countable and uncountable": "countable uncountable",
    "masculine and feminine plural": "masculine feminine plural",
    "definite singular and plural": "definite singular plural",
    "definite or plural": ["definite", "plural"],
    "plural or definite attributive":
    ["plural attributive", "definite singular attributive"],
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
    "the third person": "third-person",
    "(at least) nominative/objective/reflexive cases":
    "nominative objective",
    "singular and plural": "singular plural",
    "plural and weak singular": ["plural", "weak singular"],
    "dative-directional": "dative directional",
    "preterite and supine": "preterite supine",
    "genitive and dative": "genitive dative",
    "genitive and plural": "genitive plural",
    "dative and accusative": "dative accusative",
    "accusative/illative": "accusative illative",
    "accusative and ablative": "accusative ablative",
    "dative and accusative singular": "dative accusative singular",
    "no nominative": "no-nominative",
    "simple past": "past",
    "past —": "no-past",
    "simple future": "future",
    "simple present": "present",
    "simple past and past participle": ["past", "past participle"],
    "simple past tense and past participle": ["past", "past participle"],
    "taking a past participle": "with-past-participle",
    "literary or in compounds": "literary in-compounds",
    "certain compounds": "in-compounds idiomatic",
    "participial adjective": "participle adjective error-misspelling",
    "literary or archaic": "literary archaic",
    "literaly or archaic": "literary archaic error-misspelling",
    "literary or dialectal": "literary dialectal",
    "dated or dialectal": "dated dialectal",
    "dialectal or colloquial": "dialectal colloquial",
    "dialectal or obsolete": "dialectal obsolete",
    # XXX what is this? "with verb in simple tense": "with-simple",
    "in simple past tense": "past",
    "for most verbs": "usually",
    "in general": "usually",
    "in variation": "in-variation",
    "genitive/dative": "genitive dative",
    "dative/locative": "dative locative",
    "dative/locative/partitive": "dative locative partitive",
    "dative/partitive": "dative partitive",
    "genitive/dative/prepositional": "genitive dative prepositional",
    "dative/instrumental": "dative instrumental",
    "dative/instrumental/prepositional": "dative instrumental prepositional",
    "genitive/prepositional": "genitive prepositional",
    "genitive/dative/locative": "genitive dative locative",
    "genitive/dative/ablative": "genitive dative ablative",
    "dative/ablative/locative": "dative ablative locative",
    "ablative/vocative": "ablative vocative",
    "ablative/locative": "ablative locative",
    "ablative/instrumental": "ablative instrumental",
    "dative/ablative": "dative ablative",
    "genitive/instrumental/locative": "genitive instrumental locative",
    "genitive/dative/locative/vocative": "genitive dative locative vocative",
    "genitive/dative/instrumental": "genitive dative instrumental",
    "genitive/dative/instrumental/prepositional":
    "genitive dative instrumental prepositional",
    "prepositional masculine / neuter singular":
    ["prepositional masculine", "neuter singular"],
    "+ prepositional case": "with-prepositional",
    "+prepositional": "with-prepositional",
    "+ por": "with-por",
    "Radical": "radical",
    "accusative/instrumental": "accusative instrumental",
    "dative/adverbial case": "dative adverbial",
    "dative/genitive": "dative genitive",
    "dative/genitive/instrumental": "dative genitive instrumental",
    "dative/accusative": "dative accusative",
    "dative/accusative/locative": "dative accusative locative",
    "genitive/accusative/prepositional":
    "genitive accusative prepositional",
    "genitive/accusative/vocative": "genitive accusative vocative",
    "genitive/dative/accusative": "genitive dative accusative",
    "genitive/animate accusative": ["genitive", "animate accusative"],
    "genitive/accusative animate/prepositional":
    ["genitive prepositional", "accusative animate"],
    "accusative plural and genitive plural": "accusative genitive plural",
    "hidden-n declension": "hidden-n",
    "declension pattern of": "declension-pattern-of",
    "first/declension-2 adjective":
    "declension-1 declension-2 adjective",
    "first/declension-2 participle":
    "declension-1 declension-2 participle",
    "class 9/10": "class-9 class-10",
    "class 5/6": "class-5 class-6",
    "class 3/4": "class-3 class-4",
    "class 7/8": "class-7 class-8",
    "class 1/2": "class-1 class-2",
    "class 11/10": "class-11 class-10",
    "class 11/12": "class-11 class-12",
    "nc 1/2": "class-1 class-2",
    "nc 3/4": "class-3 class-4",
    "nc 5/6": "class-5 class-6",
    "nc 7/8": "class-7 class-8",
    "nc 9/10": "class-9 class-10",
    "nc 1": "class-1",
    "nc 2": "class-2",
    "nc 3": "class-3",
    "nc 4": "class-4",
    "nc 5": "class-5",
    "nc 6": "class-6",
    "nc 7": "class-7",
    "nc 8": "class-8",
    "nc 9": "class-9",
    "nc 10": "class-10",
    "nc 11": "class-11",
    "nc 12": "class-12",
    "nc 13": "class-13",
    "nc 14": "class-14",
    "nc 15": "class-15",
    "nc 16": "class-16",
    "nc 17": "class-17",
    "nc 18": "class-18",
    "cl. 2 to cl. 11 and cl. 16 to cl. 18":
    "class-2 class-3 class-4 class-5 class-6 class-7 class-8 class-9 class-10 class-11 class-16 class-17 class-18",
    "refl": "reflexive",
    "coll.": "colloquial",
    "colloq.": "colloquial",
    "colloq": "colloquial",
    "collo.": "colloquial",
    "collective when uncountable": "countable uncountable collective",
    "coloquial": "colloquial",
    "more colloquial": "colloquial",
    "used colloquially and jokingly": "colloquial humorous",
    "used adverbially": "adverbial",
    "adverbially": "adverbial",
    "intr.": "intransitive",
    "tr.": "transitive",
    "trans": "transitive",
    "intransitive use": "intransitive",
    "intransitive senses": "intransitive",
    "intr. impers.": "intransitive impersonal",
    "abbrev.": "abbreviation",
    "Abbreviation": "abbreviation",
    "Hiragana": "hiragana",
    "Katakana": "katakana",
    "synon. but common": "synonym common",
    "common hyperhyms": "common hypernym",
    "much more common": "common",
    "common gender": "common-gender",
    "incorrectly": "proscribed",
    "incorrect": "proscribed",
    "a hyponymic term": "hyponym",
    "a hypernymic term": "hypernym",
    "transitively": "transitive",
    "intransitively": "intransitive",
    "transitiv": "transitive",
    "intransitiv": "intransitive",
    "nominalized adjective": "noun-from-adj",
    "adjectivized noun": "adjectival",
    "adv.": "adverb",
    "infomal": "informal error-misspelling",
    "informally": "informal",
    "formally": "formal",
    "very formal": "formal",
    "unmarked form": "unstressed",
    "marked form": "stressed",
    "inifnitive": "infinitive error-misspelling",
    "inf.": "informal",
    "unformal": "informal",
    "unpolite": "impolite",
    "fairly polite": "polite",
    "postnominal": "postpositional",
    "first/second declension": "declension-1 declension-2",
    "first/second-declension": "declension-1 declension-2",
    "first/declension-2 suffix":
    "declension-1 declension-2 suffix",
    "first/declension-2 numeral plural only":
    "declension-1 declension-2 numeral plural-only plural",
    "with gendered nouns": "with-gendered-noun",
    "possessive (with noun)": "possessive with-noun",
    "possessive (without noun)": "possessive without-noun",
    "without a main word": "without-noun",
    "informal 1st possessive": "informal first-person possessive",
    "informal augmentations": "informal augmented",
    "informal alternatives": "informal",
    "strumental/locative/lative form": "instrumental locative lative",
    "instrumental/locative/lative form": "instrumental locative lative",
    "reflexive/dative/accusative form": "reflexive dative accusative",
    "reflexive/accusative/dative form": "reflexive accusative dative",
    "third-person/impersonal": "third-person impersonal",
    "impersonal/third-person": "impersonal third-person",
    "lative form": "lative",
    "reflexive form": "reflexive",
    "reflexive for": "reflexive form-of",
    "passive for": "passive form-of",
    "dative form": "dative",
    "accusative form": "accusative",
    "formal or literary": ["formal", "literary"],
    "formal or plural": ["formal", "plural"],
    "formal and written": "formal literary",
    "addressing kings and queens": "formal deferential",
    "adressing kings and queens": "formal deferential",
    "impolite 2nd possessive": "informal second-person possessive",
    "casual": "informal",
    "fast speech": "informal",
    "strong personal": "strong personal pronoun",
    "weak personal": "weak personal pronoun",
    "persent participle": "present participle",
    "with adjective or adjective-phrase complement": "with-adjective",
    "with accusative or dative": "with-accusative with-dative",
    "with accusative or genitive": "with-accusative with-genitive",
    "with accusative or ablative": "with-accusative with-ablative",
    "genitive or accusative": ["genitive accusative"],
    "genitive of personal pronoun": "genitive personal pronoun",
    "nominative and accusative definite singular":
    "nominative accusative definite singular",
    "not generally used in the plural": "singular-normally",
    "+ genitive": "with-genitive",
    "+ genitive possessive suffix or elative":
    "with-genitive with-possessive-suffix with-elative",
    "+ genitive-accusative": "with-genitive",
    "genitive + ~": "with-genitive postpositional",
    "+ partitive or (less common) possessive suffix":
    "with-partitive with-possessive-suffix",
    "+ allative": "with-allative",
    "[an (about) + accusative]": "with-an with-accusative",
    "less common": "uncommon",
    "less frequently": "uncommon",
    "no perfect or supine stem": "no-perfect no-supine",
    "no present participle": "no-present-participle",
    "no past participle": "no-past-participle",
    "past participle (obsolete except in adjectival use)":
    "obsolete past participle",
    "short past participle": "past participle short-form",
    "short past adverbial perfective participle":
    "past adverbial perfective participle short-form",
    "short past adverbial imperfective participle":
    "past adverbial imperfective participle short-form",
    "short masculine": "masculine short-form",
    "short feminine": "feminine short-form",
    "short neuter": "neuter short-form",
    "short plural": "plural short-form",
    "short singular": "singular short-form",
    "long past participle": "past participle long-form",
    "of the past participle": "past participle",
    "past participle n": "past participle neuter",
    "past participle c": "past participle common-gender",
    "past participle f": "past participle feminine",
    "past participle m": "past participle masculine",
    "past participle pl": "past participle plural",
    "of the present participle": "present participle",
    "adverbial locative noun in the pa, ku, or mu locative classes":
    "adverbial locative",
    "comparative -": "no-comparative",
    "superlative -": "no-superlative",
    "comparative form only": "comparative-only",
    "1 declension": "declension-1",
    "4 declension": "declension-4",
    "feminine ? declension": "feminine",
    "masculine ? declension": "masculine",
    "1st declension": "declension-1",
    "2nd declension": "declension-2",
    "3rd declension": "declension-3",
    "4th declension": "declension-4",
    "5th declension": "declension-5",
    "6th declension": "declension-6",
    "2nd-person": "second-person",
    "1st-person": "first-person",
    "3rd-person": "third-person",
    "1st person": "first-person",
    "2nd person": "second-person",
    "3rd person": "third-person",
    "1st actor trigger": "actor-i",
    "2nd actor trigger": "actor-ii",
    "3rd actor trigger": "actor-iii",
    "4th actor trigger": "actor-iv",
    "object trigger": "objective",
    "1st object trigger": "objective actor-i",
    "2nd object trigger": "objective actor-ii",
    "3rd object trigger": "objective actor-iii",
    "4th object trigger": "objective actor-iv",
    "potential mood": "potential",
    "causative mood": "causative",
    "comitative trigger": "comitative",
    "1st comitative trigger": "comitative actor-i",
    "2nd comitative trigger": "comitative actor-ii",
    "3rd comitative trigger": "comitative actor-iii",
    "4th comitative trigger": "comitative actor-iv",
    "locative trigger": "locative",
    "thematic trigger": "thematic",
    "benefactive trigger": "benefactive",
    "instrument trigger": "instrumental",
    "1st instrument trigger": "instrumental actor-i",
    "2nd instrument trigger": "instrumental actor-ii",
    "3rd instrument trigger": "instrumental actor-iii",
    "4th instrument trigger": "instrumental actor-iv",
    "1st": "first-person",
    "2nd": "second-person",
    "3rd": "third-person",
    "plural inv": "plural invariable",
    "plural not attested": "no-plural",
    "no plural forms": "no-plural",
    "not translated": "not-translated",
    "not mutable": "not-mutable",
    "used only predicatively": "predicative",
    "only in predicative position": "predicative",
    "only predicative": "predicative",
    "only among women": "",
    "predicate-only":
    "predicative error-misspelling",  # eleng/Luxembourgish
    "predicative only": "predicative",
    "predicatively": "predicative",
    "in attributive use": "attributive",
    "(attributive)": "attributive",
    "(predicative)": "predicative",
    "(uncountable)": "uncountable",
    "(as a measure)": "",
    "only in attributive use": "attributive",
    "present tense": "present",
    "past tense": "past",
    "feminine counterpart": "feminine",
    "feminine form": "feminine",
    "masculine counterpart": "masculine",
    "masculine form": "masculine",
    "neuter form": "neuter",
    "passive counterpart": "passive",
    "active counterpart": "active",
    "attested mostly in the passive": "passive-mostly",
    "basic stem form": "stem",
    "no supine stem": "no-supine",
    "no perfect stem": "no-perfect",
    "construct state": "construct",
    "construct form": "construct",
    "phonemic reduplicative": "reduplication",
    "reduplicated": "reduplication",
    "neutrally formal": "polite",
    "objective case": "objective",
    "first person": "first-person",
    "second person": "second-person",
    "third person": "third-person",
    "nominative case": "nominative",
    "genitive case": "genitive",
    "genitive 1": "genitive",
    "genitive 2": "genitive",
    "genitive 3": "genitive",
    "dative case": "dative",
    "dative 1": "dative",
    "dative 2": "dative",
    "dative 3": "dative",
    "accusative 1": "accusative",
    "accusative 2": "accusative",
    "accusative 3": "accusative",
    "accusative case": "accusative",
    "ergative cases": "ergative",
    "absolutive case": "absolutive",
    "ablative case": "ablative",
    "genitive unattested": "no-genitive",
    "genitive -": "no-genitive",
    "nominative plural -": "no-nominative-plural",
    "colloquially also feminine": "colloquial feminine",
    "colloquial or pejorative": "colloquial pejorative",
    "colloquial or dialectal": "colloquial dialectal",
    "pejorative or racial slur": "pejorative slur",
    "pejoratively": "pejorative",
    "racial slur": "slur",
    "in some dialects": "dialectal",
    "in other dialects": "dialectal",
    "dialects": "dialectal",
    "pejorativ": "pejorative error-misspelling",
    "idionomic": "idiomatic error-misspelling",
    "idiom": "idiomatic",
    "humorously self-deprecating": "humorous",
    "rare/awkward": "rare",
    "rare/archaic": "archaic",
    "archaic or Scotland": "archaic Scotland",
    "extremely rare": "rare",
    "now quite rare": "rare",
    "rarefied": "rare",
    "rarely": "rare",
    "rarer form": "rare",
    "relatively rare": "rare",
    "personified": "person",
    "person or animal": "person animal-not-person",
    "found only in the imperfective tenses": "no-perfect",
    "imperfekt": "imperfect error-misspelling",
    "imperf. aspect": "imperfect",
    "perfective 1": "perfect",
    "perfective 2": "perfect",
    "in counterfactual conditionals": "conditional counterfactual",
    "improbable of counterfactual": "usually counterfactual",
    "third plural indicative": "third-person plural indicative",
    "defective verb": "defective",
    "+ active 3rd infinitive in elative": "with-infinitive-iii-elative",
    "+ active 3rd infinitive in illative": "with-infinitive-iii-illative",
    "+ third infinitive in illative": "with-infinitive-iii-illative",
    "+ verb in 3rd infinitive abessive": "with-infinitive-iii-abessive",
    "+ verb in third infinitive illative or adverb":
    "with-infinitive-iii with-illative with-adverb",
    "+ partitive + 3rd person singular": "with-partitive",
    "3rd possessive": "third-person possessive",
    "active voice": "active",
    "+ infinitive": "with-infinitive",
    "+ first infinitive": "with-infinitive-i",
    "transitive + first infinitive": "transitive with-infinitive-i",
    "transitive + kV": "transitive with-kV",  # gǀkxʻâã/ǃXóõ
    "+ a + infinitive": "with-a with-infinitive",
    "+ indicative mood": "with-indicative",
    "+ conditional mood": "with-conditional",
    "+nominative": "with-nominative",
    "+ nominative": "with-nominative",
    "plus genitive": "with-genitive",
    "+ genitive": "with-genitive",
    "+ genetive": "with-genitive error-misspelling",
    "+genitive": "with-genitive",
    "+ genitive case": "with-genitive",
    "genitive +": "with-genitive",
    "nominative +": "with-nominative",
    "genitive or possessive suffix +": "with-genitive with-possessive-suffix",
    "with genitive case": "with-genitive",
    "with genitive": "with-genitive",
    "+dative": "with-dative",
    "+ dative case": "with-dative",
    "dative case +": "with-dative",
    "+ dative": "with-dative",
    "+ historic dative": "with-dative historic",
    "only with adjectives": "with-adjective",
    "plus dative": "with-dative",
    "plus dative case": "with-dative",
    "with dative": "with-dative",
    "with the dative": "with-dative",
    "with dative case": "with-dative",
    "+ accusative": "with-accusative",
    "+ accusative case": "with-accusative",
    "+accusative": "with-accusative",
    "with accusative case": "with-accusative",
    "with the accusative": "with-accusative",
    "with accusative": "with-accusative",
    "plus accusative": "with-accusative",
    "takes accusative": "with-accusative",
    "takes accusative object": "with-accusative",
    "governs the accusative": "with-accusative",
    "governs the genitive": "with-genitive",
    "governs the dative": "with-dative",
    "takes dative": "with-dative",
    "takes dative case": "with-dative",
    "zhuyin": "bopomofo",
    "Zhuyin": "bopomofo",
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
    "with subjunctives": "with-subjunctive",
    "+ subordinate clause": "with-subordinate-clause",
    "+ instrumental": "with-instrumental",
    "+instrumental": "with-instrumental",
    "+ instrumental case": "with-instrumental",
    "with instrumental case": "with-instrumental",
    "with instrumental": "with-instrumental",
    "plus instrumental": "with-instrumental",
    "with instrumental or genitive case": "with-instrumental with-genitive",
    "with instrumental or dative case": "with-instrumental with-dative",
    "+ locative": "with-locative",
    "+ locative case": "with-locative",
    "with locative": "with-locative",
    "+ illative": "with-illative",
    "intransitive + illative": "intransitive with-illative",
    "intransitive + elative": "intransitive with-elative",
    "intransitive + inessive or adessive":
    "intransitive with-inessive with-adessive",
    "intransitive + inessive": "intransitive with-inessive",
    "intransitive + adessive": "intransitive with-adessive",
    "intransitive + translative": "intransitive with-translative",
    "intransitive + partitive or transitive + accusative":
    "intransitive with-partitive transitive with-accusative",
    "transitive + partitive": "transitive with-partitive",
    "transitive + partitive + essive":
    "transitive with-partitive with-essive",
    "transitive + elative + kiinni":
    "transitive with-elative",
    "transitive (+ yllään) + partitive":
    "transitive with-partitive",
    "transitive + accusative": "transitive with-accusative",
    "transitive + elative": "transitive with-elative",
    "transitive or reflexive": "transitive reflexive",
    "illative + 3rd-person singular":
    "with-illative with-third-person-singular",
    "partitive + 3rd-person singular":
    "with-partitive with-third-person-singular",
    "+ translative": "with-translative",
    "+ negative adjective in translative": "with-translative with-negative-adj",
    "with negation": "with-negation",
    "with negated verb": "with-negation",
    "when negated": "with-negation",
    "usu. in negative": "usually with-negation",
    "predicate of copula": "copulative",
    "copular verb": "copulative",
    "copula": "copulative",  # náina/Phalura
    "+ adessive": "with-adessive",
    "+ adessive or illative": "with-adessive with-illative",
    "+absolutive": "with-absolutive",
    "+ absolutive": "with-absolutive",
    "with absolutive case": "with-absolutive",
    "with absolutive": "with-absolutive",
    "+ absolutive case": "with-absolutive",
    "plus absolutive": "with-absolutive",
    "take nouns in absolute case": "with-absolute",
    "takes nouns in absolute case": "with-absolute",
    "takes absolute case": "with-absolute",
    "+elative": "with-elative",
    "+ elative": "with-elative",
    "elative +": "with-elative",
    "elative case": "elative",
    "+ [elative]": "with-elative",
    "with elative case": "with-elative",
    "with elative": "with-elative",
    "plus elative": "with-elative",
    "+ essive": "with-essive",
    "+ comparative": "with-comparative",
    "+objective": "with-objective",
    "+ objective": "with-objective",
    "with objective case": "with-objective",
    "with objective": "with-objective",
    "plus objective": "with-objective",
    "sublative case": "sublative",
    "terminative case": "terminative",
    "+ present form": "with-present",
    "+ noun phrase] + subjunctive (verb)":
    "with-noun-phrase with-subjunctive",
    "with noun phrase": "with-noun-phrase",
    "+ [nounphrase] + subjunctive":
    "with-noun-phrase with-subjunctive",
    "+ number": "with-number",
    "with number": "with-number",
    "optative mood +": "with-optative",
    "not used in plural form": "no-plural",
    "in plural the singular form is used": "singular-only",
    "indecl": "indeclinable",
    "all forms unconjugated": "indeclinable",
    "not declined": "indeclinable",
    "not declinable": "indeclinable",
    "undeclinable": "indeclinable",
    "inconjugable": "indeclinable error-misspelling",
    "indeclinable?": "indeclinable",
    "no inflections": "indeclinable",
    "not often used": "rare",
    "interrogative adverb": "interrogative adverb",
    "perfect tense": "perfect",
    "intensive": "emphatic",
    "intensifier": "emphatic",
    "changed conjunct form": "conjunct",
    "biblical hebrew pausal form": "pausal Biblical",
    "bible": "Biblical",
    "Bibilical": "Biblical",
    "emphatic form": "emphatic",
    "emphatic form of": "emphatic form-of",
    "emphatically": "emphatic",
    "emphatical": "emphatic",
    "standard form": "standard",
    "augmented form": "augmented",
    "active form": "active",
    "passive form": "passive",
    "pre-1989 IPA": "pre-1989-IPA",
    "mutated form": "mutated",
    "auxiliary verb": "auxiliary",
    "modal auxiliary verb": "auxiliary modal",
    "transitive verb": "transitive",
    "tr and intr": "transitive intransitive",
    "intransitive verb": "intransitive",
    "transitive or intransitive": "transitive intransitive",
    "male equivalent": "masculine",
    "in compounds": "in-compounds",
    "in combination": "in-compounds",
    "attribute": "attributive",
    "in the past subjunctive": "with-past with-subjunctive",
    "in conditional": "with-conditional",
    "use the subjunctive tense of the verb that follows": "with-subjunctive",
    "kyūjitai form": "kyūjitai",
    "kyūjitai kanji": "kyūjitai",
    "shinjitai form": "shinjitai",
    "shinjitai kanji": "shinjitai",
    "grade 1 “Kyōiku” kanji": "grade-1-kanji",
    "grade 2 “Kyōiku” kanji": "grade-2-kanji",
    "grade 3 “Kyōiku” kanji": "grade-3-kanji",
    "grade 4 “Kyōiku” kanji": "grade-4-kanji",
    "grade 5 “Kyōiku” kanji": "grade-5-kanji",
    "grade 6 “Kyōiku” kanji": "grade-6-kanji",
    "uncommon “Hyōgai” kanji": "uncommon Hyōgai",
    "dialectical": "dialectal",
    "dialectal or archaic": "dialectal archaic",
    "dialectal or poetic": "dialectal poetic",
    "dialect": "dialectal",
    "obsolescent": "possibly obsolete",
    "obsolete outside dialects": "obsolete dialectal",
    "antiquated": "dated",
    "19th century": "archaic",
    "dated or regional": "dated regional",
    "dated or archaic": "archaic",
    "common and polite term": "polite",
    "most common but potentially demeaning term": "possibly derogatory",
    "highly academic": "literary",
    "highly irregular": "irregular",
    "academic": "literary",
    "learned": "literary",
    "archaic ortography": "archaic",
    "archaic elsewhere": "dialectal",
    "in the plural": "plural-only plural",
    "derog.": "derogatory",
    "derogative": "derogatory",
    "derogatively": "derogatory",
    "disparaging": "derogatory",
    "disparagingly": "derogatory",  # feic/Irish
    "deprecative": "derogatory",
    "collective sense": "collective",
    "relatively rare": "rare",
    "very rare": "rare",
    "very informal": "informal",
    "less formal": "informal",
    "very archaic": "archaic",
    "outdated": "archaic",
    "historiographic": "historical",
    "with a + inf.": "with-a with-infinitive",
    "with di + inf.": "with-di with-infinitive",
    "with che + subj.": "with-che with-subjunctive",
    "with inf.": "with-infinitive",
    "with infinitive": "with-infinitive",
    "with following infinitive": "with-infinitive",
    "followed by an infinitive": "with-infinitive",
    "zu-infinitive": "infinitive infinitive-zu",
    "zu infinitive": "infinitive infinitive-zu",
    "da-infinitive": "infinitive infinitive-da",
    "Use the future tense": "with-future",
    # XXX re-enable "~ се": "with-ce",
    "strong/mixed": "strong mixed",
    "strong/weak/mixed": "strong weak mixed",
    "weak/mixed": "weak mixed",
    "weak verb": "weak",
    "Weak conjugation": "weak",
    "Strong conjugation": "strong",
    "no auxiliary": "no-auxiliary",
    "nominative/accusative": "nominative accusative",
    "masculine/feminine": "masculine feminine",
    "masculine/neuter": "masculine neuter",
    "present/future": "present future",
    "future/present": "present future",
    "present/aoriest": "present aorist error-misspelling",
    "superlative degree": "superlative",
    "sup.": "superlative",
    "comparative degree": "comparative",
    "comp.": "comparative",
    "comparatives": "comparative",
    "positive degree": "positive",
    "pos.": "positive",
    "positive outcome": "positive",
    "negative outcome": "negative",
    "equative degree": "equative",
    "indicative and subjunctive": "indicative subjunctive",
    "indicative/subjunctive": "indicative subjunctive",
    "second/third-person": "second-person third-person",
    "singular/plural": "singular plural",
    "in the singular": "singular",
    "in the plural": "plural",
    "in singular": "singular",
    "in plural": "plural",
    "dual/plural": "dual plural",
    "collective or in the plural": "collective in-plural",
    "in the plural": "in-plural",
    "(with savrtsobi)": "with-savrtsobi",
    "plural and definite singular": ["plural", "definite singular"],
    "feminine singular & neuter plural": ["feminine singular", "neuter plural"],
    "partitive/illative": "partitive illative",
    "oblique/nominative": "oblique nominative",
    "nominative/vocative/dative/strong genitive":
    ["nominative vocative dative", "strong genitive"],
    "non-attributive": "predicative",
    "not predicative": "attributive",
    "attributive use": "attributive",
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
    "past indicative and past participle": "past indicative participle",
    "all-gender": "",
    "gender unknown": "",
    "all-case": "",
    "accusative/dative": "accusative dative",
    "accusative-singular": "accusative singular",
    "accusative-genitive": "accusative genitive",
    "dative/locative/instrumental": "dative locative instrumental",
    "dative/vocative": "dative vocative",
    "dative/vocative/locative": "dative vocative locative",
    "dative/prepositional": "dative prepositional",
    "dative/prepositional/vocative": "dative prepositional vocative",
    "prepositional/vocative": "prepositional vocative",
    "prepositional/locative": "prepositional locative",
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
    "imperfective/perfective": "imperfective perfective",
    "neg. perfective": "perfective negative",
    "neg. continuous": "continuative negative",
    "negative form": "negative",
    "negating particle": "negative particle",
    "negation": "negative",
    "continuous": "continuative",
    "continuously": "continuative",
    "animate/inanimate": "animate inanimate",
    "animate or inanimate": "animate inanimate",
    "locative/vocative": "locative vocative",
    "prospective/agentive": "prospective agentive",
    "genitive/accusative": "genitive accusative",
    "singular/duoplural": "singular dual plural",
    "duoplural": "dual plural",
    "1st/3rd": "first-person third-person",
    "first/second-person": "first-person second-person",
    "first/second/third-person":
    "first-person second-person third-person",
    "first/third/third-person": "first-person third-person",
    "first-/third-person": "first-person third-person",
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
    "male equivalent": "masculine",
    "direct/oblique/vocative": "direct oblique vocative",
    "definite/plural": "definite plural",
    "singular definite and plural": ["singular definite", "plural"],
    "agent noun": "agent",
    "agent noun of": "agent form-of",
    "Principle verb suffix": "agent suffix noun-from-verb",
    "third active infinitive": "infinitive-iii active",
    "third passive infinitive": "infinitive-iii passive",
    "British spelling": "UK",
    "Roman spelling": "romanization",
    "Perso-Arabic spelling": "Perso-Arabic",
    "Arabic/Persian": "Arabic Persian",
    "Arabic spelling": "Arabic",
    "Urdu spelling": "Urdu",
    "Urdu spelling of": "Urdu alt-of",
    "Hindi spelling": "Hindi",
    "Jawi spelling": "Jawi",
    "Mongolian spelling": "Mongolian",
    "Shahmukhi spelling": "Shahmukhi",
    "Rumi spelling": "Rumi",
    "Gurmukhi spelling": "Gurmukhi",
    "Hebrew spelling": "Hebrew",
    "Baybayin spelling": "Baybayin",
    "Tai-Tham spelling": "Tai-Tham",
    "Greek spelling": "Greek",
    "Thai spelling": "Thai",
    "Newa spelling": "Newa",
    "Devanagari spelling": "Devanagari",
    "Javanese spelling": "Javanese",
    "Gujarati spelling": "Gujarati",
    "Cham spelling": "Cham",
    "eye dialect": "pronunciation-spelling",
    "feminist or eye dialect": "pronunciation-spelling",
    "enclitic and proclitic": "enclitic proclitic",
    "Enclitic contractions": "enclitic contraction",
    "Proclitic contractions": "proclitic contraction",
    "enclitic form": "enclitic",
    "Devanagari script form of": "alt-of Devanagari",
    "Hebrew script": "Hebrew",
    "Mongolian script": "Mongolian",
    "Bengali script": "Bengali",
    "script": "character",
    "letters": "letter",
    "digits": "digit",
    "characters": "character",
    "symbols": "symbol",
    "tetragrams": "symbol",
    "letter names": "letter-name",
    "Cyrillic-script": "Cyrillic",
    "Latin-script": "Latin",
    "obsolete form of": "alt-of obsolete",
    "former word": "obsolete",
    "obs.": "obsolete",
    "etymological spelling": "nonstandard",
    "(Dialectological)": "dialectal",
    "dialectal or nonstandard": "dialectal",
    "(hence past tense)": "past",
    "(ablative case)": "ablative",
    "(genitive case)": "genitive",
    "(suffix conjugation)": "suffix",
    "(suffix conjugation)": "prefix",
    "(nós)": "with-nos",
    "(eu)": "with-eu",
    "(vós)": "with-vós",
    "(vos)": "with-vos",
    "(voseo)": "with-voseo",
    "(tu)": "with-tu",
    "(tú)": "with-tú",
    "(eles)": "with-eles",
    "(elas)": "with-elas",
    "(vocês)": "with-vocês",
    "(usted)": "with-usted",
    "(ustedes)": "with-ustedes",
    "(yo)": "with-yo",
    "(ele, ela, also used with tu and você?)":
    "with-ele with-ela with-tu with-você",
    "(eles and elas, also used with vocês and others)":
    "with-eles with-elas with-vocês with-others",
    "(eles, elas, also used with vocês)":
    "with-eles with-elas with-vocês",
    "(você)": "with-você",
    "(hiri)": "with-hiri",
    "(hura)": "with-hura",
    "(zuek)": "with-zuek",
    "(vós, sometimes used with vocês)": "with-vós with-vocês",
    "(gij)": "with-gij",
    "(tu, sometimes used with você)": "with-tu with-você",
    "(\u00e9l, ella, also used with usted)":
    "with-él with-ella with-usted",
    "(ellos, ellas, also used with ustedes)":
    "with-ellos with-ellas with-ustedes",
    "(nosotros, nosotras)": "with-nosotros with-nosotras",
    "(vosotros, vosotras)": "with-vosotros with-vosotras",
    "(vosotros or vosotras)": "with-vosotros with-vosotras",
    "(ele and ela, also used with você and others)":
    "with-ele with-ela with-você with-others",
    "(ele, ela, also used with tu and você)":
    "with-ele with-ela with-tu with-você",
    "former reform[s] only": "",
    "no conj.": "",  # XXX conjunctive/conjugation/indeclinable? dot/Latvian
    "no construct forms": "no-construct-forms",
    "no nominative plural": "no-nominative-plural",
    "no supine": "no-supine",
    "no perfect": "no-perfect",
    "no perfective": "no-perfect",
    "no genitive": "no-genitive",
    "no superlative": "no-superlative",
    "no sup.": "no-superlative",
    "no comparative": "no-comparative",
    "no comp.": "no-comparative",
    "no singulative": "no-singulative",
    "no plural": "no-plural",
    "no singular": "plural-only plural",
    "not comparable": "not-comparable",
    "incomparable": "not-comparable",
    "not generally comparable": "usually not-comparable",
    "plurale tantum": "plural-only plural",
    "plurare tantum": "plural-only plural",
    "pluralia tantum": "plural-only plural",
    "singulare tantum": "singular-only singular",
    "normally plural": "plural-normally",
    "used mostly in plural form": "plural-normally",
    "used mostly in the plural form": "plural-normally",
    "most often in the plural": "plural-normally",
    "used especially in the plural form": "plural-normally",
    "usually in the plural": "plural-normally",
    "now usually in the plural": "plural-normally",
    "suffixed pronoun": "suffix pronoun",
    "possessive suffix": "possessive suffix",
    "possessive determiner": "possessive determiner",
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
    "form I": "form-i",
    "form-I": "form-i",
    "form II": "form-ii",
    "form-II": "form-ii",
    "form III": "form-iii",
    "form-III": "form-iii",
    "form IV": "form-iv",
    "form-IV": "form-iv",
    "form V": "form-v",
    "form-V": "form-v",
    "form VI": "form-vi",
    "form-VI": "form-vi",
    "form VII": "form-vii",
    "form-VII": "form-vii",
    "form VIII": "form-viii",
    "form-VIII": "form-viii",
    "form IX": "form-ix",
    "form-IX": "form-ix",
    "form X": "form-x",
    "form-X": "form-x",
    "form XI": "form-xi",
    "form-XI": "form-xi",
    "form XII": "form-xii",
    "form-XII": "form-xii",
    "form XIII": "form-xiii",
    "form-XIII": "form-xiii",
    "form Iq": "form-iq",
    "form IIq": "form-iiq",
    "form IIIq": "form-iiiq",
    "form IVq": "form-ivq",
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
    "class 9a": "class-9a",
    "class 10": "class-10",
    "class 10a": "class-10",
    "class 11": "class-11",
    "class 12": "class-12",
    "class 13": "class-13",
    "class 14": "class-14",
    "class 15": "class-15",
    "class 16": "class-16",
    "class 17": "class-17",
    "class 18": "class-18",
    "m-wa class": "class-1 class-2",
    "m-mi class": "class-3 class-4",
    "ma class": "class-5 class-6",
    "ki-vi class": "class-7 class-8",
    "n class": "class-9 class-10",
    "u class": "class-11 class-12 class-14",
    "ku class": "class-15",
    "pa class": "class-16",
    # "ku class": "class-17",  # XXX how to distinguish from class-15?
    "mu class": "class-18",
    "first declension": "declension-1",
    "second declension": "declension-2",
    "third declension": "declension-3",
    "fourth declension": "declension-4",
    "fifth declension": "declension-5",
    "first-declension": "declension-1",
    "second-declension": "declension-2",
    "third-declension": "declension-3",
    "fourth-declension": "declension-4",
    "fifth-declension": "declension-5",
    "1st conj.": "conjugation-1",
    "2nd conj.": "conjugation-2",
    "3rd conj.": "conjugation-3",
    "4th conj.": "conjugation-4",
    "5th conj.": "conjugation-5",
    "6th conj.": "conjugation-6",
    "7th conj.": "conjugation-7",
    "first conjugation": "conjugation-1",
    "second conjugation": "conjugation-2",
    "third conjugation": "conjugation-3",
    "fourth conjugation": "conjugation-4",
    "fifth conjugation": "conjugation-5",
    "sixth conjugation": "conjugation-6",
    "seventh conjugation": "conjugation-7",
    "stress pattern 1": "stress-pattern-1",
    "stress pattern 2": "stress-pattern-2",
    "stress pattern 3": "stress-pattern-3",
    "stress pattern 3a": "stress-pattern-3a",
    "stress pattern 3b": "stress-pattern-3b",
    "stress pattern 4": "stress-pattern-4",
    "preposition stressed": "stressed-preposition",
    "tone I": "tone-1",
    "tone II": "tone-2",
    "type p": "type-p",
    "type P": "type-p",
    "type u": "type-u",
    "type U": "type-u",
    "type up": "type-up",
    "type UP": "type-up",
    "type a": "type-a",
    "type A": "type-a",
    "type ua": "type-ua",
    "type UA": "type-ua",
    "form of": "form-of",
    "ordinal form of": "ordinal form-of",
    "ordinal form of the number": "ordinal form-of",
    "ordinal form of": "ordinal form-of",
    "ordinal of": "ordinal form-of",
    "ordinal number corresponding to the cardinal number":
    "ordinal form-of",
    "ordinal form of the cardinal number": "ordinal form-of",
    "the ordinal number": "ordinal alt-of",
    "used in the form": "used-in-the-form",
    "upper case": "uppercase",
    "upper-case": "uppercase",
    "lower case": "lowercase",
    "lower-case": "lowercase",
    "mixed case": "mixedcase",
    "mixed-case": "mixedcase",
    "capital": "uppercase",
    "verb form i": "verb-form-i",
    "verb form ii": "verb-form-ii",
    "pi'el construction": "construction-pi'el",
    "pa'el construction": "construction-pa'el",
    "pa'al construction": "construction-pa'al",
    "hif'il construction": "construction-hif'il",
    "hitpa'el construction": "construction-hitpa'el",
    "hitpu'al construction": "construction-hitpu'al",
    "pu'al construction": "construction-pu'al",
    "nif'al construction": "construction-nif'al",
    "huf'al construction": "construction-huf'al",
    "peal construction": "construction-peal",
    "verbal noun": "noun-from-verb",
    "Verbal derivations": "verb",
    "abstract noun": "abstract-noun",
    "concrete verb": "concrete",
    "concrete verbs": "concrete",
    "genitive singular as substantive": "genitive singular substantive",
    "female names": "feminine proper-noun",
    "proper name": "proper-noun",
    "proper noun": "proper-noun",
    "proper nouns": "proper-noun",
    "usually in the": "usually",
    "usually in the negative": "usually with-negation",
    "non-scientific usage": "non-scientific",
    "krama inggil": "honorific",
    "krama andhap": "humble",
    "krama-ngoko": "informal",
    "ngoko": "informal",
    "McCune–Reischauer": "McCune-Reischauer",  # Dash type differs
    "gender indeterminate": "gender-neutral",
    "singular only": "singular singular-only singular",
    "not used in plural": "singular-only singular",
    "singularonly": "singular-only singular",
    "plural only": "plural plural-only",
    "imperative only": "imperative-only",
    "Imperative form of of": "imperative form-of",  # ba/Middle English
    "in general sense": "broadly",
    "by extension": "broadly",
    "by metonymy": "metonymically",
    "by synecdoche": "synecdoche",
    "by semantic narrowing": "narrowly",
    "by semantic widening": "broadly",
    "strict sense": "strict-sense",
    "baby talk": "baby-talk",
    "middle infinitive": "middle-infinitive",
    "first infinitive": "infinitive-i",
    "third-person form of the long first infinitive of":
    "third-person infinitive-i-long form-of",
    "second infinitive": "infinitive-ii",
    "second active infinitive": "infinitive-ii active",
    "second passive infinitive": "infinitive-ii passive",
    "third infinitive": "infinitive-iii",
    "third active infinitive": "infinitive-iii active",
    "third passive infinitive": "infinitive-iii passive",
    "fourth infinitive": "infinitive-iv",
    "fifth infinitive": "infinitive-v",
    "subjunctive I": "subjunctive-i",
    "subjunctive II": "subjunctive-ii",
    "morse code": "morse-code",
    "with odd-syllable stems": "with-odd-syllable-stems",
    "old orthography": "archaic",
    "Brazilian ortography": "Brazilian",
    "European ortography": "European",
    "with noun phrase": "with-noun-phrase",
    "contracted dem-form": "contracted-dem-form",
    "contractions": "contraction",
    "Yale cen": "Yale",
    "subjective pronoun": "subjective pronoun",
    "subject": "subjective",
    "subject form": "subjective",
    "‘subject form’": "subjective",  # tw.t/Egyptian
    # "object": "objective",  # XXX problems with "An object of ... form_of
    "possessive pronoun": "possessive pronoun without-noun",
    "demostrative": "demonstrative",  # eeteeṇú/Phalura
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
    "pronunciation spelling": "pronunciation-spelling",
    "eye dialect spelling of": "alt-of pronunciation-spelling",
    "alternative or obsolete spelling of":
    "alt-of obsolete alternative",
    "obsolete and rare": "obsolete rare",
    "American spelling": "US",
    "Canadian spelling": "Canada",
    "name of the": "alt-of name",  # E.g. .. letter | Latin-script letter
    "alternative name of": "alt-of alternative name",
    "alternative name for": "alt-of alternative name",
    "nonstandard spelling of": "alt-of nonstandard",
    "US standard spelling of": "alt-of US standard",
    "US spelling of": "alt-of US",
    "alternative typography of": "alt-of alternative",
    "polytonic spelling of": "alt-of polytonic",
    "variant of": "alt-of alternative",
    "uncommon spelling of": "alt-of uncommon",
    "alternative typographic spelling of": "alt-of alternative",
    "especially in typeface names": "typography",
    "alternative spelling": "alternative",
    "alternative spelling of": "alt-of alternative",
    "alternative form": "alternative",
    "alternative form of": "alt-of alternative",
    "alternative term for": "alt-of alternative",
    "alternative stem of": "alt-of stem alternative",
    "alternative letter-case form of": "alt-of",
    "medieval spelling of": "alt-of obsolete",
    "post-1930s Cyrillic spelling of": "alt-of standard Cyrillic",
    "pre-1918 spelling of": "alt-of dated",
    "pre-1945 period": "dated",
    "Plural pre-1990": "dated plural",
    "Plural pre-1990 reformed spelling": "plural",
    "unreformed spelling": "nonstandard",
    "Switzerland and Liechtenstein standard spelling of":
    "alt-of Switzerland Liechtenstein standard",
    "form removed with the spelling reform of 2012; superseded by":
    "alt-of dated",
    "excessive spelling of": "alt-of excessive",
    "exaggerated degree of": "alt-of exaggerated",
    "defective spelling of": "alt-of misspelling",
    "verbal noun of": "noun-from-verb form-of",
    "alternative verbal noun of":
    "form-of alternative noun-from-verb",
    "alternative conjugation of": "alt-of alternative",
    "abbreviation of": "alt-of abbreviation",
    "short for": "alt-of abbreviation",
    "short form": "short-form",
    "eclipsed form of": "alt-of abbreviation eclipsis",
    "apocopic form of": "alt-of abbreviation apocopic",
    "apocope": "apocopic",
    "truncated apocopic form": "apocopic",
    "apocopic form": "apocopic abbreviation",
    "apocopated": "apocopic abbreviation",
    "apocopate": "apocopic abbreviation",
    "h-prothesized form of": "alt-of prothesis-h",
    "acronym of": "alt-of abbreviation acronym",
    "acronym": "abbreviation acronym",
    "initialism of": "alt-of abbreviation initialism",
    "contraction of": "alt-of abbreviation contraction",
    "IUPAC 3-letter abbreviation for": "alt-of abbreviation",
    "IUPAC 3-letter abbreviation of": "alt-of abbreviation",
    "IUPAC 2-letter abbreviation of": "alt-of abbreviation",
    "IUPAC 2-letter abbreviation for": "alt-of abbreviation",
    "IUPAC 1-letter abbreviation of": "alt-of abbreviation",
    "IUPAC 1-letter abbreviation for": "alt-of abbreviation",
    "symbol for": "alt-of symbol",
    "praenominal abbreviation of": "alt-of abbreviation praenominal",
    "ellipsis of": "alt-of ellipsis abbreviation",
    "clipping of": "alt-of clipping abbreviation",
    "X-system spelling of": "alt-of X-system",
    "H-system spelling of": "alt-of H-system",
    "Pinyin transcription of": "alt-of Pinyin",
    "Rōmaji transcription of": "alt-of Rōmaji",
    "romaji": "Rōmaji",
    "rōmaji": "Rōmaji",
    "visual rendering of Morse code for":
    "alt-of visual-rendering morse-code",
    "soft mutation of": "form-of mutation-soft",
    "causes soft mutation": "triggers-mutation-soft",
    "non-Oxford British English standard spelling of":
    "alt-of nonstandard UK",
    "Nil standard spelling of": "alt-of UK standard",
    "nasal mutation of": "form-of mutation-nasal",
    "nasal mutation": "mutation-nasal",
    "triggers nasalization": "triggers-mutation-nasal",
    "triggers nasal mutation": "triggers-mutation-nasal",
    "triggers no mutation": "triggers-no-mutation",
    "mixed mutation of": "form-of mutation-mixed",
    "mixed mutation": "mutation-mixed",
    "aspirate mutation of": "form-of mutation-aspirate",
    "aspirate mutation": "mutation-aspirate",
    "British misspelling": "misspelling British",
    "misspelling of": "alt-of misspelling",
    "deliberate misspelling of": "alt-of misspelling deliberate",
    "common misspelling of": "alt-of misspelling",
    "misconstruction of": "alt-of misconstruction",
    "misconstructed": "misconstruction",
    "ungrammatical": "misconstruction",
    "Latin spelling of": "alt-of romanization",
    "Latn": "Latin",
    "Late Anglo-Norman spelling of": "alt-of Anglo-Norman",
    "Jawi spelling of": "alt-of Jawi",
    "Hanja form of": "alt-of hanja",
    "Hanja form? of": "alt-of hanja",
    "Hanja": "hanja",
    "Hán Nôm": "Hán-Nôm",
    "Hán tự form of": "alt-of Hán-tự",
    "Newa Spelling": "Newa",
    "Glagolitic spelling of": "alt-of Glagolitic",
    "front vowel variant of": "alt-of front-vowel",
    "front-vowel variant of": "alt-of front-vowel",
    "euphemistic spelling of": "alt-of euphemistic",
    "euphemistic reading of": "alt-of euphemistic",
    "euphemism": "euphemistic",
    "transliterated Russian pet forms": "transliteration Russian",
    "Transliteration": "transliteration",
    "transliteration needed": "",
    "Cyrillic spelling of": "alt-of Cyrillic",
    "Cyrillic spelling": "Cyrillic",
    "Latin spelling": "romanization",
    "British standard spellingh of": "alt-of UK standard",
    "British and Canada standard spelling of":
    "alt-of UK Canada standard",
    "Britain and Ireland standard spelling of":
    "alt-of Britain Ireland standard",
    "Britain and New Zealand standard spelling of":
    "alt-of Britain New-Zealand standard",
    "Britain and Canada spelling of": "alt-of Britain Canada",
    "Baybayin spelling of": "alt-of Baybayin",
    "Arabic spelling of": "alt-of Arabic",
    "Arabic (Eastern)": "Arabic-Indic",
    "Eastern Arabic": "Arabic-Indic",
    "Arabic (Western)": "Arabic",
    "Formerly standard spelling of": "alt-of archaic",
    "informal spelling of": "alt-of informal",
    "Yañalif spelling of": "alt-of Yañalif",
    "traditional orthography spelling of": "alt-of traditional",
    "traditional and simplified": "traditional simplified",
    "Taraškievica spelling of": "alt-of Taraškievica",
    "Post-1930s Cyrillic spelling of": "alt-of Cyrillic",
    "Britain spelling of": "alt-of Britain",
    "linguistically informed spelling of": "alt-of literary",
    "Chinese spelling of": "alt-of China",
    "Mongolian spelling of": "alt-of Mongolian",
    "Leet spelling of": "alt-of Leet Internet",
    "leetspeak": "Leet Internet",
    "bulletin board system slang": "slang Internet",
    "combining form of": "in-compounds form-of",
    "combining form": "in-compounds",
    "compound form": "in-compounds",
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
    "synonym of": "synonym synonym-of",
    "same as": "synonym synonym-of",
    "topicalized form of": "topicalized form-of",
    "form of": "form-of",
    "inflected form of": "form-of",
    "inflected forms": "inflected",
    "lenited form of": "lenition form-of",
    "triggers lenition": "triggers-lenition",
    "triggers lenition of a following consonant-initial noun":
    "triggers-lenition",
    "triggers eclipsis": "triggers-eclipsis",
    "triggers h-prothesis": "triggers-h-prothesis",
    "causes aspirate mutation": "triggers-mutation-aspirate",
    "triggers aspiration": "triggers-mutation-aspirate",
    "triggers mixed mutation": "triggers-mutation-mixed",
    # XXX Could be more accurate
    "triggers mixed mutation except of forms of bod": "triggers-mutation-mixed",
    "humurous": "humorous error-misspelling",
    "humourous": "humorous",
    "sarcasm": "sarcastic",
    "ecclesiastic or ironic": "Ecclesiastical ironic",
    "figuratively or literally": "figuratively literally",
    "figuratively and literary": "figuratively literary",
    "figuative": "figuratively",
    "humorously": "humorous",
    "jocular": "humorous",
    "humorous or euphemistic": "humorous euphemistic",
    "may sound impolite": "possibly impolite",
    "northern dialects": "dialectal",
    "dialectism": "dialectal",
    "archaic or loosely": "archaic broadly",
    "archaic or poetic": "archaic poetic",
    "archeic or poetic": "archaic poetic",
    "archaic or phrasal": "archaic idiomatic",
    "archaic or dialectal": "archaic dialectal",
    "archaic or literary": "archaic literary",
    "archaic or Britain": "archaic Britain",
    "archaic or nonstandard": "archaic nonstandard",
    "most dialects": "dialectal",
    "most dialects of Ripuarian": "dialectal",
    "some dialects": "dialectal",
    "some compounds": "idiomatic in-compounds",
    "as a modifier in compound words": "in-compounds",
    "used in compound adjectives": "in-compounds adjective",
    "used attributively": "attributive",
    "used predicatively": "predicative",
    "used substatively": "substantive",
    "substantival use of the verbal voice": "noun-from-verb",
    "in ancient phrases": "idiomatic",
    "unofficial spelling": "nonstandard",
    "rare nonstandard spellings": "rare nonstandard",
    "as rare alternative form": "rare",
    "nonstandard spellings": "nonstandard",
    "capitalised": "capitalized",
    "always capitalized": "capitalized",
    "sometimes not capitalized": "usually capitalized",
    "sometimes capitalized": "sometimes capitalized",
    "Sometimes capitalized": "sometimes capitalized",
    "rhetorical question": "rhetoric",
    "old-fashioned": "dated",
    "rarely used": "rare",
    "rarely": "rare",
    "partially supplied": "",
    "partially supplanted": "",
    "present tense seldom used": "present-rare",
    "often in place of present tense": "present often",
    "conjugated non-suppletively in the present tense": "irregular",
    "now rare": "archaic",
    "in the past tense": "past",
    "fixed expressions": "idiomatic",
    "formulaic": "idiomatic",
    "several set phrases": "idiomatic",
    "now colloquial": "colloquial",
    "now colloquial and nonstandard": "colloquial nonstandard",
    "colloquial or Min Nan": "colloquial Min-Nan",
    "colloquial or jargon": "colloquial jargon",
    "Wiktionary and WMF jargon": "jargon Internet",
    "colloquially": "colloquial",
    "fossil word": "archaic",
    "brusque": "impolite",
    "verbs": "verb",
    "prepositions": "prepositional",
    "postpositions": "postpositional",
    "interjections": "interjection",
    "Abbreviations": "abbreviation",
    "abbreviations": "abbreviation",
    "variants": "variant",
    "Ordinal": "ordinal",
    "ordinals": "ordinal",
    "local use": "regional",
    "more generally": "broadly",
    "loosely": "broadly",
    "broad sense": "broadly",
    "hypocoristic": "familiar",
    "familiar or childish": "familiar childish",
    "to a male": "addressee-masculine",
    "to a man": "addressee-masculine",
    "to a female": "addressee-masculine",
    "to a woman": "addressee-feminine",
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
    "Medieval and Early Modern Greek regional":
    "Medieval-Greek Early-Modern-Greek dialectal",
    "collectively": "collective",
    "collective or singulative": "collective singulative",
    "used formally in Spain": "Spain",
    "nouns": "noun",
    "phrases": "phrase",
    "with the particle lai": "with-lai",
    "adjectives": "adjective",
    "related adjective": "adjective",
    "adj": "adjective",
    "adj.": "adjective",
    "adv": "adverb",
    "adverbs": "adverb",
    "augmentatives": "augmentative",
    "pejoratives": "pejorative",
    "perjorative": "pejorative error-misspelling",
    "pejorative or colloquial": "pejorative colloquial",
    "non-standard since 2012": "nonstandard",
    "colloquialism": "colloquial",
    "non-standard since 1917": "nonstandard",
    "conditional mood": "conditional",
    "figurative": "figuratively",
    "compound words": "compound",
    "form of address": "term-of-address",
    "term of address": "term-of-address",
    "as a term of address": "term-of-address",
    "direct address": "term-of-address",
    "face-to-face address term": "term-of-address",
    "address": "term-of-address",
    "endearingly": "endearing",
    "elliptically": "ellipsis",
    "elegant": "formal",  # Elegant or Formal Thai
    "nonce word": "nonce-word",
    "neologism or slang": "neologism slang",
    "attributively": "attributive",
    "poetic term": "poetic",
    "poetic meter": "poetic",
    "in certain phrases": "in-certain-phrases",
    "deprecated template usage": "",
    "deprecated": "proscribed",
    "diacritical mark": "diacritic",
    "inflection of": "form-of",
    "mainland China": "Mainland-China",
    "spelling in China": "China",
    "rhyming slang": "slang",
    "prison slang": "slang",
    "criminal slang": "slang",
    "fandom slang": "slang lifestyle",
    "furry fandom": "slang lifestyle",
    "manga fandom slang": "slang manga",
    "real estate slang": "slang real-estate",
    "gay slang": "slang LGBT",
    "urban slang": "slang urbanism",
    "lolspeak": "humorous Internet",
    "Usenet": "Internet",
    "one-termination adjective": "one-termination",
    "two-termination adjective": "two-termination",
    "three-termination adjective": "three-termination",
    "one-termination participle": "one-termination participle",
    "two-termination participle": "two-termination participle",
    "three-termination particple": "three-termination participle",
    "semelefactive": "semelfactive error-misspelling",
    "invariant": "invariable",
    "followed by to": "with-to",
    "taking a to-infinitive": "with-to with-infinitive",
    "with bare infinitive": "with-infinitive",
    "direct object": "direct-object",
    "indirect object": "indirect-object",
    "transitive with of": "transitive-with-of",
    "with of": "with-of",
    "with on": "with-on",
    "with down": "with-down",
    "with up": "with-up",
    "with a personal pronoun": "with-personal-pronoun",
    "with an indirect object": "with-indirect-object",
    "with comparatives": "with-comparative",
    "with definite article": "with-definite-article",
    'with "the"': "with-definite-article",
    "etc.": "usually",
    "regardless of gender": "gender-neutral",
    "gender-neutral (or multigendered)": "gender-neutral",
    "ditransitive for the second object": "ditransitive",
    "double transitive": "ditransitive",
    "transitive or ditransitive": "transitive ditransitive",
    "number": "numeral",
    "numerals": "numeral",
    "Tally marks": "Tally-marks numeral",
    "+ 3rd-pers.": "with-third-person",
    "Historical": "historical",
    "hist.": "historical",
    "antiquity": "historical",
    "ideophone": "ideophonic",
    "Alsatian (Low Alemannic German)": "Alsatian Alemannic",
    "all sects": "",
    "adessive + 3rd person singular + ~":
    "with-adessive with-third-person-singular postpositional",
    "inessive + 3rd person singular + ~":
    "with-inessive with-third-person-singular postpositional",
    "~ (olemassa)": "with-olemassa",
    "3rd person singular": "third-person singular",
    "+ genitive + 3rd person singular + passive present participle":
    "with-genitive with-third-person-singular with-passive-present-participle",
    "genitive + 3rd-pers. singular + 1st infinitive":
    "with-genitive with-third-person-singular with-infinitive-i",
    "+ direct object in accusative + 3rd infinitive in illative":
    "transitive with-accusative with-infinitive-iii-illative",
    "+ direct object in accusative + past participle in translative or partitive":
    "transitive with-accusative with-past-participle-translative with-past-participle-partitive",
    "+ past participle in translative or partitive":
    "with-past-participle-translative with-past-participle-partitive",
    "active past part. taitanut": "",
    "+ passive past participle in translative":
    "with-passive-past-participle-translative",
    "+ passive past participle in partitive":
    "with-passive-past-participle-partitive",
    "+ active past participle in translative":
    "with-past-participle-translative",
    "+ adjective in ablative or allative":
    "with-adjective with-ablative with-allative",
    "in indicative or conditional mood": "in-indicative in-conditional",
    "in negative sentences": "with-negation",
    "in negative clauses": "with-negation",
    "using Raguileo Alphabet": "Raguileo-Alphabet",
    "using Raguileo alphabet": "Raguileo-Alphabet",
    "using Raguileo and Unified Alphabet": "Raguileo-Alphabet Unified",
    "transliterated": "transliteration",
    "though not derogative": "",
    "women generally don't accept to be called this way": "offensive",
    "transitive sense": "transitive",
    "in intransitive meaning": "intransitive",
    "initial change reduplication": "reduplication",
    "initial change reduplication with syncope": "reduplication syncope",
    "initial change with syncope": "syncope",
    "syncopated": "syncope",
    "reduplication with syncope": "reduplication syncope",
    "introducing subjunctive hortative": "subjunctive hortative",
    "nominative and vocative plural animate": "nominative vocative",
    "with diaeresis to indicate disyllabilicity": "",
    "aphaeretic variant": "variant",
    "mediopassive voice": "mediopassive",
    "ALL": "",
    "archaic or hypercorrect": "archaic hypercorrect",
    "as a diacritic": "diacritic",
    "as a gerund": "gerund",
    "as a calque": "calque",
    "pseudoarchaic": "dated",
    "surnames": "surname",
    "all countable senses": "countable",
    "attributive form of pyjamas": "attributive",
    "ordinal form": "ordinal",
    "ordinal form of twelve": "ordinal",
    "conjugative of": "conjugative-of",
    "correlative of": "correlative-of",
    "modern nonstandard spellings": "modern nonstandard",
    "non-standard": "nonstandard",
    "non-standard form of": "nonstandard alt-of",
    "nonanimate": "inanimate",
    "nominalized verb": "noun-from-verb",
    "nominalized": "noun-from-verb",  # XXX could this be from noun/adj
    "n-v": "verb-from-noun",
    "v-n": "noun-from-verb",
    "n-n": "noun-from-noun",
    "v-v": "verb-from-verb",
    "uses -j- as interfix": "interfix-j",
    "eulogistic": "poetic",  # XXX not really, implies praise
    "prev": "previous",
    "normal usage": "",  # In some Russian words with two heads
    "professional usage": "",  # In some Russian words with two heads
    "?? missing information.": "",
    "unknown comparative": "",
    "unknown accent pattern": "",
    "?? conj.": "",
    "pres. ??": "",
    "past ??": "",
    "see usage notes": "",
    "no known Cyrillic variant": "",
    "no first-person singular present": "no-first-person-singular-present",
    "no first-person singular preterite": "no-first-person-singular-preterite",
    "no third-person singular past historic":
    "no-third-person-singular-past-historic",
    "‘dependent’": "dependent",  # sn/Egyptian
    "‘independent’": "independent",  # ntf/Egyptian
    "eum": "hangeul",  # Apparently synonym for the Korean alphabet
    "classifiers": "classifier",
    "discourse particle": "discourse particle",
    "discourse": "discourse",  # hum/Phalura
    "numeral tones": "numeral-tones",
    "alphabetic tones": "alphabetic-tones",
    "class A infixed pronoun": "infix pronoun class-A",
    "class B infixed pronoun": "infix pronoun class-B",
    "class C infixed pronoun": "infix pronoun class-C",
    "class B & C infixed pronoun": "infix pronoun class-B class-C",
    "class I": "class-i",
    "class II": "class-ii",
    "class III": "class-iii",
    "class N": "class-n",
    "class a-i": "class-a-i",
    "to multiple people": "addressee-plural",
    "to one person": "addressee-singular",
    "actor focus": "actor-focus",
    "indirect actor trigger": "actor-indirect",
    "usually feminine": "feminine-usually",
    "but usually feminine": "feminine-usually",
    "usually masculine": "masculine-usually",
    "but usually masculine": "masculine-usually",
    "but rarely feminine": "masculine-usually",
    "but rarely masculine": "feminine-usually",
    "requires negation": "with-negation",
    "inalienable–class I agreement": "inalienable class-i",
    "inalienable–class II agreement": "inalienable class-ii",
    "inalienable–class III agreement": "inalienable class-iii",
    "no first-person singular past historic":
    "no-first-person-singular-past-historic",
    "no definite forms": "no-definite",
    "no definite form": "no-definite",
    "no diminutive": "no-diminutive",
    "no second-person singular imperative":
    "no-second-person-singular-imperative",
    "no simple past": "no-past",
    "no feminine form": "no-feminine",
    "no infinitive": "no-infinitive",
    "no longer productive": "idiomatic",
    "no past tense": "no-past",
    "no third-person singular present": "no-third-person-singular-present",
    "nominalized adjective following adjective declension": "noun-from-adj",
    # XXX this could be more accurate
    "truncative except after q and r": "truncative",  # Greenlandic
    "of masculine singular": "masculine singular nominative",
    "of masculine plural": "masculine plural nominative",
    "of feminine singular": "feminine singular nominative",
    "of feminine plural": "feminine plural nominative",
    "officialese": "bureaucratese",
    "+ optionally: adjective in accusative case + neuter noun in accusative case":
    "definite neuter with-accusative",
    "non-emphatic": "unemphatic",
    "not productive": "idiomatic",
    "passive with different sense": "passive",
    "active with different sense": "active",
    "+ von": "with-von",  # außerhalb/German
    "Symbol:": "symbol",
    "a reflexive": "reflexive",
    "active/stative": "active stative",
    "always postpostive": "postpositional",
    "postpositive": "postpositional",
    "defininte plural": "definite plural",  # aigg/Westrobothnian
    "determinative of": "determinative-of",
    "lenites": "lenition",
    "followed by indirect relative": "with-indirect-relative",
    "inflected like": "inflected-like",
    "locational noun": "locative",
    "mass noun": "uncountable",
    "negated": "past participle negative",  # fera/Westrobothnian
    "neutral": "gender-neutral",  # countryman/English
    "never clause-initial": "not-clause-initial",
    "primarily": "",
    "mostly": "",
    "now": "",
    "chiefly": "",
    "only": "",
    "somewhat": "",
    "definite articulation": "definite",  # boatsi/Aromanian
    "p-past": "passive past",
    "p‑past": "passive past",  # Fancy unicode dash περπατάω/Greek
    "ppp": "passive perfect participle",
    "plural:": "plural",
    "synonyms:": "synonym",
    "quantified:": "quantified",
    "sentence case": "sentence-case",
    "set phrase from Classical Chinese": "idiomatic Classical-Chinese",
    "the plural of": "plural-of",
    "plural of": "plural-of",
    "the reflexive case of": "reflexive-of",
    "the reflexive form of": "reflexive-of",
    "unipersonal": "",  # Too rare to track
    "used only after prepositions": "after-preposition",
    "appended after imperfective form": "in-compounds with-imperfect",
    "universal or indefinite": "universal indefinite",
    "el/ea": "third-person singular",  # o/Romanian/Verb
    "ele/ei": "third-person plural",  # vor/Romanian/Verb
    "vestre": "slang",  # type of backslang in Argentine and Uruguayan Spanish
    "onomatopoeia": "onomatopoeic",
    "ITERATIVE": "iterative",
    "OPTATIVE": "optative",
    "IMPERFECTIVE": "imperfective",
    "PERFECTIVE": "perfective",
    "(FIXME)": "error-fixme",
    "Conversive": "conversive",
    "Cholula and Milpa Alta": "Cholula Milpa-Alta",
    "Surnames": "surname",
    "metaphorically": "metaphoric",
    "hypothetic": "hypothetical",
    "Kinmen and Penghu Hokkien": "Kinmen-Hokkien Penghu-Hokkien",
    "“Jinmeiyō” kanji used for names": "Jinmeiyō",
    "by suppletion": "suppletive",
    "only some senses": "",  # Could use a tag; "limited-senses"? hero/English
    "nautical sense": "nautical",  # Without this, there's error-unknown and
                                 # the topic tags include "transportation". pay out/English
    "otherwise nonstandard": "nonstandard",  # weep/English
    "nonhuman": "non-human",  # himself/English, talking about "it"
    "both": "",  # XXX "both" should trigger the tag to the next two forms! walrus/English
    "pseudo-Latin": "hypercorrect",  # platypus/English
    "pseudo-Latinate": "hypercorrect",  # Simplex/German
    "archaic or informal": "archaic informal",  # while/English
    "more common in": "common",  # tread water/English
    "all": "",  # XXX same as "both", "all" should extend tags the following forms
    "less commonly": "uncommon",  # avid/English
    "muscle": "anatomy",  # depressor/English
    "optionally with an article": "with-article",  # Mosambik/German
    "genitive (des)": "genitive",  #ordentlicher Professor/German, Lieber/German
    "prenominally without an article": "without-article before-noun",  # Mama/German
    "usually in": "regional",  # Vergnügungspark/German
    "older ending": "archaic",  # Fritz/German
    "only in some regional vernaculars": "regional",  # umhauen/German
    "mostly only when written": "literary",  # Magnet/German
    "rarer": "rare",  # verbleichen/German
    "southern Germany": "Southern-Germany",  # Holzscheit/German
    "alternatively in the meaning": "uncommon",  # abbondare/Italian
    #XXX "for-subsense" or similar needs a tag or parsing
    "alternatively in": "regional",  # Holzscheit/German
    "nonstandard but common": "nonstandard common",  # Gedanke/German
    "colloquial or archaic": ["colloquial", "archaic"],  # Undorn/German
    "predominant when spoken": "colloquial",  # Gnom/German
    "with a numeral": "with-numeral",  # Radlermaß/German
    "not with a numeral": "without-numeral",  # Radlermaß/German
    "alternatively when": "",  # Radlermaß/German,
    "traditional/standard": "archaic standard",  # flecthen/German
    "only in some senses": "uncommon",  # hero/English
    "prescribed, more frequent": "",  # offenbaren/German These distinctions are minor
    "less frequent but not uncommon": "",  #offenbaren/German
    "predominant": "",  # März/German: "normal"
    "common but sometimes considered nonstandard": "common",  # gebären/German
    "more standard": "standard",  # Lump/German
    "more common in general usage": "common",  # Lump/German
    "rare outside": "regional",  # Park/German
    "nonstandard, rather rare": "nonstandard rare",  # Lexikon/German
    "prescribed": "literary",  # brauchen/German
    "always used in speech": "common",  # brauchen/German
    "common in writing": "common",  # brauchen/German
    "when issues of different sorts are involved": "different-sort",  # Wahnsinnsding/German
    "when issues of the same sort are involved": "same-sort",  #Wahnsinnsding/German
    "elevated": "honorific",  # Land/German
    "mostly only when written": "literary",  # Steinmetz/German
    "original but now less common": "archaic",  # winken/German
    "standard but rare in the vernacular": "literary",  # fechten/German
    "mostly found in": "regional",  # Ehrenschutz/German
    "unofficial": "colloquial",  # kørsel/Danish, although fixed, one user did a lot of this in Danish.
    "common in": "regional",  # tread water/English
    "careful style": "formal",  # valutarsi/Italian
    "less popular": "uncommon",  # rivedere/Italian
    "also when intransitive": "intransitive",  # risuonare/Italian
    "popular": "common",  # sciogliere/Italian
    "high-style": "formal",  # riesumare/Italian
    "more common": "common",  # compiersi/Italian
    "Latinate pronunciation": "hypercorrect",  # perorare/Italian
    "medio-passive voice": "mediopassive",  # afrohet/Albanian
    # ~ "comparative of": "comparative-of",  # miður/Icelandic
    "subst.": "noun",

}

# This mapping is applied to full descriptions before splitting by comma.
# Note: these cannot match just part of a description (even when separated
# by comma or semicolon), as these can contain commas and semicolons.
xlat_descs_map = {
    "with there, or dialectally it, as dummy subject": "with-dummy-subject",
    "+ location in inessive, adessive + vehicle in elative, often with pois":
    "with-inessive with-adessive with-elative",
    "+ accusative +, Genitive": "with-accusative with-genitive",
    "with genitive, instrumental or dative case":
    "with-genitive with-instrumental with-dative",
    "+ illative, allative, (verbs) 3rd infinitive in illative":
    "with-illative with-allative with-infinitive-iii-illative",
    "(inessive or adessive) + 3rd-pers. sg. + an adverb":
    "with-inessive with-adessive with-third-person-singular with-adverb",
    "+ partitive for agent, + allative for target":
    "with-partitive with-allative",
    "+ infinitive; in indicative or conditional mood":
    "with-infinitive with-indicative with-conditional",
    "transitive, auxiliary + first infinitive, active past part. taitanut or tainnut":
    "transitive, auxiliary, with-infinitive-i",
    "elative + 3rd person singular + noun/adjective in nominative or partitive or personal + translative":
    "with-elative with-third-person-singular",  # XXX very incomplete
    "group theory, of a group, semigroup, etc.": "group theory",
    "Triggers lenition of b, c, f, g, m, p, s. Triggers eclipsis of d, t.":
    "triggers-lenition triggers-eclipsis",
    # XXX this could be more precise
    "‘his’ and ‘its’ trigger lenition; ‘her’ triggers /h/-prothesis; ‘their’ triggers eclipsis": "triggers-lenition triggers-h-prothesis triggers-eclipsis",
    "for = elative; for verbs action noun in elative":
    "with-action-noun-in-elative",
    # de/Danish
    "as a personal pronoun, it has the forms dem in the oblique case and deres in the genitive; as a determiner, it is uninflected": "",
    # spinifer/Latin
    "nominative masculine singular in -er; two different stems": "",
    "^(???) please indicate transitivity!": "",
    "^(???) please provide spelling!": "",
    "please provide plural": "",
    "please provide feminine": "",
    "please provide feminine plural": "",
    "the passive, with different sense": "",
    "the active, with different sense": "",
    "m": "masculine",
    "f": "feminine",
    "classic": "",

}

# Words that are interpreted as tags at the beginning of a linkage
linkage_beginning_tags = {
    "factitive/causative": "factitive causative",
    "factive/causative": "factive causative",
    "factive": "factive",
    "factitive": "factive",  # Not sure if same or different as factive
    "causative": "causative",
    "reflexive": "reflexive",
    "frequentative": "frequentative",
    "optative": "optative",
    "affirmative": "affirmative",
    "cohortative": "cohortative",
    "applicative": "applicative",
    "stative": "stative",
    "passive": "passive",
    "optative": "optative",
    "adjective": "adjective",
    "verb": "verb",
    "noun": "noun",
    "adverb": "adverb",
}

# For a gloss to be interpreted as a form_of by parse_alt_or_inflection_of(),
# the form must contain at least one of these tags.  This is only used for
# the implicit form-of (tags followed by "of").
form_of_tags = set([
    "abessive",
    "ablative",
    "absolutive",
    "accusative",
    "adessive",
    "adjectival",
    "adverbial",
    "affirmative",
    "agentive",
    "allative",
    "aorist",
    "applicative",
    "attributive",
    "augmentative",
    "augmented",
    "benefactive",
    "causal-final",
    "causative",
    "collective",
    "comitative",
    "comparative",
    "conditional",
    "conditional-i",
    "conditional-ii",
    "connegative",
    "construct",
    "contemplative",
    "counterfactual",
    "dative",
    "debitive",
    "declension-1",
    "declension-2",
    "declension-3",
    "definite",
    "delative",
    "demonstrative",
    "desiderative",
    "diminutive",
    "distal",
    "dual",
    "durative",
    "elative",
    "endearing",
    "equative",
    "ergative",
    "essive",
    "feminine",
    "first-person",
    "form-i",
    "form-ii",
    "form-iii",
    "form-iiiq",
    "form-iiq",
    "form-iq",
    "form-iv",
    "form-ivq",
    "form-ix",
    "form-v",
    "form-vi",
    "form-vii",
    "form-viii",
    "form-x",
    "form-xi",
    "form-xii",
    "form-xiii",
    "fourth-person",
    "frequentative",
    "future",
    "gender-neutral",
    "genitive",
    "gerund",
    "hortative",
    "illative",
    "imperative",
    "imperfect",
    "imperfective",
    "impersonal",
    "in-compounds",
    "inclusive",
    "indefinite",
    "inessive",
    "infinitive",
    "infinitive-i",
    "infinitive-ii",
    "infinitive-iii",
    "infinitive-iv",
    "infinitive-v",
    "instructive",
    "instrumental",
    "interrogative",
    "iterative",
    "jussive",
    "lative",
    "locative",
    "masculine",
    "mediopassive",
    "middle-infinitive",
    "mutation-aspirate",
    "mutation-mixed",
    "mutation-nasal",
    "mutation-soft",
    "negative",
    "neuter",
    "nominal",
    "nominative",
    "non-past",
    "oblique",
    "offensive",
    "optative",
    "ordinal",
    "participle",
    "partitive",
    "passive",
    "past",
    "paucal",
    "perfect",
    "perfective",
    "pluperfect",
    "plural",
    "polite",
    "possessive",
    "potential",
    "predicative",
    "prepositional",
    "present",
    "preterite",
    "prolative",
    "pronominal",
    "prospective",
    "proximal",
    "quotative",
    "reflexive",
    "second-person",
    "singular",
    "singulative",
    "stative",
    "stressed",
    "subjective",
    "subjunctive",
    "subjunctive-i",
    "subjunctive-ii",
    "sublative",
    "superessive",
    "superlative",
    "supine",
    "terminative",
    "third-person",
    "transgressive",
    "translative",
    "unstressed",
    "vocative",
    # 2084 objective - beware of "An object of ..." (e.g., song/English)
])

# For a gloss to be interpreted as an alt_of by parse_alt_or_inflection_of(),
# the form must contain at least one of these tags.  This is only used for
# the implicit alt-of (tags followed by "of").
alt_of_tags = set([
    "abbreviation",
    "capitalized",
    "colloquial",
    "contracted",
    "dialectal",
    "historic",
    "hypercorrect",
    "initialism",
    "literary",
    "lowercase",
    "misconstruction",
    "nonstandard",
    "obsolete",
    "proscribed",
    "standard",
    "uppercase",
    "unabbreviation",  # jku/Finnish
])

# Valid tag categories / attributes.  These map to sort precedence, with
# larger values put first.
tag_categories = {
    "referent": 500,  # definite, indefinite, proximal, distal
    "degree": 400,    # comparative, superlative
    "gender": 390,    # Semantic gender (often also implies class)
    "person": 380,    # first-person, second-person, third-person, impersonal,
                      # fourth-person, inclusive, exclusive
    "object": 375,    # Object number/gender/class/definiteness/person
    "case": 370,      # Grammatical case (also direct-object, indirect-object)
    "number": 360,    # Singular, plural, dual, paucal, ...
    # "addressee",    # Something related to addressee
    "possession": 350,  # possessive, possessed-form, unpossessed-form,
                        # alienable, inalienable
    "voice": 200,     # active, passive, middle
    "tense": 190,     # present, past, imperfect, perfect, future, pluperfect
    "aspect": 180,   # Aspect of verbs (perfective, imperfective, habitual, ...)
    "mood": 170,  # cohortiative, commissive, conditional, conjunctive,
             # declarative, hortative, imperative, indicative,
             # interrogative, jussive, optative, potential, prohibitive,
             # subjunctive
             # Note that interrogative also used for, e.g., pronouns
    "non-finite": 160,  # infinitive, participle, ...
    "polarity": 150,  # positive, negative, connegative
    "pos": 50,  # Specifies part-of-speech
    "category": 40,  # person, animate, inanimate,
                 # (virile, nonvirile?), countable, uncountable
    "transitivity": 35,  # intransitive, transitive, ditransitive,
                         # ambitransitive
    # "participants",  # reflexive, reciprocal
    "register": 30,  # dialectal, formal, informal, slang, vulgar
    "dialect": 25,  # Typically uppercase tags specifying dialectal variations,
                   # region, language, who standardized, or time period
                   # when used
    "class": 20,  # Inflection class (Bantu languages, Japanese, etc)
    "trigger": 15,  # Triggers something (e.g., mutation) in some context
    "gradation": 15,  # gradation or qualifier
    "derivation": 13,  # Specifies derivation (agent, noun-from-verb,
                   # noun-from-and, noun-from-noun, verb-from-noun, ...)
    "mod": 10,  # Provides a modified form (e.g., abbreviation, mutation)
    "pragmatic": 10,  # Specifies pragmatics (e.g., stressed/unstressed)
    "phonetic": 10,  # Describes some phonetic aspect
    "lexical": 10,  # Describes some lexical/typographic aspect
    "with": 10,  # Co-occurs with something
    "order": 10,  # Word position or order
    "detail": 5,  # Provides some detail
    "script": 5,  # Provides version of word in given script in forms;
                  # sometimes also used as tag for language/country
    "misc": 1,  # lots of miscellaneous/uncategorized stuff
    "error": 0,  # error tags
    "unknown": -1,  # Only used internally
    "dummy": -2,  # Only used internally
    "dummy2": -3,  # Only used internally (this category never expands cell)
}

# Set of all valid tags
valid_tags = {
    "Adlam": "script",  # Script
    "Amharic": "script",  # Script (at least for numberals)
    "Arabic": "script",  # Also script
    "Arabic-Indic": "script",  # Also script
    "Armenian": "script",  # Also script
    "Assamese": "script",  # Also script (India)
    "Balinese": "script",  # Also script
    "Baybayin": "script",  # Also script
    "Bengali": "script",  # Also script (India)
    "Brahmi": "script",  # Script (India, historic)
    "Burmese": "script",  # Script
    "Chakma": "script",  # Script (India/Burma?)
    "Cham": "script",  # Script (Austronesian - Vietnam/Cambodia)
    "Chinese": "script",  # Also script
    "CJK": "script",  # CJK variant, e.g., Vietnamese Chữ Hán / Chữ Nôm
    "Cyrillic": "script",  # Script
    "Devanagari": "script",  # Script
    "Déné-syllabary": "script",  # Script for Canadian Indian languages?
    "Egyptian": "script",  # Also script (hieroglyph)
    "Ethiopic": "script",  # Script
    "Glagolitic": "script",  # Script
    "Gothic": "script",  # Script
    "Greek": "script",  # Also script
    "Gujarati": "script",  # Script (Indo-Arabic)
    "Gurmukhi": "script",  # Script (Indo-Arabic)
    "Gwoyeu-Romatsyh": "script",  # latin alphabet for Chinese from the 1920s
    "Hanifi-Rohingya": "script",  # Script (Perso-Arabic)
    "Hebrew": "script",  # also Script (for Aramaic)
    "Hindi": "script",  # Script (at least for numberals, e.g. 80
    "Javanese": "script",  # Also script (Indonesia)
    "Jawi": "script",  # Script (Malay and several other languages)
    "Jurchen": "script",  # Script?
    "Kannada": "script",  # Script (at least for numerals, Hindu-Arabic?)
    "Kayah-Li": "script",  # Script (Sino-Tibetan)
    "Khmer": "script",  # Script
    "Khudawadi": "script",  # Script (Sindhi language, India)
    "Lanna": "script",  # Script (Thailand)
    "Lao": "script",  # Script (Lao langage in Laos)
    "Latin": "script",  # Script
    "Lepcha": "script",  # Script (Himalayas?)
    "Limbu": "script",  # Script (Limbu language in Central Himalayas)
    "Meitei": "script",  # Script (used with Meitei language in India)
    "Mongolian": "script",  # Also script
    "Myanmar": "script",  # Also script
    "N'Ko": "script",  # Script
    "Newa": "script",  # Script (Newa Spelling) ??? निर्वाचन/Newar/Noun
    "Odia": "script",  # Script (at least for numerals)
    "Ol-Chiki": "script",  # Script (Austroasiatic language in India)
    "Old-Persian": "script",  # Script
    "Oriya": "script",  # Script (Hindu-Arabic?)
    "Osmanya": "script",  # Script (Somalia)
    "POJ": "script",  # Latin alphabet based orthography for Min Nan (Peh-ōe-jī)
    "Persian": "script",  # Also script
    "Phofsit-Daibuun": "script",  # A way of writing latin alphabet Taiwanese
    "Roman": "script",  # Script
    "Rumi": "script",  # Script (modern Malay/Indonesian)
    "Saurashtra": "script",  # Script (Surashtra language in Tamil Nadu)
    "Shahmukhi": "script",  # Script (used by Punjabi Muslims for Punjabi lang)
    "Sharada": "script",  # Script (India for Sanskrit and Kashmiri; historic)
    "Sinhalese": "script",  # Script (Sri Lanka)
    "Syriac": "script",  # Also script (for Aramaic)
    "Tai-Tham": "script",  # Script (Northern Thai?)
    "Takri": "script",  # Script (mostly historic, used in Himachal Pradesh)
    "Tamil": "script",  # Also script
    "Telugu": "script",  # Also script (India)
    "Thai": "script",  # Script
    "Tibetan": "script",  # Script
    "Tirhuta": "script",  # Script (historical: Maithili, Sanskrit)
    "Warang-Citi": "script",  # Script (Ho language, East India)
    "bopomofo": "script",  # Mandarin phonetic symbols script
    "Hán-Nôm": "detail",  # Vietnamese Latin spelling with diacritics?
    "IPA": "detail",
    "pre-1989-IPA": "detail",
    "Sinological-IPA": "detail",
    "Foochow-Romanized": "detail",  # latin script for Fuzhou Eastern Min
    "Phak-fa-su": "detail",  # latin alphabet used by missionaries for Hakka (PFS)
    "Hakka-Romanization-System": "detail",  # Taiwanese Hakka Romanization System
    "Kienning-Colloqial-Romanized": "detail",  # missionary romanization system for the Kienning Dialect of Northern Min
    "Latinxua-Sin-Wenz": "detail",
    "Tai-lo": "detail",  # romanization system for Taiwanese Hokkien
    "Tongyong-Pinyin": "detail",  # Taiwanese romanization from 2002 to 2008
    "Jyutping": "detail",  # used in Cantonese
    "McCune-Reischauer": "detail",  # Used in Korean
    "Hagfa-Pinyim": "detail",
    "Rōmaji": "detail",  # Used in Okinawan, Japanese? for Latin characters
    "Yale": "detail",   # used in Cantonese
    "Guangdong-Romanization": "detail",  # way of romanizing Cantonese, Teochew, Hakka and Hainanese
    "Wiktionary-specific": "detail",  # denotes the use of Wiktionary specific conventions in spelling etc.
    "internet-slang": "misc",
    "Jinmeiyō": "misc",  # Type of Kanji used for names
    "-i": "class",   # Japanese inflection type
    "-na": "class",  # Japanese inflection type
    "-nari": "class",  # Japanese inflection type
    "-tari": "class",  # Japanese inflection type
    "abbreviation": "mod",
    "abessive": "case",   # Case
    "ablative": "case",   # Case
    "absolute": "case",   # Case, Bashkir, Swedish [absolute reflexive]
    "absolutive": "case",  # Case (patient or experience of action)
    "abstract": "misc",
    "abstract-noun": "misc",
    "accent/glottal": "misc",
    "accent-paradigm": "detail",
    "accusative": "case",  # Case for object in many languages
    "acronym": "mod",   # abbreviation formed by the initial letters of other words
    "active": "voice",
    "actor-focus": "misc",  # Tagalog
    "actor-indirect": "misc",  # Tagalog
    "actor-i": "misc",  # Ilocano verbs
    "actor-ii": "misc",
    "actor-iii": "misc",
    "actor-iv": "misc",
    "additive": "misc",  # Greenlandic: adds suffix after last letter of stem
    "addressee-feminine": "misc",
    "addressee-masculine": "misc",
    "addressee-plural": "misc",
    "addressee-singular": "misc",
    "adessive": "case",  # Case
    "adjectival": "misc",
    "adjective": "pos",
    "adjective-declension": "class",
    "admirative": "mood",  # Verb form in Albanian
    "adnominal": "misc",
    "adverb": "pos",
    "adverbial": "misc",  # XXX is this same as adverb?
    "adverbial-manner": "misc",  # Manner of action adverbial
    "affirmative": "misc",  # Used for adjectives, interjections, pronouns
    "affix": "pos",
    "after-preposition": "misc",  # Word used only after preposition nich/Lower Sorbian
    "agent": "misc",
    "agentive": "case",  # Case indicating agent
    "alienable": "possession",  # Alienable possession; Choctaw, Ojibwe, Navajo, Tokelauan etc
    "allative": "case",  # Case
    "allative-i": "case",
    "allative-ii": "case",
    "alphabetic-tones": "misc",
    "already-form": "tense",  # e.g. hojiwa/Swahili
    "also": "misc",
    "alt-of": "misc",
    "alternative": "misc",
    "ambitransitive": "transitivity",
    "analytic": "misc",
    "anaphorically": "misc",
    "animate": "category",
    "animal-not-person": "misc",  # Refers to animal (e.g., Russian anml suffix)
    "anterior": "tense",  # French seems to have "past anterior" tense
    "aorist": "tense",  # Verb form (perfective past)  E.g., Latin, Macedonian
    "aorist-ii": "tense",  # Albanian
    "apocopic": "misc",   # Omission of last vowel (+ following consonants)
    "applicative": "mood",  # Verb form
    "approximative": "case",  # Noun form (case?), e.g., марксизм/Komi-Zyrian
    "archaic": "dialect",
    "article": "detail",
    "assertive": "mood",  # Verb form (e.g., Korean)
    "associative": "case",  # Case (e.g., Quechua)
    "ateji": "misc",
    "attributive": "case",  # Adjective attributive-only form/use
    "augmentative": "misc",  # Indicates large size, intensity, seniority
    "augmented": "misc",
    "autonomous": "person",  # nigh/Irish; verb form for subjectless clauses
    "auxiliary": "detail",
    "baby-talk": "misc",
    "base-form": "misc",  # Base form of the word (e.g., with misspellings of forms)
    "before-lenited-fh": "misc",  # Next word starts with lenited fh (Irish)
    "before-past": "misc",  # Used before the past tense (Irish)
    "before-vowel": "misc",  # next words starts with vowel (in pronunciation)
    "benefactive": "case",  # Case (beneficiary of an action)
    "broadly": "misc",
    "būdinys": "misc",
    "calque": "misc",
    "cangjie-input": "detail",  # Used in Chinese characters
    "canonical": "misc",  # Used to mark the canonical word from from the head tag
    "capitalized": "misc",
    "capitalized": "misc",
    "cardinal": "misc",
    "caritive": "case",  # Case (lack or absense of something), марксизм/Komi-Zyrian
    "catenative": "misc",
    "causal-final": "misc",
    "causative": "aspect",  # Verb aspect (e.g., Japanese); Cause/Reason (Korean)
    "character": "pos",
    "childish": "misc",
    "circumstantial": "mood",  # Verb form, e.g., patjaṉi
    "circumposition": "misc",
    "class": "detail",  # Used as a head prefix in San Juan Quajihe Chatino (class 68 etc)
    "class-1": "class",    # Inflectional classes (e.g., Bantu languages), cf. gender
    "class-10": "class",
    "class-10a": "class",
    "class-11": "class",
    "class-12": "class",
    "class-13": "class",
    "class-14": "class",
    "class-15": "class",
    "class-16": "class",
    "class-17": "class",
    "class-18": "class",
    "class-1a": "class",
    "class-2": "class",
    "class-2a": "class",
    "class-3": "class",
    "class-4": "class",
    "class-5": "class",
    "class-6": "class",
    "class-7": "class",
    "class-8": "class",
    "class-9": "class",
    "class-9a": "class",
    "class-A": "class",  # e.g., Old Irish affixed pronoun classes
    "class-B": "class",
    "class-C": "class",
    "class-i": "class",  # Choctaw
    "class-ii": "class",
    "class-iii": "class",
    "class-n": "class",  # Chickasaw
    "class-a-i": "class",  # Akkadian
    "classifier": "detail",
    "clipping": "misc",
    "clitic": "misc",
    "coactive": "mood",  # Verbs in Guaraní
    "cohortative": "mood",  # Verb form: plea, imploring, wish, intent, command, purpose
    "collective": "number",  # plural interpreted collectively
    "colloquial": "register",
    "combined-form": "misc",  # e.g. Spanish combining forms
    "comitative": "case",  # Case
    "common": "misc",  # XXX where is this used, shuould this be removed?
    "common-gender": "gender",   # Gender in Swedish, Danish
    "comparable": "category",
    "comparative": "degree",  # Comparison of adjectives/adverbs
    "comparative-only": "misc",  # Only comparative used
    "completive": "aspect",
    "composition": "detail",  # Used in Chinese characters
    "compound": "misc",  # Compound words
    "compound-of": "misc",
    "concessive": "mood",  # Verb form
    "conclusive": "mood",  # Verb form (e.g., Bulgarian)
    "concrete": "misc",  # Slavic verbs; also used to describe nouns
    "conditional": "mood",  # Verb mood
    "conditional-i": "mood",  # Verb mood (German)
    "conditional-ii": "mood",  # Verb mood (German)
    "conjugation-type": "detail",  # Used to indicate form really is conjugation class
    "conjugation-1": "class",
    "conjugation-2": "class",
    "conjugation-3": "class",
    "conjugation-4": "class",
    "conjugation-5": "class",
    "conjugation-6": "class",
    "conjugation-7": "class",
    "conjugative": "misc",  # Verb form, e.g., উঘাল/Assamese
    "conjugative-of": "detail",  # Korean
    "conjunct": "misc",  # Verb form, e.g., gikaa/Ojibwe
    "conjunct-incorporating": "misc",
    "conjunct-non-incorporating": "misc",
    "conjunctive": "mood",  # Verb mood (doubt: wish, emotion, possibility, obligation)
    "conjunctive-1": "mood",  # e.g. saprast/Latvian
    "conjunctive-2": "mood",
    "conjunction": "misc",  # Used in Phalura conjunctions, relative pronouns
    "connective": "misc",  # Group of verb forms in Korean
    "connegative": "polarity",  # Indicates verb form that goes with negative
    "consecutive": "aspect",  # Verb form, e.g., થૂંકવું/Gujarati, noun form марксизм
    "construct": "misc",  # Apparently like definite/indefinite (e.g., Arabic)
    "construction-hif'il": "misc",  # Subject is cause; active voice
    "construction-hitpa'el": "misc",  # middle voice?
    "construction-hitpu'al": "misc",  # XXX Same as hitpa'el?
    "construction-huf'al": "misc",  # Subject is cause; passive voice
    "construction-nif'al": "misc",  # Neutral about subject's role; middle voice
    "construction-pa'al": "misc",  # Neutral about subject's role; active voice
    "construction-pa'el": "misc",
    "construction-peal": "misc",  # Aramaic, Classical Syriac
    "construction-pi'el": "misc",  # Subject is agent; active voice
    "construction-pu'al": "misc",  # Subject is agent; passive voice
    "contemplative": "mood",
    "contemporary": "misc",
    "contingent": "mood",  # Verb form, উঘাল/Assamese
    "continuative": "aspect",  # Verb aspect (actions still happening; e.g., Japanese)
    "contracted": "misc",  # XXX Is this the same as contraction?
    "contracted-dem-form": "misc",
    "contraction": "mod",
    "contrastive": "mood",  # Apparently connective verb form in Korean
    "converb": "misc",  # Verb form or special converb word
    "converb-i": "misc",  # e.g., խածնել/Armenian
    "converb-ii": "misc",
    "conversive": "mood",  # Verb form/type, at least in Swahili, reverse meaning?
    "coordinating": "misc",
    "copulative": "misc",
    "correlative-of": "detail",
    "cot-caught-merger": "misc",
    "count-form": "misc",  # Nominal form in Belarusian
    "countable": "category",
    "counter": "detail",
    "counterfactual": "mood",
    "dated": "dialect",
    "dative": "case",  # Case in many languages
    "debitive": "misc",  # need or obligation (XXX is this same as "obligative" ???)
    "declension-1": "class",
    "declension-2": "class",
    "declension-3": "class",
    "declension-4": "class",
    "declension-5": "class",
    "declension-6": "class",
    "declension-pattern-of": "detail",
    "declinable": "misc",
    "defective": "misc",
    "deferential": "register",  # Addressing someone of higher status
    "definite": "referent",
    "definition": "misc",
    "definitive": "misc",  # XXX is this used same as "definite": "misc", opposite indefinite?
    "deictically": "misc",
    "delative": "case",  # Case
    "deliberate": "misc",
    "demonstrative": "misc",  # Type of pronoun
    "demonym": "misc",
    "dependent": "tense",  # περπατάω/Gree/Verb (tense?); Egyptian
    "deponent": "misc",  # Having passive form with active meaning
    "derogatory": "register",
    "desiderative": "mood",  # Verb mood
    "destinative": "case",  # Case, marks destination/something destined (e.g. Hindi)
    "determinate": "misc",  # Polish verbs (similar to "concrete" in Russian?)
    "determinative-of": "detail",  # Korean
    "determiner": "misc",  # Indicates determiner; Korean determiner verb forms?
    "deuterotonic": "misc",  # e.g., dofuissim/Old Irish
    "diacritic": "misc",
    "dialectal": "misc",
    "digit": "misc",
    "diminutive": "misc",
    "diptote": "class",  # Noun having two cases (e.g., Arabic)
    "direct": "aspect",  # Apparently verb form (e.g., Hindi, Punjabi)
    "direct-object": "case",  # Case for direct object?
    "directional": "case",  # Case?, e.g., тэр/Mongolian
    "directive": "case",  # Case (locative/nearness), e.g. Basque, Sumerian, Turkic
    "disapproving": "misc",
    "discourse": "misc",  # At lest some Ancient Greek particles
    "disjunctive": "misc",
    "distal": "referent",  # Demonstrative referent is far, cf. proximal, obviative
    "distributive": "number",  # Case in Quechua? (is this case or e.g. determiner?)
    "ditransitive": "transitivity",
    "dual": "number",       # two in number, cf. singular, trial, plural
    "dubitative": "mood",  # Verb form (e.g., Bulgarian)
    "dummy-ignore-skipped": "dummy",  # Causes "-" entries to be ignored
    "dummy-ignored-text-cell": "dummy2",  # Cell has text but ignored
    "dummy-mood": "dummy",  # Used in inflection table parsing, never in data
    "dummy-skip-this": "dummy",  # Kludge in parsing, form skipped
    "dummy-tense": "dummy",  # Used in inflection table parsing, never in data
    "durative": "aspect",  # Verb form  XXX same as continuative?
    "eclipsis": "misc",
    "egressive": "case",  # Case?  e.g., дворец/Komi-Zyrian
    "elative": "case",  # Case
    "ellipsis": "misc",
    "emphatic": "misc",
    "empty-gloss": "misc",
    "enclitic": "misc",
    "endearing": "misc",  # XXX Is this different from diminutive?
    "epic": "misc",
    "epicene": "misc",
    "equative": "case",  # Case (indicates something is like something else)
    "ergative": "misc",
    "error-fixme": "error",        # "(FIXME)" recognized in Wiktionary
    "error-lua-exec": "error",     # Lua error occurred
    "error-lua-timeout": "error",  # Lua code execution timed out
    "error-unknown-tag": "error",  # Tag not recognized
    "error-misspelling": "error",  # Misspelling was recognized in Wiktionary
    "error-unrecognized-form": "error",  # Word head or table hdr unrecognized
    "especially": "misc",
    "essive": "case",  # Case
    "essive-formal": "case",  # Hungarian case
    "essive-instructive": "case",  # Hungarian case
    "essive-modal": "case",  # Hungarian case
    "ethnic": "misc",
    "eumhun": "misc",
    "euphemistic": "misc",
    "evidential": "mood",  # Verb form (e.g., Azerbaijani)
    "exaggerated": "misc",
    "excessive": "misc",
    "exclusive": "person",  # inclusive vs. exclusive first-person; case in Quechua
    "exessive": "case",  # Case (transition away from state)
    "expectative": "mood",  # Verb form, e.g., ϯϩⲉ/Coptic
    "expletive": "misc",
    "expressively": "misc",
    "extended": "misc",  # At least in some Bulgarian forms, e.g. -лив
    "extinct": "misc",  # Uses for taxonomic entries, indicates species is extinct
    "factitive": "misc",  # Not sure if same or different as factive
    "factive": "mood",  # Verb mood, assumed to be true
    "familiar": "register",  # Formality/politeness degree of verbs etc
    "feminine": "gender",  # Grammatical gender, masculine, neuter, common, class-* etc.
    "feminine-usually": "gender",  # m/f, but usually feminine
    "figuratively": "misc",
    "finite-form": "misc",  # General category for finite verb forms
    "first-person": "person",
    "focalising": "mood",  # Verb form, e.g., ϯϩⲉ/Coptic
    "form-i": "misc",
    "form-ii": "misc",
    "form-iii": "misc",
    "form-iiiq": "misc",
    "form-iiq": "misc",
    "form-iq": "misc",
    "form-iv": "misc",
    "form-ivq": "misc",
    "form-ix": "misc",
    "form-of": "misc",
    "form-v": "misc",
    "form-vi": "misc",
    "form-vii": "misc",
    "form-viii": "misc",
    "form-x": "misc",
    "form-xi": "misc",
    "form-xii": "misc",
    "form-xiii": "misc",
    "formal": "register",  # Formality/politeness degree of verbs etc
    "four-corner": "detail",  # Used in Chinese characters
    "fourth-person": "person",
    "frequentative": "misc",
    "front-vowel": "misc",
    "fusioning": "misc",  # Greenlandic suffixes
    "future": "tense",  # Verb tense
    "future-near": "tense",  # immediate future ba/Zulu
    "future-remote": "tense",  # remote future ba/Zulu
    "future-perfect": "tense",  # future anteriore ripromettersi/Italian
    "future-i": "tense",  # Verb tense (German, e.g., vertippen)
    "future-ii": "tense",  # Verb tense (German)
    "gender-neutral": "gender",
    "general": "misc",  # In general temporal participle, e.g., talamaq/Azerbaijani
    "general-mood": "mood",  # e.g. hojiwa/Swahili
    "genitive": "case",
    "gerund": "non-finite",
    "gnomic": "mood",  # e.g. hojiwa/Swahili
    "goal": "mood",  # Verb form, e.g., উঘাল/Assamese
    "grade-1-kanji": "misc",
    "grade-2-kanji": "misc",
    "grade-3-kanji": "misc",
    "grade-4-kanji": "misc",
    "grade-5-kanji": "misc",
    "grade-6-kanji": "misc",
    "habitual": "aspect",  # Verb aspect
    "half-participle": "non-finite",  # e.g. važiuoti/Lithuanian/Verb
    "hangeul": "script",  # Korean script
    "hanja": "script",  # Han character script (Chinese characters) to write Korean
    "hard": "misc",  # sladek/Slovene
    "hellenism": "misc",
    "hidden-n": "class",   # Mongolian declension
    "hiragana": "script",  # Japanese syllabic spelling for native words
    "historic": "tense",  # Grammatical tense/mood for retelling past events
    "historical": "misc",  # Relating to history
    "honorific": "register",  # Formality/politeness degree of verbs etc
    "hortative": "mood",  # Verb mood
    "humble": "register",
    "humorous": "register",
    "hypernym": "misc",
    "hypercorrect": "misc",
    "hyponym": "misc",
    "hypothetical": "mood",  # Verb mood (e.g., Japanese)
    "ideophonic": "misc",
    "idiomatic": "misc",
    "if-not-form": "mood",  # e.g. hojiwa/Swahili
    "if-when-form": "mood",  # e.g. hojiwa/Swahili
    "illative": "case",  # Case
    "imperative": "mood",  # Mood
    "imperative-only": "misc",
    "imperfect": "tense",  # Past tense in various languages
    "imperfect-se": "misc",  # Spanish se/ra distinction
    "imperfective": "aspect",  # Verb aspect (action not completed)
    "impersonal": "person",  # Verb form, e.g., Portuguese impersonal infinitive
    "impolite": "register",  # Politeness degree of verbs etc
    "imitating": "misc",  # imitating X
    "in-certain-phrases": "misc",
    "in-compounds": "misc",
    "in-plural": "misc",
    "in-indicative": "misc",
    "in-conditional": "misc",
    "in-variation": "misc",  # E.g. crush,WiFi,lhama,tsunami/Portuguese,
    "inalienable": "possession",  # Inablienable possession: body parts etc; Choctaw, Ojibwe..
    "inanimate": "category",
    "including": "misc",
    "includes-article": "misc",  # Word form includes article
    "inclusive": "person",  # inclusive vs. exclusive first-person
    "indeclinable": "class",
    "indefinite": "referent",
    "independent": "misc",  # Verb form, e.g., gikaa/Ojibwe
    "indeterminate": "misc",  # Polish verbs (similar to "abstract" in Russian)
    "indicative": "mood",  # Indicative mood
    "indirect": "aspect",  # Verb form, e.g., بونا/
    "indirect-object": "case",  # Case for indirect object
    "inessive": "case",  # Case
    "inferential": "mood",  # Verb form (w/ aorist), e.g. -ekalmak/Turkish
    "infinitive": "non-finite",  # Verb form
    "infinitive-aorist": "non-finite",  # e.g. περπατάω/Greek non-finite form
    "infinitive-da": "non-finite",  # Estonian: indicative active negative imperfect / indicative active pluperfect / imperative active present (non-2sg) / active perfect (hypothetical action - general action)
    "infinitive-i": "non-finite",  # Finnish
    "infinitive-i-long": "non-finite",  # Finnish
    "infinitive-ii": "non-finite",  # Finnish
    "infinitive-iii": "non-finite",  # Finnish
    "infinitive-iv": "non-finite",  # Finnish
    "infinitive-ma": "non-finite",  # Estonian: positive imperfect, quotative (has happened, is happening, or will happen)
    "infinitive-v": "non-finite",  # Finnish
    "infinitive-zu": "non-finite",  # German
    "infix": "pos",
    "inferred": "mood",
    "inflected": "misc",  # Marks inflected form, constrast to uninflected (e.g., Dutch)
    "inflected-like": "misc",  # seleen/Limburgish
    "informal": "register",  # Formality/politeness degree of verbs etc
    "initialism": "misc",
    "injunctive": "mood",  # Verb form, e.g., पुस्नु/Nepali
    "instructive": "case",  # Case
    "instrumental": "case",  # Case
    "iterative": "misc",
    "intensifier": "misc",  # In participle of intensification, e.g., talamaq
    "intentive": "mood",  # Verb form, e.g., patjaṉi
    "interfix-j": "misc",  # Greenlandic: adds -j- after long vowel
    "interjection": "misc",
    "interrogative": "mood",
    "intransitive": "transitivity",
    "invariable": "misc",
    "invertive": "case",  # Case? (e.g., Сотрэш/Adyghe)
    "involuntary": "mood",  # Verb form, e.g., khitan/Indonesian
    "ionic": "misc",  # XXX ???
    "ironic": "misc",
    "irrealis": "mood",  # Verb form, e.g., たたかう/Japanese
    "irregular": "misc",  # Word has irregular inflection
    "irregular-pronunciation": "misc",  # Kanji or similar pronunciation irregular
    "italics": "misc",  # Used in head form to indicate italic character variant
    "iō-variant": "misc",  # e.g. horior/Latin, interiicio/Latin
    "jargon": "register",
    "jussive": "mood",  # Verb mood for orders, commanding, exhorting (subjunctively)
    "kanji": "misc",  # Used in word head for some Japanese symbols
    "katakana": "script",  # Japanese syllabic spelling for foreign words
    "krama": "register",  # Javanese register (polite form)
    "krama-ngoko": "register",  # Javanese register (neutral, without polite)
    "kyūjitai": "detail",  # Traditional Japanese Kanji (before 1947)
    "l-participle": "non-finite",  # dati/Proto-Slavic
    "lative": "case",  # Case, e.g., тіл/Khakas
    "lenition": "misc",
    "letter": "misc",
    "letter-name": "misc",
    "limitative": "mood",  # Verb form, e.g., ϯϩⲉ/Coptic
    "literally": "misc",
    "literary": "misc",
    "locative": "case",
    "locative-qualitative": "case",
    "long-form": "misc",  # Verb forms, отъпоустити/Old Church Slavonic; long past participle e.g. anexar/Portuguese
    "lowercase": "misc",
    "main-clause": "misc",  # e.g., omzagen/Dutch
    "mainly": "misc",
    "majestic": "register",  # Referring to kings, queens, presidents, God
    "masculine": "gender",  # Grammatial gender see feminine, neuter, common, class-* etc.
    "masculine-usually": "gender",  # m/f, but usually masculine
    "material": "misc",
    "matronymic": "misc",
    "medial": "misc",
    "mediopassive": "voice",
    "meliorative": "misc",  # XXX See essere/Italian/Noun word head
    "metaphoric": "misc",
    "metonymically": "misc",
    "metrically": "misc",  # Used in Sanskrit word heads
    "mi-form": "misc",  # Malagasy verbs
    "middle": "voice",  # At least middle voice (cf. active, passive)
    "middle-infinitive": "non-finite",
    "mildly": "misc",
    "misconstruction": "misc",  # Used for e.g. incorrect Latin plurals
    "misspelling": "misc",
    "mixed": "misc",
    "mixedcase": "misc",
    "mnemonic": "misc",
    "modal": "misc",
    "modern": "misc",
    "modified": "misc",  # Noun form, e.g., dikko/Sidamo (similar to person?)
    "monopersonal": "misc",
    "morpheme": "misc",
    "morse-code": "misc",
    "motive-form": "mood",  # Verb form for Korean (e.g., 조사하다)
    "multiplicative": "case",  # adverbial case in Finnish
    "multiword-construction": "misc",  # complex tenses in French/English conjugation
    "mutated": "misc",
    "mutation": "misc",
    "mutation-aspirate": "misc",
    "mutation-mixed": "misc",
    "mutation-nasal": "misc",
    "mutation-radical": "misc",  # "radical" in mutation tables, e.g. hun/Welsh
    "mutation-soft": "misc",  # At least Welsh
    "name": "misc",
    "narrowly": "misc",
    "natural": "misc",
    "necessitative": "mood",  # Verb form in some languages
    "negated-with": "misc",  # Indicates how word is negated, e.g., ϣⲗⲏⲗ/Coptic
    "negative": "polarity",  # Indicates negation of meaning (nominal or verbal)
    "neologism": "misc",
    "neuter": "gender",  # Gender, cf. masculine, feminine, common-gender etc.
    "next": "misc",  # Next value in sequence (number, letter, etc.)
    "no-absolute": "misc",           # No aboslute form; femri/Icelandic
    "no-auxiliary": "misc",	     # No auxiliary needed for verb (?); lavarsi/Italian
    "no-comparative": "misc",        # The word has no comparative form
    "no-construct-forms": "misc",    # The word has no construct forms
    "no-definite": "misc",	     # Danish "no definite forms"
    "no-diminutive": "misc",         # No diminutive form (goeste/West Flemish)
    "no-feminine": "misc",	     # No feminine form (ácimo/Spanish)
    "no-first-person-singular-past-historic": "misc",  # Italian
    "no-first-person-singular-present": "misc",  # Spanish (only third person?)
    "no-first-person-singular-preterite": "misc",  # Spanish (only third person?)
    "no-genitive": "misc",           # The word has no genitive form
    "no-gradation": "gradation",     # No consonant gradation
    "no-imperfective": "misc",       # No imperfective form (исходить/Russian)
    "no-infinitive": "misc",	     # No infinitive form (måste/Swedish)
    "no-nominative": "misc",         # The word has no nominative form (from this base)
    "no-nominative-plural": "misc",  # The word has no nominative plural
    "no-past": "misc",	 	     # No simple past form"
    "no-past-participle": "misc",    # The word has no past participle
    "no-perfect": "misc",            # The word has no perfect/perfective aspect/form
    "no-plural": "misc",             # The word has no plural form (= singular only)
    "no-possessor": "misc",	     # No possessor in possessive hajallan/Finnish
    "no-present-participle": "misc",  # The word has no present participle
    "no-second-person-singular-imperative": "misc",  # No imperative
    "no-senses": "misc",             # Added synthesized sense when no senses extracted
    "no-singulative": "misc",	     # no singulative form
    "no-short-form": "misc",	     # no short forms (Russian)
    "no-superlative": "misc",        # The word has no superlative form
    "no-supine": "misc",             # The word has no supine form
    "no-third-person-singular-past-historic": "misc",  # Italian
    "no-third-person-singular-present": "misc",  # mittagessen/German
    "nominal": "pos",
    "nominal-state": "misc",
    "nominative": "case",
    "nomino-accusative": "misc",  # 𒀀𒄿𒅖/Hittite XXX same as nominate/accusative???
    "non-aspectual": "aspect",  # E.g., भूलना/Hindi
    "non-durative": "misc",  # non-durative sentence, e.g., ϣⲗⲏⲗ/Coptic
    "non-numeral": "misc",  # Assamese noun forms
    "non-past": "tense",  # Verb tense (e.g., Korean)
    "non-prospective": "misc",  # e.g. götürmek/Turkish
    "non-scientific": "misc",
    "non-subject": "misc",    # ishno'/Chickasaw
    "nonce-word": "misc",
    "nondeferential": "misc",
    "nonstandard": "dialect",
    "nonvirile": "category",
    "not-clause-initial": "misc",
    "not-comparable": "category",
    "not-mutable": "misc",
    "not-translated": "misc",
    "not-yet-form": "tense",  # e.g. hojiwa/Swahili
    "noun": "pos",
    "noun-from-adj": "derivation",
    "noun-from-noun": "derivation",  # Greenlandic: suffix derives nominal from nominal
    "noun-from-verb": "derivation",  # Greenlandic: suffix derives nominal from verb
    "numeral": "pos",  # Numeral part-of-speech; also Assamese noun forms
    "numeral-tones": "misc",
    "obligative": "mood",  # Verb form (e.g., Azerbaijani)
    "object-concord": "misc",  # Verb form includes object-based inflection
    "object-first-person": "object",  # Swahili object concords, Spanish combined-form
    "object-second-person": "object",
    "object-third-person": "object",
    "object-singular": "object",
    "object-plural": "object",
    "object-definite": "object",  # Object is definite, e.g. fut/Hungarian
    "object-indefinite": "object",  # Object is indefinite
    "object-class-1": "object",  # Swahili object class for object concord
    "object-class-2": "object",
    "object-class-3": "object",
    "object-class-4": "object",
    "object-class-5": "object",
    "object-class-6": "object",
    "object-class-7": "object",
    "object-class-8": "object",
    "object-class-9": "object",
    "object-class-10": "object",
    "object-class-11": "object",
    "object-class-12": "object",
    "object-class-13": "object",
    "object-class-14": "object",
    "object-class-15": "object",
    "object-class-16": "object",
    "object-class-17": "object",
    "object-class-18": "object",
    "objective": "case",  # Case, used as an object
    "oblique": "case",  # Apparently like case form (e.g., Hindi)
    "obsolete": "dialect",
    "obviative": "referent",  # Referent is not the most salient one, cf. proximal, distal
    "offensive": "register",
    "often": "misc",
    "one-termination": "misc",
    "onomatopoeic": "misc",
    "oppositive": "misc",  # expresses contrariety
    "optative": "misc",
    "ordinal": "misc",
    "parasynonym": "misc",
    "parenthetic": "misc",
    "participle": "non-finite",
    "participle-1": "non-finite",  # e.g. saprast/Latvian/Verb
    "participle-2": "non-finite",
    "participle-3": "non-finite",
    "participle-4": "non-finite",
    "particle": "pos",
    "partitive": "case",  # Case
    "passive": "voice",
    "passive-mostly": "misc",  # Attested mostly in the passive
    "past": "tense",
    "past-future": "tense",  # Future in the past
    "past-recent": "tense",
    "past-remote": "tense",
    "patronymic": "misc",
    "paucal": "number",  # cf. singular, plural, dual, trial
    "pausal": "misc",  # Relates to prosody/pronunciation?
    "pejorative": "misc",
    "perfect": "tense",  # Tense/verb form, e.g., in Finnish
    "perfect-i": "tense",  # E.g., talamaq/Azerbaijani
    "perfect-ii": "tense",  # E.g., talamaq/Azerbaijani
    "perfective": "aspect",  # Verb aspect
    "person": "category",
    "personal": "misc",  # Type of pronoun; Verb form (e.g., Portuguese personal infinitive)
    "phoneme": "misc",
    "phrasal": "misc",
    "phrase": "misc",
    "physical": "misc",
    "pin-pen-merger": "misc",
    "place": "misc",
    "pluperfect": "tense",  # Tense/verb form
    "pluperfect-i": "tense",  # воштыны'/Udmurt
    "pluperfect-ii": "tense",
    "plural": "number",     # Number, cf. sigular, dual, trial
    "plural-of": "detail",  # Plural form of something
    "plural-of-variety": "misc",  # Plural indicating different kinds of things (Arabic)
    "plural-only": "misc",  # Word only manifested in plural in this sense
    "plural-normally": "misc",  # Usually plural, but singular may be possible
    "poetic": "misc",
    "polite": "register",  # Politeness degree of verbs etc
    "polytonic": "misc",
    "positive": "degree",  # opposite of negative (usually unattested); degree
    "possessed-form": "misc",  # Marks object that is possessed, cf. possessed
    "possessive": "possession",  # Possession (marks who possesses)
    "possessive-single": "possession",  # Possessive with single possessed
    "possessive-many": "possession",  # Possessive with multiple possessed
    "possessive-masculine": "possession",  # Possessive with masculine possessed
    "possessive-feminine": "possession",  # Possessive with feminine possessed
    "possessive-common": "possession",  # Possessive with common-g possessed
    "possessive-neuter": "possession",  # Possessive with neuter possessed
    "possibly": "misc",
    "postpositional": "misc",
    "potential": "mood",  # Verb mood
    "praenominal": "misc",
    "precursive": "mood",  # Verb form, e.g. ϯϩⲉ/Coptic
    "predicative": "case",  # Adjective predicate-only form/use
    "prefix": "pos",
    "preparative": "aspect",  # Verb form, e.g., ᠵᡠᠸᡝᡩᡝᠮᠪᡳ/Manchu
    "prepositional": "misc",
    "present": "tense",  # Verb tense
    "present-rare": "misc",  # Present tense is rare
    "presumptive": "mood",  # Verb mood, e.g., गरजना/Hindi
    "preterite": "tense",  # Verb tense (action in the past, similar to simple past)
    "preterite-present": "tense",  # word where present&preterite forms look opposite
    "preterite-perfect": "tense",  # trapassato remoto ripromettersi/Italian
    "preterite-i": "tense",  # воштыны/Udmurt
    "preterite-ii": "tense",
    "pretonic": "misc",  # Precedes stressed syllable
    "previous": "misc",  # Previous value in sequence (number, letter, etc.)
    "proclitic": "misc",
    "progressive": "aspect",  # Verb form, e.g., પચવું/Gurajati
    "prohibitive": "mood",  # Verb form (negative imperative), e.g., Old Armenian
    "prolative": "case",
    "pronominal": "misc",
    "pronominal-state": "misc",
    "pronoun": "pos",
    "pronoun-included": "misc",
    "pronunciation-spelling": "misc",
    "proper-noun": "pos",
    "proscribed": "misc",
    "prosecutive": "case",  # Case (move along a surface or way); Greenlandic -nnguaq
    "prospective": "misc",  # E.g., götürmek/Turkish
    "prothesis": "misc",
    "prothesis-h": "misc",
    "prothesis-t": "misc",
    "prototonic": "misc",  # E.g., dofuissim/Old Irish
    "proximal": "referent",  # Demonstrative referent is far, cf. distal, obviative
    "purposive": "mood",  # Verb form, e.g., patjaṉi
    "quadral": "misc",
    "quantified": "misc",  # bat/Jamaican Creole (head form)
    "quotative": "mood",  # Verb mood (marks quoted speech keeping orig person/tense)
    "radical": "detail",  # Used in Chinese characters
    "radical+strokes": "detail",  # Used in Chinese characters
    "rare": "misc",
    "realis": "mood",  # Verb form, e.g., たたかう/Japanese
    "reason": "mood",  # Verb form, e.g., উঘাল/Assamese
    "recently": "misc",  # Used in Recently complete, e.g., {ligpit,magbukid}/Tagalog
    "reciprocal": "misc",  # Mutual action (board sense reflexive)
    "reconstruction": "misc",  # This word/sense is a reconstruction for a dead language
    "reduced": "misc",  # de/Central Franconian (XXX merge with e.g. clipping?)
    "reduplication": "misc",
    "reflexive": "misc",
    "reflexive-of": "detail",  # Reflexive form of something
    "regional": "misc",
    "relational": "misc",
    "relative": "person",  # At least gp/Egyptian, nigh/Irish verb forms; conjunctions
    "renarrative": "mood",  # Verb form (e.g. Bulgarian)
    "replacive": "misc",  # Greenlandic suffixes
    "reported": "mood",  # Verb forms for reported speech
    "resultative": "misc",  # partciple in Armenian (state resulting from action)
    "retronym": "misc",
    "revised": "misc",  # Used in many Korean words, is this same as revised-jeon?
    "revised-jeon": "misc",
    "rhetoric": "misc",
    "romanization": "detail",  # Latin character version of other script
    "root": "misc",
    "sarcastic": "misc",
    "second-person": "person",
    "second-person-semantically": "person",  # semantically second person
    "secular": "misc",  # Contrast with Ecclesiastical, Tham, etc
    "semelfactive": "misc",
    "sentence-case": "misc",  # дь/Yakut
    "sentence-final": "misc",  # Korean verb forms (broad category)
    "separable": "misc",  # Used for separable verbs, e.g. omzagen/Dutch
    "separative": "case",  # e.g. keulemmaksi/Finnish
    "sequence": "misc",
    "sequential": "misc",
    "shinjitai": "misc",  # Simplified Japanese Kanji (after 1947)
    "short-form": "misc",  # Verb forms, отъпоустити/Old Church Slavonic; Portuguese short past participle e.g. anexar/Portuguese
    "si-perfective": "misc",
    "simplified": "misc",
    "simultaneous": "misc",  # simultaneous converb, e.g. խածնել/Armenian
    "singular": "number",  # Number, cf. plural, dual, trial, paucal
    "singular-normally": "misc",
    "singular-only": "misc",
    "singulative": "misc",  # Individuation of a collective or mass noun, like number
    "situative": "case",  # expressing location of things in comparison with one another
    "slang": "register",
    "slur": "misc",
    "sociative": "case",  # Case?, e.g., மரம்/Tamil
    "soft": "misc",  # najslajši/slovene
    "sometimes": "misc",
    "special": "misc",  # Adverbial verb form in Lithuanian
    "specific": "misc",  # In specific temporal participle, e.g., talamaq
    "specifically": "misc",
    "standalone": "misc",  #  Without a main word (e.g., pronoun/determiner senses)
    "standard": "misc",
    "stative": "misc",
    "stem": "misc",  # Stem rather than full forms
    "stem-primary": "misc",  # Primary stem, e.g., दुनु/Nepali
    "stem-secondary": "misc",  # Secondary stem, e.g., दुनु/Nepali
    "stress-pattern-1": "misc",
    "stress-pattern-2": "misc",
    "stress-pattern-3": "misc",
    "stress-pattern-3a": "misc",
    "stress-pattern-3b": "misc",
    "stress-pattern-4": "misc",
    "stressed": "misc",  # Marked/full form, cf. unstressed
    "stressed-preposition": "misc",
    "strict-sense": "misc",
    "strokes": "misc",
    "strong": "misc",  # strong form / strong inflection class
    "subjective": "case",  # Case, used as a subject; subject form
    "subjunctive": "mood",  # Subjunctive mood
    "subjunctive-i": "mood",  # Subjunctive i mood (German)
    "subjunctive-ii": "mood",  # Subjunctive ii mood (German)
    "sublative": "case",
    "subordinate-clause": "misc",  # e.g., ϣⲗⲏⲗ/Coptic
    "subordinating": "misc",
    "subscript": "script",  # Variant of certain characters
    "substantive": "misc",
    "subsuntive": "misc",  # Verbs in Guaraní
    "suffix": "pos",
    "superessive": "case",  # Case, e.g., Hungarian
    "superlative": "degree",  # Comparison of adjectives/adverbs
    "superplural": "number",  # Very many (rare, e.g. Barngarla (Australian))
    "superscript": "script",  # Variant of certain characters
    "supine": "non-finite",   # Various non-finite forms in several languages
    "suppletive": "misc",
    "surname": "misc",
    "suru": "class",  # Japanese verb inflection type
    "syllable-final": "misc",
    "syllable-initial": "misc",
    "symbol": "misc",
    "syncope": "misc",
    "synecdoche": "misc",
    "synonym": "misc",
    "synonym-of": "misc",
    "table-tags": "detail",  # Tags from inflection table, for all entries
    "taboo": "misc",
    "tafa-form": "misc",  # Malagasy verbs
    "temporal": "misc",  # relating to time/tense, e.g., talamaq; Finnish adverbials
    "term-of-address": "misc",
    "terminative": "aspect",  # Verb aspect/mood (e.g., Japanese); also case in Quechua?
    "thematic": "misc",
    "third-person": "person",
    "three-termination": "misc",
    "tone-1": "misc",
    "tone-2": "misc",
    "topicalized": "misc",
    "toponymic": "misc",
    "traditional": "misc",
    "transcription": "misc",
    "transgressive": "non-finite",  # Verb form  XXX non-finite/mood/tense?
    "transitive": "transitivity",
    "transitive-with-of": "misc",
    "translation-hub": "misc",  # Predictable compound term with translations, no gloss
    "translative": "case",
    "translingual": "misc",
    "transliteration": "misc",
    "trial": "number",  # Number, cf. singular, dual, plural
    "trigger-actor": "trigger",  # Actor trigger, e.g., magtinda/Tagalog
    "trigger-benefactive": "trigger",  # Benefactive trigger
    "trigger-causative": "trigger",  # Causative trigger
    "trigger-instrument": "trigger",  # Instrument trigger
    "trigger-locative": "trigger",  # Locative trigger
    "trigger-measurement": "trigger",  # Measurement trigger, e.g., rumupok/Tagalog
    "trigger-object": "trigger",  # Object trigger
    "trigger-referential": "trigger",   # Referential trigger
    "triggers-eclipsis": "trigger",      # Irish
    "triggers-h-prothesis": "trigger",   # Irish
    "triggers-lenition": "trigger",      # Irish
    "triggers-mutation-aspirate": "trigger",  # Welsh
    "triggers-mutation-mixed": "trigger",  # Welsh
    "triggers-mutation-nasal": "trigger",  # Old Irish
    "triggers-mutation-soft": "trigger",  # Welsh
    "triggers-no-mutation": "trigger",  # Irish
    "triptote": "class",  # Noun having three cases (e.g., Arabic)
    # ~ "triptote-a": "class",  # "singular triptote in ـَة (-a)" جاذب/Arabic/Adj
    "truncative": "misc",  # Greenlandic: suffix attaches to last vowel, removing stuff
    "two-termination": "misc",
    "type-a": "class",
    "type-p": "class",
    "type-u": "class",
    "type-ua": "class",
    "type-up": "class",
    "unabbreviated": "mod",
    "unaugmented": "misc",
    "uncommon": "misc",
    "uncountable": "category",
    "unemphatic": "misc",
    "uninflected": "misc",  # uninflected form (e.g., Dutch), cf. inflected
    "universal": "misc",  # universally known (καθεμία/Greek)
    # Arabic seems to use "unknown" for theoretical forms not attested
    "unknown": "misc",  # Apparently verb form, e.g., जाँच्नु/Nepali
    "unmodified": "misc",  # Noun form, e.g., dikko/Sidamo (similar to person?)
    "unpossessed-form": "possession",  # Not possessed (often omitted)
    "unspecified": "misc",  # селен/Macedonian uses this like proximal/distal
    "unstressed": "misc",  # Unstressed (unmarked, weaker) form
    "unstressed-before-j": "misc",  # unstressed when next word starts with /j/
    "uppercase": "misc",
    "used-in-the-form": "misc",
    "usually": "misc",
    "usually-without-article": "misc",
    "utterance-medial": "misc",
    "variant": "misc",
    "vav-consecutive": "misc",
    "vernacular": "register",
    "verb": "pos",
    "verb-completement": "misc",  # Used in some Chinese words (merged verb+complement?)
    "verb-form-da": "misc",  # Estonian da-form  XXX is this same as infinitive-da?
    "verb-form-des": "misc",  # Estonian des-form
    "verb-form-i": "misc",
    "verb-form-ii": "misc",
    "verb-from-noun": "derivation",  # Forms verbs from nominals
    "verb-object": "misc",  # Used in some Chinese words (verb+object in same entry?)
    "verb-from-verb": "derivation",  # Suffix modifies verbs producing verbs
    "vigesimal": "misc",
    "virile": "category",
    "visual-rendering": "misc",
    "voa-form": "misc",  # Malagasy verbs
    "vocative": "case",  # Case? used for addressee
    "volitive": "mood",  # Verb form ?  XXX is this same as volitional?
    "volitional": "mood",  # Verb mood (e.g., Japanese: suggests, urges, initates act)
    "vos-form": "register",  # Spanish verb forms used with "vos"
    "vulgar": "register",
    "weak": "misc",
    "with-a": "with",
    "with-ablative": "with",
    "with-absolute": "with",
    "with-absolutive": "with",
    "with-accusative": "with",
    "with-action-noun-in-elative": "with",
    "with-adessive": "with",
    "with-adjective": "with",
    "with-adverb": "with",
    "with-allative": "with",
    "with-an": "with",
    "with-avec": "with",
    "with-ce": "with",
    "with-che": "with",
    "with-comparative": "with",
    "with-con": "with",
    "with-conditional": "with",
    "with-da": "with",
    "with-dative": "with",
    "with-de": "with",
    "with-definite-article": "with",
    "with-di": "with",
    "with-down": "with",
    "with-ela": "with",
    "with-elas": "with",
    "with-elative": "with",
    "with-ele": "with",
    "with-eles": "with",
    "with-ella": "with",
    "with-ellas": "with",
    "with-ellos": "with",
    "with-en": "with",
    "with-essive": "with",
    "with-eu": "with",
    "with-infinitive-i": "with",
    "with-future": "with",
    "with-for": "with",
    "with-gendered-noun": "with",
    "with-genitive": "with",
    "with-gij": "with",
    "with-hiri": "with",
    "with-hura": "with",
    "with-illative": "with",
    "with-imperfect": "with",
    "with-in": "with",
    "with-indicative": "with",
    "with-indirect-object": "with",
    "with-indirect-relative": "with",
    "with-inessive": "with",
    "with-infinitive": "with",
    "with-instrumental": "with",
    "with-it-dialectally": "with",
    "with-järgi": "with",
    "with-kala": "with",
    "with-kV": "with",  # gǀkxʻâã/ǃXóõ
    "with-lai": "with",
    "with-locative": "with",
    "with-meel": "with",
    "with-negation": "with",
    "with-negative-adj": "with",
    "with-nominative": "with",
    "with-nos": "with",
    "with-nosotras": "with",
    "with-nosotros": "with",
    "with-noun": "with",
    "with-noun-phrase": "with",
    "with-number": "with",
    "with-objective": "with",
    "with-odd-syllable-stems": "with",
    "with-of": "with",
    "with-olemassa": "with",  # Finnish
    "with-on": "with",
    "with-optative": "with",
    "with-others": "with",
    "with-partitive": "with",
    "with-passive-present-participle": "with",
    "with-passive-past-participle-partitive": "with",
    "with-passive-past-participle-translative": "with",
    "with-past": "with",
    "with-past-participle": "with",
    "with-past-participle-translative": "with",
    "with-past-participle-partitive": "with",
    "with-per": "with",
    "with-personal-pronoun": "with",
    "with-por": "with",
    "with-positive-imperative": "with",
    "with-possessive-suffix": "with",
    "with-pour": "with",
    "with-prepositional": "with",
    "with-present": "with",
    "with-savrtsobi": "with",
    "with-su": "with",
    "with-subjunctive": "with",
    "with-subordinate-clause": "with",
    "with-sur": "with",
    "with-dummy-subject": "with",
    "with-there": "with",
    "with-third-person": "with",
    "with-third-person-singular": "with",
    "with-infinitive-iii": "with",
    "with-infinitive-iii-abessive": "with",
    "with-infinitive-iii-elative": "with",
    "with-infinitive-iii-illative": "with",
    "with-to": "with",
    "with-translative": "with",
    "with-tu": "with",
    "with-tú": "with",
    "with-up": "with",
    "with-usted": "with",
    "with-ustedes": "with",
    "with-você": "with",
    "with-vocês": "with",
    "with-von": "with",
    "with-vos": "with",
    "with-voseo": "with",
    "with-vosotras": "with",
    "with-vosotros": "with",
    "with-välja": "with",
    "with-vós": "with",
    "with-yo": "with",
    "with-zuek": "with",
    "with-à": "with",
    "with-él": "with",
    "without-article": "misc",  # E.g., grüun/Cimbrian
    "without-noun": "misc",
    "æ-tensing": "misc",
    "има": "misc",  # Distinguishes certain verb forms in Macedonian
    "non-human": "misc",  # XXX is there already a tag for this? himself/English - KJ
    "with-article": "misc",  # Mosambik/German
    "before-noun": "misc",  # Mama/German
    "with-numeral": "with",  # Radlermaß/German
    "without-numeral": "misc",  # Radlermaß/German
    "same-sort": "number",  # Wahnsinnsding/German
    "different-sort": "number",  # Wahnsinnsding/German
    "sigmatic": "mood",  # adiuvo/Latin
    "dummy-column": "dummy",  # in חֲתוּלָתִי‎/Hebrew, Isolated forms
    "be-prefix": "misc",  # laikytis/Lithuanian, multi-use prefix...
    "Japanese": "script",  # also script, 弧/translingual, stroke count stuff
    "l-participle": "non-finite",  # доврне/Macedonian
    "privative": "mood",  # afrohet/Albanian
    # ~ "comparative-of": "degree",  # miður/Icelandic
    "xemxin-assimilation": "misc",  # lil/Maltese
    "qamrin-unassimilation": "misc",
    "with-conjunction": "with",  # thathar/Scottish Gaelic
    "with-pronoun": "with",  # thathar/Scottish Gaelic
    "unabbreviation": "mod",  # jku/Finnish
    "long-construct": "misc",  #a ذو الحجة/Arabic
    "actor-secondary": "aspect",  # Tagalog thing
    "inferior": "degree",  #madali/Tagalog
    "superior": "degree",
    "equal": "degree",
    "l-case": "case",  #ufuy/Afar
    "k-case": "case",  #ufuy/Afar
    "t-case": "case",  #ufuy/Afar
    "h-case": "case",  #ufuy/Afar
    "with-postposition": "with",  #ufuy/Afar
    #icfide/Afar
    "immediate-future": "tense",
    "potential-i": "mood",
    "potential-ii": "mood",
    "n-affirmative": "misc",
    "v-affirmative": "misc",
    "conjunctive-i": "mood",
    "conjunctive-ii": "mood",
    "consultative": "mood",
    "h-converb":  "non-finite",
    "i-form":  "non-finite",
    "k-converb":  "non-finite",
    "innuh-converb": "non-finite",
    "innuk-converb": "non-finite",
    "v-focus": "non-finite",
    "n-focus": "non-finite",
    # qunxa/Afar
    "indicative-i": "mood",
    "indicative-ii": "mood",
    "duoplural": "number",  # niteel/Navajo
    "indefinite-person": "person",
    "spatial-person": "person",
    "middle-voice": "voice", # अवति/Sanskrit
    "inversion": "case",  # დაწერს/Sanskrit
    "full-form": "misc",  # ichwane/Zulu, "full" and "basic" forms
    "basic-form": "misc",
    "possessive-substantive": "possession",  # explicit possessives without possessed: father's computer -> that's father's
    "unmutated": "misc",  #glad/Breton
    "mutation-hard": "misc",
    "confirmative": "tense",  # сэрээх/Mongolian, past tense + evidentiality
                              # also 'resultative', but that's already used
    "with-ergative": "with",  #a ہاوُن/Kashmiri
    "with-determiner": "with",  # idealistesch/Luxembourgish
    "without-determiner": "misc",
    "with-head": "with",
    "consequential": "mood",  # erakutsi/Basque
    "past-i": "tense",  #eh/Albanian
    "past-ii": "tense",
    "focus": "detail",  #magwahil/Tagalog, trigger-focus
    "sound-plural": "class",
    "ar-infl-in": "class",  # Decomposing Arabic inflectional paradigms, سحلية/Arabic,تحو/Arabic
    "ar-infl-ah": "class",  #a قناة السويس/Arabic حماة/Arabic
    "ar-infl-an-maksura": "class",  #a مدى/Arabic
    "ar-infl-an-alef": "class",   #a سنا/Arabic
    "ar-infl-awna": "class",
    "ar-infl-a": "class",  #a رمية/Arabic # "singular triptote in ـَة (-a)" جاذب/Arabic/Adj
    "broken-form": "class",  # Arabic broken-plural and broken-paucal
    "sound-form": "class",  # Arabic sound-feminine-plural sound-masculine-paucal etc.
    
}

for k, v in valid_tags.items():
    assert isinstance(k, str)
    if v not in tag_categories:
        print("valid_tags[{!r}]={!r} - {!r} not in tag_categories!"
              .format(k, v, v))
        assert v in tag_categories

for tag in form_of_tags - set(valid_tags.keys()):
    print("tags.py:form_of_tags contains invalid tag {}"
          .format(tag))


def sort_tags(tags):
    """Sorts tags into presentation order and returns them as a tuple.
    This also removes duplicates."""
    assert isinstance(tags, (list, tuple, set))
    return tuple(sorted(set(tags), key=lambda t:
                        tag_categories.get(valid_tags.get(t, "unknown"), 0) -
                        len(t) / 1000,
                        reverse=True))

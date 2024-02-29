from .models import WordEntry

GENDER_TAGS: dict[str, str] = {
    "陰性": "feminine",
    "陽性": "masculine",
    "中性": "neuter",
}

NUMBER_TAGS: dict[str, str] = {
    "單數": "singular",
    "複數": "plural",
    "定單數": "definite singular",
    "不定複數": "indefinite plural",
    "定複數": "definite plural",
    "斜格複數": "oblique plural",
    "主格單數": "nominative singular",
    "主格複數": "nominative plural",
    "屬格單數": "genitive singular",
    "屬格複數": "genitive plural",
    "陰性單數": "feminine singular",
    "陽性單數": "masculine singular",
    "陰性複數": "feminine plural",
    "陽性複數": "masculine plural",
    "中性複數": "neuter plural",
    "中性單數": "neuter singular",
}

# https://en.wikipedia.org/wiki/Count_noun
COUNT_TAGS: dict[str, str] = {
    "可數": "countable",
    "不可數": "uncountable",
}

OTHER_TAGS: dict[str, str] = {
    "指小詞": "diminutive",
    "變格類型": "declension pattern",
}

VERB_TAGS: dict[str, str] = {
    "及物": "transitive",
    "不及物": "intransitive",
}

# https://en.wikipedia.org/wiki/Japanese_grammar#Stem_forms
JA_STEM_FORMS: dict[str, str] = {
    "未然形": "imperfective",
    "連用形": "continuative",
    "終止形": "terminal",
    "連體形": "attributive",
    "連体形": "attributive",
    "假定形": "hypothetical",
    "仮定形": "hypothetical",
    "命令形": "imperative",
}

# https://en.wikipedia.org/wiki/Voice_(grammar)
VOICE_TAGS: dict[str, str] = {
    "被動形": "passive",
    "使役形": "causative",
    "可能形": "potential",
    "意志形": "volitional",
    "否定形": "negative",
    "否定連用形": "negative continuative",
    "尊敬形": "formal",
    "完成形": "perfective",
    "接續形": "conjunctive",
    "條件形": "hypothetical conditional",
}


GRAMMATICAL_TAGS: dict[str, str] = {
    **GENDER_TAGS,
    **NUMBER_TAGS,
    **COUNT_TAGS,
    **OTHER_TAGS,
    **VERB_TAGS,
    **JA_STEM_FORMS,
    **VOICE_TAGS,
}


def translate_raw_tags(data: WordEntry) -> WordEntry:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag.lower() in GRAMMATICAL_TAGS:
            data.tags.append(GRAMMATICAL_TAGS[raw_tag.lower()])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
    return data


# https://zh.wiktionary.org/wiki/Template:T
# https://zh.wiktionary.org/wiki/Template:Head
# https://zh.wiktionary.org/wiki/Module:Gender_and_number
TEMPLATE_TAG_ARGS = {
    "f": "feminine",
    "m": "masculine",
    "n": "neuter",
    "c": "common",
    # Animacy
    "an": "animate",
    "in": "inanimate",
    # Animal (for Ukrainian, Belarusian, Polish)
    "anml": "animal",
    # Personal (for Ukrainian, Belarusian, Polish)
    "pr": "personal",
    # Nonpersonal not currently used
    "np": "nonpersonal",
    # Virility (for Polish)
    "vr": "virile",
    "nv": "nonvirile",
    # Numbers
    "s": "singular number",
    "d": "dual number",
    "p": "plural number",
    # Verb qualifiers
    "impf": "imperfective aspect",
    "pf": "perfective aspect",
    "mf": "masculine feminine",
}

import re

from .models import WordEntry
from .topics import LABEL_TOPICS

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

COMPARISON_TAGS: dict[str, str] = {
    # https://en.wikipedia.org/wiki/Comparison_(grammar)
    "原级": "positive",
    "比較級": "comparative",
    "最高級": "superlative",
}

GRAMMATICAL_TAGS: dict[str, str] = {
    **GENDER_TAGS,
    **NUMBER_TAGS,
    **COUNT_TAGS,
    **OTHER_TAGS,
    **VERB_TAGS,
    **JA_STEM_FORMS,
    **VOICE_TAGS,
    **COMPARISON_TAGS,
}

# https://zh.wiktionary.org/wiki/Template:Label
# https://zh.wiktionary.org/wiki/Module:Labels/data
# https://zh.wiktionary.org/wiki/Template:Qualifier
# https://zh.wiktionary.org/wiki/Template:古
# https://zh.wiktionary.org/wiki/Template:注释
LABEL_TAGS = {
    "棄用": "obsolete",
    "比喻": "figuratively",
    "古": "archaic",
    "陽": "masculine",
    "陰": "feminine",
    "喻": "figuratively",
    "書": "literary",
    "口": "colloquial",
    "俚": "slang",
    "俗": "slang",
    "方": "dialectal",
    "废": "obsolete",
    "貶": "derogatory",
    "罕": "rare",
    "引": "broadly",
    "現已罕用": "archaic",
    # Module:Labels/data
    "back slang": "slang",
    "synecdochically": "synecdoche",
    "不再自由造詞": "idiomatic",
    "不及物": "intransitive",
    "不可數": "uncountable",
    "不定": "indefinite",
    "不常見": "uncommon",
    "不推薦使用": "proscribed",
    "中性": "neuter",
    "中間被動語態": "mediopassive",
    "中間語態": "middle",
    "主動語態": "active",
    "主要用於否定": "usually with-negation",
    "交互": "reciprocal",
    "以單數形式": "singular",
    "以複數形式": "in-plural",
    "作定語": "attributive",
    "作格": "ergative",
    "作表語": "predicative",
    "使役": "causative",
    "俗語": "idiomatic",
    "俚語": "slang",
    "兒童用語": "childish",
    "公文": "bureaucratese",
    "冒犯": "offensive",
    "分詞": "participle",
    "前古典": "pre-Classical",
    "助動詞": "auxiliary",
    "助記符": "mnemonic",
    "及物": "transitive",
    "反問句": "rhetoric",
    "反身": "reflexive",
    "口語": "colloquial",
    "古舊": "archaic",
    "可數": "countable",
    "同性戀俚語": "slang LGBT",
    "名詞化": "noun-from-verb",
    "唯單": "singular singular-only singular",
    "唯複": "plural plural-only",
    "國際音標": "IPA",
    "基數詞": "cardinal",
    "大寫": "capitalized",
    "委婉": "euphemistic",
    "字面義": "literally",
    "完整": "perfect",
    "完整體": "perfective",
    "定語": "attributive",
    "實詞": "substantive",
    "尊敬": "honorific",
    "常用複數": "plural-normally",
    "幽默": "humorous",
    "序數詞": "ordinal",
    "廣義來說": "broadly",
    "引申": "broadly",
    "弱祈使式": "jussive",
    "強調": "emphatic",
    "後古典": "obsolete",
    "性別中立": "gender-neutral",
    "情態": "modal",
    "愛稱": "endearing",
    "所有格代詞": "possessive pronoun without-noun",
    "押韻俚語": "slang",
    "抽象名詞": "abstract-noun",
    "擬態詞": "ideophonic",
    "擬聲詞": "onomatopoeic",
    "新詞": "neologism",
    "方言": "dialectal",
    "書面": "literary",
    "有比較級": "comparable",
    "有生": "animate",
    "正式": "formal",
    "歷史": "historical",
    "比喻義": "figuratively",
    "無人稱": "impersonal",
    "無比較級": "not-comparable",
    "無生": "inanimate",
    "焦點": "focus",
    "狹義": "narrowly",
    "監獄俚語": "slang",
    "直陳語氣": "indicative",
    "短信": "Internet",
    "祈使語氣": "imperative",
    "禮貌": "polite",
    "種族歧視語": "slur",
    "粉絲用語": "slang lifestyle",
    "粗俗": "vulgar",
    "系動詞": "copulative",
    "網路用語": "Internet",
    "縮寫": "abbreviation",
    "罕用": "rare",
    "臨時語": "nonce-word",
    "虛擬語氣": "subjunctive",
    "表語": "predicative",
    "被動語態": "passive",
    "視覺方言": "pronunciation-spelling",
    "親切": "familiar",
    "詈語": "expletive",
    "詩歌": "poetic",
    "誇飾": "excessive",
    "語中音省略": "syncope",
    "諷刺": "sarcastic",
    "謙遜": "humble",
    "貶義": "derogatory",
    "轉喻義": "metonymically",
    "返璞詞": "retronym",
    "過時": "dated",
    "陰性": "feminine",
    "陽性": "masculine",
    "雙及物動詞": "ditransitive",
    "靜態動詞": "stative",
    "非完整": "imperfect",
    "非完整體": "imperfective",
    "非常罕用": "rare",
    "非標準": "nonstandard",
    "非標準形式": "nonstandard",
    "非正式": "informal",
    "首字母縮略詞": "initialism",
    "駭客語": "Leet Internet",
    "高語域": "honorific",
    # also from Module:Labels/data, but translated manually
    "喃字": "Chu-Nom",
    "反身代詞": "reflexive",
    "字面意義": "literally",
    "成語": "Chengyu",
}


ALL_TAGS = {**GRAMMATICAL_TAGS, **LABEL_TAGS}


def translate_raw_tags(data: WordEntry) -> WordEntry:
    raw_tags = []
    for raw_tag in data.raw_tags:
        for split_raw_tag in re.split(r"(?:,|，)\s*", raw_tag):
            if split_raw_tag in ALL_TAGS:
                data.tags.append(ALL_TAGS[split_raw_tag])
            elif split_raw_tag in LABEL_TOPICS and hasattr(data, "topics"):
                data.topics.append(LABEL_TOPICS[split_raw_tag])
            else:
                raw_tags.append(split_raw_tag)
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

from typing import Union

from .models import WordEntry

# https://ru.wiktionary.org/wiki/Викисловарь:Условные_сокращения
STYLE_TAGS: dict[str, Union[str, list[str]]] = {
    "бран.": "offensive",
    "вульг.": "vulgar",
    "высок.": "honorific",
    "гипокор.": "familiar",
    "груб.": "vulgar",
    "детск.": "childish",
    "диал.": "dialectal",
    # "дисфм.": "дисфемизм",
    "жарг.": "slang",
    "ирон.": "ironic",
    "истор.": "historical",
    # "канц.": "канцелярское",
    "книжн.": "literary",
    "ласк.": "diminutive",
    # "мол.": "молодёжное",
    "нар.-поэт.": "poetic",
    "нар.-разг.": "colloquial",
    # "научн.": "научное",
    "неодобр.": "disapproving",
    "неол.": "neologism",
    # "обсц.": "обсценное",
    "офиц.": "formal",
    # "патет.": "патетическое",
    "поэт.": "poetic",
    "презр.": "contemplative",
    "пренебр.": "derogatory",
    "прост.": "colloquial",
    # "проф.": "профессиональное",
    # "публиц.": "публицистическое",
    "разг.": "colloquial",
    "рег.": "regional",
    "ритор.": "rhetoric",
    "сленг.": "slang",
    "сниж.": "reduced",
    # "советск.": "советизм",
    "спец.": "special",
    "старин.": "archaic",
    "табу": "taboo",
    # "торж.": "торжественное",
    "трад.-нар.": "traditional",
    "трад.-поэт.": ["traditional", "poetic"],
    # "увелич.": "увеличительное",
    "уменьш.": "diminutive",
    "умласк.": ["diminutive", "endearing"],
    "унич.": "pejorative",
    "усилит.": "emphatic",
    "устар.": "obsolete",
    "фам.": "familiar",
    # "школьн.": "школьное",
    "шутл.": "humorous",
    "эвф.": "euphemistic",
    # "экзот.": "экзотизм",
    "экспр.": "expressively",
    # "эррат.": "эрративное",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        raw_tag_lower = raw_tag.lower()
        if raw_tag_lower in STYLE_TAGS:
            tr_tag = STYLE_TAGS[raw_tag_lower]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
    data.raw_tags = raw_tags

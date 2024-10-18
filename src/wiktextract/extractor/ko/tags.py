from .models import WordEntry

# https://ko.wiktionary.org/wiki/모듈:labels/data/topical
# https://ko.wiktionary.org/wiki/모듈:labels/data
GLOSS_TAGS = {
    "고어": "archaic",
    "자동사": "intransitive",
}

TAGS = {**GLOSS_TAGS}

TOPICS = {
    "금융": "finance",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            data.tags.append(TAGS[raw_tag])
        elif raw_tag in TOPICS:
            data.topics.append(TOPICS[raw_tag])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags

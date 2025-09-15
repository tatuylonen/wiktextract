from .models import WordEntry

# https://cs.wiktionary.org/wiki/Modul:Priznaky/seznam
LABEL_TAGS = {
    "expresivně": "expressively",
    "pejorativně": "pejorative",
}

GENDER_TAGS = {
    "mužský": "masculine",
    "životný": "animate",
    "femininum (ženský rod)": "feminine",
    "neutrum (střední rod)": "neuter",
    "maskulinum (mužský rod)": "masculine",
}


TAGS = {**LABEL_TAGS, **GENDER_TAGS}

TOPICS = {}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS and hasattr(data, "tags"):
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        elif raw_tag in TOPICS and hasattr(data, "topics"):
            topic = TOPICS[raw_tag]
            if isinstance(topic, str):
                data.topics.append(topic)
            elif isinstance(topic, list):
                data.topics.extend(topic)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags

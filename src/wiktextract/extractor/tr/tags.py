from .models import BaseModel

GLOSS_TAGS = {
    "mecaz": "metaphoric",  # "Şablon:mecaz"
    "bazen": "sometimes",
    "özellikle": "especially",
    "ender": "rare",
    "kısa": "short-form",
}

POS_HEADER_TAGS = {
    # Şablon:tr-ad
    "belirtme hâli": "accusative",
    "çoğulu": "plural",
    # Şablon:en-ad
    "üçüncü tekil kişi geniş zaman": ["third-person", "singular", "present"],
    "şimdiki zaman": "present",
    "geçmiş zaman ve yakın geçmiş zaman": "past",
    # Şablon:de-ad
    "tamlayan hâli": "genitive",
    "dişil": "feminine",
    "d": "feminine",
    "e": "masculine",
    "eril": "masculine",
}


TAGS = {**GLOSS_TAGS, **POS_HEADER_TAGS}

# https://tr.wiktionary.org/wiki/Modül:temalar/veri/konu
TOPICS = {
    "anatomi": "anatomy",
    "bilişim": "informatics",
    "diller": "language",
    "eğitim": "education",
}


def translate_raw_tags(data: BaseModel) -> None:
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

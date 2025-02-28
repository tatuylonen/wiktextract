from .models import WordEntry

GLOSS_TAGS = {
    # https://id.wiktionary.org/wiki/Templat:Istilah
    "cak": "informal",
    "kiasan": "figuratively",
    "mdt": "morpheme",
    "Sas": "literary",
}

TRANSLATION_TAGS = {
    # https://id.wiktionary.org/wiki/Modul:gender_and_number/data
    "m": "masculine",
    "f": "feminine",
    "n": "neuter",
    "jamak": "plural",
}

NUM_TAGS = {
    "tunggal": "singular",
    "plural": "plural",
}

SOUND_TAGS = {
    "RP": "Received-Pronunciation",
    "US": "US",
}

TAGS = {**TRANSLATION_TAGS, **GLOSS_TAGS, **NUM_TAGS, **SOUND_TAGS}

TOPICS = {
    "Kim": "chemistry",
    "Mat": "mathematics",
}


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

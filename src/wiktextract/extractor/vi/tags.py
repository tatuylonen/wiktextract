from .models import WordEntry

# https://vi.wiktionary.org/wiki/Mô_đun:labels/data
LABEL_TAGS = {
    "không còn dùng": "obsolete",
}
# https://vi.wiktionary.org/wiki/Mô_đun:gender_and_number/data
GENDER_NUMBER_TAGS = {
    "giống đực": "masculine",
    "giống cái": "feminine",
    "giống trung": "neuter",
    "giống chung": "common-gender",
    "gender-neutral": "neuter",
    "động vật": "animate",
    "bất động vật": "inanimate",
    "chỉ loài vật": "animal-not-person",
    "từ chỉ cá nhân": "person",
    "nonpersonal": "impersonal",
    "virile (= masculine personal)": "virile",
    "nonvirile (= other than masculine personal)": "nonvirile",
    "số ít": "singular",
    "số kép": "dual",
    "số nhiều": "plural",
    "thể chưa hoàn thành": "imperfective",
    "thể hoàn thành": "perfective",
}

LOCATIONS = {
    "hà nội": "Hà-Nội",
    "huế": "Huế",
    "sài gòn": "Saigon",
    "vinh": "Vinh",
    "thanh chương": "Thanh-Chương",
    "hà tĩnh": "Hà-Tĩnh",
}

TAGS = {**LABEL_TAGS, **GENDER_NUMBER_TAGS, **LOCATIONS}

# https://vi.wiktionary.org/wiki/Mô_đun:labels/data/topical
TOPICS = {
    "địa chấn học": "seismology",
    "thực vật học": "botany",
    "hóa học": "chemistry",
}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag.lower() in TAGS and hasattr(data, "tags"):
            tr_tag = TAGS[raw_tag.lower()]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        elif raw_tag.lower() in TOPICS and hasattr(data, "topics"):
            topic = TOPICS[raw_tag.lower()]
            if isinstance(topic, str):
                data.topics.append(topic)
            elif isinstance(topic, list):
                data.topics.extend(topic)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags

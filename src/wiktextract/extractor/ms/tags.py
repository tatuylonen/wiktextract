from .models import WordEntry

GENDER_TAGS = {
    # Modul:gender_and_number/data
    "m": "masculine",
    "f": "feminine",
    "n": "neuter",
    "c": "common",
    "neutral": "neutral",
    "bernyawa": "animate",
    "tak bernyawa": "inanimate",
    "haiwan": "animal-not-person",
    "peribadi": "personal",
    "tak peribadi": "impersonal",
    "vir": "virile",
    "nvir": "nonvirile",
    "mf": "singular",
    "du": "dual",
    "jm": "plural",
    "impf": "imperfective",
    "pf": "perfective",
    "takrifan sama": ["masculine", "feminine"],
    "mengikut keadaan": ["masculine", "feminine"],
}

POS_HEADER_TAGS = {
    "ejaan Jawi": "Jawi",
}


TAGS = {**GENDER_TAGS, **POS_HEADER_TAGS}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS and hasattr(data, "tags"):
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags

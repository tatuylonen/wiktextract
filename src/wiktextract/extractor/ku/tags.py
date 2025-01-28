from .models import WordEntry

GENDER_NUMBER_TAGS = {
    # https://ku.wiktionary.org/wiki/Modul:gender_and_number
    "m": "feminine",
    "n": "masculine",
    "nt": "neuter",
    "g": "common-gender",
    "anim": "animate",
    "inan": "inanimate",
    "animal": "animal-not-person",
    "pers": "personal",
    "npers": "impersonal",
    "vir": "virile",
    "nvir": "nonvirile",
    "yj": "singular",
    "du": "dual",
    "pj": "plural",
    "impf": "imperfective",
    "pf": "perfective",
    "gh": "transitive",
    "ngh": "intransitive",
}

TAGS = {**GENDER_NUMBER_TAGS}


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

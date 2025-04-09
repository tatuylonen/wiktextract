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

LB_TAGS = {
    # Modul:labels/data
    "kependekan": "abbreviation",
    "akronim": "acronym",
    "transitif": "transitive",
    "tidak transitif": "intransitive",
    "jussive": "jussive",
    "arkaik": "archaic",
    "atelic": "imperfective",
    "kata bantu": ["auxiliary", "verb"],
    "nombor kardinal": "cardinal",
    "kausatif": "causative",
    # "berbilang": "",
    "kebudak-budakan": "childish",
    "chữ Nôm Vietnam": ["Chữ-Nôm", "Vietnam"],
    "hinaan": "offensive",
    "hinaan kaum": ["ethnic", "offensive"],
    "eufemisme": "euphemistic",
    "kiasan": "figuratively",
    "jenaka": "humorous",
    "tidak formal": "informal",
    "ironi": "ironic",
    "harfiah": "literally",
    "slanga perubatan": "slang",  # medicine
    "metonim": "metonymically",
    "neologisme": "neologism",
    "bentuk bukan baku": "nonstandard",
    "usang": "obsolete",
    "lapuk": "obsolete",
    "kata kasar": "impolite",
    "sopan": "polite",
    "pasca-Klasik": "post-Classical",
    "slanga penjara": "slang",  # prison
    # "hina agama": "",
    "slanga": "slang",
    "slanga sekolah": "slang",  # school
    # "hina diri": "",
    "slanga universiti": "slang",  # university
    "sinkop": "syncope",
    # "teknikal": "",  # technical
    "slanga mesej": "slang",  # message
    "lucah": "vulgar",
}

POS_HEADER_TAGS = {
    "ejaan Jawi": "Jawi",
}

SOUND_TAGS = {
    "Received Pronunciation": "Received-Pronunciation",
    "General American": "General-American",
}


TAGS = {**GENDER_TAGS, **POS_HEADER_TAGS, **SOUND_TAGS, **LB_TAGS}


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

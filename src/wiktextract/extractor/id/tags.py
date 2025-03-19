from .models import WordEntry

GLOSS_TAGS = {
    # https://id.wiktionary.org/wiki/Templat:Istilah
    "cak": "slang",
    "kiasan": "figuratively",
    "mdt": "morpheme",
    "Sas": "literary",
    "arkais": "archaic",
    "klasik": "Classical",
    "nonformal": "informal",
    "akar": "root",
    "akronim": "acronym",
    "kasar": "impolite",
    "hormat": "honorific",
    "generalisasi": "general",
    "neologisme": "neologism",
    "eufemisme": "euphemism",
    "Sunda": "Sundanese",
    "Aceh": "Acehnese",
    "Banjar": "Banjarese",
    "Minangkabau": "Minangkabau",
    "Gorontalo": "Gorontalo",
    "Madura": "Madurese",
    "Batak": "Batak",
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

POS_HEADER_TAGS = {
    "pasif": "passive",
    "transitif": "transitive",
    "imperatif": "imperative",
    "aktif": "active",
}

TAGS = {
    **TRANSLATION_TAGS,
    **GLOSS_TAGS,
    **NUM_TAGS,
    **SOUND_TAGS,
    **POS_HEADER_TAGS,
}

TOPICS = {
    "Kim": "chemistry",
    "Mat": "mathematics",
    "Ling": "linguistics",
    "Dok": "medicine",
    "Bio": "biology",
    "Sas": "literature",
    "Mus": "music",
    "Antr": "anthropology",
    "Ars": "architecture",
    "Ark": "archaeology",
    "Psi": "psychology",
    "Isl": "Islam",
    "Geo": "geology",
    "Hin": "Hinduism",
    "Hid": "hydrology",
    "Huk": "law",
    "Kat": "Catholicism",
    "Fis": "physics",
    "Olr": "sports",
    "Dik": "education",
    "Far": "pharmacology",
    "Lay": "shipping",
    "Komp": "computer",
    "Kris": "Christianity",
    "Bot": "botany",
    "Stat": "statistics",
    "Tan": "agriculture",
    "Elek": "electronics",
    "Anat": "anatomy",
    "Adm": "administration",
    "Sen": "arts",
    "Tas": "Sufism",
    "Graf": "printing",
    "Astron": "astronomy",
    "Met": "meteorology",
    "Dag": "commerce",
    "Zool": "zoology",
    "Min": "mineralogy",
    "Kom": "communications",
    "Hut": "forestry",
    "Eko": "economy",
    "Tek": "technology",
    "Mil": "military",
    "Sos": "sociology",
    "Pol": "politics",
    # "Tern": "",
    "Man": "management",
    "Ikn": "fishing",
    "Fil": "philosophy",
    "Astrol": "astrology",
    "Keu": "finance",
    "Filol": "philology",
    "Metal": "metallurgy",
    "Ent": "entomology",
    "Bud": "Buddhism",
    # "Idt": "industry",
    "Mik": "mycology",
    "Pet": "petrology",
    "Dem": "demography",
    # "Hidm": "hydrometeorology",
    "Film": "film",
    "Tbg": "culinary",
    "Bakt": "bacteriology",
    "Foto": "photography",
    "Pang": ["food", "sciences"],
    "Hindu Bali": "Balinese Hinduism",
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

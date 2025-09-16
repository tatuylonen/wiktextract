from .models import WordEntry

# https://cs.wiktionary.org/wiki/Modul:Priznaky/seznam
LABEL_TAGS = {
    "expresivně": "expressively",
    "pejorativně": "pejorative",
    "zastarale": "obsolete",
}

GENDER_TAGS = {
    "mužský": "masculine",
    "životný": "animate",
    "neživotný": "inanimate",
    "femininum (ženský rod)": "feminine",
    "ženský": "feminine",
    "neutrum (střední rod)": "neuter",
    "střední": "neuter",
    "maskulinum (mužský rod)": "masculine",
}

TABLE_TAGS = {
    # Šablona:Substantivum_(cs)
    "jednotné": "singular",
    "množné": "plural",
    "nominativ": "nominative",
    "genitiv": "genitive",
    "dativ": "dative",
    "akuzativ": "accusative",
    "vokativ": "vocative",
    "lokál": "locative",
    "instrumentál": "instrumental",
    # Šablona:Adjektivum_(cs)
    "mužský\nživotný": ["masculine", "animate"],
    "mužský\nneživotný": ["masculine", "inanimate"],
    # Šablona:Stupňování_(cs)
    "pozitiv": "positive",
    "komparativ": "comparative",
    "superlativ": "superlative",
    # Šablona:Sloveso_(cs)
    "Oznamovací způsob": "indicative",
    "číslo jednotné": "singular",
    "číslo množné": "plural",
    "1.": "first-person",
    "2.": "second-person",
    "3.": "third-person",
    "přítomný čas": "present",
    "Rozkazovací způsob": "imperative",
    "číslo\njednotné": "singular",
    "Příčestí": "participle",
    "mužský životný\ni neživotný": ["masculine", "animate", "inanimate"],
    "mužský neživotný\na ženský": ["masculine", "animate", "feminine"],
    "činné": "active",
    "Přechodníky": "transgressive",
    "ženský\nstřední": ["feminine", "neuter"],
    "mužský\nženský\nstřední": ["masculine", "feminine", "neuter"],
    "přítomný": "present",
}


TAGS = {**LABEL_TAGS, **GENDER_TAGS, **TABLE_TAGS}

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

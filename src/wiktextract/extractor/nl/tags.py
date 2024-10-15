from .models import WordEntry

# https://nl.wiktionary.org/wiki/Categorie:Werkwoordsjablonen
VERB_TAGS = {
    "ergatief": "ergative",  # Sjabloon:erga
    "inergatief": "unergative",  # Sjabloon:inerg
    "hulpwerkwoord": "auxiliary",  # Sjabloon:auxl
}

# https://nl.wiktionary.org/wiki/Categorie:WikiWoordenboek:Contextlabels
GLOSS_TAGS = {
    "figuurlijk": "figuratively",
    "verouderd": "obsolete",  # Sjabloon:verouderd
}


TAGS = {**VERB_TAGS, **GLOSS_TAGS}

# https://nl.wiktionary.org/wiki/Categorie:WikiWoordenboek:Contextlabels
TOPICS = {"anatomie": "anatomy"}


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

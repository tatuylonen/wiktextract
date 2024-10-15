from .models import WordEntry

VERB_TAGS = {
    "ergatief": "ergative",  # Sjabloon:erg
    "inergatief": "unergative",  # Sjabloon:inerg
    "hulpwerkwoord": "auxiliary",  # Sjabloon:auxl
}

GLOSS_TAGS = {
    "verouderd": "obsolete",  # Sjabloon:verouderd
}


TAGS = {**VERB_TAGS, **GLOSS_TAGS}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            data.tags.append(TAGS[raw_tag])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags

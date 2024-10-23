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

TABLE_TAGS = {
    # Sjabloon:-nlnoun-
    "enkelvoud": "singular",
    "meervoud": "plural",
    "verkleinwoord": "diminutive",
    # Sjabloon:adjcomp
    "stellend": "positive",
    "vergrotend": "comparative",
    "overtreffend": "superlative",
    "onverbogen": "uninflected",
    "verbogen": "inflected",
    "partitief": "partitive",
    # Sjabloon:-nlverb-
    "onbepaalde wijs": "infinitive",
    "kort": "short-form",
    "onvoltooid": "imperfect",
    "tegenwoordig": "present",
    "toekomend": "future",
    "voltooid": "perfect",
    "onvoltooid deelwoord": ["imperfect", "participle"],
    "voltooid deelwoord": ["past", "participle"],
    "gebiedende wijs": "imperative",
    "aanvoegende wijs": "subjunctive",
    "aantonende wijs": "indicative",
    "eerste": "first-person",
    "tweede": "second-person",
    "derde": "third-person",
    "verleden": "past",
    "voorwaardelijk": "conditional",
}


TAGS = {**VERB_TAGS, **GLOSS_TAGS, **TABLE_TAGS}

# https://nl.wiktionary.org/wiki/Categorie:WikiWoordenboek:Contextlabels
TOPICS = {"anatomie": "anatomy"}


def translate_raw_tags(data: WordEntry) -> None:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag in TAGS:
            tr_tag = TAGS[raw_tag]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        elif raw_tag in TOPICS:
            data.topics.append(TOPICS[raw_tag])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags

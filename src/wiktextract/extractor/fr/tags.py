# https://fr.wiktionary.org/wiki/Annexe:Glossaire_grammatical

# https://en.wikipedia.org/wiki/Grammatical_gender
GENDER_TAGS: dict[str, str] = {
    "commun": "common",
    "féminin": "feminine",
    "masculin": "masculine",
    "neutre": "neuter",
}

# https://en.wikipedia.org/wiki/Grammatical_number
NUMBER_TAGS: dict[str, str] = {
    "singulier": "singular",
    "pluriel": "plural",
    "duel": "dual",
}

# https://en.wikipedia.org/wiki/Grammatical_mood
MOOD_TAGS: dict[str, str] = {
    "indicatif": " indicative",
    "subjonctif": "subjunctive",
    "conditionnel": "conditional",
    "impératif": "imperative",
}

VERB_FORM_TAGS: dict[str, str] = {
    "participe": "participle",
    "imparfait": "imperfect",
    "infinitif": "infinitive",
    "gérondif": "gerund",
}

# https://en.wikipedia.org/wiki/Grammatical_case
CASE_TAGS: dict[str, str] = {
    "accusatif": "accusative",
    "nominatif": "nominative",
    "datif": "dative",
    "génitif": "genitive",
    "vocatif": "vocative",
    "instrumental": "instrumental",
    "locatif": "locative",
}

# https://en.wikipedia.org/wiki/Grammatical_tense
TENSE_TAGS: dict[str, str] = {
    "présent": "present",
    "passé": "past",
    "passé simple": "past",
    "futur simple": "future",
}

# https://en.wikipedia.org/wiki/Grammatical_person
PERSON_TAGS: dict[str, str] = {
    "1ʳᵉ personne": "first-person",
    "2ᵉ personne": "second-person",
    "3ᵉ personne": "third-person",
}

GRAMMATICAL_TAGS: dict[str, str] = {
    **GENDER_TAGS,
    **NUMBER_TAGS,
    **MOOD_TAGS,
    **VERB_FORM_TAGS,
    **CASE_TAGS,
    **TENSE_TAGS,
    **PERSON_TAGS,
}

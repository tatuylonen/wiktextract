# https://fr.wiktionary.org/wiki/Annexe:Glossaire_grammatical
from .models import WordEntry

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
    "indicatif": "indicative",
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
    # https://en.wikipedia.org/wiki/Passé_composé
    "passé composé": "past multiword-construction",
    "plus-que-parfait": "pluperfect",
    "passé antérieur": "past anterior",
    "futur antérieur": "future perfect",
}

# https://en.wikipedia.org/wiki/Grammatical_person
PERSON_TAGS: dict[str, str] = {
    "1ᵉ personne": "first-person",
    "1ʳᵉ personne": "first-person",
    "2ᵉ personne": "second-person",
    "3ᵉ personne": "third-person",
}

SEMANTICS_TAGS: dict[str, str] = {
    # https://en.wikipedia.org/wiki/Definiteness
    "défini": "definite",
    "indéfini": "indefinite",
}

COMPARISON_TAGS: dict[str, str] = {
    # https://en.wikipedia.org/wiki/Comparison_(grammar)
    "positif": "positive",
    "comparatif": "comparative",
    "superlatif": "superlative",
}

GRAMMATICAL_TAGS: dict[str, str] = {
    **GENDER_TAGS,
    **NUMBER_TAGS,
    **MOOD_TAGS,
    **VERB_FORM_TAGS,
    **CASE_TAGS,
    **TENSE_TAGS,
    **PERSON_TAGS,
    **SEMANTICS_TAGS,
    **COMPARISON_TAGS,
}


def translate_raw_tags(data: WordEntry) -> WordEntry:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag.lower() in GRAMMATICAL_TAGS:
            data.tags.append(GRAMMATICAL_TAGS[raw_tag.lower()])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
    return data

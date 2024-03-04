# Grammatical glossary appendix:
# https://fr.wiktionary.org/wiki/Annexe:Glossaire_grammatical
# List of templates:
# https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_modèles
from typing import Union

from .models import WordEntry

# https://en.wikipedia.org/wiki/Grammatical_gender
GENDER_TAGS: dict[str, Union[str, list[str]]] = {
    "commun": "common",
    "féminin": "feminine",
    "masculin": "masculine",
    "neutre": "neuter",
    # https://fr.wiktionary.org/wiki/Modèle:mf
    "masculin et féminin identiques": ["masculine", "feminine"],
    # table header: https://fr.wiktionary.org/wiki/Modèle:fr-rég
    "masculin et féminin": ["masculine", "feminine"],
}

# https://en.wikipedia.org/wiki/Grammatical_number
NUMBER_TAGS: dict[str, str] = {
    "singulier": "singular",
    "pluriel": "plural",
    "duel": "dual",
    "collectif": "collective",
    "singulatif": "singulative",
}

# https://en.wikipedia.org/wiki/Grammatical_mood
MOOD_TAGS: dict[str, str] = {
    "indicatif": "indicative",
    "subjonctif": "subjunctive",
    "conditionnel": "conditional",
    "impératif": "imperative",
}

VERB_FORM_TAGS: dict[str, Union[str]] = {
    "participe": "participle",
    "imparfait": "imperfect",
    "infinitif": "infinitive",
    "gérondif": "gerund",
    # template "pt-verbe-flexion"
    "infinitif personnel": ["infinitive", "personal"],
}

# https://en.wikipedia.org/wiki/Grammatical_case
CASE_TAGS: dict[str, str] = {
    "ablatif": "ablative",
    "accusatif": "accusative",
    "nominatif": "nominative",
    "datif": "dative",
    "génitif": "genitive",
    "vocatif": "vocative",
    "instrumental": "instrumental",
    "locatif": "locative",
}

# https://en.wikipedia.org/wiki/Grammatical_tense
TENSE_TAGS: dict[str, Union[str, list[str]]] = {
    "présent": "present",
    "passé": "past",
    "passé simple": "past",
    "futur simple": "future",
    # https://en.wikipedia.org/wiki/Passé_composé
    "passé composé": "past multiword-construction",
    "plus-que-parfait": "pluperfect",
    "passé antérieur": "past anterior",
    "futur antérieur": "future perfect",
    "prétérit": "preterite",
    "présent simple, 3ᵉ pers. sing.": ["present", "third-person", "singular"],
    "participe passé": ["participle", "past"],
    "participe présent": ["participle", "present"],
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

# https://en.wikipedia.org/wiki/Occitan_language#Writing_system
OCCITAN_NORM_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:oc-norme_mistralienne
    "graphie mistralienne": "Mistralian",
    # https://fr.wiktionary.org/wiki/Modèle:oc-norme_classique
    # "graphie normalisée": "",
    # Modèle:oc-norme bonnaudienne
    # "graphie bonnaudienne": "",
}

# https://en.wikipedia.org/wiki/Breton_mutations
# https://fr.wiktionary.org/wiki/Modèle:br-nom
BRETON_MUTATION_TAGS: dict[str, str] = {
    "non muté": "unmutated",
    "adoucissante": "mutation-soft",
    "durcissante": "mutation-hard",
    "spirante": "mutation-spirant",
    "nasale": "mutation-nasal",
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
    **OCCITAN_NORM_TAGS,
    **BRETON_MUTATION_TAGS,
}


def translate_raw_tags(data: WordEntry) -> WordEntry:
    raw_tags = []
    for raw_tag in data.raw_tags:
        if raw_tag.lower() in GRAMMATICAL_TAGS:
            tr_tag = GRAMMATICAL_TAGS[raw_tag.lower()]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
    return data

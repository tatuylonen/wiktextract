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
    "indénombrable": "uncountable",  # sv-nom-c-ind
}

# https://en.wikipedia.org/wiki/Grammatical_mood
MOOD_TAGS: dict[str, str] = {
    "indicatif": "indicative",
    "subjonctif": "subjunctive",
    "conditionnel": "conditional",
    "impératif": "imperative",
    "volitif": "volitive",
}

VERB_FORM_TAGS: dict[str, Union[str, list[str]]] = {
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
    "futur": "future",
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
PERSON_TAGS: dict[str, Union[str, list[str]]] = {
    "1ᵉ personne": "first-person",
    "1ʳᵉ personne": "first-person",
    "2ᵉ personne": "second-person",
    "3ᵉ personne": "third-person",
    # Modèle:avk-conj
    "1ʳᵉ du sing.": ["first-person", "singular"],
    "2ᵉ du sing.": ["second-person", "singular"],
    "3ᵉ du sing.": ["third-person", "singular"],
    "1ʳᵉ du plur.": ["first-person", "plural"],
    "2ᵉ du plur.": ["second-person", "plural"],
    "3ᵉ du plur.": ["third-person", "plural"],
    "4ᵉ du plur.": ["fourth-person", "plural"],
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

JA_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:ja-trans
    "kanji": "kanji",
    "hiragana": "hiragana",
    "katakana": "katakana",
    "transcription": "transcription",
}

OTHER_GRAMMATICAL_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:be-tab-cas
    "prépositionnel": "prepositional",
}

# template text before gloss
SENSE_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:figuré
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_relation_entre_les_définitions
    "sens figuré": "figuratively",
    "enclise": "enclitic",
    "idiotisme": "idiomatic",
    "péjoratif": "pejorative",
    "désuet": "obsolete",
    "archaïsme": "archaic",
    "vieilli": "dated",
    "néologisme": "neologism",
    "argot": "slang",
    "rare": "rare",
    "plus rare": "rare",
    "familier": "colloquial",
    "par extension": "broadly",
}

# https://en.wikipedia.org/wiki/Voice_(grammar)
VOICE_TAGS: dict[str, Union[str, list[str]]] = {
    # https://fr.wiktionary.org/wiki/Modèle:eo-conj
    "participe actif": ["participle", "active"],
    "participe passif": ["participle", "passive"],
    "adverbe actif": ["adverb", "active"],
    "adverbe passif": ["adverb", "passive"],
    "substantif actif": ["subsuntive", "active"],
    "substantif passif": ["subsuntive", "passive"],
}

GRAMMATICAL_TAGS: dict[str, Union[str, list[str]]] = {
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
    **JA_TAGS,
    **OTHER_GRAMMATICAL_TAGS,
    **SENSE_TAGS,
    **VOICE_TAGS,
}


def translate_raw_tags(
    data: WordEntry,
    table_template_name: str = "",
    tag_dict: dict[str, str] = GRAMMATICAL_TAGS,
) -> WordEntry:
    from .topics import TOPIC_TAGS

    raw_tags = []
    for raw_tag in data.raw_tags:
        raw_tag_lower = raw_tag.lower()
        if raw_tag_lower in tag_dict:
            tr_tag = tag_dict[raw_tag_lower]
            if isinstance(tr_tag, str):
                data.tags.append(tr_tag)
            elif isinstance(tr_tag, list):
                data.tags.extend(tr_tag)
        elif hasattr(data, "topics") and raw_tag_lower in TOPIC_TAGS:
            data.topics.append(TOPIC_TAGS[raw_tag_lower])
        else:
            raw_tags.append(raw_tag)
    data.raw_tags = raw_tags
    if table_template_name != "":
        return convert_table_headers(data, table_template_name)
    return data


def convert_table_headers(data: WordEntry, template_name: str) -> WordEntry:
    if template_name == "avk-tab-conjug":
        # https://fr.wiktionary.org/wiki/Modèle:avk-tab-conjug
        tags = {
            "1": "first-person",
            "2": "second-person",
            "3": "third-person",
            "4": "fourth-person",
        }
        return translate_raw_tags(data, tag_dict=tags)
    return data

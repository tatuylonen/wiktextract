# Grammatical glossary appendix:
# https://fr.wiktionary.org/wiki/Annexe:Glossaire_grammatical
# List of templates:
# https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_modèles
from .models import WordEntry

# https://en.wikipedia.org/wiki/Grammatical_gender
GENDER_TAGS: dict[str, str | list[str]] = {
    "commun": "common",
    "féminin": "feminine",
    "masculin": "masculine",
    "neutre": "neuter",
    # https://fr.wiktionary.org/wiki/Modèle:mf
    "masculin et féminin identiques": ["masculine", "feminine"],
    # table header: https://fr.wiktionary.org/wiki/Modèle:fr-rég
    "masculin et féminin": ["masculine", "feminine"],
    # "Modèle:mf ?", "Modèle:fm ?"
    "masculin ou féminin (l’usage hésite)": ["masculine", "feminine"],
    "féminin ou masculin (l’usage hésite)": ["feminine", "masculine"],
    "invariable": "invariable",  # Modèle:invar
    # Modèle:flex-ku-nommixt
    "masculin sing.": ["masculine", "singular"],
    "féminin sing.": ["feminine", "singular"],
    # Template:ja-flx-adj-な
    "neutre négatif": ["neuter", "negative"],
    "neutre passé": ["neuter", "past"],
    "neutre négatif passé": ["neuter", "negative", "past"],
    "poli négatif": ["polite", "negative"],
    "poli passé": ["polite", "past"],
    "poli négatif passé": ["polite", "negative", "past"],
    # Template:m
    "masculin animé": ["masculine", "animate"],
    "masculin inanimé": ["masculine", "inanimate"],
    # Template:f
    "féminin animé": ["feminine", "animate"],
    "féminin inanimé": ["feminine", "inanimate"],
}

# https://en.wikipedia.org/wiki/Grammatical_number
NUMBER_TAGS: dict[str, str | list[str]] = {
    "singulier": "singular",
    "pluriel": "plural",
    "duel": "dual",
    "collectif": "collective",
    "singulatif": "singulative",
    "indénombrable": "uncountable",  # sv-nom-c-ind
    "au singulier": "singular",
    "au singulier uniquement": "singular-only",
    "au pluriel": "plural",
    "au pluriel uniquement": "plural-only",
    "singulier et pluriel identiques": ["singular", "plural"],
    "nom collectif": "collective",
    # "générique": "",  # Modèle:g
    # "nom d'unité": "",  # Modèle:nu
    "généralement indénombrable": "uncountable",
    "dénombrable": "countable",
}

# https://en.wikipedia.org/wiki/Grammatical_mood
MOOD_TAGS: dict[str, str] = {
    "indicatif": "indicative",
    "subjonctif": "subjunctive",
    "conditionnel": "conditional",
    "impératif": "imperative",
    "volitif": "volitive",
    "déclaratif": "declarative",
    "interrogatif": "interrogative",
    "aperceptif": "apperceptive",
    "euphémique": "euphemistic",
    "évidentiel": "evidential",
    "spéculatif": "speculative",
    "assertif": "assertive",
    "hortatif": "hortative",
    "promissif": "promissive",
    "conditionnel / subjonctif": ["conditional", "subjunctive"],
    "conjonctif": "subjunctive",
    "provisionnel": "temporal",
}

VERB_FORM_TAGS: dict[str, str | list[str]] = {
    "participe": "participle",
    "imparfait": "imperfect",
    # Template:ku-conj-trans
    "parfait": "perfect",
    "imparfait narratif": ["imperfect", "narrative"],
    "infinitif": "infinitive",
    "gérondif": "gerund",
    # template "pt-verbe-flexion"
    "infinitif personnel": ["infinitive", "personal"],
    "supin": "supine",
    # Template:ko-conj
    "conjugaison": "conjugation",
    "radical": "radical",
    "formes finales": "final",
    "registre formel": "formal",
    "registre informel": "informal",
    "non poli": "impolite",
    "poli": "polite",
    "formes nominales": "nominal",
    "formes conjonctives": "subjunctive",
    # Template:ja-在る
    "formes de base": "base-form",
    "affirmatif": "affirmative",
    "négatif": "negative",
    "adverbial": "adverbial",
    # Template:bg-verbe186
    "aoriste": "aorist",
    "participe passé passif": ["participle", "past", "passive"],
    "participe passé actif": ["participle", "past", "active"],
    "participe imparfait": ["participle", "imperfect"],
}

# https://en.wikipedia.org/wiki/Grammatical_case
CASE_TAGS: dict[str, str | list[str]] = {
    "ablatif": "ablative",
    "accusatif": "accusative",
    "accusatif génitif": ["accusative", "genitive"],
    "nominatif": "nominative",
    "datif": "dative",
    "génitif": "genitive",
    "vocatif": "vocative",
    "instrumental": "instrumental",
    "locatif": "locative",
    "comitatif": "comitative",
    "essif": "essive",
    "illatif": "illative",
    # Template:ro-nom-tab
    "nominatif accusatif": ["nominative", "accusative"],
    "datif génitif": ["dative", "genitive"],
    # Template:ko-nom
    "nominatif / attributif": ["nominative", "attributive"],
}

# https://en.wikipedia.org/wiki/Grammatical_tense
TENSE_TAGS: dict[str, str | list[str]] = {
    "présent": "present",
    "passé": "past",
    "passé simple": "past",
    "futur": "future",
    "futur simple": "future",
    # https://en.wikipedia.org/wiki/Passé_composé
    "passé composé": ["past", "multiword-construction"],
    "plus-que-parfait": "pluperfect",
    "passé antérieur": ["past", "anterior"],
    "futur antérieur": ["future", "perfect"],
    "prétérit": "preterite",
    "présent simple, 3ᵉ pers. sing.": ["present", "third-person", "singular"],
    "participe passé": ["participle", "past"],
    "participe présent": ["participle", "present"],
    # Template:ku-conj-trans
    "présent progressif": ["present", "progressive"],
    "prétérit et imparfait": ["preterite", "imperfect"],
    "non passé": "non-past",
    "présent / futur": ["present", "future"],
}

# https://en.wikipedia.org/wiki/Grammatical_person
PERSON_TAGS: dict[str, str | list[str]] = {
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
    "anglicisme": "Anglicism",
    "pronominal": "pronominal",
    "diminutif": "diminutive",
    "réfléchi": "reflexive",  # Modèle:réfl
    "réciproque": "reciprocal",  # Modèle:réciproque
    "impersonnel": "impersonal",  # Modèle:impers
    "transitif": "transitive",  # Modèle:t
    "intransitif": "intransitive",  # Modèle:i
    "injurieux": "offensive",  # Modèle:injurieux
    # Modèle:zh-formes
    "simplifié": "Simplified Chinese",
    "traditionnel": "Traditional Chinese",
    # Modèle:flex-ku-nomf
    "ézafé principal": ["ezafe", "primary"],
    "ézafé secondaire": ["ezafe", "secondary"],
    "cas oblique": "oblique",
    # Modèle:ku-conj-trans
    "forme affirmative": "affirmative",
    "forme négative": "negative",
    # Modèle:bg-nom
    "forme de base": "base-form",
    "pluriel numéral": ["plural", "numeral"],
    "animé": "animate",
    "inanimé": "inanimate",
    # Template:ko-nom
    "hangeul": "hangeul",
    "hanja": "hanja",
    "avec clitique": "clitic",
}

# template text before gloss
SENSE_TAGS: dict[str, str] = {
    # https://fr.wiktionary.org/wiki/Modèle:figuré
    # https://fr.wiktionary.org/wiki/Catégorie:Modèles_de_relation_entre_les_définitions
    # Catégorie:Modèles de genre textuel
    # Catégorie:Modèles de registre
    "sens figuré": "figuratively",
    "sens propre": "literally",
    "par métonymie": "metonymically",  # Modèle:par métonymie
    "par hyperbole": "hyperbole",
    "par extension": "broadly",
    "par analogie": "analogy",
    "en particulier": "especially",
    "par litote": "litotes",
    "par euphémisme": "euphemism",
    "spécifiquement": "specifically",
    "génériquement": "generically",
    "spécialement": "especially",
    "généralement": "generally",
    "enclise": "enclitic",
    "idiotisme": "idiomatic",
    "péjoratif": "pejorative",
    "désuet": "obsolete",
    "archaïsme": "archaic",
    "vieilli": "dated",
    "néologisme": "neologism",
    "argot": "slang",
    "rare": "rare",
    # "plus rare": "rare",
    "littéraire": "literary",  # Modèle:littéraire
    "poétique": "poetic",  # Modèle:poétique
    # "didactique": "",  # Modèle:didactique
    "soutenu": "formal",  # Modèle:soutenu
    "informel": "informal",  # Modèle:informel
    "familier": "familiar",  # Modèle:familier
    "très familier": "very-familiar",  # Modèle:très familier
    "populaire": "colloquial",  # Modèle:populaire
    "vulgaire": "vulgar",  # Modèle:vulgaire
    "langage enfantin": "childish",  # Modèle:enfantin
    # Catégorie:Modèles de thématique
    "anglicisme informatique": "Anglicism",
    "proverbe": "proverb",
    "collectivement": "collectively",
    "courant": "common",  # Modèle:courant
}

# https://en.wikipedia.org/wiki/Voice_(grammar)
VOICE_TAGS: dict[str, str | list[str]] = {
    # https://fr.wiktionary.org/wiki/Modèle:eo-conj
    "participe actif": ["participle", "active"],
    "participe passif": ["participle", "passive"],
    "adverbe actif": ["adverb", "active"],
    "adverbe passif": ["adverb", "passive"],
    "substantif actif": ["subsuntive", "active"],
    "substantif passif": ["subsuntive", "passive"],
    "actif": "active",
    "passif": "passive",
}

# Module:lexique/data
LEXIQUE_TAGS = {
    "hindouisme": "Hinduism",
    "judaïsme": "Judaism",
    "marxisme": "Marxism",
    "nazisme": "Nazism",
    "physique": "physical",
    "rhétorique": "rhetoric",
    "antiquité": "Ancient",
    "antiquité grecque": "Ancient-Greek",
    "antiquité romaine": "Ancient-Roman",
    "bible": "Biblical",
    "moyen âge": "Middle-Ages",
    "union européenne": "European-Union",
    "analyse": "analytic",
}

# Template:cmn-pron
# https://fr.wiktionary.org/wiki/自由
ZH_PRON_TAGS = {
    "pinyin": "Pinyin",
    "efeo": "EFEO",  # https://en.wikipedia.org/wiki/EFEO_Chinese_transcription
    "wade-giles": "Wade-Giles",
    "yale": "Yale",
    "zhuyin": "Bopomofo",
    "mandarin": "Mandarin",
    "cantonais": "Cantonese",
    "cantonais (yue)": "Cantonese",
    "jyutping": "Jyutping",
    "hakka": "Hakka",
    "pha̍k-fa-sṳ": "Phak-fa-su",
    "meixian, guangdong": ["Meixian", "Guangdong"],
    "jin": "Jin",
    "mindong": "Eastern-Min",
    # https://en.wikipedia.org/wiki/Bàng-uâ-cê
    "bàng-uâ-cê (fuzhou)": ["Bang-ua-ce", "Fuzhou"],
    "minnan": "Min",
    "pe̍h-ōe-jī (hokkien : fujian, taïwan)": [
        "Peh-oe-ji",
        "Hokkien",
        "Fujian",
        "Taiwan",
    ],
    "chaozhou, peng'im": ["Chaozhou", "Peng'im"],
    "wu": "Wu",
    "shanghai": "Shanghai",
    "chinois médiéval": "Medieval-Chinese",
    "chinois archaïque": "Old-Chinese",
    "baxter-sagart": "Baxter-Sagart",
    "zhengzhang": "Zhengzhang",
}

ASPECT_TAGS = {
    "perfectif": "perfective",  # Modèle:perfectif
    "imperfectif": "imperfective",  # Modèle:imperfectif
}

GRAMMATICAL_TAGS: dict[str, str | list[str]] = {
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
    **LEXIQUE_TAGS,
    **ZH_PRON_TAGS,
    **ASPECT_TAGS,
}


def translate_raw_tags(
    data: WordEntry,
    table_template_name: str = "",
    tag_dict: dict[str, str] = GRAMMATICAL_TAGS,
) -> WordEntry:
    from .topics import SLANG_TOPICS, TOPIC_TAGS

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
        elif hasattr(data, "topics") and raw_tag_lower in SLANG_TOPICS:
            data.topics.append(SLANG_TOPICS[raw_tag_lower])
            if "slang" not in data.tags:
                data.tags.append("slang")
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
